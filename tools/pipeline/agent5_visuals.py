"""
Agent 5: Visual Storytelling — post-processing only (no LLM API)

Image prompts are generated IN-SESSION in Claude Code on Opus 4.8 via the
`/visuals <slug>` slash command — no Gemini, no Anthropic API. This script does
only the deterministic work:

  --expand          Inject CHARACTER_DESCRIPTION + STYLE_SUFFIX constants into the
                    compact **Visual:** fields of 05_prompts.md, rebuild phrase files.
  --extract         Extract docx/script_corrected.docx → md/script_corrected.md.
                    Called automatically by the /visuals skill when script_corrected.docx exists.
                    (Extraction only — no API.)

Usage:
    /visuals <slug>                                                  # generate compact prompts in-session
    python tools/pipeline/agent5_visuals.py "<slug>" --expand        # assemble full Imagen prompts
    python tools/pipeline/agent5_visuals.py "<slug>" --extract       # extract script_corrected.docx → .md
"""

import sys
import os
import json
import re
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, export_to_docx, get_output_dir, read_script_docx_text, CHARACTER_DESCRIPTION, STYLE_SUFFIX

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/04_final.md"
OUTPUT_FILENAME = "md/05_prompts.md"

SYSTEM_PROMPT = """\
You are a visual director for a YouTube psychology channel. Your only job in this pass is visual storytelling.

You will receive the final narration script. Read it fully to understand the arc, then work through it \
systematically — assigning a visual scene to each moment.

## Output Format

Return a JSON array with no markdown fencing:
[{"sentence": "exact quoted sentence(s) from the script", "visual": "40-60 word image description", "beat": "<beat name from the architecture below>", "include_figure": true|false}, ...]

The `beat` field is required. Use the exact beat name from the architecture's Beat Sequence below.

The `include_figure` field is required — `true` when the scene meaningfully needs the faceless figure, `false` when the scene is better served by an object, environment, anatomical diagram, or pure absence. See the "When to Include the Figure" section below.

## Pacing Rules

- Generate as many images as needed — one per sentence is the default
- Group 2-3 consecutive sentences ONLY when they describe the identical visual scene (same object, same action, \
same spatial framing) — any new concept, location, object, or emotional beat = new entry
- Section transitions always get their own image
- Statistics, metaphors, and [Visual Pause] moments each get their own image
- Every sentence in the script must be covered by exactly one entry
- There is no upper or lower limit — cover the script completely

## Composition Types

Each visual must specify one of these compositions. Vary across the full set — use each at least 6 \
times where the beat allows, never repeat the same type more than twice in a row:

- **Close-up**: just hands holding an object, a detail of posture, two hands in contrast
- **Overhead**: figure viewed from directly above, small in large empty space
- **Wide**: figure tiny against a large architectural element (doorframe, wall, staircase, bookshelf)
- **Two-figure contrast**: left/right split showing before vs after, trapped vs free, alone vs connected
- **Sequential**: one figure shown twice in same frame at different moments (ghost posture, faded duplicate)
- **Object-forward**: the prop dominates the frame, figure interacts with it from the side
- **Cross-section / cutaway**: a structure sliced open to reveal its interior (a head shown as a cutaway, \
a building cross-section, an exposed mechanism inside a box)
- **Scale-shift**: a normally small thing rendered enormous (a single neuron the size of a tree, a thought \
rendered as architecture), or a normally large thing rendered tiny
- **Diagrammatic / schematic**: an unlabeled flowchart, gear chain, circuit-style layout, or anatomical \
plate — composition reads as illustration-from-a-textbook rather than scene-from-life
- **Still-life (no figure)**: scene contains NO human figure — just a single object, a pair of objects, \
or an empty environment that carries the emotion (a chair, a closed door, a desk, a pair of shoes)
- **Diptych / before-after**: two equally weighted frames side-by-side showing the same subject in two \
states (then/now, old/new, before/after) — distinct from two-figure contrast because both halves can be \
objects, environments, or postures
- **Theatre tableau**: three or more figures arranged in a stage-like composition, frozen mid-gesture, \
centered, slightly stylized

Any composition may be rendered without a figure when the scene's meaning lives in absence, \
in objects, in an environment, or in an anatomical/diagrammatic mechanism — see the next section.

## When to Include the Figure

The faceless figure is the SIGNATURE element of this channel — it carries embodied emotion, the \
feeling of being a person inside a body. But not every sentence is about a person. Some sentences \
are about absence, signals, objects, mechanisms, or pure environment. For those, the figure becomes \
a generic intrusion that dilutes the meaning. Treat the figure as a precious resource you spend, \
not a default you stamp.

For EACH visual, decide whether the scene meaningfully requires the faceless figure to convey what \
the sentence is doing. Set `include_figure: true` only when the answer is YES.

INCLUDE the figure when:
- The sentence is about a person doing, holding, carrying, releasing, collapsing, rising, or \
  sitting with something.
- The emotional weight lives in a body — interior burden made physical, embodied tension, \
  self-confrontation, two states of a self side-by-side.
- The sentence asks the viewer to FEEL like they are the figure.

OMIT the figure when:
- The sentence is about an absence ("nothing happened", "no one called", "no funeral").
- The meaning is a list of objects, places, or signals (an empty chair, an empty mailbox, a \
  single closed door, a half-empty glass).
- The sentence describes a psychological mechanism that reads more clearly as an anatomical \
  cutaway, a cross-section, or a 19th-century scientific diagram than as a person.
- The scene is pure environment — a hallway, an empty room, a horizon.
- A symbolic object carries the meaning more powerfully than any body would.

When in doubt, ask: does the sentence want the viewer to see a *person*, or to see *what a person \
is left with*?

CALIBRATION: across the full set, expect roughly 50–70% include_figure=true. If your output is \
90%+ figures, you are under-using absence. If 30% or below, you are losing the channel's signature.

## Beat Sequence & Visual Register

{VISUAL_REGISTER_BLOCK}

## What Each Visual Must Include

1. Composition type (implied by the scene description, not labeled)
2. Exact body posture — conveys emotion without any face
3. Props or minimal environment (one ink-line doorframe, a desk, a phone, a chair)
4. Spatial relationship between figure and object/space

## Character Rules

If a scene includes a figure (`include_figure: true`), that figure is FACELESS: blank smooth oval head, \
no eyes, no nose, no mouth, no ears, no hair. Completely androgynous body. Convey ALL emotion through \
posture and body position only — never describe a facial expression.

If a scene omits the figure (`include_figure: false`), do not invent body parts or implied silhouettes. \
The composition stands on its objects, its environment, or its anatomical/diagrammatic structure. \
Anatomical fragments (a sectioned chest, a cross-section of a hand) are permissible without counting \
as a "figure" — they live in the diagrammatic register and `include_figure` stays `false`.

## Framing Rule (CRITICAL)

If your description includes a figure, the *entire head must fit inside the frame* with visible headroom \
above. Never describe a shot that would crop the top of the head. If you want a hand-only or detail-only \
shot, explicitly say "hand only, no head or body visible in frame" — do not just leave the head implied.

Examples of correct framing language:
- "Faceless figure standing centered, full head visible with clear space above"
- "Close-up of two hands only — no head, no torso, no body visible in frame"
- "Wide view: faceless figure in lower portion of frame, entire body and head visible, large empty space above"

Examples to avoid:
- "Bust shot of faceless figure" (ambiguous — may crop head)
- "Faceless figure's torso and shoulders" (head fate unclear — may be cropped)
- Any phrasing that asks for partial body without explicitly saying what is and isn't in frame

## Forbidden Terms — Replace Before Outputting

- "glowing" / "illuminated" / "lit up" → describe the object plainly ("phone screen", "laptop screen")
- "scribbles", "tangled lines", "jagged marks" floating around a figure → remove entirely
- "dim", "dark", "shadowed" environment → always clean white background, remove these
- Any readable text, labels, numbers, or digits on objects

## Good Examples (match this specificity and length)

**With figure (`include_figure: true`):**

- "Faceless figure perched on the edge of a bed, one hand resting limp on a face-down phone on the \
mattress, spine bowed forward, shoulders drawn inward"
- "Overhead view: faceless figure lying flat on a bare floor, arms spread slightly outward, seen from \
directly above, surrounded by empty space"
- "Two faceless figures side by side — left one stands with shoulders collapsed, right one stands upright \
with arms open; wide gap between them"
- "Close-up of two hands: one hand open and releasing a small rectangular shape, the other hand empty \
and open below it"
- "Faceless figure dwarfed beside a tall doorframe, one hand on the frame edge, entire body small against \
the architectural scale"
- "Faceless figure seated at a desk, one hand flat on a closed book, other arm hanging loose at the side, \
torso leaning slightly back"

**Without figure (`include_figure: false`):**

- "An empty wooden chair with a straight back angled slightly toward an open empty doorway on a plain \
bare floor, the doorway framing only hollow white emptiness beyond"
- "An empty rural mailbox mounted on a weathered wooden post, its small metal door hanging open on a \
slack hinge, the interior hollow with fine cross-hatched darkness, the red flag lowered and still"
- "Cross-section anatomical diagram of a human chest cavity in 19th-century scientific etching style, \
the ribcage opened like a delicate cabinet, each rib finely articulated in cross-hatched ink, a small \
nested chamber at center"
- "A tipped antique hourglass on its side with fine sand spilling in a delicate curving stream onto a \
plain surface, beside it a single glass vessel half-filled with water, one round droplet suspended \
mid-fall above its surface"
- "A single closed wooden door at the end of a long bare corridor, no figure, the corridor walls drawn \
in receding parallel cross-hatched lines, heavy negative space, the door rendered as the sole subject"

## Script Cleaning

Before processing, mentally strip these from the script:
- [EDITOR NOTE: ...] annotations
- Metadata headers (lines starting with #, Generated:, Model:, ARCHITECTURE:, ---)

[Visual Pause] markers ARE preserved in the input — treat them as beat-boundary signals (the writer is \
telling you "this is a moment of weight, hold the image"). Do not quote them in the `sentence` field, but \
use them to recognize that you are crossing into a new beat.

The sentences you quote in "sentence" fields must be clean narration text only.
"""

