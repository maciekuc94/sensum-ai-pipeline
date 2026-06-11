# Gen 5 /draft — architektura obietnic, bez ściskacza, bez /hook: Brainstorm / Discovery Notes
Date: 2026-06-11 · Goal: przeprojektować łańcuch pisania skryptu pod retencję (curiosity loops co ~60–90 s, filmy 10–15 min) i wdrożyć poprawki z audytu łańcucha, jednocześnie UPRASZCZAJĄC system (ściskacz out, /hook scalony w /draft).

Cross-ref: `outputs/channel_assets/diagnoza_pierwszych_3_filmow_2026-06.md` (dźwignia C.2 — re-hooki), audyt łańcucha /draft z sesji 2026-06-11 (forensyka slug 4 + dyff maszyna-vs-człowiek slug 2–3 + model kosztowy), `2026-06-07-context-checker-ensemble.md` (Gen 4), `2026-06-07-poprawka-doktryny-glosu.md` (v2/v2.1 + ściskacz).

## Kontekst wejściowy (ustalenia, na których stoi projekt)

**Z diagnozy 3 filmów:** dystrybucja jest, hook @ 0:30 w normie (57%/53%), like ratio ~100% — ale krzywa retencji **bez plateau**: stały zjazd, bo narracja liniowo domyka temat („widz dostaje odpowiedź na tytuł i wychodzi"). Recepta C.2: **nowa pętla/obietnica co ~60–90 s; zmienia się architektura obietnic, nie tożsamość** (format zostaje wolny i ciepły). Wszystkie 3 filmy <10 min; user chce 10–15 min.

**Z audytu łańcucha (2026-06-11):**
- Maszyna dowozi realnie **~75–80%**, nie „~99%" (slug 3: user dotknął 62% zdań, ciął −18%, przepisał 100% zdań dwóch ostatnich sekcji w ~54 min).
- Fixer: 51/51 wdrożeń, zero samowoli — ale klauzula „pomiń gorszą" to **martwa litera**; ~20–25% [Z] section-checkerów to false positives z **biasem anty-obrazowym** („przejmuje stery" oflagowane jako kalka; spłaszczanie żywych konkretów). [K] celne, arc-checker = najwyższa wartość/zgłoszenie.
- **Ściskacz tnie dokładnie to, czego chce diagnoza**: na slugu 4 wyciął „Jest w tym wszystkim jedna rzecz, o której mało kto wie…" (tryb 1 meta-tease) — wzorcowy otwieracz pętli; rozmontował też kulminację budowaną przez [A]2 (ślepota międzyetapowa).
- /hook jako osobna bramka empirycznie się nie broni: slug 3 i 4 = pieczątka no-op; slug 2 = rewrite 10/10 wklejony i **~90% przepisane ręcznie** przez usera; bramka nagrodziła tik, który user wyciął („No tak. Ja zawsze tak." 2/2 za Identification); tekst z `--apply` **omija wszystkie checkery**.
- Koszty: Step 5 (lead skleja korekty in-session) ≈ 45% kosztu przebiegu; doktryna „zwrot = treść pliku" podwaja wyjście subagentów (≈38%); razem ~połowa kosztu to mechanika w drogich kontekstach.
- Proces: brak deterministycznej walidacji; wynik maszyny nietrwały — `04_final.md` sluga 2 **nadpisany** treścią po redakcji podczas migracji (pełny dyff bezpowrotnie stracony; `outputs/` w `.gitignore`).

## Summary / key decisions

**D1 — Ściskacz (3d) SKASOWANY w całości.** User: „chcę usunąć ściskacza. będę sam poprawiał skrypt to wytnę to co mi nie pasuje." Kompresja przegadania wraca świadomie do docx-passa usera. Kasacja (git trzyma historię — precedens lean-redesign): `workflows/pipeline/03d_compressor.md`, `.claude/agents/draft-compressor.md`, Step 6.5 w `draft.md`, artefakt `04_final_presqueeze.md`. Sukcesja funkcji: tease-killing — problem znika wraz z agentem (re-hooki bezpieczne z konstrukcji); backstop doktryny „badania pokazują"/cyfry — przejmuje **walidator deterministyczny** (D5, tylko zgłasza, user tnie); ogólne odchudzanie — user. `04_final.md` = wyjście fixera.

**D2 — Retencja: pisarz + arc-checker (bez nowego agenta).**
- **Pisarz** (`03a_writer.md`): nowa zasada strukturalna „**Architektura obietnic**" (~3 zdania): pełnej odpowiedzi na pytanie tytułu nie oddawaj przed zamknięciem — odsłaniaj warstwami; każda sekcja, zanim domknie swoją myśl, otwiera następne pytanie (zapowiedź odwrócenia / paradoks / niedokończona scena — środki różne); zamknięcie domyka wszystkie otwarte pętle. **Celowo bez fraz-szablonów** (doktryna anty-kalibracyjna zostaje — „ale jest w tym coś dziwniejszego" nie może stać się tikiem co skryptu). Kadencja 60–90 s wychodzi sama z przejść `##` (sekcja ≈ 60–90 s mówienia).
- **Arc-checker** (`03b_arc_checker.md`): nowa soczewka „**Pętle i obietnice**" — buduje **mapę pętli** (gdzie otwarta → gdzie domknięta; zapisana w `iter/arc.md`, pokazywana w raporcie `/draft`), flaguje `[A]`: dwie+ sekcje z rzędu domknięte „na płasko" (długi odcinek bez nowej obietnicy), przedwczesna pełna odpowiedź na tytuł, pętla otwarta i nigdy niedomknięta.
- **`voice_brief.md` NIETKNIĘTY** (pętle to struktura, nie głos; tożsamość bez zmian — dokładnie wg diagnozy) poza usunięciem nieaktualnej noty „ściskacz 3d i tak je tnie".

