# /package — Title ↔ Thumbnail Packaging Strategist — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a new in-session `/package` agent that designs 3 radically different "packaging" strategies (strategy name · title · thumbnail napis · visual concept) bound by a curiosity gap, renders 3 SENSUM-etching thumbnails, and feeds its titles to `/publish` — replacing the old `/thumbnails` agent entirely.

**Architecture:** `/package` runs in-session on Opus 4.8 (no API) after `/hook`, before `/publish`. It writes a human-facing strategy doc (`md/07_package.md`) plus render-ready prompts (`md/07_prompts.md`) in the exact `## Thumbnail N` format the **existing, unchanged** renderer (`tools/pipeline/agent7_thumbnails.py`) already parses — so zero Python logic changes. The chosen title flows to `/publish` STEP 1 via a backward-compatible read (falls back to generating 5 titles when `07_package.md` is absent). The napis is a Canva-overlay text proposal and never enters the render prompt (Scientific-Etching "no text in image" contract).

**Tech Stack:** Markdown SOPs (`workflows/pipeline/`) + Claude Code slash commands (`.claude/commands/`) + Agent-Teams agent config (`.claude/agents/`) + the existing Gemini Vertex AI renderer (Python, reused as-is). **No unit-test framework exists in this repo** — verification is artifact-based: run the command with `--no-render` (free), then assert on the written files + `grep` sweeps. Paid render is exercised once at the end.

**Execution note:** Repo is on `main`. Start by branching (`feat/package-agent`); commit per task; do NOT push or open a PR unless the user asks. Windows shell: prefix Python runs with `PYTHONIOENCODING=utf-8`.

---

### Task 0: Branch

- [ ] **Step 1: Create the feature branch**

Run:
```bash
git checkout -b feat/package-agent
```
Expected: `Switched to a new branch 'feat/package-agent'`

---

### Task 1: Write the `/package` SOP (the rulebook)

This is the single source of truth the command reads. Write it first.

**Files:**
- Create: `workflows/pipeline/07_package.md`

- [ ] **Step 1: Write the SOP file**

Create `workflows/pipeline/07_package.md` with exactly this content:

````markdown
# Agent — Package (Title ↔ Thumbnail Strategist) — in-session, Opus 4.8

## Objective
Produce **3 radically different "packaging" strategies** for a video — each a coherent **{strategy name · title · thumbnail napis · visual concept}** unit bound by a **curiosity gap** — then render one thumbnail per strategy (3 total) in the SENSUM Scientific-Etching style. Runs **in-session on Opus 4.8 (no API)**; the Python step only renders via Gemini.

This agent is the **successor to the old Agent 7 `/thumbnails`**. It owns the title↔thumbnail synergy the old split (titles in Agent 8, thumbnails in Agent 7) could never achieve.

## When to run
After `/hook` (script locked), **before `/publish`** — its titles feed Agent 8. **Manual agent — only when the user explicitly asks** (the default path renders 3 images = render credits + ~1.5 min).

## Inputs
- Script source, first that exists: `outputs/videos_pl/{slug}/docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`.
- `tools/utils.py` — `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` constants (copy verbatim into render prompts).
- `workflows/pipeline/08_publish.md` **STEP 1** — the canonical **title doctrine** (Identity Provocation, HARD BANS, ≤70 chars, no trailing period). Package titles obey it; this file does NOT restate it.

