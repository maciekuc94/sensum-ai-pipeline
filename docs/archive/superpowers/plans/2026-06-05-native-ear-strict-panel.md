# Surowy panel Native-Ear (Agent 3d) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Podnieść surowość krytyka native-ear w `/draft-team` przez panel dwóch zimnych uszu o różnych soczewkach, niższe progi, zawężony guard, tryb zbieżności w ostatniej rundzie i twardy stop na nierozwiązanym BLOCKERZE w pozycji impact.

**Architecture:** Edytujemy wyłącznie pliki promptów/SOP w markdown — żadnego kodu Pythona. `03d_native_ear.md` zyskuje soczewkę, niższe progi, zawężony guard i tryb zbieżności. `draft-team.md` spawnuje dwa ucha, agreguje sumę flag (NATIVE tylko gdy oba) i dokłada gałąź hard-stop. Rola `native-ear-critic.md` i `agent_teams_reference.md` zostają zsynchronizowane z nowym kontraktem. Wszystko odwracalne `git checkout`.

**Tech Stack:** Markdown (SOP/command/agent-role), Claude Code Agent Teams (`/draft-team`), git. Brak testów jednostkowych — weryfikacja to Grep/Read na spójność kontraktu.

**Spec źródłowy:** `docs/archive/superpowers/specs/2026-06-05-native-ear-strict-panel-design.md`

---

## File Structure

| Plik | Odpowiedzialność | Zmiana |
|---|---|---|
| `workflows/pipeline/03d_native_ear.md` | Kontrakt pojedynczego ucha (co hunt, progi, guard, dampener, output) | Soczewka, niższe progi, zawężony guard, tryb zbieżności, sufiks A/B w nazwach plików |
| `.claude/agents/native-ear-critic.md` | Rola teammate'a (briefing → SOP) | Wzmianka o soczewce + sufiksie A/B w nazwach artefaktów |
| `.claude/commands/draft-team.md` | Orkiestracja debaty | Spawn 2 uszu, agregacja sumy flag, hard-stop, dwa logi, teardown obu |
| `docs/agent_teams_reference.md` | Dokumentacja `/draft-team` | Opis panelu (dwa ucha, progi, hard-stop) |

Kolejność zadań = kolejność zależności: najpierw kontrakt ucha (Task 1), potem rola wskazująca na kontrakt (Task 2), potem orkiestracja używająca obu (Task 3), na końcu dokumentacja (Task 4).

**Konwencja sufiksów (obowiązuje cały plan):** Ucho A = soczewka `składnia-rejestr` → pisze `..._A_...`. Ucho B = soczewka `rytm-klisza` → pisze `..._B_...`.

---

## Task 1: Kontrakt ucha — `03d_native_ear.md`

**Files:**
- Modify: `workflows/pipeline/03d_native_ear.md`

- [ ] **Step 1: Dodaj sekcję „## Soczewka (lens)" po „## Your stance"**

Wstaw nową sekcję bezpośrednio po akapicie „## Your stance" (przed „## Inputs to load"):

```markdown
## Soczewka (lens) — lead przydziela ją w briefingu

`/draft-team` uruchamia Cię jako **jedno z dwóch uszu panelu**. Lead w briefingu podaje Twoją
**soczewkę** i **sufiks pliku** (`A` lub `B`). Polujesz **głównie** w swojej soczewce; jaskrawy tell
spoza soczewki też flaguj (w Minor Notes, jeśli to nie Twoja domena), ale nie rozmydlaj uwagi.

- **`lens: składnia-rejestr` (sufiks A)** — 4 nazwane tells, kalki struktury EN, niezręczne
  kolokacje/dopełniacze, zderzenia rejestru (urzędniczo-prawniczy ton w intymnym). To rdzeń „What to
  hunt" niżej.
- **`lens: rytm-klisza` (sufiks B)** — płaski/monotonny rytm, frazesy i klisze, zdania „za ładne /
  pisane jak content, nie mówione na żywo", abstrakcja tam, gdzie ma stać konkretny obraz, watowanie.
  Patrz „What to hunt → Warstwa rytmu i kliszy (soczewka B)".

Jeśli lead nie poda soczewki, działaj jak soczewka `składnia-rejestr` (sufiks A) — to zachowanie
zgodne ze starym, jednoosobowym 3d.
```

