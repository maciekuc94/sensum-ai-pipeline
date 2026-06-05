# Agent — Package (Title ↔ Thumbnail Strategist) — in-session, Opus 4.8

## Objective
Produce **3 radically different "packaging" strategies** for a video — each a coherent **{strategy name · title · thumbnail napis · visual concept}** unit bound by a **curiosity gap** — then render one thumbnail per strategy (3 total) in the SENSUM Scientific-Etching style. Runs **in-session on Opus 4.8 (no API)**; the Python step only renders via Gemini.

This agent is the **successor to the old Agent 7 `/thumbnails`**. It owns the title↔thumbnail synergy the old split (titles in Agent 8, thumbnails in Agent 7) could never achieve.

## When to run
After `/hook` (script locked), **before `/publish`** — its titles feed Agent 8. **Manual agent — only when the user explicitly asks** (the default path renders 3 images = render credits + ~1.5 min).

## Inputs
- Script source, first that exists: `outputs/videos_pl/{slug}/docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`.
- `tools/utils.py` — `CHARACTER_DESCRIPTION` and `STYLE_SUFFIX` constants (copy verbatim into render prompts).
- `workflows/pipeline/08_publish.md` **STEP 1** — the canonical **title doctrine** (Identity Provocation, HARD BANS, ≤70 chars, no trailing period). Package titles obey it; this file does NOT restate it.

## Command
```bash
/package <slug>                 # 3 strategies + text, then render 3 thumbnails
/package <slug> --no-render     # 3 strategies + text only (free; unblocks /publish titles without spending credits)
```
Render step the command calls (no LLM):
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_thumbnails.py "<slug>" --render --no-grain
```
Re-roll the winner after picking: `... --render --no-grain --indices N --count 3`.

## The 3-strategy contract

Generate exactly **3** strategies. Each attacks a **distinct psychological angle** on THIS script — pick the 3 best-fitting from the menu (like the script architecture selector), never 3 flavours of one angle:

- **Reframe neurobiologiczny** — the hidden mechanism beneath the symptom.
- **Uderzenie w mit** — overturns a belief the viewer holds as obvious.
- **Rozgrzeszenie lęku/winy** — names the hidden fear, lifts the guilt.
- **Paradoks** — two "opposite" things revealed as one.
- **Reframe tożsamości** — "to nie lenistwo, to alarm".

### 1 · Title — inherits the SENSUM doctrine
Each strategy's title obeys **08_publish.md STEP 1** in full (do not restate it — read it). Additional, package-only requirement: **the title must form a curiosity gap with its own napis** — the title names the symptom/experience; the napis points at the hidden cause/paradox/twist. Title and napis NEVER say the same thing. ≤70 chars, natural spoken Polish, no trailing period.

### 2 · Napis (Canva overlay) — the new rule
- **2–3 words, ALL CAPS.** Smartphone test: legible as a postage stamp.
- **Never restates the title.** It is the other half of the gap — the provocation / hidden cause (title „Czujesz, że jesteś w tyle?" → napis „ZEGAR KŁAMIE").
- **SENSUM taste, not tabloid.** Same clickbait ban-list as titles (no „SZOK", „SEKRET", „NIE UWIERZYSZ", „SZOKUJĄCA PRAWDA", neon-arrow energy). An artful metaphoric jolt.
- **Never goes into the render prompt.** Scientific Etching = no text in image. The napis is recorded in `07_package.md` for the manual Canva overlay only.

### 3 · Visual concept — smartphone test × Scientific Etching
- **One dominant, high-contrast symbol/metaphor pulled from the script** (instruction's „jeden potężny symbol… znaczek pocztowy"). No micro-clutter, no busy scenes.
- **Binding Scientific Etching contract** (the `scientific-etching-guard` skill enforces it): #F4E5CA flat solid sage-beige background (no texture), #582F0E dark-brown ink only, fine-liner + cross-hatching, no gradients/fills, never photorealistic; faceless figures, **full head never cropped**; no text/words/numbers; full-bleed, no borders.
- **Reserve negative space for the napis** — compose so one clean region (e.g. upper third or one side) is calm, high-contrast space where the 2–3-word Canva overlay will sit legibly. (This is the package upgrade over the old Agent 7 — the image is designed to host the overlay.)
- The 3 visuals must be **visually distinct** (different dominant symbol + composition).

**Visual vocabulary (optional palette, at most one per strategy):** single figure in a symbolic environment · symbolic still-life / one central object · dual / ghost figure (lived self beside unlived self) · metaphorical interior space · anatomical / 19th-century textbook cross-section (shapes only, no readable text).

### Render-prompt expansion
For each strategy, expand its visual concept into a full **~400-word render prompt**: open with the scene, embed `CHARACTER_DESCRIPTION` **verbatim only if a figure appears**, close with `STYLE_SUFFIX` **verbatim**. These go to `md/07_prompts.md` (text-free; the napis is NOT in the prompt).

## Outputs

**`md/07_package.md`** — human-facing strategy doc + title handoff to `/publish`:
```
# Package — <topic>   ·  Generated: <YYYY-MM-DD>  ·  Slug: <slug>

