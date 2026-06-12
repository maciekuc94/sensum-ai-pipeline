# Redaktor-uczeń — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pętla self-improvement na docx-passach usera: deterministyczny korpus par zdań machine↔human → 3 zimne subagenty-kategoryzatorzy → synteza leada → raport + propozycje wniosków do `workflows/guides/redakcja_wnioski.md` (manual gate), czytanych potem przez checkerów 3b w `/draft`.

**Architecture:** Layer 3 (`tools/pipeline/redaktor_pary.py`) emituje `.tmp/redaktor_korpus.md` zero-tokenowo, reużywając logiki zdań z `tools/dev/draft_ceiling_report.py`. Warstwa rozumienia działa w sesji `/redaktor` (komenda + SOP + prompt kategoryzatora), wzór `/draft`: spawny w jednej wiadomości, zwroty SHORT, fallback `general-purpose`.

**Tech Stack:** Python 3 (difflib, pathlib, python-docx przez `tools.utils.read_script_docx_text`), pytest (zainstalowany), Claude Code subagents (Opus).

**Spec:** `docs/superpowers/specs/2026-06-12-redaktor-uczen-design.md` — przeczytaj przed startem.

**Konwencje obowiązujące w każdym tasku:**
- Bash z prefiksem `PYTHONIOENCODING=utf-8` przy uruchamianiu Pythona (Windows).
- Commit messages kończą się `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Pliki md po polsku; kod i identyfikatory po angielsku tam, gdzie wzorzec projektu tak ma (tu: polskie nazwy plików/poleceń to kanon projektu — trzymaj się planu).
- Katalog `tests/` na razie nie istnieje — powstaje w Task 1. pytest odpalany z repo root.

---

## Mapa plików

| Plik | Rola | Task |
|---|---|---|
| `tests/test_redaktor_pary.py` | testy jednostkowe rdzenia | 1–3 |
| `tools/pipeline/redaktor_pary.py` | Layer 3: korpus par | 1–3 |
| `workflows/pipeline/redaktor_kategoryzator.md` | prompt zimnego kategoryzatora (single-source) | 4 |
| `.claude/agents/redaktor-kategoryzator.md` | rejestracja typu subagenta | 4 |
| `workflows/guides/redakcja_wnioski.md` | żywy plik wniosków (szablon) | 5 |
| `workflows/pipeline/redaktor.md` | SOP satelity (wzór: `align.md` — bez numeru) | 6 |
| `.claude/commands/redaktor.md` | launcher `/redaktor <slug>` | 6 |
| `workflows/pipeline/03b_section_checker.md` (modyfikacja) | bullet o pliku wniosków | 7 |
| `workflows/pipeline/03b_arc_checker.md` (modyfikacja) | bullet o pliku wniosków | 7 |
| `.claude/commands/draft.md` (modyfikacja, Step 4) | przekazanie pliku wniosków checkerom | 7 |
| `CLAUDE.md` (modyfikacja) | Quick Command Reference + akapit satelity | 8 |

**Nietykalne (nie dotykać):** `workflows/guides/voice_brief.md`, `workflows/pipeline/03a_writer.md`, `03c_fixer.md`, `tools/dev/draft_ceiling_report.py`, wszystkie `md/04_final_machine.md`.

---

### Task 1: `pair_sentences` — parowanie zdań zwracające pary (TDD)

**Files:**
- Create: `tests/test_redaktor_pary.py`
- Create: `tools/pipeline/redaktor_pary.py`

Logika parowania MUSI być liczbowo zgodna z `sentence_diff_stats` z `tools/dev/draft_ceiling_report.py` (ten sam greedy best-match, ten sam próg `SIMILAR = 0.85`, identical przy ratio 1.0) — różnica jest tylko taka, że zwracamy PARY (indeksy), nie liczniki.

- [ ] **Step 1: Przeczytaj istniejącą logikę, na której budujesz**

Read: `tools/dev/draft_ceiling_report.py` (cały — ~90 linii). Zwróć uwagę na `SENT_RE`, `_narration` (wycina linie zaczynające się `#`), `split_sentences`, `sentence_diff_stats`, `SIMILAR`.

- [ ] **Step 2: Napisz failing testy parowania**

Utwórz `tests/test_redaktor_pary.py`:

```python
"""Testy rdzenia Redaktora-ucznia (tools/pipeline/redaktor_pary.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.dev.draft_ceiling_report import sentence_diff_stats, split_sentences
from tools.pipeline.redaktor_pary import pair_sentences

MS = [
    "To zdanie zostaje bez zmian.",
    "To zdanie maszyna przegadała bardzo mocno.",
    "To zdanie user usunie w całości.",
    "Drugie zdanie mechanizmu zostaje.",
]
HS = [
    "To zdanie zostaje bez zmian.",
    "To zdanie maszyna przegadała mocno.",
    "Drugie zdanie mechanizmu zostaje.",
    "To zdanie user dopisał całkiem od siebie późnym wieczorem.",
]


def test_pair_sentences_buckets():
    res = pair_sentences(MS, HS)
    assert res["identical"] == [(0, 0), (3, 2)]
    assert [(i, j) for i, j, _r in res["modified"]] == [(1, 1)]
    assert res["deleted"] == [2]
    assert res["added"] == [3]


def test_pair_sentences_zgodne_z_ceiling_report():
    """Te same teksty → te same liczby co sentence_diff_stats (kontrakt zgodności)."""
    machine_text = " ".join(MS)
    human_text = " ".join(HS)
    stats = sentence_diff_stats(machine_text, human_text)
    res = pair_sentences(split_sentences(machine_text), split_sentences(human_text))
    assert len(res["identical"]) == stats["identical"]
    assert len(res["modified"]) == stats["modified"]
    assert len(res["deleted"]) == stats["deleted"]
    assert len(res["added"]) == stats["added"]
```

