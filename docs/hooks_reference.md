# Hooki w Claude Code — kompletna instrukcja

> Referencja „jak napisać i konfigurować hooki". Źródła:
> - https://code.claude.com/docs/en/hooks-guide.md (przewodnik — use cases, troubleshooting)
> - https://code.claude.com/docs/en/hooks.md (pełna referencja — eventy, schema, exit codes)
>
> Pobrane **2026-06-09**. Nazwy eventów, pól JSON, exit codes i bloki kodu zostawione **verbatim**
> po angielsku — to kontrakt z harnessem. Proza wyjaśniająca po polsku.

---

## Czym są hooki i do czego służą

Hook to **polecenie powłoki** (lub wywołanie HTTP/MCP/promptu), które Claude Code odpala automatycznie
w konkretnym momencie sesji — przed wykonaniem narzędzia, po zakończeniu tury, przy starcie sesji itd.
Hooki pozwalają:

- **blokować** niebezpieczne operacje zanim zostaną wykonane (`PreToolUse` → `exit 2`);
- **wstrzykiwać kontekst** do rozmowy (stan gałęzi, wyniki testów, aktywne flagi środowiska);
- **reagować na zdarzenia** (powiadomienie, gdy Claude czeka, formatowanie po zapisaniu pliku);
- **wymuszać standardy** projektu (linting po edycji, wymóg zaliczenia testów przed `Stop`).

Hooki są **deterministyczne**: to zwykłe skrypty. To ty kontrolujesz co robią — model ich nie pisze na
bieżąco.

> **Bezpieczeństwo — najważniejsze ostrzeżenie:** hooki wykonują się z **pełnymi uprawnieniami twojego
> użytkownika systemu**. Mogą modyfikować, usuwać i odczytywać wszystkie pliki dostępne twojemu
> kontu. Sprawdź i przetestuj każdy hook przed dodaniem do konfiguracji.

---

## Gdzie konfigurować hooki

Hooki definiuje się w plikach JSON ustawień Claude Code. Miejsce zapisu decyduje o zasięgu:

| Lokalizacja | Zasięg | Współdzielony z repozytorium |
|:---|:---|:---|
| `~/.claude/settings.json` | wszystkie twoje projekty | nie |
| `.claude/settings.json` | bieżący projekt | tak (możesz commitować) |
| `.claude/settings.local.json` | bieżący projekt | nie (gitignored) |
| Managed policy settings | cała organizacja | tak (admin) |
| `hooks/hooks.json` w pluginie | gdy plugin jest aktywny | tak (z pluginem) |
| Frontmatter skilla lub agenta | gdy komponent jest aktywny | tak (z komponentem) |

Administratorzy mogą ustawić `allowManagedHooksOnly`, by zablokować hooki użytkownika, projektu
i pluginów (wyjątek: pluginy z `enabledPlugins` w managed settings).

Do przeglądania skonfigurowanych hooków służy komenda `/hooks` — pokazuje wszystkie eventy, liczby
hooków, źródło każdego (User / Project / Local / Plugin / Session / Built-in) i szczegóły handlera.
Menu jest **tylko do odczytu** — żeby edytować, zmień bezpośrednio plik JSON.

---

## Struktura konfiguracji

Trzy poziomy zagnieżdżenia:

1. **Hook event** — punkt w cyklu życia, np. `PreToolUse`, `Stop`
2. **Matcher group** — filtr kiedy hook ma odpalić, np. „tylko dla narzędzia Bash"
3. **Hook handler** — co uruchomić: polecenie powłoki, URL HTTP, narzędzie MCP, prompt lub agent

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/validate-bash.sh"
          }
        ]
      }
    ]
  }
}
```

### Matcher — wzorzec dopasowania

Pole `matcher` filtruje, kiedy hook odpala. Reguły interpretacji:

| Wartość matchera | Traktowana jako | Przykład |
|:---|:---|:---|
| `"*"`, `""` lub pominięta | dopasuj wszystko | odpala na każde wystąpienie eventu |
| tylko litery, cyfry, `_`, `\|` | dokładny string lub lista rozdzielona `\|` | `Bash` tylko Bash; `Edit\|Write` oba |
| zawiera inne znaki | wyrażenie regularne JavaScript | `^Notebook` wszystkie narzędzia Notebook; `mcp__memory__.*` wszystkie narzędzia serwera `memory` |

**Co matcher filtruje — zależy od eventu:**

| Event | Pole filtrowane przez matcher | Przykładowe wartości |
|:---|:---|:---|
| `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied` | nazwa narzędzia | `Bash`, `Edit\|Write`, `mcp__.*` |
| `SessionStart` | sposób rozpoczęcia sesji | `startup`, `resume`, `clear`, `compact` |
| `SessionEnd` | powód zakończenia sesji | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` |
| `SubagentStart`, `SubagentStop` | typ agenta | `general-purpose`, `Explore`, `Plan`, nazwa własna |
| `Notification` | typ powiadomienia | `permission_prompt`, `idle_prompt`, `auth_success` |
| `PreCompact`, `PostCompact` | co wywołało kompakcję | `manual`, `auto` |
| `ConfigChange` | źródło konfiguracji | `user_settings`, `project_settings`, `local_settings`, `skills` |
| `FileChanged` | nazwy plików do śledzenia (dosłowne) | `.envrc\|.env` |
| `UserPromptExpansion` | nazwa komendy | nazwy twoich skillli i komend |
| `Elicitation`, `ElicitationResult` | nazwa serwera MCP | nazwy skonfigurowanych serwerów MCP |

