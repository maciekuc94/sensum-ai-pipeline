# Master SOP: YouTube Psychology Content Pipeline

This pipeline takes a psychology topic from raw idea to a production-ready narration script with AI-generated images, thumbnails, and a publish package. It pulls from two scientific sources (Gemini + Google Search, PubMed), verifies every claim against peer-reviewed sources, and writes a structured YouTube script before generating visuals. All output is local; nothing is published automatically.

For high-level operating invariants (color palette, file layout, model routing, locked output formats), see [CLAUDE.md](../../CLAUDE.md). For per-step detail, see the matching `workflows/pipeline/NN_*.md` file.

---

## Architecture

```
Topic (string)
    │
    ▼
[Agent 0: Materials] (optional)
    │  Extracts insights from a reference PDF via Gemini 3.1 Pro
    ▼
outputs/videos/{slug}/md/00_materials_insights.md
    │
    ▼
[Agent 1: Research]
    │  Gemini 3.1 Pro (Google Search Grounding) + PubMed
    ▼
outputs/videos/{slug}/md/01_research.md
    │
    ▼
[Agent 2: Verify]
    │  Gemini 3.1 Pro classifies every claim: VERIFIED / FLAGGED / REMOVED
    ▼
outputs/videos/{slug}/md/02_verified_research.md
    │
    ▼
[Agent 3: Script — orchestrates 3a → 3n → 3b → 3c]
    │  3a Draft   — Claude Opus 4.7 writes ~1,700-word narration
    │  3n Novelty — Sonnet 4.6 dedupes against prior shipped scripts
    │  3b Critic  — Sonnet 4.6 names the single weakest moment
    │  3c Rewrite — Opus 4.7 applies the critique
    ▼
outputs/videos/{slug}/md/03_script_draft.md  (+ 03a/03b/03n intermediates)
    │
    ▼
[Agent 4a: Edit]
    │  Sonnet 4.6 copy-edits for speech flow, active voice, zero jargon
    ▼
outputs/videos/{slug}/md/04_script_final.md
    │
    ▼
[Agent 4b: Hook Gate]  ◀──── must verdict RECORD before voiceover
    │  Sonnet 4.6 scores opening 37 words / 200 words; rewrites in place up to 3×
    ▼
outputs/videos/{slug}/md/04_script_final.md  (modified in place)
outputs/videos/{slug}/md/04b_hook_score.md
outputs/videos/{slug}/md/04_script_final.bak.md  (created once, never overwritten)
    │
    ├──────────────────────────────┬──────────────────────────────┐
    ▼                              ▼                              ▼
[Agent 5: Visuals]          [Agent 6: Narration]            [Agent 8: Publish]
    │  Opus 4.7 writes          │  Deterministic — strips        │  Sonnet 4.6 + YouTube
    │  one prompt per beat      │  EDITOR NOTEs + IMAGE markers  │  autocomplete scraper
    ▼                              ▼                              ▼
outputs/videos/{slug}/md/    outputs/videos/{slug}/md/      outputs/videos/{slug}/md/
  05_image_prompts.md          06_script_narration.md         07_publish_package.md
  05_image_phrases.md
    │                              │                              │
    │                              ▼                              │
    │                       [Agent 7: TTS] (optional, currently blocked)
    │                              │  Reference audio for pacing
    │                              ▼
    │                       outputs/videos/{slug}/tts/*.wav
    │                              │
    │   ┌──────────────────────────┴──────────────────────────────┘
    │   │  (manual gate — review all three before generating images/thumbs)
    │   │
    ▼   ▼
[Agent 9: Images] (manual)             [Agent 10: Thumbnails] (manual)
    │  Gemini 3 Pro Image Preview         │  Opus 4.7 → Gemini 3 Pro Image Preview
    ▼                                     ▼
outputs/videos/{slug}/images/         outputs/videos/{slug}/thumbnails*/
    │                                     │
    └─────────────┬───────────────────────┘
                  │  (record voiceover → studio_one export → WAV)
                  ▼
[Align Agent] (post-record)
    │  faster-whisper aligns voiceover.wav to known script
    ▼
outputs/videos/{slug}/edit/
  subtitles.srt + timeline.fcpxml + preview.html + alignment.json
                  │
                  ▼
            Import into DaVinci Resolve → final edit → publish
```

Out-of-band, on a weekly cron:

```
[Agent 11: Niche Intelligence]   (tools/intelligence/agent11_intelligence.py)
   YouTube API + Gemini Vision → outputs/intelligence/YYYY-WNN_*.pptx
   Sidecar `YYYY-WNN_tag_signals.md` is auto-read by Agent 8.
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
ANTHROPIC_API_KEY=your-key-here
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

Optional (Agent 11 niche intelligence only):

```
YOUTUBE_API_KEY=your-youtube-data-api-key
SENSUM_CHANNEL_ID=UCxxxxxxxxxxxxx
NCBI_API_KEY=your-ncbi-key       # raises PubMed rate limits
```

### 3. Vertex AI authentication

```bash
gcloud auth application-default login
```

Required for Agents 1, 2, 9, 10, and 11.

---

## End-to-End Walkthrough

Example topic: `"emotional dysregulation in ADHD"` — slug: `emotional-dysregulation-in-adhd`

All commands prefix with `PYTHONIOENCODING=utf-8` on Windows to avoid Unicode print errors.

### Step 0 — Materials (optional)

Before starting, check `materials/` for any relevant PDF books. Always ask which PDF to use — never auto-select. If no book is available, skip to Step 1.

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent0_materials.py --topic "emotional dysregulation in ADHD" --pdf "materials/Your Book.pdf"
```

Review: `outputs/videos/emotional-dysregulation-in-adhd/md/00_materials_insights.md`. Re-run if extraction looks thin.

See [00_materials.md](00_materials.md) for the full SOP.

### Step 1 — Research

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent1_research.py "emotional dysregulation in ADHD"
```

Queries Gemini 3.1 Pro with Google Search Grounding and PubMed (top 10 papers). Review: `outputs/videos/emotional-dysregulation-in-adhd/md/01_research.md`.

### Step 2 — Verify

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "emotional-dysregulation-in-adhd"
```

Gemini 3.1 Pro fact-checks every claim against peer-reviewed sources. Review every Flagged claim before continuing.

### Step 3 — Script (Draft → Novelty → Critic → Rewrite)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent3.py "emotional-dysregulation-in-adhd"
```

Runs all four sub-passes automatically. Review `md/03_novelty_report.md` and `md/03_script_draft.md`. Run the sub-agents individually (`agent3a_draft.py`, `agent3n_novelty.py`, `agent3b_critic.py`, `agent3c_rewrite.py`) if you want to inspect or edit an intermediate file.

### Step 4a — Edit

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent4a_edit.py "emotional-dysregulation-in-adhd"
```

Opens with `[EDITOR NOTE: ...]` annotations. Review for prose-only changes (no scientific claim alterations).

### Step 4b — Hook Gate

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent4b_hook.py "emotional-dysregulation-in-adhd"
```

Scores the opening 37 words (Tier 1, ≥8) and the opening 200 words (Tier 2, ≥7). Rewrites in place up to 3 attempts. Verdict must be `RECORD` before recording voiceover. See [04b_hook.md](04b_hook.md).

### Steps 5, 6, 8 — Parallel-safe after 4b

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent5_visuals.py "emotional-dysregulation-in-adhd"
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_narration.py "emotional-dysregulation-in-adhd"
PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "emotional-dysregulation-in-adhd"
```

- Agent 5 — one Imagen prompt per sentence/beat with beat-aware visual register
- Agent 6 — deterministic teleprompter strip (no API calls)
- Agent 8 — titles, hooks, 5 Shorts, description, chapters, bibliography, tags

Review `05_image_prompts.md` carefully — it is the only gate before image cost. See [05_visuals.md](05_visuals.md) and [08_publish.md](08_publish.md).

### Step 7 — TTS Voice Reference (optional, currently blocked)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_tts.py "emotional-dysregulation-in-adhd"
```

> Currently blocked. `MODEL_VERIFIED = False` because `gemini-3.1-flash-tts-preview` was never confirmed against Vertex. See [07_tts.md](07_tts.md) and the Technical Note in CLAUDE.md.

### **STOP — manual gate before Agents 9 and 10**

Agents 9 and 10 cost API credits and time. Always pause after Agent 8 completes and wait for explicit instruction before running either. This is a locked invariant.

### Step 9 — Generate Images (manual)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent9_images.py "emotional-dysregulation-in-adhd" --generate
```

Renders each prompt via Gemini 3 Pro Image Preview at 16:9. See [09_images.md](09_images.md).

### Step 10 — Generate Thumbnails (manual)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent10_thumbnails.py "emotional-dysregulation-in-adhd" --no-grain
```

Five thumbnail concepts via Opus 4.7 + Gemini 3 Pro Image Preview. Grain added manually in Canva after the title overlay. See [10_thumbnails.md](10_thumbnails.md).

### Align — Post-Record (DaVinci Bundle)

After recording your voiceover in Studio One and exporting to `outputs/videos/{slug}/voiceover/voiceover.wav`:

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "emotional-dysregulation-in-adhd"
```

Forced alignment (faster-whisper, local, free) produces an SRT + FCPXML you import into DaVinci Resolve. See [align.md](align.md) and the one-time [davinci_subtitle_preset.md](../guides/davinci_subtitle_preset.md) setup.

