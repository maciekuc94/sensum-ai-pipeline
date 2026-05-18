"""
Agent 8: Publish Package
Runs three passes in sequence and produces one master output file:
  1. Titles & Hooks — 5 title options + 2 opening hooks
  2. YouTube Shorts — 5 clip segments (Surprise, Emotion, Standalone, CTA-Hook, Practical Tip)
  3. YouTube Metadata — description, chapters, bibliography, tags (with live autocomplete scraping)

Inputs:
  outputs/{slug}/md/04_script_final.md   (titles + metadata)
  outputs/{slug}/md/06_script_narration.md  (shorts clips)
  outputs/{slug}/md/02_verified_research.md (bibliography)

Outputs:
  outputs/{slug}/md/07_publish_package.md
  outputs/{slug}/docx/07_publish_package.docx

Usage:
    python tools/agent8_publish.py "emotional-dysregulation-in-adhd"
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import export_to_docx, get_env, read_output, write_output, query_claude as _query_claude_base

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCRIPT_FILENAME = "md/04_script_final.md"
NARRATION_FILENAME = "md/06_script_narration.md"
RESEARCH_FILENAME = "md/02_verified_research.md"
OUTPUT_FILENAME = "md/07_publish_package.md"

CLAUDE_MODEL = "claude-sonnet-4-6"

# Per-prompt context budgets for the metadata pass. The pass uses script + research
# as reference for tags/bibliography; full files would balloon the prompt without
# improving output quality. Tuned to stay well under Claude's input window on low-cost runs.
SCRIPT_CONTEXT_CHARS = 6000
RESEARCH_CONTEXT_CHARS = 4000

SHORT_TYPES = [
    ("Surprise",      "A fact that contradicts common belief — stops the scroll"),
    ("Emotion",       "A moment with fear, shame, hope, or identity — hits the viewer personally"),
    ("Standalone",    "An idea complete in itself — full value without watching the main video"),
    ("CTA-Hook",      "An open loop — leaves the viewer wanting the full video"),
    ("Practical Tip", "One concrete thing the viewer can apply right now"),
]

_BRAND_USE = [
    "you may have noticed", "research suggests", "it makes sense that",
    "you're not alone in this", "what we know is", "studies show",
    "many people find", "the science of", "it's completely understandable",
    "let's understand this together", "researchers discovered",
]
_BRAND_AVOID = [
    "hack", "secret", "shocking truth", "you won't believe", "destroy",
    "toxic", "red flags", "wake up", "brutally honest",
    "most people don't know", "this will change everything", "studies PROVE",
]

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _extract_topic(script_content: str) -> str:
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Final:"):
            return line[len("# Script Final:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _query_claude(prompt: str, step_label: str, max_tokens: int = 4096) -> tuple[str, dict]:
    return _query_claude_base(prompt, CLAUDE_MODEL, max_tokens, step_label)


# ---------------------------------------------------------------------------
# Pass 1 — Titles & Hooks
# ---------------------------------------------------------------------------


def _build_titles_prompt(script_content: str) -> str:
    return f"""\
You are a YouTube growth expert for a psychology channel with deep knowledge of what drives clicks and watch time.

Read this video script and generate the following. Be specific to the actual content — do not write generic psychology titles.

5 TITLE OPTIONS:
- Each title must be under 60 characters
- Use curiosity gap, specificity, or emotional tension — pick the strongest angle for each
- Avoid clickbait; every title must be accurate to the script content
- Format: numbered list, title text only (no explanation)

2 ALTERNATIVE OPENING HOOKS:
- Each hook replaces the first 2–4 sentences spoken in the video
- Must immediately address the viewer's pain, curiosity, or a surprising fact
- Do NOT start with "In this video...", "Today we're going to...", or "Welcome back"
- Write for spoken delivery — short punchy sentences, second person ("you"/"your")
- Format: label as "Hook A:" and "Hook B:" followed by the hook text

Return ONLY the titles and hooks. No preamble, no explanation, no commentary after.

## Script

