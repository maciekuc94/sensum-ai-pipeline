"""
Agent 8: Publish Package — Advanced YouTube Metadata Engineer / NLP Optimization Pipeline.

Runs three passes in sequence and produces one master output file:
  1. Titles — 5 long-form title variants (Identity Provocation blueprint: identity reframe / paradox / system-architectural reveal)
  2. YouTube Shorts — 3–5 lead-in packages, each with one identity-reframe title, a 1–2 sentence cognitive-dissonance description, a 3–5 multi-word backend-tag block, and a Script Lines to Clip split (Hook + Core payload, each tagged with the script quarter Q1–Q4 for DaVinci search)
  3. YouTube Metadata — description (Hook Segment + Explanatory Block with identity-absolution framing), chapters, bibliography (Research & References), 3-hashtag block, and 10–15 multi-word tag block (Tag #1 = exact-match primary keyword extracted from the chosen title; single-word tags prohibited; SENSUM-uppercase brand exception only)

Inputs:
  outputs/videos_pl/{slug}/md/04_script_final.md   (titles + metadata)
  outputs/videos_pl/{slug}/md/06_script_narration.md  (shorts clips + quarter splits)
  outputs/videos_pl/{slug}/md/02_verified_research.md (bibliography)

Outputs:
  outputs/videos_pl/{slug}/md/07_publish_package.md
  outputs/videos_pl/{slug}/docx/07_publish_package.docx

Usage:
    python tools/pipeline/agent8_publish.py "emotional-dysregulation-in-adhd"
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
    avoid_kw = ", ".join(f'"{k}"' for k in _BRAND_AVOID)
    return f"""\
You are an Advanced YouTube Metadata Engineer for the SENSUM channel — niche: behavioral science, neurobiology, emotional states. You operate with cold, empirical, mathematical precision. Your job is to bypass the Pre-sampling Queue and accelerate Impression Velocity through identity-provocation titles.

Read this script and generate exactly 5 long-form title variants. Each title must function as an **identity reframe, paradox, or system-level architectural reveal** — never as instruction, advice, or a list.

## TITLE ARCHITECTURE — Identity Provocation Blueprint

A qualifying title does ONE of the following:
- **Identity reframe** — names a state the viewer believes about themselves and inverts it ("You're Not Lazy. Your Reward System Is Misfiring.").
- **Paradox** — pairs two ideas the viewer assumes are opposites and reveals their unity ("What If Your Anxiety Is the System Working Perfectly?").
- **System-level architectural reveal** — describes the viewer's inner mechanism as a system the viewer didn't know they were running ("Your Nervous System Is Running on Outdated Settings.").

The viewer must feel addressed at the level of *identity* or *underlying mechanism* — not at the level of behavior or advice.

## HARD BANS (any of these auto-disqualifies a title)

- Instructional verbs: "how to", "how you can", "ways to", "tips for", "guide to", "steps to", "stop", "fix".
- List formats: "5 …", "7 things …", any leading number used as a counter.
- Generic mental-health framings: "anxiety", "trauma", "depression" used as standalone topical labels without an identity / paradox / system reframe around them.
- Advisory framing: "you should", "you need to", "what you must know".
- Clickbait words: {avoid_kw}.

## CONSTRAINTS

- Exactly 5 titles. Each under 60 characters.
- Specific to THIS script's actual content. Do not invent claims the script doesn't make.
- No quotation marks, no labels, no explanation. Numbered 1–5, title text only.
- Mix architectural modes across the 5 — at least 2 of the 3 modes (identity reframe / paradox / system reveal) must be represented.

Return ONLY the 5 numbered titles. No preamble, no commentary, no opening hooks, no closing remarks.

## Script

{script_content}
"""


def run_titles_pass(script_content: str) -> str:
    prompt = _build_titles_prompt(script_content)
    text, _ = _query_claude(prompt, "pass 1 — titles", max_tokens=1024)
    return text


# ---------------------------------------------------------------------------
# Pass 2 — YouTube Shorts (3 sub-passes)
# ---------------------------------------------------------------------------


def _build_shorts_pass1_prompt(narration: str) -> str:
    return f"""\
You are an expert YouTube Shorts strategist specializing in psychology content.

Read this full narration script and map every passage that has a credible path to qualifying as a YouTube Short under the algorithm's retention rules.

