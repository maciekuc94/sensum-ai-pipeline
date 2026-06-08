"""
Agent 6b: Image QA (style compliance check)

Audits every PNG in `outputs/videos_pl/{slug}/images/` against the SENSUM style
contract using Gemini 2.5 Flash on Vertex AI. Cheap (~$0.04 per 120-image video)
and roughly 2 minutes per video.

Checks:
  1. The drawn SUBJECT is clean engraving — no texture/grain/mottling baked
     INTO the figure or object. (The empty background is flattened to exact
     #F4E5CA deterministically in post by `flatten_background`, so background
     texture is NOT a defect; texture ON the subject cannot be auto-fixed and
     IS a real failure → reroll.)
  2. Only ink color is dark brown (~#582F0E). No greens, greys, ochres, etc.
  3. NO decorative border, frame, panel, or outline around the image.
  4. If a human figure appears, the entire head is inside the frame.
  5. No visible text, letters, numbers, or labels anywhere.

Outputs:
  outputs/videos_pl/{slug}/md/06_qa.md  — markdown report

Usage:
  python tools/pipeline/agent6b_image_qa.py "<slug>"
  python tools/pipeline/agent6b_image_qa.py "<slug>" --quiet
  python tools/pipeline/agent6b_image_qa.py "<slug>" --retry

`--retry` automatically regenerates failed indices via Agent 6 (one attempt)
and re-runs QA on those indices only. Does NOT delete images. Reports always.
"""

import argparse
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import get_output_dir, get_env, write_output, read_output

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QA_REPORT_FILENAME = "md/06_qa.md"
QA_MODEL = "gemini-2.5-flash"
QA_TEMPERATURE = 0.0  # deterministic — image QA is a binary style gate
REQUEST_DELAY = 1.0  # seconds between Vertex AI calls

QA_PROMPT = (
    "You are auditing an illustration for strict style compliance. "
    "IMPORTANT CONTEXT: the empty sage-beige background is GUARANTEED clean by a "
    "deterministic post-process that flattens it to exact #F4E5CA, so you must NOT "
    "fail an image for texture, grain, mottling or tint in the EMPTY background "
    "area — that is already handled and cannot be a defect. Judge only what is "
    "actually DRAWN. The illustration MUST satisfy ALL of the following:\n"
    "1. The drawn SUBJECT itself is clean line-and-cross-hatch engraving: no "
    "photographic texture, no paper-grain, mottling or noise baked INTO the "
    "figure/object, no aged-paper or parchment look on the subject. Texture sitting "
    "ON the subject cannot be auto-flattened and IS a real failure that needs a "
    "re-render — flag it.\n"
    "2. The only ink color is dark brown (~#582F0E). "
    "No greens, no greys, no ochres, no other colors.\n"
    "3. There is NO decorative border, frame, panel, or outline surrounding "
    "the image. The illustration is full-bleed.\n"
    "4. If a human figure is shown, the entire head is inside the frame "
    "(not cropped at the top).\n"
    "5. No visible text, letters, numbers, or labels anywhere.\n\n"
    "Reply in this exact format and nothing else:\n"
    "VERDICT: PASS  (or)  VERDICT: FAIL\n"
    "REASONS: <if FAIL, one short phrase per violated rule, comma-separated; "
    "if PASS write \"none\">"
)


# ---------------------------------------------------------------------------
# Vertex AI helpers
# ---------------------------------------------------------------------------


def _init_client():
    """Return a Vertex AI genai client. Mirrors agent6_images.py."""
    try:
        project = get_env("GOOGLE_CLOUD_PROJECT")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        print("\nSet GOOGLE_CLOUD_PROJECT in your .env file, e.g.:")
        print("  GOOGLE_CLOUD_PROJECT=my-gcp-project-id")
        sys.exit(1)

    try:
        from google import genai
        client = genai.Client(vertexai=True, project=project, location="global")
        return client, project
    except Exception as exc:
        print(f"\nError: Failed to initialise Vertex AI — {exc}")
        print("\nMake sure you have authenticated:")
        print("  gcloud auth application-default login")
        sys.exit(1)


def _audit_one(client, image_path: Path) -> tuple[str, str]:
    """Send a single image to Gemini 2.5 Flash, return (verdict, reasons).

    verdict ∈ {"PASS", "FAIL", "ERROR"}.
    """
    from google.genai import types as genai_types

    img_bytes = image_path.read_bytes()
    try:
        response = client.models.generate_content(
            model=QA_MODEL,
            contents=[
                genai_types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                QA_PROMPT,
            ],
            config=genai_types.GenerateContentConfig(temperature=QA_TEMPERATURE),
        )
    except Exception as exc:
        return "ERROR", f"vertex call failed: {exc}"

    text = (response.text or "").strip()
    verdict_match = re.search(r"VERDICT:\s*(PASS|FAIL)", text, re.IGNORECASE)
    reasons_match = re.search(r"REASONS:\s*(.+?)(?:\n|$)", text, re.IGNORECASE | re.DOTALL)
    if not verdict_match:
        return "ERROR", f"could not parse verdict from: {text[:200]!r}"
    verdict = verdict_match.group(1).upper()
    reasons = reasons_match.group(1).strip() if reasons_match else "—"
    return verdict, reasons


