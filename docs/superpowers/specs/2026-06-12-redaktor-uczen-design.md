# Redaktor-uczeń — spec designu (zatwierdzony 2026-06-12)

> Kopalnia wzorców z docx-passów usera. Analizuje pary `04_final_machine.md` ↔ `script_corrected.md`
> ze wszystkich slugów, wyciąga systematyczne wzorce redakcji usera i proponuje wnioski,
> które po zatwierdzeniu czytają **checkerzy 3b** w `/draft`. Cel: podnosić sufit maszyny
> (~75–80%, mierzony przez `draft_ceiling_report.py`) — mniej pracy na każdym kolejnym docx passie.

## Decyzje usera (brainstorm 2026-06-12)

1. **Output:** raport + gotowe diffy propozycji; wnioski żyją w **oddzielnym pliku**
   (`workflows/guides/redakcja_wnioski.md`), **nie** w `voice_brief.md` — rozdzielenie
   ręcznie kuratorowanej doktryny od pętli self-improvement, żeby nie inflacjonować reguł.
2. **Konsument wniosków:** checkerzy 3b (sekcyjni + arc) jako „profil redakcyjny usera";
   **pisarz 3a nie czyta** (zostaje luźny; zero banned-list przy generacji — doktryna
   „cold checker bije zamrożoną listę" nienaruszona).
3. **Uruchamianie:** ręcznie, `/redaktor <slug>`, po każdym docx passie. Architektura
   analizy: **A — ensemble zimnych kategoryzatorów** (3 niezależne zimne subagenty
   + synteza leada z progiem zbieżności).

## Architektura — przepływ jednego uruchomienia

`/redaktor <slug>` (slug = świeżo skorygowany film; analiza obejmuje zawsze cały korpus):

0. **Ekstrakcja (bookend):** jeśli `docx/script_corrected.docx` nowszy niż
   `md/script_corrected.md` (lub md brak) → ekstrakcja docx→md (reuse istniejącej
   ścieżki `--extract`).
1. **`tools/pipeline/redaktor_pary.py`** (deterministyczny, zero tokenów):
   - skanuje `outputs/videos_pl/*/`, wybiera slugi z parą machine↔corrected;
     machine = `md/04_final_machine.md`, fallback `md/04_final.md`;
     human = `md/script_corrected.md`;
   - **tag generacji łańcucha** per slug, wykrywany po plikach:
     `gen5` (jest `04_final_machine.md`) / `sciskacz` (jest `04_final_presqueeze.md`)
     / `lean` (pozostałe);
   - parowanie zdań: reuse logiki `draft_ceiling_report.py` (regex zdań + difflib
     `SequenceMatcher`, próg SIMILAR = 0.85), **w obrębie sekcji `##`**; zdania
     niesparowane w sekcji → fallback parowania globalnego;
   - emituje **korpus** `.tmp/redaktor_korpus.md`: każda edycja jako
     `MOD` (z diffem słowo-po-słowie) / `DEL` / `ADD`, z sekcją, slugiem i tagiem
     generacji; na końcu statystyki ceiling per slug (reuse `sentence_diff_stats`)
     jako trend.
2. **Ensemble — 3 zimne subagenty-kategoryzatorzy** (typ
   `.claude/agents/redaktor-kategoryzator.md`, prompt single-sourced w
   `workflows/pipeline/redaktor_kategoryzator.md`): każdy niezależnie (równolegle,
   ślepo — bez wglądu w obecny plik wniosków i w wyniki pozostałych) czyta korpus
   i kategoryzuje wzorce edycji usera (co systematycznie tnie / skraca /
   przeformułowuje / dopisuje), z cytatami-dowodami `machine → human` (slug).
   Wynik: `.tmp/redaktor_kat_{1,2,3}.md`; zwrot SHORT (ścieżka + liczby),
   nigdy treść.
3. **Synteza (lead):** wzorzec wchodzi do raportu tylko przy zbieżności
   **≥2 z 3 kategoryzatorów** i dowodach z **≥2 filmów**. Porównanie z obecnym
   plikiem wniosków → propozycje trzech typów: **DODAJ / WZMOCNIJ** (nowy dowód)
   / **WYGAŚ** (nie potwierdza się). Ślepota kategoryzatorów = niezależna
   re-walidacja starych wniosków w każdym przebiegu.
4. **Raport** → `docs/research/redaktor/raport_RRRR-MM-DD.md`: wzorce z cytatami,
   rozkład per generacja łańcucha, trend ceiling między filmami (czy % dotkniętych
   zdań spada = czy pętla działa), propozycje jako gotowe diffy pliku wniosków.
5. **Manual gate:** user zatwierdza całość lub wybrane → dopiero wtedy lead
   aplikuje zmiany do `workflows/guides/redakcja_wnioski.md`.

## Plik wniosków — `workflows/guides/redakcja_wnioski.md`

- **Twardy limit: max 10 aktywnych wniosków.** Jedenasty wymaga wyparcia
  najsłabszego (ranking, nie akumulacja).
- **Format wniosku:** ID; jedna linijka sformułowana jako **heurystyka uwagi
  dla checkera** („user systematycznie X — sprawdzaj takie miejsca ostrzej"),
  nigdy zakaz frazy; 2–3 cytaty-dowody `machine → human` (slug); licznik filmów
  potwierdzających; daty (dodano / ostatnio potwierdzono); status
  `aktywny` / `wstępny` (dowody z <2 filmów).
- **Wygasanie:** wniosek niepotwierdzony w 2 kolejnych przebiegach → propozycja
  przeniesienia do sekcji **Archiwum** (z powodem); user zatwierdza.
- **Nagłówek-kontrakt:** „heurystyki uwagi z redakcji usera; przy konflikcie
  z `voice_brief.md` — voice_brief wygrywa". Checkerzy oceniają nadal kontekstowo.

## Wpięcie w /draft (jedyna zmiana istniejących plików)

- `workflows/pipeline/03b_section_checker.md` + `03b_arc_checker.md`: jedna
  linijka — „jeśli istnieje `workflows/guides/redakcja_wnioski.md`, przeczytaj
  jako profil redakcyjny usera (heurystyki uwagi, nie zakazy)".
- `.claude/commands/draft.md`: lead przekazuje ścieżkę pliku wniosków checkerom
  (gdy plik istnieje).
- **Nietykalne:** `voice_brief.md`, prompt pisarza 3a, fixer, `draft_ceiling_report.py`
  (zostaje jako szybki pomiar liczbowy).

## Nowe pliki

| Plik | Rola |
|---|---|
| `.claude/commands/redaktor.md` | launcher `/redaktor <slug>` |
| `workflows/pipeline/redaktor.md` | SOP (bez numeru — satelita post-docx, precedens: `align.md`) |
| `workflows/pipeline/redaktor_kategoryzator.md` | prompt kategoryzatora (single-source) |
| `.claude/agents/redaktor-kategoryzator.md` | definicja zimnego subagenta |
| `tools/pipeline/redaktor_pary.py` | diff korpusu (Layer 3) |
| `workflows/guides/redakcja_wnioski.md` | żywy plik wniosków (zmiany tylko po akcepcie usera) |
| `docs/research/redaktor/raport_*.md` | raporty per uruchomienie |

## Edge cases

- **0 par w korpusie** → komenda kończy się komunikatem, zero kosztu.
- **1 para** → raport oznaczony „wstępny"; wnioski tylko ze statusem `wstępny`.
- **docx bez ekstraktu md** → auto-ekstrakcja na starcie (krok 0).
- **Sekcje przearanżowane przez usera** → fallback parowania globalnego.
- **Dopiski usera (ADD)** → osobna kategoria wzorców („czego maszynie brakuje").
- **Wzorzec tylko ze slugów sprzed Gen 5** → flaga „możliwe, że już naprawione"
  (rozkład per generacja w raporcie).

## Testy

- pytest dla `redaktor_pary.py`: split zdań, parowanie MOD/DEL/ADD, tagowanie
  generacji, format korpusu — na małych fixture'ach.
- Smoke E2E na realnym slugu 3: buckety liczbowo zgodne z `draft_ceiling_report.py`
  (ta sama logika parowania).

## Poza zakresem (świadomie)

- Plik lekcji czytany przez pisarza (odtwarzałby banned-phrase-list — odrzucone).
- Automatyczne uruchamianie przy innych agentach (ukryte koszty — odrzucone).
- Modyfikacje `voice_brief.md` przez system (doktryna ręczna — nietykalna).
- Analiza retencji widzów (to osobny projekt — Retention Lens, nie ten spec).
