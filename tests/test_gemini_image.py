"""
Gemini image generation test — 5 images from the crying video.

Generates images 001-005 using a Gemini model and saves them to
  outputs/why-you-are-prone-to-crying-and-why-that-s-okay/images_gemini_test/

Compare against the Imagen 4 Ultra originals in the `images/` folder to
evaluate style adherence before committing to a migration.

Usage:
    python tools/test_gemini_image.py
    python tools/test_gemini_image.py --model gemini-2.5-flash-preview-0514

If the default model ID fails with 404, check Vertex AI Model Garden for
the correct ID and pass it with --model.
"""

import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import get_env, get_output_dir

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

SLUG = "why-you-are-prone-to-crying-and-why-that-s-okay"
PROMPTS_FILENAME = "md/06_image_prompts.md"
TEST_COUNT = 10
REQUEST_DELAY = 15  # seconds between requests

# Default model — update to whatever Vertex AI model you want to test.
# Candidates:
#   gemini-2.5-flash-image                 (Google's recommended Imagen 4 successor)
#   gemini-2.0-flash-preview-image-generation
#   imagen-3.0-generate-002
DEFAULT_MODEL = "gemini-3-pro-image-preview"

TARGET_BACKGROUND = (244, 229, 202)  # #F4E5CA sage beige
TARGET_SIZE = (1920, 1080)

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


def _parse_prompts(md_content: str, count: int) -> list[str]:
    """Extract the first `count` Imagen prompts from the markdown file."""
    prompts = re.findall(
        r'\*\*Imagen prompt:\*\*\n(.*?)(?=\n---|\Z)',
        md_content,
        re.DOTALL,
    )
    return [p.strip() for p in prompts[:count]]


def _resize_to_target(image_path: Path) -> None:
    """Scale to fit inside 1920x1080, pad remainder with sage beige (#F4E5CA).
    Preserves the full composition — no cropping, no stretching.
    The padding is invisible after _enforce_background_color converts white → beige."""
    from PIL import Image, ImageOps
    img = Image.open(str(image_path)).convert("RGB")
    if img.size != TARGET_SIZE:
        img = ImageOps.pad(img, TARGET_SIZE, color=TARGET_BACKGROUND, centering=(0.5, 0.5))
        img.save(str(image_path))


def _enforce_background_color(image_path: Path) -> None:
    import numpy as np
    from PIL import Image
    arr = np.array(Image.open(str(image_path)).convert("RGB"))
    mask = (arr[:, :, 0] > 240) & (arr[:, :, 1] > 240) & (arr[:, :, 2] > 240)
    arr[mask] = TARGET_BACKGROUND
    Image.fromarray(arr).save(str(image_path))


def _generate_with_generate_images(client, model: str, prompt: str) -> bytes:
    """Try Imagen-style generate_images() API."""
    from google.genai import types as genai_types
    response = client.models.generate_images(
        model=model,
        prompt=prompt,
        config=genai_types.GenerateImagesConfig(
            number_of_images=1,
            aspect_ratio="16:9",
            negative_prompt=NEGATIVE_PROMPT,
        ),
    )
    return response.generated_images[0].image.image_bytes


def _generate_with_generate_content(client, model: str, prompt: str) -> bytes:
    """Gemini-style generate_content() API with IMAGE modality."""
    from google.genai import types as genai_types
    negative_text = (
        "\n\nAvoid in this image: face, eyes, nose, mouth, facial features, "
        "photorealistic face, 3D render, green/dark/colored background, "
        "cropped head, head out of frame."
    )
    # GenerateContentConfig doesn't support image_generation_config (not in schema).
    # Aspect ratio is handled post-generation via center-crop in _resize_to_target.
    response = client.models.generate_content(
        model=model,
        contents=prompt + negative_text,
        config=genai_types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )
    candidates = response.candidates or []
    if not candidates or not candidates[0].content:
        raise ValueError("Empty response from model (possible safety filter)")
    for part in candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            return part.inline_data.data
    raise ValueError("No image found in generate_content() response")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    model = DEFAULT_MODEL
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        model = sys.argv[idx + 1]

    print(f"\n=== Gemini Image Test ===")
    print(f"Model  : {model}")
    print(f"Slug   : {SLUG}")
    print(f"Images : {TEST_COUNT}")
    print()

    # Load prompts
    output_dir = get_output_dir(SLUG)
    prompts_path = output_dir / PROMPTS_FILENAME
    if not prompts_path.exists():
        print(f"Error: {prompts_path} not found")
        sys.exit(1)

    md_content = prompts_path.read_text(encoding="utf-8")
    prompts = _parse_prompts(md_content, TEST_COUNT)
    if not prompts:
        print("Error: could not parse any prompts from file")
        sys.exit(1)
    print(f"Loaded {len(prompts)} prompts")

    # Init Vertex AI
    # Gemini 3 models require location="global"; regional endpoints return 404.
    # Imagen and Gemini 2.x models use the configured regional location.
    project = get_env("GOOGLE_CLOUD_PROJECT")
    if model.startswith("gemini-3"):
        location = "global"
    else:
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    try:
        from google import genai
        client = genai.Client(vertexai=True, project=project, location=location)
    except Exception as exc:
        print(f"\nError: Failed to initialise Vertex AI — {exc}")
        print("Run: gcloud auth application-default login")
        sys.exit(1)

    # Output folder
    test_dir = output_dir / "images_gemini_test"
    test_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput : {test_dir}\n")

    # Choose API: imagen-* models use generate_images(); gemini-* use generate_content()
    use_generate_images = not model.startswith("gemini-")
    api_name = "generate_images()" if use_generate_images else "generate_content(IMAGE)"
    print(f"API    : {api_name}\n")

    success = 0
    for i, prompt_text in enumerate(prompts, start=1):
        filename = f"image_{i:03d}.png"
        out_path = test_dir / filename
        print(f"[{i}/{len(prompts)}] {filename} ...")

        try:
            if use_generate_images:
                img_bytes = _generate_with_generate_images(client, model, prompt_text)
            else:
                img_bytes = _generate_with_generate_content(client, model, prompt_text)

            out_path.write_bytes(img_bytes)
            _resize_to_target(out_path)
            _enforce_background_color(out_path)
            print(f"  Saved: {out_path}")
            success += 1
        except Exception as exc:
            print(f"  Error: {exc}")

        if i < len(prompts):
            print(f"  Waiting {REQUEST_DELAY}s...")
            time.sleep(REQUEST_DELAY)

    print(f"\n{'='*40}")
    print(f"Done: {success}/{len(prompts)} images generated")
    print(f"\nTest output  : {test_dir}")
    print(f"Imagen 4 ref : {output_dir / 'images'}")


if __name__ == "__main__":
    main()
