# Narrative Architectures — Sensum Script SOP

This document defines how Agent 3 structures scripts. It replaces the previous 6-section template. Both Agent 3 (writing) and Agent 4 (editing) enforce these rules.

---

## Thematic Constraint

Every script must surface the gap between *what the brain does automatically* and *who the person believes they are*. This is the channel's core identity. The viewer should finish the video understanding something about themselves that they couldn't quite name before.

---

## Banned Phrases

These are hard bans. Agent 3 must not write them. Agent 4 must catch and remove any that appear.

**Banned openers:**
- "You are scrolling through your phone..."
- "You just closed the tab..."
- "I know that feeling"
- Any opener that starts with the viewer performing a mundane digital action

**Banned inline phrases:**
- "Read that again"
- "Take a breath"
- "Let that sink in"
- "Wondering what is wrong with you"
- "You are not alone" (as a standalone reassurance line — this can appear naturally in context, but not as an isolated comfort statement)

**Banned structural patterns:**
- Numbered prescription lists at the close (1st, 2nd, 3rd...)
- Ending with "This week, try..." or any challenge framed as a homework assignment
- Any section header used as narration (do not say "Now let's look at the science" or similar)

---

## The Four Narrative Architectures

Agent 3 reads the topic and verified research, then picks the single architecture that best fits. The choice is declared on the **first line** of the script output:

```
ARCHITECTURE: [Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit]
```

The architecture is a **shape**, not a rigid template. Use it to determine the entry point and the through-line — not as a checklist.

---

### Architecture 1 — The Forensic Case Study

**When to use:** The topic has a strange, counterintuitive, or extreme manifestation — a symptom, a case study, a behavior that seems impossible until you understand the mechanism.

**Entry point:** Open with a specific strange symptom, a documented case, or a biological anomaly. Something that makes the viewer think: *that can't be right.*

**Required content nodes:**
1. The symptom or case — described in precise, concrete detail
2. The investigation — what researchers found when they looked inside the brain
3. The culprit — the mechanism responsible, explained clearly
4. The ordinary implication — what this extreme case reveals about the viewer's own everyday experience

**Close constraint:** End on the implication for the viewer's life. Not steps. Not a list. The moment of recognition.

---

### Architecture 2 — The Historical Reversal

**When to use:** There is a belief that was treated as settled truth 30–50 years ago and has been substantially overturned by 2020–2026 research.

**Entry point:** State the old "truth" as if it were still true — then reveal that it isn't. The shock of that reversal is the hook.

**Required content nodes:**
1. The old belief — stated plainly, as most people still hold it
2. The study or discovery that broke it — specific, recent, verifiable
3. The mechanism the new research reveals — what is actually happening
4. The rewrite — what the viewer now understands that contradicts what they were taught

**Close constraint:** End on what the viewer now knows that most people don't. Not what they should do with it — just the weight of knowing it.

---

### Architecture 3 — The Socratic Challenge

**When to use:** The topic has a question at its core — something the viewer has probably asked themselves but never got a satisfying answer to. The question is hard enough that it can't be answered immediately.

**Entry point:** Ask the question directly. Do not soften it. Do not immediately begin answering it.

**Required content nodes:**
1. The question — posed cleanly and left open
2. Logical step 1 — the first thing you need to understand to approach the answer
3. Logical step 2 — the next layer
4. Logical step 3 — the piece that makes the answer inevitable
5. The answer — it should feel like the viewer worked it out themselves
6. The question reframed — return to the opening question, now with a different meaning

**Close constraint:** The final line should echo the opening question, but the answer is now obvious. No additional instruction needed.

---

### Architecture 4 — The Systems Audit

**When to use:** The topic involves a recurring pattern, a feedback loop, or a behavioral mechanism that can be understood as a system with inputs, outputs, and failure modes.

**Entry point:** Describe the brain or the behavior as a complex system. Use plain-English engineering terms — latency, recursive loop, cache, bandwidth, failure mode, signal, override. Keep the tone precise and cool, not clinical.

