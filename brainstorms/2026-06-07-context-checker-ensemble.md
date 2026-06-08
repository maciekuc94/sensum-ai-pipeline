# Context-aware ensemble checker (Gen 4 /draft): Brainstorm / Discovery Notes
Date: 2026-06-07 · Goal: po lean-redesign (3 agenty) — drugi problem: checker łapie kalki zdaniowe, ale nie widzi, że dwa poprawne zdania razem nie mają sensu, ani że metafora pęka między sekcjami. Zaprojektować ensemble: section-checkery (zdanie+kontekst) + arc-checker (całość), bez dryfu.

Cross-ref: `2026-06-07-lean-draft-redesign.md` (Gen 3 — pisarz→checker→fixer, na którym to stoi).

## Summary / key decisions

**Problem, który to wywołał.** Po lean-redesign odpaliliśmy checker+fixer kilka razy na drafcie slug-3, żeby zobaczyć, czy więcej przejść łapie więcej zgrzytów. Dwa odkrycia:
1. **Iteracja dryfuje (Idea B odrzucona).** Checker→fixer→checker na **zmieniającej się** kopii nie zbiega: własna poprawka fixera staje się następnym zgłoszeniem checkera (zgrzyty: 12→18→10→21, ping-pong „kamień", „reszta ciebie", „wyrok→skreślić"). Sekwencja na ruchomym tekście = thrash.
2. **Checker jest niekompletny-ale-nie-błędny.** Różne zimne odczyty łapią różne podzbiory („ma ciało" przepuszczone w r1–r3, złapane w r4). Sygnał: nie iterować po tym samym, tylko **wziąć sumę wielu niezależnych odczytów zamrożonego oryginału**.

**Idea A przyjęta — ensemble na zamrożonym oryginale.** Wiele zimnych checkerów czyta **ten sam, niezmienny `03a_draft.md`**; jeden terminalny fixer scala ich sumę. Poprawka nigdy nie staje się nowym błędem, bo żaden checker nie widzi poprawek. Zbieżność z definicji (nic nie pływa).

**Druga oś — kontekst, nie tylko zdanie.** Przykład usera: „Pomyśl przez chwilę, kto ustawił zasady na tej tablicy. **Bo to nie ty je wymyśliłeś.**" — każde zdanie osobno OK, razem nie domykają się w sens. Zdaniowy checker tego nie łapie (każde zdanie przechodzi w izolacji). Potrzebny odczyt **jak zdania się łączą**.

**Jednostka = sekcja `## `, nie pocięte zdania.** User: „NIE karm checkerów pociętymi zdaniami". Czytanie zdań w izolacji zabiło /refine. Sekcja (~150 słów) + zakładka ±1 akapit to jednostka, w której (a) split uwagi zdanie/kontekst jest pomijalny, (b) ocena zdania **w kontekście** jest lepsza niż w izolacji. Zwalidowane na „Skąd się wziął sędzia": jeden zunifikowany section-checker złapał „ma ciało" (3-rundowy ocalały) **plus** nowe `[K]`-zgrzyty kontekstu, w jednym przebiegu.

**Jeden zunifikowany section-checker, nie dwa.** User: „może nie potrzebujemy phrase checker — tylko context checker, który też sprawdzi zdania, ale zwróci uwagę na kontekst." → jeden agent, dwa przejścia po kolei: **[Z]** każde zdanie na własną rękę (gładki kontekst NIE usprawiedliwia kalki), potem **[K]** jak się łączą.

**Po jednym section-checkerze na `## ` + jeden arc-checker.** User: „Puszczamy tyle context-checkerów ile jest `##`. Równolegle jeden agent przegląda, czy całość się klei." Section-checker w jednej sekcji jest **konstrukcyjnie ślepy** na własności międzysekcyjne (metafora pękająca między sekcjami, klamra otwarcie↔zamknięcie, narastanie, przejścia `##`→`##`). Arc-checker robi tylko to i **nie** dubluje zdań.

**Fixer: struktura przed zdaniem.** `[K]`/`[A]` to poprawki **strukturalne** (mostek, cięcie, przepisane przejście, dociągnięte odniesienie) — robione **przed** `[Z]` (chirurgiczne podmiany), bo zmieniają sąsiedztwo. Przy `[A]`/`[K]` maksymalna powściągliwość; nigdy nowa metafora, nigdy przepisana sekcja.

**Reguła stopu.** „Aż checker nic nie znajdzie" jest **błędna** — brief checkera („jeśli się wahasz, i tak wpisz") gwarantuje, że na ~1100 słowach nigdy nie zejdzie do zera. Stop = stała liczba przejść (po jednym na sekcję + jeden arc, równolegle, raz). Bez pętli.

## Co zbudowane (ten build)
- `workflows/pipeline/03b_section_checker.md` — **NOWY** (zdania `[Z]` + kontekst `[K]`, jedna sekcja + zakładka, flaguje tylko swój rewir).
- `workflows/pipeline/03b_arc_checker.md` — **NOWY** (całość `[A]`: metafora / klamra / narastanie / przejścia; nie dubluje zdań).
- `workflows/pipeline/03c_fixer.md` — **ZMIENIONY** (scalona lista z tagami; `[A]`/`[K]` przed `[Z]`; powściągliwość na strukturze).
- `.claude/commands/draft.md` — **PRZEPISANY** (pisarz → spis `## ` → N section + 1 arc równolegle na zamrożonym → scal → fixer).
- `03b_checker.md` (stary whole-script) — **legacy**, niereferencjonowany przez nowy `/draft`; zostaje do czasu walidacji.

## Do dosynchronizowania (po walidacji, świadomie odłożone)
CLAUDE.md + tabela Agent Chain wciąż opisują pojedynczy `03b_checker`. Sync po pierwszym dobrym przebiegu — nie ruszam kanonu usera, dopóki nowy schemat się nie obroni na realnym tekście.

## Poza zakresem (nietknięte)
Research 0/1/2, /hook, /visuals, /publish, /package, align, pisarz (`03a_writer.md` bez zmian).

## Otwarte flagi
- Czy arc-checker i section-checkery nie generują **podwójnych** zgłoszeń tej samej rzeczy (granica „zdanie vs łuk"). Prompt arc mówi „nie dubluj zdań" — sprawdzić na realnym przebiegu, czy trzyma.
- Liczba section-checkerów = liczba `## ` (tu ~7). Jeśli pisarz da bardzo drobne sekcje (12+), rozważyć łączenie sąsiednich w jeden rewir. Na razie 1:1.
