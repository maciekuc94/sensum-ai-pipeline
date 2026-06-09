---
description: Łańcuch skryptu SENSUM (2026-06-07, Gen 4) — pisarz → ensemble (section-checker na każde ## + 1 arc-checker, równolegle, na zamrożonym oryginale) → fixer → ściskacz (zimny pass, tylko cięcie przegadania). Jeden przebieg, bez pętli, in-session, no API. Finalną redakcję robisz na docx.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob, Agent
---

# /draft — pisarz → section+arc checkery (ensemble) → fixer → ściskacz

Zimne konteksty Opus, każdy ślepy na pozostałe; Ty (lead) tylko przekazujesz pliki
i kolejność. Jeden przebieg:
- **pisarz** pisze cały skrypt luźno,
- na **zamrożonym** drafcie rusza **ensemble checkerów równolegle**: jeden
  **section-checker na każde `## `** (zdania `[Z]` + kontekst `[K]` w obrębie
  sekcji) **plus jeden arc-checker** (spójność całości `[A]` — metafora, klamra,
  narastanie, przejścia),
- **fixer** scala ich zgłoszenia i wstawia poprawki chirurgicznie — najpierw
  struktura (`[A]`/`[K]`), potem zdania (`[Z]`),
- **ściskacz** (zimny pass, **tylko cięcie**) usuwa 6 trybów przegadania
  (zapowiadanie ruchu, powtórzenia, watę, antytezy-rusztowania, serie spójników,
  „badania pokazują") — nigdy nic nie dopisuje (cut-only = zero thrashu).

**Dlaczego ensemble na zamrożonym oryginale, nie pętla.** Iterowanie
checker→fixer→checker na **zmieniającej się** kopii **dryfuje** — własna poprawka
fixera staje się następnym zgłoszeniem checkera i tekst pływa bez zbieżności. Tu
każdy checker czyta **ten sam, zamrożony `03a_draft.md`** i nigdy nie widzi cudzych
poprawek → poprawka nie może stać się nowym błędem. Różne zimne odczyty łapią różne
podzbiory zgrzytów; bierzemy ich **sumę**, nie sekwencję.

**Dlaczego osobno sekcja i łuk.** Section-checker zamknięty w jednej sekcji nie
zobaczy, że metafora pęka między sekcjami albo że zamknięcie nie spłaca otwarcia —
to widać tylko z lotu ptaka. Arc-checker robi dokładnie to i **nie** dubluje zdań.

Kanon głosu: `workflows/guides/voice_brief.md` (v2). Prompty (single source of
truth): `03a_writer.md`, `03b_section_checker.md`, `03b_arc_checker.md`,
`03c_fixer.md`, `03d_compressor.md`. **Każdy subagent czyta swój prompt sam** — Ty go nie streszczasz.

`$1` = slug pod `outputs/videos_pl/`.

---

## Step 1 — Walidacja
Potwierdź, że istnieje `outputs/videos_pl/$1/md/02_verified_research.md`. Brak →
powiedz userowi, żeby najpierw uruchomił
`PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "$1"`, i zatrzymaj się.

## Step 2 — Pisarz (zimny subagent Opus)
Zespawnuj subagenta (`Agent`, `subagent_type: general-purpose`, `model: opus`) z
briefem dokładnie tej treści:

> Jesteś pisarzem SENSUM, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03a_writer.md` i wykonaj go dokładnie. Badania (tło, po
> angielsku): `outputs/videos_pl/$1/md/02_verified_research.md` — przeczytaj je.
> Temat wynika z badań (slug: `$1`). Zapisz gotową narrację do
> `outputs/videos_pl/$1/md/03a_draft.md` (markdown, sekcje `## `, żadnych
> metadanych). Twój zwrot = treść pliku.

Poczekaj na ukończenie.

## Step 3 — Spis sekcji (Ty, in-session)
Wczytaj `outputs/videos_pl/$1/md/03a_draft.md`. Wypisz **w kolejności** wszystkie
nagłówki `## ` — to lista rewirów dla section-checkerów (zwykle 6–8). Utwórz folder
`outputs/videos_pl/$1/md/iter/`. Ten draft jest od teraz **zamrożony** — żaden
checker go nie zmienia.

## Step 4 — Ensemble checkerów (RÓWNOLEGLE — wszystkie spawny w JEDNEJ wiadomości)
Wyślij **wszystkie** poniższe spawny w **jednej** wiadomości (równoległość). Każdy
to świeży zimny subagent (`general-purpose`, `model: opus`).

**a) Po jednym section-checkerze na każdy nagłówek z kroku 3.** Dla sekcji o
indeksie `NN` (`01`, `02`, …) i nagłówku `<HEADER>`:

> Jesteś native'owym redaktorem polskim, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03b_section_checker.md` i wykonaj go dokładnie. Cały
> scenariusz: `outputs/videos_pl/$1/md/03a_draft.md`. **Twoja sekcja: `<HEADER>`.**
> Flaguj tylko zdania w tej sekcji (sąsiednie akapity czytaj dla kontekstu, nie
> poprawiaj). Zapisz listę zgłoszeń do `outputs/videos_pl/$1/md/iter/sek_NN.md`.
> Twój zwrot = treść pliku.

**b) Jeden arc-checker:**

