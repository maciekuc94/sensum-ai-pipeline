"""
Agent 4b: Hook Refiner (two-tier, iterative)

Evaluates the polished script produced by Agent 4a using a two-tier rubric:

  Tier 1 — 15-Second Window (first 37 words). Primary gate. Pass = >= 8/10.
  Tier 2 — 30-Second Hook (first 150-200 words). Secondary. Pass = >= 7/10.

If either tier fails, the agent rewrites the first 37 words IN-PLACE in
04_script_final.md and re-scores. Up to MAX_ATTEMPTS passes. The original
opening is preserved once as 04_script_final.bak.md.

Reference: docs/specs/2026-05-15-15-second-hook-research.md
Chain: 3a -> 3b -> 3c -> 4a -> 4b -> record

Usage:
    python tools/agent4b_hook.py "emotional-dysregulation-in-adhd"
"""

import re
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

INPUT_FILENAME = "md/04_script_final.md"
BACKUP_FILENAME = "md/04_script_final.bak.md"
LOG_FILENAME = "md/04b_hook_score.md"

CLAUDE_MODEL = "claude-sonnet-4-6"

WORDS_15S = 37          # ~15 seconds at 150 wpm
WORDS_30S = 200         # full hook window
MAX_ATTEMPTS = 3
T1_PASS = 8
T2_PASS = 7

# Lines we skip when locating the start of actual narration.
_META_LINE_PATTERNS = [
    re.compile(r"^\s*#"),                       # markdown headings
    re.compile(r"^\s*Generated:", re.I),
    re.compile(r"^\s*Model:", re.I),
    re.compile(r"^\s*Pass:", re.I),              # "Pass: 1 of 3 (Draft)", "Pass: 3 of 3 (Rewrite applied)"
    re.compile(r"^\s*Editor notes", re.I),
    re.compile(r"^\s*Estimated duration:", re.I),
    re.compile(r"^\s*ARCHITECTURE:", re.I),
    re.compile(r"^\s*-{3,}\s*$"),                # horizontal rules
]


