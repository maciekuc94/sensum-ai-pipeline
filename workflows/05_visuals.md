# Workflow: Agent 5 — Visual Storytelling

## Purpose

Agent 5 reads the final edited script (`04_script_final.md`) and uses Claude
Opus 4.7 to write production-ready image prompts. This is a dedicated visual
storytelling pass — the model focuses entirely on composition, pacing, and
emotional resonance, with no narrative writing responsibilities.

Since 2026-05-15 Agent 5 is **beat-aware**: it reads the script's
`ARCHITECTURE:` declaration (Forensic Case Study, Historical Reversal,
Socratic Challenge, or Systems Audit) and applies a *Visual Register Map*
specific to each beat of that architecture. The symptom-beat looks
different from the mechanism-beat from the close. The register maps live
in [workflows/narrative_architectures.md](narrative_architectures.md) under
"Visual Register Maps" and are mirrored in `VISUAL_REGISTER_MAPS` inside
[tools/agent5_visuals.py](../tools/agent5_visuals.py).

The result is `05_image_prompts.md`, which the human reviews before Agent 9
generates the actual images.

**Why separate from the script?** When the script writer (Agent 3) handles
both narrative and visual tasks simultaneously, quality drops in both. A
dedicated visual agent reads the finished script with fresh eyes and thinks
like a visual director: composition variety, emotional arc in images, full
sentence-level coverage.

---

## Prerequisites

1. **Agent 4 must have run successfully.** The file
   `outputs/[slug]/04_script_final.md` must exist.

2. **Anthropic API key** — set in `.env` at the project root:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

---

## Run Command

```bash
python tools/agent5_visuals.py "emotional-dysregulation-in-adhd"
```

Can be run **in parallel with Agent 6** (narration strip) — both read
`04_script_final.md` independently.

```bash
python tools/agent5_visuals.py "emotional-dysregulation-in-adhd"
python tools/agent6_narration.py "emotional-dysregulation-in-adhd"
```

---

## What the Agent Does

Agent 5 receives the clean narration script and makes two decisions per
moment: **where** an image goes (pacing) and **what** it shows (composition).

**Pacing target:** One image per sentence by default. Images are grouped only
when consecutive sentences describe the identical visual scene — same object,
same action, same spatial framing. No upper or lower limit.

**Composition vocabulary** (12 types, varied across the set, ≥6 of each where the
beat allows, never repeat the same type more than twice in a row):
- Close-up: hands, posture detail, object detail
- Overhead: figure viewed from above in empty space
- Wide: figure small against large architectural element
- Two-figure contrast: before/after, alone/connected, trapped/free
- Sequential: one figure shown twice at different moments in same frame
- Object-forward: prop dominates, figure interacts from the side
- Cross-section / cutaway: a structure sliced open to reveal its interior
- Scale-shift: the small made enormous, or the large made tiny
- Diagrammatic / schematic: textbook-plate composition, no labels
- Still-life (no figure): scene contains no human figure — just objects/environment
- Diptych / before-after: two equally weighted halves side-by-side
- Theatre tableau: three or more figures arranged in a stage-like composition

**Beat-specific register applied per architecture.** Each architecture has a
register map naming preferred compositions, metaphor families, mood, and what
to avoid for each beat. The agent reads the script's `ARCHITECTURE:` line and
applies the matching map. See
[narrative_architectures.md → Visual Register Maps](narrative_architectures.md)
for the full table.

**Character rules enforced automatically:**
- Every figure is faceless (blank smooth oval head, no features)
- Gender-neutral androgynous body
- All emotion through posture only — no facial expressions

**Brand style injected automatically** for every Imagen prompt:
- `#582F0E` dark brown ink lines on white background
- 19th-century scientific journal engraving style
- No text, no labels, no gradients, no photorealism
- 16:9 aspect ratio

---

## Output Location

```
outputs/
└── emotional-dysregulation-in-adhd/
    ├── 04_script_final.md         (Agent 4 output — input for Agent 5)
    └── 05_image_prompts.md           (Agent 5 output — review before Agent 9)
```

