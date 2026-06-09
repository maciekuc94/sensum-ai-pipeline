# Subagenci w Claude Code — kompletna instrukcja tworzenia

> Referencja „jak dobrze stworzyć subagenta". Źródło: https://code.claude.com/docs/en/sub-agents
> (pobrane 2026-06-09). Pola/nazwy narzędzi/bloki kodu zostawione **verbatim** po angielsku — to kontrakt
> z harnessem, nie tłumacz ich. Proza wyjaśniająca po polsku.

---

## Czym jest subagent (i kiedy go w ogóle tworzyć)

Subagent to wyspecjalizowany asystent AI z **własnym oknem kontekstu**, **własnym system promptem**,
**wybranym zestawem narzędzi** i **niezależnymi uprawnieniami**. Robi swoją pracę u siebie i do głównej
rozmowy **wraca tylko podsumowanie** — surowe logi, wyniki wyszukiwań i treści plików zostają w jego
kontekście, nie zaśmiecają Twojego.

**Stwórz subagenta, kiedy:**
- zadanie poboczne zalałoby główną rozmowę outputem, którego i tak nie będziesz później czytać
  (testy, dokumentacja, przetwarzanie logów, przeszukiwanie kodu);
- **wielokrotnie** spawnujesz tego samego pracownika z tą samą instrukcją (warto go zapisać raz);
- chcesz **wymusić ograniczenia** — np. agent tylko-do-odczytu, bez `Write`/`Edit`;
- chcesz **obniżyć koszt** — rutynę przepuścić przez tańszy/szybszy model (Haiku).

**Czego subagent NIE potrafi:**
- **nie widzi historii** głównej rozmowy (poza forkiem — patrz niżej): startuje na świeżo;
- **nie może spawnować kolejnych subagentów** (brak zagnieżdżania — `Agent(...)` w definicji subagenta
  nie działa). Jeśli potrzebujesz delegacji wielopoziomowej → łańcuch subagentów z głównej rozmowy
  albo Skills;
- działa **w obrębie jednej sesji** (do równoległych, komunikujących się sesji służą *agent teams*).

### Co wybrać — szybka decyzja

| Sytuacja | Narzędzie |
|---|---|
| Zadanie generuje dużo outputu, liczy się tylko wynik (podsumowanie) | **Subagent** |
| Powtarzalny prompt/workflow, ale **w kontekście głównej rozmowy** | **Skill** (`Skill` tool) |
| Zadanie poboczne, ale subagent potrzebowałby zbyt dużo tła by być użyteczny | **Fork** (`/fork`) |
| Praca równoległa, gdzie workerzy muszą gadać ze sobą / podważać się nawzajem | **Agent team** |
| Szybkie pytanie o coś, co już jest w rozmowie (bez narzędzi, odpowiedź wyrzucana) | `/btw` |
| Częsty back-and-forth, wspólny kontekst faz (plan→impl→testy), drobna zmiana, liczy się latencja | **Główna rozmowa** |

---

## Najszybsza droga: `/agents` (zalecane)

Komenda `/agents` otwiera interaktywny interfejs do zarządzania subagentami (zakładki **Running** i
**Library**): podgląd wszystkich (built-in / user / project / plugin), tworzenie z kreatorem lub
generowaniem przez Claude, edycja, usuwanie.

Kreator prowadzi przez: **lokalizację** (Personal `~/.claude/agents/` vs Project) → **Generate with
Claude** (Claude sam pisze `name`, `description`, system prompt z Twojego opisu) → **wybór narzędzi**
→ **wybór modelu** → **kolor** → **pamięć** (memory scope) → zapis.

> **Subagent z `/agents` działa natychmiast.** Plik dodany/edytowany **ręcznie na dysku** wymaga
> **restartu sesji** (subagenci ładują się na starcie sesji).

---

## Gdzie żyje plik — zasięg (scope) i pierwszeństwo

Subagent to plik **Markdown z YAML frontmatter**. Lokalizacja wyznacza zasięg; przy kolizji nazw wygrywa
wyższy priorytet:

| Lokalizacja | Zasięg | Priorytet | Jak utworzyć |
|---|---|---|---|
| Managed settings | cała organizacja | 1 (najwyższy) | przez managed settings (admin) |
| `--agents` (flaga CLI) | bieżąca sesja | 2 | JSON przy starcie Claude Code |
| `.claude/agents/` | bieżący projekt | 3 | interaktywnie lub ręcznie |
| `~/.claude/agents/` | wszystkie Twoje projekty | 4 | interaktywnie lub ręcznie |
| `agents/` w pluginie | gdzie plugin włączony | 5 (najniższy) | instalacja pluginu |

- **Project** (`.claude/agents/`) — dla subagentów związanych z konkretnym repo; **commituj do gita**, by
  zespół ich używał i ulepszał. Wykrywane przez chodzenie w górę od cwd (katalogi z `--add-dir` **nie**
  są skanowane pod subagentów).
- **User** (`~/.claude/agents/`) — osobiste, dostępne we wszystkich projektach.
- Oba skanowane **rekurencyjnie** — można porządkować w podfolderach (`agents/review/`, `agents/research/`).
  W project/user **podfolder nie wpływa na tożsamość** — liczy się **wyłącznie pole `name`**.
  ⚠️ **Trzymaj `name` unikalne w całym drzewie:** dwa pliki z tym samym `name` w jednym zasięgu → jeden
  zostaje **po cichu odrzucony, bez ostrzeżenia**.
- **Plugin** — tu podfolder **staje się częścią identyfikatora**: `agents/review/security.md` w pluginie
  `my-plugin` rejestruje się jako `my-plugin:review:security`.

### Wariant sesyjny: `--agents` (JSON, bez zapisu na dysk)

Do szybkich testów/automatyzacji — subagenci istnieją tylko w tej sesji:

```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer. Use proactively after code changes.",
    "prompt": "You are a senior code reviewer. Focus on code quality, security, and best practices.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  },
  "debugger": {
    "description": "Debugging specialist for errors and test failures.",
    "prompt": "You are an expert debugger. Analyze errors, identify root causes, and provide fixes."
  }
}'
```

JSON przyjmuje te same pola co plik (`prompt` = system prompt, odpowiednik ciała Markdown): `description`,
`prompt`, `tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`, `hooks`, `maxTurns`,
`skills`, `initialPrompt`, `memory`, `effort`, `background`, `isolation`, `color`.

---

## Anatomia pliku

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
tools: Read, Glob, Grep
model: sonnet
---

You are a code reviewer. When invoked, analyze the code and provide
specific, actionable feedback on quality, security, and best practices.
```

- **Frontmatter** = metadane i konfiguracja. **Ciało Markdown** = **system prompt** kierujący zachowaniem.
- Subagent dostaje **tylko ten system prompt** (+ podstawowe info o środowisku, np. cwd) — **nie** dostaje
  pełnego system promptu Claude Code.
- Startuje w **bieżącym cwd głównej rozmowy**. `cd` w narzędziu Bash/PowerShell **nie utrzymuje się**
  między wywołaniami i nie zmienia cwd głównej rozmowy. Po izolowaną kopię repo → `isolation: worktree`.

---

## Pełna tabela pól frontmatter

Wymagane są **tylko** `name` i `description`.

| Pole | Wym. | Opis |
|---|---|---|
| `name` | **Tak** | Unikalny identyfikator, małe litery i myślniki. Hooki dostają go jako `agent_type`. Nazwa pliku **nie musi** pasować |
| `description` | **Tak** | **Kiedy** Claude ma delegować do tego subagenta (na tym opiera się delegacja — patrz niżej) |
| `tools` | Nie | Allowlista narzędzi. Pominięte → **dziedziczy wszystkie**. Żeby wstrzyknąć Skills, użyj `skills`, nie listuj tu `Skill` |
| `disallowedTools` | Nie | Denylista — usuwa z odziedziczonej/podanej listy |
| `model` | Nie | `sonnet`, `opus`, `haiku`, pełne ID (np. `claude-opus-4-8`) albo `inherit`. Domyślnie `inherit` |
| `permissionMode` | Nie | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`. Ignorowane dla subagentów z pluginu |
| `maxTurns` | Nie | Maks. liczba tur agentic zanim subagent się zatrzyma |
| `skills` | Nie | Skills wstrzykiwane do kontekstu na starcie (**pełna treść**, nie sam opis). Subagent i tak może wołać inne skills przez `Skill` |
| `mcpServers` | Nie | Serwery MCP dla tego subagenta. Wpis = nazwa już skonfigurowanego serwera albo inline definicja. Ignorowane dla pluginów |
| `hooks` | Nie | Hooki cyklu życia w zasięgu tego subagenta. Ignorowane dla pluginów |
| `memory` | Nie | Trwała pamięć: `user`, `project`, `local`. Włącza uczenie się między sesjami |
| `background` | Nie | `true` → zawsze uruchamiaj w tle. Domyślnie `false` |
| `effort` | Nie | Poziom wysiłku gdy subagent aktywny; nadpisuje sesję. `low`/`medium`/`high`/`xhigh`/`max` (zależnie od modelu) |
| `isolation` | Nie | `worktree` → izolowana kopia repo w tymczasowym git worktree (domyślnie z domyślnej gałęzi, nie `HEAD` rodzica). Auto-sprzątane jeśli brak zmian |
| `color` | Nie | Kolor w UI: `red`, `blue`, `green`, `yellow`, `purple`, `orange`, `pink`, `cyan` |
| `initialPrompt` | Nie | Auto-wysyłane jako pierwsza tura usera, **gdy agent działa jako sesja główna** (`--agent`/setting `agent`). Komendy i skills są przetwarzane; doklejane przed promptem usera |

