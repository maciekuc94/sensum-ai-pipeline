# Workflow: Agent 5 — Visual Storytelling

## Purpose

Agent 5 reads the final edited script (`04_final.md`) and generates production-ready image prompts. This is a dedicated visual storytelling pass — the model focuses entirely on composition, pacing, and emotional resonance, with no narrative writing responsibilities.

Agent 5 reads the script's **natural emotional arc** organically — it is not tied to any declared architecture (narrative architectures were retired 2026-06-07; the lean `/draft` chain writes the script freely, with no architecture tag). Lead the visual register with the arc the script *actually* has: an intimate, observational opening → a deepening toward the cost, mechanism, or origin → a wide, quiet, resolving close. When the script supports it, lean on a recurring faceless figure (the viewer's „ty") and a recurring object-motif that returns transformed at the close.

Since 2026-05-28 Agent 5 runs **inside the Claude Code session** — Opus 4.8 generates prompts directly, no Anthropic API call. The Python script (`agent5_visuals.py --expand`) handles only the post-processing: injecting CHARACTER_DESCRIPTION + STYLE_SUFFIX constants into every visual description and exporting phrase files. (`--extract` is extraction-only — it pulls `docx/script_corrected.docx` to `md/script_corrected.md`, which `/visuals` uses as its source when present. Called automatically by the skill.)

The result is `05_prompts.md`, which the human reviews before Agent 6 generates the actual images.

---

## Prerequisites

1. **Agent 3 must have run successfully.** The file `outputs/videos_pl/{slug}/md/04_final.md` must exist.

2. **No API key needed** — Agent 5 now runs in-session.

---

## Run Command

```
/visuals <slug>
```

Claude Code slash command. Generates compact `05_prompts.md` in-session (Opus 4.8, no API cost), then auto-runs `agent5_visuals.py --expand` to assemble full Imagen prompts and export phrase files.

Can be run **in parallel with Agent 8** — both read the script independently.

---

## Prompt — the exact instructions to follow when generating image prompts

You are a visual director for a YouTube psychology channel. Your only job in this pass is visual storytelling.

Read the final narration script fully to understand the arc, then work through it systematically — assigning a compact visual description to each moment.

### Output Format (compact — what you write)

Write the header block first, then one entry per image separated by `---`. Use this exact structure:

```
# Image Prompts: <topic>
Generated: <YYYY-MM-DD>
Source: md/04_final.md
Agent: agent5_visuals (claude-opus-4-8 / Claude Code)
Total images: <N>

Review and edit these prompts before expanding. Run --expand to assemble full Imagen prompts.

---

## Image 001
**Figure:** yes|no
**Sentence:** "<exact verbatim sentence(s) from script>"
**Visual:**
<40–60 word image description — posture, composition, props, spatial relationship>

---

## Image 002
...
```

Extract `<topic>` from the first `# ` heading of `04_final.md` (or the first line of `md/script_corrected.md` when present).

**Critical:** write only the core visual description in `**Visual:**` — do NOT prepend CHARACTER_DESCRIPTION or append STYLE_SUFFIX. The expand step injects those constants automatically.

### Pacing Rules

- Generate as many images as needed — one per sentence is the default
- Group 2–3 consecutive sentences ONLY when they describe the identical visual scene (same object, same action, same spatial framing) — any new concept, location, object, or emotional beat = new entry
- Section transitions always get their own image
- Statistics, metaphors, and [Visual Pause] moments each get their own image
- Every sentence in the script must be covered by exactly one entry
- There is no upper or lower limit — cover the script completely

### Composition Types

Each visual must imply one of these compositions. Vary across the full set — use each at least 6 times where the script allows, never repeat the same type more than twice in a row:

- **Close-up**: just hands holding an object, a detail of posture, two hands in contrast
- **Overhead**: figure viewed from directly above, small in large empty space
- **Wide**: figure tiny against a large architectural element (doorframe, wall, staircase, bookshelf)
- **Two-figure contrast**: left/right split showing before vs after, trapped vs free, alone vs connected
- **Sequential**: one figure shown twice in same frame at different moments (ghost posture, faded duplicate)
- **Object-forward**: the prop dominates the frame, figure interacts with it from the side
- **Cross-section / cutaway**: a structure sliced open to reveal its interior (a head shown as a cutaway, a building cross-section, an exposed mechanism inside a box)
- **Scale-shift**: a normally small thing rendered enormous (a single neuron the size of a tree, a thought rendered as architecture), or a normally large thing rendered tiny
- **Diagrammatic / schematic**: an unlabeled flowchart, gear chain, circuit-style layout, or anatomical plate — composition reads as illustration-from-a-textbook rather than scene-from-life
- **Still-life (no figure)**: scene contains NO human figure — just a single object, a pair of objects, or an empty environment that carries the emotion (a chair, a closed door, a desk, a pair of shoes)
- **Diptych / before-after**: two equally weighted frames side-by-side showing the same subject in two states (then/now, old/new, before/after) — distinct from two-figure contrast because both halves can be objects, environments, or postures
- **Theatre tableau**: three or more figures arranged in a stage-like composition, frozen mid-gesture, centered, slightly stylized

Any composition may be rendered without a figure when the scene's meaning lives in absence, in objects, in an environment, or in an anatomical/diagrammatic mechanism.

### Metaphor Mandate — abstract lines become concrete images

The single biggest difference between a forgettable image and a strong one: a CONCRETE sentence can be shown literally; an ABSTRACT / conceptual / emotional sentence must be TRANSLATED into a concrete visual metaphor — never illustrated literally as "a figure embodying the idea".

Run this test on EVERY sentence:
- **Concrete** — names a physical action, object, or place ("przespałeś budzik", "telefon w dłoni")? → show it directly.
- **Abstract** — a concept, judgment, feeling, or generalization with no physical anchor ("twoja wartość na czymś się opiera", "jesteś do niczego", "życie napędzane strachem")? → you MUST invent a concrete metaphor (object, environment, dynamic situation, or spatial relationship) that CARRIES the idea.

Build the metaphor in this order of preference:
1. **Figure inside a dynamic situation** — the ground cracking under it, fleeing its own shadow, balancing on one fragile support. Strongest: it SHOWS the idea happening.
2. **Figure interacting with a meaning-bearing object** — reaching for a bar always out of reach; a hand holding a magnifying glass over one tiny mark.
3. **Object / environment alone** when a body adds nothing.

Pick an interesting CAMERA. Frontal eye-level on a centred figure is the most inert choice — avoid it for abstract beats.

### Anti-patterns — the boring defaults to REFUSE

What the model reaches for when it gives up on storytelling. If your visual for an abstract sentence is one of these, rewrite it:
- A faceless figure standing front-facing, arms at sides, "being" the abstraction.
- Two figures standing side by side AS the whole idea (two-figure contrast is only allowed when both halves DO something specific).
- A figure sitting passively with no object, situation, or spatial tension.
- "A figure representing [abstract noun]" — representation is not storytelling.

Gut-check: does this frame SHOW the idea happening, or just POINT at it? If it points, find the image that makes it happen.

### Grandeur gear — scale & sweep on the dramatic beats

