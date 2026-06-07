# -*- coding: utf-8 -*-
"""
md_to_pdf_sensum.py — konwerter Markdown -> JEDEN DLUGI PDF (bez podzialu na strony)
w STYLU SENSUM. Renderuje md -> HTML (brandowy CSS) -> PDF przez Playwright + systemowy
Chrome; wysokosc strony = wysokosc calej tresci (jedna ciagla strona, zero paginacji).

Dlaczego nie docx->PDF: Word zawsze paginuje. Przegladarka uklada tresc w jednej kolumnie
i swietnie auto-skaluje szerokie tabele (zero trybu poziomego, zero powtarzanych naglowkow).

DESIGN (frontend-design 2026-06-07): kierunek "antyczna monografia naukowa" — zgodny z
brandem SENSUM (XIX-wieczna rycina). Display Cormorant Garamond, tekst EB Garamond,
etykiety wersalikami z rozstrzeleniem, cyfry nautyczne (oldstyle) w tekscie i tabularne
w tabelach, subtelne ziarno papieru (SVG noise), inicjal (drop cap), podwojna linia pod
mastheadem, ornament zamiast linii ---. Paleta: tlo #F4E5CA, atrament #582F0E + odcienie
#EBD9B8 / #CDB488 (uzyte WYLACZNIE wewnatrz dokumentu, nie w generowanych grafikach).

Parser blokow reuzyty z md_to_docx_sensum (jedno zrodlo md).

Uzycie (z korzenia repo):
  PYTHONIOENCODING=utf-8 python tools/dev/md_to_pdf_sensum.py <plik.md> [<plik2.md> ...]
  ... [--out <katalog>]   # domyslnie .pdf laduje obok zrodla
  ... [--no-logo]
Wspiera glob: "docs/research/*.md"
"""
import argparse
import base64
import glob as globmod
import html as htmllib
import io
import sys
from pathlib import Path

