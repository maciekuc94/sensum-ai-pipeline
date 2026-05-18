"""
Agent 9: Image Generation
Reads the final script produced by Agent 4, extracts all [IMAGE: ...] markers,
expands them into full image prompts, and (optionally) generates the
images via Gemini 3 Pro Image Preview on Vertex AI (location=global).

Two-phase workflow:
  Phase 1 — Extract prompts (run first, then review 05_image_prompts.md):
      python tools/agent9_images.py "slug"

  Phase 2 — Generate images (run after reviewing/editing prompts):
      python tools/agent9_images.py "slug" --generate
"""

import argparse
import re
import sys
import os
import time
import json
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import read_output, write_output, get_output_dir, get_env, export_to_docx, CHARACTER_DESCRIPTION, STYLE_SUFFIX

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


def _extract_topic_from_script(script_content: str) -> str:
    """Extract the topic from the first heading of the final script file."""
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Final:"):
            return line[len("# Script Final:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _extract_image_markers(script_content: str) -> list[str]:
    """Return all [IMAGE: description] descriptions found in the script."""
    return re.findall(r'\[IMAGE:\s*([^\]]+)\]', script_content)


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


def _clean_script_for_sentences(script_content: str) -> str:
    """Strip non-narration content (markers, headers, metadata) from the script."""
    text = script_content
    text = re.sub(r'\[IMAGE:[^\]]+\]', '', text)
    text = re.sub(r'\[EDITOR NOTE:[^\]]+\]', '', text)
    text = re.sub(r'^#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^(Generated:|Model:|Estimated duration:|Editor notes).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _extract_script_image_pairs(script_content: str) -> list[dict]:
    """Split script by [IMAGE: ...] markers, return (script_visual, sentence) pairs."""
    sections = re.split(r'\[IMAGE:\s*([^\]]+)\]', script_content)
    # sections = [pre_text, marker1, text_after_1, marker2, text_after_2, ...]
    if len(sections) < 3:
        return []

    pairs = []
    for i in range(1, len(sections) - 1, 2):
        script_visual = sections[i].strip()
        following = sections[i + 1]
        following = re.sub(r'\[EDITOR NOTE:[^\]]+\]', '', following)
        following = re.sub(r'^#.*$', '', following, flags=re.MULTILINE)
        following = re.sub(r'^---.*$', '', following, flags=re.MULTILINE)
        following = re.sub(r'^(Generated:|Model:|Estimated duration:).*$', '', following, flags=re.MULTILINE)
        following = following.strip()
        sentences = re.split(r'(?<=[.!?])\s+', following)
        sentence_group = ' '.join(s.strip() for s in sentences[:3] if s.strip())
        if sentence_group and script_visual:
            pairs.append({"script_visual": script_visual, "sentence": sentence_group})

    return pairs


HAIKU_MODEL = "claude-haiku-4-5-20251001"
HAIKU_MAX_TOKENS = 8192


def _call_claude_for_json(
    client,
    system: str,
    batches: list[str],
    *,
    temperature: float | None = None,
    label: str = "Calling Haiku",
) -> tuple[list[dict], dict]:
    """Run a Claude Haiku call per batch, strip JSON fencing, return concatenated items + usage."""
    all_items: list[dict] = []
    total_usage = {"model": HAIKU_MODEL, "input_tokens": 0, "output_tokens": 0}

    for i, batch in enumerate(batches, start=1):
        print(f"  {label} batch {i}/{len(batches)}...")
        kwargs: dict = dict(
            model=HAIKU_MODEL,
            max_tokens=HAIKU_MAX_TOKENS,
            system=system,
            messages=[{"role": "user", "content": batch}],
        )
        if temperature is not None:
            kwargs["temperature"] = temperature
        message = client.messages.create(**kwargs)

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = re.sub(r'^```[a-z]*\n?', '', raw)
            raw = re.sub(r'\n?```$', '', raw)

        all_items.extend(json.loads(raw))
        total_usage["input_tokens"] += message.usage.input_tokens
        total_usage["output_tokens"] += message.usage.output_tokens

    return all_items, total_usage


def _enhance_script_visuals(pairs: list[dict]) -> tuple[list[dict], dict]:
    """Use Haiku to refine script-embedded [IMAGE: ...] descriptions into production-ready visuals."""
    import anthropic

    system = (
        "You are a visual director writing image descriptions for a YouTube psychology video rendered in 19th-century scientific etching style.\n\n"
        "For each JSON entry you receive, you will see:\n"
        "- 'script_visual': the scriptwriter's image description (your primary source)\n"
        "- 'sentence': the narration text this image illustrates\n\n"
        "YOUR TASK: produce a refined 'visual' description that:\n"
        "1. Preserves the scene setting and action from 'script_visual' — keep what is specific\n"
        "2. Expands it to 40-60 words with concrete props, spatial positioning, and body language\n"
        "3. Shows emotion through POSTURE ONLY — no facial expressions, no faces\n"
        "4. Uses 'sentence' as context to understand the emotional beat — then find an unexpected, vivid way to show it\n\n"
        "BE INVENTIVE with composition — vary these across the set:\n"
        "- Close-up: just hands holding an object, two hands in different gestures, a detail of posture\n"
        "- Overhead: figure viewed from directly above, small in a large empty floor\n"
        "- Wide: figure tiny against a large object or architectural element (doorway, wall, staircase)\n"
        "- Two-figure contrast: left/right split showing before vs after, alone vs connected, trapped vs free\n"
        "- Sequential: one figure shown twice in the same frame at different moments (ghost posture, faded duplicate)\n"
        "- Object-forward: the prop dominates the frame, figure interacts with it from the side\n\n"
        "FORBIDDEN — remove or replace:\n"
        "- 'glowing' / 'illuminated' / 'lit' → describe the object without light effect (e.g. 'phone screen', 'laptop')\n"
        "- 'scribbles', 'tangled lines', 'jagged marks' floating around a figure → remove entirely\n"
        "- 'dim', 'dark', 'shadowed' environment → remove; background is always clean white\n"
        "- Any readable text, labels, numbers, or digits on objects\n\n"
        "GOOD EXAMPLES (match this level of specificity):\n"
        "- 'Faceless figure perched on the edge of a bed, one hand resting limp on a face-down phone on the mattress, spine bowed forward, shoulders drawn inward'\n"
        "- 'Overhead view: faceless figure lying flat on a bare floor, arms spread slightly outward, seen from directly above, surrounded by empty space'\n"
        "- 'Two faceless figures side by side — left one stands with shoulders collapsed, right one stands upright with arms open; wide gap between them'\n"
        "- 'Close-up of two hands: one hand open and releasing a small rectangular shape, the other hand empty and open below it'\n"
        "- 'Faceless figure dwarfed beside a tall doorframe, one hand on the frame edge, entire body small against the architectural scale'\n\n"
        "Return a JSON array with no markdown fencing:\n"
        '[{"sentence": "exact sentence from input", "visual": "refined scene description"}, ...]'
    )

    mid = len(pairs) // 2
    batches = [
        json.dumps(pairs[:mid], ensure_ascii=False, indent=2),
        json.dumps(pairs[mid:], ensure_ascii=False, indent=2),
    ]

    client = anthropic.Anthropic(api_key=get_env("ANTHROPIC_API_KEY"))
    return _call_claude_for_json(client, system, batches, temperature=1, label="Enhancing prompts")


def _generate_literal_prompts(script_content: str) -> tuple[list[dict], dict]:
    """Call Claude Haiku in batches to produce one literal visual description per sentence."""
    import anthropic

    clean_text = _clean_script_for_sentences(script_content)

    system = (
        "You are generating image descriptions for a YouTube psychology video. "
        "Your single job: convert each sentence into a LITERAL, DRAWABLE visual scene.\n\n"
        "TRANSLATION RULES — most important:\n"
        "- If the script names specific people, objects, or places — show them exactly: "
        "'woman with a sourdough kitchen' → faceless figure standing at a kitchen counter with a rustic sourdough loaf; "
        "'guy announcing his startup' → faceless figure standing before a small group, arms open, a building silhouette behind him\n"
        "- If the script describes an action — show the action: "
        "'you scrolled past her post' → a hand holding a phone, thumb mid-swipe across the screen\n"
        "- If the script states a psychological concept — find its most concrete physical form: "
        "'nervous system perceives a threat' → character standing rigid, shoulders drawn up, weight shifted back\n"
        "- Abstract metaphors are your cue to go concrete: "
        "'you carry that weight' → character hunched forward, a heavy dark shape pressing down on their upper back\n\n"
        "CHARACTER RULES:\n"
        "- Every person in the scene is FACELESS: smooth blank oval head, NO eyes, nose, mouth, ears, or hair\n"
        "- NEVER describe facial expressions — convey ALL emotion through posture only\n"
        "- NEVER describe readable text, numbers, or digits on any object (a clock is 'a clock', not '2:00 AM')\n"
        "- NEVER describe darkness, dim lighting, glowing light sources, or shadows — "
        "background is always clean flat white\n\n"
        "GROUPING RULES:\n"
        "- Group 2–3 consecutive sentences ONLY when they show the IDENTICAL visual scene\n"
        "- A new location, object, or action = a new entry\n"
        "- Every sentence must be covered by exactly one entry\n\n"
        "Return a JSON array with no markdown fencing:\n"
        '[{"sentence": "exact sentence(s) from script", "visual": "one concrete drawable scene, max 20 words"}, ...]'
    )

    # Split into two halves to stay within Haiku's 8192 output token limit
    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    mid = len(paragraphs) // 2
    batches = [
        "\n\n".join(paragraphs[:mid]),
        "\n\n".join(paragraphs[mid:]),
    ]

    client = anthropic.Anthropic(api_key=get_env("ANTHROPIC_API_KEY"))
    return _call_claude_for_json(client, system, batches, label="Generating prompts")


def _build_imagen_prompt(description: str) -> str:
    # If the marker still uses the old structured format, extract only the scene= content
    scene_match = re.search(r'scene=(.+)', description, re.DOTALL)
    scene = scene_match.group(1).strip() if scene_match else description.strip()
    return CHARACTER_DESCRIPTION + ". " + scene + ", " + STYLE_SUFFIX


def _build_prompts_file(topic: str, items: list[dict]) -> str:
    """Build the 05_image_prompts.md content from a list of {sentence, visual} dicts."""
    today = date.today().isoformat()
    count = len(items)

    lines = [
        f"# Image Prompts: {topic}",
        f"Generated: {today}",
        f"Source: {SCRIPT_FILENAME}",
        f"Total images: {count}",
        "",
        "Review and edit these prompts before generating. "
        "Each prompt feeds directly into Vertex AI Imagen.",
        "",
        "---",
    ]

    for i, item in enumerate(items, start=1):
        imagen_prompt = _build_imagen_prompt(item["visual"])
        lines += [
            "",
            f"## Image {i:03d}",
            f'**Sentence:** "{item["sentence"].strip()}"',
            "**Imagen prompt:**",
            imagen_prompt,
            "",
            "---",
        ]

    return "\n".join(lines) + "\n"


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
    """Phase 1 (legacy): check that 05_image_prompts.md was produced by Agent 5."""
    print(f"\n=== Agent 9: Image Generation — Phase 1 Check ===")
    print(f"Slug : {slug}")
    print()
    print("Agent 5 now writes 05_image_prompts.md directly.")
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
