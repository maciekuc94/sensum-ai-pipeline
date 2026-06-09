# Agent Skills w Claude Code — kompletna instrukcja tworzenia

> Referencja „jak dobrze stworzyć skill". Źródło: https://code.claude.com/docs/en/skills.md
> (pobrane 2026-06-09). Pola/nazwy narzędzi/bloki kodu zostawione **verbatim** po angielsku — to kontrakt
> z harnessem, nie tłumacz ich. Proza wyjaśniająca po polsku.

---

## Czym jest skill (i czym różni się od slash command / subagenta)

**Skill** to plik `SKILL.md` z instrukcjami — Claude dostaje go do zestawu narzędzi i może go załadować
automatycznie, gdy uzna to za właściwe, albo możesz wywołać go ręcznie przez `/nazwa-skilla`.

Stwórz skill, gdy:
- wklejasz te same instrukcje, checklistę lub procedurę wielokrotnie w czat;
- fragment `CLAUDE.md` urósł do procedury — lepiej wyciąć go do skilla (treść skilla ładuje się **tylko
  gdy używany**, nie za każdym razem jak `CLAUDE.md`);
- chcesz, by Claude **sam** wychwytywał sytuacje i stosował reguły bez Twojej jawnej prośby (doctrine
  guards, guardrails jakości).

### Trzy narzędzia — kiedy co wybrać

| Sytuacja | Narzędzie |
|---|---|
| Powtarzalny prompt/workflow **w kontekście głównej rozmowy**, Claude ma sam wiedzieć kiedy | **Skill** (`SKILL.md`, auto-invocation przez `description`) |
| Wielokrotnie spawnujesz tego samego workera, wynik wraca jako podsumowanie, nie śmieci głównego kontekstu | **Subagent** (`.claude/agents/AGENT.md`) |
| Kilkukrokowa procedura wywoływana tylko ręcznie przez `/komendę`, stały flow | **Slash command** (`.claude/commands/deploy.md`) |

**Kluczowa różnica skill vs slash command:** custom commands zostały połączone ze skills — plik
`.claude/commands/deploy.md` i `.claude/skills/deploy/SKILL.md` dają ten sam `/deploy` i działają
identycznie. Skills mają jednak dodatkowe możliwości: katalog z plikami pomocniczymi, frontmatter
sterujący tym, kto wywołuje skill (Ty vs Claude), oraz **auto-invocation** — Claude może załadować skill
automatycznie, gdy uzna go za właściwy (slash command tego nie robi).

**Kluczowa różnica skill vs subagent:** skill działa **w kontekście głównej rozmowy** — widzi historię,
wynik zostaje inline. Subagent startuje ze świeżym, izolowanym kontekstem; do rozmowy wraca tylko
podsumowanie. Skill z `context: fork` łączy obie opcje: działa jak subagent (forked context), ale
definiujesz go jak skill.