# parser bloków + regex inline = jedno źródło z konwerterem docx (ten sam katalog)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from md_to_docx_sensum import parse_blocks, INLINE_RE  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "outputs" / "channel_assets" / "SENSUM_LOGO.png"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,600&family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400;1,600&family=JetBrains+Mono:wght@400;500&display=swap');
:root{ --beige:#F4E5CA; --ink:#582F0E; --tint:#EBD9B8; --hair:#CDB488; --measure:720px; --wide:1180px; }
*{ box-sizing:border-box; }
html{ background:var(--beige); -webkit-print-color-adjust:exact; print-color-adjust:exact; }
body{ margin:0; width:max-content; background:var(--beige); color:var(--ink);
  font-family:'EB Garamond', Georgia, serif; font-size:18px; line-height:1.58;
  font-variant-numeric:oldstyle-figures; font-feature-settings:"kern","liga","onum";
  text-rendering:optimizeLegibility; }
.page{ position:relative; padding:70px 82px 78px; margin:0; }
.page::before{ content:""; position:absolute; inset:0; z-index:0; pointer-events:none;
  opacity:.5; mix-blend-mode:multiply;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='200' height='200'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3CfeColorMatrix type='matrix' values='0 0 0 0 0.345 0 0 0 0 0.184 0 0 0 0 0.055 0 0 0 0.34 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E"); }
.page>*{ position:relative; z-index:1; }
.logo{ display:block; width:114px; height:auto; margin:2px auto 14px; }
h1.masthead{ font-family:'Cormorant Garamond','EB Garamond',serif; text-align:center;
  font-size:48px; font-weight:600; letter-spacing:.5px; line-height:1.1; text-wrap:balance;
  max-width:860px; margin:.1em auto .55em; padding-bottom:.28em; border-bottom:5px double var(--ink); }
h1{ font-family:'Cormorant Garamond','EB Garamond',serif; font-size:34px; font-weight:700;
  max-width:var(--measure); margin:1.4em auto .5em; padding-bottom:.16em;
  border-bottom:3px double var(--ink); text-wrap:balance; }
h2{ font-size:24px; font-weight:700; max-width:var(--measure); margin:1.75em auto .55em;
  padding-bottom:.16em; border-bottom:1.5px solid var(--ink); text-wrap:balance; }
h3{ font-family:'EB Garamond',serif; text-transform:uppercase; letter-spacing:.14em;
  font-size:15px; font-weight:700; max-width:var(--measure); margin:1.6em auto .5em; }
p{ max-width:var(--measure); margin:.6em auto; text-align:justify; hyphens:auto; }
p.lead::first-letter{ float:left; font-family:'Cormorant Garamond',serif; font-weight:700;
  font-size:4.6em; line-height:.72; padding:.02em .1em 0 0; color:var(--ink); }
p.lead::first-line{ font-variant:small-caps; letter-spacing:.02em; }
ul,ol{ max-width:var(--measure); margin:.55em auto; padding-left:1.45em; }
li{ margin:.34em 0; padding-left:.15em; }
li::marker{ color:var(--ink); }
strong{ font-weight:700; }
em{ font-style:italic; }
code{ font-family:'JetBrains Mono',Consolas,monospace; font-size:.8em; color:var(--ink);
  background:var(--tint); border:1px solid rgba(88,47,14,.18); padding:.05em .4em;
  border-radius:4px; overflow-wrap:anywhere; }
blockquote{ max-width:var(--measure); margin:1.2em auto; background:var(--tint);
  border-left:4px solid var(--ink); padding:.75em 1.15em; font-style:italic; }
blockquote p{ max-width:none; margin:.35em 0; text-align:left; }
.fleuron{ display:flex; align-items:center; gap:16px; max-width:var(--measure);
  margin:1.9em auto; color:var(--ink); }
.fleuron::before,.fleuron::after{ content:""; flex:1; border-top:1px solid var(--hair); }
.fleuron span{ font-size:17px; opacity:.9; }
.summary{ font-weight:700; }
table{ border-collapse:collapse; margin:1.2em auto 1.6em; font-size:15px;
  border:1.5px solid var(--ink); max-width:var(--measure);
  font-variant-numeric:lining-nums tabular-nums; }
table.wide{ max-width:var(--wide); font-size:12.5px; }
thead th{ background:var(--ink); color:var(--beige); font-weight:700; text-align:left;
  text-transform:uppercase; letter-spacing:.05em; font-size:.82em; padding:8px 11px; vertical-align:top; }
tbody td{ padding:7px 11px; border-top:1px solid var(--hair); vertical-align:top; }
tbody tr:nth-child(odd){ background:var(--tint); }
tbody tr:nth-child(even){ background:var(--beige); }
table code{ font-size:.92em; }
"""


def inline_html(text):
    out = []
    for part in INLINE_RE.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append("<strong>" + htmllib.escape(part[2:-2]) + "</strong>")
        elif part.startswith("`") and part.endswith("`"):
            out.append("<code>" + htmllib.escape(part[1:-1]) + "</code>")
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            out.append("<em>" + htmllib.escape(part[1:-1]) + "</em>")
        else:
            out.append(htmllib.escape(part))
    return "".join(out)


def table_html(tbl):
    cols = max(len(r) for r in tbl)
    head, body = tbl[0], tbl[1:]
    wide = "wide" if cols >= 8 else ""
    th = "".join(f"<th>{inline_html(c)}</th>" for c in head)
    rows = []
    for r in body:
        tds = "".join(f"<td>{inline_html(r[j]) if j < len(r) else ''}</td>" for j in range(cols))
        rows.append(f"<tr>{tds}</tr>")
    return f'<table class="{wide}"><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


def blocks_to_html(blocks):
    parts = []
    first_h1 = False
    seen_h2 = False
    lead_used = False
    i, n = 0, len(blocks)
    while i < n:
        kind, payload = blocks[i]
        if kind == "table":
            parts.append(table_html(payload))
            i += 1
            continue
        if kind == "bullet":
            items = []
            while i < n and blocks[i][0] == "bullet":
                items.append(f"<li>{inline_html(blocks[i][1])}</li>")
                i += 1
            parts.append("<ul>" + "".join(items) + "</ul>")
            continue
        if kind == "quote":
            paras = []
            while i < n and blocks[i][0] == "quote":
                paras.append(f"<p>{inline_html(blocks[i][1])}</p>")
                i += 1
            parts.append("<blockquote>" + "".join(paras) + "</blockquote>")
            continue
        if kind == "h1":
            cls = "" if first_h1 else ' class="masthead"'
            parts.append(f"<h1{cls}>{inline_html(payload)}</h1>")
            first_h1 = True
        elif kind == "h2":
            seen_h2 = True
            parts.append(f"<h2>{inline_html(payload)}</h2>")
        elif kind == "h3":
            parts.append(f"<h3>{inline_html(payload)}</h3>")
        elif kind == "summary":
            parts.append(f'<p class="summary">▸ {inline_html(payload)}</p>')
        elif kind == "hr":
            parts.append('<div class="fleuron"><span>❧</span></div>')
        else:  # "p"
            cls = ""
            if first_h1 and not seen_h2 and not lead_used:
                cls = ' class="lead"'
                lead_used = True
            parts.append(f"<p{cls}>{inline_html(payload)}</p>")
        i += 1
    return "\n".join(parts)


def logo_data_uri():
    if not LOGO.exists():
        return None
    try:
        from PIL import Image
        img = Image.open(LOGO)
        if img.mode not in ("RGBA", "RGB"):
            img = img.convert("RGBA")
        if max(img.size) > 320:
            ratio = 320 / max(img.size)
            img = img.resize((round(img.width * ratio), round(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        data = buf.getvalue()
    except Exception:
        data = LOGO.read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def build_html(md, logo=True):
    body = blocks_to_html(parse_blocks(md))
    logo_tag = ""
    if logo:
        uri = logo_data_uri()
        if uri:
            logo_tag = f'<img class="logo" src="{uri}" alt="SENSUM"/>'
    return (
        '<!DOCTYPE html><html lang="pl"><head><meta charset="utf-8">'
        f"<style>{CSS}</style></head><body><div class=\"page\">"
        f"{logo_tag}\n{body}</div></body></html>"
    )


def render_pdf(html, out_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        try:
            page.evaluate("() => document.fonts.ready.then(() => true)")
        except Exception:
            pass
        page.wait_for_timeout(400)
        dims = page.evaluate(
            "() => ({w: Math.ceil(document.body.scrollWidth), h: Math.ceil(document.body.scrollHeight)})"
        )
        page.emulate_media(media="screen")
        page.pdf(
            path=str(out_path),
            width=f"{dims['w']}px",
            height=f"{dims['h']}px",
            print_background=True,
            margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
        )
        browser.close()
    return dims


def convert(src: Path, out: Path, logo: bool = True):
    md = src.read_text(encoding="utf-8")
    html = build_html(md, logo=logo)
    out.parent.mkdir(parents=True, exist_ok=True)
    dims = render_pdf(html, out)
    return out, dims


def _expand(paths):
    files = []
    for pat in paths:
        if any(ch in pat for ch in "*?["):
            files.extend(sorted(globmod.glob(pat)))
        else:
            files.append(pat)
    return [Path(f) for f in files]


def main():
    ap = argparse.ArgumentParser(description="Konwerter Markdown -> jeden dlugi PDF w stylu SENSUM.")
    ap.add_argument("paths", nargs="+", help="pliki .md lub glob (np. docs/research/*.md)")
    ap.add_argument("--out", default=None, help="katalog wyjsciowy (domyslnie obok zrodla)")
    ap.add_argument("--no-logo", action="store_true", help="bez logo SENSUM na gorze")
    args = ap.parse_args()

    srcs = [p for p in _expand(args.paths) if p.suffix.lower() == ".md" and p.exists()]
    if not srcs:
        print("Brak plikow .md do konwersji.")
        return
    out_dir = Path(args.out) if args.out else None
    for src in srcs:
        out = (out_dir / (src.stem + ".pdf")) if out_dir else src.with_suffix(".pdf")
        try:
            written, dims = convert(src, out, logo=not args.no_logo)
            kb = written.stat().st_size // 1024
            print(f"OK  {src.name} -> {written}  ({dims['w']}x{dims['h']}px, {kb} KB)")
        except Exception as ex:
            print(f"FAIL {src.name}: {ex}")
    print("DONE")


if __name__ == "__main__":
    main()
