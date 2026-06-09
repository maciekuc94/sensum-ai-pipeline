# Custom Slash Commands w Claude Code — kompletna instrukcja tworzenia

> Referencja „jak dobrze stworzyć custom slash command / skill". Źródło: https://code.claude.com/docs/en/slash-commands.md
> (pobrane 2026-06-09). Pola/nazwy pól frontmatter/nazwy narzędzi/bloki kodu zostawione **verbatim** po angielsku —
> to kontrakt z harnessem, nie tłumacz ich. Proza wyjaśniająca po polsku.

---

## Czym jest custom slash command i kiedy go tworzyć

Custom slash command (od wersji 2.x traktowany jako **skill**) to plik Markdown, który rozszerza możliwości
Claude Code o powtarzalne, nazwane workflow — wywoływane wpisaniem `/nazwa` w czacie. Tworzysz go, gdy:

- **regularnie wklejasz te same instrukcje** do czatu — wyłącz je do pliku raz i wywołuj komendą,
- **fragment `CLAUDE.md` urósł w procedurę** — procedury należą do skills/commands, fakty i reguły do `CLAUDE.md`,
- chcesz **ograniczyć narzędzia** dostępne na czas wykonania konkretnego zadania,
- chcesz **wymusić model lub poziom wysiłku** (inny niż sesyjny) dla danego workflow,
- **workflow ma efekty uboczne** (deploy, commit, wysyłka) i chcesz go wywoływać tylko ręcznie.

> **Konwergencja: `.claude/commands/` = `.claude/skills/`.**
> Plik w `.claude/commands/deploy.md` i skill w `.claude/skills/deploy/SKILL.md` tworzą dokładnie tę samą
> komendę `/deploy` i działają identycznie. Istniejące pliki `.claude/commands/` nie wymagają migracji —
> harness obsługuje oba formaty. Skills dodają opcjonalne funkcje (katalog z plikami pomocniczymi);
> commands są prostsze dla jednolinicowych instrukcji.

---

## Gdzie żyją pliki — zasięg i pierwszeństwo

Lokalizacja pliku wyznacza zasięg. Przy kolizji nazw wygrywa wyższy priorytet:

| Lokalizacja | Format | Zasięg | Komenda |
|---|---|---|---|
| Managed settings (admin) | dowolny | cała organizacja | najwyższy priorytet |
| `~/.claude/skills/<nazwa>/SKILL.md` | Skill | wszystkie Twoje projekty | `/nazwa` |
| `.claude/skills/<nazwa>/SKILL.md` | Skill | bieżący projekt | `/nazwa` |
| `.claude/commands/<nazwa>.md` | Command | bieżący projekt | `/nazwa` |
| `<plugin>/skills/<nazwa>/SKILL.md` | Plugin skill | gdzie plugin włączony | `/plugin:nazwa` |

**Plik command (`.claude/commands/`)** — nazwa pliku bez rozszerzenia staje się komendą:
`.claude/commands/publish.md` → `/publish`.

**Plik skill (`.claude/skills/<katalog>/SKILL.md`)** — nazwa katalogu staje się komendą:
`.claude/skills/publish/SKILL.md` → `/publish`.

**Plugin skill** — katalog jest poprzedzony nazwą pluginu:
`my-plugin/skills/review/SKILL.md` → `/my-plugin:review`.

Gdy skill i command mają tę samą nazwę, **skill ma pierwszeństwo**.

### Wykrywanie zmian na żywo

Claude Code obserwuje katalogi skills pod kątem zmian. Edycja istniejącego `SKILL.md` lub pliku `.claude/commands/`
**wchodzi w życie natychmiast**, bez restartu sesji. Utworzenie nowego katalogu skills od zera wymaga restartu.

---

## Format pliku

Każdy plik składa się z dwóch części:

1. **YAML frontmatter** między `---` — metadane i konfiguracja (wszystkie pola opcjonalne).
2. **Ciało Markdown** — instrukcje, które Claude wykonuje; to zawartość komendy.

```yaml
---
description: Co robi ta komenda i kiedy jej używać.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob, Agent
disable-model-invocation: true
---

# /moja-komenda

Instrukcje dla Claude...

$ARGUMENTS
```

Minimalne działające polecenie to sam plik Markdown bez frontmatter. Frontmatter
dodaje kontrolę nad zachowaniem.

---

## Pełna tabela pól frontmatter

Wszystkie pola są opcjonalne. Tylko `description` jest mocno zalecane.

