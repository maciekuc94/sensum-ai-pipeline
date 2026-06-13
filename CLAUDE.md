# Agent Instructions

You're working inside the **WAT framework** (Workflows, Agents, Tools). This architecture separates concerns so that probabilistic AI handles reasoning while deterministic code handles execution. That separation is what makes this system reliable.

## The WAT Architecture

**Layer 1: Workflows (The Instructions)** — Markdown SOPs in `workflows/`. Each defines the objective, inputs, which tools to use, outputs, and edge cases. Plain language.

**Layer 2: Agents (The Decision-Maker)** — your role. Read the relevant workflow, run tools in sequence, handle failures, ask when unclear; connect intent to execution without doing everything yourself. *Example:* to verify research, read `workflows/pipeline/02_verify.md`, then run `tools/pipeline/agent2_verify.py "<slug>"`.

**Layer 3: Tools (The Execution)** — Python in `tools/` for the deterministic work: API calls, file ops, transforms. Consistent, testable, fast. Secrets in `.env`.

**Why this matters — and where the rule bends.** Offloading execution to deterministic scripts keeps you on orchestration. **But the creative core has no Layer 3:** the `/draft` script chain, `/visuals` prompts, `/package` strategies, and `/publish` copy *execute in-session* — you can't make good Polish prose deterministic. Python stays only where the work is genuinely mechanical (research APIs, image render, forced alignment, validation, docx). The three layers hold; the reasoning↔execution boundary just moved.

**Where `.claude/` fits — it is NOT a fourth layer.** It's the Claude Code *interface* to the three layers: `commands/` = manual launchers, `skills/` = auto-firing routers + doctrine guards, `agents/` = specialist sub-contexts for `/draft` + `/publish`, `settings.json` = harness config. The instructions still live in `workflows/`; `.claude/` only triggers and configures them.

**"Agent" is two words.** WAT "Agent" (Layer 2) = the reasoning orchestrator — *you*, a role, not a file. A Claude Code "agent" (`.claude/agents/*.md`) = a spawned subagent context. Same word, two things — the #1 source of confusion here.

## Channel Language (2026-05-25 — Polish localization)

**This pipeline produces Polish-language SENSUM content.** The channel is `@sensumpolska` on YouTube. All script-writing agents (3a writer / 3b checkers / 3c fixer / 8) generate Polish output; the voice canon (`workflows/guides/voice_brief.md`) is in Polish. The English pipeline as it stood on 2026-05-25 is preserved at Git tag `en-pipeline-v1`. The legacy English channel `@hello.sensum` is dormant.

**To restore English behavior** (any granularity — single file, full pipeline, branch): `git checkout en-pipeline-v1 -- <path>`.

**No banned-phrase lists.** The lean draft chain deliberately keeps none — the cold checker (3b) catches calques/translationese live, reading the whole script with a fault-finding native ear, which beats any frozen list. The user's final docx pass is the last filter.

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
.claude/                 # Claude Code interface (NOT a WAT layer — see "Where .claude/ fits")
  commands/              # Manual slash launchers: /draft /visuals /package /publish /animate
  agents/                # Cold /draft specialists: draft-{writer,section-checker,arc-checker,fixer} + /publish teammates: native-copy-critic + publish-{copywriter,seo,clips}
  skills/                # 10 skills: 2 guards (scientific-etching, native-voice) + 4 routers (write-script, package-thumbnail, render-images, publish-package) + 4 utils (two-color-thumbnail, grain-thumbnail, sensum-pdf, grill-me)
  settings.json          # Shared harness config (committed); settings.local.json = personal (gitignored)
tools/
  pipeline/              # Agent scripts 0–8 + align + draft_{merge,check}.py (Gen 5 Layer 3); lib/ = align helper modules (aligner, fcpxml_writer, …)
  dev/                   # Standalone tools: add_grain, finish_thumbnail, md_to_pdf_sensum, analyze_subtitles, research_{gate,topic}_signals
  mission_control/       # Read-only web kokpit (FastAPI + vanilla JS): stan slugów, artefakty, backlog — python tools/mission_control/server.py
  utils.py               # Shared constants/utilities (CHARACTER_DESCRIPTION, STYLE_SUFFIX) — all agents import
  research_sources.py    # Peer-reviewed source aggregation for Agent 1 (PubMed + Europe PMC)
