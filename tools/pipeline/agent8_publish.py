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
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
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
You are a senior YouTube SEO and tags expert writing Shorts metadata for SENSUM — a long-form psychology education channel for emotionally literate adults.

You know what drives Shorts discovery in the psychology / mental-health niche:
- Tags must be words the viewer would actually type into search, not words that happen to appear in the clip
- Metaphors and props in the narration (cookies, batteries, GPS, villages, doors) are illustrations — you tag the underlying psychological concept they point to, never the prop
- Established psychology terms (rumination, attachment, regulation, burnout, masking, anhedonia) outperform invented compounds every time
- YouTube is case-insensitive, so "SENSUM" and "sensum" are duplicates — one slot wasted

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
- End with: #Shorts plus 2 single-word lowercase topic hashtags (e.g. #shorts #willpower #habits)
- No researcher names, no inline citations

Tags rules:
- Exactly 15 tags per Short — SINGLE-WORD ONLY, plain comma-separated, no # prefix. Each tag must be ONE WORD (no spaces, no hyphens). Include "SENSUM" (uppercase) once as the only brand tag.

- **The tag test:** For each tag, ask *"Would someone who needs this Short actually type this exact word into YouTube search?"* If you can't picture a real person — someone living the problem this Short addresses — typing it, leave it out. 13 strong tags beats 15 with filler.

- Good tags fall into one of three buckets:
  1. The lived experience as people name it (burnout, loneliness, procrastination, comparison)
  2. The clinical / pop-psychology term they might've encountered (rumination, attachment, regulation, selfworth)
  3. The broader discovery layer they browse in (psychology, mentalhealth, selfhelp, mindset)

- Be careful with metaphors. The Short may use vivid analogies — a cookie, a GPS, a village, a battery. Those illustrate the idea; they are not the idea. Tag the underlying concept the metaphor points to, never the prop.

- Tags should be tuned to THIS Short's specific angle, not the parent video as a whole.
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


def _load_niche_signals() -> str:
    """Return the most recent {week}_tag_signals.md content, or '' if none exists.

    Sidecar is produced by Agent 11 alongside the weekly PPTX report.
    Agent 8 uses it as additional context for tag selection.
    """
    intel_dir = Path("outputs/intelligence")
    if not intel_dir.exists():
        return ""
    files = sorted(intel_dir.glob("*_tag_signals.md"), reverse=True)
    if not files:
        return ""
    try:
        return files[0].read_text(encoding="utf-8")
    except Exception as exc:
        print(f"  niche signals read failed: {type(exc).__name__}: {exc}")
        return ""


