"""
Agent 6c: Ozywiacz — obiektowe petle animacyjne (boil loops).

Czyta `md/06c_animation_plan.md` (pisany przez /animate, akceptowany przez
uzytkownika) i dla kazdego beatu produkuje zapetlony klip MP4 — drop-in na
timeline DaVinci zamiast statycznego PNG. Estetyka: lekki "boil" przerysowanej
kreski (decyzja 2026-06-10, brainstorms/2026-06-10-agent6c-ozywiacz.md) —
zadnej stabilizacji klatek.

Tryby beatu:
  edit  — baza = gotowa ilustracja sceny (images_post/ lub images/);
          fazy ruchu to EDYCJE obrazu w gemini-2.5-flash-image (GUARD-prompt
          ogranicza zmiane do wskazanego obszaru), kazda po two_color.
  sheet — arkusz 3 faz generowany od zera (CHARACTER_DESCRIPTION + V8),
          ciecie na sprite'y (alpha z flood-fill, odrzut wyciekow krawedziowych),
          kompozycja cyklu na bazowej scenie w punkcie Anchor.

Uzycie:
  python tools/pipeline/agent6c_animate.py "<slug>"              # caly plan
  python tools/pipeline/agent6c_animate.py "<slug>" --indices "1,37"
  python tools/pipeline/agent6c_animate.py "<slug>" --no-gen     # tylko sklejka
  python tools/pipeline/agent6c_animate.py "<slug>" --force      # nadpisz klatki

Wyjscie: images_anim/image_NNN_anim.mp4 + images_anim/frames/NNN/{*.png,strip.png}
"""

import argparse
import re
import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import (
    get_env, get_output_dir, two_color, CHARACTER_DESCRIPTION, STYLE_SUFFIX,
)

PLAN_FILENAME = "md/06c_animation_plan.md"
IMAGE_MODEL = "gemini-2.5-flash-image"
GEN_SLEEP = 8           # sekundy miedzy wywolaniami API
DEFAULT_FPS = 6
DEFAULT_SECONDS = 10

GUARD_EDIT = (
    "This is an EDIT of the provided ink illustration. Reproduce the input image "
    "EXACTLY — identical composition, identical linework, identical cross-hatching, "
    "identical background — with ONE small change only, strictly limited to {scope}: "
    "{change} Do not move, redraw or restyle anything else. Keep the strict "
    "two-colour look: dark brown #582F0E ink on flat solid sage beige #F4E5CA, "
    "no other colours, no text, no border."
)

SHEET_RULES = (
    "character pose sheet: three separate full-body studies of the SAME character — "
    f"{CHARACTER_DESCRIPTION} — arranged side by side in ONE horizontal row, evenly "
    "spaced with generous gaps, the three figures NOT overlapping and NOT touching, "
    "each figure fully isolated against the empty background, no scene, no ground "
    "line, no shadows under the feet, all three the SAME size and proportions, "
)


# ---------------------------------------------------------------------------
# Parser planu
# ---------------------------------------------------------------------------

def parse_plan(text: str) -> list[dict]:
    """`## Beat NNN` + pola `**Klucz:** wartosc` -> lista beatow."""
    beats = []
    parts = re.split(r"^## Beat (\d+)\s*$", text, flags=re.M)[1:]
    for num, body in zip(parts[0::2], parts[1::2]):
        fields = {k.lower(): v.strip()
                  for k, v in re.findall(r"\*\*([\w-]+):\*\*\s*(.+)", body)}
        phases = {k.split()[-1].lower(): v
                  for k, v in re.findall(r"\*\*(Phase \w+):\*\*\s*(.+)", body)}
        beats.append({
            "num": int(num),
            "image": fields.get("image", f"image_{int(num):03d}.png"),
            "mode": fields.get("mode", "edit").lower(),
            "motion": fields.get("motion", "custom"),
            "fps": float(fields.get("fps", DEFAULT_FPS)),
            "seconds": float(fields.get("seconds", DEFAULT_SECONDS)),
            "pattern": [p.strip() for p in fields.get("pattern", "base,a").split(",")],
            "scope": fields.get("scope", "the moving object"),
            "phases": phases,                       # {"a": opis, "b": opis, ...}
            "sheet_poses": fields.get("sheet-poses", ""),
            "anchor": fields.get("anchor", ""),     # "x,y" — punkt stop sprite'a
        })
    return beats


# ---------------------------------------------------------------------------
# Generacja (wspolny klient)
# ---------------------------------------------------------------------------

def _client():
    import google.genai as genai
    return genai.Client(vertexai=True, project=get_env("GOOGLE_CLOUD_PROJECT"),
                        location="global")


def _gen(client, contents) -> bytes:
    from google.genai import types as genai_types
    from tools.pipeline.agent6_images import _generate_image_with_retry
    return _generate_image_with_retry(client, genai_types, IMAGE_MODEL, contents)


def _post(path: Path) -> None:
    """two_color + dopasowanie do 1920x1080 w miejscu."""
    import cv2
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Nieczytelny obraz: {path}")
    if img.shape[:2] != (1080, 1920):
        img = cv2.resize(img, (1920, 1080), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(path), img)
    two_color(path)