## Command
```bash
/package <slug>                 # 3 strategies + text, then render 3 thumbnails
/package <slug> --no-render     # 3 strategies + text only (free; unblocks /publish titles without spending credits)
```
Render step the command calls (no LLM):
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py "<slug>" --render --no-grain
```
Re-roll the winner after picking: `... --render --no-grain --indices N --count 3`.

## The 3-strategy contract

Generate exactly **3** strategies. Each attacks a **distinct psychological angle** on THIS script — pick the 3 best-fitting from the menu (like the script architecture selector), never 3 flavours of one angle:

- **Reframe neurobiologiczny** — the hidden mechanism beneath the symptom.
- **Uderzenie w mit** — overturns a belief the viewer holds as obvious.
- **Rozgrzeszenie lęku/winy** — names the hidden fear, lifts the guilt.
- **Paradoks** — two "opposite" things revealed as one.
- **Reframe tożsamości** — "to nie lenistwo, to alarm".

### 1 · Title — inherits the SENSUM doctrine
Each strategy's title obeys **08_publish.md STEP 1** in full (do not restate it — read it). Additional, package-only requirement: **the title must form a curiosity gap with its own napis** — the title names the symptom/experience; the napis points at the hidden cause/paradox/twist. Title and napis NEVER say the same thing. ≤70 chars, natural spoken Polish, no trailing period.

### 2 · Napis (Canva overlay) — the new rule
- **2–3 words, ALL CAPS.** Smartphone test: legible as a postage stamp.
- **Never restates the title.** It is the other half of the gap — the provocation / hidden cause (title „Czujesz, że jesteś w tyle?" → napis „ZEGAR KŁAMIE").
- **SENSUM taste, not tabloid.** Same clickbait ban-list as titles (no „SZOK", „SEKRET", „NIE UWIERZYSZ", „SZOKUJĄCA PRAWDA", neon-arrow energy). An artful metaphoric jolt.
- **Never goes into the render prompt.** Scientific Etching = no text in image. The napis is recorded in `07_package.md` for the manual Canva overlay only.

### 3 · Visual concept — smartphone test × Scientific Etching
- **One dominant, high-contrast symbol/metaphor pulled from the script** (instruction's „jeden potężny symbol… znaczek pocztowy"). No micro-clutter, no busy scenes.
- **Binding Scientific Etching contract** (the `scientific-etching-guard` skill enforces it): #F4E5CA flat solid sage-beige background (no texture), #582F0E dark-brown ink only, fine-liner + cross-hatching, no gradients/fills, never photorealistic; faceless figures, **full head never cropped**; no text/words/numbers; full-bleed, no borders.
- **Reserve negative space for the napis** — compose so one clean region (e.g. upper third or one side) is calm, high-contrast space where the 2–3-word Canva overlay will sit legibly. (This is the package upgrade over the old Agent 7 — the image is designed to host the overlay.)
- The 3 visuals must be **visually distinct** (different dominant symbol + composition).

**Visual vocabulary (optional palette, at most one per strategy):** single figure in a symbolic environment · symbolic still-life / one central object · dual / ghost figure (lived self beside unlived self) · metaphorical interior space · anatomical / 19th-century textbook cross-section (shapes only, no readable text).

### Render-prompt expansion
For each strategy, expand its visual concept into a full **~400-word render prompt**: open with the scene, embed `CHARACTER_DESCRIPTION` **verbatim only if a figure appears**, close with `STYLE_SUFFIX` **verbatim**. These go to `md/07_prompts.md` (text-free; the napis is NOT in the prompt).

## Outputs

**`md/07_package.md`** — human-facing strategy doc + title handoff to `/publish`:
```
# Package — <topic>   ·  Generated: <YYYY-MM-DD>  ·  Slug: <slug>

## Strategy 1 — <angle name>   [PRIMARY — recommended]
- **Tytuł:** <≤70 chars, no trailing period>
- **Napis (Canva overlay):** ALL-CAPS 2–3 words
- **Koncept wizualny:** <1–2 sentences: dominant symbol + where the negative space for the napis sits>

## Strategy 2 — <angle name>
- **Tytuł:** …
- **Napis (Canva overlay):** …
- **Koncept wizualny:** …

## Strategy 3 — <angle name>
- **Tytuł:** …
- **Napis (Canva overlay):** …
- **Koncept wizualny:** …
```
Strategy 1 = the model's strongest recommendation (`[PRIMARY]`). The user may re-rank by editing the file; `/publish` reads `[PRIMARY]` (or the first strategy if none marked) as the primary-keyword source.

**`md/07_prompts.md`** — the 3 full render prompts in the exact `## Thumbnail N` format the renderer parses:
```
# Thumbnail Prompts: <topic>
Generated: <YYYY-MM-DD>
Model: claude-opus-4-8 (Claude Code)

## Thumbnail 1

<full ~400-word etching prompt for strategy 1 — text-free>

---

## Thumbnail 2

<… strategy 2 …>

---

## Thumbnail 3

<… strategy 3 …>
```

**`thumbnails_no_grain/thumbnail_01..03.png`** — one render per strategy (1920×1080, sage-beige pad, text-free). Strategy N → `thumbnail_0N.png`.