> Jesteś redaktorem patrzącym na spójność całości, dispatchowanym na zimno.
> Przeczytaj `workflows/pipeline/03b_arc_checker.md` i wykonaj go dokładnie na całym
> `outputs/videos_pl/$1/md/03a_draft.md`. Zapisz zgłoszenia `[A]` do
> `outputs/videos_pl/$1/md/iter/arc.md`. Twój zwrot = treść pliku.

Poczekaj, aż **wszystkie** skończą.

## Step 5 — Scal listy (Ty, in-session)
Złóż jeden plik `outputs/videos_pl/$1/md/03b_corrections.md`:
1. najpierw blok z `arc.md` (zgłoszenia `[A]`),
2. potem sekcje w kolejności dokumentu (`sek_01.md`, `sek_02.md`, …), każda ze
   swoimi `[K]` i `[Z]`.
Zachowaj tagi `[A]`/`[K]`/`[Z]` — fixer po nich segreguje kolejność. Pomiń sekcje,
które zwróciły „Brak zgłoszeń".

## Step 6 — Fixer (świeży zimny subagent Opus)
Zespawnuj **nowego** subagenta (`general-purpose`, `model: opus`) z briefem:

> Jesteś redaktorem, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03c_fixer.md` i wykonaj go dokładnie. Scenariusz:
> `outputs/videos_pl/$1/md/03a_draft.md`. Scalona lista poprawek (tagi
> `[A]`/`[K]`/`[Z]`): `outputs/videos_pl/$1/md/03b_corrections.md`. Wstaw poprawki
> chirurgicznie — najpierw `[A]`/`[K]` (struktura), potem `[Z]` (zdania) — i zapisz
> CAŁY poprawiony scenariusz do `outputs/videos_pl/$1/md/04_final.md` (zachowaj
> nagłówki `## `). Twój zwrot = treść pliku.

Poczekaj na ukończenie.

## Step 6.5 — Ściskacz (świeży zimny subagent Opus, TYLKO cięcie)
Najpierw zachowaj wersję sprzed ściśnięcia do porównania — skopiuj (Bash)
`md/04_final.md` → `md/04_final_presqueeze.md`. Potem zespawnuj **nowego**
subagenta (`general-purpose`, `model: opus`) z briefem:

> Jesteś ściskaczem SENSUM, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03d_compressor.md` i wykonaj go dokładnie. Scenariusz:
> `outputs/videos_pl/$1/md/04_final.md`. **Tylko tniesz** 6 trybów przegadania —
> nigdy nie dopisujesz, nigdy nowej metafory, trzymasz zasadę zachowawczą. Zapisz
> CAŁY ściśnięty scenariusz z powrotem do `outputs/videos_pl/$1/md/04_final.md`
> (zachowaj nagłówki `## `). Twój zwrot = treść pliku.

Poczekaj na ukończenie.

## Step 7 — Raport
Wczytaj `outputs/videos_pl/$1/md/04_final.md`. Zdaj userowi:
- liczbę słów **przed i po ściśnięciu** (porównaj `04_final_presqueeze.md` →
  `04_final.md`; podaj ile słów / % ucięto),
- ile zgłoszeń łącznie (`[Z]` / `[K]` / `[A]` — policz po tagach w
  `03b_corrections.md`),
- ślad: `md/03a_draft.md` (surowy, zamrożony), `md/iter/sek_*.md` + `md/iter/arc.md`
  (zgłoszenia per checker), `md/03b_corrections.md` (scalone),
  `md/04_final_presqueeze.md` (po fixerze, przed ściskaczem), `md/04_final.md`
  (finał, ściśnięty),
- **pokaż finalny scenariusz** w czacie do oceny,
- przypomnij, że finalną redakcję robisz na `docx/script_corrected.docx` (eksport
  docx robi `/hook`),
- następna komenda: `/hook $1`.

## Notes
- **Wszystkie checkery czytają zamrożony `03a_draft.md` — nigdy cudze poprawki.**
  To gwarancja braku dryfu. Nie spawnuj checkerów sekwencyjnie na zmieniającym się
  tekście.
- **Po jednym section-checkerze na `## `.** Policz nagłówki dynamicznie (6–8 to
  norma, ale bierz tyle, ile jest).
- **Nie tnij draftu na pliki-fragmenty.** Każdy checker dostaje ścieżkę do CAŁEGO
  draftu + swój nagłówek; czyta swoją sekcję z naturalną zakładką ±1 akapit.
  Karmienie pociętymi zdaniami zabija kontekst (to zabiło stary /refine).
- **Równoległość = wszystkie spawny kroku 4 w JEDNEJ wiadomości.**
- **Bez pętli.** Pisarz → ensemble → fixer → ściskacz i koniec. Twoje ucho na
  `script_corrected.docx` to ostatni sufit — nie iterujemy maszyną w nieskończoność.
- **Ściskacz tylko tnie.** Ostatni pass; usuwa przegadanie, NIGDY nie dopisuje
  (cut-only = zero thrashu — nie wprowadzi dziwnych zdań). Wersja sprzed ściśnięcia
  zostaje w `md/04_final_presqueeze.md` do porównania.
- **NIE** shelluj do `tools/pipeline/agent3*.py` — to martwa legacy ścieżka Gemini.
- Jeśli spawn subagenta zawiedzie: odpal danego agenta jako pojedyncze, **świeże,
  zimne przejście** in-session wg jego pliku-promptu, w tej samej kolejności i z
  tymi samymi plikami wyjściowymi. (Section-checkery można wtedy puścić
  sekwencyjnie — i tak czytają zamrożony oryginał, więc kolejność nie szkodzi.)
