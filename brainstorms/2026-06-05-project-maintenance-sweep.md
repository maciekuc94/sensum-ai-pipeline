# Przegląd konserwacyjny projektu (trash sweep): Notatki z grill-me
Data: 2026-06-05 · Cel: Przejść projekt, zdecydować KEEP / DELETE / ARCHIVE; zbudować powtarzalną rutynę „wyrzucania śmieci". Właściciel = minimalista, nie znosi nieużywanych rzeczy w pipeline.

## Status: WYKONANE ✔ (z uwagą o równoległej sesji gita — patrz „Log egzekucji")

## Log egzekucji (2026-06-05)
- ✔ **Tier A skasowany** (zweryfikowano: 0 pycache, 0 iter, 0 bak): 5× `__pycache__`, `.tmp/instrukcje dla agenta.txt`, `videos_pl/2_why.../.tmp/`, 2× `.bak.md`, 18× iteracje `03{b,c,d}_*_iter*.md`.
- ✔ **Intel skasowany**: `outputs/intelligence/thumbnails/` + `2026-W21_niche_intelligence.pptx`. Zachowane: `intelligence.db`, `cost_log.json`, `2026-W21_tag_signals.md`.
- ✔ **posterize_thumbnails.py** — `git rm` (już w commicie równoległej sesji).
- ✔ **Archiwum** → `docs/archive/`: architecture_review.md, inspiration_log.md, 2026-05-15-15-second-hook-research.md (git mv) + `docs/archive/superpowers/` 5 plików (2 tracked git mv + 3 untracked mv). Puste `docs/superpowers/` i `docs/specs/` usunięte.
- ✔ **requirements.txt** += matplotlib, python-pptx, faster-whisper, soundfile. (NIE ruszone: aiplatform, oauthlib.)
- ✔ **videos_en (4 GB)** → robocopy do `D:\ClaudeCode\SENSUM EN` (puste, utworzone wcześniej). Weryfikacja: **1235 plików / 4 289 622 842 B po obu stronach — ZGODNE**. Oryginał usunięty po weryfikacji.
- ✔ **brainstorm fluency-first-chain** — zostawiony.

### ⚠ Uwaga: równoległa aktywność gita
W trakcie sesji branch `feat/package-agent` przeskoczył `e3a3b9b → 4422c68` (liniowo) commitami `fix(publish)`/`fix(intel)`, których ta sesja NIE robiła. Inna sesja/terminal robi `git add -A && commit` i **wciągnęła moje staged zmiany** (git rm posterize + git mv archiwum) do swoich commitów. Skutek: nieszkodliwy, ale:
- `requirements.txt` (moja zmiana) wciąż uncommitted — może trafić do następnego commitu tamtej sesji z niepasującym opisem.
- 3 untracked pliki w `docs/archive/superpowers/` czekają na `git add`.
- **Rekomendacja:** sprawdź, czy nie masz drugiej aktywnej sesji Claude w tym repo; zacommituj `requirements.txt` + `docs/archive/superpowers/*` osobno, świadomym opisem.

### Bilans miejsca
- Projekt schudł o **~4.0 GB** (videos_en) + ~8.6 MB (intel) + ~0.35 MB (Tier A).
- Dysk D: netto wolne: **~9 MB** (videos_en tylko przeniesione na tym samym D: do `SENSUM EN`). Żeby odzyskać 4 GB z D:, przenieś `SENSUM EN` na inny dysk/chmurę.
- `outputs/` po: channel_assets 207M, videos_pl 475M, intelligence 1.1M.

## Podsumowanie / kluczowe decyzje
(aktualizowane na bieżąco)
- **DELETE Tier A** (cała pewna śmieciarka) — ZATWIERDZONE: pycache×5, .tmp, *.bak.md×3, iteracje 03*_iter*×18, posterize_thumbnails.py.
- **videos_en (4 GB)** — ARCHIWIZUJ NA ZEWNĄTRZ → potem USUŃ. ⚠ Brak jeszcze miejsca docelowego (flaga).
- **Scratch plany/specy** (superpowers plans+specs, stary spec, inspiration_log, architecture_review) — ARCHIWIZUJ do `docs/archive/` (nie kasuj).
- **Rutyna** — NIE buduję teraz. Jednorazowy przegląd. (Można wrócić później.)