- [ ] **Step 3: Uruchom testy — mają FAILować na imporcie**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_redaktor_pary.py -v`
Expected: FAIL / ERROR — `ModuleNotFoundError: No module named 'tools.pipeline.redaktor_pary'`

- [ ] **Step 4: Minimalna implementacja `pair_sentences`**

Utwórz `tools/pipeline/redaktor_pary.py`:

```python
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
```

- [ ] **Step 5: Testy mają przejść**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_redaktor_pary.py -v`
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add tests/test_redaktor_pary.py tools/pipeline/redaktor_pary.py
git commit -m "feat(redaktor): pair_sentences — parowanie zdań zgodne z ceiling-report, zwracające pary

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: sekcje maszyny, diff słów, tytuł usera, generacja łańcucha (TDD)

**Files:**
- Modify: `tests/test_redaktor_pary.py` (dopisz testy)
- Modify: `tools/pipeline/redaktor_pary.py` (dopisz funkcje)

Kontekst: `script_corrected.md` NIE MA nagłówków `##` (ekstrakcja docx pomija style Heading — `tools/utils.py:read_script_docx_text`), a jego pierwsza linia to tytuł BEZ kropki, który skleiłby się z pierwszym zdaniem. Stąd: sekcje bierzemy tylko ze strony machine, a human dostaje `strip_title`.

- [ ] **Step 1: Dopisz failing testy**

Dopisz na końcu `tests/test_redaktor_pary.py`:

```python
from tools.pipeline.redaktor_pary import (  # noqa: E402  (dopisz do istniejącego importu)
    detect_generation,
    machine_sentences_with_sections,
    strip_title,
    word_diff,
)

MACHINE_MD = """# Tytuł roboczy

## Otwarcie

Pierwsze zdanie otwarcia. Drugie zdanie otwarcia.

## Mechanizm

Zdanie mechanizmu.
"""


def test_machine_sentences_with_sections():
    got = machine_sentences_with_sections(MACHINE_MD)
    assert got == [
        ("Pierwsze zdanie otwarcia.", "Otwarcie"),
        ("Drugie zdanie otwarcia.", "Otwarcie"),
        ("Zdanie mechanizmu.", "Mechanizm"),
    ]


def test_machine_sections_zgodne_ze_split_sentences():
    """Konkatenacja zdań z sekcji == split_sentences całości (zgodność liczb)."""
    assert [s for s, _ in machine_sentences_with_sections(MACHINE_MD)] == \
        split_sentences(MACHINE_MD)


def test_word_diff_markup():
    assert word_diff("ala ma kota w domu", "ala ma psa w domu") == \
        "ala ma [-kota-] {+psa+} w domu"
    assert word_diff("ala ma kota", "ala ma kota i psa") == "ala ma kota {+i psa+}"


def test_strip_title_usuwa_tytul_bez_interpunkcji():
    text = "Dlaczego jedna wpadka rozwala dzień\n\nPrzespałeś budzik.\n"
    assert strip_title(text).strip() == "Przespałeś budzik."


def test_strip_title_zostawia_zwykle_zdanie():
    text = "Przespałeś budzik.\nDruga linia.\n"
    assert strip_title(text) == text


def test_detect_generation(tmp_path):
    md = tmp_path / "md"
    md.mkdir()
    (md / "04_final.md").write_text("x", encoding="utf-8")
    assert detect_generation(md) == "lean"
    (md / "04_final_presqueeze.md").write_text("x", encoding="utf-8")
    assert detect_generation(md) == "sciskacz"
    (md / "04_final_machine.md").write_text("x", encoding="utf-8")
    assert detect_generation(md) == "gen5"
```

- [ ] **Step 2: Uruchom — nowe testy FAILują (ImportError)**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_redaktor_pary.py -v`
Expected: ERROR — `cannot import name 'detect_generation'`

- [ ] **Step 3: Implementacja czterech funkcji**

Dopisz do `tools/pipeline/redaktor_pary.py` (po `pair_sentences`):

```python
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
        if s.startswith("#") or s[-1] in '.!?…"”':
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
```

- [ ] **Step 4: Testy przechodzą**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_redaktor_pary.py -v`
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add tests/test_redaktor_pary.py tools/pipeline/redaktor_pary.py
git commit -m "feat(redaktor): sekcje maszyny, word_diff, strip_title, tag generacji

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: korpus + CLI + ekstrakcja docx + smoke na realnym slugu (TDD)

