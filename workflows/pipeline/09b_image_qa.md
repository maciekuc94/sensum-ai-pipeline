# Workflow: Agent 9b — Image QA (style compliance check)

## Purpose

Agent 9b is a vision-based second pass over the images produced by **Agent 9**.
It catches style violations that the in-pipeline color enforcement (`_enforce_background_color`)
cannot detect — textured backgrounds, decorative borders, wrong color tints,
and cropped heads.

The validator uses **Gemini 2.5 Flash** on Vertex AI to score each PNG against
the SENSUM style contract and writes a markdown report. It does **not** delete
or modify images. With `--retry`, it will spawn Agent 9 once to regenerate the
failed indices, then re-audit them.

---

## When to run

After Agent 9 finishes, before you start adding film grain or moving on to
voiceover. The QA pass is fast (~2 minutes per 120-image video) and cheap
(~$0.04 per video at Gemini 2.5 Flash pricing) so there's no reason to skip it.

---

## Prerequisites

Same as Agent 9:

1. Images exist at `outputs/videos/{slug}/images/image_*.png`.
2. `GOOGLE_CLOUD_PROJECT` is set in `.env`.
3. Application Default Credentials are authenticated:
   ```bash
   gcloud auth application-default login
   ```

---

## Usage

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent9b_image_qa.py "<slug>"
```

Flags:

- `--quiet` — only print the summary, suppress per-image output.
- `--retry` — after QA, regenerate failed indices via Agent 9 (one attempt),
  then re-audit those indices and update the report.

Examples:

```bash
# Audit only
PYTHONIOENCODING=utf-8 python tools/pipeline/agent9b_image_qa.py "5_how_to_actually_stay_mentally_healthy"

# Audit, then auto-regenerate failures and re-audit
PYTHONIOENCODING=utf-8 python tools/pipeline/agent9b_image_qa.py "5_how_to_actually_stay_mentally_healthy" --retry
```

---

## What it checks

Each image must pass ALL five rules:

1. Background is a single flat solid sage beige (~#F4E5CA). No texture, paper
   grain, mottling, aged-paper effect, parchment fibers, stains, or any color
   tint other than warm beige.
2. The only ink color is dark brown (~#582F0E). No greens, no greys, no ochres,
   no other colors.
3. There is NO decorative border, frame, panel, or outline around the image.
   Full-bleed composition.
4. If a human figure is shown, the entire head is inside the frame (not cropped
   at the top).
5. No visible text, letters, numbers, or labels anywhere.

The prompt sent to Gemini 2.5 Flash returns:

```
VERDICT: PASS  (or)  VERDICT: FAIL
REASONS: <if FAIL, comma-separated phrases; if PASS write "none">
```

---

## Output

`outputs/videos/{slug}/md/09_image_qa.md` — markdown report with:

- Summary header (pass / fail / error counts, model used).
- `## Failed images` — table of failed PNGs and the human-readable reasons.
- `## Errored images` — only present if Vertex calls failed.
- `## Passed images` — compact count + index range.

Exit code is always 0 — failures are data, not crashes.

---

## Cost & performance

| Item | Value |
| --- | --- |
| Model | `gemini-2.5-flash` (Vertex AI, location=global) |
| Per-image cost | ~$0.0003 |
| Per 120-image video | ~$0.04 |
| Inter-call delay | 1 s |
| 120-image runtime | ~2 minutes |

If the Vertex model ID changes, edit `QA_MODEL` near the top of
`tools/pipeline/agent9b_image_qa.py`.

---

## Limitations

- **False positives.** Gemini 2.5 Flash is conservative — it may flag heavy
  cross-hatching as "texture" or interpret strong shading as a "border."
  Always sanity-check the report before retrying. False-positive rate has
  not been tuned exhaustively; treat the report as a triage tool, not gospel.

- **No automatic deletion.** The validator never deletes images. Even with
  `--retry`, Agent 9 overwrites in place — your originals are gone, but no
  cleanup happens otherwise.

- **One retry only.** `--retry` triggers a single regen pass. If the
  regenerated image still fails, fix the underlying prompt in
  `md/05_image_prompts.md` and rerun Agent 9 manually.

---

## Common issues

**`No images found in outputs/videos/<slug>/images/`**

Agent 9 has not run yet, or the slug is wrong. Verify:
```bash
ls outputs/videos/<slug>/images/
```

**`vertex call failed: 404 ...`**

The Gemini 2.5 Flash model ID may have changed. Try `gemini-2.5-flash-001`
in `QA_MODEL`.

**Every image fails with the same reason**

The model is being overly strict (or the prompt is too rigid). Inspect the
images manually — if they look fine, loosen the QA prompt in
`tools/pipeline/agent9b_image_qa.py`.

---

## Why this exists

Before Agent 9b, every defect (textured backgrounds, wrong colors, unwanted
frames) had to be caught by manually scrolling 100+ images per video. The
existing `_enforce_background_color` pass in `agent9_images.py` only repairs
solid wrong-color flats — it cannot detect texture variance or borders. A
$0.04 QA pass per video catches the rest. Style violations get a name and a
report; the user keeps final say.