- [ ] **Step 2: Obniż próg werdyktu**

Znajdź w sekcji „## Severity" linię:

```
**Verdict threshold:** `REWORK` if there is **≥1 BLOCKER**, or **≥3 FIX**, or **≥5 WATCH** forming a
drift pattern. Otherwise `NATIVE`, with any residual FIX/WATCH listed in Minor Notes.
```

Zamień na:

```
**Verdict threshold (zaostrzony 2026-06-05):** `REWORK` if there is **≥1 BLOCKER**, or **≥2 FIX**, or
**≥3 WATCH** forming a drift pattern. Otherwise `NATIVE`, with any residual FIX/WATCH listed in Minor
Notes.
```

- [ ] **Step 3: Przepisz „Iteration dampener" na tryb zbieżności (ostatnia runda, ostrzejszy próg)**

Znajdź:

```
**Iteration dampener (round N ≥ 3):** only re-challenge **unresolved tells + new calques the rewrite
introduced**. Do not open new minor stylistic nits — converge. `REWORK` only on a remaining BLOCKER
or ≥3 unresolved/new FIX.
```

Zamień na:

```
**Tryb zbieżności (ostatnia runda, N == MAX == 3):** re-challenge **tylko nierozwiązane tells** +
łap **nowe** kalki wprowadzone przepisaniem. **Nie otwieraj nowych drobnych WATCH-ów** — zbiegaj.
Ale zbieżność ≠ miękkość: `REWORK` na **pozostałym BLOCKERZE lub ≥2** nierozwiązanych/nowych FIX
(ostrzej niż dawne ≥3). Rundy 1…MAX-1 działają z pełną surowością (wszystkie flagi).
```

- [ ] **Step 4: Zawęź ochronę obrazów w „Anti-sterility guard"**

Znajdź akapit zaczynający się od „**Protect the strongest images — never demand they change**":

```
**Protect the strongest images — never demand they change** (per `voice_corpus.md` §E.f): the cold
open, the central object-motif, the anchor sentences, the final image. If one of these is already
vivid native Polish, leave it. „Redakcja bezwzględna ≠ redakcja wszędzie."
```

Zamień na:

```
**Protect the strongest images — ALE tylko bez tella** (per `voice_corpus.md` §E.f, zawężone
2026-06-05): klauzula „never demand they change" obejmuje **wyłącznie** 4 kotwice — the cold open, the
central object-motif, the anchor sentences, the final image — **i tylko gdy dana linia nie niesie
żadnego tella**. Jeśli już jest żywą, natywną polszczyzną — zostaw. Ale kotwica z tellem (kalka,
nominalizacja, trailing-verb, zderzenie rejestru itd.) **traci ochronę** — flaguj ją normalnie.
„Redakcja bezwzględna ≠ redakcja wszędzie", ale ochrona ≠ immunitet dla kalki.
```

(Pierwszy akapit guardu — „reject over-corrected / flattened / de-imaged rewrites" — **zostaje bez
zmian**: to sam w sobie mechanizm surowości.)

- [ ] **Step 5: Dołóż warstwę soczewki B do „## What to hunt"**

Na końcu sekcji „## What to hunt (translationese only)", tuż przed linią „Litmus (from §C): …", wstaw:

```markdown
**Warstwa rytmu i kliszy (soczewka B — `lens: rytm-klisza`):**

- **Płaski/monotonny rytm** — ciąg zdań tej samej długości i budowy; brak oddechu, brak krótkiego
  zdania-uderzenia tam, gdzie myśl powinna wybrzmieć.
- **Frazes / klisza** — gotowy zwrot, który czytelnik mija wzrokiem („na końcu dnia", „w głębi duszy",
  „każdy z nas wie"), zamiast świeżego, konkretnego sformułowania.
- **„Za ładne" / pisane, nie mówione** — zdanie wygładzone jak akapit z bloga, nie jak coś, co ktoś
  naprawdę mówi nad kawą; elegancja kosztem prawdy głosu.
- **Abstrakcja zamiast obrazu** — pojęcie ogólne („poczucie braku kontroli") tam, gdzie ma stać
  konkretny, zmysłowy obraz.
- **Watowanie** — słowa, które nic nie wnoszą („tak naprawdę", „pewien rodzaj", „w jakimś sensie").

Severity tej warstwy idzie tą samą skalą (pozycja impact → BLOCKER). Soczewka A poluje na powyższe
tylko, jeśli jest jaskrawe; soczewka B traktuje to jako rdzeń.
```

- [ ] **Step 6: Zsufiksuj nazwy plików logu (input, output, message-back)**

Wykonaj trzy podmiany w pliku:

1. W „## Inputs to load", punkt 3:
   - z: `On round `N > 1` only: your own prior log `03d_nativeear_iter{N-1}.md``
   - na: `On round `N > 1` only: your own prior log `03d_nativeear_<suffix>_iter{N-1}.md` (suffix = `A`/`B` z briefingu)`
2. W „## Output", linia z docelową ścieżką:
   - z: `Write to `outputs/videos_pl/<slug>/md/03d_nativeear_iter<N>.md` with this exact header:`
   - na: `Write to `outputs/videos_pl/<slug>/md/03d_nativeear_<suffix>_iter<N>.md` (suffix = `A`/`B` z briefingu) with this exact header:`
3. W „## After writing the log", zdanie z message-back:
   - z: `Message the lead **one line**: the path you wrote (`outputs/videos_pl/<slug>/md/03d_nativeear_iter<N>.md`)`
   - na: `Message the lead **one line**: the path you wrote (`outputs/videos_pl/<slug>/md/03d_nativeear_<suffix>_iter<N>.md`)`

Dodatkowo w nagłówku output-schematu zmień linię `Pass: Native-Ear Critic (iteration <N>)` na
`Pass: Native-Ear Critic — lens <składnia-rejestr|rytm-klisza> (iteration <N>)`.

- [ ] **Step 7: Weryfikacja — sprawdź, że kontrakt jest spójny**

Run (Grep, `output_mode: content`):
- `≥2 FIX` w `workflows/pipeline/03d_native_ear.md` → oczekiwane: trafienie w „Verdict threshold" i w „Tryb zbieżności".
- `Soczewka \(lens\)` → oczekiwane: 1 trafienie (nagłówek nowej sekcji).
- `03d_nativeear_<suffix>_iter` → oczekiwane: ≥3 trafienia (input, output, message-back).
- `rytm-klisza` → oczekiwane: ≥2 trafienia (sekcja soczewki + warstwa hunt).

Oczekiwane: brak pozostałego `≥3 FIX` jako progu (stary próg) i brak gołego `03d_nativeear_iter` bez sufiksu w ścieżkach zapisu.

- [ ] **Step 8: Commit**

```bash
git add workflows/pipeline/03d_native_ear.md
git commit -m @'
feat(draft-team): tighten native-ear contract — lens, lower thresholds, narrowed guard

Add lens section (składnia-rejestr / rytm-klisza), drop verdict threshold to
≥2 FIX / ≥3 WATCH, narrow image-protection to anchors-without-tells, convert
the dampener into a stricter convergence mode, add the rhythm/cliché hunt
layer, and suffix log filenames with A/B for the two-ear panel.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
'@
```

---

## Task 2: Rola teammate'a — `native-ear-critic.md`

**Files:**
- Modify: `.claude/agents/native-ear-critic.md`

- [ ] **Step 1: Dodaj wzmiankę o soczewce do briefingu**

Znajdź zdanie:

```
When the lead assigns a pass it gives you a **slug** and an **iteration number N**:
```

Zamień na:

```
When the lead assigns a pass it gives you a **slug**, an **iteration number N**, a **soczewkę**
(`lens: składnia-rejestr` albo `lens: rytm-klisza`) i **sufiks pliku** (`A` lub `B`). Polujesz głównie
w swojej soczewce — szczegóły w sekcji „## Soczewka (lens)" w `03d_native_ear.md`.
```

- [ ] **Step 2: Zsufiksuj nazwy artefaktów w punktach 2 i 3**

1. Punkt 2 — z:
   `On round N>1 also read your prior log `outputs/videos_pl/<slug>/md/03d_nativeear_iter{N-1}.md``
   na:
   `On round N>1 also read your prior log `outputs/videos_pl/<slug>/md/03d_nativeear_<suffix>_iter{N-1}.md``
2. Punkt 3 — z:
   `Write `outputs/videos_pl/<slug>/md/03d_nativeear_iter<N>.md` per the schema`
   na:
   `Write `outputs/videos_pl/<slug>/md/03d_nativeear_<suffix>_iter<N>.md` per the schema`

- [ ] **Step 3: Weryfikacja**

Run (Grep, `output_mode: content`): `03d_nativeear_<suffix>_iter` w `.claude/agents/native-ear-critic.md` → oczekiwane: 2 trafienia. `soczewk` → oczekiwane: ≥1 trafienie. Brak gołego `03d_nativeear_iter` bez sufiksu.

- [ ] **Step 4: Commit**

```bash
git add .claude/agents/native-ear-critic.md
git commit -m @'
feat(draft-team): native-ear role carries lens + A/B suffix for the panel

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
'@
```

---

## Task 3: Orkiestracja — `draft-team.md`

**Files:**
- Modify: `.claude/commands/draft-team.md`

- [ ] **Step 1: Zaktualizuj tabelę „Division of labor" i intro**

W tabeli „**Division of labor:**" znajdź wiersz:

```
| Language / translationese — 3c category **J** + the four named tells | **Native-Ear Critic teammate (cold context)** |
```

Zamień na:

```
| Language / translationese — 3c category **J** + the four named tells | **Panel: dwa Native-Ear Critics (cold context) — soczewka składnia-rejestr (A) + rytm-klisza (B)** |
```

- [ ] **Step 2: Przepisz Step 4 — spawn DWÓCH uszu z soczewkami**

Zamień całą treść sekcji „## Step 4 — Spawn the Native-Ear Critic teammate (once)" na:

```markdown
## Step 4 — Spawn the Native-Ear panel (dwa ucha, raz)

Spawnuj **dwa** teammate'y typu `native-ear-critic`, oba in-process, oba persystentne na całą debatę
(trzymają historię swoich zarzutów, by re-challenge'ować słabe poprawki), oba odcięte od Twojego
kontekstu pisania:

- `nativeear-A` — soczewka **składnia-rejestr**, sufiks **A**.
- `nativeear-B` — soczewka **rytm-klisza**, sufiks **B**.

Nie przekazuj im żadnego uzasadnienia z pisania. Briefing każdego ucha to wyłącznie: slug, jego
soczewka + sufiks, że ma iść za `workflows/pipeline/03d_native_ear.md`, i numer rundy.
```

- [ ] **Step 3: Przepisz Step 5 — pętla panelu z agregacją i hard-stopem**

Zamień całą treść sekcji „## Step 5 — Native-ear debate loop" na:

```markdown
## Step 5 — Debata panelu (`N = 1`, `MAX = 3`)

Najpierw skopiuj A–I-clean script (ostatni `03b_revised_iter{N}.md` ze Step 3) do
`outputs/videos_pl/$1/md/04_working.md`. Potem pętla:

1. **Przydziel rundę OBU uszom.** Wyślij do `nativeear-A`: *"Native-ear pass: slug `$1`, iteracja `N`,
   `lens: składnia-rejestr`, sufiks `A`. Przeczytaj `outputs/videos_pl/$1/md/04_working.md` na zimno i
   idź za `workflows/pipeline/03d_native_ear.md`."* Analogicznie do `nativeear-B` z `lens: rytm-klisza`,
   sufiks `B`. **Poczekaj na powiadomienie o ukończeniu od OBU.**
2. **Wczytaj oba werdykty.** Przeczytaj `03d_nativeear_A_iter{N}.md` i `03d_nativeear_B_iter{N}.md`;
   z każdego sparsuj pierwszą niepustą linię po `## VERDICT` (dokładnie `NATIVE` / `REWORK`; cokolwiek
   innego = `UNKNOWN`).
