# Settings, Permissions i Environment Variables w Claude Code

> Referencja operacyjna. Źródła: https://code.claude.com/docs/en/settings.md,
> https://code.claude.com/docs/en/permissions.md, https://code.claude.com/docs/en/env-vars.md
> (pobrane 2026-06-09). Klucze settings, nazwy zmiennych, reguły permissions i bloki JSON
> zostawione **verbatim** po angielsku — to kontrakt z harnessem, nie tłumacz ich.
> Proza wyjaśniająca po polsku.

---

## Czym są pliki ustawień i czemu są trzy rodzaje

Claude Code używa **plików JSON** (`settings.json`) do konfiguracji narzędzi, uprawnień, zmiennych
środowiskowych i zachowania sesji. To nie to samo co `CLAUDE.md` — tamten plik to pamięć/instrukcje
dla modelu, ten to konfiguracja harnessu. Claude Code auto-odświeża ustawienia w trakcie sesji (bez
restartu), z wyjątkiem `model` i `outputStyle`, które wczytywane są raz na start.

Ustawienia mogą też trafiać do `settings.json` pod kluczem `env` — wtedy zmienne env obowiązują
zawsze, niezależnie od tego, jak uruchomiono `claude`.

---

## Hierarchia plików i precedencja

Od **najwyższego** do **najniższego** priorytetu:

| Poziom | Plik / źródło | Kto może edytować | Git |
|---|---|---|---|
| 1. Managed (enterprise) | `managed-settings.json` (MDM / rejestr / server-managed) | Administrator IT | nie dot. |
| 2. CLI flags | `--settings <plik>` / `--permission-mode` itp. | użytkownik | nie dot. |
| 3. Local project | `.claude/settings.local.json` | użytkownik (ten komputer) | **gitignored** |
| 4. Shared project | `.claude/settings.json` | cały zespół | **commitować** |
| 5. User global | `~/.claude/settings.json` | użytkownik (wszystkie projekty) | nie dot. |

**Reguła scalania:** wartości skalarne z wyższego poziomu nadpisują niższy; **tablice są konkatenowane
i deduplikowane** — niższy poziom może dodawać wpisy, ale nie usuwać tych z wyższego.

**Managed settings** nie mogą być nadpisane niczym, włącznie z `--allowedTools`.

### Lokalizacje pliku managed-settings.json

| System | Ścieżka |
|---|---|
| macOS | `/Library/Application Support/ClaudeCode/managed-settings.json` |
| Linux / WSL | `/etc/claude-code/managed-settings.json` |
| Windows | `C:\Program Files\ClaudeCode\managed-settings.json` |

Dropiny: pliki `managed-settings.d/*.json` są scalane z `managed-settings.json` (konwencja systemd).

### Co commitować

- `.claude/settings.json` — **TAK**, to konfiguracja zespołu (permissions, model, hooki)
- `.claude/settings.local.json` — **NIE** (gitignored, ustawienia osobiste)
- `.env` — **NIGDY** (sekrety; Claude Code czyta go automatycznie przy starcie)

---

## Weryfikacja aktywnych ustawień

Wpisz `/status` w sesji Claude Code → zakładka **Setting sources** pokazuje, które warstwy zostały
załadowane i przez jaki mechanizm (np. `Enterprise managed settings (remote)`, `(plist)`, `(HKLM)`,
`(file)`). Zakładka **Config** to edytor wybranych togglei (motyw, verbose itp.) — nie wyświetla
zawartości `settings.json`.

---

## Pełna tabela kluczy settings.json

Klucze podzielone tematycznie. Kolumna „Managed only" = działa tylko w `managed-settings.json`.

### Model i sesja