Skills w Claude Code implementują otwarty standard [Agent Skills](https://agentskills.io), działający
w wielu narzędziach AI. Claude Code rozszerza standard o: invocation control, subagent execution i
dynamic context injection.

---

## Struktura pliku i lokalizacja

Każdy skill to **katalog** z plikiem `SKILL.md` jako punktem wejściowym. Nazwa katalogu staje się
komendą do wpisania po `/`.

```text
.claude/skills/
└── deploy-staging/
    ├── SKILL.md           # główne instrukcje (wymagany)
    ├── reference.md       # szczegółowa dokumentacja API — ładowana na żądanie
    ├── examples.md        # przykłady — ładowane na żądanie
    └── scripts/
        └── helper.py      # skrypt wykonywany, nie ładowany do kontekstu
```

Plik `SKILL.md` powinien mieć **poniżej 500 linii**. Obszerny materiał referencyjny przenoś do osobnych
plików w katalogu skilla i linkuj je z `SKILL.md`, by Claude wiedział co gdzie znajdzie.

### Gdzie żyją skills — zasięg i pierwszeństwo

| Lokalizacja | Ścieżka | Zasięg |
|---|---|---|
| Enterprise | managed settings | wszyscy użytkownicy organizacji (najwyższy priorytet) |
| Personal | `~/.claude/skills/<nazwa>/SKILL.md` | wszystkie Twoje projekty |
| Project | `.claude/skills/<nazwa>/SKILL.md` | tylko ten projekt |
| Plugin | `<plugin>/skills/<nazwa>/SKILL.md` | gdzie plugin jest włączony |

Przy kolizji nazw: enterprise bije personal, personal bije project. Skille z pluginów używają przestrzeni
nazw `plugin-name:skill-name` — nie mogą kolidować z innymi poziomami.

**Automatyczne wykrywanie z katalogów nadrzędnych i podkatalogów.** Claude Code ładuje skills z
`.claude/skills/` w katalogu startowym i we wszystkich katalogach nadrzędnych aż do roota repo. Obsługuje
też monorepo: gdy edytujesz pliki w `packages/frontend/`, Claude Code szuka skills w
`packages/frontend/.claude/skills/`. W `.claude/skills/` pliki `.claude/commands/` nadal działają — przy
kolizji nazwy skill ma pierwszeństwo.

**Wykrywanie zmian na żywo.** Skill dodany lub edytowany w czasie sesji jest wykrywany automatycznie —
nie trzeba restartować (w odróżnieniu od subagentów).

**Skills z dodatkowych katalogów.** Dodaj ścieżki w `settings.json`:
```json
{
  "additionalSkillDirectories": ["/shared/team-skills", "~/my-skills"]
}
```

---

## Anatomia SKILL.md

```yaml
---
name: deploy-staging
description: Deploy the application to the staging environment. Use when the user asks
  to deploy, push to staging, or test a release. DISTINCT from /deploy-production.
when_to_use: "trigger phrases: deploy to staging, push to staging, release to test env, wdróż na staging"
disable-model-invocation: true
allowed-tools: Bash(./scripts/deploy.sh *) Bash(git *)
context: fork
---

Deploy $ARGUMENTS to staging:

1. Run the test suite
2. Build the application
3. Push to the staging target
4. Verify the deployment succeeded
```

- **Frontmatter** = YAML między `---` markers — metadane i konfiguracja.
- **Ciało Markdown** = instrukcje, które Claude wykonuje po wywołaniu skilla.
- Treść skilla wchodzi do rozmowy jako jedna wiadomość i **zostaje w kontekście przez całą sesję** (każda
  linia to koszt tokenów przez kolejne tury). Pisz konkretnie — co robić, nie dlaczego.

---

## Pełna tabela pól frontmatter

Wszystkie pola są opcjonalne. Tylko `description` jest **zalecane** — bez niego Claude nie wie, kiedy
skilla użyć.

| Pole | Wym. | Opis |
|---|---|---|
| `name` | Nie | Etykieta wyświetlana w listingach skills. Domyślnie = nazwa katalogu. **Nie zmienia** komendy do wpisania (wyjątek: plugin-root `SKILL.md`, gdzie `name` ustawia też komendę). |
| `description` | Zalecane | Co skill robi i kiedy go użyć. **Claude decyduje o auto-wywołaniu wyłącznie na podstawie tego pola.** Jeśli pominięty — używany jest pierwszy akapit treści. Łączony tekst `description` + `when_to_use` obcinany do **1 536 znaków** w listingu skills. |
| `when_to_use` | Nie | Dodatkowy kontekst kiedy Claude powinien wywołać skill — triggery, przykładowe frazy, scenariusze. Dołączany do `description` w listingu i wlicza się do limitu 1 536 znaków. |
| `argument-hint` | Nie | Podpowiedź w autocomplete wskazująca oczekiwane argumenty. Przykład: `[issue-number]` lub `[filename] [format]`. |
| `arguments` | Nie | Nazwane argumenty pozycyjne dla `$name` substitution w treści skilla. String rozdzielony spacjami lub lista YAML. Nazwy mapują się na pozycje w kolejności. |
| `disable-model-invocation` | Nie | `true` → tylko Ty możesz wywołać skill (znika z kontekstu Claude). Dla workflows z side-effects (`/commit`, `/deploy`, `/send-slack-message`). Zapobiega też preloadowaniu do subagentów. Domyślnie: `false`. |
| `user-invocable` | Nie | `false` → ukrywa skill z menu `/`. Dla wiedzy tła, której user nie powinien wywoływać bezpośrednio. Domyślnie: `true`. |
| `allowed-tools` | Nie | Narzędzia, z których Claude może korzystać bez pytania o zgodę, gdy skill jest aktywny. String rozdzielony spacją lub przecinkiem, albo lista YAML. Nie ogranicza dostępności — pozostałe narzędzia są nadal wywoływalne. |
| `disallowed-tools` | Nie | Narzędzia usuwane z dostępnej puli, gdy skill jest aktywny. Ograniczenie znika po następnej wiadomości. |
| `context` | Nie | `fork` → skill działa w izolowanym subagent context (nie widzi historii rozmowy). Treść `SKILL.md` staje się promptem napędzającym subagenta. |
| `agent` | Nie | Typ agenta dla `context: fork` (np. `Explore`, `Plan`). Explore i Plan pomijają `CLAUDE.md` i git status — lekkie, tanie. |

### Jak skill dostaje komendę (źródło nazwy)

| Lokalizacja skilla | Źródło nazwy komendy | Przykład |
|---|---|---|
| Katalog w `~/.claude/skills/` lub `.claude/skills/` | Nazwa katalogu | `.claude/skills/deploy-staging/SKILL.md` → `/deploy-staging` |
| Plik w `.claude/commands/` | Nazwa pliku bez rozszerzenia | `.claude/commands/deploy.md` → `/deploy` |
| Podkatalog `skills/` w pluginie | Nazwa katalogu, z namespace pluginu | `my-plugin/skills/review/SKILL.md` → `/my-plugin:review` |
| Plugin-root `SKILL.md` | Pole `name` z frontmatter (fallback: nazwa katalogu pluginu) | `my-plugin/SKILL.md` z `name: review` → `/my-plugin:review` |

### Tabela invocation — kto wywołuje, kiedy ładowany

| Frontmatter | Ty możesz | Claude może | Kiedy ładowany do kontekstu |
|---|---|---|---|
| (domyślnie) | Tak | Tak | Opis zawsze w kontekście; pełna treść po wywołaniu |
| `disable-model-invocation: true` | Tak | Nie | Opis **poza** kontekstem; pełna treść po Twoim wywołaniu |
| `user-invocable: false` | Nie | Tak | Opis zawsze w kontekście; pełna treść po wywołaniu |

> **Uwaga o subagentach.** W normalnej sesji Claude widzi tylko opisy skills (progressive disclosure).
> Subagent z polem `skills:` w frontmatter dostaje **pełną treść** wymienionych skills przy starcie —
> nie ma progressive disclosure. Skills z `disable-model-invocation: true` nie mogą być preloadowane.

---

## Progressive disclosure i lifecycle treści

**Progressive disclosure** oznacza, że Claude widzi stale tylko **opisy** skills (skrócone do 1 536
znaków), nie ich pełną treść. Pełna treść ładuje się dopiero po wywołaniu — do tej pory kosztuje
praktycznie nic. Dlatego długi materiał referencyjny opłaca się trzymać w skillach zamiast w `CLAUDE.md`.

**Po wywołaniu:** treść `SKILL.md` wchodzi do rozmowy jako jedna wiadomość i **zostaje w kontekście przez
całą sesję** — Claude Code nie rereadsuje pliku w kolejnych turach. Każda linia to stały koszt tokenów.

**Auto-kompakcja.** Gdy rozmowa jest kompaktowana, Claude Code reattachuje najnowsze wywołanie każdego
skilla po podsumowaniu (pierwsze 5 000 tokenów skilla; łączny budżet 25 000 tokenów dla wszystkich
skills, od najnowiej wywołanego). Starsze skills mogą zostać całkowicie odrzucone. Jeśli skill przestał
wpływać na zachowanie — wywołaj go ponownie po kompakcji.

**Pliki pomocnicze** (`reference.md`, `examples/`, `scripts/`) są ładowane na żądanie przez Claude
(gdy ich potrzebuje i gdy `SKILL.md` na nie wskazuje) — nie wchodzą do kontekstu automatycznie.

---

## Jak pisać `description` — triggering i granice

`description` to jedyna rzecz, na podstawie której Claude decyduje o auto-wywołaniu. Złe `description`
= skill się nie odpala albo odpala się za często.

### Zasady pisania dobrego `description`

1. **Klucz użycia na początku.** Łączny tekst jest obcinany do 1 536 znaków — to, co najważniejsze,
   musi być pierwsze.
2. **Słowa kluczowe, które użytkownik naturalnie powie.** Claude szuka dopasowania między prośbą
   użytkownika a opisem. Pisz od strony wyzwalacza, nie od strony implementacji.
3. **Tryggery jawne + `when_to_use` na frazy.** W `description` — ogólna sytuacja; w `when_to_use` —
   konkretne frazy (po polsku i angielsku, jeśli użytkownik mówi w obu językach).
4. **Wyraźne granice — `DISTINCT from`.** Jeśli masz dwa podobne skills, napisz explicite, czym się
   różnią: `DISTINCT from /deploy-production`. Bez tego Claude będzie mylił się między nimi.
5. **Zwężaj, gdy odpala się za często.** Jeśli skill odpala się kiedy nie trzeba — dodaj
   `disable-model-invocation: true` (tylko wywołanie ręczne) albo zrób opis bardziej konkretnym.
6. **Doctrine guards: "Use when about to…".** Dla guardrails (styl, głos, QA) użyj frazy
   `Use when about to [ACTION]` + lista sytuacji + wyraźna granica `OUTSIDE the /command commands`.

### Przykład — dobry `description` dla doctrine guard

```yaml
description: Use when about to generate, render, write prompts for, or describe ANY image,
  thumbnail, channel banner, chart, diagram, or slide for this project (also when the user
  uses Polish terms like obrazek, grafika, miniaturka, wykres) — especially ad-hoc/freeform
  requests made OUTSIDE the /visuals and /package commands. Loads the binding style contract
  so the first attempt is on-brand instead of drifting.
```

### Przykład — dobry `description` dla natural-language router

```yaml
description: Use when about to write, rewrite, tighten, translate, or "improve" ANY spoken
  script prose OUTSIDE the /draft and /publish commands — freeform Polish requests like
  "napisz/przepisz/popraw akapit", "napisz inne intro", "przepisz zakończenie", "skróć ten
  fragment", or English "rewrite this paragraph / write a new opening".
when_to_use: "Polish triggers: napisz akapit, przepisz intro, popraw zakończenie, skróć fragment,
  napisz alternatywną wersję. English: rewrite this, write a new opening, tighten this section."
```

### Tabela patologii `description`

| Problem | Symptom | Naprawa |
|---|---|---|
| Za ogólny opis | Skill nie odpala się nigdy | Dodaj słowa kluczowe, które user powie naturalnie |
| Za szerokie granice | Odpala się przy każdej rozmowie | Zawęź do konkretnej sytuacji; dodaj `DISTINCT from` |
| Brak fraz PL | Skill nie odpala się na polskie prośby | Dodaj triggery PL w `when_to_use` |
| Dwa podobne skills | Claude miesza je lub wywołuje oba | Dodaj `DISTINCT from /drugi-skill` do obu |
| Opis za długi | Obcięty w listingu | Skróć do 1 536 znaków łącznie z `when_to_use` |

### Troubleshooting (z dokumentacji)

**Skill się nie odpala:**
1. Sprawdź, czy opis zawiera słowa kluczowe, które user naturalnie mówi.
2. Zweryfikuj, że skill pojawia się w `What skills are available?`.
3. Przeformułuj prośbę tak, by pasowała do opisu.
4. Wywołaj bezpośrednio `/nazwa-skilla`, jeśli jest `user-invocable`.

**Skill odpala się za często:**
1. Uczyń opis bardziej konkretnym.
2. Dodaj `disable-model-invocation: true`, jeśli chcesz tylko ręcznego wywołania.

**Opis obcięty w listingu:**
Skróć łączny tekst `description` + `when_to_use` do 1 536 znaków. Najważniejsze informacje (case,
kiedy używać) trzymaj na początku.

---

## Argumenty i string substitution

Argumenty przekazujesz po nazwie skilla: `/fix-issue 123` albo `/migrate-component SearchBar React Vue`.

### Tabela dostępnych substitutionów

| Zmienna | Opis |
|---|---|
| `$ARGUMENTS` | Wszystkie argumenty jako jeden string. Jeśli `$ARGUMENTS` nie ma w treści — argumenty doklejane są jako `ARGUMENTS: <wartość>` na końcu. |
| `$ARGUMENTS[N]` | Argument po 0-based indeksie. `$ARGUMENTS[0]` = pierwszy. |
| `$N` | Skrót dla `$ARGUMENTS[N]`. `$0` = pierwszy, `$1` = drugi. |
| `$name` | Nazwany argument zadeklarowany w polu `arguments` frontmatter. Pozycje w kolejności: `arguments: [issue, branch]` → `$issue` = arg0, `$branch` = arg1. |
| `${CLAUDE_SESSION_ID}` | ID bieżącej sesji. Dla logowania, plików sesyjnych. |
| `${CLAUDE_SKILL_DIR}` | Katalog zawierający `SKILL.md` skilla. W komendach bash injection — referencja do bundled scripts niezależna od cwd. |

Multi-word argumenty otaczaj cudzysłowem: `/my-skill "hello world" second` → `$0` = `hello world`,
`$1` = `second`. Żeby wstawić literalne `$` przed cyfrą lub `ARGUMENTS` — escaped: `\$1.00`.

```yaml
---
name: migrate-component
description: Migrate a UI component from one framework to another
arguments: [component, from_framework, to_framework]
---

Migrate the $component component from $from_framework to $to_framework.
Preserve all existing behavior and tests.
```

Wywołanie: `/migrate-component SearchBar React Vue`

---

## Dynamiczny kontekst (`!` injection)

Składnia `` !`<komenda>` `` uruchamia komendę shell **zanim treść skilla trafi do Claude**. Wynik zastępuje
placeholder — Claude dostaje gotowe dane, nie sam placeholder.

```yaml
---
name: summarize-changes
description: Summarizes uncommitted changes and flags anything risky. Use when the user
  asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice
such as missing error handling, hardcoded values, or tests that need updating. If the diff
is empty, say there are no uncommitted changes.
```

Jak działa injection:
1. Każde `` !`<komenda>` `` wykonywane natychmiast (przed tym, jak Claude cokolwiek zobaczy).
2. Wynik zastępuje placeholder w treści skilla jako plain text.
3. Claude dostaje gotowy prompt z danymi już wbudowanymi.

To **preprocessing** — Claude nie wykonuje komendy, tylko widzi wynik.

**Ważne ograniczenia:**
- Substitution działa raz po oryginalnym pliku. Wynik komendy nie jest reskanowany pod kolejne `!`
  placeholdery (brak wielokrotnych przejść).
- `!` musi być na początku linii lub bezpośrednio po spacji. `KEY=!`cmd`` — `!` po innym znaku → literalny
  tekst, komenda nie uruchomi się.
- Multi-line: użyj fenced code block otwartego z `` ```! ``

````markdown
## Environment
```!
node --version
npm --version
git status --short
```
````

**Wyłączenie** dla projektu: `"disableSkillShellExecution": true` w `settings.json` (każdy placeholder
zamieniany na `[shell command execution disabled by policy]`). Bundled i managed skills nie są tym
dotknięte.

> **Tip:** By wymusić głębsze rozumowanie w skilla — wstaw `ultrathink` gdziekolwiek w treść.

---

## Typy treści skills

### Treść referencyjna (wiedza stosowana inline)

Konwencje, wzorce, style guides, wiedza domenowa. Działa w rozmowie inline — Claude stosuje ją do
bieżącego zadania.

```yaml
---
name: api-conventions
description: API design patterns and conventions for this codebase
---

When writing API endpoints:
- Use RESTful naming conventions
- Return consistent error formats
- Include request validation
```

### Treść zadaniowa (krok-po-kroku akcja)

Deployments, commity, generowanie kodu. Zazwyczaj chcesz wywoływać je ręcznie przez `/nazwa`,
nie pozwolić, by Claude decydował sam. Dodaj `disable-model-invocation: true`.

```yaml
---
name: deploy
description: Deploy the application to production
context: fork
disable-model-invocation: true
---

Deploy the application:
1. Run the test suite
2. Build the application
3. Push to the deployment target
```

---

## Skills w subagentach (`context: fork`)

`context: fork` sprawia, że skill działa w izolowanym kontekście — **nie widzi historii rozmowy**.
Treść `SKILL.md` staje się promptem napędzającym subagenta.

```yaml
---
name: pr-summary
description: Summarize changes in a pull request
context: fork
agent: Explore
allowed-tools: Bash(gh *)
---

## Pull request context
- PR diff: !`gh pr diff`
- PR comments: !`gh pr view --comments`
- Changed files: !`gh pr diff --name-only`

## Your task
Summarize this pull request...
```

> **Ostrzeżenie.** `context: fork` ma sens tylko dla skills z konkretnymi instrukcjami zadaniowymi.
> Skill zawierający tylko wytyczne (np. „stosuj te konwencje API") bez zadania — subagent dostanie
> wytyczne, ale bez actionable prompt i wróci bez wyniku.

### Skills vs subagenty — dwa kierunki

| Podejście | System prompt | Zadanie | Ładuje też |
|---|---|---|---|
| Skill z `context: fork` | Z wybranego `agent` type | Treść `SKILL.md` | `CLAUDE.md`, chyba że agent to Explore lub Plan |
| Subagent z polem `skills` | Ciało Markdown subagenta | Wiadomość delegująca od Claude | Preloaded skills + `CLAUDE.md` |

**Explore i Plan pomijają `CLAUDE.md` i git status** — są lekkie i tanie; użyj ich, gdy skill potrzebuje
szybkiej analizy bez pełnych reguł projektu. Jeśli reguła **musi** dotrzeć do forked skill → przekaż ją
w prompcie delegującym.

**Preload skills do subagenta** (kierunek odwrotny): subagent z polem `skills:` w frontmatter dostaje
pełną treść wymienionych skills przy starcie. Bez tego pola subagent i tak może wywołać skills przez
`Skill` tool — ale nie mają ich w swoim promptcie startowym.

---

## Pełny przykład `SKILL.md` — kompletny verbatim

Skill do summaryzowania uncommitted changes z live git injection:

```yaml
---
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks
  what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you notice
such as missing error handling, hardcoded values, or tests that need updating. If the diff
is empty, say there are no uncommitted changes.
```

Ścieżka: `~/.claude/skills/summarize-changes/SKILL.md`

Wywołanie ręczne: `/summarize-changes`
Auto-invocation: Claude załaduje, gdy user zapyta „What did I change?" albo poprosi o commit message.

---

## Bundled skills (wbudowane)

Claude Code dołącza zestaw bundled skills dostępnych w każdej sesji, w tym `/code-review`, `/batch`,
`/debug`, `/loop`, `/claude-api`. W odróżnieniu od wbudowanych komend (które wykonują stałą logikę),
bundled skills są prompt-based: dają Claude szczegółowe instrukcje i pozwalają mu orkiestrować pracę
narzędziami. Wywołujesz je tak samo jak każdy skill — przez `/` i nazwę.

Pełna lista bundled skills oznaczona jest etykietą **Skill** w kolumnie Purpose w
[commands reference](https://code.claude.com/docs/en/commands).

---

## Dystrybucja i udostępnianie

| Zasięg | Jak |
|---|---|
| Projekt | Commituj `.claude/skills/` do version control |
| Plugin | Utwórz katalog `skills/` w pluginie |
| Organizacja | Wdróż przez managed settings |

**Plugin skills** używają namespace `plugin-name:skill-name` — nie mogą kolidować z innymi poziomami.
Dodaj `.claude-plugin/plugin.json` do katalogu skills, by załadować je jako plugin (może bundlować
agentów, hooks i MCP servers).

**Override widoczności z settings** (bez edycji pliku skilla): `/skills` w UI → zaznacz skill →
`Space` cykluje stany → `Enter` zapisuje do `.claude/settings.local.json`. Albo ręcznie:

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

| Wartość | Widoczny dla Claude | W menu `/` |
|---|---|---|
| `"on"` | Nazwa i opis | Tak |
| `"name-only"` | Tylko nazwa | Tak |
| `"user-invocable-only"` | Ukryty | Tak |
| `"off"` | Ukryty | Ukryty |

Plugin skills nie podlegają `skillOverrides` — zarządzaj nimi przez `/plugin`.

---

## Skills w projekcie SENSUM — kontekst i wzorce

Projekt używa dwóch typów skills w `.claude/skills/`:

### Typ 1: Doctrine guards (auto-invocation, user-invocable)

Odpalają się automatycznie, gdy Claude ma coś generować — strażnicy stylu marki.

- **`scientific-etching-guard`** — wychwytuje każde żądanie generowania/opisywania wizuali poza
  `/visuals` i `/package`; wstrzykuje kontrakt Scientific Etching (2 kolory, styl, no-text, no-frame,
  no-texture-in-prompt) przed pierwszą próbą.
- **`native-voice-guard`** — wychwytuje każdą wolną edycję prozy skryptu poza `/draft` i `/publish`;
  wstrzykuje kanon głosu SENSUM v2 (7 reguł) tak, by jednorazowe przepisanie nie dryfowało od głosu.

Kluczowe `description` pattern dla doctrine guard:
```
Use when about to [ACTION] [OBIEKT] OUTSIDE the [/komendy]. [Efekt: co skill wnosi].
```

### Typ 2: Natural-language routery (auto-invocation, user-invocable)

Łapią prośby po polsku i angielsku i kierują do właściwego agenta pipeline.

- **`render-images`** — freeform prośba o renderowanie obrazów → Agent 6
- **`write-script`** → `/draft`
- **`score-hook`** → Agent 4 hook gate
- **`package-thumbnail`** → `/package`
- **`publish-package`** → `/publish`

Kluczowe `description` pattern dla natural-language routera:
```
Use when [prośba PL/EN opisana z perspektywy usera]. [Triggery PL w when_to_use].
DISTINCT from [pokrewne komendy/skills].
```

### Szablon do skopiowania — doctrine guard

```yaml
---
name: my-style-guard
description: Use when about to [AKCJA] [OBIEKT] for this project — especially ad-hoc/freeform
  requests made OUTSIDE the /komenda1 and /komenda2 commands. Loads the binding [REGUŁA]
  contract so the first attempt is on-brand instead of drifting.
---

# My Style Guard

[Krótkie zdanie: co ten skill robi i dlaczego jest potrzebny]

## Non-negotiables (every [OBIEKT], no exceptions)
- **Reguła 1.** ...
- **Reguła 2.** ...

## If the user explicitly asks for something off-doctrine
User instructions outrank this skill. If the user *explicitly* wants [wyjątek]:
flag the conflict once ("[komunikat]?"), confirm, then proceed.

## Source of truth
- `CLAUDE.md` → "[sekcja]"
- `workflows/guides/[plik].md`

## What this skill does NOT do
[Granica — czego skill NIE zastępuje]
```

### Szablon do skopiowania — natural-language router

```yaml
---
name: my-router
description: Use when the user asks to [CZYNNOŚĆ] — Polish: "[fraza1]", "[fraza2]";
  English: "[phrase1]", "[phrase2]". DISTINCT from /inne-komendy (which does [co innego]).
when_to_use: "Polish triggers: [lista], [lista]. English triggers: [list], [list]."
---

# My Router

[Jedno zdanie opisu]

Run: `[komenda lub ścieżka do skryptu]`

## What this skill does
[Krótko: co uruchamia i z jakimi flagami]

## When NOT to use this skill
[Granica — kiedy użytkownik powinien użyć innej komendy]
```

---

## Gotchas (pułapki)

- **Zmiana pliku w sesji jest wykrywana od razu** (live detection) — inaczej niż subagenty, które
  wymagają restartu.
- **Treść wchodzi do kontekstu i zostaje tam przez całą sesję.** Każda linia to stały koszt tokenów.
  Ogranicz `SKILL.md` do ~500 linii; obszerny materiał → osobne pliki w katalogu.
- **Auto-kompakcja może odrzucić starszy skill.** Jeśli masz wiele skills i skill przestał wpływać na
  zachowanie — wywołaj go ponownie po kompakcji.
- **`context: fork` bez konkretnego zadania = pusty return.** Skill zawierający tylko wytyczne (bez
  akcji do wykonania) w forked context wróci bez wyniku.
- **`!` injection działa raz, bez re-skanowania.** Wynik nie jest sprawdzany pod kolejne placeholdery.
  `!` musi być na początku linii lub po spacji — nie po innym znaku.
- **`disable-model-invocation: true` blokuje też preload do subagentów.** Skill z tym polem nie może
  być wstrzyknięty do subagenta przez pole `skills:`.
- **`allowed-tools` wymaga workspace trust dialog** dla skills z `.claude/skills/` projektu. Uprawnienie
  bierze się z akceptacji dialogu, tak jak `allowedTools` w `.claude/settings.json`. Przeglądaj skills
  przed trustowaniem repo.
- **Dwa skills o tej samej nazwie na tym samym poziomie.** Nie ostrzega — jeden zostaje odrzucony
  po cichu (inaczej niż subagenty, ale ten sam wzorzec; pilnuj unikalności).
- **Skill z opisu niejednoznacznego.** Claude używa `description` do auto-trigger — jeśli opis jest
  zbyt ogólny, skill będzie się odpalał przy każdej rozmowie na dany temat. Dodaj `DISTINCT from`.

---

## Zasoby powiązane

- [Sub-agents](https://code.claude.com/docs/en/sub-agents) — delegacja z izolowanym kontekstem
- [Plugins](https://code.claude.com/docs/en/plugins) — pakowanie i dystrybucja skills
- [Hooks](https://code.claude.com/docs/en/hooks) — automatyzacja wokół eventów narzędzi
- [Commands reference](https://code.claude.com/docs/en/commands) — built-in commands i bundled skills
- [Permissions](https://code.claude.com/docs/en/permissions) — kontrola dostępu do narzędzi i skills
- [Debug your config](https://code.claude.com/docs/en/debug-your-config) — diagnoza gdy skill nie
  pojawia się lub nie triggeruje

---

*Źródło: https://code.claude.com/docs/en/skills.md — pobrane 2026-06-09.*