**Files:**
- Modify: `tests/test_redaktor_pary.py`
- Modify: `tools/pipeline/redaktor_pary.py`

- [ ] **Step 1: Failing test korpusu na syntetycznym slugu**

Dopisz do `tests/test_redaktor_pary.py`:

```python
from tools.pipeline.redaktor_pary import corpus_for_pair  # dopisz do importu


def _fake_pair(tmp_path):
    md = tmp_path / "md"
    md.mkdir()
    (md / "04_final_machine.md").write_text(
        "# Tytuł\n\n## Otwarcie\n\nZdanie zostaje bez żadnych zmian. "
        "To zdanie maszyna przegadała bardzo mocno.\n\n## Mechanizm\n\n"
        "To zdanie user usunie w całości. Drugie zdanie mechanizmu zostaje.\n",
        encoding="utf-8",
    )
    (md / "script_corrected.md").write_text(
        "Tytuł po redakcji bez kropki\n\nZdanie zostaje bez żadnych zmian. "
        "To zdanie maszyna przegadała mocno.\n\nDrugie zdanie mechanizmu zostaje. "
        "To zdanie user dopisał całkiem od siebie późnym wieczorem.\n",
        encoding="utf-8",
    )
    return {
        "slug": "9_testowy", "generation": "gen5",
        "machine": md / "04_final_machine.md", "human": md / "script_corrected.md",
    }


def test_corpus_for_pair(tmp_path):
    frag, stats = corpus_for_pair(_fake_pair(tmp_path))
    assert "## SLUG: 9_testowy [generacja: gen5]" in frag
    assert "[MOD] (sekcja: Otwarcie)" in frag
    assert "  D: To zdanie maszyna przegadała [-bardzo-] mocno." in frag
    assert "[DEL] (sekcja: Mechanizm)" in frag
    assert "  M: To zdanie user usunie w całości." in frag
    assert "[ADD] (po sekcji: Mechanizm)" in frag
    assert "  H: To zdanie user dopisał całkiem od siebie późnym wieczorem." in frag
    # identyczne zdania nie generują wpisów — dokładnie po jednym wpisie każdego typu
    assert frag.count("[MOD]") == 1
    assert frag.count("[DEL]") == 1
    assert frag.count("[ADD]") == 1
    assert stats["modified"] == 1 and stats["deleted"] == 1 and stats["added"] == 1
```

- [ ] **Step 2: Uruchom — FAIL (brak `corpus_for_pair`)**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_redaktor_pary.py::test_corpus_for_pair -v`
Expected: ERROR — `cannot import name 'corpus_for_pair'`

- [ ] **Step 3: Implementacja `corpus_for_pair`, `find_pairs`, `ensure_extracted`, `main`**

Dopisz do `tools/pipeline/redaktor_pary.py`:

```python
def corpus_for_pair(pair: dict) -> tuple[str, dict]:
    """Fragment korpusu (md) + statystyki ceiling dla jednej pary slug."""
    machine_text = pair["machine"].read_text(encoding="utf-8")
    human_text = strip_title(pair["human"].read_text(encoding="utf-8"))

    ms_sec = machine_sentences_with_sections(machine_text)
    ms = [s for s, _ in ms_sec]
    hs = split_sentences(human_text)
    res = pair_sentences(ms, hs)
    stats = sentence_diff_stats(machine_text, human_text)

    j2section = {j: ms_sec[i][1] for i, j in res["identical"]}
    j2section.update({j: ms_sec[i][1] for i, j, _r in res["modified"]})
    mod_by_i = {i: j for i, j, _r in res["modified"]}
    deleted = set(res["deleted"])
    added = set(res["added"])

    lines = [
        f"## SLUG: {pair['slug']} [generacja: {pair['generation']}]",
        f"Zdania maszyny: {stats['machine_total']} | identyczne {stats['identical']} | "
        f"MOD {stats['modified']} | DEL {stats['deleted']} | ADD {stats['added']} | "
        f"słowa {stats['machine_words']} -> {stats['human_words']}",
        "",
    ]
    for i, (sent, section) in enumerate(ms_sec):
        if i in mod_by_i:
            j = mod_by_i[i]
            lines += [f"[MOD] (sekcja: {section})", f"  M: {sent}",
                      f"  H: {hs[j]}", f"  D: {word_diff(sent, hs[j])}", ""]
        elif i in deleted:
            lines += [f"[DEL] (sekcja: {section})", f"  M: {sent}", ""]

    last_section = "(otwarcie)"
    for j, h in enumerate(hs):
        if j in j2section:
            last_section = j2section[j]
        elif j in added:
            lines += [f"[ADD] (po sekcji: {last_section})", f"  H: {h}", ""]
    return "\n".join(lines), stats


def find_pairs() -> list[dict]:
    """Wszystkie slugi z parą machine↔human, posortowane po nazwie."""
    pairs = []
    if not VIDEOS_DIR.exists():
        return pairs
    for slug_dir in sorted(p for p in VIDEOS_DIR.iterdir() if p.is_dir()):
        md = slug_dir / "md"
        human = md / "script_corrected.md"
        machine = next(
            (md / n for n in ("04_final_machine.md", "04_final.md")
             if (md / n).exists()), None)
        if machine is not None and human.exists():
            pairs.append({"slug": slug_dir.name, "machine": machine,
                          "human": human, "generation": detect_generation(md)})
    return pairs