SYSTEM_PROMPT = """\
Jesteś hook refinerem dla polskiego kanału psychologicznego YouTube SENSUM. Oceniasz otwarcie wypolerowanego skryptu używając dwustopniowej rubryki i produkujesz przepisane otwarcie kiedy potrzeba.

**Skrypt jest po polsku. Twoja analiza i przepisanie również po polsku. NAZWY PÓL OUTPUTU (TIER1_SCORE, REWRITE_15S, VERDICT, itp.) pozostają po angielsku — parser kodu na nich polega.**

Robocza teoria kanału dotycząca okna 15 sekund jest w docs/specs/2026-05-15-15-second-hook-research.md. Aplikuj ją.

## Tier 1 - 15-Second Window (PRIMARY)

Pierwsze ~37 słów narracji. Tu algorytm YouTube i mózg widza oba decydują czy oglądać dalej. Punktuj 1-10 w skali:

  - First-Sentence Grip (0-3): czy zdanie 1 samo w sobie zapracowuje na zdanie 2?
    Konkretny podmiot, <=14 słów, bez abstrakcyjnego stackowania.
  - Specificity Within 15s (0-3): konkretny szczegół / obraz / liczba (zaokrąglona) /
    stan ciała / scena pojawia się do słowa 37.
  - Identification Moment (0-2): widz myśli "to ja" do słowa 37.
  - Loop Opened (0-2): nierozwiązane pytanie lub sprzeczność jest trzymana
    w głowie widza, której musi dokończyć oglądania żeby zamknąć.

Aplikuj -1 punkt karny za KAŻDY red flag wyzwolony (wymień je):
  - Otwiera retorycznym pytaniem ("Czy kiedykolwiek...?")
  - Prowadzi statystyką przed jakimkolwiek emocjonalnym setupem
  - Pierwsze zdanie dłuższe niż 14 słów
  - Brak konkretnego szczegółu do słowa 25
  - Używa "wielu ludzi" / "wszyscy" / "większość z nas"
  - Stackowane abstrakcyjne rzeczowniki w zdaniu 1
  - Jakakolwiek klauzula którą można skasować bez utraty znaczenia
  - Prosi widza o "zasubskrybuj", "polub", "zostań z nami"
  - Meta-framing ("dzisiaj porozmawiamy o", "w tym filmie omówimy")
  - Research-framing w pierwszych 37 słowach: jakikolwiek z "naukowcy odkryli",
    "badania pokazują", "wyniki badań", "z badań wynika", "neuronauka wykazała",
    "jedno badanie", "ostatnie badanie", "meta-analiza", "dane pokazują",
    "psychologowie nazywają to", "nauka jest jasna". Widz ufa mówcy,
    nie cytatowi. Research jest niewidoczny.
  - Notacja statystyczna lub precyzyjne findings w pierwszych 37 słowach:
    dziesiętne (0,62), effect sizes (d = X, r = X), p-values, liczby badań
    ("94 eksperymenty"), liczby uczestników ("8000 osób"), terminy metodologiczne
    (pre-registered, double-blind, longitudinalne, meta-analiza), lub jakikolwiek
    inny artefakt research-paperowy.
  - Wyjaśnia mechanizm przed wylądowaniem uczucia — widz powinien rozpoznać
    siebie zanim jakiekolwiek wyjaśnienie się zacznie.
  - Polskie cringe self-help frazy ("po prostu BĄDŹ", "zaufaj procesowi",
    "wszechświat ci podpowiada", "wibruj wyżej") w pierwszych 37 słowach
  - Polskie academic-textbookowe frazy ("warto zauważyć", "należy podkreślić",
    "kluczowe jest") w pierwszych 37 słowach

Próg zaliczenia: 8/10.

## Tier 2 - 30-Second Hook (SECONDARY)

Pierwsze ~150-200 słów. Co dzieje się PO otwarciu bramki 15s. Punktuj 1-10:

  - Tension (0-3): nierozwiązane pytanie lub sprzeczność się utrzymuje.
  - Personal Relevance (0-3): widz nadal czuje że to jest o nim.
  - Specificity (0-2): konkretne szczegóły kontynuują, bez abstrakcyjnego dryfu.
  - Forward Momentum (0-2): ostatnia linia hooka sprawia że zatrzymanie się
    wydaje niemożliwe.

Próg zaliczenia: 7/10.

## Instrukcja przepisania

MUSISZ wyprodukować przepisane pierwsze 37 słów dla Tier 1, za każdym razem, nawet kiedy wynik już zalicza. Jeśli istniejące otwarcie jest świetne, zwróć je verbatim. Jeśli jest słabe, przepisz używając jednego z sześciu wzorców z research doc (Anomalous Case / Inverted Truth / Direct Question / Visceral Image / Self-Audit / Stakes Reveal). Przepisanie musi:

  - Być dokładnie <=37 słów (uwaga: polski jest "gęstszy" niż angielski, ale
    37 słów polskich nadal mieści się w ~15 sekundach przy ~130 wpm polskim).
  - Czytać się na głos w <=15 sekund.
  - Pasować do voice kanału: ciepły terapeuta rozmawiający z jedną osobą.
    Najpierw waliduj uczucie, potem zasugeruj mechanizm. Nie listicle
    energy, nie lecture energy.
  - Research jest niewidoczny: BEZ "naukowcy odkryli", BEZ "badania pokazują",
    BEZ "wyniki badań", BEZ "z badań wynika", BEZ "neuronauka wykazała",
    BEZ "jedno badanie", BEZ "meta-analiza", BEZ "psychologowie nazywają to",
    BEZ notacji statystycznej, BEZ dziesiętnych, BEZ liczb badań, BEZ terminów
    metodologicznych. Mówca po prostu wie. Prawdziwe cytaty żyją w opisie YouTube.
  - Najpierw prosty język — nigdy nie nazywaj terminu naukowego i potem go
    nie tłumacz. Jeśli termin w ogóle się pojawia, to raz, późno.
  - Bez zbanowanych fraz (bez "Czy kiedykolwiek", bez "wielu ludzi", bez
    "zostań z nami").
  - Bez polskich cringe self-help fraz ("po prostu BĄDŹ", "zaufaj procesowi").
  - Zachowaj tę samą architekturę i temat co oryginał.

## Output Format - MANDATORY

Zwróć DOKŁADNIE ten szablon, bez preambuły i bez końcowej prozy. **Nazwy pól (TIER1_SCORE, REWRITE_15S, VERDICT, itp.) pozostają po angielsku — parser ich szuka:**

TIER1_SCORE: <int 1-10>
TIER1_BREAKDOWN:
- First-Sentence Grip: <n>/3 - <jedno zdanie po polsku>
- Specificity Within 15s: <n>/3 - <jedno zdanie po polsku>
- Identification Moment: <n>/2 - <jedno zdanie po polsku>
- Loop Opened: <n>/2 - <jedno zdanie po polsku>
TIER1_RED_FLAGS: <lista po przecinkach lub "none">

TIER2_SCORE: <int 1-10>
TIER2_BREAKDOWN:
- Tension: <n>/3 - <jedno zdanie po polsku>
- Personal Relevance: <n>/3 - <jedno zdanie po polsku>
- Specificity: <n>/2 - <jedno zdanie po polsku>
- Forward Momentum: <n>/2 - <jedno zdanie po polsku>

BIGGEST_WEAKNESS: <jedno zdanie po polsku nazywające pojedynczy największy problem w oknie 15s>

REWRITE_15S:
<<<
<przepisane pierwsze 37 słów po polsku, <=37 słów, bez cudzysłowów, bez markdown>
>>>

VERDICT: <"record" | "polish" | "rewrite">
"""


