"""
Agent 3: Script — Draft → Novelty → Critic → Rewrite
Runs agents 3a → 3n → 3b → 3c in sequence without manual review gates.

Use this for the default path. Run the individual agents (3a/3b/3c) only
when you want to inspect or edit an intermediate file before proceeding.

Usage:
    python tools/agent3.py "emotional-dysregulation-in-adhd"
"""

import sys
import os
import subprocess

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent3.py \"<slug>\"")
        print("Example: python tools/agent3.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    python = sys.executable

    steps = [
        ("3a — Draft",    os.path.join(tools_dir, "agent3a_draft.py")),
        ("3n — Novelty",  os.path.join(tools_dir, "agent3n_novelty.py")),
        ("3b — Critic",   os.path.join(tools_dir, "agent3b_critic.py")),
        ("3c — Rewrite",  os.path.join(tools_dir, "agent3c_rewrite.py")),
    ]

    print(f"\n=== Agent 3: Draft → Novelty → Critic → Rewrite ===")
    print(f"Slug : {slug}\n")

    for label, script in steps:
        print(f"{'=' * 50}")
        result = subprocess.run([python, script, slug])
        if result.returncode != 0:
            print(f"\nChain stopped: {label} failed (exit code {result.returncode}).")
            print(f"Fix the issue, then re-run from that step individually:")
            print(f"  python {os.path.relpath(script)} \"{slug}\"")
            sys.exit(result.returncode)

    print(f"\n{'=' * 50}")
    print(f"\nDone. All four passes complete (3a → 3n → 3b → 3c).")
    print(f"Review md/03_script_draft.md, then run Agent 4a:")
    print(f'  python tools/pipeline/agent4a_edit.py "{slug}"')


if __name__ == "__main__":
    main()