{script_content}
"""


def run_titles_pass(script_content: str) -> str:
    prompt = _build_titles_prompt(script_content)
    text, _ = _query_claude(prompt, "pass 1 — titles and hooks", max_tokens=1024)
    return text


# ---------------------------------------------------------------------------
# Pass 2 — YouTube Shorts (3 sub-passes)
# ---------------------------------------------------------------------------


def _build_shorts_pass1_prompt(narration: str) -> str:
    types_list = "\n".join(f"- {name}: {desc}" for name, desc in SHORT_TYPES)
    return f"""\
You are an expert YouTube Shorts strategist specializing in psychology content.

Read this full narration script and map every passage that could work as a YouTube Short.

The 5 Short types you are mapping candidates for:
{types_list}

For each candidate passage you find:
- Quote the exact lines verbatim (no paraphrasing, no summarising)
- State which Short type(s) it could serve
- Explain in one sentence why it qualifies

Do NOT select winners yet. Your job is to survey the entire script and surface every viable option. Be thorough — it is better to over-identify candidates than to miss a strong one.

## Script

{narration}
"""


def _build_shorts_pass2_prompt(narration: str, analysis: str) -> str:
    return f"""\
You are an expert YouTube Shorts strategist. You have already analyzed a narration script and identified candidate passages. Now select the single best clip for each of the 5 Short types.

The 5 Short types:
1. Surprise — A fact that contradicts common belief — stops the scroll
2. Emotion — A moment with fear, shame, hope, or identity — hits the viewer personally
3. Standalone — An idea complete in itself — full value without watching the main video
4. CTA-Hook — An open loop — leaves the viewer wanting the full video
5. Practical Tip — One concrete thing the viewer can apply right now

Rules:
- Select exactly one Short per type — 5 Shorts total
- No two Shorts may share any lines
- Use the EXACT sentences from the narration — do not paraphrase, rewrite, or add words
- If a passage could serve multiple types, assign it to the type where it is strongest and pick a different passage for the other type
- Prefer self-contained passages that make sense when pulled out of context

Output format — use this block exactly for all 5 Shorts, separated by ---:

## Short [N] — [Type]
**Why this works:** [1 sentence explaining the psychology trigger]

**Script lines to clip:**
> [exact lines from narration, copy/paste ready]

---

## Narration Script

{narration}

## Candidate Analysis from Pass 1

{analysis}
"""


_SHORTS_BRAND_SYSTEM = """\
You are writing YouTube Shorts metadata for a psychology channel called SENSUM.

Brand voice rules:
- Warm, specific, and grounded in the viewer's lived experience
- Never use: hack, secret, shocking, toxic, red flags, wake up, brutally honest, you won't believe
- Use instead: "you may have noticed", "research suggests", "it makes sense that", "you're not alone in this"
- Do not name researchers or cite study years — say "researchers found" or "scientists discovered"
- Brand promise: "You are not broken. Here's what the science says."

Title rules:
- Maximum 60 characters
- Speaks to the psychology insight directly — not the video format
- Creates curiosity or emotional recognition, not manufactured shock

Description rules:
- 1-2 sentences only — state the core claim or insight directly
- End with: #Shorts plus 2-3 relevant topic hashtags (e.g. #Psychology #MentalHealth #Anxiety)
- No researcher names, no inline citations

Tags rules:
- Exactly 10-12 tags per Short — plain comma-separated strings, no # prefix
- Mix: 2-3 near-exact title/phrase variants tied to the clip's specific angle
       3-4 named psychology or science concepts that appear in the clip (e.g. "Zeigarnik Effect", "psychological detachment")
       3-4 broad discovery terms the target audience searches (e.g. "mental health", "burnout", "anxiety relief")
       Always include "SENSUM" and "SENSUM Science" at the end
- Tags should be tuned to THIS Short's specific angle, not the parent video as a whole
"""


def _build_shorts_pass3_prompt(narration: str, shorts_text: str) -> str:
    return f"""\
{_SHORTS_BRAND_SYSTEM}