Eventy bez wsparcia dla matchera (ignorują pole `matcher`):
`UserPromptSubmit`, `PostToolBatch`, `Stop`, `TeammateIdle`, `TaskCreated`, `TaskCompleted`,
`WorktreeCreate`, `WorktreeRemove`, `MessageDisplay`, `CwdChanged`.

#### Narzędzia MCP w matcherze

Narzędzia MCP mają format `mcp__<serwer>__<narzędzie>`. Aby dopasować wszystkie narzędzia serwera,
użyj `.*` na końcu (samo `mcp__memory` to dokładny string — nie pasuje do żadnego narzędzia):

```
mcp__memory__.*        → wszystkie narzędzia serwera memory
mcp__.*__write.*       → każde narzędzie zaczynające się od "write" z dowolnego serwera
```

#### Doprecyzowanie przez pole `if`

Na każdym handlerze można ustawić pole `if` (składnia reguł uprawnień), które działa jak dodatkowy
filtr — np. `"Bash(git *)"` odpala tylko gdy subpolecenie pasuje do `git *`,
`"Edit(*.ts)"` tylko dla plików TypeScript. Dostępne wyłącznie dla eventów narzędziowych.

---

## Typy handlerów

| Typ | Pole `type` | Kiedy używać |
|:---|:---|:---|
| Command | `"command"` | skrypt powłoki; wejście przez stdin, wyjście przez exit code + stdout |
| HTTP | `"http"` | lokalny lub zdalny endpoint; wejście przez POST body, wyjście przez response body |
| MCP tool | `"mcp_tool"` | wywołanie narzędzia już podłączonego serwera MCP |
| Prompt | `"prompt"` | jednoturowa ocena przez model Claude; zwraca decyzję tak/nie |
| Agent | `"agent"` | subagent z dostępem do narzędzi (Read, Grep, Glob); eksperymentalny |

### Pola wspólne dla wszystkich handlerów

| Pole | Wymagane | Opis |
|:---|:---|:---|
| `type` | tak | `"command"`, `"http"`, `"mcp_tool"`, `"prompt"` lub `"agent"` |
| `if` | nie | reguła uprawnień jako dodatkowy filtr; tylko eventy narzędziowe |
| `timeout` | nie | sekundy do anulowania (domyślnie 600 dla command/http/mcp_tool; 30 dla prompt; 60 dla agent) |
| `statusMessage` | nie | własny tekst spinnera wyświetlany podczas działania hooka |
| `once` | nie | jeśli `true`, odpala raz na sesję (tylko frontmatter skilla; ignorowane w settings) |

### Pola handlera `command`

| Pole | Wymagane | Opis |
|:---|:---|:---|
| `command` | tak | polecenie powłoki lub ścieżka do pliku wykonywalnego (exec form gdy `args` ustawione) |
| `args` | nie | lista argumentów; gdy obecna, `command` jest plikiem wykonywalnym (exec form — bez powłoki) |
| `async` | nie | jeśli `true`, działa w tle bez blokowania |
| `asyncRewake` | nie | działa w tle i budzi Claude przy exit code 2 (implikuje `async`) |
| `shell` | nie | `"bash"` (domyślnie) lub `"powershell"`; patrz sekcja Windows niżej |

**Exec form vs shell form:** gdy `args` jest obecne, `command` jest bezpośrednio wykonywanym plikiem
(brak powłoki, brak tokenizacji). Gdy `args` brak, `command` jest przekazywany do powłoki (`sh -c` na
macOS/Linux, Git Bash na Windows, lub PowerShell gdy Git Bash niedostępny). W exec form używaj
`${CLAUDE_PROJECT_DIR}` — podstawienie ścieżek działa bez cudzysłowów.

> **Windows uwaga:** Exec form wymaga prawdziwego pliku `.exe`. Skrypty `.cmd` i `.bat` (npm, npx,
> eslint) nie działają w exec form — użyj `node` bezpośrednio lub shell form.

### Pola handlera `http`

| Pole | Wymagane | Opis |
|:---|:---|:---|
| `url` | tak | URL do wysłania żądania POST |
| `headers` | nie | dodatkowe nagłówki jako pary klucz-wartość; wspierają `$VAR_NAME` |
| `allowedEnvVars` | nie | lista nazw zmiennych środowiskowych dozwolonych w `headers` |

