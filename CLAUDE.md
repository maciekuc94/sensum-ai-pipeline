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

**Banned-phrase lists for Polish are intentionally empty** in both Polish style guides — they fill in *empirically* as the readers / doctrine gate and the user flag real cringe-phrases from shipped Polish scripts. The English guides accumulated their banned-phrase lists across dozens of scripts; the Polish guides start blank and grow the same way.

**Research is still in English.** Agents 1/2 produce `01_research.md` and `02_verified_research.md` in English (PubMed + Europe PMC + Gemini sources are English-language). Polish script agents read English research and produce Polish output — this is intentional, not a bug. Do not localize Agents 0/1/2.

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
.claude/
  commands/              # Slash commands (user-invoked): /draft /hook /visuals /package /publish (/draft + /publish default to Agent-Teams panels; auto-fallback in-session)
  agents/                # Agent-Teams teammates (script-reader: cohesion + voice/lyricism cold readers; native-copy critic; publish specialists)
  skills/                # Auto-invoked skills (model picks via `description`): doctrine guards (scientific-etching-guard, native-voice-guard) + natural-language routers (render-images, write-script, score-hook, package-thumbnail, publish-package) that fire on plain-language requests outside the slash commands
tools/
  pipeline/              # Agent scripts 0–8 + align (the full production chain)
  dev/                   # Support tools: add_grain.py
  utils.py               # Shared utilities (all agents import from here)
  research_sources.py    # Peer-reviewed source aggregation for Agent 1 (PubMed + Europe PMC)
workflows/
  pipeline/              # Numbered SOPs 00–08 (one per pipeline agent), plus align.md
  guides/                # style_guide.md, style_guide_images.md, narrative_architectures.md
outputs/
  videos_pl/             # Polish-channel videos (one folder per slug). videos_en/ exists for legacy English content.
  channel_assets/        # Shared brand assets (logo, fonts, colors)
.env                     # API keys and environment variables (NEVER store secrets anywhere else)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Design Standards

**Color palette:** Two colors only — #F4E5CA (Sage Beige, exclusive background, described in prompts as a **flat solid sage beige background with no texture**; the paper-grain look is applied in post via `add_grain.py`, never requested in the prompt) and #582F0E (Dark Brown, all ink lines, cross-hatching, and silhouettes). No other colors permitted in any generated visual, slide, chart, or asset. The illustration style is Scientific Etching: fine-liner ink sketches with cross-hatching for depth, referencing 19th-century scientific journal engravings. No gradients, no fills, no watercolor. No text, no labels, no words in any generated image. No decorative borders or frames around the image — full-bleed composition.

## Technical Notes

Operative rules live here; the *why/history* behind each lives in auto-memory (`project_*.md`, lazy-loaded), full specs in `workflows/guides/` + `workflows/pipeline/` + `docs/`. Pointers below are canonical — don't re-narrate decisions here.

**No Claude API — everything in-session (Opus 4.8).** Zero Anthropic API calls. `/draft`, `/hook`, `/visuals`, `/package`, `/publish` all run in-session; `query_claude()` removed, `ANTHROPIC_API_KEY` not required. Gemini (Vertex AI) only for research (0/1/2), image render (6, package-render), QA (6b). In-session prompts single-sourced in `workflows/pipeline/03{a,b,c,d,e}_*.md`, `04_hook.md`, `05_visuals.md`, `07_package.md`, `08_publish.md`. Legacy Gemini paths survive behind `--api`.

**Windows encoding.** Prefix Bash pipeline runs with `PYTHONIOENCODING=utf-8` (avoids Unicode codec errors), e.g. `PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "slug"`.

**PubMed zero results = OK.** Auto-derived query sometimes returns nothing from PubMed; fine — Europe PMC runs in parallel as a second peer-reviewed provider (`research_sources.py`) and Gemini adds refs. Agent 2 verifies regardless — proceed normally.

### Script voice — the non-negotiables

