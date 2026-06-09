---
name: score-hook
description: Use when the user asks in plain language (no slash command) to score / check / fix the opening HOOK of a SENSUM script — Polish triggers like "oceń hook", "sprawdź hook", "popraw otwarcie", "jak wypada hook", "hook dla slugu", or English "score/check the hook", optionally naming the video by number ("slug 2", "dwójka") or by folder-name fragment. Routes the Agent 4 gate (/hook): resolves the slug, checks the script prerequisite, then runs /hook.
user-invocable: false
---

# Score Hook — naturalny router do /hook

Pozwala odpalić bramkę hooka **mówiąc po ludzku** („oceń hook dla dwójki")
zamiast pamiętać `/hook <slug>`.

## Krok 0 — Rozwiąż slug
Slugi to foldery w `outputs/videos_pl/` z **numerycznym prefiksem**.
- Sama liczba → folder zaczynający się od tej liczby + `_`. **Potwierdź nazwę
  folderu jedną linią.**
- Fragment nazwy → dopasuj (`ls outputs/videos_pl/`).
- Niejednoznaczne / brak → wylistuj slugi i zapytaj który.

## Krok 1 — Sprawdź warunek wstępny
`/hook` ocenia finalny skrypt. Sprawdź `outputs/videos_pl/<slug>/md/04_final.md`:
- Jest → gotowe.
- Brak → zatrzymaj się; powiedz userowi, że trzeba najpierw `/draft <slug>`.

## Krok 2 — Odpal procedurę
Potwierdź rozwiązany slug jedną linią, potem uruchom **`/hook <slug>`** (in-session,
bez kredytów — wystarczy potwierdzenie slugu). Bramka modyfikuje `04_final.md`
w miejscu (backup `04_final.bak.md`) i eksportuje `docx/script.docx`.

## Krok 3 — Zaraportuj
To, co raportuje `/hook`: wyniki Tier 1 (15s) / Tier 2 (30s), werdykt
(`RECORD`/`polish`/`rewrite`), czy otwarcie przepisano, następny krok.

## Uwagi
- Doktryna głosu należy do `native-voice-guard` + samego `/hook` — router jej nie
  powtarza.
- **Instrukcje usera biją ten skill.**