---

## Output File Reference

All files live in `outputs/videos/{slug}/`.

| Agent | File | Description |
|-------|------|-------------|
| 0 | `md/00_materials_insights.md` | Book insights extracted from reference PDF (optional) |
| 1 | `md/01_research.md` | Raw research from Gemini and PubMed |
| 2 | `md/02_verified_research.md` | Claims categorised as Verified, Flagged, or Removed |
| 3a | `md/03a_draft.md` | First-pass narration (rewritten in place by 3n) |
| 3n | `md/03_novelty_report.md` | Per-iteration n-gram + semantic dedupe log |
| 3n | `md/03a_draft.bak.md` | Pre-novelty backup of `03a_draft.md` (first run only) |
| 3b | `md/03b_critique.md` | Critic analysis — editable before 3c |
| 3c | `md/03_script_draft.md` | Rewritten script — feeds 4a |
| 4a | `md/04_script_final.md` | Copy-edited script |
| 4b | `md/04b_hook_score.md` | Hook score per attempt + final verdict |
| 4b | `md/04_script_final.bak.md` | Pre-hook-refine backup (first run only) |
| 5 | `md/05_image_prompts.md` | One Imagen prompt per sentence/beat |
| 5 | `md/05_image_phrases.md` | Short phrase index used by Align |
| 6 | `md/06_script_narration.md` | Clean teleprompter script |
| 7 | `tts/*.wav` | TTS reference audio (optional, currently blocked) |
| 8 | `md/07_publish_package.md` | Titles, hooks, 5 Shorts packages, YouTube metadata |
| 9 | `images/image_NNN.png` | Generated 16:9 images |
| 10 | `thumbnails_no_grain/thumbnail_NN.png` | 5 thumbnail concepts at 1920×1080 |
| Align | `edit/subtitles.srt` + `edit/timeline.fcpxml` + `edit/preview.html` + `edit/alignment.json` | DaVinci bundle |
| 4a, 5, 6, 8 | `docx/*.docx` | Word exports of the corresponding markdown |

---

## Science Standard

Every factual claim in the final script must originate from the **Verified Claims** section of `md/02_verified_research.md`. Flagged claims require stronger peer-reviewed sources before use. Removed claims must not appear anywhere in the script. Pop-science sources (Psychology Today, Verywell Mind, WebMD, news articles, blogs) are not acceptable regardless of context.

---

## Common Troubleshooting

| Error | Fix |
|-------|-----|
| `Vertex AI error: Application Default Credentials not found` | Run `gcloud auth application-default login` |
| `GOOGLE_CLOUD_PROJECT not set` | Add `GOOGLE_CLOUD_PROJECT=your-project-id` to `.env` |
| `ANTHROPIC_API_KEY not set` | Add `ANTHROPIC_API_KEY=your-key` to `.env` |
| Agent 2 returns `Verified: 0 claims` | Topic too broad — try a more specific phrasing |
| Agent 7 exits with code 1 immediately | `MODEL_VERIFIED = False` — see [07_tts.md](07_tts.md) |
| Agent 9 `--generate`: `md/05_image_prompts.md not found` | Run Agent 5 first |
| Unicode errors on Windows | Prefix the command with `PYTHONIOENCODING=utf-8` |

---

## Detailed Workflow Links

```
workflows/pipeline/00_materials.md   — Agent 0 (reference book extraction)
workflows/pipeline/01_research.md    — Agent 1
workflows/pipeline/02_verify.md      — Agent 2
workflows/pipeline/03_script.md      — Agents 3a / 3n / 3b / 3c
workflows/pipeline/04a_edit.md       — Agent 4a (script editing)
workflows/pipeline/04b_hook.md       — Agent 4b (hook gate)
workflows/pipeline/05_visuals.md     — Agent 5 (visual storytelling)
workflows/pipeline/06_narration.md   — Agent 6 (narration strip)
workflows/pipeline/07_tts.md         — Agent 7 (TTS — currently blocked)
workflows/pipeline/08_publish.md     — Agent 8 (titles, shorts, metadata)
workflows/pipeline/09_images.md      — Agent 9 (image generation, manual)
workflows/pipeline/10_thumbnails.md  — Agent 10 (thumbnails, manual)
workflows/pipeline/11_intelligence.md — Agent 11 (weekly niche report)
workflows/pipeline/align.md          — Align (post-record DaVinci bundle)
workflows/guides/style_guide.md      — Script style rules
workflows/guides/style_guide_images.md — Image style rules
workflows/guides/narrative_architectures.md — 4 narrative shapes + visual register maps
workflows/guides/davinci_subtitle_preset.md — One-time DaVinci subtitle preset
```
