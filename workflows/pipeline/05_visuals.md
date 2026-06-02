# Workflow: Agent 5 — Visual Storytelling

## Purpose

Agent 5 reads the final edited script (`04_final.md`) and generates production-ready image prompts. This is a dedicated visual storytelling pass — the model focuses entirely on composition, pacing, and emotional resonance, with no narrative writing responsibilities.

Since 2026-05-15 Agent 5 is **beat-aware**: it reads the script's `ARCHITECTURE:` declaration (Composite Portrait, Forensic Case Study, Historical Reversal, Socratic Challenge, or Systems Audit) and applies a *Visual Register Map* specific to each beat of that architecture. Since 2026-05-29 the default architecture is **Composite Portrait** (recurring figure + recurring object-motif, ~10–15 min, full second person).

Since 2026-05-28 Agent 5 runs **inside the Claude Code session** — Opus 4.8 generates prompts directly, no Anthropic API call. The Python script (`agent5_visuals.py --expand`) handles only the post-processing: injecting CHARACTER_DESCRIPTION + STYLE_SUFFIX constants into every visual description and exporting phrase files. (`--extract` is extraction-only — it pulls `docx/script_corrected.docx` to `md/script_corrected.md`, which `/visuals` uses as its source when present. Called automatically by the skill.)

The result is `05_prompts.md`, which the human reviews before Agent 9 generates the actual images.

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
Architecture: <architecture name>
Total images: <N>

Review and edit these prompts before expanding. Run --expand to assemble full Imagen prompts.

---

## Image 001
**Beat:** <beat name from the architecture>
**Figure:** yes|no
**Sentence:** "<exact verbatim sentence(s) from script>"
**Visual:**
<40–60 word image description — posture, composition, props, spatial relationship>

---

## Image 002
...
```

Extract `<topic>` from the first `# ` heading of `04_final.md`. Extract `<architecture>` from the `ARCHITECTURE:` line (first non-blank line of the script body). Default to `Composite Portrait` if missing (the channel default).

**Critical:** write only the core visual description in `**Visual:**` — do NOT prepend CHARACTER_DESCRIPTION or append STYLE_SUFFIX. The expand step injects those constants automatically.

### Pacing Rules

- Generate as many images as needed — one per sentence is the default
- Group 2–3 consecutive sentences ONLY when they describe the identical visual scene (same object, same action, same spatial framing) — any new concept, location, object, or emotional beat = new entry
- Section transitions always get their own image
- Statistics, metaphors, and [Visual Pause] moments each get their own image
- Every sentence in the script must be covered by exactly one entry
- There is no upper or lower limit — cover the script completely

### Composition Types

Each visual must imply one of these compositions. Vary across the full set — use each at least 6 times where the beat allows, never repeat the same type more than twice in a row:

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

**CALIBRATION:** across the full set, expect roughly 50–70% `**Figure:** yes`. If your output is 90%+ figures, you are under-using absence. If 30% or below, you are losing the channel's signature.

### Beat Sequence & Visual Register

**Read the script's `ARCHITECTURE:` line and apply the matching register below.**

---

**FORENSIC CASE STUDY** (4 beats: Symptom → Investigation → Culprit → Implication)

Beats appear in order; [Visual Pause] markers and transitions ("Start with the symptom…", "Now the investigation…", "Here is the mechanism…", "Now look at what this reveals…") signal beat boundaries.

**Beat 1 — The Symptom (opening)**
- Mood: clinical observation, quiet, intimate
- Preferred compositions: close-up of posture detail, overhead of figure in empty space, still-life
- Metaphor families: clinical evidence — clipboard, single chair, phone face-down, stethoscope on desk
- Scale: small, single-subject, intimate
- Avoid: dynamic action, multi-figure scenes, dramatic motion

**Beat 2 — The Investigation**
- Mood: forensic, diagrammatic, evidence-gathering
- Preferred compositions: object-forward (magnifier, lab instruments), cross-section/cutaway, two-figure contrast (researcher vs. subject), diagrammatic/schematic
- Metaphor families: investigation tools — magnifier, microscope, evidence board, schematic diagram, exposed mechanism, dissection layout
- Scale: medium with annotated detail
- Avoid: empty environments — populate with evidence

**Beat 3 — The Culprit (mechanism revealed)**
- Mood: revelation, structural, unveiling
- Preferred compositions: cross-section, cutaway, scale-shift (the small made enormous), diagrammatic, x-ray transparency
- Metaphor families: anatomy revealed — brain cross-section, exposed gear, machine interior, root system underground, building cutaway
- Scale: dramatic, the hidden made huge
- Avoid: surface-level exteriors, generic faceless figure poses

