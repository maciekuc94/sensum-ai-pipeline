---
name: scientific-etching-guard
description: Use when about to generate, render, write prompts for, or describe ANY image, thumbnail, channel banner, chart, diagram, slide, or other visual asset for this SENSUM project (also when the user uses Polish terms like obrazek, grafika, miniaturka, okładka, or wykres) — especially ad-hoc/freeform requests made OUTSIDE the /visuals and /package commands. Loads the binding Scientific Etching contract so the first attempt is on-brand instead of drifting to photorealistic or adding forbidden colours/text.
user-invocable: false
---

# Scientific Etching Guard

Every visual for this project obeys ONE contract. Non-negotiable:

## Non-negotiables (every image, no exceptions)
- **Palette — two colours only.** #F4E5CA (Sage Beige) = background: a *flat
  solid* sage beige, **no texture**. #582F0E (Dark Brown) = every ink line,
  cross-hatch, silhouette. No other colour anywhere.
- **Style — Scientific Etching.** Fine-liner ink + cross-hatching for depth,
  like a 19th-century scientific-journal engraving. No gradients, no fills, no
  watercolour, **never photorealistic**.
- **No text.** No words, letters, labels, or numbers inside the image.
- **No frame.** Full-bleed composition — no borders, no decorative edges.
- **Never put texture words in a prompt** (vellum / aged paper / parchment /
  grain) — the model renders them literally. Ask for a "flat solid sage beige
  background, no texture". Grain is added in POST via `tools/utils.py:add_grain`
  (`tools/dev/add_grain.py`), never in the prompt.

## If the user explicitly asks for something off-doctrine
User instructions outrank this skill. If the user *explicitly* wants
photorealistic / extra colours / text-in-image: do NOT silently comply and do
NOT refuse — flag the conflict once ("to poza doktryną Scientific Etching —
potwierdzasz?"), confirm, then proceed.

## Source of truth (open for full detail)
- `CLAUDE.md` → "## Design Standards"
- `workflows/guides/style_guide_images.md`
- Constants injected by `/visuals --expand`: `tools/utils.py` → `STYLE_SUFFIX`,
  `CHARACTER_DESCRIPTION` (the recurring figure).

## What this skill does NOT do
It does not replace the deterministic safety nets (`STYLE_SUFFIX`, the
background-colour enforcer, Agent 6b QA) — those stay the hard gate. This skill
injects intent *before* I start, so the freeform path is on-brand from attempt #1.
