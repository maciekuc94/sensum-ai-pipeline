"""
Agent 3b: Script Revisor (B++ v2 chain)
Reads the draft from Agent 3a and runs a full-script Copilot-style revision pass
applying 8 diff-derived revision moves on every sentence. On iteration 2+, also
reads the prior `03_review.md` from the Reviewer and the prior revised draft, and
addresses only the issues the Reviewer flagged.

Replaces former Agent 3b (single-weakest-moment critic).

Output goes to `md/03_script_draft.md` (overwrites previous iteration).

Usage:
    python tools/pipeline/agent3b_revisor.py "<slug>"
    python tools/pipeline/agent3b_revisor.py "<slug>" --iteration 2
"""

import argparse
import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, load_style_guide, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRAFT_FILENAME = "md/03a_draft.md"
REVIEW_FILENAME = "md/03_review.md"
PREV_REVISION_FILENAME = "md/03_script_draft.md"
OUTPUT_FILENAME = "md/03_script_draft.md"

CLAUDE_MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def _build_prompt(
    style_guide: str,
    narrative_architectures: str,
    draft_text: str,
    iteration: int,
    prior_review: str | None,
    prior_revision: str | None,
) -> str:
    iteration_block = ""
    if iteration > 1 and prior_review and prior_revision:
        iteration_block = f"""

## Iteration {iteration} — Reviewer flagged your previous revision

Reviewer feedback from previous iteration:

{prior_review}

Your previous revision (the one Reviewer flagged):

{prior_revision}

**Twoje zadanie w tej iteracji:** Wróć do ORYGINALNEGO draftu (Script Draft poniżej) jako bazy i zastosuj wszystkie wcześniejsze rewizje **plus** napraw konkretne issues które Reviewer wyflagował. Nie wprowadzaj nowych zmian poza tymi z listy Reviewera. Jeśli Reviewer powiedział "fix X w paragraph 4" — fix tylko X. Reszta poprzedniej revision musi zostać zachowana (jest already dobra wg Reviewera, skoro nie była flagged).
"""

    return f"""\
Jesteś Copilot-style revisorem dla polskich skryptów SENSUM. Twoja praca to **revision-pass na CAŁOŚCI skryptu** — sentence-by-sentence — z dyscypliną edytora który zna 8 konkretnych wzorców edycji wyciągniętych z empirycznej analizy diffa (oryginał vs ręcznie poprawiona wersja).

**Skrypt jest po polsku. Twój output również po polsku.**

## Twoja filozofia revision

To NIE jest single-weakest-moment critique. To jest **full-pass curation** — przechodzisz przez każde zdanie i pytasz: czy któryś z 8 revision moves powinien być zastosowany? Większość zdań zostawiasz nietkniętych — tylko te które **wyraźnie** odpowiadają jednemu z wzorców poniżej przepisujesz.

## 8 revision moves (każdy z przykładem oryginał → poprawione)

### 1. Embodied clarity (pokaż sensację, nie opisuj wrażenia)
❌ "To konkretne wrażenie w klatce piersiowej" → ✓ "Coś w klatce piersiowej"
❌ "Odczuwasz wewnątrz siebie tę dotkliwą obecność" → ✓ "Czujesz to. Coś w klatce."
**Test:** Zdanie zaczyna się od meta-formuły ("To...", "To wrażenie...") zamiast od czystej sceny? Przepisz.

### 2. Cut redundancy (negative-positive duplicates)
❌ "Nie smutek dokładnie. Nie zazdrość dokładnie." → ✓ "Nie smutek. Nie zazdrość."
❌ "Nie jest to gniew, a raczej coś bliższego..." → ✓ "Nie gniew. Coś bliższego..."
**Test:** "dokładnie", "raczej", "w pewnym sensie" mogłoby zniknąć bez zmiany znaczenia? Wytnij.

### 3. De-judging tone (neutralny opis, nie wewnętrzny osąd)
❌ "coś w tobie jest złamane" → ✓ "coś jest z tobą nie tak" (samo "z tobą", nie "w tobie")
❌ "twoja psychika jest uszkodzona" → ✓ "twój system działa inaczej"
**Test:** Słowo brzmi jak diagnoza pacjenta? Zamień na neutralny stan.

### 4. Generalize personal details (uniwersalny konkret, nie biograficzny)
❌ "ciocia przy wigilii, mama patrzyła, ojciec w samochodzie" → ✓ "komentarze słyszane od lat — przy rodzinnym stole, w samochodzie, w szkole, w internecie"
**Test:** Konkret jest imienny/personalny (jedna osoba) czy kategoryczny (typ sytuacji)? Dąż do kategorycznego.

### 5. Symbolic metaphor over numbered lists
❌ "do 30 mieszkanie, do 35 ślub, do 40 dzieci" → ✓ "wyobrażona tarcza z terminami, które rzekomo powinieneś już odhaczyć"
❌ "system mierzy: lajki, followersi, zarobki" → ✓ "system mierzy szczyty"
**Test:** Lista konkretów tam gdzie jedna metafora mogłaby to zamknąć? Zwiń.

### 6. Diagnostic over collapse-narrative
❌ "Coś się zepsuło niedawno" → ✓ "Problem pojawił się wtedy, gdy zmieniły się dane"
❌ "System nie działa już jak kiedyś" → ✓ "System został zaprojektowany do funkcjonowania w małej grupie, a dziś dostaje próbkę tysiąc razy większą"
**Test:** Mówisz "to się zepsuło" (collapse) czy "to działa jak zaprojektowane, tylko warunki się zmieniły" (diagnostic)? Wybieraj drugie.

### 7. Agency in Permission Practice (verb wyboru)
❌ "Cztery rzeczy, które możesz zauważyć..." → ✓ "Cztery rzeczy, które możesz zrobić..."
Dozwolone czasowniki agency: **zrobić / wypróbować / zauważyć / dać sobie / nieść ze sobą**. Domyślnie wybieraj **aktywne (zrobić/wypróbować)**; *zauważyć* używaj TYLKO gdy mechanizm skryptu jest naprawdę o zauważaniu.

### 8. Softening pressure (temporalne softenery)
❌ "Twoje ciało nie potrzebuje, żebyś rozwiązał problem" → ✓ "Twoje ciało nie potrzebuje, żebyś **teraz** rozwiązał problem"
❌ "Połóż dłoń na klatce piersiowej" → ✓ "Połóż dłoń na klatce piersiowej, **tam gdzie czujesz ciężar**"
Softener słowa: *teraz / na chwilę / tylko jedną minutę / wystarczy że / nie musisz / tam gdzie*. Każdy tip z imperatywem w Permission Practice MUSI mieć softener.

## Constraints

- **Preserve length ±10%** — nie wycinaj całych akapitów ani nie dodawaj nowych sekcji
- **Preserve voice** — warm therapist, ty/twój, polska intymność terapeutyczna
- **Preserve architecture choice** — pierwsza linia (ARCHITECTURE: ...) zostaje bez zmian
- **Preserve Permission Practice structure** — dokładnie 4 numerowane tipy, recognition close po sekcji
- **Jeśli zdanie jest already dobre** (nie pasuje do żadnego z 8 wzorców) — zostaw bez zmian
- **NIE dodawaj** stage directions w nawiasach kwadratowych ani `[EDITOR NOTE]` inline — Reviewer skanuje czysty tekst osobno
- **NIE zmieniaj** twierdzeń naukowych ani struktury narracyjnej — tylko prozę

## Polish voice hard rules (nigdy nie naruszaj)

- **Zakaz "I" na początku zdania** — "I twój mózg..." / "I oba..." to kalka angielskiego "And...". Przepisz jako: "A twój mózg..." (kontrast) lub zintegruj ze zdaniem poprzednim.
- **Zakaz "Bo" na początku zdania** — "Bo wygląda jakby..." to kalka angielskiego "Because...". Przekształć w zdanie podrzędne lub użyj spójnika wewnątrz zdania.
- **Brak hedgingu własnej obserwacji** — nie pisz "To brzmi banalnie, dopóki..." przed właściwą treścią. Mów wprost; nie uprzedzaj że coś "brzmi banalnie/dziwnie/prosto".
- **Brak meta-zapowiedzi** — nie pisz "Tu jest moment, w którym chcę, żebyś..." ani "Wróćmy do...". Wejdź od razu w treść.
- **PP tipy: somatic/głos, nie kognitywne listy** — "Wymień jedną rzecz" = lista (zakazane). Tip musi być aktem w ciele lub głosie: "Połóż", "Powiedz na głos", "Weź wdech", "Zauważ gdzie w ciele".
- **Brak meta-komentarza między PP a recognition close** — nie dodawaj akapitu wyjaśniającego tipy ("To są mikropraktyki...") po ostatnim tipie. PP → recognition close bezpośrednio.
{iteration_block}

## Style Guide (kontekst)
{style_guide}

## Narrative Architectures (kontekst)
{narrative_architectures}

## Script Draft (revisuj to)
{draft_text}

## Output
Zwróć **kompletny zrewidowany skrypt** — od pierwszej linii (ARCHITECTURE: ...) do ostatniej. Bez preambuły, bez komentarzy, bez listy zmian. Tylko czysty tekst skryptu.
"""


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, script_text: str, iteration: int) -> str:
    today = date.today().isoformat()
    return (
        f"# Script Revision: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Pass: Revisor (iteration {iteration})\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{script_text}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Agent 3b — Script Revisor (B++ v2)")
    parser.add_argument("slug", help="Output directory slug under outputs/videos_pl/")
    parser.add_argument("--iteration", type=int, default=1, help="Revision iteration number (default 1)")
    args = parser.parse_args()

    slug = args.slug.strip()
    iteration = args.iteration
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)
    if iteration < 1:
        print("Error: --iteration must be >= 1")
        sys.exit(1)

    print(f"\n=== Agent 3b: Script Revisor (iteration {iteration}) ===")
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
    print(f"  Style guide loaded ({len(style_guide):,} characters)")
    print(f"  Narrative architectures loaded ({len(narrative_architectures):,} characters)")

    # Step 2 — Read original draft (always from 3a)
    print(f"\n[2/4] Reading {DRAFT_FILENAME}...")
    try:
        draft_content = read_output(slug, DRAFT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3a first:")
        print(f'  python tools/pipeline/agent3a_draft.py "{slug}"')
        sys.exit(1)

    topic = "Unknown Topic"
    for line in draft_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Draft:"):
            topic = line[len("# Script Draft:"):].strip()
            break
        if line.startswith("# "):
            topic = line[2:].strip()
            break

    print(f"  Topic : {topic}")
    print(f"  Draft length: {len(draft_content):,} characters")

    # Step 2b — If iteration > 1, also read prior review + prior revision
    prior_review = None
    prior_revision = None
    if iteration > 1:
        try:
            prior_review = read_output(slug, REVIEW_FILENAME)
            print(f"  Prior review loaded ({len(prior_review):,} characters)")
        except FileNotFoundError:
            print(f"  Warning: iteration > 1 but no {REVIEW_FILENAME} found — treating as iteration 1")
            iteration = 1
        try:
            prior_revision = read_output(slug, PREV_REVISION_FILENAME)
            print(f"  Prior revision loaded ({len(prior_revision):,} characters)")
        except FileNotFoundError:
            print(f"  Warning: iteration > 1 but no {PREV_REVISION_FILENAME} found — treating as iteration 1")
            iteration = 1
            prior_review = None
            prior_revision = None

    # Step 3 — Call Claude
    print(f"\n[3/4] Calling Claude API for revision pass (iteration {iteration})...")
    prompt = _build_prompt(
        style_guide,
        narrative_architectures,
        draft_content,
        iteration,
        prior_review,
        prior_revision,
    )

    try:
        script_text, usage = query_claude(prompt, CLAUDE_MODEL, 8192, f"revision iter {iteration}")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    print(f"  Revised script received ({len(script_text):,} characters)")
    print(f"  Tokens: in={usage['input_tokens']:,} out={usage['output_tokens']:,}")

    # Step 4 — Save output (overwrites previous iteration)
    print(f"\n[4/4] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, script_text, iteration)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Next: agent3c_reviewer.py")


if __name__ == "__main__":
    main()
