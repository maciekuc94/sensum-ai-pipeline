# Konwencja nazw plików w slugu

Kanon nazewnictwa dla każdego folderu wideo w `outputs/videos_pl/{slug}/`. Jedno źródło prawdy — gdy nazwy się rozjeżdżają (stare slugi, backupy, pliki testowe), ten dokument rozstrzyga.

**Zasada główna:** `NN[litera]_<treść>.md`, gdzie **NN = numer agenta, który plik tworzy**, a `<treść>` opisuje zawartość jednoznacznie (bez kolizji między agentami).

## `md/` — wyjścia SOP

| Plik | Zawiera | Tworzy |
| --- | --- | --- |
| `01_research.md` | Dossier researchu (EN) | Agent 1 |
| `02_verified_research.md` | Zweryfikowany research (EN) | Agent 2 |
| `03a_draft.md` | Pierwszy pełny draft narracji (PL) | 3a pisarz |
| `03b_corrections.md` | Scalone uwagi korektorów | 3b |
| `iter/arc.md`, `iter/sek_NN.md` | Surowe notatki 3b (arc + per-sekcja) | 3b |
| `04_final.md` | Finalny skrypt maszyny | 3c fixer |
| `04_final_machine.md` | Nietykalny snapshot maszyny (pomiar sufitu) | /draft (kopia po fixerze) |
| `iter/fixer_skips.md` | Log pominięć fixera | 3c fixer |
| `05_image_prompts.md` | Prompty obrazków per-scena | Agent 5 |
| `05_phrases.md` | Pliki fraz do forced-alignment | Agent 5 |
| `06_qa.md` | Raport QA obrazków | Agent 6b |
| `07_package.md` | Strategie tytuł + miniatura | Agent 7 / Package |
| `07_package_prompts.md` | Prompty renderu miniatury (`## Thumbnail N`) | Agent 7 / Package |
| `08_publish.md` | Finalna paczka publikacyjna | Agent 8 |
| `script_corrected.md` | Skrypt po ręcznej korekcie (extract z `script_corrected.docx`) | user + extract |

### Dwie świadome „nietypowości" (nie bałagan — wynikają z logiki pipeline'u)

- **`04_final_machine.md` jest nietykalny** — snapshot wyniku maszyny do diffu ze `script_corrected`; nigdy nie nadpisywany, także przy migracjach nazewnictwa (Gen 5).
- **`script_corrected.md` jest bez numeru** — jest lustrem `script_corrected.docx`, który edytujesz w Wordzie. Spójność z nazwą docx > numeracja.

### Rozróżnienie, które kiedyś myliło

`05_image_prompts.md` (prompty obrazków per-scena, Agent 5) vs `07_package_prompts.md` (prompty renderu miniatury, Agent 7). Różne agenty, różny cel — nazwa mówi to wprost. (Historycznie oba nazywały się `05_prompts`/`07_prompts` — zmienione 2026-06-09.)

## Pozostałe foldery slugu

| Folder | Zawiera | Tworzy |
| --- | --- | --- |
| `docx/` | `script.docx` (Agent 4), `script_corrected.docx` (ręczna korekta usera), `05_phrases.docx`, `08_publish.docx` | Agent 4 / user / 5 / 8 |
| `images/` | `image_NNN.png` | Agent 6 |
| `thumbnails_no_grain/` | render miniatur (3-pro, ~4K) przed wykończeniem | Agent 7 |
| `thumbnails/` | wybrana miniatura + wersja `_2color_grain` (po finiszu) | Package finish + user |
| `voiceover/` | nagrane audio (`.wav`) | user (Studio One) |
| `edit/` | `subtitles.srt`, `timeline.fcpxml`, `preview.html`, `alignment.json`, `whisper_words.json` | Align |

## Co NIE jest kanonem (śmieci — kasujemy, nie trzymamy)

- `*.bak.md`, `*.bak.*` — backupy
- `*_squeezetest*`, `*_test*`, `*.full83.*` — pliki testowe
- `*.preCorrected.*` — warianty sprzed korekty
- `08_working.md` — roboczy plik /publish (zastąpiony przez `08_publish.md`)
- `08d_nativecopy_iter*.md` — iteracje Native-Copy Critica (zastąpione przez finalny `08_publish.md`)
- `*_bak/` (katalogi, np. `images_preCorrected_bak/`) — backupy całych serii
- `.tmp/` — disposable z definicji

**Uwaga:** `outputs/` jest w `.gitignore` (a także `.tmp/` i `*.bak.md`). Kasowanie w tych folderach jest **trwałe** — nie ma `git restore`. Pewności szukaj w kopiach chmurowych, nie lokalnie.

## Dryf historyczny — to jest OK

Stare slugi mogą mieć **luki** (brak `03b_corrections`/`iter/` — sprzed lean-chain z 2026-06-07) albo nazwy zretrofitowane do kanonu (jedynka: `04b_hook→04_hook`, `09_qa→06_qa`, `08b_thumbnail_concepts→07_package`). Nie regenerujemy historii — retrofitujemy tylko nazwy, których plik 1:1 odpowiada kanonowi.

## Bezpieczna zmiana nazwy kanonicznej (protokół anty-przeoczenie)

Nazwy plików w kodzie to **literały** (np. `OUTPUT_FILENAME = "md/05_image_prompts.md"`), duplikowane w wielu plikach — nie są składane z numeru agenta. Dlatego przy zmianie nazwy kanonicznej:

1. **Grep PRZED** repo-wide po starym literale → pełna lista trafień.
2. **Granica zmiany = kod + `.claude/` + `workflows/` + `CLAUDE.md`.** Wyklucz `brainstorms/` i `docs/superpowers/plans/` — to datowane zapisy historyczne; ich nie przepisujemy.
3. **Token-swap** (skryptem, nie modelem — taniej i pewniej niż ręczny replace), potem **grep PO** z oczekiwaniem zera trafień poza wykluczeniami.
4. **Wyczyść `__pycache__`** — stary `.pyc` może maskować literał.
5. **`py_compile`** na dotkniętych skryptach + zmień nazwy plików `md/` w istniejących slugach.
