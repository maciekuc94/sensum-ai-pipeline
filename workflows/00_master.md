# Master SOP: YouTube Psychology Content Pipeline

This pipeline takes a psychology topic from raw idea to a production-ready narration script with AI-generated images. It pulls from two scientific sources (Gemini + Google Search, PubMed), verifies every claim against peer-reviewed sources, and writes a structured YouTube script before generating visuals. All output is local; nothing is published automatically.

---

## Architecture

```
Topic (string)
    │
    ▼
[Agent 0: Materials] (optional)
    │  Extracts insights from a reference book PDF via Gemini 2.5 Flash
    │
    ▼
outputs/[slug]/md/00_materials_insights.md (if book provided)
    │
    ▼
[Agent 1: Research]
    │  Queries Gemini 2.5 Pro (Google Search Grounding) + PubMed
    │
    ▼
outputs/[slug]/md/01_research.md
    │
    ▼
[Agent 2: Verify]
    │  Gemini classifies every claim as VERIFIED / FLAGGED / REMOVED
    │
    ▼
outputs/[slug]/md/02_verified_research.md
    │
    ▼
[Agent 3a: Draft]
    │  Claude Opus 4.7 writes a ~1,700-word narration script
    │  Chooses one of 4 narrative architectures
    │
    ▼
outputs/[slug]/md/03a_draft.md  ← REVIEW
    │
    ▼
[Agent 3n: Novelty]
    │  Compares draft against every prior shipped narration:
    │  - Pass A: 4-token n-gram literal match
    │  - Pass B: Claude semantic / structural reuse check
    │  - Pass C: Claude rewrites flagged spans in place (iterate up to 3x)
    │
    ▼
outputs/[slug]/md/03_novelty_report.md  ← REVIEW
outputs/[slug]/md/03a_draft.md          ← updated in place (original at 03a_draft.bak.md)
    │
    ▼
[Agent 3b: Critic]
    │  Claude Opus 4.7 identifies the single weakest moment
    │
    ▼
outputs/[slug]/md/03b_critique.md  ← REVIEW + OPTIONALLY EDIT
    │
    ▼
[Agent 3c: Rewrite]
    │  Claude Opus 4.7 applies the fix — returns complete script
    │
    ▼
outputs/[slug]/md/03_script_draft.md
    │
    ▼
[Agent 4: Edit]
    │  Claude Opus 4.7 copy-edits for speech flow, active voice, and zero jargon
    │
    ▼
outputs/[slug]/md/04_script_final.md
    │
    ├──────────────────────────────────────────────────────────┐
    ▼                                                          ▼
[Agent 6: Narration]                               [Agent 5: Visual Storytelling]
    │  Strips EDITOR NOTEs →                           │  Claude Opus 4.7 reads the finished script
    │  clean teleprompter script                        │  and writes one prompt per sentence
    ▼                                                  │  as a dedicated visual director
outputs/[slug]/md/06_script_narration.md           ▼
                                           outputs/[slug]/md/05_image_prompts.md  ← REVIEW + EDIT
    │
    ▼
[Agent 7: TTS Voice Reference] (optional)
    │  Gemini Flash TTS reference audio (voice: Puck)
    │
    ▼
outputs/[slug]/tts/gemini_Puck.wav
    │
    ▼ (record voiceover in DaVinci Resolve)
    │
    ▼
[Agent 9: Generate Images]
    │  Sends each prompt to Vertex AI Imagen
    ▼
outputs/[slug]/images/image_001.png … image_NNN.png
    │
    ▼
[Agent 8: Publish Package]
    │  Claude Opus 4.7 generates titles, hooks, 5 YouTube Shorts packages,
    │  description, chapters, bibliography, tags
    │  YouTube autocomplete scraping provides real SEO keyword data
    │
    ▼
outputs/[slug]/md/07_publish_package.md
outputs/[slug]/docx/07_publish_package.docx
```

---

## Prerequisites

### 1. Python

Python 3.10 or later.

```bash
pip install -r requirements.txt
```

### 2. Environment variables

Create a `.env` file in the project root. Required vars:

```
ANTHROPIC_API_KEY=your-key-here
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

Optional vars (higher rate limits, not required):

```
NCBI_API_KEY=your-ncbi-key       # PubMed works without this; key raises rate limits
```

### 3. Vertex AI authentication

```bash
gcloud auth application-default login
```

This is required for Agents 1, 2, and 9. Run it once; credentials are cached.

---

## End-to-End Walkthrough

Example topic: `"emotional dysregulation in ADHD"` — slug: `emotional-dysregulation-in-adhd`

---

### Step 0 — Materials (optional)

Before starting, check `materials/` for any relevant PDF books. Always ask which PDF to use — never auto-select.

If a book is available:

```bash
python tools/agent0_materials.py --topic "emotional dysregulation in ADHD" --pdf "materials/Your Book.pdf"
```

If no book is available, skip this step entirely and proceed to Step 1.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/00_materials_insights.md`. Check that key frameworks and examples were captured. Re-run if the extraction looks thin.