| Klucz | Opis | Przykład |
|---|---|---|
| `model` | Domyślny model (nadpisuje `--model` i `ANTHROPIC_MODEL` na sesję) | `"claude-sonnet-4-6"` |
| `availableModels` | Ogranicz modele dostępne przez `/model` / `--model` / `ANTHROPIC_MODEL` | `["sonnet", "haiku"]` |
| `modelOverrides` | Mapuj Anthropic model ID → provider-specific ARN/ID (Bedrock itp.) | `{"claude-opus-4-6": "arn:…"}` |
| `effortLevel` | Utrwal poziom wysiłku między sesjami (`low`/`medium`/`high`/`xhigh`) | `"xhigh"` |
| `alwaysThinkingEnabled` | Domyślnie włącz extended thinking | `true` |
| `showThinkingSummaries` | Pokaż bloki thinking w sesjach interaktywnych | `true` |
| `cleanupPeriodDays` | Pliki sesji starsze niż N dni usuwane przy starcie (min. 1, domyślnie 30) | `20` |
| `viewMode` | Domyślny tryb widoku: `"default"`, `"verbose"`, `"focus"` | `"verbose"` |
| `autoUpdatesChannel` | Kanał aktualizacji: `"latest"` (domyślnie) lub `"stable"` | `"stable"` |
| `minimumVersion` | Dolna granica wersji (nie blokuje startu, uniemożliwia downgrade) | `"2.1.100"` |
| `language` | Preferowany język odpowiedzi Claude (np. `"japanese"`, `"spanish"`) | `"polish"` |

### Uprawnienia i bezpieczeństwo

| Klucz | Opis | Przykład |
|---|---|---|
| `permissions` | Obiekt z polami `allow`, `deny`, `ask`, `additionalDirectories`, `defaultMode` — patrz sekcja Permissions | |
| `autoMode` | Konfiguruj tryb auto (`environment`, `allow`, `soft_deny`, `hard_deny`); `"$defaults"` dziedziczy wbudowane reguły | `{"soft_deny": ["Never run terraform apply"]}` |
| `disableAutoMode` | `"disable"` — usuwa `auto` z cyklu Shift+Tab | `"disable"` |

### Środowisko i zmienne

| Klucz | Opis | Przykład |
|---|---|---|
| `env` | Zmienne środowiskowe przekazywane do każdej sesji i subprocesów | `{"FOO": "bar", "PYTHONIOENCODING": "utf-8"}` |
| `defaultShell` | Domyślna powłoka dla poleceń `!`: `"bash"` lub `"powershell"` | `"powershell"` |

### Agent i subagenci

| Klucz | Opis | Przykład |
|---|---|---|
| `agent` | Uruchom główny wątek jako nazwany subagent (system prompt + narzędzia z definicji agenta) | `"code-reviewer"` |
| `teammateMode` | Tryb wyświetlania agent team: `auto`, `in-process`, `tmux` | `"in-process"` |

### Hooki i statusline

| Klucz | Opis | Przykład |
|---|---|---|
| `hooks` | Konfiguracja hooków lifecycle — patrz osobna referencja hooków | |
| `disableAllHooks` | Wyłącz wszystkie hooki i custom status line | `true` |
| `statusLine` | Konfiguracja custom status line | `{"type": "command", "command": "~/.claude/statusline.sh"}` |
| `allowedHttpHookUrls` | Allowlist URL dla HTTP hooków (obsługuje `*`) | `["https://hooks.example.com/*"]` |
| `httpHookAllowedEnvVars` | Allowlist nazw zmiennych env, które HTTP hooki mogą interpolować w nagłówkach | `["MY_TOKEN"]` |
| `allowManagedHooksOnly` | *(Managed only)* Załaduj tylko hooki z managed settings i SDK | `true` |

### MCP serwery

| Klucz | Opis | Przykład |
|---|---|---|
| `enableAllProjectMcpServers` | Auto-approve wszystkie serwery z `.mcp.json` | `true` |
| `enabledMcpjsonServers` | Lista serwerów z `.mcp.json` do zatwierdzenia | `["memory", "github"]` |
| `disabledMcpjsonServers` | Lista serwerów z `.mcp.json` do odrzucenia | `["filesystem"]` |
| `allowedMcpServers` | *(Managed only)* Allowlist MCP serwerów dla użytkowników | `[{"serverName": "github"}]` |
| `deniedMcpServers` | *(Managed only)* Denylist MCP serwerów (przeważa nad allowlist) | `[{"serverName": "filesystem"}]` |
| `allowManagedMcpServersOnly` | *(Managed only)* Tylko serwery z managed settings są respektowane | `true` |