The renderer now applies museum-grade master-engraving craft to every image automatically (deep tonal range, sculptural light, refined detail — Agent 6). YOUR job is to decide WHERE the composition itself goes big. On the climactic / high-stakes / dramatic-metaphor beats (the cost, the collapse, the turn), stage with cinematic GRANDEUR: monumental scale (a small figure dwarfed by a towering element, or one object rendered vast), a dramatic camera (low worm's-eye up, steep overhead, strong diagonal recession into depth), sweeping dynamic energy. RESERVE it — keep the intimate openings intimate and the quiet close quiet. Grandeur is a spike on the peak beats, not a constant: if every image is epic, none is.

### When to Include the Figure (`include_figure: yes|no`)

The faceless figure is the SIGNATURE element of this channel — it carries embodied emotion, the feeling of being a person inside a body. But not every sentence is about a person. Some sentences are about absence, signals, objects, mechanisms, or pure environment. For those, the figure becomes a generic intrusion that dilutes the meaning. Treat the figure as a precious resource you spend, not a default you stamp.

**Set `**Figure:** yes` only when the answer is YES to: does this sentence meaningfully require the faceless figure?**

INCLUDE the figure when:
- The sentence is about a person doing, holding, carrying, releasing, collapsing, rising, or sitting with something.
- The emotional weight lives in a body — interior burden made physical, embodied tension, self-confrontation, two states of a self side-by-side.
- The sentence asks the viewer to FEEL like they are the figure.

OMIT the figure when:
- The sentence is about an absence ("nothing happened", "no one called", "no funeral").
- The meaning is a list of objects, places, or signals (an empty chair, an empty mailbox, a single closed door, a half-empty glass).
- The sentence describes a psychological mechanism that reads more clearly as an anatomical cutaway, a cross-section, or a 19th-century scientific diagram than as a person.
- The scene is pure environment — a hallway, an empty room, a horizon.
- A symbolic object carries the meaning more powerfully than any body would.

When in doubt, ask: does the sentence want the viewer to see a *person*, or to see *what a person is left with*?

**CALIBRATION:** across the full set, expect roughly 60–75% `**Figure:** yes` — the faceless figure is the channel's signature, but spend absence deliberately (objects, environments, mechanisms). If your output is 90%+ figures, you are under-using absence; if 40% or below, you are losing the signature.

### Emotional Arc

The script is **not tagged with any architecture** — read it and follow the emotional arc it *actually* has, then lead the visual register with that arc. Don't impose a fixed structure; if the script moves differently, follow the script. The point is that the visuals should breathe with the script's movement, not stamp one mood across the whole set.

Most SENSUM scripts move roughly like this:

- **Opening — the surface.** Intimate, observational, a caught private moment. Prefer close-ups of posture, object-forward (a telltale object), overhead of the figure small in space, still-life. Avoid diagram/explanation here — observe, don't diagnose yet.
- **Middle — the cost, the mechanism, the origin.** This is where weight accumulates and the "why" is revealed. Prefer figure-burdened / sequential (same figure twice, before/after the toll), and — where it genuinely fits — cutaway/cross-section, scale-shift (the small root made enormous), diagrammatic, two-figure contrast. Keep it warm, not cold-lab, when it's the figure's own history.
- **Close — the reframe and recognition.** Settling, lightened, returned-but-changed. Prefer diptych (old reading vs new reading of the same thing), the figure holding the recurring motif differently, figure upright/opened, and a wide, quiet resolving frame. Avoid "fixed/cured" triumph — this is acceptance, not victory; echo the opening with one element changed.

**Recurring spine (when the script supports it).** Many scripts have a recurring faceless figure (the same protagonist — the viewer's own „ty", same silhouette, evolving posture) and a single recurring object-motif (a chair, a door, a stone, a clock, a thread) introduced early and returning transformed at the close. When they're there, lean on them: give the motif its own object-forward / still-life frames, and use the **Sequential** composition (same figure twice in one frame) to show change over time. This continuity is the visual spine — but it's driven by the script, not mandatory.

---

### Character Rules

If a scene includes a figure (`**Figure:** yes`), that figure is FACELESS: blank smooth oval head, no eyes, no nose, no mouth, no ears, no hair. Completely androgynous body. Convey ALL emotion through posture and body position only — never describe a facial expression.

If a scene omits the figure (`**Figure:** no`), do not invent body parts or implied silhouettes. The composition stands on its objects, its environment, or its anatomical/diagrammatic structure. Anatomical fragments (a sectioned chest, a cross-section of a hand) are permissible without counting as a "figure" — they live in the diagrammatic register and `**Figure:**` stays `no`.

### Framing Rule (CRITICAL)

If your description includes a figure, the *entire head must fit inside the frame* with visible headroom above. Never describe a shot that would crop the top of the head. If you want a hand-only or detail-only shot, explicitly say "hand only, no head or body visible in frame" — do not just leave the head implied.

Examples of correct framing language:
- "Faceless figure standing centered, full head visible with clear space above"
- "Close-up of two hands only — no head, no torso, no body visible in frame"
- "Wide view: faceless figure in lower portion of frame, entire body and head visible, large empty space above"

Examples to avoid:
- "Bust shot of faceless figure" (ambiguous — may crop head)
- "Faceless figure's torso and shoulders" (head fate unclear — may be cropped)
- Any phrasing that asks for partial body without explicitly saying what is and isn't in frame

### Forbidden Terms

Replace or remove before writing any entry:
- "glowing" / "illuminated" / "lit up" → describe the object plainly ("phone screen", "laptop screen")
- "scribbles", "tangled lines", "jagged marks" floating around a figure → remove entirely
- "dim", "dark", "shadowed" environment → always clean white background, remove these
- Any readable text, labels, numbers, or digits on objects

### Good Examples (match this specificity and length)

**With figure (`**Figure:** yes`):**

- "Faceless figure perched on the edge of a bed, one hand resting limp on a face-down phone on the mattress, spine bowed forward, shoulders drawn inward"
- "Overhead view: faceless figure lying flat on a bare floor, arms spread slightly outward, seen from directly above, surrounded by empty space"
- "Two faceless figures side by side — left one stands with shoulders collapsed, right one stands upright with arms open; wide gap between them"
- "Close-up of two hands: one hand open and releasing a small rectangular shape, the other hand empty and open below it"

**Without figure (`**Figure:** no`):**

- "An empty wooden chair with a straight back angled slightly toward an open empty doorway on a plain bare floor, the doorway framing only hollow emptiness beyond"
- "Cross-section anatomical diagram of a human chest cavity in 19th-century scientific etching style, the ribcage opened like a delicate cabinet, each rib finely articulated in cross-hatched ink, a small nested chamber at center"
- "A tipped antique hourglass on its side with fine sand spilling in a delicate curving stream onto a plain surface, beside it a single glass vessel half-filled with water, one round droplet suspended mid-fall above its surface"

**Abstract → concrete metaphor (the hard cases — translate, don't illustrate):**

- "self-worth stays grounded regardless of the day" → a figure stands still while roots from its feet grip the earth and a gust of torn paper and dry leaves streams past unmoved (NOT "a figure standing firmly")
- "worth propped up by one thing — results" → a figure balancing on a thin plank held up by a single fragile post over empty space
- "it's not one thing that cracks — the ground under you cracks" → a figure braced as deep fissures split the floor apart beneath its feet
- "growth became 'you're never enough yet'" → a figure on tip-toe reaching for a bar always lifted just beyond its fingertips, earlier bars receding behind
- "a life driven by fear of yourself" → a figure fleeing its own long cast shadow, which rises off the floor into a clawed pursuer
- "judging your whole self over one ordinary day" → a hand holding a magnifying glass that blows one tiny speck into a huge looming blot, the rest of the surface clean

### Script Cleaning

Before processing, mentally strip these from the script:
- [EDITOR NOTE: ...] annotations
- Metadata headers (lines starting with #, Generated:, Model:, ---)
- `## ` section-divider headers (2026-06-01) — these are editorial pause-markers, not spoken narration; `_clean_script` in `agent5_visuals.py` strips them automatically via `^#.*$`. Never generate an image for a section header line.

[Visual Pause] markers ARE preserved — treat them as moments of weight (the writer is telling you "hold the image here"). Do not quote them in the `**Sentence:**` field, but use them to recognize a shift in the emotional arc.

The text you quote in `**Sentence:**` fields must be clean narration text only.

### Self-Check List (before saving)

Before writing the file, verify:
1. Every sentence in the script is covered by exactly one entry (no gaps, no double-coverage)
2. `**Figure:**` calibration: roughly 60–75% yes across the full set
3. No entry has "glowing", "dim", "shadowed", "scribbles", or readable text
4. Head-framing rule: every `**Figure:** yes` entry either shows the full head or explicitly excludes the head ("hand only")
5. The visual register follows the script's emotional arc (intimate open → deepen → resolving close), with composition variety across the set
6. No `**Visual:**` entry contains CHARACTER_DESCRIPTION or STYLE_SUFFIX text
7. `Total images: <N>` in the header matches the actual count
8. **Metaphor check:** every abstract / conceptual / emotional sentence is a concrete metaphor (object / situation / spatial relation), NOT a literal front-facing figure — zero "standing figure doing the abstraction", zero "two figures standing" as the whole idea
9. **Grandeur is reserved:** dramatic scale/camera is spent on the peak/cost beats, not stamped on intimate openings or the quiet close

---

## Output Location

```
outputs/
└── videos_pl/
    └── {slug}/
        └── md/
            ├── 04_final.md         (Agent 3 finalize — input for Agent 5)
            ├── 05_prompts.md       (Agent 5 output — review before Agent 6)
            └── 05_phrases.md       (simple phrase table for alignment)
```

---

## Output Format

**Compact format** (what `/visuals` writes — before `--expand`):

```markdown
## Image 001
**Figure:** yes
**Sentence:** "exact quoted sentence from the script"
**Visual:**
Faceless figure perched on the edge of a bed, one hand resting limp on a face-down phone on the mattress, spine bowed forward, shoulders drawn inward

---
```

**Full format** (after `--expand` injects constants):

```markdown
## Image 001
**Figure:** yes
**Sentence:** "exact quoted sentence from the script"
**Imagen prompt:**
[CHARACTER_DESCRIPTION]. Faceless figure perched on the edge of a bed..., [STYLE_SUFFIX]

---
```

Agent 6 reads the `**Imagen prompt:**` field and sends it directly to Vertex AI.

---

## How to Review 05_prompts.md

Open `outputs/videos_pl/{slug}/md/05_prompts.md` after `--expand` completes. This is the only manual gate before images are generated — spend time here.

**Check pacing:**
- Is every sentence covered? Scroll through and spot any gaps.
- Are section transitions getting their own image?

**Check composition variety:**
- Scroll through — are you seeing a mix across the full 12-type vocabulary?
- Specifically watch for cutaways, scale-shifts, diagrammatic, still-life, and diptych.
- Flag any run of 3+ identical composition types and rewrite one.

**Check the emotional arc:**
- Does the visual register follow the script's arc? The opening should feel quiet and intimate; the deepening/mechanism stretch can use cutaway/scale-shift/diagrammatic; the close should be wide and resolving.
- Mood should track the script's movement — not one register stamped across the whole set.

**Check emotional accuracy:**
- Does each image amplify the emotional beat of its sentence?
- Statistics and mechanism explanations should feel clinical/precise. Empathy sections should feel open or collapsed.

**Check forbidden terms:**
- Scan for "glowing", "dim", "shadowed", "scribbles", "tangled lines", readable text — rewrite or remove any found.

**Edit directly** in `05_prompts.md` before running Agent 6. Changes to the `**Imagen prompt:**` line are what Imagen receives.

---

## Common Issues

**`04_final.md` not found**

Agent 3 has not been run yet for this slug, or the slug is misspelled. Run:
```
/draft <slug>
```

**Fewer than 60 prompts generated**

The script may be shorter than expected, or Claude grouped too many sentences together. Review `05_prompts.md` and split dense entries by hand, or re-run `/visuals <slug>`.

**`--expand` finds no `**Visual:**` fields**

The compact `05_prompts.md` may be corrupted or already expanded. If it already has `**Imagen prompt:**` entries, it's ready for Agent 6. If it's empty or malformed, re-run `/visuals <slug>`.

**Mood is flat — one register stamped across the whole set**

The emotional arc isn't being followed. Spot-fix: edit the `**Imagen prompt:**` lines directly so the opening stays intimate (close-ups, still-life), the middle can deepen (cutaway, scale-shift, diagrammatic, two-figure contrast), and the close opens wide and resolves. Or re-run `/visuals` — prompts are non-deterministic and a second pass usually tracks the arc better.

---

## Next Step

After reviewing and editing `05_prompts.md`, generate the images:

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --generate
```