# ---------------------------------------------------------------------------
# Tryb edit
# ---------------------------------------------------------------------------

def frames_edit(client, beat: dict, base_png: Path, frames_dir: Path,
                force: bool, no_gen: bool) -> None:
    from google.genai import types as genai_types
    import cv2
    frames_dir.mkdir(parents=True, exist_ok=True)
    base_dst = frames_dir / "base.png"
    if force or not base_dst.exists():
        cv2.imwrite(str(base_dst), cv2.imread(str(base_png)))
    base_part = genai_types.Part.from_bytes(data=base_png.read_bytes(),
                                            mime_type="image/png")
    for name, change in beat["phases"].items():
        dst = frames_dir / f"{name}.png"
        if dst.exists() and not force:
            print(f"    {name}: istnieje, pomijam (--force aby nadpisac)")
            continue
        if no_gen:
            print(f"    {name}: brak klatki a --no-gen — pomijam beat")
            return
        print(f"    gen {name} ...", flush=True)
        prompt = GUARD_EDIT.format(scope=beat["scope"], change=change)
        dst.write_bytes(_gen(client, [base_part, prompt]))
        _post(dst)
        time.sleep(GEN_SLEEP)


# ---------------------------------------------------------------------------
# Tryb sheet — ciecie arkusza (sprawdzone na mocku Wedrowki)
# ---------------------------------------------------------------------------