### Atrybucja w git

| Klucz | Opis | Przykład |
|---|---|---|
| `attribution` | Konfiguracja podpisu w commitach i PR | `{"commit": "Co-Authored-By: AI", "pr": ""}` |
| `includeCoAuthoredBy` | **Deprecated** — użyj `attribution`. Domyślnie `true` | `false` |
| `includeGitInstructions` | Dołącz wbudowane instrukcje git do system promptu (domyślnie `true`) | `false` |

### UI i terminal

| Klucz | Opis | Przykład |
|---|---|---|
| `tui` | Renderer TUI: `"fullscreen"` (alt-screen, brak migotania) lub `"default"` | `"fullscreen"` |
| `editorMode` | Tryb klawiatury dla inputu: `"normal"` lub `"vim"` | `"vim"` |
| `autoScrollEnabled` | Podążaj za nowym outputem w fullscreen (domyślnie `true`) | `false` |
| `showTurnDuration` | Pokaż czas trwania tury (domyślnie `true`) | `false` |
| `spinnerTipsEnabled` | Pokaż tipy w spinnerze (domyślnie `true`) | `false` |
| `syntaxHighlightingDisabled` | Wyłącz syntax highlighting w diffach i blokach kodu | `true` |
| `prefersReducedMotion` | Ogranicz animacje UI | `true` |
| `preferredNotifChannel` | Metoda powiadomień: `"auto"`, `"terminal_bell"`, `"iterm2"`, `"notifications_disabled"` itp. | `"terminal_bell"` |

### Pamięć (memory)

| Klucz | Opis | Przykład |
|---|---|---|
| `autoMemoryEnabled` | Włącz auto memory (domyślnie `true`) | `false` |
| `autoMemoryDirectory` | Niestandardowy katalog auto memory (ścieżka bezwzględna lub `~/…`) | `"~/my-memory-dir"` |
| `claudeMdExcludes` | Glob patterny plików `CLAUDE.md` do pominięcia | `["**/vendor/**/CLAUDE.md"]` |
| `claudeMd` | *(Managed only)* Instrukcje CLAUDE.md wstrzyknięte przez organizację | `"Always run make lint…"` |

### Wtyczki (plugins)

| Klucz | Opis | Przykład |
|---|---|---|
| `enabledPlugins` | Włącz/wyłącz wtyczki (`"plugin@marketplace": true/false`) | `{"formatter@acme-tools": true}` |
| `extraKnownMarketplaces` | Zdefiniuj dodatkowe marketplace dla repozytorium (team onboarding) | patrz przykład niżej |
| `strictKnownMarketplaces` | *(Managed only)* Allowlist źródeł marketplace | |
| `strictPluginOnlyCustomization` | *(Managed only)* Blokuj skills/agents/hooks/MCP z user i project sources | `["skills", "hooks"]` |

### Worktree

| Klucz | Opis | Przykład |
|---|---|---|
| `worktree.baseRef` | Baza nowych worktree: `"fresh"` (origin/<default>) lub `"head"` (lokalny HEAD) | `"head"` |
| `worktree.symlinkDirectories` | Katalogi do symlinkowania z głównego repo do worktree | `["node_modules", ".cache"]` |
| `worktree.sparsePaths` | Sparse checkout — tylko wymienione katalogi | `["packages/my-app"]` |
| `worktree.bgIsolation` | Izolacja tła: `"worktree"` (domyślnie) lub `"none"` | `"none"` |

### Klucze tylko w `~/.claude.json` (nie w settings.json)

Dodanie ich do `settings.json` wygeneruje błąd walidacji schematu.

| Klucz | Opis |
|---|---|
| `autoConnectIde` | Auto-połącz z IDE przy starcie (domyślnie `false`) |
| `autoInstallIdeExtension` | Auto-instaluj rozszerzenie VS Code (domyślnie `true`) |
| `teammateDefaultModel` | Domyślny model dla teammates w agent team |

### Inne ważne klucze

