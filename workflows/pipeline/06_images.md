# Workflow: Agent 6 — Image Generation

## Purpose

Agent 6 reads the `md/05_prompts.md` file produced by **Agent 5** and
renders each prompt as a PNG using **Gemini 3 Pro Image Preview** on Vertex AI.
It runs in two phases separated by a human review step so prompts can be
refined before spending API credits on generation.

The image-prompt content itself is **owned by Agent 5** (`tools/pipeline/agent5_visuals.py`).
Agent 6 is a renderer — it does not generate or rewrite prompts.

---

## Prerequisites

1. **Agent 5 must have run successfully.** The file
   `outputs/videos_pl/{slug}/md/05_prompts.md` must exist. If it does not, run:
   ```bash
   PYTHONIOENCODING=utf-8 python tools/pipeline/agent5_visuals.py "<slug>"
   ```

2. **Google Cloud project** — set in `.env` at the project root:
   ```
   GOOGLE_CLOUD_PROJECT=my-gcp-project-id
   ```
   Region is hard-coded to `global` — Gemini 3 Pro Image Preview returns 404 on
   regional endpoints.

3. **Application Default Credentials** — authenticate once per workstation:
   ```bash
   gcloud auth application-default login
   ```

4. **Python dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Phase 1: Verify prompts file

Run the script with no flags to confirm `05_prompts.md` exists and
report the parsed prompt count:

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>"
```

Expected output:

```
=== Agent 6: Image Generation — Phase 1 Check ===
Slug : <slug>

Agent 5 writes 05_prompts.md directly.
Run Agent 5 if you have not already:
  python tools/pipeline/agent5_visuals.py "<slug>"

  Found existing md/05_prompts.md with 76 prompt(s).

Review and edit md/05_prompts.md, then generate images:
  python tools/pipeline/agent6_images.py "<slug>" --generate
```

If the file does not exist, the command exits with a clear pointer to run
Agent 5 first.

---

## Phase 2: Review prompts

Open `outputs/videos_pl/{slug}/md/05_prompts.md` before running generation. Each
block looks like this:

```markdown
## Image 001
**Sentence:** "You are 27. Or 32. Or 41."
**Beat:** opening_hook
**Imagen prompt:**
a completely androgynous faceless gender-neutral human mannequin figure with
a smooth featureless blank oval head — [...full CHARACTER_DESCRIPTION...].
A faceless figure holds a phone in both hands, thumbs positioned for scrolling.
minimalist high-contrast ink illustration on clean flat white background,
color palette strictly limited to #582F0E dark brown ink lines on white —
[...full STYLE_SUFFIX...] — 16:9 aspect ratio
```

**What to check and edit:**

- Does the prompt accurately represent the moment in the script? Cross-reference
  the surrounding narration if needed.
- Is the visual specific enough? Vague abstractions ("emotions", "thoughts")
  produce inconsistent renders — replace with concrete posture, props, and
  spatial cues.
- The character description and style suffix are already embedded in each
  prompt (prepended/appended by Agent 5). Edits to them propagate only to the
  one prompt you edit.
- Watch for unintended faces, head-cropping, or readable text — the negative
  prompt blocks these, but prompts that explicitly request them will still
  fight the negative.

Edit the file freely. Agent 6 reads it as-is at Phase 2 time.

---

## Phase 3: Generate images

Once the prompts are approved, run with `--generate`:

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --generate
```

Optional flags:
- `--start N` — start from prompt N (1-based).
- `--limit N` — render only N prompts.
- `--indices "22,26,35"` — regenerate only the listed 1-based indices.
  Overrides `--start`/`--limit` and **overwrites existing PNGs** at those
  indices (the normal flow skips existing files; with `--indices` the user is
  explicitly asking for replacements). Use this to re-render specific bad
  images without redoing the whole set.
- `--grain N` — apply film grain at intensity N to freshly-generated images.

Expected output:

```
=== Agent 6: Image Generation — Phase 2 (Generate Images) ===
Slug : <slug>

[1/3] Reading md/05_prompts.md...
  Loaded 76 prompt(s)

[2/3] Initialising Vertex AI Imagen...
  Project  : my-gcp-project-id
  Location : global
  Model    : gemini-3-pro-image-preview

[3/3] Generating 76 image(s)...
  [1/76] Generating image_001.png...
  Saved: outputs/videos_pl/<slug>/images/image_001.png
  Waiting 20s (rate limit)...
  ...
```

**What it does:**
- Parses each `**Imagen prompt:**` block from `md/05_prompts.md`.
- Appends a short negative instruction (face suppression, color-drift
  suppression, head-cropping suppression) to each prompt.
- Calls `gemini-3-pro-image-preview` with `response_modalities=["IMAGE"]`.
- Saves the result as `image_NNN.png`.
- Post-processes each image in this order: resizes/pillarboxes to 1920×1080
  with `#F4E5CA` padding → **`two_color`** hard-quantizes every pixel to the
  nearer of the two brand anchors `#582F0E` / `#F4E5CA`, collapsing every
  off-brand cast (greenish/grey muck inside objects, any residual background
  texture) onto the strict two-colour contract in one deterministic step, while
  the cross-hatching survives (dark strokes → ink, gaps → paper). Form is
  untouched — only colour. This **replaces** the older
  `enforce_background_color` + `flatten_background` pair on the generate path
  (both remain available as the `--correct-bg` / `--flatten-bg` aux modes).
  **Grain is NOT applied here** — it is added later in post (DaVinci Resolve).
- Waits 20 s between calls to stay under the Vertex AI quota.

Existing files at the target path are skipped — to re-render a single image,
delete `image_NNN.png` first.