## The Triple Retention Filter

A viable Shorts candidate is a passage that can pass ALL THREE of these filters. Pass 1 surveys candidates; Pass 2 will make the final selection.

1. **COGNITIVE AUTONOMY** — the passage is (or can be trimmed into) a complete self-contained thought with internal structure: thesis → proof or example → conclusion. The viewer receives ONE whole idea in roughly 30 seconds without needing context from the surrounding video. If a candidate only makes sense when paired with what comes before or after, it fails this filter.

2. **INSTANT HOOK (0:01)** — the opening sentence hits a strong emotion or resonates with a specific lived problem within the first 1.5 seconds of spoken delivery. The viewer must feel something or recognise their own life from word one. Generic openings, framing language, definitions, or transitions ("And here's the thing", "Let's talk about", "So what does this mean") do NOT count as hooks.

3. **CURIOSITY GAP** — the passage delivers one complete answer while opening a larger door. After watching, the viewer should feel: "this resolved the small question — what about the bigger one?" That bigger question is what the main long-form video answers. A passage that fully closes the loop and leaves the viewer satisfied has no path to drive views to the main video and fails this filter.

The fragment should land in the 25–70 second range when read aloud at conversational pace (~50–150 words).

## What to Do

For each candidate passage you find:
- Quote the exact lines verbatim (no paraphrasing, no summarising).
- Suggest a free-form **angle tag** (2–4 words) describing the Short's actual pull. Examples: "Mind-blow reveal", "Naming the unnamed", "Open loop", "Practical reframe", "Body-feels-this", "Identity absolution". Do not constrain yourself to a fixed menu — describe what this specific passage does.
- For EACH of the three filters above, mark the candidate as PASS, BORDERLINE, or FAIL with a one-line reason. Be honest. A borderline opener like "And here's the thing" gets marked BORDERLINE on Instant Hook, not PASS.

Do NOT select winners yet. Your job is to survey the entire script and surface every viable option. Be thorough — it is better to over-identify candidates and let Pass 2 cut, than to miss a strong one.

## Script

{narration}
"""


def _build_shorts_pass2_prompt(narration: str, analysis: str) -> str:
    return f"""\
You are an expert YouTube Shorts strategist. You have already analyzed a narration script and identified candidate passages with PASS / BORDERLINE / FAIL marks against the Triple Retention Filter. Now select the final Shorts using a HARD AND-GATE.

## SELECTION RULE — Triple Retention Filter (HARD AND-GATE)

A candidate qualifies as a Short ONLY if it passes ALL THREE of these filters. Failing any single filter disqualifies it, no matter how strong it is on the other two. BORDERLINE counts as FAIL for the purposes of selection.

1. **COGNITIVE AUTONOMY** — does this 30-second fragment stand as a complete whole? Internal structure must be thesis → proof or example → conclusion. If the viewer needs context from the rest of the video to understand it, the Shorts algorithm will reject it and viewers will swipe. Disqualified.

2. **INSTANT HOOK (0:01)** — do the first 1.5 seconds hit a strong emotion or resonate with a specific lived problem? If the opening reads like throat-clearing, framing, definitions, or a generic transition ("And here's the thing", "Let's talk about", "So what does this mean"), viewers swipe in the first second. Disqualified.

3. **CURIOSITY GAP** — does the cut leave the viewer with a feeling of incompleteness that only watching the main video can resolve? A Short that fully closes the loop and leaves the viewer satisfied has no path to drive views to the long-form video — and the whole point of the Shorts strategy is to drive views to the main video. Disqualified.

## SELECTION RULES

- Select **the strongest 4 candidates** that pass all three filters. Every passage that genuinely passes all three filters is qualified — DO NOT withhold qualified Shorts because you can name something stronger. The cap is 4 strong-passers, not "the absolute top 2." A 10-minute psychology script with this much material almost always contains 3–4 passages that cleanly pass.
- Only if FEWER than 4 candidates genuinely pass all three filters do you return fewer (3, 2, even 1). Be honest about which dropped, and on which filter. Borderline candidates still count as failed — do not promote them. But do not over-prune either: a clean three-filter pass is a qualified Short.
- You are NOT constrained to any fixed archetype menu. They can all be the same "type" if that is what the script genuinely supports.
- No two Shorts may share any lines.
- Use the EXACT sentences from the narration — do not paraphrase, rewrite, or add words.
- Each Short should land in the 25–70 second range when read aloud (~50–150 words).
- For each Short, choose a free-form **angle tag** (2–4 words) describing its actual pull — examples: "Mind-blow reveal", "Naming the unnamed", "Open loop", "Practical reframe", "Body-feels-this", "Identity absolution".