# ---------------------------------------------------------------------------
# Helpers - narration extraction & splicing
# ---------------------------------------------------------------------------


def _is_meta_line(line: str) -> bool:
    return any(p.search(line) for p in _META_LINE_PATTERNS)


def _find_narration_start(script: str) -> int:
    """Return the character offset of the first real narration line.

    Skips metadata headers, blank lines, ARCHITECTURE declarations, etc.
    """
    pos = 0
    for line in script.splitlines(keepends=True):
        if line.strip() == "" or _is_meta_line(line):
            pos += len(line)
            continue
        return pos
    # Fallback: no narration found
    return 0


def _strip_inline_markers(text: str) -> str:
    """Remove [EDITOR NOTE: ...] and [IMAGE: ...] and similar bracket markers."""
    text = re.sub(r"\[EDITOR NOTE:[^\]]*\]", "", text)
    text = re.sub(r"\[IMAGE:[^\]]*\]", "", text)
    text = re.sub(r"\[Visual Pause\]", "", text, flags=re.I)
    return text


def _word_count(text: str) -> int:
    return len(text.split())


def _take_words_with_sentence_extension(words: list[str], n: int, lookahead: int = 6) -> str:
    """Take the first n words; if the n-th word does not end a sentence, peek up to
    `lookahead` additional words for a sentence terminator and include them."""
    base = words[:n]
    if base and base[-1].endswith((".", "!", "?")):
        return " ".join(base)
    # Look ahead a few words for a sentence terminator
    for i in range(n, min(n + lookahead, len(words))):
        if words[i].endswith((".", "!", "?")):
            return " ".join(words[: i + 1])
    return " ".join(base)


def _extract_15s_window(script: str) -> str:
    """Return the first ~37 words of clean narration text, sentence-aware."""
    start = _find_narration_start(script)
    body = _strip_inline_markers(script[start:])
    words = body.split()
    return _take_words_with_sentence_extension(words, WORDS_15S).strip()


def _extract_30s_window(script: str) -> str:
    """Return the first ~200 words of clean narration text, sentence-aware."""
    start = _find_narration_start(script)
    body = _strip_inline_markers(script[start:])
    words = body.split()
    return _take_words_with_sentence_extension(words, WORDS_30S, lookahead=15).strip()


def _extract_topic(script: str) -> str:
    for line in script.splitlines():
        line = line.strip()
        if line.startswith("# Script Final:"):
            return line[len("# Script Final:") :].strip()
        if line.startswith("# Script Draft:"):
            return line[len("# Script Draft:") :].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _splice_first_37_words(script: str, new_opening: str) -> str:
    """Replace the first complete sentences spanning ~37 words with new_opening.

    Strategy: find the narration start, walk through it sentence-by-sentence
    until the accumulated word count >= WORDS_15S, replace that block, keep
    everything after byte-identical.
    """
    start = _find_narration_start(script)
    pre = script[:start]
    body = script[start:]

    # Walk sentences. A "sentence" ends at . ! or ? followed by whitespace or EOF.
    sentence_pattern = re.compile(r"[^.!?]+[.!?]+(?:\s+|$)|[^.!?]+$", re.S)
    word_total = 0
    cutoff = 0
    for match in sentence_pattern.finditer(body):
        sentence = match.group(0)
        clean = _strip_inline_markers(sentence)
        word_total += _word_count(clean)
        cutoff = match.end()
        if word_total >= WORDS_15S:
            break

    if cutoff == 0:
        # Pathological case: no sentence boundary found. Replace the first
        # WORDS_15S words by character iteration.
        words_seen = 0
        in_word = False
        i = 0
        while i < len(body) and words_seen < WORDS_15S:
            ch = body[i]
            if ch.isalnum() or ch in "'-":
                if not in_word:
                    words_seen += 1
                    in_word = True
            else:
                in_word = False
            i += 1
        cutoff = i

    trailing = body[cutoff:]
    # Ensure new_opening ends with sentence punctuation; add a paragraph break
    # before the trailing content for readability.
    new_opening = new_opening.strip()
    if not new_opening.endswith((".", "!", "?")):
        new_opening += "."
    # Preserve a paragraph separator before trailing text.
    separator = "\n\n" if trailing.strip() else "\n"
    return pre + new_opening + separator + trailing.lstrip("\n")


