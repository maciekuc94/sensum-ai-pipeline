"""
Agent 3b: Script Critic (Pass 2 of 3)
Reads the draft from Agent 3a and identifies the single weakest moment —
the place where the argument loses momentum, a transition feels forced,
or the hook fails to pay off.

Review and optionally edit outputs/[slug]/md/03b_critique.md before running
Agent 3c. You can change the "Suggested Rewrite" section to guide the rewrite
in a different direction.

Usage:
    python tools/agent3b_critic.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRAFT_FILENAME = "md/03a_draft.md"
OUTPUT_FILENAME = "md/03b_critique.md"

CLAUDE_MODEL = "claude-sonnet-4-6"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def _build_prompt(script_text: str) -> str:
    return f"""\
You are a first-time YouTube viewer who clicked on a psychology video and will close the tab the moment it bores you.

Read this script draft carefully. Identify the single weakest moment — where the argument loses momentum, a transition feels forced, the hook fails to pay off, or the viewer is most likely to disengage.

Return ONLY the structured analysis below. No preamble, no additional commentary.

## Weakest Moment
[Quote the exact passage — 1–4 sentences — from the script]

## Why It's Weak
[One sentence explaining the problem from a viewer's perspective]

## Suggested Rewrite
[Your improved version of that passage — match the length and style of the original. This can be edited before the rewrite agent runs.]

---

## Script Draft

{script_text}
"""


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, critique_text: str) -> str:
    today = date.today().isoformat()
    return (
        f"# Script Critique: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Pass: 2 of 3 (Critic)\n"
        f"\n"
        f"_Review this file before running Agent 3c. "
        f"You may edit the 'Suggested Rewrite' section to guide the rewrite in a different direction._\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{critique_text}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent3b_critic.py \"<slug>\"")
        print("Example: python tools/agent3b_critic.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 3b: Script Critic (Pass 2/3) ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Read the draft
    print(f"[1/3] Reading {DRAFT_FILENAME}...")
    try:
        draft_content = read_output(slug, DRAFT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3a first:")
        print(f'  python tools/agent3a_draft.py "{slug}"')
        sys.exit(1)

    # Extract topic from draft header
    topic = "Unknown Topic"
    for line in draft_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Draft:"):
            topic = line[len("# Script Draft:"):].strip()
            break
        if line.startswith("# "):
            topic = line[2:].strip()
            break

    print(f"  Topic : {topic}")
    print(f"  Draft length: {len(draft_content):,} characters")

    # Step 2 — Call Claude for critic analysis
    print(f"\n[2/3] Calling Claude API for critic analysis...")
    prompt = _build_prompt(draft_content)

    try:
        critique_text, usage = query_claude(prompt, CLAUDE_MODEL, 2048, "critic analysis")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    # Display weakest moment for quick review
    for line in critique_text.splitlines():
        if line.strip().startswith("## Weakest Moment"):
            print(f"  Weakest moment identified — see {OUTPUT_FILENAME} for details")
            break

    # Step 3 — Save output
    print(f"\n[3/3] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, critique_text)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Review the critique and optionally edit the 'Suggested Rewrite' section, then run Agent 3c:")
    print(f'  python tools/agent3c_rewrite.py "{slug}"')


if __name__ == "__main__":
    main()
