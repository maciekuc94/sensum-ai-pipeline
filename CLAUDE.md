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

**Color palette:** Two colors only — #F4E5CA (Sage Beige, exclusive background, described in prompts as a **flat solid sage beige background with no texture**; the paper-grain look is applied in post via `add_grain.py`, never requested in the prompt) and #582F0E (Dark Brown, all ink lines, cross-hatching, and silhouettes). No other colors permitted in any generated visual, slide, chart, or asset. The illustration style is Scientific Etching: fine-liner ink sketches with cross-hatching for depth, referencing 19th-century scientific journal engravings. No gradients, no fills, no watercolor. No text, no labels, no words in any generated image. No decorative borders or frames around the image — full-bleed composition.

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

**Permission Practice closing section (2026-05-24, locked)**
Every script ends with a mandatory Permission Practice section sitting between the architecture body and the recognition close. Exactly **4 numbered embodied micro-practices** — somatic acts, noticing, naming, breathing, micro-thresholds. Never optimization, scheduling, list-making, "talk to a therapist", "set boundaries", or anything that could appear unchanged on a productivity blog. Header template: *"Four things you can [verb], when [trigger]:"* — verb varies (do/try/notice/give yourself/carry with you); trigger ties to the script's specific mechanism. The recognition close still has the FINAL word — the tips are a beat, not the destination. Full spec lives in `workflows/guides/narrative_architectures.md` under "Permission Practice closing section (universal)". Agent 3a generates it; Agent 4a verifies (does not regenerate); Agent 3b/3c flag and rewrite optimization-flavored tips. Title doctrine unchanged — still identity-provocation only; tips are inside-the-video payoff, not click bait.

**Number policy:** Round, framed numbers only ("roughly half", "most people"). Banned in scripts: decimals (0.62), effect sizes (d = X, r = X), p-values, study counts ("94 experiments"), participant counts ("8,000 people"), methodology terms (pre-registered, double-blind, longitudinal, meta-analysis). If a number doesn't land emotionally as plain English, cut it.

**Jargon policy:** Plain language first. Describe the phenomenon in everyday words. Name a scientific term only if (a) the name itself is memorable and (b) it appears once, late, after the idea has already landed. Never use the jargon-then-translation pattern ("ego depletion — the depletion of…").

**Darwin exception (Historical Reversal architecture only):** Scripts using Historical Reversal may name Darwin as a historical narrative device (the "wrong view" being overturned). This is the structural antagonist of the architecture, not an inline citation. No other historical figures or researchers may be named.

