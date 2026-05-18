# Agent 8 — Publish Package

## Purpose

Runs three passes in one command and produces a single master file with everything needed to publish the video on YouTube.

| Pass | What it does | Model |
|------|-------------|-------|
| 1 — Titles & Hooks | 5 title options + 2 alternative opening hooks | claude-opus-4-7 |
| 2 — YouTube Shorts | 5 clip segments, one per Short strategy | claude-opus-4-7 (3 sub-passes) |
| 3 — YouTube Metadata | Description, chapters, bibliography, tags | claude-opus-4-7 + YouTube scraper |

---

## Prerequisites

- `outputs/{slug}/md/04_script_final.md` — produced by Agent 4
- `outputs/{slug}/md/06_script_narration.md` — produced by Agent 6
- `outputs/{slug}/md/02_verified_research.md` — produced by Agent 2
- `ANTHROPIC_API_KEY` set in `.env`
- Internet access (for YouTube autocomplete scraping in Pass 3)

Run this agent after you have recorded your voiceover and completed video editing, so you can fill in the `[XX:XX]` chapter timestamps immediately.

---

## How to Run

```bash
python tools/agent8_publish.py "emotional-dysregulation-in-adhd"
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

[2/4] Pass 1 — Titles & Hooks...
  Querying claude-opus-4-7 — pass 1 — titles and hooks...
  Done (512 chars)

[3/4] Pass 2 — YouTube Shorts (3 sub-passes)...
  Querying claude-opus-4-7 — shorts pass 1 — candidate mapping...
  Querying claude-opus-4-7 — shorts pass 2 — selection...
  Querying claude-opus-4-7 — shorts pass 3 — titles and descriptions...
  Done (3,200 chars)

[4/4] Pass 3 — YouTube Metadata...
  Scraping YouTube autocomplete suggestions...
  Collected 187 unique suggestions
  Scraping competitor video tags...
  Collected 94 competitor tags
  Querying claude-opus-4-7 — pass 3 — YouTube metadata...
  Done

Saving md/07_publish_package.md...
  Saved: outputs/emotional-dysregulation-in-adhd/md/07_publish_package.md
  Word export: outputs/emotional-dysregulation-in-adhd/docx/07_publish_package.docx

Done. Review md/07_publish_package.md before uploading to YouTube.
```

---

## Output

**`outputs/{slug}/md/07_publish_package.md`** — one master file with three sections:

```
# Publish Package — {topic}

---

## Titles & Opening Hooks
1. **[Title 1]**
...
Hook A: [text]
Hook B: [text]

---

## YouTube Shorts Package
## Short 1 — Surprise
**Why this works:** ...
**Title:** ...
**Description:** ...
**Tags:** tag 1, tag 2, ...
**Script lines to clip:**
> [exact lines]

---
[... 4 more Shorts ...]

---

## Video Description (paste into YouTube Studio)
[4 paragraphs]

Timestamps:
00:00 Introduction
[XX:XX] ...

📚 Research & References:
...

## YouTube Tags
tag 1, tag 2, ...
```

**`outputs/{slug}/docx/07_publish_package.docx`** — Word export of the same file.

---

## How to Review

### Titles & Hooks

- Pick one title. Paste it into YouTube Studio when uploading.
- Hook A / Hook B are optional replacements for your video's opening line — useful if you want to re-record the intro.

### YouTube Shorts

- 5 Short strategies: Surprise, Emotion, Standalone, CTA-Hook, Practical Tip
- Find each quoted passage in your video editor timeline and clip it
- Paste the provided Title and Description when uploading each Short to YouTube
- Add `#Shorts` hashtag (already included in descriptions)

### YouTube Metadata

- Fill in the `[XX:XX]` chapter timestamps after your video edit is locked
- Paste the full description block into YouTube Studio > Description
- Paste all tags into YouTube Studio > Tags field (comma-separated, no # prefix)
- Verify bibliography links match the sources in `02_verified_research.md`

---

## Pass 2: Shorts — Five Strategy Types

| Type | Psychology trigger |
|------|--------------------|
| Surprise | Contradicts a common belief — stops the scroll |
| Emotion | Fear, shame, hope, or identity — hits personally |
| Standalone | Complete idea — full value without the main video |
| CTA-Hook | Open loop — leaves the viewer wanting more |
| Practical Tip | One concrete action the viewer can apply now |

Pass 2 runs three sub-passes internally:
1. **Candidate mapping** — surveys every passage for all five types
2. **Selection** — picks the single strongest per type (no shared lines)
3. **Metadata** — writes a title and description for each selected clip

---

## Common Issues

| Error | Fix |
|-------|-----|
| `md/04_script_final.md not found` | Run Agent 4 first |
| `md/06_script_narration.md not found` | Run Agent 6 first |
| `md/02_verified_research.md not found` | Run Agent 2 first |
| YouTube scraping returns 0 suggestions | Network issue — tags will be AI-generated from topic knowledge |
| `No JSON found in Claude response` | Retry — rare parsing failure on metadata pass |