| Klucz | Opis | Przykład |
|---|---|---|
| `apiKeyHelper` | Skrypt (`/bin/sh`) generujący token API (wysyłany jako `X-Api-Key` i `Authorization: Bearer`) | `"/bin/generate_temp_api_key.sh"` |
| `plansDirectory` | Gdzie zapisywać plany (domyślnie `~/.claude/plans`) | `"./plans"` |
| `respectGitignore` | Uwzględnij `.gitignore` w autouzupełnianiu `@` (domyślnie `true`) | `false` |
| `skipWebFetchPreflight` | Pomiń check domeny WebFetch przez `api.anthropic.com` (przydatne na Vertex/Bedrock) | `true` |
| `companyAnnouncements` | Komunikaty wyświetlane przy starcie (losowo z tablicy) | `["Zapoznaj się z guidelines"]` |
| `requiredMinimumVersion` | *(Managed only)* Minimalna wersja wymagana do startu (blokuje startup) | `"2.1.150"` |
| `requiredMaximumVersion` | *(Managed only)* Maksymalna dozwolona wersja | `"2.1.150"` |
| `forceLoginMethod` | *(Managed only)* `claudeai` lub `console` — ogranicza metodę logowania | `"claudeai"` |
| `forceLoginOrgUUID` | *(Managed only)* UUID organizacji wymaganej przy logowaniu | `"xxxx-xxxx-…"` |

---

## Sekcja Permissions

### Klucze obiektu `permissions`

| Klucz | Opis | Przykład |
|---|---|---|
| `allow` | Tablica reguł — narzędzie działa bez pytania | `["Bash(npm run *)"]` |
| `ask` | Tablica reguł — narzędzie pyta o potwierdzenie | `["Bash(git push *)"]` |
| `deny` | Tablica reguł — narzędzie zablokowane | `["WebFetch", "Read(./.env)"]` |
| `additionalDirectories` | Dodatkowe katalogi robocze do odczytu/edycji plików | `["../docs/"]` |
| `defaultMode` | Domyślny tryb uprawnień (patrz tabela trybów) | `"acceptEdits"` |
| `disableBypassPermissionsMode` | `"disable"` — blokuje tryb bypassPermissions | `"disable"` |
| `skipDangerousModePermissionPrompt` | Pomiń potwierdzenie przed wejściem w bypassPermissions | `true` |
| `allowManagedPermissionRulesOnly` | *(Managed only)* Tylko reguły z managed settings obowiązują | `true` |

### Tryby uprawnień (`defaultMode`)

| Tryb | Opis |
|---|---|
| `default` | Standardowe zachowanie — prosi o zgodę przy pierwszym użyciu każdego narzędzia |
| `acceptEdits` | Auto-akceptuje edycje plików i powszechne komendy FS (`mkdir`, `touch`, `mv`, `cp` itp.) |
| `plan` | Tryb tylko-do-odczytu — Claude czyta pliki i uruchamia read-only polecenia, nie edytuje |
| `auto` | Auto-zatwierdza z przetwarzaniem bezpieczeństwa w tle (research preview); od v2.1.142 ignorowany w `.claude/settings.json` — ustaw w `~/.claude/settings.json` |
| `dontAsk` | Auto-odrzuca narzędzia, chyba że pre-approved przez `/permissions` lub `allow` rules |
| `bypassPermissions` | Pomija wszystkie pytania o zgodę (tylko w izolowanych środowiskach!) |

**Uwaga:** `auto` w project/local settings jest ignorowane od v2.1.142 — żeby repozytorium
nie mogło samo sobie nadać trybu auto. Ustaw go w `~/.claude/settings.json`.

### Kolejność ewaluacji reguł

`deny` → `ask` → `allow`. Pierwsza pasująca reguła wygrywa. Reguła `deny` bez specyfikatora
(np. `"Bash"`) usuwa narzędzie z kontekstu Claude całkowicie. Reguła `deny` ze specyfikatorem
(np. `"Bash(rm *)"`) zostawia narzędzie dostępne, ale blokuje pasujące wywołania.

### Składnia reguł uprawnień

Format: `Tool` lub `Tool(specifier)`.

**Dopasowanie wszystkich użyć narzędzia:**

| Reguła | Efekt |
|---|---|
| `Bash` | Wszystkie polecenia Bash |
| `WebFetch` | Wszystkie żądania WebFetch |
| `Read` | Wszystkie odczyty plików |

