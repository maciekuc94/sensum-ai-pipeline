---
description: Title↔thumbnail packaging strategist — 3 strategies (title+napis+concept) in-session on Opus 4.8, then render 3 thumbnails via Gemini. Successor to /thumbnails.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob
---

# /package — Title ↔ Thumbnail Packaging Strategist (in-session, Opus 4.8)

You design **3 radically different "packaging" strategies** for the video — each a coherent **{strategy name · title · thumbnail napis · visual concept}** bound by a **curiosity gap** — in-session (you are Opus 4.8, no Gemini, no Anthropic API), then hand the 3 visual prompts to `agent7_package.py --render`, which renders one thumbnail per strategy via Gemini. `$1` is the slug under `outputs/videos_pl/`.

> **Manual agent.** Run `/package` only when the user explicitly asks — the default path renders 3 images (credits + ~1.5 min). Pass `--no-render` for a free text-only pass.

> **Successor to `/thumbnails`.** Replaces the old 5-composition-type thumbnail agent. Runs **after `/draft`, before `/publish`** — its titles feed Agent 8.

## Workflow

1. **Validate input.** Resolve the script source (first that exists): `outputs/videos_pl/$1/docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`. If none exists, tell the user to run `/draft $1` first, and stop. (Unlike old `/thumbnails`, you do NOT need `08_publish.md` — `/package` runs before `/publish`.)
   - **Reverse-order check:** if `outputs/videos_pl/$1/md/08_publish.md` already exists, `/publish` has already run on a standalone title — warn that after this `/package` the user must **re-run `/publish $1`** to pick up the co-designed title. Warn and continue (redesigning the thumbnail post-publish is a legitimate reason to be here).

2. **Load source + rulebook + brand constants:**
   - The script source above (theme, emotional angles, metaphors). If it is only a `.docx`, run `PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "$1" --extract` and read `outputs/videos_pl/$1/.tmp/08_narration.md`.
   - `workflows/pipeline/07_package.md` — the 3-strategy contract (single source of truth).
   - `workflows/pipeline/08_publish.md` **STEP 1** — the title doctrine the package titles must obey.
   - `tools/utils.py` — copy `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` **verbatim** (brand contract; never paraphrase).

3. **Design 3 strategies** following `07_package.md`:
   - 3 distinct psychological angles. Each → {name, title, napis, visual concept}.
   - Title obeys 08_publish.md STEP 1 + forms a curiosity gap with its napis (title ≠ napis).
   - Napis: 2–3 ALL-CAPS words, SENSUM taste, never in the render prompt.
   - Visual: one dominant high-contrast symbol, Scientific-Etching contract, **negative space reserved for the napis**. Apply the **v8 thumbnail doctrine** (`07_package.md` §4): metaphor in tension (not a static icon or a flat standing figure), **mandatory rozmach** (cinematic scale / scale-contrast / dramatic camera angle), **emotion through posture** (faces are blank), and the 128 px instant-read test. Make camera angle + scale + posture **explicit** in the render prompt — vague prompts default to a flat stander.

4. **Write two files:**
   - `outputs/videos_pl/$1/md/07_package.md` — the human-facing strategy doc (exact format in `07_package.md`), Strategy 1 marked `[PRIMARY — recommended]`.
   - `outputs/videos_pl/$1/md/07_package_prompts.md` — the 3 full ~400-word render prompts under `## Thumbnail 1/2/3` headers (text-free; `CHARACTER_DESCRIPTION` only where a figure appears; each ends with `STYLE_SUFFIX` verbatim). The renderer parses these headers.

5. **Render** (skip this step if `$2` is `--no-render`):
   ```bash
   PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_package.py "$1" --render --no-grain
   ```
   Renders strategy N → `thumbnails_no_grain/thumbnail_0N.png` (**`gemini-3-pro-image-preview`, native ~4K ≈ 5504×3072, padded to exact 16:9**, sage-beige, text-free). 20s rate limit between calls; premium 4K renders are slower (~2–3 min total).

6. **Report back:** the 3 strategies (name · title · napis), how many thumbnails rendered + the folder (`thumbnails_no_grain/`). Remind the user: pick ONE strategy (title + thumbnail together to preserve the gap); in Canva add that strategy's **napis** as the overlay (in the reserved space) + grain; the chosen **title** is already available to `/publish` (it reads `07_package.md`). Re-roll one image: `agent7_package.py "$1" --render --no-grain --indices N --count 3`.

## Notes
- **You are the model.** Write all 3 strategies + both files in this conversation — no API. The Python step only renders (Gemini) and post-processes.
- Pull `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` from `tools/utils.py` at runtime — never invent or summarize them.
- The napis is for the manual Canva overlay; it must NEVER appear in `07_package_prompts.md` (no-text-in-image contract, re-enforced by the renderer's negative prompt).
