# Master SOP: YouTube Psychology Content Pipeline

This pipeline takes a psychology topic from raw idea to a production-ready narration script with AI-generated images, thumbnails, and a publish package. It pulls from two scientific sources (Gemini + Google Search, PubMed), verifies every claim against peer-reviewed sources, and writes a structured YouTube script before generating visuals. All output is local; nothing is published automatically.

For high-level operating invariants (color palette, file layout, model routing, locked output formats), see [CLAUDE.md](../../CLAUDE.md). For per-step detail, see the matching `workflows/pipeline/NN_*.md` file.

> **Stage 3 = Gen 5 cold-subagent chain (2026-06-11).** `/draft <slug>` runs cold subagents, one pass, no loop, no API: **3a Writer** (Opus, 1500–2200 words, promise architecture) → **3b ensemble** (a section-checker per `## ` + one arc-checker with a loop map, in parallel; Sonnet section / Opus arc) → `draft_merge.py` → **3c Fixer** (Opus, skip clause + `iter/fixer_skips.md`) → snapshot `04_final_machine.md` → `draft_check.py --export` (doctrine validator + docx). No Ściskacz, no `/hook` (both retired 2026-06-11 — see `brainstorms/2026-06-11-gen5-draft-redesign.md`). Authoritative: `03a_writer.md`, `03b_section_checker.md`, `03b_arc_checker.md`, `03c_fixer.md`, `.claude/commands/draft.md`, `workflows/guides/voice_brief.md`, CLAUDE.md §„Script chain (Agent 3)".

---

## Architecture

```
Topic (string)
    │
    ▼
[Agent 0: Materials] (optional)
    │  Extracts insights from a reference PDF via Gemini 3.1 Pro
    ▼
outputs/videos_pl/{slug}/md/00_materials_insights.md
    │
    ▼
[Agent 1: Research]
    │  Gemini 3.1 Pro (Google Search Grounding) + PubMed
    ▼
outputs/videos_pl/{slug}/md/01_research.md
    │
    ▼
[Agent 2: Verify]
    │  Gemini 3.1 Pro classifies every claim: VERIFIED / FLAGGED / REMOVED
    ▼
outputs/videos_pl/{slug}/md/02_verified_research.md
    │
    ▼
[Agent 3: Script — 3a Writer → 3b ensemble (section+arc) → merge → 3c Fixer → validator, cold subagents via `/draft <slug>`]
    │  3a Writer    — Opus 4.8 (cold) writes the whole 1500-2200-word narration, one loose pass (promise architecture)
    │  3b ensemble  — parallel cold subagents: one section-checker per `## ` (Sonnet) + one arc-checker with loop map (Opus)
    │  draft_merge.py — deterministic merge of iter/ findings → 03b_corrections.md
    │  3c Fixer     — Opus 4.8 (cold) applies corrections surgically, skips clearly-worse ones → 04_final.md + iter/fixer_skips.md
    │  draft_check.py --export — doctrine validator (report-only) + docx/script.docx
    │  One pass, no loop, no API
    ▼
outputs/videos_pl/{slug}/md/03a_draft.md → 03b_corrections.md → 04_final.md
outputs/videos_pl/{slug}/md/04_final_machine.md  (untouchable machine snapshot)
outputs/videos_pl/{slug}/docx/script.docx
    │
    ├──────────────────────────────────────────────────────────────┐
    ▼                                                              ▼
[Agent 5: Visuals — `/visuals`]                              [Agent 8: Publish — `/publish`]
    │  Opus 4.8 (in-session)                                      │  Opus 4.8 (in-session), 9 steps
    │  one prompt per beat                                         │  + autocomplete/finalize bookends
    ▼                                                              ▼
outputs/videos_pl/{slug}/md/                            outputs/videos_pl/{slug}/md/
  05_image_prompts.md                                              08_publish.md
  05_phrases.md
    │                                                              │
    │   ┌──────────────────────────────────────────────────────────┘
    │   │  (manual gate — review both before generating images/thumbs)
    │   │
    ▼   ▼
[Agent 6: Images] (manual)             [Agent 7→Package] (manual — `/package`)
    │  Gemini 3 Pro Image Preview         │  Opus 4.8 concepts (in-session) → Gemini 3 Pro Image render
    ▼                                     ▼
outputs/videos_pl/{slug}/images/         outputs/videos_pl/{slug}/thumbnails*/
    │                                     │
    └─────────────┬───────────────────────┘
                  │  (record voiceover → studio_one export → WAV)
                  ▼
[Align Agent] (post-record)
    │  faster-whisper aligns voiceover.wav to known script
    ▼