---

## Output Format

```markdown
# Image Prompts: [Topic]
Generated: [date]
Source: 04_script_final.md
Agent: agent5_visuals (claude-opus-4-7)
Total images: [N]

---

## Image 001
**Beat:** The Symptom
**Sentence:** "exact quoted sentence from the script"
**Imagen prompt:**
[CHARACTER_DESCRIPTION]. [visual scene], [STYLE_SUFFIX]

---
```

The `**Beat:**` line tags which beat of the architecture the image belongs to
(e.g. The Symptom / The Investigation / The Culprit / The Implication for a
Forensic Case Study).

---

## How to Review 05_image_prompts.md

Open `outputs/[slug]/05_image_prompts.md`. This is the only manual gate before
images are generated — spend time here.

**Check pacing:**

- Is every sentence covered? Scroll through and spot any gaps.
- Are images distributed across all six sections (hook, reframe, science,
  context, prescription, close)?

**Check composition variety:**
- Scroll through — are you seeing a mix across the full 12-type vocabulary?
  Specifically watch for cutaways, scale-shifts, diagrammatic, still-life,
  and diptych — these are the additions that drive variety.
- Flag any run of 3+ identical composition types and rewrite one.

**Check beat-aware register:**
- Does each beat *look* like its register? Symptom-beat should feel quiet
  and intimate; investigation-beat should be evidence/diagrammatic;
  mechanism-reveal should use cutaway/scale-shift; close should be wide
  and resolving.
- If three Investigation-beat images are all generic faceless figures with
  no investigation props (no magnifier, no schematic, no evidence board),
  the register is being ignored — rewrite one.
- Beats should appear in the order declared by the architecture (e.g.
  Forensic Case Study: Symptom → Investigation → Culprit → Implication).

**Check emotional accuracy:**
- Does each image amplify the emotional beat of its sentence?
- Statistics and mechanism explanations should feel clinical/precise.
  Empathy sections should feel open or collapsed. Prescription sections
  should feel active and directed.

**Check forbidden terms:**
- Scan for "glowing", "dim", "shadowed", "scribbles", "tangled lines",
  readable text — rewrite or remove any found.

**Edit directly** in `05_image_prompts.md` before running Agent 9. Changes to
the `**Imagen prompt:**` line are what Imagen receives.

---

## Common Issues

**"Output file not found" error on startup**

Agent 4 has not been run yet for this slug, or the slug is misspelled.

```bash
python tools/agent4a_edit.py "emotional-dysregulation-in-adhd"
python tools/agent5_visuals.py "emotional-dysregulation-in-adhd"
```

**Fewer than 60 prompts generated**

The script may be shorter than expected, or Agent 5 grouped too many
sentences together. Review `05_image_prompts.md` and split dense entries by
hand, or re-run Agent 5.

**JSON parse error**

Rare — Claude occasionally returns malformed JSON in one batch. Re-run
Agent 5; the batching is non-deterministic and a clean run usually succeeds.

**Beat field missing, wrong, or all the same beat**

Confirm the script's first non-blank, non-header line begins
`ARCHITECTURE:` followed by one of the four names exactly:
`Forensic Case Study`, `Historical Reversal`, `Socratic Challenge`,
`Systems Audit`. If the line is missing, Agent 5 falls back to the
Forensic Case Study register — which is wrong for any other architecture.
Fix the script header (or `04_script_final.md`) and re-run Agent 5.

**Investigation-beat images all show generic faceless figures**

The register is being read but ignored. Spot-fix: edit those `**Imagen
prompt:**` lines directly to insert investigation props (magnifier,
microscope, evidence board, schematic diagram, cutaway). Or re-run
Agent 5 — the prompts are non-deterministic and the second pass typically
applies the register more aggressively.

---

## Next Step

After reviewing and editing `05_image_prompts.md`, generate the images:

```bash
python tools/agent9_images.py "emotional-dysregulation-in-adhd" --generate
```