See `workflows/00_materials.md` for the full SOP.

---

### Step 1 — Research

```bash
python tools/agent1_research.py "emotional dysregulation in ADHD"
```

Queries Gemini 2.5 Pro with Google Search Grounding and PubMed (top 10 papers). Synthesises results into a structured markdown document.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/01_research.md`. Check that the Studies Referenced table contains DOIs, and that the Raw Gemini Research Summary references peer-reviewed papers. If only pop-science sources appear, narrow the topic and re-run.

---

### Step 2 — Verify

```bash
python tools/agent2_verify.py "emotional-dysregulation-in-adhd"
```

Sends the research document to Gemini for claim-by-claim fact-checking. Produces three lists: Verified, Flagged, Removed.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/02_verified_research.md`. Check the Summary line. Read every Flagged claim — decide whether to accept the risk or find stronger sources. Removed claims must not appear in the final script.

---

### Step 3 — Script (Draft → Critic → Rewrite)

```bash
python tools/agent3.py "emotional-dysregulation-in-adhd"
```

Runs all four passes automatically:

1. **3a Draft** — Claude Opus 4.7 writes a ~1,700-word narration script, choosing one of four narrative architectures
2. **3n Novelty** — Compares the draft against every prior shipped narration. Pass A is a deterministic 4-token n-gram match; Pass B is a Claude semantic/structural check; Pass C rewrites flagged spans in place, iterating up to 3 times. The original draft is preserved at `md/03a_draft.bak.md`. See `workflows/03_script.md` for the full SOP and `md/03_novelty_report.md` for findings.
3. **3b Critic** — Claude Opus 4.7 identifies the single weakest moment as a first-time viewer
4. **3c Rewrite** — Claude Opus 4.7 applies the fix; only the weak section is replaced

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/03_novelty_report.md`. If the verdict is `PASS` or `PASS_AFTER_REWRITE`, continue. If `RESIDUAL_AFTER_3_ATTEMPTS`, skim the residual semantic findings and decide whether to manually edit before Agent 4a. Then open `md/03_script_draft.md` and check word count and that the rewritten section flows naturally.

> **Manual control:** Run `agent3a_draft.py`, `agent3n_novelty.py`, `agent3b_critic.py`, `agent3c_rewrite.py` individually if you want to inspect or edit an intermediate file before the next pass.

---

### Step 4a — Edit

```bash
python tools/agent4a_edit.py "emotional-dysregulation-in-adhd"
```

Claude Opus 4.7 copy-edits the draft: rewrites passive constructions, removes hedging language, ensures every scientific term has a plain-language explanation. Returns the full edited script with inline `[EDITOR NOTE: ...]` annotations.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/04_script_final.md`. Skim the EDITOR NOTEs — they should document prose improvements only. If any note touches a scientific claim, read that passage carefully.

---

### Step 4b — Hook Scorer

```bash
python tools/agent4b_hook.py "emotional-dysregulation-in-adhd"
```

Scores the opening 150–200 words on a 1–10 scale (tension, personal relevance, specificity, forward momentum). Provides a targeted rewrite suggestion for the weakest element. Final quality gate before recording.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/04b_hook_score.md`. If the score is 7+, proceed to record. If 5–6, apply the rewrite suggestion to `04_script_final.md` and re-run. If below 5, rewrite the opening.

See `workflows/04b_hook.md` for the full SOP.

---

### Step 5 — Visual Storytelling

```bash
python tools/agent5_visuals.py "emotional-dysregulation-in-adhd"
```

Claude Opus 4.7 reads the finished edited script and writes one image prompt per sentence (or per visual beat). Can be run in parallel with Step 6.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/05_image_prompts.md`. Check that every sentence is covered, composition variety is strong, and emotional accuracy is right. Edit any prompts that are vague or use forbidden terms. This is the only gate before images are generated.

See `workflows/05_visuals.md` for the full SOP.

---

### Step 6 — Narration Script

```bash
python tools/agent6_narration.py "emotional-dysregulation-in-adhd"
```