def _check_background_color(image_path: Path) -> str | None:
    """Sample 4 corners of the image and check if background matches #F4E5CA.
    Returns a failure reason string if wrong color, None if OK.
    Runs locally — no API call needed.
    """
    import numpy as np
    from PIL import Image

    TARGET = (244, 229, 202)  # #F4E5CA sage beige
    TOLERANCE = 20  # max RMS distance; worst passing image observed at 12.1
    SAMPLE = 30     # corner area in pixels

    img = Image.open(str(image_path)).convert("RGB")
    w, h = img.size
    arr = np.array(img)

    strips = [
        arr[:SAMPLE, :],       # top strip, full width
        arr[h - SAMPLE:, :],   # bottom strip, full width
        arr[:, :SAMPLE],       # left strip, full height
        arr[:, w - SAMPLE:],   # right strip, full height
    ]
    samples = np.concatenate([s.reshape(-1, 3) for s in strips], axis=0)
    avg = samples.mean(axis=0)
    dist = float(np.sqrt(((avg - np.array(TARGET)) ** 2).mean()))
    if dist > TOLERANCE:
        r, g, b = int(avg[0]), int(avg[1]), int(avg[2])
        return f"background color #{r:02X}{g:02X}{b:02X} is not sage beige #F4E5CA"
    return None


def _check_missing_images(slug: str, images_dir: Path) -> list[dict]:
    """Return FAIL entries for expected image indices absent from images/."""
    try:
        content = read_output(slug, "md/05_prompts.md")
    except FileNotFoundError:
        return []
    header_match = re.search(r'^Total images:\s*(\d+)', content, re.MULTILINE)
    if header_match:
        total = int(header_match.group(1))
    else:
        total = len(re.findall(r'^## Image \d+', content, re.MULTILINE))
    if total == 0:
        return []
    present = {_index_from_filename(p) for p in images_dir.glob("image_*.png")} if images_dir.exists() else set()
    return [
        {"index": i, "filename": f"image_{i:03d}.png", "verdict": "FAIL", "reasons": "image file missing"}
        for i in range(1, total + 1) if i not in present
    ]


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------


def _index_from_filename(path: Path) -> int | None:
    m = re.match(r"image_(\d+)\.png$", path.name)
    return int(m.group(1)) if m else None


def _write_report(slug: str, results: list[dict], model_id: str) -> Path:
    """Write the markdown QA report. `results` is a list of
    {index, filename, verdict, reasons}."""
    failed = [r for r in results if r["verdict"] == "FAIL"]
    errored = [r for r in results if r["verdict"] == "ERROR"]
    passed = [r for r in results if r["verdict"] == "PASS"]

    lines = []
    lines.append(f"# Image QA Report — {slug}")
    lines.append("")
    lines.append(f"- Model: `{model_id}` (Vertex AI, location=global)")
    lines.append(f"- Total images: {len(results)}")
    lines.append(f"- Passed: {len(passed)}")
    lines.append(f"- Failed: {len(failed)}")
    if errored:
        lines.append(f"- Errored: {len(errored)}")
    lines.append("")
    lines.append("## Failed images")
    lines.append("")
    if failed:
        lines.append("| Index | File | Reasons |")
        lines.append("|---|---|---|")
        for r in failed:
            lines.append(f"| {r['index']:03d} | `{r['filename']}` | {r['reasons']} |")
    else:
        lines.append("_None — all images passed._")
    lines.append("")
    if errored:
        lines.append("## Errored images")
        lines.append("")
        lines.append("| Index | File | Error |")
        lines.append("|---|---|---|")
        for r in errored:
            lines.append(f"| {r['index']:03d} | `{r['filename']}` | {r['reasons']} |")
        lines.append("")
    lines.append("## Passed images")
    lines.append("")
    if passed:
        idxs = sorted(r["index"] for r in passed)
        # Compact range view
        groups = []
        run_start = idxs[0]
        prev = idxs[0]
        for i in idxs[1:]:
            if i == prev + 1:
                prev = i
                continue
            groups.append((run_start, prev))
            run_start = i
            prev = i
        groups.append((run_start, prev))
        compact = ", ".join(
            f"{a:03d}" if a == b else f"{a:03d}–{b:03d}" for a, b in groups
        )
        lines.append(f"Count: {len(passed)} — indices: {compact}")
    else:
        lines.append("_None._")
    lines.append("")

    path = write_output(slug, QA_REPORT_FILENAME, "\n".join(lines))
    return path


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------


