"""
Agent 9b: Image QA (style compliance check)

Audits every PNG in `outputs/videos/{slug}/images/` against the SENSUM style
contract using Gemini 2.5 Flash on Vertex AI. Cheap (~$0.04 per 120-image video)
and roughly 2 minutes per video.

Checks:
  1. Background is a single flat solid sage beige (~#F4E5CA). No texture,
     paper grain, mottling, aged-paper effect, parchment fibers, stains,
     or color tint other than warm beige.
  2. Only ink color is dark brown (~#582F0E). No greens, greys, ochres, etc.
  3. NO decorative border, frame, panel, or outline around the image.
  4. If a human figure appears, the entire head is inside the frame.
  5. No visible text, letters, numbers, or labels anywhere.

Outputs:
  outputs/videos/{slug}/md/09_image_qa.md  — markdown report

Usage:
  python tools/pipeline/agent9b_image_qa.py "<slug>"
  python tools/pipeline/agent9b_image_qa.py "<slug>" --quiet
  python tools/pipeline/agent9b_image_qa.py "<slug>" --retry

`--retry` automatically regenerates failed indices via Agent 9 (one attempt)
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
from tools.utils import get_output_dir, get_env, write_output

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QA_REPORT_FILENAME = "md/09_image_qa.md"
QA_MODEL = "gemini-2.5-flash"
REQUEST_DELAY = 1.0  # seconds between Vertex AI calls

QA_PROMPT = (
    "You are auditing an illustration for strict style compliance. "
    "The illustration MUST satisfy ALL of the following:\n"
    "1. Background is a single flat solid sage beige color (~#F4E5CA). "
    "No texture, no grain visible to a human eye, no aged-paper effect, "
    "no parchment fibers, no mottling, no color tint other than warm beige.\n"
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
    """Return a Vertex AI genai client. Mirrors agent9_images.py."""
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
    png_files = sorted(images_dir.glob("image_*.png"))
    if not png_files:
        print(f"No images found in {images_dir}")
        sys.exit(1)

    if only_indices is not None:
        wanted = set(only_indices)
        png_files = [p for p in png_files if _index_from_filename(p) in wanted]
        if not png_files:
            print(f"No images match indices {only_indices} in {images_dir}")
            sys.exit(1)

    client, project = _init_client()

    print(f"\n=== Agent 9b: Image QA ===")
    print(f"Slug    : {slug}")
    print(f"Project : {project}")
    print(f"Model   : {QA_MODEL}")
    print(f"Images  : {len(png_files)}")
    print()

    results: list[dict] = []
    for i, path in enumerate(png_files, start=1):
        idx = _index_from_filename(path) or 0
        verdict, reasons = _audit_one(client, path)
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

    return results


def _retry_failed(slug: str, failed_indices: list[int]) -> None:
    """Spawn agent9_images.py to regenerate the failed indices."""
    if not failed_indices:
        return
    script = Path(__file__).parent / "agent9_images.py"
    cmd = [
        sys.executable, str(script), slug,
        "--generate",
        "--indices", ",".join(str(i) for i in failed_indices),
        "--grain", "12",
    ]
    print(f"\n=== Agent 9b: Retry — regenerating {len(failed_indices)} failed images ===")
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
            "  python tools/pipeline/agent9b_image_qa.py \"5_how_to_actually_stay_mentally_healthy\"\n"
            "  python tools/pipeline/agent9b_image_qa.py \"5_how_to_actually_stay_mentally_healthy\" --retry\n"
        ),
    )
    parser.add_argument("slug", help="Output slug under outputs/videos/.")
    parser.add_argument("--quiet", action="store_true",
                        help="Suppress per-image stdout, only print summary.")
    parser.add_argument("--retry", action="store_true",
                        help="After QA, auto-regenerate failed images via Agent 9 and re-run QA on them.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    results = audit(slug, quiet=args.quiet)
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
