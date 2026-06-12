# Spec: Surowy panel Native-Ear (Agent 3d) — „wszystko naraz" (1+2+3)

Data: 2026-06-05
Status: zaakceptowany kształt (do przeglądu użytkownika przed implementacją)
Dotyczy: `/draft-team` → debata native-ear (Agent 3d)

---

## Problem

Krytyk natywności 3d w `/draft-team` jest **za miękki na wszystkich osiach naraz** (potwierdzone przez
użytkownika — wskazał wszystkie cztery przecieki):

1. **Za łatwo daje `NATIVE`** — skrypt przechodzi, mimo że wciąż słychać kalki/sztywność (próg werdyktu
   za wysoki: `≥1 BLOCKER / ≥3 FIX / ≥5 WATCH`).
2. **Znajduje, ale odpuszcza** — akceptuje słabe poprawki zamiast docisnąć (dampener za wcześnie miękki).
3. **Mało łapie** — całe typy nienaturalności przechodzą (rytm, klisze, zdania „za ładne") — dziś zakres
   to *tylko* translationese.
4. **Za szybko chroni linię** — klauzula ochrony obrazów („never demand they change") odpuszcza zdania,
   które powinna ruszyć.

## Cel

Podnieść surowość 3d na wszystkich czterech osiach, **bez** wpadania w znaną pułapkę „dokręcania" —
mielenia prozy w zgodną papkę i przepalania wszystkich rund (dlatego w 3d istnieje anti-sterility guard).
Mechanizm ma być **surowy, ale zbieżny** (kończy się w ≤3 rundach).

## Nie-cele (YAGNI)

- Nie ruszamy zwykłego `/draft` (in-session kat. J) — zostaje tanią ścieżką domyślną, bez zmian.
- Nie ruszamy 3a/3b/3c (kategorie A–I) ani selekcji architektury.
- Nie usuwamy anti-sterility guard — zawężamy go (patrz niżej), nie kasujemy.
- Nie zwiększamy liczby rund (zostaje 3).

## Decyzje (zablokowane z użytkownikiem)

| Decyzja | Wybór |
|---|---|
| Kierunek | **Wszystko naraz (1+2+3)**: panel dwóch uszu + dokręcenie progów + twarda semantyka werdyktu |
| Max rund debaty | **3** (surowość z progu+panelu+hard-stopu, nie z liczby rund) |
| Zakres hard-stopu | **Tylko BLOCKER w pozycji impact** (hook / cold open / kotwica / Permission Practice / recognition close) |

---

## Projekt

### 1. Panel — dwa zimne uszy o różnych soczewkach (Droga 2)

`/draft-team` Step 4 spawnuje **dwóch** teammate'ów typu `native-ear-critic` (oba na zimno, oba czytają
`04_working.md`), różniących się **soczewką przekazaną w briefingu leada**:

- **Ucho A — „Składnia i rejestr"**: 4 nazwane tells (pronoun flood, nominalizacja, genitive-stack,
  trailing-verb), kalki struktury EN, niezręczne kolokacje/dopełniacze, zderzenia rejestru
  (urzędniczo-prawniczy ton w intymnym). To dzisiejszy zakres 3d.
- **Ucho B — „Rytm i klisza"**: płaski/monotonny rytm, frazesy i klisze, zdania „za ładne / pisane jak
  content, nie mówione na żywo", abstrakcja tam, gdzie ma stać konkretny obraz, watowanie. To **nowy**
  zakres odpowiadający na „mało łapie".

Jedna soczewka per ucho jest celowa — gdyby jedno ucho ścigało wszystko, rozmydliłoby uwagę. Różne
soczewki łapią rozłączne klasy usterek.

**Implementacja soczewki:** jeden SOP (`03d_native_ear.md`) zyskuje sekcję „## Soczewka (lens)"; lead w
briefingu nazywa soczewkę (`lens: składnia-rejestr` albo `lens: rytm-klisza`). Ucho poluje **głównie** w
swojej soczewce, ale jaskrawy tell spoza soczewki też flaguje. Bez drugiego pliku roli — dwa nazwane
egzemplarze tego samego typu (`nativeear-A`, `nativeear-B`).

**Agregacja werdyktu (lead):** suma flag obu uszu. Werdykt rundy = `NATIVE` **tylko gdy oba** ucha dają
`NATIVE`. Jeśli choć jedno daje `REWORK` → runda poprawek. To strukturalnie likwiduje „za łatwo NATIVE".

### 2. Dokręcenie każdego ucha (Droga 1)

Zmiany w `03d_native_ear.md`, obowiązują oba ucha:

- **Próg werdyktu**: z `≥1 BLOCKER / ≥3 FIX / ≥5 WATCH` → **`≥1 BLOCKER / ≥2 FIX / ≥3 WATCH`** (drift).
- **Zakres**: Ucho B dokłada rytm/klisza/„za ładne" (sekcja „What to hunt" rozszerzona o część dla
  soczewki rytm-klisza).
