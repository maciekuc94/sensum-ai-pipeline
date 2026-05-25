"""
Agent 3a: Script Draft (Pass 1 of 3)
Reads the verified research document produced by Agent 2 and writes a complete
~1,850-word narration script using one of the four narrative architectures,
followed by a mandatory Permission Practice closing section and recognition close.

Review outputs/[slug]/md/03a_draft.md before running Agent 3b.

Usage:
    python tools/agent3a_draft.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, load_style_guide, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESEARCH_FILENAME = "md/02_verified_research.md"
MATERIALS_FILENAME = "md/00_materials_insights.md"
OUTPUT_FILENAME = "md/03a_draft.md"

CLAUDE_MODEL = "claude-opus-4-7"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_narrative_architectures() -> str:
    return load_style_guide("narrative_architectures.md")


def _extract_topic_from_research(research_content: str) -> str:
    for line in research_content.splitlines():
        line = line.strip()
        if line.startswith("# Verified Research:"):
            return line[len("# Verified Research:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _load_materials_insights(slug: str) -> str | None:
    try:
        return read_output(slug, MATERIALS_FILENAME)
    except FileNotFoundError:
        return None


def _build_prompt(
    style_guide: str,
    narrative_architectures: str,
    research_content: str,
    materials_insights: str | None = None,
) -> str:
    materials_section = ""
    if materials_insights:
        materials_section = f"\n## Book Insights (Trusted Source — Do Not Verify)\n{materials_insights}\n"

    return f"""\
You are a professional YouTube scriptwriter for a psychology channel.

## Style Guide (follow this exactly)
{style_guide}

## Narrative Architectures (follow this exactly)
{narrative_architectures}

## Verified Research (your content source)
{research_content}
{materials_section}
## Your Task
Write a complete video narration script on the topic covered in the Verified Research above.

Requirements:
- Target length: ~1,850 words (approximately 14 minutes at 130 wpm) — the bump from the older ~1,700 target absorbs the mandatory Permission Practice section described below.
- Read the Narrative Architectures document above. Choose the single architecture that best fits this topic and research. Declare your choice on the FIRST LINE of your script:
  ARCHITECTURE: [Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit]
  Then write the script following that architecture's entry point, required content nodes, and close constraint. Treat the architecture as a shape, not a rigid template.
- Avoid all banned phrases and structural patterns listed in the Narrative Architectures document.
- Use [Visual Pause] on its own line (maximum 3–4 times per script) at moments that require silence for impact.

**Mandatory Permission Practice closing section.** Every script — regardless of architecture — must include a Permission Practice section AFTER the architecture body and BEFORE the final recognition close. This is the channel's locked structural rule.

- Header template: *"Four things you can [verb], when [trigger phrase tied to the script's specific mechanism]:"*
  - verb varies: do / try / notice / give yourself / carry with you
  - trigger phrase ties to the script's phenomenon — e.g. *"...when the avoidance hits"*, *"...when this lands in your body"*, *"...when the shame starts"*, *"...when the loop begins"*
- Exactly **4 numbered items**. Not 3. Not 5. Always 4.
- Each item = one declarative line + one short unpack line. Roughly 15–35 words per item.
- Voice = **embodied micro-practice**: somatic acts (breathing, hand placement, posture), noticing (locating sensation in the body), naming (saying one word out loud), micro-thresholds (write the first sentence, then stop). The tips are *practices*, not *advice*.
- **Forbidden tip kinds** (these break the channel):
  - Scheduling tips ("set a time", "block your calendar")
  - List-making tips ("write down 3 things…")
  - Optimization tips ("be more productive", "stop overthinking")
  - Generic self-help tips ("talk to a therapist", "set boundaries", "communicate clearly")
  - Homework framing ("this week, try…", "your assignment is…")
  - Anything that could appear unchanged on a productivity blog
- **Litmus test for each tip:** Could this line appear word-for-word on a productivity blog or in a generic self-help thread? If yes — wrong. Rewrite as a somatic, noticing, or micro-threshold act.
- All existing voice rules still apply inside this section: no researcher names, no "studies show", no decimals, round numbers only, plain language first.