## WHY-THIS-WORKS REQUIREMENT

For each selected Short, the **Why this works** sentence must explicitly address each of the three filters in this order:
- The thesis–proof–conclusion structure of this passage (what the complete thought is).
- What emotional or experiential beat lands inside the opening 1.5 seconds (the exact line + the feeling it triggers).
- The specific curiosity gap it leaves open (the bigger question that points to the main video).

Output format — use this block exactly for each Short, separated by ---:

## Short [N] — [self-chosen angle tag]
**Why this works:** [Cognitive Autonomy: complete-thought structure | Instant Hook: opening 1.5s emotion/problem | Curiosity Gap: forward door to main video]

**Script lines to clip:**
> [exact lines from narration, copy/paste ready]

---

## Narration Script

{narration}

## Candidate Analysis from Pass 1

{analysis}
"""


_SHORTS_BRAND_SYSTEM = """\
You are an Advanced YouTube Metadata Engineer writing Shorts lead-in packages for SENSUM — a long-form psychology channel for emotionally literate adults. Niche: behavioral science, neurobiology, emotional states. Each Short is a feed-lead-in: its job is to map the viewer's cognitive dissonance in 30 seconds and drive a click to the Related Video anchor.

Brand voice for Shorts descriptions (warm, validating — title voice differs):
- State the claim directly in the speaker's own voice. Grounded in the viewer's lived experience.
- Research is invisible. Do NOT use: "researchers found", "studies show", "scientists discovered", "research suggests", "according to researchers", "studies suggest", "research shows", "the science is clear". The viewer trusts the speaker, not the citation. Never name researchers or cite study years.
- Never use: hack, secret, shocking, toxic, red flags, wake up, brutally honest, you won't believe.
- Brand promise: "You are not broken. Here's what the science says."

Title rules:
- Produce exactly ONE title per Short (not a list of candidates).
- Maximum 60 characters.
- High-impact reframe: identity-reframe, paradox, or system-architectural reveal. Examples of the shape: "Your Depression Isn't a Flaw. It's a Misfiled Map." / "What If Your Procrastination Is Loyalty to an Old Self?"
- Speak to the psychology insight at the identity / mechanism level. Never instructional ("How to…", "Tips for…", "5 ways…").
- Creates curiosity or emotional recognition. Not manufactured shock.

Description rules:
- 1-2 sentences only — map the **core cognitive dissonance** the Short surfaces, optimized to drive the click to the Related Video anchor.
- End with: #Shorts plus 2 single-word lowercase topic hashtags (e.g. #Shorts #willpower #habits). Each hashtag must be ONE WORD — no spaces. "#nervous system" is wrong; use "#nervoussystem" or "#regulation".

Backend Tag Block rules (kept tight — Shorts algorithm barely reads backend tags; the real categorization signal is the description hashtags):
- 3–5 multi-word intent phrases per Short. Each phrase 2–4 words. Comma-separated, no `#` prefix.
- Tag #1 is the strongest search-shaped phrase that maps to THIS Short's core claim — treat it as the primary keyword for the Short.
- Every phrase must be extracted from (or be a direct paraphrase of the search intent behind) THIS Short's quoted lines.
- SINGLE-WORD TAGS ARE PROHIBITED. "psychology", "anxiety", "trauma" cause semantic dilution. The only single-word allowance is the brand handle "SENSUM" (uppercase), included ONCE.
- Be careful with metaphors. The Short may use vivid analogies (cookie, GPS, village, battery, door). Those illustrate the idea; they are not the idea. Tag the underlying concept, never the prop.
- Tags tuned to THIS Short's specific angle, not the parent video as a whole. Quality over quantity — 3 strong tags beats 5 padded with filler.