## Self-check before writing
- [ ] Exactly **3** strategies, **3 distinct angles**.
- [ ] Every title obeys 08_publish.md STEP 1 (no clickbait, no instructional verb, no list, no mechanistic subject, ≤70 chars, no trailing period).
- [ ] Every napis is **2–3 ALL-CAPS words** and **≠ its title** (real curiosity gap); no tabloid words.
- [ ] Every visual = one dominant symbol, etching contract, **negative space reserved for the napis**, no text in the prompt.
- [ ] `07_prompts.md` uses `## Thumbnail N` headers; each prompt ends with `STYLE_SUFFIX` verbatim; `CHARACTER_DESCRIPTION` only where a figure appears.
- [ ] Strategy 1 marked `[PRIMARY — recommended]`.

## Rate limiting & recovery
3 renders × 20s spacing ≈ 1–1.5 min. Re-roll one strategy's image: `agent7_thumbnails.py <slug> --render --no-grain --indices N`. Variations of the winner: `--indices N --count 3`. All renders too similar: re-run `/package <slug>` for a fresh strategy pass.

## Post-production (Canva, manual)
1. Open the chosen `thumbnail_0N.png` in Canva.
2. Add the strategy's **napis** as the text overlay (place it in the reserved negative space).
3. Apply film grain to the whole composition (Gaussian std dev 12 on 0–255).
4. Export. Use the strategy's **tytuł** as the YouTube title (already available to `/publish`).
````

- [ ] **Step 2: Verify the file exists and headers are intact**

Run:
```bash
grep -c "^## Strategy" workflows/pipeline/07_package.md; grep -c "STYLE_SUFFIX" workflows/pipeline/07_package.md
```
Expected: prints `3` then a non-zero count (≥3).

- [ ] **Step 3: Commit**

```bash
git add workflows/pipeline/07_package.md
git commit -m "feat(package): add /package SOP (3-strategy title+thumbnail rulebook)"
```

---

### Task 2: Write the `/package` slash command

**Files:**
- Create: `.claude/commands/package.md`

- [ ] **Step 1: Write the command file**

Create `.claude/commands/package.md` with exactly this content:

````markdown
---
description: Title↔thumbnail packaging strategist — 3 strategies (title+napis+concept) in-session on Opus 4.8, then render 3 thumbnails via Gemini. Successor to /thumbnails.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob
---

# /package — Title ↔ Thumbnail Packaging Strategist (in-session, Opus 4.8)

You design **3 radically different "packaging" strategies** for the video — each a coherent **{strategy name · title · thumbnail napis · visual concept}** bound by a **curiosity gap** — in-session (you are Opus 4.8, no Gemini, no Anthropic API), then hand the 3 visual prompts to `agent7_thumbnails.py --render`, which renders one thumbnail per strategy via Gemini. `$1` is the slug under `outputs/videos_pl/`.

> **Manual agent.** Run `/package` only when the user explicitly asks — the default path renders 3 images (credits + ~1.5 min). Pass `--no-render` for a free text-only pass.

> **Successor to `/thumbnails`.** Replaces the old 5-composition-type thumbnail agent. Runs **after `/hook`, before `/publish`** — its titles feed Agent 8.

## Workflow

1. **Validate input.** Resolve the script source (first that exists): `outputs/videos_pl/$1/docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`. If none exists, tell the user to run `/draft $1` (then `/hook $1`) first, and stop. (Unlike old `/thumbnails`, you do NOT need `08_publish.md` — `/package` runs before `/publish`.)

2. **Load source + rulebook + brand constants:**
   - The script source above (theme, emotional angles, metaphors). If it is only a `.docx`, run `PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "$1" --extract` and read `outputs/videos_pl/$1/.tmp/08_narration.md`.
   - `workflows/pipeline/07_package.md` — the 3-strategy contract (single source of truth).
   - `workflows/pipeline/08_publish.md` **STEP 1** — the title doctrine the package titles must obey.
   - `tools/utils.py` — copy `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` **verbatim** (brand contract; never paraphrase).

3. **Design 3 strategies** following `07_package.md`:
   - 3 distinct psychological angles. Each → {name, title, napis, visual concept}.
   - Title obeys 08_publish.md STEP 1 + forms a curiosity gap with its napis (title ≠ napis).
   - Napis: 2–3 ALL-CAPS words, SENSUM taste, never in the render prompt.
   - Visual: one dominant high-contrast symbol, Scientific-Etching contract, **negative space reserved for the napis**.