### Pola handlera `mcp_tool`

| Pole | Wymagane | Opis |
|:---|:---|:---|
| `server` | tak | nazwa skonfigurowanego serwera MCP (musi być już podłączony) |
| `tool` | tak | nazwa narzędzia na tym serwerze |
| `input` | nie | argumenty narzędzia; stringi wspierają `${ścieżka}` z JSON input |

### Placeholdery ścieżek

- `${CLAUDE_PROJECT_DIR}` — katalog główny projektu
- `${CLAUDE_PLUGIN_ROOT}` — katalog instalacji pluginu
- `${CLAUDE_PLUGIN_DATA}` — persistentny katalog danych pluginu

### Hooki w frontmatterze skilli i agentów

Hooki można definiować bezpośrednio w frontmatterze skilla lub agenta YAML — są aktywne przez cały
czas życia komponentu:

```yaml
---
name: secure-operations
description: Perform operations with security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

---

## Wejście JSON (stdin)

Command hooki otrzymują dane przez stdin jako JSON. HTTP hooki — jako ciało żądania POST.

### Pola wspólne (wszystkie eventy)

| Pole | Opis |
|:---|:---|
| `session_id` | identyfikator bieżącej sesji |
| `transcript_path` | ścieżka do pliku JSONL z konwersacją |
| `cwd` | bieżący katalog roboczy w momencie odpałania hooka |
| `permission_mode` | aktualny tryb uprawnień: `"default"`, `"plan"`, `"acceptEdits"`, `"auto"`, `"dontAsk"`, `"bypassPermissions"` |
| `effort` | obiekt z polem `level`: `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"` |
| `hook_event_name` | nazwa eventu który odpalił hook |
| `agent_id` | unikalny identyfikator subagenta (tylko wewnątrz subagenta) |
| `agent_type` | nazwa typu agenta (tylko wewnątrz subagenta) |

Przykład dla `PreToolUse` (Bash):

```json
{
  "session_id": "abc123",
  "transcript_path": "/home/user/.claude/projects/.../transcript.jsonl",
  "cwd": "/home/user/my-project",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse",
  "tool_name": "Bash",
  "tool_input": {
    "command": "npm test"
  }
}
```

---

## Wyjście i exit codes

### Exit codes

| Exit code | Znaczenie |
|:---|:---|
| `0` | sukces; Claude Code parsuje stdout w poszukiwaniu pól JSON |
| `2` | błąd blokujący; stdout i JSON są ignorowane; tekst z stderr trafia do Claude jako wiadomość o błędzie |
| inne (1, 3…) | nieblokujący błąd; wykonanie kontynuuje; pierwsza linia stderr pokazywana w transkrypcie |

> **Ważne:** exit code `1` to **nieblokujący** błąd — Claude Code kontynuuje mimo konwencji
> Uniksowej. Aby wymusić blokadę, używaj **zawsze `exit 2`**.
> Wyjątek: `WorktreeCreate` — każdy niezerowy exit code przerywa tworzenie worktree.

### Exit code 2 — efekt per event

| Event | Blokuje? | Co się dzieje przy exit 2 |
|:---|:---|:---|
| `PreToolUse` | tak | blokuje wywołanie narzędzia |
| `PermissionRequest` | tak | odmawia pozwolenia |
| `UserPromptSubmit` | tak | blokuje przetwarzanie promptu i usuwa go |
| `UserPromptExpansion` | tak | blokuje rozwinięcie komendy |
| `Stop` | tak | zapobiega zatrzymaniu Claude, kontynuuje rozmowę |
| `SubagentStop` | tak | zapobiega zatrzymaniu subagenta |
| `TeammateIdle` | tak | zapobiega przejściu w stan idle (teammate kontynuuje) |
| `TaskCreated` | tak | cofa tworzenie zadania |
| `TaskCompleted` | tak | zapobiega oznaczeniu zadania jako zakończone |
| `ConfigChange` | tak | blokuje zastosowanie zmian konfiguracji (poza `policy_settings`) |
| `PreCompact` | tak | blokuje kompakcję |
| `PostToolBatch` | tak | zatrzymuje pętlę agenta przed kolejnym wywołaniem modelu |
| `Elicitation` | tak | odmawia elicitation |
| `ElicitationResult` | tak | blokuje odpowiedź (akcja staje się `decline`) |
| `WorktreeCreate` | tak | każdy niezerowy exit code przerywa tworzenie |
| `PostToolUse` | nie | pokazuje stderr Claude (narzędzie już się wykonało) |
| `PostToolUseFailure` | nie | pokazuje stderr Claude |
| `Notification` | nie | pokazuje stderr tylko użytkownikowi |
| `SubagentStart` | nie | pokazuje stderr tylko użytkownikowi |
| `SessionStart` | nie | pokazuje stderr tylko użytkownikowi |
| `SessionEnd` | nie | pokazuje stderr tylko użytkownikowi |
| `StopFailure` | nie | exit code i stdout są ignorowane |
| `PermissionDenied` | nie | exit code ignorowany; użyj `hookSpecificOutput.retry: true` w JSON |

