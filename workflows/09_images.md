# Workflow: Agent 9 — Image Generation

## Purpose

Agent 9 reads the `05_image_prompts.md` file produced by Agent 5 and generates
actual PNG images using Vertex AI Imagen. It runs in two phases separated by a
human review step so you can refine prompts before spending API credits on
generation.

---

## Prerequisites

1. **Agent 4 must have run successfully.** The file
   `outputs/[slug]/04_script_final.md` must exist and contain `[IMAGE: ...]`
   markers.

2. **Google Cloud project** — set in `.env` at the project root:
   ```
   GOOGLE_CLOUD_PROJECT=my-gcp-project-id
   ```
   Optionally override the default region:
   ```
   GOOGLE_CLOUD_LOCATION=us-central1
   ```

3. **Application Default Credentials** — authenticate once per workstation:
   ```bash
   gcloud auth application-default login
   ```
   The script uses ADC automatically; no service-account key file is required.

4. **Python dependencies installed:**
   ```
   pip install -r requirements.txt
   ```
   The `google-cloud-aiplatform` package must be present for image generation.

---

## Phase 1: Extract Prompts

Run the script without `--generate` to extract all `[IMAGE: ...]` markers and
expand them into full Imagen prompts:

```bash
python tools/agent9_images.py "emotional-dysregulation-in-adhd"
```

Expected output:

```
=== Agent 9: Image Generation — Phase 1 Check ===
Slug : emotional-dysregulation-in-adhd

[1/3] Reading 04_script_final.md...
  Topic : emotional dysregulation in ADHD
  Script length: 9,430 characters

[2/3] Extracting [IMAGE: ...] markers...
  Found 8 image marker(s)

[3/3] Saving 05_image_prompts.md...
  Saved: outputs/emotional-dysregulation-in-adhd/05_image_prompts.md

Found 8 prompt(s). Review and edit 05_image_prompts.md, then run:
  python tools/agent9_images.py "emotional-dysregulation-in-adhd" --generate
```

**What it does:**
- Reads the final script and finds every `[IMAGE: ...]` marker using a regex
- Appends a fixed style suffix to each description to produce a full Imagen prompt
- Saves all prompts to `05_image_prompts.md` for your review

**Output:** `outputs/[slug]/05_image_prompts.md`

---

## Phase 2: Review Prompts

Open `outputs/[slug]/05_image_prompts.md` before running generation. Each block
looks like this:

```markdown
## Image 001
**Script marker:** [IMAGE: a brain split into two halves]
**Imagen prompt:**
a brain split into two halves, flat vector illustration, soft warm color palette, dark background, psychology/mental health theme, minimal and modern, 16:9 aspect ratio
```

**What to check and edit:**

- Does the prompt accurately represent what should appear at that moment in the
  script? Cross-reference the surrounding narration if needed.