4. **Write two files:**
   - `outputs/videos_pl/$1/md/07_package.md` — the human-facing strategy doc (exact format in `07_package.md`), Strategy 1 marked `[PRIMARY — recommended]`.
   - `outputs/videos_pl/$1/md/07_prompts.md` — the 3 full ~400-word render prompts under `## Thumbnail 1/2/3` headers (text-free; `CHARACTER_DESCRIPTION` only where a figure appears; each ends with `STYLE_SUFFIX` verbatim). The renderer parses these headers.

5. **Render** (skip this step if `$2` is `--no-render`):
   ```bash
   PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py "$1" --render --no-grain
   ```
   Renders strategy N → `thumbnails_no_grain/thumbnail_0N.png` (1920×1080, sage-beige, text-free). 20s rate limit between calls.

6. **Report back:** the 3 strategies (name · title · napis), how many thumbnails rendered + the folder (`thumbnails_no_grain/`). Remind the user: pick ONE strategy (title + thumbnail together to preserve the gap); in Canva add that strategy's **napis** as the overlay (in the reserved space) + grain; the chosen **title** is already available to `/publish` (it reads `07_package.md`). Re-roll one image: `agent7_thumbnails.py "$1" --render --no-grain --indices N --count 3`.

## Notes
- **You are the model.** Write all 3 strategies + both files in this conversation — no API. The Python step only renders (Gemini) and post-processes.
- Pull `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` from `tools/utils.py` at runtime — never invent or summarize them.
- The napis is for the manual Canva overlay; it must NEVER appear in `07_prompts.md` (no-text-in-image contract, re-enforced by the renderer's negative prompt).
````

- [ ] **Step 2: Verify frontmatter + key references**

Run:
```bash
grep -E "argument-hint|07_package.md|--no-render|agent7_thumbnails.py" .claude/commands/package.md
```
Expected: matches for the argument-hint line, `07_package.md`, `--no-render`, and the renderer call.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/package.md
git commit -m "feat(package): add /package slash command (in-session strategist + render handoff)"
```

---

### Task 3: Note the renderer now serves `/package` (docstring only — no logic change)

The renderer is reused unchanged. Only its docstring is updated so future readers know `/package` is the producer of `md/07_prompts.md`.

**Files:**
- Modify: `tools/pipeline/agent7_thumbnails.py:1-19` (module docstring)

- [ ] **Step 1: Update the docstring**

Replace the opening docstring block. Old first lines:
```python
"""
Agent 7: Thumbnail Generation — render 5 thumbnail image candidates for a given output.

Two-step process:
  1. Concepts (5 full image prompts) are generated IN-SESSION in Claude Code on
     Opus 4.8 via the `/thumbnails <slug>` slash command — no Gemini, no Anthropic
     API. The command writes them to md/07_prompts.md.
```
New:
```python
"""
Render engine — render thumbnail image candidates for a given output (used by /package).

Two-step process:
  1. Concepts (full image prompts) are generated IN-SESSION in Claude Code on
     Opus 4.8 via the `/package <slug>` slash command — no Gemini, no Anthropic
     API. The command writes them to md/07_prompts.md (`## Thumbnail N` headers).
     (Legacy: the retired `/thumbnails` command wrote the same file format.)
```

- [ ] **Step 2: Verify Python still parses (no logic touched)**

Run:
```bash
PYTHONIOENCODING=utf-8 python -c "import ast; ast.parse(open('tools/pipeline/agent7_thumbnails.py', encoding='utf-8').read()); print('OK')"
```
Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add tools/pipeline/agent7_thumbnails.py
git commit -m "docs(render): note agent7 render engine is now driven by /package"
```

---

### Task 4: Title handoff — `/publish` reads `07_package.md` (backward-compatible)

Three files get the same handoff rule. The fallback (generate 5 titles) preserves standalone `/publish`.

**Files:**
- Modify: `workflows/pipeline/08_publish.md` (STEP 1, after the heading)
- Modify: `.claude/commands/publish.md` (Step 3, item 1)
- Modify: `.claude/agents/publish-copywriter.md` (the STEP 1 bullet)

- [ ] **Step 1: Insert the package-handoff note in the SOP**

In `workflows/pipeline/08_publish.md`, find:
```
# STEP 1 — Titles (long-form, 5 candidates)

Generate exactly **5 long-form title variants** in Polish.
```
Insert a blockquote between the heading and the "Generate exactly" line, so it reads:
```
# STEP 1 — Titles (long-form, 5 candidates)

> **Package handoff (preferred source).** If `md/07_package.md` exists (written by `/package`), its **3 strategy titles are the canonical title set** — co-designed with the thumbnails for curiosity-gap synergy. Read them, list all 3 under `## Titles`, and treat the one marked `[PRIMARY — recommended]` (or the first if unmarked) as the strongest for the step-4 primary-keyword extraction. **Skip the 5-candidate generation below** in that case. Generate the 5 candidates here ONLY when `07_package.md` is absent (standalone `/publish` run).

Generate exactly **5 long-form title variants** in Polish.
```

- [ ] **Step 2: Update the `/publish` command's titles bullet**

In `.claude/commands/publish.md`, find:
```
1. **Titles** — 5 candidates (Identity Provocation blueprint).
```
Replace with:
```
1. **Titles** — if `md/07_package.md` exists, use its **3 strategy titles** (canonical, co-designed with the thumbnails; `[PRIMARY]` = strongest for keyword extraction). Otherwise 5 candidates (Identity Provocation blueprint). See 08_publish.md STEP 1.
```

- [ ] **Step 3: Update the publish-copywriter teammate (for `/publish-team`)**

In `.claude/agents/publish-copywriter.md`, find:
```
- **STEP 1 — Titles** (5 long-form candidates, Identity-Provocation blueprint).
```
Replace with:
```
- **STEP 1 — Titles** (if `outputs/videos_pl/<slug>/md/07_package.md` exists, use its **3 strategy titles verbatim** as the canonical set — co-designed with the thumbnails; otherwise 5 long-form candidates, Identity-Provocation blueprint).
```

- [ ] **Step 4: Verify all three references landed**

Run:
```bash
grep -l "07_package.md" workflows/pipeline/08_publish.md .claude/commands/publish.md .claude/agents/publish-copywriter.md
```
Expected: all three paths printed.

- [ ] **Step 5: Commit**

```bash
git add workflows/pipeline/08_publish.md .claude/commands/publish.md .claude/agents/publish-copywriter.md
git commit -m "feat(publish): consume /package titles when present (fallback to 5 candidates)"
```

---

### Task 5: Retire `/thumbnails` completely

Per the user's decision, the command disappears (no stub). The render engine (Task 3) stays. Restore path is documented in Task 7.

**Files:**
- Delete: `.claude/commands/thumbnails.md`
- Delete: `workflows/pipeline/07_thumbnails.md` (its composition vocabulary is preserved inside `07_package.md`)

- [ ] **Step 1: Remove both files**

Run:
```bash
git rm .claude/commands/thumbnails.md workflows/pipeline/07_thumbnails.md
```
Expected: both staged for deletion.

- [ ] **Step 2: Verify no source file still invokes `/thumbnails`**

Run (excludes outputs/ historical artifacts and the reversibility doc, which legitimately mentions it):
```bash
grep -rn "/thumbnails" --include="*.md" --include="*.py" . | grep -v "outputs/" | grep -v "docs/reversibility.md"
```
Expected: no output (every live reference is repointed in Tasks 6–7). If anything prints, fix that file before committing.

- [ ] **Step 3: Commit**

```bash
git commit -m "refactor(package): retire /thumbnails command + old SOP (superseded by /package)"
```

---

### Task 6: Update `CLAUDE.md` references (`/thumbnails` → `/package`)

CLAUDE.md is actively edited (status `M`) — **grep each line before replacing** to match the exact on-disk text.

**Files:**
- Modify: `CLAUDE.md` (5 spots: directory layout, Agent Chain table row, Quick Command Reference, Images & publish bullet, Manual-agents + Parallel-safe notes)

- [ ] **Step 1: Directory layout — commands line**

Find:
```
  commands/              # Slash commands (user-invoked): /draft /hook /visuals /publish /thumbnails + *-team
```
Replace with:
```
  commands/              # Slash commands (user-invoked): /draft /hook /visuals /package /publish + *-team
```

- [ ] **Step 2: Agent Chain table — the Agent 7 row**

Find the row beginning `| 7 **(manual)** | ` and replace the whole row with:
```
| 7 → Package **(manual)** | `/package <slug>` + `agent7_thumbnails.py --render` | Opus 4.8 strategies (in-session) + Gemini 3 Pro Image render | `04_final.md` (script) | `md/07_package.md` + `md/07_prompts.md` + `thumbnails_no_grain/thumbnail_0N.png` × 3 |
```

- [ ] **Step 3: Quick Command Reference line**

Find:
```
/thumbnails <slug>                               # Agent 7 concepts → agent7_thumbnails.py --render
```
Replace with:
```
/package <slug>                                # Strateg opakowania (tytuł+napis+miniatura) → render 3; po /hook, przed /publish
```

- [ ] **Step 4: "Images & publish" — the Thumbnails bullet**

Find the sentence starting `**Thumbnails** ` and ending `20s rate limit).` Replace that sentence with:
```
**Package (was Thumbnails)** `/package <slug>` → 3 strategie `{tytuł+napis+koncept}` + render 3 via `agent7_thumbnails.py --render --no-grain` (grain + napis-overlay added manually in Canva; 20s rate limit). Runs after `/hook`, before `/publish`; chosen title feeds `/publish` STEP 1 via `07_package.md`. Napis never enters the Gemini prompt (no-text contract).
```

- [ ] **Step 5: Manual-agents + Parallel-safe notes**

Find:
```
**Manual agents — never run automatically:** Agents 6 and 7 generate images and thumbnails (cost + time). Always stop the pipeline after Agent 8 completes and wait for explicit instruction before running either.
```
Replace with:
```
**Manual agents — never run automatically:** `/package` (3 thumbnails + strategies) and Agent 6 (images) cost render credits + time. `/package` runs after `/hook` and before `/publish` (it feeds the title); Agent 6 after `/visuals`. Only run either on explicit instruction.
```
Then find the line beginning `**Parallel-safe after Agent 3 (script chain):**` and replace its last sentence `Agent 7 can run in parallel with Agent 6.` with `\`/package\` runs after \`/hook\` and before \`/publish\` (it feeds the title), independent of Agents 5/6.`