### Wyjście JSON (exit 0 + stdout)

Zamiast lub oprócz exit code, hook może zwrócić JSON przez stdout. Claude Code odczytuje z niego
pola sterujące. Wymagane: exit 0, stdout musi zawierać **tylko** obiekt JSON.

**Zasada:** albo exit codes (sam sygnał), albo exit 0 + JSON (szczegółowe sterowanie) — nie obie
metody jednocześnie.

Trzy rodzaje pól:

- **Pola uniwersalne** — działają we wszystkich eventach
- **Top-level `decision` i `reason`** — używane przez większość eventów do blokowania
- **`hookSpecificOutput`** — zagnieżdżony obiekt dla eventów wymagających bogatszego sterowania;
  wymaga pola `hookEventName` ustawionego na nazwę eventu

#### Pola universalne

| Pole | Domyślnie | Opis |
|:---|:---|:---|
| `continue` | `true` | `false` → Claude całkowicie przestaje przetwarzać po tym hooku |
| `stopReason` | brak | wiadomość dla użytkownika gdy `continue` jest `false` |
| `suppressOutput` | `false` | `true` → stdout hooka ukryty z transkryptu (widoczny w debug logu) |
| `systemMessage` | brak | ostrzeżenie wyświetlane użytkownikowi |
| `terminalSequence` | brak | sekwencja escape terminala do emisji (OSC 0/1/2/9/99/777, BEL); zastępuje zapis do `/dev/tty` |

Aby zatrzymać Claude całkowicie niezależnie od eventu:

```json
{ "continue": false, "stopReason": "Build failed, fix errors before continuing" }
```

#### Wzorce sterowania decyzjami (per event)

| Eventy | Wzorzec | Kluczowe pola |
|:---|:---|:---|
| `UserPromptSubmit`, `UserPromptExpansion`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`, `Stop`, `SubagentStop`, `ConfigChange`, `PreCompact` | top-level `decision` | `decision: "block"`, `reason` |
| `TeammateIdle`, `TaskCreated`, `TaskCompleted` | exit code lub `continue: false` | exit 2 = blokada z feedbackiem; `{"continue": false, "stopReason": "..."}` = stop całkowity |
| `PreToolUse` | `hookSpecificOutput` | `permissionDecision` (allow/deny/ask/defer), `permissionDecisionReason` |
| `PermissionRequest` | `hookSpecificOutput` | `decision.behavior` (allow/deny) |
| `PermissionDenied` | `hookSpecificOutput` | `retry: true` → model może ponowić |
| `MessageDisplay` | `hookSpecificOutput` | `displayContent` zastępuje tekst na ekranie (nie w transkrypcie) |
| `WorktreeCreate` | ścieżka na stdout | hook drukuje absolutną ścieżkę nowego worktree |
| `Elicitation` | `hookSpecificOutput` | `action` (accept/decline/cancel), `content` |
| `ElicitationResult` | `hookSpecificOutput` | `action`, `content` (nadpisanie) |
| `SessionStart`, `Setup`, `SubagentStart` | tylko kontekst | `additionalContext` dodaje kontekst; brak blokowania |
| `WorktreeRemove`, `Notification`, `SessionEnd`, `PostCompact`, `InstructionsLoaded`, `StopFailure`, `CwdChanged`, `FileChanged` | brak | tylko side effects (logowanie, cleanup) |

#### `additionalContext` — wstrzykiwanie kontekstu

Pole `additionalContext` wewnątrz `hookSpecificOutput` przekazuje string do okna kontekstu Claude.
Claude Code owija go system reminderem i wstawia do rozmowy w momencie odpałania hooka:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": "This file is generated. Edit src/schema.ts and run `bun generate` instead."
  }
}
```

Miejsce wstawienia zależy od eventu:
- `SessionStart`, `Setup`, `SubagentStart` → na początku rozmowy, przed pierwszym promptem
- `UserPromptSubmit`, `UserPromptExpansion` → obok przesłanego promptu
- `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch` → obok wyniku narzędzia
- `Stop`, `SubagentStop` → na końcu tury; rozmowa kontynuuje

---

## Pełna lista eventów

### Cykl życia sesji

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `SessionStart` | przy starcie nowej sesji lub wznowieniu (resume/clear/compact) | nie |
| `Setup` | tylko przy `--init-only` lub `--init`/`--maintenance` w trybie `-p` | nie |
| `SessionEnd` | gdy sesja się kończy | nie |

#### `SessionStart`

Przydatny do ładowania kontekstu deweloperskiego: aktywna gałąź, otwarte issue, niezatwierdzone
zmiany. Dla statycznego kontekstu który nie wymaga skryptu — użyj `CLAUDE.md`.

