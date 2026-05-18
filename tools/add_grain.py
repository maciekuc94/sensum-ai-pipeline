import sys
from PIL import Image
import numpy as np
from pathlib import Path

GRAIN_INTENSITY = 12

def add_grain(slug: str, intensity: int = GRAIN_INTENSITY):
    src_dir = Path(f"outputs/{slug}/images")
    dst_dir = Path(f"outputs/{slug}/images_grain")
    dst_dir.mkdir(exist_ok=True)

    rng = np.random.default_rng(42)
    images = sorted(src_dir.glob("*.png"))
    if not images:
        print(f"No images found in {src_dir}")
        return

    for img_path in images:
        img = Image.open(img_path).convert("RGBA")
        arr = np.array(img, dtype=np.float32)
        noise = rng.normal(0, intensity, arr[:, :, :3].shape)
        arr[:, :, :3] = np.clip(arr[:, :, :3] + noise, 0, 255)
        result = Image.fromarray(arr.astype(np.uint8), "RGBA")
        result.save(dst_dir / img_path.name)
        print(f"Saved: {img_path.name}")

    print(f"\nDone: {len(images)} images at intensity {intensity} -> {dst_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/add_grain.py <slug> [intensity]")
        sys.exit(1)
    slug = sys.argv[1]
    intensity = int(sys.argv[2]) if len(sys.argv) > 2 else GRAIN_INTENSITY
    add_grain(slug, intensity)