**Beat 4 — The Implication (close)**
- Mood: quiet, resolving, wide
- Preferred compositions: wide (figure-in-landscape), figure-walking-away, doorframe/passage, figure on a threshold
- Metaphor families: return to life — open doorway, horizon line, single figure walking forward, dawn-window, empty path
- Scale: expansive, figure small but resolved
- Avoid: tight intimacy, claustrophobia

---

**HISTORICAL REVERSAL** (4 beats: Old Belief → Discovery → New Mechanism → Rewrite)

**Beat 1 — The Old Belief**
- Mood: dignified, period, settled
- Preferred compositions: formal portrait pose, single-figure dignified, still-life (old textbook), framed picture on a wall
- Metaphor families: period authority — old textbook, lecture podium, wall portrait, framed certificate, dusty leather-bound book
- Scale: medium, formal, centered
- Avoid: motion, contemporary objects, asymmetry

**Beat 2 — The Discovery That Broke It**
- Mood: dynamic, unexpected angle, off-balance
- Preferred compositions: two-figure contrast (old vs. new), object-forward (single new instrument), diptych showing rupture
- Metaphor families: a hand reaching past a barrier, a single new tool, a notebook page mid-write, a paper torn down the middle
- Scale: medium with one element breaking the symmetry
- Avoid: settled formal compositions — break the visual rhythm of Beat 1

**Beat 3 — The New Mechanism**
- Mood: modern, diagrammatic, clean
- Preferred compositions: cross-section, schematic/diagrammatic, anatomical cutaway, scale-shift
- Metaphor families: modern science — clean diagram, flowchart, exposed circuit board, anatomical plate
- Scale: medium with annotated detail
- Avoid: period imagery, formal portraits

**Beat 4 — The Rewrite**
- Mood: side-by-side weight, recognition, settled-new
- Preferred compositions: diptych (before/after), two-figure contrast (then/now), erasure-and-replace layout
- Metaphor families: comparison artifacts — left page vs. right page, framed old vs. open new, a hand crossing out and rewriting
- Scale: balanced, two-element composition
- Avoid: single-element shots — this beat IS the contrast

---

**SOCRATIC CHALLENGE** (6 beats: Question → Step 1 → Step 2 → Step 3 → Answer → Question Reframed)

**Beat 1 — The Question**
- Mood: open, suspended, facing-the-unknown
- Preferred compositions: figure shown from behind facing away, figure facing a blank wall, figure on a threshold, still-life (closed door alone)
- Metaphor families: the unanswered — blank wall, empty page, closed door, fork in a path
- Scale: medium, figure-centered, surrounded by space
- Avoid: answers, resolution imagery, multi-figure scenes

**Beat 2 — Logical Step 1**
- Mood: instructional, careful, single-idea
- Preferred compositions: object-forward (one prop), close-up of a single hand on a single object, isolated still-life
- Metaphor families: foundational objects — a single brick, a single key, a single coin, an open palm
- Scale: tight, one-element
- Avoid: complexity, multiple objects

**Beat 3 — Logical Step 2**
- Mood: building, additive, sequence
- Preferred compositions: two-element still-life, hand placing a second object beside the first, sequential frames
- Metaphor families: stacking — two bricks, a hand bridging two objects, a chain link
- Scale: medium, two-element
- Avoid: chaos, more than two focal points

**Beat 4 — Logical Step 3**
- Mood: completing, click-into-place
- Preferred compositions: three-element arrangement, sequential, fitting-together imagery
- Metaphor families: locking mechanisms — three bricks forming an arch, a key entering a lock, a final puzzle piece
- Scale: medium, structural
- Avoid: incompleteness imagery

**Beat 5 — The Answer**
- Mood: revelation, quiet recognition
- Preferred compositions: scale-shift, cross-section, single-element revealed
- Metaphor families: opened-up — door swung open, lid lifted off a box, curtain pulled back, a single object now in full view
- Scale: dramatic
- Avoid: dimming, atmospheric haze

**Beat 6 — The Question Reframed**
- Mood: returned-but-changed, settled
- Preferred compositions: echo of Beat 1 composition (figure-from-behind, threshold) — but one element deliberately changed
- Metaphor families: same scene, new posture — open door instead of closed, figure stepping forward instead of standing still
- Scale: medium, deliberately echoing the opener
- Avoid: a brand-new visual register — the *return* is the point

---

**SYSTEMS AUDIT** (5 beats: System Description → Failure Mode → Trigger → What System Optimizes For → Diagnostic Conclusion)