Matcher: `startup` (nowa sesja), `resume` (--resume/--continue//resume), `clear` (/clear),
`compact` (kompakcja).

Obsługuje tylko `type: "command"` i `type: "mcp_tool"`.

Dodatkowe pola wyjścia (`hookSpecificOutput`):
- `additionalContext` — string dodany do kontekstu Claude przed pierwszym promptem
- `initialUserMessage` — string jako pierwsza wiadomość użytkownika (tryb non-interactive)
- `sessionTitle` — ustawia tytuł sesji (jak `/rename`)
- `watchPaths` — tablica ścieżek do śledzenia przez `FileChanged`
- `reloadSkills` — boolean; jeśli `true`, Claude Code ponownie skanuje katalogi skilli po zakończeniu hooków SessionStart

Hooki `SessionStart` mają dostęp do `CLAUDE_ENV_FILE` — zmienne środowiskowe zapisane do tego pliku
będą dostępne we wszystkich kolejnych poleceniach Bash w sesji.

```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Current branch: feat/auth-refactor\nUncommitted: src/auth.ts\nActive issue: #4211",
    "sessionTitle": "auth-refactor"
  }
}
```

#### `SessionEnd`

Uruchamia się gdy sesja kończy się. Przydatny do cleanup, logowania statystyk. Brak sterowania
decyzjami. Domyślny timeout: 1.5 sekundy (nadpisywalny przez `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS`).

Dodatkowe pole wejścia: `reason` (`clear`, `resume`, `logout`, `prompt_input_exit`, `bypass_permissions_disabled`, `other`).

---

### Eventy na każdą turę

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `UserPromptSubmit` | gdy użytkownik wysyła prompt, przed przetworzeniem przez Claude | tak |
| `UserPromptExpansion` | gdy komenda slash rozija się w prompt | tak |
| `Stop` | gdy główny agent kończy odpowiedź | tak |
| `StopFailure` | gdy tura kończy się błędem API | nie |

#### `UserPromptSubmit`

Umożliwia walidację promptu, dodanie kontekstu lub blokadę. Domyślny timeout: **30 sekund** (krótszy
niż inne eventy — blokuje przetwarzanie przed każdym promptem).

Dodatkowe pole wejścia: `prompt` (tekst który wysłał użytkownik).

Blokowanie:
```json
{
  "decision": "block",
  "reason": "Explanation for decision",
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "My additional context here",
    "sessionTitle": "My session title"
  }
}
```

#### `Stop`

Odpala gdy główny agent Claude kończy odpowiedź. Przydatny do wymuszenia dodatkowych kroków przed
zatrzymaniem (testy, lint, walidacja). Pole `stop_hook_active` to `true` gdy Claude już kontynuuje
w wyniku hooka Stop — sprawdź by uniknąć nieskończonej pętli. Po 8 kolejnych blokadach Claude Code
nadpisuje hook i kończy turę.

Dodatkowe pola wejścia: `stop_hook_active`, `last_assistant_message`, `background_tasks`, `session_crons`.

Sterowanie:
```json
{
  "decision": "block",
  "reason": "Must be provided when Claude is blocked from stopping"
}
```

Lub łagodniejszy feedback (nie powoduje ikony błędu w transkrypcie):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "Stop",
    "additionalContext": "Please run the test suite before finishing"
  }
}
```

---

### Eventy w pętli agenta (narzędzia)

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `PreToolUse` | po tym jak Claude tworzy parametry narzędzia, przed wykonaniem | tak |
| `PermissionRequest` | gdy pojawia się dialog uprawnień | tak |
| `PermissionDenied` | gdy auto mode odrzuca wywołanie narzędzia | nie (retry) |
| `PostToolUse` | po pomyślnym zakończeniu wywołania narzędzia | nie (feedback) |
| `PostToolUseFailure` | po nieudanym wywołaniu narzędzia | nie (feedback) |
| `PostToolBatch` | po rozwiązaniu całej paczki równoległych wywołań | tak |

#### `PreToolUse`

Matcher: nazwa narzędzia (`Bash`, `Edit`, `Write`, `Read`, `Glob`, `Grep`, `Agent`, `WebFetch`,
`WebSearch`, `AskUserQuestion`, `ExitPlanMode`, nazwy narzędzi MCP).

Pola wejścia: `tool_name`, `tool_input` (pola zależne od narzędzia), `tool_use_id`.

Sterowanie przez `hookSpecificOutput` (bogatsza kontrola niż inne eventy):

| Pole | Opis |
|:---|:---|
| `permissionDecision` | `"allow"` (pomiń dialog uprawnień), `"deny"` (zablokuj), `"ask"` (pytaj użytkownika), `"defer"` (odłóż do wznowienia — tylko `-p`) |
| `permissionDecisionReason` | powód: przy `"allow"`/`"ask"` widoczny dla użytkownika; przy `"deny"` widoczny dla Claude |
| `updatedInput` | modyfikuje parametry narzędzia przed wykonaniem (zastępuje cały obiekt wejścia) |
| `additionalContext` | string dodany do kontekstu Claude obok wyniku narzędzia |

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Database writes are not allowed in production"
  }
}
```

