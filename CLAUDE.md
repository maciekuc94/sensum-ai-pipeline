# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)**
- Markdown SOPs stored in `workflows/`
- Each workflow defines the objective, required inputs, which tools to use, expected outputs, and how to handle edge cases
- Written in plain language, the same way you'd brief someone on your team

**Layer 2: Agents (The Decision-Maker)**
- This is your role. You're responsible for intelligent coordination.
- Read the relevant workflow, run tools in the correct sequence, handle failures gracefully, and ask clarifying questions when needed
- You connect intent to execution without trying to do everything yourself
- Example: If you need to pull data from a website, don't attempt it directly. Read `workflows/scrape_website.md`, figure out the required inputs, then execute `tools/scrape_single_site.py`

**Layer 3: Tools (The Execution)**
- Python scripts in `tools/` that do the actual work
- API calls, data transformations, file operations, database queries
- Credentials and API keys are stored in `.env`
- These scripts are consistent, testable, and fast

**Why this matters:** By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

## Channel Language (2026-05-25 — Polish localization)

**This pipeline produces Polish-language SENSUM content.** The channel is `@sensumpolska` on YouTube. All script-writing agents (3a/3b/3c/4b/8) generate Polish output; style guides (`workflows/guides/style_guide.md`, `workflows/guides/narrative_architectures.md`) are in Polish. The English pipeline as it stood on 2026-05-25 is preserved at Git tag `en-pipeline-v1` and English versions of style guides live alongside Polish ones as `.en.md` files. The legacy English channel `@hello.sensum` is dormant.

**To restore English behavior** (any granularity — single file, full pipeline, branch): see `docs/reversibility.md` for ready-to-copy `git checkout en-pipeline-v1 -- <path>` commands.

**Banned-phrase lists for Polish are intentionally empty** in both Polish style guides — they fill in *empirically* as the Reviewer (Agent 3c) and the user flag real cringe-phrases from shipped Polish scripts. The English guides accumulated their banned-phrase lists across dozens of scripts; the Polish guides start blank and grow the same way.

**Research is still in English.** Agents 1/2 produce `01_research.md` and `02_verified_research.md` in English (PubMed + Gemini sources are English-language). Polish script agents read English research and produce Polish output — this is intentional, not a bug. Do not localize Agents 0/1/2.

## How to Operate

**1. Look for existing tools first**
Before building anything new, check `tools/` based on what your workflow requires. Only create new scripts when nothing exists for that task.

**2. Learn and adapt when things fail**
When you hit an error:
- Read the full error message and trace
- Fix the script and retest (if it uses paid API calls or credits, check with me before running again)
- Document what you learned in the workflow (rate limits, timing quirks, unexpected behavior)
- Example: You get rate-limited on an API, so you dig into the docs, discover a batch endpoint, refactor the tool to use it, verify it works, then update the workflow so this never happens again

**3. Keep workflows current**
Workflows should evolve as you learn. When you find better methods, discover constraints, or encounter recurring issues, update the workflow. That said, don't create or overwrite workflows without asking unless I explicitly tell you to. These are your instructions and need to be preserved and refined, not tossed after one use.

## The Self-Improvement Loop

Every failure is a chance to make the system stronger:
1. Identify what broke
2. Fix the tool
3. Verify the fix works
4. Update the workflow with the new approach
5. Move on with a more robust system

This loop is how the framework improves over time.

## File Structure

