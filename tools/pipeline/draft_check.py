"""Draft chain (Gen 5) — deterministic validator + docx export (Layer 3).

Validates md/04_final.md against the doctrine the chain must not violate
(report-only; the user decides on the docx pass):
  - every '## ' section of the frozen draft survived the fixer,
  - no research attribution in narration ("badania pokazują" itd.),
  - no digits in narration (numbers must be round words per voice canon),
  - no leftover checker artifacts [Z]/[K]/[A],
  - word count inside the writer window (default 1500-2200),
  - file present, non-empty, ends with sentence punctuation.

--export additionally writes docx/script.docx via tools.utils.export_to_docx
(the bookend formerly living in agent4_hook.py).

Usage:
    PYTHONIOENCODING=utf-8 python tools/pipeline/draft_check.py "<slug>" [--export]
"""

import argparse
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import get_output_dir, export_to_docx

BANNED_PATTERNS = [
    r"badania pokazują", r"badania potwierdzają", r"badania dowodzą",
    r"z badań wynika", r"naukowcy odkryli", r"wyniki badań",
]
ARTIFACT_RE = re.compile(r"\[(Z|K|A)\]")
HEADER_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def _headers(text: str) -> list[str]:
    return [m.group(1) for m in HEADER_RE.finditer(text)]


def _narration(text: str) -> str:
    return "\n".join(l for l in text.splitlines() if not l.strip().startswith("#"))


def validate_script(draft: str, final: str,
                    min_words: int = 1500, max_words: int = 2200) -> list[str]:
    findings: list[str] = []

    missing = [h for h in _headers(draft) if h not in _headers(final)]
    for h in missing:
        findings.append(f"Sekcja z draftu zniknęła w finale: \"## {h}\"")

    narration = _narration(final)
    low = narration.lower()
    for pat in BANNED_PATTERNS:
        for m in re.finditer(pat, low):
            findings.append(f"Atrybucja badań w narracji: \"…{narration[max(0, m.start()-20):m.end()+20].strip()}…\"")

    digit_lines = [l.strip() for l in narration.splitlines() if re.search(r"\d", l)]
    if digit_lines:
        findings.append(f"Cyfry w narracji ({len(digit_lines)} linii), np.: \"{digit_lines[0][:80]}\"")

    if ARTIFACT_RE.search(narration):
        findings.append("Artefakt checkerów [Z]/[K]/[A] został w finale.")

    words = len(narration.split())
    if not (min_words <= words <= max_words):
        findings.append(f"Liczba słów poza widełkami: {words} (cel {min_words}-{max_words}).")

    stripped = narration.strip()
    if not stripped:
        findings.append("Finał jest pusty.")
    elif stripped[-1] not in ".!?…\"”":
        findings.append(f"Plik wygląda na urwany — kończy się na: \"…{stripped[-40:]}\"")

    return findings


def main() -> None:
    parser = argparse.ArgumentParser(description="Gen 5 — walidacja 04_final.md + eksport docx")
    parser.add_argument("slug")
    parser.add_argument("--export", action="store_true", help="po walidacji wyeksportuj docx/script.docx")
    parser.add_argument("--min-words", type=int, default=1500)
    parser.add_argument("--max-words", type=int, default=2200)
    args = parser.parse_args()

    md_dir = get_output_dir(args.slug) / "md"
    final_path = md_dir / "04_final.md"
    draft_path = md_dir / "03a_draft.md"
    if not final_path.exists():
        print(f"Error: {final_path} nie istnieje — najpierw /draft.")
        sys.exit(1)

    final = final_path.read_text(encoding="utf-8")
    if draft_path.exists():
        draft = draft_path.read_text(encoding="utf-8")
    else:
        print(f"Uwaga: {draft_path} nie istnieje — pomijam sprawdzanie przetrwania sekcji.")
        draft = final

    findings = validate_script(draft, final, args.min_words, args.max_words)
    words = len(_narration(final).split())
    print(f"=== draft_check: {args.slug} ===")
    print(f"Słowa (bez nagłówków): {words}")
    print(f"Sekcje ## : {len(_headers(final))}")
    if findings:
        print(f"WERDYKT: {len(findings)} uwag(i) — przejrzyj przed nagraniem:")
        for f in findings:
            print(f"  - {f}")
    else:
        print("WERDYKT: CZYSTO — zero uwag.")

    if args.export:
        export_to_docx(
            args.slug, "md/04_final.md", "docx/script.docx",
            sentence_per_line=True, no_spacing=True, preserve_blank_lines=True,
        )
        print("Eksport -> docx/script.docx")


if __name__ == "__main__":
    main()
