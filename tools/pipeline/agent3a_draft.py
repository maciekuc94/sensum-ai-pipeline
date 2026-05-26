"""
Agent 3a: Script Draft (Pass 1 of 3)
Reads the verified research document produced by Agent 2 and writes a complete
~1,850-word narration script using one of the four narrative architectures,
followed by a mandatory Permission Practice closing section and recognition close.

Review outputs/[slug]/md/03a_draft.md before running Agent 3b.

Usage:
    python tools/agent3a_draft.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, load_style_guide, query_gemini_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESEARCH_FILENAME = "md/02_verified_research.md"
MATERIALS_FILENAME = "md/00_materials_insights.md"
OUTPUT_FILENAME = "md/03a_draft.md"

GEMINI_MODEL = "gemini-3.1-pro-preview"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_narrative_architectures() -> str:
    return load_style_guide("narrative_architectures.md")


def _extract_topic_from_research(research_content: str) -> str:
    for line in research_content.splitlines():
        line = line.strip()
        if line.startswith("# Verified Research:"):
            return line[len("# Verified Research:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _load_materials_insights(slug: str) -> str | None:
    try:
        return read_output(slug, MATERIALS_FILENAME)
    except FileNotFoundError:
        return None


def _build_prompt(
    style_guide: str,
    narrative_architectures: str,
    research_content: str,
    materials_insights: str | None = None,
) -> str:
    materials_section = ""
    if materials_insights:
        materials_section = f"\n## Insighty z książki (zaufane źródło — nie weryfikuj)\n{materials_insights}\n"

    return f"""\
Jesteś polskim scenarzystą skryptów psychologicznych dla kanału SENSUM.

**WAŻNE: Cały skrypt piszesz po polsku. Research poniżej jest po angielsku — to zaufane źródło treści, ale Twój output musi być w naturalnym polskim, nie tłumaczeniem słowo-po-słowie.**

## Voice anchors (kluczowe dla autentyczności polskiej)

Piszesz w polskiej tradycji **reportażu psychologicznego** (Hugo-Bader, Tochman — zawsze konkretny obraz, nigdy pretensjonalna metafora) skrzyżowanego z **polską intymnością terapeutyczną** (Wojciech Eichelberger w nocnym radiu, Bogdan de Barbaro — ciepło bez wellness-blogu i bez akademickiej dystansy).

Voice: jak ktoś kto myśli i mówi po polsku siedząc obok widza, nie jak ktoś tłumaczący angielską strukturę zdania na polski.

**Forma gramatyczna:** używaj formy **męskiej jako neutralnej** (kanał dla obu płci — standard polskich mediów). Czas teraźniejszy jest bezpłciowy i preferowany; unikaj czasu przeszłego tam gdzie teraźniejszy wystarczy. Kiedy czas przeszły jest niezbędny — forma męska: "piłeś", "mogłeś", "kupiłeś".

**Sześć żelaznych zasad polskiej autentyczności:**

1. **Konkretny obraz zamiast literackiej ozdoby.** "Trzysta zdjęć z wakacji w twoim feedzie. I twoje wieczory na kanapie." NIE "Trzysta cudzych szczytów przeciwko twojej pełnej topografii".

2. **Najprostsze słowo zamiast eleganckiego synonimu.** "Czujesz to w klatce" NIE "Odczuwasz wewnątrz siebie tę dotkliwą obecność". "Boli" NIE "manifestuje się dotkliwie".

3. **Zdanie z podmiotem zamiast efektownego fragmentu.** Polski lubi fragmenty dla emfazy, ale zaczynanie zdań od spójników ("I", "Bo", "A") to natychmiastowy znak tłumaczenia. Polska redakcja tego nie robi.

4. **Polskie konkrety kulturowe gdzie pasują — ale uniwersalne, nie biograficzne.** Kanapa, balkon, papierosy, smartfon w łóżku o pierwszej w nocy, "komentarze słyszane od lat — przy rodzinnym stole, w samochodzie, w szkole, w internecie". Polskie scenografie zamiast neutralnych. **Unikaj imiennych biograficznych szczegółów** ("ciocia przy wigilii", "szef Marek", "babcia w Krakowie") — widz myśli "to nie ja, to ktoś inny". Konkret kategoryczny (typ sytuacji którą każdy zna) > konkret biograficzny (jedna osoba, jedno wydarzenie).

5. **Embodied clarity — pokaż sensację, nie opisuj wrażenia.** ❌ "To konkretne wrażenie w klatce piersiowej" → ✓ "Coś w klatce piersiowej". Pozwól widzowi na inferencję; nie meta-wyjaśniaj co czuje. Unikaj zdań zaczynających się od meta-formuły ("To...", "To jest...", "To wrażenie...") gdy możesz pokazać scenę bezpośrednio.

