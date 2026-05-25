"""
Agent 4a: Script Editing
Reads the script draft produced by Agent 3 and uses the Anthropic Claude API
to perform stylistic copy-editing, producing a polished, production-ready
narration script.

Usage:
    python tools/agent4a_edit.py "emotional-dysregulation-in-adhd"

Takes the SLUG (not the topic) because the script draft was already written
by Agent 3.
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, load_style_guide, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/03_script_draft.md"
OUTPUT_FILENAME = "md/04_script_final.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------



def _load_narrative_architectures() -> str:
    """Load the narrative architectures SOP from workflows/narrative_architectures.md."""
    return load_style_guide("narrative_architectures.md")


def _extract_topic_from_script(script_content: str) -> str:
    """Extract the topic from the first heading of the script draft file."""
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Draft:"):
            return line[len("# Script Draft:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _build_prompt(style_guide: str, narrative_architectures: str, script_content: str) -> str:
    """Build the editing prompt for Claude."""
    return f"""\
Jesteś profesjonalnym redaktorem skryptów dla polskiego kanału psychologicznego YouTube SENSUM.

**Skrypt jest po polsku. Twój output również po polsku (włącznie z [EDITOR NOTE] po polsku).**

## Style Guide (zasady które egzekwujesz)
{style_guide}

## Architektury Narracyjne (zbanowane frazy i zasady strukturalne które egzekwujesz)
{narrative_architectures}

## Script Draft (to co edytujesz)
{script_content}

## Twoje zadanie
Zredaguj szkic skryptu powyżej tak żeby czytał się naturalnie kiedy wypowiadany na głos i w pełni przestrzegał style guide. Jesteś copy editorem — poprawiasz jakość prozy, flow, rytm i dobór słów. NIE zmieniasz twierdzeń naukowych.

### Zasady edycji

1. **Naturalny flow mowy** — Wytnij lub przepisz każde zdanie które brzmi akademicko, bezosobowo lub hedgingowo. Każda linia musi brzmieć jak ciepły terapeuta rozmawiający z jedną osobą. Widz ufa mówcy, nie cytatowi.

2. **Najpierw prosty język, nigdy jargon-then-translation** — Jeśli szkic wprowadza termin naukowy i potem go tłumaczy ("dysregulacja emocjonalna — czyli rozregulowanie emocji…"), PRZEPISZ tak żeby prosty język prowadził. Usuń termin całkowicie chyba że sama nazwa jest naprawdę zapamiętywalna. Jeśli zostawisz termin, umieść go raz, późno, po tym jak codzienny opis wylądował. Nigdy nie wprowadzaj terminu tylko po to żeby go przetłumaczyć.

3. **Research jest niewidoczny — wytnij całe research-framingowe language.** Skanuj i przepisz/wytnij każdy przypadek: "naukowcy odkryli", "badania pokazują", "wyniki badań", "z badań wynika", "ostatnie badania", "badanie z 2019", "meta-analiza", "w N badaniach", "dane pokazują", "według badań", "nauka jest jasna", "psychologowie nazywają to", "neuronaukowcy nazywają to", "neuronauka wykazała", "w [roku]" wprowadzającym badanie. Zamień na bezpośrednie twierdzenia w głosie mówcy — nie podmieniając na inną frazę research-framingową. Zastąpieniem jest nieobecność, nie inny cytat. Przykład: "Z badań wynika że twój mózg robi X" → "Twój mózg robi X". Dodaj [EDITOR NOTE] dla każdej istotnej zmiany.

4. **Bez liczb jako findings** — Skanuj i przepisz: dziesiętne (0,62), effect sizes (d = X, r = X), p-values, liczby badań ("94 eksperymenty"), liczby uczestników ("8000 osób"), terminy metodologiczne (pre-registered, double-blind, longitudinalne, meta-analiza), notacja statystyczna w jakiejkolwiek formie. Zamień na zaokrąglone, opisowe liczby ("około połowa", "większość ludzi", "w wielu przypadkach") lub wytnij całkowicie. Jeśli liczba nie ląduje emocjonalnie w prostym polskim, wytnij.

5. **Różnorodność zdań** — Mieszaj krótkie uderzające zdania z fragmentami dla emfazy. Rozbijaj długie lub złożone zdania. Polski naturalnie ma dłuższe zdania podrzędne — równoważ kontrastem.