def _cut_sheet(sheet_png: Path, frames_dir: Path, names: list[str]) -> dict:
    """Tnie arkusz na sprite'y RGBA; zwraca {nazwa: sciezka}."""
    import cv2
    import numpy as np
    img = cv2.imread(str(sheet_png))
    ink = (np.abs(img.astype(int) - np.array([14, 47, 88])).sum(axis=2) < 30
           ).astype(np.uint8) * 255
    big = cv2.dilate(ink, np.ones((9, 9), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(big)
    comps = sorted(((stats[i, 0], stats[i, 1], stats[i, 2], stats[i, 3], stats[i, 4])
                    for i in range(1, n) if stats[i, 4] > 4000),
                   key=lambda c: -c[4])[:len(names)]
    comps.sort(key=lambda c: c[0])
    out = {}
    scale_h = max(c[3] for c in comps)
    for name, (x, y, w, h, _a) in zip(names, comps):
        x0, y0 = max(0, x - 8), max(0, y - 8)
        crop = img[y0:min(img.shape[0], y + h + 8), x0:min(img.shape[1], x + w + 8)]
        bg = ((np.abs(crop.astype(int) - np.array([14, 47, 88])).sum(axis=2) >= 30)
              ).astype(np.uint8)
        ff = bg.copy()
        mask = np.zeros((ff.shape[0] + 2, ff.shape[1] + 2), np.uint8)
        for xx in range(0, ff.shape[1], 4):
            for yy in (0, ff.shape[0] - 1):
                if ff[yy, xx]:
                    cv2.floodFill(ff, mask, (xx, yy), 2)
        for yy in range(0, ff.shape[0], 4):
            for xx in (0, ff.shape[1] - 1):
                if ff[yy, xx]:
                    cv2.floodFill(ff, mask, (xx, yy), 2)
        alpha = np.where(ff == 2, 0, 255).astype(np.uint8)
        # odrzut wyciekow z sasiednich figur (komponenty dotykajace krawedzi)
        n2, lab2, st2, _ = cv2.connectedComponentsWithStats(
            (alpha > 0).astype(np.uint8), connectivity=8)
        if n2 > 2:
            main = 1 + int(np.argmax(st2[1:, 4]))
            hh, ww = alpha.shape
            for ci in range(1, n2):
                if ci == main:
                    continue
                bx, by, bw, bh = st2[ci, 0], st2[ci, 1], st2[ci, 2], st2[ci, 3]
                if bx <= 1 or by <= 1 or bx + bw >= ww - 1 or by + bh >= hh - 1 \
                        or st2[ci, 4] < 200:
                    alpha[lab2 == ci] = 0
        rgba = cv2.cvtColor(crop, cv2.COLOR_BGR2BGRA)
        rgba[:, :, 3] = alpha
        s = 520.0 / scale_h
        rgba = cv2.resize(rgba, (max(1, round(rgba.shape[1] * s)),
                                 max(1, round(rgba.shape[0] * s))),
                          interpolation=cv2.INTER_AREA)
        p = frames_dir / f"sprite_{name}.png"
        cv2.imwrite(str(p), rgba)
        out[name] = p
    return out


def frames_sheet(client, beat: dict, base_png: Path, frames_dir: Path,
                 force: bool, no_gen: bool) -> None:
    """Generuje arkusz faz, tnie i komponuje klatki na bazowej scenie."""
    import cv2
    import numpy as np
    from tools.pipeline.agent6_images import (
        V8_BG_RULE, V8_FIGURE_RULE, V8_MASTER_RENDERING, V8_NEGATIVE,
    )
    frames_dir.mkdir(parents=True, exist_ok=True)
    sheet_png = frames_dir / "_sheet.png"
    if (force or not sheet_png.exists()) and not no_gen:
        prompt = (V8_BG_RULE + V8_FIGURE_RULE + SHEET_RULES + beat["sheet_poses"]
                  + ", " + STYLE_SUFFIX + V8_MASTER_RENDERING + V8_NEGATIVE)
        print("    gen arkusz ...", flush=True)
        sheet_png.write_bytes(_gen(client, prompt))
        _post(sheet_png)
        time.sleep(GEN_SLEEP)
    if not sheet_png.exists():
        print("    brak arkusza a --no-gen — pomijam beat")
        return
    names = sorted(beat["phases"].keys()) or ["a", "b", "c"]
    sprites = _cut_sheet(sheet_png, frames_dir, names)
    base = cv2.imread(str(base_png))
    try:
        ax, ay = (int(v) for v in beat["anchor"].split(","))
    except ValueError:
        ax, ay = 960, 900
    cv2.imwrite(str(frames_dir / "base.png"), base)
    for name, sp_path in sprites.items():
        sp = cv2.imread(str(sp_path), cv2.IMREAD_UNCHANGED)
        h, w = sp.shape[:2]
        x0, y0 = ax - w // 2, ay - h
        frame = base.copy()
        a = sp[:, :, 3:4].astype(float) / 255.0
        roi = frame[y0:y0 + h, x0:x0 + w].astype(float)
        frame[y0:y0 + h, x0:x0 + w] = (a * sp[:, :, :3] + (1 - a) * roi
                                       ).astype(np.uint8)
        cv2.imwrite(str(frames_dir / f"{name}.png"), frame)


# ---------------------------------------------------------------------------
# Sklejka petli
# ---------------------------------------------------------------------------

def assemble(beat: dict, frames_dir: Path, out_mp4: Path) -> bool:
    import cv2
    import numpy as np
    frames = {p.stem: cv2.imread(str(p))
              for p in frames_dir.glob("*.png") if not p.stem.startswith(("sprite_", "_", "strip"))}
    missing = [k for k in set(beat["pattern"]) if k not in frames]
    if missing:
        print(f"    !! brak klatek {missing} — beat pominiety")
        return False
    order = [k for k in ("base", "a", "b", "c", "d") if k in frames]
    strip = np.hstack([cv2.resize(frames[k], (480, 270)) for k in order])
    cv2.imwrite(str(frames_dir / "strip.png"), strip)
    vw = cv2.VideoWriter(str(out_mp4), cv2.VideoWriter_fourcc(*"mp4v"),
                         beat["fps"], (1920, 1080))
    total = int(beat["seconds"] * beat["fps"])
    n = 0
    while n < total:
        for key in beat["pattern"]:
            vw.write(frames[key])
            n += 1
    vw.release()
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Agent 6c: obiektowe petle animacyjne")
    ap.add_argument("slug")
    ap.add_argument("--indices", help="np. '1,37' — tylko te beaty (numery z planu)")
    ap.add_argument("--no-gen", action="store_true",
                    help="bez API: tylko sklejka z istniejacych klatek")
    ap.add_argument("--force", action="store_true", help="nadpisz istniejace klatki")
    args = ap.parse_args()

    out_dir = get_output_dir(args.slug)
    plan_path = out_dir / PLAN_FILENAME
    if not plan_path.exists():
        sys.exit(f"Brak {plan_path} — najpierw /animate {args.slug}")
    beats = parse_plan(plan_path.read_text(encoding="utf-8"))
    if args.indices:
        wanted = {int(i) for i in args.indices.split(",")}
        beats = [b for b in beats if b["num"] in wanted]
    if not beats:
        sys.exit("Plan nie zawiera pasujacych beatow.")

    anim_dir = out_dir / "images_anim"
    anim_dir.mkdir(exist_ok=True)
    client = None if args.no_gen else _client()
    print(f"=== Agent 6c: {len(beats)} beat(ow), tryb {'sklejka' if args.no_gen else 'generacja+sklejka'} ===")
    done = 0
    for beat in beats:
        num = beat["num"]
        print(f"[Beat {num:03d}] {beat['motion']} ({beat['mode']})")
        base_png = out_dir / "images_post" / beat["image"]
        if not base_png.exists():
            base_png = out_dir / "images" / beat["image"]
        if not base_png.exists():
            print(f"    !! brak obrazu {beat['image']} — pomijam")
            continue
        frames_dir = anim_dir / "frames" / f"{num:03d}"
        if beat["mode"] == "sheet":
            frames_sheet(client, beat, base_png, frames_dir, args.force, args.no_gen)
        else:
            frames_edit(client, beat, base_png, frames_dir, args.force, args.no_gen)
        stem = Path(beat["image"]).stem
        if assemble(beat, frames_dir, anim_dir / f"{stem}_anim.mp4"):
            done += 1
            print(f"    OK -> images_anim/{stem}_anim.mp4")
    print(f"\nGotowe: {done}/{len(beats)} petli w {anim_dir}")


if __name__ == "__main__":
    main()
