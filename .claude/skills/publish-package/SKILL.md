---
name: publish-package
description: Use when the user asks in plain language (no slash command) to publish / prepare the YouTube PUBLISH package, description, tags, chapters, or Shorts copy for a SENSUM video — Polish triggers like "opublikuj", "zrób opis", "zrób tagi", "przygotuj metadane", "paczka publikacyjna", "opis i tagi dla slugu", or English "make the publish package / description / tags", optionally naming the video by number ("slug 2", "dwójka") or by folder-name fragment. Routes the Agent 8 procedure (/publish): resolves the slug, checks the script prerequisite, then runs /publish.
user-invocable: false
---

# Publish Package — naturalny router do /publish

Pozwala odpalić paczkę publikacyjną **mówiąc po ludzku** („zrób opis i tagi dla
dwójki") zamiast pamiętać `/publish <slug>`.

## Krok 0 — Rozwiąż slug
Slugi to foldery w `outputs/videos_pl/` z **numerycznym prefiksem**.
- Sama liczba → folder zaczynający się od tej liczby + `_`. **Potwierdź nazwę
  folderu jedną linią.**
- Fragment nazwy → dopasuj (`ls outputs/videos_pl/`).
- Niejednoznaczne / brak → wylistuj slugi i zapytaj który.

## Krok 1 — Sprawdź warunek wstępny
`/publish` potrzebuje finalnego skryptu + zweryfikowanego researchu. Sprawdź:
- skrypt: `docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`,
- research: `md/02_verified_research.md`.
- Brak skryptu → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>`
  i `/hook <slug>`.

## Krok 2 — Odpal procedurę
Potwierdź rozwiązany slug jedną linią, potem uruchom **`/publish <slug>`**
(in-session, bez kredytów — wystarczy potwierdzenie slugu; jedyne wywołania
zewnętrzne to deterministyczne bookendy `--signals`/`--finalize`).

## Krok 3 — Zaraportuj
To, co raportuje `/publish`: liczba tytułów, zdań opisu, rozdziałów, tagów +
długość, liczba Shortów, ostrzeżenia `[Q?]`/`[MISSING]` do naprawy przed
publikacją, następny krok (`/package <slug>` jeśli jeszcze nie zrobiony).

## Uwagi
- Doktryna copy (research-invisible, tagi, hashtagi) należy do samego `/publish` —
  router jej nie powtarza.
- **Instrukcje usera biją ten skill.**
