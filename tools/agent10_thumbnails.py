"""
Agent Thumbnails: Generate 5 thumbnail image candidates for a given output.

Two-step process:
  1. Claude Opus 4.7 generates 5 creative thumbnail concepts (full image prompts)
  2. Gemini 3 Pro Image Preview (Vertex AI) renders each one

Usage:
    PYTHONIOENCODING=utf-8 python tools/agent10_thumbnails.py <slug>
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import (
    read_output, get_output_dir, get_env,
    query_claude, STYLE_SUFFIX, CHARACTER_DESCRIPTION,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

IMAGE_MODEL = "gemini-3-pro-image-preview"
GRAIN_INTENSITY = 12  # project standard (Gaussian std dev on 0–255)
REQUEST_DELAY = 20    # seconds between Vertex AI calls to stay under QPM quota

TARGET_BACKGROUND = (244, 229, 202)  # #F4E5CA sage beige
TARGET_SIZE = (1920, 1080)

NEGATIVE_TEXT = (
    "\n\nAvoid in this image: face, eyes, nose, mouth, facial features, "
    "photorealistic face, 3D render, green/dark/colored background, "
    "cropped head, text, words, labels, numbers, captions."
)

# ---------------------------------------------------------------------------
# Post-processing (mirrors agent9_images.py)
# ---------------------------------------------------------------------------


def _resize_to_target(image_path: Path) -> None:
    """Scale to fit inside 1920×1080, pad remainder with sage beige — no cropping."""
    from PIL import Image, ImageOps
    img = Image.open(str(image_path)).convert("RGB")
    if img.size != TARGET_SIZE:
        img = ImageOps.pad(img, TARGET_SIZE, color=TARGET_BACKGROUND, centering=(0.5, 0.5))
        img.save(str(image_path))


def _enforce_background_color(image_path: Path) -> None:
    """Replace near-white pixels with exact brand background color (#F4E5CA)."""
    import numpy as np
    from PIL import Image
    arr = np.array(Image.open(str(image_path)).convert("RGB"))
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask] = TARGET_BACKGROUND
    Image.fromarray(arr).save(str(image_path))


