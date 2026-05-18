"""
pipeline.py — YouTube Psychology content pipeline runner.

Usage:
    python pipeline.py "emotional dysregulation in ADHD"
    python pipeline.py "topic" --continue-on-error
    python pipeline.py "topic" --no-pause       # headless: skip pauses + optional steps
    python pipeline.py                           # prompts for topic

Flow:
    Steps 0–6  →  [PAUSE: review script + image prompts]
    Step 7 (optional TTS)  →  Step 8  →  [PAUSE: approve image generation]
    Step 9
"""

import argparse
import subprocess
import sys
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tools.utils import make_slug

TOOLS = Path(__file__).parent / "tools"

# Set by main() from CLI flags; consulted by run/pause/approve.
_OPTIONS = {"continue_on_error": False, "no_pause": False, "serial": False}


def run(cmd: list[str], step_label: str) -> int:
    code = subprocess.run(cmd, cwd=Path(__file__).parent).returncode
    if code != 0:
        print(f"  {step_label} failed (exit code {code}).")
        if not _OPTIONS["continue_on_error"]:
            sys.exit(code)
    return code


def _run_step(cmd: list[str], step_label: str) -> tuple[str, int]:
    """Subprocess wrapper for parallel execution. Returns (label, exit_code)."""
    print(f"  [parallel] {step_label} starting...")
    code = subprocess.run(cmd, cwd=Path(__file__).parent).returncode
    print(f"  [parallel] {step_label} finished (exit {code}).")
    return step_label, code


