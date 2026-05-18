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
.tmp/           # Temporary files (scraped data, intermediate exports). Regenerated as needed.
tools/          # Python scripts for deterministic execution
workflows/      # Markdown SOPs defining what to do and how
.env            # API keys and environment variables (NEVER store secrets anywhere else)
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
PYTHONIOENCODING=utf-8 python tools/agent3.py "slug"
```

**PubMed zero results**
The auto-derived PubMed query sometimes returns zero results (query too specific or wrong MeSH terms). This is acceptable if the Gemini research section contains solid peer-reviewed references. Agent 2 verifies claims against scientific literature regardless of PubMed results — proceed to Agent 2 as normal.

**Darwin exception to no-inline-citations rule**
Scripts using the Historical Reversal narrative architecture may name Darwin as a historical narrative device (the "wrong view" being overturned). This is not an inline citation — it is the structural antagonist of the architecture. All actual scientific claims must still use "researchers found / scientists discovered / in one study."

**Image generation — Agent 9**
Agent 9 uses `gemini-3-pro-image-preview` via Vertex AI with `location="global"` (regional endpoints return 404 for this model). The API is `generate_content(response_modalities=["IMAGE"])` — not `generate_images()`. The negative prompt is embedded in the prompt text, not passed as a parameter. Aspect ratio is handled post-generation via `ImageOps.pad()` (pillarbox with #F4E5CA sage beige — no stretching, no cropping). Image prompts use a clean flat white background (defined in `STYLE_SUFFIX` in `utils.py`); #F4E5CA is applied as post-processing via `--correct-bg` (PIL-only). The `--transparent`/`rembg` path was removed — see plan `enumerated-doodling-lovelace.md` F4.

**Thumbnail generation — agent10_thumbnails.py**
Run after Agent 8 (needs `07_publish_package.md`) and Agent 9 is optional. Two-step: Claude Opus 4.7 generates 5 distinct thumbnail concepts (one per composition type), then Gemini renders each at 1920×1080. Run with `--no-grain` — grain is applied manually in Canva after adding the title text overlay. Prompts are saved to `thumbnail_prompts.md` for reference. Flags: `--no-grain` (recommended), `--reuse-prompts` (skip Claude step, reload saved prompts), `--indices 1,4` (only generate those prompt numbers), `--count 3` (generate N variations per prompt — named `thumbnail_01_v1.png` etc). Rate limit: 20s between Vertex AI calls. Gemini is stochastic — exact pixel-identical re-runs are impossible; `--reuse-prompts` reuses the same prompt text but produces new renders.

**Agent 8 web scraping**
`agent8_publish.py` scrapes Google Autocomplete and YouTube search results for SEO tags. This is fragile — if Google/YouTube changes their HTML, the scraper returns an empty tag list silently and the rest of the output is fine. If the tags section in `07_publish_package.md` looks empty or short, the scraper has broken; add tags manually.

## Quick Command Reference

All agents (except 0 and 1) take a **slug** — the output directory name under `outputs/`. Never pass the raw topic after Agent 1.

```bash
# Standard invocation:
PYTHONIOENCODING=utf-8 python tools/agentN_name.py "<slug>"

# List existing slugs:
ls outputs/
```

**Agents that take a TOPIC:** Agent 0 (`--topic` flag), Agent 1 (positional arg). All others take a slug.  
**Before running any agent:** verify the previous agent's output exists in `outputs/{slug}/md/`.  
**Parallel-safe after Agent 4a:** Agents 5, 6, and 8 can run simultaneously.  
**For flags and error recovery:** see the matching `workflows/NN_name.md` file.

## Agent Chain

Complete pipeline — run in this order. Each agent reads its **Input** and writes its **Output** inside `outputs/{slug}/`.

| Agent | Script | Model | Input | Output |
| --- | --- | --- | --- | --- |
| 0 (optional) | `agent0_materials.py` | Gemini 2.5 Flash | PDF + topic | `md/00_materials_insights.md` |
| 1 | `agent1_research.py` | Gemini 2.5 Pro + PubMed | topic string | `md/01_research.md` |
| 2 | `agent2_verify.py` | Gemini 2.5 Pro | `01_research.md` | `md/02_verified_research.md` |
| 3 | `agent3.py` | runs 3a → 3n → 3b → 3c | slug | all `03_*.md` files |
| 3a | `agent3a_draft.py` | Claude Opus 4.7 | `02_verified_research.md` | `md/03a_draft.md` |
| 3n | `agent3n_novelty.py` | Claude Sonnet 4.6 | `03a_draft.md` + prior corpus | `md/03_novelty_report.md` + revised `03a_draft.md` |
| 3b | `agent3b_critic.py` | Claude Sonnet 4.6 | `03a_draft.md` | `md/03b_critique.md` |
| 3c | `agent3c_rewrite.py` | Claude Opus 4.7 | `03a_draft.md` + `03b_critique.md` | `md/03_script_draft.md` |
| 4a | `agent4a_edit.py` | Claude Sonnet 4.6 | `03_script_draft.md` | `md/04_script_final.md` |
| 4b **(gate)** | `agent4b_hook.py` | Claude Sonnet 4.6 | `04_script_final.md` | `md/04b_hook_score.md` + revised `04_script_final.md` in place |
| 5 | `agent5_visuals.py` | Claude Opus 4.7 | `04_script_final.md` | `md/05_image_prompts.md` |
| 6 | `agent6_narration.py` | deterministic | `04_script_final.md` | `md/06_script_narration.md` |
| 7 (optional) | `agent7_tts.py` | Gemini Flash TTS / Chirp3 HD | `06_script_narration.md` | `tts/*.wav` |
| 8 | `agent8_publish.py` | Claude Sonnet 4.6 + web scrape | `04`, `06`, `02` outputs | `md/07_publish_package.md` |
| 9 | `agent9_images.py` | Gemini 3 Pro Image Preview | `05_image_prompts.md` | `images/image_*.png` |
| 10 | `agent10_thumbnails.py` | Claude Opus 4.7 + Gemini 3 Pro Image Preview | `04_script_final.md` + `07_publish_package.md` | `thumbnails/thumbnail_0N.png` × 5 |

**Parallel-safe after Agent 4a:** Agents 5, 6, and 8 can run simultaneously. Agent 7 depends on Agent 6. Agent 9 depends on Agent 5. Agent 10 depends on Agent 8 (for `07_publish_package.md`) and can run in parallel with Agent 9.

**Quality gate — Agent 4b:** Scores opening hook (Tier 1: ≥8/10 at 37 words; Tier 2: ≥7/10 at 200 words). Verdict must be `RECORD` before recording voiceover. Modifies `04_script_final.md` in place; backup saved to `04_script_final.bak.md`.

**Novelty check — Agent 3n:** Compares new draft against all prior `outputs/*/md/06_script_narration.md` files (the shipped corpus). First video ever produces `SKIPPED` verdict automatically — that is correct behavior.

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