# ---------------------------------------------------------------------------
# Visual Register Maps — one per architecture
# Source of truth: workflows/narrative_architectures.md (## Visual Register Maps)
# This dict mirrors that doc so the agent is self-contained.
# ---------------------------------------------------------------------------

VISUAL_REGISTER_MAPS = {
    "Forensic Case Study": """\
This script uses the **Forensic Case Study** architecture. It has four beats. Identify which beat each \
sentence belongs to and choose composition + metaphor from that beat's register. Beats appear in order; \
[Visual Pause] markers and explicit transitions ("Start with the symptom…", "Now the investigation…", \
"Here is the mechanism…", "Now look at what this reveals…") signal beat boundaries.

**Beat 1 — The Symptom (opening)**
- Mood: clinical observation, quiet, intimate
- Preferred compositions: close-up of posture detail, overhead of figure in empty space, still-life
- Metaphor families: clinical evidence — clipboard, single chair, phone face-down, stethoscope on desk
- Scale: small, single-subject, intimate
- Avoid: dynamic action, multi-figure scenes, dramatic motion

**Beat 2 — The Investigation**
- Mood: forensic, diagrammatic, evidence-gathering
- Preferred compositions: object-forward (magnifier, lab instruments), cross-section/cutaway, \
two-figure contrast (researcher vs. subject), diagrammatic/schematic
- Metaphor families: investigation tools — magnifier, microscope, evidence board, schematic diagram, \
exposed mechanism, dissection layout
- Scale: medium with annotated detail
- Avoid: empty environments — populate with evidence

**Beat 3 — The Culprit (mechanism revealed)**
- Mood: revelation, structural, unveiling
- Preferred compositions: cross-section, cutaway, scale-shift (the small made enormous), \
diagrammatic, x-ray transparency
- Metaphor families: anatomy revealed — brain cross-section, exposed gear, machine interior, \
root system underground, building cutaway
- Scale: dramatic, the hidden made huge
- Avoid: surface-level exteriors, generic faceless figure poses

**Beat 4 — The Implication (close)**
- Mood: quiet, resolving, wide
- Preferred compositions: wide (figure-in-landscape), figure-walking-away, doorframe/passage, \
figure on a threshold
- Metaphor families: return to life — open doorway, horizon line, single figure walking forward, \
dawn-window, empty path
- Scale: expansive, figure small but resolved
- Avoid: tight intimacy, claustrophobia
""",
    "Historical Reversal": """\
This script uses the **Historical Reversal** architecture. It has four beats. Identify which beat each \
sentence belongs to and choose composition + metaphor from that beat's register.

**Beat 1 — The Old Belief**
- Mood: dignified, period, settled
- Preferred compositions: formal portrait pose, single-figure dignified, still-life (old textbook), \
framed picture on a wall
- Metaphor families: period authority — old textbook, lecture podium, wall portrait, framed certificate, \
dusty leather-bound book
- Scale: medium, formal, centered
- Avoid: motion, contemporary objects, asymmetry

**Beat 2 — The Discovery That Broke It**
- Mood: dynamic, unexpected angle, off-balance
- Preferred compositions: two-figure contrast (old vs. new), object-forward (single new instrument), \
diptych showing rupture
- Metaphor families: a hand reaching past a barrier, a single new tool, a notebook page mid-write, \
a paper torn down the middle
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
- Preferred compositions: diptych (before/after), two-figure contrast (then/now), \
erasure-and-replace layout
- Metaphor families: comparison artifacts — left page vs. right page, framed old vs. open new, \
a hand crossing out and rewriting
- Scale: balanced, two-element composition
- Avoid: single-element shots — this beat IS the contrast
""",
    "Socratic Challenge": """\
This script uses the **Socratic Challenge** architecture. It has six beats. Identify which beat each \
sentence belongs to and choose composition + metaphor from that beat's register.

**Beat 1 — The Question**
- Mood: open, suspended, facing-the-unknown
- Preferred compositions: figure shown from behind facing away, figure facing a blank wall, \
figure on a threshold, still-life (closed door alone)
- Metaphor families: the unanswered — blank wall, empty page, closed door, fork in a path
- Scale: medium, figure-centered, surrounded by space
- Avoid: answers, resolution imagery, multi-figure scenes

**Beat 2 — Logical Step 1**
- Mood: instructional, careful, single-idea
- Preferred compositions: object-forward (one prop), close-up of a single hand on a single object, \
isolated still-life
- Metaphor families: foundational objects — a single brick, a single key, a single coin, an open palm
- Scale: tight, one-element
- Avoid: complexity, multiple objects

**Beat 3 — Logical Step 2**
- Mood: building, additive, sequence
- Preferred compositions: two-element still-life, hand placing a second object beside the first, \
sequential frames
- Metaphor families: stacking — two bricks, a hand bridging two objects, a chain link
- Scale: medium, two-element
- Avoid: chaos, more than two focal points

**Beat 4 — Logical Step 3**
- Mood: completing, click-into-place
- Preferred compositions: three-element arrangement, sequential, fitting-together imagery
- Metaphor families: locking mechanisms — three bricks forming an arch, a key entering a lock, \
a final puzzle piece
- Scale: medium, structural
- Avoid: incompleteness imagery

**Beat 5 — The Answer**
- Mood: revelation, quiet recognition
- Preferred compositions: scale-shift, cross-section, single-element revealed
- Metaphor families: opened-up — door swung open, lid lifted off a box, curtain pulled back, \
a single object now in full view
- Scale: dramatic
- Avoid: dimming, atmospheric haze (style forbids it anyway)

**Beat 6 — The Question Reframed**
- Mood: returned-but-changed, settled
- Preferred compositions: echo of Beat 1 composition (figure-from-behind, threshold) — but one element \
deliberately changed
- Metaphor families: same scene, new posture — open door instead of closed, figure stepping forward \
instead of standing still
- Scale: medium, deliberately echoing the opener
- Avoid: a brand-new visual register — the *return* is the point
""",
    "Systems Audit": """\
This script uses the **Systems Audit** architecture. It has five beats. Identify which beat each \
sentence belongs to and choose composition + metaphor from that beat's register.

**Beat 1 — The System Description**
- Mood: engineering-precise, schematic, cool
- Preferred compositions: schematic/diagrammatic, cross-section, exposed-machine, still-life of \
the machine at rest
- Metaphor families: machine anatomy — gears in a row, pipes and valves, a circuit board, \
a cutaway engine
- Scale: medium with annotated detail
- Avoid: human warmth, organic curves

**Beat 2 — The Failure Mode**
- Mood: malfunction, interruption, jam
- Preferred compositions: object-forward with one element broken/displaced, close-up of a jammed \
gear, diptych (working/broken)
- Metaphor families: breakage — bent gear, snapped wire, leaking pipe, an arrow halted mid-flight, \
a stuck lever
- Scale: medium, single-failure-point
- Avoid: full-system shots — zoom in on the broken part

**Beat 3 — The Trigger**
- Mood: cause-and-effect, sequence
- Preferred compositions: sequential, theatre tableau (dominoes mid-fall), object-forward \
(input-leading-to-output)
- Metaphor families: trigger chain — a hand pressing a button, a pebble starting a rockslide, \
a match approaching a fuse
- Scale: medium, sequential
- Avoid: static single-shot imagery — show the chain

**Beat 4 — What the System Is Actually Optimizing For**
- Mood: pulled-back, reveal-of-purpose, redirection
- Preferred compositions: wide reveal showing where outputs actually go, two-figure contrast \
(expected vs. actual destination), diagrammatic (redirected-flow)
- Metaphor families: misdirection — water flowing somewhere unexpected, a track switching, \
a current pulling sideways
- Scale: wide, redirective
- Avoid: tight close-ups — pull back to show the *real* destination

**Beat 5 — The Diagnostic Conclusion**
- Mood: settled, system-at-rest, accepting
- Preferred compositions: the system shown calmly, working-as-designed, diagrammatic (annotated \
schematic), still-life
- Metaphor families: accepted-machine — a clock ticking steadily, a river flowing in its bed, \
an engine idling
- Scale: medium, balanced
- Avoid: triumph imagery, transformation imagery — this is *acceptance*, not victory
""",
}

