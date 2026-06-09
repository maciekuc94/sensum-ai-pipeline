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
PYTHONIOENCODING=utf-8 python tools/pipeline/agent7_package.py "<slug>" --render --no-grain
```
Re-roll the winner after picking: `... --render --no-grain --indices N --count 3`.

## The 3-strategy contract

Generate exactly **3** strategies. Each attacks a **distinct psychological angle** on THIS script — pick the 3 best-fitting from the menu, never 3 flavours of one angle:

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

### 4 · Storytelling, rozmach & CTR — the v8 thumbnail doctrine
The thumbnail is the **single highest-stakes frame of the whole video** — the click. It is rendered on the **premium model (`gemini-3-pro-image-preview`, native ~4K)**, so push the craft to the ceiling. Same storytelling spine as Agent 5's v8 image doctrine, dialled to maximum:

- **Metaphor in TENSION, never a static icon.** The dominant symbol must be a concrete metaphor caught in a *moment* — mid-action, mid-break, forces colliding, a scale clash — not a calm object just sitting there or a figure simply standing and "being" the idea. Power order: **figure in a dynamic situation > figure straining against a charged object > a single charged object mid-event > inert object.**
- **Rozmach is MANDATORY here** (in body images grandeur is *reserved*; in the thumbnail it is the *default*). Reach for cinematic scale every time: a dramatic camera angle (low-angle so the symbol towers; top-down so the human is dwarfed), an exaggerated **scale contrast** (tiny human vs colossal symbol — the slug-3 *górujący budzik nad maleńką figurą* is the baseline, not the ceiling), deep one-point perspective, one dominant force filling the frame.
- **Emotion through POSTURE — faces are blank.** The figure has no face, so the **body carries the feeling**: collapse, recoil, curling inward, straining, reaching, surging. A faceless body in a charged posture out-emotes any neutral standing mannequin. Never a calm front-facing stander.
- **The 1-second / postage-stamp test.** It must read *instantly* at 128 px: ONE focal point, massive figure-ground contrast, zero micro-detail that dissolves when shrunk. If you can't name it as a stamp, it fails.
- **Visual curiosity gap.** The image itself poses a question (*what's crushing them? why are they so small? what's about to break?*) that the title + napis answer — **image, title, napis = three points of one hook.**
- **Scroll-stop = scale + tension + contrast**, not prettiness. Reject: a floating symbol with no stakes, two calm figures, a tiny element lost in space, busy multi-element scenes, anything that reads as "a tasteful illustration" rather than "a moment that demands explanation."

### Render-prompt expansion
For each strategy, expand its visual concept into a full **~400-word render prompt** that makes the grandeur **explicit** — name the **camera angle, the scale contrast, and the charged posture** (the model renders what you specify; a vague prompt defaults to a flat standing figure). Open with the dramatic scene, embed `CHARACTER_DESCRIPTION` **verbatim only if a figure appears**, close with `STYLE_SUFFIX` **verbatim**. These go to `md/07_package_prompts.md` (text-free; the napis is NOT in the prompt).

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

**`md/07_package_prompts.md`** — the 3 full render prompts in the exact `## Thumbnail N` format the renderer parses:
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

**`thumbnails_no_grain/thumbnail_01..03.png`** — one render per strategy (**`gemini-3-pro-image-preview`, native ~4K ≈ 5504×3072, padded to exact 16:9**, sage-beige, text-free). Strategy N → `thumbnail_0N.png`. The premium model + 4K are reserved for these 3 click-assets; body images (Agent 6) stay on flash-v8.

## Self-check before writing
- [ ] Exactly **3** strategies, **3 distinct angles**.
- [ ] Every title obeys 08_publish.md STEP 1 (no clickbait, no instructional verb, no list, no mechanistic subject, ≤70 chars, no trailing period).
- [ ] Every napis is **2–3 ALL-CAPS words** and **≠ its title** (real curiosity gap); no tabloid words.
- [ ] Every visual = one dominant symbol, etching contract, **negative space reserved for the napis**, no text in the prompt.
- [ ] Every visual clears the **rozmach + CTR bar**: metaphor in tension (not a static icon or a flat standing figure), cinematic scale or scale-contrast, emotion carried by posture, reads instantly at 128 px.
- [ ] Each render prompt makes the **camera angle + scale + posture explicit** (no vague scene that defaults to a flat stander).
- [ ] `07_package_prompts.md` uses `## Thumbnail N` headers; each prompt ends with `STYLE_SUFFIX` verbatim; `CHARACTER_DESCRIPTION` only where a figure appears.
- [ ] Strategy 1 marked `[PRIMARY — recommended]`.

## Rate limiting & recovery
3 renders × 20s spacing on the premium 3-pro model (native 4K renders are slower) ≈ 2–3 min. Re-roll one strategy's image: `agent7_package.py <slug> --render --no-grain --indices N`. Variations of the winner: `--indices N --count 3`. All renders too similar: re-run `/package <slug>` for a fresh strategy pass.

## Post-production — the SENSUM thumbnail finish (2026-06-08)

The picked thumbnail gets a **deterministic two-colour + coarse-grain finish
*before* Canva**, so Canva is reduced to the napis overlay. Decided + validated on
slug-3 thumbnail #2 (`thumbnail_02_v2`), 2026-06-08.

**Finish (applied to the chosen `thumbnail_0N.png`, in this order):**
1. **2-colour** — hard-snap every pixel to the nearer of `#582F0E` / `#F4E5CA`
   (`tools/utils.py:two_color`), the same brand contract as the body images.
2. **Coarse grain `s2/i18`** — `add_grain(intensity=18, grain_scale=2)`. At native
   ~4K (~5504 px) grain needs a ~2 px *cell* (`grain_scale=2`), not 1 px, or it
   vanishes when YouTube downscales the thumbnail; std-dev 18. Fine 1-px grain is
   invisible at this size — that is why thumbnail grain is `s2/i18`, heavier and
   coarser than the body-image standard.

> Script: `python tools/dev/finish_thumbnail.py "<thumbnail.png>"` (deterministic two_color + grain s2/i18 finish).

**Run it — `grain-thumbnail` skill / `finish_thumbnail.py` (2026-06-08).** Both
steps run in one deterministic command — or just say *„dodaj grain do
`<ścieżka>`"* and the `grain-thumbnail` skill routes to it (no hand-work):
```bash
PYTHONIOENCODING=utf-8 python tools/dev/finish_thumbnail.py "<path/to/thumbnail_0N.png>"
```
Writes a `*_final.png` copy and leaves the original untouched (grain is
irreversible); `--in-place` overwrites, `--out <path>` sets an explicit
destination. Deterministic (`rng_seed=42`), so re-runs match.

**Canva (manual) — napis only:**
1. Open the finished `thumbnail_0N.png` in Canva.
2. Add the strategy's **napis** as the text overlay in the reserved negative space.
   Grain is already baked in — do **not** add Canva grain.
3. Export. Use the strategy's **tytuł** as the YouTube title (already available to `/publish`).
