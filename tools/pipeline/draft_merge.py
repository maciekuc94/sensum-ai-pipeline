"""Draft chain (Gen 5) — deterministic merge of checker findings (Layer 3).

Merges outputs/videos_pl/{slug}/md/iter/ (arc.md + sek_*.md) into
md/03b_corrections.md: the [A] findings block from arc.md first (the
"## Mapa pętli" section is informational and stays OUT of corrections),
then sek_NN.md in document order, skipping files with no numbered findings.
Prints tag counters for the /draft report. No LLM, no network.

Usage:
    PYTHONIOENCODING=utf-8 python tools/pipeline/draft_merge.py "<slug>"
"""

import argparse
import re
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import get_output_dir

# Pozycja zgłoszenia = linia zaczynająca się numerem listy z tagiem [A]/[Z]/[K].
# Obsługuje zarówno plain [Z] jak i pogrubione **[Z]** (Markdown bold).
ITEM_RE = re.compile(r"^\s*\d+\.\s*\*{0,2}\[(A|Z|K)\]\*{0,2}", re.M)
ARC_FINDINGS_HEADER_RE = re.compile(r"^##\s*Zgłoszenia.*$", re.M)


def count_tags(text: str) -> dict:
    counts = {"A": 0, "Z": 0, "K": 0}
    for m in ITEM_RE.finditer(text):
        counts[m.group(1)] += 1
    return counts


def _arc_findings(text: str) -> str:
    """Zwróć część arc.md od nagłówka '## Zgłoszenia…' w dół (bez mapy pętli).
    Stary format (bez nagłówków) -> cały tekst."""
    m = ARC_FINDINGS_HEADER_RE.search(text)
    return text[m.start():] if m else text


def merge_corrections(iter_dir: Path) -> tuple[str, dict]:
    parts: list[str] = []
    arc_path = iter_dir / "arc.md"
    if arc_path.exists():
        findings = _arc_findings(arc_path.read_text(encoding="utf-8"))
        if ITEM_RE.search(findings):
            parts.append("## Łuk — zgłoszenia [A]\n\n" + findings.strip() + "\n")
    for sek in sorted(iter_dir.glob("sek_*.md")):
        text = sek.read_text(encoding="utf-8")
        if ITEM_RE.search(text):
            parts.append(f"## {sek.stem}\n\n" + text.strip() + "\n")
    if parts:
        body = "# Scalone korekty (3b)\n\n" + "\n".join(parts)
    else:
        body = "# Scalone korekty (3b)\n\nBrak zgłoszeń.\n"
    return body, count_tags(body)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gen 5 — scal iter/ do 03b_corrections.md")
    parser.add_argument("slug", help="Slug pod outputs/videos_pl/")
    args = parser.parse_args()

    md_dir = get_output_dir(args.slug) / "md"
    iter_dir = md_dir / "iter"
    if not iter_dir.is_dir():
        print(f"Error: {iter_dir} nie istnieje — najpierw ensemble checkerów (/draft Step 4).")
        sys.exit(1)

    body, counts = merge_corrections(iter_dir)
    out = md_dir / "03b_corrections.md"
    out.write_text(body, encoding="utf-8")
    print(f"Scalono -> {out}")
    print(f"Tagi: [A]={counts['A']} [Z]={counts['Z']} [K]={counts['K']} "
          f"(razem {sum(counts.values())})")


if __name__ == "__main__":
    main()
