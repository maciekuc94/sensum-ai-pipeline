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

Each step can also run alone (the two-colour-thumbnail / grain-thumbnail skills
route here): --two-color-only snaps without grain (preview the clean palette
first), --grain-only grains an already-snapped file (warns if the input has
more than 2 colours, because grain belongs on the snapped render).

Grain is irreversible, so by default the result is written to a copy and the
original is left untouched (`*_final.png` for the full finish, `*_2col.png`
for --two-color-only, `*_grain.png` for --grain-only). Pass --in-place to
overwrite, or --out for an explicit destination.

Usage:
    python tools/dev/finish_thumbnail.py "<path/to/thumbnail.png>"
    python tools/dev/finish_thumbnail.py "<path>" --two-color-only
    python tools/dev/finish_thumbnail.py "<path>" --grain-only
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

# mode -> (default copy suffix, banner label)
_MODES = {
    "finish": ("_final", "two-colour + coarse grain"),
    "two_color": ("_2col", "two-colour only (no grain)"),
    "grain": ("_grain", "coarse grain only"),
}


def _count_colours(path: Path) -> int | None:
    try:
        from PIL import Image
        import numpy as np
        arr = np.array(Image.open(path).convert("RGB")).reshape(-1, 3)
        return len(np.unique(arr, axis=0))
    except Exception:
        return None


def finish_thumbnail(
    path: str, *, mode: str = "finish", in_place: bool = False, out: str | None = None
) -> Path:
    src = Path(path)
    if not src.exists():
        print(f"Error: file not found: {src}")
        sys.exit(1)
    if src.suffix.lower() != ".png":
        print(f"Error: expected a .png thumbnail, got: {src.suffix or '(none)'}")
        sys.exit(1)

    suffix, label = _MODES[mode]
    if out:
        dst = Path(out)
    elif in_place:
        dst = src
    else:
        dst = src.with_name(src.stem + suffix + ".png")
    dst.parent.mkdir(parents=True, exist_ok=True)

    steps = [s for s, on in (("two_color", mode != "grain"), ("grain", mode != "two_color")) if on]
    total = len(steps)

    print(f"=== SENSUM thumbnail finish — {label} ===")
    print(f"Source : {src.name}")
    print(f"Output : {dst.name}" + ("  (in place)" if dst == src else ""))

    step = 0
    if "two_color" in steps:
        # two-colour — snap every pixel to the two brand anchors
        step += 1
        two_color(src, output_path=dst)
        ncol = _count_colours(dst)
        if ncol is None:
            print(f"  [{step}/{total}] two_color applied")
        else:
            note = "" if ncol == 2 else "  (WARNING: expected exactly 2)"
            print(f"  [{step}/{total}] two_color -> {ncol} colour(s){note}")

    if "grain" in steps:
        step += 1
        if mode == "grain":
            # grain belongs ON the snapped render — warn (don't block) on a raw input
            ncol = _count_colours(src)
            if ncol is not None and ncol > 2:
                print(
                    f"  WARNING: input has {ncol} colours — grain belongs on the two-colour "
                    "render; run --two-color-only first (07_package.md → Post-production)"
                )
            if dst != src:
                dst.write_bytes(src.read_bytes())
        add_grain(dst, intensity=THUMB_GRAIN_INTENSITY, grain_scale=THUMB_GRAIN_SCALE, rng_seed=THUMB_GRAIN_SEED)
        print(f"  [{step}/{total}] add_grain intensity={THUMB_GRAIN_INTENSITY} grain_scale={THUMB_GRAIN_SCALE} (seed={THUMB_GRAIN_SEED})")

    print(f"\nDone -> {dst}")
    if "grain" in steps:
        print("Next: open in Canva and add the napis overlay only — grain is already baked in (do NOT add Canva grain).")
    else:
        print("Next: review the clean two-colour render; add grain before Canva (grain-thumbnail / --grain-only).")
    return dst


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Apply the SENSUM thumbnail finish to one PNG: two-colour + coarse grain s2/i18 (default), or one step alone."
    )
    ap.add_argument("path", help="Path to the thumbnail PNG to finish")
    mode_grp = ap.add_mutually_exclusive_group()
    mode_grp.add_argument(
        "--two-color-only", dest="two_color_only", action="store_true",
        help="Only snap to the two brand colours (no grain); default copy suffix *_2col.png",
    )
    mode_grp.add_argument(
        "--grain-only", dest="grain_only", action="store_true",
        help="Only add coarse grain s2/i18 (expects an already two-colour input); default copy suffix *_grain.png",
    )
    out_grp = ap.add_mutually_exclusive_group()
    out_grp.add_argument(
        "--in-place", dest="in_place", action="store_true",
        help="Overwrite the source file instead of writing a copy",
    )
    out_grp.add_argument("--out", help="Explicit output path (overrides the default copy)")
    args = ap.parse_args()
    mode = "two_color" if args.two_color_only else "grain" if args.grain_only else "finish"
    finish_thumbnail(args.path, mode=mode, in_place=args.in_place, out=args.out)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main()
