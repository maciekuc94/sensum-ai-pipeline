"""
Agent 3c: Script Reviewer — LEGACY Gemini --api fallback

DEFAULT PATH (since 2026-05-29): the Reviewer runs **in-session in Claude Code on
Opus 4.8** as part of the `/draft` loop. No Gemini, no Anthropic API. The prompt
is the single source of truth in `workflows/pipeline/03c_reviewer.md`.

This script is kept only as a Gemini-3.1-Pro fallback. It reads the revised draft
from Agent 3b and judges it against critical-issue categories, outputting a
VERDICT (PASS/FLAG) + flagged issues. **Does NOT rewrite.** `parse_verdict` is a
shared helper imported by the orchestrator.

Output goes to `md/03c_review_iter{N}.md`.

Usage (legacy):
    python tools/pipeline/agent3c_reviewer.py "<slug>"
"""

import argparse
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, load_style_guide, query_gemini_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


GEMINI_MODEL = "gemini-3.1-pro-preview"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def _build_prompt(style_guide: str, narrative_architectures: str, revised_text: str) -> str:
    return f"""\
Jesteś quality reviewerem dla polskich skryptów SENSUM. Twoja praca to OCENIĆ zrewidowany skrypt — **nie przepisywać**.

**Skrypt jest po polsku. Twoja analiza również po polsku.**

## Twoja rola

Czytasz skrypt po revision pass. Skanujesz pod kątem **critical-issue categories** wymienionych poniżej. Wydajesz VERDICT: PASS (skrypt ready to ship) albo FLAG (jeden lub więcej critical issues — Revisor musi address w następnej iteracji).

**NIE PRZEPISUJESZ.** Jeśli widzisz issue — cytujesz exact quote ze skryptu i podajesz krótką sugestię kierunku (1 linia). Revisor zdecyduje jak konkretnie przepisać.

**Kalibracja:** default to FLAG jeśli uncertain. Lepiej iteracja więcej niż za luźny PASS.

## Critical-issue categories (każda triggeruje FLAG)

### A. Permission Practice integrity
- Sekcja istnieje? Dokładnie 4 numerowane tipy? Recognition close PO sekcji (nie kończy się na poradzie)?
- Każdy tip jest **ucieleśnioną mikropraktyką** (somatyczny akt, zauważanie, nazywanie, mikro-próg)?
- Żaden tip NIE brzmi jak: generyczny self-help ("porozmawiaj z terapeutą", "ustal granice"), scheduling ("zablokuj kalendarz"), list-making, homework framing, optymalizacja?
- Czasownik w nagłówku to **agency verb** (zrobić/wypróbować) NIE pasywne (zauważyć — chyba że mechanizm naprawdę o zauważaniu)?
- Każdy tip z imperatywem ma **temporalny softener** (teraz / na chwilę / tylko jedną minutę / wystarczy że / tam gdzie)?

### B. Banned phrases (research-framing, self-help, academic-textbook)
- **Research-framing:** "naukowcy odkryli", "badania pokazują", "wyniki badań", "z badań wynika", "psychologowie nazywają to", "neuronauka wykazała", "według badań", "dane pokazują", "jedno badanie", "meta-analiza", "w [roku]" jako wstęp do badania
- **Polish self-help duchowo-rozwojowy:** "po prostu BĄDŹ", "zaufaj procesowi", "wszechświat ci podpowiada", "wibruj wyżej", "to nie przypadek że...", "energie się rozeszły"
- **Polish academic-textbook:** "warto zauważyć", "należy podkreślić", "kluczowe jest", "istotne wydaje się", "na uwagę zasługuje", "nie sposób pominąć", "co ciekawe"

### C. Abstract-meta language patterns
- Zdania zaczynające się od meta-formuły ("To konkretne wrażenie...", "To uczucie pojawia się gdy...") zamiast od czystej sceny
- Meta-zapowiedzi: "Teraz patrzymy gdzie...", "Teraz spojrzymy na...", "Zobaczmy razem...", "Przyjrzyjmy się..."

### D. Voice inconsistency (kalki z angielskiego, bezosobowe konstrukcje)
- Zdania zaczynające się od "I", "Bo", "A", "Ale", "Bowiem" (kalka z EN "And/Because")
- Bezosobowe konstrukcje: "mówi się że", "uważa się że", "trzeba", "należy", "powinno się"
- Anthropomorfizacja uczuć: "ma imię", "mieszka w", "krzyczy w tobie" (Tumblr poetry)
- Hedging: "być może", "prawdopodobnie", "wydaje się że", "raczej"

### E. Numbered list outside Permission Practice
- Numerowane listy preskrypcyjne są dozwolone TYLKO w Permission Practice. Jeśli znajdziesz numerowaną listę gdziekolwiek indziej — FLAG.

### F. Research-numbers w narracji
- Dziesiętne (0,62), effect sizes (d = X, r = X), p-values, liczby badań ("94 eksperymenty"), liczby uczestników ("8000 osób"), terminy metodologiczne (pre-registered, double-blind, longitudinalne, meta-analiza)

### G. Imienne biograficzne szczegóły
- Konkrety personalne ("ciocia Hania", "szef Marek przy zebraniu", "babcia w Krakowie") zamiast kategorycznych ("ktoś w pracy", "starsza osoba w rodzinie")

## Output schema (sztywny — parser oczekuje tego dokładnie)

```
## VERDICT
PASS

## Critical Issues
(empty — none found)

## Minor Notes (informational, don't block ship)
- (optional stylistic observations)

## Telemetry
- Iteration: 1
- Word count: ~NNN
- Architecture: <declared in script>
```

ALBO (jeśli FLAG):

```
## VERDICT
FLAG

## Critical Issues
- **[A. Permission Practice]**: "exact quote from script" → suggestion direction
- **[B. Banned phrase — academic]**: "warto zauważyć" w paragraph 4 → wytnij lub przepisz na bezpośrednie
- **[C. Abstract-meta]**: "To uczucie pojawia się gdy" w intro → pokaż sensację zamiast opisywać

## Minor Notes (informational, don't block ship)
- (optional)

## Telemetry
- Iteration: 1
- Word count: ~NNN
- Architecture: <declared>
```

**Bardzo ważne:** trzymaj się dokładnie tej struktury markdown z nagłówkami `## VERDICT`, `## Critical Issues`, `## Minor Notes`, `## Telemetry`. Pierwsza linia po `## VERDICT` to musi być DOKŁADNIE `PASS` albo `FLAG` (nic więcej). Parser tego oczekuje.

## Style Guide (kontekst)
{style_guide}

## Narrative Architectures (kontekst)
{narrative_architectures}

## Revised Script (review this)
{revised_text}

Zwróć WYŁĄCZNIE strukturę markdown opisaną wyżej. Bez preambuły, bez komentarzy.
"""


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, review_text: str) -> str:
    today = date.today().isoformat()
    return (
        f"# Script Review: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {GEMINI_MODEL}\n"
        f"Pass: Reviewer\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{review_text}\n"
    )