Below are 5 selected YouTube Shorts. For each one, add **Title**, **Description**, and **Tags** fields.

Rules:
- Insert **Title:**, **Description:**, and **Tags:** between "Why this works" and "Script lines to clip" — in that order
- Do NOT change or rephrase the "Why this works" text
- Do NOT alter the "Script lines to clip" content — copy it exactly
- Keep the same markdown structure and --- separators
- Tags must be a single comma-separated line (no bullets, no # prefix)

Output the full 5-short block with the new fields included. No preamble, no commentary.

## Narration Script (for context only)

{narration}

## Selected Shorts from Pass 2

{shorts_text}
"""


def run_shorts_pass(narration: str) -> str:
    analysis, _ = _query_claude(_build_shorts_pass1_prompt(narration), "shorts pass 1 — candidate mapping")
    shorts_text, _ = _query_claude(_build_shorts_pass2_prompt(narration, analysis), "shorts pass 2 — selection")
    enhanced, _ = _query_claude(_build_shorts_pass3_prompt(narration, shorts_text), "shorts pass 3 — titles and descriptions")
    return enhanced


# ---------------------------------------------------------------------------
# Pass 3 — YouTube Metadata
# ---------------------------------------------------------------------------


def _scrape_suggestions(query: str) -> list[str]:
    try:
        encoded = urllib.parse.quote(query)
        url = (
            "https://suggestqueries.google.com/complete/search"
            f"?client=youtube&ds=yt&q={encoded}&hl=en"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8")
        match = re.search(r"\((\[.+\])\)", raw, re.DOTALL)
        if not match:
            return []
        data = json.loads(match.group(1))
        return [item[0] for item in data[1] if isinstance(item, list) and item]
    except Exception as exc:
        print(f"  autocomplete failed for {query!r}: {type(exc).__name__}: {exc}")
        return []


def _alphabet_soup(base_query: str) -> list[str]:
    results: list[str] = list(_scrape_suggestions(base_query))
    for letter in "abcdefghijklmnopqrstuvwxyz":
        results.extend(_scrape_suggestions(f"{base_query} {letter}"))
        time.sleep(0.1)
    return list(dict.fromkeys(results))


def _scrape_competitor_tags(topic: str, n: int = 7) -> list[str]:
    tags: list[str] = []
    try:
        encoded = urllib.parse.quote(topic)
        search_url = f"https://www.youtube.com/results?search_query={encoded}"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
        video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        seen: set[str] = set()
        unique_ids = [v for v in video_ids if not (v in seen or seen.add(v))][:n]
        for vid in unique_ids:
            try:
                vreq = urllib.request.Request(
                    f"https://www.youtube.com/watch?v={vid}",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                with urllib.request.urlopen(vreq, timeout=8) as vresp:
                    vhtml = vresp.read().decode("utf-8")
                m = re.search(
                    r'ytInitialPlayerResponse\s*=\s*(\{.+?\});\s*(?:var|const|let|window)',
                    vhtml, re.DOTALL,
                )
                if m:
                    data = json.loads(m.group(1))
                    kws = data.get("videoDetails", {}).get("keywords", [])
                    tags.extend(kws)
                time.sleep(0.15)
            except Exception as exc:
                print(f"  video {vid} tag scrape failed: {type(exc).__name__}: {exc}")
                continue
    except Exception as exc:
        print(f"  competitor search failed: {type(exc).__name__}: {exc}")
    return list(dict.fromkeys(tags))


def _build_metadata_prompt(topic: str, script: str, research: str, suggestions: list[str], competitor_tags: list[str]) -> str:
    use_kw = ", ".join(f'"{k}"' for k in _BRAND_USE[:6])
    avoid_kw = ", ".join(f'"{k}"' for k in _BRAND_AVOID)
    suggestions_block = (
        "\n".join(f"- {s}" for s in suggestions[:300])
        if suggestions
        else "(unavailable)"
    )
    competitor_block = (
        "\n".join(f"- {t}" for t in competitor_tags[:150])
        if competitor_tags
        else "(unavailable)"
    )

    return f"""\
You are a YouTube metadata specialist for SENSUM, a psychology education channel.
Brand promise: "You are not broken. Here's what the science says."
Tone: Mr. Rogers meets neuroscience — warm, validating, never preachy or clinical.

## SENSUM Title Rules
- Warm and validating. Preferred language: {use_kw}
- NEVER use: {avoid_kw}
- 2–8 words. No colons unless elegant. No question marks that feel manipulative.

## Description Hook Rules (4 paragraphs)
1. Open with deep emotional validation in second person. The reader should feel seen immediately.
   Example opening: "You must be so incredibly tired."
2. Name the daily reality — the cycle or pattern the viewer is caught in. Still validating, never diagnostic.
3. "In this video, we explore..." — name 3–4 specific psychological concepts covered (use the exact scientific terms from the script).
4. Briefly tease the practical framework or path forward.

## Bibliography Format
**Concept Label:** Author, A., et al. (Year). One plain-English sentence: what this research shows and why it matters to the viewer.

---

## Topic
{topic}

## Final Script (first {SCRIPT_CONTEXT_CHARS} chars)
{script[:SCRIPT_CONTEXT_CHARS]}

## Verified Research (sources for bibliography)
{research[:RESEARCH_CONTEXT_CHARS]}

## Audience Search Signals (YouTube autocomplete)
{suggestions_block}

## Competitor Video Tags (scraped from top search results)
{competitor_block}

---

## Task

Return a single JSON object. No preamble, no commentary outside the JSON block.

```json
{{
  "description_hook": "Paragraph 1.\\n\\nParagraph 2.\\n\\nIn this video, we explore...\\n\\nParagraph 4.",
  "chapters": [
    {{"label": "Introduction", "placeholder": "00:00"}},
    {{"label": "Chapter Name", "placeholder": "[XX:XX]"}}
  ],
  "bibliography": [
    {{
      "concept": "Concept Label",
      "author": "Author, A., et al.",
      "year": "2021",
      "summary": "One plain-English sentence."
    }}
  ],
  "hashtags": ["#Psychology", "#MentalHealth", "#SENSUMScience", "#Neuroscience", "#EmotionalWellbeing"],
  "tags": ["tag 1", "tag 2", "tag 3"]
}}
```

Rules:
- chapters: detect natural section breaks from ## headings or bold section labels in the script. Produce 6–12 chapters. Labels: 2–5 words.
- tags: Produce exactly 15 tags using this mix:
  - 2–3 near-exact title/phrase variants (e.g. the video title and one close reword)
  - 4–5 named psychology or science concepts that appear explicitly in the script (e.g. "Zeigarnik Effect", "psychological detachment", "work-related rumination")
  - 3–4 broad discovery tags the target audience searches (e.g. "mental health", "burnout", "work stress", "psychology explained")
  - 2 fixed brand tags — always include "SENSUM" and "SENSUM Science"
  Use the audience search signals and competitor tags as reference for real viewer language — you may borrow, adapt, or ignore them. You are NOT restricted to selecting from those lists. Plain strings only, no # prefix."""


def _parse_metadata(response: str) -> dict:
    match = re.search(r"```json\s*([\s\S]+?)\s*```", response)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{[\s\S]+\}", response)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in Claude response.")