6. **Symboliczna metafora wygrywa nad numerowaną listą.** ❌ "do 30 mieszkanie, do 35 ślub, do 40 dzieci" → ✓ "wyobrażona tarcza z terminami, które rzekomo powinieneś już odhaczyć". Jeśli używasz **listy konkretów** tam gdzie **jedna metafora** mogłaby to zamknąć w obrazie — zwiń do metafory.

**Lista cringe-wzorców których MUSISZ unikać** (z polskiego pisania, zidentyfikowanych empirycznie):

- Zdania zaczynające się od `I`, `Bo`, `A`, `Ale`, `Bowiem` (kalka z EN "And/Because")
- Anthropomorfizacja uczuć: "ma imię", "mieszka w", "krzyczy w tobie" (Tumblr poetry)
- Kalki rzeczownik+rzeczownik: "wadą charakteru" (← character flaw), "twoim charakterem", "siła woli" (← willpower), "jakość życia" (← quality of life)
- Mieszanie kategorii semantycznych w listach uderzających ("Wyżej. Niżej. Bezpiecznie. Niebezpiecznie." — pierwsze dwa to hierarchia, drugie dwa to stan)
- Pretensjonalne metafory mieszające domeny ("szczyty topografii", "ocean myśli", "labirynt serca")
- Literackie ozdobniki: "odczuwa", "doświadcza", "manifestuje się", "uobecnia się", "konstytuuje" (zamień na: czuje, ma, jest, dzieje się)
- Polski self-help duchowo-rozwojowy: "po prostu BĄDŹ", "zaufaj procesowi", "wszechświat ci podpowiada", "wibruj wyżej", "to nie przypadek że...", "energie się rozeszły"
- Polski academic-textbookowy: "warto zauważyć", "należy podkreślić", "kluczowe jest", "istotne wydaje się", "na uwagę zasługuje", "co ciekawe"
- Meta-zapowiedzi: "Teraz patrzymy gdzie...", "Teraz spojrzmy na...", "Zobaczmy razem...", "Przyjrzyjmy się..." — skrypt nie zapowiada co zrobi, po prostu to robi. Zamiast zapowiedzi — zdanie otwierające treść wprost.

Pełna specyfikacja banowanych wzorców strukturalnych w `narrative_architectures.md` sekcja "Zbanowane wzorce strukturalne".

**Test lakmusowy dla każdego akapitu:** Czy ten akapit mogłaby napisać Polka myśląca po polsku siedząc nad kawą, czy brzmi jak ktoś tłumaczący angielski tekst? Jeśli jakikolwiek wzorzec z listy się pojawia — przepisz.

## Style Guide (przestrzegaj dokładnie)
{style_guide}

## Architektury Narracyjne (przestrzegaj dokładnie)
{narrative_architectures}

## Zweryfikowane Badania (Twoje źródło treści — po angielsku, output piszesz po polsku)
{research_content}
{materials_section}
## Twoje zadanie
Napisz kompletny skrypt narracji wideo na temat omawiany w Zweryfikowanych Badaniach powyżej. Skrypt w całości po polsku.

Wymagania:
- Docelowa długość: ~1,850 słów (około 14 minut przy 130 wpm) — wzrost z poprzedniego ~1,700 absorbuje obowiązkową sekcję Permission Practice opisaną niżej. Uwaga: polski jest "gęstszy" niż angielski (mniej słów na tę samą treść), więc celuj raczej w 1,600–1,750 słów polskich = ~14 min narracji.
- Przeczytaj dokument Architektury Narracyjne powyżej. Wybierz pojedynczą architekturę najlepiej pasującą do tego tematu i badania. Zadeklaruj swój wybór na PIERWSZEJ LINII skryptu:
  ARCHITECTURE: [Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit]
  (Nazwy architektur pozostają po angielsku jako wewnętrzne identyfikatory — używane przez agenty downstream.)
  Potem napisz skrypt zgodnie z punktem wejścia tej architektury, wymaganymi węzłami treściowymi i ograniczeniem close. Traktuj architekturę jako kształt, nie sztywny szablon.
- Unikaj wszystkich zbanowanych fraz i wzorców strukturalnych wymienionych w dokumencie Architektury Narracyjne (lista konkretnych fraz jest na razie pusta — przestrzegaj zasad wysokopoziomowych: research niewidoczny, bez hedgingu, bez bezosobowych konstrukcji, bez polskiego duchowo-rozwojowego ani academic-textbookowego rejestru).
- Używaj [Visual Pause] w osobnej linii (maksymalnie 3–4 razy na skrypt) w momentach wymagających ciszy dla impaktu.

