"""Anim Lock Static — rejestracja klatek + zamrożenie statyki dla pętli Agenta 6c.

Problem: każda faza beatu to niezależne przerysowanie sceny przez Gemini —
cały obiekt ląduje o kilka px gdzie indziej i statyczna część sceny "telepie się"
w pętli. To NIE jest boil kreski (ten zostaje), tylko misrejestracja obiektów.

Naprawa, per faza (a/b/c) względem base.png:
  1. ALIGN  — globalne przesunięcie (korelacja fazowa FFT na masce tuszu),
  2. LOCK   — automatyczna maska ruchu (gęstość diffu w oknach: prawdziwy ruch
              jest lokalnie gęsty, boil rozproszony); poza maską klatka dostaje
              piksele bazy 1:1, w masce zostaje faza (ruch + lokalny boil).

Oryginalne klatki Gemini trafiają do frames/NNN/raw/ przy pierwszym przebiegu;
kolejne przebiegi czytają ZAWSZE z raw/ (idempotentne strojenie parametrów).
Po przebiegu odśwież mp4: agent6c_animate.py "<slug>" --no-gen [--indices ...].

Użycie:
  python tools/dev/anim_lock_static.py "<slug>"                    # wszystkie beaty
  python tools/dev/anim_lock_static.py "<slug>" --beats "47,60"
  python tools/dev/anim_lock_static.py "<slug>" --restore          # przywróć raw
  flagi strojenia: --win 24 --thresh 0.05 --pad 12 --max-shift 40
"""

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.ndimage import binary_dilation, uniform_filter

INK_THRESHOLD = 128