6. **Bez konstrukcji bezosobowych** — Polska gramatyka pozwala na bezosobowe formy ("mówi się", "uważa się", "powiada się", "trzeba", "należy", "powinno się") które brzmią klinicznie i dystansująco. Przepisuj na konstrukcje osobowe ("ja mówię ci", "ty czujesz", "twój mózg robi") i flaguj zmianę.

7. **Bez hedgingu — zamień na bezpośrednie twierdzenia, nie research framing** — Zamień "być może", "prawdopodobnie", "wydaje się", "może okazać się że", "raczej", "z pewnymi badaniami sugerującymi" na bezpośrednie twierdzenia w głosie mówcy. "Twój mózg robi X" wygrywa nad "Z badań wynika że twój mózg robi X". NIE podmieniaj hedgingu na frazy research-framingowe.

8. **Łuk emocjonalny** — Waliduj uczucie zanim wyjaśnisz mechanizm. Widz powinien rozpoznać siebie zanim jakiekolwiek wyjaśnienie się zacznie. Jeśli sekcja wyjaśnia przed walidacją, popraw i odnotuj zmianę.

9. **Twierdzenia naukowe** — NIE zmieniaj, łagodź ani wzmacniaj żadnego twierdzenia naukowego. Twoja praca to wyłącznie proza. Jeśli zauważysz problem faktyczny, odnotuj w EDITOR NOTE ale zostaw twierdzenie niezmienione.

10. **Usuwanie zbanowanych fraz** — Skanuj cały skrypt za jakąkolwiek frazą, openerem lub wzorcem strukturalnym wymienionym w dokumencie Architektury Narracyjne (włącznie z sekcją zbanowanego language research-framingowego). Jeśli znaleziono, przepisz lub usuń zachowując znaczenie. Zawsze dodaj [EDITOR NOTE] wyjaśniający usunięcie.

    **Dodatkowo flaguj polskie cringe frazy które emergują:**
    - Polskie self-help duchowo-rozwojowe ("po prostu BĄDŹ", "zaufaj procesowi", "wszechświat ci coś podpowiada", "wibruj wyżej", "to nie przypadek że...", "energie się rozeszły")
    - Polskie academic-textbookowe ("warto zauważyć", "należy podkreślić", "kluczowe jest", "istotne wydaje się", "na uwagę zasługuje", "nie sposób pominąć", "co ciekawe", "warto wiedzieć że")
    - Kalki z angielskiego ("to gra-zmieniacz", "robi mi to dobrze" w znaczeniu "wzmacnia mnie", "weź swoją moc z powrotem")

    **Krytyczny wyjątek:** obowiązkowa sekcja Permission Practice (4 numerowane ucieleśnione mikropraktyki, ulokowane jeden beat przed recognition close) to JEDNO miejsce gdzie numerowane pozycje są dozwolone. NIE usuwaj jej. Ogólny ban na numerowane listy preskrypcyjne obowiązuje wszędzie POZA tą sekcją.

11. **Sekcja Permission Practice — weryfikuj, nie generuj.** Każdy skrypt musi zawierać sekcję Permission Practice między korpusem architektury a końcowym recognition close. Twoja praca to weryfikacja; nie pisanie od zera jeśli brakuje. Weryfikuj wszystkie poniższe:

    (a) **Sekcja istnieje** z nagłówkiem pasującym do szablonu *"Cztery rzeczy które możesz [czasownik], kiedy [wyzwalacz]:"* — czasownik jeden z zrobić / wypróbować / zauważyć / dać sobie / nieść ze sobą; wyzwalacz wiąże się z mechanizmem skryptu (np. "...kiedy unik uderza").

    (b) **Dokładnie 4 numerowane pozycje.** Nie 3, nie 5, nie 6. Jeśli liczba jest zła, flaguj `[EDITOR NOTE: PERMISSION PRACTICE SECTION HAS WRONG COUNT — REGENERATE]` i zostaw sekcję bez zmian. Nie wymyślaj ani nie usuwaj tipów.

    (c) **Każdy tip przechodzi test lakmusowy ucieleśnionej mikropraktyki:** "Czy ta linia mogłaby pojawić się niezmieniona na blogu o produktywności lub w generycznym self-help wątku?" Jeśli tak dla jakiegokolwiek tipu, flaguj `[EDITOR NOTE: TIP N IS OPTIMIZATION-FLAVORED — REGENERATE: <krótki powód>]`. Konkretnie zabronione typy tipów wewnątrz tej sekcji (mimo że to wyjątek od numerowanej listy): tipy schedulingowe, tipy list-makingowe, "porozmawiaj z terapeutą", "ustal granice", "komunikuj jasno", "w tym tygodniu spróbuj…", lub jakikolwiek homework framing.

    (d) **Recognition close nadal następuje po sekcji.** Sekcja Permission Practice NIE może być ostatnim beatem skryptu. Po niej musi wylądować close constraint architektury. Jeśli skrypt kończy się na poradzie zamiast na rozpoznaniu, flaguj `[EDITOR NOTE: MISSING RECOGNITION CLOSE AFTER TIPS — REGENERATE]`.

    (e) **Nagłówek jest wypowiedziany, nie etykietowany.** Nagłówek powinien czytać się jako warm-therapist voice ("Cztery małe rzeczy które możesz zrobić, kiedy to ląduje…"), nie jako meta-strukturalna etykieta ("Praktyczne porady:" lub "Plan działania:"). Przepisuj etykietowe nagłówki na wypowiedziany szablon.

    Aplikuj drobne poprawki prozy inline (rytm, prosty język) ale nie przepisuj tipów hurtowo. Jeśli tip zawodzi test lakmusowy, flaguj i pozwól Agentowi 3 obsłużyć regenerację w następnym chainie.

