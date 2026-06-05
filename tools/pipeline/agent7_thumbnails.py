"""
Render engine — render thumbnail image candidates for a given output (used by /package).

Two-step process:
  1. Concepts (full image prompts) are generated IN-SESSION in Claude Code on
     Opus 4.8 via the `/package <slug>` slash command — no Gemini, no Anthropic
     API. The command writes them to md/07_prompts.md (`## Thumbnail N` headers).
     (Legacy: the retired `/thumbnails` command wrote the same file format.)
  2. THIS script renders each prompt via Gemini 3 Pro Image Preview (Vertex AI)
     and post-processes (resize -> background enforce -> optional grain).

This script makes NO Claude/Anthropic API call. It only renders.

Usage:
    /thumbnails <slug>                                            # generate concepts in-session, then render
    PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py <slug> --render
    PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py <slug> --render --no-grain
    PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py <slug> --render --indices 1,4 --count 2
    PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py <slug> --reuse-prompts   # re-render a prior run's prompts
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import (
    read_output, get_output_dir, get_env,
    add_grain, resize_to_target, enforce_background_color,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_MODEL = "gemini-3-pro-image-preview"
GRAIN_INTENSITY = 12  # project standard (Gaussian std dev on 0–255)
REQUEST_DELAY = 20    # seconds between Vertex AI calls to stay under QPM quota

PROMPTS_MD = "md/07_prompts.md"   # written by /thumbnails (in-session concepts)

NEGATIVE_TEXT = (
    "\n\nAvoid in this image: face, eyes, nose, mouth, facial features, "
    "photorealistic face, 3D render, green/dark/colored background, "
    "cropped head, text, words, labels, numbers, captions."
)


# ---------------------------------------------------------------------------
# Prompt loading
# ---------------------------------------------------------------------------


def _parse_prompts_text(text: str) -> list[str]:
    """Parse `## Thumbnail N` sections into a list of prompt strings."""
    sections = text.split("## Thumbnail ")
    prompts = []
    for section in sections[1:]:
        body = section.split("\n", 1)[-1]  # strip the "N\n" header line
        body = body.strip().rstrip("-").strip()
        if body:
            prompts.append(body)
    return prompts


def _load_prompts_md(slug: str) -> list[str]:
    """Load the 5 concepts written in-session by /thumbnails to md/07_prompts.md."""
    try:
        text = read_output(slug, PROMPTS_MD)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"No concepts found at {PROMPTS_MD}.\n"
            f"Generate them in-session first:  /thumbnails {slug}"
        )
    prompts = _parse_prompts_text(text)
    if not prompts:
        raise ValueError(f"Could not parse any prompts from {PROMPTS_MD}")
    return prompts


def _load_saved_prompts(thumbnails_dir: Path) -> list[str]:
    """Parse prompts from an existing thumbnail_prompts.md file (re-render a prior run)."""
    prompts_path = thumbnails_dir / "thumbnail_prompts.md"
    if not prompts_path.exists():
        raise FileNotFoundError(f"No saved prompts found at {prompts_path}")
    prompts = _parse_prompts_text(prompts_path.read_text(encoding="utf-8"))
    if not prompts:
        raise ValueError("Could not parse any prompts from thumbnail_prompts.md")
    return prompts


# ---------------------------------------------------------------------------
# Image generation + post-processing (Gemini / Vertex AI)
# ---------------------------------------------------------------------------


def _generate_image(
    client, prompt: str, output_path: Path, index: int, total: int, apply_grain: bool
) -> bool:
    """Generate one image via Gemini and apply post-processing. Returns True on success."""
    from google.genai import types as genai_types

    print(f"  Generating thumbnail {index}/{total}...")
    try:
        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt + NEGATIVE_TEXT,
            config=genai_types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )
    except Exception as exc:
        print(f"  ERROR generating thumbnail {index}: {exc}")
        return False

    candidates = response.candidates
    if not candidates:
        print(f"  ERROR: No candidates returned for thumbnail {index}")
        return False

    img_bytes = None
    for part in candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            img_bytes = part.inline_data.data
            break

    if not img_bytes:
        print(f"  ERROR: No image bytes in response for thumbnail {index}")
        return False

    output_path.write_bytes(img_bytes)

    # Post-processing: resize → bg enforce → (optional) grain
    resize_to_target(output_path)
    enforce_background_color(output_path)
    if apply_grain:
        add_grain(output_path, intensity=GRAIN_INTENSITY)

    print(f"  Saved: {output_path.name}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if len(sys.argv) < 2:
        print("Usage: PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py <slug> --render [--no-grain] [--indices 1,4] [--count 2]")
        print("       (generate concepts first in Claude Code:  /thumbnails <slug>)")
        sys.exit(1)

    slug = sys.argv[1]
    raw_flags = sys.argv[2:]
    flags = set(raw_flags)
    apply_grain = "--no-grain" not in flags
    reuse_prompts = "--reuse-prompts" in flags
    # --render is the explicit primary flag; default also renders.

    # --indices 1,4  →  only generate these prompt numbers (1-based)
    indices_filter: list[int] | None = None
    for f in raw_flags:
        if f.startswith("--indices="):
            indices_filter = [int(x) for x in f.split("=", 1)[1].split(",")]
        elif f == "--indices" and raw_flags.index(f) + 1 < len(raw_flags):
            indices_filter = [int(x) for x in raw_flags[raw_flags.index(f) + 1].split(",")]

    # --count 3  →  generate each selected prompt this many times
    count = 1
    for f in raw_flags:
        if f.startswith("--count="):
            count = int(f.split("=", 1)[1])
        elif f == "--count" and raw_flags.index(f) + 1 < len(raw_flags):
            count = int(raw_flags[raw_flags.index(f) + 1])

    concept_source = "prior-run prompts (--reuse-prompts)" if reuse_prompts else f"in-session concepts ({PROMPTS_MD})"

    print("=== Agent Thumbnails (render) ===")
    print(f"Slug       : {slug}")
    print(f"Grain      : {'yes' if apply_grain else 'no'}")
    print(f"Prompts    : {concept_source}")
    if indices_filter:
        print(f"Indices    : {indices_filter}  x{count}")

    output_dir = get_output_dir(slug)
    # Use a separate output folder when grain is disabled so originals are preserved
    out_folder = "thumbnails" if apply_grain else "thumbnails_no_grain"
    thumbnails_dir = output_dir / out_folder
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    # Step 1 — load prompts (no LLM call)
    if reuse_prompts:
        # Re-render a prior run. Prompts live alongside the images, so the source
        # folder must match the grain mode of the run that originally generated them.
        src_dir = thumbnails_dir
        if not (src_dir / "thumbnail_prompts.md").exists():
            alt = output_dir / ("thumbnails_no_grain" if apply_grain else "thumbnails")
            if (alt / "thumbnail_prompts.md").exists():
                src_dir = alt
        print(f"\n[1/2] Loading saved prompts from {src_dir.name}/thumbnail_prompts.md...")
        try:
            prompts = _load_saved_prompts(src_dir)
        except (FileNotFoundError, ValueError) as exc:
            print(f"\nError: {exc}")
            sys.exit(1)
    else:
        print(f"\n[1/2] Loading in-session concepts from {PROMPTS_MD}...")
        try:
            prompts = _load_prompts_md(slug)
        except (FileNotFoundError, ValueError) as exc:
            print(f"\nError: {exc}")
            sys.exit(1)
    print(f"  Loaded {len(prompts)} prompts.")

    # Save a copy of the prompts alongside the rendered images for traceability.
    prompts_md = "# Thumbnail Prompts\n\n"
    for i, p in enumerate(prompts, 1):
        prompts_md += f"## Thumbnail {i}\n\n{p}\n\n---\n\n"
    (thumbnails_dir / "thumbnail_prompts.md").write_text(prompts_md, encoding="utf-8")

    # Step 2 — render via Gemini (Vertex AI)
    print(f"\n[2/2] Generating images via {IMAGE_MODEL} (Vertex AI)...")
    try:
        from google import genai
        project = get_env("GOOGLE_CLOUD_PROJECT")
        client = genai.Client(vertexai=True, project=project, location="global")
        print(f"  Project  : {project}")
        print(f"  Model    : {IMAGE_MODEL}")
    except Exception as exc:
        print(f"\nError: Failed to initialise Vertex AI — {exc}")
        print("Make sure you have authenticated: gcloud auth application-default login")
        sys.exit(1)

    # Build the work list: (prompt_index_1based, variation_number, prompt_text)
    work: list[tuple[int, int, str]] = []
    for i, prompt in enumerate(prompts, 1):
        if indices_filter and i not in indices_filter:
            continue
        for v in range(1, count + 1):
            work.append((i, v, prompt))

    total = len(work)
    success_count = 0
    for job_num, (i, v, prompt) in enumerate(work, 1):
        if count > 1:
            out_path = thumbnails_dir / f"thumbnail_{i:02d}_v{v}.png"
        else:
            out_path = thumbnails_dir / f"thumbnail_{i:02d}.png"
        ok = _generate_image(client, prompt, out_path, job_num, total, apply_grain)
        if ok:
            success_count += 1
        if job_num < total:
            print(f"  Waiting {REQUEST_DELAY}s before next request...")
            time.sleep(REQUEST_DELAY)

    print(f"\nDone. {success_count}/{total} thumbnails saved to outputs/videos_pl/{slug}/{out_folder}/")


if __name__ == "__main__":
    main()
