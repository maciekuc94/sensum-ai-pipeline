# Pipeline Teardown — SENSUM (pełny audyt)

> **Stan na:** 2026-06-05 · **Zakres:** cała maszyneria produkcyjna (agenci 0–8 + satelity + współdzielone). **Read-only** — to analiza decyzyjna, nie zmiana kodu.
> **Cel:** zrozumieć end-to-end jak pipeline działa *naprawdę* (kod, nie tylko SOP), zmapować zależności i koszty, i dla każdego komponentu wydać werdykt **co zostawić / uprościć / wyciąć**.

## Metodyka

- **Kod czytany z hosta** (`ast` + regex), do tego punktowy wgląd w subtelną logikę. Twierdzenia o kodzie są weryfikowane w kodzie, nie przepisywane z SOP.
- **LOC = liczba znaków nowej linii + 1.** Uwaga: wcześniejsze pomiary PowerShell (`Measure-Object -Line`) **zaniżały** o ~25–30% (dawały 835 dla `agent8_publish.py`); poprawna wartość to **1093**, zgodna z „~1,090" w `docs/architecture_review.md`. W całym dokumencie używam liczb `ast`.
- **„SOP vs kod"** w każdej sekcji jawnie zaznacza rozjazdy (dryf) między dokumentacją a implementacją.

## Legenda werdyktów

| Werdykt | Znaczenie |
|---|---|
| `ZOSTAW` | Wartość proporcjonalna do kosztu/złożoności. Nie ruszać. |
| `UPROŚĆ` | Wartościowy, ale przerośnięty lub zdryfowany — konkretna propozycja odchudzenia. |
| `WYTNIJ` | Kandydat do usunięcia — z uzasadnieniem i listą „co sprawdzić przed cięciem". |

## Rubryka (5 kryteriów werdyktu)

1. **Używalność** — czy realnie używane w produkcji.
2. **Koszt** — wydatek API / czas / tokeny.
3. **Utrzymanie** — linie, złożoność, liczba gałęzi.
4. **Redundancja** — czy nakłada się na inny komponent.
5. **Dryf** — czy dokumentacja zgadza się z kodem.

## Spis treści