**Required content nodes:**
1. The system description — what it is and what it is designed to do
2. The failure mode being examined — what goes wrong and how
3. The trigger — what activates the failure mode
4. What the system is actually optimizing for — often different from what the person thinks
5. The diagnostic conclusion — what the system's behavior reveals

**Close constraint:** End with what the system *needs* — not what the *person should do*. This is a subtle but important distinction. The system has its own logic. Respect it.

---

## `[Visual Pause]` Marker

Use `[Visual Pause]` on its own line to indicate a moment where silence carries more weight than words. The narration pauses. The image holds.

- Maximum **3–4 per script**
- Place it between sentences, on its own line
- Use it only at moments of genuine weight — a revelation, a stark truth, a shift in perspective
- Agent 9 (image generation) ignores this marker completely; it is for narration timing and video editing only

**Format:**
```
[Visual Pause]
```

---

## Visual Register Maps

Agent 5 reads the `ARCHITECTURE:` line on top of the script and applies a **beat-specific visual register** to each section. The register is a *direction*, not a checklist — its job is to keep the symptom-beat from looking like the mechanism-beat from looking like the close.

Each register specifies: *Mood*, *Preferred Compositions*, *Metaphor Families*, *Scale*, and what to *Avoid*. Agent 5 still has to invent the specific shot.

---

### Forensic Case Study

**Beat 1 — The Symptom (opening)**
- Mood: clinical observation, quiet, intimate
- Preferred compositions: close-up of posture detail, overhead of figure in empty space, still-life of a single object
- Metaphor families: clinical evidence — a clipboard, a single chair, a phone face-down on a mattress, a stethoscope on a desk
- Scale: small, single-subject, intimate
- Avoid: dynamic action, multi-figure scenes, dramatic motion

**Beat 2 — The Investigation**
- Mood: forensic, diagrammatic, evidence-gathering
- Preferred compositions: object-forward (magnifying glass, lab instruments), cross-section/cutaway, two-figure contrast (researcher vs. subject), labeled diagrammatic illustration without text
- Metaphor families: investigation tools — magnifier, microscope, evidence board, schematic diagram, exposed mechanism, dissection layout
- Scale: medium with annotated detail
- Avoid: empty environments — populate with evidence

**Beat 3 — The Culprit (mechanism revealed)**
- Mood: revelation, structural, unveiling
- Preferred compositions: cross-section, cutaway, scale-shift (the small made enormous), x-ray transparency, anatomical view
- Metaphor families: anatomy revealed — brain cross-section, exposed gear, machine interior, root system underground, building cutaway
- Scale: dramatic, the hidden made huge
- Avoid: surface-level exteriors, generic faceless figure poses

**Beat 4 — The Implication (close)**
- Mood: quiet, resolving, wide
- Preferred compositions: wide (figure-in-landscape), figure-walking-away, doorframe/passage, figure on a threshold
- Metaphor families: return to life — open doorway, horizon line, single figure walking forward, dawn-window, an empty path
- Scale: expansive, figure small but resolved
- Avoid: tight intimacy, claustrophobia

---

### Historical Reversal

**Beat 1 — The Old Belief**
- Mood: dignified, period, settled
- Preferred compositions: formal portrait pose, single-figure dignified, old-textbook layout, framed picture on a wall
- Metaphor families: period authority — old textbook, lecture podium, wall-mounted portrait, framed certificate, dusty leather-bound book
- Scale: medium, formal, centered
- Avoid: motion, contemporary objects, asymmetry

**Beat 2 — The Discovery That Broke It**
- Mood: dynamic, unexpected angle, off-balance
- Preferred compositions: dutch-angle equivalent (tilted horizon line), two-figure contrast (old vs. new), object-forward with a single new instrument
- Metaphor families: a hand reaching past a barrier, a single new tool, a notebook page mid-write, a paper torn down the middle
- Scale: medium with one element breaking the frame's symmetry
- Avoid: settled formal compositions — break the visual rhythm of beat 1

