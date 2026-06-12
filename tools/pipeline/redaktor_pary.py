"""Redaktor-uczeń (Layer 3) — korpus par machine ↔ docx-pass do analizy wzorców.

Skanuje outputs/videos_pl/*/, dla każdego sluga z parą (04_final_machine.md,
fallback 04_final.md  ×  script_corrected.md) paruje zdania logiką
draft_ceiling_report (regex zdań + difflib, próg 0.85) i emituje
.tmp/redaktor_korpus.md: [MOD] (z diffem słów) / [DEL] / [ADD] w kolejności
dokumentu, z sekcją maszyny i tagiem generacji łańcucha. Zero tokenów, zero API.

Usage:
    PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "<slug>"

<slug> = świeżo skorygowany film: walidowany (musi mieć parę); jeśli
docx/script_corrected.docx jest nowszy niż md/script_corrected.md (albo md
brak), najpierw robiona jest ekstrakcja. Korpus ZAWSZE obejmuje wszystkie
slugi z parą.
"""

import argparse
import datetime as dt
import difflib
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.dev.draft_ceiling_report import SIMILAR, sentence_diff_stats, split_sentences
from tools.utils import read_script_docx_text

VIDEOS_DIR = Path(__file__).resolve().parents[2] / "outputs" / "videos_pl"
TMP_DIR = Path(__file__).resolve().parents[2] / ".tmp"


def pair_sentences(ms: list[str], hs: list[str]) -> dict:
    """Greedy best-match jak sentence_diff_stats, ale zwraca pary (indeksy).

    Kontrakt: liczby kubełków identyczne z sentence_diff_stats dla tych samych
    list zdań (test test_pair_sentences_zgodne_z_ceiling_report).
    """
    used: set[int] = set()
    identical: list[tuple[int, int]] = []
    modified: list[tuple[int, int, float]] = []
    for i, m in enumerate(ms):
        best_ratio, best_j = 0.0, -1
        for j, h in enumerate(hs):
            if j in used:
                continue
            r = difflib.SequenceMatcher(None, m, h).ratio()
            if r > best_ratio:
                best_ratio, best_j = r, j
        if best_ratio == 1.0:
            identical.append((i, best_j))
            used.add(best_j)
        elif best_ratio >= SIMILAR:
            modified.append((i, best_j, best_ratio))
            used.add(best_j)
    matched_m = {i for i, _ in identical} | {i for i, _, _ in modified}
    return {
        "identical": identical,
        "modified": modified,
        "deleted": [i for i in range(len(ms)) if i not in matched_m],
        "added": [j for j in range(len(hs)) if j not in used],
    }