| Pole | Opis |
|---|---|
| `name` | Wyświetlana nazwa w listingach. **Nie zmienia** nazwy komendy (ta pochodzi z nazwy pliku/katalogu), z jednym wyjątkiem: `SKILL.md` na korzeniu pluginu. |
| `description` | Co robi skill i kiedy go używać. Claude używa tego do automatycznego decydowania, kiedy załadować skill. Pierwsze słowa są najważniejsze — opis jest przycinany do 1 536 znaków. |
| `when_to_use` | Dodatkowy kontekst wyzwalaczy (dołączany do `description`, liczy się do limitu 1 536 znaków). |
| `argument-hint` | Podpowiedź wyświetlana podczas autouzupełniania. Przykład: `[issue-number]` lub `[filename] [format]`. |
| `arguments` | Nazwane argumenty pozycyjne do podstawiania `$name`. Przyjmuje ciąg oddzielony spacjami lub listę YAML. Nazwy odpowiadają pozycjom po kolei. |
| `disable-model-invocation` | `true` → Claude nie ładuje tego skilla automatycznie; nie pojawia się w jego kontekście opisów. Wywołasz tylko ręcznie przez `/nazwa`. Używaj dla workflow z efektami ubocznymi. Domyślnie: `false`. |
| `user-invocable` | `false` → ukrywa skill z menu `/`; Claude może go ładować automatycznie, ale Ty nie wywołasz ręcznie. Przydatne dla tła wiedzy, nie akcji. Domyślnie: `true`. |
| `allowed-tools` | Narzędzia, które Claude może używać bez pytania o zgodę gdy skill jest aktywny. Ciąg oddzielony spacją/przecinkiem lub lista YAML. |
| `disallowed-tools` | Narzędzia usuwane z puli gdy skill jest aktywny. Przydatne dla autonomicznych skillów, np. blokada `AskUserQuestion` w pętli. Ograniczenie znika po Twojej następnej wiadomości. |
| `model` | Model na czas działania skilla. Nadpisuje sesję tylko na bieżący turn; sesyjny model wraca przy następnym prompcie. Przyjmuje te same wartości co `/model` albo `inherit`. |
| `effort` | Poziom wysiłku gdy skill aktywny. Nadpisuje sesyjny. Opcje: `low`, `medium`, `high`, `xhigh`, `max` (dostępność zależy od modelu). |
| `context` | `fork` → skill działa w izolowanym subagent-kontekście; treść SKILL.md staje się promptem subagenta. |
| `agent` | Typ subagenta gdy `context: fork`. Opcje: `Explore`, `Plan`, `general-purpose` albo dowolny custom agent z `.claude/agents/`. Domyślnie `general-purpose`. |
| `hooks` | Hooki cyklu życia w zasięgu tego skilla. Patrz dokumentacja hooków. |
| `paths` | Wzorce glob ograniczające kiedy skill jest aktywowany automatycznie. Ciąg oddzielony przecinkiem lub lista YAML. |
| `shell` | Shell dla poleceń `` !`cmd` `` i bloków ` ```! `. Wartości: `bash` (domyślnie) lub `powershell`. Wymaga `CLAUDE_CODE_USE_POWERSHELL_TOOL=1`. |

---

## Argumenty: `$ARGUMENTS`, `$N`, `$name`

Możesz przekazywać argumenty do komendy. Są dostępne przez kilka wariantów podstawienia:

| Zmienna | Opis |
|---|---|
| `$ARGUMENTS` | Wszystko co wpisano po nazwie komendy jako jeden ciąg. Jeśli `$ARGUMENTS` nie występuje w treści, harness doklejа `ARGUMENTS: <wartość>` na końcu. |
| `$ARGUMENTS[N]` | Argument na pozycji N (indeksowany od 0). `$ARGUMENTS[0]` = pierwszy argument. |
| `$N` | Skrót: `$0` = pierwszy argument, `$1` = drugi itd. |
| `$name` | Nazwany argument z pola `arguments` frontmatter. Nazwy mapują się na pozycje po kolei. |
| `${CLAUDE_SESSION_ID}` | ID bieżącej sesji. Przydatne do logowania, plików per-sesja. |
| `${CLAUDE_EFFORT}` | Bieżący poziom wysiłku: `low`, `medium`, `high`, `xhigh`, lub `max`. |
| `${CLAUDE_SKILL_DIR}` | Ścieżka do katalogu zawierającego `SKILL.md`. Używaj w poleceniach bash do odwołań do skryptów bundlowanych ze skillem, bez względu na bieżący cwd. |

Argumenty wielowyrazowe owijaj cudzysłowami: `/moja-komenda "hello world" second` →
`$0` = `hello world`, `$1` = `second`.

Żeby wstawić dosłowny `$` przed cyfrą lub `ARGUMENTS`, poprzedź backslashem: `\$1.00`.

**Przykład z argumentami pozycyjnymi:**

```yaml
---
name: migrate-component
description: Migrate a component from one framework to another
---