**Beat 3 — The New Mechanism**
- Mood: modern, diagrammatic, clean
- Preferred compositions: cross-section, schematic diagram, flowchart-like sequence, anatomical cutaway
- Metaphor families: modern science — clean diagram, flowchart arrows, exposed circuit board, anatomical illustration
- Scale: medium with annotated detail
- Avoid: period imagery, formal portraits

**Beat 4 — The Rewrite**
- Mood: side-by-side weight, recognition, settled-new
- Preferred compositions: diptych (before/after), two-figure contrast (then/now), erasure-and-replace layout
- Metaphor families: comparison artifacts — left page vs. right page, framed old vs. open new, a hand crossing out and rewriting
- Scale: balanced, two-element composition
- Avoid: single-element shots — this beat is *about* the contrast

---

### Socratic Challenge

**Beat 1 — The Question**
- Mood: open, suspended, facing-the-unknown
- Preferred compositions: back-of-head shot (figure looking away from viewer), figure facing a blank wall, figure on a threshold
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
- Preferred compositions: three-element arrangement, completed structure, fitting-together imagery
- Metaphor families: locking mechanisms — three bricks forming an arch, a key entering a lock, a final puzzle piece
- Scale: medium, structural
- Avoid: incompleteness imagery

**Beat 5 — The Answer**
- Mood: revelation, quiet recognition
- Preferred compositions: scale-shift (the small made enormous), cross-section, single-element revealed
- Metaphor families: opened-up — door swung open, lid lifted off a box, curtain pulled back, a single object now in full light
- Scale: dramatic
- Avoid: dimming, atmospheric haze (style forbids it anyway)

**Beat 6 — The Question Reframed**
- Mood: returned-but-changed, settled
- Preferred compositions: echo of Beat 1 composition (back-of-head, threshold) — but now with one element changed
- Metaphor families: same scene, new posture — open door instead of closed, figure stepping forward instead of standing still
- Scale: medium, deliberately echoing the opener
- Avoid: a brand-new visual register — the *return* is the point

---

### Systems Audit

**Beat 1 — The System Description**
- Mood: engineering-precise, schematic, cool
- Preferred compositions: schematic diagram, exposed-machine, flowchart-style layout, cross-section
- Metaphor families: machine anatomy — gears in a row, pipes and valves, a circuit board, a cutaway engine
- Scale: medium with annotated detail
- Avoid: human warmth, organic curves

**Beat 2 — The Failure Mode**
- Mood: malfunction, interruption, jam
- Preferred compositions: object-forward with one element broken/displaced, close-up of a jammed gear, before/after split
- Metaphor families: breakage — bent gear, snapped wire, leaking pipe, an arrow halted mid-flight, a stuck lever
- Scale: medium, single-failure-point
- Avoid: full-system shots — zoom in on the broken part

**Beat 3 — The Trigger**
- Mood: cause-and-effect, sequence
- Preferred compositions: sequential frames (3 panels), domino-effect arrangement, input-leading-to-output
- Metaphor families: trigger chain — a hand pressing a button, a pebble starting a rockslide, a match approaching a fuse
- Scale: medium, sequential
- Avoid: static single-shot imagery — show the chain

**Beat 4 — What the System Is Actually Optimizing For**
- Mood: pulled-back, reveal-of-purpose, redirection
- Preferred compositions: wide reveal showing where outputs actually go, two-figure contrast (expected vs. actual destination), redirected-flow diagram
- Metaphor families: misdirection — water flowing somewhere unexpected, a track switching, a current pulling sideways
- Scale: wide, redirective
- Avoid: tight close-ups — pull back to show the *real* destination

**Beat 5 — The Diagnostic Conclusion**
- Mood: settled, system-at-rest, accepting
- Preferred compositions: the system shown calmly, working-as-designed, an annotated schematic
- Metaphor families: accepted-machine — a clock ticking steadily, a river flowing in its bed, an engine idling
- Scale: medium, balanced
- Avoid: triumph imagery, transformation imagery — this is *acceptance*, not victory

---

**Note for Agent 5:** Each beat above is a *direction*, not a checklist. Use the composition + metaphor + scale as starting points and invent the specific shot. The register exists to ensure that the symptom-beat does not look like the mechanism-beat does not look like the close.
