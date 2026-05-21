"""
Agent 5: Visual Storytelling
Reads the final edited script and generates production-ready image prompts.
This is a dedicated visual pass — Claude Opus 4.7 focuses entirely on visual
composition, pacing, and emotional resonance without writing the script.

Outputs 05_image_prompts.md directly, ready for human review before Agent 9 generates images.

Usage:
    python tools/agent5_visuals.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
import json
import re
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, export_to_docx, CHARACTER_DESCRIPTION, STYLE_SUFFIX

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/04_script_final.md"
OUTPUT_FILENAME = "md/05_image_prompts.md"
CLAUDE_MODEL = "claude-opus-4-7"

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
    """Build 05_image_phrases.md — a simple table mapping image number to narration phrase."""
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


def _build_prompts_file(topic: str, items: list[dict], architecture: str = "") -> str:
    """Build the 05_image_prompts.md content from a list of {sentence, visual, beat} dicts."""
    today = date.today().isoformat()
    count = len(items)

    lines = [
        f"# Image Prompts: {topic}",
        f"Generated: {today}",
        f"Source: {SCRIPT_FILENAME}",
        f"Agent: agent5_visuals (claude-opus-4-7)",
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
# Claude API
# ---------------------------------------------------------------------------


def _generate_visuals(script_content: str) -> tuple[list[dict], dict, str]:
    """Call Claude Opus 4.7 in two batches to produce image prompts for the full script.

    Returns (items, usage, architecture). The architecture is read from the script's
    ARCHITECTURE: line and used to splice the matching visual register map into the
    system prompt before each call.
    """
    import anthropic

    architecture = _extract_architecture(script_content)
    system_prompt = _build_system_prompt(architecture)
    print(f"  Architecture: {architecture}")

    clean_text = _clean_script(script_content)

    # Split by paragraphs into two halves to stay within output token limits
    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    mid = len(paragraphs) // 2
    batches = [
        "\n\n".join(paragraphs[:mid]),
        "\n\n".join(paragraphs[mid:]),
    ]

    client = anthropic.Anthropic(api_key=get_env("ANTHROPIC_API_KEY"))
    all_items: list[dict] = []
    total_usage = {"model": CLAUDE_MODEL, "input_tokens": 0, "output_tokens": 0}

    for batch_num, batch_text in enumerate(batches, start=1):
        print(f"  Generating image prompts batch {batch_num}/{len(batches)}...")
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=16000,
            system=system_prompt,
            messages=[{"role": "user", "content": batch_text}],
        )

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = re.sub(r'^```[a-z]*\n?', '', raw)
            raw = re.sub(r'\n?```$', '', raw)

        items = json.loads(raw)
        all_items.extend(items)
        total_usage["input_tokens"] += message.usage.input_tokens
        total_usage["output_tokens"] += message.usage.output_tokens
        print(f"    Batch {batch_num}: {len(items)} prompts generated")

    return all_items, total_usage, architecture


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent5_visuals.py \"<slug>\"")
        print("Example: python tools/agent5_visuals.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 5: Visual Storytelling ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Read the final script
    print(f"[1/3] Reading {SCRIPT_FILENAME}...")
    try:
        script_content = read_output(slug, SCRIPT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 4 first:")
        print(f'  python tools/agent4a_edit.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic_from_script(script_content)
    print(f"  Topic  : {topic}")
    print(f"  Script length: {len(script_content):,} characters")

    # Step 2 — Generate image prompts via Claude Opus 4.7
    print(f"\n[2/3] Generating image prompts with {CLAUDE_MODEL}...")
    try:
        items, usage, architecture = _generate_visuals(script_content)
    except Exception as exc:
        print(f"\nError: Visual prompt generation failed — {exc}")
        sys.exit(1)

    if not items:
        print(f"\nError: No prompts generated from script.")
        sys.exit(1)

    print(f"  Total prompts generated: {len(items)}")

    # Step 3 — Save prompts file
    print(f"\n[3/3] Saving {OUTPUT_FILENAME}...")
    content = _build_prompts_file(topic, items, architecture)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    phrases_content = _build_phrases_file(topic, items)
    phrases_path = write_output(slug, "md/05_image_phrases.md", phrases_content)
    print(f"  Phrases: {phrases_path}")
    docx_path = export_to_docx(slug, "md/05_image_phrases.md", "docx/06_image_phrases.docx")
    print(f"  Word export: {docx_path}")

    print(f"\nGenerated {len(items)} image prompts. Review and edit {OUTPUT_FILENAME}, then run Agent 9:")
    print(f'  python tools/agent9_images.py "{slug}" --generate')


if __name__ == "__main__":
    main()