**Directory layout:**
```
.tmp/                    # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/
  pipeline/              # Agent scripts 0–8 + align (the full production chain)
  intelligence/          # Intelligence Agent + intelligence module (analyzer, collector, db, slide_builder, vision)
  dev/                   # Support tools: add_grain.py
  utils.py               # Shared utilities (all agents import from here)
workflows/
  pipeline/              # Numbered SOPs 00–08 (one per pipeline agent), plus align.md and intelligence.md
  guides/                # style_guide.md, style_guide_images.md, narrative_architectures.md
outputs/
  videos_pl/             # Polish-channel videos (one folder per slug). videos_en/ exists for legacy English content.
  channel_assets/        # Shared brand assets (logo, fonts, colors)
  intelligence/          # Intelligence Agent analysis outputs
.env                     # API keys and environment variables (NEVER store secrets anywhere else)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Design Standards

**Color palette:** Two colors only — #F4E5CA (Sage Beige, exclusive background, described in prompts as a **flat solid sage beige background with no texture**; the paper-grain look is applied in post via `add_grain.py`, never requested in the prompt) and #582F0E (Dark Brown, all ink lines, cross-hatching, and silhouettes). No other colors permitted in any generated visual, slide, chart, or asset. The illustration style is Scientific Etching: fine-liner ink sketches with cross-hatching for depth, referencing 19th-century scientific journal engravings. No gradients, no fills, no watercolor. No text, no labels, no words in any generated image. No decorative borders or frames around the image — full-bleed composition.

## Technical Notes

**No Claude API — all Claude runs in-session (2026-05-29)**
The pipeline makes **zero Anthropic API calls**. Every Claude step runs in-session in Claude Code on Opus 4.8 via slash commands: `/draft` (3a Drafter + the 3b Revisor ↔ 3c Reviewer loop), `/hook` (4b), `/visuals` (5), `/publish` (8 — the full publish package), `/thumbnails` (7 concepts). `query_claude()` was removed from `tools/utils.py`; `ANTHROPIC_API_KEY` is no longer required. Gemini (Vertex AI) remains only for research (Agents 0/1/2), image rendering (6, 7-render), and QA (6b). Prompts for the in-session agents are single-sourced in `workflows/pipeline/03{a,b,c}_*.md`, `04_hook.md`, `05_visuals.md`, `08_publish.md`, and `07_thumbnails.md`. Legacy Gemini-API script paths survive only behind an `--api` flag (`agent3.py`, `agent3b/3c`, `agent4_hook.py --api`, `agent8_publish.py --api`).

**Windows terminal encoding**
When running pipeline scripts via Bash on this machine, prefix with `PYTHONIOENCODING=utf-8` to avoid codec errors on Unicode characters (e.g., arrows in print statements):

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent3.py "slug"
```

**PubMed zero results**
The auto-derived PubMed query sometimes returns zero results (query too specific or wrong MeSH terms). This is acceptable if the Gemini research section contains solid peer-reviewed references. Agent 2 verifies claims against scientific literature regardless of PubMed results — proceed to Agent 2 as normal.

**Research-invisible script voice (2026-05-21; Polish equivalents 2026-05-25)**
Scripts must read as a warm therapist talking to one person — research entirely invisible. The channel is research-*grounded* (Agents 0/1/2 still do PubMed verification) but never research-*forward* in the script. Findings appear as observations about being human, spoken in the speaker's own voice. The viewer trusts the speaker, not the citation. All real bibliographic citations live in the YouTube description (Agent 8 output) — never in the spoken narration.

Polish forbidden phrases (research-framing): "naukowcy odkryli", "badania pokazują", "wyniki badań", "z badań wynika", "ostatnie badania", "neuronauka wykazała", "psychologowie nazywają to", "dane pokazują", "według badań", "nauka jest jasna", "jedno badanie", "meta-analiza", "w [roku]" wprowadzające badanie. List grows empirically as the channel ships content.

**Permission Practice closing section (2026-05-24; reformatted to prose 2026-05-29)**
Every script ends with a mandatory Permission Practice section (~4 embodied micro-practices, between architecture body and recognition close). **As of 2026-05-29 it is flowing prose ("Czasem wystarczy…" anaphora), NOT a numbered list — numbered prescriptive lists are now banned everywhere in the script.** Full spec in `workflows/guides/narrative_architectures.md`. Agent 3a generates it; 3b keeps it as prose + applies softeners; 3c flags numbered-list regressions and PP integrity violations.

