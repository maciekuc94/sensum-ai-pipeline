---
name: grain-thumbnail
description: Use when the user asks in plain language to add the SENSUM coarse grain (s2/i18) to an EXISTING thumbnail file given its path. Polish triggers like "dodaj grain do <ścieżka>", "dograinuj miniaturę <plik>", "ziarno do thumbnaila <plik>", "dodaj ziarno do <plik>", or English "add grain to <thumbnail path>". The user names a concrete PNG file/path. DISTINCT from two-color-thumbnail (the two-colour snap — the step BEFORE this one). For the FULL finish ("wykończ miniaturę", "zrób finish miniatury", "two_color i grain") run finish_thumbnail.py with NO flags (both steps, *_final copy). Also DISTINCT from package-thumbnail (which DESIGNS / renders a new thumbnail and costs credits). Local, deterministic, no API cost. Routes to tools/dev/finish_thumbnail.py --grain-only.
user-invocable: false
---

# Grain Thumbnail — grube ziarno miniatury (s2/i18, bez two_color)

Pozwala **mówiąc po ludzku** („dodaj grain do `<ścieżka>`") nałożyć na JEDNĄ
miniaturę grube ziarno `s2/i18` — drugi krok doktryny **SENSUM thumbnail
finish** (`07_package.md` → Post-production), tuż **przed Canvą**. Operacja
lokalna, deterministyczna, **bez kredytów**.

## Krok 0 — Ustal plik
User podaje ścieżkę do PNG (zwykle wynik two_color, np.
`outputs/videos_pl/<slug>/thumbnails_no_grain/<nazwa>_2col.png`).
- **Ścieżka podana** → użyj jej wprost.
- **Sam slug / brak ścieżki** → wylistuj `outputs/videos_pl/<slug>/thumbnails*/`
  i zapytaj, który plik.

## Krok 1 — Sprawdź plik
Potwierdź, że plik **istnieje** i jest **`.png`**. Jeśli nie — zatrzymaj się
i powiedz userowi (nie zgaduj innego pliku).

## Krok 2 — Odpal grain
Domyślnie zapis do **kopii `_grain`** (oryginał nietknięty — grain jest
nieodwracalny):
```bash
PYTHONIOENCODING=utf-8 python tools/dev/finish_thumbnail.py "<ścieżka>" --grain-only
```
- User chce **nadpisać** oryginał → dodaj `--in-place`.
- User chce **konkretną nazwę** wyjścia → `--out "<ścieżka>"`.
- Skrypt **ostrzeże**, jeśli wejście ma >2 kolory (grain należy kłaść na
  renderze po two_color) — przekaż ostrzeżenie userowi i zaproponuj najpierw
  skill `two-color-thumbnail`; kontynuuj tylko, jeśli user świadomie chce.

## Krok 3 — Zaraportuj
- co zrobił grain: **add_grain i18/s2** (seed=42, deterministyczny),
- **ścieżkę wyniku**,
- przypomnienie: do Canvy idzie **tylko napis** (overlay) w wolnej przestrzeni;
  **ziarno jest już wpieczone — nie dodawać grain w Canvie**.

## Uwagi
- To NIE jest ziarno body-image (`i12/s1`) — miniatura przy ~4K potrzebuje
  grubszego ziarna (cell ~2 px), bo drobne ziarno znika po downscale YouTube.
- Kolejność doktryny: `two_color` (skill `two-color-thumbnail`) → `grain`
  (ten skill). Pełny finish jedną komendą: `finish_thumbnail.py "<plik>"`
  bez flag (kopia `_final`).
- To **nie projektuje** miniatury — od projektu/renderu jest `package-thumbnail`
  / `/package`. Ten skill wykańcza już gotowy plik.
- **Instrukcje usera biją skill:** jeśli wprost poda inną intensywność/skalę,
  każe nadpisać in-place albo pominąć kopię — zastosuj się.
