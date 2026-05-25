"""
Two-color posterize for thumbnails (or any image folder).

Maps every pixel to one of the brand palette's two colors by luminance:
  - dark   -> #582F0E  (Dark Brown ink)
  - light  -> #F4E5CA  (Sage Beige background)

Originals are never modified. Output goes to a sibling `_posterized` folder.
See memory `feedback_preserve_originals_grain` for the preserve-originals rule.

Usage:
    python tools/dev/posterize_thumbnails.py <slug> [threshold]
    python tools/dev/posterize_thumbnails.py 5_how_to_actually_stay_mentally_healthy
    python tools/dev/posterize_thumbnails.py 5_how_to_actually_stay_mentally_healthy 160

Default threshold: 165 (0-255 luma). Lower -> less ink; Higher -> more ink.
"""

import sys
from pathlib import Path

import numpy as np
from PIL import Image


BACKGROUND = (244, 229, 202)  # #F4E5CA
INK = (88, 47, 14)            # #582F0E
DEFAULT_THRESHOLD = 165


def posterize(src: Path, dst: Path, threshold: int) -> None:
    img = Image.open(src).convert("RGB")
    arr = np.asarray(img, dtype=np.uint8)
    # Rec. 709 luma
    luma = (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2])
    mask_ink = luma < threshold
    out = np.empty_like(arr)
    out[mask_ink] = INK
    out[~mask_ink] = BACKGROUND
    Image.fromarray(out, mode="RGB").save(dst)


def batch(slug: str, threshold: int) -> None:
    src_dir = Path("outputs") / "videos" / slug / "thumbnails_no_grain"
    if not src_dir.exists():
        src_dir = Path("outputs") / "videos" / slug / "thumbnails"
    if not src_dir.exists():
        print(f"No thumbnails folder found under outputs/videos/{slug}/")
        sys.exit(1)

    dst_dir = src_dir.parent / f"{src_dir.name}_posterized"
    dst_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(src_dir.glob("*.png"))
    if not images:
        print(f"No PNGs in {src_dir}")
        return

    for p in images:
        posterize(p, dst_dir / p.name, threshold)
        print(f"Saved: {p.name}")

    print(f"\nDone: {len(images)} images at threshold {threshold} -> {dst_dir}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/dev/posterize_thumbnails.py <slug> [threshold]")
        sys.exit(1)
    slug = sys.argv[1]
    threshold = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_THRESHOLD
    batch(slug, threshold)
