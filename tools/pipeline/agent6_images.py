"""
Agent 6: Image Generation

Reads `md/05_image_prompts.md` produced by Agent 5 (which is the source of
truth for image prompts in the current pipeline) and renders each prompt to
a PNG via Gemini 3 Pro Image Preview on Vertex AI (location=global).

Two-phase workflow:
  Phase 1 — Verify prompts file exists (Agent 5 must have run first):
      python tools/pipeline/agent6_images.py "slug"

  Phase 2 — Generate images:
      python tools/pipeline/agent6_images.py "slug" --generate

Auxiliary modes:
  --correct-bg    Replace near-white pixels with #F4E5CA in existing images.
  --apply-grain N Apply film grain at intensity N to existing images.
  --sync-scripts  Insert [IMAGE_NNN] cue markers into 04_final.md
                  aligned with the rows in 05_image_prompts.md.
  --transparent   Generate on white background; output RGBA PNGs with
                  transparent background to images_transparent/. Compatible
                  with --indices. Never overwrites images/.
"""

import argparse
import re
import subprocess
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import (
    read_output, write_output, get_output_dir, get_env,
    add_grain, resize_to_target, enforce_background_color, make_transparent,
    flatten_background, two_color,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/04_final.md"
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
# v8 render recipe — "professionalism + rozmach" (tuned flash, 2026-06-08)
# Master-engraving CRAFT + figure discipline + flat-bg + strengthened negative
# are applied to EVERY render below (universal quality uplift, validated on
# slug 3 v8 A/B). GRANDEUR / dramatic scale is deployed per-beat by Agent 5
# (workflows/pipeline/05_visuals.md), NOT blanket-stamped here — so intimate
# openings stay intimate. Revert: restore IMAGE_MODEL + remove this block.
# ---------------------------------------------------------------------------

V8_BG_RULE = (
    "BACKGROUND RULE (absolute, highest priority): the entire background — every pixel that is "
    "not part of the figure or the staged props — is ONE flat solid sage beige (#F4E5CA), "
    "completely empty and uniform: no grey, no toned panel, no backdrop, no shadow field, no "
    "halo, no vignette, no square inner panel, no album-cover framing. "
)

V8_FIGURE_RULE = (
    "FIGURE RULE (highest priority): any human figure is a smooth, seamless, sexless, fully "
    "androgynous featureless mannequin — ONE continuous smooth surface like a blank dress-form, "
    "with NO visible joints, NO ball-and-socket segments, NO wooden panel seams. The figure has NO "
    "gender: shoulders and hips the SAME width, the chest a single smooth FLAT plane like a plain "
    "tailor's dress-form — no breasts, no cleavage, no pectoral curve, no nipples, no areola; straight "
    "waist, no hourglass, no feminine curve. Wherever skin is bare, render it as a smooth blank surface "
    "— no navel, no collarbones, no shoulder blades, no spine line, no abdominal or rib lines — just a "
    "clean contour with cross-hatch shading for volume. Absolutely no face. If the scene implies a "
    "clothed person, draw simple plain clothing. If the scene is a STILL LIFE with no figure (objects "
    "or an environment only), draw ONLY those objects with NO human figure, no mannequin, no hand and "
    "no body anywhere in the frame. "
)

V8_MASTER_RENDERING = (
    " RENDERING — museum-grade master engraving: render with the craftsmanship of a 19th-century "
    "master engraving plate, the calibre of a Gustave Dore or Albrecht Durer engraving. Full rich "
    "tonal range achieved purely through engraver's craft — deep, dense, velvety shadows built from "
    "tightly layered cross-hatching and burin lines that wrap and follow the form, luminous clean "
    "highlights, finely graded mid-tones; directional light that models every surface as sculptural and "
    "volumetric. Intricate, controlled, confident linework with refined detail in materials, fabric "
    "folds and props — the precision of a published plate, richly worked yet never cluttered. Bold dark "
    "#582F0E espresso-brown ink, strong and decisive, NEVER faint or pale. Deep shadows are always DENSE "
    "HATCHING, never a flat solid black silhouette fill. "
)

V8_NEGATIVE = (
    "\n\nAvoid in this image: face, eyes, nose, mouth, facial features; "
    "nipples, areola, breasts, breast swell, cleavage, chest or pectoral definition, "
    "navel, belly button, genitals, pubic area, visible musculature, muscle tone, six-pack abs, "
    "defined abdomen, rib lines, collarbones, shoulder blades, spine furrow; "
    "hourglass figure, feminine curves, wide hips, narrow tapered waist, curvy silhouette; "
    "ecorche, anatomical study, medical anatomy chart, realistic skin detail; "
    "wooden ball joints, visible body joints, segmented manikin limbs, panel seams, articulated doll joints; "
    "faint lines, pale washed-out linework, thin light-grey lines, low-contrast faded sketch, under-inked; "
    "flat even dull lighting, uniform monotonous line weight, amateur flat shading; "
    "busy cluttered overcrowded cramped composition, messy tangled scribble; "
    "solid black silhouette fill, flat black shape; "
    "front-view standing anatomy chart pose, gridded anatomy study; "
    "photorealistic, photograph, 3D render; "
    "any background other than one flat solid sage beige (#F4E5CA) — no paper texture, no mottling, "
    "no parchment, no vellum, no grain, no green tint, no grey tint, no shading in the background, "
    "no grey or toned backdrop, no shaded halo or vignette behind the figure; "
    "decorative border, frame, inner panel or rectangle around the image; "
    "cropped head, head out of frame, head touching top edge."
)

# Transparent mode (overlays) renders on white, so the sage-bg rules don't apply.
NEGATIVE_TRANSPARENT = (
    "\n\nAvoid in this image: face, facial features, photorealistic face, 3D render, "
    "nipples, breasts, cleavage, navel, visible musculature, anatomical study; "
    "faint pale washed-out linework; solid black silhouette fill; "
    "cropped head, head out of frame, paper texture, decorative border, frame, inner panel."
)


def _generate_image_with_retry(client, genai_types, model, full_prompt, max_retries=4, image_config=None):
    """Call Vertex image generation with 429 backoff; return raw image bytes.

    image_config (genai_types.ImageConfig) is optional: flash body images pass
    None (default resolution); agent7 thumbnails pass a 4K 16:9 ImageConfig to
    render the premium 3-pro asset at native 4K. None leaves behavior unchanged.
    """
    delay = 30
    for attempt in range(max_retries + 1):
        try:
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=genai_types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=image_config,
                ),
            )
            candidates = response.candidates or []
            if not candidates or not candidates[0].content or not candidates[0].content.parts:
                raise ValueError("Empty response (possible safety filter)")
            for part in candidates[0].content.parts:
                if hasattr(part, "inline_data") and part.inline_data:
                    return part.inline_data.data
            raise ValueError("No image in response")
        except Exception as exc:
            msg = str(exc)
            if ("429" in msg or "RESOURCE_EXHAUSTED" in msg) and attempt < max_retries:
                print(f"    429 — backoff {delay}s (retry {attempt + 1}/{max_retries})")
                time.sleep(delay)
                delay = min(delay * 2, 120)
                continue
            raise