Przy wielu hookach PreToolUse zwracających różne decyzje — precedencja: `deny` > `defer` > `ask` > `allow`.

#### `PostToolUse`

Matcher: nazwa narzędzia (te same wartości co `PreToolUse`).

Pola wejścia: `tool_name`, `tool_input`, `tool_response`, `tool_use_id`, opcjonalnie `duration_ms`.

Dodatkowe pola wyjścia (`hookSpecificOutput`):

| Pole | Opis |
|:---|:---|
| `decision` | `"block"` → dodaje `reason` obok wyniku narzędzia (narzędzie już się wykonało) |
| `reason` | wyjaśnienie dla Claude przy `decision: "block"` |
| `additionalContext` | string dodany do kontekstu Claude obok wyniku narzędzia |
| `updatedToolOutput` | zastępuje wynik narzędzia przed przesłaniem do Claude (musi pasować do kształtu wyniku) |

---

### Eventy subagentów

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `SubagentStart` | gdy spawanowany jest subagent przez narzędzie Agent | nie (tylko kontekst) |
| `SubagentStop` | gdy subagent kończy działanie | tak |
| `TaskCreated` | gdy zadanie jest tworzone przez TaskCreate | tak |
| `TaskCompleted` | gdy zadanie jest oznaczane jako ukończone | tak |
| `TeammateIdle` | gdy teammate agent teams przechodzi w stan idle | tak |

#### `SubagentStart`

Matcher: typ agenta (`general-purpose`, `Explore`, `Plan`, lub własna nazwa z frontmattera).

Nie może blokować tworzenia subagenta, ale może wstrzyknąć kontekst przez `additionalContext`
w `hookSpecificOutput`.

#### `SubagentStop`

Matcher: typ agenta (te same wartości co `SubagentStart`).

Dodatkowe pola wejścia: `stop_hook_active`, `agent_id`, `agent_type`, `agent_transcript_path`,
`last_assistant_message`, `background_tasks`, `session_crons`.

Używa tego samego formatu sterowania co `Stop` (patrz wyżej).

---

### Eventy kompakcji i zarządzania kontekstem

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `PreCompact` | przed kompakcją kontekstu | tak |
| `PostCompact` | po kompakcji | nie |

Matcher dla obu: `manual` (ręczna `/compact`) lub `auto` (automatyczna przy pełnym oknie).

---

### Eventy środowiska i plików

| Event | Kiedy odpala | Blokowanie? | Dostęp do `CLAUDE_ENV_FILE` |
|:---|:---|:---|:---|
| `CwdChanged` | gdy zmienia się katalog roboczy (np. `cd`) | nie | tak |
| `FileChanged` | gdy śledzony plik zmienia się na dysku | nie | tak |
| `ConfigChange` | gdy zmienia się plik konfiguracji w trakcie sesji | tak (poza `policy_settings`) | nie |
| `InstructionsLoaded` | gdy ładowany jest plik CLAUDE.md lub `.claude/rules/*.md` | nie | nie |

#### `FileChanged`

Matcher pełni dwie role:
1. **Buduje listę plików do śledzenia** — wartość jest dzielona na `|` i każdy segment jest dosłowną
   nazwą pliku w bieżącym katalogu (`.envrc|.env` śledzi dokładnie te dwa pliki).
2. **Filtruje które hooki uruchamiają się** — gdy śledzony plik się zmieni.

Dodatkowe pola wejścia: `file_path` (ścieżka do zmienionego pliku), `event` (`"change"`, `"add"`, `"unlink"`).

---

### Eventy worktree

| Event | Kiedy odpala | Zachowanie |
|:---|:---|:---|
| `WorktreeCreate` | gdy tworzony jest worktree (`--worktree` lub `isolation: "worktree"`) | zastępuje domyślne zachowanie git |
| `WorktreeRemove` | gdy worktree jest usuwany | tylko cleanup |

`WorktreeCreate` wymaga zwrócenia absolutnej ścieżki do nowego katalogu (command hook: drukuje na stdout;
HTTP hook: zwraca `hookSpecificOutput.worktreePath`).

---

### Eventy powiadomień i wyświetlania

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `Notification` | gdy Claude Code wysyła powiadomienie | nie |
| `MessageDisplay` | gdy tekst odpowiedzi asystenta jest wyświetlany (strumieniowanie) | nie (tylko display) |

#### `Notification`

Matcher: typ powiadomienia (`permission_prompt`, `idle_prompt`, `auth_success`,
`elicitation_dialog`, `elicitation_complete`, `elicitation_response`).

Dodatkowe pola wejścia: `message`, opcjonalnie `title`, `notification_type`.

Przydatny do przekazywania powiadomień do zewnętrznych serwisów lub wyświetlania alert systemu.

#### `MessageDisplay`

