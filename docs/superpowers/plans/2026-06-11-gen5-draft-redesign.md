# Gen 5 /draft Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Przebudować łańcuch pisania skryptu na Gen 5 wg speca `brainstorms/2026-06-11-gen5-draft-redesign.md`: ściskacz (3d) i bramka `/hook` skasowane, architektura obietnic (curiosity loops) w pisarzu + arc-checkerze, długość 1500–2200 słów (film 10–15 min), scalanie korekt i walidacja jako deterministyczne skrypty, krótkie zwroty subagentów, nietykalny snapshot maszyny.

**Architecture:** Łańcuch po zmianie: pisarz (Opus) → ensemble równolegle (section-checkery Sonnet ×9–13 + arc-checker Opus z mapą pętli, na zamrożonym `03a_draft.md`) → `draft_merge.py` (skrypt) → fixer (Opus, aktywna klauzula pominięć → `iter/fixer_skips.md`) → snapshot `04_final_machine.md` → `draft_check.py --export` (walidacja + docx). Brak ściskacza, brak `/hook` — eksport docx i backstop doktryny przejmuje walidator; ocena otwarcia (Tier-1) przechodzi do reguły 5 pisarza i do arc-checkera.

**Tech Stack:** Python 3.10+ (stdlib + istniejące `tools/utils.py`: `get_output_dir`, `export_to_docx`), `unittest` (stdlib — repo nie ma pytest), markdown prompty, Claude Code slash command. Windows: każde wywołanie Pythona przez Bash z prefiksem `PYTHONIOENCODING=utf-8`.

**Źródło prawdy:** spec `brainstorms/2026-06-11-gen5-draft-redesign.md` (D1–D6). Przy konflikcie plan ↔ spec wygrywa spec.

---

## Mapa plików

| Akcja | Plik | Odpowiedzialność po zmianie |
|---|---|---|
| Create | `tools/pipeline/draft_merge.py` | Deterministyczne scalanie `iter/arc.md` + `iter/sek_*.md` → `md/03b_corrections.md` + liczniki tagów |
| Create | `tools/pipeline/draft_check.py` | Walidator finału (sekcje/zakazy/cyfry/widełki/artefakty) + `--export` docx |
| Create | `tools/dev/draft_ceiling_report.py` | Pętla pomiarowa: diff `04_final_machine` vs `script_corrected` |
| Create | `tests/test_draft_merge.py`, `tests/test_draft_check.py`, `tests/test_ceiling_report.py` | unittest (stdlib) |
| Rewrite | `workflows/pipeline/03a_writer.md` | + architektura obietnic, Tier-1 w regule 5, długość 1500–2200 |
| Rewrite | `workflows/pipeline/03b_arc_checker.md` | + mapa pętli, ocena otwarcia, wykonanie zamknięcia |
| Modify | `workflows/pipeline/03b_section_checker.md` | nagłówek Sonnet, anty-spłaszczenie, wariant-pierwszy |
| Modify | `workflows/pipeline/03c_fixer.md` | aktywna klauzula pominięć + log `iter/fixer_skips.md` |
| Modify | `.claude/agents/draft-{writer,section-checker,arc-checker,fixer}.md` | kontrakt krótkiego zwrotu (+ wzmianki o mapie/logu) |
| Rewrite | `.claude/commands/draft.md` | orkiestracja Gen 5 (merge skryptem, snapshot, walidator+eksport, raport) |
| Delete | `workflows/pipeline/03d_compressor.md`, `.claude/agents/draft-compressor.md` | ściskacz out (D1) |
| Delete | `.claude/commands/hook.md`, `workflows/pipeline/04_hook.md`, `tools/pipeline/agent4_hook.py`, `.claude/skills/score-hook/` | /hook out (D3) |
| Modify | `tools/utils.py:183` | komentarz: usunąć `/hook` z listy slash commands |
| Modify | `.claude/commands/{visuals,publish,package}.md`, `.claude/skills/{publish-package,write-script,package-thumbnail,render-images}/SKILL.md`, `.claude/skills/native-voice-guard/SKILL.md`, `workflows/pipeline/{07_package,08_publish,00_master}.md`, `workflows/guides/{file_naming,voice_brief}.md`, `CLAUDE.md` | wymiana odwołań /hook + ściskacz na stan Gen 5 |

**Konwencje obowiązujące w całym planie:**
- Komendy uruchamiaj przez narzędzie **Bash** (nie PowerShell) z prefiksem `PYTHONIOENCODING=utf-8`; ścieżki względne od rootu repo `D:\ClaudeCode\YouTube psychology`.
- Commit po każdym tasku; wiadomości kończ stopką `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Pliki markdown czytaj narzędziem Read przed Edit (wymóg harnessu). Edycje `old_string` muszą trafić bajt w bajt — kopiuj z Read, nie z tego planu, jeśli się rozjadą (plan pisany z working tree z 2026-06-11; przy rozjeździe wygrywa working tree + intencja speca).

---

### Task 0: Checkpoint — zacommituj zastany working tree

Branch `refactor/lean-draft-cutover` ma niezacommitowany poprzedni refactor (dedykowane typy `draft-*`, agent6c, zmiany align). Gen 5 musi startować z czystego stanu, żeby commity były czytelne.

**Files:** żadnych zmian treści — tylko git.

- [ ] **Step 0.1: Sprawdź stan**

Run: `git status --short`
Expected: linie `M` (draft.md, CLAUDE.md, agent_align.py, lib/*, align.md) + `??` (.claude/agents/draft-*.md, animate.md, agent6c_animate.py, 06c_animate.md, brainstorm 06-10, brainstorm 2026-06-11-gen5, docs/superpowers/plans/2026-06-11-gen5-draft-redesign.md).

- [ ] **Step 0.2: Commit checkpointu**

```bash
git add -A
git commit -m "refactor(draft): checkpoint pre-Gen5 — dedykowane typy draft-*, agent6c, align tweaks + spec i plan Gen 5

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 0.3: Zweryfikuj czysty tree**

Run: `git status --short`
Expected: pusto.

---

### Task 1: `tools/pipeline/draft_merge.py` — scalanie korekt (Layer 3)

Zastępuje Step 5 leada (dziś ≈45% kosztu przebiegu). Kontrakt: czyta `outputs/videos_pl/{slug}/md/iter/`, pisze `md/03b_corrections.md` (blok `[A]` z arc.md najpierw — bez mapy pętli, potem `sek_*.md` w kolejności numerów, z pominięciem plików bez zgłoszeń), drukuje liczniki tagów.

**Files:**
- Create: `tests/test_draft_merge.py`
- Create: `tools/pipeline/draft_merge.py`

- [ ] **Step 1.1: Napisz failing test**

Utwórz katalog `tests/` z pustym `tests/__init__.py`, potem `tests/test_draft_merge.py`:

```python
import unittest
from pathlib import Path
import tempfile

from tools.pipeline.draft_merge import merge_corrections, count_tags

ARC = """## Mapa pętli
- Otwarcie: pytanie o budzik -> domknięte w sekcji 06.

## Zgłoszenia [A]
1. [A] gdzie: Otwarcie + Zamknięcie · co nie gra: klamra niespłacona · jak spiąć: dopowiedz obraz budzika.
2. [A] gdzie: sekcje 03-04 · co nie gra: powtórzenie · jak spiąć: zredukuj do zdania.
"""

SEK_01 = """1. [Z] cytat: „ma ciało" · czemu zgrzyta: kalka · naturalna wersja: „jest namacalny".
2. [K] cytat: „Pomyśl. Bo to nie ty." · co się nie klei: fałszywe „bo" · jak skleić: usuń spójnik.
"""

SEK_02 = "Brak zgłoszeń w tej sekcji.\n"


class TestMerge(unittest.TestCase):
    def _build_iter(self, tmp: Path) -> Path:
        it = tmp / "iter"
        it.mkdir()
        (it / "arc.md").write_text(ARC, encoding="utf-8")
        (it / "sek_01.md").write_text(SEK_01, encoding="utf-8")
        (it / "sek_02.md").write_text(SEK_02, encoding="utf-8")
        return it

    def test_merge_order_and_skip(self):
        with tempfile.TemporaryDirectory() as td:
            body, counts = merge_corrections(self._build_iter(Path(td)))
            self.assertLess(body.index("[A]"), body.index("[Z]"))  # arc przed sekcjami
            self.assertNotIn("Mapa pętli", body)                    # mapa NIE wchodzi do korekt
            self.assertNotIn("Brak zgłoszeń", body)                 # sek_02 pominięta
            self.assertIn("sek_01", body)
            self.assertEqual(counts, {"A": 2, "Z": 1, "K": 1})

    def test_count_tags_ignores_prose_mentions(self):
        body = "naglowek o zgloszeniach [Z] i [K]\n1. [Z] cytat · x · y\n2. [K] cytat · x · y\n"
        self.assertEqual(count_tags(body), {"A": 0, "Z": 1, "K": 1})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 1.2: Uruchom — ma failować**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_draft_merge -v`
Expected: `ModuleNotFoundError: No module named 'tools.pipeline.draft_merge'`

- [ ] **Step 1.3: Implementacja**

`tools/pipeline/draft_merge.py`:

```python
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
ITEM_RE = re.compile(r"^\s*\d+\.\s*\[(A|Z|K)\]", re.M)
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
```

- [ ] **Step 1.4: Testy na zielono**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_draft_merge -v`
Expected: `OK` (2 testy).

- [ ] **Step 1.5: Weryfikacja na realnych danych (slug 4)**

Run: `PYTHONIOENCODING=utf-8 python tools/pipeline/draft_merge.py "4_stane_sie_swoim_rodzicem"`
Expected: `Tagi: [A]=2 [Z]=32 [K]=17 (razem 51)` — liczby z forensyki sluga 4. Jeśli liczniki się różnią, obejrzyj `outputs/videos_pl/4_stane_sie_swoim_rodzicem/md/iter/sek_01.md` i dopasuj `ITEM_RE` do realnego formatu pozycji (np. myślniki zamiast numeracji), aż liczniki się zgodzą. **Uwaga:** krok nadpisuje `03b_corrections.md` sluga 4 wersją scaloną skryptem — akceptowalne (treść zgłoszeń identyczna, znikają zdublowane nagłówki leada).

- [ ] **Step 1.6: Commit**

```bash
git add tests/__init__.py tests/test_draft_merge.py tools/pipeline/draft_merge.py outputs/videos_pl/4_stane_sie_swoim_rodzicem/md/03b_corrections.md
git commit -m "feat(draft): draft_merge.py — deterministyczne scalanie korekt ensemble (Gen 5 D5)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(Jeśli `outputs/` jest w `.gitignore`, git add tej ścieżki zwróci ostrzeżenie — pomiń ją wtedy w `git add`.)

