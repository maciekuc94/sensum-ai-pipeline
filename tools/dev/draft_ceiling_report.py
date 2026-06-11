"""Gen 5 measurement loop — how far is the machine from the user's ceiling?

Compares the untouchable machine snapshot (md/04_final_machine.md; fallback
md/04_final.md) against the user's final edit (md/script_corrected.md) and
prints: words before/after (cut-rate), sentence buckets (identical / modified /
deleted / added), % of machine sentences touched. Run after each docx pass to
trend whether doctrine changes reduce manual work.

Usage:
    PYTHONIOENCODING=utf-8 python tools/dev/draft_ceiling_report.py "<slug>"
"""

import argparse
import difflib
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import get_output_dir

SENT_RE = re.compile(r"[^.!?…]+[.!?…]+(?:\s|$)|[^.!?…]+$", re.S)
SIMILAR = 0.85


def _narration(text: str) -> str:
    return " ".join(l.strip() for l in text.splitlines()
                    if l.strip() and not l.strip().startswith("#"))


def split_sentences(text: str) -> list[str]:
    return [m.group(0).strip() for m in SENT_RE.finditer(_narration(text))
            if m.group(0).strip()]


def sentence_diff_stats(machine: str, human: str) -> dict:
    ms, hs = split_sentences(machine), split_sentences(human)
    used: set[int] = set()
    identical = modified = 0
    for m in ms:
        best_ratio, best_j = 0.0, -1
        for j, h in enumerate(hs):
            if j in used:
                continue
            r = difflib.SequenceMatcher(None, m, h).ratio()
            if r > best_ratio:
                best_ratio, best_j = r, j
        if best_ratio == 1.0:
            identical += 1
            used.add(best_j)
        elif best_ratio >= SIMILAR:
            modified += 1
            used.add(best_j)
    deleted = len(ms) - identical - modified
    added = len(hs) - len(used)
    pct = (len(ms) - identical) / len(ms) * 100 if ms else 0.0
    return {
        "machine_total": len(ms), "human_total": len(hs),
        "identical": identical, "modified": modified,
        "deleted": deleted, "added": added,
        "machine_words": len(_narration(machine).split()),
        "human_words": len(_narration(human).split()),
        "pct_touched": pct,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Gen 5 — diff maszyna vs redakcja usera")
    parser.add_argument("slug")
    args = parser.parse_args()
    md = get_output_dir(args.slug) / "md"

    machine_path = md / "04_final_machine.md"
    if not machine_path.exists():
        machine_path = md / "04_final.md"
    human_path = md / "script_corrected.md"
    if not human_path.exists():
        print(f"Error: {human_path} nie istnieje — najpierw ekstrakcja docx "
              f"(np. /visuals albo agent5_visuals.py --extract).")
        sys.exit(1)

    s = sentence_diff_stats(machine_path.read_text(encoding="utf-8"),
                            human_path.read_text(encoding="utf-8"))
    cut = (1 - s["human_words"] / s["machine_words"]) * 100 if s["machine_words"] else 0.0
    print(f"=== draft_ceiling_report: {args.slug} (machine: {machine_path.name}) ===")
    print(f"Słowa: {s['machine_words']} -> {s['human_words']}  (cut-rate {cut:+.1f}% maszyny)")
    print(f"Zdania maszyny: {s['machine_total']}  | identyczne {s['identical']}"
          f" | zmienione {s['modified']} | usunięte {s['deleted']} | dodane od zera {s['added']}")
    print(f"Dotknięte: {s['pct_touched']:.0f}% zdań maszyny")


if __name__ == "__main__":
    main()