- [ ] **Step 6: Verify no stale `/thumbnails` left in CLAUDE.md**

Run:
```bash
grep -n "thumbnails" CLAUDE.md
```
Expected: only `thumbnails_no_grain/...` path mentions remain (output folder name is unchanged); no `/thumbnails` command references.

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude): repoint /thumbnails references to /package + new ordering"
```

---

### Task 7: Update the etching-guard skill + reversibility doc

**Files:**
- Modify: `.claude/skills/scientific-etching-guard/SKILL.md` (frontmatter `description`)
- Modify: `docs/reversibility.md` (append a new section)

- [ ] **Step 1: Repoint the etching-guard description**

In `.claude/skills/scientific-etching-guard/SKILL.md`, find in the `description:` line:
```
especially ad-hoc/freeform requests made OUTSIDE the /visuals and /thumbnails commands.
```
Replace with:
```
especially ad-hoc/freeform requests made OUTSIDE the /visuals and /package commands.
```

- [ ] **Step 2: Append the reversibility section**

Append to the end of `docs/reversibility.md`:
```markdown

## Mechanizm szósty — /package zastępuje /thumbnails (2026-06-05)

`/thumbnails` (Agent 7: 5 konceptów wg typów kompozycji, bez tekstu) został zastąpiony przez `/package` — strateg opakowania, który projektuje 3 strategie `{tytuł + napis + koncept}` z luką informacyjną, renderuje 3 miniatury i podaje tytuł do `/publish`. **Silnik renderu (`tools/pipeline/agent7_thumbnails.py`) NIE został usunięty** — `/package` go używa (zmieniono tylko docstring).