- [§1 Mapa pipeline'u](#1-mapa-pipelineu)
- [§2 Tabela kosztów i modeli](#2-tabela-kosztów-i-modeli)
- [§3 Tabela zależności (deklarowany kontrakt)](#3-tabela-zależności-deklarowany-kontrakt)
- [§4 Warstwy systemu](#4-warstwy-systemu)
- [§5 Sekcje per agent](#5-sekcje-per-agent)
- [§6 Zbiorczy rejestr werdyktów](#6-zbiorczy-rejestr-werdyktów)
- [§7 Dług i dryf](#7-dług-i-dryf)

---

## §1 Mapa pipeline'u

Przepływ danych. `*` = plik modyfikowany w miejscu. **GATE** = brama jakości (stop przed dalej). **MANUAL** = nigdy automatycznie (koszt).

```
  Agent 0 (materials, OPCJONALNY)   PDF + topic ─► md/00_materials_insights.md
        │  (Gemini, wkład wiedzy — nie blokuje łańcucha)
        ▼
  topic ─► Agent 1 (research) ───────────────► md/01_research.md
                 (Gemini + PubMed + Europe PMC)        │
                                                        ▼
            Agent 2 (verify) ──────────────────► md/02_verified_research.md
                 (Gemini)                                │
                                                         ▼
   /draft ── Agent 3 (script chain) ─► 03_architecture.md, 03a/03b*/03c*, ─► md/04_final.md
                 (Opus in-session: selektor → 3a → pętla 3b↔3c)             │
                                                                            ▼
   /hook ─── Agent 4  ★GATE★ ─────────► 04_hook.md, 04_final.md*, docx/script.docx
                 (Opus in-session; --apply splice)                          │
                                                                            │  (po /hook: edycja w Wordzie → script_corrected.docx)
                        ┌───────────────────────────────────┬──────────────┘
                        ▼                                    ▼
   /visuals ─ Agent 5 ─► md/05_prompts.md         /publish ─ Agent 8 ─► md/08_publish.md (+docx)
                 (Opus in-session; --expand)             (Opus in-session; 9 kroków)
                        │                                    ▲
                        ▼                                    │ czyta: 02_verified_research.md
   Agent 6 (images) ★MANUAL★ ─► images/image_*.png          │        + script_corrected/script/04_final
                 (Gemini 3 Pro Image)                        │
                        │                            Intelligence (SATELITA, okresowy)
                        ▼                            web ─► outputs/intelligence/{week}_tag_signals.md ─┘
   Agent 6b (QA) ─► md/06_qa.md                              (Agent 8 czyta najnowszy sidecar)
                 (Gemini 2.5 Flash)

   /package ─ Agent 7 ★MANUAL★ ─► 07_prompts.md + thumbnails_no_grain/*.png
                 (Opus in-session koncepty + Gemini render; czyta 04_final + 08_publish)

   ── PO NAGRANIU (voiceover w Studio One → voiceover/voiceover.wav) ──
   Align (SATELITA, lokalny/darmowy) ── voiceover.wav + 05_phrases + script ─► edit/ (subtitles.srt, timeline.fcpxml, preview.html, alignment.json)
```

**Równoległość:** po Agencie 3 — Agent 5 ∥ Agent 8. Agent 6 zależy od 5. Agent 7 ∥ Agent 6.

---

## §2 Tabela kosztów i modeli

LOC = `ast`. „in-session" = Opus 4.8 w Claude Code, **bez API** (koszt = tokeny sesji). „Gemini" = płatne Vertex AI. „lokalne/web" = darmowe.

| Agent | Plik(i) `.py` (LOC) | Silnik / usługa | Płatność | Tryb |
|---|---|---|---|---|
| 0 materials | `agent0_materials.py` (177) | Gemini 3.1 Pro | Gemini API | opcjonalny |
| 1 research | `agent1_research.py` (334) + `research_sources.py` (267) | Gemini 3.1 Pro + PubMed + Europe PMC | Gemini API (płatne) + PubMed/EPMC (darmowe) | auto |
| 2 verify | `agent2_verify.py` (406) | Gemini 3.1 Pro | Gemini API | auto |
| 3 chain | `agent3.py` (179), `agent3b_revisor.py` (318), `agent3c_reviewer.py` (269) | Opus in-session (`/draft`); legacy `--api` → Gemini | in-session (legacy: Gemini) | auto (in-session) |
| 4 hook ★GATE★ | `agent4_hook.py` (675) | Opus in-session; `--apply` deterministyczny; legacy `--api` | in-session (legacy: Gemini) | auto (in-session) |
| 5 visuals | `agent5_visuals.py` (695) | Opus in-session; `--expand`/`--extract` deterministyczne | in-session (brak Gemini/`--api` w skrypcie — do weryfikacji §7) | auto (in-session) |
| 6 images ★MANUAL★ | `agent6_images.py` (580) | Gemini 3 Pro Image Preview | Gemini API | manual |
| 6b QA | `agent6b_image_qa.py` (395) | Gemini 2.5 Flash | Gemini API (tanie) | opcjonalny |
| 7 package ★MANUAL★ | `agent7_thumbnails.py` (263) | Opus in-session (koncepty) + Gemini 3 Pro Image (render) | in-session + Gemini API | manual |
| 8 publish | `agent8_publish.py` (1093) | Opus in-session; `--signals` web-scrape; legacy `--api` | in-session + web (darmowe); legacy: Gemini | auto (in-session) |
| Align | `agent_align.py` (375) | faster-whisper (lokalnie) | lokalne (darmowe) | po nagraniu |
| Intelligence | `intelligence.py` (263), `analyzer.py` (269), `collector.py` (228), `db.py` (144), `slide_builder.py` (733), `vision.py` (80) | Gemini (vision) + web-scrape + SQLite + matplotlib | Gemini API + web | okresowy |
| Teams (opt-in) | `.claude/agents/*` (konfiguracje) | dodatkowe konteksty Opus in-session | in-session (więcej tokenów) | opt-in |
| Współdzielone | `utils.py` (552), `add_grain.py` (50) | importowane przez agentów; `add_grain` = post-processing ziarna | — | biblioteka |

**Sygnał audytowy:** legacy `--api` (Gemini) wykryty w `agent3/3b/3c/4/8`. Ślad `anthropic`/`query_claude`/`ANTHROPIC_API` wykryty **tylko w `utils.py`** — mimo deklaracji „query_claude() usunięty" (→ §7).

---

## §3 Tabela zależności (deklarowany kontrakt)

Wg `CLAUDE.md` (Agent Chain) — **weryfikowane w sekcjach per agent**; rozjazdy trafiają do §7. Pliki są w `outputs/videos_pl/{slug}/`.

| Agent | Czyta | Pisze |
|---|---|---|
| 0 | PDF + `topic` | `md/00_materials_insights.md` |
| 1 | `topic` (string) | `md/01_research.md` |
| 2 | `md/01_research.md` | `md/02_verified_research.md` |
| 3 | `md/02_verified_research.md` | `md/03_architecture.md`, `md/03a_draft.md`, `md/03b_revised_iter*.md`, `md/03c_review_iter*.md`, `md/04_final.md` |
| 4 | `md/04_final.md` | `md/04_hook.md`, `md/04_final.md` (in place), `md/04_final.bak.md`, `docx/script.docx` |
| 5 | `md/04_final.md` lub `docx/script_corrected.docx` | `md/05_prompts.md` (+ `05_phrases` przez `--expand`) |
| 6 | `md/05_prompts.md` | `images/image_*.png` |
| 6b | `images/*.png` | `md/06_qa.md` |
| 7 | `md/04_final.md` + `md/08_publish.md` | `md/07_prompts.md`, `thumbnails_no_grain/thumbnail_0N.png` |
| 8 | `docx/script_corrected.docx` → `docx/script.docx` → `md/04_final.md` + `md/02_verified_research.md` (+ najnowszy `tag_signals.md`) | `md/08_publish.md`, `docx/08_publish.docx` |
| Align | `voiceover/voiceover.wav` + `md/05_phrases.md` + `script_corrected.docx`/`script.docx`/`04_final.md` | `edit/subtitles.srt`, `edit/timeline.fcpxml`, `edit/preview.html`, `edit/alignment.json` |
| Intelligence | web (autocomplete + nisza) | `outputs/intelligence/{week}_tag_signals.md` |

**Interfejsy = pliki `md/`/`docx/`.** Łańcuch jest luźno sprzężony przez pliki: każdy agent można uruchomić, gdy jego wejście istnieje (stąd równoległość 5 ∥ 8).

---

## §4 Warstwy systemu

**Core chain (0–8)** — główny tor produkcji jednego wideo. ~5 759 linii (z Align). Reżim: „No Claude API — wszystko in-session"; Gemini tylko do researchu (0/1/2), renderu obrazów (6, 7-render) i QA (6b).

**Satelity** (niezależne od pojedynczego wideo):
- **Align** (`agent_align.py`, 375) — po nagraniu; faster-whisper lokalnie; składa bundle do DaVinci. Darmowy.
- **Intelligence** (`tools/intelligence/`, ~1 717 linii w 6 plikach) — okresowy; zasila tagi Agenta 8 przez `{week}_tag_signals.md`. Zawiera `slide_builder.py` (733!) — największy pojedynczy plik satelity, do weryfikacji użycia.
- **Agent Teams** (`.claude/agents/*` + warianty `-team`) — opt-in; cold-context krytycy (3d/8d). Koszt: dodatkowe konteksty Opus.

**Legacy (`--api`)** — w `agent3/3b/3c/4/8` współistnieje stara ścieżka Gemini obok domyślnej in-session. Kandydat przekrojowy do oceny „zostaw jako fallback vs wytnij" (§7).

**Guides (kontekst, nie audytowane jak kod):** `style_guide.md`, `narrative_architectures.md`, `voice_corpus.md`, `style_guide_images.md` — to specyfikacje doktryny głosu/stylu czytane przez agentów skryptowych in-session. Opisane jako kontekst; nie dostają werdyktu `ZOSTAW/UPROŚĆ/WYTNIJ`.

---

## §5 Sekcje per agent

> Każda sekcja: Rola · Wejście→wyjście · Komenda+flagi · Przewodnik po kodzie · SOP vs kod · Koszt i zależności · Werdykt. Budowane etapami — najpierw wzorzec (Agent 8), reszta po akceptacji formatu.

### Agent 0 — Materials (opcjonalny)

**Rola.** Z dostarczonego PDF-a (książka/artykuł) + tematu wyciąga przez Gemini kluczowe insighty jako wkład wiedzy do researchu. Opcjonalny — nie blokuje łańcucha.

**Wejście → wyjście.** *Czyta:* ścieżkę PDF + `--topic`. *Pisze:* `md/00_materials_insights.md`.

**Komenda + flagi.** `python tools/pipeline/agent0_materials.py --topic "…" --pdf <plik>` (argparse w `main`).

**Przewodnik po kodzie** (5 funkcji): `_load_prompt()` (L27) wczytuje prompt z `00_materials_prompt.md`, zdejmując linie `#`/`<!--` (wzorzec `_load_prompt` współdzielony przez 0/1/2) · `extract_pdf_text()` (L43, br=4) PyPDF iteruje strony i skleja tekst · `query_gemini_extraction()` (L69) Gemini Client + `GenerateContentConfig` + `generate_content` (topic + tekst książki) · `build_output()` (L104) składa md z datą · `main()` (L123) argparse + walidacja + zapis.

**SOP vs kod.** Zgodne z `00_materials.md` (Gemini 3.1 Pro, opcjonalny wkład; research po angielsku).

**Koszt i zależności.** Gemini API (płatne). Brak wejść z innych agentów (źródłem jest PDF); wyjście to *opcjonalny* wkład do Agenta 1.

**Werdykt: `ZOSTAW` (warunkowo).** Mały (177 lin.), izolowany. *Używalność:* sensowny tylko gdy realnie podajesz materiał źródłowy — jeśli nigdy nie używasz PDF-wkładu, kandydat na `WYTNIJ`. *Co sprawdzić:* czy w ostatnich produkcjach `00_materials_insights.md` w ogóle powstaje.

### Agent 1 — Research

**Rola.** Z tematu buduje research po angielsku: Gemini z groundingiem Google Search + recenzowane źródła (PubMed + Europe PMC) → `01_research.md` z tabelą prac.

**Wejście → wyjście.** *Czyta:* `topic` (pozycyjny string). *Pisze:* `md/01_research.md`.

**Komenda + flagi.** `python tools/pipeline/agent1_research.py "<topic>"` (argparse).

**Przewodnik po kodzie** (10 funkcji): `_load_prompt()` (L30) jak w A0 · `query_gemini()` (L41, br=2) Gemini Client z **`Tool(GoogleSearch())`** (grounding!) + `generate_content` → tekst researchu · `_derive_subqueries()` (L89) + `_parse_query_list()` (L119, br=6) rozbijają temat na podzapytania do baz (parsują listę: JSON `loads` lub split linii) · `gather_research_papers()` (L144) woła `research_sources.gather_peer_reviewed()` · `_authors_str`/`_doi_link` (L158/166) formatują · `build_markdown()` (L172, br=9) + `_add_row()` (L230) składają md (tekst Gemini + tabela prac, dedup po DOI/tytule) · `main()` (L294).

**SOP vs kod.** Zgodne: „PubMed zero = OK" (EPMC leci równolegle); research po angielsku.

**Koszt i zależności.** Gemini API (płatne, z groundingiem) + PubMed/EPMC (darmowe, przez `research_sources.py`, 267 lin.). Wyjście → Agent 2.

**Werdykt: `ZOSTAW`.** Rdzeń wiarygodności kanału. *Redundancja:* dwa źródła recenzowane (PubMed+EPMC) to celowy fallback, nie do cięcia. *Uwaga kosztowa:* grounding Google Search w `query_gemini` to realny koszt/zmienność — dobrze wiedzieć, że dzieje się tu, nie tylko czysty LLM.

### Agent 2 — Verify

**Rola.** Weryfikuje twierdzenia z `01_research.md` (Gemini) i zapisuje zweryfikowany research z werdyktami — wejście dla agentów skryptowych.

**Wejście → wyjście.** *Czyta:* `md/01_research.md`. *Pisze:* `md/02_verified_research.md`.

**Komenda + flagi.** `python tools/pipeline/agent2_verify.py "<slug>"`.

**Przewodnik po kodzie** (9 funkcji): `_load_prompt()` (L34) · `query_gemini_verify()` (L47, br=4) Gemini sprawdza twierdzenia · `_extract_topic_from_research` (L109), `_split_blocks` (L120, regex split), `_field`/`_claim_text` (L134/141) parsują bloki twierdzeń · `parse_gemini_response()` (L159, br=6) mapuje odpowiedź na werdykty (`upper()`) · `build_markdown()` (L215, br=9) składa zweryfikowany md · `main()` (L332, br=5).

**SOP vs kod.** Zgodne z `02_verify.md` (weryfikacja niezależna od wyniku PubMed).

**Koszt i zależności.** Gemini API. Wejście: Agent 1. Wyjście → Agent 3 (i bibliografia Agenta 8).

**Werdykt: `ZOSTAW`.** Brama jakości faktów; średni rozmiar (406 lin.), bez redundancji.

### Agent 3 — Script chain (`/draft`)

**Rola.** Z `02_verified_research.md` tworzy gotowy scenariusz po polsku: selektor architektury → Drafter (3a) → pętla Revisor (3b) ↔ Reviewer (3c). Całość in-session na Opusie; trzy skrypty `.py` to legacy Gemini fallback.

**Wejście → wyjście.** *Czyta:* `md/02_verified_research.md`. *Pisze:* `md/03_architecture.md`, `md/03a_draft.md`, `md/03b_revised_iter*.md`, `md/03c_review_iter*.md`, `md/04_final.md`.

**Komenda + flagi.** `/draft <slug> [architecture] [--sciezka]` (domyślne, in-session); `/draft-team` (z krytykiem 3d). Legacy: `python agent3.py "<slug>" [--max-iterations N] [--start-iteration N]`.

**Przewodnik po kodzie.**
*Tor domyślny (in-session, brak `.py`):* `/draft` wykonuje Step 1.6 selektor (scoring 5 architektur → `03_architecture.md`, spec `03_architecture_select.md`) → 3a Drafter (`03a_drafter.md`: Stage 1 native PL + Stage 2 audyt doktryny) → pętlę 3b↔3c (max 5 iter; FLAG-at-max prepend ostrzeżenia). Linia `ARCHITECTURE:` jest zdejmowana z `04_final.md`. Logika żyje w `workflows/pipeline/03*.md` + `voice_corpus.md`.

*Tor legacy (`.py`, tylko `--api`):*
- `agent3.py` (179) — orkiestrator. `main()` (br=12): pre-check, że `03a_draft.md` istnieje (Drafter NIE jest tu odpalany — docstring to potwierdza), pętla `_run()` (L32, `subprocess.run`) 3b→3c, czyta werdykt `parse_verdict`, `PASS`→stop / `FLAG`→następna iteracja, na końcu `shutil.copy` revised→`04_final.md` + (jeśli nie PASS) prepend ostrzeżenia o shipowaniu.
- `agent3b_revisor.py` (318) — `_build_prompt()` (legacy prompt rewizji), `build_output`, `main()` (br=14) woła Gemini, zapisuje `03b_revised_iter{N}.md`.
- `agent3c_reviewer.py` (269) — `_build_prompt()`, **`parse_verdict()`** (L163, br=4 — pierwsza linia po `## VERDICT` = PASS/FLAG; **współdzielony**, importowany przez `agent3.py`), `main()`.

**SOP vs kod.** ✅ Parser contract (`## VERDICT`→PASS/FLAG) zgodny. ⚠️ Prompty rewizji/recenzji żyją **podwójnie**: `.py` (legacy) i `03b/03c_*.md` (in-session) — duplikacja jak w Agencie 8.

**Koszt i zależności.** Tor domyślny: in-session (Opus; pętla = wiele iteracji = realny koszt tokenów). Legacy: Gemini. Wejście: Agent 2. Wyjście → Agent 4.

**Werdykt: `UPROŚĆ`.** *Używalność:* in-session = rdzeń; legacy (3 pliki, ~766 lin.) = fallback. *Redundancja:* prompty zduplikowane. *Propozycja:* zachować `parse_verdict` (współdzielony) osobno; resztę legacy (orkiestrator + prompty 3b/3c) wydzielić lub wyciąć z przekrojowym `--api` (§7). *Co sprawdzić:* czy prompty legacy 3b/3c rozjechały się z `.md`.

### Agent 4 — Hook gate (`/hook`)

**Rola.** Brama jakości otwarcia: ocenia pierwsze sekundy scenariusza in-session (Tier 1 ≥8/10 @ ~37 słów, Tier 2 ≥7/10 @ ~200 słów); po werdykcie `RECORD` skrypt deterministycznie wkleja przepisany hook.

**Wejście → wyjście.** *Czyta:* `md/04_final.md`. *Pisze:* `md/04_hook.md`, `md/04_final.md` (in place), `md/04_final.bak.md`, `docx/script.docx`.

**Komenda + flagi.** `/hook <slug>` (scoring in-session) → `agent4_hook.py --apply` (splice). Legacy: `--api` (scoring przez Gemini). `main` używa `add_mutually_exclusive_group`.

**Przewodnik po kodzie** (18 funkcji):
- *Ekstrakcja okien:* `_find_narration_start` (L186), `_is_meta_line`/`_strip_inline_markers`/`_word_count`, `_take_words_with_sentence_extension` (L213, br=3 — dobiera słowa do końca zdania), `_extract_15s_window` (~37 słów) / `_extract_30s_window` (~200 słów), `_extract_topic`.
- *Splice:* `_splice_first_37_words()` (L256, br=7) — regex znajduje granicę pierwszych ~37 słów i podmienia otwarcie; `_ensure_backup` (L307) zapisuje `.bak`.
- *Parsowanie oceny:* `_parse_response` (L322) + zagnieżdżone `_grab_int`/`_grab_block`; `_bar`/`_format_attempt_log` formatują log.
- *Tryby:* `run_apply()` (L538, br=8) — deterministyczny: bierze przepisany hook (in-session), splice, zapis + `04_hook.md` + docx; `run_api()` (L398, br=13) — legacy: pętla scoringu przez Gemini. `main()` (L645) — `--apply` vs `--api`.

**SOP vs kod.** ✅ Verdict `RECORD` przed nagraniem; modyfikuje `04_final.md` in place + backup; eksport `docx/script.docx` (downstream auto-wykrywa `script_corrected.docx`).

**Koszt i zależności.** Tor domyślny: in-session (scoring) + deterministyczny `--apply` (bez API). Legacy: Gemini. Wejście: Agent 3. Wyjście → nagranie + Agent 5/8 (przez docx).

**Werdykt: `ZOSTAW` rdzeń + `UPROŚĆ` legacy.** *Używalność:* brama hooka krytyczna; `--apply` deterministyczny = `ZOSTAW`. *Utrzymanie:* 675 lin., z czego `run_api` (legacy) to spory blok. *Propozycja:* `run_api` razem z przekrojowym `--api` (§7); rdzeń (okna + splice + `run_apply`) zostaje.

### Agent 5 — Visuals (`/visuals`)

**Rola.** Z gotowego scenariusza tworzy prompty obrazów: in-session Opus pisze kompaktowy `05_prompts.md`, a skrypt deterministycznie rozwija je w pełne prompty Imagen + pliki fraz. **Brak Gemini/API w skrypcie.**

**Wejście → wyjście.** *Czyta:* `md/04_final.md` lub `docx/script_corrected.docx`. *Pisze:* `md/05_prompts.md` (in-session) + `05_phrases` (przez `--expand`).

**Komenda + flagi.** `/visuals <slug>` (in-session) → `agent5_visuals.py --expand`; `--extract` (docx→md, auto gdy corrected obecny).

**Przewodnik po kodzie** (10 funkcji, wszystkie deterministyczne): `_extract_architecture` (L407, z linii `ARCHITECTURE:`) · `_build_system_prompt` (L415, wg architektury) · `_extract_topic_from_script` · `_clean_script` (regex) · `_build_imagen_prompt` (L454, wstrzykuje figurę) · `_build_phrases_file` (L465) · `_build_prompts_file` (L479) · `_expand_mode()` (L529, br=7 — rdzeń `--expand`: parsuje `**Visual:**`, wstrzykuje CHARACTER_DESCRIPTION + STYLE_SUFFIX z `utils.py`, zapisuje pliki fraz) + `_replacer` (L554) · `main()` (L626).

**SOP vs kod.** ✅ Zgodne z `05_visuals.md` (kompaktowy `**Visual:**` 40–60 słów; `--expand` dokleja STYLE_SUFFIX). ⚠️ **`architecture_review.md` wymienia `agent5_visuals.py` wśród 6 plików z `--api` — to nieprawda:** skrypt nie ma ani Gemini, ani flagi `--api` (potwierdzone mapą funkcji). → §7.

**Koszt i zależności.** **Bez API** (deterministyczny + in-session Opus do pisania promptów). Wejście: Agent 4. Wyjście → Agent 6.

**Werdykt: `ZOSTAW`.** Deterministyczny most scenariusz→obrazy, zero kosztu API. *Jedyna akcja:* sprostować `architecture_review.md`.

### Agent 6 — Images (★ manual)

**Rola.** Renderuje obrazy w stylu Scientific Etching przez Gemini 3 Pro Image z `05_prompts.md`. Manualny (koszt + czas).

**Wejście → wyjście.** *Czyta:* `md/05_prompts.md`. *Pisze:* `images/image_*.png`.

**Komenda + flagi.** `agent6_images.py --generate [--indices "22,26"] [--start N] [--limit N] [--grain] [--transparent]`; `_parse_args` z `add_mutually_exclusive_group`.

**Przewodnik po kodzie** (10 funkcji): `generate_images()` (L136, **br=24** — rdzeń: Client + `GenerateContentConfig(response_modalities=["IMAGE"])`, pętla po promptach, `--indices` regeneruje wybrane nadpisując, `sleep` na rate-limit, zapis png) · `extract_and_save_prompts` (L108) + `_parse_prompts_from_file` (L76, br=6) · `apply_grain_pass` (L331, woła `utils.add_grain`) · `correct_background` (L373, `utils.enforce_background_color`) · `sync_scripts` (L408, br=7) · `_run_auto_qa` (L62, `subprocess` → 6b) · `_norm`/`_parse_args`/`main`.

**SOP vs kod.** ✅ Zgodne: `location="global"`, negative prompt w tekście, `ImageOps.pad()` (przez `utils.resize_to_target`), `_enforce_background_color` safety-net, grain dopiero w poście. „Nigdy texture w promptcie" egzekwowane poza skryptem (guard/6b).

**Koszt i zależności.** Gemini 3 Pro Image (płatne) — **manual**. Wejście: Agent 5. Wyjście → Agent 6b + montaż. Image-opsy importowane z `utils.py`.

**Werdykt: `ZOSTAW`.** Rdzeń wizualny; `--indices` (re-roll bez przepłacania pełnego setu) to dobra optymalizacja kosztu. Bez redundancji.

### Agent 6b — Image QA (opcjonalny)

**Rola.** Waliduje każdy obraz vs kontrakt stylu (Gemini 2.5 Flash) + deterministyczny test koloru tła; pisze `06_qa.md`, `--retry` regeneruje upadłe.

**Wejście → wyjście.** *Czyta:* `images/*.png`. *Pisze:* `md/06_qa.md`.

**Komenda + flagi.** `agent6b_image_qa.py "<slug>" [--retry]`.

**Przewodnik po kodzie** (10 funkcji): `_init_client` (L74) · `_audit_one()` (L95 — Gemini vision audytuje 1 obraz: `from_bytes`, parsuje PASS/FAIL) · `_check_background_color()` (L125 — **deterministyczny**: numpy liczy średni kolor brzegów i dystans do #F4E5CA, uzupełnia audyt LLM) · `_check_missing_images` (L156) · `_index_from_filename` · `_write_report` (L186, br=8) · `audit()` (L254, br=12 — pętla po obrazach + `sleep`) · `_retry_failed()` (L315, `subprocess` → agent6 `--indices`) · `main`.

**SOP vs kod.** ✅ Zgodne: Gemini 2.5 Flash, `06_qa.md`, `--retry` jedna próba, nigdy nie kasuje.

**Koszt i zależności.** Gemini 2.5 Flash (tanie) — opcjonalny. Wejście: Agent 6. Wyjście: raport + ewentualny re-roll (woła Agent 6 `--indices`).

**Werdykt: `ZOSTAW`.** Tani strażnik jakości; deterministyczny test koloru to dobry dodatek do audytu LLM. *Używalność:* opcjonalny — jeśli nie używasz QA, kandydat na `WYTNIJ`, ale koszt utrzymania niski.

### Agent 7 — Package / Thumbnails (★ manual · DRYF)

**Rola.** Renderuje miniatury przez Gemini 3 Pro Image z konceptów wygenerowanych in-session. Następca `/thumbnails` to `/package` (3 strategie title + napis + concept).

**Wejście → wyjście.** *Czyta:* `md/04_final.md` + `md/08_publish.md` (+ `md/07_prompts.md`). *Pisze:* `md/07_prompts.md`, `thumbnails_no_grain/thumbnail_0N.png`.

**Komenda + flagi.** `/package <slug>` (in-session koncepty → render) lub `/thumbnails <slug>`; skrypt `agent7_thumbnails.py --render --no-grain`.

**Przewodnik po kodzie** (5 funkcji): `_parse_prompts_text` (L55) · `_load_prompts_md` (L67) / `_load_saved_prompts` (L82) · `_generate_image()` (L98, br=6 — Gemini Client, `generate_content`, `write_bytes`, rate-limit) · `main()` (L149, **br=22** — cała logika CLI: wczytaj prompty, renderuj N miniatur, `sleep` 20s rate-limit; grain dokładany manualnie w Canvie).

**SOP vs kod.** ⚠️ **Wyraźny dryf nazewnictwa:** żyją równolegle `/package` *i* `/thumbnails`, SOP-y `07_package.md` (89) *i* `07_thumbnails.md` (57), dwa skille — a skrypt to wciąż `agent7_thumbnails.py`. CLAUDE.md już przemianowano na `/package` (następca), stara ścieżka żyje obok. → §7 (flagowy przypadek).

**Koszt i zależności.** Gemini 3 Pro Image (render, płatne) + in-session Opus (koncepty) — **manual**, 20s rate-limit. Wejście: Agent 4 + Agent 8. Wyjście → miniatura (grain w Canvie).

**Werdykt: `UPROŚĆ`.** Funkcjonalnie OK, ale dryf thumbnails→package myli (dwie komendy/SOP-y/skille na jeden skrypt). *Propozycja:* dokończyć migrację — `/package` jako jedyne wejście, usunąć `07_thumbnails.md` + komendę/skill `/thumbnails`, rozważyć rename `agent7_thumbnails.py` → `agent7_package.py`. *Co sprawdzić:* czy `07_prompts.md` to nadal właściwy plik wyjściowy `/package`.

### Agent 8 — Publish (`/publish`)  ·  ★ wzorzec sekcji

**Rola.** Z gotowego scenariusza buduje komplet metadanych publikacyjnych YouTube (5 tytułów, opis + 3 hashtagi, znaczniki czasu, tagi long-form, bibliografia, paczka Shorts) — w sesji na Opusie; skrypt `.py` dokłada tylko deterministyczne bookendy.

**Wejście → wyjście.**
- *Czyta* (priorytet narracji): `docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`; do tego `md/02_verified_research.md` (bibliografia) i najnowszy `outputs/intelligence/*_tag_signals.md` (miękko).
- *Pisze:* `md/08_publish.md` (+ `docx/08_publish.docx`); transient: `.tmp/08_narration.md`, `.tmp/08_signals.md`.

**Komenda + flagi.** `/publish <slug>` (domyślne, in-session). Skrypt: `--extract` / `--signals [--topic="…"]` / `--finalize` / `--api` (legacy). CLI parsowany **ręcznie** w `main()` (brak `argparse` — stąd `FLAGS=[]` w skanie).

**Przewodnik po kodzie** (29 funkcji; plik dzieli się na DWA tory).

*Tor domyślny — bookendy in-session (to faktycznie odpala `/publish`):*
- `main()` (L1061) — ręczny parser `argv`: wyłuskuje `--flag`, `--topic=`, pozycyjny `slug`; dispatch do `run_extract`/`run_signals`/`run_finalize`/`run_api_pipeline`; bez flagi → instrukcja „użyj `/publish`".
- `run_extract()` (L813) → `_load_narration()` (L104) — materializuje narrację do `.tmp/08_narration.md` (bo `Read` nie czyta `.docx`); priorytet corrected > script > final.
- `run_signals()` (L856) — PRE: ustala polski seed (`--topic=` albo `_derive_seed_topic()` L829 = nagłówek researchu/skryptu, bo corrected.docx ma zdjęte nagłówki → `_extract_topic()` zwraca „Unknown Topic"), `_alphabet_soup()` (L502) skrobie YouTube autocomplete (`_scrape_suggestions()` L482: zapytanie + a–z, `sleep(0.1)`, dedup), `_load_niche_signals()` (L511) wczytuje najnowszy tygodniowy sidecar (`parents[2]` = root, nie CWD); zapisuje `.tmp/08_signals.md`. Fail-soft: brak sieci → `(unavailable)`.
- `run_finalize()` (L936) — POST nad in-session `md/08_publish.md`: (1) `_annotate_script_quarters()` (L384) + `_quarter_for_quote()` (L405) tagują Hook/Core-payload znacznikiem ćwiartki **Q1–Q4** (narracja dzielona na 4 równe części wg liczby słów; dla cytatu dopasowanie substring 60/30/15 znaków → pozycja słowa → ćwiartka; inaczej `[Q?]`); (2) `_validate_shorts_clip_blocks()` (L442) wstawia głośny `[MISSING …]`, gdy Short nie ma bloku „Script Lines to Clip"; (3) `_trim_tags_in_markdown()` (L909) → `_trim_tags_to_budget()` (L682) przycina linię tagów do 450 znaków od ogona, zachowując slot `SENSUM`; (4) liczy `[Q?]` jako widoczny sygnał błędu; `export_to_docx`.

*Tor legacy `--api` (Gemini — odpala się TYLKO z flagą `--api`):*
- `run_api_pipeline()` (L987) spina 3 przebiegi: `run_titles_pass` (`_build_titles_prompt`) → `run_shorts_pass` (`_build_shorts_pass{1,2,3}_prompt` + wspólna anotacja/walidacja) → `run_metadata_pass` (autocomplete + niche + Gemini + `_parse_metadata` L672 + trim) → `build_master_output()` (L781, z `_build_metadata_block` L745) składa `08_publish.md`.
- `_query_gemini()` (L128) — 2-liniowy delegat do `_query_gemini_base()` z `utils.py`.
- **Wielkie f-stringi promptów** `_build_titles_prompt` (≈62 lin.), `_build_shorts_pass*` (≈165 lin.), `_build_metadata_prompt` (≈96 lin.) — **to te same prompty, które w torze domyślnym żyją w `workflows/pipeline/08_publish.md`**.
- Pomocnicze: `_extract_topic` (L118), `_usage` (L1051, sam tekst pomocy).

*Współdzielone przez oba tory:* `_annotate_script_quarters`/`_quarter_for_quote`, `_validate_shorts_clip_blocks`, `_scrape_suggestions`/`_alphabet_soup`, `_load_niche_signals`, `_trim_tags_to_budget`.

**SOP vs kod.**
- ✅ *Zgodne:* 9 kroków in-session; locked output (Tag #1, 3 hashtagi, 5 zdań, `[Q1]–[Q4]`, `[MISSING]`); bookendy `--extract/--signals/--finalize`; `PROJECT_ROOT = parents[2]` potwierdzone w `_load_niche_signals`.
- ⚠️ *Dryf nazewnictwa:* `_load_niche_signals` docstring mówi „Agent 11", a `run_signals` w logu „Intelligence Agent" — ten sam komponent (sidecar tagów). Kosmetyka, ale myli.
- ⚠️ *Redundancja:* prompty (titles/shorts/metadata) istnieją **dwukrotnie** — w `.py` (legacy) i w `08_publish.md` (in-session). Zmiana doktryny w jednym miejscu nie propaguje do drugiego.

**Koszt i zależności.** Tor domyślny: in-session (Opus) + darmowy web-scrape autocomplete; zależy od `02_verified_research.md` i (miękko) od sidecara Intelligence. Tor legacy: płatny Gemini. **LOC 1093** — największy plik pipeline'u, z czego ~połowa to legacy + prompty.

**Werdykt: `UPROŚĆ`.**
- *Używalność:* tor in-session = rdzeń produkcji (wysoka); tor `--api` = rzadki/żaden fallback.
- *Utrzymanie:* 1093 linii, ~500 to legacy prompt-buildery duplikujące `08_publish.md`.
- *Redundancja:* prompty w dwóch miejscach (kod + SOP) — realne ryzyko rozjazdu.
- *Propozycja:* wydzielić tor `--api` (`_query_gemini`, `_build_*_prompt`, `run_*_pass`, `run_metadata_pass`, `_parse_metadata`, `_build_metadata_block`, `build_master_output`, `run_api_pipeline`) do `agent8_legacy.py` — plik domyślny spada do ~500 linii samych bookendów — albo `WYTNIJ` legacy, jeśli Gemini-fallback jest martwy.
- *Co sprawdzić przed cięciem:* czy `--api` jest jeszcze kiedykolwiek używany; czy prompty w `.py` już się rozjechały z `08_publish.md` (jeśli tak — kopia w `.py` jest martwa i myląca). Decyzja wspólna z przekrojowym `--api` (§7).

### Satelita — Align (`agent_align.py`)

**Rola.** Po nagraniu lektora dopasowuje audio do znanego scenariusza (faster-whisper, lokalnie) i składa bundle do DaVinci Resolve: napisy SRT + timeline FCPXML + podgląd HTML. Eliminuje 2–4h ręcznej synchronizacji na wideo.

**Wejście → wyjście.** *Czyta:* `voiceover/voiceover.wav` + `md/05_phrases.md` + `script_corrected.docx`/`script.docx`/`04_final.md`. *Pisze:* `edit/subtitles.srt`, `edit/timeline.fcpxml`, `edit/preview.html`, `edit/alignment.json`.

**Komenda + flagi.** `python tools/pipeline/agent_align.py "<slug>"` (`parse_args`); auto-wykrywa audio i obrazy.

**Przewodnik po kodzie** (5 funkcji): `_find_default_audio` (L60, br=4 — szuka `voiceover.wav`) · `_find_background` (L74) · `_discover_images` (L85, br=5 — zbiera obrazy do timeline) · `main(args)` (L104, **br=17, ~239 lin.** — rdzeń: faster-whisper aligna audio do znanego skryptu, mapuje frazy z `05_phrases.md`, generuje SRT/FCPXML/preview, zapisuje `alignment.json` przez `json.dumps`) · `parse_args` (L346).

**SOP vs kod.** ✅ Zgodne z `align.md`: lokalny faster-whisper (darmowy), bundle do DaVinci, naming bez numeru (osobny od `intelligence.py`).

**Koszt i zależności.** **Lokalne (darmowe)** — zero API. Wejście: nagranie + 05_phrases + scenariusz. Niezależny od reszty łańcucha (post-record).

**Werdykt: `ZOSTAW`.** Wysoki zwrot (oszczędza 2–4h/wideo), zero kosztu API, izolowany. Klasyczny „zostaw".

### Satelita — Intelligence (`tools/intelligence/`, 6 plików, ~1 717 lin.)

**Rola.** Okresowy wywiad niszowy: zbiera dane o kanałach konkurencji (YouTube Data API), analizuje i produkuje (a) sidecar `{week}_tag_signals.md` — jedyny punkt integracji z core (czyta go Agent 8) — oraz (b) tygodniowy deck PPTX z wykresami.

**Wejście → wyjście.** *Czyta:* web (YouTube Data API + autocomplete). *Pisze:* `outputs/intelligence/{week}_tag_signals.md` + deck PPTX + SQLite.

**Komenda + flagi.** `python tools/intelligence/intelligence.py [--skip-vision] [--skip-comments] [--days N]`.

**Przewodnik po kodzie** (per plik):
- `intelligence.py` (263) — orkiestrator. `run()` (L98, br=7) spina: `collector.discover_channels`/`fetch_*` → `db.upsert_*` → `analyzer.*` → `vision.classify_thumbnails` → `slide_builder.build_deck` → `_write_tag_signals()` (L42, br=4 — sidecar z `most_common` tagów). `_week_label` (ISO tydzień).
- `analyzer.py` (269, 9 funkcji czystej analizy, bez API) — `trending_topics`, `view_velocity`, `engagement_rate`, `content_gaps`, `comment_sentiment`, `publish_timing`, `evergreen_split`, `top_title_words`, `duration_engagement`.
- `collector.py` (229, 8 funkcji) — **YouTube Data API** (wymaga klucza): `discover_channels`, `fetch_channel_stats`, `fetch_recent_videos` (L102, br=13), `fetch_comments`, `download_thumbnails`; `sleep` na rate-limit.
- `db.py` (144, 6 funkcji) — **SQLite**: `init_db`, `upsert_channel/video`, `insert_comments`, `save_snapshot`, `get_prev_snapshot` (wzrost tydzień-do-tygodnia).
- `slide_builder.py` (**733, 31 funkcji**) — **PPTX + matplotlib**: 16 slajdów (`_slide_01_cover` … `_slide_16_upload_frequency`) + helpery wykresów/fontów. Największy plik satelity — cały dla deck'a.
- `vision.py` (80, 1 funkcja) — `classify_thumbnails` (Gemini vision klasyfikuje style miniatur konkurencji).

**SOP vs kod.** ✅ `PROJECT_ROOT = parents[2]` (gotcha z CLAUDE.md). ⚠️ Nazewnictwo „Agent 11" vs „Intelligence Agent" (jak w sidecarze Agenta 8).

**Koszt i zależności.** YouTube Data API (klucz, limity) + Gemini vision (płatne) + web. **Tylko `tag_signals.md` zasila core (Agent 8)**; deck PPTX to osobny produkt. Po stronie Agenta 8 fail-soft (brak sidecara = pomijany).

**Werdykt: `UPROŚĆ` / kandydat do częściowego `WYTNIJ`.**
- *Używalność:* kluczowe pytanie — czy realnie czytasz tygodniowy **deck PPTX**? Jeśli nie, `slide_builder.py` (733 lin.) + duża część `analyzer`/`collector`/`db` to martwy ciężar.
- *Wartość dla core:* potrzebny jest **tylko** sidecar tagów (Agent 8). Intelligence można zredukować do mini-skryptu „autocomplete/nisza → sidecar", a cały tor PPTX wyciąć.
- *Propozycja:* używasz deck'a → `ZOSTAW`; nie → `WYTNIJ` `slide_builder.py` + odchudź collector/db/analyzer do tego, co zasila sidecar.
- *Co sprawdzić:* kiedy ostatnio powstał/był użyty deck PPTX; czy `tag_signals.md` realnie wpływa na tagi (czy Agent 8 go znajduje).

### Satelita — Agent Teams (opt-in)

**Rola.** Opcjonalny tryb: cold-context krytycy w osobnych oknach polują na translationese (3d Native-Ear w `/draft-team`) i kalki w human-facing copy (8d Native-Copy w `/publish-team`) w adversarialnej debacie ≤3 rundy.

**Wejście → wyjście.** Konfiguracje w `.claude/agents/*`; krytycy piszą `md/03d_*` / `md/08d_*`. Wymaga `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.

**Komenda + flagi.** `/draft-team <slug>`, `/publish-team <slug>` (warianty `-team` zwykłych komend).

**Przewodnik po kodzie.** Brak `.py` — definicje agentów (markdown) + logika w `draft-team.md` (145) / `publish-team.md` (146) + SOP-y `03d_native_ear.md` (148) / `08d_native_copy.md` (175). Pełna spec: `docs/agent_teams_reference.md` (286). Mechanika: adversarialna debata (BLOCKER w pozycjach wpływu), anti-sterility guard, fallback do zwykłego `/draft`/`/publish`, **jeden team naraz** (mandatory teardown).

**SOP vs kod.** ✅ Zgodne z `agent_teams_reference.md`. Brak kodu = brak dryfu kod↔SOP.

**Koszt i zależności.** **Dodatkowe konteksty Opus** (więcej tokenów) — opt-in. Zwykłe `/draft`/`/publish` zostają tańszym defaultem.

**Werdykt: `ZOSTAW` (opt-in).** Nie obciąża domyślnej ścieżki. *Używalność:* jeśli nigdy nie używasz `-team`, to narzut dokumentacyjny — kandydat na `WYTNIJ` (komendy + agenci + 2 SOP-y + reference), ale zero kosztu gdy nieużywane. *Decyzja:* czy native-critic daje wartość ponad zwykły 3c kat. J.

### Współdzielone — `utils.py` (552) + `add_grain.py` (50)

**Rola.** Biblioteka wspólna wszystkich agentów: env, ścieżki/IO, plumbing Gemini, eksport docx, operacje na obrazach. `add_grain.py` = dev-tool nakładający ziarno.

**Wejście → wyjście.** Importowane (`from tools.utils import …`); brak własnego wejścia/wyjścia pipeline'owego.

**Komenda + flagi.** `utils.py` — biblioteka, nieuruchamiana wprost (tylko import). `add_grain.py` — `python tools/dev/add_grain.py "<slug>" [intensity]`.

**Przewodnik po kodzie** (`utils.py`, 20 funkcji): *env/ścieżki* — `_load_env`, `get_env`, `make_slug`, `next_output_number`, `get_output_dir`, `write_output`/`read_output`, `load_style_guide` · *LLM* — **`query_gemini_text()`** (L211, br=8 — JEDYNY wspólny plumbing Gemini, używany przez ścieżki legacy `--api`; `sleep` na retry) · *docx* — `read_script_docx_text` (L281, czyta `.docx`, którego `Read` nie ruszy), **`export_to_docx()`** (L293, **br=28** — md→docx z tabelami; `_apply_spacing`/`_add_inline`/`_parse_row`/`_flush_table`) · *obrazy* — `resize_to_target` (L463, `ImageOps.pad`), `enforce_background_color` (L477, safety-net #F4E5CA), `make_transparent`, `add_grain` (L520, szum numpy) · `log_cost`.
`add_grain.py`: `batch_grain()` (L25) — woła `utils.add_grain` po wszystkich obrazach slug-a.

**SOP vs kod.** ✅ Komentarz L204-207 dokumentuje usunięcie `query_claude()` (2026-05-29) — **to komentarz, nie martwy kod** (trop „claudeapi" ze skanu = fałszywy alarm, zweryfikowany). STYLE_SUFFIX / enforcement tła zgodne z doktryną koloru.

**Koszt i zależności.** Sam bezkosztowy; `query_gemini_text` to wspólny koszt legacy. Importowany niemal wszędzie.

**Werdykt: `ZOSTAW`.** Rdzeń infrastrukturalny. *Uwaga:* `query_gemini_text` używany **tylko** przez ścieżki legacy `--api` — jeśli wytniesz całe legacy (§7), ta funkcja może stać się martwa (sprawdź importy przed cięciem). `export_to_docx` (br=28) złożona, ale potrzebna (każdy docx idzie przez nią).

---

## §6 Zbiorczy rejestr werdyktów

Posortowane wg zysku (najpierw największe cięcia). „Zysk" = szacowana redukcja linii / kosztu / złożoności.

| # | Komponent | Werdykt | Zysk | Co zrobić | Sprawdzić przed cięciem |
|---|---|---|---|---|---|
| 1 | **Legacy `--api`** (przekrojowo: `agent3/3b/3c`, `agent4.run_api`, `agent8` tor `--api`) | `UPROŚĆ`→`WYTNIJ` | ~1 500+ lin. w 5 plikach (+ `utils.query_gemini_text`) | wydzielić do `tools/pipeline/_legacy/` albo usunąć cały Gemini-fallback | czy `--api` kiedykolwiek używasz; czy prompty `.py` rozjechały się z `.md` |
| 2 | **Intelligence — deck PPTX** (`slide_builder.py` + część collector/db/analyzer) | `WYTNIJ` (warunkowo) | ~733 lin. + część z ~1 717 | wyciąć generator PPTX, zostawić tylko tor „→ `tag_signals.md`" | czy deck PPTX jest realnie czytany |
| 3 | **Agent 8 publish** | `UPROŚĆ` | ~500 lin. (legacy w pliku) | wydzielić tor `--api` → `agent8_legacy.py`; domyślny plik ~500 lin. | jw. (`--api`) |
| 4 | **Agent 3 chain** (3 pliki) | `UPROŚĆ` | ~766 lin. legacy | zachować `parse_verdict`; orkiestrator + prompty 3b/3c → legacy/out | czy prompty legacy ≠ `.md` |
| 5 | **Agent 4 hook** | `UPROŚĆ` (legacy) | blok `run_api` | `run_api` razem z cięciem `--api`; rdzeń (splice + `run_apply`) zostaje | jw. |
| 6 | **Agent 7 package/thumbnails** | `UPROŚĆ` | porządek (nie linie) | dokończyć migrację thumbnails→package (usunąć starą komendę/SOP/skill, rename pliku) | czy `07_prompts.md` to wyjście `/package` |
| 7 | **Agent 0 materials** | `ZOSTAW` warunkowo | 177 lin. (jeśli `WYTNIJ`) | zostaw, jeśli używasz PDF-wkładu | czy `00_materials_insights.md` w ogóle powstaje |
| 8 | **Agent 6b QA** | `ZOSTAW` (opcj.) | 395 lin. (jeśli `WYTNIJ`) | zostaw — tani strażnik jakości | czy używasz QA obrazów |
| 9 | **Agent Teams** | `ZOSTAW` (opt-in) | komendy + agenci + 2 SOP-y (jeśli `WYTNIJ`) | zostaw — nie obciąża defaultu | czy używasz `-team` |
| 10 | **Agent 1, 2, 5, 6, Align, `utils.py`** | `ZOSTAW` | — | nie ruszać (rdzeń) | — |

**Sumarycznie:** największy jednorazowy zysk to **decyzja o legacy `--api`** (poz. 1, a w jej ramach 3/4/5 to ten sam temat) oraz **decyzja o deck'u PPTX Intelligence** (poz. 2). Reszta to porządki (poz. 6) i warunkowe cięcia zależne od Twojego realnego użycia (poz. 7–9). Rdzeń produkcji jednego wideo (1, 2, 5, 6, Align + `utils`) zostaje nietknięty.

---

## §7 Dług i dryf

Rozjazdy kod ↔ dokumentacja i dług do posprzątania (zweryfikowane w trakcie audytu):

1. **Migracja `thumbnails → package` niedokończona.** Równolegle żyją: komendy `/package` + `/thumbnails`, SOP-y `07_package.md` (89) + `07_thumbnails.md` (57), dwa skille — a skrypt to wciąż `agent7_thumbnails.py`. CLAUDE.md już wskazuje `/package` jako następcę. *Sprzątanie:* wybrać `/package` jako jedyne wejście, usunąć starą komendę/SOP/skill, rozważyć rename pliku → `agent7_package.py`.

2. **Legacy `--api` w 5 plikach** (`agent3.py`, `agent3b_revisor.py`, `agent3c_reviewer.py`, `agent4_hook.py`, `agent8_publish.py`) + wspólny `utils.query_gemini_text`. Reżim „wszystko in-session" sprawił, że to ścieżka rzadko/nigdy używana. *Decyzja:* zostaw jako fallback vs wytnij (§6 poz. 1).

3. **`architecture_review.md` jest nieaktualny.** (a) Wymienia **6** plików z `--api`, w tym `agent5_visuals.py` — **błąd**: `agent5` nie ma ani `--api`, ani Gemini (faktycznie jest ich **5**). (b) Mówi o agent8 „~1 090 linii" — **zgodne** z rzeczywistością (1093; PowerShell zaniżał do 835). *Sprzątanie:* sprostować listę plików `--api`.

4. **Prompty zduplikowane (kod vs SOP).** Dla agentów 3b/3c/4/8 prompty żyją **dwukrotnie**: jako f-stringi w `.py` (tor legacy) i w `workflows/pipeline/*.md` (tor in-session). Zmiana doktryny w jednym miejscu nie propaguje do drugiego. *Sprzątanie:* przy cięciu legacy znika automatycznie; póki legacy żyje — ryzyko cichego rozjazdu.

5. **Nazewnictwo „Agent 11" vs „Intelligence Agent".** `agent8._load_niche_signals` docstring mówi „Agent 11"; logi i reszta — „Intelligence Agent". Ten sam komponent (sidecar tagów). *Sprzątanie:* ujednolicić na „Intelligence Agent".

6. **Fałszywy alarm (zweryfikowany, BEZ długu):** trafienie `anthropic`/`query_claude`/`ANTHROPIC_API` w `utils.py` to **komentarz** (L204-207) dokumentujący usunięcie `query_claude()` — nie martwy kod. Zostawić.

**Uwaga metodyczna:** liczby linii w `CLAUDE.md`/spec sprzed audytu pochodziły z zaniżającego pomiaru PowerShell (~−25%). Poprawne wartości (`ast`) są w §2.