**Wzorce dla Bash:**

| Reguła | Dopasowuje |
|---|---|
| `Bash(npm run build)` | Dokładnie `npm run build` |
| `Bash(npm run test *)` | Komendy zaczynające się od `npm run test` |
| `Bash(* --version)` | Dowolna komenda kończąca się `--version` |
| `Bash(git * main)` | `git checkout main`, `git log --oneline main` itp. |

Spacja przed `*` ma znaczenie: `Bash(ls *)` pasuje do `ls -la` ale nie `lsof`.
`Bash(ls*)` pasuje do obu. `:*` na końcu jest odpowiednikiem ` *`.

Złożone komendy (`&&`, `||`, `;`, `|`): każda podkomenda musi pasować do reguły niezależnie.

**Read i Edit — typy ścieżek:**

| Pattern | Znaczenie | Przykład |
|---|---|---|
| `//path` | Absolutna ścieżka od roota FS | `Read(//Users/alice/secrets/**)` |
| `~/path` | Od katalogu domowego | `Read(~/.zshrc)` |
| `/path` | Względna od project root | `Edit(/src/**/*.ts)` |
| `path` lub `./path` | Względna od bieżącego katalogu | `Read(*.env)` |

Na Windows ścieżki są normalizowane do POSIX: `C:\Users\alice` → `/c/Users/alice`.

**WebFetch:**

`WebFetch(domain:example.com)` — pasuje do żądań do `example.com`.

**MCP:**

| Reguła | Efekt |
|---|---|
| `mcp__puppeteer` | Wszystkie narzędzia serwera `puppeteer` |
| `mcp__puppeteer__*` | Odpowiednik powyższego (wildcard) |
| `mcp__puppeteer__puppeteer_navigate` | Konkretne narzędzie `puppeteer_navigate` |

**Agent (subagenci):**

| Reguła | Efekt |
|---|---|
| `Agent(Explore)` | Subagent Explore |
| `Agent(my-custom-agent)` | Niestandardowy subagent |

---

## Zmienne środowiskowe — tabela operacyjna