Script Lines to Clip rules:
- Two sub-sections, in this exact order: `Hook (first ~3s):` followed by the exact opening line(s) the editor cuts in for the first ~3 seconds; then `Core payload:` followed by the exact line(s) carrying the Short's main claim.
- Quote both blocks verbatim from the narration script — same words, same punctuation. No paraphrasing, no summarising. The editor uses these exact lines to find the cut points in the recorded audio.
- The combined hook + payload should still land in the 25–70 second range when read aloud at conversational pace (~50–150 words total across both blocks).
"""


def _build_shorts_pass3_prompt(narration: str, shorts_text: str) -> str:
    return f"""\
{_SHORTS_BRAND_SYSTEM}

Below are the **selected** YouTube Shorts (between 1 and 4 — Pass 2 returned only those candidates that passed the Triple Retention Filter as a hard AND-gate). For each Short Pass 2 provided, add **Title**, **Description**, **Tags**, and a restructured **Script Lines to Clip** block (split into Hook + Core payload). **DROP** the `**Why this works:**` line — it was Pass 2's internal selection justification and does not appear in the final published output.

HARD RULES (violating any of these breaks downstream tooling):

1. **DROP the `**Why this works:**` line entirely.** It is not part of the final output. Do not rephrase it as a description, do not preserve it as a comment, do not move it elsewhere. Delete it.

2. **Exactly ONE of each labelled field per Short.** Under each `## Short N` heading there must be exactly one `**Title:**` line, exactly one `**Description:**` line, exactly one `**Tags:**` line, and exactly one `**Script Lines to Clip:**` block. NEVER output two of any field under the same Short.

3. **VALIDATION GATE — read this BEFORE writing each Short.** For each Short, before writing ANY field (Title / Description / Tags / Script Lines), check: do I have BOTH a Hook quote AND a Core payload quote sourced verbatim from Pass 2 or the Narration Script? If NO, OMIT that Short entirely — do not write its Title, Description, or Tags. Move on to the next Short. **A 3-Short output with all four fields intact on every Short is REQUIRED. A 4-Short output with one missing Script Lines block is REJECTED downstream and triggers a regeneration cost.**

   The `**Script Lines to Clip:**` block format:
   - `Hook (first ~3s):` followed by `> ` and the exact opening line(s) the editor cuts in for the first ~3 seconds — verbatim from Pass 2 or the Narration Script. No paraphrasing.
   - `Core payload:` followed by `> ` and the remaining quoted line(s) carrying the Short's main claim — verbatim. No paraphrasing.
   If Pass 2 provided only one short quote, place it under `Hook (first ~3s):` and source the `Core payload:` from the next 1–2 sentences in the Narration Script that continue the same thought verbatim. If you cannot find a verbatim continuation in the narration, OMIT THE WHOLE SHORT (validation gate above).

4. **Field order is LOCKED:** under each `## Short N — [angle tag]` heading, the lines must appear in this exact order — and no others:
   - `**Title:**` (single title, max 60 chars, identity-reframe / paradox / system-reveal blueprint)
   - `**Description:**` (1–2 sentences mapping the cognitive dissonance, ending with `#Shorts #x #y`)
   - `**Tags:**` (3–5 multi-word intent phrases, comma-separated, no `#` prefix)
   - `**Script Lines to Clip:**` (followed immediately by `Hook (first ~3s):` and `Core payload:` blocks on their own lines, each followed by `> ` quoted lines)

5. **Tags — KEEP TIGHT.** 3–5 multi-word intent phrases per Short, each 2–4 words, comma-separated, no `#` prefix. Single-word tags are PROHIBITED (semantic dilution). Brand exception: SENSUM appears once (uppercase) as the only single-word entry. Every phrase extractable from THIS Short's quoted lines or a direct-intent paraphrase. Backend tags are a categorization safety net on Shorts, not a discovery driver — the description hashtags carry the real algorithmic signal.

6. **Description:** state the claim directly in the speaker's own voice. NO research-framing language — no "researchers found", no "studies show", no "scientists discovered", no "research suggests", no "according to researchers". The viewer trusts the speaker, not the citation.

7. **Title:** identity-reframe, paradox, or system-architectural reveal. NEVER instructional, advisory, or list-format. Max 60 characters.

8. **Keep the `---` separators between Shorts and the heading line `## Short N — [angle tag]` exactly as Pass 2 produced them.**

Output one full block per Short Pass 2 provided, with the new fields included. No preamble, no commentary outside the blocks.

## Narration Script (for context — use to split Hook from Core payload and to source any continuation lines)

{narration}

