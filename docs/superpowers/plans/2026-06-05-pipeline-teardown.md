# Pipeline Teardown — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, recommended here) or superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zbudować jeden dokument `docs/pipeline_teardown.md` — pełny, krytyczny teardown całego pipeline'u SENSUM (jak działa + co kod naprawdę robi + zależności/koszty + werdykt co wyciąć/uprościć).

**Architecture:** Dokument budowany etapami: najpierw część globalna (mapa/koszty/zależności) + JEDNA sekcja-wzorzec (Agent 8) → checkpoint akceptacji formatu → masowa produkcja pozostałych sekcji per agent wg zaakceptowanego szablonu → część decyzyjna (rejestr werdyktów + dług/dryf) → self-review całości. Kod analizowany przez context-mode (`ast` w sandboxie), żeby ~7 tys. linii nie weszło do kontekstu sesji.

**Tech Stack:** Markdown (deliverable); Python `ast` przez context-mode (`ctx_execute_file`/`ctx_batch_execute`) do strukturalnej analizy kodu; `Read` punktowo na subtelną logikę; `Grep`/`Glob` do cross-checków.

**Adaptacje względem domyślnego szablonu writing-plans:**
- Deliverable to dokument, nie kod → **„bramki weryfikacji"** zastępują testy pytest (konkretne sprawdzenia z oczekiwanym wynikiem).
- **Git odłożony** na życzenie właściciela („zostawmy gita na później"). Trwałym checkpointem każdej sekcji jest zapis pliku (`Write`/`Edit`). Pojedynczy, opcjonalny commit na końcu (Task 20) — tylko jeśli właściciel zechce.

**Decyzje domykające otwarte pytania spec §14:**
- Agent-wzorzec = **Agent 8 (publish)** — największy (835 linii), najwięcej trybów; jeśli szablon udźwignie 8, udźwignie każdego.
- Guides (`style_guide.md`, `narrative_architectures.md`, `voice_corpus.md`, `style_guide_images.md`) = **opis jako kontekst**, nie audytowane werdyktem jak kod (krótki akapit w §4).

---

## Pliki: docelowy i źródłowe

**Tworzony:**
- Create: `docs/pipeline_teardown.md` — jedyny deliverable.
- Plan: `docs/superpowers/plans/2026-06-05-pipeline-teardown.md` (ten plik).

**Analizowane (read-only — NIE modyfikujemy):**
- Core: `tools/pipeline/agent0_materials.py`, `agent1_research.py`, `agent2_verify.py`, `agent3.py`, `agent3b_revisor.py`, `agent3c_reviewer.py`, `agent4_hook.py`, `agent5_visuals.py`, `agent6_images.py`, `agent6b_image_qa.py`, `agent7_thumbnails.py`, `agent8_publish.py`
- Satelity: `tools/pipeline/agent_align.py`; `tools/intelligence/{intelligence,analyzer,collector,db,slide_builder,vision}.py`
- Współdzielone: `tools/utils.py`, `tools/research_sources.py`, `tools/dev/add_grain.py`
- Workflowy: `workflows/pipeline/*.md` (22 pliki); komendy `.claude/commands/*.md` (8); agenci teams `.claude/agents/*`
- Referencje: `CLAUDE.md`, `docs/architecture_review.md`, `docs/agent_teams_reference.md`, `docs/reversibility.md`

---

## Konwencje wykonania (współdzielone)

### A. SECTION RECIPE — procedura sekcji per agent (każdy agent w Etapie B stosuje JĄ)

Każda sekcja agenta to nagłówek `## Agent N — <Nazwa>` + 7 pól szablonu (spec §7). Procedura:

**R1. Analiza strukturalna kodu (context-mode, bez wczytywania surowca):**
`ctx_execute_file` na pliku `.py` agenta, kod `ast` wypisuje strukturę:
```python
import ast, sys
src = open(PATH, encoding="utf-8").read()
tree = ast.parse(src)
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        args = [a.arg for a in node.args.args]
        doc = (ast.get_docstring(node) or "").splitlines()[:1]
        # zlicz gałęzie decyzyjne w funkcji
        branches = sum(isinstance(n, (ast.If, ast.For, ast.While, ast.Try)) for n in ast.walk(node))
        # zewnętrzne wywołania (nazwy) — sygnał kosztu/IO/API
        calls = sorted({n.func.attr for n in ast.walk(node)
                        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)})
        print(f"def {node.name}({', '.join(args)}) | branches={branches} | {doc} | calls={calls[:12]}")
```
Wynik: lista funkcji + liczba gałęzi + wywołania (sygnały API/IO/subprocess). Do kontekstu wchodzi tylko ta lista, nie kod.

**R2. Punktowy `Read`:** tylko funkcje, które w R1 mają dużo gałęzi lub niejasne wywołania — czytaj te fragmenty, żeby opisać logikę wiernie.

**R3. SOP vs kod:** zestaw zachowanie z kodu z odpowiednim workflow `.md` (i wpisem w `CLAUDE.md`). Wypisz konkretne rozjazdy (drift) albo „zgodne".

**R4. Draft sekcji** — 7 pól: Rola / Wejście→wyjście / Komenda+flagi / Przewodnik po kodzie (logika w pełni, boilerplate jednym zdaniem) / SOP vs kod / Koszt i zależności / Werdykt (`ZOSTAW`|`UPROŚĆ`|`WYTNIJ` + uzasadnienie wg rubryki 5-kryterialnej: używalność·koszt·utrzymanie·redundancja·dryf).

**R5. Zapis:** `Edit` (append) sekcji do `docs/pipeline_teardown.md`.

### B. BRAMKA WERYFIKACJI sekcji (zastępuje test — uruchom po R5)

Sekcja przechodzi, gdy WSZYSTKO prawda:
1. Obecne wszystkie 7 pól szablonu (Grep nagłówków pól w sekcji).
2. Każda funkcja z listy R1 jest wymieniona w „Przewodniku po kodzie" (porównaj nazwy 1:1).
3. Każde twierdzenie o API/koszcie ma pokrycie w `calls` z R1 (żaden koszt nie zmyślony).
4. Pole „Wejście→wyjście" zgadza się z tabelą zależności (§3) — interfejsy plikowe się spinają.
5. Werdykt obecny i uzasadniony wg 5 kryteriów rubryki.

Sposób sprawdzenia 1–2 (przykład):
```
Grep -n "Werdykt|Przewodnik po kodzie|Wejście" docs/pipeline_teardown.md   # pola obecne
```
+ wzrokowe porównanie listy funkcji R1 z treścią sekcji. Jeśli któraś funkcja niesie logikę a jej brak → uzupełnij i ponów bramkę.

### C. Polityka git

Domyślnie **bez commitów per task** (życzenie właściciela). Zapis pliku = checkpoint. Opcjonalny pojedynczy commit dopiero w Task 20.

### D. Język i konwencja

Dokument PL; identyfikatory/ścieżki/flagi w oryginale. Nagłówki sekcji jednolite: `## Agent N — <Nazwa>` (satelity: `## Satelita — <Nazwa>`).

---

## Etap A — Szkielet + wzorzec

### Task 1: Indeks źródeł w context-mode + globalne fakty strukturalne

**Files:**
- Analyze (read-only): wszystkie pliki z sekcji „Analizowane" powyżej.
- Create: (nic — to prep; wynik trafia do KB context-mode i do notatek roboczych w kontekście)

- [ ] **Step 1: Zindeksuj kod i workflowy do context-mode**

Wywołaj `ctx_index` (lub `ctx_batch_execute` z `ls`-ami) na `tools/` i `workflows/pipeline/`, żeby późniejsze cross-cutting pytania (gdzie używane, dryf) były tanie.

- [ ] **Step 2: Zbierz globalne fakty: I/O każdego agenta**

`ctx_execute_file`/`ctx_batch_execute` — dla każdego `.py` wypisz: ścieżki czytane (`open(...read)`, `read_*`) i pisane (`open(...write)`, `to_docx`, `savefig`, `.save(`). Kod `ast`/regex zwraca pary (agent → reads[], writes[]).
Expected: tabela „kto czyta/pisze co" dla 13+ plików — surowiec do §3.

- [ ] **Step 3: Zbierz sygnały kosztu/modelu**

Grep po całym `tools/` za: `vertexai`, `generate_content`, `GenerativeModel`, `gemini-`, `faster_whisper`, `whisper`, `subprocess`, `requests`/`httpx`, `eutils`/`europepmc`. Zmapuj agent → (model/usługa, czy płatne).
Expected: surowiec do tabeli kosztów §2 + warstwy §4 (in-session vs Gemini vs lokalne).

- [ ] **Bramka Task 1:** Masz (a) zaindeksowane KB, (b) tabelę reads/writes dla wszystkich plików, (c) mapę kosztów/usług. Bez tego nie ruszamy globalnej części.

---

### Task 2: Szkielet doca + część globalna (§1–§4)

**Files:**
- Create: `docs/pipeline_teardown.md`

- [ ] **Step 1: Zapisz szkielet i nagłówek**

`Write` pliku z nagłówkiem (tytuł, „Stan na: 2026-06-05", jednozdaniowy cel, spis treści) + pustymi nagłówkami sekcji §1–§7 i placeholderem listy agentów. Dodaj na górze blok „Legenda werdyktów" (`ZOSTAW`/`UPROŚĆ`/`WYTNIJ`) i „Rubryka (5 kryteriów)".

- [ ] **Step 2: §1 Mapa pipeline'u**

Diagram przepływu (ASCII) od `topic` przez 0/1/2 → 3 → 4 → 5∥8 → 6/6b → 7 → align; oznacz core/satelita/legacy. Źródło: Task 1 + `CLAUDE.md` „Agent Chain".

- [ ] **Step 3: §2 Tabela kosztów** — z danych Task 1 Step 3 (agent · model/usługa · in-session/Gemini/lokalne · płatne? · manual/auto).

- [ ] **Step 4: §3 Tabela zależności** — z danych Task 1 Step 2 (agent · czyta · pisze). To kontrakt, do którego bramki sekcji (B.4) będą się odwoływać.

- [ ] **Step 5: §4 Warstwy systemu** — core (0–8) vs satelity (align/intelligence/teams) vs legacy (`--api`); + krótki akapit o guides jako kontekście.

- [ ] **Bramka Task 2:** §1–§4 wypełnione realnymi danymi (nie placeholderami). Sprawdź: każdy agent z inwentarza występuje w tabeli kosztów (§2) i zależności (§3).
```
Grep -n "agent0|agent1|agent2|agent3|agent4|agent5|agent6|agent7|agent8|align|intelligence" docs/pipeline_teardown.md
```
Expected: każdy obecny ≥1×.

---

### Task 3: Sekcja-WZORZEC — Agent 8 (publish)

**Files:**
- Modify: `docs/pipeline_teardown.md` (append `## Agent 8 — Publish`)
- Analyze: `tools/pipeline/agent8_publish.py` (835), `workflows/pipeline/08_publish.md` (235), `08d_native_copy.md` (175), `.claude/commands/publish.md`, `publish-team.md`

- [ ] **Step 1–5: Zastosuj SECTION RECIPE (R1–R5)** dla Agenta 8.
  Specyfika do wychwycenia: 9 kroków in-session; bookendy `--extract`/`--signals`/`--finalize`; `_load_niche_signals()`; kontrakty „locked output" (Tag #1, 3 hashtagi, 5 zdań, `[Q1]–[Q4]`); ścieżka legacy `--api`. Werdykt całości + ewentualne „UPROŚĆ" pod-elementy.

- [ ] **Bramka Task 3:** Uruchom BRAMKĘ WERYFIKACJI (sekcja B, pkt 1–5) dla Agenta 8.

- [ ] **CHECKPOINT 1 — akceptacja wzorca (właściciel):**
  Pokaż właścicielowi część globalną (§1–§4) + sekcję Agent 8. Zapytaj wprost: „Czy ten format/głębia/długość sekcji są OK, zanim wyprodukuję pozostałe 13?". **Nie ruszaj Etapu B bez zielonego światła.** Jeśli poprawki → nanieś na wzorzec i zaktualizuj SECTION RECIPE, potem dalej.

---

## Etap B — Sekcje per agent (po akceptacji wzorca)

> Każdy task: zastosuj SECTION RECIPE (R1–R5) + BRAMKĘ WERYFIKACJI (B). Poniżej tylko specyfika i pliki.

### Task 4: Agent 0 — Materials
**Files:** Analyze `tools/pipeline/agent0_materials.py` (132), `workflows/pipeline/00_materials.md`, `00_materials_prompt.md`. Modify doc (append).
- [ ] Recipe + bramka. Specyfika: opcjonalny; wejście PDF+topic; Gemini 3.1 Pro; `_load_prompt()`. Werdykt: czy realnie używany.

### Task 5: Agent 1 — Research
**Files:** Analyze `agent1_research.py` (273), `01_research.md`, `01_research_prompt.md`, `tools/research_sources.py` (216, jeśli wołany stąd). Modify doc.
- [ ] Recipe + bramka. Specyfika: PubMed + Europe PMC (`research_sources.py`) + Gemini; „PubMed zero = OK". Werdykt + redundancja providerów.

### Task 6: Agent 2 — Verify
**Files:** Analyze `agent2_verify.py` (336), `02_verify.md`, `02_verify_prompt.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: weryfikacja `01→02`; Gemini 3.1 Pro.

### Task 7: Agent 3 — Script chain
**Files:** Analyze `agent3.py` (151), `agent3b_revisor.py` (253), `agent3c_reviewer.py` (202); `03_script.md`, `03_architecture_select.md`, `03a_drafter.md`, `03b_revisor.md`, `03c_reviewer.md`; `.claude/commands/draft.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: selektor architektury (Step 1.6); pętla 3b↔3c (max 5, FLAG-at-max); in-session vs legacy `--api`; parser contract (`## VERDICT` → PASS/FLAG). Co robi `agent3.py` naprawdę vs in-session `/draft` (kandydat na dryf/legacy).

### Task 8: Agent 4 — Hook gate
**Files:** Analyze `agent4_hook.py` (544), `04_hook.md`; `.claude/commands/hook.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: scoring Tier1/Tier2; `--apply` splice; backup `.bak.md`; eksport `docx/script.docx`.

### Task 9: Agent 5 — Visuals
**Files:** Analyze `agent5_visuals.py` (570), `05_visuals.md`; `.claude/commands/visuals.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: `--expand` (CHARACTER_DESCRIPTION+STYLE_SUFFIX), `--extract` (docx→md), pliki fraz.

### Task 10: Agent 6 — Images
**Files:** Analyze `agent6_images.py` (484), `06_images.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: Gemini 3 Pro Image, `location="global"`, `--indices`, `ImageOps.pad()`, `_enforce_background_color`. Manual (koszt).

### Task 11: Agent 6b — Image QA
**Files:** Analyze `agent6b_image_qa.py` (334), `06b_image_qa.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: Gemini 2.5 Flash; `06_qa.md`; `--retry`; nigdy nie kasuje.

### Task 12: Agent 7 — Package / Thumbnails (UWAGA: dryf)
**Files:** Analyze `agent7_thumbnails.py` (216), `07_package.md` (89), `07_thumbnails.md` (57); `.claude/commands/package.md`, `thumbnails.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: **dryf nazewnictwa** — `/package` vs `/thumbnails`, dwa SOP-y, jeden skrypt. To flagowy przypadek do §7 (dług). Werdykt powinien wskazać kierunek sprzątania.

### Task 13: Satelita — Align
**Files:** Analyze `agent_align.py` (333), `align.md`. Modify doc.
- [ ] Recipe + bramka. Specyfika: faster-whisper lokalnie (darmowe); wejście `voiceover.wav`+frazy+docx; wyjście SRT/FCPXML/preview. Werdykt: oszczędność godzin vs złożoność.

### Task 14: Satelita — Intelligence (moduł 6 plików)
**Files:** Analyze `tools/intelligence/{intelligence,analyzer,collector,db,slide_builder,vision}.py`, `intelligence.md`. Modify doc.
- [ ] Recipe (R1 dla każdego z 6 plików) + bramka. Jeden werdykt modułu + noty per plik. Specyfika: zasila `outputs/intelligence/{week}_tag_signals.md` czytane przez Agent 8; `PROJECT_ROOT` (3 poziomy); `slide_builder.py` (595) — czy używany? Werdykt: realna używalność (kandydat z pytania właściciela).

### Task 15: Satelita — Agent Teams
**Files:** Analyze `.claude/agents/*`, `docs/agent_teams_reference.md`, `draft-team.md`, `publish-team.md`, `03d_native_ear.md`, `08d_native_copy.md`. Modify doc.
- [ ] Recipe (dostosowany — to konfiguracje/prompty, nie `.py`) + bramka. Specyfika: opt-in, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, jeden team naraz, koszt (dodatkowe konteksty Opus). Werdykt: wartość vs koszt/komplikacja.

### Task 16: Współdzielone — utils / research_sources / add_grain
**Files:** Analyze `tools/utils.py` (453), `tools/research_sources.py` (216, jeśli nieopisany w Task 5), `tools/dev/add_grain.py`. Modify doc.
- [ ] Recipe (R1) + bramka. Specyfika: `utils.py` — co eksportuje, kto importuje (Grep `from utils`/`import utils`); `STYLE_SUFFIX`, `_enforce_background_color`. `add_grain.py` — post-processing ziarna. Werdykt per plik (raczej ZOSTAW; szukaj martwego kodu).

- [ ] **Bramka Etapu B:** Każdy agent z inwentarza (§5 spec) ma sekcję z kompletem 7 pól i werdyktem.
```
Grep -c "## Agent|## Satelita|## Współdzielone" docs/pipeline_teardown.md
```
Expected: liczba sekcji = liczba pozycji inwentarza (14). Braki → dopisz.

---

## Etap C — Część decyzyjna

### Task 17: §6 Zbiorczy rejestr werdyktów

**Files:** Modify `docs/pipeline_teardown.md` (append §6).

- [ ] **Step 1: Zbierz wszystkie werdykty**
```
Grep -n "Werdykt" docs/pipeline_teardown.md
```
Wyciągnij dla każdego: agent, werdykt, jednozdaniowe uzasadnienie, szacowany zysk (linie/koszt/złożoność).

- [ ] **Step 2: Zbuduj tabelę** posortowaną: najpierw `WYTNIJ`, potem `UPROŚĆ`, na końcu `ZOSTAW`; w grupie wg zysku malejąco. Kolumny: Komponent · Werdykt · Zysk · Co zrobić · Co sprawdzić przed cięciem.

- [ ] **Bramka Task 17:** Liczba wierszy rejestru = liczba sekcji agentów (każdy ma dokładnie jeden wpis). Cross-check liczby z Bramką Etapu B.

### Task 18: §7 Dług i dryf

**Files:** Modify `docs/pipeline_teardown.md` (append §7).

- [ ] **Step 1:** Zbierz wszystkie „SOP vs kod: dryf" z sekcji + znane przekrojowe (thumbnails→package, legacy `--api` w 6 plikach). Lista: rozjazd · gdzie · proponowane sprzątanie.
- [ ] **Bramka Task 18:** Każdy dryf wykryty w sekcjach (Grep „dryf"/„rozjazd") jest w §7.

---

## Etap D — Domknięcie

### Task 19: Self-review całości vs spec (kryteria sukcesu §12)

**Files:** Read `docs/pipeline_teardown.md`, `docs/superpowers/specs/2026-06-05-pipeline-teardown-design.md`.

- [ ] **Step 1: Pokrycie spec** — przejdź kryteria sukcesu spec §12: (a) każdy agent 7 pól, (b) każdy werdykt, (c) mapa+koszty+zależności, (d) rejestr posortowany, (e) twierdzenia o kodzie zweryfikowane. Wypisz luki.
- [ ] **Step 2: Skan placeholderów** — Grep `TODO|TBD|placeholder|XXX|\?\?\?` w docu; wyczyść.
- [ ] **Step 3: Spójność** — nazwy funkcji/flag użyte w sekcjach zgodne z R1; nagłówki jednolite.
- [ ] **Step 4: Napraw luki inline.** Jeśli brak sekcji/pola/werdyktu → uzupełnij (wróć do właściwego recipe).
- [ ] **Bramka Task 19:** Wszystkie kryteria §12 spełnione; zero placeholderów; spójne nazwy.

### Task 20 (opcjonalny): Commit do gita

**Tylko jeśli właściciel zechce** (domyślnie pomijamy).
- [ ] Zapytaj: „Zapisać teardown do historii gita?". Jeśli tak — celowany add tylko nowych plików doca/spec/plan:
```bash
git add docs/pipeline_teardown.md docs/superpowers/specs/2026-06-05-pipeline-teardown-design.md docs/superpowers/plans/2026-06-05-pipeline-teardown.md
git commit -m "docs: pipeline teardown — pełny audyt + werdykty"
```

---

## Self-Review planu (wykonane przy pisaniu)

- **Pokrycie spec:** §1–§4 → Task 2; per-agent szablon (spec §7) → SECTION RECIPE + Tasks 3–16; rubryka (spec §8) → R4 + bramka B.5; rejestr werdyktów (spec §6) → Task 17; dług/dryf (spec §7) → Task 18; staging template-first (spec §10) → Etapy A/B + CHECKPOINT 1; context-mode (spec §11) → R1; kryteria sukcesu (spec §12) → Task 19; inwentarz (spec §5) → „Pliki źródłowe" + Tasks 4–16. **Brak luk.**
- **Placeholdery:** brak „TBD/TODO/wpisz później"; treść recipe i bramek konkretna (kod `ast`, komendy Grep, oczekiwane wyniki).
- **Spójność:** nazwy „SECTION RECIPE (R1–R5)", „BRAMKA WERYFIKACJI (B1–B5)", nagłówki `## Agent N —` używane jednolicie w całym planie; werdykty `ZOSTAW/UPROŚĆ/WYTNIJ` spójne ze spec.