---

### Task 2: `tools/pipeline/draft_check.py` — walidator + eksport docx (Layer 3)

Backstop doktryny po likwidacji ściskacza (D1) + dom dla eksportu docx po likwidacji /hook (D3). **Tylko raportuje** (exit 0 zawsze, poza brakiem pliku); decyzje podejmuje user.

**Files:**
- Create: `tests/test_draft_check.py`
- Create: `tools/pipeline/draft_check.py`

- [ ] **Step 2.1: Napisz failing test**

`tests/test_draft_check.py`:

```python
import unittest

from tools.pipeline.draft_check import validate_script

DRAFT = """## Otwarcie

Przespałeś budzik. To nie koniec świata.

## Zamknięcie

Może problem nigdy nie był w tobie.
"""

GOOD_FINAL = DRAFT  # te same sekcje, czysta narracja


class TestValidate(unittest.TestCase):
    def test_clean_script_passes(self):
        findings = validate_script(DRAFT, GOOD_FINAL, min_words=5, max_words=50)
        self.assertEqual(findings, [])

    def test_missing_section_flagged(self):
        final = GOOD_FINAL.replace("## Zamknięcie", "## Inny tytuł")
        findings = validate_script(DRAFT, final, min_words=5, max_words=50)
        self.assertTrue(any("Zamknięcie" in f for f in findings))

    def test_banned_attribution_flagged(self):
        final = GOOD_FINAL + "\nBadania pokazują, że to działa.\n"
        findings = validate_script(DRAFT, final, min_words=5, max_words=50)
        self.assertTrue(any("badania pokazują" in f.lower() for f in findings))

    def test_digits_and_tags_flagged(self):
        final = GOOD_FINAL + "\nAż 73 procent ludzi. [Z] artefakt.\n"
        findings = validate_script(DRAFT, final, min_words=5, max_words=60)
        self.assertTrue(any("cyfr" in f.lower() for f in findings))
        self.assertTrue(any("artefakt" in f.lower() or "[Z]" in f for f in findings))

    def test_word_window(self):
        findings = validate_script(DRAFT, GOOD_FINAL, min_words=1500, max_words=2200)
        self.assertTrue(any("words" in f.lower() or "słów" in f.lower() for f in findings))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2.2: Uruchom — ma failować**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_draft_check -v`
Expected: `ModuleNotFoundError: No module named 'tools.pipeline.draft_check'`

- [ ] **Step 2.3: Implementacja**

`tools/pipeline/draft_check.py`:

```python
"""Draft chain (Gen 5) — deterministic validator + docx export (Layer 3).

Validates md/04_final.md against the doctrine the chain must not violate
(report-only; the user decides on the docx pass):
  - every '## ' section of the frozen draft survived the fixer,
  - no research attribution in narration (\"badania pokazują\" itd.),
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
    draft = draft_path.read_text(encoding="utf-8") if draft_path.exists() else final

    findings = validate_script(draft, final, args.min_words, args.max_words)
    words = len(_narration(final).split())
    print(f"=== draft_check: {args.slug} ===")
    print(f"Słowa (bez nagłówków): {words}")
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
```

- [ ] **Step 2.4: Testy na zielono**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_draft_check -v`
Expected: `OK` (5 testów).

- [ ] **Step 2.5: Weryfikacja na realnych danych (slug 4, bez --export)**

Run: `PYTHONIOENCODING=utf-8 python tools/pipeline/draft_check.py "4_stane_sie_swoim_rodzicem"`
Expected: sekcje OK (zero „zniknęła"), zero atrybucji, zero artefaktów, **1 uwaga**: liczba słów ~1106 poza widełkami 1500–2200 (slug 4 to stara generacja — to poprawne zachowanie walidatora, nie bug).

- [ ] **Step 2.6: Commit**

```bash
git add tests/test_draft_check.py tools/pipeline/draft_check.py
git commit -m "feat(draft): draft_check.py — walidator doktryny + eksport docx (Gen 5 D5, sukcesja 3d/hook)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 3: `workflows/pipeline/03a_writer.md` — architektura obietnic + Tier-1 + długość

Prompt pisarza (single source of truth). Pełna podmiana treści — reguły v2 zostają verbatim, zmieniają się: kontrakt zwrotu (linia 3), czas filmu (intro), reguła 5 (esencja Tier-1 z /hook), nowy blok „Architektura obietnic", długość, norma sekcji.

**Files:**
- Rewrite: `workflows/pipeline/03a_writer.md`

- [ ] **Step 3.1: Podmień całą treść pliku (Write)**

```markdown
# Agent 3a — Pisarz (zimny subagent Opus)

Dispatchowany na zimno. Twój zwrot = krótkie potwierdzenie zapisu (ścieżka +
liczba słów), NIE pełna treść pliku. Bez przykładów-kalibracji — pisz jak żywy
człowiek, nie jak dopasowywacz reguł.

---

Jesteś świetnym polskim autorem piszącym ciepłą, mądrą narrację do filmu na
YouTube (voiceover; finalny film ma mieć 10–15 minut). Kanał rozmawia z jedną
osobą o jej wewnętrznym życiu — o wstydzie, winie, lęku, zmęczeniu, o poczuciu,
że jest się „w tyle".

Lead daje ci **ścieżkę do badań** (po angielsku) i **temat**. Przeczytaj badania —
mają ci dać prawdę o zjawisku. Bierzesz z nich zrozumienie; wolno też trochę
odsłonić mechanizm w tekście, byle bez aparatu (patrz reguła 4).

Napisz całą narrację. Trzymaj się tych siedmiu rzeczy, i niczego poza nimi:

1. **Ciepło, do jednej osoby — ale wolno też wyjaśnić zjawisko.** Mówisz „ty",
   jak mądry przyjaciel, nie jak wykładowca. Głównie DO człowieka — czasem jednak
   wolno trochę wytłumaczyć mechanizm; zrozumienie pogłębia to, do czego
   prowadzisz.
2. **Uczucia nazywaj wprost.** Wstyd, wina, lęk, wyrzuty sumienia — to rdzeń, nie
   żargon. Nazywaj je po imieniu.
3. **Bez żargonu trudnego dla zwykłego człowieka.** Słowo, którego przeciętny
   człowiek nie rozumie („dysonans poznawczy", „kwantyfikator") — wytnij. Słowo
   zrozumiałe („układ nerwowy") jest w porządku. Test: czy zwykły człowiek to
   rozumie.
4. **Wyjaśniaj mechanizm, ale bez atrybucji do badań.** Wolno odsłonić odrobinę
   mechanizmu — ale jak rzecz, którą po prostu wiesz, **bez** „badania pokazują"
   w narracji (atrybucja żyje w opisie Agenta 8). Wciąż **bez** nazwisk badaczy,
   lat, decymali, effect-size, p-value, liczby badań / uczestników. Liczby tylko
   okrągłe i oprawione („blisko połowy"); jeśli liczba nie niesie emocji — wytnij.
5. **Otwórz hookiem, zamknij rozpoznaniem.** Otwórz konkretem, w którym człowiek
   się rozpozna („Przespałeś budzik.") — sceną albo pytaniem. **Pierwsze ~37 słów
   to bramka:** pierwsze zdanie krótkie (≤14 słów) i konkretne; do słowa ~37 musi
   paść szczegół albo obraz, przy którym widz pomyśli „to ja"; zero rozbiegu,
   zero abstrakcyjnych rzeczowników na starcie, żadnego „w tym filmie". Zamknij
   tak, żeby zobaczył coś o sobie — nie instrukcją, nie listą kroków. Recognition
   close zawsze ostatni.
6. **Część praktyczna — opcjonalna i lekka.** Mały konkretny ruch („Czasem
   wystarczy…") tylko jeśli sam wynika z treści. Jeśli nie pasuje — pomiń, idź
   prosto do zamknięcia. Nigdy numerowana lista.
7. **Naturalny mówiony polski.** Pisz tak, jak Polak mówi na głos do drugiej
   osoby. Rodzaj męski generyczny zawsze OK — używaj go, kiedykolwiek trzeba.

**Architektura obietnic (retencja).** Pełnej odpowiedzi na pytanie tytułu nie
oddawaj przed zamknięciem — odsłaniaj ją warstwami. Każda sekcja, zanim domknie
swoją myśl, otwiera następne pytanie: raz zapowiedzią odwrócenia, raz paradoksem,
raz niedokończoną sceną — środki różne, bez jednego powtarzanego szablonu.
Zamknięcie domyka wszystkie otwarte pętle.

**Metafora — wolność, nie przymus.** Nie musisz trzymać się jednej metafory przez
cały tekst; wolno kilka obrazów, jeśli ożywiają tekst.

**Najważniejsze: pisz LUŹNO, jednym ruchem, nie broniąc się przed tą listą.** Nie
sil się na liryzm ani „ładne" zdania — naturalność wygrywa z ozdobnością. Po
każdym zdaniu sprawdź jedno: **czy Polak powiedziałby to na głos drugiej osobie?**
Jeśli to tylko coś, co dało się napisać — przepisz prościej.

**Długość: 1500–2200 słów** (film 10–15 minut po redakcji).

**Zapis:** czysta narracja w markdown, sekcje oddzielone krótkimi roboczymi
nagłówkami `## ` (np. `## Otwarcie`); zwykle 9–13 sekcji — jedna sekcja to
~60–90 sekund mówienia. Żadnych metadanych, żadnych komentarzy o tekście — tylko
sam scenariusz.
```

- [ ] **Step 3.2: Commit**

```bash
git add workflows/pipeline/03a_writer.md
git commit -m "feat(draft): pisarz Gen 5 — architektura obietnic, bramka 37 słów w regule 5, 1500-2200 słów (D2/D3/D4)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: `workflows/pipeline/03b_arc_checker.md` — mapa pętli, otwarcie, wykonanie zamknięcia

**Files:**
- Rewrite: `workflows/pipeline/03b_arc_checker.md`

- [ ] **Step 4.1: Podmień całą treść pliku (Write)**