**Full re-render after a script change (lesson, 2026-06-08).** The skip-existing
behaviour means a bare `--generate` will NOT refresh a slug that already has
images — it only fills in missing numbers, then auto-runs QA + one retry on
whatever it touched. So after editing the script (e.g. swapping in
`script_corrected` and re-running `/visuals` to rewrite `05_prompts.md`),
`--generate` silently skips every existing `image_NNN.png` and leaves the old
visuals in place. To force a true full re-render, either delete `images/` first
or pass `--indices` covering the whole stale set (`--indices` overwrites in
place). Verify the swap actually took with a byte-hash diff against a backup —
because **Agent 6b QA validates STYLE only (colour, text, frames, faces), never
whether an image matches its sentence**, a stale image left over from the old
script passes QA cleanly and the gap is invisible without the hash check.
Rationale: slug-3 corrected-script rerender (2026-06-08).

**Output:** `outputs/videos_pl/{slug}/images/image_001.png`, `image_002.png`, ...

---

## Auxiliary modes

### `--correct-bg` — background correction pass

Copies `images/` to `images_corrected/` and replaces near-white pixels with
exact `#F4E5CA`. Useful if you regenerated images outside the standard pipeline
and need to enforce brand background color.

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --correct-bg
```

### `--flatten-bg` — background flatten pass (in place)

Flattens model background texture to flat `#F4E5CA` across `images/`, **in place**
(no re-render). The `--generate` pipeline already runs this on every fresh image;
this mode is for flattening images that already exist. Idempotent — safe to re-run.
Honors `--indices "1,6"` to flatten only specific images. Preserves the drawn
subject; texture **on** the subject is left for a reroll (Agent 6b QA flags it).

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --flatten-bg
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --flatten-bg --indices "1,6"
```

### `--two-color` — hard two-colour brand pass

Snaps every pixel of `images/image_*.png` to the nearer of `#582F0E` / `#F4E5CA`
(see `tools/utils.py:two_color`) — the **same pass the `--generate` path now runs
on every fresh image**. Removes off-brand casts inside objects and any background
texture in one deterministic step; form is untouched, only colour. Non-destructive
by default: writes the quantized copies to `images_post/` for review, leaving
`images/` intact. Add `--in-place` to overwrite `images/`. Honors `--indices "1,6"`.
Grain is never applied here (added later in DaVinci).

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --two-color
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --two-color --in-place --indices "1,6"
```

### `--apply-grain N` — grain pass

Copies images (from `images_corrected/` if it exists, otherwise `images/`) to
`images_grain/` with Gaussian film grain at intensity N applied. Standard
intensity is 12.

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --apply-grain 12
```

### `--sync-scripts` — insert cue markers

Updates `md/04_final.md` so each row in `md/05_prompts.md` has a
matching `[IMAGE_NNN]` cue marker inserted before the sentence it illustrates.
This is for editor reference during recording — it does not affect Agent 6
narration (Agent 6 strips these defensively).

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --sync-scripts
```

---

## Image Style (enforced by Agent 5, not Agent 6)

The bichromatic SENSUM contract — `#F4E5CA` background + `#582F0E` ink only,
19th-century scientific etching, no facial features, no text — is enforced by
Agent 5 when it constructs each prompt. The `CHARACTER_DESCRIPTION` and
`STYLE_SUFFIX` constants live in `tools/utils.py` and are imported by Agent 5.

To change the default style, edit `tools/utils.py` and rerun Agent 5. Agent 6
does **not** re-apply the style — it just renders whatever is in
`md/05_prompts.md`.

---

## Limitations

- **Text rendering** — Gemini frequently distorts text within images. The
  style suffix forbids text and the negative prompt suppresses it, but prompts
  that explicitly describe books, papers, or signs may still produce garbled
  characters. Describe these as objects (e.g. "open book") without naming
  what is written.

- **Faces** — Despite explicit negative prompts, Gemini occasionally renders
  faint facial features on figures. Re-render affected images by deleting the
  file and rerunning Phase 2.

- **Consistency across images** — Gemini does not maintain visual consistency
  between separate calls. The repeated `CHARACTER_DESCRIPTION` reduces drift
  but does not eliminate it.

- **Rate limit** — Vertex AI Gemini 3 Pro Image Preview has a low QPM quota.
  Agent 6 spaces calls 20 s apart. A 76-image script takes ~25 minutes.

- **Stochasticity** — Re-running the same prompt produces a different render.
  This is expected behavior of the model.

---

## Common Issues

**`md/05_prompts.md not found`**

Agent 5 has not been run for this slug. Run it first:
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent5_visuals.py "<slug>"
```

**`Header says N images but M prompt blocks were parsed`**

The `Total images:` line in the prompts file and the actual block count
disagree. Usually means the file was hand-edited and a block was added or
removed without updating the header. Generation proceeds with the parsed
count; fix the header for clarity.

**`Failed to initialise Vertex AI`**

Application Default Credentials are missing or expired:
```bash
gcloud auth application-default login
```

**Individual `Failed to generate image_NNN.png` warnings**

One image failed (safety filter, transient API error, etc.) but the rest
continued. Inspect the warning, fix the prompt in `md/05_prompts.md`,
delete the failing PNG (or run with `--start NNN --limit 1`), and rerun
Phase 2.

---

## Output Location

```
outputs/videos_pl/<slug>/
├── md/
│   ├── 04_final.md         (Agent 4b output)
│   └── 05_prompts.md        (Agent 5 output — Agent 6 input)
├── images/                         (Agent 6 --generate output)
│   ├── image_001.png
│   ├── image_002.png
│   └── ...
├── images_corrected/               (--correct-bg output, optional)
└── images_grain/                   (--apply-grain output, optional)
```