### Przywrócenie `/thumbnails`

```bash
# Commit sprzed zmiany (opis: „retire /thumbnails command"):
git log --oneline -- .claude/commands/thumbnails.md | head

# Przywróć komendę i stary SOP:
git checkout <pre-change-commit> -- .claude/commands/thumbnails.md workflows/pipeline/07_thumbnails.md

# (Opcjonalnie) cofnij handoff tytułu w publishu, jeśli chcesz czysty rozdział agentów:
git checkout <pre-change-commit> -- workflows/pipeline/08_publish.md .claude/commands/publish.md .claude/agents/publish-copywriter.md

git add -A && git commit -m "restore /thumbnails (revert /package)"
```

`agent7_thumbnails.py` działa identycznie pod obiema komendami (parsuje `md/07_prompts.md`, format `## Thumbnail N`), więc render nie wymaga żadnego cofania.
```

- [ ] **Step 3: Verify**

Run:
```bash
grep -c "/package" .claude/skills/scientific-etching-guard/SKILL.md; grep -c "Mechanizm szósty" docs/reversibility.md
```
Expected: `1` then `1`.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/scientific-etching-guard/SKILL.md docs/reversibility.md
git commit -m "docs(reversibility): document /package supersedes /thumbnails + etching-guard repoint"
```