Zmienne te można też ustawić w `settings.json` pod kluczem `env`. W powłoce:
```powershell
$env:ANTHROPIC_MODEL = "claude-opus-4-8"
claude
```
Lub trwale dla sesji PowerShell:
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL", "claude-opus-4-8", "User")
```

### Uwierzytelnianie i provider

| Zmienna | Opis |
|---|---|
| `ANTHROPIC_API_KEY` | Klucz API (`X-Api-Key`). W sesji interaktywnej pyta o potwierdzenie przed nadpisaniem subskrypcji |
| `ANTHROPIC_AUTH_TOKEN` | Niestandardowy token `Authorization: Bearer …` |
| `ANTHROPIC_BASE_URL` | Nadpisz endpoint API (proxy / gateway) |
| `ANTHROPIC_MODEL` | Nazwa modelu; nadpisywane przez `--model` i `/model` |
| `ANTHROPIC_VERTEX_BASE_URL` | Nadpisz endpoint Vertex AI |
| `ANTHROPIC_VERTEX_PROJECT_ID` | GCP project ID dla Vertex AI |
| `ANTHROPIC_BEDROCK_BASE_URL` | Nadpisz endpoint Bedrock |
| `ANTHROPIC_FOUNDRY_API_KEY` | Klucz API dla Microsoft Foundry |
| `ANTHROPIC_FOUNDRY_BASE_URL` | Pełny base URL zasobu Foundry |
| `CLAUDE_CODE_USE_VERTEX` | Użyj Vertex AI |
| `CLAUDE_CODE_USE_BEDROCK` | Użyj Amazon Bedrock |
| `CLAUDE_CODE_USE_FOUNDRY` | Użyj Microsoft Foundry |
| `CLAUDE_CODE_OAUTH_TOKEN` | OAuth access token dla Claude.ai (alternatywa dla `/login`) |

### Model i wysiłek

| Zmienna | Opis |
|---|---|
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | Nadpisz model Opus |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | Nadpisz model Sonnet |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | Nadpisz model Haiku (tło, mniejsze zadania) |
| `CLAUDE_CODE_EFFORT_LEVEL` | Poziom wysiłku: `low`/`medium`/`high`/`xhigh`/`max`/`auto`. Nadpisuje `/effort` i `effortLevel` |
| `MAX_THINKING_TOKENS` | Budżet tokenów dla extended thinking (0 = wyłącz) |
| `CLAUDE_CODE_DISABLE_THINKING` | `1` — wyłącz extended thinking bezwarunkowo |
| `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` | `1` — wyłącz adaptive reasoning, użyj fixed budget z `MAX_THINKING_TOKENS` |
| `CLAUDE_CODE_MAX_OUTPUT_TOKENS` | Maks. tokeny output na request |
| `CLAUDE_CODE_SUBAGENT_MODEL` | Model dla subagentów |

### Timeouty i limity

| Zmienna | Opis | Domyślnie |
|---|---|---|
| `API_TIMEOUT_MS` | Timeout żądań API | 600 000 (10 min) |
| `BASH_DEFAULT_TIMEOUT_MS` | Domyślny timeout dla Bash | 120 000 (2 min) |
| `BASH_MAX_TIMEOUT_MS` | Maks. timeout Bash (model może ustawić niżej) | 600 000 (10 min) |
| `BASH_MAX_OUTPUT_LENGTH` | Maks. znaki w outputcie Bash (powyżej → zapis do pliku) | — |
| `CLAUDE_CODE_MAX_RETRIES` | Liczba ponownych prób przy błędach API | 10 |
| `CLAUDE_CODE_MAX_TURNS` | Cap na liczbę tur agentycznych | — |
| `MCP_TIMEOUT` | Timeout startu serwera MCP | 30 000 (30 s) |
| `MCP_TOOL_TIMEOUT` | Timeout wykonania narzędzia MCP | ~28 godz. |
| `MCP_CONNECT_TIMEOUT_MS` | Timeout oczekiwania na połączenie batch MCP | 5 000 |

### Agent Teams i subagenci

| Zmienna | Opis |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` | `1` — włącz agent teams (eksperymentalne) |
| `CLAUDE_CODE_DISABLE_AGENT_VIEW` | `1` — wyłącz background agents i agent view |
| `CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS` | Timeout bezczynności dla background subagentów (domyślnie 600 000) |
| `CLAUDE_CODE_AUTO_BACKGROUND_TASKS` | `1` — automatycznie przesuń długie zadania w tło (~2 min) |
| `CLAUDE_CODE_FORK_SUBAGENT` | `1` — forked subagenci domyślnie; `0` — wyłącz |

### Kontekst i kompaktacja