Strips `[EDITOR NOTE: ...]` annotations from the final script to produce a clean teleprompter-ready narration file. No AI calls. Can be run in parallel with Step 5.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/06_script_narration.md`. Confirm no `[EDITOR NOTE:` text remains. Read the opening paragraph aloud — it should flow naturally.

---

### Step 7 — TTS Voice Reference (optional)

```bash
python tools/agent7_tts.py "emotional-dysregulation-in-adhd"
```

Generates a single Gemini Flash TTS reference audio file (voice: Puck) from the narration script. Use `--all` to generate all 11 voice variants.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/tts/gemini_Puck.wav`. Listen and use as a pacing reference during recording. Delete the file after recording.

See `workflows/07_tts.md` for the full SOP.

---

### Step 9 — Generate Images

**Prerequisite:** Agent 5 must have run and `md/05_image_prompts.md` must be reviewed.

```bash
python tools/agent9_images.py "emotional-dysregulation-in-adhd" --generate
```

Calls Vertex AI Imagen for each prompt. Saves PNGs to `outputs/emotional-dysregulation-in-adhd/images/`.

**Review:** Open `outputs/emotional-dysregulation-in-adhd/images/`. Check image count matches prompt count. Regenerate individual images by editing the prompt in `05_image_prompts.md` and re-running.

---

### Step 8 — Publish Package

```bash
python tools/agent8_publish.py "emotional-dysregulation-in-adhd"
```

Runs three passes in one command:
1. **Titles & Hooks** — 5 title options + 2 alternative opening hooks
2. **YouTube Shorts** — 5 clip segments, one per Short strategy (Surprise, Emotion, Standalone, CTA-Hook, Practical Tip)
3. **YouTube Metadata** — description, chapter timestamps, bibliography, SEO tags (with live YouTube autocomplete scraping)

**Review:** Open `outputs/emotional-dysregulation-in-adhd/md/07_publish_package.md`. Pick a title, fill in the `[XX:XX]` timestamps after video editing, clip the Shorts passages in your timeline, then paste everything into YouTube Studio.

See `workflows/08_publish.md` for the full SOP.

---

## Output File Reference

All files live in `outputs/[slug]/`.

| Agent | File | Description |
|-------|------|-------------|
| 0 | `md/00_materials_insights.md` | Book insights extracted from reference PDF (optional) |
| 1 | `md/01_research.md` | Raw research from Gemini and PubMed |
| 2 | `md/02_verified_research.md` | Claims categorised as Verified, Flagged, or Removed |
| 3a | `md/03a_draft.md` | First-pass narration script — review before running 3n |
| 3n | `md/03_novelty_report.md` | Per-iteration log of literal + semantic duplicate spans, rewrites applied, and final verdict (`PASS` / `PASS_AFTER_REWRITE` / `RESIDUAL_AFTER_3_ATTEMPTS`) |
| 3n | `md/03a_draft.bak.md` | Pre-novelty backup of `md/03a_draft.md` (created only on first novelty run) |
| 3b | `md/03b_critique.md` | Critic analysis — review and optionally edit before running 3c |
| 3c | `md/03_script_draft.md` | Rewritten script — feeds Agent 4a |
| 4a | `md/04_script_final.md` | Copy-edited script — source for narration AND Agent 5 |
| 4b | `md/04b_hook_score.md` | Hook score 1–10, weakness, rewrite suggestion — review before recording |
| 5 | `md/05_image_prompts.md` | One Imagen prompt per sentence/beat, written by the visual storytelling agent |
| 6 | `md/06_script_narration.md` | Clean narration script (no EDITOR NOTEs) — for recording |
| 7 | `tts/gemini_Puck.wav` | TTS reference audio — optional, delete after recording |
| 9 | `images/image_001.png` … | Generated 16:9 images, one per script marker |
| 8 | `md/07_publish_package.md` | Titles, hooks, 5 Shorts packages, YouTube metadata |
| 4a, 5, 6, 8 | `docx/*.docx` | Word exports of the corresponding markdown files |

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
| Agent 9 `--generate`: `md/05_image_prompts.md not found` | Run Agent 5 first |

---

## Detailed Workflow Links

```
workflows/00_materials.md  — Agent 0 detailed SOP (reference book extraction)
workflows/01_research.md   — Agent 1 detailed SOP
workflows/02_verify.md     — Agent 2 detailed SOP
workflows/03_script.md     — Agents 3a / 3n / 3b / 3c detailed SOP (script writing + novelty dedupe)
workflows/04a_edit.md      — Agent 4a detailed SOP (script editing)
workflows/04b_hook.md      — Agent 4b detailed SOP (hook scorer)
workflows/05_visuals.md    — Agent 5 detailed SOP (visual storytelling)
workflows/06_narration.md  — Agent 6 detailed SOP (narration script)
workflows/07_tts.md        — Agent 7 detailed SOP (TTS voice reference, optional)
workflows/08_publish.md    — Agent 8 detailed SOP (titles, shorts, YouTube metadata)
workflows/09_images.md     — Agent 9 detailed SOP (image generation)
workflows/style_guide.md   — Script style rules and example transcript
```