# ---------------------------------------------------------------------------
# Auto-QA helper
# ---------------------------------------------------------------------------


def _run_auto_qa(slug: str) -> None:
    """Spawn Agent 6b --retry after image generation."""
    script = Path(__file__).parent / "agent6b_image_qa.py"
    cmd = [sys.executable, str(script), slug, "--retry"]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    print(f"\n=== Auto QA — running Agent 6b --retry ===")
    subprocess.run(cmd, check=False, env=env)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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
    print(f"\n=== Agent 6: Image Generation — Phase 1 Check ===")
    print(f"Slug : {slug}")
    print()
    print("Agent 5 writes 05_image_prompts.md directly.")
    print("Run Agent 5 if you have not already:")
    print(f'  python tools/pipeline/agent5_visuals.py "{slug}"')
    print()

    # Verify the prompts file already exists
    try:
        content = read_output(slug, PROMPTS_FILENAME)
        prompts = _parse_prompts_from_file(content)
        print(f"  Found existing {PROMPTS_FILENAME} with {len(prompts)} prompt(s).")
        print(f"\nReview and edit {PROMPTS_FILENAME}, then generate images:")
        print(f'  python tools/pipeline/agent6_images.py "{slug}" --generate')
    except FileNotFoundError:
        print(f"  {PROMPTS_FILENAME} not found. Run Agent 5 first:")
        print(f'  python tools/pipeline/agent5_visuals.py "{slug}"')
        sys.exit(1)


# ---------------------------------------------------------------------------
# Phase 2 — Generate images
# ---------------------------------------------------------------------------


