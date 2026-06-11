---
name: write-script
description: Use when the user asks in plain language (no slash command) to write / draft / create the SCRIPT or scenariusz for a SENSUM video — Polish triggers like "napisz skrypt", "stwórz scenariusz", "zrób draft", "napisz scenariusz do filmu", "skrypt dla slugu", or English "write/draft the script", optionally naming the video by number ("slug 2", "dwójka", "drugi film") or by folder-name fragment. Routes the Agent 3 chain (/draft): resolves the slug, checks the research prerequisite, confirms, then runs /draft.
user-invocable: false
---

# Write Script — naturalny router do /draft

Pozwala odpalić łańcuch skryptu **mówiąc po ludzku** („napisz skrypt dla
dwójki") zamiast pamiętać `/draft <slug>`. Rozpoznaje intencję → uruchamia
właściwą procedurę.

## Krok 0 — Rozwiąż slug
Slugi to foldery w `outputs/videos_pl/` z **numerycznym prefiksem**
(`2_why_you_can_t_stick_to_anything`).
- Sama liczba („slug 2", „dwójka", „drugi") → folder zaczynający się od tej
  liczby + `_`. **Potwierdź rozwiązaną nazwę folderu jedną linią.**
- Fragment nazwy → dopasuj (`ls outputs/videos_pl/`).
- Niejednoznaczne / brak → wylistuj slugi i zapytaj który. (Jedyne dozwolone
  dopytanie — tożsamość slugu musi być pewna.)

## Krok 1 — Sprawdź warunek wstępny
`/draft` potrzebuje zweryfikowanego researchu. Sprawdź
`outputs/videos_pl/<slug>/md/02_verified_research.md`:
- Jest → gotowe.
- Brak → zatrzymaj się; powiedz userowi, że trzeba najpierw
  `PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "<slug>"`
  (a jeśli brak też `01_research.md` — najpierw Agent 1).

## Krok 2 — Odpal procedurę
Potwierdź rozwiązany slug jedną linią, potem uruchom **`/draft <slug>`** (komenda
in-session, Gen 5: pisarz → ensemble checkerów → merge skryptem → fixer →
snapshot → walidator + eksport docx). `/draft` przyjmuje WYŁĄCZNIE slug —
żadnych dodatkowych argumentów.

`/draft` nie wydaje kredytów (in-session), więc nie wymaga osobnego potwierdzenia
kosztów — wystarczy potwierdzenie slugu z Kroku 0.

## Krok 3 — Zaraportuj
To, co raportuje `/draft`: liczba słów, zgłoszenia [A]/[Z]/[K] + pominięcia
fixera, mapa pętli, werdykt walidatora; następny krok (redakcja `docx/script.docx`).

## Uwagi
- Doktryna głosu należy do `native-voice-guard` + samego `/draft` — ten router jej
  nie powtarza, tylko routuje procedurę.
- **Instrukcje usera biją ten skill.**