**D3 — /hook SCALONY w /draft (emerytura osobnej bramki).** „Wcześniejsza implementacja hooka": (a) esencja Tier 1 wchodzi do reguły 5 pisarza (pierwsze ~37 słów = konkret/scena/pytanie, w którym człowiek się rozpoznaje, zero rozbiegu) — prewencja u źródła; (b) zimną ocenę otwarcia robi **arc-checker** (otwarcie = pierwsza pętla architektury obietnic; słabe → `[A]` → fixer → poprawka przechodzi normalną, sprawdzaną ścieżką — domyka to dziurę „splice omija checkery"); (c) eksport `docx/script.docx` przenosi się na koniec `/draft` (mechaniczny bookend, Layer 3). Na emeryturę: `.claude/commands/hook.md`, `tools/pipeline/agent4_hook.py` (po wyjęciu logiki eksportu docx), `workflows/pipeline/04_hook.md`, skill `.claude/skills/score-hook`; artefakt `04_final.bak.md` przestaje powstawać. `/package`: warunek „po /hook" → „po /draft". **Zabezpieczenie:** jeśli retencja @ 0:30 na filmach 4–5 spadnie poniżej ~55%, bramkę przywracamy z gita. (Nadpisuje „Nie ruszać: hooki" z diagnozy — decyzja usera w tym brainstormie, z pełnym obrazem dowodów.)

**D4 — Długość: filmy 10–15 min → target pisarza 1500–2200 słów.** Matematyka: tempo czytania usera ~118–132 wpm (~125 śr., zmierzone z filmów 2–3), cięcie docx ~16% → 1500 słów ⇒ ~10 min filmu, 2200 ⇒ ~15 min. Zmiany: linia długości w `03a_writer.md` („Długość: 1500–2200 słów; cel: film 10–15 minut po redakcji docx", nagłówek „~8–11 minut" → odpowiednio); norma sekcji w `draft.md` „zwykle 6–8" → „**zwykle 9–13**" (kadencja 60–90 s przy dłuższym tekście). Konsekwencja przyjęta świadomie: dłuższy film przy płaskiej architekturze = gorsza retencja — **D2 (pętle) jest warunkiem koniecznym D4**, idą razem. Downstream (poza zakresem, odnotowane): ~40–60% więcej obrazów (Agenci 5/6, kredyty renderu) i dłuższy montaż na film.

**D5 — Poprawki z audytu (bundlowane — te same pliki, jeden cutover):**
- **Filtr FP:** `03b_section_checker.md` — linia anty-spłaszczeniowa („rodzimy idiom i żywy konkret ≠ kalka; flagujesz to, czego Polak by NIE POWIEDZIAŁ, nie to, co «pisane»") + reguła „najnaturalniejszy wariant pierwszy". `03c_fixer.md` — **aktywacja klauzuli pominięcia**: jawny krok osądu per [Z] (propozycja lepsza od oryginału?), pominięcia logowane do `iter/fixer_skips.md` (raport pokazuje licznik).
- **Redaktor brzegów:** arc-checker — punkt „**wykonanie zamknięcia**" (ozdobny/przegadany close → `[A]`; dotąd nikt nie oceniał ornamentu ostatnich beatów — slug 3: 0/17 zdań finału przeżyło redakcję).
- **`tools/pipeline/draft_merge.py`** (NOWY, Layer 3): scala `iter/arc.md` + `iter/sek_NN.md` → `03b_corrections.md` deterministycznie (kolejność: [A] → sekcje wg dokumentu; skip „Brak zgłoszeń"; licznik tagów). Zastępuje Step 5 leada (≈45% kosztu przebiegu, źródło zdublowanych nagłówków).
- **Krótkie zwroty subagentów:** kontrakt „zwrot = ścieżka + liczba słów/zgłoszeń + 1 zdanie" zamiast pełnej treści pliku (−~38% proxy; lead i tak czyta z dysku). Zmiana w briefach `draft.md` + twardych regułach definicji `draft-{writer,section-checker,arc-checker,fixer}.md`.
- **Snapshot:** po fixerze kopia `md/04_final_machine.md` — **nietykalna** (zakaz nadpisywania, także w migracjach; naprawia klasę utraty danych ze sluga 2; podstawa pętli pomiarowej).
- **`tools/pipeline/draft_check.py`** (NOWY, Layer 3): walidator + eksport. Sprawdza: wszystkie sekcje `## ` draftu przetrwały fixera; zero „badania pokazują/potwierdzają", cyfr/decymali/procentów w narracji; widełki 1500–2200 słów; plik kompletny (niepusty, nie urwany); brak artefaktów `[Z]/[K]/[A]`. Wynik w raporcie `/draft` (czerwone = user decyduje, nic nie zmienia sam). `--export`: `04_final.md` → `docx/script.docx` (logika wyjęta z `agent4_hook.py`).
- **Porządki:** nagłówek `03b_section_checker.md` „(zimny subagent Opus)" → Sonnet; `CLAUDE.md` — „~99%" → uczciwe ~75–80%, tabela Agent Chain (3d i 4 out, walidator in), Quick Reference, destylat głosu bez wzmianek o ściskaczu, `/package` po `/draft`.
- **Pętla pomiarowa (opcjonalna, rekomendowana):** `tools/dev/draft_ceiling_report.py` — po redakcji usera diff `04_final_machine.md` vs `script_corrected` → % zdań dotkniętych, cut-rate, trend per slug.

**D6 — Nowy kształt łańcucha (Gen 5):**
```
/draft <slug>:
  pisarz (Opus, zimny)                          → md/03a_draft.md  [zamrożony]
  ensemble równolegle (zimne):
    section-checker ×N (Sonnet, ~9–13)          → md/iter/sek_NN.md
    arc-checker (Opus; + pętle/otwarcie/close)  → md/iter/arc.md (+ mapa pętli)
  draft_merge.py (skrypt)                       → md/03b_corrections.md
  fixer (Opus, zimny; klauzula pominięcia żywa) → md/04_final.md + md/iter/fixer_skips.md
  kopia (skrypt)                                → md/04_final_machine.md  [nietykalny]
  draft_check.py --export (skrypt)              → werdykt walidacji + docx/script.docx
  raport leada: słowa, tagi [Z]/[K]/[A], liczba pominięć fixera, MAPA PĘTLI, werdykt walidatora
po /draft: user docx-pass (script_corrected.docx) → nagranie. /hook nie istnieje; /package po /draft.
```

## Plan plików

- **Zmieniane:** `workflows/pipeline/03a_writer.md` (architektura obietnic, Tier-1 w regule 5, długość 1500–2200), `03b_section_checker.md` (anty-spłaszczenie, wariant-pierwszy, nagłówek Sonnet), `03b_arc_checker.md` (pętle+mapa, otwarcie, wykonanie zamknięcia), `03c_fixer.md` (aktywna klauzula + log pominięć), `.claude/commands/draft.md` (Step 5→skrypt, Step 6.5 out, walidator+eksport+snapshot, raport, krótkie zwroty, norma sekcji 9–13), `.claude/agents/draft-{writer,section-checker,arc-checker,fixer}.md` (kontrakt zwrotu), `CLAUDE.md` (sync j.w.), `workflows/guides/voice_brief.md` (tylko nota v2.1), `workflows/pipeline/07_package.md` + skille routujące wzmiankujące /hook (`score-hook` out, `package-thumbnail`/`write-script` — sync warunków).
- **Nowe:** `tools/pipeline/draft_merge.py`, `tools/pipeline/draft_check.py`, opcjonalnie `tools/dev/draft_ceiling_report.py`.
- **Kasowane:** `workflows/pipeline/03d_compressor.md`, `.claude/agents/draft-compressor.md`, `.claude/commands/hook.md`, `workflows/pipeline/04_hook.md`, `tools/pipeline/agent4_hook.py` (po przeniesieniu eksportu docx), `.claude/skills/score-hook/`.

## Walidacja rolloutu (slug 5 = pierwszy przebieg Gen 5)

1. Raport `/draft`: mapa pętli obecna i sensowna; `fixer_skips` niepusty (klauzula żyje); walidator zielony; długość w widełkach.
2. Docx-pass usera mierzalnie lżejszy niż slug 3 (62% zdań / −18%): `draft_ceiling_report.py`.
3. Film po publikacji (kryteria z diagnozy D): krzywa z plateau po 1. minucie; retencja śr. > 35–40%; **0:30 ≥ ~55%** — spadek poniżej = przywrócenie bramki /hook z gita.

## Poza zakresem (nietknięte)

Research 0/1/2, `/visuals`, `/publish`, `/package` (poza warunkiem wejścia), align, Agenci 6/6b/6c, poprawki produkcyjne B1–B5 z diagnozy (audio LUFS, ostatnia mila publish, napisy, QA wizualne, preset eksportu — osobna checklista operacyjna), `en-pipeline-v1`.

## Q&A log

### Q1 — Zakres planu
- Asked: tylko retencja (C.2) / retencja+audyt / cała diagnoza z B1–B5?
- Captured: **retencja + poprawki z audytu** — te same pliki, jeden cutover; B1–B5 poza zakresem.

### Q2 — Mechanizm curiosity loops
- Asked: pisarz+arc-checker / nowy loop-checker / rozszerzony /hook (Tier 3)?
- Captured: **pisarz + arc-checker** — prewencja u źródła + zimna detekcja, zero nowych agentów.

### Q3 — Konflikt ściskacz ↔ re-hooki
- Asked: redefinicja trybu 1 + ochrona [A] / sama redefinicja / sama ochrona?
- Captured: **PIVOT — ściskacz usunięty w całości.** „chcę usunąć ściskacza. będę sam poprawiał skrypt to wytnę to co mi nie pasuje." Konflikt znika z konstrukcji; backstop doktryny przejmuje walidator (D1/D5).

### Q4 — Uproszczenie systemu + los /hook
- Asked (user): czy upraszczanie ma sens; czy agent na hook jest potrzebny / da się wcześniej?
- Captured: pisarz/ensemble/fixer mają twarde dowody wartości — nie ruszać; **jedyny zasadny kandydat = /hook → SCALIĆ w /draft** (Tier-1 do pisarza, ocena otwarcia w arc-checkerze, docx na koniec /draft, komenda+skill na emeryturę, safeguard 0:30 ≥ ~55%).
- Flags: nadpisuje „Nie ruszać: hooki" z diagnozy — świadomie, decyzją usera.

### Dyrektywa — długość filmów
- Captured: **10–15 minut** (wszystkie dotychczasowe <10). → target pisarza 1500–2200 słów (D4).

## Open flags (pending)

- Walidacja całości na slugu 5 (kryteria wyżej); w razie spadku 0:30 — przywrócenie /hook.
- `draft_ceiling_report.py` — opcjonalny; decyzja przy implementacji.
- Nieanalizowany A/B `md/ab_opus/` na slugu 4 — może odpowiedzieć, czy checkery na Opusie mają niższy FP-rate niż Sonnet (kontekst dla filtra FP, nie blokuje wdrożenia).
- Commit całości na słowo usera (branch `refactor/lean-draft-cutover` ma też niezacommitowany poprzedni refactor).