def generate_images(
    slug: str,
    limit: int | None = None,
    start: int = 1,
    grain: int = 0,
    indices: list[int] | None = None,
    transparent: bool = False,
) -> None:
    """Phase 2: read approved prompts and call Vertex AI Imagen for each.

    If `indices` is supplied (1-based list), only those exact prompts are
    rendered and `start`/`limit` are ignored. Used for selective re-rendering
    of specific bad images without touching the rest of the set.

    If `transparent` is True, generates on white background and outputs RGBA
    PNGs with transparent background to images_transparent/. Does not touch
    images/. Grain is skipped in transparent mode.
    """
    print(f"\n=== Agent 6: Image Generation — Phase 2 (Generate Images) ===")
    print(f"Slug : {slug}")
    if transparent:
        print(f"Mode : transparent (white bg → RGBA alpha → images_transparent/)")
    if indices:
        print(f"Indices: {indices}")
    else:
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
        print(f'  python tools/pipeline/agent6_images.py "{slug}"')
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

    # Build a list of (image_num, prompt_text) pairs honoring either --indices
    # or --start/--limit (mutually exclusive in practice; indices wins).
    if indices:
        bad = [i for i in indices if i < 1 or i > len(prompts)]
        if bad:
            print(f"\nError: --indices contains values outside 1..{len(prompts)}: {bad}")
            sys.exit(1)
        prompt_jobs: list[tuple[int, str]] = [(i, prompts[i - 1]) for i in indices]
    else:
        if start > len(prompts):
            print(f"\nError: --start={start} exceeds {len(prompts)} parsed prompt(s).")
            sys.exit(1)
        selected = prompts[start - 1:]
        if limit:
            selected = selected[:limit]
        prompt_jobs = [(start + i, p) for i, p in enumerate(selected)]
    print(f"  Loaded {len(prompt_jobs)} prompt(s)")

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

    IMAGE_MODEL = "gemini-2.5-flash-image"  # v8 (2026-06-08): tuned flash; was gemini-3-pro-image-preview
    print(f"  Project  : {project}")
    print(f"  Location : {location}")
    print(f"  Model    : {IMAGE_MODEL}")

    # Step 3 — Generate images
    print(f"\n[3/3] Generating {len(prompt_jobs)} image(s)...")
    output_dir = get_output_dir(slug)
    images_dir = output_dir / ("images_transparent" if transparent else "images")
    images_dir.mkdir(parents=True, exist_ok=True)

    total = len(prompt_jobs)
    success = 0
    REQUEST_DELAY = 20  # seconds between requests to stay under QPM quota

    # v8 recipe (V8_BG_RULE / V8_FIGURE_RULE / V8_MASTER_RENDERING / V8_NEGATIVE)
    # is applied below from the module-level constants.

    WHITE_BG_OVERRIDE = (
        " BACKGROUND: flat solid pure white background (#FFFFFF), no texture, no grain. "
        "Do not use sage beige, cream, or any warm-toned background."
    )

    # When --indices is supplied, the user wants those exact images regenerated;
    # don't skip existing files in that mode.
    overwrite_existing = bool(indices)

    for seq, (image_num, prompt_text) in enumerate(prompt_jobs, start=1):
        filename = f"image_{image_num:03d}.png"
        output_path = images_dir / filename

        if output_path.exists() and not overwrite_existing:
            print(f"  [{seq}/{total}] Skipping {filename} (already exists)")
            success += 1
            continue

        print(f"  [{seq}/{total}] Generating {filename}...")

        try:
            if transparent:
                full_prompt = (
                    V8_FIGURE_RULE + prompt_text + WHITE_BG_OVERRIDE
                    + V8_MASTER_RENDERING + NEGATIVE_TRANSPARENT
                )
            else:
                full_prompt = (
                    V8_BG_RULE + V8_FIGURE_RULE + prompt_text
                    + V8_MASTER_RENDERING + V8_NEGATIVE
                )
            img_bytes = _generate_image_with_retry(client, genai_types, IMAGE_MODEL, full_prompt)

            with open(str(output_path), "wb") as f:
                f.write(img_bytes)
            if transparent:
                resize_to_target(output_path, background=(255, 255, 255))
                make_transparent(output_path)
                print(f"  Grain skipped (transparent mode)")
            else:
                resize_to_target(output_path)
                two_color(output_path)                      # hard 2-colour brand pass — replaces enforce+flatten
                if grain > 0:
                    add_grain(output_path, intensity=grain)
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
    print(f"\n=== Agent 6: Film Grain Pass ===")
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
        add_grain(dst_path, intensity=intensity)
        print(f"  [{i}/{len(png_files)}] {src_path.name} -> {dst_path}")

    print(f"\nDone. {len(png_files)} image(s) with grain saved to {grain_dir}")