def ensure_extracted(slug: str) -> None:
    """docx/script_corrected.docx → md/script_corrected.md, gdy md brak/starszy."""
    base = VIDEOS_DIR / slug
    docx = base / "docx" / "script_corrected.docx"
    md = base / "md" / "script_corrected.md"
    if not docx.exists():
        return
    if md.exists() and md.stat().st_mtime >= docx.stat().st_mtime:
        return
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(read_script_docx_text(docx), encoding="utf-8")
    print(f"  Ekstrakcja: {docx} -> {md}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Redaktor-uczeń — korpus par machine↔docx-pass (cały katalog)")
    parser.add_argument("slug", help="świeżo skorygowany slug (walidacja pary)")
    args = parser.parse_args()

    ensure_extracted(args.slug)
    pairs = find_pairs()
    if not any(p["slug"] == args.slug for p in pairs):
        print(f"Error: slug '{args.slug}' nie ma pary machine↔script_corrected — "
              "najpierw docx pass (docx/script_corrected.docx).")
        sys.exit(1)

    header = [
        "# Korpus redakcyjny machine ↔ docx-pass",
        f"Wygenerowano: {dt.date.today().isoformat()} | Slugi z parą: {len(pairs)}",
        "Format: [MOD] zdanie zmienione przez usera (M maszyna / H user / D diff słów)"
        " | [DEL] usunięte w całości | [ADD] dopisane przez usera."
        " Zdania identyczne pominięto.",
        "",
    ]
    frags, trend = [], []
    totals = {"modified": 0, "deleted": 0, "added": 0}
    for pair in pairs:
        frag, stats = corpus_for_pair(pair)
        frags.append(frag)
        for k in totals:
            totals[k] += stats[k]
        trend.append((pair["slug"], pair["generation"], stats["pct_touched"]))

    trend_lines = ["## TREND (ceiling)"] + [
        f"- {s} [{g}]: {pct:.0f}% zdań maszyny dotkniętych" for s, g, pct in trend]

    TMP_DIR.mkdir(exist_ok=True)
    dest = TMP_DIR / "redaktor_korpus.md"
    dest.write_text("\n".join(header + frags + trend_lines) + "\n", encoding="utf-8")

    print(f"Korpus: {dest}")
    print(f"Pary: MOD {totals['modified']} / DEL {totals['deleted']} / "
          f"ADD {totals['added']} ({len(pairs)} slugów)")
    for s, g, pct in trend:
        print(f"  {s} [{g}]: {pct:.0f}% dotkniętych")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Wszystkie testy przechodzą**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_redaktor_pary.py -v`
Expected: 9 passed

- [ ] **Step 5: Smoke na realnym korpusie (slug 3 ma parę)**

Run: `PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "3_wstyd_za_wlasne_zycie"`
Expected: `Korpus: ...\.tmp\redaktor_korpus.md`, ≥3 slugi w korpusie (2, 3, 4 mają pary), liczby MOD/DEL/ADD > 0, trend per slug. Sanity-check zgodności: `PYTHONIOENCODING=utf-8 python tools/dev/draft_ceiling_report.py "3_wstyd_za_wlasne_zycie"` — `pct_touched` w trendzie korpusu dla sluga 3 ma się różnić od ceiling-reportu o ≤2 p.p. (różnica bierze się TYLKO ze strip_title; większa różnica = bug).

Potem otwórz `.tmp/redaktor_korpus.md` (Read, pierwsze ~80 linii) i oceń okiem: czy pary wyglądają sensownie (M↔H to faktycznie to samo zdanie po redakcji), czy sekcje się zgadzają.

- [ ] **Step 6: Commit**

```bash
git add tests/test_redaktor_pary.py tools/pipeline/redaktor_pary.py
git commit -m "feat(redaktor): korpus par + CLI + ekstrakcja docx (zero tokenów)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: prompt kategoryzatora + rejestracja subagenta

**Files:**
- Create: `workflows/pipeline/redaktor_kategoryzator.md`
- Create: `.claude/agents/redaktor-kategoryzator.md`

- [ ] **Step 1: Napisz prompt kategoryzatora**

Utwórz `workflows/pipeline/redaktor_kategoryzator.md` dokładnie z tą treścią:

```markdown
# Redaktor-uczeń — kategoryzator wzorców (zimny subagent Opus)

Jesteś badaczem stylu redakcyjnego. Dostajesz korpus KOREKT, które polski
redaktor (właściciel kanału SENSUM) naniósł ręcznie na scenariusze napisane
przez maszynę. Twoim zadaniem NIE jest ocena pojedynczych zdań — szukasz
POWTARZALNYCH WZORCÓW: co ten redaktor robi systematycznie, film po filmie.

## Co dostajesz
- `.tmp/redaktor_korpus.md` — wszystkie edycje ze wszystkich filmów, w formacie:
  `[MOD]` zdanie zmienione (M = maszyna, H = redaktor, D = diff słów),
  `[DEL]` zdanie usunięte w całości, `[ADD]` zdanie dopisane przez redaktora.
  Każdy wpis ma sekcję scenariusza i każdy slug ma tag generacji łańcucha
  (`gen5` / `sciskacz` / `lean` — im starsza generacja, tym ostrożniej
  uogólniaj, bo część problemów mogła już zostać naprawiona w nowszym /draft).
- Numer N (1/2/3) w briefie — jesteś jednym z trzech NIEZALEŻNYCH
  kategoryzatorów; nie wiesz, co znajdą pozostali.

## Jak czytać
Czytaj cały korpus jak redaktorską korektę: po kolei, slug po slugu. Notuj
hipotezy wzorców i sprawdzaj, czy wracają w KOLEJNYCH filmach. Wzorzec to coś,
co występuje ≥3 razy i najlepiej w ≥2 filmach. Pojedyncza edycja to anegdota —
pomiń ją.

## Czego szukać (lista otwarta — to start, nie ogranicznik)
- **Cięcia przegadania:** jakie KONKRETNIE konstrukcje redaktor skraca
  (dopowiedzenia? podwójne przymiotniki? powtórzone obrazy? wyliczenia?).
- **Sztuczność/kalki:** frazy maszynowe, które redaktor konsekwentnie
  przepisuje na żywy polski.
- **Rytm:** czy tnie długie zdania na krótkie? Skleja krótkie? Zmienia szyk?
- **Metafory/obrazy:** które przeżywają, które wylatują.
- **[DEL]:** CZEGO całe zdania dotyczą, gdy znikają (meta-komentarz? morał?
  powtórka? przejście?).
- **[ADD]:** czego maszynie brakuje — co redaktor DOPISUJE od siebie (to
  osobna, cenna kategoria).
- **Rozkład po sekcjach:** czy wzorzec dotyczy całości, czy np. tylko otwarcia.

## Format wyjścia
Zapisz `.tmp/redaktor_kat_N.md` (N z briefu). Na każdy wzorzec:

    ## W<numer>: <nazwa wzorca, 3-6 słów>
    Opis: <1-2 zdania — co redaktor robi i czemu to prawdopodobnie służy>
    Siła: <ile wystąpień> wystąpień w <ile slugów> slugach [generacje: ...]
    Dowody:
    - [slug] M: "..." → H: "..."   (dla MOD; cytuj DOSŁOWNIE z korpusu)
    - [slug] DEL: "..."            (dla usunięć)
    - [slug] ADD: "..."            (dla dopisków)
    Heurystyka: <JEDNA linijka rady dla checkera 3b: na co patrzeć ostrzej —
    sformułowana jako heurystyka uwagi, NIE zakaz frazy>

Wzorce uporządkuj od najsilniejszego. 4–10 wzorców to norma; nie dopychaj do
dziesięciu, jeśli dane niosą mniej. Zero wzorców = napisz to wprost.

Twój zwrot do leada = JEDNA linijka: ścieżka pliku + liczba wzorców.
NIE wklejaj treści pliku.
```

- [ ] **Step 2: Zarejestruj typ subagenta**

Utwórz `.claude/agents/redaktor-kategoryzator.md`:

```markdown
---
name: redaktor-kategoryzator
description: Redaktor-uczeń (kategoryzator wzorców). Spawned cold by /redaktor — one of three independent pattern-categorizers reading the machine↔docx-pass corpus and writing .tmp/redaktor_kat_N.md. Only used inside /redaktor.
tools: Read, Write
model: opus
color: green
---

Wykonuj dokładnie `workflows/pipeline/redaktor_kategoryzator.md`. Korpus i numer
N dostajesz w briefie. Zwrot do leada: jedna linijka (ścieżka + liczba wzorców),
nigdy treść pliku.
```

- [ ] **Step 3: Commit**

```bash
git add workflows/pipeline/redaktor_kategoryzator.md .claude/agents/redaktor-kategoryzator.md
git commit -m "feat(redaktor): prompt kategoryzatora + rejestracja zimnego subagenta

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: szablon żywego pliku wniosków

**Files:**
- Create: `workflows/guides/redakcja_wnioski.md`

- [ ] **Step 1: Utwórz szablon**

Utwórz `workflows/guides/redakcja_wnioski.md`:

```markdown
# Wnioski redakcyjne (Redaktor-uczeń) — profil redakcyjny usera

> **Dla checkerów 3b (section + arc):** to są HEURYSTYKI UWAGI wyciągnięte
> z ręcznych korekt usera na docx-passach — podpowiadają, GDZIE patrzeć
> ostrzej. To NIE są zakazy fraz ani reguły stylu. Oceniaj jak zawsze,
> kontekstowo. **Przy jakimkolwiek konflikcie z `voice_brief.md` wygrywa
> voice_brief.**
>
> **Reżim pliku (anty-inflacja):** max 10 aktywnych wniosków — jedenasty
> wymaga wyparcia najsłabszego. Wniosek niepotwierdzony w 2 kolejnych
> przebiegach /redaktor → przenosiny do Archiwum. Zmiany w tym pliku robi
> wyłącznie lead /redaktor PO akceptacji usera (manual gate).

