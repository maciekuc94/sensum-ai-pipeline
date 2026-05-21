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

**Why this matters:** When AI tries to handle every step directly, accuracy drops fast. If each step is 90% accurate, you're down to 59% success after just five steps. By offloading execution to deterministic scripts, you stay focused on orchestration and decision-making where you excel.

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

**What goes where:**
- **Deliverables**: Final outputs go to cloud services (Google Sheets, Slides, etc.) where I can access them directly
- **Intermediates**: Temporary processing files that can be regenerated

**Directory layout:**
```
.tmp/                    # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/
  pipeline/              # Agent scripts 0–6, 8–10 + align (the full production chain)
  intelligence/          # Agent 11 + intelligence module (analyzer, collector, db, slide_builder, vision)
  dev/                   # Support tools: add_grain.py
  utils.py               # Shared utilities (all agents import from here)
workflows/
  pipeline/              # Numbered SOPs 00–11 (one per agent step)
  guides/                # style_guide.md, style_guide_images.md, narrative_architectures.md
outputs/
  videos/                # One folder per produced video (slug-named)
  channel_assets/        # Shared brand assets (logo, fonts, colors)
  intelligence/          # Agent 11 analysis outputs
.env                     # API keys and environment variables (NEVER store secrets anywhere else)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Design Standards

**Color palette:** Two colors only — #F4E5CA (Sage Beige, exclusive background, always described as aged vellum paper texture) and #582F0E (Dark Brown, all ink lines, cross-hatching, and silhouettes). No other colors permitted in any generated visual, slide, chart, or asset. The illustration style is Scientific Etching: fine-liner ink sketches with cross-hatching for depth, referencing 19th-century scientific journal engravings. No gradients, no fills, no watercolor. No text, no labels, no words in any generated image.

## Technical Notes

**Claude API routing**
`query_claude()` in `tools/utils.py` uses the direct Anthropic API (`anthropic.Anthropic` + `ANTHROPIC_API_KEY`), not Vertex AI. `claude-opus-4-7` is not available in the `visual-studio-code-494218` GCP project via Vertex AI — do not revert to `AnthropicVertex` for Claude calls.

**Windows terminal encoding**
When running pipeline scripts via Bash on this machine, prefix with `PYTHONIOENCODING=utf-8` to avoid codec errors on Unicode characters (e.g., arrows in print statements):

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent3.py "slug"
```

**PubMed zero results**
The auto-derived PubMed query sometimes returns zero results (query too specific or wrong MeSH terms). This is acceptable if the Gemini research section contains solid peer-reviewed references. Agent 2 verifies claims against scientific literature regardless of PubMed results — proceed to Agent 2 as normal.

**Research-invisible script voice (2026-05-21)**
Scripts must read as a warm therapist talking to one person — research entirely invisible. No researcher names, no study years, AND no research-framing verbs: forbidden in any form are "researchers found / studies show / scientists discovered / research shows / neuroscience has found / one study / a meta-analysis / the data shows / according to research / the science is clear / psychologists call this". The channel is research-*grounded* (Agents 0/1/2 still do PubMed verification) but never research-*forward* in the script. Findings appear as observations about being human, spoken in the speaker's own voice. The viewer trusts the speaker, not the citation. All real bibliographic citations live in the YouTube description (Agent 8 output) — never in the spoken narration.

**Number policy:** Round, framed numbers only ("roughly half", "most people"). Banned in scripts: decimals (0.62), effect sizes (d = X, r = X), p-values, study counts ("94 experiments"), participant counts ("8,000 people"), methodology terms (pre-registered, double-blind, longitudinal, meta-analysis). If a number doesn't land emotionally as plain English, cut it.

**Jargon policy:** Plain language first. Describe the phenomenon in everyday words. Name a scientific term only if (a) the name itself is memorable and (b) it appears once, late, after the idea has already landed. Never use the jargon-then-translation pattern ("ego depletion — the depletion of…").

**Darwin exception (Historical Reversal architecture only):** Scripts using Historical Reversal may name Darwin as a historical narrative device (the "wrong view" being overturned). This is the structural antagonist of the architecture, not an inline citation. No other historical figures or researchers may be named.