## Ustalenia z gita (fakty, nie do dyskusji)
- `outputs/` → **w .gitignore w całości**. Wszystko pod `outputs/` istnieje TYLKO na dysku. Kasowanie nieodwracalne (brak siatki bezpieczeństwa gita).
- `videos_en` (4 GB) → NIE w gicie, NIE w tagu `en-pipeline-v1`. Reversibility pipeline'u od niego NIE zależy.
- `*.bak.md`, `__pycache__/`, `.tmp/` → gitignored. Kasowanie = czysty delete.
- `tools/dev/posterize_thumbnails.py` → JEST w gicie (odzyskiwalny z historii).
- tag `en-pipeline-v1` istnieje (przywraca KOD pipeline'u, nie rendery).

## Inwentarz kandydatów (baza dowodowa z 3 sond eksploracyjnych)

### TIER A — Pewna śmieciarka (regenerowalna lub z żywą kopią)
| Pozycja | Co | Rozmiar | Dowód |
|---|---|---|---|
| `__pycache__/` ×5 | bytecode Pythona | ~248 KB | auto-regen |
| `.tmp/instrukcje dla agenta.txt` | scratch | 2.6 KB | .tmp disposable |
| `outputs/videos_pl/2_why.../.tmp/` | scratch | 8.3 KB | .tmp disposable |
| `*.bak.md` ×3 (04_final.bak, 07_prompts_dense.bak) | backupy | ~24 KB | żywa kopia istnieje |
| `03b/03c/03d_*_iter*.md` ×18 | pośrednie iteracje scenariusza | ~73 KB | finał 04_final.md istnieje |
| `tools/dev/posterize_thumbnails.py` | osierocony filtr posterize | — | 0 referencji; w gicie (odzyskiwalny) |

### TIER B — Wielka decyzja (nieodwracalna)
| Pozycja | Co | Rozmiar | Uwaga |
|---|---|---|---|
| `outputs/videos_en/` | 6 gotowych ang. filmów (dormant kanał @hello.sensum) | **4.0 GB** | tylko na dysku; pipeline reversibility niezależny |

### TIER C — Osąd użytkownika (małe)
| Pozycja | Co | Werdykt sondy |
|---|---|---|
| `docs/superpowers/plans/` + `specs/` (5 plików, m.in. package-agent, pipeline-teardown, hook-first-seconds — z dziś) | robocze plany/specy, untracked | scratch — aktywne czy skończone? |
| `docs/specs/2026-05-15-15-second-hook-research.md` | stary spec, untracked | nie referencjonowany |
| `workflows/guides/inspiration_log.md` | log pomysłów na tematy | nie referencjonowany |
| `docs/architecture_review.md` | dok przeglądu architektury | w gicie, ale nie w CLAUDE.md — żywy czy porzucony? |
| `brainstorms/2026-06-05-fluency-first-chain.md` | brainstorm z dziś, untracked | commit czy scratch? |
| `outputs/intelligence/thumbnails/` | ~450 screenshotów YT (tydz. 21) | 8.1 MB — prune stare tygodnie? |
| `outputs/intelligence/2026-W21_niche_intelligence.pptx` | tygodniowe slajdy | regenerowalne z .db |

### KEEP — celowo (NIE ruszać)
- Pliki `.en.md` + `docs/reversibility.md` (ścieżka przywracania EN)
- Legacy `--api` ścieżki: `agent3.py`, `agent3b_revisor.py`, `agent3c_reviewer.py` + warianty w 4/5/8
- `outputs/channel_assets/` (brand, 206 MB), `intelligence/intelligence.db`, `cost_log.json`
- Wszystkie żywe komendy/workflow/guide/agenci/skille (37 plików — w pełni podłączone)
- `tools/research_sources.py` (importowany przez agent1), `utils.py`, `add_grain.py`, `tools/intelligence/*`, `tools/pipeline/lib/*`, `agent_align.py`

## Log Q&A

### Runda 1 (4 pytania)
- **EN 4 GB** → „Zarchiwizuj na zewnątrz, potem usuń". Świadomy nieodwracalności; reversibility pipeline'u niezależny. → potrzebne miejsce docelowe.
- **Śmieci Tier A** → „Skasuj wszystko". Pełna zgoda na całą partię.
- **Scratch plany/specy** → „Zarchiwizuj do docs/archive/". Nie kasować — przenieść.
- **Rutyna** → „Nie, tylko ten przegląd". Bez /cleanup i bez /schedule na teraz.

### Runda 2 (4 pytania)
- **EN backup → dokąd** → `D:\ClaudeCode\SENSUM EN` (kopia tam, weryfikacja, potem usunięcie oryginału). Uwaga: ten sam dysk D: → 4 GB dalej zajęte na D:, ale POZA projektem (cel: out of pipeline ✔).
- **Intel śmieci** → „Skasuj oba" — `outputs/intelligence/thumbnails/` (~8.1 MB) + `2026-W21_niche_intelligence.pptx`. Zostają: .db, cost_log.json, tag_signals.md.
- **Brainstorm fluency-first-chain** → „Zostaw w brainstorms/". KEEP (poza pipeline'em, konwencja grill-me).
- **Backstop** → „Tak — zależności Pythona". Dodatkowy przegląd nieużywanych pakietów przed egzekucją.

### Runda 3 — przegląd zależności (requirements.txt vs faktyczne importy)
Wynik: **brak grubego pakietu do wyrzucenia**; problemem jest niekompletny manifest.
- **USED + declared (OK, 9):** google-genai, requests, python-dotenv, python-slugify, Pillow, python-docx, pdfplumber, google-api-python-client, numpy.
- **IMPORTOWANE, ale NIE w requirements.txt (4 — luka reprodukowalności, do DODANIA):** `matplotlib` + `python-pptx` (slide_builder), `faster-whisper` (aligner), `soundfile` (fcpxml_writer). Świeży `pip install -r` nie postawiłby Intelligence ani Align.
- **DECLARED bez importu (2 — możliwe zbędne, NISKIE zaufanie):** `google-cloud-aiplatform`, `google-auth-oauthlib`. Wszystkie Gemini idą przez `google.genai (vertexai=True)`; oauthlib bez śladu. Ryzyko: transitive auth Vertex/YouTube. Rekomendacja: NIE usuwać bez testu na czystym venv.

### Runda 4 (finał)
- **Deps** → „Dodaj 4 brakujące, 2 niepewne zostaw". requirements.txt += matplotlib, python-pptx, faster-whisper, soundfile. google-cloud-aiplatform / google-auth-oauthlib NIE rusza (ryzyko auth).
- **Egzekucja** → „Tak — wykonaj wszystko". Commit gita zostawiony userowi (nie commituję bez prośby).

## Otwarte flagi (po grillingu)
- (rozwiązane) wszystkie decyzje podjęte.
- Po egzekucji zostają STAGED zmiany gita (git rm posterize + git mv archiwum) — do commitu przez usera.
- 2 niepewne deps (aiplatform, oauthlib) — opcjonalny test na czystym venv kiedyś.

## Decyzje (bufory na czysto)
- **DELETE (Tier A, zatwierdzone):** `tools/__pycache__/`, `tools/dev/__pycache__/`, `tools/pipeline/__pycache__/`, `tools/pipeline/lib/__pycache__/`, `tools/intelligence/__pycache__/`, `.tmp/instrukcje dla agenta.txt`, `outputs/videos_pl/2_why.../.tmp/`, wszystkie `outputs/videos_pl/**/*.bak.md` (×2 — sondy mówiły 3, realnie 2), wszystkie `outputs/videos_pl/**/03{b,c,d}_*_iter*.md` (×18), `tools/dev/posterize_thumbnails.py` (git rm).
- **DELETE (po archiwizacji do `D:\ClaudeCode\SENSUM EN`):** `outputs/videos_en/` (4 GB).
- **DELETE (Intel):** `outputs/intelligence/thumbnails/`, `outputs/intelligence/2026-W21_niche_intelligence.pptx`.
- **KEEP (potwierdzone):** `brainstorms/2026-06-05-fluency-first-chain.md`, `intelligence/intelligence.db`, `cost_log.json`, `2026-W21_tag_signals.md`.
- **ARCHIVE → docs/archive/:** `docs/superpowers/plans/*` + `specs/*`, `docs/specs/2026-05-15-15-second-hook-research.md`, `workflows/guides/inspiration_log.md`, `docs/architecture_review.md`.
- **KEEP:** wszystko z sekcji „KEEP — celowo" powyżej.
