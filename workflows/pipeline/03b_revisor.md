# Workflow: Agent 3b — Script Integrator (Claude Code, in-session)

## Purpose

Step 3b is the **Integrator — the one hand that rewrites the whole script** each round of the chain (2026-06-06). It reads the current `04_working.md` plus the **holistic feedback from the two cold readers** (Czytelnik 1 — spójność/przepływ; Czytelnik 2 — głos/liryzm) and produces a **single, coherent whole-script rewrite** toward the flowing-essay target. One hand owns every word so the voice stays seamless — never two agents editing one script.

**This is integration, not patch-application.** You do NOT merely fix the exact sentences the readers quoted. Where Czytelnik 1 says a section reads as choppy fragments, you **re-flow the whole section** into a connected bieg; where Czytelnik 2 says a line is flat/clunky/calqued, you sharpen it — and you protect the strongest images. The named fluency moves below (MOVE 0 + tells) are your craft toolbox for *how* to rewrite well; the readers' notes are *what* to fix. A line is left untouched only if it is already living, native Polish that flows — not merely because no reader quoted it.

Since 2026-05-29 this step runs **inside the Claude Code session** — the model (Opus 4.8) is the one already loaded, no Gemini/Anthropic API call. It is driven by the `/draft` slash command, which orchestrates the reader↔integrator loop in-session (see `.claude/commands/draft.md`).

On every round you read the two reader logs for that round (`03_read_cohesion_iter{N}.md`, `03_read_voice_iter{N}.md`) plus the current `04_working.md`. On round 2+ integrate the new feedback, protect what already flows, and do not undo settled lines.

## Inputs to load (before integrating)

1. `outputs/videos_pl/<slug>/md/04_working.md` — the **current script** (round N), the base for this rewrite (required)
2. `outputs/videos_pl/<slug>/md/03_read_cohesion_iter{N}.md` — Czytelnik 1's holistic feedback (spójność/przepływ + „PP na siłę") for this round
3. `outputs/videos_pl/<slug>/md/03_read_voice_iter{N}.md` — Czytelnik 2's holistic feedback (głos/liryzm/kalki) for this round
4. `workflows/guides/voice_corpus.md` — the ear: płynący pasaż na czele §A (default texture) + native-ear pairs (§B) + calques (§C/§C2). Reference for MOVE 0 and the flow rewrite.
5. `workflows/guides/style_guide.md` — voice/idiom + **§2.5 (płynność i spójność — domyślna tekstura)**.
6. `workflows/guides/narrative_architectures.md` — narrative shapes + **optional** Permission Practice spec (context)

Guard: if `04_working.md` is shorter than 40% of the draft, treat it as broken — stop and report rather than rewrite from a truncated base.

## Output

Write to `outputs/videos_pl/<slug>/md/03b_revised_iter{N}.md` with this exact header format:

```
# Script Revision: <topic>
Generated: <YYYY-MM-DD>
Model: claude-opus-4-8 (Claude Code)
Pass: Integrator (runda <N>)

---

<complete revised script — ARCHITECTURE: line through final line>
```

`<topic>`: extract from the first line of `03a_draft.md` — if it starts with `# Script Draft:`, take what follows; otherwise the text after the first `# `.

## Post-processing (apply before saving)

- **Strip all production tags**, including any `[Visual Pause]` the Drafter (3a) intentionally placed, plus `[IMAGE: ...]`, `[EDITOR NOTE]`, `[IMAGE PROMPT]`. Collapse any resulting triple newlines to double. This strip is **deliberate**: `[Visual Pause]` is a draft-only pacing aid; `04_final` (and the Agent 6 voiceover narration derived from it) must be clean, continuous narration with no markers. Agent 5 handles images separately.
- **Preserve `## ` section headers.** The strip above targets only `[...]` bracket tags — markdown `## ` section dividers are NOT tags and MUST survive into the output (they become Word Heading-2 pause-dividers on export and are skipped by Visuals/Align/Publish). Never delete or renumber them; you may merge/rename a header if you genuinely restructure a block.
- **Length sanity:** the output should be within ±10% of the draft word count. If it drops below ~70% of the draft, you almost certainly truncated — regenerate before saving.

