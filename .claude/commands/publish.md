---
description: Agent 8 publish package — 9 focused steps; DOMYŚLNIE specialist Agent-Teams generators + cold-context Native-Copy Critic na human-facing copy (titles, description, chapters, Shorts copy); auto-fallback do pełnego in-session gdy Agent Teams niedostępny (no API).
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob, Agent, TeamCreate, SendMessage, TeamDelete
---

# /publish — Agent 8 Publish Package (Agent Teams + Native-Copy Critic, domyślnie)

The same 9 focused steps from `workflows/pipeline/08_publish.md` run — but instead of you running all
of them in-session, **specialist teammates** generate them in their own contexts **by default**, and a
dedicated **Native-Copy Critic** teammate reads the assembled package **cold** and debates only the
human-facing Polish copy. The critic has its own context window, so it never rationalizes copy it wrote
— it replaces the owner's manual Copilot pass on the published copy. **No Gemini, no Anthropic API.**

`$1` is the slug — a folder under `outputs/videos_pl/`. The two deterministic bookends
(`agent8_publish.py --extract` / `--signals` / `--finalize`) are deterministic helpers, no LLM.

**Why a team and not just a subagent:** the native-copy review is a multi-round debate — the critic
must *remember what it challenged* to push back on weak fixes. A persistent teammate keeps that history;
its independence comes from never receiving the generators' reasoning.

**Roster & division of labor:**

| Concern | Owner |
|---|---|
| Input validation, `--extract`/`--signals`/`--finalize`, **chapters (step 3)**, **bibliography (step 5)**, assembly, debate rewrites | **Lead** (you, in-session) |
| Titles (1), Description+hashtags (2), Shorts titles (7), Shorts descriptions (8) — warm copy | teammate `pubcopy` (`publish-copywriter`) |
| Long-form tags (4), Shorts tags (9) — search-shaped | teammate `pubseo` (`publish-seo`) |
| Clip selection (6) — Triple Retention, verbatim quotes | teammate `pubclips` (`publish-clips`) |
| Language / translationese on human copy — the cold ear | teammate `pubcritic` (`native-copy-critic`) |

The prompts are single-sourced in `workflows/pipeline/`: the 9 step-prompts + master template +
self-check live in `08_publish.md`; the critic's prompt is `08d_native_copy.md`. **You are the model**
for the lead-owned steps; each teammate is the model for its own steps.

**File ownership is strict (two agents never edit one file):** generators write only their `.tmp/`
scratch file; you own `md/08_working.md` + `md/08_publish.md`; the critic only *reads* `08_working.md`
and *writes* its `08d_nativecopy_iter*.md` logs.

---

## Step 1 — Validate inputs

- Confirm `outputs/videos_pl/$1/md/02_verified_research.md` exists. If missing, tell the user to run
  `PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "$1"` first, and stop.
- Resolve the **script source** (first that exists): `docx/script_corrected.docx` > `docx/script.docx`
  > `md/04_final.md`. If none exists, tell the user to run `/draft $1` first, and stop.
- **Package-handoff gate.** Check whether `outputs/videos_pl/$1/md/07_package.md` exists. If it is
  **missing**, do not silently proceed: warn the user that `/package` has not run, so the titles here
  will be generated **standalone** and won't be co-designed with the thumbnail (curiosity-gap synergy
  lost) — and that running `/package $1` *after* `/publish` is **too late**: it orphans the package and
  forces a full re-run. Recommend running `/package $1` first. Proceed only on explicit confirmation
  (standalone publish is a supported but inferior mode per `08_publish.md` STEP 1).

## Step 1.5 — Preflight the team (graceful fallback)

Agent Teams is experimental and enabled via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in the
committed `.claude/settings.json`). On Windows / the VS Code extension, split panes are unsupported, so the
team runs **in-process** (the user presses **Shift+Down** to view a teammate).

If you cannot spawn teammates (feature unavailable, spawn error), **do not hard-fail.** Fall back to
**fully in-session behavior (no team)**: run all 9 steps in-session per `08_publish.md`, assemble
`md/08_publish.md`, run `--finalize`, and tell the user the native-copy debate was skipped because Agent
Teams was unavailable. This in-session-only path is the **only** cheaper route — there is no separate
command and no `--solo` flag; the rest of this command assumes the team is available.

