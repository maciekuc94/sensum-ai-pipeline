# Pamięć w Claude Code — CLAUDE.md i auto memory

> Referencja „jak działa i jak utrzymywać system pamięci". Źródło: https://code.claude.com/docs/en/memory.md
> (pobrane 2026-06-09). Nazwy plików, składnia importów, komendy i bloki kodu zostawione **verbatim**
> po angielsku — to kontrakt z harnessem. Proza wyjaśniająca po polsku.

---

## Co to jest i po co

Każda sesja Claude Code startuje z pustym oknem kontekstu. Dwa mechanizmy przenoszą wiedzę między
sesjami:

- **CLAUDE.md** — pliki instrukcji, które _Ty_ piszesz; ładowane na starcie każdej sesji.
- **Auto memory** — notatki, które _Claude_ sam zapisuje na podstawie Twoich korekt i preferencji.

| | CLAUDE.md | Auto memory |
|---|---|---|
| **Kto pisze** | Ty | Claude |
| **Co zawiera** | Instrukcje i reguły | Wnioski i wzorce |
| **Zasięg** | Projekt, user lub org | Per-repo, wspólne dla worktrees |
| **Ładowane** | W każdej sesji (w całości) | W każdej sesji (pierwsze 200 linii / 25 KB) |
| **Do czego** | Standardy kodu, workflows, architektura | Komendy build, debugowanie, preferencje odkryte przez Claude |

**Ważne:** CLAUDE.md to kontekst, nie wymuszenie. Claude traktuje go jak instrukcję, którą stara się
realizować — ale nie ma gwarancji ścisłego przestrzegania, zwłaszcza przy niejasnych lub sprzecznych
regułach. Jeśli potrzebujesz twardego wymuszenia (np. zablokuj komendę bezwarunkowo), użyj
[hooka `PreToolUse`](/en/hooks-guide).

---

## Hierarchia plików pamięci i precedencja

Pliki ładowane są **w kolejności od najszerszego zasięgu do najbardziej szczegółowego** — instrukcje
bliżej katalogu roboczego czytane są **po** tych z góry, czyli mają wyższy priorytet w kontekście.