Migrate the $0 component from $1 to $2.
Preserve all existing behavior and tests.
```

Wywołanie `/migrate-component SearchBar React Vue` podstawia `SearchBar` → `$0`, `React` → `$1`, `Vue` → `$2`.

**Przykład z nazwanymi argumentami:**

```yaml
---
name: session-logger
description: Log activity for this session
arguments: [action, target]
---

Log the following to logs/${CLAUDE_SESSION_ID}.log:

Action: $action
Target: $target
```

---

## Dynamiczny kontekst: `!` i bloki kodu `!`

Prefiksy `!` pozwalają **wstrzyknąć output powłoki zanim Claude zobaczy treść skilla**.
Polecenie wykonuje się **po stronie harnessu** — Claude widzi tylko wynik, nie polecenie.

### Forma inline: `` !`polecenie` ``

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request in 3-5 bullet points.
```

Każde `` !`polecenie` `` jest uruchamiane raz przed przekazaniem treści do Claude.
Output zastępuje placeholder jako zwykły tekst — nie jest skanowany ponownie.
Inline `!` działa tylko gdy `!` zaczyna linię lub pojawia się po białym znaku; `KEY=!`cmd`` nie działa.

### Forma wieloliniowa: blok ` ```! `

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

Wszystkie polecenia w bloku są uruchamiane, ich output wstrzykiwany w miejsce bloku.

> **Wyłączanie shell injection** (polityka organizacyjna): ustaw `"disableSkillShellExecution": true`
> w managed settings. Każde polecenie zostanie zastąpione `[shell command execution disabled by policy]`.
> Nie dotyczy bundled skills.

---

## Odwołania do plików przez `@`

W treści komendy możesz dołączyć zawartość pliku używając odwołania `@`:

```markdown
Przejrzyj ten plik: @src/main.py
```

Claude odczyta i wstawi zawartość pliku w miejsce odwołania. To standardowy mechanizm `@`-mentions
Claude Code — nie jest specyficzny dla komend, ale naturalnie sprawdza się w ich treści.

---

## Kontrola, kto może wywołać skill

Domyślnie zarówno Ty, jak i Claude możecie wywołać każdy skill. Dwa pola frontmatter to ograniczają:

| Frontmatter | Ty możesz wywołać | Claude może wywołać | Kiedy ładowany do kontekstu |
|---|---|---|---|
| (brak) | Tak | Tak | Opis zawsze; pełna treść przy wywołaniu |
| `disable-model-invocation: true` | Tak | Nie | Opis nie w kontekście; treść ładowana gdy Ty wywołasz |
| `user-invocable: false` | Nie | Tak | Opis zawsze; pełna treść przy wywołaniu |

```yaml
---
name: deploy
description: Deploy the application to production
disable-model-invocation: true
---

Deploy $ARGUMENTS to production:

1. Run the test suite
2. Build the application
3. Push to the deployment target
4. Verify the deployment succeeded
```

---

## Uruchamianie w subagent-kontekście (`context: fork`)

`context: fork` sprawia, że skill działa w izolowanym subagent-kontekście. Treść skilla staje się
promptem subagenta — subagent nie ma dostępu do historii Twojej rozmowy.

```yaml
---
name: deep-research
description: Research a topic thoroughly
context: fork
agent: Explore
---

Research $ARGUMENTS thoroughly:

1. Find relevant files using Glob and Grep
2. Read and analyze the code
3. Summarize findings with specific file references
```

Pole `agent` wskazuje typ subagenta (`Explore`, `Plan`, `general-purpose`, albo custom z `.claude/agents/`).
Jeśli pominięte — używa `general-purpose`.

> **`context: fork` ma sens tylko dla skillów z konkretnymi instrukcjami zadaniowymi.** Jeśli skill
> zawiera tylko wytyczne (np. konwencje API), subagent dostaje wytyczne bez żadnego zadania i nic
> nie zwraca.

---

## Pre-approve narzędzi dla skilla

`allowed-tools` daje Claude zgodę na używanie wymienionych narzędzi bez osobnego pytania o uprawnienia
gdy skill jest aktywny. Nie ogranicza dostępnych narzędzi — każde nadal jest wywoływalne, a globalne
ustawienia uprawnień obowiązują dla pozostałych.

```yaml
---
name: commit
description: Stage and commit the current changes
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *)
---
```

