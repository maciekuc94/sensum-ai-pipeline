# MCP w Claude Code — kompletna instrukcja

> Referencja „jak skonfigurować i używać serwerów MCP". Źródło: https://code.claude.com/docs/en/mcp.md
> (pobrane 2026-06-09). Komendy `claude mcp ...`, klucze `.mcp.json`, nazwy transportów i bloki
> kodu/JSON zostawione **verbatim** po angielsku — to kontrakt z harnessem, nie tłumacz ich.
> Proza wyjaśniająca po polsku.

---

## Czym jest MCP i co daje

**Model Context Protocol (MCP)** to otwarty standard integracji AI z zewnętrznymi narzędziami
(specyfikacja: [modelcontextprotocol.io](https://modelcontextprotocol.io/introduction)). Serwer MCP
jest mostem między Claude Code a zewnętrznym systemem — trackerem zadań, bazą danych, API, monitorem
błędów. Zamiast kopiować dane do czatu, Claude czyta i działa bezpośrednio na tym systemie.

**Co zyskujesz przez serwer MCP:**

- **Narzędzia** — Claude może wywoływać funkcje serwera (np. stwórz issue, zapytaj bazę, pobierz logi)
- **Zasoby** — dane do przeczytania przez `@server:protocol://path` (pliki, schematy, dokumentacja)
- **Prompty MCP jako slash commands** — serwer może dostarczać gotowe komendy, np. `/mcp__github__pr_review 456`

**Przykłady zastosowań:**

- „Zaimplementuj feature z JIRA ENG-4521 i utwórz PR na GitHubie"
- „Sprawdź Sentry i podaj najczęstsze błędy z ostatnich 24 h"
- „Znajdź e-maile 10 losowych użytkowników z PostgreSQL"
- „Zaktualizuj szablon e-mail według nowego projektu z Figmy"

**W tym projekcie (SENSUM) używane serwery MCP:**

- **context-mode** — oszczędzanie okna kontekstu (`ctx_execute`, `ctx_search`, `ctx_fetch_and_index`)
- **claude-in-chrome** — automatyzacja przeglądarki Chrome (narzędzia ładowane przez `ToolSearch`)

---

## Jak dodać serwer — przegląd opcji

### Opcja 1 — Zdalny serwer HTTP (zalecane)

Najszerzej wspierany transport dla usług chmurowych.

```bash
# Podstawowa składnia
claude mcp add --transport http <name> <url>

# Połączenie z Notion
claude mcp add --transport http notion https://mcp.notion.com/mcp

# Z tokenem Bearer w nagłówku
claude mcp add --transport http secure-api https://api.example.com/mcp \
  --header "Authorization: Bearer your-token"
```

> W `.mcp.json` i `claude mcp add-json` pole `type` przyjmuje też alias `streamable-http` — to
> oficjalna nazwa tego transportu w specyfikacji MCP. Konfiguracje skopiowane z dokumentacji
> serwerów działają bez zmian.

### Opcja 2 — Zdalny serwer SSE (przestarzały)

Transport Server-Sent Events jest **deprecated** — gdzie możliwe, używaj HTTP.

```bash
claude mcp add --transport sse asana https://mcp.asana.com/sse

# Z kluczem API
claude mcp add --transport sse private-api https://api.company.com/sse \
  --header "X-API-Key: your-key-here"
```

### Opcja 3 — Lokalny serwer stdio

Serwer uruchamia się jako proces lokalny. Najlepszy do narzędzi wymagających bezpośredniego dostępu
do systemu lub własnych skryptów.

```bash
# Podstawowa składnia
claude mcp add [options] <name> -- <command> [args...]

# Dodanie serwera Airtable
claude mcp add --env AIRTABLE_API_KEY=YOUR_KEY --transport stdio airtable \
  -- npx -y airtable-mcp-server

# Serwer lokalnej bazy PostgreSQL
claude mcp add --transport stdio db -- npx -y @bytebase/dbhub \
  --dsn "postgresql://readonly:pass@prod.db.com:5432/analytics"
```

> **Ważne — `--` (podwójny myślnik):** Oddziela opcje Claude od komendy i argumentów serwera.
> Wszystko po `--` trafia do serwera bez zmian. Bez separatora Claude próbuje parsować flagi serwera
> (np. `--port`) jako własne opcje i zwraca błąd.
>
> Zmienna `CLAUDE_PROJECT_DIR` jest automatycznie ustawiana w środowisku spawnanego serwera stdio
> i wskazuje na katalog projektu — można ją czytać przez `process.env.CLAUDE_PROJECT_DIR` (Node)
> lub `os.environ["CLAUDE_PROJECT_DIR"]` (Python).

### Opcja 4 — Zdalny serwer WebSocket

Utrzymuje trwałe, dwukierunkowe połączenie — przydatne gdy serwer sam pushuje eventy do Claude
(alerty, wyniki CI). Gdy serwer tylko odpowiada na żądania, lepiej używać HTTP (obsługuje OAuth
i flagę `--transport`). WebSocket konfiguruje się przez `.mcp.json` lub `claude mcp add-json`:

```bash
claude mcp add-json events-server \
  '{"type":"ws","url":"wss://mcp.example.com/socket","headers":{"Authorization":"Bearer YOUR_TOKEN"}}'
```

### Dodawanie z JSON (`add-json`)

Gdy masz gotową konfigurację JSON:

```bash
# Serwer HTTP
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'

# Serwer stdio
claude mcp add-json local-tools '{"type":"stdio","command":"/path/to/server","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'
```

### Import z Claude Desktop

Na macOS i WSL można zaimportować serwery skonfigurowane w Claude Desktop:

```bash
claude mcp add-from-claude-desktop
# Pojawi się interaktywne menu — wybierz serwery do importu
```

---

## Zarządzanie serwerami

```bash
claude mcp list               # Lista wszystkich skonfigurowanych serwerów
claude mcp get github         # Szczegóły konkretnego serwera
claude mcp remove github      # Usunięcie serwera
/mcp                          # Panel statusu (wewnątrz sesji Claude Code)
```

Serwery ze scope `project` (`.mcp.json`) wymagają jednorazowego zatwierdzenia przed użyciem.
Status `⏸ Pending approval` w `claude mcp list` oznacza oczekiwanie na akceptację — uruchom Claude
interaktywnie, żeby zatwierdzić. Reset zatwierdzonych wyborów: `claude mcp reset-project-choices`.

Nazwa `workspace` jest zarezerwowana — Claude Code pomija serwer o tej nazwie.

---

## Scopes — gdzie żyje konfiguracja

Trzy zakresy decydują, które projekty ładują serwer i czy konfiguracja jest współdzielona z zespołem.

| Scope       | Dostępny w             | Udostępniony zespołowi   | Przechowywany w                 |
|-------------|------------------------|--------------------------|----------------------------------|
| `local`     | Tylko bieżący projekt  | Nie                      | `~/.claude.json`                 |
| `project`   | Tylko bieżący projekt  | Tak, przez kontrolę wersji | `.mcp.json` w katalogu projektu |
| `user`      | Wszystkie projekty     | Nie                      | `~/.claude.json`                 |

### local (domyślny)

Prywatny serwer tylko dla bieżącego projektu. Przechowywany w `~/.claude.json`. Stosuj dla
konfiguracji developerskich, eksperymentalnych lub z danymi uwierzytelniającymi, których nie chcesz
w repozytorium.

```bash
# Domyślnie to local
claude mcp add --transport http stripe https://mcp.stripe.com

# Jawne określenie scope
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

Wynik w `~/.claude.json`:

```json
{
  "projects": {
    "/path/to/your/project": {
      "mcpServers": {
        "stripe": {
          "type": "http",
          "url": "https://mcp.stripe.com"
        }
      }
    }
  }
}
```

### project — commitowany w repozytorium

Plik `.mcp.json` w katalogu projektu — commituj go do gita, żeby wszyscy w zespole mieli te same
narzędzia. Przed użyciem Claude Code pyta o zatwierdzenie ze względów bezpieczeństwa.

```bash
claude mcp add --transport http paypal --scope project https://mcp.paypal.com/mcp
```

Wynikowy `.mcp.json`:

```json
{
  "mcpServers": {
    "shared-server": {
      "command": "/path/to/server",
      "args": [],
      "env": {}
    }
  }
}
```

### user — dostępny globalnie

Przechowywany w `~/.claude.json`, dostępny we wszystkich projektach na tej maszynie, prywatny dla
Twojego konta.

```bash
claude mcp add --transport http hubspot --scope user https://mcp.hubspot.com/anthropic
```

### Hierarchia i precedencja (przy konflikcie nazw)

Gdy ten sam serwer jest zdefiniowany w więcej niż jednym miejscu, Claude Code łączy się z nim raz,
używając definicji z najwyższego priorytetu. **Pola nie są mergowane** — całość pochodzi z jednego
źródła.

1. **local** (najwyższy priorytet)
2. **project** (`.mcp.json`)
3. **user**
4. Serwery dostarczane przez pluginy
5. Konektory claude.ai

---

## Zmienne środowiskowe w `.mcp.json`

`.mcp.json` obsługuje ekspansję zmiennych środowiskowych, dzięki czemu możesz commitować konfigurację
bez hardkodowania sekretów.

**Wspierana składnia:**

- `${VAR}` — wartość zmiennej `VAR`
- `${VAR:-default}` — wartość `VAR` jeśli ustawiona, inaczej `default`

**Gdzie działa ekspansja:** `command`, `args`, `env`, `url`, `headers`.

**Przykład z ekspansją:**

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

Jeśli wymagana zmienna nie jest ustawiona i nie ma domyślnej wartości, Claude Code zgłosi błąd
parsowania konfiguracji.

---

## Transporty — schemat wpisu serwera

### Pola wspólne (wszystkie typy)

| Pole         | Typ      | Opis                                                                        |
|--------------|----------|-----------------------------------------------------------------------------|
| `type`       | string   | `"http"` / `"streamable-http"` / `"sse"` / `"ws"` / `"stdio"`             |
| `timeout`    | number   | Limit czasu jednego wywołania narzędzia (ms); wartości < 1000 są ignorowane |
| `alwaysLoad` | boolean  | Ładuje narzędzia serwera do kontekstu od razu, bez deferral (domyślnie false) |

### HTTP / SSE / WebSocket

| Pole            | Typ    | Opis                                                     |
|-----------------|--------|----------------------------------------------------------|
| `url`           | string | Adres serwera                                            |
| `headers`       | object | Statyczne nagłówki HTTP (np. `Authorization`)            |
| `headersHelper` | string | Komenda shell generująca nagłówki dynamicznie            |
| `oauth`         | object | Konfiguracja OAuth (`clientId`, `callbackPort`, `scopes`, `authServerMetadataUrl`) |

### stdio

| Pole      | Typ           | Opis                                                    |
|-----------|---------------|---------------------------------------------------------|
| `command` | string        | Ścieżka do pliku wykonywalnego                          |
| `args`    | string[]      | Argumenty wiersza poleceń                               |
| `env`     | object        | Zmienne środowiskowe przekazywane do procesu serwera    |

### Pełny przykład `.mcp.json` z różnymi typami

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_PAT}"
      }
    },
    "local-scripts": {
      "type": "stdio",
      "command": "${HOME}/.local/bin/my-mcp-server",
      "args": ["--config", "${CLAUDE_PROJECT_DIR:-./}/.mcp-config.json"],
      "env": {
        "LOG_LEVEL": "info"
      }
    },
    "events": {
      "type": "ws",
      "url": "wss://mcp.example.com/socket",
      "headers": {
        "Authorization": "Bearer ${WS_TOKEN}"
      },
      "alwaysLoad": true
    }
  }
}
```

---

## Autoryzacja — OAuth i inne schematy

### OAuth 2.0 dla zdalnych serwerów

Claude Code automatycznie rozpoznaje serwery wymagające OAuth, gdy zwracają `401 Unauthorized`
lub `403 Forbidden`. Pełny flow:

1. Dodaj serwer: `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`
2. Uruchom `/mcp` w Claude Code
3. Postępuj według kroków w przeglądarce

**Ważne szczegóły OAuth:**

- Tokeny są przechowywane bezpiecznie i odświeżane automatycznie
- „Clear authentication" w menu `/mcp` cofa dostęp
- Jeśli przekierowanie przeglądarki nie działa, skopiuj pełny URL callback ręcznie
- OAuth działa tylko z transportem HTTP i SSE (nie stdio, nie ws)
- Jeśli skonfigurowano `headers.Authorization` i serwer go odrzuci — Claude Code zgłosi błąd
  zamiast fallbackować na OAuth; sprawdź ważność tokenu

### Stały port callbacku OAuth

Gdy serwer wymaga konkretnego redirect URI zarejestrowanego z góry:

```bash
claude mcp add --transport http --callback-port 8080 my-server https://mcp.example.com/mcp
```

### Pre-konfigurowane dane uwierzytelniające OAuth

Gdy serwer nie obsługuje Dynamic Client Registration:

```bash
claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

Przez zmienną środowiskową (tryb CI):

```bash
MCP_CLIENT_SECRET=your-secret claude mcp add --transport http \
  --client-id your-client-id --client-secret --callback-port 8080 \
  my-server https://mcp.example.com/mcp
```

Sekret trafia do keychain systemu (macOS) lub pliku credentials — **nie** do `~/.claude.json`.

### Ograniczenie scope'ów OAuth

```json
{
  "mcpServers": {
    "slack": {
      "type": "http",
      "url": "https://mcp.slack.com/mcp",
      "oauth": {
        "scopes": "channels:read chat:write search:read"
      }
    }
  }
}
```

Wartość `oauth.scopes` nadpisuje zakresy reklamowane przez serwer — przydatne, gdy chcesz ograniczyć
dostęp do zatwierdzonego podzbioru uprawnień.

### Dynamiczne nagłówki (Kerberos, krótkotrwałe tokeny, SSO)

Zamiast tokenu statycznego możesz użyć `headersHelper` — komenda shell generuje nagłówki przy każdym
połączeniu:

```json
{
  "mcpServers": {
    "internal-api": {
      "type": "http",
      "url": "https://mcp.internal.example.com",
      "headersHelper": "/opt/bin/get-mcp-auth-headers.sh"
    }
  }
}
```

Wymagania: skrypt musi wypisać na stdout JSON z parami klucz-wartość (`string: string`); timeout 10 s;
dynamiczne nagłówki nadpisują statyczne `headers` o tej samej nazwie.

---

## Używanie narzędzi, zasobów i promptów MCP

### Narzędzia — nazewnictwo `mcp__server__tool`

Narzędzia dostarczone przez serwer MCP pojawiają się w Claude Code pod nazwą
`mcp__<server-name>__<tool-name>`. Przykłady z tego projektu:

- `mcp__plugin_context-mode_context-mode__ctx_execute`
- `mcp__plugin_context-mode_context-mode__ctx_search`
- `mcp__claude-in-chrome__navigate`

Narzędzia MCP są domyślnie **deferowane** (patrz sekcja Tool Search poniżej) — nie ładują się przy
starcie sesji, tylko na żądanie przez `ToolSearch`. Żeby załadować schemat konkretnego narzędzia
przed wywołaniem: `ToolSearch(query: "select:mcp__server__tool")`.

### Zasoby przez `@`

Zasoby MCP można przywołać przez `@` w prompcie:

```
Can you analyze @github:issue://123 and suggest a fix?
Compare @postgres:schema://users with @docs:file://database/user-model
```

Zasoby pojawiają się w autocomplete razem z plikami przy wpisaniu `@`. Są fetchowane i dołączane
automatycznie jako załączniki.

### Prompty MCP jako slash commands

Serwer może dostarczać gotowe prompty widoczne jako komendy. Format: `/mcp__servername__promptname`.

```
/mcp__github__list_prs
/mcp__github__pr_review 456
/mcp__jira__create_issue "Bug in login flow" high
```

Nazwy serwera i promptu są normalizowane (spacje → podkreślniki). Prompty pojawiają się w menu `/`.

---

## Tool Search — deferowanie narzędzi MCP

Domyślnie Claude Code **nie ładuje definicji narzędzi MCP przy starcie sesji**. Przy każdym żądaniu
Claude korzysta z narzędzia `ToolSearch`, żeby znaleźć potrzebne narzędzia na żądanie. Tylko
faktycznie użyte narzędzia trafiają do kontekstu — to oszczędza okno kontekstu przy dużej liczbie
serwerów.

### Konfiguracja `ENABLE_TOOL_SEARCH`

| Wartość    | Zachowanie                                                                                |
|------------|-------------------------------------------------------------------------------------------|
| (nie ustawiona) | Wszystkie narzędzia MCP deferowane. Na Vertex AI i niestandardowym `ANTHROPIC_BASE_URL` — ładowanie upfront |
| `true`     | Pełny deferral (wymuś nawet na Vertex AI)                                                 |
| `auto`     | Tryb progowy: ładuj upfront jeśli zmieszczą się w 10% okna kontekstu, reszta deferowana  |
| `auto:N`   | Tryb progowy z niestandardowym `N`% (np. `auto:5`)                                       |
| `false`    | Wszystkie narzędzia ładowane upfront — bez deferral                                       |

```bash
ENABLE_TOOL_SEARCH=auto:5 claude
ENABLE_TOOL_SEARCH=false claude
```

Można też ustawić w `settings.json` (pole `env`).

### `alwaysLoad` — wyłączenie deferral dla serwera

Jeśli narzędzia serwera mają być zawsze dostępne bez kroku wyszukiwania:

```json
{
  "mcpServers": {
    "core-tools": {
      "type": "http",
      "url": "https://mcp.example.com/mcp",
      "alwaysLoad": true
    }
  }
}
```

Wymaga Claude Code v2.1.121+. Zwiększa zużycie kontekstu — stosuj tylko dla niezbędnych narzędzi.

### Wyłączenie narzędzia `ToolSearch`

```json
{
  "permissions": {
    "deny": ["ToolSearch"]
  }
}
```

---

## Uprawnienia i bezpieczeństwo

### `allowedMcpServers` / `deniedMcpServers`

Dla organizacji potrzebujących centralnej kontroli nad tym, do jakich serwerów użytkownicy mogą
się podłączyć — patrz [Managed MCP configuration](https://code.claude.com/docs/en/managed-mcp).
Administratorzy mogą wdrożyć stały zestaw serwerów przez `managed-mcp.json` i ograniczać serwery
przez `allowedMcpServers` / `deniedMcpServers`.

### `--strict-mcp-config`

Flaga startowa wymuszająca, że Claude Code przyjmuje konfigurację MCP **tylko** z pliku config
(nie z interaktywnych promptów). Przydatne w środowiskach CI/CD.

### Limity outputu narzędzi

Claude Code wyświetla ostrzeżenie, gdy output narzędzia MCP przekroczy **10 000 tokenów**.
Domyślny limit: **25 000 tokenów**.

```bash
export MAX_MCP_OUTPUT_TOKENS=50000
claude
```

Timeout jednego wywołania narzędzia: zmienna `MCP_TOOL_TIMEOUT` (domyślnie ~28 h) lub pole
`timeout` w konfiguracji serwera. Timeout startowy całego serwera: `MCP_TIMEOUT` (np.
`MCP_TIMEOUT=10000 claude`).

---

## Scoping serwerów MCP do subagentów

Przy tworzeniu subagenta (`.claude/agents/<name>.md`) możesz ograniczyć mu dostępne serwery MCP
przez pole `mcpServers` w frontmatterze — tylko wymienione serwery będą dostępne w tym subagentach
(zamiast dziedziczenia całego zestawu sesji nadrzędnej). Szczegóły i przykłady:
`docs/subagents_reference.md`.

---

## Pluginy i serwery MCP

Pluginy mogą bundlować serwery MCP — automatycznie dostarczają narzędzia po zainstalowaniu pluginu.
Konfiguracja w `.mcp.json` w katalogu pluginu lub inline w `plugin.json`:

```json
{
  "mcpServers": {
    "database-tools": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "DB_URL": "${DB_URL}"
      }
    }
  }
}
```

Zmienne specjalne dla pluginów: `${CLAUDE_PLUGIN_ROOT}` (pliki bundlowane), `${CLAUDE_PLUGIN_DATA}`
(trwały stan przeżywający update pluginu), `${CLAUDE_PROJECT_DIR}` (katalog projektu).

Po włączeniu/wyłączeniu pluginu w trakcie sesji: `/reload-plugins`.

---

## Gotchas — częste pułapki

| Problem | Przyczyna i rozwiązanie |
|---------|------------------------|
| Narzędzie MCP niedostępne mimo skonfigurowanego serwera | Tool Search jest aktywny — użyj `ToolSearch(query: "select:mcp__server__tool")` przed wywołaniem |
| `spawn claude ENOENT` w Claude Desktop | `command` w konfiguracji nie jest pełną ścieżką; znajdź ją przez `which claude` |
| Serwer stdio ignoruje `${CLAUDE_PROJECT_DIR}` w `.mcp.json` | W scope project/local dodaj default: `${CLAUDE_PROJECT_DIR:-.}` — bez niego ekspansja może zwrócić pusty string |
| Serwer pojawia się jako `⏸ Pending approval` | Serwer project-scope czeka na zatwierdzenie — uruchom Claude interaktywnie |
| OAuth: „does not support dynamic client registration" | Serwer wymaga pre-konfiguracji — zarejestruj app w portalu developerskim, użyj `--client-id` |
| Serwer w `/mcp` jako `failed` po 5 próbach | Reconnect: HTTP/SSE — ręcznie z `/mcp`; stdio — nie reconnectuje się automatycznie |
| Output ostrzeżenie >10 000 tokenów | Ustaw `MAX_MCP_OUTPUT_TOKENS=50000` lub poproś autora serwera o paginację |
| Nazwa serwera `workspace` zignorowana | Zarezerwowana nazwa — zmień nazwę serwera |
| `--env KEY=value` plus nazwa serwera bez żadnej opcji między nimi | CLI czyta nazwę jako kolejną parę `KEY=value` — wstaw inną opcję między `--env` a nazwą serwera |
| Serwer claude.ai nie pojawia się mimo logowania | Aktywna metoda auth to `ANTHROPIC_API_KEY` lub `apiKeyHelper` — konektory claude.ai ładują się tylko przez auth claude.ai (`/login`) |

---

## Źródło

- Główne: https://code.claude.com/docs/en/mcp.md (pobrane 2026-06-09)
- Quickstart: https://code.claude.com/docs/en/mcp-quickstart
- Managed MCP: https://code.claude.com/docs/en/managed-mcp
- Specyfikacja protokołu: https://modelcontextprotocol.io/introduction
- Katalog serwerów: https://claude.ai/directory