# ---------------------------------------------------------------------------
# Background correction pass
# ---------------------------------------------------------------------------


def correct_background(slug: str) -> None:
    """Copy images/ to images_corrected/, applying background color correction to each."""
    import shutil
    print(f"\n=== Agent 6: Background Color Correction ===")
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
        enforce_background_color(dst_path)
        print(f"    Saved: {dst_path}")

    print(f"\nDone. {total} corrected image(s) saved to {corrected_dir}")


# ---------------------------------------------------------------------------
# Background flatten pass — kill model bg texture in place (no re-render)
# ---------------------------------------------------------------------------


def flatten_background_pass(slug: str, indices: list[int] | None = None) -> None:
    """Flatten model background texture to flat sage in images/, IN PLACE.

    Deterministic post-process (see utils.flatten_background): keeps the drawn
    subject, collapses the textured *empty* background to exact #F4E5CA. Safe to
    re-run (idempotent). Texture ON the subject is preserved by design — that
    needs a re-render (Agent 6b QA flags it as a real failure).
    """
    print(f"\n=== Agent 6: Background Flatten Pass (in place) ===")
    output_dir = get_output_dir(slug)
    images_dir = output_dir / "images"
    png_files = sorted(images_dir.glob("image_*.png"))
    if not png_files:
        print(f"No images found in {images_dir}")
        return
    if indices:
        wanted = {f"image_{i:03d}.png" for i in indices}
        png_files = [p for p in png_files if p.name in wanted]
        if not png_files:
            print(f"No images matched --indices {sorted(indices)} in {images_dir}")
            return
    total = len(png_files)
    print(f"  Images dir: {images_dir}")
    print(f"  Images    : {total}")
    print()
    for i, src_path in enumerate(png_files, start=1):
        flatten_background(src_path)
        print(f"  [{i}/{total}] flattened {src_path.name}")
    print(f"\nDone. {total} image(s) flattened in place.")


def two_color_pass(slug: str, indices: list[int] | None = None, *, in_place: bool = False) -> None:
    """Hard two-colour brand pass over every body image (see utils.two_color).

    Snaps each pixel to the nearer of {#582F0E ink, #F4E5CA sage}, collapsing
    every off-brand cast (greenish/grey muck inside objects, residual background
    texture) onto the two brand anchors in one deterministic step. Form is
    untouched — only colour. Cross-hatching survives (dark -> ink, gaps -> paper)
    so the result reads as a clean engraving. Grain is NOT applied (added later
    in DaVinci).

    Non-destructive by default: writes the quantized copies to images_post/ for
    review, leaving images/ intact. Pass in_place=True to overwrite images/.
    Honors --indices.
    """
    label = "in place" if in_place else "-> images_post/"
    print(f"\n=== Agent 6: Two-Colour Brand Pass ({label}) ===")
    output_dir = get_output_dir(slug)
    images_dir = output_dir / "images"
    png_files = sorted(images_dir.glob("image_*.png"))
    if not png_files:
        print(f"No images found in {images_dir}")
        return
    if indices:
        wanted = {f"image_{i:03d}.png" for i in indices}
        png_files = [p for p in png_files if p.name in wanted]
        if not png_files:
            print(f"No images matched --indices {sorted(indices)} in {images_dir}")
            return
    dest_dir = images_dir if in_place else (output_dir / "images_post")
    if not in_place:
        dest_dir.mkdir(parents=True, exist_ok=True)
    total = len(png_files)
    print(f"  Source : {images_dir}")
    print(f"  Dest   : {dest_dir}")
    print(f"  Images : {total}")
    print()
    for i, src_path in enumerate(png_files, start=1):
        two_color(src_path, output_path=dest_dir / src_path.name)
        print(f"  [{i}/{total}] two-colour {src_path.name}")
    print(f"\nDone. {total} image(s) written to {dest_dir}.")


# ---------------------------------------------------------------------------
# Script sync — align [IMAGE_NNN] markers with 05_image_prompts.md
# ---------------------------------------------------------------------------


