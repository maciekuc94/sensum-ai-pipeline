"""
Agent 5: Visual Storytelling — post-processing only (no LLM API)

Image prompts are generated IN-SESSION in Claude Code on Opus 4.8 via the
`/visuals <slug>` slash command — no Gemini, no Anthropic API. This script does
only the deterministic work:

  --expand          Inject CHARACTER_DESCRIPTION + STYLE_SUFFIX constants into the
                    compact **Visual:** fields of 05_prompts.md, rebuild phrase files.
  --extract         Extract docx/script_corrected.docx → md/script_corrected.md.
                    Called automatically by the /visuals skill when script_corrected.docx exists.
                    (Extraction only — no API.)

Usage:
    /visuals <slug>                                                  # generate compact prompts in-session
    python tools/pipeline/agent5_visuals.py "<slug>" --expand        # assemble full Imagen prompts
    python tools/pipeline/agent5_visuals.py "<slug>" --extract       # extract script_corrected.docx → .md
"""

import sys
import os
import json
import re
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, export_to_docx, get_output_dir, read_script_docx_text, CHARACTER_DESCRIPTION, STYLE_SUFFIX

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/04_final.md"
OUTPUT_FILENAME = "md/05_prompts.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _extract_topic_from_script(script_content: str) -> str:
    """Extract the topic from the first heading of the final script file."""
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Final:"):
            return line[len("# Script Final:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _clean_script(script_content: str) -> str:
    """Strip metadata and EDITOR NOTEs, return clean narration text.

    [Visual Pause] markers are PRESERVED — they are emotional-arc signals for the visual director.
    """
    text = script_content
    text = re.sub(r'\[EDITOR NOTE:[^\]]+\]', '', text)
    text = re.sub(r'\[IMAGE:[^\]]+\]', '', text)
    text = re.sub(r'^#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^---.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^(Generated:|Model:|Pass:|Estimated duration:|Editor notes).*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _build_imagen_prompt(visual: str, include_figure: bool = True) -> str:
    """Assemble the full Imagen prompt from a visual description.

    Prepends CHARACTER_DESCRIPTION only when the scene includes the faceless figure.
    When include_figure is False, the visual stands alone as object/environment/diagram.
    """
    if include_figure:
        return CHARACTER_DESCRIPTION + ". " + visual.strip() + ", " + STYLE_SUFFIX
    return visual.strip() + ", " + STYLE_SUFFIX


def _build_phrases_file(topic: str, items: list[dict]) -> str:
    """Build 05_phrases.md — a simple table mapping image number to narration phrase."""
    lines = [
        f"# Image Phrases: {topic}",
        "",
        "| # | Phrase |",
        "|---|--------|",
    ]
    for i, item in enumerate(items, start=1):
        phrase = item["sentence"].strip().replace('"', '"').replace('"', '"')
        lines.append(f'| {i:03d} | "{phrase}" |')
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Expand mode — post-process compact prompts file (no API call)
# ---------------------------------------------------------------------------


def _expand_mode(slug: str) -> None:
    """Expand **Visual:** fields in compact 05_prompts.md into full **Imagen prompt:** entries.

    Called either by --expand flag or automatically when a compact file is detected.
    Also rebuilds 05_phrases.md and exports 05_phrases.docx.
    """
    print(f"\n=== Agent 5: Expand Imagen Prompts ===")
    print(f"Slug: {slug}\n")

    try:
        content = read_output(slug, OUTPUT_FILENAME)
    except FileNotFoundError:
        print(f"Error: {OUTPUT_FILENAME} not found. Run /visuals {slug} first.")
        sys.exit(1)

    if "**Visual:**" not in content:
        if "**Imagen prompt:**" in content:
            print("Already expanded (no **Visual:** fields found). Nothing to do.")
            return
        print("Error: No **Visual:** or **Imagen prompt:** fields found.")
        print("The file may be corrupted. Delete it and re-run /visuals.")
        sys.exit(1)

    items: list[dict] = []

    def _replacer(m: re.Match) -> str:
        figure_str = m.group(2).strip().lower()
        sentence_line = m.group(3)
        sentence_raw = m.group(4).strip()
        visual_text = m.group(5).strip()
        include_figure = figure_str == "yes"
        # Strip outer quote pair for the phrase table (keep sentence_line intact for the prompts file)
        sentence_clean = sentence_raw
        if len(sentence_clean) >= 2 and sentence_clean[0] in ('"', '“') and sentence_clean[-1] in ('"', '”'):
            sentence_clean = sentence_clean[1:-1]
        items.append({"sentence": sentence_clean, "include_figure": include_figure})
        imagen_prompt = _build_imagen_prompt(visual_text, include_figure)
        return (
            f"**Figure:** {figure_str}\n"
            f"{sentence_line}\n"
            f"**Imagen prompt:**\n{imagen_prompt}"
        )

    # Match Figure + Sentence + Visual block, stopping at the next separator or image header
    pattern = re.compile(
        r'(\*\*Figure:\*\*\s*(yes|no))\n'
        r'(\*\*Sentence:\*\*\s*(.+?))\n'
        r'\*\*Visual:\*\*\n(.*?)(?=\n\n---|\n\n## Image|\Z)',
        re.DOTALL | re.IGNORECASE,
    )

    expanded = pattern.sub(_replacer, content)

    if not items:
        print("Error: Pattern matched no entries. Check the compact file format.")
        sys.exit(1)

    # Update the review note in the header
    expanded = expanded.replace(
        "Review and edit these prompts before expanding. Run --expand to assemble full Imagen prompts.",
        "Review and edit these prompts before generating. Each prompt feeds directly into Vertex AI Imagen.",
    )

    output_path = write_output(slug, OUTPUT_FILENAME, expanded)
    print(f"  Expanded {len(items)} image prompts → {output_path}")

    # Rebuild phrase files
    topic = "Unknown Topic"
    for line in expanded.splitlines():
        if line.startswith("# Image Prompts:"):
            topic = line[len("# Image Prompts:"):].strip()
            break

    phrases_content = _build_phrases_file(topic, items)
    phrases_path = write_output(slug, "md/05_phrases.md", phrases_content)
    print(f"  Phrases: {phrases_path}")
    docx_path = export_to_docx(slug, "md/05_phrases.md", "docx/05_phrases.docx")
    print(f"  Word export: {docx_path}")

    print(f"\nDone. Review {OUTPUT_FILENAME}, then run Agent 9:")
    print(f'  PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "{slug}" --generate')


# ---------------------------------------------------------------------------
# NOTE: Image-prompt GENERATION happens in-session in Claude Code on Opus 4.8
# via `/visuals` (prompt source: workflows/pipeline/05_visuals.md). The former
# `_generate_visuals()` Anthropic-API call was removed on 2026-05-29, and the
# legacy architecture / beat-register generation scaffolding (SYSTEM_PROMPT,
# VISUAL_REGISTER_MAPS, _extract_architecture, _build_system_prompt,
# _build_prompts_file) was removed on 2026-06-07 when narrative architectures
# were retired. The `_clean_script` helper above is retained for reference only
# and is no longer invoked by this script.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Agent 5: Visual Storytelling — generate image prompts from script"
    )
    parser.add_argument("slug", help="Output directory slug")
    parser.add_argument(
        "--extract",
        action="store_true",
        help="Extract docx/script_corrected.docx → md/script_corrected.md (called automatically by /visuals skill).",
    )
    parser.add_argument(
        "--expand",
        action="store_true",
        help="Expand **Visual:** fields in existing 05_prompts.md into full Imagen prompts, then rebuild phrase files.",
    )
    args = parser.parse_args()

    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    if args.expand:
        _expand_mode(slug)
        return

    print(f"\n=== Agent 5: Visual Storytelling ===")
    print(f"Slug : {slug}")
    print()

    if args.extract:
        # Extraction only (no LLM). Pull the user-edited body text out of
        # docx/script_corrected.docx → md/script_corrected.md for /visuals.
        docx_path = get_output_dir(slug) / "docx" / "script_corrected.docx"
        if not docx_path.exists():
            print(f"No script_corrected.docx found at {docx_path} — nothing to extract.")
            sys.exit(0)
        text = read_script_docx_text(docx_path)
        out = get_output_dir(slug) / "md" / "script_corrected.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"  Extracted → md/script_corrected.md")
        sys.exit(0)

    # Default path: image prompts are produced in-session by /visuals. This script
    # only assembles them. Check for an existing compact or expanded prompts file.
    prompts_path = get_output_dir(slug) / OUTPUT_FILENAME
    if prompts_path.exists():
        existing_content = prompts_path.read_text(encoding="utf-8")
        if "**Visual:**" in existing_content:
            print("Found compact 05_prompts.md (generated by /visuals). Running --expand...")
            _expand_mode(slug)
            return
        elif "**Imagen prompt:**" in existing_content:
            print("05_prompts.md already expanded. Nothing to do.")
            print(f"Review {OUTPUT_FILENAME} and run Agent 9 when ready:")
            print(f'  PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "{slug}" --generate')
            sys.exit(0)

    print("\nError: md/05_prompts.md not found.")
    print("\nGenerate image prompts via Claude Code slash command (no API cost):")
    print(f"  /visuals {slug}")
    sys.exit(1)


if __name__ == "__main__":
    main()
