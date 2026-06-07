# -*- coding: utf-8 -*-
"""
md_to_docx_sensum.py — konwerter dowolnego Markdown -> Word .docx w STYLU SENSUM.

JEDNO ZRODLO PRAWDY o brandowym docx. Styl marki jest zaszyty tutaj — nie odtwarzaj
go recznie i nie uzywaj tools/utils.export_to_docx (to nie-brandowy eksporter pipeline'u,
motyw Office, przykuty do outputs/videos_pl/).

Styl: tlo bezowe #F4E5CA, atrament brazowy #582F0E, font EB Garamond, logo SENSUM na gorze,
tabele z brazowym paskiem naglowka (bezowy tekst) na bezowych komorkach, brazowe ramki.
Obsluga md: H1/H2/H3, **bold**, `code`, listy (- / *), cytaty (>), tabele GFM,
<details>/<summary>, --- (pomijane).

Uzycie (z korzenia repo):
  PYTHONIOENCODING=utf-8 python tools/dev/md_to_docx_sensum.py <plik.md> [<plik2.md> ...]
  ... [--out <katalog>]   # domyslnie .docx laduje obok zrodla
  ... [--no-logo]         # bez logo na gorze
Wspiera tez glob: "docs/research/*.md"
"""
import argparse
import glob as globmod
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / "outputs" / "channel_assets" / "SENSUM_LOGO.png"

# --- Jedno zrodlo prawdy: paleta + fonty SENSUM ---
BROWN = RGBColor(0x58, 0x2F, 0x0E)
BEIGE = RGBColor(0xF4, 0xE5, 0xCA)
BROWN_HEX = "582F0E"
BEIGE_HEX = "F4E5CA"
BODY_FONT = "EB Garamond"
MONO_FONT = "Consolas"

SEP_RE = re.compile(r"^\s*\|?(\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")


def style_run(r, color=BROWN, font=BODY_FONT, bold=None, italic=None):
    r.font.color.rgb = color
    r.font.name = font
    rpr = r._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), font)
    rfonts.set(qn("w:hAnsi"), font)
    rfonts.set(qn("w:cs"), font)
    if bold is not None:
        r.bold = bold
    if italic is not None:
        r.italic = italic


def add_inline(p, text, color=BROWN, italic=None):
    for part in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            style_run(p.add_run(part[2:-2]), color, BODY_FONT, bold=True, italic=italic)
        elif part.startswith("`") and part.endswith("`"):
            style_run(p.add_run(part[1:-1]), color, MONO_FONT, italic=italic)
        else:
            style_run(p.add_run(part), color, BODY_FONT, italic=italic)


def set_page_background(doc, hexcolor):
    bg = OxmlElement("w:background")
    bg.set(qn("w:color"), hexcolor)
    doc.element.insert(0, bg)
    doc.settings.element.append(OxmlElement("w:displayBackgroundShape"))


def shade(cell, hexcolor):
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcolor)
    cell._tc.get_or_add_tcPr().append(shd)


def set_table_borders(table, hexcolor):
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), "4")
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), hexcolor)
        borders.append(el)
    table._tbl.tblPr.append(borders)


def setup_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(11.5)
    normal.font.color.rgb = BROWN
    for lvl, size in [(1, 22), (2, 16), (3, 13)]:
        st = doc.styles[f"Heading {lvl}"]
        st.font.name = BODY_FONT
        st.font.bold = True
        st.font.color.rgb = BROWN
        st.font.size = Pt(size)


def add_table(doc, buf):
    cols = max(len(r) for r in buf)
    padded = [r + [""] * (cols - len(r)) for r in buf]
    header, body = padded[0], padded[1:]
    table = doc.add_table(rows=1 + len(body), cols=cols)
    set_table_borders(table, BROWN_HEX)
    for i, txt in enumerate(header):
        cell = table.rows[0].cells[i]
        shade(cell, BROWN_HEX)
        cell.text = ""
        add_inline(cell.paragraphs[0], txt, color=BEIGE)
        for r in cell.paragraphs[0].runs:
            r.bold = True
    for ri, row in enumerate(body, start=1):
        for i, txt in enumerate(row):
            cell = table.rows[ri].cells[i]
            shade(cell, BEIGE_HEX)
            cell.text = ""
            add_inline(cell.paragraphs[0], txt)
    doc.add_paragraph()


def convert(src: Path, out: Path, logo: bool = True):
    md = src.read_text(encoding="utf-8")
    doc = Document()
    setup_styles(doc)
    set_page_background(doc, BEIGE_HEX)
    if logo and LOGO.exists():
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(LOGO), width=Inches(1.7))
        doc.add_paragraph()

    buf = []
    for raw in md.splitlines():
        s = raw.strip()
        if s.startswith("|") and s.endswith("|") and "|" in s[1:]:
            if SEP_RE.match(s):
                continue
            inner = s[1:-1]
            buf.append([c.strip() for c in inner.split("|")])
            continue
        if buf:
            add_table(doc, buf)
            buf = []
        if s.startswith("<details") or s.startswith("</details"):
            continue
        m = re.match(r"<summary>(.*?)</summary>", s)
        if m:
            p = doc.add_paragraph()
            add_inline(p, "▸ " + m.group(1))
            for r in p.runs:
                r.bold = True
            continue
        if s.startswith("### "):
            add_inline(doc.add_heading(level=3), s[4:])
        elif s.startswith("## "):
            add_inline(doc.add_heading(level=2), s[3:])
        elif s.startswith("# "):
            add_inline(doc.add_heading(level=1), s[2:])
        elif s.startswith("> "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            add_inline(p, s[2:], italic=True)
        elif s == ">":
            continue
        elif s.startswith("- ") or s.startswith("* "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            style_run(p.add_run("•  "))
            add_inline(p, s[2:])
        elif s.startswith("---") or s == "":
            continue
        else:
            add_inline(doc.add_paragraph(), s)
    if buf:
        add_table(doc, buf)

    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return out


def _expand(paths):
    files = []
    for pat in paths:
        if any(ch in pat for ch in "*?["):
            files.extend(sorted(globmod.glob(pat)))
        else:
            files.append(pat)
    return [Path(f) for f in files]


def main():
    ap = argparse.ArgumentParser(description="Konwerter Markdown -> docx w stylu SENSUM.")
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
        out = (out_dir / (src.stem + ".docx")) if out_dir else src.with_suffix(".docx")
        try:
            written = convert(src, out, logo=not args.no_logo)
            print(f"OK  {src.name} -> {written}  ({written.stat().st_size} B)")
        except Exception as ex:
            print(f"FAIL {src.name}: {ex}")
    print("DONE")


if __name__ == "__main__":
    main()