**Then write the recognition close after the section.** The tips are a beat, not the destination. The FINAL line of the script must still land on implication / recognition — never on a tip and never on a "go do this" instruction. The architecture's close constraint still governs the recognition beat; the Permission Practice section sits one beat before it.

**Voice — warm therapist talking to one person.** You sit across from the viewer. You validate the feeling before explaining the mechanism. You don't perform expertise; you offer recognition.

**Research is invisible.** You read research; the script never references it. NO research-framing language in any form — no "researchers found", no "studies show", no "scientists discovered", no "neuroscience has found", no "one study", no "a meta-analysis", no "research shows", no "the data shows", no "the science is clear", no "psychologists call this", no "in [year]" introducing a study. The findings appear as observations about being human, spoken in the speaker's own voice. The viewer trusts the speaker, not the citation. Real bibliographic citations live in the YouTube description (Agent 8), never here.

**Plain language first.** Describe the phenomenon in everyday words. Name a scientific term only if (a) the name itself is genuinely memorable, and (b) it appears once, late, after the idea has already landed in plain words. Default to no name. NEVER use the jargon-then-translation pattern ("ego depletion — the depletion of…") — it reads like a lecture.

**No numbers as findings.** No decimals, no effect sizes (d = X, r = X), no p-values, no study counts ("94 experiments"), no participant counts ("8,000 people"), no methodology terms (pre-registered, double-blind, longitudinal, meta-analysis). Round, framed numbers only ("roughly half", "most people", "in many cases"). If a number doesn't land emotionally as plain English, cut it.

**Confident speaker voice.** Replace hedging ("might", "perhaps", "could be") with direct claims spoken by the speaker — not by citing research. "Your brain does X" beats "Research shows your brain does X".

- Use metaphors and analogies — one strong metaphor per scientific concept
- ONLY use claims from the Verified Claims section of the research (NOT flagged or removed claims)
- Write in second person ("you", "your") throughout
- Short punchy sentences. Fragments for emphasis.
- Do NOT include any [IMAGE: ...] markers — a dedicated visual agent (Agent 5) handles image prompts separately.
"""


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, script_text: str) -> str:
    today = date.today().isoformat()
    return (
        f"# Script Draft: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Pass: 1 of 3 (Draft)\n"
        f"Estimated duration: ~14 min (~1,850 words)\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{script_text}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent3a_draft.py \"<slug>\"")
        print("Example: python tools/agent3a_draft.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 3a: Script Draft (Pass 1/3) ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Load style guides
    print("[1/4] Loading style guides...")
    try:
        style_guide = load_style_guide()
        narrative_architectures = _load_narrative_architectures()
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    print(f"  Style guide loaded ({len(style_guide):,} characters)")
    print(f"  Narrative architectures loaded ({len(narrative_architectures):,} characters)")

    # Step 2 — Read verified research
    print(f"\n[2/4] Reading {RESEARCH_FILENAME}...")
    try:
        research_content = read_output(slug, RESEARCH_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 2 first:")
        print(f'  python tools/agent2_verify.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic_from_research(research_content)
    print(f"  Topic  : {topic}")
    print(f"  Research file length: {len(research_content):,} characters")

    # Step 2b — Load book insights if available
    materials_insights = _load_materials_insights(slug)
    if materials_insights:
        print(f"  Book insights loaded ({len(materials_insights):,} characters)")
    else:
        print(f"  No book insights found (run Agent 0 to add a reference book)")

    # Step 3 — Call Claude
    print(f"\n[3/4] Calling Claude API to write the draft...")
    prompt = _build_prompt(style_guide, narrative_architectures, research_content, materials_insights)

    try:
        script_text, usage = query_claude(prompt, CLAUDE_MODEL, 8192, "script draft")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    print(f"  Draft received ({len(script_text):,} characters)")

    # Extract declared architecture for display
    for line in script_text.splitlines():
        if line.strip().upper().startswith("ARCHITECTURE:"):
            print(f"  {line.strip()}")
            break

    # Step 4 — Save output
    print(f"\n[4/4] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, script_text)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Review the draft, then run Agent 3b:")
    print(f'  python tools/agent3b_critic.py "{slug}"')


if __name__ == "__main__":
    main()