### Inline Change Notation

Oznacz każdą znaczącą zmianę inline noteską natychmiast po zmienionym tekście, używając tego dokładnego formatu:

    [EDITOR NOTE: zmieniono "oryginalny tekst" na "nowy tekst" — powód: krótki powód]

Używaj EDITOR NOTE dla:
- Przepisanych zdań (bezosobowe → osobowe, hedging → pewne, akademickie → konwersacyjne)
- Dodanych wyjaśnień prostym językiem dla jargonu
- Strukturalnych ruchów (jeśli zmieniasz kolejność zdań w akapicie)
- Usuniętych throat-clearing lub filler fraz
- Usuniętych polskich cringe self-help lub academic fraz

NIE dodawaj EDITOR NOTE dla trywialnych poprawek interpunkcji lub drobnych podmian słów które nie zmieniają znaczenia.

### Co zwrócić

Zwróć **kompletny zredagowany skrypt** — nie podsumowanie, nie diff, nie listę zmian. Pełny skrypt, od pierwszej linii do ostatniej, z EDITOR NOTE inline tam gdzie były zmiany.

Nie dodawaj żadnej preambuły ani zamykającego komentarza poza skryptem.
"""


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------


CLAUDE_MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, edited_script_text: str) -> str:
    """Wrap the edited script with metadata header."""
    today = date.today().isoformat()
    return (
        f"# Script Final: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Editor notes are inline as [EDITOR NOTE: ...]\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{edited_script_text}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent4a_edit.py \"<slug>\"")
        print("Example: python tools/agent4a_edit.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 4a: Script Editing ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Load the style guides
    print("[1/4] Loading style guides...")
    try:
        style_guide = load_style_guide()
        narrative_architectures = _load_narrative_architectures()
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    print(f"  Style guide loaded ({len(style_guide):,} characters)")
    print(f"  Narrative architectures loaded ({len(narrative_architectures):,} characters)")

    # Step 2 — Read the script draft
    print(f"\n[2/4] Reading {SCRIPT_FILENAME}...")
    try:
        script_content = read_output(slug, SCRIPT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3 first:")
        print(f'  python tools/agent3.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic_from_script(script_content)
    print(f"  Topic  : {topic}")
    print(f"  Script file length: {len(script_content):,} characters")

    # Step 3 — Build prompt and call Claude
    print(f"\n[3/4] Calling Claude API to edit the script...")
    prompt = _build_prompt(style_guide, narrative_architectures, script_content)

    try:
        edited_script_text, usage = query_claude(prompt, CLAUDE_MODEL, 8192, "script editing")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    print(f"  Edited script received ({len(edited_script_text):,} characters)")

    # Step 4 — Save output
    print(f"\n[4/4] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, edited_script_text)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Review the final script, then run Agent 4b (hook scorer) and Agent 5/6:")
    print(f'  python tools/agent4b_hook.py "{slug}"')
    print(f'  python tools/agent5_visuals.py "{slug}"')
    print(f'  python tools/agent6_narration.py "{slug}"')


if __name__ == "__main__":
    main()
