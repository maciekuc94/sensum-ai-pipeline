---
description: Generate Agent 5 image prompts using in-session Opus (no API call), then expand into full Imagen prompts.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob
---

# /visuals — Agent 5 Visual Storytelling (in-session)

You are running Agent 5 (Visual Storyteller) of the SENSUM pipeline. Argument `$1` is the slug — a folder name under `outputs/videos_pl/`.

Your job: read the final script and generate compact image prompts *yourself* (you are Opus 4.8, in-session — no Anthropic API). Save the compact prompts file, then trigger `--expand` to inject CHARACTER_DESCRIPTION and STYLE_SUFFIX constants into every entry.

## Workflow

1. **Validate inputs**:
   - Confirm `outputs/videos_pl/$1/md/04_final.md` exists. If missing, tell the user to run `/draft $1` first (Agent 3 must complete), and stop.
   - **Hook-gate check:** if `outputs/videos_pl/$1/md/04_hook.md` is absent, `/hook` has not run — warn that image prompts will be anchored to an un-gated opening (and `05_phrases.md` row 1, which feeds Align's SRT, will be the unreviewed first line); recommend `/hook $1` first. Warn and continue.

2. **Load source materials**:
   - **Script source:** if `outputs/videos_pl/$1/docx/script_corrected.docx` exists, first run `python tools/pipeline/agent5_visuals.py "$1" --extract` to extract it to `md/script_corrected.md`, then use `md/script_corrected.md` as the script text (it reflects the user-edited version). Otherwise use `outputs/videos_pl/$1/md/04_final.md`. (Scripts are **not** tagged with any narrative architecture — that concept was retired 2026-06-04; read the script and follow the emotional arc it actually has, per `05_visuals.md`.)
   - `workflows/pipeline/05_visuals.md` — contains the exact visual direction instructions, beat registers, compact output format, and self-check list

3. **Generate the compact prompts file** following the Prompt section in `05_visuals.md`. Write to `outputs/videos_pl/$1/md/05_image_prompts.md` using the compact format: each entry uses `**Visual:**` containing only the 40–60 word visual description. Do NOT write CHARACTER_DESCRIPTION or STYLE_SUFFIX — those are injected by the expand step.

4. **Generate the phrases file** — write `outputs/videos_pl/$1/md/05_phrases.md` as a simple markdown table:
   ```
   # Image Phrases: <topic>

   | # | Phrase |
   |---|--------|
   | 001 | "<sentence from image 001>" |
   | 002 | "<sentence from image 002>" |
   ...
   ```

5. **Run the expand step** via Bash:
   ```bash
   PYTHONIOENCODING=utf-8 python tools/pipeline/agent5_visuals.py "$1" --expand
   ```
   This injects CHARACTER_DESCRIPTION + STYLE_SUFFIX into every `**Visual:**` field, rewrites `05_image_prompts.md` with full `**Imagen prompt:**` entries, and exports `05_phrases.docx`.

6. **Report back** to the user:
   - Total image count
   - Next command:
     ```
     PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "$1" --generate
     ```

## Notes

- You are the model (Opus 4.8, in-session). Generate the image prompts in this conversation — do NOT call any API or shell out to a Python script for the generation step.
- Do not skip the self-check list at the bottom of `05_visuals.md` before saving.
- Write only the core visual descriptions in `**Visual:**` fields — the expand step handles all brand constants.
- Every `**Sentence:**` field must be an exact verbatim quote from the script (no paraphrasing).