Odpala na każdą paczkę linii podczas strumieniowania. Zwróć `displayContent` w `hookSpecificOutput`
by zastąpić wyświetlany tekst. **Tylko wyświetlanie** — transkrypt i to co widzi Claude pozostają bez zmian.
Domyślny timeout: 10 sekund.

---

### Eventy MCP elicitation

| Event | Kiedy odpala | Blokowanie? |
|:---|:---|:---|
| `Elicitation` | gdy serwer MCP prosi o dane od użytkownika | tak (przechwycenie) |
| `ElicitationResult` | po odpowiedzi użytkownika, przed wysłaniem do serwera | tak |

Matcher: nazwa serwera MCP.

---

## Hooki na Windows / PowerShell

To środowisko (Windows 11, PowerShell) wymaga specjalnej uwagi:

### Metoda 1: `shell: "powershell"` (najprostsze)

Ustaw `"shell": "powershell"` na handlerze command — Claude Code wykrywa `pwsh.exe` (PowerShell 7+)
z fallbackiem do `powershell.exe` (5.1). Działa niezależnie od `CLAUDE_CODE_USE_POWERSHELL_TOOL`.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "shell": "powershell",
            "command": "Write-Host 'File written'"
          }
        ]
      }
    ]
  }
}
```

### Metoda 2: Exec form z `powershell.exe` i `-File`

Dla bardziej złożonych skryptów (.ps1) — użyj exec form z `-NoProfile -ExecutionPolicy Bypass`:

```json
{
  "hooks": {
    "MessageDisplay": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/plain-display.ps1"
            ]
          }
        ]
      }
    ]
  }
}
```

Flaga `-NoProfile` pomija ładowanie profilu PowerShell (szybszy start), `-ExecutionPolicy Bypass`
pozwala uruchomić lokalny plik skryptu.

### Przykładowy skrypt `.ps1` — odczyt stdin i zwrot JSON

```powershell
$batch = [Console]::In.ReadToEnd() | ConvertFrom-Json
$text = $batch.delta -replace '\*\*', '' -replace '`', ''
@{
  hookSpecificOutput = @{
    hookEventName = "MessageDisplay"
    displayContent = $text
  }
} | ConvertTo-Json
```

### Uwagi specyficzne dla Windows

- W exec form `command` musi być prawdziwym plikiem `.exe` — skrypty `.cmd` i `.bat` nie działają
  bez powłoki. Aby uruchomić narzędzie npm/npx, wskaż `node` bezpośrednio:
  ```json
  { "command": "node", "args": ["${CLAUDE_PROJECT_DIR}/node_modules/eslint/bin/eslint.js"] }
  ```
- Brak `/dev/tty` na Windows — używaj `terminalSequence` w JSON output do powiadomień terminala.
- `CLAUDE_ENV_FILE` działa tak samo jak na Uniksie — dołączaj zmienne przez `>>`, nie `>`.

---

## Dwa pełne przykłady

### Przykład 1 — `PreToolUse`: blokowanie niebezpiecznych poleceń Bash (exit 2)

Skrypt `.claude/hooks/block-rm.sh` (Linux/macOS):

```bash
#!/bin/bash

command=$(jq -r '.tool_input.command' < /dev/stdin)

if [[ "$command" == *"rm -rf"* ]]; then
  echo "Blocked: rm -rf commands are not allowed" >&2
  exit 2
fi

exit 0
```

Konfiguracja w `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "if": "Bash(rm *)",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.sh",
            "args": []
          }
        ]
      }
    ]
  }
}
```

Pole `if` zawęża do Bash subpoleceń pasujących do `rm *`, więc skrypt odpala się tylko gdy oba
filtry pasują (matcher Bash + `if` rm).

Wersja PowerShell (`.claude/hooks/block-rm.ps1`):

```powershell
$input_data = [Console]::In.ReadToEnd() | ConvertFrom-Json
$command = $input_data.tool_input.command

if ($command -match 'rm\s+-rf') {
  Write-Error "Blocked: rm -rf commands are not allowed"
  exit 2
}

exit 0
```

Konfiguracja (Windows):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-rm.ps1"
            ]
          }
        ]
      }
    ]
  }
}
```

### Przykład 2 — `SessionStart`: wstrzyknięcie kontekstu git przy starcie sesji

Skrypt `.claude/hooks/session-context.sh` (Linux/macOS):

```bash
#!/bin/bash

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
CHANGES=$(git status --short 2>/dev/null | wc -l | tr -d ' ')
LAST_COMMIT=$(git log -1 --oneline 2>/dev/null || echo "none")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "Branch: $BRANCH\nUncommitted changes: $CHANGES files\nLast commit: $LAST_COMMIT",
    "sessionTitle": "$BRANCH"
  }
}
EOF
```

Wersja PowerShell (`.claude/hooks/session-context.ps1`):