---

### Task 8: End-to-end smoke test (free text-only first, then one paid render)

Use an existing slug with a locked script. `1_czujesz_ze_jestes_w_tyle` has `md/08_publish.md` (so a script exists); confirm a script source is present first.

**Files:** none (verification only).

- [ ] **Step 1: Confirm a real slug + script source exists**

Run:
```bash
ls outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/04_final.md outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/docx/ 2>$null
```
Expected: at least one of `04_final.md` / `script.docx` / `script_corrected.docx` exists. If not, pick another slug from `ls outputs/videos_pl/`.

- [ ] **Step 2: Run `/package` in text-only mode (free)**

In Claude Code:
```
/package 1_czujesz_ze_jestes_w_tyle --no-render
```
Then verify the two artifacts:
```bash
grep -c "^## Strategy" outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_package.md
grep -c "^## Thumbnail" outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_prompts.md
grep -c "PRIMARY" outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_package.md
```
Expected: `3`, `3`, `1`.

- [ ] **Step 3: Manually assert the contract on the written strategies**

Open `md/07_package.md` and confirm for each of the 3 strategies: title ≤70 chars with no trailing period; napis is 2–3 ALL-CAPS words; **title text ≠ napis text** (real curiosity gap); no clickbait words (SZOK/SEKRET/NIE UWIERZYSZ). Open `md/07_prompts.md` and confirm no prompt contains the napis text or any "text/words/labels" instruction, and each ends with the verbatim `STYLE_SUFFIX`.

- [ ] **Step 4: Confirm the publish handoff reads it**

In Claude Code, start `/publish 1_czujesz_ze_jestes_w_tyle` and confirm STEP 1 lists the **3 titles from `07_package.md`** (not 5 freshly invented). Then temporarily rename the file and confirm the fallback:
```bash
Move-Item outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_package.md outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_package.bak.md
```
Re-run `/publish` STEP 1 mentally/dry — it must fall back to generating 5. Then restore:
```bash
Move-Item outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_package.bak.md outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/md/07_package.md
```

- [ ] **Step 5 (paid, ask the user first): one render pass**

Only after the user OKs spending render credits:
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py "1_czujesz_ze_jestes_w_tyle" --render --no-grain
```
Verify:
```bash
ls outputs/videos_pl/1_czujesz_ze_jestes_w_tyle/thumbnails_no_grain/thumbnail_0*.png
```
Expected: `thumbnail_01.png`, `thumbnail_02.png`, `thumbnail_03.png`. Eyeball each: two colors only, no text in the image, full (uncropped) head if a figure is present, clear negative space where the napis will sit.

- [ ] **Step 6: Final dangling-reference sweep**

Run:
```bash
grep -rn "/thumbnails" --include="*.md" --include="*.py" . | grep -v "outputs/" | grep -v "docs/reversibility.md"
```
Expected: no output.

---

## Self-review (done while writing this plan)

- **Spec coverage:** standalone `/package` (Task 2) ✓; 3-strategy curiosity-gap rulebook incl. napis + smartphone-test×etching synthesis + reserved negative space (Task 1) ✓; reuse render engine unchanged (Task 3) ✓; default render 3 + text proposals, `--no-render` option (Tasks 1–2) ✓; title handoff to `/publish` with fallback, incl. `/publish-team` (Task 4) ✓; `/thumbnails` removed completely (Task 5) ✓; CLAUDE.md + etching-guard + reversibility updated (Tasks 6–7) ✓.
- **Placeholder scan:** new-file content is given in full; edits are exact old→new strings. No TBD/TODO.
- **Naming consistency:** `md/07_package.md` (strategy doc) and `md/07_prompts.md` (render prompts, `## Thumbnail N`) used identically across Tasks 1, 2, 4, 8; renderer flags (`--render --no-grain --indices --count`) match `agent7_thumbnails.py`'s real parser; folder `thumbnails_no_grain/` matches the engine's `--no-grain` output path.
- **Known soft spot:** the `/publish` STEP 1 fallback is prose-level (no automated test harness exists); Task 8 Step 4 exercises both branches manually.
````
