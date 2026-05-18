"""
Agent 3c: Script Rewrite (Pass 3 of 3)
Reads the draft (Agent 3a) and the critique (Agent 3b) and rewrites only the
weakest section identified by the critic. Returns the complete script with
that section replaced.

Output feeds directly into Agent 4 (edit).

Usage:
    python tools/agent3c_rewrite.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import read_output, write_output, get_env, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DRAFT_FILENAME = "md/03a_draft.md"
CRITIQUE_FILENAME = "md/03b_critique.md"
OUTPUT_FILENAME = "md/03_script_draft.md"

CLAUDE_MODEL = "claude-opus-4-7"

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def _build_prompt(draft_text: str, critique_text: str) -> str:
    return f"""\
You are a professional YouTube scriptwriter. A critic reviewed your script draft and identified one weak section.

Apply the critic's suggested rewrite to replace that section in the original script. Keep everything else exactly as written — do not improve, adjust, or clean up any other part of the script.

Return the complete script with only that section replaced. No commentary, no preamble, no explanation.

## Critic Feedback
{critique_text}

## Original Script Draft
{draft_text}
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
        f"Pass: 3 of 3 (Rewrite applied)\n"
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
        print("Usage: python tools/agent3c_rewrite.py \"<slug>\"")
        print("Example: python tools/agent3c_rewrite.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 3c: Script Rewrite (Pass 3/3) ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Read draft
    print(f"[1/4] Reading {DRAFT_FILENAME}...")
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

    # Step 2 — Read critique
    print(f"\n[2/4] Reading {CRITIQUE_FILENAME}...")
    try:
        critique_content = read_output(slug, CRITIQUE_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3b first:")
        print(f'  python tools/agent3b_critic.py "{slug}"')
        sys.exit(1)

    print(f"  Critique length: {len(critique_content):,} characters")

    # Step 3 — Call Claude to apply the rewrite
    print(f"\n[3/4] Calling Claude API to apply rewrite...")
    prompt = _build_prompt(draft_content, critique_content)

    try:
        script_text, usage = query_claude(prompt, CLAUDE_MODEL, 8192, "rewrite")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    print(f"  Rewritten script received ({len(script_text):,} characters)")

    # Step 4 — Save output
    print(f"\n[4/4] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, script_text)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Review the final script draft, then run Agent 4:")
    print(f'  python tools/agent4a_edit.py "{slug}"')


if __name__ == "__main__":
    main()
