"""
Batch grain pass over a video's images.

Loops the shared `tools.utils.add_grain` helper over every PNG in
`outputs/{slug}/images/` and writes the results to `outputs/{slug}/images_grain/`.
Original images are never modified — see memory `feedback_preserve_originals_grain`.

Note on slug: this script accepts whatever path suffix you have under `outputs/`.
For the standard layout pass `videos/<slug>`. See memory `add_grain_path_quirk`.

Usage:
    python tools/dev/add_grain.py <slug> [intensity]
    python tools/dev/add_grain.py videos/4_why_you_can_t_stick_to_anything
    python tools/dev/add_grain.py videos/4_why_you_can_t_stick_to_anything 14
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import add_grain, GRAIN_INTENSITY_DEFAULT


def batch_grain(slug: str, intensity: int = GRAIN_INTENSITY_DEFAULT) -> None:
    src_dir = Path("outputs") / slug / "images"
    dst_dir = Path("outputs") / slug / "images_grain"
    dst_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(src_dir.glob("*.png"))
    if not images:
        print(f"No images found in {src_dir}")
        return

    for img_path in images:
        # rng_seed=42 keeps re-runs deterministic for visual comparison.
        add_grain(img_path, intensity=intensity, out_path=dst_dir / img_path.name, rng_seed=42)
        print(f"Saved: {img_path.name}")

    print(f"\nDone: {len(images)} images at intensity {intensity} -> {dst_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/dev/add_grain.py <slug> [intensity]")
        sys.exit(1)
    slug = sys.argv[1]
    intensity = int(sys.argv[2]) if len(sys.argv) > 2 else GRAIN_INTENSITY_DEFAULT
    batch_grain(slug, intensity)