Dla skillów w `.claude/skills/` projektu `allowed-tools` wchodzi w życie po zaakceptowaniu dialogu
workspace trust dla tego folderu — tak samo jak reguły uprawnień w `.claude/settings.json`.

---

## Bundled skills (wbudowane komendy oparte na promptach)

Claude Code dostarcza zestaw bundled skills dostępnych w każdej sesji. Różnią się od typowych
built-in commands tym, że działają jako prompt-based: dają Claude szczegółowe instrukcje i pozwalają
mu orkiestrować pracę narzędziami. Wywołujesz je tak samo jak własne komendy.

Wybrane bundled skills:

| Skill | Cel |
|---|---|
| `/code-review` | Przegląd kodu pod kątem jakości, bezpieczeństwa, maintainability |
| `/debug` | Analiza błędów i testów, znajdowanie przyczyn |
| `/batch` | Uruchamianie operacji na wielu plikach/elementach |
| `/loop` | Powtarzanie skilla w pętli z zadanym interwałem |
| `/run` | Uruchomienie i sprawdzenie działania aplikacji |
| `/verify` | Potwierdzenie że zmiana działa (bez cofania się do testów) |
| `/run-skill-generator` | Nagranie przepisu startowego projektu dla `/run` i `/verify` |

Bundled skills są listowane razem z built-in commands w referencji poleceń; kolumna „Purpose" oznacza je jako **Skill**.

---

## Ograniczanie dostępu do skillów

Możesz kontrolować, które skille Claude może wywoływać:

**Wyłącz wszystkie skille** dodając do reguł deny w `/permissions`:

```text
Skill
```

**Zezwól lub zablokuj konkretne skille** przez reguły uprawnień:

```text
# Zezwól tylko konkretnym
Skill(commit)
Skill(review-pr *)

# Zablokuj konkretne
Skill(deploy *)
```

Składnia: `Skill(nazwa)` = dokładne dopasowanie, `Skill(nazwa *)` = prefix z dowolnymi argumentami.

**Ukryj indywidualny skill** przez `disable-model-invocation: true` w frontmatter — usuwa skill
z kontekstu Claude całkowicie.

---

## Nadpisywanie widoczności skillów przez `skillOverrides`

`skillOverrides` w pliku settings pozwala kontrolować widoczność skillów bez edycji ich `SKILL.md`.
Menu `/skills` może to zapisywać za Ciebie (zaznacz skill, naciśnij `Space` by przełączać stan, `Enter` by zapisać).

| Wartość | Widoczne dla Claude | W menu `/` |
|---|---|---|
| `"on"` | Nazwa i opis | Tak |
| `"name-only"` | Tylko nazwa | Tak |
| `"user-invocable-only"` | Ukryte | Tak |
| `"off"` | Ukryte | Nie |

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

Plugin skills nie są objęte `skillOverrides` — zarządzaj nimi przez `/plugin`.

---

## Cykl życia treści skilla w sesji

Gdy Ty lub Claude wywołacie skill, treść `SKILL.md` wchodzi do rozmowy jako jedna wiadomość i
**pozostaje tam przez całą sesję**. Claude Code nie odczytuje pliku ponownie przy kolejnych turach —
pisz instrukcje jako ciągłe wytyczne, nie jednorazowe kroki.

Przy auto-kompakcji kontekstu skille są przenoszone dalej w granicach budżetu tokenów. Po kompakcji
**5 000 pierwszych tokenów** każdego skilla jest re-dołączane; wszystkie skille dzielą łączny budżet
**25 000 tokenów** (wypełniany od najnowiej wywołanego). Jeśli skill przestaje wpływać na zachowanie
po kompakcji — wywołaj go ponownie.

---

## Pełny przykład pliku komendy (verbatim z projektu SENSUM)

Tak wygląda `.claude/commands/draft.md` — komenda orkiestrująca łańcuch subagentów przez pisanie
do plików i przekazywanie ścieżek; `$1` = slug wideo (`$ARGUMENTS[0]`):