**Permission Practice — two registers / „path beat" (2026-05-31)**
Permission Practice now has **two registers**, same *form* (prose, „Czasem wystarczy…", ~4 practices, softeners, recognition close still last), different *content*. **Somatic** (default, unchanged): breath/hand/noticing/naming — for topics whose only real move is internal (envy, shame, anxiety). **Strategic** (new — the „beat ścieżki"): behavioral micro-practices (choose one thing for the season, set-aside-not-discard, reframe the day job as ground) — only when the topic offers a genuine *external move* (career „too many interests", decision paralysis). **Trigger rule** lives in `narrative_architectures.md` „Dwa rejestry"; `/draft <slug> [arch] --sciezka` forces strategic. **Hard invariants unchanged:** prose not numbered list, temporal softeners, research-invisible (practical move as a plain human invitation, never a named framework/jargon — no „serial mastery / far transfer"), and **recognition close always gets the last word** (the map is a beat, not the destination — even the M-shaped video that inspired this ends on recognition). 3c category A now accepts the strategic register as valid (not auto-FLAG as "advice") but still BLOCKERs on numbered list / missing-softener / optimization-scheduling framing / no recognition after PP. Origin: brainstorm over two viral EN scripts the user loves (`workflows/guides/reference_scripts/` + `inspiration_log.md`) — M-shaped earns the strategic register, the super-sensor („cry easily") script is pure-permission and proves the beat must stay optional. The inspiration_log is the standing loop: user drops liked scripts, we extract the one genuinely-new lesson, default to NOT bloating.

**Narrative architectures — Composite Portrait is the default (2026-05-29; re-spec'd same day after pilot)**
There are five narrative architectures, all written at the channel's native length (**~10–15 min / ~1,500–1,750 Polish words → ~140–180 images** at one-per-sentence density). **`Composite Portrait` is the default** — Agent 3a uses it unless `/draft <slug> "<Architecture Name>"` forces one of the four others (Forensic Case Study, Historical Reversal, Socratic Challenge, Systems Audit). Composite Portrait follows one archetype figure through four movements (Surface → Cost → Origin → Reframe), in **full second person „ty"** (the figure is the viewer — *„Kupujesz nowy notatnik…"*), and threads a recurring object-motif. The reusable faceless figure (`CHARACTER_DESCRIPTION`) is its recurring protagonist (the viewer's avatar). **The initial ~20-min long-form + voice-braid (3rd-person „ktoś" + „ty" fold-backs) experiment was retired 2026-05-29** after the slug-2 pilot: the braid read as distancing/artificial in Polish, and ~20 min was longer than the format needs. Inspired by long-form portrait essays (e.g. Du Cinema) but realized at SENSUM's native length. Full spec in `workflows/guides/narrative_architectures.md` + `05_visuals.md` register.

**Craft calibration (2026-05-29, from slug-2 pilot + external native-ear review)** — enforced globally in `style_guide.md` / 3a / 3c: **one central metaphor per script** (don't stack secondary metaphors — podatek + dom na wodzie + bak paliwa + loteria…); **at most 2–3 attention-imperatives** („Zwróć uwagę"/„Popatrz"/„Zatrzymaj się"/„Pomyśl"); **no uncited round-number stat** — even „blisko połowy tego, co robisz…" reads as research-without-citation, describe it instead.

**Number policy:** Round, framed numbers only ("roughly half", "most people"). Banned in scripts: decimals (0.62), effect sizes (d = X, r = X), p-values, study counts ("94 experiments"), participant counts ("8,000 people"), methodology terms (pre-registered, double-blind, longitudinal, meta-analysis). If a number doesn't land emotionally as plain English, cut it. **Even a round number stated as fact ("blisko połowy tego, co robisz…") reads as an uncited research stat — describe the phenomenon without the number instead.**

**Jargon policy:** Plain language first. Describe the phenomenon in everyday words. Name a scientific term only if (a) the name itself is memorable and (b) it appears once, late, after the idea has already landed. Never use the jargon-then-translation pattern ("ego depletion — the depletion of…").

**Darwin exception (Historical Reversal architecture only):** Scripts using Historical Reversal may name Darwin as a historical narrative device (the "wrong view" being overturned). This is the structural antagonist of the architecture, not an inline citation. No other historical figures or researchers may be named.

**Clinical-anchor exception (2026-06-01, any architecture):** Exactly one established clinical anchor per script may be named and framed as "Badania nad [efektem] pokazują, że…" (e.g., "efekt świeżego startu" / fresh-start effect) — a deliberate device, not a general research citation. Hard limits: only one such frame per script; no author names, no years, no numbers, no methodology terms alongside it; a second research-framing frame in the same script is a BLOCKER (3c category B). All other research-invisible rules remain unchanged.

**Image generation — Agent 6**
Agent 6 uses `gemini-3-pro-image-preview` via Vertex AI with `location="global"` (regional endpoints return 404 for this model). The API is `generate_content(response_modalities=["IMAGE"])` — not `generate_images()`. The negative prompt is embedded in the prompt text, not passed as a parameter. Aspect ratio is handled post-generation via `ImageOps.pad()` (pillarbox with #F4E5CA sage beige — no stretching, no cropping). Image prompts specify `#F4E5CA` sage beige background directly in `STYLE_SUFFIX` in `utils.py`; `_enforce_background_color` also runs automatically after each image is saved as a safety net (note: this only catches solid wrong-color flats — textured backgrounds and decorative frames pass through it; Agent 6b catches those). **STYLE_SUFFIX rule:** never say "vellum", "aged paper", "parchment", or any texture descriptor in the prompt — Gemini interprets those literally and renders paper grain into the image; the prompt asks for a flat solid background and `add_grain.py` adds grain in post.

**Selective regeneration — `--indices`**
`agent6_images.py --generate --indices "22,26,97"` regenerates only the listed 1-based indices and overwrites existing PNGs at those positions. Other images are untouched. Use this for re-rolling specific bad images flagged by Agent 6b without spending API credits on the whole set.

**Image QA — Agent 6b**
After Agent 6, run `agent6b_image_qa.py "<slug>"` to validate every image against the SENSUM style contract using Gemini 2.5 Flash on Vertex AI. Checks: flat solid sage beige background (no texture), dark brown ink only (no other colors), no decorative borders/frames, no head cropping, no visible text. Writes `md/06_qa.md` listing failures. Use `--retry` to auto-regenerate failed indices via Agent 6 (one attempt). The validator never deletes images; it reports and lets the user decide.

**Thumbnail generation — `/thumbnails` + agent7_thumbnails.py**
Run after Agent 8 (needs `08_publish.md`). Two-step: `/thumbnails <slug>` generates 5 thumbnail concepts in-session (Opus 4.8, no API) into `md/07_prompts.md`, then `agent7_thumbnails.py "<slug>" --render --no-grain` renders each at 1920×1080 via Gemini. `--no-grain` — grain is applied manually in Canva after adding the title overlay. Rate limit: 20s between Vertex AI calls. For all flags and the composition-type rubric see `workflows/pipeline/07_thumbnails.md`.

**Agent 8 publish package — in-session, 9 focused steps (2026-06-02)**
Agent 8 runs entirely in Claude Code via `/publish <slug>` — **no API**. The old 3-mega-prompt Gemini pipeline (titles / shorts / metadata) is split into **9 single-responsibility steps** so each concern gets a dedicated reasoning pass: (1) titles, (2) description + 3 hashtags, (3) timestamps, (4) long-form tags, (5) bibliography, (6) shorts clip-selection, (7) shorts titles, (8) shorts descriptions, (9) shorts tags. Prompts are single-sourced in `workflows/pipeline/08_publish.md` (the master-file template + self-check live there too). Two deterministic Python bookends bracket the in-session run: `agent8_publish.py "<slug>" --extract` (materialize narration → `.tmp/08_narration.md`, since Claude can't Read `.docx`), `--signals` (scrape YouTube autocomplete + load the latest niche `_tag_signals.md` → `.tmp/08_signals.md`; pass `--topic="<polish seed>"` for real Polish autocomplete), and `--finalize` (annotate clip blocks with `[Q1]–[Q4]`, trim the tag line to the 450-char budget, validate every Short has a clip block, export `docx/08_publish.docx`). The legacy Gemini orchestrator survives behind `agent8_publish.py "<slug>" --api`.

**Output reminders (locked):** Tag #1 = exact-match primary keyword from the chosen title (algorithm front-loads weight here — don't waste it); **5–8** multi-word tags total, single-word prohibited except `SENSUM`-once; exactly 3 hashtags (`#sensum` first); description is exactly 5 sentences; bibliography heading is `Badania i źródła:`; Shorts clips tagged `[Q1]–[Q4]` — `[Q?]` means the quote didn't substring-match (paraphrase slipped in), `[MISSING]` means a Short lacks its clip block — fix both before publishing. The autocomplete scraper is fragile: if the tags look thin, it failed; the package is still valid via niche signals + script, add tags manually.

**Script revision architecture (B++ v2) — full chain in-session on Opus 4.8 (2026-05-29)**
Agent 3 runs entirely in Claude Code via `/draft <slug>` — **no API**: 3a Drafter → 3b Revisor ↔ 3c Reviewer loop, all on the in-session Opus 4.8 model. Loop exits on PASS or max iterations (default 5); on FLAG at max, `04_final.md` is prepended with a warning header — review `03c_review_iter{N}.md` before recording. Prompt templates are single source of truth: `03a_drafter.md`, `03b_revisor.md`, `03c_reviewer.md`. The legacy Gemini-API loop (`agent3.py` orchestrating `agent3b_revisor.py`/`agent3c_reviewer.py`) is kept only as an `--api` fallback; those files retain shared helpers (`parse_verdict`, `build_output`). **Reviewer independence note:** in-session, 3c shares context with 3b — the `03c_reviewer.md` prompt enforces a fresh critical pass (default FLAG on uncertainty, no rewriting). Pre-revisor English chain preserved at Git tag `agent-chain-v1-prerevisor`; see `docs/reversibility.md`.

**Fluency-first script chain refactor (2026-05-30)** — addressed the root cause of mediocre native Polish despite Opus 4.8: the chain was tuned for *policy/structure* compliance and had **no owner for sentence-level Polish naturalness**, so calques passed a clean PASS. Four changes: **(1) Voice-first Drafter** — `03a_drafter.md` now writes in two ordered stages: Stage 1 produces living native Polish from voice anchors + corpus + research *without* prohibition lists in front; Stage 2 audits that prose against doctrine and fixes only genuine violations, protecting voice (constraints-first was producing defensive, flat prose). **(2) New `workflows/guides/voice_corpus.md`** — the positive Polish ear: exemplar passages from the user's own shipped slug-1 narration (§A) + native-ear correction pairs from the slug-1 raw→hand diff (§B) + slug-2 calques to avoid (§C). Replaces the *English* orchid/dandelion transcript as the primary rhythm anchor. Read by 3a/3b/3c. **(3) 3b MOVE 0 — open-ended naturalness sweep:** rewrite any sentence that isn't natural spoken Polish even if it matches none of the 11 named moves; philosophy changed from "leave most sentences untouched" to "leave only if already natural Polish." **(4) 3c category J — translationese gate:** real FLAG at ≥2 calque/awkward sentences; this is the gate that replaces the user's manual Copilot pass. Also de-bloated: removed the ~200-line Visual Register Maps from `narrative_architectures.md` (redundant — the canonical copy lives in `05_visuals.md`, the only file Agent 5 reads; the text agents 3a/3b/3c never needed it). `narrative_architectures.md` = structure owner, `style_guide.md` = voice owner, prompts reference rather than re-inline.

**Agent Teams variant — `/draft-team` + cold-context Native-Ear Critic (Agent 3d) (2026-06-02)**
The translationese gate has a structural weakness: in-session, 3b/3c share the context that *wrote* the calque, so they rationalize their own prose (the gap `03b` documents — calques like „Znasz to uczucie z palców" passed a clean loop). `/draft-team` fixes this with a **Claude Code Agent Team**. It runs 3a + the 3b↔3c loop in-session **exactly as `/draft`**, but **scopes the in-session 3c to categories A–I and defers category J (idiomatic Polish / translationese) to a separate `native-ear-critic` teammate** that has its **own context window** — it never saw the drafting/revising reasoning, so it reads the prose cold, like the owner's manual Copilot pass. **It is designed to replace that manual Copilot pass.** After the A–I loop reaches PASS, the lead copies the script to `md/04_working.md` and runs an **adversarial native-ear debate** (≤3 rounds): critic flags calques/the 4 named tells (BLOCKER in impact positions — hook, anchor lines, PP, recognition close) → lead rewrites only the challenged sentences → critic **re-challenges** weak fixes and scans for new calques, until verdict `NATIVE` (then finalize `04_final.md`) or `REWORK` at max (ship-warning header). An **anti-sterility guard** makes the critic also reject over-flattened rewrites and protect the strongest images (`voice_corpus.md` §E.f), so the debate doesn't grind prose into compliant mush. Artifacts add `md/03d_nativeear_iter*.md`; the full review trail is kept. **File ownership is strict** — lead owns/edits `03a/03b/03c/04_working/04_final`; the teammate only *reads* `04_working.md` and *writes* its own `03d_*` logs (two agents never edit one file). Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (set in `.claude/settings.local.json`); runs **in-process** on Windows/VS Code (split panes unsupported — Shift+Down to view the critic). **Falls back to plain `/draft` behavior** (in-session 3c runs A–J) if Agent Teams is unavailable. **Token cost:** one extra Opus context across ≤3 language rounds — use `/draft` for the cheaper path. Prompts are single-sourced: critic = `workflows/pipeline/03d_native_ear.md`, role = `.claude/agents/native-ear-critic.md`, orchestration = `.claude/commands/draft-team.md`. Reference: `docs/agent_teams_reference.md`. `/draft` stays the default; `/draft-team` is opt-in when native Polish is the priority.

**Script-chain Tier-1 sharpening (2026-05-30, after external Gemini/Copilot review)** — two changes on top of the fluency-first refactor, chosen to sharpen without re-bloating (most of the external feedback was already implemented or scope-creep). **(1) Severity triage in 3c** — every Critical Issue is now classified `BLOCKER` / `FIX` / `WATCH`; `03c_reviewer.md` issues `FLAG` only on ≥1 BLOCKER, ≥2 same-category FIX, or ≥3 drift-pattern WATCH (else PASS with residue in Minor Notes). An **iteration dampener** tightens this from iteration 3 on (FLAG only on BLOCKER or ≥2 same-category FIX) to stop grinding on minor stutters, and an **edit-guard** (report over-correction sterility as a FIX, never reward padding) replaces the rejected "goosebumps FLAG". **The loop parser contract is unchanged** — the first line after `## VERDICT` is still exactly `PASS`/`FLAG`; severity lives inside the Critical Issues block as a prefix, so `draft.md` needs no logic change. This directly answers the over-correction risk of blanket default-FLAG. **(2) Four named Polish syntactic tells** — `pronoun flood` (drop redundant possessives), `rzeczownikomania/nominalizacja` (restore the verb), `genitive-stack` (collapse dopełniacz chains), `trailing verb` (EN dependent-clause word order). Single-sourced in `voice_corpus.md` §C2; named in 3b MOVE 0 (fix proactively) and 3c category J (gate). These catch calques that pass logically/clean — the layer the old general "translationese" wording missed.

**Agent 5 in-session — Opus 4.8 (2026-05-29)**
Agent 5 (Visual Storyteller) runs in Claude Code via `/visuals <slug>` — no API. Claude generates compact `05_prompts.md` entries (with `**Visual:**` field, 40–60 word descriptions) directly in-session, then `agent5_visuals.py --expand` injects CHARACTER_DESCRIPTION + STYLE_SUFFIX constants and exports phrase files. Prompt template lives in `workflows/pipeline/05_visuals.md` (single source of truth). The `--extract` flag extracts `docx/script_corrected.docx` → `md/script_corrected.md`; the `/visuals` skill calls this automatically when `script_corrected.docx` is present and uses the extracted file as its script source.

**Niche Trend Signals — Intelligence Agent ↔ Agent 8 integration**
Intelligence Agent writes a sidecar `outputs/intelligence/{week_label}_tag_signals.md` alongside its PPTX deck. Agent 8 auto-reads the latest sidecar via `_load_niche_signals()` and injects it as a supporting reference for the back half of the tag list (Tag #1 is always the exact-match primary keyword from the chosen title — Niche Signals never displace it). Integration fails soft — if no sidecar exists, Agent 8 works as before. **Pathing note:** Intelligence Agent's `PROJECT_ROOT` is `Path(__file__).parent.parent.parent` (three levels up) — `.parent.parent` resolves to `tools/` and breaks `outputs/intelligence/`.

## Quick Command Reference

All agents (except 0 and 1) take a **slug** — the output directory name under `outputs/videos_pl/`. Never pass the raw topic after Agent 1.

```bash
# Standard Python invocation:
PYTHONIOENCODING=utf-8 python tools/pipeline/agentN_name.py "<slug>"

# Script chain (Agent 3) — slash command in Claude Code:
#   /draft <slug> [architecture]
# Default architecture: Composite Portrait (~10–15 min, full second person). Pass a name to force another, e.g. /draft <slug> "Forensic Case Study".
# Runs 3a Drafter + the full 3b↔3c loop in-session (Opus 4.8, no API), finalizes 04_final.md.

# Script chain + adversarial native-ear debate (Agent Teams) — slash command in Claude Code:
#   /draft-team <slug> [architecture] [--sciezka]
# Same 3a + 3b↔3c loop in-session, but in-session 3c covers A–I only and a cold-context
# Native-Ear Critic teammate (Agent 3d) owns translationese (cat J) in a ≤3-round debate that
# replaces the manual Copilot pass. Opt-in (extra Opus context); /draft stays the default/fallback.

# Hook gate (Agent 4) — slash command in Claude Code:
#   /hook <slug>
# Scores the opening in-session (Opus 4.8, no API), then agent4_hook.py --apply splices the rewrite.

# Image prompt generation (Agent 5) — slash command in Claude Code:
#   /visuals <slug>
# Generates compact 05_prompts.md in-session (Opus 4.8, no API), then auto-runs agent5_visuals.py --expand.

# Publish package (Agent 8) — slash command in Claude Code:
#   /publish <slug>
# Builds the package in-session across 9 focused steps (Opus 4.8, no API).
# Bookends: agent8_publish.py --extract (narration) and --signals (autocomplete) before,
# --finalize (Q1–Q4 + tag trim + validate + docx) after. Legacy Gemini: --api.

# Thumbnail concepts (Agent 7) — slash command in Claude Code:
#   /thumbnails <slug>
# Generates 5 concepts in-session (Opus 4.8, no API), then agent7_thumbnails.py --render renders via Gemini.

# Intelligence agent:
PYTHONIOENCODING=utf-8 python tools/intelligence/intelligence.py

# List existing slugs:
ls outputs/videos_pl/
```

**Agents that take a TOPIC:** Agent 0 (`--topic` flag), Agent 1 (positional arg). All others take a slug.  
**Before running any agent:** verify the previous agent's output exists in `outputs/videos_pl/{slug}/md/`.  
**Parallel-safe after Agent 3 (script chain):** Agents 5, 6, and 8 can run simultaneously.  
**Agent 3 entry point:** `/draft <slug>` (Claude Code slash command — runs 3a + the full 3b↔3c loop in-session on Opus 4.8, finalizes `04_final.md`). The legacy `python tools/pipeline/agent3.py "<slug>"` runs only the Gemini-API 3b/3c loop over an existing `md/03a_draft.md` (`--api` fallback).  
**Hook gate entry point:** `/hook <slug>` (in-session scoring on Opus 4.8, then `agent4_hook.py --apply` splices the rewrite).  
**Publish entry point:** `/publish <slug>` (Claude Code slash command — 9 focused steps in-session on Opus 4.8, bracketed by `agent8_publish.py --extract`/`--signals`/`--finalize`). The legacy `python tools/pipeline/agent8_publish.py "<slug>" --api` runs the Gemini 3-pass orchestrator end-to-end.  
**Legacy agent3.py flags:** `--max-iterations N` (default 5), `--start-iteration N` — apply to the Gemini `--api` fallback only.  
**For flags and error recovery:** see the matching `workflows/pipeline/NN_name.md` file. Style guides are in `workflows/guides/`.

## Agent Chain

Complete pipeline — run in this order. Each agent reads its **Input** and writes its **Output** inside `outputs/videos_pl/{slug}/`.

All pipeline scripts live in `tools/pipeline/`. Intelligence Agent lives in `tools/intelligence/`.

| Agent | Script | Model | Input | Output |
| --- | --- | --- | --- | --- |
| 0 (optional) | `pipeline/agent0_materials.py` | Gemini 3.1 Pro | PDF + topic | `md/00_materials_insights.md` |
| 1 | `pipeline/agent1_research.py` | Gemini 3.1 Pro + PubMed | topic string | `md/01_research.md` |
| 2 | `pipeline/agent2_verify.py` | Gemini 3.1 Pro | `01_research.md` | `md/02_verified_research.md` |
| 3 (whole chain) | `/draft <slug>` (Claude Code slash command) | Opus 4.8 (Claude Code, in-session — no API) | `02_verified_research.md` | `03a_draft.md`, `03b_revised_iter*.md`, `03c_review_iter*.md` + `md/04_final.md` |
| 3a | (inside `/draft`) | Opus 4.8 (in-session — no API) | `02_verified_research.md` | `md/03a_draft.md` |
| 3b | (inside `/draft`; legacy `agent3b_revisor.py --api`) | Opus 4.8 in-session (legacy: Gemini 3.1 Pro) | `03a_draft.md` (+ `03c_review_iter{N-1}.md` on iter > 1) | `md/03b_revised_iter{N}.md` |
| 3c | (inside `/draft`; legacy `agent3c_reviewer.py --api`) | Opus 4.8 in-session (legacy: Gemini 3.1 Pro) | `03b_revised_iter{N}.md` | `md/03c_review_iter{N}.md` |
| 4 **(gate)** | `/hook <slug>` + `agent4_hook.py --apply` | Opus 4.8 in-session (legacy: `--api` Gemini) | `04_final.md` | `md/04_hook.md` + revised `04_final.md` in place + `docx/script.docx` |
| 5 | `/visuals <slug>` (Claude Code slash command) | Opus 4.8 (Claude Code, in-session — no API) | `04_final.md` (or `script_corrected.docx` if present) | `md/05_prompts.md` |
| 8 | `/publish <slug>` (Claude Code slash command; bookends `agent8_publish.py --extract/--signals/--finalize`) | Opus 4.8 (Claude Code, in-session — no API; legacy: `--api` Gemini + web scrape) | `script_corrected.docx` → `script.docx` → `04_final.md` + `02_verified_research.md` | `md/08_publish.md` + `docx/08_publish.docx` |
| 6 **(manual)** | `pipeline/agent6_images.py` | Gemini 3 Pro Image Preview | `05_prompts.md` | `images/image_*.png` |
| 6b **(QA, optional)** | `pipeline/agent6b_image_qa.py` | Gemini 2.5 Flash | `images/*.png` | `md/06_qa.md` |
| 7 **(manual)** | `/thumbnails <slug>` + `agent7_thumbnails.py --render` | Opus 4.8 concepts (in-session) + Gemini 3 Pro Image Preview render | `04_final.md` + `08_publish.md` | `md/07_prompts.md` + `thumbnails_no_grain/thumbnail_0N.png` × N |
| Align **(post-record)** | `pipeline/agent_align.py` | faster-whisper (local, free) | `voiceover/voiceover.wav` + `05_phrases.md` + `script_corrected.docx` / `script.docx` / `04_final.md` | `edit/subtitles.srt` + `edit/timeline.fcpxml` + `edit/preview.html` + `edit/alignment.json` |

**Parallel-safe after Agent 3 (script chain):** Agents 5 and 8 can run simultaneously. Agent 6 depends on Agent 5. Agent 7 can run in parallel with Agent 6.

**Manual agents — never run automatically:** Agents 6 and 7 generate images and thumbnails (cost + time). Always stop the pipeline after Agent 8 completes and wait for explicit instruction before running either.

**Align Agent — Forced Alignment & DaVinci Bundle:** Runs *after* voiceover recording (Studio One → exported WAV at `voiceover/voiceover.wav`). Uses faster-whisper to align audio to the known script, then emits an SRT + FCPXML the user imports into DaVinci Resolve. Eliminates ~2-4 hours of manual subtitle syncing and image placement per video. Local-only, no API costs. Naming: file is `tools/pipeline/agent_align.py` (no number — avoids confusion with the unrelated `intelligence.py` analysis tool). See `workflows/pipeline/align.md` and one-time `workflows/guides/davinci_subtitle_preset.md` for setup.

**Quality gate — Agent 4 (`/hook <slug>`):** Scores opening hook in-session on Opus 4.8 (Tier 1: ≥8/10 at 37 words; Tier 2: ≥7/10 at 200 words), then `agent4_hook.py --apply` splices the rewrite deterministically. Verdict must be `RECORD` before recording voiceover. Modifies `04_final.md` in place; backup saved to `04_final.bak.md`. Also exports `docx/script.docx` — edit this in Word/Copilot 365/Gemini and save as `docx/script_corrected.docx`; all downstream agents (Agent 8, /visuals, Align) auto-detect the corrected file.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