def load_ink(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Zwraca (obraz RGB jako array, binarna maska tuszu)."""
    img = np.array(Image.open(path).convert("RGB"))
    ink = np.array(Image.open(path).convert("L")) < INK_THRESHOLD
    return img, ink


def estimate_shift(ref_ink: np.ndarray, mov_ink: np.ndarray, max_shift: int) -> tuple[int, int]:
    """Korelacja fazowa FFT: o ile przesunąć mov, by pokrył ref. Zwraca (dy, dx)."""
    h, w = ref_ink.shape
    F = np.fft.rfft2(ref_ink.astype(np.float32))
    G = np.fft.rfft2(mov_ink.astype(np.float32))
    R = F * np.conj(G)
    R /= np.abs(R) + 1e-9
    corr = np.fft.irfft2(R, s=(h, w))
    peak = np.unravel_index(np.argmax(corr), corr.shape)
    dy = peak[0] if peak[0] <= h // 2 else peak[0] - h
    dx = peak[1] if peak[1] <= w // 2 else peak[1] - w
    if abs(dy) > max_shift or abs(dx) > max_shift:
        return 0, 0  # nieprawdopodobny estymat (np. rotacja) — nie ruszaj
    return int(dy), int(dx)


def apply_shift(img: np.ndarray, dy: int, dx: int, bg: np.ndarray) -> np.ndarray:
    """Przesuwa obraz o (dy, dx), odsłonięte pasy wypełnia kolorem tła."""
    if dy == 0 and dx == 0:
        return img
    out = np.roll(img, (dy, dx), axis=(0, 1))
    if dy > 0:
        out[:dy, :] = bg
    elif dy < 0:
        out[dy:, :] = bg
    if dx > 0:
        out[:, :dx] = bg
    elif dx < 0:
        out[:, dx:] = bg
    return out


def motion_mask(diffs: list[np.ndarray], win: int, thresh: float, pad: int) -> np.ndarray:
    """Maska ruchu beatu: komórki, gdzie średnia gęstość diffu (po fazach) > thresh."""
    density = np.zeros(diffs[0].shape, dtype=np.float32)
    for d in diffs:
        density += uniform_filter(d.astype(np.float32), size=win)
    density /= len(diffs)
    mask = density > thresh
    if pad > 0:
        mask = binary_dilation(mask, iterations=pad)
    return mask


def process_beat(beat_dir: Path, win: int, thresh: float, pad: int, max_shift: int) -> None:
    raw_dir = beat_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    phases = [p for p in ("a", "b", "c", "d") if (beat_dir / f"{p}.png").exists()
              or (raw_dir / f"{p}.png").exists()]
    if not phases:
        print(f"  [{beat_dir.name}] brak faz — pomijam")
        return

    # raw/ = źródło prawdy (oryginały Gemini); pierwszy przebieg je tworzy
    for p in phases + ["base"]:
        if not (raw_dir / f"{p}.png").exists():
            shutil.copy2(beat_dir / f"{p}.png", raw_dir / f"{p}.png")

    base_img, base_ink = load_ink(raw_dir / "base.png")
    bg = base_img[0, 0]  # narożnik = tło (two_color gwarantuje czysty kolor)

    aligned: dict[str, np.ndarray] = {}
    diffs: list[np.ndarray] = []
    shifts: dict[str, tuple[int, int]] = {}
    for p in phases:
        img, ink = load_ink(raw_dir / f"{p}.png")
        dy, dx = estimate_shift(base_ink, ink, max_shift)
        img = apply_shift(img, dy, dx, bg)
        aligned[p] = img
        shifts[p] = (dy, dx)
        gray = img.mean(axis=2) < INK_THRESHOLD
        diffs.append(gray != base_ink)

    mask = motion_mask(diffs, win, thresh, pad)
    mask_pct = 100.0 * mask.sum() / mask.size

    frozen_pcts = []
    for p in phases:
        out = base_img.copy()
        out[mask] = aligned[p][mask]
        Image.fromarray(out).save(beat_dir / f"{p}.png")
        d = diffs[phases.index(p)]
        frozen = d & ~mask  # diff, który właśnie zamroziliśmy
        frozen_pcts.append(100.0 * frozen.sum() / d.size)

    strip = np.hstack([base_img] + [np.array(Image.open(beat_dir / f"{p}.png")) for p in phases])
    Image.fromarray(strip).save(beat_dir / "strip.png")

    shift_txt = " ".join(f"{p}:({s[0]:+d},{s[1]:+d})" for p, s in shifts.items())
    print(f"  [{beat_dir.name}] shift {shift_txt} | maska ruchu {mask_pct:.1f}% kadru"
          f" | zamrożony dryf {max(frozen_pcts):.2f}% px")


def restore_beat(beat_dir: Path) -> None:
    raw_dir = beat_dir / "raw"
    if not raw_dir.is_dir():
        return
    for f in raw_dir.glob("*.png"):
        shutil.copy2(f, beat_dir / f.name)
    print(f"  [{beat_dir.name}] przywrócono oryginały z raw/")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug")
    ap.add_argument("--beats", help="np. '47,60' — tylko te beaty (numery z planu)")
    ap.add_argument("--win", type=int, default=24, help="okno gęstości diffu (px)")
    ap.add_argument("--thresh", type=float, default=0.05,
                    help="próg gęstości ruchu (ułamek okna, domyślnie 0.05)")
    ap.add_argument("--pad", type=int, default=12, help="dylatacja maski (px)")
    ap.add_argument("--max-shift", type=int, default=40, help="maks. uznawane przesunięcie")
    ap.add_argument("--restore", action="store_true", help="przywróć oryginały z raw/")
    args = ap.parse_args()

    frames_root = Path("outputs/videos_pl") / args.slug / "images_anim" / "frames"
    if not frames_root.is_dir():
        sys.exit(f"Brak {frames_root} — najpierw wygeneruj beaty (agent6c_animate.py).")

    wanted = None
    if args.beats:
        wanted = {f"{int(x):03d}" for x in args.beats.split(",")}

    beat_dirs = sorted(d for d in frames_root.iterdir() if d.is_dir()
                       and (wanted is None or d.name in wanted))
    print(f"Anim Lock Static — {len(beat_dirs)} beatów (win={args.win}, "
          f"thresh={args.thresh}, pad={args.pad})")
    for bd in beat_dirs:
        if args.restore:
            restore_beat(bd)
        else:
            process_beat(bd, args.win, args.thresh, args.pad, args.max_shift)
    if not args.restore:
        print("\nGotowe. Odśwież pętle: PYTHONIOENCODING=utf-8 python "
              f"tools/pipeline/agent6c_animate.py \"{args.slug}\" --no-gen")


if __name__ == "__main__":
    main()