```markdown
# Agent 3b — Arc checker: spójność całości (zimny subagent Opus)

Dispatchowany na zimno. Twój zwrot = krótkie potwierdzenie zapisu (ścieżka +
liczba zgłoszeń `[A]`), NIE treść pliku.

Czytasz **cały** scenariusz i patrzysz **wyłącznie na poziom całości** — to, czego
nie widać, gdy czyta się jedną sekcję. Pojedynczymi zdaniami i kalkami zajmują się
inni (section-checkery) — **nie duplikuj ich**; nie flaguj pojedynczego koślawego
zdania. Twój rewir to łuk, nie cegła.

## Czego szukasz
- **Pętle i obietnice (retencja).** Widz zostaje, dopóki coś jest otwarte.
  Sprawdź architekturę obietnic: czy każda sekcja, zanim domknie swoją myśl,
  otwiera następne pytanie? Flaguj: **dwie lub więcej sekcji z rzędu domkniętych
  „na płasko"** (długi odcinek bez żadnej nowej obietnicy), **przedwczesną pełną
  odpowiedź na pytanie tytułu** (po niej film nie ma już powodu trwać),
  **pętlę otwartą i nigdy niedomkniętą**.
- **Otwarcie (pierwsze ~37 słów) — pierwsza pętla filmu.** Flaguj, gdy: pierwsze
  zdanie jest długie albo abstrakcyjne; do słowa ~37 nie pada konkret, w którym
  widz się rozpozna; otwarcie zaczyna od meta („w tym filmie", „chcę ci
  opowiedzieć"); po 37 słowach nie zostaje żadne otwarte pytanie.
- **Spójność obrazów (v2 — bez przymusu jednej metafory).** Kilka metafor / obrazów
  jest OK, jeśli ożywiają tekst — **nie** flaguj drugiego obrazu tylko za to, że jest
  drugi. Flaguj **wyłącznie**: ten sam obraz użyty **niespójnie** (raz znaczy co
  innego niż wcześniej) albo dwa obrazy, które realnie **kłócą się** w jednym
  miejscu i mylą czytelnika.
- **Klamra (otwarcie ↔ zamknięcie).** Czy zamknięcie **spłaca** to, co otwarcie
  obiecało? Flaguj, gdy otwarcie stawia obraz / pytanie, którego zamknięcie nie
  domyka — albo gdy zamknięcie wprowadza zupełnie nowy obraz znikąd.
- **Wykonanie zamknięcia.** Ostatnie 1–2 beaty mają być proste i suche.
  Flaguj zamknięcie ozdobne, przegadane albo piętrzące obrazy — recognition close
  ma uderzać jednym zdaniem, nie bukietem.
- **Narastanie.** Czy tekst **buduje**, czy dreptasz w miejscu? Flaguj sekcję,
  która tylko **powtarza innymi słowami** to, co już padło wcześniej (powtórzenie
  międzysekcyjne).
- **Przejścia `##`→`##`.** Czy każda sekcja **podaje pałeczkę** następnej, czy
  stoją obok siebie jak osobne eseje? Flaguj twarde szwy — miejsca, gdzie czytelnik
  spada z jednej myśli w drugą bez mostka.

## Format — DWIE części, w tej kolejności

**Część 1 — `## Mapa pętli`** (zawsze; informacyjna — do raportu, NIE wchodzi do
scalonych korekt): jedna linia na pętlę:
`- otwarta: <sekcja> („<krótki cytat zapowiedzi>") → domknięta: <sekcja> / NIGDY`
Po liście jedno zdanie: które odcinki są bez żadnej otwartej pętli (od–do
sekcji), albo `Pokrycie ciągłe.`

**Część 2 — `## Zgłoszenia [A]`** — ponumerowana lista markdown, każda pozycja
otagowana `[A]`:
- **gdzie** — której sekcji / których dwóch sekcji dotyczy (nazwy nagłówków) +
  krótki cytat kotwiczący,
- **co nie gra na poziomie całości** — płaski odcinek bez obietnicy /
  przedwczesna odpowiedź na tytuł / niedomknięta pętla / słabe otwarcie /
  ozdobne zamknięcie / niespójny obraz / niespłacona klamra / powtórzenie /
  twardy szew,
- **jak spiąć** — najmniejszy ruch, który to scala (mostek między sekcjami,
  ujednolicenie obrazu, cięcie powtórzonej sekcji). Nie przepisuj — wskaż.

Bez wstępu i podsumowania. Jeśli zgłoszeń brak: w Części 2 napisz jedną linię
`Łuk trzyma — brak zgłoszeń.` (Część 1 — mapę pętli — zapisz zawsze).
```

- [ ] **Step 4.2: Commit**

```bash
git add workflows/pipeline/03b_arc_checker.md
git commit -m "feat(draft): arc-checker Gen 5 — mapa pętli + ocena otwarcia + wykonanie zamknięcia (D2/D3/D5)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: `workflows/pipeline/03b_section_checker.md` — anty-spłaszczenie + wariant-pierwszy + nagłówek Sonnet

**Files:**
- Rewrite: `workflows/pipeline/03b_section_checker.md`

- [ ] **Step 5.1: Podmień całą treść pliku (Write)**

```markdown
# Agent 3b — Section checker: zdania + kontekst (zimny subagent Sonnet)

Dispatchowany na zimno. Twój zwrot = krótkie potwierdzenie zapisu (ścieżka +
liczba zgłoszeń `[Z]`/`[K]`), NIE treść pliku. **Bez przykładów-kalibracji** —
czytaj native'owym uchem, nie listą zakazów.

Lead przydzielił ci **jedną sekcję** `## ` całego scenariusza. Pozostałe sekcje
sprawdzają równolegle inni — nie zajmuj się nimi.

---

## Co dostajesz
- Ścieżkę do **całego** scenariusza (`03a_draft.md`).
- **Nagłówek twojej sekcji** (dokładny, np. `## Skąd się wziął sędzia`) — to twój
  rewir.

## Jak czytać
Przeczytaj cały plik, ale wzrok trzymaj na swojej sekcji. Przeczytaj ją razem z
**akapitem przed** i **akapitem po** (z sąsiednich sekcji) — żeby słyszeć kontekst,
w którym te zdania padają. **Flaguj tylko zdania ze SWOJEJ sekcji.** Sąsiednie
akapity są po to, żebyś rozumiał wejście i wyjście — nie po to, żeby je poprawiać.

Ten tekst napisała AI. Załóż, że są w nim zdania, których żaden Polak nie
powiedziałby na głos — **oraz** miejsca, gdzie dwa zdania osobno brzmią OK, ale
razem nie kleją się w sens. Twoim zadaniem jest znaleźć jedno i drugie. Nie chwal
tekstu. Jeśli się wahasz — i tak wpisz.

## Dwa przejścia — w tej kolejności

