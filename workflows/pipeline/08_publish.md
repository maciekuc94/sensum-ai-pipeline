# Agent 8 — Publish Package

## Purpose

Runs three passes in one command and produces a single master file with everything needed to publish the long-form video on YouTube — plus 3–5 Shorts lead-in packages designed to drive clicks back to the main video.

Agent 8 operates as an **Advanced YouTube Metadata Engineer / NLP Optimization Pipeline** — cold, empirical decision logic for tag selection and NLP anchoring; warm, validating speaker voice in the description and Shorts body copy.

| Pass | What it does | Model |
|------|-------------|-------|
| 1 — Titles | 5 long-form title variants in the Identity Provocation blueprint (identity reframe / paradox / system-architectural reveal) | claude-sonnet-4-6 |
| 2 — YouTube Shorts | 3–5 lead-in packages — single identity-reframe title, cognitive-dissonance description, 3–5 multi-word backend tags, Hook + Core-payload clip split with Q1–Q4 marker | claude-sonnet-4-6 (3 sub-passes) |
| 3 — YouTube Metadata | Description (Hook Segment + Explanatory Block with identity-absolution framing), chapters, bibliography, 3 hashtags, 10–15 multi-word tag block (Tag #1 = exact-match primary keyword from chosen title) | claude-sonnet-4-6 + YouTube scrapers |

---

## Prerequisites

- `outputs/videos/{slug}/md/04_script_final.md` — produced by Agent 4
- `outputs/videos/{slug}/md/06_script_narration.md` — produced by Agent 6
- `outputs/videos/{slug}/md/02_verified_research.md` — produced by Agent 2
- `ANTHROPIC_API_KEY` set in `.env`
- Internet access (for YouTube autocomplete scraping in Pass 3)
- _Optional:_ latest `outputs/intelligence/*_tag_signals.md` (auto-produced by Agent 11 alongside the weekly PPTX). Agent 8 uses it as a **supporting reference** for the back half of the tag list when present; behaves identically if absent. Single-word terms in the signals block are rendered as multi-word phrases in the final tags. The **primary signal** for Tag #1 is the chosen long-form title — niche signals expand from there.

Run this agent after you have recorded your voiceover and completed video editing, so you can fill in the `[XX:XX]` chapter timestamps immediately.

---

## How to Run

```bash
python tools/pipeline/agent8_publish.py "emotional-dysregulation-in-adhd"
```

Expected output:

```
=== Agent 8: Publish Package ===
Slug : emotional-dysregulation-in-adhd

[1/4] Reading input files...
  Topic    : emotional dysregulation in ADHD
  Script   : 9,240 chars
  Narration: 8,100 chars
  Research : 7,500 chars

[2/4] Pass 1 — Titles (Identity Provocation)...
  Querying claude-sonnet-4-6 — pass 1 — titles...
  Done (512 chars)

[3/4] Pass 2 — YouTube Shorts (3 sub-passes)...
  Querying claude-sonnet-4-6 — shorts pass 1 — candidate mapping...
  Querying claude-sonnet-4-6 — shorts pass 2 — selection...
  Querying claude-sonnet-4-6 — shorts pass 3 — titles and descriptions...
  Done (3,200 chars)

[4/4] Pass 3 — YouTube Metadata...
  Scraping YouTube autocomplete suggestions...
  Collected 187 unique suggestions
  Scraping competitor video tags...
  Collected 94 competitor tags
  Querying claude-sonnet-4-6 — pass 3 — YouTube metadata...
  Tag block: 12 tags, 432 chars (within doctrine; under 450-char target; YouTube cap is 500)
  Done

Saving md/07_publish_package.md...
  Saved: outputs/videos/emotional-dysregulation-in-adhd/md/07_publish_package.md
  Word export: outputs/videos/emotional-dysregulation-in-adhd/docx/07_publish_package.docx

Done. Review md/07_publish_package.md before uploading to YouTube.
```

---

## Output

**`outputs/videos/{slug}/md/07_publish_package.md`** — one master file with three sections:

```
# Publish Package — {topic}

---

## Titles
1. [Identity reframe title]
2. [Paradox title]
3. [System-architectural reveal title]
4. ...
5. ...

---

## Video Description (paste into YouTube Studio)

[Block 1 — Hook Segment: 3–6 visceral fragments, no filler]

[Block 2 — Explanatory Block with identity-absolution framing, names 3–5 concepts in plain language]

Timestamps:
00:00 Introduction
[XX:XX] Core Concept A
[XX:XX] ...

Research & References:
• Concept Label — Qualifier: Author, A., et al. (Year).
• ...

#sensum #topic #concept

---
*SENSUM — Science of Kindness*

---

## YouTube Tags (copy all, paste into Tags field)

primary keyword phrase, long tail variant one, long tail variant two, supporting intent phrase, ..., broader category anchor, SENSUM (10–15 tags, comma-separated, under 450 chars; Tag #1 = exact-match primary keyword extracted from the chosen title)

---

## YouTube Shorts Package

## Short 1 — [self-chosen angle tag]
**Title:** [identity-reframe / paradox / system-reveal, max 60 chars]
**Description:** [1–2 sentences mapping cognitive dissonance] #Shorts #topic #concept
**Tags:** primary phrase for this Short, supporting variant, ... (3–5 multi-word phrases)
**Script Lines to Clip:**
Hook (first ~3s): [Q2]
> "exact opening line(s) from narration"

Core payload: [Q2]
> "exact line(s) carrying the core claim"

---
[... 2–4 more Shorts ...]
```

**`outputs/videos/{slug}/docx/07_publish_package.docx`** — Word export of the same file.

---

## How to Review

### Titles

- Pick one title. Paste it into YouTube Studio when uploading.
- All 5 should function as identity reframes, paradoxes, or system-architectural reveals. None should be instructional (`How to…`, `5 tips…`, `Ways to…`) — if one slipped through, regenerate.

### Video Description

- Block 1 must hit the viewer with concrete somatic / emotional fragments in the first two lines. No greeting, no setup, no conversational filler.
- Block 2 must lead with identity-absolution framing ("These aren't character flaws — they're the signals of…" or similar) and then name 3–5 concepts in plain language.
- Total under 120 words.

### Timestamps

- Fill in the `[XX:XX]` chapter timestamps after your video edit is locked. The `00:00 Introduction` row is correct out of the box.

### Research & References

- Verify bibliography entries match the sources in `02_verified_research.md`. Bibliography is decision-procedure driven: any thematic tie qualifies for inclusion; only true zero-tie entries are excluded.

### Tags (long-form)

- Paste the full comma-separated tag string into YouTube Studio > Tags field (no `#` prefix).
- **Tag #1 = exact-match primary keyword.** It should be a real search-shaped phrase (test by pasting into YouTube search — autocomplete should suggest queries shaped like it). If Tag #1 is metaphor-heavy and would not autocomplete, regenerate the metadata pass.
- 10–15 tags total. Slot order (front-loaded by algorithmic weight): Tag #1 (primary keyword), Tags #2–#5 (strongest variations), Tags #6–#12 (supporting intent phrases — this is where Niche Trend Signals get rendered as multi-word), Tags #13–#15 (optional broader 2–3 word category anchors).
- Every tag is multi-word (≥2 words). If you see a single-word entry that is not `SENSUM`, regenerate.
- `SENSUM` (uppercase) appears once as the only single-word brand entry. Slot anywhere.
- Total under 450 chars target (agent prints the actual length on completion; YouTube hard cap is 500).

### YouTube Shorts

- 3–5 Shorts. Each has ONE title (not a candidate list), a short description, 3–5 multi-word backend tags, and the Hook/Core-payload clip split. Backend tags are a categorization safety net on Shorts — the real algorithmic signal is the description hashtags (`#Shorts #sensum #topic`).
- The Q1–Q4 marker on each clip block tells you which quarter of the narration script the quoted line lives in — open `06_script_narration.md`, count to that quarter, and text-search for the quoted phrase to locate the cut in DaVinci.
- Paste the Title + Description into YouTube Studio when uploading each Short.

---

## Pass 2: Shorts — Selection Logic

Pass 2 runs three sub-passes internally:

1. **Candidate mapping** — surveys every passage in the narration script, applies the Triple Retention Filter (Cognitive Autonomy / Instant Hook / Curiosity Gap), and marks each passage PASS / BORDERLINE / FAIL on each filter.
2. **Selection** — selects up to 4 candidates that pass ALL THREE filters (hard AND-gate). No shared lines between Shorts. Angle tags are free-form (not constrained to a fixed menu).
3. **Lead-in packaging** — for each selected Short, generates one identity-reframe title, the cognitive-dissonance description, the 3–5 multi-word backend-tag block, and the Hook + Core-payload clip split. The deterministic post-step then tags each Hook / Core-payload label with the script quarter (Q1–Q4).

---

## Common Issues

| Error | Fix |
|-------|-----|
| `md/04_script_final.md not found` | Run Agent 4 first |
| `md/06_script_narration.md not found` | Run Agent 6 first |
| `md/02_verified_research.md not found` | Run Agent 2 first |
| YouTube scraping returns 0 suggestions | Network issue — tag-generation falls back on script + niche signals |
| `No JSON found in Claude response` | Retry — rare parsing failure on metadata pass |
| Tag block exceeds 500-char budget | Agent prints a WARNING; trim the weakest 1–2 phrases manually before pasting |
| `[Q?]` appears on a Shorts clip block | The quote line did not substring-match the narration — usually means the model paraphrased rather than quoted verbatim; either edit the quote to match the script, or regenerate the Shorts pass |
