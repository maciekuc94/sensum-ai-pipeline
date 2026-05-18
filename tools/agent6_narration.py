"""
Agent 6 — Narration Script Generator

Reads outputs/[slug]/04_script_final.md and strips all [IMAGE: ...] markers
and [EDITOR NOTE: ...] inline annotations to produce a clean teleprompter-ready
narration script at outputs/[slug]/06_script_narration.md.

No API calls. Deterministic. Safe to re-run.

Usage:
    python tools/agent6_narration.py "what-porn-does-to-your-brain"
"""

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import export_to_docx


IMAGE_LINE_RE = re.compile(r"^\s*\[IMAGE:[^\]]*\]\s*$")
EDITOR_NOTE_RE = re.compile(r"\s*\[EDITOR NOTE:[^\]]*\]")


def strip_markers(text: str) -> str:
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        if IMAGE_LINE_RE.match(line):
            continue
        line = EDITOR_NOTE_RE.sub("", line)
        cleaned.append(line)

    # Collapse runs of 2+ blank lines to a single blank line
    result = []
    blank_run = 0
    for line in cleaned:
        if line.strip() == "":
            blank_run += 1
            if blank_run <= 1:
                result.append(line)
        else:
            blank_run = 0
            result.append(line)

    return "\n".join(result).strip()


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            # Strip "Script Final: " prefix written by Agent 4
            if title.lower().startswith("script final:"):
                title = title[len("script final:"):].strip()
            return title
    return "Narration Script"


def build_header(title: str) -> str:
    return f"# {title}\n### Narration Script\n\n---"


def word_count(text: str) -> int:
    # Exclude header lines for word count
    lines = [l for l in text.splitlines() if not l.startswith("#") and l.strip() != "---"]
    return len(" ".join(lines).split())


def main(slug: str) -> None:
    base = Path("outputs") / slug
    input_path = base / "md" / "04_script_final.md"
    output_path = base / "md" / "06_script_narration.md"

    if not input_path.exists():
        print(f"Error: {input_path} not found. Run Agent 4 first.")
        sys.exit(1)

    raw = input_path.read_text(encoding="utf-8")
    title = extract_title(raw)

    # Strip front-matter lines (everything up to and including the first ---)
    body_start = raw.find("\n---\n")
    body = raw[body_start + 5:] if body_start != -1 else raw

    cleaned_body = strip_markers(body)
    header = build_header(title)
    output = f"{header}\n\n{cleaned_body}\n"

    output_path.write_text(output, encoding="utf-8")

    docx_path = export_to_docx(slug, "md/06_script_narration.md", "docx/06_script_narration.docx")

    words = word_count(cleaned_body)
    print(f"=== Agent 6: Narration Script ===")
    print(f"Slug  : {slug}")
    print(f"Input : {input_path}")
    print(f"Output: {output_path}")
    print(f"Docx  : {docx_path}")
    print(f"Words : {words}")
    print()
    print("Done. Review the narration script before recording voiceover.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python tools/agent6_narration.py <slug>")
        sys.exit(1)
    main(sys.argv[1])
