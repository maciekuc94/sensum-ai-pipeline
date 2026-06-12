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


def machine_sentences_with_sections(text: str) -> list[tuple[str, str]]:
    """Zdania maszyny z nagłówkiem sekcji `## `, z której pochodzą.

    Tekst przed pierwszą sekcją dostaje etykietę "(otwarcie)". Linie nagłówków
    wycina _narration wewnątrz split_sentences, więc konkatenacja zdań ==
    split_sentences(text) — patrz test zgodności.
    """
    out: list[tuple[str, str]] = []
    header = "(otwarcie)"
    buf: list[str] = []

    def flush() -> None:
        for s in split_sentences("\n".join(buf)):
            out.append((s, header))

    for line in text.splitlines():
        if line.strip().startswith("## "):
            flush()
            header = line.strip()[3:].strip()
            buf = []
        else:
            buf.append(line)
    flush()
    return out


def word_diff(machine: str, human: str) -> str:
    """Diff słowo-po-słowie: [-usunięte-] {+dodane+}."""
    mw, hw = machine.split(), human.split()
    sm = difflib.SequenceMatcher(None, mw, hw)
    parts: list[str] = []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            parts.extend(mw[i1:i2])
        if op in ("delete", "replace"):
            parts.append("[-" + " ".join(mw[i1:i2]) + "-]")
        if op in ("insert", "replace"):
            parts.append("{+" + " ".join(hw[j1:j2]) + "+}")
    return " ".join(parts)


def strip_title(text: str) -> str:
    """Usuwa pierwszą niepustą linię, jeśli wygląda na tytuł (bez interpunkcji
    na końcu). script_corrected.md zaczyna się tytułem bez kropki — bez tego
    doklejałby się do pierwszego zdania i fałszował parę na otwarciu."""
    lines = text.splitlines()
    for k, line in enumerate(lines):
        s = line.strip()
        if not s:
            continue
        if s.startswith("#") or s[-1] in '.!?…""':
            return text
        return "\n".join(lines[k + 1:])
    return text


def detect_generation(md_dir: Path) -> str:
    """Tag generacji łańcucha /draft, po obecnych plikach snapshotu."""
    if (md_dir / "04_final_machine.md").exists():
        return "gen5"
    if (md_dir / "04_final_presqueeze.md").exists():
        return "sciskacz"
    return "lean"
