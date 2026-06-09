---
name: grain_thumbnail
description: Use when the user asks in plain language to apply the SENSUM thumbnail finish — two-colour + coarse grain (s2/i18) — to an EXISTING thumbnail file given its path. Polish triggers like "dodaj grain do <ścieżka>", "dograinuj miniaturę <plik>", "ziarno do thumbnaila <plik>", "wykończ miniaturę", "zrób finish miniatury", "two_color i grain do <plik>", or English "add grain to <thumbnail path>", "finish this thumbnail". The user names a concrete PNG file/path. DISTINCT from package-thumbnail (which DESIGNS / renders a new thumbnail and costs credits) — this skill post-finishes one already-rendered thumbnail before Canva, locally, with no API cost. Routes to tools/dev/finish_thumbnail.py.
user-invocable: false
---

# Grain Thumbnail — naturalny finish miniatury (two_color + grubsze ziarno)

Pozwala **mówiąc po ludzku** („dodaj grain do `<ścieżka>`") wykończyć JEDNĄ
miniaturę zgodnie z doktryną **SENSUM thumbnail finish** (`07_package.md` →
Post-production): najpierw snap do dwóch kolorów marki, potem grubsze ziarno
`s2/i18`, jeszcze **przed Canvą**. Operacja lokalna, deterministyczna, **bez
kredytów**.

## Krok 0 — Ustal plik
User podaje ścieżkę do PNG (np. `outputs/videos_pl/<slug>/thumbnails/<nazwa>.png`).
- **Ścieżka podana** → użyj jej wprost.
- **Sam slug / brak ścieżki** → wylistuj `outputs/videos_pl/<slug>/thumbnails*/`
  i zapytaj, który plik (zwykle wybrana miniatura w `thumbnails/`, albo surowy
  `thumbnails_no_grain/thumbnail_0N.png`).

## Krok 1 — Sprawdź plik
Potwierdź, że plik **istnieje** i jest **`.png`**. Jeśli nie — zatrzymaj się
i powiedz userowi (nie zgaduj innego pliku).

## Krok 2 — Odpal finish
Domyślnie zapis do **kopii `_final`** (oryginał nietknięty — grain jest
nieodwracalny):
```bash
PYTHONIOENCODING=utf-8 python tools/dev/finish_thumbnail.py "<ścieżka>"
```
- User chce **nadpisać** oryginał → dodaj `--in-place`.
- User chce **konkretną nazwę** wyjścia → `--out "<ścieżka>"`.

## Krok 3 — Zaraportuj
- co zrobił finish: **two_color** (snap do #582F0E / #F4E5CA — sanity: 2 kolory)
  → **add_grain i18/s2**,
- **ścieżkę wyniku**,
- przypomnienie: do Canvy idzie **tylko napis** (overlay) w wolnej przestrzeni;
  **ziarno jest już wpieczone — nie dodawać grain w Canvie**.

## Uwagi
- **Zakres jest stały: `two_color` → `grain s2/i18`** (kanon `07_package.md`).
  To NIE jest ziarno body-image (`i12/s1`) — miniatura przy ~4K potrzebuje
  grubszego ziarna (cell ~2 px), bo drobne ziarno znika po downscale YouTube.
- Grain idzie **na** render zsnapowany do dwóch kolorów, nie na surowy
  (native bywa ~800 kolorów) — dlatego two_color jest pierwszy.
- To **nie projektuje** miniatury — od projektu/renderu jest `package-thumbnail`
  / `/package`. Ten skill **wykańcza** już gotowy plik.
- **Instrukcje usera biją skill:** jeśli wprost poda inną intensywność/skalę,
  każe nadpisać in-place albo pominąć kopię — zastosuj się.