## Selected Shorts from Pass 2

{shorts_text}
"""


_QUARTER_LABEL_RE = re.compile(r"^(Hook \(first ~3s\):|Core payload:)\s*(?:\[Q[1-4?]\])?\s*$")


def _annotate_script_quarters(narration: str, shorts_text: str) -> str:
    """Tag each Hook / Core-payload label with the script quarter (Q1–Q4) of its quote.

    Splits the narration into four equal-word-count quarters, then for every
    `Hook (first ~3s):` and `Core payload:` label in the Shorts text, finds the
    first following `> …` line and appends `[Q1] / [Q2] / [Q3] / [Q4]` to the
    label based on where that quote appears in the narration. The editor uses
    the marker to locate the line in DaVinci by text-search within the right
    quarter of the script. Falls back to `[Q?]` when no match is found, so
    failures are visible rather than silent.
    """
    words = narration.split()
    total = len(words)
    if total == 0:
        return shorts_text
    q1_end = total // 4
    q2_end = total // 2
    q3_end = (total * 3) // 4

    narration_lower = narration.lower()

    def _quarter_for_quote(raw_quote: str) -> str:
        stripped = raw_quote.lstrip("> ").strip().strip('"').strip("'").strip("“”")
        if not stripped:
            return "Q?"
        for needle_len in (60, 30, 15):
            needle = stripped[:needle_len].lower()
            if not needle:
                continue
            idx = narration_lower.find(needle)
            if idx >= 0:
                word_pos = len(narration[:idx].split())
                if word_pos < q1_end:
                    return "Q1"
                if word_pos < q2_end:
                    return "Q2"
                if word_pos < q3_end:
                    return "Q3"
                return "Q4"
        return "Q?"

    lines = shorts_text.splitlines()
    output: list[str] = []
    for i, line in enumerate(lines):
        match = _QUARTER_LABEL_RE.match(line.strip())
        if not match:
            output.append(line)
            continue
        quote_line = ""
        for j in range(i + 1, min(i + 6, len(lines))):
            if lines[j].lstrip().startswith(">"):
                quote_line = lines[j]
                break
        quarter = _quarter_for_quote(quote_line) if quote_line else "Q?"
        output.append(f"{match.group(1)} [{quarter}]")
    return "\n".join(output)


def _validate_shorts_clip_blocks(shorts_text: str) -> tuple[str, list[int]]:
    """Validate that every Short in the text has a `**Script Lines to Clip:**` block.

    The Pass 3 prompt marks this block as MANDATORY but the model occasionally
    omits it. For any Short missing the block, append a visible placeholder so
    the failure is loud, not silent — the editor will see `[MISSING …]` instead
    of just a Short that quietly lacks clip refs. Returns the annotated text
    and a list of Short numbers that were missing the block.
    """
    blocks = re.split(r"(?m)(?=^## Short \d+)", shorts_text)
    broken: list[int] = []
    output_blocks: list[str] = []
    for block in blocks:
        header_match = re.match(r"^## Short (\d+)", block)
        if not header_match:
            output_blocks.append(block)
            continue
        if "**Script Lines to Clip:**" not in block:
            broken.append(int(header_match.group(1)))
            block = block.rstrip() + "\n\n**Script Lines to Clip:** [MISSING — model dropped this block; locate the lines manually in 06_script_narration.md or rerun the Shorts pass]\n\n---\n"
        output_blocks.append(block)
    return "".join(output_blocks), broken


def run_shorts_pass(narration: str) -> str:
    analysis, _ = _query_claude(_build_shorts_pass1_prompt(narration), "shorts pass 1 — candidate mapping")
    shorts_text, _ = _query_claude(_build_shorts_pass2_prompt(narration, analysis), "shorts pass 2 — selection")
    enhanced, _ = _query_claude(_build_shorts_pass3_prompt(narration, shorts_text), "shorts pass 3 — titles and descriptions")
    annotated = _annotate_script_quarters(narration, enhanced)
    validated, broken = _validate_shorts_clip_blocks(annotated)
    if broken:
        print(f"  WARNING: Shorts {broken} missing `**Script Lines to Clip:**` block — placeholder inserted; regenerate or locate lines manually")
    return validated


# ---------------------------------------------------------------------------
# Pass 3 — YouTube Metadata
# ---------------------------------------------------------------------------


def _scrape_suggestions(query: str) -> list[str]:
    try:
        encoded = urllib.parse.quote(query)
        url = (
            "https://suggestqueries.google.com/complete/search"
            f"?client=youtube&ds=yt&q={encoded}&hl=pl&gl=PL"
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


def _build_metadata_prompt(topic: str, script: str, research: str, suggestions: list[str], competitor_tags: list[str], niche_signals: str = "", titles_text: str = "") -> str:
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
    titles_block = titles_text.strip() if titles_text.strip() else "(unavailable)"

    return f"""\
