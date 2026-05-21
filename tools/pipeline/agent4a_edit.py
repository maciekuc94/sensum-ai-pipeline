"""
Agent 4a: Script Editing
Reads the script draft produced by Agent 3 and uses the Anthropic Claude API
to perform stylistic copy-editing, producing a polished, production-ready
narration script.

Usage:
    python tools/agent4a_edit.py "emotional-dysregulation-in-adhd"

Takes the SLUG (not the topic) because the script draft was already written
by Agent 3.
"""

import sys
import os
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env, load_style_guide, query_claude

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/03_script_draft.md"
OUTPUT_FILENAME = "md/04_script_final.md"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------



def _load_narrative_architectures() -> str:
    """Load the narrative architectures SOP from workflows/narrative_architectures.md."""
    return load_style_guide("narrative_architectures.md")


def _extract_topic_from_script(script_content: str) -> str:
    """Extract the topic from the first heading of the script draft file."""
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Draft:"):
            return line[len("# Script Draft:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _build_prompt(style_guide: str, narrative_architectures: str, script_content: str) -> str:
    """Build the editing prompt for Claude."""
    return f"""\
You are a professional script editor for a YouTube psychology channel.

## Style Guide (the rules you are enforcing)
{style_guide}

## Narrative Architectures (banned phrases and structural rules you are enforcing)
{narrative_architectures}

## Script Draft (what you are editing)
{script_content}

## Your Task
Edit the script draft above so it reads naturally when spoken aloud and fully
complies with the style guide. You are a copy editor — you improve prose
quality, flow, rhythm, and word choice. You do NOT alter scientific claims.

### Editing Rules

1. **Natural speech flow** — Cut or rewrite any sentence that sounds academic,
   passive, or hedging. Every line must sound like a warm therapist talking
   to one person. The viewer trusts the speaker, not the citation.

2. **Plain language first, never jargon-then-translation** — If the draft
   introduces a scientific term and then translates it ("ego depletion — the
   depletion of..."), REWRITE so the plain language leads. Strip the term
   entirely unless the name itself is genuinely memorable. If you keep the
   term, place it once, late, after the everyday description has landed. Never
   set up a term just to translate it.

3. **Research is invisible — strip all research-framing language.** Scan for
   and rewrite/cut every instance of: "researchers found", "studies show",
   "scientists discovered", "research shows", "neuroscience has found",
   "one study", "a recent study", "a 2019 study", "a meta-analysis",
   "across N studies", "the data shows", "according to research", "the science
   is clear", "psychologists call this", "neuroscientists call this", "in
   [year]" introducing a study. Replace with direct claims in the speaker's
   own voice — not by substituting a different research-framing phrase. The
   replacement is absence, not another citation. Example: "Research shows
   your brain does X" → "Your brain does X". Add an [EDITOR NOTE] for each
   substantial rewrite.

4. **No numbers as findings** — Scan for and rewrite: decimals (0.62), effect
   sizes (d = X, r = X), p-values, study counts ("94 experiments"),
   participant counts ("8,000 people"), methodology terms (pre-registered,
   double-blind, longitudinal, meta-analysis), statistical notation of any
   kind. Replace with round, framed numbers ("roughly half", "most people",
   "in many cases") or cut entirely. If a number doesn't land emotionally as
   plain English, cut it.

5. **Sentence variety** — Mix short punchy sentences with fragments for emphasis.
   Break up any long or complex sentences.

6. **No passive voice** — Rewrite every passive construction in active voice and
   flag it.

7. **No hedging — replace with direct claims, not research framing** — Replace
   "might", "perhaps", "could be", "some studies suggest" with direct claims
   in the speaker's own voice. "Your brain does X" beats "Research shows your
   brain does X". DO NOT substitute hedging with research-framing phrases.

8. **Emotional arc** — Validate the feeling before explaining the mechanism.
   The viewer should recognize themselves before any explanation begins. If a
   section explains before validating, fix it and note the change.

9. **Scientific claims** — Do NOT alter, soften, or strengthen any scientific
   claim. Your job is prose only. If you notice a factual concern, note it in
   an EDITOR NOTE but leave the claim unchanged.

10. **Banned phrase removal** — Scan the entire script for any phrase, opener, or
    structural pattern listed in the Narrative Architectures document's banned
    list (including the banned research-framing language section). If found,
    rewrite or remove it while keeping the meaning intact. Always add an
    [EDITOR NOTE] explaining the removal.

### Inline Change Notation

Mark every significant change with an inline note immediately after the changed
text, using this exact format:

    [EDITOR NOTE: changed "original text" to "new text" — reason: brief reason]

Use EDITOR NOTEs for:
- Rewritten sentences (passive → active, hedging → confident, academic → conversational)
- Added plain-language explanations for jargon
- Structural moves (if you reorder sentences within a paragraph)
- Removed throat-clearing or filler phrases

Do NOT add EDITOR NOTEs for trivial punctuation fixes or minor word swaps that
do not change meaning.

### What to Return

Return the **complete edited script** — not a summary, not a diff, not a list of
changes. The full script, from the first line to the last, with EDITOR NOTEs
inline where changes were made.

Do not add any preamble or closing commentary outside the script itself.
"""


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------


CLAUDE_MODEL = "claude-sonnet-4-6"


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, edited_script_text: str) -> str:
    """Wrap the edited script with metadata header."""
    today = date.today().isoformat()
    return (
        f"# Script Final: {topic}\n"
        f"Generated: {today}\n"
        f"Model: {CLAUDE_MODEL}\n"
        f"Editor notes are inline as [EDITOR NOTE: ...]\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{edited_script_text}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/agent4a_edit.py \"<slug>\"")
        print("Example: python tools/agent4a_edit.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 4a: Script Editing ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Load the style guides
    print("[1/4] Loading style guides...")
    try:
        style_guide = load_style_guide()
        narrative_architectures = _load_narrative_architectures()
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    print(f"  Style guide loaded ({len(style_guide):,} characters)")
    print(f"  Narrative architectures loaded ({len(narrative_architectures):,} characters)")

    # Step 2 — Read the script draft
    print(f"\n[2/4] Reading {SCRIPT_FILENAME}...")
    try:
        script_content = read_output(slug, SCRIPT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 3 first:")
        print(f'  python tools/agent3.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic_from_script(script_content)
    print(f"  Topic  : {topic}")
    print(f"  Script file length: {len(script_content):,} characters")

    # Step 3 — Build prompt and call Claude
    print(f"\n[3/4] Calling Claude API to edit the script...")
    prompt = _build_prompt(style_guide, narrative_architectures, script_content)

    try:
        edited_script_text, usage = query_claude(prompt, CLAUDE_MODEL, 8192, "script editing")
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    print(f"  Edited script received ({len(edited_script_text):,} characters)")

    # Step 4 — Save output
    print(f"\n[4/4] Saving output to {OUTPUT_FILENAME}...")
    content = build_output(topic, edited_script_text)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Review the final script, then run Agent 4b (hook scorer) and Agent 5/6:")
    print(f'  python tools/agent4b_hook.py "{slug}"')
    print(f'  python tools/agent5_visuals.py "{slug}"')
    print(f'  python tools/agent6_narration.py "{slug}"')


if __name__ == "__main__":
    main()