# ---------------------------------------------------------------------------
# Verdict parser (used by orchestrator)
# ---------------------------------------------------------------------------


def parse_verdict(review_content: str) -> str:
    """Extract 'PASS' or 'FLAG' from a review file content.

    Looks for the line immediately following '## VERDICT'. Returns 'PASS', 'FLAG',
    or 'UNKNOWN' if the schema is malformed.
    """
    lines = review_content.splitlines()
    for i, line in enumerate(lines):
        if line.strip() == "## VERDICT":
            for j in range(i + 1, min(i + 5, len(lines))):
                candidate = lines[j].strip()
                if candidate in ("PASS", "FLAG"):
                    return candidate
            return "UNKNOWN"
    return "UNKNOWN"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 3c — Script Reviewer (B++ v2)")
    parser.add_argument("slug", help="Output directory slug under outputs/videos_pl/")
    parser.add_argument("--iteration", type=int, default=1, help="Review iteration number (default 1)")
    args = parser.parse_args()

    slug = args.slug.strip()
    iteration = args.iteration
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 3c: Script Reviewer (iteration {iteration}) ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Load style guides
    print("[1/4] Loading style guides...")
    try:
        style_guide = load_style_guide()
        narrative_architectures = load_style_guide("narrative_architectures.md")
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)

    # Step 2 — Read revised draft
    revised_filename = f"md/03b_revised_iter{iteration}.md"
    print(f"\n[2/4] Reading {revised_filename}...")
    try:
        revised_content = read_output(slug, revised_filename)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3b first:")
        print(f'  python tools/pipeline/agent3b_revisor.py "{slug}" --iteration {iteration}')
        sys.exit(1)

    topic = "Unknown Topic"
    for line in revised_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Revision:") or line.startswith("# Script Draft:"):
            topic = line.split(":", 1)[1].strip()
            break
        if line.startswith("# "):
            topic = line[2:].strip()
            break

    print(f"  Topic : {topic}")
    print(f"  Revised script length: {len(revised_content):,} characters")

    # Step 3 — Call Gemini
    print(f"\n[3/4] Calling Gemini API for review...")
    prompt = _build_prompt(style_guide, narrative_architectures, revised_content)

    try:
        review_text, usage = query_gemini_text(prompt, GEMINI_MODEL, 8192, "review")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Gemini API call failed — {exc}")
        sys.exit(1)

    print(f"  Review received ({len(review_text):,} characters)")
    print(f"  Tokens: in={usage['input_tokens']:,} out={usage['output_tokens']:,}")

    # Step 4 — Save output + display verdict
    output_filename = f"md/03c_review_iter{iteration}.md"
    print(f"\n[4/4] Saving output to {output_filename}...")
    content = build_output(topic, review_text)
    output_path = write_output(slug, output_filename, content)
    print(f"  Saved: {output_path}")

    verdict = parse_verdict(review_text)
    print(f"\n  VERDICT: {verdict}")
    if verdict == "FLAG":
        print(f"  → Run Agent 3b again with --iteration {iteration + 1} to address flagged issues")
    elif verdict == "PASS":
        print(f"  → Ready to copy md/03b_revised_iter{iteration}.md → md/04_final.md")
    else:
        print(f"  → Warning: verdict could not be parsed; check {output_filename} manually")


if __name__ == "__main__":
    main()
