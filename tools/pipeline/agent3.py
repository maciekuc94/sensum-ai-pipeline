"""
Agent 3: Script Chain Orchestrator — LEGACY Gemini --api fallback

DEFAULT PATH (since 2026-05-29): the entire script chain — Drafter (3a) AND the
Revisor↔Reviewer loop (3b ↔ 3c) — runs **in-session in Claude Code on Opus 4.8**
via `/draft <slug>`. No Gemini, no Anthropic API. See `.claude/commands/draft.md`
and the prompt specs `workflows/pipeline/03{a,b,c}_*.md`.

This script is kept only as a fallback: it runs the loop via the Gemini 3.1 Pro
API (`agent3b_revisor.py` / `agent3c_reviewer.py`) over an existing
`md/03a_draft.md`, then copies the final revised draft → `md/04_final.md`. Its
`parse_verdict` import from `agent3c_reviewer` is still a shared helper.

Usage (legacy):
    python tools/pipeline/agent3.py "<slug>"
    python tools/pipeline/agent3.py "<slug>" --max-iterations 3
    python tools/pipeline/agent3.py "<slug>" --start-iteration 2   # continue from iter 2
"""

import argparse
import os
import shutil
import subprocess
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_output_dir
from tools.pipeline.agent3c_reviewer import parse_verdict


def _run(label: str, script: str, slug: str, extra_args: list[str] | None = None) -> int:
    python = sys.executable
    cmd = [python, script, slug]
    if extra_args:
        cmd.extend(extra_args)
    print(f"\n{'=' * 60}")
    print(f"Running: {label}")
    print(f"{'=' * 60}")
    result = subprocess.run(cmd)
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent 3 orchestrator (B++ v2): Revisor↔Reviewer loop over an existing 03a_draft.md"
    )
    parser.add_argument("slug", help="Output directory slug")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Max Revisor↔Reviewer iterations (default 5)",
    )
    parser.add_argument(
        "--start-iteration",
        type=int,
        default=1,
        help="Start loop from this iteration (default 1). Use to continue an existing run.",
    )
    args = parser.parse_args()

    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)
    if args.max_iterations < 1:
        print("Error: --max-iterations must be >= 1")
        sys.exit(1)
    if args.start_iteration < 1:
        print("Error: --start-iteration must be >= 1")
        sys.exit(1)
    if args.start_iteration > args.max_iterations:
        print("Error: --start-iteration cannot exceed --max-iterations")
        sys.exit(1)

    # Pre-check: draft must exist before the loop can run.
    draft_path = get_output_dir(slug) / "md" / "03a_draft.md"
    if not draft_path.exists():
        print(f"Error: md/03a_draft.md not found at {draft_path}")
        print()
        print("The Drafter (3a) is no longer run by this script. Generate the draft first:")
        print(f'  In Claude Code, run:  /draft {slug}')
        print()
        print("Or write md/03a_draft.md manually following workflows/pipeline/03a_drafter.md")
        sys.exit(1)

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    revisor = os.path.join(tools_dir, "agent3b_revisor.py")
    reviewer = os.path.join(tools_dir, "agent3c_reviewer.py")

    print(f"\n=== Agent 3: Revisor↔Reviewer Loop (LEGACY Gemini --api fallback) ===")
    print(f"Slug           : {slug}")
    print(f"Max iterations : {args.max_iterations}")
    print(f"Start iteration: {args.start_iteration}")
    print(f"Draft input    : {draft_path}")

    # Revisor↔Reviewer loop (Gemini 3.1 Pro)
    final_verdict = "UNKNOWN"
    iterations_used = 0

    for iteration in range(args.start_iteration, args.max_iterations + 1):
        iterations_used = iteration

        # Revisor pass
        rc = _run(
            f"Agent 3b — Revisor (Gemini, iteration {iteration})",
            revisor,
            slug,
            ["--iteration", str(iteration)],
        )
        if rc != 0:
            print(f"\nChain stopped: 3b iter {iteration} failed (exit code {rc}).")
            sys.exit(rc)

        # Reviewer pass
        rc = _run(
            f"Agent 3c — Reviewer (Gemini, iteration {iteration})",
            reviewer,
            slug,
            ["--iteration", str(iteration)],
        )
        if rc != 0:
            print(f"\nChain stopped: 3c iter {iteration} failed (exit code {rc}).")
            sys.exit(rc)

        # Read verdict
        review_content = read_output(slug, f"md/03c_review_iter{iteration}.md")
        final_verdict = parse_verdict(review_content)
        print(f"\n[Loop control] Iteration {iteration} verdict: {final_verdict}")

        if final_verdict == "PASS":
            print(f"[Loop control] PASS — exiting loop after iteration {iteration}")
            break
        elif final_verdict == "FLAG" and iteration < args.max_iterations:
            print(f"[Loop control] FLAG — restarting Revisor with reviewer feedback")
            continue
        else:
            # FLAG at max iterations or UNKNOWN verdict
            break

    # Finalize: copy revised draft → final
    print(f"\n{'=' * 60}")
    print(f"Finalizing: copy md/03b_revised_iter{iterations_used}.md → md/04_final.md")
    print(f"{'=' * 60}")

    output_dir = get_output_dir(slug)
    src = output_dir / "md" / f"03b_revised_iter{iterations_used}.md"
    dst = output_dir / "md" / "04_final.md"

    if not src.exists():
        print(f"Error: source file does not exist: {src}")
        sys.exit(1)

    shutil.copy(src, dst)
    print(f"Copied: {dst}")

    # If verdict was FLAG at max iter, prepend warning to 04_final.md
    if final_verdict != "PASS":
        warning_header = (
            f"# WARNING: Script shipped after {iterations_used} Reviewer iteration(s) "
            f"with verdict {final_verdict}\n"
            f"# Review md/03c_review_iter{iterations_used}.md for unresolved issues before recording voiceover.\n"
            f"# Generated: {date.today().isoformat()}\n\n"
        )
        existing = dst.read_text(encoding="utf-8")
        dst.write_text(warning_header + existing, encoding="utf-8")
        print(f"\n[Warning] Prepended ship warning to 04_final.md")
        print(f"          Final verdict: {final_verdict} after {iterations_used} iteration(s)")
    else:
        print(f"\n[Success] Final verdict: PASS after {iterations_used} iteration(s)")

    print(f"\nDone. Next: the hook gate (in-session):")
    print(f'  /hook {slug}')


if __name__ == "__main__":
    main()
