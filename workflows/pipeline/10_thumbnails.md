# Agent 10 — Thumbnail Generation

## Objective
Generate 5 distinct thumbnail concepts for a video using Claude Opus 4.7, then render each via
Gemini 3 Pro Image Preview. Output 5 PNGs (1920×1080) in the SENSUM bichromatic style.

## When to Run
After Agent 8 has produced `07_publish_package.md`. Runs independently of Agent 9.

## Inputs
- `outputs/videos/{slug}/md/04_script_final.md` — Script for concept generation
- `outputs/videos/{slug}/md/07_publish_package.md` — Title, hook, and metadata context

## Command

**Standard (recommended — no grain):**
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent10_thumbnails.py "<slug>" --no-grain
```

Grain is applied manually in Canva after adding the title text overlay, so skip it here.

## Flags
- `--no-grain` — Skip film grain post-processing (recommended: use this)
- `--reuse-prompts` — Skip Claude step; reload saved prompts and re-render (new images, same text)
- `--indices 1,4` — Only generate thumbnails at specific indices (comma-separated)
- `--count N` — Generate N variations per prompt (named `thumbnail_01_v1.png`, `thumbnail_01_v2.png`, etc.)

## Outputs
- `outputs/videos/{slug}/thumbnails_no_grain/thumbnail_01.png` … `thumbnail_05.png` (use these)
- `outputs/videos/{slug}/thumbnail_prompts.md` — Saved prompts for reference / `--reuse-prompts`

Output images are 1920×1080 (16:9), padded with #F4E5CA sage beige if the generated aspect ratio differs.

## Post-Production Workflow
1. Open thumbnail in Canva
2. Add title text overlay
3. Apply film grain to the whole composition (grain intensity: std dev 12 on 0–255 scale)
4. Export final thumbnail

## Process
1. Claude Opus 4.7 generates 5 distinct thumbnail concepts — one per composition type:
   - Symbolic close-up object
   - Figure in environment
   - Typographic / diagrammatic
   - Dramatic negative space
   - Abstract symbol / pattern
2. Each concept becomes a Gemini image prompt with the SENSUM style contract
3. Gemini 3 Pro Image Preview renders each concept (20s delay between renders — rate limit)
4. Images are padded to 1920×1080 with #F4E5CA sage beige pillarbox if needed

## Rate Limiting
5 Gemini renders × 20s spacing ≈ 2 min total. Do not reduce spacing.

## Error Recovery
- Single render failed: `--indices N` to re-render only that thumbnail
- All renders feel too similar: omit `--reuse-prompts` for a fresh concept pass
- Want more options: `--count 3` generates 3 variations per prompt (15 images total)

## Style Contract (invariant)
- Palette: #F4E5CA (sage beige background) + #582F0E (dark brown ink only)
- Style: 19th-century scientific etching — fine-liner, cross-hatching, no gradients, no fills
- No text, labels, or words in generated images
- No facial features on figures (faceless / silhouette only)