workflows/
  pipeline/              # Numbered SOPs 00–08 (one per agent) + align.md
  guides/                # voice_brief.md (voice canon), file_naming.md (slug file-naming canon), style_guide_images.md, davinci_subtitle_preset.md
docs/                    # Lazy-read references: Claude Code authoring guides (subagents/skills/…) + research/ + archive/
brainstorms/             # Dated design-decision logs (cited as rationale throughout this file)
materials/               # Agent-0 input materials (PDFs etc.)
outputs/
  videos_pl/             # Polish videos (one folder per slug); videos_en/ = legacy English
  channel_assets/        # Shared brand assets (logo, fonts, colors)
.tmp/                    # Disposable intermediate files (regenerated as needed)
.env                     # API keys / secrets (NEVER store secrets anywhere else)
```

**Core principle:** Local files are just for processing. Anything I need to see or use lives in cloud services. Everything in `.tmp/` is disposable.

## Design Standards

**Color palette:** Two colors only — #F4E5CA (Sage Beige, exclusive background, described in prompts as a **flat solid sage beige background with no texture**; the paper-grain look is applied in post via `add_grain.py`, never requested in the prompt) and #582F0E (Dark Brown, all ink lines, cross-hatching, and silhouettes). No other colors permitted in any generated visual, slide, chart, or asset. The illustration style is Scientific Etching: fine-liner ink sketches with cross-hatching for depth, referencing 19th-century scientific journal engravings. No gradients, no fills, no watercolor. No text, no labels, no words in any generated image. No decorative borders or frames around the image — full-bleed composition.

## Technical Notes

Operative rules live here; the *why/history* behind each lives in auto-memory (`project_*.md`, lazy-loaded), full specs in `workflows/guides/` + `workflows/pipeline/` + `docs/`. Pointers below are canonical — don't re-narrate decisions here.

### Authoring Claude Code internals — read the matching `docs/` reference first

Zanim napiszesz lub mocno zmienisz **subagenta, skilla, slash command, hooka, agent team, konfigurację MCP/settings albo CLAUDE.md/pamięć**, otwórz pasującą referencję w `docs/` i trzymaj się jej. Czytaj **on-demand** (lazy) — **nie** wciągaj ich przez import `@` do CLAUDE.md (to ~170 KB eager-load w każdej sesji). Zdestylowane z oficjalnych docs (`code.claude.com/docs`, 2026-06-09):

| Co piszesz / edytujesz | Przeczytaj najpierw |
| --- | --- |
| Subagent (`.claude/agents/*.md`, `Agent` tool) | `docs/subagents_reference.md` |
| Agent team (`/publish` teammates) | `docs/agent_teams_reference.md` |
| Skill (`.claude/skills/`) | `docs/skills_reference.md` |
| Slash command (`.claude/commands/`) | `docs/slash_commands_reference.md` |
| Hook (settings.json lub frontmatter) | `docs/hooks_reference.md` |
| `settings.json` / permissions / env vars | `docs/settings_reference.md` |
| Serwer MCP (`.mcp.json`, scoping) | `docs/mcp_reference.md` |
| CLAUDE.md / system pamięci | `docs/memory_reference.md` |

**No Claude API — everything in-session (Opus 4.8).** Zero Anthropic API calls. `/draft`, `/visuals`, `/package`, `/publish` all run in-session; `query_claude()` removed, `ANTHROPIC_API_KEY` not required. Gemini (Vertex AI) only for research (0/1/2), image render (6, package-render), QA (6b). In-session prompts single-sourced in `workflows/pipeline/03a_writer.md` / `03b_section_checker.md` / `03b_arc_checker.md` / `03c_fixer.md`, `05_visuals.md`, `07_package.md`, `08_publish.md`. Legacy Gemini paths survive behind `--api`.

**Windows encoding.** Prefix Bash pipeline runs with `PYTHONIOENCODING=utf-8` (avoids Unicode codec errors), e.g. `PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "slug"`.

**PubMed zero results = OK.** Auto-derived query sometimes returns nothing from PubMed; fine — Europe PMC runs in parallel as a second peer-reviewed provider (`research_sources.py`) and Gemini adds refs. Agent 2 verifies regardless — proceed normally.

### Script voice — the non-negotiables

Pełny kanon: `workflows/guides/voice_brief.md` (v2 2026-06-07 — 7 reguł + zasady nadrzędne). Poniżej operacyjny destylat — wiążący dla każdej edycji prozy (in-session, `/draft`, freeform przez `native-voice-guard`). **Pivot v2:** SENSUM odrobinę bardziej wyjaśniający i swobodniejszy formalnie — mechanizm wolno trochę odsłonić, koniec przymusu jednej metafory. Rationale: brainstorm `brainstorms/2026-06-07-poprawka-doktryny-glosu.md`:

- **Explain mechanism, no research attribution (v2.1).** Warm therapist to one person; you may *lightly* explain the mechanism (zrozumienie pogłębia wgląd) — but as something you simply know, **no** „badania pokazują" in narration. (Validated on slug 3: the writer used „badania pokazują" 2×, the user cut both; mechanism-explaining was kept.) Still no researcher names / years / decimals / counts / methodology terms in narration; full citations live only in the Agent 8 description. The validator (draft_check.py) flags any „badania pokazują" that slips; you cut it on the docx pass. Rationale: memory `feedback_no_inline_citations.md`; brainstorm `2026-06-07-poprawka-doktryny-glosu.md`.
- **Number policy.** Round, framed numbers only ("roughly half", "most people"). Banned: decimals, effect sizes, p-values, study/participant counts, methodology terms. Even a round number stated as fact ("blisko połowy…") reads as an uncited stat — describe the phenomenon instead. If a number doesn't land emotionally, cut it.
- **Jargon ≠ feelings (v2: test = comprehensibility).** Ban only jargon a layperson wouldn't understand („dysonans poznawczy", „kwantyfikator"). A term an ordinary person *does* grasp („układ nerwowy") is fine now — no more once-late ceremony. **Naming feelings (wstyd, wina, lęk, wyrzuty sumienia) is NOT jargon — it's the core; name them outright.**
- **Permission Practice — optional + light.** Include a micro-practice only if a real concrete move grows from the central image; if not, go straight to the recognition close. When present: flowing prose („Czasem wystarczy…" anaphora), **never** a numbered list. **Recognition close always last.** Rationale: memory `project_pp_prose_and_style_calibration.md`, `project_path_beat_register.md`.
- **Warmth + free gender (v2).** Speak DO the person, warmly, never auditing the system. Masculine generic freely — use it whenever needed; no gender rule, no impersonal contortions (v2: the gender rule was dropped entirely). Rationale: memory `project_voice_doctrine.md`.
- **Craft (v2: metaphor freed).** No one-metaphor rule — several images are fine if they enliven the text (the single-metaphor straitjacket made scripts monotonous and over-strained one image into koślawe coinages). The one remaining brake on przekombinowanie is **pisz luźno, naturalność > ozdobność** — now load-bearing. Still: no uncited round-number stat. Rationale: brainstorm `2026-06-07-poprawka-doktryny-glosu.md`.

### Script chain (Agent 3)

- **Gen 5 cold-subagent flow (2026-06-11).** `/draft <slug>` runs cold-context subagents — dedicated thin specialists `.claude/agents/draft-*.md` (Opus: writer/arc-checker/fixer, Sonnet: section-checkers), each blind to the others; the lead only passes files. One pass: **3a Writer** (1500–2200 words = 10–15 min film; **architektura obietnic** — each section opens the next question, the full answer to the title lands only at the close; first ~37 words = the hook gate, now a writer rule) → frozen-draft **ensemble in parallel** (one **3b section-checker per `## `** [Z]/[K], anti-flattening rule: native idiom ≠ calque, plus one **3b arc-checker** [A] with a **loop map** — promises/loops, opening, close execution, metaphors, klamra, transitions) → **`draft_merge.py`** (deterministic merge, zero tokens) → **3c Fixer** (applies surgically, [A]/[K] before [Z]; **mandatory skip clause** — clearly-worse proposals are skipped and logged to `md/iter/fixer_skips.md`) → snapshot **`md/04_final_machine.md` (untouchable — never overwrite, also in migrations)** → **`draft_check.py --export`** (report-only doctrine validator: sections survived / no research attribution / no digits / 1500–2200 window / no artifacts; exports `docx/script.docx`). Subagent returns are SHORT (path + counts — never the file body). **No Ściskacz (3d) and no `/hook`** — over-writing is cut by the user on docx; Tier-1 lives in writer rule 5 + arc-checker judges the opening; safeguard: if @0:30 retention on films 4–5 drops below ~55%, restore the gate from git. Spec: `03a_writer.md` / `03b_section_checker.md` / `03b_arc_checker.md` / `03c_fixer.md` + `voice_brief.md`. Rationale: brainstorms `2026-06-07-lean-draft-redesign.md`, `2026-06-07-context-checker-ensemble.md`, `2026-06-07-poprawka-doktryny-glosu.md`, `2026-06-11-gen5-draft-redesign.md`.
- **Why cold subagents.** The same model in one context rubber-stamps its own weird sentences (proven this redesign: the old reader panel + `/refine` were no-ops). A fresh context reading the whole text with fault-finding framing — replicating plain-chat conditions — actually catches them. That asymmetry is the whole design.
- **The user's docx pass is the ceiling.** The machine delivers ~75–80% (measured: slug 3 — 62% of sentences touched, −18% words on the user pass); final editorial judgment happens on `docx/script_corrected.docx`. We don't iterate the machine to perfection. `/publish` still uses Agent Teams (3 specialists + Native-Copy Critic 8d, auto-fallback in-session); spec `docs/agent_teams_reference.md`. Since Gen 5 the docx pass also owns trimming over-writing (no Ściskacz).

### Images & publish

- **Agent 6 (images).** `gemini-2.5-flash-image` (tuned-flash **v8**, 2026-06-08; was `gemini-3-pro-image-preview` — ~3.4× cheaper, ~90% parity, validated on slug-3 A/B) via Vertex AI, `location="global"` (regional → 404); API `generate_content(response_modalities=["IMAGE"])`; **v8 render recipe** (module constants `V8_BG_RULE` / `V8_FIGURE_RULE` / `V8_MASTER_RENDERING` / `V8_NEGATIVE` + `_generate_image_with_retry` 429 backoff) wraps every prompt — flat-bg + androgynous figure/flat-chest discipline + master-engraving craft (Doré/Dürer tonal range, dense cross-hatch, never solid fill) + strengthened negative; negative prompt embedded in text; aspect via `ImageOps.pad()` (pillarbox #F4E5CA). Background set in `STYLE_SUFFIX` (`utils.py`); **the generate path ends in a deterministic `two_color` pass** (2026-06-08) — every pixel hard-snapped to the nearer of `#582F0E` / `#F4E5CA`, guaranteeing the strict two-colour contract and stripping off-brand casts inside objects + any bg texture in one step; form untouched, only colour (replaces the old `enforce_background_color` + `flatten_background` — both still live as `--correct-bg` / `--flatten-bg`; aux batch `--two-color` defaults to `images_post/`, `--in-place` overwrites). Agent 6b still catches form issues (faces / text / frames / cropped heads). **Never** put texture words (vellum / aged paper / parchment / grain) in a prompt — Gemini renders them literally; ask for a flat solid background. **Grain is added later in DaVinci Resolve — never in-pipeline, never in the prompt.** Rationale: memory `project_color_master.md`, `feedback_no_texture_in_prompts.md`, `feedback_no_head_crop.md`; two-colour POST validated on slug-3 (2026-06-08).
- **`--indices`** (`agent6_images.py --generate --indices "22,26,97"`) regenerates only the listed 1-based images, overwriting in place — re-roll Agent 6b failures without re-spending on the full set. **Agent 6b QA** (`agent6b_image_qa.py`) validates every image vs the style contract (Gemini 2.5 Flash), writes `md/06_qa.md`; `--retry` regenerates failures (one attempt); never deletes. **Package (was Thumbnails)** `/package <slug>` → 3 strategie {tytuł+napis+koncept} + render 3 via `agent7_package.py --render --no-grain` (3-pro native ~4K; 20s rate limit). **Thumbnail finish (2026-06-08):** the picked thumbnail gets a deterministic **2-colour (`two_color`) + coarse grain `s2/i18`** (`add_grain(intensity=18, grain_scale=2)`) before Canva — at ~4K a fine 1-px grain vanishes on downscale, so thumbnail grain is heavier/coarser than the body-image standard. **Canva = napis overlay only** (grain already baked in). Spec: `07_package.md` → Post-production. Runs after `/draft`, before `/publish`; chosen title feeds `/publish` STEP 1 via `07_package.md`. Napis never enters the Gemini prompt (no-text contract). Flags/rubrics: `workflows/pipeline/06*.md`, `07_package.md`.
- **Agent 8 publish** runs in-session across 9 single-responsibility steps (titles / description+3 hashtags / timestamps / long-form tags / bibliography / shorts clip-selection / shorts titles / shorts descriptions / shorts tags). Bookends: `--extract` (narration → `.tmp/`), `--signals` (autocomplete; `--topic="<polish seed>"`), `--finalize` (Q1–Q4 + tag trim + validate + docx). Spec: `08_publish.md`.
- **Locked publish output:** Tag #1 = exact-match primary keyword from the chosen title; 5–8 multi-word tags (single-word prohibited except `SENSUM`-once); exactly 3 hashtags (`#sensum` first); description exactly 5 sentences; bibliography heading `Badania i źródła:`; Shorts clips tagged `[Q1]–[Q4]` (`[Q?]` = paraphrase slipped in, `[MISSING]` = Short lacks its clip block — fix both before publishing). Autocomplete scraper is fragile — thin tags = it failed; package still valid via script, add tags manually. Rationale: memory `project_long_tail_tags.md`, `project_shorts_quarter_markers.md`, `feedback_bibliography_verified_only.md`, `feedback_no_prepublication_checklist.md`.
- **Agent 5 (visuals)** in-session: generates compact `05_image_prompts.md` (`**Visual:**` field, 40–60 words), then `agent5_visuals.py --expand` injects CHARACTER_DESCRIPTION + STYLE_SUFFIX and exports phrase files. `--extract` pulls `script_corrected.docx` → md (auto-called when the corrected docx is present). **v8 storytelling doctrine (2026-06-08):** Metaphor Mandate (abstract line → concrete metaphor, never a literal standing figure) + anti-patterns + Grandeur gear (cinematic scale/camera reserved for peak/cost beats; per-image master-engraving craft is applied by Agent 6, not here). Spec: `05_visuals.md`.

## Quick Command Reference

All agents except 0/1 take a **slug** (output dir under `outputs/videos_pl/`), never the raw topic. Agent 0 takes `--topic`, Agent 1 a positional topic string. Before running any agent, verify the previous agent's output exists in `outputs/videos_pl/{slug}/md/`. Command *behavior/flags* live in the `### ` notes above + `workflows/pipeline/NN_name.md`; this is just the syntax.

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agentN_name.py "<slug>"   # standard Python agent (Windows: keep the prefix)
/draft <slug>                              # Agent 3 Gen 5 — pisarz → ensemble (section+arc, mapa pętli) → merge (skrypt) → fixer → snapshot → walidator+docx (zimne subagenty, jeden przebieg, no API)
/visuals <slug>                            # Agent 5 → agent5_visuals.py --expand
/publish <slug>                            # Agent 8 — 9 steps + Native-Copy Critic 8d (default); bookends --extract / --signals / --finalize; auto-fallback in-session
/package <slug>                            # Strateg opakowania (tytuł+napis+miniatura) → render 3; po /draft, przed /publish
/animate <slug>                            # Agent 6c planner — typuje beaty do pętli animacyjnych, pisze plan, STOP przed generacją (slug 4+)
/redaktor <slug>                           # Redaktor-uczeń — korpus par machine↔docx (tool) → 3 zimne kategoryzatory → synteza → raport + wnioski dla checkerów 3b (manual gate); po każdym docx passie
ls outputs/videos_pl/                      # list existing slugs
PYTHONIOENCODING=utf-8 python tools/mission_control/server.py   # Mission Control — kokpit na localhost:7777 (read-only; nic nie odpala, komendy do skopiowania)
```

**Parallel-safe after Agent 3:** Agents 5 and 8 simultaneously (6 depends on 5); `/package` runs after `/draft`, before `/publish`. **Legacy Gemini paths** sit behind `--api` (inert — in-session slash commands are the default). Voice canon: `workflows/guides/voice_brief.md`.

## Agent Chain

Complete pipeline — run in this order. Each agent reads its **Input** and writes its **Output** inside `outputs/videos_pl/{slug}/`.

All pipeline scripts live in `tools/pipeline/`.

| Agent | Script | Model | Input | Output |
| --- | --- | --- | --- | --- |
| 0 (optional) | `pipeline/agent0_materials.py` | Gemini 3.1 Pro | PDF + topic | `md/00_materials_insights.md` |
| 1 | `pipeline/agent1_research.py` | Gemini 3.1 Pro + PubMed + Europe PMC | topic string | `md/01_research.md` |
| 2 | `pipeline/agent2_verify.py` | Gemini 3.1 Pro | `01_research.md` | `md/02_verified_research.md` |
| 3 (whole chain) | `/draft <slug>` (Claude Code slash command; pisarz → ensemble section+arc → merge → fixer → walidator, cold subagents, one pass, no API) | Opus 4.8 lead + cold subagents (Opus: writer/arc/fixer · Sonnet: section-checkers) — no API | `02_verified_research.md` | `md/03a_draft.md`, `md/03b_corrections.md`, `md/04_final.md` + `md/04_final_machine.md` + `md/iter/fixer_skips.md` + `docx/script.docx` |
| 3a writer | (inside `/draft`) cold subagent; `03a_writer.md` + `voice_brief.md` | Opus 4.8 (cold subagent — no API) | `02_verified_research.md` | `md/03a_draft.md` |
| 3b section-checker (×N, per `## `) | (inside `/draft`) cold subagent; sentence `[Z]` + context `[K]`; `03b_section_checker.md` | Sonnet 4.6 (cold subagent — no API) | frozen `md/03a_draft.md` | `md/iter/sek_NN.md` |
| 3b arc-checker | (inside `/draft`) cold subagent; whole-arc `[A]` + mapa pętli; `03b_arc_checker.md` | Opus 4.8 (cold subagent — no API) | frozen `md/03a_draft.md` | `md/iter/arc.md` |
| 3c fixer | (inside `/draft`) cold subagent; surgical swap-in (`[A]`/`[K]` before `[Z]`); `03c_fixer.md` | Opus 4.8 (cold subagent — no API) | frozen `md/03a_draft.md` + `md/03b_corrections.md` | `md/04_final.md` |
| 5 | `/visuals <slug>` (Claude Code slash command) | Opus 4.8 (Claude Code, in-session — no API) | `04_final.md` (or `script_corrected.docx` if present) | `md/05_image_prompts.md` |
| 8 | `/publish <slug>` (Claude Code slash command; 3 specialist generators + Native-Copy Critic 8d by default, auto-fallback in-session; bookends `agent8_publish.py --extract/--signals/--finalize`) | Opus 4.8 (in-session lead + 4 teammate contexts — no API; legacy: `--api` Gemini + web scrape) | `script_corrected.docx` → `script.docx` → `04_final.md` + `02_verified_research.md` | `md/08_publish.md` + `docx/08_publish.docx` + `md/08d_nativecopy_iter*.md` |
| 8d | (inside `/publish`) `native-copy-critic` teammate | Opus 4.8 (Claude Code teammate — no API) | `md/08_working.md` | `md/08d_nativecopy_iter{N}.md` |
| 6 **(manual)** | `pipeline/agent6_images.py` | Gemini 2.5 Flash Image (tuned-flash v8) | `05_image_prompts.md` | `images/image_*.png` |
| 6b **(QA, optional)** | `pipeline/agent6b_image_qa.py` | Gemini 2.5 Flash | `images/*.png` | `md/06_qa.md` |
| 6c **(manual, slug 4+)** | `/animate <slug>` (planner) + `pipeline/agent6c_animate.py` | Opus 4.8 plan (in-session) + Gemini 2.5 Flash Image (edycje faz) | `05_image_prompts.md` + `images_post/` | `md/06c_animation_plan.md` + `images_anim/image_NNN_anim.mp4` |
| 7 → Package **(manual)** | `/package <slug>` + `agent7_package.py --render` | Opus 4.8 strategies (in-session) + Gemini 3 Pro Image render (`gemini-3-pro-image-preview`, ~4K) | `04_final.md` (script) | `md/07_package.md` + `md/07_package_prompts.md` + `thumbnails_no_grain/thumbnail_0N.png` × 3 |
| Align **(post-record)** | `pipeline/agent_align.py` | faster-whisper (local, free) | `voiceover/voiceover.wav` + `05_phrases.md` + `script_corrected.docx` / `script.docx` / `04_final.md` | `edit/subtitles.srt` + `edit/timeline.fcpxml` + `edit/preview.html` + `edit/alignment.json` |

**Parallel-safe after Agent 3 (script chain):** Agents 5 and 8 can run simultaneously. Agent 6 depends on Agent 5. `/package` runs after `/draft` and before `/publish` (it feeds the title), independent of Agents 5/6.

**Manual agents — never run automatically:** `/package` (3 thumbnails + strategies) and Agent 6 (images) cost render credits + time. `/package` runs after `/draft` and before `/publish` (it feeds the title); Agent 6 after `/visuals`. Only run either on explicit instruction.

**Agent 6c — Ożywiacz (2026-06-10, slug 4+ only):** `/animate <slug>` typuje 10–15 beatów do obiektowych pętli animacyjnych (zasada: hook / metafora centralna / puenta; ruch musi być związany znaczeniowo z narracją) i pisze `md/06c_animation_plan.md` — **manual gate**: generacja (`agent6c_animate.py`, ~$0.08–0.12/beat) tylko po akceptacji planu. Wynik: zapętlone klipy `images_anim/image_NNN_anim.mp4` (mp4v, ~10 s) — **drop-in** na timeline DaVinci zamiast PNG (ruchy kamery usera bez zmian). Estetyka: lekki „boil" przerysowanej kreski = feature (decyzja usera — **nigdy nie stabilizować klatek**); pętle asynchroniczne względem audio; zero zmian w `agent_align`/FCPXML. Tryby: `edit` (edycje sceny z GUARD-promptem, domyślny) / `sheet` (arkusz faz → sprite'y → kompozycja, oszczędnie). Iteracja rytmu za darmo: edytuj Pattern/FPS w planie + `--no-gen`; re-roll: `--indices N --force`. Spec: `workflows/pipeline/06c_animate.md`; rationale: `brainstorms/2026-06-10-agent6c-ozywiacz.md`.

**Align Agent — Forced Alignment & DaVinci Bundle:** Runs *after* voiceover recording (Studio One → exported WAV at `voiceover/voiceover.wav`). Uses faster-whisper to align audio to the known script, then emits an SRT + FCPXML the user imports into DaVinci Resolve. Eliminates ~2-4 hours of manual subtitle syncing and image placement per video. Local-only, no API costs. Naming: file is `tools/pipeline/agent_align.py` (no number — it's a post-record satellite, not a numbered pipeline stage). See `workflows/pipeline/align.md` and one-time `workflows/guides/davinci_subtitle_preset.md` for setup.

**Redaktor-uczeń — wzorce z docx-passów (2026-06-12):** `/redaktor <slug>` po każdym docx passie. `redaktor_pary.py` buduje `.tmp/redaktor_korpus.md` (pary zdań machine↔human ze WSZYSTKICH slugów, tag generacji), 3 zimne `redaktor-kategoryzator` (Opus) niezależnie kategoryzują wzorce, lead syntetyzuje (próg ≥2/3 kategoryzatorów + ≥2 filmy) → raport `docs/research/redaktor/` + propozycje do `workflows/guides/redakcja_wnioski.md` (manual gate; max 10 aktywnych, wygasanie po 2 pudłach). Wnioski czytają TYLKO checkerzy 3b (nigdy pisarz — to by odtwarzało banned-listy); kategoryzatorzy nigdy nie widzą obecnych wniosków (ślepa re-walidacja). `voice_brief.md` nietykalny. Spec: `docs/superpowers/specs/2026-06-12-redaktor-uczen-design.md`.

**Walidator + eksport (Gen 5):** `draft_check.py --export` w ogonie `/draft` raportuje naruszenia doktryny (report-only) i eksportuje `docx/script.docx` — edit this in Word/Copilot 365/Gemini and save as `docx/script_corrected.docx`; all downstream agents (Agent 8, /visuals, Align) auto-detect the corrected file. Osobnej bramki hooka nie ma — Tier-1 żyje w regule 5 pisarza i w arc-checkerze (safeguard: 0:30 < ~55% ⇒ przywróć bramkę /hook z gita).

## Bottom Line

You sit between what I want (workflows) and what actually gets done (tools). Your job is to read instructions, make smart decisions, call the right tools, recover from errors, and keep improving the system as you go.

Stay pragmatic. Stay reliable. Keep learning.
