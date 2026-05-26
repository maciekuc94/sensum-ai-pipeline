# Workflow: Agent 6 — Narration Script

## Purpose

Agent 6 converts `04_script_final.md` into a clean teleprompter-ready narration script. It strips every `[IMAGE: ...]` marker and every `[EDITOR NOTE: ...]` inline annotation, leaving pure spoken prose that can be read directly into a microphone or pasted into teleprompter software.

This step produces no images and makes no AI calls. It is deterministic, free, and safe to re-run.

---

## Prerequisites

1. **Agent 3 must have run successfully.** The file `outputs/videos_pl/{slug}/md/04_script_final.md` must exist (orchestrator copies it after the Revisor↔Reviewer loop exits).

2. **No API keys required.** This tool is pure Python with no external dependencies.

---

## Run Command

```bash
python tools/pipeline/agent6_narration.py "emotional-dysregulation-in-adhd"
```

Note: the argument is the **slug** (hyphenated, lowercase), the same slug used throughout the pipeline.

Example output:

```
=== Agent 6: Narration Script ===
Slug  : emotional-dysregulation-in-adhd
Input : outputs/videos_pl/emotional-dysregulation-in-adhd/md/04_script_final.md
Output: outputs/videos_pl/emotional-dysregulation-in-adhd/md/06_script_narration.md
Words : 1,712

Done. Review the narration script before recording voiceover.
```

---

## What the Script Strips

| Marker | Example | Action |
|--------|---------|--------|
| IMAGE line | `[IMAGE: a figure seated at a desk, sparse cross-hatching]` | Line removed entirely |
| EDITOR NOTE | `[EDITOR NOTE: changed "X" to "Y" — reason: ...]` | Stripped inline; surrounding prose preserved |

Blank lines are collapsed so no double-blank gaps remain.

---

## Reviewer Checklist

Open `outputs/videos_pl/{slug}/md/06_script_narration.md` and confirm:

- No `[IMAGE:` or `[EDITOR NOTE:` text anywhere in the file
- Word count printed by the tool falls between **1,500 and 2,000 words**
- Read the first paragraph aloud — does it flow naturally?
- Read the prescription section aloud — are the action items punchy and clear?
- The outro teases the next video by name

If you find a stray marker, check whether it used an unusual bracket format (e.g. nested brackets) and re-run after fixing `04_script_final.md`.

---

## Output Location

```
outputs/
└── videos_pl/
    └── {slug}/
        └── md/
            ├── 04_script_final.md       (Agent 3 finalize — input for this step)
            └── 06_script_narration.md   (Agent 6 output — clean narration)
```

---

## Common Issues

**"Error: outputs/videos_pl/{slug}/md/04_script_final.md not found"**

Agent 3 has not been run yet for this slug, or the slug is misspelled. The orchestrator writes `04_script_final.md` automatically when the Revisor↔Reviewer loop exits.

```bash
python tools/pipeline/agent3.py "{slug}"
python tools/pipeline/agent6_narration.py "{slug}"
```

**Word count is below 1,500**

The final script was shorter than expected. Go back and check `04_script_final.md` directly — the narration tool strips only markers, not content. If the script itself is thin, re-run Agent 3.

---

## Next Step

Once you have reviewed the narration script, run Agent 8 for the publish package:

```bash
python tools/pipeline/agent8_publish.py "{slug}"   # titles, hooks, Shorts, metadata
```
