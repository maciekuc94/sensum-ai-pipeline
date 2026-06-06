# Folder `.claude/`: commands vs skills — Brainstorm / Discovery Notes
Date: 2026-06-06 · Goal: zrozumieć różnicę commands↔skills, zdecydować czy/co migrować na skills, i czy skasować nieużywane zwykłe `/draft` i `/publish`

## Summary / key decisions
(aktualizowane na bieżąco)

- **Stan faktyczny `.claude/`** (zinwentaryzowany 2026-06-06):
  - `commands/` (7, user-invoked): `draft`, `draft-team`, `hook`, `package`, `publish`, `publish-team`, `visuals`
  - `agents/` (5, teammate'y dla wariantów -team): `native-ear-critic`, `native-copy-critic`, `publish-copywriter`, `publish-seo`, `publish-clips`
  - `skills/` (2, model-invoked): `grill-me`, `scientific-etching-guard`
- **Mental model (korekta mitu „skills są najlepsze"):** commands i skills to NIE konkurenci — to różne *wyzwalacze*.
  - **Command** = *TY* decydujesz kiedy (wpisujesz `/draft <slug>`). Świadome, deterministyczne, parametryzowane.
  - **Skill** = *CLAUDE* decyduje kiedy (dopasowuje `description` do sytuacji). Auto-ładowanie wiedzy/doktryny + może nieść własne pliki (references/, scripts/).
  - Hype o skills dotyczy tej drugiej kategorii: automatyczne wstrzyknięcie właściwej doktryny w odpowiednim momencie, bez pamiętania o komendzie. `scientific-etching-guard` to dokładnie to (auto-pilnuje stylu obrazów poza `/visuals`).
- **Czy migrować pipeline-commands → skills?** Wstępna teza: w większości NIE. Etapy pipeline'u (draft/hook/visuals/package/publish) są świadome, sekwencyjne, kosztowne (kredyty renderu, tokeny) — chcesz je odpalać ręcznie. Auto-inwokacja = ryzyko, że Claude odpali `/publish` gdy tylko o nim rozmawiasz.
- **Czy da się skasować samo `/draft` i `/publish`?** TAK, technicznie bezpiecznie:
  - `draft-team.md` / `publish-team.md` **nie importują** plików `draft.md`/`publish.md`. „Fall back to plain /draft" = *zachowanie* wpisane wprost w plik -team + czytane z `workflows/pipeline/` (`03a/03b/03c_*.md`, `08_publish.md`).
  - Koszt kasowania: (1) tracisz tańszą ścieżkę bez debaty zespołowej; (2) ~54 odwołań do `/draft` i ~72 do `/publish` w repo (głównie CLAUDE.md, wskaźniki „uruchom /draft najpierw", tabele) — część to martwe wskaźniki do posprzątania.

## Q&A log

### Q0 — Kontekst otwierający (z wiadomości użytkownika)
- Captured:
  - „Słyszałem że skills są najlepszą rzeczą w Claude, a dużo mam w commands." → mit do skorygowania (patrz mental model wyżej).
  - „Da się przerobić commands na skills? Czy jest sens?" → główne pytanie projektowe.
  - „Mam publish i publish-team, tak samo draft i draft-team. **Używam tylko teamów.** Da się pozbyć samego publish i samego draft?" → konkretny, wykonalny wątek.
- Flags: brak.

### Q1 — Kasować zwykłe /draft i /publish, czy zostawić jako tani fallback?
- Asked: opcje (1) skasuj oba teamy-only, (2) zostaw jako fallback, (3) scal w jedną komendę na etap
- Captured: użytkownik nie wybrał — zgłosił, że **nie rozumie różnicy 1 vs 3**. Doprecyzowuję (patrz niżej).
- Kluczowa różnica 1 vs 3:
  - **Opcja 1** = kasujesz `draft.md`/`publish.md`, ale **dalej wpisujesz `/draft-team`, `/publish-team`** (nazwa „-team" zostaje na zawsze). Zero przepisywania — tylko usunięcie 2 plików + naprawa wskaźników.
  - **Opcja 3** = zwijasz dwie komendy w jedną: wpisujesz **krótkie `/draft`, `/publish`**, a one **domyślnie robią zachowanie zespołowe** (panel native-ear). „-team" znika z nazw. Wymaga przeniesienia treści `draft-team.md`→`draft.md` + ewentualnej flagi `--solo` na tani tryb.
  - Obie kończą z **tą samą liczbą komend (5)**. Różnica = co WPISUJESZ i jak się nazywa.
- **DECYZJA: Opcja 3** — scalamy w jedną komendę na etap. Treść `draft-team.md`→`draft.md`, `publish-team.md`→`publish.md`; sufiks „-team" znika; `/draft slug` i `/publish slug` domyślnie robią zachowanie zespołowe (panel native-ear / native-copy). Krótkie nazwy.
- Flags: brak.

### Q2 — Zachować świadomą flagę --solo (tani tryb bez debaty), czy tylko niewidzialny auto-fallback?
- Asked: (czeka)
- Rozróżnienie:
  - **Auto-fallback** (zostaje zawsze, niewidzialny): gdy Agent Teams jest niedostępny/wysypie się, komenda po cichu robi zwykłe zachowanie in-session — nigdy nie utkniesz. To już jest wpisane w pliki -team (Step 1.5).
  - **Flaga `--solo`** (opcjonalna, świadoma): przełącznik „ten jeden run bez debaty, oszczędź tokeny". Skoro używasz tylko teamów — prawdopodobnie zbędna (YAGNI; można dodać w 2 min później).
- **DECYZJA: tylko auto-fallback** (użytkownik: „auto-fall back"). Bez świadomej flagi `--solo`. `/draft` i `/publish` zawsze celują w wersję zespołową; jedyna tania ścieżka to niewidzialny fallback gdy Agent Teams niedostępny.
- Flags: brak.
- (kontekst: w trakcie sesji włączono **ultracode** — planowanie/sprzątanie zrobimy workflow-em wieloagentowym po zamknięciu decyzji.)

### Q3 — Skills opportunity: guard-skill na głos skryptu (analog scientific-etching-guard, ale dla słów)?
- Asked: (czeka)
- Kontekst: to realny payoff „czy jest sens w skills". `scientific-etching-guard` auto-pilnuje stylu OBRAZÓW przy freeform poza `/visuals`. Analogiczna luka dla SŁÓW: gdy prosisz freeform „popraw ten akapit / napisz inne intro" BEZ `/draft`, żadna doktryna głosu nie ładuje się automatycznie. Kandydat: `script-voice-guard` ładujący research-invisibility + number policy + jargon policy + bezrodzajowość/ciepło, gdy Claude ma dotknąć prozy skryptu poza pipeline'm.
- **DECYZJA: najpierw zmierz lukę** (użytkownik wybrał „Najpierw zmierz lukę"). Workflow analityczny (4 agentów równolegle) → dane → user decyduje.
- Captured: decyzja odroczona do wyników workflow.
- Flags: czeka na wynik workflow → wtedy decyzja yes/no o `script-voice-guard`.

## Workflow analityczny (ultracode) — uruchomiony 2026-06-06
4 agentów równolegle (read-only), potem synteza lead-a:
1. **cross-ref-map** — każde odwołanie /draft /publish /draft-team /publish-team w repo, skategoryzowane + czy scalenie je urywa + fix. (pod Opcję 3)
2. **doctrine-gap** — doktryny głosu z CLAUDE.md + guides; zawsze-ładowane vs luka freeform; rekomendacja o `script-voice-guard` na danych. (pod Q3)
3. **folder-health** — pełny inwentarz `.claude/`, redundancje, złe kategoryzacje, inne usprawnienia.
4. **skills-bestpractice** — aktualne docs Claude Code: SKILL.md, triggering po description, progressive disclosure, skill vs command.

## WYNIKI WORKFLOW (2026-06-06) + nowy wymóg /btw

### Przełomowa odpowiedź na pytanie wyjściowe (z best-practices, oparte na docs)
**W aktualnym Claude Code (2025-2026) commands i skills to ZLANY mechanizm.** Plik `.claude/commands/X.md` ORAZ skill `.claude/skills/X/SKILL.md` — oba tworzą `/X` i działają tak samo. Komendy nadal działają, ale **skille to forma rekomendowana**, bo dodają: (1) auto-inwokację po `description`, (2) teczkę plików wspierających (`references/`, `scripts/`), (3) bogatszy frontmatter (`disable-model-invocation`, `user-invocable`, `when_to_use`, `context: fork`, `arguments`). → Realna różnica to nie „command vs skill", tylko **„tylko-ręczny vs auto-inwokowalny przez model".** „Command" = po prostu skill, który odpalasz tylko ręcznie. Źródła: docs.claude.com/claude-code/skills + /agent-skills/best-practices.

→ **Odpowiedź na „da się przerobić commands na skills? sens?":** TAK, trywialnie, i sens = odblokowuje auto-inwokację (twoje /btw!) + pliki wspierające. Dla etapów z efektami ubocznymi (render/publish) trzymasz je ręczne LUB z guardem-potwierdzeniem (jak render-images), więc nie tracisz świadomej kontroli.

### NOWY WYMÓG (z /btw, 2026-06-06): natural-language routing
User: „zależy mi, żebym mógł np. napisać »wygeneruj grafiki dla slugu 2« i będziesz wiedział o co mi chodzi — uruchomisz odpowiednią procedurę." → To jest DOKŁADNIE use-case skilli (auto-inwokacja po `description`). Reframe: prawdziwy cel sesji to nie tylko „odchudzić .claude", ale **sterowanie naturalnym językiem zamiast pamiętania slashy.** Merge (Opcja 3) to podzbiór; routing-skille to główne danie.

### ⚠️ ZDARZENIE: forkowany agent /btw SAM utworzył plik (flag bezpieczeństwa)
- `/btw` odpalił osobny agent w tle (fork fa3b), który **utworzył `.claude/skills/render-images/SKILL.md`** (3751 B, uncommitted) — i SAM oznaczył to SECURITY WARNING: self-modification konfiguracji startowej bez wyraźnego „stwórz skill". User wyraził *życzenie*, nie polecenie budowy.
- Treść pliku jest SOLIDNA: rozwiązuje slug po numerycznym prefiksie (`2_*`), sprawdza prerekwizyty (05_prompts→/visuals→agent6), **wymusza potwierdzenie przed kredytami** (Agent 6 = manual w doktrynie), nie duplikuje doktryny stylu, honoruje „po prostu odpal".
- **DECYZJA DO PODJĘCIA:** zostawić / poprawić / usunąć ten plik. (Merytorycznie OK; pytanie proceduralne + czy chcemy ten wzorzec.)

### cross-ref pod scalenie (Opcja 3) — 71 odwołań, 15 plików do edycji
- **PUŁAPKA #1 (najważniejsza):** dziś „/draft"/„/publish" = TANIA wersja solo; „-team" = zespołowa. Opcja 3 ODWRACA semantykę. Każde zdanie kontrastujące obie komendy („zwykłe /draft/publish tańszym defaultem", „Fallback: plain /draft") staje się FAŁSZYWE → PRZEPISAĆ na „auto-fallback in-session gdy Agent Teams niedostępny", nie tylko podmienić nazwę.
- **PUŁAPKA #2:** scalony draft.md/publish.md MUSI zachować Step 1.5 (graceful fallback) — to jedyna tania ścieżka po „bez --solo". „Fall back to plain /draft" → „fall back to fully in-session (no team)" (samoodwołanie = pętla).
- **PUŁAPKA #3:** `.claude/agents/*.md` mają „/draft-team"/„/publish-team" w YAML `description:` + body („spawned by /publish-team") → podmienić na „/draft"/„/publish". Pliki agentów ZOSTAJĄ.
- **PUŁAPKA #4:** wzmianki o parserze werdyktu (03d/08d) — podmienić nazwę komendy, NIE ruszać kontraktu PASS/FLAG/NATIVE.
- BEZPIECZNE (zero zmian): wszystkie „run /draft first" (hook/visuals/package/publish), docstringi .py, settings.local.json.
- NIE EDYTOWAĆ (artefakty datowane): docs/archive + docs/superpowers plany/specy, ten brainstorm, 2026-06-05-hook-first-seconds.md. Ewentualnie nagłówek „SUPERSEDED".
- Pliki do edycji: CLAUDE.md (tabele Quick Ref + Agent Chain + proza), draft.md, publish.md, 5×agents/, 03d_native_ear, 08d_native_copy, 03_architecture_select, docs/agent_teams_reference, docs/pipeline_teardown(.md+.docx re-eksport). + USUNĄĆ draft-team.md, publish-team.md.

### doctrine-gap (Q3) — REKOMENDACJA: TAK, dodać guard, ale CIENKI (pointer, nie kopia reguł)
- Dane (freeform-frequency proxy): outputs/ jest gitignored, ale na dysku **2/2 wyprodukowanych filmów ma ręcznie poprawiony plik prozy POZA slashem** (slug1 `06_narration_corrected.md`, slug2 `script_corrected.md`, 3.5–24% tekstu przepisane ręcznie). To DESIGNED, powtarzalny etap (voice_corpus §B/§E cytuje te diffy; /visuals+/publish+align auto-wykrywają corrected). → freeform edycja prozy jest realna i cykliczna.
- Kluczowy argument: obrazy mają 3 deterministyczne bezpieczniki (STYLE_SUFFIX, _enforce_background_color, QA 6b) — proza freeform poza /draft ma ZERO (gates 3b/3c/3d działają tylko wewnątrz slasha). Najwyższe ryzyko: research-invisibility, Permission Practice (proza/rejestr), bezrodzajowość (formy męskie), one-metaphor/attention-imperative (budżet całoskryptowy). Ich szczegół egzekucji (blocklisty kalek, pary korekcyjne §G, anti-patterns) jest lazy-loaded w guides, NIE w always-loaded CLAUDE.md.
- **WARUNEK:** guard MUSI być cienki (non-negotiables + protokół „flag-conflict-once" + wskaźniki „otwórz voice_corpus §B/C/G + style_guide §4/11/12"), NIE zamrożona kopia reguł — bo doktryna głosu wciąż się zmienia tygodniowo (kopia by zgniła i kłóciła się z guides). Zbudowany jako fork reguł = dług; jako pointer = wysoka wartość.

### folder-health — findings (poza scaleniem)
- **HIGH:** `allowed-tools` w draft-team/publish-team deklarują nieistniejący token `Agent`; brakuje `TeamDelete`/`Task*`/`Monitor` (teardown/spawn/wait). Po scaleniu draft.md/publish.md MUSZĄ dostać poprawny superset narzędzi Teams — inaczej „domyślnie zespołowo" cicho degraduje do solo. (Zweryfikować realne nazwy przez ToolSearch.)
- **HIGH:** `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` siedzi tylko w settings.local.json (per-maszyna, gitignored). Po Opcji 3 zespół = default komendy → przenieść env do commitowanego `.claude/settings.json`, inaczej po świeżym klonie /draft cicho leci solo.
- **MED:** opis (description) scalonych draft/publish trzeba przepisać, by wspominał tryb zespołowy (pokazuje się w /help i liście skilli). Niespójność języka EN/PL w draft-team (Step 4+ po polsku) — ujednolicić w scalonym pliku.
- **LOW:** martwe wpisy `gh.exe ... repo create` w permissions.allow — usunąć. Brak guarda voice = ta sama luka co etching-guard dla obrazów (zgodne z rekomendacją doctrine).
- Reszta folderu ZDROWA: 0 osieroconych agentów, 0 martwych referencji do workflowów, kategoryzacja command/skill/agent poprawna (nic nie trzeba przenosić).

### Q4 — Zakres routerów naturalnego języka
- **DECYZJA: render-images jako wzór + rozwinąć na WSZYSTKIE etapy.** Pełne sterowanie naturalnym językiem. render-images ZOSTAJE (do przeglądu/dopracowania). Robimy analogiczne routery: „napisz skrypt dla…"→draft, „opublikuj…"→publish, „zrób miniaturę…"→package, „oceń hook…"→hook.
- Flags: pozostaje fork PROJEKTOWY jak je zrobić (osobne router-skille vs wzbogacić istniejące komendy o triggery) — Q5.

### Q5 — Design routerów
- **DECYZJA: A — osobne cienkie routery per etap** (jak render-images). Komendy /draft /publish zostają ręcznymi playbookami; auto-odpalanie + confirm-gate w cienkiej warstwie routera. Bezpieczne.
- Routery do zbudowania: render-images (jest), draft-router („napisz/stwórz skrypt dla…"), publish-router („opublikuj…/zrób opis dla…"), package-router („zrób miniaturę/okładkę dla…"), hook-router („oceń hook dla…"). Każdy ~30 linii, confirm na kosztownych (package/render).

### Q6/Q7 — decyzje końcowe
- **Q6: TAK** — zbudować cienki `native-voice-guard`. **Q7: buduj wszystko teraz (ultracode).**

## WYKONANO (2026-06-06)
**Nowe skille (6):** `render-images` (zostawiony jako wzór + `user-invocable:false`), `write-script`, `score-hook`, `package-thumbnail` (confirm-gate na kredyty), `publish-package`, `native-voice-guard`. Wszystkie routery `user-invocable:false` (łapią naturalny język, nie zaśmiecają menu `/`).
**Scalenie (Opcja 3):** `draft-team.md`→`draft.md`, `publish-team.md`→`publish.md` (team = default, auto-fallback in-session, allowed-tools +TeamDelete, pułapki semantyczne #1–4 naprawione), oba pliki `-team` USUNIĘTE.
**Cross-ref:** 5×agents/ (description+body), 03d/08d (rename + semantyczna L24), 03_architecture_select (dedupe), CLAUDE.md (File Structure, sekcja Agent Teams, tabela Quick Ref, tabela Agent Chain), docs/agent_teams_reference.md (nagłówki + fallback + ścieżki). Weryfikacja: **0 `-team` w runtime + kanonicznym reference.**
**Override workflow:** zachowano `Agent` w allowed-tools (workflow błędnie twierdził, że nie istnieje — to realne narzędzie tego harnessu).
**Pominięte świadomie:** docs/pipeline_teardown.md(+.docx) — datowana analiza-snapshot, zostawiona jak superpowers specs (nie fałszować historii); martwe wpisy gh.exe w permissions (LOW, nie ruszam allowlisty bez potrzeby).

## ⚠️ NOWY FLAG (wykryty w weryfikacji): całe `.claude/` jest w `.gitignore` (linia 9)
- Konsekwencja: **cała ta praca (scalenie + 6 skilli + settings) jest LOKALNA — niewersjonowana.** Działa na tej maszynie, ale nie trafia do gita; świeży klon / inna maszyna jej nie ma.
- **Unieważnia fix HIGH o settings.json:** przeniesienie env do `.claude/settings.json` NIE daje „commitowalności" (settings.json też ignorowany). Działa lokalnie, ale nie rozwiązuje reprodukowalności po świeżym klonie. (Zostawione — nieszkodliwe, czystszy podział env vs permissions.)
- **Decyzja dla użytkownika (follow-up):** czy odignorować część `.claude/` w `.gitignore` (np. `commands/`, `skills/`, `agents/`, `settings.json`), trzymając `settings.local.json` ignorowany — żeby cała ta warstwa była wersjonowana i przeżyła reklon? To zmiana polityki gitignore — Twoja decyzja.

## Open flags (pending input)
- **.gitignore policy** — wersjonować `.claude/` config czy zostawić lokalnie? (patrz wyżej)
- **Restart sesji** — menu `/` odświeży nowe/usunięte komendy dopiero po restarcie Claude Code.
- **Test routerów** — w nowej turze napisać „wygeneruj grafiki dla slugu 2" / „napisz skrypt dla dwójki" by potwierdzić auto-inwokację.