3. **Agreguj.** `panelVerdict = NATIVE` **tylko gdy oba** ucha dały `NATIVE`; w przeciwnym razie
   `REWORK`. Zbierz **sumę** linii-zarzutów z obu logów (to lista do przepisania).
4. **Rozgałęzienie:**
   - `panelVerdict == NATIVE` → wyjdź z debaty.
   - `REWORK` & `N < MAX` → **przepisz tylko zaczepione zdania** (suma flag obu uszu) w `04_working.md`,
     w stronę `voice_corpus.md` §A, warsztatem z `03b_revisor.md` (MOVE 0 + 4 tells). **Nie ruszaj
     nie-zaczepionych linii** (dryf) i **nie przekorygowuj** — życie wracaj ostrzejszym konkretnym
     obrazem, nigdy spłaszczeniem; chroń najmocniejsze obrazy (cold open, motyw, kotwice, obraz końcowy)
     **o ile nie niosą tella**. Zapisz `04_working.md`, `N = N + 1`, kontynuuj.
   - `REWORK`/`UNKNOWN` & `N == MAX` → **sprawdź hard-stop** (krok 5 niżej).
5. **Hard-stop (tylko BLOCKER w pozycji impact, przy `N == MAX`).** Przejrzyj sumę zarzutów z ostatniej
   rundy. Jeśli istnieje **nierozwiązany BLOCKER, którego tag pozycji to impact** (hook / cold open /
   kotwica / Permission Practice / recognition close), **NIE wysyłaj automatycznie** — zatrzymaj się i
   zapytaj użytkownika (AskUserQuestion), pokazując konkretne zdanie + nazwany tell:
   - **(a) Popraw w miejscu** — przepisz tę linię teraz wg wskazówki ucha, potem przejdź do Step 6 jako
     język-NATIVE.
   - **(b) Przyjmij z ostrzeżeniem** — przejdź do Step 6, oznacz język jako not-NATIVE (nagłówek WARNING).
   - **(c) Jeszcze jedna runda** — wykonaj **dokładnie jedną** dodatkową rundę (przydziel obu uszom
     `N = MAX + 1`, przepisz, ponownie sprawdź). Po tej rundzie hard-stop oferuje **już tylko (a) lub
     (b)** — nigdy kolejnej rundy (gwarancja zbieżności).
   Jeśli **nie ma** nierozwiązanego BLOCKERA w impakcie (są tylko FIX/WATCH poza impactem, albo werdykt
   nieparsowalny) → wyjdź, oznacz język not-NATIVE → ship z nagłówkiem WARNING w Step 6.
6. **Tryb zbieżności (N == MAX)** jest egzekwowany przez ucha per `03d_native_ear.md` (re-challenge
   nierozwiązanych + nowe kalki; bez nowych WATCH-ów) — z Twojej strony nic poza honorowaniem ich
   węższych findingów.
```

- [ ] **Step 4: Zaktualizuj Step 6 — nagłówek WARNING wskazuje OBA logi**

W sekcji „## Step 6 — Finalize" znajdź blok nagłówka WARNING:

```
# WARNING: Script shipped with <A–I: FLAG@iterN | language: REWORK@iterN> — review before recording.
# A–I (structure/policy): md/03c_review_iter<N>.md
# Language (native-ear): md/03d_nativeear_iter<N>.md
# Generated: <YYYY-MM-DD>
```

Zamień linię `# Language (native-ear): …` na **dwie** linie:

```
# Language — składnia-rejestr (A): md/03d_nativeear_A_iter<N>.md
# Language — rytm-klisza (B): md/03d_nativeear_B_iter<N>.md
```