**[Z] — Zdania (mikroskop).** Przejdź swoją sekcję zdanie po zdaniu. Dla każdego
jedno pytanie: *czy Polak powiedziałby to na głos drugiej osobie — czy to tylko
coś, co dało się napisać?* Szukaj kalek z angielskiego, koślawego szyku,
książkowych konstrukcji, dosłowności („ma ciało"), „przetłumaczonej" składni.
**To, że zdanie gładko płynie z poprzednim, NIE usprawiedliwia kalki** — gładki
kontekst nie znosi zgrzytu w samym zdaniu.

**Obrazowość ≠ kalka.** Rodzimy idiom („przejmuje stery") i żywy konkret („Nie
mówi się o nim przy obiedzie.") **nie są błędem** — flagujesz to, czego Polak by
**nie powiedział**, nie to, co jest „pisane", obrazowe albo ozdobne. Nie
spłaszczaj żywego zdania do bezbarwnego.

**[K] — Kontekst (szersza soczewka).** Teraz patrz, jak zdania w twojej sekcji
**łączą się ze sobą**. Szukaj:
- fałszywego „bo" / „dlatego" — drugie zdanie udaje, że wynika z pierwszego, a nie
  wynika,
- skoku myślowego — brakuje ogniwa, czytelnik musi się domyślać,
- wiszącego odniesienia — „to", „ją", „doczepiona" bez jasnego, do czego się
  odnosi,
- dwóch zdań, z których każde osobno jest OK, ale **razem nie mają sensu** (np.
  „Pomyśl, kto ustawił zasady. Bo to nie ty je wymyśliłeś." — drugie nie domyka
  pierwszego),
- powtórzenia tej samej myśli innymi słowami w obrębie sekcji,
- metafory użytej w sekcji niespójnie.

## Format
Ponumerowana lista markdown. Każda pozycja **otagowana** `[Z]` albo `[K]`:

- `[Z]` — **cytat** (dokładny fragment) · **czemu zgrzyta** (kalka / szyk /
  książkowe / „tak się nie mówi") · **naturalna wersja** (jak powie żywy
  człowiek). Jeśli podajesz więcej niż jedną wersję — **najnaturalniejsza zawsze
  pierwsza** (fixer bierze pierwszą, gdy nie zdecyduje inaczej).
- `[K]` — **cytat** (oba zdania / fragment, którego dotyczy) · **co się nie klei**
  (fałszywe „bo" / skok / wiszące „to" / razem bez sensu / powtórzenie) · **jak
  skleić** (najmniejszy ruch: mostek, cięcie, dociągnięcie odniesienia — nie nowa
  metafora).

Bez wstępu, bez podsumowania, bez chwalenia — sama lista. Jeśli w twojej sekcji
naprawdę nic nie zgrzyta (rzadkie), napisz jedną linię: `Brak zgłoszeń w tej
sekcji.`
```

- [ ] **Step 5.2: Commit**

```bash
git add workflows/pipeline/03b_section_checker.md
git commit -m "feat(draft): section-checker Gen 5 — anty-spłaszczenie (FP filter), wariant-pierwszy, nagłówek Sonnet (D5)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: `workflows/pipeline/03c_fixer.md` — aktywna klauzula pominięć + log

**Files:**
- Rewrite: `workflows/pipeline/03c_fixer.md`

- [ ] **Step 6.1: Podmień całą treść pliku (Write)**

```markdown
# Agent 3c — Fixer (zimny subagent Opus)

Dispatchowany na zimno. Twój zwrot = krótki raport (ścieżki zapisanych plików +
ile poprawek wdrożonych / ile pominiętych), NIE treść pliku. Chirurgicznie,
**nie** całościowy rewrite.

---

Dostajesz scenariusz oraz **scaloną listę poprawek**. Każda pozycja jest
otagowana:
- `[Z]` — pojedyncze zdanie brzmi nie po polsku (cytat → naturalna wersja),
- `[K]` — dwa zdania w sekcji nie kleją się w sens (cytat → jak skleić),
- `[A]` — coś nie gra na poziomie całości (pętle / otwarcie / zamknięcie /
  metafora / klamra / przejście / powtórzenie → jak spiąć).

Jesteś tym samym modelem, co autor. Całościowy rewrite tylko wprowadzi nowe dziwne
zdania. Dlatego ruszasz **wyłącznie** to, co jest na liście, i tak mało, jak się
da.

## Kolejność — struktura przed zdaniem
**Najpierw `[A]` i `[K]`, dopiero potem `[Z]`.** Poprawki kontekstu i łuku są
**strukturalne** — wstawiasz krótki mostek, tniesz zbędne słowo, przepisujesz
przejście, dociągasz wiszące odniesienie. Zrób je pierwsze, bo zmieniają
sąsiedztwo, w którym potem siedzą podmiany zdań. Przy `[A]`/`[K]` trzymaj
**maksymalną powściągliwość**: najmniejszy ruch, który scala — **nigdy** nowa
metafora, **nigdy** przepisana cała sekcja. Jeśli zgłoszenie `[A]` każe wyciąć
powtórzoną sekcję, a to wyrwałoby dziurę — nie wycinaj, tylko zredukuj powtórzenie
do jednego zdania.

Potem `[Z]`: dla **każdego** zgłoszenia najpierw OSĄDŹ, potem działaj.

## Osąd per zgłoszenie — klauzula pominięcia (OBOWIĄZKOWA)
Dla każdego `[Z]` zadaj sobie jedno pytanie, ZANIM podmienisz: **czy proponowana
wersja jest naprawdę naturalniejsza od oryginału?**
- Jest lepsza → wstaw (przy kilku wariantach wolno wybrać dowolny; domyślnie
  pierwszy).
- Jest gorsza, cięższa, spłaszcza żywy obraz albo rodzimy idiom, wprowadza wiszące
  odniesienie → **POMIŃ i odnotuj w logu**. Checker bywa nadgorliwy — ty jesteś
  filtrem. Pominięcie uzasadnionej wątpliwości to poprawne działanie, nie
  nieposłuszeństwo.

## Szew i zgodność
Gdzie podmiana zrobiła zgrzyt na styku z sąsiednim zdaniem — lekko popraw
przejście. Jeśli podmiana zmieniła **rodzaj albo liczbę** słowa, do którego
odnoszą się dalsze zaimki / końcówki czasowników (np. „część ciebie…
powiedział**a**" → „coś w tobie… powiedział**o**", więc i następne „że
powiedział**a**" → „powiedział**o**") — **dociągnij zgodność** w sąsiedztwie.

## Zapis — DWA pliki
1. **CAŁY poprawiony scenariusz** w markdown, z zachowaniem nagłówków `## `, do
   pliku wskazanego w briefie. Bez komentarzy, bez listy zmian — tylko gotowy
   tekst.
2. **Log pominięć** do `md/iter/fixer_skips.md`: ponumerowana lista — cytat
   zgłoszenia + jedno zdanie, czemu oryginał zostaje. Jeśli niczego nie
   pominąłeś, zapisz jedną linię: `Brak pominięć.`
```

- [ ] **Step 6.2: Commit**

```bash
git add workflows/pipeline/03c_fixer.md
git commit -m "feat(draft): fixer Gen 5 — obowiązkowy osąd per [Z] + log pominięć iter/fixer_skips.md (D5)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 7: Definicje subagentów — krótki zwrot + mapa/log

Cztery pliki `.claude/agents/draft-*.md` (cienkie persony). Wszystkie edycje to Edit (Read przed Edit).

**Files:**
- Modify: `.claude/agents/draft-writer.md`
- Modify: `.claude/agents/draft-section-checker.md`
- Modify: `.claude/agents/draft-arc-checker.md`
- Modify: `.claude/agents/draft-fixer.md`

- [ ] **Step 7.1: draft-writer.md — kontrakt zwrotu**

Edit old_string:
```
- Twój zwrot (ostatnia wiadomość) = pełna treść zapisanego pliku.
```
new_string:
```
- Twój zwrot (ostatnia wiadomość) = krótki raport: ścieżka zapisanego pliku +
  liczba słów + jedno zdanie statusu. NIE wklejaj treści pliku.
```

- [ ] **Step 7.2: draft-section-checker.md — kontrakt zwrotu**

Edit old_string:
```
- Twój zwrot (ostatnia wiadomość) = pełna treść zapisanego pliku.
```
new_string:
```
- Twój zwrot (ostatnia wiadomość) = krótki raport: ścieżka pliku + liczba
  zgłoszeń [Z]/[K]. NIE wklejaj treści pliku.
```

- [ ] **Step 7.3: draft-arc-checker.md — zakres oceny + dwuczęściowy plik + kontrakt zwrotu**

Edit 1 — old_string:
```
2. Przeczytaj cały wskazany scenariusz i oceń łuk: metafory między sekcjami, klamrę
   (czy zamknięcie spłaca otwarcie), narastanie napięcia, przejścia.
3. Zapisz zgłoszenia `[A]` do pliku wskazanego w briefie.
```
new_string:
```
2. Przeczytaj cały wskazany scenariusz i oceń łuk: pętle i obietnice (retencja),
   otwarcie (pierwsze ~37 słów), metafory między sekcjami, klamrę (czy zamknięcie
   spłaca otwarcie), wykonanie zamknięcia, narastanie napięcia, przejścia.
3. Zapisz do pliku wskazanego w briefie DWIE części: `## Mapa pętli`, potem
   `## Zgłoszenia [A]` (format w prompcie).
```

Edit 2 — old_string:
```
- Twój zwrot (ostatnia wiadomość) = pełna treść zapisanego pliku.
```
new_string:
```
- Twój zwrot (ostatnia wiadomość) = krótki raport: ścieżka pliku + liczba
  zgłoszeń [A] + jedno zdanie o pokryciu pętli. NIE wklejaj treści pliku.
```

- [ ] **Step 7.4: draft-fixer.md — log pominięć + klauzula + kontrakt zwrotu**

Edit 1 — old_string:
```
3. Zapisz CAŁY poprawiony scenariusz do pliku wskazanego w briefie (zachowaj
   nagłówki `## `).
```
new_string:
```
3. Zapisz CAŁY poprawiony scenariusz do pliku wskazanego w briefie (zachowaj
   nagłówki `## `) oraz log pominięć do `md/iter/fixer_skips.md`.
```

Edit 2 — old_string:
```
- Minimalna ingerencja: zmieniasz to, co flagują zgłoszenia; reszty tekstu nie
  ulepszasz na własną rękę.
- Twój zwrot (ostatnia wiadomość) = pełna treść zapisanego pliku.
```
new_string:
```
- Minimalna ingerencja: zmieniasz to, co flagują zgłoszenia; reszty tekstu nie
  ulepszasz na własną rękę.
- Klauzula pominięcia to obowiązek, nie opcja: propozycję wyraźnie gorszą od
  oryginału pomijasz i odnotowujesz w logu — nie wstawiasz mechanicznie.
- Twój zwrot (ostatnia wiadomość) = krótki raport: ścieżki obu plików + ile
  poprawek wdrożonych / ile pominiętych. NIE wklejaj treści plików.
```

- [ ] **Step 7.5: Commit**

```bash
git add .claude/agents/draft-writer.md .claude/agents/draft-section-checker.md .claude/agents/draft-arc-checker.md .claude/agents/draft-fixer.md
git commit -m "feat(draft): definicje subagentów Gen 5 — krótkie zwroty, mapa pętli (arc), log pominięć (fixer)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: `.claude/commands/draft.md` — orkiestracja Gen 5

Pełna podmiana treści (Write). To jedyne źródło procedury leada.

**Files:**
- Rewrite: `.claude/commands/draft.md`

- [ ] **Step 8.1: Podmień całą treść pliku (Write)**

````markdown
---
description: Łańcuch skryptu SENSUM (Gen 5, 2026-06-11) — pisarz → ensemble (section-checker na każde ## + 1 arc-checker z mapą pętli, równolegle, na zamrożonym oryginale) → scalenie skryptem → fixer (klauzula pominięć) → snapshot → walidator + eksport docx. Jeden przebieg, bez pętli, in-session, no API. Finalną redakcję (w tym cięcie przegadania) robisz na docx.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob, Agent
---

# /draft — pisarz → section+arc checkery (ensemble) → fixer → walidator

Zimne konteksty, każdy ślepy na pozostałe — dedykowani specjaliści
`.claude/agents/draft-*.md` z modelem przypiętym we frontmatter wg roli (Opus:
pisarz/fixer/arc, Sonnet: section-checkery); Ty (lead) tylko przekazujesz
pliki i kolejność. Jeden przebieg:
- **pisarz** pisze cały skrypt luźno (1500–2200 słów = film 10–15 min;
  architektura obietnic: każda sekcja otwiera następne pytanie, pełna odpowiedź
  na tytuł dopiero przy zamknięciu),
- na **zamrożonym** drafcie rusza **ensemble checkerów równolegle**: jeden
  **section-checker na każde `## `** (zdania `[Z]` + kontekst `[K]` w obrębie
  sekcji) **plus jeden arc-checker** (mapa pętli + zgłoszenia `[A]`: pętle i
  obietnice, otwarcie ~37 słów, metafory, klamra, wykonanie zamknięcia,
  narastanie, przejścia),
- **`draft_merge.py`** (skrypt, zero tokenów) scala zgłoszenia do
  `03b_corrections.md`,
- **fixer** wstawia poprawki chirurgicznie — najpierw struktura (`[A]`/`[K]`),
  potem zdania (`[Z]`); propozycję wyraźnie gorszą od oryginału POMIJA i loguje
  (`iter/fixer_skips.md`),
- **snapshot**: kopia `04_final_machine.md` — NIETYKALNA,
- **`draft_check.py --export`** waliduje doktrynę (sekcje / atrybucja badań /
  cyfry / widełki słów / artefakty) i eksportuje `docx/script.docx`.

**Dlaczego ensemble na zamrożonym oryginale, nie pętla.** Iterowanie
checker→fixer→checker na **zmieniającej się** kopii **dryfuje** — własna poprawka
fixera staje się następnym zgłoszeniem checkera i tekst pływa bez zbieżności. Tu
każdy checker czyta **ten sam, zamrożony `03a_draft.md`** i nigdy nie widzi cudzych
poprawek → poprawka nie może stać się nowym błędem. Różne zimne odczyty łapią różne
podzbiory zgrzytów; bierzemy ich **sumę**, nie sekwencję.

**Dlaczego osobno sekcja i łuk.** Section-checker zamknięty w jednej sekcji nie
zobaczy, że metafora pęka między sekcjami, że pętla ciekawości nigdy się nie
domyka albo że zamknięcie nie spłaca otwarcia — to widać tylko z lotu ptaka.
Arc-checker robi dokładnie to i **nie** dubluje zdań.

**Gen 5 — nie ma ściskacza ani osobnej bramki `/hook`.** Cięcie przegadania
robisz Ty na docx (decyzja 2026-06-11); bramkę hooka zastąpiły: reguła 5 pisarza
(bramka 37 słów) + ocena otwarcia w arc-checkerze; backstop doktryny i eksport
docx przejął `draft_check.py`. Rationale:
`brainstorms/2026-06-11-gen5-draft-redesign.md`.

Kanon głosu: `workflows/guides/voice_brief.md` (v2). Prompty (single source of
truth): `03a_writer.md`, `03b_section_checker.md`, `03b_arc_checker.md`,
`03c_fixer.md`. **Każdy subagent czyta swój prompt sam** — Ty go nie streszczasz.
Definicje specjalistów (`.claude/agents/draft-*.md`) są celowo cienkie — persona +
twarde reguły; procedura zostaje wyłącznie w plikach-promptach (zero dublowania).

`$1` = slug pod `outputs/videos_pl/`.

---

## Step 1 — Walidacja
Potwierdź, że istnieje `outputs/videos_pl/$1/md/02_verified_research.md`. Brak →
powiedz userowi, żeby najpierw uruchomił
`PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "$1"`, i zatrzymaj się.

## Step 2 — Pisarz (zimny subagent Opus)
Zespawnuj subagenta (`Agent`, `subagent_type: draft-writer`) z
briefem dokładnie tej treści:

> Jesteś pisarzem SENSUM, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03a_writer.md` i wykonaj go dokładnie. Badania (tło, po
> angielsku): `outputs/videos_pl/$1/md/02_verified_research.md` — przeczytaj je.
> Temat wynika z badań (slug: `$1`). Zapisz gotową narrację do
> `outputs/videos_pl/$1/md/03a_draft.md` (markdown, sekcje `## `, żadnych
> metadanych). Twój zwrot = krótki raport (ścieżka + liczba słów), NIE treść
> pliku.

Poczekaj na ukończenie.

## Step 3 — Spis sekcji (Ty, in-session)
Wczytaj `outputs/videos_pl/$1/md/03a_draft.md`. Wypisz **w kolejności** wszystkie
nagłówki `## ` — to lista rewirów dla section-checkerów (zwykle 9–13 przy
1500–2200 słowach). Utwórz folder `outputs/videos_pl/$1/md/iter/`. Ten draft jest
od teraz **zamrożony** — żaden checker go nie zmienia.

## Step 4 — Ensemble checkerów (RÓWNOLEGLE — wszystkie spawny w JEDNEJ wiadomości)
Wyślij **wszystkie** poniższe spawny w **jednej** wiadomości (równoległość). Każdy
to świeży zimny specjalista — section-checkery jako `subagent_type:
draft-section-checker`, arc-checker jako `subagent_type: draft-arc-checker`
(model siedzi we frontmatter definicji).

**a) Po jednym section-checkerze na każdy nagłówek z kroku 3 (`draft-section-checker`).** Dla
sekcji o indeksie `NN` (`01`, `02`, …) i nagłówku `<HEADER>`:

> Jesteś native'owym redaktorem polskim, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03b_section_checker.md` i wykonaj go dokładnie. Cały
> scenariusz: `outputs/videos_pl/$1/md/03a_draft.md`. **Twoja sekcja: `<HEADER>`.**
> Flaguj tylko zdania w tej sekcji (sąsiednie akapity czytaj dla kontekstu, nie
> poprawiaj). Zapisz listę zgłoszeń do `outputs/videos_pl/$1/md/iter/sek_NN.md`.
> Twój zwrot = krótki raport (ścieżka + liczba zgłoszeń), NIE treść pliku.

**b) Jeden arc-checker (`draft-arc-checker`):**