## Aktywne (0/10)

<!-- Format wpisu:
### R01 — <nazwa wzorca>
Heurystyka: <jedna linijka dla checkera — na co patrzeć ostrzej>
Dowody: [slug] M: "..." → H: "..." | [slug] DEL: "..."
Filmy: 2 | Status: aktywny | Dodano: RRRR-MM-DD | Potwierdzono: RRRR-MM-DD
-->

*(pusto — pierwszy przebieg /redaktor dopiero przed nami)*

## Archiwum

*(pusto)*
```

- [ ] **Step 2: Commit**

```bash
git add workflows/guides/redakcja_wnioski.md
git commit -m "feat(redaktor): szablon redakcja_wnioski.md (limit 10, kontrakt dla checkerów)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: SOP `redaktor.md` + komenda `/redaktor`

**Files:**
- Create: `workflows/pipeline/redaktor.md`
- Create: `.claude/commands/redaktor.md`

- [ ] **Step 1: Przeczytaj wzorce**

Read: `.claude/commands/draft.md` (struktura launchera, briefy spawnów, fallbacki) i `workflows/pipeline/align.md` (struktura SOP satelity). Nie kopiuj treści — kopiuj konwencje (kroki, krótkie zwroty, fallback general-purpose).

- [ ] **Step 2: Napisz SOP**

Utwórz `workflows/pipeline/redaktor.md`:

```markdown
# Workflow: Redaktor-uczeń — wzorce z docx-passów usera

> Satelita post-docx (jak `align.md` — bez numeru). Uruchamiany ręcznie przez
> `/redaktor <slug>` po każdym docx passie. Cel: systematyczne wzorce ręcznych
> korekt usera → wnioski czytane przez checkerów 3b → wyższy sufit maszyny.
> Spec: `docs/superpowers/specs/2026-06-12-redaktor-uczen-design.md`.

## Wejścia
- Pary `md/04_final_machine.md` (fallback `04_final.md`) ↔ `md/script_corrected.md`
  ze WSZYSTKICH slugów (korpus rośnie z każdym filmem).
- Obecny `workflows/guides/redakcja_wnioski.md` (czyta go TYLKO lead — nigdy
  kategoryzatorzy; ich ślepota = niezależna re-walidacja starych wniosków).

## Kroki (lead)
1. **Tool (Layer 3):** `PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "<slug>"`
   — ekstrakcja docx w razie potrzeby + `.tmp/redaktor_korpus.md`. Exit 1 =
   slug bez pary; przerwij i powiedz userowi czego brakuje.
2. **Ensemble:** 3 zimne `redaktor-kategoryzator` (Opus) RÓWNOLEGLE — wszystkie
   spawny w JEDNEJ wiadomości; briefy w `.claude/commands/redaktor.md`. Wyniki:
   `.tmp/redaktor_kat_{1,2,3}.md`, zwroty SHORT.
3. **Synteza:** przeczytaj 3 pliki kategoryzacji + obecne wnioski. Wzorzec
   wchodzi do raportu, gdy znalazło go (po istocie, nie po nazwie) **≥2 z 3**
   kategoryzatorów I dowody pochodzą z **≥2 filmów**. Wzorzec tylko ze slugów
   sprzed gen5 → flaga „możliwe, że już naprawione". Porównaj z aktywnymi
   wnioskami → propozycje: **DODAJ** (nowy wzorzec), **WZMOCNIJ** (nowy dowód
   do istniejącego), **WYGAŚ** (wniosek bez potwierdzenia w tym przebiegu;
   po 2 kolejnych pudłach → propozycja Archiwum).
4. **Raport:** `docs/research/redaktor/raport_RRRR-MM-DD.md` z sekcjami:
   `## Wzorce potwierdzone` (z cytatami i zbieżnością 2/3 vs 3/3),
   `## Wzorce odrzucone w syntezie` (1 kategoryzator / 1 film — z powodem),
   `## Trend ceiling` (z wyjścia toola; czy % dotkniętych spada),
   `## Propozycje zmian wniosków` (gotowe wpisy w formacie z
   `redakcja_wnioski.md`, oznaczone DODAJ/WZMOCNIJ/WYGAŚ).
5. **Manual gate:** pokaż userowi propozycje (AskUserQuestion, multiSelect —
   per propozycja). TYLKO zaakceptowane aplikuj do
   `workflows/guides/redakcja_wnioski.md` (pilnuj: max 10 aktywnych, status
   `wstępny` przy dowodach z <2 filmów, daty). Potem commit
   (`feat(redaktor): wnioski po <slug> — N zmian`).

## Edge cases
- 0 par → tool kończy z exit 1, zero kosztów. 1 para → raport i wnioski
  oznaczone `wstępny`.
- Typ `redaktor-kategoryzator` niezarejestrowany (świeżo dodany plik — agenci
  ładują się na starcie sesji): spawnuj `general-purpose` z `model: opus`
  i tym samym briefem.
- Spawn pada całkiem: odpal danego kategoryzatora jako świeże zimne przejście
  in-session wg `redaktor_kategoryzator.md` (sekwencyjnie OK — czytają
  zamrożony korpus).