def pause(message: str) -> None:
    print(f"\n{'━' * 60}")
    print(f"  {message}")
    print(f"{'━' * 60}")
    if _OPTIONS["no_pause"]:
        print("  [--no-pause: skipping]")
        return
    try:
        input("  Press Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)


def approve(prompt: str) -> bool:
    if _OPTIONS["no_pause"]:
        # Headless runs never silently approve a paid/destructive step.
        print(f"\n  {prompt} [--no-pause: declining]")
        return False
    try:
        answer = input(f"\n  {prompt} [y/N] ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)
    return answer in ("y", "yes")


def step_header(number: str, label: str) -> None:
    print(f"\n{'─' * 60}")
    print(f"  STEP {number}: {label}")
    print(f"{'─' * 60}")


def output_note(path: str) -> None:
    print(f"  → {path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the YouTube psychology content pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "topic",
        nargs="*",
        help="Video topic (joined into a single string). If omitted, prompts interactively.",
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue running subsequent steps even if one fails. Default: halt on first failure.",
    )
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Skip all interactive pauses and decline optional steps. For headless/CI runs.",
    )
    parser.add_argument(
        "--serial",
        action="store_true",
        help="Run steps 5/6/8 serially (debug). Default: parallel via thread pool.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _OPTIONS["continue_on_error"] = args.continue_on_error
    _OPTIONS["no_pause"] = args.no_pause
    _OPTIONS["serial"] = args.serial

    if args.topic:
        topic = " ".join(args.topic)
    else:
        if _OPTIONS["no_pause"]:
            print("Error: --no-pause requires a topic argument (no interactive prompt).")
            sys.exit(1)
        topic = input("Topic: ").strip()
        if not topic:
            print("No topic provided. Exiting.")
            sys.exit(1)

    slug = make_slug(topic)
    out = f"outputs/{slug}"

    print(f"\n  Topic : {topic}")
    print(f"  Slug  : {slug}")

    # -----------------------------------------------------------------------
    # STEP 0 — Materials (optional)
    # -----------------------------------------------------------------------
    step_header("0", "Materials — extract insights from a reference PDF (optional)")
    if approve("Reference PDF?"):
        pdf_path = input("  PDF path: ").strip()
        if pdf_path:
            run(
                [sys.executable, str(TOOLS / "agent0_materials.py"),
                 "--topic", topic, "--pdf", pdf_path],
                "Step 0",
            )
            output_note(f"{out}/md/00_materials_insights.md")
        else:
            print("  No path — skipping.")
    else:
        print("  Skipping.")

    # -----------------------------------------------------------------------
    # STEP 1 — Research
    # -----------------------------------------------------------------------
    step_header("1", "Research — Gemini 2.5 Pro + PubMed")
    run([sys.executable, str(TOOLS / "agent1_research.py"), topic], "Step 1")
    output_note(f"{out}/md/01_research.md")

    # -----------------------------------------------------------------------
    # STEP 2 — Verify
    # -----------------------------------------------------------------------
    step_header("2", "Verify — Gemini classifies every claim: VERIFIED / FLAGGED / REMOVED")
    run([sys.executable, str(TOOLS / "agent2_verify.py"), slug], "Step 2")
    output_note(f"{out}/md/02_verified_research.md")

    # -----------------------------------------------------------------------
    # STEP 3 — Script (3a → 3n → 3b → 3c)
    # -----------------------------------------------------------------------
    step_header("3", "Script — Claude Opus writes ~1,700-word narration (3-pass)")
    run([sys.executable, str(TOOLS / "agent3.py"), slug], "Step 3")
    output_note(f"{out}/md/03_script_draft.md")

    # -----------------------------------------------------------------------
    # STEP 4 — Edit + Hook gate
    # -----------------------------------------------------------------------
    step_header("4", "Edit — copy-edit for speech flow and active voice")
    run([sys.executable, str(TOOLS / "agent4a_edit.py"), slug], "Step 4")
    output_note(f"{out}/md/04_script_final.md")

    step_header("4b", "Hook gate — score opening hook (must reach RECORD before recording)")
    run([sys.executable, str(TOOLS / "agent4b_hook.py"), slug], "Step 4b")
    output_note(f"{out}/md/04b_hook_score.md")

    # -----------------------------------------------------------------------
    # STEPS 5, 6, 8 — Visuals, Narration, Publish Package
    # 5 and 6 are independent (both read 04_script_final.md).
    # 8 depends on 6's output (06_script_narration.md), so it starts after 6 finishes.
    # All three share a single thread pool so 5 can keep running while 8 takes over from 6.
    # -----------------------------------------------------------------------
    cmd5 = [sys.executable, str(TOOLS / "agent5_visuals.py"), slug]
    cmd6 = [sys.executable, str(TOOLS / "agent6_narration.py"), slug]
    cmd8 = [sys.executable, str(TOOLS / "agent8_publish.py"), slug]

    if _OPTIONS["serial"]:
        step_header("5", "Visuals — generate production-ready image prompts")
        run(cmd5, "Step 5")
        output_note(f"{out}/md/05_image_prompts.md")

        step_header("6", "Narration — strip markers for clean teleprompter script")
        run(cmd6, "Step 6")
        output_note(f"{out}/md/06_script_narration.md")

        step_header("8", "Publish — titles, hooks, description, chapters, tags, shorts")
        run(cmd8, "Step 8")
        output_note(f"{out}/md/07_publish_package.md")
    else:
        step_header("5/6/8", "Visuals + Narration + Publish — running in parallel (use --serial to disable)")
        results: dict[str, int] = {}
        with ThreadPoolExecutor(max_workers=3) as ex:
            f5 = ex.submit(_run_step, cmd5, "Step 5")
            f6 = ex.submit(_run_step, cmd6, "Step 6")

            def _step8_after_6() -> tuple[str, int]:
                label6, code6 = f6.result()
                if code6 != 0:
                    print(f"  [parallel] Step 8 skipped: {label6} failed (exit {code6}).")
                    return "Step 8", code6
                return _run_step(cmd8, "Step 8")

            f8 = ex.submit(_step8_after_6)

            for fut in (f5, f6, f8):
                label, code = fut.result()
                results[label] = code

        output_note(f"{out}/md/05_image_prompts.md")
        output_note(f"{out}/md/06_script_narration.md")
        output_note(f"{out}/md/07_publish_package.md")

        failed = [(lbl, c) for lbl, c in results.items() if c != 0]
        if failed and not _OPTIONS["continue_on_error"]:
            for lbl, c in failed:
                print(f"  {lbl} failed (exit code {c}).")
            sys.exit(failed[0][1])

    # -----------------------------------------------------------------------
    # PAUSE — review script and image prompts
    # -----------------------------------------------------------------------
    pause(
        "REVIEW GATE\n"
        f"  Script  : {out}/md/06_script_narration.md\n"
        f"  Prompts : {out}/md/05_image_prompts.md\n\n"
        "  Edit 05_image_prompts.md before continuing."
    )

    # -----------------------------------------------------------------------
    # STEP 7 — TTS Voice Reference (optional)
    # -----------------------------------------------------------------------
    step_header("7", "TTS Voice Reference — Gemini Flash pacing reference (optional)")
    if approve("Generate TTS reference audio?"):
        run([sys.executable, str(TOOLS / "agent7_tts.py"), slug], "Step 7")
        output_note(f"{out}/tts/gemini_Puck.wav")
    else:
        print("  Skipping.")

    # -----------------------------------------------------------------------
    # PAUSE — explicit approval before image generation
    # -----------------------------------------------------------------------
    print(f"\n{'━' * 60}")
    print("  IMAGE GENERATION APPROVAL")
    print(f"  Prompts: {out}/md/05_image_prompts.md")
    print(f"{'━' * 60}")
    if not approve("Generate all images now? This costs ~$0.04 per image."):
        print("  Skipping image generation. Run manually:")
        print(f"  python tools/agent9_images.py {slug} --generate")
        print()
        sys.exit(0)

    # -----------------------------------------------------------------------
    # STEP 9 — Generate Images
    # -----------------------------------------------------------------------
    step_header("9", "Generate Images — Gemini 3 Pro Image Preview via Vertex AI")
    run([sys.executable, str(TOOLS / "agent9_images.py"), slug, "--generate"], "Step 9")
    output_note(f"{out}/images/image_001.png … image_NNN.png")

    print(f"\n{'─' * 60}")
    print("  Pipeline complete.")
    print(f"{'─' * 60}\n")


if __name__ == "__main__":
    main()