> Jesteś redaktorem patrzącym na spójność całości, dispatchowanym na zimno.
> Przeczytaj `workflows/pipeline/03b_arc_checker.md` i wykonaj go dokładnie na całym
> `outputs/videos_pl/$1/md/03a_draft.md`. Zapisz do
> `outputs/videos_pl/$1/md/iter/arc.md` dwie części: `## Mapa pętli` i
> `## Zgłoszenia [A]`. Twój zwrot = krótki raport (ścieżka + liczba zgłoszeń +
> zdanie o pokryciu pętli), NIE treść pliku.

Poczekaj, aż **wszystkie** skończą.

## Step 5 — Scal listy (SKRYPT — nie rób tego ręcznie)
Uruchom (Bash):

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/draft_merge.py "$1"
```

Skrypt składa `outputs/videos_pl/$1/md/03b_corrections.md` (blok `[A]` z arc.md —
bez mapy pętli — potem `sek_NN.md` w kolejności, z pominięciem „Brak zgłoszeń")
i drukuje liczniki tagów `[A]/[Z]/[K]` — zanotuj je do raportu. Mapa pętli
celowo NIE wchodzi do korekt (zostaje w `iter/arc.md` — informacyjna).

## Step 6 — Fixer (świeży zimny subagent Opus)
Zespawnuj **nowego** subagenta (`subagent_type: draft-fixer`) z briefem:

> Jesteś redaktorem, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03c_fixer.md` i wykonaj go dokładnie. Scenariusz:
> `outputs/videos_pl/$1/md/03a_draft.md`. Scalona lista poprawek (tagi
> `[A]`/`[K]`/`[Z]`): `outputs/videos_pl/$1/md/03b_corrections.md`. Wstaw poprawki
> chirurgicznie — najpierw `[A]`/`[K]` (struktura), potem `[Z]` (zdania), każdą
> `[Z]` najpierw osądź (klauzula pominięcia) — i zapisz CAŁY poprawiony scenariusz
> do `outputs/videos_pl/$1/md/04_final.md` (zachowaj nagłówki `## `) oraz log
> pominięć do `outputs/videos_pl/$1/md/iter/fixer_skips.md`. Twój zwrot = krótki
> raport (ścieżki + wdrożone/pominięte), NIE treść plików.

Poczekaj na ukończenie.

## Step 6.5 — Snapshot maszyny (Bash)
Zachowaj nietykalną kopię wyniku maszyny:

```bash
cp "outputs/videos_pl/$1/md/04_final.md" "outputs/videos_pl/$1/md/04_final_machine.md"
```

**`04_final_machine.md` jest NIETYKALNY** — nigdy go nie nadpisuj ani nie
edytuj (także przy migracjach nazewnictwa). To podstawa pomiaru sufitu maszyny
(diff vs `script_corrected`).

## Step 7 — Walidator + eksport docx (Bash)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/draft_check.py "$1" --export
```

Walidator tylko raportuje (sekcje przetrwały / atrybucja badań / cyfry /
artefakty / widełki 1500–2200 słów / kompletność) i eksportuje
`docx/script.docx`. Uwagi NIE blokują — trafiają do raportu, decyzja należy do
usera na docx.

## Step 8 — Raport
Wczytaj `outputs/videos_pl/$1/md/04_final.md`. Zdaj userowi:
- liczbę słów finału i liczbę sekcji (z wyjścia `draft_check.py`),
- zgłoszenia łącznie `[A]` / `[Z]` / `[K]` (liczniki z `draft_merge.py`) + ile
  poprawek fixer pominął (przeczytaj `md/iter/fixer_skips.md` — wypisz powody),
- **MAPĘ PĘTLI** — zacytuj w całości sekcję `## Mapa pętli` z `md/iter/arc.md`
  (architektura obietnic skryptu na jeden rzut oka),
- werdykt walidatora (wypunktuj uwagi, jeśli są),
- ślad: `md/03a_draft.md` (surowy, zamrożony), `md/iter/sek_*.md` + `md/iter/arc.md`
  (zgłoszenia per checker), `md/03b_corrections.md` (scalone),
  `md/iter/fixer_skips.md` (pominięcia), `md/04_final.md` (finał),
  `md/04_final_machine.md` (nietykalny snapshot), `docx/script.docx` (eksport),
- **pokaż finalny scenariusz** w czacie do oceny,
- następne kroki: edytuj `docx/script.docx` (tam tniesz przegadanie) → zapisz
  jako `docx/script_corrected.docx` → nagranie; potem `/visuals $1` + `/publish
  $1` (równolegle), `/package $1` po `/draft` a przed `/publish`.

## Notes
- **Wszystkie checkery czytają zamrożony `03a_draft.md` — nigdy cudze poprawki.**
  To gwarancja braku dryfu. Nie spawnuj checkerów sekwencyjnie na zmieniającym się
  tekście.
- **Po jednym section-checkerze na `## `.** Policz nagłówki dynamicznie (9–13 to
  norma przy 1500–2200 słowach, ale bierz tyle, ile jest).
- **Nie tnij draftu na pliki-fragmenty.** Każdy checker dostaje ścieżkę do CAŁEGO
  draftu + swój nagłówek; czyta swoją sekcję z naturalną zakładką ±1 akapit.
  Karmienie pociętymi zdaniami zabija kontekst (to zabiło stary /refine).
- **Równoległość = wszystkie spawny kroku 4 w JEDNEJ wiadomości.**
- **Krótkie zwroty.** Żaden subagent nie wkleja treści pliku do czatu — Ty czytasz
  pliki z dysku. (Pełne zwroty podwajały koszt wyjścia każdego spawna i zaśmiecały
  Twój kontekst.)
- **Bez pętli, bez ściskacza, bez /hook.** Pisarz → ensemble → merge → fixer →
  snapshot → walidator i koniec. Twoje ucho na `script_corrected.docx` to ostatni
  sufit — tam tniesz przegadanie i ozdobniki (decyzja Gen 5, 2026-06-11).
- **Model wg roli (2026-06-09, utrzymane w Gen 5).** `opus`: pisarz (3a),
  arc-checker (3b/b), fixer (3c) — generacja głosu, osąd całości, integracja;
  **swap pisarza był testowany i zamknięty** (Sonnet/Gemini łamały reguły głosu).
  `sonnet`: section-checkery (3b/a, ×9–13) — detekcja wg jawnej rubryki `[Z]/[K]`.
  Haiku nigdzie — section-checker potrzebuje native'owego ucha do polszczyzny.
  Modele siedzą we frontmatter definicji `.claude/agents/draft-*.md`; param
  `model` w wywołaniu `Agent` **nadpisuje** frontmatter — tak robi się
  jednorazowe testy A/B innego modelu bez ruszania plików.