- Kategoryzator zwróci 0 wzorców: to legalny wynik — odnotuj w raporcie.

## Wyjścia
- `.tmp/redaktor_korpus.md`, `.tmp/redaktor_kat_{1,2,3}.md` (disposable)
- `docs/research/redaktor/raport_RRRR-MM-DD.md` (trwały)
- zaktualizowany `workflows/guides/redakcja_wnioski.md` (tylko po akcepcie)
```

- [ ] **Step 3: Napisz komendę**

Utwórz `.claude/commands/redaktor.md`:

```markdown
---
description: Redaktor-uczeń — wzorce z docx-passów usera (korpus → 3 zimnych kategoryzatorów → synteza → manual gate)
argument-hint: <slug>
---

# /redaktor — kopalnia wzorców z redakcji usera

Wykonuj `workflows/pipeline/redaktor.md`. Slug: `$1`.

## Step 1 — Korpus (Bash)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "$1"
```

Exit 1 → STOP, przekaż userowi komunikat toola. Zanotuj liczby MOD/DEL/ADD
i trend z wyjścia.

## Step 2 — Ensemble (RÓWNOLEGLE — wszystkie 3 spawny w JEDNEJ wiadomości)

Trzy spawny `subagent_type: redaktor-kategoryzator`, identyczny brief poza N
(1, 2, 3):

> Jesteś badaczem stylu redakcyjnego, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/redaktor_kategoryzator.md` i wykonaj go dokładnie.
> Korpus: `.tmp/redaktor_korpus.md`. Twój numer: N=<N>. Zapisz wzorce do
> `.tmp/redaktor_kat_<N>.md`. Twój zwrot = jedna linijka (ścieżka + liczba
> wzorców), NIE treść pliku.

Fallback: typ niezarejestrowany → `general-purpose` z `model: opus`, ten sam
brief. Poczekaj aż wszystkie 3 skończą.

## Step 3 — Synteza (Ty, in-session)

Przeczytaj `.tmp/redaktor_kat_{1,2,3}.md` + `workflows/guides/redakcja_wnioski.md`.
Progi i typy propozycji — wg `workflows/pipeline/redaktor.md` krok 3
(≥2/3 kategoryzatorów, ≥2 filmy, flaga generacji).

## Step 4 — Raport

Zapisz `docs/research/redaktor/raport_$(date +%F).md` wg sekcji z SOP (krok 4).
Pokaż userowi skrót: liczba wzorców potwierdzonych, trend ceiling, lista
propozycji jedną linijką każda.

## Step 5 — Manual gate + aplikacja

AskUserQuestion (multiSelect) z propozycjami DODAJ/WZMOCNIJ/WYGAŚ. Zaakceptowane
zaaplikuj do `workflows/guides/redakcja_wnioski.md` (max 10 aktywnych; format
wpisu z komentarza w tym pliku; daty; status wstępny/aktywny). Na koniec:

```bash
git add workflows/guides/redakcja_wnioski.md docs/research/redaktor/
git commit -m "feat(redaktor): wnioski po $1"
```

Nic nie zaakceptowane → commit samego raportu.

## Czego NIE robić
- NIE pokazuj kategoryzatorom `redakcja_wnioski.md` (ślepa re-walidacja).
- NIE edytuj `voice_brief.md`, promptu pisarza ani fixera.
- NIE aplikuj żadnego wniosku bez akceptu w Step 5.
```

- [ ] **Step 4: Commit**

```bash
git add workflows/pipeline/redaktor.md .claude/commands/redaktor.md
git commit -m "feat(redaktor): SOP satelity + komenda /redaktor

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: wpięcie wniosków w checkerów 3b (`/draft`)

**Files:**
- Modify: `workflows/pipeline/03b_section_checker.md` (sekcja `## Co dostajesz`)
- Modify: `workflows/pipeline/03b_arc_checker.md` (preambuła, przed `## Czego szukasz`)
- Modify: `.claude/commands/draft.md` (Step 4 — oba briefy)

- [ ] **Step 1: Section checker — dodaj bullet**

Read `workflows/pipeline/03b_section_checker.md`. W sekcji `## Co dostajesz` (po bullecie o nagłówku sekcji) dopisz:

```markdown
- (Jeśli lead podał w briefie) `workflows/guides/redakcja_wnioski.md` — profil
  redakcyjny usera z pętli Redaktora-ucznia: heurystyki uwagi (gdzie patrzeć
  ostrzej), NIE zakazy fraz. Przy konflikcie z `voice_brief.md` wygrywa
  voice_brief.
```

- [ ] **Step 2: Arc checker — dodaj akapit**

Read `workflows/pipeline/03b_arc_checker.md`. Po preambule (przed `## Czego szukasz`) dopisz ten sam sens jedną linijką:

```markdown
Jeśli lead podał w briefie `workflows/guides/redakcja_wnioski.md`, przeczytaj go
przed scenariuszem — to heurystyki uwagi z redakcji usera (nie zakazy); przy
konflikcie z `voice_brief.md` wygrywa voice_brief.
```

- [ ] **Step 3: draft.md Step 4 — rozszerz briefy**