outputs/videos_pl/{slug}/edit/
  subtitles.srt + timeline.fcpxml + preview.html + alignment.json
                  │
                  ▼
            Import into DaVinci Resolve → final edit → publish
```

---

## Prerequisites

### 1. Python

Python 3.10 or later.

```bash
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root. Required:

```
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

Optional:

```
NCBI_API_KEY=your-ncbi-key                 # raises PubMed rate limits
```

### 3. Vertex AI authentication

```bash
gcloud auth application-default login
```

Required for Agents 1, 2, 6, and 7.

---

## End-to-End Walkthrough

Example topic: `"emotional dysregulation in ADHD"` — slug: `emotional-dysregulation-in-adhd`

All commands prefix with `PYTHONIOENCODING=utf-8` on Windows to avoid Unicode print errors.

### Step 0 — Materials (optional)

Before starting, check `materials/` for any relevant PDF books. Always ask which PDF to use — never auto-select. If no book is available, skip to Step 1.

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent0_materials.py --topic "emotional dysregulation in ADHD" --pdf "materials/Your Book.pdf"
```

Review: `outputs/videos_pl/emotional-dysregulation-in-adhd/md/00_materials_insights.md`. Re-run if extraction looks thin.

See [00_materials.md](00_materials.md) for the full SOP.

### Step 1 — Research

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent1_research.py "emotional dysregulation in ADHD"
```

Queries Gemini 3.1 Pro with Google Search Grounding and PubMed (top 10 papers). Review: `outputs/videos_pl/emotional-dysregulation-in-adhd/md/01_research.md`.

### Step 2 — Verify

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "emotional-dysregulation-in-adhd"
```

Gemini 3.1 Pro fact-checks every claim against peer-reviewed sources. Review every Flagged claim before continuing.

### Step 3 — Script (Writer → ensemble → merge → Fixer → validator, cold subagents)

In Claude Code:

```text
/draft emotional-dysregulation-in-adhd
```

That slash command runs the whole script chain **in-session — no API** as cold subagents, one pass: **3a Writer** (Opus) saves `md/03a_draft.md` (1500–2200 words, promise architecture); a **3b ensemble** reads the frozen draft in parallel — one section-checker per `## ` (Sonnet) plus one arc-checker with a loop map (Opus); `draft_merge.py` merges findings into `md/03b_corrections.md`; **3c Fixer** (Opus) applies them surgically, skipping clearly-worse proposals (`md/iter/fixer_skips.md`); the machine snapshot is copied to `md/04_final_machine.md` (untouchable); `draft_check.py --export` validates doctrine and exports `docx/script.docx`. No loop. Review the loop map and `md/04_final.md`; the final editorial pass (including trimming over-writing) is yours on `docx/script_corrected.docx`. See [03a_writer.md](03a_writer.md), [03b_section_checker.md](03b_section_checker.md), [03b_arc_checker.md](03b_arc_checker.md), [03c_fixer.md](03c_fixer.md), [voice_brief.md](../guides/voice_brief.md).

### Steps 5 & 8 — Parallel-safe after 3

```bash
# Both run in Claude Code (Opus 4.8, in-session — no API):
#   /visuals emotional-dysregulation-in-adhd
#   /publish emotional-dysregulation-in-adhd
```

- Agent 5 — one Imagen prompt per sentence/beat with beat-aware visual register
- Agent 8 — 9 focused steps: titles, description + hashtags, timestamps, long-form tags, bibliography, then shorts clip-selection / titles / descriptions / tags. Legacy Gemini end-to-end stays at `agent8_publish.py "<slug>" --api`.

Review `05_image_prompts.md` carefully — it is the only gate before image cost. See [05_visuals.md](05_visuals.md) and [08_publish.md](08_publish.md).

### **STOP — manual gate before Agents 6 and 7**

Agents 6 and 7 cost API credits and time. Always pause after Agent 8 completes and wait for explicit instruction before running either. This is a locked invariant.

### Step 6 — Generate Images (manual)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "emotional-dysregulation-in-adhd" --generate
```

Renders each prompt via Gemini 3 Pro Image Preview at 16:9. See [06_images.md](06_images.md).

### Step 7 — Generate Package: titles + thumbnails (manual)

In Claude Code (generates 3 packaging strategies in-session, then renders 3):

```text
/package emotional-dysregulation-in-adhd
```

Three packaging strategies (title + napis + visual concept) via Opus 4.8 (in-session, no API) → 3 thumbnails rendered by `agent7_package.py --render` on Gemini 3 Pro Image Preview. Grain + napis overlay added manually in Canva. Runs before `/publish` (its title feeds Agent 8). See [07_package.md](07_package.md).

### Align — Post-Record (DaVinci Bundle)

After recording your voiceover in Studio One and exporting to `outputs/videos_pl/{slug}/voiceover/voiceover.wav`:

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "emotional-dysregulation-in-adhd"
```

