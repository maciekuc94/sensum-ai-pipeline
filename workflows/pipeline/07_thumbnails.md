# Agent 7 — Thumbnail Generation

## Objective
Generate 5 distinct thumbnail concepts for a video **in-session in Claude Code on Opus 4.8** (no API), then render each via Gemini 3 Pro Image Preview. Output 5 PNGs (1920×1080) in the SENSUM bichromatic style.

Since 2026-05-29 the concept generation runs in-session via `/thumbnails <slug>` — no Anthropic API. The Python script (`agent7_thumbnails.py --render`) only renders the concepts via Gemini and post-processes; it makes no Claude call.

## When to Run
After Agent 8 has produced `08_publish.md`. Runs independently of Agent 9. **Manual agent — only when the user explicitly asks.**

## Inputs
- `outputs/videos_pl/{slug}/md/04_final.md` — script (theme, emotional angles)
- `outputs/videos_pl/{slug}/md/08_publish.md` — title + hook + metadata context
- `tools/utils.py` — `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` constants (copy verbatim into prompts)

## Command

```bash
# in Claude Code (generate concepts in-session, then render):
/thumbnails <slug>

# the render step the slash command calls (no LLM):
PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py "<slug>" --render --no-grain
```

Grain is applied manually in Canva after adding the title text overlay, so `--no-grain` is the default here.

## Flags (render step)
- `--render` — render the in-session concepts from `md/07_prompts.md` (primary path)
- `--no-grain` — skip film grain post-processing (recommended: use this)
- `--reuse-prompts` — re-render a prior run's prompts from `thumbnails*/thumbnail_prompts.md`
- `--indices 1,4` — only render specific indices (comma-separated)
- `--count N` — render N variations per prompt (`thumbnail_01_v1.png`, `thumbnail_01_v2.png`, …)

## Outputs
- `outputs/videos_pl/{slug}/md/07_prompts.md` — the 5 concepts written in-session by `/thumbnails`
- `outputs/videos_pl/{slug}/thumbnails_no_grain/thumbnail_01.png` … `thumbnail_05.png` (use these)
- `outputs/videos_pl/{slug}/thumbnails_no_grain/thumbnail_prompts.md` — copy of the prompts for reference / `--reuse-prompts`

Output images are 1920×1080 (16:9), padded with #F4E5CA sage beige if the generated aspect ratio differs.

## Concept generation rules (what `/thumbnails` must follow)

Write 5 complete, production-ready image prompts. Each will be sent directly to the image model, so make them polished and self-contained.

- All 5 must be visually **distinct** — different composition, metaphor, and emotional angle on the video's theme.
- Each prompt is ~400 words: open with the scene concept, embed `CHARACTER_DESCRIPTION` **verbatim only if a figure appears**, then close with `STYLE_SUFFIX` verbatim.
- No two thumbnails may share a composition type. Use one per thumbnail, in this order:

**Composition types (one per thumbnail, in order):**
1. **Single figure in symbolic environment** — the androgynous figure stands or sits inside a scene that metaphorically represents the emotional state (e.g., surrounded by many closed doors, inside a vast library of unlived lives, at the edge of a fog-filled mirror).
2. **Symbolic still life** — an arrangement of meaningful objects without a figure, or the figure interacts with one central object that carries the whole emotional weight (e.g., a jar full of folded notes, a set of clocks showing different times, a single empty chair at a long table).
3. **Dual / ghost figure** — two versions of the same androgynous figure in one frame: one solid and present, one faded/dissolving — the lived self beside the unlived self.
4. **Metaphorical interior space** — the viewer looks into a conceptual space: a private cemetery of headstones shaped like life choices, a filing-cabinet drawer open to miniature frozen tableaux, a theatre stage with one spotlight on an empty chair.
5. **Anatomical / internal diagram** — cross-section or schematic (19th-century textbook anatomy plate) showing the psychological concept as internal architecture: the chest opened to reveal a smaller self curled inside; the brain mapped into chambers (shapes only, no readable text).

## Rate Limiting
5 Gemini renders × 20s spacing ≈ 2 min total. Do not reduce spacing.

## Error Recovery
- Single render failed: `--render --indices N` to re-render only that thumbnail
- All renders feel too similar: re-run `/thumbnails <slug>` for a fresh concept pass
- Want more options: `--render --count 3` generates 3 variations per prompt (15 images total)

## Post-Production Workflow
1. Open thumbnail in Canva
2. Add title text overlay
3. Apply film grain to the whole composition (grain intensity: std dev 12 on 0–255 scale)
4. Export final thumbnail

## Style Contract (invariant)
- Palette: #F4E5CA (flat solid sage beige background, no texture) + #582F0E (dark brown ink only)
- Style: 19th-century scientific etching — fine-liner, cross-hatching, no gradients, no fills
- No text, labels, or words in generated images
- No facial features on figures (faceless / silhouette only); full head, never cropped
- No decorative borders or frames — full-bleed composition