def _ensure_backup(slug: str, original_content: str) -> bool:
    """Create the backup file if it does not already exist. Returns True if created."""
    try:
        read_output(slug, BACKUP_FILENAME)
        return False
    except FileNotFoundError:
        write_output(slug, BACKUP_FILENAME, original_content)
        return True


# ---------------------------------------------------------------------------
# Claude response parsing
# ---------------------------------------------------------------------------


def _parse_response(text: str) -> dict:
    """Parse the structured response from Claude. Tolerant of minor drift."""
    def _grab_int(pattern: str, fallback: int = 0) -> int:
        m = re.search(pattern, text)
        return int(m.group(1)) if m else fallback

    def _grab_block(start_marker: str, end_marker: str) -> str:
        m = re.search(
            re.escape(start_marker) + r"\s*(.*?)\s*" + re.escape(end_marker),
            text,
            re.S,
        )
        return m.group(1).strip() if m else ""

    t1_score = _grab_int(r"TIER1_SCORE:\s*(\d+)")
    t2_score = _grab_int(r"TIER2_SCORE:\s*(\d+)")

    t1_breakdown = _grab_block("TIER1_BREAKDOWN:", "TIER1_RED_FLAGS:")
    t2_breakdown = _grab_block("TIER2_BREAKDOWN:", "BIGGEST_WEAKNESS:")

    red_flags_match = re.search(r"TIER1_RED_FLAGS:\s*(.*?)\n", text)
    red_flags = red_flags_match.group(1).strip() if red_flags_match else "none"

    weakness_match = re.search(r"BIGGEST_WEAKNESS:\s*(.+?)\n", text)
    weakness = weakness_match.group(1).strip() if weakness_match else ""

    rewrite_match = re.search(r"REWRITE_15S:\s*<<<\s*(.*?)\s*>>>", text, re.S)
    rewrite = rewrite_match.group(1).strip() if rewrite_match else ""

    verdict_match = re.search(r"VERDICT:\s*\"?(\w+)\"?", text)
    verdict = verdict_match.group(1).strip().lower() if verdict_match else ""

    return {
        "t1_score": t1_score,
        "t2_score": t2_score,
        "t1_breakdown": t1_breakdown,
        "t2_breakdown": t2_breakdown,
        "red_flags": red_flags,
        "weakness": weakness,
        "rewrite": rewrite,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def _bar(score: int) -> str:
    score = max(0, min(10, score))
    return "█" * score + "░" * (10 - score)


def _format_attempt_log(attempt_num: int, parsed: dict, applied: bool) -> str:
    return (
        f"## Attempt {attempt_num}\n"
        f"### Tier 1 — 15-Second Window: {parsed['t1_score']}/10  [{_bar(parsed['t1_score'])}]\n"
        f"{parsed['t1_breakdown']}\n\n"
        f"**Red flags triggered:** {parsed['red_flags']}\n\n"
        f"### Tier 2 — 30-Second Hook: {parsed['t2_score']}/10  [{_bar(parsed['t2_score'])}]\n"
        f"{parsed['t2_breakdown']}\n\n"
        f"**Biggest weakness:** {parsed['weakness']}\n\n"
        f"### Rewritten first 37 words ({'applied to 04_script_final.md' if applied else 'not applied — already passing'}):\n"
        f"> {parsed['rewrite']}\n"
        f"\n"
        f"_(words: {_word_count(parsed['rewrite'])})_\n"
        f"\n---\n\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python tools/agent4b_hook.py "<slug>"')
        print('Example: python tools/agent4b_hook.py "emotional-dysregulation-in-adhd"')
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print("\n=== Agent 4b: Hook Refiner (two-tier, iterative) ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Load current script and back up the original opening on first run
    print(f"[1] Reading {INPUT_FILENAME}...")
    try:
        script = read_output(slug, INPUT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 4a first:")
        print(f'  python tools/agent4a_edit.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic(script)
    print(f"  Topic: {topic}")

    backup_created = _ensure_backup(slug, script)
    if backup_created:
        print(f"  Backup created: {BACKUP_FILENAME}")
    else:
        print(f"  Backup already exists: {BACKUP_FILENAME} (preserved)")

    # Step 2 — Iterative refine loop
    attempt_logs: list[str] = []
    final_parsed: dict | None = None
    attempts_used = 0
    applied_any_rewrite = False

    for attempt in range(1, MAX_ATTEMPTS + 1):
        attempts_used = attempt
        print(f"\n[2.{attempt}] Scoring with Claude (attempt {attempt}/{MAX_ATTEMPTS})...")

        hook15 = _extract_15s_window(script)
        hook30 = _extract_30s_window(script)

        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"## Otwarcie skryptu do oceny\n\n"
            f"### Obecne pierwsze 37 słów (okno Tier 1):\n{hook15}\n\n"
            f"### Obecne pierwsze 200 słów (okno Tier 2):\n{hook30}\n"
        )

        try:
            response_text, _ = query_claude(prompt, CLAUDE_MODEL, 2048, "hook refiner")
        except EnvironmentError as exc:
            print(f"\nError: {exc}")
            sys.exit(1)
        except Exception as exc:
            print(f"\nError: Claude API call failed — {exc}")
            sys.exit(1)

        parsed = _parse_response(response_text)
        final_parsed = parsed

        t1, t2 = parsed["t1_score"], parsed["t2_score"]
        print(f"  Tier 1 (15s): {t1}/10  [{_bar(t1)}]")
        print(f"  Tier 2 (30s): {t2}/10  [{_bar(t2)}]")

        passed = t1 >= T1_PASS and t2 >= T2_PASS
        rewrite = parsed["rewrite"]
        rewrite_wc = _word_count(rewrite)

        # Apply rewrite if needed (and if it is valid)
        apply_rewrite = False
        if not passed:
            if not rewrite:
                print("  Warning: refiner returned an empty rewrite. Skipping splice.")
            elif rewrite_wc > WORDS_15S:
                print(f"  Warning: rewrite is {rewrite_wc} words (>{WORDS_15S}). Skipping splice.")
            else:
                script = _splice_first_37_words(script, rewrite)
                write_output(slug, INPUT_FILENAME, script)
                apply_rewrite = True
                applied_any_rewrite = True
                print(f"  Applied rewrite ({rewrite_wc} words) to {INPUT_FILENAME}.")

        attempt_logs.append(_format_attempt_log(attempt, parsed, apply_rewrite))

        if passed:
            print("  Both tiers pass thresholds — stopping.")
            break

    # Step 3 — Build verdict and write the log
    assert final_parsed is not None
    t1, t2 = final_parsed["t1_score"], final_parsed["t2_score"]
    final_passed = t1 >= T1_PASS and t2 >= T2_PASS

    if final_passed:
        verdict = "record"
    elif attempts_used >= MAX_ATTEMPTS:
        verdict = "rewrite"
    else:
        verdict = "polish"

    print(f"\n[3] Final verdict: {verdict.upper()}")
    print(f"  Attempts used: {attempts_used}/{MAX_ATTEMPTS}")
    print(f"  Final 15s score: {t1}/10")
    print(f"  Final 30s score: {t2}/10")
    if applied_any_rewrite:
        print(f"  Original opening preserved at: {BACKUP_FILENAME}")
        print(f"  To revert: copy {BACKUP_FILENAME} over {INPUT_FILENAME}")

    today = date.today().isoformat()
    log = (
        f"# Hook Refiner Log: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Source: {INPUT_FILENAME}\n"
        f"Backup: {BACKUP_FILENAME}\n"
        f"\n---\n\n"
        + "".join(attempt_logs)
        + f"## Final\n"
        f"- Final 15s score: **{t1}/10**\n"
        f"- Final 30s score: **{t2}/10**\n"
        f"- Attempts used: {attempts_used}/{MAX_ATTEMPTS}\n"
        f"- Verdict: **{verdict}**\n"
        f"- Backup of original opening: `{BACKUP_FILENAME}`\n"
    )
    write_output(slug, LOG_FILENAME, log)
    print(f"\n  Log saved: {LOG_FILENAME}")

    if verdict == "rewrite":
        print("\nNext: open the script and rewrite the opening by hand. "
              "Then re-run this agent to confirm both tiers pass.")
    elif verdict == "polish":
        print("\nNext: consider re-running once more, or accept the current state.")
    else:
        print("\nNext: proceed to Agent 5 (visuals) and Agent 6 (narration).")


if __name__ == "__main__":
    main()