## Strategy 1 — <angle name>   [PRIMARY — recommended]
- **Tytuł:** <≤70 chars, no trailing period>
- **Napis (Canva overlay):** ALL-CAPS 2–3 words
- **Koncept wizualny:** <1–2 sentences: dominant symbol + where the negative space for the napis sits>

## Strategy 2 — <angle name>
- **Tytuł:** …
- **Napis (Canva overlay):** …
- **Koncept wizualny:** …

## Strategy 3 — <angle name>
- **Tytuł:** …
- **Napis (Canva overlay):** …
- **Koncept wizualny:** …
```
Strategy 1 = the model's strongest recommendation (`[PRIMARY]`). The user may re-rank by editing the file; `/publish` reads `[PRIMARY]` (or the first strategy if none marked) as the primary-keyword source.

**`md/07_prompts.md`** — the 3 full render prompts in the exact `## Thumbnail N` format the renderer parses:
```
# Thumbnail Prompts: <topic>
Generated: <YYYY-MM-DD>
Model: claude-opus-4-8 (Claude Code)

## Thumbnail 1

<full ~400-word etching prompt for strategy 1 — text-free>

---

## Thumbnail 2

<… strategy 2 …>

---

## Thumbnail 3

<… strategy 3 …>
```

**`thumbnails_no_grain/thumbnail_01..03.png`** — one render per strategy (1920×1080, sage-beige pad, text-free). Strategy N → `thumbnail_0N.png`.

## Self-check before writing
- [ ] Exactly **3** strategies, **3 distinct angles**.
- [ ] Every title obeys 08_publish.md STEP 1 (no clickbait, no instructional verb, no list, no mechanistic subject, ≤70 chars, no trailing period).
- [ ] Every napis is **2–3 ALL-CAPS words** and **≠ its title** (real curiosity gap); no tabloid words.
- [ ] Every visual = one dominant symbol, etching contract, **negative space reserved for the napis**, no text in the prompt.
- [ ] `07_prompts.md` uses `## Thumbnail N` headers; each prompt ends with `STYLE_SUFFIX` verbatim; `CHARACTER_DESCRIPTION` only where a figure appears.
- [ ] Strategy 1 marked `[PRIMARY — recommended]`.

## Rate limiting & recovery
3 renders × 20s spacing ≈ 1–1.5 min. Re-roll one strategy's image: `agent7_thumbnails.py <slug> --render --no-grain --indices N`. Variations of the winner: `--indices N --count 3`. All renders too similar: re-run `/package <slug>` for a fresh strategy pass.

## Post-production (Canva, manual)
1. Open the chosen `thumbnail_0N.png` in Canva.
2. Add the strategy's **napis** as the text overlay (place it in the reserved negative space).
3. Apply film grain to the whole composition (Gaussian std dev 12 on 0–255).
4. Export. Use the strategy's **tytuł** as the YouTube title (already available to `/publish`).