(Dołącz tylko log(i) ucha/uszu, które nie osiągnęły `NATIVE`.)

- [ ] **Step 5: Zaktualizuj Step 7 — teardown OBU uszu**

W „## Step 7 — Tear down the team" znajdź:

```
Ask the `nativeear` teammate to shut down, then clean up the team.
```

Zamień na:

```
Ask **both** teammates (`nativeear-A` and `nativeear-B`) to shut down, then clean up the team.
```

- [ ] **Step 6: Zaktualizuj Step 8 (raport) i Notes**

1. W „## Step 8 — Report back", linię:
   `- **Native-ear debate:** verdict (NATIVE/REWORK) + rounds used`
   zamień na:
   `- **Native-ear panel:** werdykt A (składnia-rejestr) + werdykt B (rytm-klisza) + rundy; jeśli był hard-stop, którą opcję (a/b/c) wybrał użytkownik`
2. W „## Notes", w punkcie o koszcie tokenów:
   `- **Token cost:** the critic is one extra Opus context carried across ≤3 language rounds.`
   zamień na:
   `- **Token cost:** panel to **dwa** dodatkowe konteksty Opus × do 3 rund (do 6 przebiegów). `/draft` (in-session kat. J) zostaje tańszą ścieżką.`
3. W „## Notes", w punkcie o file ownership:
   `the teammate only *reads* `04_working.md` and *writes* its own `03d_nativeear_iter*.md`.`
   zamień na:
   `each teammate only *reads* `04_working.md` and *writes* its own `03d_nativeear_{A,B}_iter*.md`.`

- [ ] **Step 7: Zaktualizuj fallback w Step 1.5 (liczba mnoga)**

W „## Step 1.5", zdanie „If you cannot spawn a teammate at Step 4 …" pozostaje sensowne, ale dla
spójności zmień „spawn a teammate" na „spawn the panel teammates" i „the native-ear debate was skipped"
zostaje. Konkretnie znajdź:

```
If you cannot spawn a teammate at Step 4 (feature unavailable, spawn error), **do not hard-fail.**
```
zamień na:
```
If you cannot spawn the panel teammates at Step 4 (feature unavailable, spawn error), **do not hard-fail.**
```

- [ ] **Step 8: Weryfikacja**

Run (Grep, `output_mode: content` na `.claude/commands/draft-team.md`):
- `nativeear-A` → oczekiwane: ≥2 trafienia (spawn + assign). `nativeear-B` → ≥2.
- `panelVerdict` → ≥2 trafienia (agregacja + branch).
- `Hard-stop` → ≥1 trafienie. `AskUserQuestion` → ≥1.
- `03d_nativeear_A_iter` i `03d_nativeear_B_iter` → po ≥1 (Step 6 nagłówek + Step 5 read).
- Brak gołego `nativeear` jako pojedynczego teammate'a w Step 7 (ma być `nativeear-A` and `nativeear-B`).

Read: otwórz Step 5 i przeczytaj na głos pętlę — upewnij się, że `NATIVE` wychodzi tylko gdy oba ucha NATIVE, a hard-stop odpala wyłącznie na BLOCKERZE w impakcie przy `N == MAX`, i że opcja (c) daje dokładnie jedną dodatkową rundę.

- [ ] **Step 9: Commit**

```bash
git add .claude/commands/draft-team.md
git commit -m @'
feat(draft-team): two-ear native panel with union aggregation + impact hard-stop

Spawn nativeear-A (składnia-rejestr) and nativeear-B (rytm-klisza); panel
verdict is NATIVE only if both ears pass, flags are unioned for the rewrite.
At max round, an unresolved impact-position BLOCKER triggers a user hard-stop
(fix / accept-with-warning / one extra round) instead of silent ship. WARNING
header and teardown now cover both ears.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
'@
```

---

## Task 4: Dokumentacja — `agent_teams_reference.md`

**Files:**
- Modify: `docs/agent_teams_reference.md:348-354`