| Poziom | Lokalizacja | Zasięg | Commitować? |
|---|---|---|---|
| **Managed policy** | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`<br>Linux/WSL: `/etc/claude-code/CLAUDE.md`<br>Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Wszystkie sesje na maszynie (org-wide) | Zarządza IT/DevOps (MDM/GPO) |
| **User** | `~/.claude/CLAUDE.md` | Wszystkie Twoje projekty | Nie (prywatne) |
| **Project** | `./CLAUDE.md` lub `./.claude/CLAUDE.md` | Cały projekt, widoczne dla zespołu | **Tak** |
| **Local** | `./CLAUDE.local.md` | Bieżący projekt, prywatne | **Nie** (dodaj do `.gitignore`) |

Dodatkowe lokalizacje w ramach projektu:
- `.claude/rules/*.md` — reguły tematyczne (opcjonalnie z `paths:` frontmatter, patrz niżej).
- `~/.claude/rules/` — user-level rules (ładowane przed project rules → niższy priorytet).

**Managed policy nie może być wykluczona** przez indywidualne ustawienia — zawsze wchodzi do kontekstu.

### Kolejność w kontekście

Dla katalogu roboczego `foo/bar/` Claude ładuje (w tej kolejności):
1. Managed policy
2. `~/.claude/CLAUDE.md` (user)
3. `~/.claude/rules/` (user-level rules)
4. `foo/CLAUDE.md` (ancestor)
5. `foo/CLAUDE.local.md`
6. `foo/bar/CLAUDE.md` (project root)
7. `foo/bar/.claude/CLAUDE.md`
8. `foo/bar/.claude/rules/` (project rules bez `paths:`)
9. `foo/bar/CLAUDE.local.md`

Pliki z podkatalogów (poniżej cwd) **nie ładują się na starcie** — trafiają do kontekstu dopiero gdy
Claude odczyta plik w tym podkatalogu (lazy-load).

---

## Jak Claude ładuje pliki

Claude Code chodzi **w górę drzewa katalogów** od bieżącego cwd, sprawdzając każdy katalog
pod kątem `CLAUDE.md` i `CLAUDE.local.md`. Wszystkie znalezione pliki są **konkatenowane w kontekście**
(nie nadpisują się). W obrębie jednego katalogu `CLAUDE.local.md` jest dołączany **po** `CLAUDE.md`
(prywatne notatki są ostatnie w tym poziomie).

Pliki w podkatalogach poniżej cwd ładują się **leniwie** (lazy-load): wchodzą do kontekstu
dopiero w momencie, gdy Claude czyta pliki w danym podkatalogu.

### `--add-dir` i dodatkowe katalogi

Domyślnie flaga `--add-dir` daje Claude dostęp do dodatkowych katalogów, ale **nie ładuje** ich
CLAUDE.md. Żeby je załadować:

```bash
CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 claude --add-dir ../shared-config
```

Ładuje wtedy `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` i `CLAUDE.local.md`
z dodatkowego katalogu.

### Wykluczanie plików — `claudeMdExcludes`

W dużych monorepo inne zespoły mogą mieć swoje CLAUDE.md, które Claude niepotrzebnie wciągnie.
Wyklucz je przez `.claude/settings.local.json` (ustawiaj lokalnie, nie commituj):

```json
{
  "claudeMdExcludes": [
    "**/monorepo/CLAUDE.md",
    "/home/user/monorepo/other-team/.claude/rules/**"
  ]
}
```

Wzorce dopasowywane do ścieżek absolutnych (glob syntax). Można ustawiać na każdym poziomie
settingsów (user/project/local/policy) — tablice mergowane.

### Komentarze HTML w CLAUDE.md

Block-level komentarze HTML (`<!-- maintainer notes -->`) są **usuwane przed wstrzyknięciem** do
kontekstu — nie kosztują tokenów. Przydatne do zostawiania notatek dla ludzi bez obciążania sesji.
W blokach kodu komentarze są **zachowywane**.

---

## Importy — `@path/to/file`

CLAUDE.md może importować inne pliki. Importowane pliki **są rozwijane i ładowane do kontekstu na
starcie** (nie lazy-load, mimo że to osobne pliki).

```text
See @README for project overview and @package.json for available npm commands for this project.

# Additional Instructions
- git workflow @docs/git-instructions.md
```

**Zasady:**
- Ścieżki względne rozwiązywane względem **pliku zawierającego import** (nie cwd).
- Ścieżki absolutne i `~/` też działają.
- Rekurencja: importowany plik może importować kolejne — **maksymalna głębokość 4 hopy**.
- Importy w blokach kodu (` ``` `) **NIE są przetwarzane** — Claude traktuje je literalnie.
- Przy pierwszym napotkaniu zewnętrznych importów w projekcie Claude pokazuje **dialog
  zatwierdzenia** — odrzucenie blokuje importy na stałe (dialog już się nie pojawi).

**Przykład — współdzielone instrukcje dla worktrees** (import z home dir zamiast `CLAUDE.local.md`,
który istnieje tylko w jednym worktree):