**Beat 1 — The System Description**
- Mood: engineering-precise, schematic, cool
- Preferred compositions: schematic/diagrammatic, cross-section, exposed-machine, still-life of the machine at rest
- Metaphor families: machine anatomy — gears in a row, pipes and valves, a circuit board, a cutaway engine
- Scale: medium with annotated detail
- Avoid: human warmth, organic curves

**Beat 2 — The Failure Mode**
- Mood: malfunction, interruption, jam
- Preferred compositions: object-forward with one element broken/displaced, close-up of a jammed gear, diptych (working/broken)
- Metaphor families: breakage — bent gear, snapped wire, leaking pipe, an arrow halted mid-flight, a stuck lever
- Scale: medium, single-failure-point
- Avoid: full-system shots — zoom in on the broken part

**Beat 3 — The Trigger**
- Mood: cause-and-effect, sequence
- Preferred compositions: sequential, theatre tableau (dominoes mid-fall), object-forward (input-leading-to-output)
- Metaphor families: trigger chain — a hand pressing a button, a pebble starting a rockslide, a match approaching a fuse
- Scale: medium, sequential
- Avoid: static single-shot imagery — show the chain

**Beat 4 — What the System Is Actually Optimizing For**
- Mood: pulled-back, reveal-of-purpose, redirection
- Preferred compositions: wide reveal showing where outputs actually go, two-figure contrast (expected vs. actual destination), diagrammatic (redirected-flow)
- Metaphor families: misdirection — water flowing somewhere unexpected, a track switching, a current pulling sideways
- Scale: wide, redirective
- Avoid: tight close-ups — pull back to show the *real* destination

**Beat 5 — The Diagnostic Conclusion**
- Mood: settled, system-at-rest, accepting
- Preferred compositions: the system shown calmly, working-as-designed, diagrammatic (annotated schematic), still-life
- Metaphor families: accepted-machine — a clock ticking steadily, a river flowing in its bed, an engine idling
- Scale: medium, balanced
- Avoid: triumph imagery, transformation imagery — this is *acceptance*, not victory

---