def _build_metadata_prompt(topic: str, script: str, research: str, suggestions: list[str], competitor_tags: list[str], niche_signals: str = "") -> str:
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
    niche_block = niche_signals.strip() if niche_signals.strip() else "(unavailable)"

    return f"""\
You are a senior YouTube SEO and tags expert working on the SENSUM channel — a long-form psychology education channel for emotionally literate adults.

You have deep experience with what actually drives YouTube discovery in the mental-health / psychology / self-development niche:
- You know the difference between a tag a viewer searches for and a word that just appears in a script
- You know that metaphors and props in a script (cookies, batteries, GPS, doors, villages) are illustrations, not search terms — you tag the underlying psychological concept they point to
- You know that established clinical and pop-psychology terms (rumination, regulation, attachment, burnout, selfworth, anhedonia, limerence, masking) are what serious viewers actually search for
- You know YouTube tags are case-insensitive, so "SENSUM" and "sensum" are duplicates and a wasted slot
- You know the audience's search vocabulary changes weekly — and the Niche Trend Signals block below tells you exactly what's trending in this niche right now
- You write for the viewer searching, not for the viewer watching — the script tells you what the video IS, the tags tell YouTube who needs it

Brand promise: "You are not broken. Here's what the science says."
Tone: Mr. Rogers meets neuroscience — warm, validating, never preachy or clinical.

## SENSUM Title Rules
- Warm and validating. Preferred language: {use_kw}
- NEVER use: {avoid_kw}
- 2–8 words. No colons unless elegant. No question marks that feel manipulative.

## Description Hook Rules (two short paragraphs)

Write TWO short paragraphs. Emotional and relatable — NOT science jargon. The viewer should feel seen first, then learn what the video covers.

**Paragraph 1 — Concrete + relatable.** Open with 3–6 short fragment-style observations or behaviours from the script's topic, written like everyday language someone would actually say. Then one transition sentence that softly reframes those behaviours through the lens of psychology — without using jargon. Aim for 2–4 sentences total.

Examples of the tone (from other channels, for reference only):
- "Weird habits. Random quirks. Talking to yourself. Daydreaming too much. Staying up late thinking about life. Some of these habits may seem strange on the surface… but psychology suggests they can sometimes be linked to higher intelligence, creativity, emotional depth, or deeper self-awareness."
- "You restart the gym. You buy the journal. You download the language app. And every time, the same quiet thought returns: maybe I'm just not the disciplined type. That story has a name in psychology — and it isn't laziness."

**Paragraph 2 — "In this video, we explore..."** Start exactly with "In this video, we explore" and name 3–5 of the actual concepts from the script — but translate them into plain everyday language. NO jargon like "ego depletion" or "intention-behavior gap" in this paragraph. Instead say things like "the science behind why willpower fades", "what really decides whether a habit sticks", "the moment a goal starts to feel hollow". End with one warm closing sentence about understanding yourself / the topic better. 2–3 sentences total.

Hard rules for the whole description:
- NO researcher names, NO study years, NO Latin-sounding jargon
- NO second-person preachy lines like "You must be so incredibly tired"
- Use concrete sensory examples over abstract concepts
- Keep total length under 120 words across both paragraphs

## Bibliography Format
• Concept Label — Optional Qualifier: Author, A., et al. (Year).

That is the full entry — citation only, ending with the year in parentheses and a period. NO descriptive sentence, NO summary, NO "why it matters." Just the citation line.

When a concept has multiple landmark sources (original study + replication, original + meta-analysis), produce a separate bibliography entry per source and use the qualifier to distinguish them (e.g. "Ego Depletion — Original Study", "Ego Depletion — Meta-Analysis", "Ego Depletion — Replication Failure").

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

## Niche Trend Signals (latest weekly intelligence report — internal niche data)
{niche_block}

---

## Task

Return a single JSON object. No preamble, no commentary outside the JSON block.

```json
{{
  "description_hook": "In this video, we explore [concept 1] — [brief framing] — alongside [concept 2], [concept 3], and what research on [concept 4] actually tells us about [audience-relevant angle].",
  "chapters": [
    {{"label": "Introduction", "placeholder": "00:00"}},
    {{"label": "Chapter Name", "placeholder": "[XX:XX]"}}
  ],
  "bibliography": [
    {{
      "concept": "Concept Label — Optional Qualifier",
      "author": "Author, A., et al.",
      "year": "2021"
    }}
  ],
  "hashtags": ["#sensum", "#topic", "#concept"],
  "tags": ["tag1", "tag2", "tag3"]
}}
```

Rules:
- chapters: detect natural section breaks from ## headings or bold section labels in the script. Produce 6–12 chapters. Labels: 2–5 words.
- hashtags: Produce 3 hashtags only. Single-word, lowercase, with # prefix. First hashtag is always "#sensum". The other 2 are the single-word core topic + one single-word concept from the script (e.g. "#sensum #willpower #grit"). NO multi-word hashtags, NO camelCase combinations.
- tags: Produce exactly 15 tags, SINGLE-WORD ONLY. Plain comma-separated, no # prefix. Each tag must be ONE WORD (no spaces, no hyphens). Always include "SENSUM" (uppercase) once as the only brand tag — no casing duplicates.

  **The tag test.** Before adding any tag, ask: *"Would someone who needs this video actually type this exact word into YouTube search?"* If you can't picture a real person — someone living the problem the video addresses — typing it, leave it out. Stronger to return 13 tags that pass this test than 15 padded with filler.

  Think about who your viewer is: they're feeling something specific (shame, exhaustion, drift, grief, stuckness) and they're searching for either the **feeling**, the **concept**, or the **niche**. Good tags fall into one of those three buckets:
  - The lived experience as people name it: "burnout", "loneliness", "procrastination", "comparison"
  - The clinical or research term they might've encountered: "rumination", "attachment", "selfworth", "regulation"
  - The discovery layer they browse in: "psychology", "mentalhealth", "selfhelp", "mindset"

  Be careful with metaphors. The script may use vivid analogies — a cookie, a GPS, a village, a battery, a closed door. Those illustrate the idea; they are not the idea. Tag the underlying concept the metaphor points to (e.g. willpower, navigation → direction-in-life, comparison, depletion-myth, loss), not the prop itself.

  Mix roughly: 2–3 single-word variants of the topic itself, 6–7 named psychology / mental-health terms the video genuinely covers, 4–5 broader discovery terms the SENSUM audience searches, plus SENSUM. Adjust the mix to whatever genuinely fits the video — don't force a category.

  **Highest-priority reference: the Niche Trend Signals block above.** It lists single-word terms currently trending in this exact niche this week. When a signal-block term clearly fits the video's content, borrow it — these are words your audience is actively searching right now. Audience search signals and competitor tags are secondary reference. You are not restricted to any of these lists, but you should generally borrow heavily from them when relevance is there."""


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

    niche_signals = _load_niche_signals()
    if niche_signals:
        print(f"  Loaded niche tag signals ({len(niche_signals)} chars)")
    else:
        print("  No niche tag signals found (Agent 11 sidecar absent — skipping)")

    prompt = _build_metadata_prompt(topic, script, research, suggestions, competitor_tags, niche_signals)
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
        f"• {b['concept']}: {b['author']} ({b['year']})."
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