```text
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

**Importy nie redukują kontekstu** — split CLAUDE.md na wiele plików z `@` pomoże w organizacji,
ale wszystkie trafiają do okna kontekstu i tak.

---

## `CLAUDE.local.md` — prywatne notatki

Plik `CLAUDE.local.md` w katalogu projektu to miejsce na Twoje lokalne preferencje, które nie
powinny wejść do repozytorium: URL środowiska sandbox, testowe dane, osobiste skróty.

- Ładuje się **obok** `CLAUDE.md` (po nim, w tym samym katalogu).
- Dodaj `CLAUDE.local.md` do `.gitignore` — `/init` robi to automatycznie przy wyborze opcji
  „personal".
- Istnieje tylko w danym worktree — jeśli pracujesz na kilku worktrees i chcesz współdzielić
  prywatne instrukcje, importuj plik z home dir: `@~/.claude/my-project-instructions.md`.

---

## Reguły tematyczne — `.claude/rules/`

Dla większych projektów możesz rozbić instrukcje na pliki tematyczne. Każdy plik powinien pokrywać
jeden temat (`testing.md`, `api-design.md`). Pliki odkrywane rekurencyjnie — można porządkować
w podfolderach (`frontend/`, `backend/`).

```text
your-project/
├── .claude/
│   ├── CLAUDE.md           # Główne instrukcje projektu
│   └── rules/
│       ├── code-style.md   # Konwencje kodu
│       ├── testing.md      # Konwencje testów
│       └── security.md     # Wymagania bezpieczeństwa
```

Reguły **bez frontmatter** ładują się na starcie z takim samym priorytetem jak `.claude/CLAUDE.md`.

### Reguły path-scoped (warunkowe)

Reguły z `paths:` w YAML frontmatter ładują się **tylko gdy Claude pracuje z pasującymi plikami**
— zmniejsza to szum i oszczędza kontekst:

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

Reguły bez `paths` ładują się bezwarunkowo. Reguły path-scoped są wyzwalane gdy Claude **czyta
pliki** pasujące do wzorca (nie przy każdym wywołaniu narzędzia).

Wzorce glob w `paths`:

| Wzorzec | Pasuje do |
|---|---|
| `**/*.ts` | Wszystkie pliki `.ts` w każdym katalogu |
| `src/**/*` | Wszystkie pliki w `src/` |
| `*.md` | Pliki Markdown w katalogu głównym |
| `src/components/*.tsx` | Komponenty React w konkretnym katalogu |
| `src/**/*.{ts,tsx}` | TypeScript i TSX wszędzie w `src/` |

### Symlinki w `.claude/rules/`

Katalog obsługuje symlinki — możesz utrzymywać wspólny zestaw reguł i linkować do wielu projektów:

```bash
ln -s ~/shared-claude-rules .claude/rules/shared
ln -s ~/company-standards/security.md .claude/rules/security.md
```

---

## Bootstrap — `/init`

Uruchom `/init` w repo, żeby wygenerować startowy CLAUDE.md automatycznie. Claude analizuje
codebase i tworzy plik z komendami build, instrukcjami testów i konwencjami, które odkryje.
Jeśli CLAUDE.md już istnieje, `/init` proponuje ulepszenia zamiast nadpisywać.

Tryb interaktywny (fazy: CLAUDE.md + skills + hooks):

```bash
CLAUDE_CODE_NEW_INIT=1 claude
# następnie: /init
```

Przy `/init` w repo z istniejącym `AGENTS.md` — odczytuje go i wbudowuje istotne fragmenty w
wygenerowany CLAUDE.md. Czyta też `.cursorrules`, `.devin/rules/`, `.windsurfrules`.

---

## Komenda `/memory` — przegląd i edycja

`/memory` wylistowuje wszystkie załadowane pliki CLAUDE.md, CLAUDE.local.md i rules, pozwala
przełączyć auto memory i daje link do folderu auto memory. Wybierz plik, żeby otworzyć go
w edytorze.

Żeby dodać instrukcje przez rozmowę:
- „add this to CLAUDE.md" → Claude edytuje plik CLAUDE.md.
- „always use pnpm, not npm" → Claude zapisuje do auto memory.

---

## Auto memory

Auto memory to mechanizm, w którym Claude sam zapisuje notatki między sesjami: komendy build,
wnioski z debugowania, konwencje kodu, preferencje workflow. Claude **nie zapisuje czegoś przy
każdej sesji** — decyduje, co warto zapamiętać na podstawie przydatności w przyszłości.

Wymaga Claude Code v2.1.59+. Sprawdź wersję: `claude --version`.

### Lokalizacja

```text
~/.claude/projects/<project>/memory/
├── MEMORY.md          # Skrócony indeks, ładowany do każdej sesji
├── debugging.md       # Szczegółowe notatki o debugowaniu
├── api-conventions.md # Decyzje projektowe API
└── ...                # Inne pliki tematyczne tworzone przez Claude
```

Ścieżka `<project>` pochodzi z repozytorium git — wszystkie worktrees i podkatalogi tego samego
repo **współdzielą jeden katalog auto memory**. Auto memory jest **lokalne dla maszyny** (nie
synchronizuje się między maszynami).

### Co ładuje się do sesji

Pierwsze **200 linii** `MEMORY.md` albo pierwsze **25 KB** (co nastąpi pierwsze) — ładowane na
start każdej sesji. Claude utrzymuje `MEMORY.md` jako zwięzły indeks, przenosząc szczegóły do
osobnych plików tematycznych. Te pliki tematyczne (`debugging.md` itd.) **nie ładują się na
starcie** — Claude czyta je na żądanie w trakcie sesji.

Limit 200 linii/25 KB dotyczy **tylko** `MEMORY.md`. CLAUDE.md ładuje się w całości.

### Włączanie i wyłączanie

Auto memory jest **domyślnie włączone**. Wyłącz przez `/memory` (toggle) albo przez settings:

```json
{
  "autoMemoryEnabled": false
}
```

Przez zmienną środowiskową: `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`.

Niestandardowa lokalizacja (wartość musi być ścieżką absolutną lub zaczynać od `~/`):

```json
{
  "autoMemoryDirectory": "~/my-custom-memory-dir"
}
```

---

## Najlepsze praktyki pisania CLAUDE.md

### Kiedy dodawać do CLAUDE.md

Traktuj CLAUDE.md jako miejsce na to, co musiałbyś wyjaśniać od nowa. Dodawaj gdy:
- Claude popełnia ten sam błąd po raz drugi.
- Code review wyłapuje coś, co Claude powinien wiedzieć o tym codebase.
- Wpisujesz tę samą korektę w czat, którą wpisałeś poprzedniej sesji.
- Nowy member teamu potrzebowałby tego kontekstu, żeby być produktywny.

Zachowaj fakty, które Claude powinien mieć **w każdej sesji**: komendy build, konwencje, layout
projektu, reguły „zawsze rób X". Wieloetapowe procedury lub reguły ważne tylko dla fragmentu
codebase → przenieś do Skills lub path-scoped rules.

### Rozmiar

Celuj w **mniej niż 200 linii** na plik CLAUDE.md. Dłuższe pliki konsumują więcej kontekstu
i obniżają przestrzeganie. Jeśli plik rośnie:
- Użyj path-scoped rules (`.claude/rules/` z `paths:`) — ładują się tylko przy pasujących plikach.
- Podziel przez importy `@` — pomaga w organizacji, ale **nie redukuje kontekstu** (wszystko
  wchodzi do okna na starcie).

### Struktura

Używaj nagłówków i punktorów Markdown do grupowania powiązanych instrukcji. Claude skanuje
strukturę tak samo jak czytelnicy — zorganizowane sekcje są łatwiejsze do realizacji niż gęste
akapity.

### Konkretność

Pisz instrukcje na tyle konkretne, żeby można było je zweryfikować:

| Zamiast | Napisz |
|---|---|
| „Format code properly" | „Use 2-space indentation" |
| „Test your changes" | „Run `npm test` before committing" |
| „Keep files organized" | „API handlers live in `src/api/handlers/`" |

### Spójność

Dwie sprzeczne reguły → Claude może wybrać jedną arbitralnie. Przeglądaj CLAUDE.md, zagnieżdżone
pliki i `.claude/rules/` regularnie — usuwaj przestarzałe lub konfliktujące instrukcje.
W monorepo: `claudeMdExcludes` wyklucza pliki innych zespołów.

### Rozdzielanie reguł od historii

Dobra praktyka (stosowana w tym repo):
- **CLAUDE.md** → reguły operacyjne (architektura, standardy, „zawsze rób X"), wiążące dla każdej
  sesji i każdego agenta.
- **Auto memory** (`project_*.md` itp.) → „dlaczego/historia", wnioski z poprzednich sesji,
  kontekst decyzji — lazy-loaded, nie obciąża kontekstu na starcie.
- **workflows/guides/** i **workflows/pipeline/** → pełne specyfikacje i SOPy — ładowane na
  żądanie przez Skills lub importy, gdy potrzebne.

To trójwarstwowe rozdzielenie pozwala utrzymać CLAUDE.md zwięzłym, nie gubiąc wiedzy.

---

## Pełny przykład CLAUDE.md z importami

```markdown
# Mój projekt