- **Guard — precyzyjne cięcie**:
  - **Zostaje** część „odrzucaj spłaszczone / przekorygowane / odobrazowione przepisania" — to *sam w
    sobie* mechanizm surowości (flaguje papkę jako FIX „przywróć konkret/obraz").
  - **Zawężona** ochrona obrazów: „never demand they change" działa **wyłącznie** dla dosłownie 4 kotwic
    (cold open, centralny motyw-obiekt, zdania-kotwice, obraz końcowy) **i tylko gdy linia nie niesie
    żadnego tella**. Linia-kotwica z tellem → ochrona nie obowiązuje, leci do flag. To odpowiedź na „za
    szybko chroni linię".

### 3. Twarda semantyka werdyktu — hard-stop (Droga 3)

Zmiana w `/draft-team` Step 5/6. Dziś: nierozwiązany problem przy `N == MAX` → ship z nagłówkiem WARNING.
Nowość:

- **Nierozwiązany BLOCKER w pozycji impact** (hook / cold open / kotwica / Permission Practice /
  recognition close) po ostatniej rundzie → **NIE wysyła automatycznie**. Lead zatrzymuje pętlę, pokazuje
  użytkownikowi konkretne zdanie(a) + nazwany tell i pyta: **(a)** poprawić w miejscu, **(b)** przyjąć z
  ostrzeżeniem, **(c)** jeszcze jedna runda.
- **Nierozwiązany FIX/WATCH poza impactem** po ostatniej rundzie → ship z nagłówkiem WARNING jak dziś
  (nie blokujemy całego pipeline'u o sztywność w środku akapitu).

### 4. Zbieżność — żeby „wszystko naraz" się kończyło

Niższe progi + dwa ucha mogłyby młócić w nieskończoność. Dlatego dampener **nie znika — robi się węższy,
nie miększy** (zmiana sensu „Iteration dampener" w `03d_native_ear.md`):

- **Rundy 1 … MAX-1**: pełna surowość, oba ucha, wszystkie flagi.
- **Runda ostatnia (N == MAX == 3)**: tryb zbieżności — oba ucha re-challenge'ują **tylko nierozwiązane**
  tells + łapią **nowe** kalki wprowadzone przepisaniem; `REWORK` trzaska na **pozostałym BLOCKERZE lub
  ≥2** nierozwiązanych/nowych FIX (ostrzej niż dzisiejsze ≥3), ale ucha **nie otwierają nowych drobnych
  WATCH-ów**. Surowo, ale zbieżnie.

### 5. Pliki, artefakty, koszt, odwracalność

**Pliki dotykane:**

- `workflows/pipeline/03d_native_ear.md` — progi, sekcja soczewki, zawężony guard, dampener=tryb
  zbieżności w ostatniej rundzie, rozszerzony zakres polowania dla soczewki rytm-klisza.
- `.claude/commands/draft-team.md` — Step 4 (spawn **dwóch** uszu z soczewkami), Step 5 (agregacja sumy
  flag, `NATIVE` tylko gdy oba; gałąź hard-stop na BLOCKERZE w impakcie przy `N==MAX`), Step 6 (nagłówek
  WARNING wskazuje **oba** logi), Step 7 (teardown obu uszu).
- `docs/agent_teams_reference.md` — opis `/draft-team` (dwa ucha, panel, nowe progi, hard-stop).

**Artefakty (logi):** `outputs/videos_pl/<slug>/md/03d_nativeear_A_iter{N}.md` oraz
`03d_nativeear_B_iter{N}.md` (prefiks `03d_nativeear_` zachowany dla ciągłości grep/przeglądu).

**Koszt (uczciwie):** dwa ucha × do 3 rund = **do 6 kontekstów Opus** na draft (dziś ≤3). `/draft` (bez
teamu) zostaje tanią ścieżką bez zmian — to świadomy wybór „droższe, ale surowsze".

**Odwracalność:** wszystkie zmiany to pliki `.md` w gicie — rewert jednym `git checkout <plik>`.

**Follow-up (osobno, nie w tym specu):** jednoliniowa korekta wzmianki o `/draft-team` w `CLAUDE.md`
(„cold-context Native-Ear Critic (3d)" → panel dwóch uszu) — przez skill `revise-claude-md`.

---

## Kryteria akceptacji

1. `/draft-team` spawnuje dwa ucha o rozłącznych soczewkach; każde pisze własny log `03d_nativeear_{A,B}_iter{N}.md`.
2. Runda kończy się `NATIVE` **tylko** gdy oba ucha zwrócą `NATIVE`; pojedyncze `REWORK` wymusza poprawki.
3. Próg każdego ucha to `≥1 BLOCKER / ≥2 FIX / ≥3 WATCH`.
4. Guard chroni linię „bez zmian" tylko dla 4 kotwic i tylko gdy nie niosą tella; spłaszczone przepisania
   nadal są flagowane.
5. Ostatnia runda działa w trybie zbieżności (re-challenge nierozwiązanych + nowe kalki; `REWORK` na
   BLOCKERZE lub ≥2 FIX; bez nowych WATCH-ów).
6. Nierozwiązany BLOCKER w pozycji impact po ostatniej rundzie zatrzymuje pętlę i pyta użytkownika
   (a/b/c) zamiast cichego ship-z-WARNING; pozostałe nierozwiązania → ship z WARNING.
7. `/draft` pozostaje niezmieniony.
8. Wszystkie nowe nazwy plików/artefaktów spójne; teardown sprząta oba ucha (jeden team na raz).