- **`04_final_machine.md` jest nietykalny.** Snapshot wyniku maszyny — nigdy nie
  nadpisywać (utrata snapshotu sluga 2 w migracji = bezpowrotnie stracony pomiar).
- **NIE** shelluj do `tools/pipeline/agent3*.py` — to martwa legacy ścieżka Gemini.
- Jeśli typ `draft-*` nie jest zarejestrowany (plik definicji dodany/zmieniony
  ręcznie w trakcie sesji — subagenci ładują się na starcie sesji): spawnuj
  `general-purpose` z modelem wg roli i tym samym briefem.
- Jeśli spawn subagenta zawiedzie całkiem: odpal danego agenta jako pojedyncze, **świeże,
  zimne przejście** in-session wg jego pliku-promptu, w tej samej kolejności i z
  tymi samymi plikami wyjściowymi. (Section-checkery można wtedy puścić
  sekwencyjnie — i tak czytają zamrożony oryginał, więc kolejność nie szkodzi.)
- Jeśli `draft_merge.py` / `draft_check.py` padnie: przeczytaj traceback, napraw
  narzędzie (Layer 3), powtórz krok. Nie rób scalania/walidacji ręcznie w sesji —
  to wraca do drogiego anty-wzorca, który te skrypty zastąpiły.
````

- [ ] **Step 8.2: Commit**

```bash
git add .claude/commands/draft.md
git commit -m "feat(draft): orkiestracja Gen 5 — merge+walidator skryptami, snapshot, krótkie zwroty, bez 3d i /hook (D1/D3/D5/D6)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

### Task 9: Emerytury — ściskacz + /hook (kasacje; git trzyma historię)

**Files:**
- Delete: `workflows/pipeline/03d_compressor.md`, `.claude/agents/draft-compressor.md`, `.claude/commands/hook.md`, `workflows/pipeline/04_hook.md`, `tools/pipeline/agent4_hook.py`, `.claude/skills/score-hook/` (cały katalog)
- Modify: `tools/utils.py` (komentarz)

- [ ] **Step 9.1: Kasacje przez git rm**

```bash
git rm workflows/pipeline/03d_compressor.md .claude/agents/draft-compressor.md .claude/commands/hook.md workflows/pipeline/04_hook.md tools/pipeline/agent4_hook.py
git rm -r .claude/skills/score-hook
```

Expected: 6 ścieżek usuniętych. (Eksport docx nie ginie — `export_to_docx` żyje w `tools/utils.py` i jest wołany przez `draft_check.py --export` z Task 2.)

- [ ] **Step 9.2: `tools/utils.py` — komentarz o slash commands**

Read `tools/utils.py` okolice linii 183, potem Edit — old_string:
```
# in-session in Claude Code on Opus 4.8 via slash commands (/draft, /hook,
```
new_string:
```
# in-session in Claude Code on Opus 4.8 via slash commands (/draft,
```
(Jeśli realna linia różni się drobnie, dopasuj — intencja: usunąć `/hook` z wyliczanki; reszta linii bez zmian.)

- [ ] **Step 9.3: Sanity — nic nie importuje skasowanego modułu**

Run: `grep -rn "agent4_hook" tools/ .claude/ workflows/ --include="*.py" --include="*.md"`
Expected: zero trafień (wszystkie odwołania w md znikają w Task 10/11/12; jeśli coś zostało — to jest lista do poprawki, wróć po Task 12 i sprawdź ponownie).

- [ ] **Step 9.4: Commit**

```bash
git add tools/utils.py
git commit -m "refactor(draft)!: emerytura ściskacza (3d) i bramki /hook — Gen 5 D1/D3

Kompresja przegadania -> docx-pass usera; Tier-1 -> reguła 5 pisarza;
ocena otwarcia -> arc-checker; eksport docx + backstop doktryny -> draft_check.py.
Safeguard: retencja @0:30 < ~55% na filmach 4-5 => przywrócić bramkę z gita.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 10: Wymiana odwołań — komendy, skille, workflowy, guides

Wszystkie edycje: Read przed Edit; old_string bajt w bajt z pliku.

**Files:** `.claude/commands/{visuals,publish,package}.md`, `workflows/pipeline/{07_package,08_publish}.md`, `workflows/guides/{file_naming,voice_brief}.md`, `.claude/skills/{publish-package,write-script,package-thumbnail,render-images,native-voice-guard}/SKILL.md`

- [ ] **Step 10.1: `.claude/commands/visuals.md` — usuń hook-gate check**

Usuń (Edit → new_string puste, razem ze znakiem nowej linii) bullet:
```
   - **Hook-gate check:** if `outputs/videos_pl/$1/md/04_hook.md` is absent, `/hook` has not run — warn that image prompts will be anchored to an un-gated opening (and `05_phrases.md` row 1, which feeds Align's SRT, will be the unreviewed first line); recommend `/hook $1` first. Warn and continue.
```

- [ ] **Step 10.2: `.claude/commands/publish.md`**

old: ``If none exists, tell the user to run `/draft $1` then `/hook $1` first, and stop.``
new: ``If none exists, tell the user to run `/draft $1` first, and stop.``

- [ ] **Step 10.3: `.claude/commands/package.md` — 3 edycje**

(1) old: ``Runs **after `/hook`, before `/publish`** — its titles feed Agent 8.``
    new: ``Runs **after `/draft`, before `/publish`** — its titles feed Agent 8.``
(2) old: ``If none exists, tell the user to run `/draft $1` (then `/hook $1`) first, and stop.``
    new: ``If none exists, tell the user to run `/draft $1` first, and stop.``
(3) usuń cały bullet hook-gate check:
```
   - **Hook-gate check:** if `outputs/videos_pl/$1/md/04_hook.md` is absent, `/hook` has not run — warn that the opening is un-gated and the packaging titles will be built on an unreviewed script; recommend `/hook $1` first. Warn and continue (do not hard-stop).
```

- [ ] **Step 10.4: `workflows/pipeline/07_package.md`**

old: ``After `/hook` (script locked), **before `/publish`**``
new: ``After `/draft` (script locked), **before `/publish`**``

- [ ] **Step 10.5: `workflows/pipeline/08_publish.md` (tabela troubleshooting)**

old: ``| Script source missing | Run `/draft` then `/hook` (exports `docx/script.docx`); or edit to `docx/script_corrected.docx` |``
new: ``| Script source missing | Run `/draft` (exports `docx/script.docx`); or edit to `docx/script_corrected.docx` |``

- [ ] **Step 10.6: `workflows/guides/file_naming.md` — tabela + nota**

Edit 1 — old_string (3 wiersze tabeli):
```
| `04_final_presqueeze.md` | Skrypt przed ściskaczem | 3c fixer |
| `04_final.md` | Finalny lean-skrypt | 3d ściskacz (hook poprawia *in place*) |
| `04_hook.md` | Log oceny hooka | Agent 4 |
```
new_string:
```
| `04_final.md` | Finalny skrypt maszyny | 3c fixer |
| `04_final_machine.md` | Nietykalny snapshot maszyny (pomiar sufitu) | /draft (kopia po fixerze) |
| `iter/fixer_skips.md` | Log pominięć fixera | 3c fixer |
```

Edit 2 — old_string:
```
- **`04_final` dzieli numer z `04_hook`** — bo Agent 4 (hook) modyfikuje finalny skrypt *w miejscu* (backup `04_final.bak.md` jest tymczasowy, kasowany po weryfikacji).
```
new_string:
```
- **`04_final_machine.md` jest nietykalny** — snapshot wyniku maszyny do diffu ze `script_corrected`; nigdy nie nadpisywany, także przy migracjach nazewnictwa (Gen 5).
```

- [ ] **Step 10.7: `workflows/guides/voice_brief.md` — nota v2.1**

old: ``oba; ściskacz 3d i tak je tnie.)*``
new: ``oba; walidator `draft_check.py` flaguje każde, które się prześlizgnie.)*``

- [ ] **Step 10.8: `.claude/skills/native-voice-guard/SKILL.md`**

old: ``(atrybucja żyje tylko w opisie Agenta 8; ściskacz 3d i tak ją tnie). Wciąż``
new: ``(atrybucja żyje tylko w opisie Agenta 8; walidator i tak ją flaguje). Wciąż``

- [ ] **Step 10.9: `.claude/skills/publish-package/SKILL.md`**

old:
```
- Brak skryptu → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>`
  i `/hook <slug>`.
```
new:
```
- Brak skryptu → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>`.
```

- [ ] **Step 10.10: `.claude/skills/write-script/SKILL.md` (przy okazji: usuwa stary Gen-2 opis raportu)**

old:
```
To, co raportuje `\draft`: wybrana architektura, liczba słów, werdykt pętli,
następny krok (`/hook <slug>`).
```
new:
```
To, co raportuje `/draft`: liczba słów, zgłoszenia [A]/[Z]/[K] + pominięcia
fixera, mapa pętli, werdykt walidatora; następny krok (redakcja `docx/script.docx`).
```

- [ ] **Step 10.11: `.claude/skills/package-thumbnail/SKILL.md`**

old:
```
- Brak → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>` (i
  `/hook <slug>`).
```
new:
```
- Brak → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>`.
```

- [ ] **Step 10.12: `.claude/skills/render-images/SKILL.md`**

old:
```
3. Brak `04_final.md` → zatrzymaj się; powiedz userowi, że trzeba najpierw
   `/draft <slug>` (i `/hook <slug>`).
```
new:
```
3. Brak `04_final.md` → zatrzymaj się; powiedz userowi, że trzeba najpierw
   `/draft <slug>`.
```

- [ ] **Step 10.13: Commit**