- Is the subject specific enough for Imagen to render correctly? Vague
  descriptions like "emotions" generate inconsistent results — add visual
  specifics ("two overlapping circles, one red one blue, person standing
  between them").
- Are there any prompts with human faces or complex text? Imagen struggles with
  both — rephrase to avoid them (see Limitations below).
- Does the style suffix feel appropriate? You can edit the suffix per-image
  directly in this file before running Phase 2. The script reads whatever is
  in `05_image_prompts.md` at generation time.
- Is the emotional tone of each image consistent with the script's arc?
  (empathy → science → empowerment)

Edit `05_image_prompts.md` freely. The script reads the file as-is, so any
changes you make here are what gets sent to Imagen.

---

## Phase 3: Generate Images

Once you are satisfied with the prompts, run with the `--generate` flag:

```bash
python tools/agent9_images.py "emotional-dysregulation-in-adhd" --generate
```

Expected output:

```
=== Agent 9: Image Generation — Phase 2 (Generate Images) ===
Slug : emotional-dysregulation-in-adhd

[1/3] Reading 05_image_prompts.md...
  Loaded 8 prompt(s)

[2/3] Initialising Vertex AI Imagen...
  Project  : my-gcp-project-id
  Location : us-central1
  Model    : imagen-4.0-ultra-generate-001

[3/3] Generating 8 image(s)...
  [1/8] Generating image_001.png...
  Saved: outputs/emotional-dysregulation-in-adhd/images/image_001.png
  [2/8] Generating image_002.png...
  Saved: outputs/emotional-dysregulation-in-adhd/images/image_002.png
  ...

Generated 8/8 images.
Images saved to: outputs/emotional-dysregulation-in-adhd/images
```

**What it does:**
- Reads `05_image_prompts.md` and parses the Imagen prompts
- Calls Vertex AI `imagen-4.0-ultra-generate-001` for each prompt (one image per call)
- Saves each result as a zero-padded PNG: `image_001.png`, `image_002.png`, etc.
- If an individual image fails, prints a warning and continues rather than
  aborting the batch

**Output:** `outputs/[slug]/images/image_001.png`, `image_002.png`, ...

---

## Reviewer Checklist

After generation, open the images folder and work through these questions:

- Do images match the script context at the timestamp where each marker appears?
- Is the visual style consistent across all images (palette, illustration style,
  overall mood)?
- Are there any images with text artifacts, garbled words, or visible distortions?
- Does the color palette feel appropriate for the topic? (Dark background with
  warm accents is the default; adjust per-prompt in `05_image_prompts.md` and
  regenerate only those images if needed.)

If individual images need to be regenerated, edit the specific prompt in
`05_image_prompts.md` and rerun Phase 2. Existing images are overwritten by
filename, so only the changed ones need attention.

---

## Image Style

The default style suffix appended to every prompt enforces the SENSUM brand aesthetic:

```
minimalist high-contrast ink illustration on clean flat white background,
color palette strictly limited to #582F0E dark brown ink lines on white — no other colors whatsoever,
technique: detailed cross-hatching for depth and shadow, fine-liner ink sketch, 2D perspective, heavy negative space,
style: 19th-century scientific journal engraving, zero photorealism, no gradients, no glows, no blurs,
no golden ochre, no moss green, no watercolor, no color fills,
absolutely no text, no words, no letters, no numbers, no labels anywhere,
16:9 aspect ratio
```

Background is applied in post-processing: after generation the `--correct-bg` pass replaces near-white pixels with exact `#F4E5CA`.

A consistent character description is also prepended to every prompt — a faceless gender-neutral mannequin figure with a blank oval head, drawn entirely in ink lines with cross-hatching — to maintain visual continuity across all images in a video.

This suffix is **baked into the code** (`STYLE_SUFFIX` and `CHARACTER_DESCRIPTION` constants in `tools/agent9_images.py`) and applied automatically during Phase 1. To use a different style for a specific image, edit the `**Imagen prompt:**` line in `05_image_prompts.md` directly before running Phase 2 — the code reads whatever is in the file.

To change the default style for all future runs, update `STYLE_SUFFIX` in `tools/agent9_images.py` and update this workflow doc to match.

---

## Limitations

- **Text rendering** — Imagen frequently distorts or misrenders text within
  images. Avoid prompts that ask for readable words, labels, or numbers.
  Describe visual metaphors instead.

- **Human faces** — Realistic faces are unreliable and may trigger safety
  filters. Use silhouettes, abstract figures, or icon-style representations
  of people.

- **Complex scenes** — Prompts with more than two or three interacting elements
  tend to produce cluttered or incoherent results. Keep each prompt focused on
  a single clear subject.

- **Consistency across images** — Imagen does not maintain visual consistency
  between separate calls. The style suffix helps, but colors and illustration
  style will vary slightly. If tight consistency is needed, consider
  post-processing or manual adjustments.

- **API quota** — Each image is one API call. Large scripts with many IMAGE
  markers will consume quota quickly. Review prompts carefully before running
  Phase 2 to avoid regenerating images unnecessarily.

---

## Common Issues

**"Output file not found" on Phase 1**

Agent 4 has not been run yet for this slug, or the slug is misspelled.

```bash
python tools/agent4a_edit.py "emotional-dysregulation-in-adhd"
python tools/agent9_images.py "emotional-dysregulation-in-adhd"
```

**"No [IMAGE: ...] markers found"**

The final script does not contain any IMAGE markers. Add markers in the format
`[IMAGE: description of visual]` to `04_script_final.md` and rerun Phase 1.

**"05_image_prompts.md not found" on Phase 2**

Phase 1 has not been run yet. Run it first:

```bash
python tools/agent9_images.py "emotional-dysregulation-in-adhd"
```

**"GOOGLE_CLOUD_PROJECT is missing or empty"**

Add your GCP project ID to `.env`:
```
GOOGLE_CLOUD_PROJECT=my-gcp-project-id
```

**"Failed to initialise Vertex AI"**

Your Application Default Credentials are missing or expired. Re-authenticate:
```bash
gcloud auth application-default login
```

**Individual image warnings during generation**

A warning like `Warning: Failed to generate image_003.png — ...` means one
image failed but the rest continued. Check the error detail, fix the prompt
in `05_image_prompts.md`, and rerun Phase 2 (the successful images will be
overwritten but are unchanged).

---

## Output Location

```
outputs/
└── emotional-dysregulation-in-adhd/
    ├── 01_research.md             (Agent 1 output)
    ├── 02_verified_research.md    (Agent 2 output)
    ├── 03_script_draft.md         (Agent 3 output)
    ├── 04_script_final.md         (Agent 4a output)
    ├── 05_image_prompts.md        (Agent 5 output — input for Agent 9)
    ├── 05_image_prompts.md           (Agent 9 Phase 1 output — human-reviewed)
    └── images/
        ├── image_001.png          (Agent 9 Phase 2 output)
        ├── image_002.png
        └── ...
```