---

## `description` — najważniejsze pole (steruje delegacją)

Claude decyduje **kiedy** sięgnąć po subagenta na podstawie: opisu zadania w prompcie usera, **pola
`description`** i bieżącego kontekstu. To `description` robi robotę — pisz je konkretnie i „od strony
wyzwalacza":

- powiedz **wprost, kiedy** użyć agenta (np. *„Use immediately after writing or modifying code"*);
- żeby zachęcić do **proaktywnej** delegacji, wpleć frazy typu **`use proactively`**,
  **`MUST BE USED`**, **`use immediately after ...`**;
- jeden agent = **jedno zadanie**; rozmyte „do wszystkiego" psuje trafność delegacji.

Przykłady dobrych opisów (z oficjalnych wzorców):
- `Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.`
- `Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.`

---

## Narzędzia: `tools` i `disallowedTools`

- **Pominięte `tools` → subagent dziedziczy wszystkie** narzędzia wewnętrzne i MCP z głównej rozmowy.
- **`tools` = allowlista** (tylko te), **`disallowedTools` = denylista** (wszystko oprócz tych).
- Gdy oba ustawione: **najpierw `disallowedTools`, potem `tools`** rozwiązywane na tym, co zostało.
  Narzędzie w obu → usunięte.

```markdown
---
name: safe-researcher
description: Research agent with restricted capabilities
tools: Read, Grep, Glob, Bash      # wyłącznie te — bez Write/Edit/MCP
---
```

```markdown
---
name: no-writes
description: Inherits every tool except file writes
disallowedTools: Write, Edit       # wszystko poza zapisem plików
---
```

**Narzędzia niedostępne dla subagentów** — nawet jeśli wpiszesz je w `tools`:
`Agent`, `AskUserQuestion`, `EnterPlanMode`, `ExitPlanMode` (chyba że `permissionMode: plan`),
`ScheduleWakeup`, `WaitForMcpServers`. (Zależą od UI/stanu sesji głównej.)

**Ograniczanie, jakich subagentów wolno spawnować** — tylko gdy agent działa jako wątek główny
(`claude --agent`): składnia `Agent(typ1, typ2)` w `tools` jako allowlista; samo `Agent` (bez nawiasów)
= dowolny; brak `Agent` = żadnych. W definicji **subagenta** to bez znaczenia — subagenci i tak nie
spawnują subagentów. (Od v2.1.63 `Task` przemianowane na `Agent`; stare `Task(...)` działa jako alias.)

---

## `model` — wybór i kolejność rozwiązywania

Wartości: **alias** (`sonnet`/`opus`/`haiku`), **pełne ID** (`claude-opus-4-8`, `claude-sonnet-4-6` — jak
`--model`), **`inherit`** (jak główna rozmowa). Pominięte → **`inherit`**.

Kolejność rozstrzygania przy wywołaniu:
1. zmienna `CLAUDE_CODE_SUBAGENT_MODEL` (jeśli ustawiona),
2. parametr `model` przekazany per-wywołanie,
3. `model` z frontmatter definicji,
4. model głównej rozmowy.

> Routowanie rutyny na Haiku/Sonnet to główny sposób kontroli kosztów. Built-in **Explore** chodzi na
> Haiku właśnie dlatego.

---

## `permissionMode`

| Tryb | Zachowanie |
|---|---|
| `default` | Standardowe sprawdzanie z promptami |
| `acceptEdits` | Auto-akceptacja edycji plików i typowych komend FS w cwd / `additionalDirectories` |
| `auto` | Klasyfikator w tle ocenia komendy i zapisy do chronionych katalogów |
| `dontAsk` | Auto-odmowa promptów (jawnie dozwolone narzędzia nadal działają) |
| `bypassPermissions` | Pomija prompty — **ostrożnie** (pozwala zapis do `.git`, `.claude`, `.vscode` itd.; `rm -rf /` i tak prompuje jako bezpiecznik) |
| `plan` | Tryb planowania (tylko odczyt) |

Jeśli **rodzic** używa `bypassPermissions` lub `acceptEdits` → **ma pierwszeństwo**, nie da się nadpisać.
Jeśli rodzic w `auto` → subagent dziedziczy `auto`, a jego `permissionMode` z frontmatter jest ignorowany.

---

## `skills` — preload wiedzy domenowej

```markdown
---
name: api-developer
description: Implement API endpoints following team conventions
skills:
  - api-conventions
  - error-handling-patterns
---

Implement API endpoints. Follow the conventions and patterns from the preloaded skills.
```

Wstrzykuje **pełną treść** wymienionych skills na starcie. To steruje, **co preloadowane**, nie **co
dostępne** — bez tego pola subagent i tak odkryje i zawoła skills przez `Skill`. Żeby całkiem zablokować
skills: pomiń `Skill` w `tools` lub dodaj do `disallowedTools`. Nie da się preloadować skilla z
`disable-model-invocation: true` (brakujący/wyłączony jest pomijany z warningiem w debug logu).

---

## `memory` — trwała pamięć między sesjami

```markdown
---
name: code-reviewer
description: Reviews code for quality and best practices
memory: user
---

You are a code reviewer. As you review code, update your agent memory with
patterns, conventions, and recurring issues you discover.
```

| Zasięg | Lokalizacja | Kiedy |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name>/` | wiedza przydatna we wszystkich projektach |
| `project` | `.claude/agent-memory/<name>/` | wiedza projektowa, do współdzielenia przez gita **(zalecany default)** |
| `local` | `.claude/agent-memory-local/<name>/` | wiedza projektowa, **bez** commitowania |

Po włączeniu: system prompt dostaje instrukcje czytania/zapisu katalogu pamięci **oraz pierwsze 200 linii
/ 25 KB `MEMORY.md`** (co pierwsze) z poleceniem kuracji powyżej limitu; automatycznie włączane są
`Read`/`Write`/`Edit`. Działa najlepiej, gdy w ciele promptu **wprost** poprosisz agenta, by zaglądał do
pamięci przed pracą i zapisywał wnioski po.

---

## Hooki

**Dwa miejsca:**

**(1) W frontmatter** — działają tylko gdy ten subagent jest aktywny, sprzątane po zakończeniu.
Wspierane wszystkie eventy; najczęstsze: `PreToolUse`, `PostToolUse`, `Stop` (przy uruchomieniu jako
subagent `Stop` jest konwertowany na `SubagentStop`).

```markdown
---
name: code-reviewer
description: Review code changes with automatic linting
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-command.sh $TOOL_INPUT"
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: "./scripts/run-linter.sh"
---
```

**(2) W `settings.json`** — reagują na cykl życia subagentów w sesji głównej: `SubagentStart`
(matcher = nazwa typu agenta) i `SubagentStop`.

```json
{
  "hooks": {
    "SubagentStart": [
      { "matcher": "db-agent",
        "hooks": [{ "type": "command", "command": "./scripts/setup-db-connection.sh" }] }
    ],
    "SubagentStop": [
      { "hooks": [{ "type": "command", "command": "./scripts/cleanup-db-connection.sh" }] }
    ]
  }
}
```

> Na Windows pisz skrypty hooków w PowerShell i dodaj `shell: powershell` do wpisu hooka.

**Wyłączanie subagentów** — `permissions.deny` w settings: `"deny": ["Agent(Explore)", "Agent(my-agent)"]`
(działa dla built-in i custom), albo `claude --disallowedTools "Agent(Explore)"`.

---

## Praca z subagentami

### Delegacja automatyczna
Claude sam deleguje na podstawie `description`. Stąd: dobre `description` = dobra delegacja.

### Wywołanie jawne (3 poziomy eskalacji)
- **Język naturalny** — wymień subagenta w prompcie, Claude zwykle deleguje:
  `Use the test-runner subagent to fix failing tests`
- **`@`-mention** — gwarantuje, że ten subagent obsłuży jedno zadanie. W pickerze `@` albo ręcznie
  `@agent-<name>` (plugin: `@agent-my-plugin:code-reviewer`). Twój pełny prompt nadal idzie do Claude —
  mention steruje **którym** subagentem, nie jego promptem.
- **Cała sesja jako subagent** — `claude --agent code-reviewer` (system prompt subagenta **zastępuje**
  domyślny CC, jak `--system-prompt`; CLAUDE.md/pamięć ładują się normalnie). Default dla projektu:
  `{ "agent": "code-reviewer" }` w `.claude/settings.json` (flaga CLI nadpisuje setting).

### Foreground vs background
- **Foreground** — blokuje główną rozmowę, prompty o uprawnienia trafiają do Ciebie.
- **Background** — działa równolegle; korzysta z **już przyznanych** uprawnień i **auto-odrzuca** każde
  wywołanie, które normalnie by prompowało (pytania doprecyzowujące → wywołanie pada, ale agent leci dalej).
  Wymuszenie: poproś „run this in the background" albo **Ctrl+B**. Globalny kill-switch:
  `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1`. Przy `CLAUDE_CODE_FORK_SUBAGENT=1` **każdy** spawn idzie w tło.

### Wzorce
- **Izolacja głośnego outputu** — testy/dokumentacja/logi w subagencie, do głównej rozmowy wraca tylko
  podsumowanie: `Use a subagent to run the test suite and report only the failing tests with their error messages`.
- **Równoległy research** — kilka niezależnych subagentów naraz: `Research the authentication, database,
  and API modules in parallel using separate subagents` (działa, gdy ścieżki nie zależą od siebie).
- **Łańcuch** — sekwencja, gdzie Claude przekazuje kontekst dalej: `Use the code-reviewer subagent to
  find performance issues, then use the optimizer subagent to fix them`.

---

## Co ładuje się na starcie (kluczowe dla pisania promptu)

Każdy subagent (poza forkiem) startuje z **świeżym, izolowanym** kontekstem: **nie widzi** historii
rozmowy, wcześniej zawołanych skills ani plików, które Claude już czytał. Jego początkowy kontekst to:

- **System prompt** — własny (ciało MD / pole `prompt`) + detale środowiska, **nie** pełny CC system prompt;
- **Task message** — prompt delegujący, który Claude pisze przy przekazaniu zadania;
- **CLAUDE.md i pamięć** — cała hierarchia, którą ładuje główna rozmowa (`~/.claude/CLAUDE.md`, reguły
  projektu, `CLAUDE.local.md`, polityki managed);
- **Git status** — snapshot z początku sesji rodzica (brak, gdy to nie repo lub `includeGitInstructions:false`);
- **Preloaded skills** — pełna treść z pola `skills`.

> **Explore i Plan jako jedyne pomijają CLAUDE.md i git status** (dla szybkości/taniości) — nie ma pola,
> by to zmienić. Główna rozmowa i tak czyta ich wyniki z pełnym CLAUDE.md, więc większość reguł nie musi
> docierać do samego subagenta. **Jeśli reguła MUSI dotrzeć** (np. „ignoruj `vendor/`") — **powtórz ją w
> prompcie delegującym.** To najczęstszy błąd: zakładanie, że subagent „wie" coś z rozmowy.

### Resume i kompakcja
- **Resume** — poproś Claude, by kontynuował poprzedniego subagenta (zachowuje pełną historię, tool calls,
  rozumowanie). Mechanizm `SendMessage` (po ID agenta) działa tylko przy włączonym
  `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`. Transkrypty: `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl`.
- Kompakcja głównej rozmowy **nie rusza** transkryptów subagentów (osobne pliki). Subagenci mają
  auto-kompakcję (~95% pojemności; `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` obniża próg). Sprzątanie wg
  `cleanupPeriodDays` (domyślnie 30 dni).

---

## Fork bieżącej rozmowy

Fork to subagent, który **dziedziczy całą dotychczasową rozmowę** zamiast startować na świeżo: ten sam
system prompt, narzędzia, model i historia wiadomości — możesz dać mu zadanie poboczne bez tłumaczenia
kontekstu. Jego tool calls i tak zostają poza Twoją rozmową; wraca tylko wynik. Używaj, gdy named subagent
potrzebowałby zbyt dużo tła, albo gdy chcesz **równolegle spróbować kilku podejść** z tego samego punktu.

- Ręcznie: `/fork draft unit tests for the parser changes so far` (Claude nazwie fork od pierwszych słów
  dyrektywy; pojawia się w panelu pod promptem, działa w tle, wynik wraca jako wiadomość).
- Sterowanie panelem: `↑/↓` między wierszami, `Enter` otwiera transkrypt + follow-up, `x` zamyka/zatrzymuje,
  `Esc` wraca do promptu.
- Włączanie: od v2.1.161 `/fork` domyślnie; wcześniej `CLAUDE_CODE_FORK_SUBAGENT=1`. Przy włączonym fork
  mode Claude spawnuje fork wszędzie tam, gdzie użyłby general-purpose (named jak Explore — bez zmian), a
  **każdy** spawn idzie w tło. Fork **nie może** spawnować kolejnych forków.

| | **Fork** | **Named subagent** |
|---|---|---|
| Kontekst | pełna historia rozmowy | świeży + przekazany prompt |
| System prompt i narzędzia | jak sesja główna | z pliku definicji |
| Model | jak sesja główna | z pola `model` |
| Uprawnienia | prompty w Twoim terminalu | auto-odrzucane w tle |
| Prompt cache | **współdzielony z główną sesją** (taniej) | osobny |

---

## Best practices (oficjalne + sprawdzone)

1. **Jeden subagent = jedno zadanie.** Wąsko wyspecjalizowany bije „uniwersalnego".
2. **Szczegółowe `description`** od strony wyzwalacza — to ono decyduje o delegacji. Wpleć
   `use proactively` / `use immediately after ...` gdy chcesz proaktywności.
3. **Ograniczaj narzędzia** do niezbędnego minimum (bezpieczeństwo + skupienie). Reviewer = bez
   `Write`/`Edit`; debugger = z `Edit`, bo naprawia.
4. **Konkretny workflow w ciele promptu** — ponumerowane „When invoked: 1… 2… 3…" + format outputu
   (priorytety: Critical / Warning / Suggestion).
5. **Commituj project-subagentów do gita** — zespół ich używa i ulepsza.
6. **Powtórz krytyczne reguły w prompcie delegującym** — subagent nie zna historii rozmowy.
7. **Plik ręczny → restart sesji.** `/agents` → od ręki.
8. **Pilnuj unikalności `name`** w całym drzewie — duplikat ginie po cichu.

### Szablon do skopiowania

```markdown
---
name: my-agent
description: <co robi + KIEDY delegować; dodaj "use proactively" jeśli ma się odpalać sam>
tools: Read, Grep, Glob          # tylko niezbędne; pomiń pole = dziedziczy wszystkie
model: inherit                   # albo sonnet / opus / haiku / pełne ID
# permissionMode: plan           # opcjonalnie
# memory: project                # opcjonalnie (uczenie się między sesjami)
---

You are a <rola>. <jedno zdanie misji>

When invoked:
1. ...
2. ...
3. ...

<Checklista / na co patrzeć>

Provide output as:
- Critical (must fix)
- Warnings (should fix)
- Suggestions (consider)
```

---

## Pełne przykłady (verbatim z dokumentacji)

### Code reviewer — tylko odczyt, bez modyfikacji

```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---

You are a senior code reviewer ensuring high standards of code quality and security.

When invoked:
1. Run git diff to see recent changes
2. Focus on modified files
3. Begin review immediately

Review checklist:
- Code is clear and readable
- Functions and variables are well-named
- No duplicated code
- Proper error handling
- No exposed secrets or API keys
- Input validation implemented
- Good test coverage
- Performance considerations addressed

Provide feedback organized by priority:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (consider improving)

Include specific examples of how to fix issues.
```

### Debugger — analizuje i naprawia (ma `Edit`)

```markdown
---
name: debugger
description: Debugging specialist for errors, test failures, and unexpected behavior. Use proactively when encountering any issues.
tools: Read, Edit, Bash, Grep, Glob
---

You are an expert debugger specializing in root cause analysis.

When invoked:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

Debugging process:
- Analyze error messages and logs
- Check recent code changes
- Form and test hypotheses
- Add strategic debug logging
- Inspect variable states

For each issue, provide:
- Root cause explanation
- Evidence supporting the diagnosis
- Specific code fix
- Testing approach
- Prevention recommendations

Focus on fixing the underlying issue, not the symptoms.
```

### Data scientist — domena poza kodem, jawnie `model: sonnet`

```markdown
---
name: data-scientist
description: Data analysis expert for SQL queries, BigQuery operations, and data insights. Use proactively for data analysis tasks and queries.
tools: Bash, Read, Write
model: sonnet
---

You are a data scientist specializing in SQL and BigQuery analysis.

When invoked:
1. Understand the data analysis requirement
2. Write efficient SQL queries
3. Use BigQuery command line tools (bq) when appropriate
4. Analyze and summarize results
5. Present findings clearly

Key practices:
- Write optimized SQL queries with proper filters
- Use appropriate aggregations and joins
- Include comments explaining complex logic
- Format results for readability
- Provide data-driven recommendations

For each analysis:
- Explain the query approach
- Document any assumptions
- Highlight key findings
- Suggest next steps based on data

Always ensure queries are efficient and cost-effective.
```

### Database query validator — `Bash` + walidacja hookiem (tylko SELECT)

Gdy potrzebujesz precyzji większej niż `tools`: dopuść `Bash`, ale `PreToolUse` blokuje zapisy.

```markdown
---
name: db-reader
description: Execute read-only database queries. Use when analyzing data or generating reports.
tools: Bash
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/validate-readonly-query.sh"
---

You are a database analyst with read-only access. Execute SELECT queries to answer questions about the data.

When asked to analyze data:
1. Identify which tables contain the relevant data
2. Write efficient SELECT queries with appropriate filters
3. Present results clearly with context

You cannot modify data. If asked to INSERT, UPDATE, DELETE, or modify schema, explain that you only have read access.
```

Skrypt walidujący (czyta JSON ze stdin, wyciąga komendę, `exit 2` blokuje i zwraca błąd do Claude przez stderr):

```bash
#!/bin/bash
# Blocks SQL write operations, allows SELECT queries

# Read JSON input from stdin
INPUT=$(cat)

# Extract the command field from tool_input using jq
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Block write operations (case-insensitive)
if echo "$COMMAND" | grep -iE '\b(INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|REPLACE|MERGE)\b' > /dev/null; then
  echo "Blocked: Write operations not allowed. Use SELECT queries only." >&2
  exit 2
fi

exit 0
```

Na macOS/Linux: `chmod +x ./scripts/validate-readonly-query.sh`. Na Windows: PowerShell + `shell: powershell`.

---

## Pułapki (gotchas)

- **Plik ręczny nie ładuje się od razu** — restart sesji. `/agents` omija ten problem.
- **Duplikat `name` w jednym zasięgu = cichy drop** jednego z plików, bez ostrzeżenia.
- **Subagenci nie zagnieżdżają się** — `Agent(...)` w definicji subagenta nie działa; potrzebujesz łańcucha
  z głównej rozmowy albo Skills.
- **Background auto-odrzuca prompty** — jeśli agent potrzebowałby uprawnień/pytania, padnie cicho; przy
  braku uprawnień uruchom ponownie w foreground.
- **`cd` nie utrzymuje się** między tool calls; po izolację → `isolation: worktree`.
- **Plugin-subagenci ignorują `hooks`, `mcpServers`, `permissionMode`** — przenieś plik do
  `.claude/agents/` lub `~/.claude/agents/`, jeśli ich potrzebujesz.
- **Dużo subagentów zwracających obszerne wyniki** też zżera kontekst głównej rozmowy — do trwałej
  równoległości użyj agent teams.
- **Subagent nie zna rozmowy** — wszystko, co istotne, musi być w `description`, ciele promptu albo
  prompcie delegującym.

---

*Źródło: https://code.claude.com/docs/en/sub-agents — pobrane 2026-06-09. Wersja `.md`: `…/sub-agents.md`.*
