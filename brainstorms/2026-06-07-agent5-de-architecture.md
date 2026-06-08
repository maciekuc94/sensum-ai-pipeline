# Brainstorm: De-architektura Agenta 5 (visuals) — „Łuk organiczny"

**Data:** 2026-06-07
**Status:** zatwierdzone, w realizacji
**Powiązane:** `2026-06-07-lean-draft-redesign.md` (redesign łańcucha draftu, który porzucił architektury)

## Problem

Łańcuch draftu został przeprojektowany na lean (3a pisarz → 3b checker → 3c fixer). Pisarz pisze całą narrację **swobodnie, jednym przebiegiem — bez deklarowania architektury** (Composite Portrait / Forensic Case Study / Historical Reversal / Socratic Challenge / Systems Audit). Skutek: nowe slugi nie mają `03_architecture.md` ani linii `ARCHITECTURE:` w skrypcie.

Ale **Agent 5 (`/visuals`) został w starej epoce** — jego workflow (`05_visuals.md`) i kod (`agent5_visuals.py`) są wciąż „beat-aware": szukają architektury, a gdy jej nie znajdą (czyli zawsze), lecą w fallback na domyślną kanału **Composite Portrait**. Użytkownik zobaczył w nagłówku `05_prompts.md` linię `Architecture: Composite Portrait` i nie rozpoznał skąd się wzięła — bo architektur już nie używa.

Architektura żyje już tylko jako pozostałość w: `05_visuals.md`, `agent5_visuals.py` (martwy kod), plus drobne odwołania/analogie. Komentarz w `agent5_visuals.py` sam się przyznaje (l. 613-618): *„retained for reference only and are no longer invoked."*

## Decyzja: „Łuk organiczny" (opcja C)

Wycinamy koncept architektury z Agenta 5 i zastępujemy go **organicznym rozpoznaniem łuku** — spójnym z duchem lean-draftu (pisz naturalnie, nic narzuconego).

Konkretnie w `05_visuals.md`:
- **Usuwamy:** instrukcje czytania architektury (`03_architecture.md` / `ARCHITECTURE:` / fallback Composite Portrait), całą sekcję „Beat Sequence & Visual Register" z 5 mapami architektur, pole `**Beat:**` z formatu wyjścia, linię `Architecture:` z nagłówka, pozycje o beat/architekturze z self-checku i common-issues.
- **Dodajemy** zwięzłą notkę **„Emotional Arc"**: przeczytaj skrypt, rozpoznaj jego naturalny łuk i prowadź nim rejestr wizualny — intymne/obserwacyjne otwarcie → pogłębienie ku mechanizmowi/źródłu (cutaway, scale-shift, diagram gdzie pasuje) → szerokie, ciche domknięcie. Nie narzucaj sztywnej struktury, podążaj za faktycznym ruchem skryptu.
- **Zostaje:** słownik 12 kompozycji, reguła wariancji, reguła kadrowania głowy, zasady postaci (bezgłowa figura), forbidden terms, pacing, self-check (oczyszczony).
- **Kalibracja figury:** ustalona jedna wartość **~60-75%** (figura to sygnatura kanału, ale absencję wydajemy świadomie). Zastępuje rozjazd baza 50-70% vs override Composite Portrait 70-80%.

W `agent5_visuals.py` (czyste usunięcie martwego kodu — zero ryzyka dla żywych ścieżek `--extract`/`--expand`):
- Kasujemy: `SYSTEM_PROMPT` (z `{VISUAL_REGISTER_BLOCK}`), `VISUAL_REGISTER_MAPS`, `VISUAL_REGISTER_FALLBACK`, `_extract_architecture`, `_build_system_prompt`, `_build_prompts_file` (asembler z liniami `Architecture:`/`**Beat:**`).
- Aktualizujemy komentarz legacy, by nie wspominał wyciętych helperów.
- Nie ruszamy żywych: `_build_imagen_prompt`, `_build_phrases_file`, `_expand_mode`, `main`, stałych `CHARACTER_DESCRIPTION`/`STYLE_SUFFIX`.

Drobne: `07_package.md` (l. 29) — usuwamy wiszącą analogię „(like the script architecture selector)".

Zostawiamy świadomie (fałszywe alarmy / defensywne): `agent4_hook.py` (skip linii `ARCHITECTURE:` — defensywny dla starych slugów), `lib/aligner.py` (regex generyczny ALLCAPS, architektura tylko jako przykład w komentarzu), `00_master.md` („## Architecture" = architektura WAT; baner już oznacza beaty jako stale), `08_publish.md` („architectural reveal" = nazwa trybu tytułu, nie beat).

Bieżący slug `3_wstyd_za_wlasne_zycie`: czyścimy już wygenerowany `05_prompts.md` (usuwamy nagłówek `Architecture:` + 83 pola `**Beat:**`), żeby był spójny z nową doktryną.

## Rozważane alternatywy

- **A — Minimal (tylko kompozycje):** wytnij wszystko, zero wskazówek łuku. Odrzucone: grafiki spłaszczyłyby się w strumień „różnych kompozycji" bez świadomości łuku emocjonalnego.
- **B — Jeden rejestr (de-architektura):** promuj rejestr Composite Portrait na jedyny, zawsze-włączony, z polem `**Beat:**`. Odrzucone: re-wprowadza nazwane ruchy = architektura pod inną nazwą; narzuca sztywny 5-ruchowy łuk skryptowi pisanemu swobodnie — ten sam rozjazd, który właśnie usuwamy.
- **C — Łuk organiczny:** ✅ wybrane. Zachowuje praktyczne dźwignie jakości (kompozycje, kalibracja, łuk jako prosa-wskazówka), usuwa scaffolding. Najbliższe filozofii lean-draftu.

## Bezpieczeństwo

Zmiana zachowania jest w całości w workflowie (`05_visuals.md` — to czyta Opus in-session). Kod to czyste usunięcie martwego kodu: żywe ścieżki `--extract`/`--expand` (`_expand_mode`) nie wołają ani map rejestru, ani funkcji architektury, ani `_build_prompts_file`. Weryfikacja: `py_compile` + smoke `--expand` na już-rozwiniętym slugu (powinno zwrócić „Already expanded. Nothing to do.").