**Obowiązkowa sekcja Permission Practice (zamykająca).** Każdy skrypt — niezależnie od architektury — musi zawierać sekcję Permission Practice PO korpusie architektury i PRZED końcowym recognition close. To zablokowana reguła strukturalna kanału.

- Szablon nagłówka: *"Cztery rzeczy które możesz [czasownik], kiedy [wyzwalacz powiązany z konkretnym mechanizmem skryptu]:"*
  - czasownik varies: zrobić / wypróbować / zauważyć / dać sobie / nieść ze sobą
  - **Domyślnie wybieraj aktywne czasowniki:** *zrobić / wypróbować*. Pasywne *zauważyć* używaj TYLKO gdy mechanizm skryptu jest naprawdę o zauważaniu (np. skrypt o introspekcji). W innych przypadkach *zauważyć* osłabia sekcję — widz dostaje agency, nie observership.
  - wyzwalacz wiąże się ze zjawiskiem skryptu — np. *"...kiedy unik uderza"*, *"...kiedy to ląduje w ciele"*, *"...kiedy wstyd się zaczyna"*, *"...kiedy pętla się włącza"*
- Dokładnie **4 numerowane pozycje**. Nie 3. Nie 5. Zawsze 4.
- Każda pozycja = jedna linia deklaratywna + jedna krótka linia unpack. Mniej więcej 15–35 słów na pozycję.
- Voice = **ucieleśniona mikropraktyka**: akty somatyczne (oddychanie, umieszczenie dłoni, postawa), zauważanie (lokalizowanie wrażenia w ciele), nazywanie (wypowiedzenie jednego słowa na głos), mikro-progi (napisz pierwsze zdanie, potem przestań). Tipy są *praktykami*, nie *radami*.
- **Softening pressure — każdy tip z imperatywem ma temporalny softener.** Słowa softenery: *teraz / na chwilę / tylko jedną minutę / wystarczy że / nie musisz / tam gdzie*. Przykłady: ❌ "Twoje ciało nie potrzebuje, żebyś rozwiązał problem" → ✓ "Twoje ciało nie potrzebuje, żebyś **teraz** rozwiązał problem". ❌ "Połóż dłoń na klatce piersiowej" → ✓ "Połóż dłoń na klatce piersiowej, **tam gdzie czujesz ciężar**". Bez softenerów tipy brzmią jak prescripcja, nie pozwolenie.
- **Zabronione typy tipów** (psują kanał):
  - Tipy schedulingowe ("ustal czas", "zablokuj kalendarz")
  - Tipy list-makingowe ("zapisz 3 rzeczy…")
  - Tipy optymalizacyjne ("bądź bardziej produktywny", "przestań overthinkować")
  - Generyczne tipy self-helpowe ("porozmawiaj z terapeutą", "ustal granice", "komunikuj jasno")
  - Homework framing ("w tym tygodniu spróbuj…", "twoje zadanie to…")
  - Cokolwiek co mogłoby pojawić się niezmienione na blogu o produktywności
- **Test lakmusowy dla każdego tipu:** Czy ta linia mogłaby pojawić się słowo-w-słowo na blogu o produktywności lub w generycznym wątku self-help? Jeśli tak — źle. Przepisz jako somatyczny, zauważający lub mikro-progowy akt.
- Wszystkie istniejące voice rules nadal obowiązują wewnątrz tej sekcji: bez nazwisk badaczy, bez "badania pokazują", bez dziesiętnych, tylko zaokrąglone liczby, najpierw prosty język.

**Potem napisz recognition close po tej sekcji.** Tipy są beatem, nie destynacją. OSTATNIA linia skryptu musi nadal lądować na implikacji / rozpoznaniu — nigdy na poradzie i nigdy na instrukcji "idź zrób to". Ograniczenie close architektury nadal rządzi recognition beatem; sekcja Permission Practice siedzi jeden beat przed nim.

**Voice — ciepły terapeuta rozmawiający z jedną osobą.** Siedzisz naprzeciwko widza. Walidujesz uczucie zanim wyjaśnisz mechanizm. Nie performujesz eksperckości; oferujesz rozpoznanie.

**Research jest niewidoczny.** Czytasz badania; skrypt nigdy ich nie cytuje. ŻADNEGO language research-framingowego w jakiejkolwiek formie — bez "naukowcy odkryli", bez "badania pokazują", bez "wyniki badań", bez "neuronauka wykazała", bez "jedno badanie", bez "meta-analiza", bez "z badań wynika", bez "dane pokazują", bez "nauka jest jasna", bez "psychologowie nazywają to", bez "w [roku]" wprowadzającego badanie. Odkrycia pojawiają się jako obserwacje o byciu człowiekiem, wypowiedziane głosem mówcy. Widz ufa mówcy, nie cytatowi. Prawdziwe cytaty bibliograficzne żyją w opisie YouTube (Agent 8), nigdy tutaj.