```powershell
$branch = (git rev-parse --abbrev-ref HEAD 2>$null) ?? "unknown"
$changes = (git status --short 2>$null | Measure-Object -Line).Lines
$lastCommit = (git log -1 --oneline 2>$null) ?? "none"

@{
  hookSpecificOutput = @{
    hookEventName    = "SessionStart"
    additionalContext = "Branch: $branch`nUncommitted changes: $changes files`nLast commit: $lastCommit"
    sessionTitle     = $branch
  }
} | ConvertTo-Json -Depth 5
```

Konfiguracja (Windows, tylko przy `startup`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "powershell.exe",
            "args": [
              "-NoProfile",
              "-ExecutionPolicy",
              "Bypass",
              "-File",
              "${CLAUDE_PROJECT_DIR}/.claude/hooks/session-context.ps1"
            ]
          }
        ]
      }
    ]
  }
}
```

---

## Hooki w tym projekcie (SENSUM pipeline)

Pipeline SENSUM realnie korzysta z hooków w następujący sposób:

**`SessionStart`** — pluginy `superpowers` i `context-mode` rejestrują swoje hooki SessionStart,
które wstrzykują kontekst i ładują instrukcje do rozmowy na początku każdej sesji.

**`PreToolUse` (WebFetch)** — plugin `context-mode` przechwytuje wywołania `WebFetch`, zamiast
wykonywać je bezpośrednio przekierowuje przez `ctx_fetch_and_index`, by surowe bajty stron nigdy nie
wchodziły do kontekstu konwersacji (kontekst-mode sandbox).

**`PreToolUse` (Read/Bash)** — context-mode może sterować dostępem do narzędzi Read i Bash na podstawie
reguł konfiguracji pluginu.

---

## Gotchas i częste pułapki

- **exit 1 ≠ blokada.** Konwencja Uniksowa mówi exit 1 = błąd — ale Claude Code traktuje go jako
  *nieblokujący*. Do blokowania zawsze `exit 2`.

- **JSON tylko przy exit 0.** Jeśli hook wyjdzie z exit 2, cały JSON na stdout jest ignorowany —
  do Claude trafia tylko stderr.

- **Stdout musi zawierać tylko JSON.** Jeśli profil powłoki wypisuje cokolwiek przy starcie (banner,
  `nvm use`, itp.), JSON parsing się posypie. Użyj `/hooks`, żeby to sprawdzić, lub `--debug`.

- **Brak `/dev/tty` w hookach.** Od Claude Code v2.1.139 hooki działają bez kontrolnego terminala
  (na Windows nigdy go nie było). Do powiadomień używaj `terminalSequence` w JSON output.

- **`stop_hook_active` w hookach Stop.** Sprawdzaj to pole zanim zablokujesz — bez tego hook Stop
  może kręcić się w nieskończoność. Claude Code przerwie po 8 kolejnych blokadach.

- **`SessionStart` odpala też przy resume/compact.** Matcher `startup` odpala tylko przy nowej
  sesji — użyj go gdy chcesz uniknąć podwójnego ładowania kontekstu.

- **`SessionEnd` ma domyślny timeout 1.5 sekundy.** Dla dłuższych operacji cleanup ustaw
  `CLAUDE_CODE_SESSIONEND_HOOKS_TIMEOUT_MS` lub `timeout` w konfiguracji hooka.

- **MCP tool hooki a `SessionStart`.** Serwery MCP podłączają się po odpaleniu hooków SessionStart
  — hooki `mcp_tool` na tym evencie dostają błąd "not connected" przy pierwszym uruchomieniu.

- **Na Windows — ścieżki z exec form.** Przy exec form i `${CLAUDE_PROJECT_DIR}` ścieżki ze spacjami
  przechodzą bez cudzysłowów (każdy element `args` to jeden argument verbatim). W shell form każdy
  placeholder owijaj podwójnymi cudzysłowami.

- **`policy_settings` nie do zablokowania.** Nawet przy `ConfigChange` z exit 2 — zmiany managed
  settings zawsze wchodzą w życie.

---

## Debugowanie hooków

Szczegóły wykonania (które hooki pasowały, exit codes, pełny stdout i stderr) trafiają do debug loga:

```text
[DEBUG] Executing hooks for PostToolUse:Write
[DEBUG] Found 1 hook commands to execute
[DEBUG] Executing hook command: <Your command> with timeout 600000ms
[DEBUG] Hook command completed with status 0: <Your stdout>
```

Uruchom Claude Code z flagą:

```
claude --debug-file C:\Users\<user>\claude-hooks-debug.txt
```

lub `claude --debug` (logi w `~/.claude/debug/<session-id>.txt`).

Dla bardziej szczegółowych logów matchowania:

```
CLAUDE_CODE_DEBUG_LOG_LEVEL=verbose claude
```

---

## Źródła

- Przewodnik: https://code.claude.com/docs/en/hooks-guide.md
- Pełna referencja: https://code.claude.com/docs/en/hooks.md
- Pobrano: 2026-06-09
