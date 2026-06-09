---
name: render-images
description: Use when the user asks in plain language (no slash command) to generate / render / create the illustration images for a SENSUM video — Polish triggers like "wygeneruj grafiki", "zrób obrazki", "grafiki dla slugu", "wyrenderuj obrazy", "zrób grafiki do filmu", "obrazki do", or English "generate/render images", optionally naming the video by number ("slug 2", "dwójka", "drugi film") or by folder-name fragment. Routes the Agent 5 → Agent 6 image procedure: resolves the slug, checks prerequisites, and ALWAYS confirms before spending render credits (Agent 6 is manual by doctrine).
user-invocable: false
---

# Render Images — naturalny router procedury obrazów

Ten skill pozwala odpalić pipeline ilustracji **mówiąc po ludzku**
(„wygeneruj grafiki dla slugu 2") zamiast pamiętać `/visuals` + komendę Agenta 6.
Rozpoznaje intencję → uruchamia właściwą procedurę, ale **nigdy nie wydaje
kredytów renderu bez potwierdzenia.**

## Krok 0 — Rozwiąż slug
Slugi to foldery w `outputs/videos_pl/` z **numerycznym prefiksem**:
`1_czujesz_ze_jestes_w_tyle`, `2_why_you_can_t_stick_to_anything`,
`3_wstyd_za_wlasne_zycie`, `4_jak_dziecinstwo_wplywa_na_zwiazek`, …
- Samo liczba („slug 2", „dwójka", „drugi") → folder, którego nazwa zaczyna się od
  tej liczby + `_`. **Potwierdź rozwiązaną nazwę folderu jedną linią** zanim ruszysz dalej.
- Fragment nazwy → dopasuj do listy (`ls outputs/videos_pl/`).
- Niejednoznaczne / brak trafienia → wylistuj dostępne slugi i zapytaj który. (To
  **jedyne** dozwolone dopytanie — tożsamość slugu musi być pewna przed renderem.)

## Krok 1 — Sprawdź warunki wstępne (procedura to łańcuch)
Render obrazów (Agent 6) potrzebuje promptów (Agent 5), które potrzebują finalnego
skryptu. Sprawdź w tej kolejności dla `outputs/videos_pl/<slug>/`:
1. Jest `md/05_image_prompts.md` z rozwiniętymi wpisami `**Imagen prompt:**` → gotowe na Agenta 6.
2. Brak `05_image_prompts.md`, ale jest `md/04_final.md` (lub `docx/script_corrected.docx`) →
   najpierw uruchom `/visuals <slug>` (Agent 5), potem przejdź do Agenta 6.
3. Brak `04_final.md` → zatrzymaj się; powiedz userowi, że trzeba najpierw
   `/draft <slug>` (i `/hook <slug>`).

## Krok 2 — POTWIERDŹ przed wydaniem kredytów (nienegocjowalne)
Agent 6 jest oznaczony w CLAUDE.md jako „manual — never run automatically", a render
kosztuje kredyty obrazowe Gemini. Przed uruchomieniem pokaż userowi:
- rozwiązany slug,
- ile obrazów powstanie (policz bloki `**Imagen prompt:**` w `05_image_prompts.md`),
- dokładną komendę, którą zaraz odpalisz,
i uzyskaj wyraźne „tak". **Nie renderuj na cichym założeniu.**

## Krok 3 — Wykonaj procedurę
Po potwierdzeniu, z korzenia repo:
```bash
# (tylko jeśli brak 05_image_prompts.md) najpierw Agent 5:
/visuals <slug>
# Agent 6 — render (domyślnie auto-odpala Agent 6b QA --retry, chyba że --skip-qa):
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --generate
```
- Re-roll tylko wybranych nieudanych obrazów? Użyj `--indices "22,26,97"` (1-based,
  nadpisuje w miejscu) zamiast pełnego re-renderu.
- Wynik ląduje w `outputs/videos_pl/<slug>/images/`; werdykty QA w `md/06_qa.md`.

## Krok 4 — Zaraportuj
Powiedz userowi: rozwiązany slug, liczba wygenerowanych obrazów, gdzie wylądowały
i które ewentualnie oblały QA 6b (do re-rolla przez `--indices`).

## Uwagi
- Doktryna stylu (paleta dwukolorowa, Scientific Etching, brak tekstu) należy do
  `scientific-etching-guard` + `STYLE_SUFFIX` — ten skill jej **nie powtarza**, tylko
  routuje procedurę.
- **Instrukcje usera biją ten skill:** jeśli wprost powie „po prostu odpal, bez
  pytania", pomiń potwierdzenie z Kroku 2 ten jeden raz.
```
