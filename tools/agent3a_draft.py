"""
Agent 3a: Script Draft (Pass 1 of 3)
Reads the verified research document produced by Agent 2 and writes a complete
~1,700-word narration script using one of the four narrative architectures.

Review outputs/[slug]/md/03a_draft.md before running Agent 3b.

Usage:
    python tools/agent3a_draft.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
- Target length: ~1,700 words (approximately 13 minutes at 130 wpm)
- Read the Narrative Architectures document above. Choose the single architecture that best fits this topic and research. Declare your choice on the FIRST LINE of your script:
  ARCHITECTURE: [Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit]
  Then write the script following that architecture's entry point, required content nodes, and close constraint. Treat the architecture as a shape, not a rigid template.
- Avoid all banned phrases and structural patterns listed in the Narrative Architectures document.
- Use [Visual Pause] on its own line (maximum 3–4 times per script) at moments that require silence for impact.
- Every scientific term must be immediately followed by a plain-language explanation
- Use metaphors and analogies — one strong metaphor per scientific concept
- ONLY use claims from the Verified Claims section of the research (NOT flagged or removed claims)
- Write in second person ("you", "your") throughout
- Short punchy sentences. Fragments for emphasis. No hedging language.
- No inline citations — never name researchers, authors, or study years (e.g. never "Smith et al. (2020) found" or "a 2019 study by Jones"). Use "researchers found" / "scientists discovered" / "studies show" instead. All citations go in the YouTube description.
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
        f"Estimated duration: ~13 min (~1,700 words)\n"
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