**Image generation — Agent 9**
Agent 9 uses `gemini-3-pro-image-preview` via Vertex AI with `location="global"` (regional endpoints return 404 for this model). The API is `generate_content(response_modalities=["IMAGE"])` — not `generate_images()`. The negative prompt is embedded in the prompt text, not passed as a parameter. Aspect ratio is handled post-generation via `ImageOps.pad()` (pillarbox with #F4E5CA sage beige — no stretching, no cropping). Image prompts specify `#F4E5CA` sage beige background directly in `STYLE_SUFFIX` in `utils.py`; `_enforce_background_color` also runs automatically after each image is saved as a safety net (note: this only catches solid wrong-color flats — textured backgrounds and decorative frames pass through it; Agent 9b catches those). The `--transparent`/`rembg` path was removed — see plan `enumerated-doodling-lovelace.md` F4. **STYLE_SUFFIX rule:** never say "vellum", "aged paper", "parchment", or any texture descriptor in the prompt — Gemini interprets those literally and renders paper grain into the image; the prompt asks for a flat solid background and `add_grain.py` adds grain in post.

**Selective regeneration — `--indices`**
`agent9_images.py --generate --indices "22,26,97"` regenerates only the listed 1-based indices and overwrites existing PNGs at those positions. Other images are untouched. Use this for re-rolling specific bad images flagged by Agent 9b without spending API credits on the whole set.

**Image QA — Agent 9b**
After Agent 9, run `agent9b_image_qa.py "<slug>"` to validate every image against the SENSUM style contract using Gemini 2.5 Flash on Vertex AI. Checks: flat solid sage beige background (no texture), dark brown ink only (no other colors), no decorative borders/frames, no head cropping, no visible text. Writes `md/09_image_qa.md` listing failures. Cost ~$0.04 per 120-image video; runtime ~2 minutes. Use `--retry` to auto-regenerate failed indices via Agent 9 (one attempt). The validator never deletes images; it reports and lets the user decide.

**Thumbnail generation — agent10_thumbnails.py**
Run after Agent 8 (needs `07_publish_package.md`) and Agent 9 is optional. Two-step: Claude Opus 4.7 generates 5 distinct thumbnail concepts (one per composition type), then Gemini renders each at 1920×1080. Run with `--no-grain` — grain is applied manually in Canva after adding the title text overlay. Prompts are saved to `thumbnail_prompts.md` for reference. Flags: `--no-grain` (recommended), `--reuse-prompts` (skip Claude step, reload saved prompts), `--indices 1,4` (only generate those prompt numbers), `--count 3` (generate N variations per prompt — named `thumbnail_01_v1.png` etc). Rate limit: 20s between Vertex AI calls. Gemini is stochastic — exact pixel-identical re-runs are impossible; `--reuse-prompts` reuses the same prompt text but produces new renders.

**Agent 8 web scraping**
`agent8_publish.py` scrapes Google Autocomplete and YouTube search results for SEO tags. This is fragile — if Google/YouTube changes their HTML, the scraper returns an empty tag list silently and the rest of the output is fine. The YouTube competitor-tag scraper currently returns 0 results most runs (YouTube payload shape changed — `JSONDecodeError: Extra data`); Agent 8 still produces a valid package because it falls back on Niche Trend Signals + autocomplete + script context. If the tags section in `07_publish_package.md` looks empty or short, the scraper has broken; add tags manually.

**Agent 8 publish package — output format (locked, 2026-05-24 rewrite)**
Agent 8 operates as an **Advanced YouTube Metadata Engineer / NLP Optimization Pipeline** — cold, empirical decision logic for tag selection and NLP anchoring; warm-validating speaker voice in description and Shorts body copy. Do not loosen these without explicit instruction:

- **Long-form titles** — 5 variants in the **Identity Provocation blueprint**: each title must function as an identity reframe ("You're Not Lazy. Your Reward System Is Misfiring."), a paradox ("What If Your Anxiety Is the System Working Perfectly?"), or a system-architectural reveal ("Your Nervous System Is Running on Outdated Settings."). Banned: instructional verbs (`how to`, `tips`, `ways to`, `stop`, `fix`), list-format (`5 …`, `7 things …`), advisory framing. Each under 60 chars. At least 2 of the 3 modes represented across the 5.
- **Description** — three-block NLP-anchored structure, total under 120 words.
  - **Block 1 (Hook Segment, lines 1–2):** 3–6 visceral somatic/emotional fragments, no conversational filler, no greeting.
  - **Block 2 (Explanatory Block, line 3+):** identity-absolution framing ("These aren't character flaws — they're the signals of…"), names 3–5 concepts in plain language, closes warm. The phrase "In this video, we explore" is permitted but no longer mandated.
  - Hard rules: no researcher names, no study years, no Latin-sounding jargon in body, no second-person preachy lines.
- **Timestamps** — explicit `Timestamps:` heading followed by `00:00 Introduction` and `[XX:XX] Chapter Name` placeholder rows. 6–12 chapters.
- **References** — heading is `Research & References:` (no book emoji). Format unchanged: `• Concept Label — Optional Qualifier: Author, A., et al. (Year).` One per line, bullet `•`, ends with year-in-parens and period. No summary sentence.
- **Hashtags** (end of description block, before `---`) — **unchanged**: exactly 3, single-word, lowercase, `#` prefix. First is always `#sensum`. Other 2 are the strongest single-word topical hashtags.
- **YouTube Tags** — **10–15 multi-word tags**, comma-separated, no `#` prefix, total under 450 chars (agent prints actual length; YouTube hard cap is 500). Slot structure, front-loaded by algorithmic weight: **Tag #1 = exact-match primary keyword** extracted from the chosen long-form title (algorithm front-loads semantic weight onto Tag #1 — don't waste it); **Tags #2–#5** = strongest long-tail variations and paraphrases of the primary keyword (3–5 words each); **Tags #6–#12** = supporting long-tail intent phrases (2–4 words) including Niche Trend Signals rendered as multi-word phrases; **Tags #13–#15** (optional) = broader 2–3 word category anchors ("permission psychology", "emotional regulation"). Single-word tags PROHIBITED — they cause semantic dilution and format decoupling on this niche. Brand exception: `SENSUM` (uppercase) appears once as the only single-word entry, slot anywhere. Every phrase extractable from script's literal language or a direct-intent paraphrase. Niche Trend Signals are a **supporting reference for the back half** — the primary keyword from the chosen title leads.
- **Shorts package** — 3–5 Shorts, each with: single **Title** (max 60 chars, identity-reframe blueprint), **Description** (1–2 sentences mapping cognitive dissonance, ends with `#Shorts #x #y`), **Tags** (3–5 multi-word backend phrases, 2–4 words each, comma-separated, no `#` prefix, single-word prohibited except `SENSUM`-once), and **Script Lines to Clip** split into `Hook (first ~3s): [Q?]` and `Core payload: [Q?]` sub-blocks with verbatim `> ` quoted lines. Shorts backend tags are a categorization safety net, not a discovery driver — the description hashtag block carries the real algorithmic signal on Shorts (the Shorts recommendation engine is fully decoupled from long-form and barely reads backend tags). The `[Q1]/[Q2]/[Q3]/[Q4]` marker is computed deterministically by `_annotate_script_quarters` and tells the editor which quarter of `06_script_narration.md` to text-search in DaVinci. `[Q?]` means the quote did not substring-match — usually a paraphrase that needs fixing.

The Agent 8 metadata prompt frames Claude as an Advanced YouTube Metadata Engineer / NLP Optimization Pipeline operating with cold, empirical, mathematical precision (long-form titles in identity-provocation voice; description body and Shorts descriptions remain warm/validating).

**Niche Trend Signals — Agent 11 ↔ Agent 8 integration**
Agent 11 (weekly niche intelligence) writes a sidecar **`outputs/intelligence/{week_label}_tag_signals.md`** alongside its PPTX deck. The file is single-word-only and has four sections: Top Trending Tags / Top Trending Title Topics / Top Title Words / Content Gaps. Agent 8 automatically reads the latest sidecar (newest by filename sort) via `_load_niche_signals()` and injects it into the metadata prompt as `## Niche Trend Signals (latest weekly intelligence report)`. The prompt treats this block as a **supporting reference for the back half of the tag list** (post 2026-05-24 doctrine shift — previously it was "highest-priority", but Tag #1 must now be the exact-match primary keyword extracted from the chosen long-form title, since YouTube's algorithm front-loads semantic weight on Tag #1). The integration fails soft — if no sidecar exists, Agent 8 still works as before. Agent 11's `PROJECT_ROOT` is `Path(__file__).parent.parent.parent` (three levels up, not two) — a prior bug used `.parent.parent` which resolved to `tools/` and broke `outputs/intelligence/` pathing.

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
| 9b **(QA, optional)** | `pipeline/agent9b_image_qa.py` | Gemini 2.5 Flash | `images/*.png` | `md/09_image_qa.md` |
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
