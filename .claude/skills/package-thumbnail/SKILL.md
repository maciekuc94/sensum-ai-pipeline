---
name: package-thumbnail
description: Use when the user asks in plain language (no slash command) to design / make / render the THUMBNAIL, miniatura, okładka, or title-packaging for a SENSUM video — Polish triggers like "zrób miniaturę", "zaprojektuj okładkę", "miniatura dla slugu", "zrób thumbnail", "zaproponuj tytuł i miniaturę", or English "make/design the thumbnail", optionally naming the video by number ("slug 2", "dwójka") or by folder-name fragment. Routes the Agent 7/Package procedure (/package): resolves the slug, checks the script prerequisite, and ALWAYS confirms before spending render credits (Package is manual by doctrine).
user-invocable: false
---

# Package Thumbnail — naturalny router do /package

Pozwala odpalić strategistę opakowania **mówiąc po ludzku** („zrób miniaturę dla
dwójki") zamiast pamiętać `/package <slug>`. **Renderuje 3 obrazy → kredyty;
nigdy bez potwierdzenia.**

## Krok 0 — Rozwiąż slug
Slugi to foldery w `outputs/videos_pl/` z **numerycznym prefiksem**.
- Sama liczba → folder zaczynający się od tej liczby + `_`. **Potwierdź nazwę
  folderu jedną linią.**
- Fragment nazwy → dopasuj (`ls outputs/videos_pl/`).
- Niejednoznaczne / brak → wylistuj slugi i zapytaj który.

## Krok 1 — Sprawdź warunek wstępny
`/package` potrzebuje skryptu. Sprawdź w kolejności:
`docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`.
- Jest którykolwiek → gotowe.
- Brak → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>` (i
  `/hook <slug>`).

## Krok 2 — POTWIERDŹ przed wydaniem kredytów (nienegocjowalne)
`/package` jest oznaczony w CLAUDE.md jako manual; domyślny bieg renderuje **3
miniatury** (kredyty Gemini + ~1.5 min). Przed uruchomieniem pokaż userowi:
- rozwiązany slug,
- że powstaną 3 strategie + 3 wyrenderowane miniatury,
- alternatywę **`/package <slug> --no-render`** (sam tekst, za darmo),
i uzyskaj wyraźne „tak". **Nie renderuj na cichym założeniu.**

## Krok 3 — Odpal procedurę
Po potwierdzeniu uruchom **`/package <slug>`** (lub `/package <slug> --no-render`
jeśli user chce tylko strategie tekstowe).

## Krok 4 — Zaraportuj
To, co raportuje `/package`: 3 strategie (nazwa · tytuł · napis), ile miniatur
wyrenderowano + folder `thumbnails_no_grain/`, przypomnienie o wyborze JEDNEJ
strategii i overlay napisu w Canvie.

## Uwagi
- Doktryna stylu należy do `scientific-etching-guard` + `STYLE_SUFFIX` — router jej
  nie powtarza.
- **Instrukcje usera biją ten skill:** jeśli wprost powie „po prostu odpal", pomiń
  potwierdzenie z Kroku 2 ten jeden raz.