def audit(slug: str, *, quiet: bool = False, only_indices: list[int] | None = None) -> list[dict]:
    """Run QA on all images (or only the supplied indices). Returns results list."""
    images_dir = get_output_dir(slug) / "images"

    missing = _check_missing_images(slug, images_dir)
    if only_indices is not None:
        wanted = set(only_indices)
        missing = [r for r in missing if r["index"] in wanted]

    png_files = sorted(images_dir.glob("image_*.png")) if images_dir.exists() else []
    if only_indices is not None:
        wanted = set(only_indices)
        png_files = [p for p in png_files if _index_from_filename(p) in wanted]
        if not png_files and not missing:
            print(f"No images match indices {only_indices} in {images_dir}")
            sys.exit(1)
    elif not png_files and not missing:
        print(f"No images found in {images_dir}")
        sys.exit(1)

    if not png_files:
        if not quiet:
            print(f"\n=== Agent 9b: Image QA ===")
            for r in missing:
                print(f"  MISS  {r['filename']}  image file missing")
        return sorted(missing, key=lambda r: r["index"])

    client, project = _init_client()

    print(f"\n=== Agent 9b: Image QA ===")
    print(f"Slug    : {slug}")
    print(f"Project : {project}")
    print(f"Model   : {QA_MODEL}")
    if missing:
        print(f"Missing : {sorted(r['index'] for r in missing)}")
    print(f"Images  : {len(png_files)}")
    print()

    results: list[dict] = []
    for i, path in enumerate(png_files, start=1):
        idx = _index_from_filename(path) or 0
        verdict, reasons = _audit_one(client, path)
        color_fail = _check_background_color(path)
        if color_fail:
            verdict = "FAIL"
            reasons = f"{color_fail}, {reasons}" if reasons and reasons != "none" else color_fail
        results.append({
            "index": idx,
            "filename": path.name,
            "verdict": verdict,
            "reasons": reasons,
        })
        if not quiet:
            tag = {"PASS": "PASS", "FAIL": "FAIL", "ERROR": "ERR "}[verdict]
            print(f"  [{i:3d}/{len(png_files)}] {tag}  {path.name}  {reasons if verdict != 'PASS' else ''}")
        if i < len(png_files):
            time.sleep(REQUEST_DELAY)

    return sorted(missing + results, key=lambda r: r["index"])


def _retry_failed(slug: str, failed_indices: list[int]) -> None:
    """Spawn agent6_images.py to regenerate the failed indices."""
    if not failed_indices:
        return
    script = Path(__file__).parent / "agent6_images.py"
    cmd = [
        sys.executable, str(script), slug,
        "--generate",
        "--indices", ",".join(str(i) for i in failed_indices),
    ]
    print(f"\n=== Agent 6b: Retry — regenerating {len(failed_indices)} failed images ===")
    print(f"  {' '.join(cmd)}")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    subprocess.run(cmd, check=False, env=env)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agent 9b: vision-based image QA against SENSUM style rules.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/pipeline/agent6b_image_qa.py \"5_how_to_actually_stay_mentally_healthy\"\n"
            "  python tools/pipeline/agent6b_image_qa.py \"5_how_to_actually_stay_mentally_healthy\" --retry\n"
        ),
    )
    parser.add_argument("slug", help="Output slug under outputs/videos/.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-image stdout, only print summary.")
    parser.add_argument("--retry", action="store_true",
                        help="After QA, auto-regenerate failed images via Agent 9 and re-run QA on them.")
    parser.add_argument("--indices", type=str, default=None,
                        help="Comma-separated 1-based indices to audit only (e.g. \"4,13,31\").")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    only_indices: list[int] | None = None
    if args.indices:
        try:
            only_indices = [int(x.strip()) for x in args.indices.split(",") if x.strip()]
        except ValueError:
            print(f"Error: --indices must be comma-separated integers, got: {args.indices!r}")
            sys.exit(1)

    results = audit(slug, quiet=args.quiet, only_indices=only_indices)
    report_path = _write_report(slug, results, QA_MODEL)

    failed = [r for r in results if r["verdict"] == "FAIL"]
    errored = [r for r in results if r["verdict"] == "ERROR"]
    print(f"\nReport: {report_path}")
    print(f"  Pass: {len(results) - len(failed) - len(errored)}  Fail: {len(failed)}  Error: {len(errored)}")

    if args.retry and failed:
        failed_indices = sorted(r["index"] for r in failed)
        _retry_failed(slug, failed_indices)
        print(f"\n=== Agent 9b: Re-running QA on retried indices ===")
        results2 = audit(slug, quiet=args.quiet, only_indices=failed_indices)
        # Merge: replace the retried entries in the original results, keep others.
        retry_map = {r["index"]: r for r in results2}
        merged = [retry_map.get(r["index"], r) for r in results]
        report_path = _write_report(slug, merged, QA_MODEL)
        failed2 = [r for r in results2 if r["verdict"] == "FAIL"]
        print(f"\nRetry result: {len(failed_indices) - len(failed2)}/{len(failed_indices)} now pass")
        print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