```yaml
---
description: Łańcuch skryptu SENSUM (2026-06-07, Gen 4) — pisarz → ensemble (section-checker na każde ## + 1 arc-checker, równolegle, na zamrożonym oryginale) → fixer → ściskacz (zimny pass, tylko cięcie przegadania). Jeden przebieg, bez pętli, in-session, no API. Finalną redakcję robisz na docx.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob, Agent
---

# /draft — pisarz → section+arc checkery (ensemble) → fixer → ściskacz

...

`$1` = slug pod `outputs/videos_pl/`.

## Step 1 — Walidacja
Potwierdź, że istnieje `outputs/videos_pl/$1/md/02_verified_research.md`.

## Step 2 — Pisarz (zimny subagent Opus)
Zespawnuj subagenta z briefem:

> Jesteś pisarzem SENSUM, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/03a_writer.md` i wykonaj go dokładnie. Badania: ...
```

Klucz: `allowed-tools: Agent` umożliwia harness spawnowanie subagentów. `$1` mapuje na pierwszy
argument — wywołanie `/draft moj-slug` podstawia `moj-slug` wszędzie gdzie stoi `$1`.

---

## Minimalny przykład z dokumentacji (verbatim): `/fix-issue`

```yaml
---
name: fix-issue
description: Fix a GitHub issue
disable-model-invocation: true
---

Fix GitHub issue $ARGUMENTS following our coding standards.

1. Read the issue description
2. Understand the requirements
3. Implement the fix
4. Write tests
5. Create a commit
```

Wywołanie `/fix-issue 123` → Claude dostaje „Fix GitHub issue 123 following our coding standards...".

---

## Wskazówki praktyczne dla pipeline SENSUM

- **Skrypt Pythona przez `!`** — wywołaj skrypt przed przekazaniem treści do Claude:
  `` !`PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py moj-slug --generate` ``
  Output skryptu trafi do kontekstu; Claude widzi tylko wynik, nie polecenie.

- **Slug jako `$ARGUMENTS` / `$1`** — każda komenda producyjna przyjmuje slug jako jedyny argument;
  używaj `$1` (= `$ARGUMENTS[0]`) lub po prostu `$ARGUMENTS` jeśli slug zawsze jest jeden.

- **`argument-hint: <slug>`** — daje podpowiedź w autouzupełnieniu bez ograniczania co można wpisać.

- **`allowed-tools: Agent`** — wymagane gdy komenda spawnuje subagenty (`/draft`, `/hook`, `/visuals`).

- **`disable-model-invocation: true`** — użyj dla komend z efektami ubocznymi (`/publish`, `/package`)
  żeby Claude nie wywoływał ich sam na podstawie kontekstu rozmowy.

- **`model`** — możesz ustawić model per-komenda; np. komenda QA na szybszym/tańszym modelu, komenda
  twórcza na Opus 4.8.

- **Workflow file jako single source of truth** — instrukcje operacyjne trzymaj w `workflows/pipeline/`,
  a w ciele komendy pisz „przeczytaj `workflows/pipeline/03a_writer.md` i wykonaj go dokładnie" —
  tak robi `/draft`. Unikasz duplikacji instrukcji między komendą a workflow.

---

## Pułapki (gotchas)

- **Brak `$ARGUMENTS` w treści** — harness doklejuje `ARGUMENTS: <wartość>` na końcu; Claude to
  widzi, ale może to wyglądać nieelegancko. Lepiej umieścić `$ARGUMENTS` explicite w logicznym miejscu.
- **`!` musi być na początku linii lub po białym znaku** — `KEY=!`cmd`` nie uruchamia polecenia,
  zostaje jako tekst dosłowny.
- **Skill i command o tej samej nazwie** — skill wygrywa, command jest ignorowany. Pilnuj unikalności.
- **Nowy katalog skills** — wymaga restartu sesji żeby być obserwowany. Edycja istniejącego pliku
  działa bez restartu.
- **`context: fork` bez zadania** — jeśli skill zawiera tylko wytyczne (konwencje), a nie konkretne
  zadanie, subagent nie ma co zrobić i wraca z niczym. Fork ma sens tylko z akcją do wykonania.
- **`user-invocable: false` nie blokuje Skill tool** — Claude nadal może wywołać skill programatycznie
  przez `Skill(nazwa)`. Żeby całkowicie zablokować automatyczne wywołanie: `disable-model-invocation: true`.
- **Opis przycinany do 1 536 znaków** — klucz jest na początku; długie `when_to_use` może zostać
  ucięte. Sprawdź `/doctor` czy budżet opisów nie jest przepełniony.
- **`allowed-tools` w projekcie** — wchodzi w życie dopiero po zaakceptowaniu workspace trust dialog;
  przed tym Claude będzie pytać o każde narzędzie osobno.
- **`disallowed-tools` czyści się** po Twojej następnej wiadomości — to narzędzie na czas trwania
  wywołania skilla, nie trwały zakaz.
- **Skille nie zagnieżdżają się bezpośrednio** — skill może spawnować subagenta (`context: fork`
  lub `allowed-tools: Agent`), ale subagent nie może wywołać kolejnego forka.

---

*Źródło: https://code.claude.com/docs/en/slash-commands.md — pobrane 2026-06-09.*
