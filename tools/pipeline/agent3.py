"""
Agent 3: Script Chain Orchestrator (B++ v2)
Drafter (3a, Opus) → Revisor↔Reviewer loop (3b/3c, Sonnet, max 2 iter) → copy 03→04

The loop only re-invokes the Revisor — never the Drafter. This caps cost: 1 Opus
call + 2–4 Sonnet calls per script.

Usage:
    python tools/pipeline/agent3.py "<slug>"
    python tools/pipeline/agent3.py "<slug>" --max-iterations 3
    python tools/pipeline/agent3.py "<slug>" --skip-drafter   # start from existing 03a_draft.md
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
        description="Agent 3 orchestrator (B++ v2): Drafter → Revisor↔Reviewer loop"
    )
    parser.add_argument("slug", help="Output directory slug")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=2,
        help="Max Revisor↔Reviewer iterations (default 2)",
    )
    parser.add_argument(
        "--skip-drafter",
        action="store_true",
        help="Skip Agent 3a (use existing md/03a_draft.md as input)",
    )
    args = parser.parse_args()

    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)
    if args.max_iterations < 1:
        print("Error: --max-iterations must be >= 1")
        sys.exit(1)

    tools_dir = os.path.dirname(os.path.abspath(__file__))
    drafter = os.path.join(tools_dir, "agent3a_draft.py")
    revisor = os.path.join(tools_dir, "agent3b_revisor.py")
    reviewer = os.path.join(tools_dir, "agent3c_reviewer.py")

    print(f"\n=== Agent 3: Script Chain (B++ v2) ===")
    print(f"Slug           : {slug}")
    print(f"Max iterations : {args.max_iterations}")
    print(f"Skip drafter   : {args.skip_drafter}")

    # Step 1 — Drafter (Opus, one-shot)
    if not args.skip_drafter:
        rc = _run("Agent 3a — Drafter (Opus 4.7)", drafter, slug)
        if rc != 0:
            print(f"\nChain stopped: 3a failed (exit code {rc}).")
            sys.exit(rc)
    else:
        print("\n[Skipping 3a Drafter — using existing md/03a_draft.md]")

    # Step 2 — Revisor↔Reviewer loop (Sonnet only)
    final_verdict = "UNKNOWN"
    iterations_used = 0

    for iteration in range(1, args.max_iterations + 1):
        iterations_used = iteration

        # Revisor pass
        rc = _run(
            f"Agent 3b — Revisor (Sonnet, iteration {iteration})",
            revisor,
            slug,
            ["--iteration", str(iteration)],
        )
        if rc != 0:
            print(f"\nChain stopped: 3b iter {iteration} failed (exit code {rc}).")
            sys.exit(rc)

        # Reviewer pass
        rc = _run(
            f"Agent 3c — Reviewer (Sonnet, iteration {iteration})",
            reviewer,
            slug,
        )
        if rc != 0:
            print(f"\nChain stopped: 3c iter {iteration} failed (exit code {rc}).")
            sys.exit(rc)

        # Read verdict
        review_content = read_output(slug, "md/03_review.md")
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

    # Step 3 — Finalize: copy revised draft → final
    print(f"\n{'=' * 60}")
    print(f"Finalizing: copy md/03_script_draft.md → md/04_script_final.md")
    print(f"{'=' * 60}")

    output_dir = get_output_dir(slug)
    src = output_dir / "md" / "03_script_draft.md"
    dst = output_dir / "md" / "04_script_final.md"

    if not src.exists():
        print(f"Error: source file does not exist: {src}")
        sys.exit(1)

    shutil.copy(src, dst)
    print(f"Copied: {dst}")

    # Step 4 — If verdict was FLAG at max iter, prepend warning to 04_script_final.md
    if final_verdict != "PASS":
        warning_header = (
            f"# WARNING: Script shipped after {iterations_used} Reviewer iteration(s) "
            f"with verdict {final_verdict}\n"
            f"# Review md/03_review.md for unresolved issues before recording voiceover.\n"
            f"# Generated: {date.today().isoformat()}\n\n"
        )
        existing = dst.read_text(encoding="utf-8")
        dst.write_text(warning_header + existing, encoding="utf-8")
        print(f"\n[Warning] Prepended ship warning to 04_script_final.md")
        print(f"          Final verdict: {final_verdict} after {iterations_used} iteration(s)")
    else:
        print(f"\n[Success] Final verdict: PASS after {iterations_used} iteration(s)")

    print(f"\nDone. Next: agent4b_hook.py")
    print(f'  python tools/pipeline/agent4b_hook.py "{slug}"')


if __name__ == "__main__":
    main()