## Step 2 — Load source materials (lead)

- Read `workflows/pipeline/08_publish.md` — the canonical 9-step spec, master-file template, and
  self-check. Read `workflows/pipeline/08d_native_copy.md` (the critic contract you parse against).
- **Materialize the narration** (Claude can't Read `.docx`):
  ```bash
  PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "$1" --extract
  ```
  This writes `outputs/videos_pl/$1/.tmp/08_narration.md` (resolved via script_corrected.docx >
  script.docx > 04_final.md) — the shared narration every generator reads.
- Read `outputs/videos_pl/$1/md/02_verified_research.md` (you own the step-5 bibliography).

## Step 3 — Create the team & spawn generators

Create a team named `publish-$1`. Spawn three generator teammates **in-process** using their agent
types — `pubcopy` (`publish-copywriter`), `pubseo` (`publish-seo`), `pubclips` (`publish-clips`) — and
the critic `pubcritic` (`native-copy-critic`). Each teammate's briefing is only: the slug, that it
follows `08_publish.md` (or `08d_native_copy.md` for the critic) for its steps, and which wave it is in.
**Do not pass any generation rationale to the critic** — its isolation is the whole point.

## Step 4 — Wave 1 (parallel)

Dispatch concurrently, then wait for all three to report:

1. **`pubclips`** — run **step 6** (clip selection) → `.tmp/08_clips.md`.
2. **`pubcopy`** — run **steps 1–2** (titles + description+hashtags) → `.tmp/08_copy.md`.
3. **Lead, in-session, concurrently:**
   - Generate **step 3 chapters** (6–12 viewer-perspective labels; first `00:00`, rest `[XX:XX]`) and
     **step 5 bibliography** (INCLUDE/EXCLUDE every `02_verified_research.md` entry; English concept
     labels; citation-only) per `08_publish.md`. Hold these for assembly.
   - Run the signals bookend so `pubseo` has its input:
     ```bash
     PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "$1" --signals "--topic=<short Polish search seed from the script + your strongest working title>"
     ```
     (writes `.tmp/08_signals.md`).

## Step 5 — Wave 2 (parallel)

After wave 1 completes (clips + titles exist, signals written), dispatch concurrently and wait:

1. **`pubcopy`** — run **steps 7–8** (Shorts titles + descriptions), reading `.tmp/08_clips.md`; append
   to `.tmp/08_copy.md`.
2. **`pubseo`** — run **step 4** (long-form tags; Tag #1 = exact-match primary keyword from the
   strongest title in `.tmp/08_copy.md`; reads `.tmp/08_signals.md`) and **step 9** (Shorts tags per
   clip) → `.tmp/08_tags.md`.

## Step 6 — Assemble the working package (lead)

Read `.tmp/08_copy.md`, `.tmp/08_tags.md`, `.tmp/08_clips.md`, and combine with your own chapters +
bibliography. `Write` `outputs/videos_pl/$1/md/08_working.md` in the **exact section order** of the
master-file template in `08_publish.md` (Titles → Video Description with Timestamps + `Badania i
źródła:` + 3 hashtags → YouTube Tags → YouTube Shorts Package). For each Short, assemble the LOCKED
field order (`**Title:**`, `**Description:**`, `**Tags:**`, `**Script Lines to Clip:**`) and place the
full contiguous verbatim passage from `.tmp/08_clips.md` under the clip block as consecutive `> ` lines.
**Leave the `**Script Lines to Clip:**` label with no quarter marker** — `--finalize` adds the single
`[Q1]–[Q4]`. Run the `08_publish.md` self-check against the assembled file before the debate.

## Step 7 — Native-copy debate loop (`N = 1`, `MAX = 3`)

The critic reads `md/08_working.md` cold. Loop:

1. **Assign the pass.** Message `pubcritic`: *"Native-copy pass: slug `$1`, iteration `N`. Read
   `outputs/videos_pl/$1/md/08_working.md` cold and follow `workflows/pipeline/08d_native_copy.md`."*
   Wait for its completion notification.
2. **Read the verdict.** Read `outputs/videos_pl/$1/md/08d_nativecopy_iter{N}.md`; parse the first
   non-blank line after `## VERDICT` (exactly `NATIVE` or `REWORK`; anything else = `UNKNOWN`).
3. **Branch:**
   - `NATIVE` → exit the debate.
   - `REWORK` & `N < MAX` → **rewrite only the challenged copy lines** in `08_working.md` (titles,
     description, chapter labels, Shorts titles/descriptions only — **never** tags, bibliography, or a
     verbatim Shorts clip passage), toward the STEP 1/STEP 2 register in `08_publish.md` and the voice canon in
     `workflows/guides/voice_brief.md`. **Do not touch un-challenged lines** (avoid drift) and **do not
     over-correct** — restore the hit through a sharper phrasing, never by flattening; protect the
     strongest title. Save `08_working.md`, set `N = N + 1`, continue.
   - `REWORK`/`UNKNOWN` at `N == MAX` → exit, mark the language verdict not-NATIVE.
4. **Iteration dampener (N ≥ 3)** is enforced by the critic per `08d_native_copy.md` (re-challenge
   unresolved + new calques only) — no action needed from you beyond honoring its narrower findings.

## Step 8 — Finalize

Copy `outputs/videos_pl/$1/md/08_working.md` → `outputs/videos_pl/$1/md/08_publish.md`.

If the debate ended **not** `NATIVE`, prepend a WARNING header to `08_publish.md`:

```
# WARNING: Publish copy shipped with language: REWORK@iter<N> — review before publishing.
# Language (native-copy): md/08d_nativecopy_iter<N>.md
# Generated: <YYYY-MM-DD>

```

Then run the finalize bookend over the master file:
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "$1" --finalize
```
This annotates each clip block with its quarter (`[Q1]–[Q4]`), trims the long-form tag line to the
450-char budget, validates every Short has a `**Script Lines to Clip:**` block (loud `[MISSING]`
otherwise), and exports `docx/08_publish.docx`.

## Step 9 — Tear down the team

Ask each teammate to shut down, then clean up the team. **Always do this** — Agent Teams allows only one
team at a time, so a lingering team blocks future `/draft` and `/publish` runs. Do cleanup
from the lead, never from a teammate.

## Step 10 — Report back

- Title count, description sentence count, chapter count.
- Long-form tag count + the char length `--finalize` printed.
- Shorts count + any `[Q?]` (paraphrased quote) / `[MISSING]` (dropped clip block) warnings — tell the
  user to fix those before publishing.
- **Native-copy debate:** verdict (`NATIVE`/`REWORK`) + rounds used; if not clean, point at
  `md/08d_nativecopy_iter<N>.md`.
- **Order reminder:** `/package $1` runs *before* `/publish` (its titles feed STEP 1) — it is **not** a
  next step. If `07_package.md` was absent, the titles above are standalone (see the Step 1
  package-handoff gate). After publish, the only remaining work is manual: images (Agent 6) and
  recording + Align.

## Notes

- **You are the model** for the lead-owned steps (chapters, bibliography, assembly, rewrites). Each
  generator teammate is the model for its steps; the critic is the model for 8d. Do NOT shell out to
  the legacy Gemini path — `agent8_publish.py "$1" --api` is a fallback only. The only shell calls are
  the three deterministic bookends (`--extract`, `--signals`, `--finalize`).
- **Falls back to fully in-session (no team)** if Agent Teams is unavailable (Step 1.5) — that
  in-session-only path is the only cheaper route; there is no separate command and no `--solo` flag.
- **Token cost:** four extra Opus contexts (3 generators + 1 critic across ≤3 language rounds) above the
  in-session run.
- Everything is Polish except verbatim script quotes (already Polish) and the bibliography concept
  labels (stay English). Keep the published copy research-invisible.
- Keep the gate honest: the native-copy critic must genuinely re-read, not rubber-stamp. A wasted round
  is cheaper than shipping a calqued title.
