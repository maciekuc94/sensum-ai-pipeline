"""SENSUM thumbnail finish — two-colour + coarse grain on a single thumbnail.

Applies the documented post-production *thumbnail finish*
(`workflows/pipeline/07_package.md` → Post-production) to ONE thumbnail PNG,
given its path:

  1. two_color  — hard-snap every pixel to the nearer of #582F0E / #F4E5CA
                  (the same brand two-colour contract as the body images).
  2. add_grain  — coarse grain s2/i18 (intensity=18, grain_scale=2). At a native
                  ~4K thumbnail a 2-px grain *cell* is needed, or the grain
                  vanishes when YouTube downscales the thumbnail. This is heavier
                  and coarser than the body-image grain standard (i12/s1).

Order matters: grain goes ON the two-colour render, not the raw 819-colour one,
so off-brand casts inside objects are collapsed first.

Grain is irreversible, so by default the result is written to a `*_final.png`
copy and the original is left untouched. Pass --in-place to overwrite, or --out
for an explicit destination.

Usage:
    python tools/dev/finish_thumbnail.py "<path/to/thumbnail.png>"
    python tools/dev/finish_thumbnail.py "<path>" --in-place
    python tools/dev/finish_thumbnail.py "<path>" --out "<path/to/out.png>"
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import two_color, add_grain  # noqa: E402

# SENSUM thumbnail finish constants — 07_package.md → Post-production (2026-06-08).
# Validated on slug-3 thumbnail #2. Heavier/coarser than the body-image grain
# (i12/s1) on purpose: fine grain disappears when YouTube downscales a ~4K image.
THUMB_GRAIN_INTENSITY = 18
THUMB_GRAIN_SCALE = 2
THUMB_GRAIN_SEED = 42  # deterministic — matches tools/dev/add_grain.py


def finish_thumbnail(path: str, *, in_place: bool = False, out: str | None = None) -> Path:
    src = Path(path)
    if not src.exists():
        print(f"Error: file not found: {src}")
        sys.exit(1)
    if src.suffix.lower() != ".png":
        print(f"Error: expected a .png thumbnail, got: {src.suffix or '(none)'}")
        sys.exit(1)

    if out:
        dst = Path(out)
    elif in_place:
        dst = src
    else:
        dst = src.with_name(src.stem + "_final.png")
    dst.parent.mkdir(parents=True, exist_ok=True)

    print("=== SENSUM thumbnail finish ===")
    print(f"Source : {src.name}")
    print(f"Output : {dst.name}" + ("  (in place)" if dst == src else ""))

    # 1) two-colour — snap every pixel to the two brand anchors
    two_color(src, output_path=dst)
    try:
        from PIL import Image
        import numpy as np
        arr = np.array(Image.open(dst).convert("RGB")).reshape(-1, 3)
        ncol = len(np.unique(arr, axis=0))
        note = "" if ncol == 2 else "  (WARNING: expected exactly 2)"
        print(f"  [1/2] two_color -> {ncol} colour(s){note}")
    except Exception:
        print("  [1/2] two_color applied")

    # 2) coarse grain s2/i18, in place on the output
    add_grain(dst, intensity=THUMB_GRAIN_INTENSITY, grain_scale=THUMB_GRAIN_SCALE, rng_seed=THUMB_GRAIN_SEED)
    print(f"  [2/2] add_grain intensity={THUMB_GRAIN_INTENSITY} grain_scale={THUMB_GRAIN_SCALE} (seed={THUMB_GRAIN_SEED})")

    print(f"\nDone -> {dst}")
    print("Next: open in Canva and add the napis overlay only — grain is already baked in (do NOT add Canva grain).")
    return dst


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Apply the SENSUM two-colour + coarse-grain finish (s2/i18) to one thumbnail PNG."
    )
    ap.add_argument("path", help="Path to the thumbnail PNG to finish")
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument(
        "--in-place", dest="in_place", action="store_true",
        help="Overwrite the source file instead of writing a *_final.png copy",
    )
    grp.add_argument("--out", help="Explicit output path (overrides the default *_final.png copy)")
    args = ap.parse_args()
    finish_thumbnail(args.path, in_place=args.in_place, out=args.out)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main()