- **Research-invisible.** Warm therapist talking to one person; research entirely invisible (channel is research-*grounded*, never research-*forward*). No researcher names / study years / "badania pokazują" / decimals / counts in narration; all citations live in the Agent 8 description. Forbidden PL research-framing phrases + rationale: memory `feedback_no_inline_citations.md`; spec `style_guide.md`.
- **Number policy.** Round, framed numbers only ("roughly half", "most people"). Banned: decimals, effect sizes, p-values, study/participant counts, methodology terms. Even a round number stated as fact ("blisko połowy…") reads as an uncited stat — describe the phenomenon instead. If a number doesn't land emotionally, cut it.
- **Jargon policy.** Plain language first; name a scientific term only if it's memorable AND appears once, late, after the idea landed. Never jargon-then-translation.
- **Darwin exception** (Historical Reversal only): Darwin may be named as the structural antagonist (the "wrong view"). No other figures/researchers.
- **Clinical-anchor exception** (any architecture): exactly one established clinical anchor per script may be framed „Badania nad [efektem] pokazują, że…" (e.g. „efekt świeżego startu"). No author/year/number/methodology alongside it; a second research-framing frame is caught by the doctrine gate (`03e`).
- **Permission Practice** (OPTIONAL since 2026-06-06 — was mandatory): include micro-practices **only if a real concrete move arises from the script's central image** — never bolted on. If the topic doesn't carry one, go straight to the recognition close. When present: flowing prose („Czasem wystarczy…" anaphora), ~1–4 practices, **never** a numbered list (banned everywhere); two registers — somatic (default) vs strategic („beat ścieżki", topic-triggered external move; `--sciezka` forces). **Recognition close stays mandatory — always the last word.** Drafter judges fit; Czytelnik 1 flags a bolted-on PP as a seam. Spec: `narrative_architectures.md` „Sekcja Permission Practice (opcjonalna)" / „Dwa rejestry". Rationale: memory `project_path_beat_register.md`, `project_pp_prose_and_style_calibration.md`.
- **Bezrodzajowość + ciepło.** Address the viewer gender-neutrally (present-tense / impersonal default; inner quote „coś poszło źle"); speak DO the person, never describe the system. Spec: `voice_corpus.md` §0 + §G; enforced by Czytelnik 2 (głos/ciepło) + doctrine gate (gender/person). Rationale: memory `project_voice_doctrine.md`.
- **Craft calibration.** One central metaphor per script (don't stack); at most 2–3 attention-imperatives („Zwróć uwagę"/„Popatrz"/…); no uncited round-number stat. Enforced in `style_guide.md` / 3a / readers / doctrine gate. Rationale: memory `project_pp_prose_and_style_calibration.md`.

### Script chain (Agent 3)

- **Architecture per topic.** `/draft` runs an in-session selector (Step 1.6) before 3a — scores all 5 architectures on topic-fit, writes `md/03_architecture.md`. Composite Portrait is eligible but no longer the blind default; anti-repeat is a tiebreak only; `$2` forces a named architecture. The `ARCHITECTURE:` line is stripped from the recorded `04_final.md`/`script.docx`. Spec: `03_architecture_select.md`. Rationale: memory `project_architecture_selection.md`, `project_composite_portrait.md`.
- **Flowing-essay chain (2026-06-06 redesign).** Target voice: **płynny esej-voiceover z nutą liryzmu, spójny** (`style_guide.md` §2.5, `voice_corpus.md` §A — płynący pasaż na czele; default texture is connected prose, NOT staccato fragments). Chain in-session: **3a Drafter** (voice-first, flowing texture, PP optional) → copy to `04_working.md` → **panel of 2 cold readers** (Czytelnik 1 spójność/przepływ → `03c_reviewer.md`; Czytelnik 2 głos/liryzm/kalki → `03d_native_ear.md`) → **3b Integrator** rewrites the WHOLE script (one hand) from both reader logs → loop until **both readers say `PŁYNIE`** (soft cap ~5 rounds, else ship-with-WARNING) → **thin doctrine gate** (`03e_doctrine_gate.md`) → `04_final.md`. Readers give **holistic editorial feedback, not categorical triage** (no BLOCKER/FIX/WATCH, no iteration-dampener, no anti-sterility brake on polishing). The old defensive 3c (categories A–K) is retired; its non-negotiables live in `03e`. Spec: `03{a,b,c,d,e}_*.md` + `voice_corpus.md`. Rationale: spec `docs/superpowers/specs/2026-06-06-flowing-essay-script-chain-design.md`. Reversibility: `docs/reversibility.md`.
- **Agent Teams (default in `/draft` + `/publish`).** `/draft` spawns **two cold-context `script-reader` teammates** (lens spójność + lens głos-liryzm), each reading `04_working.md` cold and giving whole-script editorial feedback, debating fixes across rounds; the lead (Integrator) owns every rewrite so the voice stays one hand. Panel passes when **both** verdicts are `PŁYNIE` (parser: first non-blank line after `## VERDICT` is `PŁYNIE`/`REWORK`). `/publish` uses 3 specialist generators + a cold-context Native-Copy Critic (8d). Both **auto-fall back to fully in-session (no team) when Agent Teams is unavailable** — no separate command, no `--solo` flag. Need `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` (committed `.claude/settings.json`), and require **one team at a time** (mandatory teardown — a lingering team blocks the other). Full spec: `docs/agent_teams_reference.md`.

### Images & publish

- **Agent 6 (images).** `gemini-3-pro-image-preview` via Vertex AI, `location="global"` (regional → 404); API `generate_content(response_modalities=["IMAGE"])`; negative prompt embedded in text; aspect via `ImageOps.pad()` (pillarbox #F4E5CA). Background set in `STYLE_SUFFIX` (`utils.py`) + `_enforce_background_color` safety net (catches solid flats only — Agent 6b catches texture/frames). **Never** put texture words (vellum / aged paper / parchment / grain) in a prompt — Gemini renders them literally; ask for a flat solid background, `add_grain.py` adds grain in post. Rationale: memory `project_color_master.md`, `feedback_no_texture_in_prompts.md`, `feedback_no_head_crop.md`.
- **`--indices`** (`agent6_images.py --generate --indices "22,26,97"`) regenerates only the listed 1-based images, overwriting in place — re-roll Agent 6b failures without re-spending on the full set. **Agent 6b QA** (`agent6b_image_qa.py`) validates every image vs the style contract (Gemini 2.5 Flash), writes `md/06_qa.md`; `--retry` regenerates failures (one attempt); never deletes. **Package (was Thumbnails)** `/package <slug>` → 3 strategie {tytuł+napis+koncept} + render 3 via `agent7_thumbnails.py --render --no-grain` (grain + napis-overlay added manually in Canva; 20s rate limit). Runs after `/hook`, before `/publish`; chosen title feeds `/publish` STEP 1 via `07_package.md`. Napis never enters the Gemini prompt (no-text contract). Flags/rubrics: `workflows/pipeline/06*.md`, `07_package.md`.
- **Agent 8 publish** runs in-session across 9 single-responsibility steps (titles / description+3 hashtags / timestamps / long-form tags / bibliography / shorts clip-selection / shorts titles / shorts descriptions / shorts tags). Bookends: `--extract` (narration → `.tmp/`), `--signals` (autocomplete; `--topic="<polish seed>"`), `--finalize` (Q1–Q4 + tag trim + validate + docx). Spec: `08_publish.md`.
- **Locked publish output:** Tag #1 = exact-match primary keyword from the chosen title; 5–8 multi-word tags (single-word prohibited except `SENSUM`-once); exactly 3 hashtags (`#sensum` first); description exactly 5 sentences; bibliography heading `Badania i źródła:`; Shorts clips tagged `[Q1]–[Q4]` (`[Q?]` = paraphrase slipped in, `[MISSING]` = Short lacks its clip block — fix both before publishing). Autocomplete scraper is fragile — thin tags = it failed; package still valid via script, add tags manually. Rationale: memory `project_long_tail_tags.md`, `project_shorts_quarter_markers.md`, `feedback_bibliography_verified_only.md`, `feedback_no_prepublication_checklist.md`.
- **Agent 5 (visuals)** in-session: generates compact `05_prompts.md` (`**Visual:**` field, 40–60 words), then `agent5_visuals.py --expand` injects CHARACTER_DESCRIPTION + STYLE_SUFFIX and exports phrase files. `--extract` pulls `script_corrected.docx` → md (auto-called when the corrected docx is present). Spec: `05_visuals.md`.

## Quick Command Reference

All agents except 0/1 take a **slug** (output dir under `outputs/videos_pl/`), never the raw topic. Agent 0 takes `--topic`, Agent 1 a positional topic string. Before running any agent, verify the previous agent's output exists in `outputs/videos_pl/{slug}/md/`. Command *behavior/flags* live in the `### ` notes above + `workflows/pipeline/NN_name.md`; this is just the syntax.

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agentN_name.py "<slug>"   # standard Python agent (Windows: keep the prefix)
/draft <slug> [architecture] [--sciezka]   # Agent 3 — selector + 3a Drafter + 2 cold readers (spójność+głos) ↔ Integrator loop (miękki ~5) + doctrine gate; auto-fallback in-session
/hook <slug>                               # Agent 4 hook gate → agent4_hook.py --apply
/visuals <slug>                            # Agent 5 → agent5_visuals.py --expand
/publish <slug>                            # Agent 8 — 9 steps + Native-Copy Critic 8d (default); bookends --extract / --signals / --finalize; auto-fallback in-session
/package <slug>                            # Strateg opakowania (tytuł+napis+miniatura) → render 3; po /hook, przed /publish
ls outputs/videos_pl/                      # list existing slugs
```

**Parallel-safe after Agent 3:** Agents 5 and 8 simultaneously (6 depends on 5); `/package` runs after `/hook`, before `/publish`. **Legacy Gemini paths** sit behind `--api` (`agent3.py` flags `--max-iterations N` / `--start-iteration N` apply there only); the in-session slash commands are the default entry points. Style guides: `workflows/guides/`.

## Agent Chain

Complete pipeline — run in this order. Each agent reads its **Input** and writes its **Output** inside `outputs/videos_pl/{slug}/`.

All pipeline scripts live in `tools/pipeline/`.

| Agent | Script | Model | Input | Output |
| --- | --- | --- | --- | --- |
| 0 (optional) | `pipeline/agent0_materials.py` | Gemini 3.1 Pro | PDF + topic | `md/00_materials_insights.md` |
| 1 | `pipeline/agent1_research.py` | Gemini 3.1 Pro + PubMed + Europe PMC | topic string | `md/01_research.md` |
| 2 | `pipeline/agent2_verify.py` | Gemini 3.1 Pro | `01_research.md` | `md/02_verified_research.md` |
| 3 (whole chain) | `/draft <slug>` (Claude Code slash command; Drafter → 2 cold readers ↔ Integrator loop → doctrine gate; auto-fallback in-session) | Opus 4.8 (in-session lead + 2 teammate contexts — no API) | `02_verified_research.md` | `03_architecture.md`, `03a_draft.md`, `04_working.md`, `03_read_cohesion_iter*.md`, `03_read_voice_iter*.md`, `03b_revised_iter*.md` + `md/04_final.md` |
| 3a | (inside `/draft`) | Opus 4.8 (in-session — no API) | `02_verified_research.md` | `md/03a_draft.md` |
| 3b Integrator | (inside `/draft`) one-hand whole-script rewrite | Opus 4.8 in-session — no API | `04_working.md` + both reader logs (round N) | `md/03b_revised_iter{N}.md` → `04_working.md` |
| 3c Czytelnik 1 (spójność) | (inside `/draft`) `script-reader` teammate | Opus 4.8 (teammate — no API) | `04_working.md` | `md/03_read_cohesion_iter{N}.md` |
| 3d Czytelnik 2 (głos/liryzm) | (inside `/draft`) `script-reader` teammate | Opus 4.8 (teammate — no API) | `04_working.md` | `md/03_read_voice_iter{N}.md` |
| 3e doctrine gate | (inside `/draft`) lead in-session | Opus 4.8 — no API | final `04_working.md` | `md/04_final.md` (strips `ARCHITECTURE:`) |
| 4 **(gate)** | `/hook <slug>` + `agent4_hook.py --apply` | Opus 4.8 in-session (legacy: `--api` Gemini) | `04_final.md` | `md/04_hook.md` + revised `04_final.md` in place + `docx/script.docx` |
| 5 | `/visuals <slug>` (Claude Code slash command) | Opus 4.8 (Claude Code, in-session — no API) | `04_final.md` (or `script_corrected.docx` if present) | `md/05_prompts.md` |
| 8 | `/publish <slug>` (Claude Code slash command; 3 specialist generators + Native-Copy Critic 8d by default, auto-fallback in-session; bookends `agent8_publish.py --extract/--signals/--finalize`) | Opus 4.8 (in-session lead + 4 teammate contexts — no API; legacy: `--api` Gemini + web scrape) | `script_corrected.docx` → `script.docx` → `04_final.md` + `02_verified_research.md` | `md/08_publish.md` + `docx/08_publish.docx` + `md/08d_nativecopy_iter*.md` |
| 8d | (inside `/publish`) `native-copy-critic` teammate | Opus 4.8 (Claude Code teammate — no API) | `md/08_working.md` | `md/08d_nativecopy_iter{N}.md` |
| 6 **(manual)** | `pipeline/agent6_images.py` | Gemini 3 Pro Image Preview | `05_prompts.md` | `images/image_*.png` |
| 6b **(QA, optional)** | `pipeline/agent6b_image_qa.py` | Gemini 2.5 Flash | `images/*.png` | `md/06_qa.md` |
| 7 → Package **(manual)** | `/package <slug>` + `agent7_thumbnails.py --render` | Opus 4.8 strategies (in-session) + Gemini 3 Pro Image render | `04_final.md` (script) | `md/07_package.md` + `md/07_prompts.md` + `thumbnails_no_grain/thumbnail_0N.png` × 3 |
| Align **(post-record)** | `pipeline/agent_align.py` | faster-whisper (local, free) | `voiceover/voiceover.wav` + `05_phrases.md` + `script_corrected.docx` / `script.docx` / `04_final.md` | `edit/subtitles.srt` + `edit/timeline.fcpxml` + `edit/preview.html` + `edit/alignment.json` |

**Parallel-safe after Agent 3 (script chain):** Agents 5 and 8 can run simultaneously. Agent 6 depends on Agent 5. `/package` runs after `/hook` and before `/publish` (it feeds the title), independent of Agents 5/6.

**Manual agents — never run automatically:** `/package` (3 thumbnails + strategies) and Agent 6 (images) cost render credits + time. `/package` runs after `/hook` and before `/publish` (it feeds the title); Agent 6 after `/visuals`. Only run either on explicit instruction.

**Align Agent — Forced Alignment & DaVinci Bundle:** Runs *after* voiceover recording (Studio One → exported WAV at `voiceover/voiceover.wav`). Uses faster-whisper to align audio to the known script, then emits an SRT + FCPXML the user imports into DaVinci Resolve. Eliminates ~2-4 hours of manual subtitle syncing and image placement per video. Local-only, no API costs. Naming: file is `tools/pipeline/agent_align.py` (no number — it's a post-record satellite, not a numbered pipeline stage). See `workflows/pipeline/align.md` and one-time `workflows/guides/davinci_subtitle_preset.md` for setup.

**Quality gate — Agent 4 (`/hook <slug>`):** Scores opening hook in-session on Opus 4.8 (Tier 1: ≥8/10 at 37 words; Tier 2: ≥7/10 at 200 words), then `agent4_hook.py --apply` splices the rewrite deterministically. Verdict must be `RECORD` before recording voiceover. Modifies `04_final.md` in place; backup saved to `04_final.bak.md`. Also exports `docx/script.docx` — edit this in Word/Copilot 365/Gemini and save as `docx/script_corrected.docx`; all downstream agents (Agent 8, /visuals, Align) auto-detect the corrected file.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