You are an **Advanced YouTube Metadata Engineer and NLP Optimization Pipeline** for the SENSUM channel. Niche: behavioral science, neurobiology, emotional states. Your sole purpose is to convert raw script data and research into a highly optimized Publish Package designed to **bypass the Pre-sampling Queue and accelerate Impression Velocity**.

Execute every task with cold, empirical, mathematical precision. The OUTPUT you produce (description body, references) is warm and validating in the speaker's voice — but your decision logic for tag selection, NLP anchoring, and E-E-A-T construction is algorithmic. You are not writing prose for the viewer to enjoy; you are constructing an NLP surface for YouTube's discovery pipeline.

Operating principles:
- A tag is a search query, not a vocabulary word. If you can't picture a real person living this problem typing it into YouTube search, it has no place in the tag block.
- **Tag #1 carries the most algorithmic weight.** YouTube front-loads semantic weight onto the first tag in the list. Tag #1 must be the **exact-match primary keyword** of the video — a search-shaped phrase extracted from (or paraphrased from) the strongest of the 5 candidate titles provided above. The remaining tags then cluster around this primary keyword.
- Single-word tags cause **semantic dilution and format decoupling** on this niche. Tags are multi-word phrases (≥2 words). The only exception is the brand handle "SENSUM" (one slot, uppercase, included once).
- Metaphors and props in the script (cookies, batteries, GPS, doors, villages) are illustrations, not search terms. Tag the underlying mechanism the metaphor points to.
- Established clinical and pop-psychology terms (rumination, regulation, attachment, burnout, masking, anhedonia, limerence) are what serious viewers actually search for — render them inside multi-word phrases that match real search behavior.
- The Niche Trend Signals block below lists single-word terms currently trending in this niche. Borrow the concepts but ALWAYS render them as multi-word phrases in the final tag list. Treat niche signals as a **supporting reference** for the back half of the tag list — the primary keyword from the chosen title leads.
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is established through the formal bibliography, not the description prose.

## Description Architecture (NLP-anchored)

Write the description body in this exact three-block structure. Total length under 120 words across all three blocks.

**Block 1 — Hook Segment (Lines 1–2).** 3–6 short fragment-style observations of somatic or emotional states the viewer recognises from their own life. No conversational filler, no greeting, no framing language. Cold cadence, lived specificity. The viewer must hit the first line and feel addressed.

Examples of the shape (do not copy verbatim):
- "Snapping at someone before you knew why. Going quiet when you meant to speak. The drift between what you wanted to say and what came out."
- "Starting over. Again. The gym bag by the door. The journal with three entries. The app you stopped opening."

**Block 2 — Explanatory Block (Line 3+).** Connect the hook to the **anatomical or psychological thesis** of the video using **identity-absolution framing**. Lead with a phrase shaped like "These aren't character flaws — they're the signals of [the mechanism the video explains]" or "What looks like [self-blame label] is actually [mechanism]". Then name 3–5 concepts the video covers, translated into plain everyday language — no jargon ("the science behind why willpower fades", not "ego depletion"). Close on one warm line about understanding the mechanism. 2–3 sentences total.

Hard rules for the whole description:
- NO researcher names, NO study years, NO Latin-sounding jargon in the description body
- NO second-person preachy lines like "You must be so incredibly tired"
- NO clickbait words: {avoid_kw}
- The phrase "In this video, we explore" is PERMITTED but no longer mandated as an opener — use it only if it serves the Explanatory Block's flow.
- Use concrete sensory examples over abstract concepts

## Bibliography — Decision Procedure (mission-critical)

The Verified Research section below contains N peer-reviewed entries. For EACH entry, you MUST explicitly decide INCLUDE or EXCLUDE based on this single question:

> "Does the script make any claim — direct or indirect, literal or thematic — that this research could plausibly support?"

- If yes (any thematic tie, even loose): **INCLUDE.**
- The ONLY ground for exclusion is **ZERO thematic tie** — the entry's topic shares no concept, mechanism, population, or finding with anything the script discusses. You must be able to state the zero-tie reason in one short sentence.

The script is research-grounded but **research-invisible**: the speaker never names a study, a researcher, or a year. That means almost no verified entry will have an explicit script anchor. **This is expected, and is NOT a ground for exclusion.** The bibliography credits the science underneath the script's claims, not the words the speaker literally said.

### Examples of LOOSE thematic tie (= INCLUDE):
- Research on cancer patients carrying past trauma → script claim "the body holds what the mind tries to move past" (population differs, mechanism matches: include)
- Research on community-based intervention for adolescent psychiatric crises → script claim "the steadiness of another person's eyes" or any co-regulation language (setting differs, principle matches: include)
- Research on workplace burnout in healthcare → script claim about chronic nervous-system overload (industry differs, mechanism matches: include)

### Examples of ZERO tie (= EXCLUDE):
- Research on agricultural yield, sports performance, software optimization, or any topic that shares no concept with the script.

### Format for each included entry:
• Concept Label — Optional Qualifier: Author, A., et al. (Year).

Citation only — ending with the year in parentheses and a period. NO descriptive sentence, NO summary, NO "why it matters."

**Default: include everything. Failing to surface a thematically-tied reference is a worse error than including a loosely-tied one.** If 4 entries are provided and 3 have any thematic tie, your bibliography MUST have 3 entries — not 1.

When a concept has multiple landmark sources (original study + replication, original + meta-analysis), produce a separate bibliography entry per source and use the qualifier to distinguish them (e.g. "Ego Depletion — Original Study", "Ego Depletion — Meta-Analysis", "Ego Depletion — Replication Failure").

---

## Topic
{topic}

