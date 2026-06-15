# Audyt spójności CLAUDE.md ↔ workflows/ ↔ .claude/ ↔ tools/ (2026-06-15)

## TL;DR

Integralność odwołań w repo jest **zdrowa** — nie znaleziono ani jednej martwej ścieżki, brakującego pliku, niewdrożonej komendy slash ani agenta opisanego w CLAUDE.md, który nie istnieje. Wszystkie 12 potwierdzonych znalezisk to **stale/sprzeczności w treści doktryny lub w martwym kodzie `--api`**, nie defekty łamiące działający pipeline. Z severity: **0 High, 5 Medium, 6 Low, 1 Info**. Najważniejsze: (1) trzy generatory `/publish` biegną na **Sonnet**, a CLAUDE.md i `publish.md` mówią o „4 kontekstach Opus"; (2) `style_guide_images.md` opisuje **porzucony kontrakt białego/transparentnego tła** sprzeczny z obowiązującym sage-beige + two_color (ryzyko realne, bo guide jest ładowany przez skill-guard); (3) liczby w „Locked publish output" CLAUDE.md (tagi 5–8, opis „exactly 5 sentences") są **przestarzałe** względem żywego SOP (12–15 tagów, ~5 zdań / 80–130 słów). Audyt jest **report-only** — poprawki to osobna bramka.

## Znaleziska

### [MEDIUM] Generatory `/publish` biegną na Sonnet, nie na Opus

- **Twierdzenie:** CLAUDE.md, tabela Agent Chain wiersz 8: „Opus 4.8 (in-session lead + 4 teammate contexts — no API)"; `.claude/commands/publish.md` L193: „Token cost: four extra Opus contexts (3 generators + 1 critic across ≤3 language rounds)".
- **Rzeczywistość:** Trzy generatory deklarują `model: sonnet` we frontmatterze: `.claude/agents/publish-copywriter.md` L5, `.claude/agents/publish-seo.md` L5, `.claude/agents/publish-clips.md` L5. Tylko `.claude/agents/native-copy-critic.md` L6 ma `model: opus`. `publish.md` L33-34/L187-188 („each teammate is the model for its own steps") potwierdzają brak nadpisania modelu przy spawnowaniu — decyduje frontmatter. Realny układ: **3× Sonnet + 1× Opus**, nie 4× Opus.
- **Werdykt:** Sprzeczność (medium). Realnie wprowadza w błąd co do kosztu/modelu, ale dotyczy etykiety, nie łamie pipeline'u.
- **Proponowana poprawka:** W `publish.md` L193 zmienić na „three extra Sonnet generator contexts + one Opus critic"; w CLAUDE.md wiersz 8 tabeli doprecyzować, że generatory są na Sonnet 4.6, a tylko lead/8d na Opus 4.8 (analogicznie do wiersza 3b section-checker = Sonnet).

### [MEDIUM] „Locked publish output": tagi long-form 5–8 vs żywe 12–15

- **Twierdzenie:** CLAUDE.md L136 „Locked publish output": „5–8 multi-word tags (single-word prohibited except SENSUM-once)".
- **Rzeczywistość:** Operacyjny kontrakt to 12–15. `workflows/pipeline/08_publish.md` STEP 4 L137 („Produce 12–15 tags total… (Earlier doctrine said 5–8…)"), self-check L308 („12–15 tags total"), `.claude/agents/publish-seo.md` L16 („12–15 tags"). SOP wprost nazywa 5–8 „Earlier doctrine". (Uwaga: poboczny trop o legacy `--api` L676 z „Produce 5–8 tags total" **niezweryfikowany** — grep nie znalazł tego stringa w 08_publish.md; rdzeń staleness jest jednak potwierdzony.)
- **Werdykt:** Stale (medium). Realna generacja czyta poprawny SOP; stała jest tylko mylącym wpisem w „locked" podsumowaniu.
- **Proponowana poprawka:** CLAUDE.md L136: „5–8 multi-word tags" → „12–15 multi-word tags (single-word prohibited except SENSUM-once)".

### [MEDIUM] „Locked publish output": opis „exactly 5 sentences" vs ~5 zdań / 80–130 słów

- **Twierdzenie:** CLAUDE.md L136: „description exactly 5 sentences".
- **Rzeczywistość:** Żywy SOP złagodził regułę. `workflows/pipeline/08_publish.md` STEP 2 L86 „~5 sentences, ~80–130 words" z jawnym „the old hard 80-word cap is lifted", powtórzone L99; self-check L305 „~5 sentences / ~80–130 words". Twarde „Exactly 5 sentences. Count them. … under 80 words" żyje tylko w `tools/pipeline/agent8_publish.py` L579/L592, wewnątrz `_build_metadata_prompt` (L553) → `run_metadata_pass` (L722), czyli w martwym orkiestratorze `--api`.
- **Werdykt:** Stale (medium). CLAUDE.md cytuje ograniczenie martwej ścieżki jako żywą doktrynę; SOP i walidatory są realnym wzorcem.
- **Proponowana poprawka:** CLAUDE.md L136: „description exactly 5 sentences" → „description ~5 sentences (~80–130 words)" dla zgodności z SOP STEP 2.

### [MEDIUM] 01_research.md — legacy ścieżka `videos/` (bez `_pl`) w sekcji Output Location

- **Twierdzenie:** CLAUDE.md, drzewo plików: „outputs/ videos_pl/ # Polish videos (one folder per slug); videos_en/ = legacy English".
- **Rzeczywistość:** `workflows/pipeline/01_research.md` ma wewnętrzną sprzeczność: sekcja „Output Location" L81-87 pokazuje legacy „outputs/ └── videos/ └── emotional-dysregulation-in-adhd/ …" (BEZ `_pl`), podczas gdy ten sam plik używa poprawnej ścieżki dwukrotnie: L67 (przykład konsoli) i L127 (sekcja Review). Katalog `videos/` bez sufiksu nie istnieje w kanonie — to pozostałość sprzed lokalizacji 2026-05-25.
- **Werdykt:** Stale (medium). „Output Location" to dokładnie miejsce, gdzie operator szuka katalogu wyjściowego, więc stale path tam realnie myli; dwie poprawne referencje obok i auto-generowana ścieżka w skrypcie ograniczają szkodę.
- **Proponowana poprawka:** W `01_research.md` (ok. L83) zmienić blok „outputs/ └── videos/" na „outputs/ └── videos_pl/".

### [MEDIUM] style_guide_images.md — porzucony kontrakt tła (białe/transparent) sprzeczny z sage-beige

- **Twierdzenie:** CLAUDE.md (Design Standards): tło = wyłącznie #F4E5CA Sage Beige, w promptach „flat solid sage beige background with no texture"; dwa kolory only; „No gradients, no fills"; paper-grain dokładany w poście przez `add_grain.py`, nigdy w promptcie.
- **Rzeczywistość:** `workflows/guides/style_guide_images.md` opisuje przeciwny, przestarzały kontrakt: L13 „Background applied in DaVinci as canvas color — images generate and export as transparent PNG"; L24 „on clean flat white background"; L25 „dark brown ink lines on white"; L45 „Warm khaki-tan fill" (khaki-tan = trzeci kolor, łamie kontrakt dwukolorowy); L87 „pure white void". Realny `tools/utils.py` potwierdza wersję CLAUDE.md: `STYLE_SUFFIX` = flat sage beige (#F4E5CA), `two_color()` (L547-582) twardo snapuje każdy piksel do #582F0E / #F4E5CA, `TARGET_BACKGROUND_RGB`=(244,229,202).
- **Werdykt:** Sprzeczność (medium). To plik kontekstu/doktryny, nie ścieżka wykonania — realny render przez utils.py jest poprawny. Ryzyko jest jednak realne: guide jest wciąż żywym źródłem (ładowany przez `.claude/skills/scientific-etching-guard/SKILL.md` L33 i `workflows/pipeline/00_master.md` L265), więc guard może wstrzyknąć błędny biały/transparent kontrakt do freeform image-promptów.
- **Proponowana poprawka:** W `style_guide_images.md` zamienić „flat white background" / „ink lines on white" / „transparent PNG + DaVinci canvas color" / „Warm khaki-tan fill" / „pure white void" na obowiązujący kontrakt: flat solid sage beige (#F4E5CA) tło w promptcie, dwa kolory (#582F0E ink na #F4E5CA), brak wypełnień, two_color snap w poście; usunąć khaki-tan fill. (Opcjonalnie zaktualizować nagłówek L3 „Read by Agent 5" — Agent 5 dziś dostaje STYLE_SUFFIX z utils.py przez `--expand`, nie czyta guide'a.)

### [LOW] Shorts tags 8–10 (SOP) vs 3–5 (legacy `--api`)

- **Twierdzenie:** SOP STEP 9 L237 i agent SEO L18: „8–10 multi-word intent phrases per Short" (CLAUDE.md nie podaje liczby dla Shorts).
- **Rzeczywistość:** Ścieżka legacy `--api` w `tools/pipeline/agent8_publish.py` używa starszego kontraktu 3–5: L322 „3–5 multi-word intent phrases per Short. Each phrase 2–4 words.", L358 i L361 „Tags — KEEP TIGHT. 3–5 multi-word intent phrases". Prompt jest uruchamialny (`_build_shorts_pass3_prompt` → L512 → `run_api_pipeline` L991 → flaga `--api` L1084), ale CLAUDE.md deklaruje ścieżki `--api` jako „inert — in-session slash commands are the default".
- **Werdykt:** Stale (low). To wewnętrzna niespójność dwóch ścieżek (żywej 8–10 i dormantnej `--api` 3–5), nie rozjazd CLAUDE.md↔plik; domyślny przepływ nigdy nie dotyka starego promptu.
- **Proponowana poprawka:** Zsynchronizować prompty `--api` (`_SHORTS_BRAND_SYSTEM` L322 + pass3 L358/361) do 8–10, albo dopisać w docstringu, że ścieżka `--api` jest zamrożona na starym kontrakcie Shorts.

### [LOW] agent8_publish.py `--api`: prompt 5–8 tagów vs print/walidacja „doctrine 12–15"

- **Twierdzenie:** CLAUDE.md/SOP: long-form tagi 12–15; `--finalize` trim do budżetu 480 znaków.
- **Rzeczywistość:** W `tools/pipeline/agent8_publish.py` ścieżka `--api` jest samozaprzeczna: `_build_metadata_prompt` (L676) każe „Produce 5–8 tags total", a ta sama funkcja `run_metadata_pass` (L722) drukuje L742 „doctrine 12–15" i L744 ustawia `within_doctrine = … else "OUTSIDE doctrine 12–15"` (warunek `12<=len<=15`). Przebieg idealnie wykonujący prompt (np. 7 tagów) wydrukuje „OUTSIDE doctrine 12–15". Prompt 5–8 zgadza się z CLAUDE.md; print 12–15 z SOP L137 — dwie połówki funkcji zakotwiczone w dwóch doktrynach. Trimmer `_trim_tags_to_budget` (480 znaków) jest poprawny.
- **Werdykt:** Sprzeczność (low). Mylący komunikat w uśpionym kodzie `--api`, zero wpływu na aktywny pipeline.
- **Proponowana poprawka:** W `run_metadata_pass`/`_build_metadata_prompt` ujednolicić jeden próg — albo print L742/L744 na 5–8 (zgodnie z promptem tej samej funkcji), albo podnieść prompt do 12–15.

### [LOW] Martwa stała SHORT_TYPES — sztywne menu archetypów sprzeczne z anti-archetyp STEP 6

- **Twierdzenie:** SOP STEP 6 L200: „You are NOT constrained to any fixed archetype menu" (dobór Shorts wg „Triple Retention Filter (HARD AND-GATE)", L187).
- **Rzeczywistość:** `tools/pipeline/agent8_publish.py` L66-72 nadal definiuje `SHORT_TYPES = [("Surprise",…),("Emotion",…),("Standalone",…),("CTA-Hook",…),("Practical Tip",…)]` — dokładnie to sztywne menu, którego SOP zabrania. Grep po całym repo: `SHORT_TYPES` występuje **tylko raz** (definicja L66), zero użyć — martwa stała.
- **Werdykt:** Orphan (low). Nic nie czyta stałej, więc aktywny dobór Shorts już działa wg HARD AND-GATE; to relikt mogący zmylić przyszłego czytelnika kodu.
- **Proponowana poprawka:** Usunąć nieużywaną `SHORT_TYPES` (L66-72), albo opatrzyć komentarzem „legacy — niezgodne z aktualnym STEP 6 anti-archetyp".

### [LOW] Angielskie stałe _BRAND_USE / _BRAND_AVOID — relikt en-pipeline

- **Twierdzenie:** CLAUDE.md: pipeline po polsku, opublikowana kopia research-invisible; bany clickbaitu są w SOP STEP 1 po polsku (`08_publish.md` L62: „hack, sekret, szokująca prawda…").
- **Rzeczywistość:** `tools/pipeline/agent8_publish.py` L74-84 żyją angielskie `_BRAND_USE` (m.in. „research suggests", „studies show") i `_BRAND_AVOID` (m.in. „hack", „secret", „shocking truth"). Konsumpcja tylko w `_build_titles_prompt` (L138, czyta `_BRAND_AVOID`) i `_build_metadata_prompt` (L554) — obie na ścieżce `--api`. `_BRAND_USE` nie jest referencjonowane nigdzie (podwójnie martwe).
- **Werdykt:** Orphan (low). Relikt en-pipeline-v1, NIE sprzeczność z CLAUDE.md (CLAUDE.md opisuje rzeczywistość poprawnie); kandydat do usunięcia razem z resztą `--api`.
- **Proponowana poprawka:** Brak pilnej. Opcjonalnie odnotować w docstringu, że `_BRAND_USE`/`_BRAND_AVOID` są angielskie i dotyczą tylko ścieżki `--api` (relikt en-pipeline), by nie mylić operatora.

### [LOW] 06_images.md — przestarzały model renderera (gemini-3-pro-image-preview)

- **Twierdzenie:** CLAUDE.md L133: „Agent 6 (images). `gemini-2.5-flash-image` (tuned-flash v8, 2026-06-08; was `gemini-3-pro-image-preview`…)"; tabela wiersz 6: „Gemini 2.5 Flash Image (tuned-flash v8)".
- **Rzeczywistość:** Kod zgadza się z CLAUDE.md — `tools/pipeline/agent6_images.py` L345: `IMAGE_MODEL = "gemini-2.5-flash-image"`. Natomiast SOP `workflows/pipeline/06_images.md` — do którego CLAUDE.md L134 wprost kieruje operatora („Flags/rubrics: workflows/pipeline/06*.md") — w 5 miejscach podaje wycofany model: L6, L27, L138, L151, L278 („Gemini 3 Pro Image Preview" / „gemini-3-pro-image-preview"). Plik nosi też niezależny legacy-drift „Imagen" (np. L135 „Initialising Vertex AI Imagen", L81/L148 „**Imagen prompt:**").
- **Werdykt:** Stale (low). Staleness wyłącznie dokumentacyjny; renderer (kod) poprawny. Mylące są zwłaszcza noty o QPM/quota (L278) i szacunki czasu oparte na starym modelu.
- **Proponowana poprawka:** W `06_images.md` zamienić 5 wystąpień modelu (L6, 27, 138, 151, 278) na „gemini-2.5-flash-image (tuned-flash v8)" i dopisać, że 3-pro/4K zostaje wyłącznie w Agencie 7 (miniatury); opcjonalnie zaktualizować „Imagen"→Gemini. Bez zmian w kodzie ani CLAUDE.md.

### [LOW] Drzewo plików w CLAUDE.md pomija komendę /redaktor

- **Twierdzenie:** CLAUDE.md L60: „commands/ # Manual slash launchers: /draft /visuals /package /publish /animate".
- **Rzeczywistość:** `.claude/commands/` zawiera 6 komend: animate.md, draft.md, package.md, publish.md, **redaktor.md**, visuals.md. `redaktor.md` L2 ma frontmatter „description: Redaktor-uczeń — wzorce z docx-passów usera…" — to żywa komenda, spójnie opisana w samym CLAUDE.md niżej (L150 Quick Command Reference + sekcja L190). Wiersz drzewa L60 wymienia 5 z 6.
- **Werdykt:** Stale (low). Niekompletna lista poglądowa w drzewie, niespójna z resztą tego samego pliku; bez wpływu na działanie.
- **Proponowana poprawka:** CLAUDE.md L60: dopisać /redaktor → „Manual slash launchers: /draft /visuals /package /publish /animate /redaktor".

### [INFO] Drzewo plików w CLAUDE.md pomija agenta redaktor-kategoryzator

- **Twierdzenie:** CLAUDE.md L61: „agents/ # Cold /draft specialists: draft-{writer,section-checker,arc-checker,fixer} + /publish teammates: native-copy-critic + publish-{copywriter,seo,clips}".
- **Rzeczywistość:** `.claude/agents/` zawiera 9 plików; dziewiąty to **redaktor-kategoryzator.md** (frontmatter L2-3: „name: redaktor-kategoryzator", „Spawned cold by /redaktor", model: opus). Agent jest opisany w treści CLAUDE.md (paragraf Redaktor-uczeń, ~L190) i ma własny workflow. Wiersz L61 wylicza 8 z 9.
- **Werdykt:** Stale (info). Luka w kompletności opisowego wiersza inwentarza, nie sprzeczność funkcjonalna.
- **Proponowana poprawka:** CLAUDE.md L61: dopisać kategoryzatora, np. „… + publish-{copywriter,seo,clips} + /redaktor: redaktor-kategoryzator".

## Szkielet mechaniczny

> Uwaga procesowa: w przebiegu workflow `args` nie dotarł do skryptu, więc syntezator napisał pierwotnie, że szkielet „przekazany jako undefined". Poniższa sekcja została uzupełniona ręcznie deterministycznym skanerem (`.tmp/audit_refs.py`, v3 świadomy konwencji) **i domknięta dodatkowymi grepami** — jest autorytatywna.

**Integralność odwołań plikowych: ZDROWA.** Po odfiltrowaniu konwencji projektu (slug-relative `md/…`, basename pod `tools/`/`workflows/`, zewnętrzna auto-pamięć `project_*`/`feedback_*`, nazwy logiczne agentów/komend) z 242 unikalnych odwołań zostają **2 quasi-realne martwe**, oba benign:

- `outputs/videos_pl/emotional-dysregulation-in-adhd/md/00_materials_insights.md` (← `00_master.md`) — stary przykładowy slug; ten sam trop pokrywa finding [MEDIUM] o legacy `videos/` w `01_research.md`. Poprawka: zaktualizować przykład albo oznaczyć jako ilustracyjny.
- `docs/research/redaktor/` (← `redaktor.md`, CLAUDE.md) — katalog wyjściowy redaktora; tworzony przy **pierwszym** przebiegu `/redaktor`. **Oczekiwane**, nie błąd (ew. `.gitkeep`).

**`.tmp/08_*` — FAŁSZYWY ALARM (rozstrzygnięte).** Warianty wykryte przez skaner (`.tmp/08_x.md` vs `/.tmp/08_x.md` vs `1/.tmp/08_narration.md`) to fragmenty **tej samej** ścieżki `outputs/videos_pl/$1/.tmp/08_X.md`, pocięte na różnych granicach regexa. `publish.md` L75 podaje pełną ścieżkę, kroki 6/1-2/3/7-8/9 czytają i zapisują spójnie do `.tmp/08_{narration,copy,clips,signals,tags}.md`. Handoff jest poprawny — audytor publish słusznie tego nie zgłosił.

**Sieroty — niemal wszystkie FAŁSZYWE (skaner czytał tylko pliki-dokumenty, nie `.py`):**

- `00_materials_prompt.md` / `01_research_prompt.md` / `02_verify_prompt.md` — **NIE martwe duplikaty**: to aktywne szablony promptów ładowane przez kod (`agent0_materials.py` L29, `agent1_research.py` L32, `agent2_verify.py` L36). SOP-y `00_materials.md`/`01_research.md`/`02_verify.md` to wersje dla człowieka. Para SOP↔prompt jest celowa.
- `lib/phrase_mapper.py`, `lib/preview_writer.py` (i `aligner`/`fcpxml_writer`/`subtitle_chunker`) — importowane przez `agent_align.py` L34-52. Żywe.
- `mission_control/backlog_parser.py`, `pipeline_state.py` — moduły wewnętrzne Mission Control (server.py + testy). Żywe.
- `06b_image_qa.md` — SOP Agenta 6b; wzmiankowany skrótowo, koreluje z `agent6b_image_qa.py`. Żywy.

**Jedyna realna (semi-)sierota: `tools/dev/draft_ceiling_report.py`** — zbudowany i **otestowany** (`tests/test_ceiling_report.py`), opisany w brainstormie/planie Gen 5 jako „opcjonalny/rekomendowany", ale **niewpięty do operacyjnego CLAUDE.md** (brak w Quick Command Reference i w opisie pętli pomiarowej). Decyzja: albo dopisać jednowierszowo do CLAUDE.md (narzędzie pętli pomiarowej `04_final_machine.md` vs `script_corrected`), albo świadomie zostawić jako dev-only. Severity: low/info.

**Wniosek:** warstwa mechaniczna nie dorzuca żadnego High/Medium — potwierdza zdrowie odwołań i dokłada jedną drobną pozycję (`draft_ceiling_report.py` nieudokumentowany). 12 znalesisk semantycznych powyżej to pełny obraz.

## Czego NIE zmieniamy

- **Ścieżki slug-relative i auto-generowana ścieżka w skrypcie** — agenty zapisują do `outputs/videos_pl/{slug}/…` i to skrypt (nie SOP) tworzy realny katalog; nie „naprawiać" przykładów slugów w SOP-ach na sztywne nazwy.
- **Ścieżki `--api` jako celowo zamrożony fallback** — CLAUDE.md sam deklaruje je jako „inert; in-session slash commands are the default". Stale liczby/prompty w `--api` (Shorts 3–5, opis „exactly 5", `_BRAND_*`) to świadomie zachowany relikt; ich „naprawa" jest opcjonalna i porządkowa, nie pilna. Nie przepisywać `--api` na nowy kontrakt bez decyzji o losie całej ścieżki.
- **Boil kreski w animacji jako feature** (nie dotyczy bezpośrednio findings, ale typowy fałszywy alarm) — nie wygładzać; bugiem jest tylko misrejestracja całych obiektów.
- **Research po angielsku (Agenci 0/1/2)** — `01_research.md`/`02_verified_research.md` są celowo angielskie; problem w findingu dotyczy WYŁĄCZNIE nazwy katalogu (`videos/` → `videos_pl/`), nie języka.
- **Nazwa pliku `agent_align.py` bez numeru** — to satelita post-record, nie numerowany etap; nie „dopinać" numeru.

## Następny krok

Audyt jest **REPORT-ONLY** — poprawki to osobna bramka (zgodnie z kulturą projektu: report-only walidatory, manual gate na zmiany doktryny). Lista poprawek pogrupowana:

### (a) Trywialne / mechaniczne — inwentarze i martwe przykłady (low ryzyko, można zrobić hurtem)

1. CLAUDE.md L60 — dopisać `/redaktor` do listy launcherów.
2. CLAUDE.md L61 — dopisać `redaktor-kategoryzator` do listy agentów.
3. CLAUDE.md L136 — „5–8 multi-word tags" → „12–15 multi-word tags"; „description exactly 5 sentences" → „description ~5 sentences (~80–130 words)".
4. CLAUDE.md wiersz 8 tabeli + `publish.md` L193 — generatory = Sonnet 4.6, tylko 8d/lead = Opus 4.8 („three extra Sonnet generators + one Opus critic").
5. `01_research.md` ~L83 — `videos/` → `videos_pl/`.
6. `06_images.md` L6/27/138/151/278 — `gemini-3-pro-image-preview` → `gemini-2.5-flash-image (tuned-flash v8)`; opcjonalnie „Imagen"→Gemini.
7. `style_guide_images.md` L13/24/25/45/87 — wymienić kontrakt białego/transparent/khaki na sage-beige + dwa kolory + two_color; usunąć „Warm khaki-tan fill".

### (b) Wymagające decyzji — sieroty i martwy kod (skasować czy wpiąć / dopisać notkę)

1. `agent8_publish.py` L66-72 `SHORT_TYPES` — **skasować** (martwa, sprzeczna z anti-archetyp STEP 6) czy zostawić z komentarzem „legacy"? Rekomendacja: skasować.
2. `agent8_publish.py` L74-84 `_BRAND_USE` / `_BRAND_AVOID` — usunąć razem z resztą `--api` przy ewentualnym sprzątaniu legacy, czy zostawić z notką w docstringu? Decyzja zależy od losu całej ścieżki `--api`.
3. `agent8_publish.py` `--api` `run_metadata_pass` print 12–15 vs prompt 5–8 (L742/744 vs L676) oraz Shorts 3–5 (L322/358/361) — zdecydować: zsynchronizować `--api` do aktualnego SOP (12–15 / 8–10) czy oznaczyć cały blok `--api` jako zamrożony i odpuścić. Spójne z decyzją (b.2).

— Zalecenie ogólne: skoro wszystkie 5 Medium dotyczą **dokumentacji/etykiet** (nie zachowania), grupa (a) jest niskoryzykowna i warto ją wykonać jednym commitem; grupa (b) to wyłącznie kod `--api` i powinna czekać na jedną decyzję „sprzątamy czy zamrażamy legacy".