def _add_grain(image_path: Path, intensity: int = GRAIN_INTENSITY) -> None:
    """Add film grain noise (Gaussian) for a vintage etching feel."""
    import numpy as np
    from PIL import Image
    arr = np.array(Image.open(str(image_path)).convert("RGB"), dtype=np.int16)
    noise = np.random.default_rng().normal(0, intensity, arr.shape).astype(np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(str(image_path))


# ---------------------------------------------------------------------------
# Step 1: Claude Opus 4.7 — thumbnail concept generation
# ---------------------------------------------------------------------------

COMPOSITION_TYPES = """\
1. Single figure in symbolic environment — the androgynous figure stands or sits inside a scene that metaphorically represents the emotional state (e.g., surrounded by many closed doors, inside a vast library of unlived lives, at the edge of a fog-filled mirror)
2. Symbolic still life — an arrangement of meaningful objects without a figure, or the figure interacts with one central object that carries the whole emotional weight (e.g., a jar full of folded notes, a set of clocks showing different times, a single empty chair at a long table)
3. Dual / ghost figure — two versions of the same androgynous figure in one frame: one solid and present, one faded, ghostly, or dissolving — representing the lived self beside the unlived self
4. Metaphorical interior space — the viewer looks into a conceptual space: a private cemetery of headstones shaped like life choices, a filing cabinet drawer open to reveal miniature frozen tableaux, a theatre stage with one spotlight on an empty chair
5. Anatomical / internal diagram — cross-section or schematic style (19th-century textbook anatomy plate) showing the psychological concept as internal architecture: the chest opened to reveal a smaller self curled inside, the brain mapped with labeled chambers for "who I became" vs "who I could have been" (labels as visual shapes only, no readable text)"""


def _generate_thumbnail_concepts(script_content: str, publish_content: str) -> list[str]:
    """Call Claude Opus 4.7 to generate 5 distinct thumbnail image prompts."""

    script_excerpt = script_content[:4000]
    publish_excerpt = publish_content[:2000]

    prompt = f"""You are a visual art director for a YouTube psychology channel rendered in 19th-century scientific etching style.

Your task: create 5 complete, production-ready image generation prompts for thumbnail candidates for the video below. Each prompt will be sent directly to an AI image model — write them as polished, self-contained directives.

---
VIDEO SCRIPT (excerpt):
{script_excerpt}

PUBLISH PACKAGE (titles and hooks):
{publish_excerpt}
---

CHARACTER STYLE — embed verbatim in every prompt that includes a figure:
{CHARACTER_DESCRIPTION}

IMAGE STYLE — append verbatim to every prompt:
{STYLE_SUFFIX}

---
REQUIREMENTS:
- Each of the 5 thumbnails must look visually DISTINCT — different composition, different metaphor, different emotional angle on the video's theme
- Each prompt must be ~400 words: open with the scene concept, then embed CHARACTER STYLE if a figure appears, then close with IMAGE STYLE
- No two thumbnails may share the same composition type

COMPOSITION TYPES — use one per thumbnail, in this order:
{COMPOSITION_TYPES}

---
OUTPUT FORMAT — output exactly the text below with your prompts filled in, nothing before or after:

---THUMBNAIL_1---
[full image generation prompt for composition type 1]

---THUMBNAIL_2---
[full image generation prompt for composition type 2]

---THUMBNAIL_3---
[full image generation prompt for composition type 3]

---THUMBNAIL_4---
[full image generation prompt for composition type 4]

---THUMBNAIL_5---
[full image generation prompt for composition type 5]"""

    text, usage = query_claude(
        prompt=prompt,
        model="claude-opus-4-7",
        max_tokens=8000,
        step_label="5 thumbnail concepts",
    )
    print(f"  Tokens — input: {usage['input_tokens']:,}, output: {usage['output_tokens']:,}")

    # Parse the 5 prompts
    parts = text.split("---THUMBNAIL_")
    prompts = []
    for part in parts[1:]:
        # Each part looks like: "1---\n[prompt text]\n"
        body = part.split("---", 1)[-1].strip()
        if body:
            prompts.append(body)

    if len(prompts) != 5:
        raise ValueError(
            f"Expected 5 thumbnail prompts from Claude, got {len(prompts)}.\n"
            f"Raw output (first 800 chars):\n{text[:800]}"
        )

    return prompts


# ---------------------------------------------------------------------------
# Step 2: Gemini — image generation + post-processing
# ---------------------------------------------------------------------------


def _load_saved_prompts(thumbnails_dir: Path) -> list[str]:
    """Parse prompts from an existing thumbnail_prompts.md file."""
    prompts_path = thumbnails_dir / "thumbnail_prompts.md"
    if not prompts_path.exists():
        raise FileNotFoundError(f"No saved prompts found at {prompts_path}")
    text = prompts_path.read_text(encoding="utf-8")
    sections = text.split("## Thumbnail ")
    prompts = []
    for section in sections[1:]:
        body = section.split("\n", 1)[-1]  # strip the "N\n" header line
        body = body.strip().rstrip("-").strip()
        if body:
            prompts.append(body)
    if not prompts:
        raise ValueError("Could not parse any prompts from thumbnail_prompts.md")
    return prompts


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
    _resize_to_target(output_path)
    _enforce_background_color(output_path)
    if apply_grain:
        _add_grain(output_path, intensity=GRAIN_INTENSITY)

    print(f"  Saved: {output_path.name}")
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if len(sys.argv) < 2:
        print("Usage: PYTHONIOENCODING=utf-8 python tools/agent10_thumbnails.py <slug> [--no-grain] [--reuse-prompts]")
        sys.exit(1)

    slug = sys.argv[1]
    raw_flags = sys.argv[2:]
    flags = set(raw_flags)
    apply_grain = "--no-grain" not in flags
    reuse_prompts = "--reuse-prompts" in flags

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

    print("=== Agent Thumbnails ===")
    print(f"Slug       : {slug}")
    print(f"Grain      : {'yes' if apply_grain else 'no'}")
    print(f"Prompts    : {'reuse saved' if reuse_prompts else 'generate new (Claude Opus 4.7)'}")
    if indices_filter:
        print(f"Indices    : {indices_filter}  x{count}")

    output_dir = get_output_dir(slug)
    # Use a separate output folder when grain is disabled so originals are preserved
    out_folder = "thumbnails" if apply_grain else "thumbnails_no_grain"
    thumbnails_dir = output_dir / out_folder
    thumbnails_dir.mkdir(parents=True, exist_ok=True)

    if reuse_prompts:
        # Load prompts saved by a previous run
        src_dir = output_dir / "thumbnails"
        print(f"\n[1/3] Loading saved prompts from thumbnails/thumbnail_prompts.md...")
        prompts = _load_saved_prompts(src_dir)
        print(f"  Loaded {len(prompts)} prompts.")
        # Copy prompts file into new folder for traceability
        prompts_md = "# Thumbnail Prompts\n\n"
        for i, p in enumerate(prompts, 1):
            prompts_md += f"## Thumbnail {i}\n\n{p}\n\n---\n\n"
        (thumbnails_dir / "thumbnail_prompts.md").write_text(prompts_md, encoding="utf-8")
    else:
        # Step 1 — Read script inputs
        print("\n[1/3] Reading input files...")
        script_content = read_output(slug, "md/04_script_final.md")
        publish_content = read_output(slug, "md/07_publish_package.md")
        print(f"  Script  : {len(script_content):,} chars")
        print(f"  Publish : {len(publish_content):,} chars")

        # Step 2 — Claude Opus 4.7 generates 5 thumbnail concepts
        print("\n[2/3] Claude Opus 4.7 — generating thumbnail concepts...")
        prompts = _generate_thumbnail_concepts(script_content, publish_content)
        print(f"  Got {len(prompts)} prompts.")

        # Save prompts for reference
        prompts_md = "# Thumbnail Prompts\n\n"
        for i, p in enumerate(prompts, 1):
            prompts_md += f"## Thumbnail {i}\n\n{p}\n\n---\n\n"
        (thumbnails_dir / "thumbnail_prompts.md").write_text(prompts_md, encoding="utf-8")
        print(f"  Prompts saved: {out_folder}/thumbnail_prompts.md")

    # Step 3 — Generate images via Gemini (Vertex AI)
    step = "2" if reuse_prompts else "3"
    print(f"\n[{step}/3] Generating images via {IMAGE_MODEL} (Vertex AI)...")
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

    print(f"\nDone. {success_count}/{total} thumbnails saved to outputs/{slug}/{out_folder}/")


if __name__ == "__main__":
    main()
