"""Offline smoke test for agent4b_hook.py helpers — no API calls.

Validates:
  - _find_narration_start skips metadata + ARCHITECTURE line correctly.
  - _extract_15s_window returns clean narration words (no markers, no headers).
  - _splice_first_37_words replaces only the first sentences ~37 words long
    and leaves the rest byte-identical.

Run from the project root:
    python tests/test_agent4b_smoke.py
"""

import sys
import os
from pathlib import Path

# Make tools/ importable
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.agent4b_hook import (  # noqa: E402
    _find_narration_start,
    _extract_15s_window,
    _extract_30s_window,
    _splice_first_37_words,
    _word_count,
    WORDS_15S,
)


SAMPLE_SLUG = "why-you-can-t-just-relax-on-weekends"
SAMPLE_PATH = ROOT / "outputs" / SAMPLE_SLUG / "md" / "04_script_final.md"


def assert_eq(label: str, actual, expected) -> None:
    if actual != expected:
        print(f"  FAIL [{label}]")
        print(f"    expected: {expected!r}")
        print(f"    actual  : {actual!r}")
        sys.exit(1)
    print(f"  pass [{label}]")


def assert_true(label: str, cond: bool, hint: str = "") -> None:
    if not cond:
        print(f"  FAIL [{label}] {hint}")
        sys.exit(1)
    print(f"  pass [{label}]")


def main() -> None:
    if not SAMPLE_PATH.exists():
        print(f"Sample script not found: {SAMPLE_PATH}")
        sys.exit(1)

    script = SAMPLE_PATH.read_text(encoding="utf-8")

    print("\n[A] _find_narration_start")
    start = _find_narration_start(script)
    head = script[start : start + 80]
    assert_true(
        "skips '# Script Final:' headings",
        not head.lstrip().startswith("#"),
        hint=f"head={head!r}",
    )
    assert_true(
        "skips ARCHITECTURE: line",
        "ARCHITECTURE:" not in head.split("\n")[0],
        hint=f"first line at start: {head.split(chr(10))[0]!r}",
    )
    assert_true(
        "first narration word is 'Friday'",
        head.lstrip().startswith("Friday"),
        hint=f"head={head!r}",
    )

    print("\n[B] _extract_15s_window")
    hook15 = _extract_15s_window(script)
    wc15 = _word_count(hook15)
    print(f"  ({wc15} words)")
    print(f"  -> {hook15!r}")
    assert_true(
        "15s window word count between 30 and 40",
        30 <= wc15 <= 40,
        hint=f"wc15={wc15}",
    )
    assert_true(
        "no editor-note markers in window",
        "[EDITOR NOTE" not in hook15 and "[IMAGE" not in hook15,
    )
    assert_true(
        "no ARCHITECTURE: in window",
        "ARCHITECTURE" not in hook15,
    )

    print("\n[C] _extract_30s_window")
    hook30 = _extract_30s_window(script)
    wc30 = _word_count(hook30)
    print(f"  ({wc30} words)")
    assert_true(
        "30s window word count between 150 and 210",
        150 <= wc30 <= 210,
        hint=f"wc30={wc30}",
    )

    print("\n[D] _splice_first_37_words — byte preservation")
    new_opening = (
        "Saturday morning. Your jaw locks before your eyes open. "
        "The migraine arrives like clockwork. You assume the flu. "
        "It is not the flu. It is something stranger, and your body has been "
        "rehearsing this for five days."
    )
    new_wc = _word_count(new_opening)
    assert_true(f"test opening fits 37-word budget ({new_wc}<=37)", new_wc <= 37)

    spliced = _splice_first_37_words(script, new_opening)

    # Header preserved verbatim
    start_after = _find_narration_start(spliced)
    original_header = script[:_find_narration_start(script)]
    spliced_header = spliced[:start_after]
    assert_eq("metadata header preserved exactly", spliced_header, original_header)

    # Body tail (after the splice region) must appear verbatim in the spliced output
    # Pick a distinctive sentence from later in the script:
    tail_anchor = "weekend sickness"
    assert_true(
        "distinctive body sentence still present",
        tail_anchor in spliced,
        hint=f"{tail_anchor!r} missing after splice",
    )

    # New opening should appear in spliced (sans normalization of trailing period)
    assert_true(
        "new opening present in spliced output",
        new_opening.split(".")[0] in spliced,
    )

    # The original first sentence should be gone FROM THE OPENING (it appears
    # later in the body too, so we check only the first narration segment).
    spliced_opening = spliced[start_after : start_after + 200]
    assert_true(
        "original 'Friday at 5 PM' is replaced at the opening",
        "Friday at 5 PM" not in spliced_opening,
        hint=f"opening: {spliced_opening!r}",
    )

    # The rest of the script (a chunk past the hook) should be byte-identical
    # Take a 500-char slice starting at the well-known 'For vacations,' anchor:
    anchor = "For vacations,"
    if anchor in script and anchor in spliced:
        orig_slice = script[script.index(anchor) : script.index(anchor) + 500]
        spliced_slice = spliced[spliced.index(anchor) : spliced.index(anchor) + 500]
        assert_eq("500-byte tail slice after anchor matches", spliced_slice, orig_slice)
    else:
        print(f"  skip [tail-slice anchor not found: {anchor!r}]")

    print("\nAll smoke checks passed.")


if __name__ == "__main__":
    main()