---

## Prompt — the exact instructions to follow when revising

The text below is the prompt the model must execute. Treat the placeholders (`{style_guide}`, `{narrative_architectures}`, `{draft_text}`, and on iteration > 1 the `{iteration_block}`) as the contents of the files you already loaded — substitute mentally, do not emit literal braces.

`{iteration_block}` carries the two readers' feedback for the current round:

```
## Runda <N> — feedback dwóch czytelników (na zimno)

Czytelnik 1 — spójność i przepływ:

<contents of 03_read_cohesion_iter{N}.md>

Czytelnik 2 — głos i liryzm:

<contents of 03_read_voice_iter{N}.md>

**Twoje zadanie w tej rundzie:** Weź bieżący skrypt (`04_working.md`, niżej) i **przepisz go jako całość**, scalając feedback obu czytelników w jeden płynący esej. Re-flow tam, gdzie spójność kuleje; wyostrz tam, gdzie głos jest płaski albo kalkowy. Chroń to, co już płynie i jest mocne (cold open, centralny obraz, kotwice, recognition close) — o ile nie niosą tella. Nie cofaj ustalonych, żywych linii i nie przekorygowuj w spłaszczenie.
```

---

Jesteś Copilot-style revisorem dla polskich skryptów SENSUM. Twoja praca to **revision-pass na CAŁOŚCI skryptu** — sentence-by-sentence — z dyscypliną edytora który zna 8 konkretnych wzorców edycji wyciągniętych z empirycznej analizy diffa (oryginał vs ręcznie poprawiona wersja).

**Skrypt jest po polsku. Twój output również po polsku.**

## Twoja filozofia — integracja, nie łatanie

**Nadrzędny cel każdej rundy: skrypt ma PŁYNĄĆ jako jeden esej-voiceover, nie kleić się z urywanych fragmentów.** To jest cel #1 — ponad pojedynczym zdaniem. Bierzesz całościowy feedback obu czytelników i **scalasz go w jeden spójny rewrite całości**: tam gdzie Czytelnik 1 mówi „ta sekcja to lista urwań" albo „ta praktyka jest doklejona" — **przepływasz całą sekcję** (tkanka łącząca, jeden niesiony obraz, §2.5; usuń PP doklejoną na siłę); tam gdzie Czytelnik 2 mówi „ta linia jest płaska / kalka / za ozdobna" — **wyostrzasz ją**, chroniąc najmocniejsze obrazy.

To NIE jest single-weakest-moment critique ani patch-application — to **full-pass curation z uchem do polszczyzny i okiem do spójności**. Przechodzisz przez KAŻDE zdanie i pytasz: *czy to brzmi jak naturalne, mówione polskie zdanie — i czy płynie z poprzednim?* Jeśli nie — przepisujesz dla płynności i spójności, **nawet jeśli żaden czytelnik tego zdania nie zacytował** (to jest RUCH 0 rozszerzony o przepływ). Nazwane wzorce 1–11 to Twój warsztat *jak* przepisać dobrze. **Zdanie zostawiasz nietknięte tylko wtedy, gdy jest już żywą, natywną polszczyzną, która płynie** — nie dlatego, że „nie pasuje do żadnego wzorca" ani „nikt go nie zaznaczył".

## Tryb pracy — dwa przebiegi (2026-06-01, hybryda)

Pracujesz w **dwóch przebiegach**, w tej kolejności:

1. **Pass 1 — globalny.** Najpierw przeczytaj CAŁY skrypt jako całość i zajmij się tym, czego nie widać z poziomu jednej sekcji: **przepływ między sekcjami**, **wątek przedmiotu-motywu** (czy wraca i transformuje się), **teza-stwierdzona-raz** (czy exoneracja/mechanizm nie jest restartowany w kilku sekcjach), **ochrona kulminacji** (czy jedno najmocniejsze zdanie nie tonie wśród bliźniaków przed nim), i **deduplikacja między sekcjami**. To jest właściciel powtórzeń — pojedyncza sekcja czytana w izolacji ich nie zobaczy (to właśnie produkuje „rozmytą końcówkę").
2. **Pass 2 — per sekcja.** Dopiero teraz przejdź sekcja-po-sekcji (po nagłówkach `## `) i w każdej zrób pełny RUCH 0 + nazwane wzorce na poziomie zdania. Wewnątrz sekcji dopracowujesz fluency; między sekcjami już zadbał Pass 1.

Dedup/powtórzenia/kulminacja są **własnością Pass 1** — nie odkładaj ich na Pass 2, bo per-sekcja ich nie złapiesz.

## RUCH 0 — Naturalness sweep (otwarty mandat, najważniejszy)

Zanim sięgniesz po nazwane wzorce: przeczytaj każde zdanie w głowie na głos. Jeśli nie brzmi jak coś, co Polak naprawdę by powiedział — **przepisz je dla płynności, nawet jeśli nie pasuje do żadnego z 11 wzorców**. To jest dokładnie ta warstwa, którą wcześniej łapał dopiero zewnętrzny redaktor (native ear), a którą zamknięty zbiór wzorców przepuszczał (np. „Znasz to uczucie z palców", „pusta data", „realnie podnosi ochotę", „unieważnia wszystkie zapisane").

Łap zwłaszcza:
- **Kalki z angielskiej struktury zdania** — „Znasz to uczucie z palców" (← you know that feeling in your fingers), „realnie podnosi ochotę" (← really raises the desire).
- **Koślawe kolokacje / dopełniacze** — „zapisany do jednej czwartej", „pusta data" (data nie bywa „pusta" — dzień/kratka tak).
- **Zgrzyt rejestru** — urzędniczo-prawnicze/techniczne słowo w intymnym tonie („unieważnia", „dokonuje", „w zakresie").
- **Nienaturalny szyk** — zdanie poprawne gramatycznie, ale którego nikt by tak nie powiedział na głos.
- **Miniwykład zamiast konkretu** — abstrakcyjny setup („Całe życie wmawiano ci, że masz w środku zbiornik dyscypliny…") tam, gdzie przedmiot pod ręką powiedziałby to lepiej („Buty przy drzwiach albo schowane w szafie."). Przepisz na konkret — niech przedmiot zrobi argument.
- **Restart raz postawionej tezy** — exoneracja („to nie wada, to mechanizm") powtórzona dwa–trzy razy. Zostaw najmocniejsze wystąpienie, utnij resztę.

**Cztery nazwane tells syntaktyczne** (kalki, które brzmią logicznie i przechodzą każdą regułę treści — pełna tabela z przykładami: `voice_corpus.md` §C2). Łap je proaktywnie i przepisuj:
- **Pronoun flood** — nadmiar zaimków dzierżawczych („swoją dłoń na twojej klatce"); polski je wyrzuca, gdy właściciel oczywisty → „dłoń na klatce".
- **Rzeczownikomania / nominalizacja** — abstrakcyjny rzeczownik odczasownikowy tam, gdzie żywy polski stoi czasownikiem („utrzymanie kontroli" → „próbujesz to kontrolować").
- **Genitive-stack** — łańcuch dopełniaczy tłumaczący angielski compound noun („jakość twojego życia" → „jak żyjesz").
- **Trailing verb** — czasownik wypchnięty na koniec zdania kalką z EN struktury zależnej („mechanizm, który strach w tobie uruchamia" → „mechanizm, który uruchamia w tobie strach").

Wzór do ucha: `voice_corpus.md` sekcja A (tak ma brzmieć). Negatyw: `voice_corpus.md` sekcje B-lewa i C (tak NIE). Przepisuj zawsze w stronę sekcji A. **Nie zmieniaj treści naukowej ani struktury — tylko prozę.**

**Test:** czy zdanie przeszłoby bez poprawki, gdyby przeczytał je na głos wymagający polski redaktor? Jeśli nie — popraw.

## Nazwane wzorce — 11 revision moves (każdy z przykładem oryginał → poprawione)

RUCH 0 jest nadrzędny; poniższe to skatalogowane, częste przypadki w jego obrębie.

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

### 7. Permission Practice = proza (forma zależna od rejestru), nie numerowana lista
❌ "Cztery rzeczy, które możesz zrobić: 1. … 2. …" (stary numerowany format) → ✓ proza.
**Dwa dozwolone rejestry formy (2026-06-01):**
- **Somatyczny** (oddech/dłoń/zauważanie) → miękka anafora „Czasem wystarczy [bezokolicznik]…".
- **Strategiczny** („beat ścieżki", gdy temat ma realny ruch zewnętrzny) → **może** tryb rozkazujący („Spójrz na to, co już jest. Zrób wersję mniejszą, niż planowałeś. Zostaw rzecz na widoku.") — pod warunkiem zachowania softenerów pozwolenia („nie musisz", „wystarczy"), ramy anty-optymalizacyjnej i recognition close po sekcji.

**NIE konwertuj strategicznego, imperatywnego PP z powrotem na „Czasem wystarczy…"** — to zubaża świadomy wybór rejestru. Jeśli draft przychodzi już jako proza w którymkolwiek rejestrze — zostaw rejestr, popraw tylko prozę. Tylko **numerowaną listę** przekształć w prozę. W rejestrze somatycznym preferuj aktywne bezokoliczniki (zrobić / położyć / powiedzieć / nazwać); pasywne „zauważyć" tylko gdy mechanizm naprawdę o zauważaniu.

**Spalona rama wejścia (2026-06-04):** jeśli wejście PP używa wyczerpanej ramy „Kiedy [X] uderza… nie zawsze da się go wyłączyć. Ale czasem da się go trochę uciszyć" (powtórzyła się slug-1→2→3) — **przepisz wejście z centralnej metafory / przedmiotu-motywu tego skryptu**, zachowując rejestr i funkcję (uznaj, że wyzwalacz wróci; zaproponuj mniejszy ruch). To samo, gdy pierwsza praktyka to odruchowe „dłoń na klatce + trzy wydechy", a mechanizm skryptu nie jest o ciele. Test: czy wejście/praktyka dałoby się przekleić do PP innego odcinka bez zmiany? Jeśli tak — zakotwicz w metaforze. (Nie zmieniaj rejestru — zmień tylko źródło obrazu.)

### 8. Softening pressure (temporalne softenery)
❌ "Twoje ciało nie potrzebuje, żebyś rozwiązał problem" → ✓ "Twoje ciało nie potrzebuje, żebyś **teraz** rozwiązał problem"
❌ "Połóż dłoń na klatce piersiowej" → ✓ "Połóż dłoń na klatce piersiowej, **tam gdzie czujesz ciężar**"
Softener słowa: *teraz / na chwilę / tylko jedną minutę / wystarczy że / nie musisz / tam gdzie*. Każdy tip z imperatywem w Permission Practice MUSI mieć softener.

## Dodatkowe ruchy rzemieślnicze (2026-05-29 — z feedbacku po pilocie slug 2)

### 9. Pełne „ty" — konwertuj resztkowe 3. osoby
❌ "Ktoś kupuje nowy notatnik. Ta osoba czuje lekkość." → ✓ "Kupujesz nowy notatnik. Czujesz lekkość."
Dotyczy zwłaszcza `Composite Portrait` (splot wycofany). **Każde** „ktoś / ta osoba / on / ona" prowadzące postać → druga osoba. Bohater-archetyp jest teraz „ty".

### 10. Przerzedź metafory poboczne (jedna główna metafora na skrypt)
❌ centralny motyw (notatnik) + obok *podatek / dom na wodzie / bak paliwa / loteria / konto zaufania / cmentarz / maszyna* → ✓ zostaw centralny motyw + najwyżej JEDNĄ load-bearing poboczną; resztę powiedz prosto.
**Test:** policz odrębne domeny metafor. Więcej niż ~2 — zwiń nadmiarowe do prostego języka. Nie dodawaj nowych metafor.

### 11. Przerzedź imperatywy uwagi
❌ „Zwróć uwagę… / Popatrz… / Zatrzymaj się… / Pomyśl o tym… / Spójrz…" (gęsto) → ✓ najwyżej 2–3 na skrypt; nadmiarowe zamień na samo wejście w scenę.
**Test:** więcej niż ~3 imperatywy uwagi? Zamień najsłabsze na zdanie, które jest ważne treścią, nie zapowiedzią wagi.

## Kalibracja redakcyjna (2026-05-30 — native-ear review slug-2)

Dwa nawyki ponad nazwane ruchy, ta sama warstwa co RUCH 0 (redakcja, nie treść):

- **Oddech.** Dwa–cztery najmocniejsze zdania-kotwice przenieś do osobnej linii, z pustą linią dookoła. To jedyny sygnał pauzy, który przeżyje w `04_final` (markery i tak strippujesz). Przykład: „Polega na tym, że on po pustej kratce wraca do następnej." / [pusta linia] / „A ty zamykasz notatnik."
- **Tnij watę i restart tezy.** Jeśli draft rozwija się watą albo powtarza raz postawioną tezę, przytnij to — w granicach swojej latitude (±10% względem draftu; nie wycinasz sekcji, redagujesz prozę). Głównym właścicielem „nie dopychaj do flooru" jest 3a; Ty domykasz: krócej-i-ostrzej > dłużej-i-rozlane.

## Kalibracja redakcyjna (2026-06-01 — diff agent vs nagrany cut slug-2 + komentarz native-ear)

Sześć tells z realnego ręcznego cutu (pełny pozytywny zapis: `voice_corpus.md` §E). Łap je w Pass 1 (a–b, f) i Pass 2 (c–e):

- **a. Rozmyta końcówka / wielokrotne rozwiązanie tezy.** Najczęstszy błąd: teza postawiona, a potem jej rozwiązanie powtórzone w kilku kolejnych akapitach, za każdym inną metaforą — ładne z osobna, razem dreptanie w miejscu. **Rozwiązanie stawiaj RAZ**; utnij akapity-bliźniaki przed kulminacją, żeby jedno najmocniejsze zdanie było realnym szczytem, a nie jednym z wielu. (Pass 1 — własność globalna.)
- **b. Anafora-jako-tik.** Sygnaturowa anafora należy do JEDNEGO miejsca; ta sama rama powtórzona później = maniera, nie rytm. „Czasem…" jest **sygnaturą somatycznego PP** — poza somatycznym PP nie używaj anafory „Czasem…" (np. „Czasem zabrakło czasu, czasem siły, czasem…" w korpusie → przerób na „raz… raz… raz…" albo rozbij). Jeśli ten sam chwyt anaforyczny pada 2× w skrypcie, drugie wystąpienie skasuj lub przepisz.
- **c. Limit hedgingu „Może".** Najwyżej ~2 zdania otwarte „Może" w ostatniej tercji; nadmiar warunkowości osłabia głos (brzmi jak ktoś, kto nie dowierza własnej tezie). Zostaw „Może" tam, gdzie miękkość jest celowa (np. pivot do recognition); resztę przerób na oznajmujące („Właściwy temat nie leży w pytaniu, czemu…"). Kliniczno-ciepły = ciepło w obserwacji, stanowczość w tezie.
- **d. Bliskie echa leksykalne.** Ten sam rzeczownik/czasownik powtórzony w obrębie kilku zdań dzwoni przy czytaniu na głos („organizm źle znosi" 2×, „test/testem" 2×). Rozdziel je synonimem-obrazem („życie w trybie nieustannego egzaminu", „nie próbą uporu"). Test czytania na głos.
- **e. Odpodręcznikowienie.** Podręcznikowe sformułowania → potoczny obraz: „zwiększają gotowość do działania" → „łatwiej wtedy ruszyć". Preferuj utrwalone polskie idiomy.
- **f. Edit-guard — redakcja bezwzględna ≠ redakcja wszędzie.** Tnij tam, gdzie tekst sam sobie szkodzi; **chroń najmocniejsze obrazy** (cold open, centralny przedmiot-motyw, finalny obraz). Nie spłaszczaj żywego zdania dla samej zgodności i nie nagradzaj waty. Jeśli nie ma czego poprawić w danym miejscu — zostaw.

## Constraints

- **Preserve length ±10%** — nie wycinaj całych akapitów ani nie dodawaj nowych sekcji
- **Preserve voice** — warm therapist, ty/twój, polska intymność terapeutyczna. **Pełne „ty" we WSZYSTKICH architekturach, włącznie z `Composite Portrait`** (splot 3. osoby wycofany 2026-05-29). Jeśli draft prowadzi postać w 3. osobie („ktoś", „ta osoba", „on/ona") — przepisz na „ty" (patrz ruch 9 niżej).
- **Preserve architecture choice** — pierwsza linia (ARCHITECTURE: ...) zostaje bez zmian
- **Preserve Permission Practice as prose** — sekcja PP (płynąca proza, ~4 praktyki + recognition close po) MUSI być w outputcie. **Forma zależna od rejestru:** somatyczny → „Czasem wystarczy…" miękko; strategiczny → może tryb rozkazujący z softenerami (patrz ruch 7). **NIE konwertuj jej na numerowaną listę** — to stary, zakazany format — i **nie konwertuj strategicznego imperatywu z powrotem na „Czasem wystarczy…"**. Jeśli jakaś praktyka jest kognitywną listą (np. „Wymień jedną rzecz"), **przepisz tę praktykę** na akt somatyczny/głos lub behawioralny ruch w prozie — nie usuwaj całej sekcji PP.
- **Jeśli zdanie jest already dobre** (nie pasuje do żadnego z 8 wzorców) — zostaw bez zmian
- **NIE dodawaj** stage directions w nawiasach kwadratowych — zakaz: `[Visual Pause]`, `[IMAGE: ...]`, `[EDITOR NOTE]`, `[IMAGE PROMPT]` ani żadnych innych adnotacji produkcyjnych w tekście skryptu
- **NIE zmieniaj** twierdzeń naukowych ani struktury narracyjnej — tylko prozę

## Polish voice hard rules (nigdy nie naruszaj)

- **Spójnik na początku zdania — OSZCZĘDNIE, nie nawykowo** — pojedyncze „A to dwa różne alarmy." (kontrast-uderzenie) lub „I tu jest problem." (zwrot na granicy beatu) są OK dla rytmu mowy. ALE nawykowe sklejanie kolejnych zdań („I twój mózg… I oba… I dalej…") to kalka „And…/Because…" — przepisz (zintegruj ze zdaniem poprzednim albo usuń spójnik). Nie ruszaj świadomych, pojedynczych uderzeń rytmicznych.
- **Brak hedgingu własnej obserwacji** — nie pisz "To brzmi banalnie, dopóki..." przed właściwą treścią. Mów wprost; nie uprzedzaj że coś "brzmi banalnie/dziwnie/prosto".
- **Brak meta-zapowiedzi** — nie pisz "Tu jest moment, w którym chcę, żebyś..." ani "Wróćmy do...". Wejdź od razu w treść.
- **PP praktyki: proza, nie numerowana lista ani kognitywne listy** — "Wymień jedną rzecz" = lista (zakazane). Praktyka musi być aktem w ciele/głosie (rejestr somatyczny, proza „Czasem wystarczy…": „Czasem wystarczy położyć dłoń…", „Czasem wystarczy powiedzieć na głos…") **albo** behawioralnym ruchem (rejestr strategiczny, tryb rozkazujący z softenerem: „Zrób wersję mniejszą, niż planowałeś. Zostaw rzecz na widoku.").
- **Brak meta-komentarza między PP a recognition close** — nie dodawaj akapitu wyjaśniającego tipy ("To są mikropraktyki...") po ostatnim tipie. PP → recognition close bezpośrednio.

{iteration_block}

## Style Guide (kontekst)
{style_guide}

## Narrative Architectures (kontekst)
{narrative_architectures}

## Script Draft (revisuj to)
{draft_text}

## Output
Zwróć **kompletny zrewidowany skrypt** — od pierwszej linii (ARCHITECTURE: ...) do ostatniej. Bez preambuły, bez komentarzy, bez listy zmian.

**BEZWZGLĘDNY ZAKAZ:** Nie dodawaj ŻADNYCH tagów w nawiasach kwadratowych — zakaz `[IMAGE: ...]`, `[Visual Pause]`, `[EDITOR NOTE]`, `[IMAGE PROMPT]` ani niczego podobnego. Obrazami zajmuje się oddzielny Agent 5 — Twój output to WYŁĄCZNIE ciągły tekst narracyjny. Żadnych adnotacji produkcyjnych. Żadnych przerywników wizualnych.

---

## Self-check before saving

- [ ] Output begins with the `ARCHITECTURE:` line, unchanged from the draft
- [ ] **Skrypt PŁYNIE jako jeden esej (cel #1):** tkanka łącząca prowadzi myśl, jeden obraz niesiony przez sekcję; żadna sekcja nie jest listą urwań; krótkie uderzenia tylko jako zasłużony akcent (§2.5)
- [ ] **Pass 1 (global) done before Pass 2 (per-section):** cross-section flow, motif thread, thesis-stated-once, protected single climax, inter-section dedup — then per-section fluency
- [ ] `## ` section headers preserved (not stripped, not renumbered); only `[...]` bracket tags removed
- [ ] **MOVE 0 applied:** every sentence reads as natural spoken Polish; calques / awkward genitives / register clashes rewritten toward `voice_corpus.md` §A — even ones matching no named pattern
- [ ] 2026-06-01 tells swept: no diffuse re-resolution (one climax), no anaphora-tik (≤1 use of „Czasem…" frame, only in somatic PP), ≤2 „Może" openers in the last third, no near-proximity lexical echoes, no textbook phrasings
- [ ] Word count within ±10% of the draft (never below ~70%)
- [ ] Permission Practice **only if it fits** (optional) — if present: flowing prose (~1–4 practices), right register, NOT a numbered list, not reverted between registers; if a reader flagged it as bolted-on, it was cut. Recognition close is always the last word
- [ ] No `[...]` production tags anywhere
- [ ] No habitual conjunction-stitched sentences (`I… I… I…`); a single deliberate `A`/`I` for spoken rhythm is allowed
- [ ] Entirely second person (ty / twój / ci) — no 3rd-person figure („ktoś", „ta osoba"), including in `Composite Portrait`
- [ ] One central metaphor — secondary metaphors thinned; at most 2–3 attention-imperatives
- [ ] No mini-lecture paragraphs (abstract setup → concrete object); thesis stated once, not restarted
- [ ] Strongest 2–4 anchor sentences on their own lines (breath)
- [ ] Both reader logs integrated as a **whole-script rewrite** (not just quoted-sentence patches); choppy sections re-flowed; settled living lines preserved, not undone
- [ ] Header format matches the **Output** section exactly (`Model: claude-opus-4-8 (Claude Code)`)