Forced alignment (faster-whisper, local, free) produces an SRT + FCPXML you import into DaVinci Resolve. See [align.md](align.md) and the one-time [davinci_subtitle_preset.md](../guides/davinci_subtitle_preset.md) setup.

---

## Output File Reference

All files live in `outputs/videos_pl/{slug}/`.

| Agent | File | Description |
|-------|------|-------------|
| 0 | `md/00_materials_insights.md` | Book insights extracted from reference PDF (optional) |
| 1 | `md/01_research.md` | Raw research from Gemini and PubMed |
| 2 | `md/02_verified_research.md` | Claims categorised as Verified, Flagged, or Removed |
| 3a | `md/03a_draft.md` | Writer's first-pass narration (input to the 3b ensemble) |
| 3b | `md/03b_corrections.md` | Merged ensemble corrections (section-checkers + arc-checker): quote + why + natural rewrite |
| 3c | `md/04_final.md` | Final machine script (Fixer applies corrections; trimming = user docx pass) |
| 3c | `md/iter/fixer_skips.md` | Fixer skip log (clearly-worse proposals left out) |
| 3 | `md/04_final_machine.md` | Untouchable machine snapshot (ceiling metric vs `script_corrected`) |
| 5 | `md/05_image_prompts.md` | One Imagen prompt per sentence/beat |
| 5 | `md/05_phrases.md` | Short phrase index used by Align |
| 3 | `docx/script.docx` | Teleprompter-ready script, exported by `draft_check.py --export` (edit → save as `script_corrected.docx`) |
| 8 | `md/08_publish.md` | Titles, 5 Shorts packages, YouTube metadata |
| 6 | `images/image_NNN.png` | Generated 16:9 images |
| 7 | `thumbnails_no_grain/thumbnail_NN.png` | 3 packaging thumbnails at 1920×1080 |
| Align | `edit/subtitles.srt` + `edit/timeline.fcpxml` + `edit/preview.html` + `edit/alignment.json` | DaVinci bundle |
| 3, 5, 6, 8 | `docx/*.docx` | Word exports of the corresponding markdown |

---

## Science Standard

Every factual claim in the final script must originate from the **Verified Claims** section of `md/02_verified_research.md`. Flagged claims require stronger peer-reviewed sources before use. Removed claims must not appear anywhere in the script. Pop-science sources (Psychology Today, Verywell Mind, WebMD, news articles, blogs) are not acceptable regardless of context.

---

## Common Troubleshooting

| Error | Fix |
|-------|-----|
| `Vertex AI error: Application Default Credentials not found` | Run `gcloud auth application-default login` |
| `GOOGLE_CLOUD_PROJECT not set` | Add `GOOGLE_CLOUD_PROJECT=your-project-id` to `.env` |
| Agent 2 returns `Verified: 0 claims` | Topic too broad — try a more specific phrasing |
| Agent 6 `--generate`: `md/05_image_prompts.md not found` | Run Agent 5 first |
| Unicode errors on Windows | Prefix the command with `PYTHONIOENCODING=utf-8` |

---

## Detailed Workflow Links

```
workflows/pipeline/00_materials.md   — Agent 0 (reference book extraction)
workflows/pipeline/01_research.md    — Agent 1
workflows/pipeline/02_verify.md      — Agent 2
workflows/pipeline/03a_writer.md     — Agent 3a (Writer)
workflows/pipeline/03b_section_checker.md / 03b_arc_checker.md — Agent 3b ensemble (section + arc)
workflows/pipeline/03c_fixer.md      — Agent 3c (Fixer)
workflows/pipeline/05_visuals.md     — Agent 5 (visual storytelling)
workflows/pipeline/08_publish.md     — Agent 8 (titles, shorts, metadata)
workflows/pipeline/06_images.md      — Agent 6 (image generation, manual)
workflows/pipeline/07_package.md     — Package (title+thumbnail strategist, manual)
workflows/pipeline/align.md          — Align (post-record DaVinci bundle)
workflows/guides/voice_brief.md      — Script-voice canon (7 rules, v2 2026-06-07)
workflows/guides/style_guide_images.md — Image style rules
workflows/guides/davinci_subtitle_preset.md — One-time DaVinci subtitle preset
```