def run_metadata_pass(topic: str, script: str, research: str) -> dict:
    print("  Scraping YouTube autocomplete suggestions...")
    suggestions: list[str] = []
    try:
        suggestions = _alphabet_soup(topic)
        print(f"  Collected {len(suggestions)} unique suggestions")
    except Exception as exc:
        print(f"  Warning: Autocomplete scraping failed ({exc}).")

    print("  Scraping competitor video tags...")
    competitor_tags: list[str] = []
    try:
        competitor_tags = _scrape_competitor_tags(topic)
        print(f"  Collected {len(competitor_tags)} competitor tags")
    except Exception as exc:
        print(f"  Warning: Competitor tag scraping failed ({exc}).")

    prompt = _build_metadata_prompt(topic, script, research, suggestions, competitor_tags)
    raw, _ = _query_claude(prompt, "pass 3 — YouTube metadata", max_tokens=4096)

    return _parse_metadata(raw)


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def _build_metadata_block(meta: dict) -> str:
    chapters_block = "\n".join(
        f"{ch['placeholder']} {ch['label']}" for ch in meta["chapters"]
    )
    bib_block = "\n".join(
        f"**{b['concept']}:** {b['author']} ({b['year']}). {b['summary']}"
        for b in meta["bibliography"]
    )
    hashtags_line = " ".join(meta.get("hashtags", []))
    tags_line = ", ".join(meta.get("tags", []))

    return f"""\
## Video Description (paste into YouTube Studio)

{meta['description_hook']}

Timestamps:
{chapters_block}

📚 Research & References:
{bib_block}

{hashtags_line}

---
*SENSUM — Science of Kindness*

---

## YouTube Tags (copy all, paste into Tags field)

{tags_line}

---"""