| Zmienna | Opis |
|---|---|
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | Próg kompaktacji (1–100, domyślnie ~95%) |
| `DISABLE_AUTO_COMPACT` | `1` — wyłącz auto-kompaktację (ręczny `/compact` pozostaje) |
| `DISABLE_COMPACT` | `1` — wyłącz wszelką kompaktację |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS` | Nadpisz rozmiar okna kontekstowego (tylko z `DISABLE_COMPACT=1`) |

### Hooki i zmienne sesji

| Zmienna | Opis |
|---|---|
| `CLAUDECODE` | Ustawiane przez Claude Code na `1` w subprocesach (Bash, hooki, MCP stdio) — do detekcji |
| `CLAUDE_CODE_SESSION_ID` | ID bieżącej sesji (ustawiane auto w subprocesach i hookach) |
| `CLAUDE_PROJECT_DIR` | Katalog projektu (dostępny w hookach) |
| `CLAUDE_ENV_FILE` | Ścieżka do skryptu wykonywanego przed każdą komendą Bash (persist virtualenv itp.) |
| `CLAUDE_EFFORT` | Aktywny poziom wysiłku dla tury (ustawiany auto w hookach i subprocesach Bash) |

### Aktualizacje, telemetria, prywatność

| Zmienna | Opis |
|---|---|
| `DISABLE_AUTOUPDATER` | `1` — wyłącz automatyczne aktualizacje tła |
| `DISABLE_UPDATES` | `1` — zablokuj wszystkie aktualizacje (też ręczne `claude update`) |
| `DISABLE_TELEMETRY` | `1` — rezygnacja z telemetrii |
| `DO_NOT_TRACK` | `1` — odpowiednik `DISABLE_TELEMETRY` |
| `DISABLE_ERROR_REPORTING` | `1` — rezygnacja z raportowania błędów Sentry |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | Odpowiednik ustawienia `DISABLE_AUTOUPDATER` + `DISABLE_FEEDBACK_COMMAND` + `DISABLE_ERROR_REPORTING` + `DISABLE_TELEMETRY` |

### Windows i PowerShell

| Zmienna | Opis |
|---|---|
| `CLAUDE_CODE_GIT_BASH_PATH` | Ścieżka do `bash.exe` gdy Git Bash nie jest w PATH |
| `CLAUDE_CODE_USE_POWERSHELL_TOOL` | `1` — włącz narzędzie PowerShell; `0` — wyłącz |
| `CLAUDE_CODE_POWERSHELL_RESPECT_EXECUTION_POLICY` | `1` — respektuj execution policy (zamiast `-ExecutionPolicy Bypass`) |

### Ważne pozostałe

| Zmienna | Opis |
|---|---|
| `CLAUDE_CONFIG_DIR` | Nadpisz katalog konfiguracji (domyślnie `~/.claude`) — przydatne do wielu kont |
| `CLAUDE_CODE_SHELL` | Nadpisz auto-detekcję powłoki |
| `CLAUDE_CODE_SKIP_PROMPT_HISTORY` | `1` — nie zapisuj historii promptów i transkryptów sesji |
| `PYTHONIOENCODING` | Ustaw `utf-8` na Windows by uniknąć błędów Unicode codec w pipeline |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | Konfiguracja proxy dla połączeń sieciowych |
| `CLAUDE_CODE_ENABLE_TELEMETRY` | `1` — włącz zbieranie danych OpenTelemetry (metrics/logging) |
| `CLAUDE_CODE_DISABLE_WORKFLOWS` | `1` — wyłącz dynamic workflows |
| `CLAUDE_CODE_DISABLE_AUTO_MEMORY` | `1` — wyłącz auto memory |
| `CLAUDE_CODE_DISABLE_CLAUDE_MDS` | `1` — nie ładuj żadnych plików CLAUDE.md |
| `DEBUG` | `1` — tryb debug (logi → `~/.claude/debug/<session-id>.txt`) |

---

## Przykładowy settings.json — projekt SENSUM

Pełny przykład dla `.claude/settings.json` w tym repozytorium:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "claude-sonnet-4-6",
  "permissions": {
    "allow": [
      "Bash(python tools/pipeline/*.py *)",
      "Bash(python tools/*.py *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(ls *)",
      "Read(./outputs/**)",
      "Read(./tools/**)",
      "Read(./workflows/**)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(git push --force *)"
    ],
    "defaultMode": "default"
  },
  "env": {
    "PYTHONIOENCODING": "utf-8",
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  },
  "includeCoAuthoredBy": true,
  "cleanupPeriodDays": 30,
  "teammateMode": "in-process"
}
```