**Image generation — Agent 9**
Agent 9 uses `gemini-3-pro-image-preview` via Vertex AI with `location="global"` (regional endpoints return 404 for this model). The API is `generate_content(response_modalities=["IMAGE"])` — not `generate_images()`. The negative prompt is embedded in the prompt text, not passed as a parameter. Aspect ratio is handled post-generation via `ImageOps.pad()` (pillarbox with #F4E5CA sage beige — no stretching, no cropping). Image prompts specify `#F4E5CA` sage beige background directly in `STYLE_SUFFIX` in `utils.py`; `_enforce_background_color` also runs automatically after each image is saved as a safety net. The `--transparent`/`rembg` path was removed — see plan `enumerated-doodling-lovelace.md` F4.

**Thumbnail generation — agent10_thumbnails.py**
Run after Agent 8 (needs `07_publish_package.md`) and Agent 9 is optional. Two-step: Claude Opus 4.7 generates 5 distinct thumbnail concepts (one per composition type), then Gemini renders each at 1920×1080. Run with `--no-grain` — grain is applied manually in Canva after adding the title text overlay. Prompts are saved to `thumbnail_prompts.md` for reference. Flags: `--no-grain` (recommended), `--reuse-prompts` (skip Claude step, reload saved prompts), `--indices 1,4` (only generate those prompt numbers), `--count 3` (generate N variations per prompt — named `thumbnail_01_v1.png` etc). Rate limit: 20s between Vertex AI calls. Gemini is stochastic — exact pixel-identical re-runs are impossible; `--reuse-prompts` reuses the same prompt text but produces new renders.

**Agent 8 web scraping**
`agent8_publish.py` scrapes Google Autocomplete and YouTube search results for SEO tags. This is fragile — if Google/YouTube changes their HTML, the scraper returns an empty tag list silently and the rest of the output is fine. The YouTube competitor-tag scraper currently returns 0 results most runs (YouTube payload shape changed — `JSONDecodeError: Extra data`); Agent 8 still produces a valid package because it falls back on Niche Trend Signals + autocomplete + script context. If the tags section in `07_publish_package.md` looks empty or short, the scraper has broken; add tags manually.

**Agent 8 publish package — output format (locked)**
Agent 8 produces three locked sections inside `07_publish_package.md`. Do not loosen these without explicit instruction:

- **Description** — TWO short paragraphs, under 120 words total. Paragraph 1 opens with 3–6 concrete sensory observations / fragment-style behaviours (e.g. "Starting over. Again. The gym bag by the door. The journal with three entries.") and ends with one soft reframe sentence. Paragraph 2 starts exactly with "In this video, we explore" and names 3–5 actual concepts from the script translated into everyday language — NO jargon (no "ego depletion", no "intention-behavior gap", no "self-discrepancy theory"). Closes with one warm sentence about understanding yourself. Hard rules: no researcher names, no study years, no second-person preachy lines.
- **References** — citation only, one per line, leading bullet `•`, ending with `(Year).` and a period. NO summary sentence after the year. Format: `• Concept Label — Optional Qualifier: Author, A., et al. (Year).`
- **Hashtags** (end of description block, before `---`) — exactly 3, single-word, lowercase, with `#` prefix. First is always `#sensum`. Other 2 are the strongest single-word topical hashtags.
- **YouTube Tags** — exactly 15, single-word only (no spaces, no hyphens). Include `SENSUM` (uppercase) ONCE as the only brand tag — never duplicate as `sensum`. Tag selection is principle-based (no banned-word list): each tag must pass the test "would a real person searching for this video type this exact word into YouTube?" Tag the underlying concept the script illustrates, never a script metaphor / prop (cookie, GPS, village, battery, door, strangers).
- **Shorts tags** — same 15-single-word, single-`SENSUM`, principle-based rule as the main tags, tuned to each Short's specific angle.

The Agent 8 metadata prompt frames Claude as a senior YouTube SEO and tags expert (not a generic metadata specialist) — keep that framing if editing the prompt.

**Niche Trend Signals — Agent 11 ↔ Agent 8 integration**
Agent 11 (weekly niche intelligence) writes a sidecar **`outputs/intelligence/{week_label}_tag_signals.md`** alongside its PPTX deck. The file is single-word-only and has four sections: Top Trending Tags / Top Trending Title Topics / Top Title Words / Content Gaps. Agent 8 automatically reads the latest sidecar (newest by filename sort) via `_load_niche_signals()` and injects it into the metadata prompt as `## Niche Trend Signals (latest weekly intelligence report)`. The prompt treats this block as the **highest-priority reference** for tag selection. The integration fails soft — if no sidecar exists, Agent 8 still works as before. Agent 11's `PROJECT_ROOT` is `Path(__file__).parent.parent.parent` (three levels up, not two) — a prior bug used `.parent.parent` which resolved to `tools/` and broke `outputs/intelligence/` pathing.

## Quick Command Reference

All agents (except 0 and 1) take a **slug** — the output directory name under `outputs/videos/`. Never pass the raw topic after Agent 1.

```bash
# Standard invocation:
PYTHONIOENCODING=utf-8 python tools/pipeline/agentN_name.py "<slug>"

# Intelligence agent:
PYTHONIOENCODING=utf-8 python tools/intelligence/agent11_intelligence.py

# List existing slugs:
ls outputs/videos/
```

**Agents that take a TOPIC:** Agent 0 (`--topic` flag), Agent 1 (positional arg). All others take a slug.  
**Before running any agent:** verify the previous agent's output exists in `outputs/videos/{slug}/md/`.  
**Parallel-safe after Agent 4a:** Agents 5, 6, and 8 can run simultaneously.  
**For flags and error recovery:** see the matching `workflows/pipeline/NN_name.md` file. Style guides are in `workflows/guides/`.

## Agent Chain

Complete pipeline — run in this order. Each agent reads its **Input** and writes its **Output** inside `outputs/videos/{slug}/`.

All pipeline scripts live in `tools/pipeline/`. Agent 11 lives in `tools/intelligence/`.

| Agent | Script | Model | Input | Output |
| --- | --- | --- | --- | --- |
| 0 (optional) | `pipeline/agent0_materials.py` | Gemini 3.1 Pro | PDF + topic | `md/00_materials_insights.md` |
| 1 | `pipeline/agent1_research.py` | Gemini 3.1 Pro + PubMed | topic string | `md/01_research.md` |
| 2 | `pipeline/agent2_verify.py` | Gemini 3.1 Pro | `01_research.md` | `md/02_verified_research.md` |
| 3 | `pipeline/agent3.py` | runs 3a → 3n → 3b → 3c | slug | all `03_*.md` files |
| 3a | `pipeline/agent3a_draft.py` | Claude Opus 4.7 | `02_verified_research.md` | `md/03a_draft.md` |
| 3n | `pipeline/agent3n_novelty.py` | Claude Sonnet 4.6 | `03a_draft.md` + prior corpus | `md/03_novelty_report.md` + revised `03a_draft.md` |
| 3b | `pipeline/agent3b_critic.py` | Claude Sonnet 4.6 | `03a_draft.md` | `md/03b_critique.md` |
| 3c | `pipeline/agent3c_rewrite.py` | Claude Opus 4.7 | `03a_draft.md` + `03b_critique.md` | `md/03_script_draft.md` |
| 4a | `pipeline/agent4a_edit.py` | Claude Sonnet 4.6 | `03_script_draft.md` | `md/04_script_final.md` |
| 4b **(gate)** | `pipeline/agent4b_hook.py` | Claude Sonnet 4.6 | `04_script_final.md` | `md/04b_hook_score.md` + revised `04_script_final.md` in place |
| 5 | `pipeline/agent5_visuals.py` | Claude Opus 4.7 | `04_script_final.md` | `md/05_image_prompts.md` |
| 6 | `pipeline/agent6_narration.py` | deterministic | `04_script_final.md` | `md/06_script_narration.md` |
| 8 | `pipeline/agent8_publish.py` | Claude Sonnet 4.6 + web scrape | `04`, `06`, `02` outputs | `md/07_publish_package.md` |
| 9 **(manual)** | `pipeline/agent9_images.py` | Gemini 3 Pro Image Preview | `05_image_prompts.md` | `images/image_*.png` |
| 10 **(manual)** | `pipeline/agent10_thumbnails.py` | Claude Opus 4.7 + Gemini 3 Pro Image Preview | `04_script_final.md` + `07_publish_package.md` | `thumbnails/thumbnail_0N.png` × 5 |
| Align **(post-record)** | `pipeline/agent_align.py` | faster-whisper (local, free) | `voiceover/voiceover.wav` + `05_image_phrases.md` + `06_script_narration.md` | `edit/subtitles.srt` + `edit/timeline.fcpxml` + `edit/preview.html` + `edit/alignment.json` |

**Parallel-safe after Agent 4a:** Agents 5, 6, and 8 can run simultaneously. Agent 9 depends on Agent 5. Agent 10 depends on Agent 8 (for `07_publish_package.md`) and can run in parallel with Agent 9.

**Manual agents — never run automatically:** Agents 9 and 10 generate images and thumbnails (cost + time). Always stop the pipeline after Agent 8 completes and wait for explicit instruction before running either.

**Align Agent — Forced Alignment & DaVinci Bundle:** Runs *after* voiceover recording (Studio One → exported WAV at `voiceover/voiceover.wav`). Uses faster-whisper to align audio to the known script, then emits an SRT + FCPXML the user imports into DaVinci Resolve. Eliminates ~2-4 hours of manual subtitle syncing and image placement per video. Local-only, no API costs. Naming: file is `tools/pipeline/agent_align.py` (no number — avoids confusion with the unrelated `agent11_intelligence.py` analysis tool). See `workflows/pipeline/align.md` and one-time `workflows/guides/davinci_subtitle_preset.md` for setup.

**Quality gate — Agent 4b:** Scores opening hook (Tier 1: ≥8/10 at 37 words; Tier 2: ≥7/10 at 200 words). Verdict must be `RECORD` before recording voiceover. Modifies `04_script_final.md` in place; backup saved to `04_script_final.bak.md`.

**Novelty check — Agent 3n:** Compares new draft against all prior `outputs/videos/*/md/06_script_narration.md` files (the shipped corpus). First video ever produces `SKIPPED` verdict automatically — that is correct behavior.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
