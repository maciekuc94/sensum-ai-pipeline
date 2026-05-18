"""
Agent 9: Image Generation

Reads `md/05_image_prompts.md` produced by Agent 5 (which is the source of
truth for image prompts in the current pipeline) and renders each prompt to
a PNG via Gemini 3 Pro Image Preview on Vertex AI (location=global).

Two-phase workflow:
  Phase 1 — Verify prompts file exists (Agent 5 must have run first):
      python tools/agent9_images.py "slug"

  Phase 2 — Generate images:
      python tools/agent9_images.py "slug" --generate

Auxiliary modes:
  --correct-bg    Replace near-white pixels with #F4E5CA in existing images.
  --apply-grain N Apply film grain at intensity N to existing images.
  --sync-scripts  Insert [IMAGE_NNN] cue markers into 04_script_final.md
                  aligned with the rows in 05_image_prompts.md.
"""

import argparse
import re
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import read_output, write_output, get_output_dir, get_env

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/04_script_final.md"
PROMPTS_FILENAME = "md/05_image_prompts.md"

# Passed as negative_prompt to suppress face generation and background color drift.
NEGATIVE_PROMPT = (
    "face, eyes, nose, mouth, smile, lips, eyebrows, chin, teeth, "
    "realistic face, facial features, detailed face, human face, portrait, "
    "photorealistic, photograph, 3D render, "
    "green background, sage green, olive green, teal background, "
    "dark background, black background, colored background, shadowed background, gradient background, "
    "cropped head, head cut off, head out of frame, top of head touching frame edge, no headroom, "
    "head clipped by upper edge, decapitated framing, headless torso shot"
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


# Exact sage beige background color from SENSUM palette
TARGET_BACKGROUND = (244, 229, 202)  # #F4E5CA
TARGET_SIZE = (1920, 1080)


def _resize_to_target(image_path) -> None:
    """Scale to fit inside 1920x1080, pad remainder with sage beige — no cropping, no stretching."""
    from PIL import Image, ImageOps
    img = Image.open(str(image_path)).convert("RGB")
    if img.size != TARGET_SIZE:
        img = ImageOps.pad(img, TARGET_SIZE, color=TARGET_BACKGROUND, centering=(0.5, 0.5))
        img.save(str(image_path))


def _enforce_background_color(image_path) -> None:
    """Replace near-white pixels with exact brand background color (#F4E5CA).

    Threshold of 248 (not 240) preserves light cross-hatch highlights that
    earlier flattened into the background.
    """
    import numpy as np
    from PIL import Image

    arr = np.array(Image.open(str(image_path)).convert("RGB"))
    mask = (arr[:, :, 0] > 248) & (arr[:, :, 1] > 248) & (arr[:, :, 2] > 248)
    arr[mask] = TARGET_BACKGROUND
    Image.fromarray(arr).save(str(image_path))


def _add_grain(image_path, intensity: int = 10) -> None:
    """Add film grain noise to image for a vintage etching feel."""
    import numpy as np
    from PIL import Image

    arr = np.array(Image.open(str(image_path)).convert("RGB"), dtype=np.int16)
    noise = np.random.default_rng().normal(0, intensity, arr.shape).astype(np.int16)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    Image.fromarray(arr).save(str(image_path))


def _parse_prompts_from_file(content: str) -> list[str]:
    """
    Parse the Imagen prompts from 05_image_prompts.md.

    Each prompt starts at the first non-empty line after a '**Imagen prompt:**'
    marker and continues until the next blank line or '---' boundary. Lines are
    joined with a space to handle multi-line prompts.
    """
    prompts = []
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if line.strip() == "**Imagen prompt:**":
            # Collect all non-empty lines until a blank line or '---' boundary
            collected = []
            for j in range(idx + 1, len(lines)):
                stripped = lines[j].strip()
                if stripped == "" or stripped == "---":
                    if collected:
                        break
                    # Skip leading blank lines before the first content line
                    continue
                collected.append(stripped)
            if collected:
                prompts.append(" ".join(collected))
    return prompts


# ---------------------------------------------------------------------------
# Phase 1 — Extract and save prompts
# ---------------------------------------------------------------------------


def extract_and_save_prompts(slug: str) -> None:
    """Phase 1: verify that 05_image_prompts.md was produced by Agent 5."""
    print(f"\n=== Agent 9: Image Generation — Phase 1 Check ===")
    print(f"Slug : {slug}")
    print()
    print("Agent 5 writes 05_image_prompts.md directly.")
    print("Run Agent 5 if you have not already:")
    print(f'  python tools/agent5_visuals.py "{slug}"')
    print()

    # Verify the prompts file already exists
    try:
        content = read_output(slug, PROMPTS_FILENAME)
        prompts = _parse_prompts_from_file(content)
        print(f"  Found existing {PROMPTS_FILENAME} with {len(prompts)} prompt(s).")
        print(f"\nReview and edit {PROMPTS_FILENAME}, then generate images:")
        print(f'  python tools/agent9_images.py "{slug}" --generate')
    except FileNotFoundError:
        print(f"  {PROMPTS_FILENAME} not found. Run Agent 5 first:")
        print(f'  python tools/agent5_visuals.py "{slug}"')
        sys.exit(1)


# ---------------------------------------------------------------------------
# Phase 2 — Generate images
# ---------------------------------------------------------------------------


def generate_images(slug: str, limit: int | None = None, start: int = 1, grain: int = 0) -> None:
    """Phase 2: read approved prompts and call Vertex AI Imagen for each."""
    print(f"\n=== Agent 9: Image Generation — Phase 2 (Generate Images) ===")
    print(f"Slug : {slug}")
    if start > 1:
        print(f"Start: image {start:03d}")
    if limit:
        print(f"Limit: {limit} images")
    print()

    # Step 1 — Read the prompts file
    print(f"[1/3] Reading {PROMPTS_FILENAME}...")
    try:
        prompts_content = read_output(slug, PROMPTS_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Phase 1 first:")
        print(f'  python tools/agent9_images.py "{slug}"')
        sys.exit(1)

    prompts = _parse_prompts_from_file(prompts_content)
    if not prompts:
        print(f"\nError: No Imagen prompts found in {PROMPTS_FILENAME}.")
        print("Make sure the file was generated by Phase 1 and has not been corrupted.")
        sys.exit(1)

    # Validate parsed count against the header's declared total
    header_match = re.search(r'^Total images:\s*(\d+)', prompts_content, re.MULTILINE)
    if header_match:
        expected = int(header_match.group(1))
        actual = len(prompts)
        if expected != actual:
            print(
                f"[WARNING] 05_image_prompts.md header says {expected} images but "
                f"{actual} prompt blocks were parsed.\n"
                f"         This may indicate a corrupted or partially-edited file.\n"
                f"         Proceeding with {actual} parsed prompts."
            )

    if start > len(prompts):
        print(f"\nError: --start={start} exceeds {len(prompts)} parsed prompt(s).")
        sys.exit(1)
    prompts = prompts[start - 1:]
    if limit:
        prompts = prompts[:limit]
    print(f"  Loaded {len(prompts)} prompt(s)")

    # Step 2 — Initialise Vertex AI
    print(f"\n[2/3] Initialising Vertex AI Imagen...")
    try:
        project = get_env("GOOGLE_CLOUD_PROJECT")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        print("\nSet GOOGLE_CLOUD_PROJECT in your .env file, e.g.:")
        print("  GOOGLE_CLOUD_PROJECT=my-gcp-project-id")
        sys.exit(1)

    # Gemini 3 Pro Image requires location="global"; regional endpoints return 404.
    location = "global"

    try:
        from google import genai
        from google.genai import types as genai_types

        client = genai.Client(vertexai=True, project=project, location=location)
    except Exception as exc:
        print(f"\nError: Failed to initialise Vertex AI — {exc}")
        print("\nMake sure you have authenticated:")
        print("  gcloud auth application-default login")
        sys.exit(1)

    IMAGE_MODEL = "gemini-3-pro-image-preview"
    print(f"  Project  : {project}")
    print(f"  Location : {location}")
    print(f"  Model    : {IMAGE_MODEL}")

    # Step 3 — Generate images
    print(f"\n[3/3] Generating {len(prompts)} image(s)...")
    output_dir = get_output_dir(slug)
    images_dir = output_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    total = len(prompts)
    success = 0
    REQUEST_DELAY = 20  # seconds between requests to stay under QPM quota

    NEGATIVE_TEXT = (
        "\n\nAvoid in this image: face, eyes, nose, mouth, facial features, "
        "photorealistic face, 3D render, green/dark/colored background, "
        "cropped head, head out of frame."
    )

    for seq, prompt_text in enumerate(prompts, start=1):
        image_num = start + seq - 1
        filename = f"image_{image_num:03d}.png"
        output_path = images_dir / filename

        if output_path.exists():
            print(f"  [{seq}/{total}] Skipping {filename} (already exists)")
            success += 1
            continue

        print(f"  [{seq}/{total}] Generating {filename}...")

        try:
            response = client.models.generate_content(
                model=IMAGE_MODEL,
                contents=prompt_text + NEGATIVE_TEXT,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                ),
            )
            candidates = response.candidates or []
            if not candidates or not candidates[0].content:
                raise ValueError("Empty response (possible safety filter)")
            img_bytes = None
            for part in candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    img_bytes = part.inline_data.data
                    break
            if not img_bytes:
                raise ValueError("No image in response")

            with open(str(output_path), "wb") as f:
                f.write(img_bytes)
            _resize_to_target(output_path)
            _enforce_background_color(output_path)
            if grain > 0:
                _add_grain(output_path, grain)
            print(f"  Saved: {output_path}")
            success += 1
        except Exception as exc:
            print(f"  Warning: Failed to generate {filename} — {exc}")

        if seq < total:
            print(f"  Waiting {REQUEST_DELAY}s (rate limit)...")
            time.sleep(REQUEST_DELAY)

    print(f"\nGenerated {success}/{total} images.")
    print(f"Images saved to: {images_dir}")




# ---------------------------------------------------------------------------
# Grain pass — apply film grain to existing images
# ---------------------------------------------------------------------------


def apply_grain_pass(slug: str, intensity: int, limit: int | None = None, start: int = 1) -> None:
    """Apply film grain to images already in images_corrected/ (or images/), saving to images_grain/."""
    import shutil
    print(f"\n=== Agent 9: Film Grain Pass ===")
    output_dir = get_output_dir(slug)
    corrected_dir = output_dir / "images_corrected"
    images_dir = corrected_dir if corrected_dir.exists() and any(corrected_dir.glob("*.png")) else output_dir / "images"
    grain_dir = output_dir / "images_grain"
    grain_dir.mkdir(parents=True, exist_ok=True)

    png_files = sorted(images_dir.glob("image_*.png"))
    if not png_files:
        print(f"No images found in {images_dir}")
        return

    if start > len(png_files):
        print(f"Error: --start={start} exceeds {len(png_files)} image(s) in {images_dir}.")
        sys.exit(1)
    png_files = png_files[start - 1:]
    if limit:
        png_files = png_files[:limit]

    print(f"  Source    : {images_dir}")
    print(f"  Output    : {grain_dir}")
    print(f"  Intensity : {intensity}")
    print(f"  Images    : {len(png_files)}")
    print()

    for i, src_path in enumerate(png_files, start=1):
        dst_path = grain_dir / src_path.name
        shutil.copy2(str(src_path), str(dst_path))
        _add_grain(dst_path, intensity)
        print(f"  [{i}/{len(png_files)}] {src_path.name} -> {dst_path}")

    print(f"\nDone. {len(png_files)} image(s) with grain saved to {grain_dir}")


# ---------------------------------------------------------------------------
# Background correction pass
# ---------------------------------------------------------------------------


def correct_background(slug: str) -> None:
    """Copy images/ to images_corrected/, applying background color correction to each."""
    import shutil
    print(f"\n=== Agent 9: Background Color Correction ===")
    output_dir = get_output_dir(slug)
    images_dir = output_dir / "images"
    corrected_dir = output_dir / "images_corrected"
    corrected_dir.mkdir(parents=True, exist_ok=True)

    png_files = sorted(images_dir.glob("image_*.png"))
    if not png_files:
        print(f"No images found in {images_dir}")
        return

    total = len(png_files)
    print(f"  Source    : {images_dir}")
    print(f"  Corrected : {corrected_dir}")
    print(f"  Images    : {total}")
    print()

    for i, src_path in enumerate(png_files, start=1):
        dst_path = corrected_dir / src_path.name
        print(f"  [{i}/{total}] Correcting {src_path.name}...")
        shutil.copy2(str(src_path), str(dst_path))
        _enforce_background_color(dst_path)
        print(f"    Saved: {dst_path}")

    print(f"\nDone. {total} corrected image(s) saved to {corrected_dir}")


# ---------------------------------------------------------------------------
# Script sync — align [IMAGE_NNN] markers with 05_image_prompts.md
# ---------------------------------------------------------------------------


def sync_scripts(slug: str) -> None:
    """
    Update script files so image markers match 05_image_prompts.md.

    04_script_final.md: strips old [IMAGE: ...] markers, inserts [IMAGE_NNN]
    before the sentence each image maps to.
    03_script_draft.md: strips old [IMAGE: ...] markers only.
    """
    print(f"\n=== Agent 9: Sync Scripts with Image Pipeline ===")
    print(f"Slug : {slug}")
    print()

    try:
        prompts_content = read_output(slug, PROMPTS_FILENAME)
    except FileNotFoundError:
        print("Error: 05_image_prompts.md not found. Run Phase 1 first.")
        sys.exit(1)

    # Parse (image_num, first_sentence) from 05_image_prompts.md
    image_sentences: list[tuple[int, str]] = []
    # Tolerate optional metadata lines (e.g., **Beat:** ...) between the image
    # header and the **Sentence:** line — Agent 5 may insert beat tags.
    for block in re.finditer(
        r'## Image (\d+)\n(?:\*\*[^*]+\*\*[^\n]*\n)*?\*\*Sentence:\*\* "(.+?)"',
        prompts_content,
        re.DOTALL,
    ):
        num = int(block.group(1))
        full_sentence = block.group(2).strip()
        first = re.split(r'(?<=[.!?])\s+', full_sentence)[0].strip()
        image_sentences.append((num, first))

    print(f"  Parsed {len(image_sentences)} image-sentence mappings")

    try:
        final_content = read_output(slug, "md/04_script_final.md")
    except FileNotFoundError:
        print("Error: md/04_script_final.md not found.")
        sys.exit(1)

    # Strip both old-style [IMAGE: ...] and any previously inserted [IMAGE_NNN] markers
    cleaned = re.sub(r'\[IMAGE:[^\]]+\]\s*\n?', '', final_content)
    cleaned = re.sub(r'\[IMAGE_\d+\] ?', '', cleaned)

    def _norm(s: str) -> str:
        # Normalize all quote variants to single straight quote for uniform matching
        return (s.replace("‘", chr(39)).replace("’", chr(39))
                .replace("“", chr(39)).replace("”", chr(39))
                .replace(chr(34), chr(39))
                .replace("…", "..."))
    # Normalize the script text once so all quote styles are consistent
    cleaned = _norm(cleaned)

    inserted = 0
    for num, first_sentence in image_sentences:
        marker = f"[IMAGE_{num:03d}]"
        norm_sentence = _norm(first_sentence)
        escaped = re.escape(norm_sentence)
        pattern = rf'({escaped})'
        new_cleaned, count = re.subn(pattern, rf'{marker} \1', cleaned, count=1)
        if not count and len(norm_sentence) > 40:
            # Fallback: match on first 50 chars (handles Haiku sentence truncation)
            prefix = re.escape(norm_sentence[:50])
            pattern = rf'({prefix})'
            new_cleaned, count = re.subn(pattern, rf'{marker} \1', cleaned, count=1)
        if count:
            cleaned = new_cleaned
            inserted += 1

    write_output(slug, "md/04_script_final.md", cleaned)
    print(f"  md/04_script_final.md: stripped old markers, inserted {inserted}/{len(image_sentences)} [IMAGE_NNN] markers")

    try:
        draft_content = read_output(slug, "md/03_script_draft.md")
        draft_cleaned = re.sub(r'\[IMAGE:[^\]]+\]\s*\n?', '', draft_content)
        write_output(slug, "md/03_script_draft.md", draft_cleaned)
        print(f"  md/03_script_draft.md: stripped old [IMAGE: ...] markers")
    except FileNotFoundError:
        print("  md/03_script_draft.md not found — skipping")

    print(f"\nDone. Scripts are now consistent with 05_image_prompts.md.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agent 9: image prompt extraction and Imagen generation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/agent9_images.py \"emotional-dysregulation-in-adhd\"\n"
            "  python tools/agent9_images.py \"emotional-dysregulation-in-adhd\" --generate\n"
            "  python tools/agent9_images.py \"emotional-dysregulation-in-adhd\" --correct-bg\n"
            "  python tools/agent9_images.py \"emotional-dysregulation-in-adhd\" --apply-grain 12\n"
        ),
    )
    parser.add_argument("slug", help="Output slug for outputs/<slug>/.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--generate", action="store_true",
                      help="Phase 2: generate images from 05_image_prompts.md.")
    mode.add_argument("--correct-bg", action="store_true",
                      help="Re-process existing images, masking near-white to #F4E5CA.")
    mode.add_argument("--sync-scripts", action="store_true",
                      help="Align [IMAGE_NNN] markers in scripts with 05_image_prompts.md.")
    mode.add_argument("--apply-grain", type=int, metavar="N", default=0,
                      help="Apply film grain at intensity N to existing images.")

    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of prompts/images processed.")
    parser.add_argument("--start", type=int, default=1,
                        help="1-based index to start from (default: 1).")
    parser.add_argument("--grain", type=int, default=0,
                        help="Apply grain at intensity N to freshly-generated images.")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    if args.correct_bg:
        correct_background(slug)
    elif args.sync_scripts:
        sync_scripts(slug)
    elif args.apply_grain > 0:
        apply_grain_pass(slug, args.apply_grain, limit=args.limit, start=args.start)
    elif args.generate:
        generate_images(slug, limit=args.limit, start=args.start, grain=args.grain)
    else:
        extract_and_save_prompts(slug)


if __name__ == "__main__":
    main()