def build_master_output(topic: str, slug: str, titles_text: str, shorts_text: str, meta: dict) -> str:
    today = date.today().isoformat()
    metadata_block = _build_metadata_block(meta)

    return f"""\
# Publish Package — {topic}
_Generated: {today} · Agent 8 · Slug: {slug}_

---

## Titles & Opening Hooks

{titles_text.strip()}

---

{metadata_block}

## YouTube Shorts Package

{shorts_text.strip()}
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python tools/agent8_publish.py "<slug>"')
        print('Example: python tools/agent8_publish.py "emotional-dysregulation-in-adhd"')
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 8: Publish Package ===")
    print(f"Slug : {slug}")
    print()

    # Load inputs
    print("[1/4] Reading input files...")
    try:
        script = read_output(slug, SCRIPT_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print(f'\nRun Agent 4 first:\n  python tools/agent4a_edit.py "{slug}"')
        sys.exit(1)

    try:
        narration = read_output(slug, NARRATION_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print(f'\nRun Agent 6 first:\n  python tools/agent6_narration.py "{slug}"')
        sys.exit(1)

    try:
        research = read_output(slug, RESEARCH_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print(f'\nRun Agent 2 first:\n  python tools/agent2_verify.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic(script)
    print(f"  Topic    : {topic}")
    print(f"  Script   : {len(script):,} chars")
    print(f"  Narration: {len(narration):,} chars")
    print(f"  Research : {len(research):,} chars")

    # Pass 1 — Titles & Hooks
    print(f"\n[2/4] Pass 1 — Titles & Hooks...")
    try:
        titles_text = run_titles_pass(script)
    except Exception as exc:
        print(f"\nError: Titles pass failed — {exc}")
        sys.exit(1)
    print(f"  Done ({len(titles_text):,} chars)")

    # Pass 2 — YouTube Shorts (3 sub-passes)
    print(f"\n[3/4] Pass 2 — YouTube Shorts (3 sub-passes)...")
    try:
        shorts_text = run_shorts_pass(narration)
    except Exception as exc:
        print(f"\nError: Shorts pass failed — {exc}")
        sys.exit(1)
    print(f"  Done ({len(shorts_text):,} chars)")

    # Pass 3 — YouTube Metadata
    print(f"\n[4/4] Pass 3 — YouTube Metadata...")
    try:
        meta = run_metadata_pass(topic, script, research)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"\nError parsing metadata response: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Metadata pass failed — {exc}")
        sys.exit(1)
    print(f"  Done")

    # Write master output
    print(f"\nSaving {OUTPUT_FILENAME}...")
    content = build_master_output(topic, slug, titles_text, shorts_text, meta)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    docx_path = export_to_docx(slug, OUTPUT_FILENAME, "docx/07_publish_package.docx")
    print(f"  Word export: {docx_path}")

    print(f"\nDone. Review {OUTPUT_FILENAME} before uploading to YouTube.")


if __name__ == "__main__":
    main()