def sync_scripts(slug: str) -> None:
    """
    Update script files so image markers match 05_image_prompts.md.

    04_final.md: strips old [IMAGE: ...] markers, inserts [IMAGE_NNN]
    before the sentence each image maps to.
    """
    print(f"\n=== Agent 6: Sync Scripts with Image Pipeline ===")
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
        final_content = read_output(slug, "md/04_final.md")
    except FileNotFoundError:
        print("Error: md/04_final.md not found.")
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

    write_output(slug, "md/04_final.md", cleaned)
    print(f"  md/04_final.md: stripped old markers, inserted {inserted}/{len(image_sentences)} [IMAGE_NNN] markers")

    print(f"\nDone. Scripts are now consistent with 05_image_prompts.md.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agent 6: image prompt extraction and Imagen generation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python tools/pipeline/agent6_images.py \"emotional-dysregulation-in-adhd\"\n"
            "  python tools/pipeline/agent6_images.py \"emotional-dysregulation-in-adhd\" --generate\n"
            "  python tools/pipeline/agent6_images.py \"emotional-dysregulation-in-adhd\" --correct-bg\n"
            "  python tools/pipeline/agent6_images.py \"emotional-dysregulation-in-adhd\" --apply-grain 12\n"
        ),
    )
    parser.add_argument("slug", help="Output slug for outputs/<slug>/.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--generate", action="store_true",
                      help="Phase 2: generate images from 05_image_prompts.md.")
    mode.add_argument("--correct-bg", action="store_true",
                      help="Re-process existing images, masking near-white to #F4E5CA.")
    mode.add_argument("--flatten-bg", action="store_true",
                      help="Flatten model background texture to flat #F4E5CA in images/ "
                           "in place (no re-render). Honors --indices.")
    mode.add_argument("--two-color", action="store_true",
                      help="Hard two-colour brand pass: snap every pixel to the nearer of "
                           "#582F0E / #F4E5CA. Writes to images_post/ for review "
                           "(add --in-place to overwrite images/). Honors --indices.")
    mode.add_argument("--sync-scripts", action="store_true",
                      help="Align [IMAGE_NNN] markers in scripts with 05_image_prompts.md.")
    mode.add_argument("--apply-grain", type=int, metavar="N", default=0,
                      help="Apply film grain at intensity N to existing images.")

    parser.add_argument("--limit", type=int, default=None,
                        help="Limit number of prompts/images processed.")
    parser.add_argument("--start", type=int, default=1,
                        help="1-based index to start from (default: 1).")
    parser.add_argument("--indices", type=str, default=None,
                        help="Comma-separated 1-based indices to (re)generate. "
                             "Overrides --start/--limit; overwrites existing files. "
                             "Example: --indices \"22,26,35,97\"")
    parser.add_argument("--grain", type=int, default=0,
                        help="Apply grain at intensity N to freshly-generated images.")
    parser.add_argument("--skip-qa", action="store_true",
                        help="Skip the automatic Agent 6b QA run after generation.")
    parser.add_argument("--transparent", action="store_true",
                        help="Generate on white background; output RGBA PNGs with transparent "
                             "background to images_transparent/. Compatible with --indices. "
                             "Never overwrites images/.")
    parser.add_argument("--in-place", action="store_true",
                        help="With --two-color: overwrite images/ instead of writing images_post/.")

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    if args.correct_bg:
        correct_background(slug)
    elif args.flatten_bg:
        flat_indices: list[int] | None = None
        if args.indices:
            try:
                flat_indices = [int(x.strip()) for x in args.indices.split(",") if x.strip()]
            except ValueError:
                print(f"Error: --indices must be comma-separated integers, got: {args.indices!r}")
                sys.exit(1)
        flatten_background_pass(slug, indices=flat_indices)
    elif args.two_color:
        tc_indices: list[int] | None = None
        if args.indices:
            try:
                tc_indices = [int(x.strip()) for x in args.indices.split(",") if x.strip()]
            except ValueError:
                print(f"Error: --indices must be comma-separated integers, got: {args.indices!r}")
                sys.exit(1)
        two_color_pass(slug, indices=tc_indices, in_place=args.in_place)
    elif args.sync_scripts:
        sync_scripts(slug)
    elif args.apply_grain > 0:
        apply_grain_pass(slug, args.apply_grain, limit=args.limit, start=args.start)
    elif args.generate:
        indices_list: list[int] | None = None
        if args.indices:
            try:
                indices_list = [int(x.strip()) for x in args.indices.split(",") if x.strip()]
            except ValueError:
                print(f"Error: --indices must be comma-separated integers, got: {args.indices!r}")
                sys.exit(1)
            if not indices_list:
                print("Error: --indices was supplied but parsed to an empty list.")
                sys.exit(1)
        generate_images(
            slug,
            limit=args.limit,
            start=args.start,
            grain=args.grain,
            indices=indices_list,
            transparent=args.transparent,
        )
        if not args.transparent and not args.skip_qa and not indices_list:
            _run_auto_qa(slug)
    else:
        extract_and_save_prompts(slug)


if __name__ == "__main__":
    main()