**COMPOSITE PORTRAIT** (4 movements: Surface → Cost → Origin → Reframe) — **the channel default (~10–15 min, full second person „ty")**

**Signature rules (apply across the whole set):**
- **One recurring figure.** The faceless figure is the SAME protagonist throughout — same silhouette/proportions, evolving posture across the movements. This continuity is the visual spine. Lean hard on the **Sequential** composition (same figure twice in one frame, at two moments). The script is now written in **full second person**, so this figure is the viewer's own avatar — „you"; it is never a named third-person character (the voice braid was retired 2026-05-29).
- **One recurring object-motif.** A single object (chair, door, stone, thread) introduced in Surface, reappearing transformed in every movement and at the close. Give it its own object-forward / still-life frames.
- **Figure calibration runs higher here: ~70–80% `**Figure:** yes`** (the protagonist is the spine) — but keep object-only/absence frames for the motif and for breathing room.

**Beat 1 — The Surface**
- Mood: intimate, observational, a caught private moment
- Preferred compositions: close-up of the figure mid-gesture (the telltale behaviour), object-forward (the motif introduced), overhead of the figure small in space
- Metaphor families: the tell — a repeated small action, the motif-object in the figure's hands, a habitual posture
- Scale: intimate, single-subject
- Avoid: diagram/explanation, multi-figure, anything that diagnoses (we observe, not explain yet)

**Beat 2 — The Cost**
- Mood: quiet weight, accumulation, depletion
- Preferred compositions: figure carrying/burdened, sequential (same figure twice — before/after the toll), still-life of aftermath (the motif worn, heavier)
- Metaphor families: weight & residue — sagging posture, an object grown heavy, traces left behind, an emptied room
- Scale: medium, the toll made physical
- Avoid: mechanism/diagram (too early), triumph

**Beat 3 — The Origin**
- Mood: revelation, structural, tender — not clinical
- Preferred compositions: cross-section/cutaway (the origin inside), scale-shift (the small root made enormous), sequential (figure now vs an earlier self), the motif shown at its beginning
- Metaphor families: roots & beginnings — a root system, a first imprint, a hand learning the gesture for the first time, the motif as it once was
- Scale: dramatic, the hidden made visible
- Avoid: cold-lab framing (this is the figure's history — keep it warm), blame imagery

**Beat 4 — The Reframe**
- Mood: settling, recognition, lightened
- Preferred compositions: diptych (old reading vs new reading of the SAME behaviour), figure holding the motif differently (same object, new relationship), figure upright/opened
- Metaphor families: same thing seen anew — the motif re-held, a door now open, the same posture unclenched
- Scale: balanced
- Avoid: "fixed/cured" imagery — this is acceptance, not victory

**Beat 5 — Permission Practice + Recognition Close**
- Mood: at rest, quiet, returned-but-changed
- Preferred compositions: echo of Beat 1's composition but with one element changed; figure at rest with the motif resolved; wide/quiet
- Metaphor families: the return — same scene, new posture; the motif set down or held lightly
- Scale: expansive but intimate
- Avoid: a brand-new visual register — the *return* to Beat 1 is the point

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

### Script Cleaning

Before processing, mentally strip these from the script:
- [EDITOR NOTE: ...] annotations
- Metadata headers (lines starting with #, Generated:, Model:, ARCHITECTURE:, ---)
- `## ` section-divider headers (2026-06-01) — these are editorial pause-markers, not spoken narration; `_clean_script` in `agent5_visuals.py` strips them automatically via `^#.*$`. Never generate an image for a section header line.

[Visual Pause] markers ARE preserved — treat them as beat-boundary signals (the writer is telling you "this is a moment of weight, hold the image"). Do not quote them in the `**Sentence:**` field, but use them to recognize that you are crossing into a new beat.

The text you quote in `**Sentence:**` fields must be clean narration text only.

### Self-Check List (before saving)

Before writing the file, verify:
1. Every sentence in the script is covered by exactly one entry (no gaps, no double-coverage)
2. `**Figure:**` calibration: 50–70% yes across the full set
3. No entry has "glowing", "dim", "shadowed", "scribbles", or readable text
4. Head-framing rule: every `**Figure:** yes` entry either shows the full head or explicitly excludes the head ("hand only")
5. Architecture declared and beats appear in the correct order
6. No `**Visual:**` entry contains CHARACTER_DESCRIPTION or STYLE_SUFFIX text
7. `Total images: <N>` in the header matches the actual count

---

## Output Location

```
outputs/
└── videos_pl/
    └── {slug}/
        └── md/
            ├── 04_final.md         (Agent 3 finalize — input for Agent 5)
            ├── 05_prompts.md       (Agent 5 output — review before Agent 9)
            └── 05_phrases.md       (simple phrase table for alignment)
```

---

## Output Format

**Compact format** (what `/visuals` writes — before `--expand`):

```markdown
## Image 001
**Beat:** The Symptom
**Figure:** yes
**Sentence:** "exact quoted sentence from the script"
**Visual:**
Faceless figure perched on the edge of a bed, one hand resting limp on a face-down phone on the mattress, spine bowed forward, shoulders drawn inward

---
```

**Full format** (after `--expand` injects constants):

```markdown
## Image 001
**Beat:** The Symptom
**Figure:** yes
**Sentence:** "exact quoted sentence from the script"
**Imagen prompt:**
[CHARACTER_DESCRIPTION]. Faceless figure perched on the edge of a bed..., [STYLE_SUFFIX]

---
```

Agent 9 reads the `**Imagen prompt:**` field and sends it directly to Vertex AI.

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

**Check beat-aware register:**
- Does each beat *look* like its register? Symptom-beat should feel quiet and intimate; investigation-beat should be evidence/diagrammatic; mechanism-reveal should use cutaway/scale-shift; close should be wide and resolving.
- Beats should appear in the order declared by the architecture.

**Check emotional accuracy:**
- Does each image amplify the emotional beat of its sentence?
- Statistics and mechanism explanations should feel clinical/precise. Empathy sections should feel open or collapsed.

**Check forbidden terms:**
- Scan for "glowing", "dim", "shadowed", "scribbles", "tangled lines", readable text — rewrite or remove any found.

**Edit directly** in `05_prompts.md` before running Agent 9. Changes to the `**Imagen prompt:**` line are what Imagen receives.

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

The compact `05_prompts.md` may be corrupted or already expanded. If it already has `**Imagen prompt:**` entries, it's ready for Agent 9. If it's empty or malformed, re-run `/visuals <slug>`.

**Beat field missing, wrong, or all the same beat**

Confirm the script's first non-blank, non-header line begins `ARCHITECTURE:` followed by one of the five names exactly. If the line is missing, `/visuals` falls back to Composite Portrait (the channel default) — which is wrong for any forced short-form architecture. Fix `04_final.md` and re-run.

**Investigation-beat images all show generic faceless figures**

The register is being read but ignored. Spot-fix: edit the `**Imagen prompt:**` lines directly to insert investigation props (magnifier, microscope, evidence board, schematic diagram, cutaway). Or re-run `/visuals` — prompts are non-deterministic and the second pass typically applies the register more aggressively.

---

## Next Step

After reviewing and editing `05_prompts.md`, generate the images:

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "<slug>" --generate
```