VISUAL_REGISTER_FALLBACK = """\
No architecture declared in the script header. Generate visuals using the composition vocabulary above; \
identify beats organically from the script's structure and tag each entry with a beat name of your choice.
"""


def _extract_architecture(script_content: str) -> str:
    """Return the architecture name from the ARCHITECTURE: line, or 'Forensic Case Study' as fallback."""
    m = re.search(r"^\s*ARCHITECTURE:\s*(.+?)\s*$", script_content, re.MULTILINE | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return "Forensic Case Study"


def _build_system_prompt(architecture: str) -> str:
    """Splice the architecture's visual register block into the SYSTEM_PROMPT template."""
    register_block = VISUAL_REGISTER_MAPS.get(architecture, VISUAL_REGISTER_FALLBACK)
    return SYSTEM_PROMPT.replace("{VISUAL_REGISTER_BLOCK}", register_block)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_topic_from_script(script_content: str) -> str:
    """Extract the topic from the first heading of the final script file."""
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Final:"):
            return line[len("# Script Final:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _clean_script(script_content: str) -> str:
    """Strip metadata and EDITOR NOTEs, return clean narration text.

    [Visual Pause] markers are PRESERVED — they are beat-boundary signals for the visual director.
    The ARCHITECTURE: line is stripped (it's already injected into the system prompt).
    """
    text = script_content
    text = re.sub(r'\[EDITOR NOTE:[^\]]+\]', '', text)
    text = re.sub(r'\[IMAGE:[^\]]+\]', '', text)
    text = re.sub(r'^\s*ARCHITECTURE:.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r'^#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^(Generated:|Model:|Pass:|Estimated duration:|Editor notes).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _build_imagen_prompt(visual: str, include_figure: bool = True) -> str:
    """Assemble the full Imagen prompt from a visual description.

    Prepends CHARACTER_DESCRIPTION only when the scene includes the faceless figure.
    When include_figure is False, the visual stands alone as object/environment/diagram.
    """
    if include_figure:
        return CHARACTER_DESCRIPTION + ". " + visual.strip() + ", " + STYLE_SUFFIX
    return visual.strip() + ", " + STYLE_SUFFIX


def _build_phrases_file(topic: str, items: list[dict]) -> str:
    """Build 05_phrases.md — a simple table mapping image number to narration phrase."""
    lines = [
        f"# Image Phrases: {topic}",
        "",
        "| # | Phrase |",
        "|---|--------|",
    ]
    for i, item in enumerate(items, start=1):
        phrase = item["sentence"].strip().replace('"', '"').replace('"', '"')
        lines.append(f'| {i:03d} | "{phrase}" |')
    return "\n".join(lines) + "\n"


def _build_prompts_file(topic: str, items: list[dict], architecture: str = "", source: str = "") -> str:
    """Build the 05_prompts.md content from a list of {sentence, visual, beat} dicts."""
    today = date.today().isoformat()
    count = len(items)

    lines = [
        f"# Image Prompts: {topic}",
        f"Generated: {today}",
        f"Source: {source or SCRIPT_FILENAME}",
        f"Agent: agent5_visuals (claude-opus-4-8 / Claude Code)",
        f"Architecture: {architecture}" if architecture else "",
        f"Total images: {count}",
        "",
        "Review and edit these prompts before generating. "
        "Each prompt feeds directly into Vertex AI Imagen.",
        "",
        "---",
    ]

    for i, item in enumerate(items, start=1):
        include_figure = bool(item.get("include_figure", True))
        imagen_prompt = _build_imagen_prompt(item["visual"], include_figure)
        beat = item.get("beat", "").strip()
        figure_line = f"**Figure:** {'yes' if include_figure else 'no'}"
        header = f"## Image {i:03d}"

        # Beat + Figure rendered as separate field lines so agent9's tolerant
        # regex `## Image \d+\n(?:\*\*[^*]+\*\*[^\n]*\n)*?\*\*Sentence:\*\*`
        # keeps working unchanged.
        entry = ["", header]
        if beat:
            entry.append(f"**Beat:** {beat}")
        entry.append(figure_line)
        entry += [
            f'**Sentence:** "{item["sentence"].strip()}"',
            "**Imagen prompt:**",
            imagen_prompt,
            "",
            "---",
        ]
        lines += entry

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Expand mode — post-process compact prompts file (no API call)
# ---------------------------------------------------------------------------


def _expand_mode(slug: str) -> None:
    """Expand **Visual:** fields in compact 05_prompts.md into full **Imagen prompt:** entries.

    Called either by --expand flag or automatically when a compact file is detected.
    Also rebuilds 05_phrases.md and exports 05_phrases.docx.
    """
    print(f"\n=== Agent 5: Expand Imagen Prompts ===")
    print(f"Slug: {slug}\n")

    try:
        content = read_output(slug, OUTPUT_FILENAME)
    except FileNotFoundError:
        print(f"Error: {OUTPUT_FILENAME} not found. Run /visuals {slug} first.")
        sys.exit(1)

    if "**Visual:**" not in content:
        if "**Imagen prompt:**" in content:
            print("Already expanded (no **Visual:** fields found). Nothing to do.")
            return
        print("Error: No **Visual:** or **Imagen prompt:** fields found.")
        print("The file may be corrupted. Delete it and re-run /visuals.")
        sys.exit(1)

    items: list[dict] = []

    def _replacer(m: re.Match) -> str:
        figure_str = m.group(2).strip().lower()
        sentence_line = m.group(3)
        sentence_raw = m.group(4).strip()
        visual_text = m.group(5).strip()
        include_figure = figure_str == "yes"
        # Strip outer quote pair for the phrase table (keep sentence_line intact for the prompts file)
        sentence_clean = sentence_raw
        if len(sentence_clean) >= 2 and sentence_clean[0] in ('"', '“') and sentence_clean[-1] in ('"', '”'):
            sentence_clean = sentence_clean[1:-1]
        items.append({"sentence": sentence_clean, "include_figure": include_figure})
        imagen_prompt = _build_imagen_prompt(visual_text, include_figure)
        return (
            f"**Figure:** {figure_str}\n"
            f"{sentence_line}\n"
            f"**Imagen prompt:**\n{imagen_prompt}"
        )

    # Match Figure + Sentence + Visual block, stopping at the next separator or image header
    pattern = re.compile(
        r'(\*\*Figure:\*\*\s*(yes|no))\n'
        r'(\*\*Sentence:\*\*\s*(.+?))\n'
        r'\*\*Visual:\*\*\n(.*?)(?=\n\n---|\n\n## Image|\Z)',
        re.DOTALL | re.IGNORECASE,
    )

    expanded = pattern.sub(_replacer, content)

    if not items:
        print("Error: Pattern matched no entries. Check the compact file format.")
        sys.exit(1)

    # Update the review note in the header
    expanded = expanded.replace(
        "Review and edit these prompts before expanding. Run --expand to assemble full Imagen prompts.",
        "Review and edit these prompts before generating. Each prompt feeds directly into Vertex AI Imagen.",
    )

    output_path = write_output(slug, OUTPUT_FILENAME, expanded)
    print(f"  Expanded {len(items)} image prompts → {output_path}")

    # Rebuild phrase files
    topic = "Unknown Topic"
    for line in expanded.splitlines():
        if line.startswith("# Image Prompts:"):
            topic = line[len("# Image Prompts:"):].strip()
            break

    phrases_content = _build_phrases_file(topic, items)
    phrases_path = write_output(slug, "md/05_phrases.md", phrases_content)
    print(f"  Phrases: {phrases_path}")
    docx_path = export_to_docx(slug, "md/05_phrases.md", "docx/05_phrases.docx")
    print(f"  Word export: {docx_path}")

    print(f"\nDone. Review {OUTPUT_FILENAME}, then run Agent 9:")
    print(f'  PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "{slug}" --generate')


# ---------------------------------------------------------------------------
# NOTE: Image-prompt GENERATION now happens in-session in Claude Code on Opus 4.8
# via `/visuals` (prompt source: workflows/pipeline/05_visuals.md). The former
# `_generate_visuals()` Anthropic-API call was removed on 2026-05-29 (zero Claude
# API). The SYSTEM_PROMPT / _build_system_prompt / _clean_script helpers above are
# retained for reference only and are no longer invoked by this script.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent 5: Visual Storytelling — generate image prompts from script"
    )
    parser.add_argument("slug", help="Output directory slug")
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract docx/script_corrected.docx → md/script_corrected.md (called automatically by /visuals skill).",
    )
    parser.add_argument(
        "--expand",
        action="store_true",
        help="Expand **Visual:** fields in existing 05_prompts.md into full Imagen prompts, then rebuild phrase files.",
    )
    args = parser.parse_args()

    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    if args.expand:
        _expand_mode(slug)
        return

    print(f"\n=== Agent 5: Visual Storytelling ===")
    print(f"Slug : {slug}")
    print()

    if args.extract:
        # Extraction only (no LLM). Pull the user-edited body text out of
        # docx/script_corrected.docx → md/script_corrected.md for /visuals.
        docx_path = get_output_dir(slug) / "docx" / "script_corrected.docx"
        if not docx_path.exists():
            print(f"No script_corrected.docx found at {docx_path} — nothing to extract.")
            sys.exit(0)
        text = read_script_docx_text(docx_path)
        out = get_output_dir(slug) / "md" / "script_corrected.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"  Extracted → md/script_corrected.md")
        sys.exit(0)

    # Default path: image prompts are produced in-session by /visuals. This script
    # only assembles them. Check for an existing compact or expanded prompts file.
    prompts_path = get_output_dir(slug) / OUTPUT_FILENAME
    if prompts_path.exists():
        existing_content = prompts_path.read_text(encoding="utf-8")
        if "**Visual:**" in existing_content:
            print("Found compact 05_prompts.md (generated by /visuals). Running --expand...")
            _expand_mode(slug)
            return
        elif "**Imagen prompt:**" in existing_content:
            print("05_prompts.md already expanded. Nothing to do.")
            print(f"Review {OUTPUT_FILENAME} and run Agent 9 when ready:")
            print(f'  PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "{slug}" --generate')
            sys.exit(0)

    print("\nError: md/05_prompts.md not found.")
    print("\nGenerate image prompts via Claude Code slash command (no API cost):")
    print(f"  /visuals {slug}")
    sys.exit(1)


if __name__ == "__main__":
    main()
