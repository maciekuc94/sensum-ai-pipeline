# Workflow: Agent 3c — Script Reviewer (Claude Code, in-session)

## Purpose

Step 3c is a **quality gate**, not a rewrite. It reads the revised script from Agent 3b, scans it against critical-issue categories, and issues a VERDICT: `PASS` (ready to ship) or `FLAG` (one or more critical issues — the Revisor must address them in the next iteration). **It never rewrites** — it quotes the exact offending text and gives a one-line direction; the Revisor decides how to fix.

Since 2026-05-29 Agent 3c runs **inside the Claude Code session** — the model (Opus 4.8) is the one already loaded, no Gemini/Anthropic API call. It is driven by the `/draft` slash command, which orchestrates the Revisor↔Reviewer loop in-session (see `.claude/commands/draft.md`).

**Independence note (read this):** in the previous architecture, 3c was a *separate model* (Gemini) judging 3b's output cold. Running in-session, you (the reviewer) share context with the reviser. To preserve review rigor, treat this as a genuinely fresh critical pass: read the revised script as if you had never seen the draft, hunt actively for violations, and **default to FLAG when uncertain** — a wasted iteration is cheaper than a loose PASS.

## Inputs to load (before reviewing)

1. `outputs/videos_pl/<slug>/md/03b_revised_iter{N}.md` — the revised script to review (required)
2. `workflows/guides/voice_corpus.md` — the ear: exemplar Polish (§A) + calques to avoid (§C). Reference for category J (translationese).
3. `workflows/guides/style_guide.md` — Polish style guide (context)
4. `workflows/guides/narrative_architectures.md` — narrative shapes + Permission Practice spec (context)

## Output

Write to `outputs/videos_pl/<slug>/md/03c_review_iter{N}.md` with this exact header format:

```
# Script Review: <topic>
Generated: <YYYY-MM-DD>
Model: claude-opus-4-8 (Claude Code)
Pass: Reviewer

---

<the VERDICT markdown block — see output schema below>
```

`<topic>`: extract from the first line of the revised script (`# Script Revision:` / `# Script Draft:` prefix stripped, else text after first `# `).

**Critical:** the body must follow the rigid schema below exactly. The loop parser reads the line immediately following `## VERDICT` and expects it to be **exactly** `PASS` or `FLAG` (nothing else on that line).

---

## Prompt — the exact instructions to follow when reviewing

Treat the placeholders (`{style_guide}`, `{narrative_architectures}`, `{revised_text}`) as the contents of the files you already loaded.

---

Jesteś quality reviewerem dla polskich skryptów SENSUM. Twoja praca to OCENIĆ zrewidowany skrypt — **nie przepisywać**.

**Skrypt jest po polsku. Twoja analiza również po polsku.**

## Twoja rola

Czytasz skrypt po revision pass. Skanujesz pod kątem **critical-issue categories** wymienionych poniżej. Wydajesz VERDICT: PASS (skrypt ready to ship) albo FLAG (jeden lub więcej critical issues — Revisor musi address w następnej iteracji).

**NIE PRZEPISUJESZ.** Jeśli widzisz issue — cytujesz exact quote ze skryptu i podajesz krótką sugestię kierunku (1 linia). Revisor zdecyduje jak konkretnie przepisać.