**Najpierw prosty język.** Opisuj zjawisko codziennymi słowami. Nazwij termin naukowy tylko jeśli (a) sama nazwa jest naprawdę zapamiętywalna i (b) pojawia się raz, późno, po tym jak idea już wylądowała w prostych słowach. Domyślnie: bez nazwy. NIGDY nie używaj wzorca jargon-then-translation ("dysregulacja emocjonalna — czyli rozregulowanie emocji…") — to brzmi jak wykład.

**Bez liczb jako findings.** Bez dziesiętnych, bez effect sizes (d = X, r = X), bez p-values, bez liczb badań ("94 eksperymenty"), bez liczb uczestników ("8000 osób"), bez terminów metodologicznych (pre-registered, double-blind, longitudinalne, meta-analiza). Tylko zaokrąglone, opisowe liczby ("około połowa", "większość ludzi", "w wielu przypadkach"). Jeśli liczba nie ląduje emocjonalnie w prostym polskim — wytnij ją.

**Pewny głos mówcy.** Zamień hedging ("być może", "prawdopodobnie", "wydaje się że") na bezpośrednie twierdzenia wypowiadane przez mówcę — nie cytując badań. "Twój mózg robi X" wygrywa nad "Z badań wynika że twój mózg robi X".

**Polski idiom — nie tłumacz z angielskiego.** Pisz polski jak Polak który myśli po polsku, nie jak ktoś kto tłumaczy angielską strukturę zdania. Unikaj kalk: "to gra-zmieniacz" → "to zmienia wszystko"; "robi mi to dobrze" → "to mnie wzmacnia / leczy / uspokaja"; "weź swoją moc z powrotem" → unikaj w ogóle, brzmi jak Instagram coach.

- Używaj metafor i analogii — jedna mocna metafora na koncept naukowy
- TYLKO używaj twierdzeń z sekcji Verified Claims w badaniach (NIE z flagged ani removed claims)
- Pisz w drugiej osobie ("ty", "twój/twoja", "ci") konsekwentnie
- Krótkie uderzające zdania. Fragmenty dla emfazy. Polski lubi dłuższe zdania podrzędne — równoważ kontrastem.
- NIE dołączaj żadnych markerów [IMAGE: ...] — dedykowany agent wizualny (Agent 5) obsługuje image prompts oddzielnie.
"""


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, script_text: str) -> str:
    today = date.today().isoformat()
    return (
        f"# Script Draft: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {GEMINI_MODEL}\n"
        f"Pass: 1 of 3 (Draft)\n"
        f"Estimated duration: ~14 min (~1,850 words)\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{script_text}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent3a_draft.py \"<slug>\"")
        print("Example: python tools/agent3a_draft.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 3a: Script Draft (Pass 1/3) ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Load style guides
    print("[1/4] Loading style guides...")
    try:
        style_guide = load_style_guide()
        narrative_architectures = _load_narrative_architectures()
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    print(f"  Style guide loaded ({len(style_guide):,} characters)")
    print(f"  Narrative architectures loaded ({len(narrative_architectures):,} characters)")

    # Step 2 — Read verified research
    print(f"\n[2/4] Reading {RESEARCH_FILENAME}...")
    try:
        research_content = read_output(slug, RESEARCH_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 2 first:")
        print(f'  python tools/agent2_verify.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic_from_research(research_content)
    print(f"  Topic  : {topic}")
    print(f"  Research file length: {len(research_content):,} characters")

    # Step 2b — Load book insights if available
    materials_insights = _load_materials_insights(slug)
    if materials_insights:
        print(f"  Book insights loaded ({len(materials_insights):,} characters)")
    else:
        print(f"  No book insights found (run Agent 0 to add a reference book)")

    # Step 3 — Call Gemini
    print(f"\n[3/4] Calling Gemini API to write the draft...")
    prompt = _build_prompt(style_guide, narrative_architectures, research_content, materials_insights)

    try:
        script_text, usage = query_gemini_text(prompt, GEMINI_MODEL, 8192, "script draft")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Gemini API call failed — {exc}")
        sys.exit(1)

    print(f"  Draft received ({len(script_text):,} characters)")

    # Extract declared architecture for display
    for line in script_text.splitlines():
        if line.strip().upper().startswith("ARCHITECTURE:"):
            print(f"  {line.strip()}")
            break

    # Step 4 — Save output
    print(f"\n[4/4] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, script_text)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Review the draft, then run Agent 3b (revisor) or full chain:")
    print(f'  python tools/pipeline/agent3b_revisor.py "{slug}"')
    print(f'  python tools/pipeline/agent3.py "{slug}" --skip-drafter')


if __name__ == "__main__":
    main()