W `.claude/commands/draft.md`, w Step 4, w briefie **(a)** section-checkerów, po zdaniu „Zapisz listę zgłoszeń do `outputs/videos_pl/$1/md/iter/sek_NN.md`." dopisz do cytatu:

```markdown
> Jeśli istnieje `workflows/guides/redakcja_wnioski.md` i ma ≥1 aktywny wniosek,
> przeczytaj go przed scenariuszem (profil redakcyjny usera — heurystyki uwagi,
> nie zakazy).
```

Analogicznie w briefie **(b)** arc-checkera, po zdaniu o zapisie do `iter/arc.md`, dopisz tę samą linijkę cytatu.

- [ ] **Step 4: Weryfikacja spójności**

Run: `grep -rn "redakcja_wnioski" workflows/ .claude/ | grep -v Binary`
Expected: trafienia w: `03b_section_checker.md`, `03b_arc_checker.md`, `draft.md` (×2), `redaktor.md`, `redaktor_kategoryzator.md` (0 trafień tam = OK, kategoryzator NIE zna pliku wniosków — sprawdź, że go tam NIE ma), `redakcja_wnioski.md`, `.claude/commands/redaktor.md`.

- [ ] **Step 5: Commit**

```bash
git add workflows/pipeline/03b_section_checker.md workflows/pipeline/03b_arc_checker.md .claude/commands/draft.md
git commit -m "feat(draft): checkerzy 3b czytają redakcja_wnioski.md (profil redakcyjny usera)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: CLAUDE.md + smoke checklist

**Files:**
- Modify: `CLAUDE.md` (Quick Command Reference + akapit satelity przy Align)

- [ ] **Step 1: Quick Command Reference**

W bloku komend CLAUDE.md (po linii `/animate <slug>`) dodaj:

```
/redaktor <slug>                           # Redaktor-uczeń — korpus par machine↔docx (tool) → 3 zimne kategoryzatory → synteza → raport + wnioski dla checkerów 3b (manual gate); po każdym docx passie
```

- [ ] **Step 2: Akapit satelity**

Po akapicie **Align Agent** w CLAUDE.md dodaj akapit:

```markdown
**Redaktor-uczeń — wzorce z docx-passów (2026-06-12):** `/redaktor <slug>` po każdym docx passie. `redaktor_pary.py` buduje `.tmp/redaktor_korpus.md` (pary zdań machine↔human ze WSZYSTKICH slugów, tag generacji), 3 zimne `redaktor-kategoryzator` (Opus) niezależnie kategoryzują wzorce, lead syntetyzuje (próg ≥2/3 kategoryzatorów + ≥2 filmy) → raport `docs/research/redaktor/` + propozycje do `workflows/guides/redakcja_wnioski.md` (manual gate; max 10 aktywnych, wygasanie po 2 pudłach). Wnioski czytają TYLKO checkerzy 3b (nigdy pisarz — to by odtwarzało banned-listy); kategoryzatorzy nigdy nie widzą obecnych wniosków (ślepa re-walidacja). `voice_brief.md` nietykalny. Spec: `docs/superpowers/specs/2026-06-12-redaktor-uczen-design.md`.
```

- [ ] **Step 3: Pełny test suite + commit**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/ -v`
Expected: 9 passed

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md — /redaktor (Redaktor-uczeń) w Quick Reference + akapit satelity

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

- [ ] **Step 4: Manualna weryfikacja E2E (z userem, w NOWEJ sesji)**

`/redaktor` używa nowego typu subagenta — typy ładują się na starcie sesji, więc pełny test zrobić w świeżej sesji (albo liczyć na fallback general-purpose). Checklist:
1. `/redaktor 3_wstyd_za_wlasne_zycie` przechodzi kroki 1–4 bez błędów.
2. `.tmp/redaktor_kat_{1,2,3}.md` istnieją i różnią się między sobą (niezależność).
3. Raport ma 4 sekcje; każdy wzorzec potwierdzony ma cytaty z ≥2 filmów.
4. Manual gate pokazuje propozycje; po akcepcie `redakcja_wnioski.md` ma wpisy w formacie z szablonu i licznik `(N/10)` zaktualizowany.
5. Kolejny `/draft` (dowolny slug) — checkerzy dostają plik wniosków w briefie.

---

## Self-review (wykonany przy pisaniu planu)

- **Pokrycie specu:** decyzje 1–3 ✓ (Task 5–7), architektura kroków 0–5 ✓ (Task 3, 4, 6), plik wniosków + reżim ✓ (Task 5), edge cases ✓ (SOP w Task 6 + strip_title w Task 2), testy ✓ (Task 1–3), nietykalne ✓ (mapa plików).
- **Placeholdery:** brak — każdy krok ma pełny kod/treść.
- **Spójność typów:** `pair_sentences` zwraca dict z kluczami używanymi w `corpus_for_pair` ✓; `SIMILAR`/`split_sentences`/`sentence_diff_stats` importowane z ceiling-report ✓; nazwy plików `.tmp/redaktor_korpus.md` i `.tmp/redaktor_kat_N.md` spójne między toolem, promptem, SOP i komendą ✓.