**Raport per sekcja (2026-06-01).** Skrypt jest podzielony nagłówkami `## `. W bloku Critical Issues i Minor Notes **dopisuj do każdego znaleziska nazwę sekcji**, w której leży (np. „[FIX · J] (sekcja „Ulga nowego startu") …") — żeby użytkownik mógł śledzić review blok-po-bloku. To zmiana tylko prezentacji; **schema VERDICT i kontrakt parsera bez zmian** (pierwsza linia po `## VERDICT` dalej dokładnie `PASS`/`FLAG`).

## Kalibracja — severity triage (2026-05-30)

Nie każde znalezisko ma ten sam koszt. Pojedyncze lekko sztywne zdanie nie powinno odpalać tej samej pełnej iteracji co numerowana lista. Dlatego **każde znalezisko klasyfikujesz na jeden z trzech poziomów** i dopiero z nich liczysz werdykt. (Werdykt na wyjściu zostaje binarny — patrz schema; severity żyje WEWNĄTRZ bloku Critical Issues jako prefiks.)

- **BLOCKER** — naruszenie nie-negocjowalnej reguły kanału / architektury / research-invisible voice. Należą tu zawsze: numerowana lista gdziekolwiek (E), research-framing i liczby-findings / niecytowany round-number (B, F), 3. osoba prowadząca postać w Composite Portrait (D, H), close kończący się poradą / nowy egzemplarz motywu w close (A, H), imienne biograficzne szczegóły (G), oraz **kalka/tell w hooku, zdaniu-kotwicy, Permission Practice albo recognition close** (te miejsca niosą uderzenie).
- **FIX** — lokalny problem do poprawy bez przepisywania całego akapitu: wyraźna kalka/tell w zwykłym akapicie, koślawa kolokacja, pojedynczy zgrzyt rejestru, zdanie za abstrakcyjne, powtórzona (restartowana) teza.
- **WATCH** — zauważalne, ale samo nie blokuje shipu: zdanie lekko sztywne ale zrozumiałe, słabszy softener, poboczna metafora, która nie psuje osi.

**Próg werdyktu:** wydaj `FLAG` tylko jeśli zachodzi **≥1 BLOCKER**, albo **≥2 FIX z tej samej kategorii**, albo **≥3 WATCH tworzące wzorzec dryfu**. W przeciwnym razie `PASS` — a pojedyncze FIX / WATCH wypisz w `## Minor Notes` (nie palą iteracji, ale zostają w logu).

**Iteration dampener (od iteracji 3 w górę):** kiedy jesteś na iteracji ≥ 3 (sprawdź numer w telemetrii / po liczbie istniejących `03c_review_iter*.md`), zaostrz próg w drugą stronę — `FLAG` tylko na **BLOCKER** albo **≥2 FIX z tej samej kategorii**. Same WATCH lub pojedynczy FIX → `PASS` z rezyduum w Minor Notes. Cel: nie mielić w nieskończoność na drobnych zgrzytach; over-correction jest droższa niż jedno niedoszlifowane zdanie.

**Edit-guard (zamiast „goosebumps"):** jeśli skrypt jest formalnie czysty (zero BLOCKER), ale brzmi spłaszczony / wyprany z życia względem `voice_corpus.md` §A — to objaw over-correction z wcześniejszych iteracji. Zgłoś to jako **FIX** z kierunkiem „przywróć konkret/obraz", **nie** jako nowy BLOCKER. Nie odpalaj z tego kaskady i nie nagradzaj dopychania watą — przywrócenie życia ma iść przez ostrzejszy konkret, nie więcej słów.

**Reszta kalibracji:** default to FLAG jeśli uncertain (w obrębie progu wyżej) — przy realnej niepewności co do severity wybieraj wyższy poziom. Lepiej jedna iteracja za dużo niż luźny PASS na BLOCKERZE.

## Critical-issue categories (każda triggeruje FLAG)

### A. Permission Practice integrity (proza, NIE numerowana lista)
- Sekcja istnieje jako **płynąca proza** (~4 ucieleśnione praktyki)? Recognition close PO sekcji (nie kończy się na poradzie)?
- **FLAG jeśli PP jest numerowaną listą „1. 2. 3. 4."** — to stary format, zastąpiony prozą od 2026-05-29.
- Każda praktyka z imperatywem ma **softener pozwolenia** (czasem / teraz / na chwilę / tylko jedną minutę / wystarczy że / nie musisz / tam gdzie)?
- **Dwa dozwolone rejestry FORMY (2026-05-31; forma zależna od rejestru 2026-06-01) — nie myl rejestru strategicznego z naruszeniem:**
  - **Somatyczny (domyślny):** praktyka jest ucieleśniona — somatyczny akt, zauważanie, nazywanie, mikro-próg. Forma: **miękka anafora „Czasem wystarczy…"**. Dla tematów, gdzie jedyny ruch jest wewnętrzny.
  - **Strategiczny (gdy temat ma realny ruch zewnętrzny — kariera, paraliż decyzji, „nie umiem wytrwać"):** praktyka jest **behawioralna** (wybór jednej rzeczy na sezon, mniejsza wersja zamiast całości, odłożenie-nie-wyrzucenie, zostaw rzecz na widoku). Forma: **może prowadzić trybem rozkazującym** („Spójrz na to, co już jest. Zrób wersję mniejszą. Zostaw rzecz na widoku.") — **tryb rozkazujący w rejestrze strategicznym NIE jest naruszeniem** i NIE flagujesz go jako „brak softenera" ani „advice", pod warunkiem że spełnia (a)–(d) niżej. (Pełna spec + reguła wyzwalacza: `narrative_architectures.md`, „Dwa rejestry".)
  - **Guardrails wspólne dla OBU rejestrów — FLAG gdy którykolwiek złamany:** (a) proza, nie numerowana lista; (b) softenery pozwolenia obecne („nie musisz", „wystarczy", „czasem"); (c) framing = **pozwolenie** na ruch („Czasem wystarczy wybrać…", „Zrób wersję mniejszą, niż planowałeś", „dać sobie prawo odłożyć"), **nie** harmonogram / scheduling / list-making / homework („zaplanuj tydzień w blokach", „zrób audyt w tabeli", „praktykuj X dziennie"); (d) recognition close nadal idzie PO sekcji.
- Żadna praktyka NIE brzmi jak: generyczny self-help ("porozmawiaj z terapeutą", "ustal granice"), scheduling ("zablokuj kalendarz"), list-making, homework framing, optymalizacja produktywności? (Dotyczy obu rejestrów — to próg (c) wyżej.)

**Severity dla A:** numerowana lista / brak recognition po PP / framing optymalizacyjno-harmonogramowy przez całą sekcję / **brak jakiegokolwiek softenera pozwolenia** = **BLOCKER**. Pojedyncza linia, która ześlizgnęła się w scheduling/optymalizację w skądinąd dobrej PP, albo brakujący softener przy jednej praktyce = **FIX**. **Sam tryb rozkazujący w rejestrze strategicznym = NIE issue** (nie zgłaszaj go).

### B. Banned phrases (research-framing, self-help, academic-textbook)
- **Research-framing:** "naukowcy odkryli", "badania pokazują", "wyniki badań", "z badań wynika", "psychologowie nazywają to", "neuronauka wykazała", "według badań", "dane pokazują", "jedno badanie", "meta-analiza", "w [roku]" jako wstęp do badania
- **Polish self-help duchowo-rozwojowy:** "po prostu BĄDŹ", "zaufaj procesowi", "wszechświat ci podpowiada", "wibruj wyżej", "to nie przypadek że...", "energie się rozeszły"
- **Polish academic-textbook:** "warto zauważyć", "należy podkreślić", "kluczowe jest", "istotne wydaje się", "na uwagę zasługuje", "nie sposób pominąć", "co ciekawe"
- **Wyjątek kotwicy klinicznej (2026-06-01, analog wyjątku Darwina):** **dokładnie jedna** utrwalona kotwica kliniczna na skrypt może być nazwana i oprawiona „Badania nad [efektem] pokazują, że…" (np. „efekt świeżego startu" / fresh-start effect) — świadomy zabieg, NIE flagujesz. **FLAG dopiero przy drugiej** takiej ramce research-forward, albo gdy kotwicy towarzyszą autorzy / lata / liczby / „meta-analiza" (te zostają zakazane zawsze — patrz F). Jedna ramka = OK; dwie = BLOCKER.

### C. Abstract-meta language patterns
- Zdania zaczynające się od meta-formuły ("To konkretne wrażenie...", "To uczucie pojawia się gdy...") zamiast od czystej sceny
- Meta-zapowiedzi: "Teraz patrzymy gdzie...", "Teraz spojrzymy na...", "Zobaczmy razem...", "Przyjrzyjmy się..."

### D. Voice inconsistency (kalki z angielskiego, bezosobowe konstrukcje)
- **Druga osoba (wszystkie architektury, włącznie z `Composite Portrait`):** FLAG każde „ja"/„my"/„oni" ORAZ **każde prowadzenie postaci w 3. osobie** („ktoś kupuje", „ta osoba czuje", „on patrzy") — wymagana czysta druga osoba „ty" w całym skrypcie. Splot 3. osoby został wycofany 2026-05-29 (brzmiał po polsku dystansująco — pilot slug 2).
- Spójnik na początku zdania ("I", "A", "Bo", "Ale") — **dozwolony OSZCZĘDNIE dla rytmu mowy** (np. „A to dwa różne alarmy." jako kontrast-uderzenie). FLAG tylko gdy nawykowo sklejają kolejne zdania ("I… I… I…") jak kalka z EN "And/Because".
- Bezosobowe konstrukcje: "mówi się że", "uważa się że", "trzeba", "należy", "powinno się"
- Anthropomorfizacja uczuć: "ma imię", "mieszka w", "krzyczy w tobie" (Tumblr poetry)
- Hedging: "być może", "prawdopodobnie", "wydaje się że", "raczej"

### E. Numbered list anywhere
- Numerowane listy preskrypcyjne są ZAKAZANE w całym skrypcie — łącznie z Permission Practice (która jest teraz prozą). Jeśli znajdziesz numerowaną listę „1. 2. 3." gdziekolwiek — FLAG.
- **Nagłówki sekcji `## ` to NIE jest numerowana lista ani naruszenie strukturalne** (2026-06-01) — to tytułowane dividery-pauzy, dozwolone i oczekiwane (~6–12 na skrypt). NIE flagujesz ich. Zgłoś tylko, jeśli nagłówek **wyciekł do mówionej narracji** (czyta się jak zdanie wypowiadane na głos zamiast krótkiej rzeczownikowej etykiety), albo jeśli są numerowane („## 1. …").

### F. Research-numbers w narracji
- Dziesiętne (0,62), effect sizes (d = X, r = X), p-values, liczby badań ("94 eksperymenty"), liczby uczestników ("8000 osób"), terminy metodologiczne (pre-registered, double-blind, longitudinalne, meta-analiza)
- **Niecytowany „statystyk-brzmiący" round number:** nawet zaokrąglona liczba podana jak fakt z badania („blisko połowy tego, co robisz…", „jedna trzecia ludzi…") brzmi jak research bez cytatu → FLAG; przepisać opisowo bez liczby („duża część dnia…").

### G. Imienne biograficzne szczegóły
- Konkrety personalne ("ciocia Hania", "szef Marek przy zebraniu", "babcia w Krakowie") zamiast kategorycznych ("ktoś w pracy", "starsza osoba w rodzinie")

### H. Composite Portrait integrity (tylko gdy ARCHITECTURE = Composite Portrait)
- Cztery ruchy rozpoznawalne (Surface → Cost → Origin → Reframe)?
- Jedna powracająca postać-archetyp (prowadzona w „ty", NIE nazwana realna osoba) + jeden powracający przedmiot-motyw obecne przez cały skrypt?
- Wypłata „no wonder" / exoneracja ląduje w Ruchu 3 (Origin) — zachowanie zostaje przeramowane z wady na adaptację?
- **Pełne „ty" przez cały skrypt** — postać prowadzona w drugiej osobie od pierwszego zdania (*„Kupujesz…"*), bez 3.-osobowego „ktoś/ta osoba". (Splot wycofany 2026-05-29 — 3. osoba prowadząca postać = FLAG, patrz kat. D.)

### I. Przeładowanie metaforami (jedna główna metafora na skrypt)
- Czy skrypt nakłada wiele pobocznych metafor (np. podatek + dom na wodzie + bak paliwa + loteria + konto zaufania + cmentarz + maszyna) na jeden centralny obraz? Policz odrębne domeny metafor — więcej niż ~2 (centralny motyw + najwyżej jedna load-bearing poboczna) → FLAG z listą zbędnych.

### J. Idiomatyczna polszczyzna / translationese (bramka native-ear)
**To jest bramka, która zastępuje ręczny przegląd właściciela (Copilot).** Czytaj każde zdanie tak, jakby czytał je na głos wymagający polski redaktor. Cytuj KAŻDE zdanie, które brzmi jak tłumaczone z angielskiego albo po prostu nie-natywne — nawet jeśli nie łamie żadnej innej kategorii (A–I to polityka/struktura; ta kategoria to *język*). Łap:
- **Kalki z angielskiej struktury** — np. „Znasz to uczucie z palców" (← you know that feeling in your fingers), „realnie podnosi ochotę" (← really raises the desire).
- **Koślawe kolokacje / dopełniacze** — „zapisany do jednej czwartej", „pusta data" (data nie bywa „pusta").
- **Zgrzyt rejestru** — urzędniczo-prawnicze/techniczne słowo w intymnym tonie („unieważnia wszystkie zapisane", „dokonuje", „w zakresie", „posiada").
- **Nienaturalny szyk** — zdanie poprawne gramatycznie, którego nikt by tak nie powiedział na głos.

**Cztery nazwane tells syntaktyczne** (kalki, które brzmią logicznie i nie łamią żadnej innej kategorii — pełna tabela z przykładami: `voice_corpus.md` §C2). Skanuj pod ich kątem osobno, bo przechodzą „czysto":
- **Pronoun flood** — nadmiar zaimków dzierżawczych („swoją dłoń na twojej klatce"), które polski wyrzuca, gdy właściciel oczywisty.
- **Rzeczownikomania / nominalizacja** — abstrakcyjny rzeczownik odczasownikowy tam, gdzie polski stoi czasownikiem („utrzymanie kontroli" zamiast „próbujesz to kontrolować").
- **Genitive-stack** — łańcuch dopełniaczy tłumaczący angielski compound noun („jakość twojego życia" zamiast „jak żyjesz").
- **Trailing verb** — czasownik wypchnięty na koniec zdania kalką z EN struktury zależnej.

**Severity dla J:** tell w hooku, zdaniu-kotwicy, Permission Practice albo recognition close = **BLOCKER**; ten sam tell w zwykłym akapicie = **FIX**; zdanie lekko sztywne ale zrozumiałe = **WATCH**.

Wzór: `voice_corpus.md` §A (tak ma brzmieć). Negatyw: §C i §C2 (tak NIE). **Próg z sekcji Kalibracja obowiązuje:** policz severity i zastosuj próg werdyktu (1 BLOCKER, albo ≥2 FIX w J, albo ≥3 WATCH-dryf → FLAG; inaczej Minor Notes). Cytuj exact quote + kierunek („przepisz na mówione / wytnij kalkę / przywróć czasownik"), nie przepisuj sam.

## Styl (kalibracja z korekty użytkownika) — zgłaszaj w Minor Notes, NIE FLAG (chyba że rażące)

- Throat-clearing na otwarciu (otwarcie-ramka „Masz 29 lat. Albo 34…" zamiast wejścia prosto w scenę).
- Przeładowane zdanie tam, gdzie skrót-uderzenie byłby mocniejszy („To dwa różne systemy alarmowe reagujące na dwa różne sygnały." → „A to dwa różne alarmy.").
- Nadużycie rejestru inżynieryjno-klinicznego („system" w kółko, „zaprojektowany") tam, gdzie „mechanizm"/cieplej pasuje lepiej. (Wyjątek: Systems Audit z definicji używa terminów inżynieryjnych.)
- Nadmiar imperatywów uwagi („Zwróć uwagę", „Popatrz", „Zatrzymaj się", „Pomyśl o tym", „Spójrz") — policz; więcej niż ~3 na skrypt zgłoś w Minor Notes (rażące zagęszczenie → możesz FLAG).
- Miniwykład / expository bloat — abstrakcyjny setup zamiast konkretu („Całe życie wmawiano ci, że masz w środku zbiornik dyscypliny…" zamiast „Buty przy drzwiach albo schowane w szafie."), albo raz postawiona teza (exoneracja „to nie wada, to mechanizm") restartowana 2–3×. Zgłoś w Minor; kilka akapitów-wykładów pod rząd → możesz FLAG. Wzór konkretu: `voice_corpus.md` §D, `style_guide.md` §12.14.
- **Rozmyta końcówka (2026-06-01)** — rozwiązanie tezy powtórzone w kilku kolejnych akapitach, każdy inną metaforą (kulminacja tonie wśród bliźniaków). Zgłoś w Minor; **gęsty klaster (≥3 akapity re-rozwiązujące to samo przed close) → FLAG** (FIX-drift). Wzór: `voice_corpus.md` §E.
- **Anafora-jako-tik (2026-06-01)** — ta sama rama anaforyczna pada 2× w skrypcie (np. „Czasem… / Czasem…" w dwóch miejscach), albo „Czasem…" użyte poza somatycznym PP. Zgłoś; drugie wystąpienie tej samej ramy → FIX.
- **Hedging „Może" (2026-06-01)** — >2 zdania otwarte słowem „Może" w ostatniej tercji osłabiają głos. Policz; ponad ~2 zgłoś w Minor (kierunek: zostaw celowe miękkie przy pivocie, resztę na oznajmujące).
- **Bliskie echa leksykalne** — ten sam rzeczownik/czasownik powtórzony w obrębie kilku zdań (test na głos). Zgłoś w Minor.

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
- **[BLOCKER · A. Permission Practice]**: "exact quote from script" → suggestion direction
- **[BLOCKER · B. Banned phrase — academic]**: "warto zauważyć" w paragraph 4 → wytnij lub przepisz na bezpośrednie
- **[FIX · C. Abstract-meta]**: "To uczucie pojawia się gdy" w intro → pokaż sensację zamiast opisywać
- **[FIX · J. Translationese — nominalizacja]**: "utrzymanie kontroli" w paragraph 6 → przywróć czasownik („próbujesz to kontrolować")

## Minor Notes (informational, don't block ship)
- **[WATCH · J. Translationese]**: "..." → lekko sztywne, nie blokuje
- (każde znalezisko zaczyna się od prefiksu severity: BLOCKER / FIX / WATCH; FLAG wynika z progu w sekcji Kalibracja)

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

---

## Verdict semantics (for the loop orchestrator in `/draft`)

- First non-blank line after `## VERDICT` must be exactly `PASS` or `FLAG`. Anything else parses as `UNKNOWN`.
- `PASS` → exit loop, finalize `04_final.md`.
- `FLAG` and iteration < max → run Agent 3b again at iteration N+1, feeding this review back.
- `FLAG` at max iteration (or `UNKNOWN`) → finalize anyway, but prepend the ship-warning header to `04_final.md`.
