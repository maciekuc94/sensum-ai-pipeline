# Workflow: Redaktor-uczeń — wzorce z docx-passów usera

> Satelita post-docx (jak `align.md` — bez numeru). Uruchamiany ręcznie przez
> `/redaktor <slug>` po każdym docx passie. Cel: systematyczne wzorce ręcznych
> korekt usera → wnioski czytane przez checkerów 3b → wyższy sufit maszyny.
> Spec: `docs/superpowers/specs/2026-06-12-redaktor-uczen-design.md`.

## Wejścia
- Pary `md/04_final_machine.md` (fallback `04_final.md`) ↔ `md/script_corrected.md`
  ze WSZYSTKICH slugów (korpus rośnie z każdym filmem).
- Obecny `workflows/guides/redakcja_wnioski.md` (czyta go TYLKO lead — nigdy
  kategoryzatorzy; ich ślepota = niezależna re-walidacja starych wniosków).

## Kroki (lead)
1. **Tool (Layer 3):** `PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "<slug>"`
   — ekstrakcja docx w razie potrzeby + `.tmp/redaktor_korpus.md`. Exit 1 =
   slug bez pary; przerwij i powiedz userowi czego brakuje.
2. **Ensemble:** 3 zimne `redaktor-kategoryzator` (Opus) RÓWNOLEGLE — wszystkie
   spawny w JEDNEJ wiadomości; briefy w `.claude/commands/redaktor.md`. Wyniki:
   `.tmp/redaktor_kat_{1,2,3}.md`, zwroty SHORT.
3. **Synteza:** przeczytaj 3 pliki kategoryzacji + obecne wnioski. Wzorzec
   wchodzi do raportu, gdy znalazło go (po istocie, nie po nazwie) **≥2 z 3**
   kategoryzatorów I dowody pochodzą z **≥2 filmów**. Wzorzec tylko ze slugów
   sprzed gen5 → flaga „możliwe, że już naprawione". Porównaj z aktywnymi
   wnioskami → propozycje: **DODAJ** (nowy wzorzec), **WZMOCNIJ** (nowy dowód
   do istniejącego), **WYGAŚ** (wniosek bez potwierdzenia w tym przebiegu;
   po 2 kolejnych pudłach → propozycja Archiwum).
4. **Raport:** `docs/research/redaktor/raport_RRRR-MM-DD.md` z sekcjami:
   `## Wzorce potwierdzone` (z cytatami i zbieżnością 2/3 vs 3/3),
   `## Wzorce odrzucone w syntezie` (1 kategoryzator / 1 film — z powodem),
   `## Trend ceiling` (z wyjścia toola; czy % dotkniętych spada),
   `## Propozycje zmian wniosków` (gotowe wpisy w formacie z
   `redakcja_wnioski.md`, oznaczone DODAJ/WZMOCNIJ/WYGAŚ).
5. **Manual gate:** pokaż userowi propozycje (AskUserQuestion, multiSelect —
   per propozycja). TYLKO zaakceptowane aplikuj do
   `workflows/guides/redakcja_wnioski.md` (pilnuj: max 10 aktywnych, status
   `wstępny` przy dowodach z <2 filmów, daty). Potem commit
   (`feat(redaktor): wnioski po <slug> — N zmian`).

## Edge cases
- 0 par → tool kończy z exit 1, zero kosztów. 1 para → raport i wnioski
  oznaczone `wstępny`.
- Typ `redaktor-kategoryzator` niezarejestrowany (świeżo dodany plik — agenci
  ładują się na starcie sesji): spawnuj `general-purpose` z `model: opus`
  i tym samym briefem.
- Spawn pada całkiem: odpal danego kategoryzatora jako świeże zimne przejście
  in-session wg `redaktor_kategoryzator.md` (sekwencyjnie OK — czytają
  zamrożony korpus).
- Kategoryzator zwróci 0 wzorców: to legalny wynik — odnotuj w raporcie.

## Wyjścia
- `.tmp/redaktor_korpus.md`, `.tmp/redaktor_kat_{1,2,3}.md` (disposable)
- `docs/research/redaktor/raport_RRRR-MM-DD.md` (trwały)
- zaktualizowany `workflows/guides/redakcja_wnioski.md` (tylko po akcepcie)