## Build i test
- Build: `npm run build`
- Test: `npm test` (zawsze przed commitem)
- Lint: `npm run lint`

## Architektura
@docs/architecture-overview.md

## Konwencje kodu
- 2-space indentation
- API handlers: `src/api/handlers/`
- Typy: `src/types/`
- Testy obok pliku: `*.test.ts`

## Git workflow
@docs/git-instructions.md

## Prywatne (tylko lokalne — nie commituj tego bloku, przenieś do CLAUDE.local.md)
# - Mój sandbox: http://localhost:3001
```

Przykład importu AGENTS.md (jeśli repo używa innych agentów):

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

---

## Kontekst tego projektu (SENSUM pipeline)

Główny `CLAUDE.md` tego repo (ścieżka: `D:\ClaudeCode\YouTube psychology\CLAUDE.md`) stosuje
opisany powyżej układ:

- **CLAUDE.md** trzyma reguły operacyjne: architektura WAT, doktryna głosu, zasady obrazów,
  konwencje potoków — wiążące dla każdej sesji.
- **Auto memory** (`project_*.md`, lazy-loaded przez `/memory`) trzyma „dlaczego/historię"
  za każdą decyzją — kontekst rationale bez zaśmiecania kontekstu startowego.
- **`workflows/guides/`** i **`workflows/pipeline/`** — pełne specyfikacje i SOPy, ładowane
  przez Skills lub agenty na żądanie.

Jeśli CLAUDE.md rośnie: wytnij sekcje rationale do auto memory (plik `project_<temat>.md`
w `~/.claude/projects/.../memory/`), zostaw tylko operacyjny destylat.

Importy `@` warto stosować gdy instrukcje odnoszą się do istniejącej specyfikacji w
`workflows/guides/` — zamiast duplikować treść, zaimportuj źródło. Pamiętaj, że importy
i tak wchodzą do kontekstu na starcie, więc nie stosuj ich do rzadko potrzebnych treści.

---

## Gotchas i pułapki

- **CLAUDE.md to kontekst, nie enforcement.** Jeśli reguła musi być bezwzględna (np. blokada
  komendy), zrób z niej hook `PreToolUse`.
- **Importy `@` w blokach kodu nie działają** — Claude traktuje je literalnie, nie rozwijane.
- **Importy nie redukują kontekstu** — wszystkie importowane pliki wchodzą do okna na starcie.
- **Po `/compact` nie-rootowe CLAUDE.md nie są re-injectowane automatycznie** — dopiero gdy
  Claude znowu odczyta plik w danym podkatalogu. Jeśli instrukcja zaginęła po `/compact`,
  żyła tylko w rozmowie lub w zagnieżdżonym pliku — przenieś ją do CLAUDE.md w root projektu.
- **Limity auto memory:** tylko pierwsze 200 linii / 25 KB `MEMORY.md` wchodzi do kontekstu.
  Claude utrzymuje `MEMORY.md` jako indeks i przenosi szczegóły do plików tematycznych —
  pliki tematyczne nie ładują się na starcie.
- **Auto memory jest lokalne** (maszyna-specyficzne) — nie synchronizuje się między środowiskami.
- **Approval dialog dla importów** — pierwsze napotkanie importu z zewnątrz projektu wymaga
  zatwierdzenia; odrzucenie blokuje go permanentnie.
- **Managed policy CLAUDE.md nie da się wykluczyć** przez `claudeMdExcludes`.
- **`CLAUDE.local.md` w worktree** — istnieje tylko w tym worktree gdzie go stworzysz; jeśli
  pracujesz na wielu worktrees, użyj importu `@~/.claude/my-project-instructions.md`.
- **Subagenci też ładują CLAUDE.md** (z wyjątkiem Explore i Plan, które go pomijają dla
  szybkości). Reguła, która musi dotrzeć do subagenta, musi być w CLAUDE.md albo w prompcie
  delegującym.

---

*Źródło: https://code.claude.com/docs/en/memory.md — pobrane 2026-06-09.*