```bash
git add .claude/commands/visuals.md .claude/commands/publish.md .claude/commands/package.md workflows/pipeline/07_package.md workflows/pipeline/08_publish.md workflows/guides/file_naming.md workflows/guides/voice_brief.md .claude/skills/native-voice-guard/SKILL.md .claude/skills/publish-package/SKILL.md .claude/skills/write-script/SKILL.md .claude/skills/package-thumbnail/SKILL.md .claude/skills/render-images/SKILL.md
git commit -m "docs(gen5): wymiana odwołań /hook i ściskacza w komendach, skillach i guide'ach

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 11: `workflows/pipeline/00_master.md` — sync Master SOP

**Files:**
- Modify: `workflows/pipeline/00_master.md`

- [ ] **Step 11.1: Banner Stage 3 (linia 7)**

old_string (cała linia zaczynająca się od `> **Stage 3`): obecny banner „lean cold-subagent chain (2026-06-07, model split 2026-06-09) … 3d Ściskacz (Sonnet, cut-only). Authoritative: … `03d_compressor.md` …".
new_string:
```
> **Stage 3 = Gen 5 cold-subagent chain (2026-06-11).** `/draft <slug>` runs cold subagents, one pass, no loop, no API: **3a Writer** (Opus, 1500–2200 words, promise architecture) → **3b ensemble** (a section-checker per `## ` + one arc-checker with a loop map, in parallel; Sonnet section / Opus arc) → `draft_merge.py` → **3c Fixer** (Opus, skip clause + `iter/fixer_skips.md`) → snapshot `04_final_machine.md` → `draft_check.py --export` (doctrine validator + docx). No Ściskacz, no `/hook` (both retired 2026-06-11 — see `brainstorms/2026-06-11-gen5-draft-redesign.md`). Authoritative: `03a_writer.md`, `03b_section_checker.md`, `03b_arc_checker.md`, `03c_fixer.md`, `.claude/commands/draft.md`, `workflows/guides/voice_brief.md`, CLAUDE.md §„Script chain (Agent 3)".
```

- [ ] **Step 11.2: Diagram architektury — blok Agent 3 + Agent 4**

old_string (od linii `[Agent 3: Script — …` do linii `outputs/videos_pl/{slug}/md/04_final.bak.md  (created once, never overwritten)` włącznie — 16 linii):
```
[Agent 3: Script — 3a Writer → 3b ensemble (section+arc) → 3c Fixer → 3d Ściskacz, cold subagents via `/draft <slug>`]
    │  3a Writer    — Opus 4.8 (cold) writes the whole ~1000-1500-word narration, one loose pass
    │  3b ensemble  — parallel cold subagents: one section-checker per `## ` (Sonnet) + one arc-checker (Opus) → merged corrections
    │  3c Fixer     — Opus 4.8 (cold) swaps flagged sentences surgically → 04_final.md
    │  3d Ściskacz  — Sonnet 4.6 (cold, cut-only) trims over-writing → lean 04_final.md
    │  One pass, no loop, no API
    ▼
outputs/videos_pl/{slug}/md/03a_draft.md → 03b_corrections.md → 04_final.md (+ 04_final_presqueeze.md)
    │
    ▼
[Agent 4: Hook Gate — `/hook <slug>`]  ◀──── must verdict RECORD before voiceover
    │  Opus 4.8 (in-session) scores opening 37 words / 200 words; agent4_hook.py --apply splices in place
    ▼
outputs/videos_pl/{slug}/md/04_final.md  (modified in place)
outputs/videos_pl/{slug}/md/04_hook.md
outputs/videos_pl/{slug}/md/04_final.bak.md  (created once, never overwritten)
```
new_string:
```
[Agent 3: Script — 3a Writer → 3b ensemble (section+arc) → merge → 3c Fixer → validator, cold subagents via `/draft <slug>`]
    │  3a Writer    — Opus 4.8 (cold) writes the whole 1500-2200-word narration, one loose pass (promise architecture)
    │  3b ensemble  — parallel cold subagents: one section-checker per `## ` (Sonnet) + one arc-checker with loop map (Opus)
    │  draft_merge.py — deterministic merge of iter/ findings → 03b_corrections.md
    │  3c Fixer     — Opus 4.8 (cold) applies corrections surgically, skips clearly-worse ones → 04_final.md + iter/fixer_skips.md
    │  draft_check.py --export — doctrine validator (report-only) + docx/script.docx
    │  One pass, no loop, no API
    ▼
outputs/videos_pl/{slug}/md/03a_draft.md → 03b_corrections.md → 04_final.md
outputs/videos_pl/{slug}/md/04_final_machine.md  (untouchable machine snapshot)
outputs/videos_pl/{slug}/docx/script.docx
```

- [ ] **Step 11.3: Step 3 walkthrough — nagłówek + opis**

old (nagłówek): `### Step 3 — Script (Writer → ensemble → Fixer → Ściskacz, cold subagents)`
new: `### Step 3 — Script (Writer → ensemble → merge → Fixer → validator, cold subagents)`

old (akapit opisu — linia 163, cała): obecne zdanie „That slash command runs the whole script chain … 3d Ściskacz (Sonnet, cut-only) trims over-writing to the lean `md/04_final.md` (pre-squeeze kept as `md/04_final_presqueeze.md`). No loop. … [03d_compressor.md](03d_compressor.md), …".
new:
```
That slash command runs the whole script chain **in-session — no API** as cold subagents, one pass: **3a Writer** (Opus) saves `md/03a_draft.md` (1500–2200 words, promise architecture); a **3b ensemble** reads the frozen draft in parallel — one section-checker per `## ` (Sonnet) plus one arc-checker with a loop map (Opus); `draft_merge.py` merges findings into `md/03b_corrections.md`; **3c Fixer** (Opus) applies them surgically, skipping clearly-worse proposals (`md/iter/fixer_skips.md`); the machine snapshot is copied to `md/04_final_machine.md` (untouchable); `draft_check.py --export` validates doctrine and exports `docx/script.docx`. No loop. Review the loop map and `md/04_final.md`; the final editorial pass (including trimming over-writing) is yours on `docx/script_corrected.docx`. See [03a_writer.md](03a_writer.md), [03b_section_checker.md](03b_section_checker.md), [03b_arc_checker.md](03b_arc_checker.md), [03c_fixer.md](03c_fixer.md), [voice_brief.md](../guides/voice_brief.md).
```

- [ ] **Step 11.4: Usuń sekcję „Step 4 — Hook Gate" + napraw nagłówek Steps 5 & 8**

Usuń cały blok od `### Step 4 — Hook Gate` do linii `Scores the opening 37 words … See [04_hook.md](04_hook.md).` włącznie (z pustymi liniami i blokiem ```text /hook …```).
Potem old: `### Steps 5 & 8 — Parallel-safe after 4` → new: `### Steps 5 & 8 — Parallel-safe after 3`.

- [ ] **Step 11.5: Tabela Output File Reference**

old_string (4 wiersze):
```
| 3c→3d | `md/04_final.md` | Final lean script (Fixer applies corrections, Ściskacz trims over-writing) |
| 3d | `md/04_final_presqueeze.md` | Pre-Ściskacz backup of `04_final.md` |
| 4  | `md/04_hook.md` | Hook score per attempt + final verdict |
| 4  | `md/04_final.bak.md` | Pre-hook-refine backup (first run only) |
```
new_string:
```
| 3c | `md/04_final.md` | Final machine script (Fixer applies corrections; trimming = user docx pass) |
| 3c | `md/iter/fixer_skips.md` | Fixer skip log (clearly-worse proposals left out) |
| 3 | `md/04_final_machine.md` | Untouchable machine snapshot (ceiling metric vs `script_corrected`) |
```
Oraz wiersz docx — old: ``| 4  | `docx/script.docx` | Teleprompter-ready script (edit → save as `script_corrected.docx`) |`` → new: ``| 3 | `docx/script.docx` | Teleprompter-ready script, exported by `draft_check.py --export` (edit → save as `script_corrected.docx`) |``

- [ ] **Step 11.6: Detailed Workflow Links — usuń 2 linie**

Usuń linie:
```
workflows/pipeline/03d_compressor.md — Agent 3d (Ściskacz)
workflows/pipeline/04_hook.md       — Agent 4 (hook gate)
```

- [ ] **Step 11.7: Commit**

```bash
git add workflows/pipeline/00_master.md
git commit -m "docs(gen5): Master SOP — łańcuch Gen 5 (merge/walidator/snapshot), bez 3d i hook gate

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 12: `CLAUDE.md` — sync kanonu operatora

Read CLAUDE.md przed edycjami; poniżej intencja + kotwice (fragmenty unikalne). Przy drobnym rozjeździe tekstu wygrywa intencja speca D1–D6.

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 12.1: Channel Language — lista agentów piszących**

old (fragment): `(3a writer / 3b checkers / 3c fixer / 3d ściskacz / 8)` → new: `(3a writer / 3b checkers / 3c fixer / 8)`

- [ ] **Step 12.2: Script voice — bullet v2.1 (backstop)**

old (fragment): `The Ściskacz (3d) cuts any „badania pokazują" that slips.` → new: `The validator (draft_check.py) flags any „badania pokazują" that slips; you cut it on the docx pass.`

- [ ] **Step 12.3: Script chain (Agent 3) — pierwszy bullet (cały) → Gen 5**

Podmień cały bullet zaczynający się od `- **Lean cold-subagent flow (2026-06-07, Gen 4 + v2.1; model split 2026-06-09).**` (do końca tego bulletu, włącznie z `Rationale: brainstorms …poprawka-doktryny-glosu.md`.) na:
```
- **Gen 5 cold-subagent flow (2026-06-11).** `/draft <slug>` runs cold-context subagents — dedicated thin specialists `.claude/agents/draft-*.md` (Opus: writer/arc-checker/fixer, Sonnet: section-checkers), each blind to the others; the lead only passes files. One pass: **3a Writer** (1500–2200 words = 10–15 min film; **architektura obietnic** — each section opens the next question, the full answer to the title lands only at the close; first ~37 words = the hook gate, now a writer rule) → frozen-draft **ensemble in parallel** (one **3b section-checker per `## `** [Z]/[K], anti-flattening rule: native idiom ≠ calque, plus one **3b arc-checker** [A] with a **loop map** — promises/loops, opening, close execution, metaphors, klamra, transitions) → **`draft_merge.py`** (deterministic merge, zero tokens) → **3c Fixer** (applies surgically, [A]/[K] before [Z]; **mandatory skip clause** — clearly-worse proposals are skipped and logged to `md/iter/fixer_skips.md`) → snapshot **`md/04_final_machine.md` (untouchable — never overwrite, also in migrations)** → **`draft_check.py --export`** (report-only doctrine validator: sections survived / no research attribution / no digits / 1500–2200 window / no artifacts; exports `docx/script.docx`). Subagent returns are SHORT (path + counts — never the file body). **No Ściskacz (3d) and no `/hook`** — over-writing is cut by the user on docx; Tier-1 lives in writer rule 5 + arc-checker judges the opening; safeguard: if @0:30 retention on films 4–5 drops below ~55%, restore the gate from git. Spec: `03a_writer.md` / `03b_section_checker.md` / `03b_arc_checker.md` / `03c_fixer.md` + `voice_brief.md`. Rationale: brainstorms `2026-06-07-lean-draft-redesign.md`, `2026-06-07-context-checker-ensemble.md`, `2026-06-07-poprawka-doktryny-glosu.md`, `2026-06-11-gen5-draft-redesign.md`.
```

- [ ] **Step 12.4: Script chain — bullet „ceiling"**

old (fragment): `The machine delivers ~99%;` → new: `The machine delivers ~75–80% (measured: slug 3 — 62% of sentences touched, −18% words on the user pass);`
Dodaj na końcu tego bulletu zdanie: `Since Gen 5 the docx pass also owns trimming over-writing (no Ściskacz).`

- [ ] **Step 12.5: Quick Command Reference**

(1) old (linia /draft): ``/draft <slug>                              # Agent 3 — pisarz → ensemble (section+arc) → fixer → ściskacz (zimne subagenty — Opus + Sonnet wg roli, jeden przebieg, no API)``
    new: ``/draft <slug>                              # Agent 3 Gen 5 — pisarz → ensemble (section+arc, mapa pętli) → merge (skrypt) → fixer → snapshot → walidator+docx (zimne subagenty, jeden przebieg, no API)``
(2) usuń linię: ``/hook <slug>                               # Agent 4 hook gate → agent4_hook.py --apply``
(3) old (fragment): `**Parallel-safe after Agent 3:** Agents 5 and 8 simultaneously (6 depends on 5); `/package` runs after `/hook`, before `/publish`.` → new: `**Parallel-safe after Agent 3:** Agents 5 and 8 simultaneously (6 depends on 5); `/package` runs after `/draft`, before `/publish`.`

- [ ] **Step 12.6: Tabela Agent Chain**

(1) wiersz `| 3 (whole chain) | …` — old output: ``md/03a_draft.md`, `md/03b_corrections.md`, `md/04_final_presqueeze.md` + `md/04_final.md` `` → new output: ``md/03a_draft.md`, `md/03b_corrections.md`, `md/04_final.md` + `md/04_final_machine.md` + `md/iter/fixer_skips.md` + `docx/script.docx` ``; w opisie wiersza zamień `pisarz → ensemble section+arc → fixer → ściskacz` na `pisarz → ensemble section+arc → merge → fixer → walidator` (oraz `cold subagents, one pass, no API` zostaje).
(2) wiersz 3b arc-checker — w opisie dodaj `+ mapa pętli` po `whole-arc [A]`.
(3) usuń cały wiersz `| 3d ściskacz | …`.
(4) usuń cały wiersz `| 4 **(gate)** | /hook <slug> + agent4_hook.py --apply | … |`.
(5) w wierszu 5 (visuals) input zostaje bez zmian (`04_final.md` / `script_corrected.docx`).

- [ ] **Step 12.7: Akapity okołotabelowe**

(1) old (fragment, występuje po tabeli): ``/package` runs after `/hook` and before `/publish` (it feeds the title), independent of Agents 5/6.`` → new: ``/package` runs after `/draft` and before `/publish` (it feeds the title), independent of Agents 5/6.``
(2) old (fragment w „Manual agents"): ``/package` runs after `/hook` and before `/publish` (it feeds the title); Agent 6 after `/visuals`.`` → new: ``/package` runs after `/draft` and before `/publish` (it feeds the title); Agent 6 after `/visuals`.``
(3) Podmień CAŁY akapit `**Quality gate — Agent 4 (`/hook <slug>`):** …` (kończy się `…auto-detect the corrected file.`) na:
```
**Walidator + eksport (Gen 5):** `draft_check.py --export` w ogonie `/draft` raportuje naruszenia doktryny (report-only) i eksportuje `docx/script.docx` — edit this in Word/Copilot 365/Gemini and save as `docx/script_corrected.docx`; all downstream agents (Agent 8, /visuals, Align) auto-detect the corrected file. Osobnej bramki hooka nie ma — Tier-1 żyje w regule 5 pisarza i w arc-checkerze (safeguard: 0:30 < ~55% ⇒ przywróć bramkę z gita).
```

- [ ] **Step 12.8: File Structure (drzewko)**

(1) old: `commands/              # Manual slash launchers: /draft /hook /visuals /package /publish` → new: `commands/              # Manual slash launchers: /draft /visuals /package /publish /animate`
(2) old (fragment): `draft-{writer,section-checker,arc-checker,fixer,compressor}` → new: `draft-{writer,section-checker,arc-checker,fixer}`
(3) old (fragment): `10 skills: 2 guards (scientific-etching, native-voice) + 5 routers (write-script, score-hook, package-thumbnail, render-images, publish-package)` → new: `9 skills: 2 guards (scientific-etching, native-voice) + 4 routers (write-script, package-thumbnail, render-images, publish-package)`
(4) old (fragment): `pipeline/              # Agent scripts 0–8 + align; lib/ = align helper modules (aligner, fcpxml_writer, …)` → new: `pipeline/              # Agent scripts 0–8 + align + draft_{merge,check}.py (Gen 5 Layer 3); lib/ = align helper modules (aligner, fcpxml_writer, …)`

- [ ] **Step 12.9: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(gen5): CLAUDE.md — kanon Gen 5 (architektura obietnic, walidator, snapshot, ~75-80% ceiling, bez 3d/hook)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 13: `tools/dev/draft_ceiling_report.py` — pętla pomiarowa (opcjonalna, rekomendowana)

**Files:**
- Create: `tests/test_ceiling_report.py`
- Create: `tools/dev/draft_ceiling_report.py`

- [ ] **Step 13.1: Failing test**

`tests/test_ceiling_report.py`:

```python
import unittest

from tools.dev.draft_ceiling_report import sentence_diff_stats, split_sentences


class TestCeiling(unittest.TestCase):
    def test_split_sentences_basic(self):
        self.assertEqual(
            split_sentences("Ala ma kota. Kot ma Alę! Serio?"),
            ["Ala ma kota.", "Kot ma Alę!", "Serio?"],
        )

    def test_stats_buckets(self):
        machine = "Ala ma kota. Kot ma Alę. To jest zdanie trzecie. Czwarte zdanie istnieje."
        human = "Ala ma kota. Kot ma Alę! Piąte, zupełnie nowe."
        s = sentence_diff_stats(machine, human)
        self.assertEqual(s["machine_total"], 4)
        self.assertEqual(s["identical"], 1)          # "Ala ma kota."
        self.assertEqual(s["modified"], 1)           # "Kot ma Alę." -> "Kot ma Alę!" (ratio ~0.91)
        self.assertEqual(s["deleted"], 2)            # zdania 3-4 znikły
        self.assertEqual(s["added"], 1)              # "Piąte, zupełnie nowe."
        self.assertAlmostEqual(s["pct_touched"], (4 - 1) / 4 * 100, places=1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 13.2: Run — fail**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_ceiling_report -v`
Expected: `ModuleNotFoundError`

- [ ] **Step 13.3: Implementacja**

`tools/dev/draft_ceiling_report.py`:

```python
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
```

- [ ] **Step 13.4: Testy zielone + weryfikacja na slugu 3**

Run: `PYTHONIOENCODING=utf-8 python -m unittest tests.test_ceiling_report -v` → `OK`.
Run: `PYTHONIOENCODING=utf-8 python tools/dev/draft_ceiling_report.py "3_wstyd_za_wlasne_zycie"`
Expected (rząd wielkości z audytu 2026-06-11, fallback na 04_final.md): cut-rate ~18%, dotknięte ~60% — ±10 p.p. OK (inna segmentacja zdań niż w audycie).

- [ ] **Step 13.5: Commit**

```bash
git add tests/test_ceiling_report.py tools/dev/draft_ceiling_report.py
git commit -m "feat(dev): draft_ceiling_report.py — pomiar sufitu maszyna vs docx-pass (Gen 5 D5)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 14: Finalna weryfikacja całości

- [ ] **Step 14.1: Pełny zestaw testów**

Run: `PYTHONIOENCODING=utf-8 python -m unittest discover tests -v`
Expected: wszystkie testy `OK` (merge + check + ceiling).

- [ ] **Step 14.2: Sweep martwych odwołań**

Run: `grep -rn -E "agent4_hook|03d_compressor|draft-compressor|score-hook|presqueeze|04_final\.bak" .claude/ workflows/ tools/ CLAUDE.md`
Expected: **jedyne dozwolone trafienie** = historyczna nota retrofitów w `workflows/guides/file_naming.md` („04b_hook→04_hook" w sekcji o starych slugach — zostaje świadomie). Wszystko inne = przeoczenie do naprawy.

Run: `grep -rn "/hook" .claude/ workflows/ tools/ CLAUDE.md`
Expected: trafienia WYŁĄCZNIE objaśniające emeryturę (frazy typu „bez /hook", „no `/hook`", „przywróć bramkę /hook z gita") w `.claude/commands/draft.md`, `CLAUDE.md`, `workflows/pipeline/00_master.md` oraz w tym planie/brainstormie. Żadne trafienie nie może INSTRUOWAĆ uruchomienia `/hook` jako żywego kroku (prereq, „recommend /hook", „then /hook", routing skilla). Słowo „hook" bez ukośnika (reguła 5 pisarza, rubryki hook/metafora/puenta w `animate`/`publish-clips`/`06c_animate`) — zostaje.

- [ ] **Step 14.3: Walidator i merge na realnym slugu (smoke)**

Run: `PYTHONIOENCODING=utf-8 python tools/pipeline/draft_check.py "4_stane_sie_swoim_rodzicem"`
Expected: jak w Step 2.5 (1 uwaga o widełkach — stara generacja).

- [ ] **Step 14.4: Commit końcowy (jeśli coś poprawiono w sweepie)**

```bash
git status --short
git add -A
git commit -m "chore(gen5): domknięcie sweepu odwołań po cutoverze

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

(Jeśli tree czysty — pomiń commit.)

---

## Walidacja rolloutu (poza tym planem — slug 5)

Pierwszy realny przebieg `/draft` na slugu 5 sprawdza: mapę pętli w raporcie, niepusty `fixer_skips` (klauzula żyje), werdykt walidatora, długość w widełkach; po redakcji usera `draft_ceiling_report.py` (czy lżej niż 62%/−18% ze sluga 3); po publikacji filmu kryteria diagnozy D (plateau po 1. minucie, 0:30 ≥ ~55% — spadek ⇒ przywrócenie bramki /hook z gita).
