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
1500–2200 słowach). Utwórz folder `outputs/videos_pl/$1/md/iter/` — a jeśli już
istnieje (ponowny przebieg na tym samym slugu), **najpierw go wyczyść** (Bash:
`rm -f outputs/videos_pl/$1/md/iter/*.md`) — stare `sek_NN.md` z poprzedniego
draftu zatrułyby scalanie. Ten draft jest od teraz **zamrożony** — żaden checker
go nie zmienia.

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

**`04_final_machine.md` jest NIETYKALNY poza `/draft`** — nigdy go nie nadpisuj
ani nie edytuj ręcznie (także przy migracjach nazewnictwa). Świeży, pełny
przebieg `/draft` tworzy świeży snapshot — to jedyna dozwolona droga zmiany. To
podstawa pomiaru sufitu maszyny (diff vs `script_corrected`).

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