- [ ] **Step 1: Przepisz blok opisu `/draft-team`**

Zamień linie 348–354 (sekcja „### `/draft-team …`") na:

```markdown
### `/draft-team <slug> [architecture] [--sciezka]` — script chain + Native-Ear panel debate
- Lead runs 3a + the 3b↔3c loop in-session (3c scoped to categories **A–I**); a **panel of two
  cold-context `native-ear-critic` teammates** owns category **J** (translationese) in a ≤3-round
  debate: `nativeear-A` (soczewka składnia-rejestr) + `nativeear-B` (soczewka rytm-klisza).
- **Panel aggregation:** suma flag obu uszu; werdykt rundy = `NATIVE` tylko gdy **oba** ucha NATIVE.
  Próg każdego ucha: `≥1 BLOCKER / ≥2 FIX / ≥3 WATCH`. Ostatnia runda = tryb zbieżności (re-challenge
  nierozwiązanych + nowe kalki, bez nowych WATCH-ów). **Hard-stop:** nierozwiązany BLOCKER w pozycji
  impact przy ostatniej rundzie zatrzymuje i pyta użytkownika (popraw / przyjmij z ostrzeżeniem / jedna
  dodatkowa runda) zamiast cichego ship.
- Artifacts: `md/03d_nativeear_A_iter*.md`, `md/03d_nativeear_B_iter*.md`. Prompts:
  `workflows/pipeline/03d_native_ear.md`, `.claude/agents/native-ear-critic.md`,
  `.claude/commands/draft-team.md`.
- Fallback: plain `/draft` (in-session 3c runs A–J).
```

- [ ] **Step 2: Weryfikacja**

Run (Grep, `output_mode: content` na `docs/agent_teams_reference.md`): `panel of two` → ≥1. `nativeear-A` → ≥1. `≥2 FIX` → ≥1. `Hard-stop` → ≥1. Brak starego `one teammate ` `native-ear-critic` ` (Agent 3d) owns category **J**`.

- [ ] **Step 3: Commit**

```bash
git add docs/agent_teams_reference.md
git commit -m @'
docs(draft-team): document the two-ear native panel, thresholds, hard-stop

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
'@
```

---

## Follow-up (poza tym planem)

Jednoliniowa korekta wzmianki o `/draft-team` w `CLAUDE.md` (sekcja „Agent Teams (opt-in)": „cold-context
Native-Ear Critic (3d)" → „panel dwóch cold-context uszu (3d): składnia-rejestr + rytm-klisza"). Zrób
osobno przez skill `revise-claude-md`, żeby nie mieszać edycji pamięci projektu z tą zmianą.

---

## Self-Review (wykonane przy pisaniu planu)

- **Pokrycie spec:** §1 panel → Task 3 Step 2–3 + Task 1 Step 1; §2 progi/zakres/guard → Task 1 Step 2/4/5; §3 hard-stop → Task 3 Step 3 (krok 5); §4 zbieżność → Task 1 Step 3 + Task 3 Step 3 (krok 6); §5 pliki/artefakty/koszt → wszystkie taski + Task 3 Step 6; kryteria akceptacji 1–8 → pokryte (1: Task 3 Step 2; 2: Task 3 Step 3; 3: Task 1 Step 2; 4: Task 1 Step 4; 5: Task 1 Step 3; 6: Task 3 Step 3; 7: nie ruszamy `/draft`; 8: Task 1 Step 6 + Task 3 Step 5/Step 8).
- **Placeholdery:** brak TBD/TODO; każdy krok ma konkretną treść before/after.
- **Spójność nazw:** sufiks A = składnia-rejestr, B = rytm-klisza — konsekwentnie we wszystkich 4 plikach; `03d_nativeear_{A,B}_iter{N}.md` użyte identycznie w Task 1/2/3/4; `panelVerdict` i „hard-stop" zdefiniowane raz (Task 3) i nie sprzeczne; próg `≥2 FIX / ≥3 WATCH` identyczny w Task 1 i Task 4.
