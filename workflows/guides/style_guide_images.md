# Image Style Guide

Visual bible for the SENSUM channel images. Loaded by the **scientific-etching-guard** skill for freeform image requests (outside `/visuals` & `/package`). For the pipeline proper, Agent 5/6 inject the canonical background + character via `STYLE_SUFFIX` / `CHARACTER_DESCRIPTION` in `tools/utils.py`, and the generate path ends in a deterministic `two_color` snap to #582F0E / #F4E5CA. Agent 3 (script) does NOT write image markers.

---

## Brand Color Palette

All images use only these two SENSUM colors. No blue, no teal, no red, no golden ochre, no moss green, no color outside this set.

| Color name | Hex | Role |
|---|---|---|
| Sage Beige | #F4E5CA | Exclusive background — requested in prompts as a flat solid sage beige background with no texture; paper-grain is added in post (`add_grain.py`), never in the prompt |
| Dark Brown | #582F0E | All linework, ink-liner outlines, cross-hatching |

**Global rule: No text, no labels, no words, no numbers, no letters in any image.**

---

## Base Ink-Sketch Style

Every image uses this foundation:

    minimalist high-contrast ink illustration on a flat solid sage beige background (#F4E5CA) with no texture,
    color palette strictly limited to #582F0E dark brown ink lines on #F4E5CA sage beige — no other colors whatsoever,
    detailed cross-hatching for depth and shadow, fine-liner ink sketch, 2D perspective, heavy negative space,
    19th-century scientific journal engraving style, zero photorealism, no 3D effects, no gradients, no glows, no blurs,
    no golden ochre, no moss green, no watercolor, no color fills,
    absolutely no text, no words, no letters, no numbers, no labels, no captions anywhere in the image,
    16:9 aspect ratio

---

## Consistent Character

The same character appears in every image. Agent 5 (visuals) injects this at the front of every Imagen prompt automatically — do NOT include it in the `[IMAGE: ...]` description.

    a simple illustrated person with a completely blank smooth oval head, no facial features,
    no eyes, no nose, no mouth, no hair, gender-neutral body,
    drawn entirely in fine-liner ink lines in #582F0E dark brown, cross-hatching for depth and shading, no color fills

**Rules:**
- Blank smooth oval head, zero facial features — anonymous and universal
- Gender-neutral body — no gendered shape cues
- Dark brown (#582F0E) ink lines and cross-hatching only — no colour fills (no khaki-tan, no skin tone)
- Same character in every single image — this is what creates visual consistency

---

## IMAGE Marker Format

Use free-form scene descriptions only:

    [IMAGE: free-form description of the body state, environment, and emotional atmosphere]

**What to describe in the scene:**
- Body posture and gesture (curled, upright, collapsed, reaching, retreating, slumped)
- Emotional atmosphere (dense scribbles surrounding the figure, expansive open space, sparse marks)
- Environment (minimal ink lines suggesting a doorframe, floor, or pure open void)
- Props or symbols (thought bubble with abstract shapes, scattered marks, tangled lines, arrows)

**Do NOT describe:** facial features, clothing, hair, gender markers, skin tone, text, labels, or words.

**Example:**

    [IMAGE: a figure curled inward, dense tangled lines crowding around the head, vast empty space below]

Place one marker every 1–2 sentences. Every new idea, statistic, metaphor, or scene shift gets its own marker.

---

## Body Vocabulary

Write the `[IMAGE: ...]` content using body state and environment — the character visual is injected automatically.

- **Posture:** curled, upright, collapsed, still, reaching, retreating, slumped, kneeling
- **Gesture:** arms wrapped around knees, hands pressed to head, fingers spread open, arms raised, head bowed
- **Atmosphere:** dense jagged scribbles, tangled spiral marks, sparse minimal marks, bold sweeping strokes, organized geometric shapes
- **Props / symbols:** abstract thought bubble, scattered geometric shapes, tangled lines, directional arrows, wilted element, radiating strokes
- **Detail:** the angle of the head, the tension in shoulders, the weight of a posture

---

## Environment Vocabulary

- **Minimal real spaces (ink lines):** doorframe edge, window sill, floor horizon, staircase base, table surface — all as single minimal ink strokes
- **Abstract spaces:** open sage-beige void (#F4E5CA) — no lines, figure alone in open space
- **Transitional spaces:** one vertical ink line as a threshold, or radiating ink strokes suggesting light from one side
