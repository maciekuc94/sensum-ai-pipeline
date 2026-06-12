---
name: two-color-thumbnail
description: Use when the user asks in plain language to snap an EXISTING thumbnail/image to the two SENSUM brand colours WITHOUT grain, given its path. Polish triggers like "zrób two color z <plik>", "two_color na <plik>", "dwukolor <plik>", "snap do dwóch kolorów", "zbij do dwóch kolorów", or English "two-color this thumbnail", "snap to brand colours". The user names a concrete PNG file/path. DISTINCT from grain-thumbnail (which adds the coarse grain s2/i18 — the step AFTER this one) and from package-thumbnail (which DESIGNS / renders a new thumbnail and costs credits). Local, deterministic, no API cost. Routes to tools/dev/finish_thumbnail.py --two-color-only.
user-invocable: false
---

# Two-Color Thumbnail — snap miniatury do dwóch kolorów marki (bez ziarna)

Pozwala **mówiąc po ludzku** („zrób two color z `<plik>`") zbić JEDNĄ miniaturę
do dokładnie dwóch kolorów marki (#582F0E / #F4E5CA) — pierwszy krok doktryny
**SENSUM thumbnail finish** (`07_package.md` → Post-production), **bez ziarna**
(np. żeby najpierw ocenić czystą paletę). Operacja lokalna, deterministyczna,
**bez kredytów**.

## Krok 0 — Ustal plik
User podaje ścieżkę do PNG (np. `outputs/videos_pl/<slug>/thumbnails_no_grain/<nazwa>.png`).
- **Ścieżka podana** → użyj jej wprost.
- **Sam slug / brak ścieżki** → wylistuj `outputs/videos_pl/<slug>/thumbnails*/`
  i zapytaj, który plik.

## Krok 1 — Sprawdź plik
Potwierdź, że plik **istnieje** i jest **`.png`**. Jeśli nie — zatrzymaj się
i powiedz userowi (nie zgaduj innego pliku).

## Krok 2 — Odpal snap
Domyślnie zapis do **kopii `_2col`** (oryginał nietknięty):
```bash
PYTHONIOENCODING=utf-8 python tools/dev/finish_thumbnail.py "<ścieżka>" --two-color-only
```
- User chce **nadpisać** oryginał → dodaj `--in-place`.
- User chce **konkretną nazwę** wyjścia → `--out "<ścieżka>"`.

## Krok 3 — Zaraportuj
- co zrobił snap: **two_color** do #582F0E / #F4E5CA (sanity ze skryptu: dokładnie 2 kolory),
- **ścieżkę wyniku**,
- przypomnienie: przed Canvą miniaturę czeka jeszcze **ziarno** — powiedz
  „dodaj grain do `<wynik>`" (skill `grain-thumbnail`), grain idzie NA ten plik.

## Uwagi
- To jest **pierwszy** krok finiszu — `two_color` zawsze przed grainem (grain na
  surowym, ~800-kolorowym renderze utrwala off-brandowe przebarwienia).
- Pełny finish (two_color + grain) jedną komendą: `finish_thumbnail.py "<plik>"`
  bez flag (kopia `_final`).
- To **nie projektuje** miniatury — od projektu/renderu jest `package-thumbnail`
  / `/package`. Ten skill obrabia już gotowy plik.
- **Instrukcje usera biją skill:** każe nadpisać in-place, inną nazwę itd. —
  zastosuj się.