Minimalny przykład z dokumentacji (zarządzanie telemetrią):

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test *)",
      "Read(~/.zshrc)"
    ],
    "deny": [
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)"
    ]
  },
  "env": {
    "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
    "OTEL_METRICS_EXPORTER": "otlp"
  }
}
```

Przykład konfiguracji sandboxingu:

```json
{
  "sandbox": {
    "enabled": true,
    "autoAllowBashIfSandboxed": true,
    "excludedCommands": ["docker *"],
    "filesystem": {
      "allowWrite": ["/tmp/build", "~/.kube"],
      "denyRead": ["~/.aws/credentials"]
    },
    "network": {
      "allowedDomains": ["github.com", "*.npmjs.org"],
      "allowLocalBinding": true
    }
  }
}
```

---

## Sekcja Managed Settings — kluczowe zachowania

Managed settings (administrator IT) nie mogą być nadpisane przez żaden inny poziom — nawet przez
`--allowedTools` w CLI. To jedyne miejsce, gdzie działają klucze takie jak `allowManagedPermissionRulesOnly`,
`forceLoginMethod`, `requiredMinimumVersion` itp.

**Scalanie vs. nadpisywanie:**
- Tablice (np. `permissions.allow`, `sandbox.filesystem.allowWrite`) są **scalane** ze wszystkich źródeł
- Wartości skalarne z wyższego poziomu **nadpisują** niższe

**`policyHelper`** — dynamiczne managed settings: administrator może wskazać skrypt, który przy starcie
generuje JSON z ustawieniami (np. na podstawie tożsamości urządzenia). Działa tylko z MDM lub
systemowego `managed-settings.json`.

---

## Praktyczne przepisy dla projektu SENSUM (Windows + PowerShell)

**Gdzie co ustawić:**

| Co | Gdzie |
|---|---|
| `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (trwałe) | `.claude/settings.json` → `env` |
| `PYTHONIOENCODING=utf-8` (trwałe dla projektu) | `.claude/settings.json` → `env` |
| Klucz Vertex AI / Gemini | `.env` (nigdy w settings.json!) |
| `defaultMode: "acceptEdits"` (osobiste) | `~/.claude/settings.json` → `permissions` |
| Blokada `.env` przed odczytem | `.claude/settings.json` → `permissions.deny` |
| Tryb auto (eksperymentalny) | `~/.claude/settings.json` → `permissions.defaultMode` |

**Ustawienie zmiennej env trwale w PowerShell (poza settings.json):**
```powershell
[Environment]::SetEnvironmentVariable("ANTHROPIC_MODEL", "claude-opus-4-8", "User")
# Wymagany restart terminala
```

**Prefix dla pipeline (obejście Windows Unicode):**
```powershell
$env:PYTHONIOENCODING = "utf-8"
python tools/pipeline/agent1_research.py "temat"
```
Lub w `.claude/settings.json`:
```json
{ "env": { "PYTHONIOENCODING": "utf-8" } }
```

---

## Gotchas i pułapki

- **`auto` w `.claude/settings.json`** — ignorowane od v2.1.142 (repozytorium nie może samo sobie nadać
  trybu auto). Ustaw w `~/.claude/settings.json`.

- **`/path` ≠ ścieżka absolutna** — w regułach Read/Edit `/path` to ścieżka względna od project root,
  nie od roota systemu plików. Absolutna to `//path` (podwójny slash).

- **`Bash(curl http://github.com/ *)` nie chroni** — wzorce Bash są kruche; opcje przed URL, inne
  protokoły, przekierowania, zmienne, dodatkowe spacje — wszystko może obejść regułę. Bezpieczniejsze
  podejście: zablokuj `Bash(curl *)` i użyj `WebFetch(domain:github.com)`.

- **Tablice scalają się, nie nadpisują** — jeśli managed settings ustawi `allow: [X]`, a projekt
  ustawi `allow: [Y]`, efektywna lista to `[X, Y]`.

- **`model` i `outputStyle`** wczytywane są tylko raz na start sesji — zmiana w trakcie wymaga
  `/model` lub restartu.

- **`disabledMcpjsonServers`** odrzuca serwery z `.mcp.json`; `enabledMcpjsonServers` je zatwierdza.
  Oba działają jako filtr dla serwerów zdefiniowanych w plikach `.mcp.json`.

- **Hooki** — osobny temat (lifecycle events: `PreToolUse`, `PostToolUse`, `Stop`, `SessionStart` itp.).
  Dokumentacja: `workflows/pipeline/` + `.claude/settings.json` → `hooks`. Klucz `disableAllHooks: true`
  wyłącza wszystkie naraz.

- **`$schema`** — dodaj do `settings.json` dla autouzupełniania w VS Code / Cursor:
  `"$schema": "https://json.schemastore.org/claude-code-settings.json"`

---

## Źródła

- Settings: https://code.claude.com/docs/en/settings.md
- Permissions: https://code.claude.com/docs/en/permissions.md
- Environment Variables: https://code.claude.com/docs/en/env-vars.md
- Permission Modes: https://code.claude.com/docs/en/permission-modes.md
- Sandboxing: https://code.claude.com/docs/en/sandboxing.md