## Candidate Long-Form Titles (Pass 1 output — use to extract the primary keyword for Tag #1)
{titles_block}

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
  "description_hook": "Block 1 — Hook Segment fragments.\\n\\nBlock 2 — Explanatory Block with identity-absolution framing naming 3–5 concepts.",
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
  "tags": ["long tail phrase one", "long tail phrase two", "..."]
}}
```

Rules:
- `description_hook`: the full two-block description body (Hook Segment + Explanatory Block) as a single string. Use `\\n\\n` between blocks. Under 120 words total. The `Timestamps:` and `Research & References:` sections are appended by downstream tooling — do NOT include them in this field.
- `chapters`: detect natural section breaks from ## headings or bold section labels in the script. Produce 6–12 chapters. Labels: 2–5 words. First chapter is always `{{"label": "Introduction", "placeholder": "00:00"}}`. All others use `"[XX:XX]"` as a placeholder for the editor to fill in.
- `hashtags`: Produce 3 hashtags only. Single-word, lowercase, with `#` prefix. First hashtag is always `#sensum`. The other 2 are the single-word core topic + one single-word concept from the script (e.g. `#sensum #willpower #grit`). NO multi-word hashtags, NO camelCase combinations, NO spaces inside a hashtag. The hashtags block is the ONLY single-word survivor — the YouTube Tags field is exclusively multi-word (≥2 words; the SENSUM brand slot is the sole single-word exception).
- `tags`: **THE TAG PROTOCOL — NON-NEGOTIABLE.**
  - Produce **10–15 tags total**. Comma-separated in the final output, no `#` prefix. Each tag is a multi-word phrase (≥2 words). Quality over quantity — 10 strong tags beats 15 padded with filler. 2026 YouTube SEO consensus is 8–15 quality tags; going higher risks keyword-stuffing penalties and dilutes per-tag weight.
  - **SLOT STRUCTURE — order by algorithmic weight (front-loaded):**
    - **Tag #1 (mandatory): the exact-match primary keyword for this video.** Extracted from the strongest of the candidate titles provided above, OR a more search-shaped paraphrase if the chosen identity-provocation title is metaphor-heavy and would not autocomplete in YouTube search. This single slot does the heaviest discovery work — do not waste it.
    - **Tags #2–#5: strongest long-tail variations and paraphrases of the primary keyword.** 3–5 words each. They should look like real autocomplete suggestions: "how to allow yourself to feel anger", "permission to feel emotions psychology", "stop suppressing anger as a woman".
    - **Tags #6–#12: supporting long-tail intent phrases.** 2–4 words. Lived-experience phrasing the viewer would name themselves with ("why I keep self sabotaging"), clinical / mechanism phrases rendered as searches ("nervous system regulation tools", "rumination loop in anxiety"), and search-variant phrasing. This is where Niche Trend Signals get rendered as multi-word phrases (signal "regulation" → "nervous system regulation tools").
    - **Tags #13–#15 (optional): broader 2–3 word category anchors** that bind the video to the niche territory ("permission psychology", "emotional regulation", "somatic self compassion"). These exist for the topic-categorization layer YouTube uses for related-video sidebar placement. Still multi-word — single-word remains prohibited.
    - **SENSUM**: include exactly once (uppercase). The only single-word tag permitted. Slot anywhere.
  - **SINGLE-WORD TAGS ARE PROHIBITED** outside the SENSUM brand slot. "psychology", "anxiety", "trauma", "burnout", "rumination" cause semantic dilution and format decoupling — render them inside multi-word phrases.
  - **The intent test.** For each phrase, ask: *"Would a real person living the problem this video addresses type these exact words into YouTube search?"* If not, leave it out.
  - Tag metaphors by underlying concept, not the prop (e.g. willpower fatigue, not battery).
  - Every phrase must be extractable from the script's literal language OR be a direct paraphrase of the search intent the script / chosen title surfaces (Exact Speech-to-Text Match preferred — borrow the speaker's phrasing when it works as a search query).
  - **Total comma-separated string must stay under 450 characters** (the 500-char YouTube hard cap minus safety margin). Most strong phrases land in the 18–30 char range; if your phrases average 35+ chars you will overrun. Order is STRONGEST FIRST — the post-pass trimmer drops from the tail if you overrun, so weakest-last protects the slot structure above."""


def _parse_metadata(response: str) -> dict:
    match = re.search(r"```json\s*([\s\S]+?)\s*```", response)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{[\s\S]+\}", response)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in Claude response.")


def _trim_tags_to_budget(tags: list[str], char_budget: int = 450) -> list[str]:
    """Trim tags from the END of the list until the comma-joined string fits.

    Preserves the SENSUM brand-exception slot regardless of position. Trims
    non-SENSUM entries from the tail inward — the prompt instructs Claude to
    front-load by algorithmic weight (Tag #1 = exact-match primary keyword,
    Tags #2–#5 = strongest variations, tail = broader anchors), so end-trimming
    preserves the highest-weight slots. Budget defaults to 450 to leave
    headroom under YouTube's hard 500-char tag-field cap.
    """
    if not tags:
        return tags
    result = list(tags)
    while len(", ".join(result)) > char_budget and len(result) > 1:
        # Drop the last non-SENSUM entry.
        for i in range(len(result) - 1, -1, -1):
            if result[i].strip().upper() != "SENSUM":
                result.pop(i)
                break
        else:
            break
    return result


def run_metadata_pass(topic: str, script: str, research: str, titles_text: str = "") -> dict:
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

    prompt = _build_metadata_prompt(topic, script, research, suggestions, competitor_tags, niche_signals, titles_text)
    raw, _ = _query_claude(prompt, "pass 3 — YouTube metadata", max_tokens=4096)

    meta = _parse_metadata(raw)

    raw_tags = meta.get("tags", [])
    trimmed_tags = _trim_tags_to_budget(raw_tags)
    meta["tags"] = trimmed_tags
    tags_len = len(", ".join(trimmed_tags))
    dropped = len(raw_tags) - len(trimmed_tags)
    if dropped > 0:
        print(f"  Tag block: {len(trimmed_tags)} tags, {tags_len} chars (trimmed {dropped} from tail to fit 450-char target; doctrine 10–15; YouTube cap is 500)")
    else:
        within_doctrine = "within doctrine" if 10 <= len(trimmed_tags) <= 15 else f"OUTSIDE doctrine 10–15"
        print(f"  Tag block: {len(trimmed_tags)} tags, {tags_len} chars ({within_doctrine}; under 450-char target; YouTube cap is 500)")

    return meta


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

Research & References:
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

## Titles

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
        meta = run_metadata_pass(topic, script, research, titles_text)
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
