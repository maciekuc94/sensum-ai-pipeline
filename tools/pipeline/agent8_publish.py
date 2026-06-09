"""
Agent 8: Publish Package — Advanced YouTube Metadata Engineer / NLP Optimization Pipeline.

As of 2026-06-02 the publish package is generated **in-session on Opus 4.8** via the
`/publish <slug>` slash command (no API), which splits the work into 9 focused steps
(titles, description+hashtags, timestamps, long-form tags, bibliography, shorts
clip-selection, shorts titles, shorts descriptions, shorts tags). The prompts are
single-sourced in `workflows/pipeline/08_publish.md`. This script now provides the two
deterministic bookends that bracket the in-session run, plus the legacy Gemini path:

  --signals   PRE-step. Derive the topic from the script, scrape YouTube autocomplete
              and write `.tmp/08_signals.md` for the in-session long-form-tags step to
              read.
  --finalize  POST-step. Read the in-session-written `md/08_publish.md`, then in place:
              annotate each shorts clip block with its script quarter (Q1–Q4), trim the
              long-form tag line to the 480-char budget, validate every Short has a clip
              block, and export `docx/08_publish.docx`.
  --api       Legacy fallback. Run the original 3-pass Gemini orchestrator end-to-end
              (titles → shorts → metadata) and write `md/08_publish.md` itself. Kept per
              the pipeline convention that Gemini paths survive behind `--api`.

Inputs:
  outputs/videos_pl/{slug}/docx/script_corrected.docx  (preferred — user-edited script)
  outputs/videos_pl/{slug}/docx/script.docx             (fallback — exported by agent4 --apply)
  outputs/videos_pl/{slug}/md/04_final.md               (last-resort fallback)
  outputs/videos_pl/{slug}/md/02_verified_research.md   (bibliography)

Outputs:
  outputs/videos_pl/{slug}/.tmp/08_signals.md           (--signals)
  outputs/videos_pl/{slug}/md/08_publish.md             (in-session /publish, or --api)
  outputs/videos_pl/{slug}/docx/08_publish.docx         (--finalize, or --api)

Usage:
    /publish "emotional-dysregulation-in-adhd"                          # in-session (preferred)
    python tools/pipeline/agent8_publish.py "<slug>" --signals          # PRE bookend
    python tools/pipeline/agent8_publish.py "<slug>" --finalize         # POST bookend
    python tools/pipeline/agent8_publish.py "<slug>" --api              # legacy Gemini fallback
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
from tools.utils import export_to_docx, get_env, get_output_dir, read_output, write_output, query_gemini_text as _query_gemini_base, read_script_docx_text

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESEARCH_FILENAME = "md/02_verified_research.md"
OUTPUT_FILENAME = "md/08_publish.md"
SIGNALS_FILENAME = ".tmp/08_signals.md"

GEMINI_MODEL = "gemini-3.1-pro-preview"

SCRIPT_CONTEXT_CHARS = 999_999
RESEARCH_CONTEXT_CHARS = 999_999

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

# ── Section Map ─────────────────────────────────────────────────────────────
# A. Shared helpers (narration loader, topic extractor, Gemini wrapper) ~L91
# B. --api: titles pass (build_titles_prompt, run_titles_pass)          ~L124
# C. --api: shorts pass (3 prompt builders, quarter annotator, runner)  ~L200
# D. --api: metadata pass (signals scraper, prompt, parser, runner)     ~L469
# E. --api: master output builder                                        ~L766
# F. --extract bookend (narration docx → .tmp/08_narration.md)          ~L798
# G. --signals bookend (autocomplete scrape -> .tmp/08_signals.md)      ~L841
# H. --finalize bookend (Q-tag annotation, tag trim, validate, docx)    ~L921
# I. --api: legacy 3-pass Gemini orchestrator                           ~L972
# J. CLI entry point (argparse + main)                                  ~L1036
# ────────────────────────────────────────────────────────────────────────────

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _load_narration(slug: str) -> str:
    """Load narration text with priority: script_corrected.docx > script.docx > 04_final.md."""
    base = get_output_dir(slug)
    for docx_rel in ("docx/script_corrected.docx", "docx/script.docx"):
        p = base / docx_rel
        if p.exists():
            print(f"  Script   : {docx_rel}")
            return read_script_docx_text(p)
    # fallback: 04_final.md (strip front matter)
    raw = read_output(slug, "md/04_final.md")
    print(f"  Script   : md/04_final.md (fallback)")
    return raw.split("\n---\n", 1)[1].strip() if "\n---\n" in raw else raw


def _extract_topic(script_content: str) -> str:
    for line in script_content.splitlines():
        line = line.strip()
        if line.startswith("# Script Final:"):
            return line[len("# Script Final:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _query_gemini(prompt: str, step_label: str, max_tokens: int = 16384) -> tuple[str, dict]:
    return _query_gemini_base(prompt, GEMINI_MODEL, max_tokens, step_label)


# ---------------------------------------------------------------------------
# Pass 1 — Titles & Hooks
# ---------------------------------------------------------------------------


def _build_titles_prompt(script_content: str) -> str:
    avoid_kw = ", ".join(f'"{k}"' for k in _BRAND_AVOID)
    return f"""\
OUTPUT LANGUAGE: Polish. All 5 title variants must be written in Polish for the Polish-language YouTube channel @sensumpolska.

You are an Advanced YouTube Metadata Engineer for the SENSUM channel — niche: behavioral science, neurobiology, emotional states. Your job is to generate identity-provocation titles that drive clicks while maintaining psychological credibility and emotional authenticity.

Read this script and generate exactly 5 long-form title variants. Each title must function as an **identity reframe, paradox, or system-level architectural reveal** — never as instruction, advice, or a list.

## TITLE ARCHITECTURE — Identity Provocation Blueprint

A qualifying title does ONE of the following:
- **Identity reframe** — names a state the viewer believes about themselves and inverts it ("To nie lenistwo. To alarm, który uruchamia twoja psychika.").
- **Paradox** — pairs two ideas the viewer assumes are opposites and reveals their unity ("Twój mózg widzi zagrożenie tam, gdzie widzisz sukces innych").
- **System-level architectural reveal** — describes the viewer's inner mechanism in everyday language the viewer didn't know applied to them ("Porównujesz swoje życie do cudzego montażu").

The viewer must feel addressed at the level of *identity* or *underlying mechanism* — not at the level of behavior or advice.

## LANGUAGE RULES (non-negotiable)

- **Natural spoken Polish** — as if said aloud by one person to another. No academic, clinical, or mechanistic register.
- **Emotional directness** — the title must hit an emotional truth or felt recognition in the first reading. If it sounds like a research abstract, rewrite it.
- **No abstract nouns as the grammatical subject** — do NOT write titles where the subject is "układ nerwowy", "mechanizm", "system", "instynkt", "reakcja fizjologiczna" or similar clinical/mechanistic nouns. Write from the viewer's perspective or name the mechanism in a felt, human way.
- **No trailing period.** Titles end without punctuation, OR with a question mark if using the question pattern.

## RECOMMENDED PATTERNS

- **Question + answer**: "Czujesz, że jesteś w tyle? Dlatego boli to aż tak mocno"
- **Contradiction**: "To nie lenistwo. To alarm, który uruchamia twoja psychika"
- **Viewer-perspective reframe**: "Dlaczego masz wrażenie, że wszyscy cię wyprzedzili"
- **Perceptual reveal**: "Nie jesteś w tyle. Porównujesz się do cudzego skrótu"

## HARD BANS (any of these auto-disqualifies a title)

- Instructional verbs: "how to", "jak się", "jak możesz", "ways to", "tips for", "stop", "fix".
- List formats: "5 …", "7 rzeczy …", any leading number used as a counter.
- Mechanistic subjects: titles beginning with "Twój układ nerwowy…", "Twój system przetrwania…", "Mechanizm…", "Instynkt…", "Reakcja fizjologiczna…"
- Advisory framing: "powinieneś", "musisz", "co musisz wiedzieć".
- Trailing period at the end of the title.
- Clickbait words: {avoid_kw}.

## BAD EXAMPLES vs GOOD EXAMPLES

❌ "Nie jesteś w tyle. Twój układ nerwowy analizuje błędne dane." — mechanistic subject, trailing period, abstract
❌ "Lęk przed spóźnieniem to poprawna reakcja fizjologiczna." — clinical register, sounds like a textbook
❌ "Twój system przetrwania reaguje na algorytm jak na stado." — mechanistic, abstract, not emotionally direct
✓ "Czujesz, że jesteś w tyle? Dlatego boli to aż tak mocno"
✓ "To nie lenistwo. To alarm, który uruchamia twoja psychika"
✓ "Dlaczego masz wrażenie, że wszyscy cię wyprzedzili"

## CONSTRAINTS

- Exactly 5 titles. Each under 70 characters.
- Specific to THIS script's actual content. Do not invent claims the script doesn't make.
- No quotation marks, no labels, no explanation. Numbered 1–5, title text only.
- Mix architectural modes across the 5 — at least 2 of the 3 modes (identity reframe / paradox / system reveal) must be represented.

Return ONLY the 5 numbered titles. No preamble, no commentary, no opening hooks, no closing remarks.

## Script

{script_content}
"""


def run_titles_pass(script_content: str) -> str:
    prompt = _build_titles_prompt(script_content)
    text, _ = _query_gemini(prompt, "pass 1 — titles", max_tokens=4096)
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
> [the FULL contiguous passage — every sentence of the Short in script order, no gaps, verbatim from the narration; the first line is the ~3s cold open]

---

## Narration Script

{narration}

## Candidate Analysis from Pass 1

{analysis}
"""


_SHORTS_BRAND_SYSTEM = """\
OUTPUT LANGUAGE: Polish. All generated titles, descriptions, and tags must be written in Polish for the Polish-language YouTube channel @sensumpolska. Script lines to clip are quoted verbatim from the Polish narration — do not translate them.

You are an Advanced YouTube Metadata Engineer writing Shorts lead-in packages for SENSUM — a long-form psychology channel for emotionally literate adults. Niche: behavioral science, neurobiology, emotional states. Each Short is a feed-lead-in: its job is to map the viewer's cognitive dissonance in 30 seconds and drive a click to the Related Video anchor.

Brand voice for Shorts descriptions (warm, validating — title voice differs):
- State the claim directly in the speaker's own voice. Grounded in the viewer's lived experience.
- Research is invisible. Do NOT use: "researchers found", "studies show", "scientists discovered", "research suggests", "according to researchers", "studies suggest", "research shows", "the science is clear". The viewer trusts the speaker, not the citation. Never name researchers or cite study years.
- Never use: hack, secret, shocking, toxic, red flags, wake up, brutally honest, you won't believe.
- Brand promise: "You are not broken. Here's what the science says."

Title rules:
- Produce exactly ONE title per Short (not a list of candidates).
- Maximum 60 characters. No trailing period.
- High-impact reframe: identity-reframe, paradox, or system-architectural reveal.
- Language: natural spoken Polish — emotionally direct, from the viewer's perspective. No mechanistic or academic register.
- Recommended patterns: contradiction ("To nie jest X. To Y."), viewer-direct question ("Dlaczego X uruchamia w tobie Y"), direct psychological statement.
- Polish examples of the right shape: "Dlaczego cudzy sukces uruchamia w tobie panikę" / "To nie jest jedno uczucie. To dwa różne alarmy" / "Porównujesz swoje życie do cudzego montażu"
- Never instructional ("Jak…", "Tips for…", "5 ways…"). Never ends with a period.

Description rules:
- Exactly 2 sentences — first names the viewer's experience, second delivers the psychological reframe or mechanism (no jargon).
- End with: #Shorts #psychologia plus 1 single-word lowercase topic hashtag matching the Short's theme (e.g. #presja #stres #lek #smutek #emocje). Each hashtag must be ONE WORD — no spaces, no Polish diacritics in hashtags (use #lek not #lęk).

Backend Tag Block rules (kept tight — Shorts algorithm barely reads backend tags; the real categorization signal is the description hashtags):
- 3–5 multi-word intent phrases per Short. Each phrase 2–4 words. Comma-separated, no `#` prefix.
- Tag #1 is the strongest search-shaped phrase that maps to THIS Short's core claim — treat it as the primary keyword for the Short.
- Every phrase must be extracted from (or be a direct paraphrase of the search intent behind) THIS Short's quoted lines.
- SINGLE-WORD TAGS ARE PROHIBITED. "psychology", "anxiety", "trauma" cause semantic dilution. The only single-word allowance is the brand handle "SENSUM" (uppercase), included ONCE.
- Be careful with metaphors. The Short may use vivid analogies (cookie, GPS, village, battery, door). Those illustrate the idea; they are not the idea. Tag the underlying concept, never the prop.
- Tags tuned to THIS Short's specific angle, not the parent video as a whole. Quality over quantity — 3 strong tags beats 5 padded with filler.

Script Lines to Clip rules:
- ONE verbatim block: the `**Script Lines to Clip:**` label, then the FULL contiguous passage as `> ` quoted lines — every sentence of the Short in script order, no gaps. The first quoted line is the ~3s cold open; the rest carries the main claim through to the curiosity-gap cut.
- Quote it verbatim from the narration script — same words, same punctuation. No paraphrasing, no summarising. This is the exact span the editor cuts from the recorded audio, so it must be the COMPLETE passage, not just the opening line and the punchline.
- The passage must land in the 25–70 second range read aloud at conversational pace (~50–150 words). A two-line hook-plus-punchline block is too short — include the connective body that lives between them.
"""


def _build_shorts_pass3_prompt(narration: str, shorts_text: str) -> str:
    return f"""\
{_SHORTS_BRAND_SYSTEM}

Below are the **selected** YouTube Shorts (between 1 and 4 — Pass 2 returned only those candidates that passed the Triple Retention Filter as a hard AND-gate). For each Short Pass 2 provided, add **Title**, **Description**, **Tags**, and carry forward Pass 2's **Script Lines to Clip** block verbatim (the full contiguous passage). **DROP** the `**Why this works:**` line — it was Pass 2's internal selection justification and does not appear in the final published output.

HARD RULES (violating any of these breaks downstream tooling):

1. **DROP the `**Why this works:**` line entirely.** It is not part of the final output. Do not rephrase it as a description, do not preserve it as a comment, do not move it elsewhere. Delete it.

2. **Exactly ONE of each labelled field per Short.** Under each `## Short N` heading there must be exactly one `**Title:**` line, exactly one `**Description:**` line, exactly one `**Tags:**` line, and exactly one `**Script Lines to Clip:**` block. NEVER output two of any field under the same Short.

3. **VALIDATION GATE — read this BEFORE writing each Short.** For each Short, before writing ANY field (Title / Description / Tags / Script Lines), check: do I have the full contiguous verbatim passage (≥ ~50 words, not just an opening line and a punchline) sourced from Pass 2 or the Narration Script? If NO, OMIT that Short entirely — do not write its Title, Description, or Tags. Move on to the next Short. **A 3-Short output with all four fields intact on every Short is REQUIRED. A 4-Short output with one missing Script Lines block is REJECTED downstream and triggers a regeneration cost.**

   The `**Script Lines to Clip:**` block format:
   - The `**Script Lines to Clip:**` label, then the FULL contiguous passage as consecutive `> ` quoted lines — every sentence of the Short in script order, no gaps, verbatim from Pass 2 or the Narration Script. No paraphrasing.
   - The first quoted line is the ~3s cold open; the passage runs through to the curiosity-gap cut. Target 50–150 words (25–70s read aloud) — never just an opening line plus a punchline with the body dropped.
   If Pass 2 provided only a short fragment, extend it to the full contiguous passage using the surrounding sentences in the Narration Script (verbatim). If no contiguous passage reaches ~50 words, OMIT THE WHOLE SHORT (validation gate above).

4. **Field order is LOCKED:** under each `## Short N — [angle tag]` heading, the lines must appear in this exact order — and no others:
   - `**Title:**` (single title, max 60 chars, identity-reframe / paradox / system-reveal blueprint)
   - `**Description:**` (1–2 sentences mapping the cognitive dissonance, ending with `#Shorts #x #y`)
   - `**Tags:**` (3–5 multi-word intent phrases, comma-separated, no `#` prefix)
   - `**Script Lines to Clip:**` (followed immediately by the full contiguous passage as consecutive `> ` quoted lines — the entire Short, in script order, no gaps)

5. **Tags — KEEP TIGHT.** 3–5 multi-word intent phrases per Short, each 2–4 words, comma-separated, no `#` prefix. Single-word tags are PROHIBITED (semantic dilution). Brand exception: SENSUM appears once (uppercase) as the only single-word entry. Every phrase extractable from THIS Short's quoted lines or a direct-intent paraphrase. Backend tags are a categorization safety net on Shorts, not a discovery driver — the description hashtags carry the real algorithmic signal.

6. **Description:** state the claim directly in the speaker's own voice. NO research-framing language — no "researchers found", no "studies show", no "scientists discovered", no "research suggests", no "according to researchers". The viewer trusts the speaker, not the citation.

7. **Title:** identity-reframe, paradox, or system-architectural reveal. NEVER instructional, advisory, or list-format. Max 60 characters.

8. **Keep the `---` separators between Shorts and the heading line `## Short N — [angle tag]` exactly as Pass 2 produced them.**

Output one full block per Short Pass 2 provided, with the new fields included. No preamble, no commentary outside the blocks.

## Narration Script (for context — use to extend each clip to the full contiguous passage and to verify the lines are verbatim)

{narration}

## Selected Shorts from Pass 2

{shorts_text}
"""


_QUARTER_LABEL_RE = re.compile(r"^(\*\*Script Lines to Clip:\*\*)\s*(?:\[Q[1-4?]\])?\s*$")


def _annotate_script_quarters(narration: str, shorts_text: str) -> str:
    """Tag each `**Script Lines to Clip:**` block with the script quarter (Q1–Q4) of its passage.

    Splits the narration into four equal-word-count quarters, then for every
    `**Script Lines to Clip:**` label in the Shorts text, finds the first
    following `> …` line (the opening line of the verbatim passage) and appends
    `[Q1] / [Q2] / [Q3] / [Q4]` to the label based on where that passage starts
    in the narration. The editor uses the marker to locate the cut in DaVinci by
    text-search within the right quarter of the script. Falls back to `[Q?]`
    when no match is found, so failures are visible rather than silent. A
    `[MISSING …]` placeholder line is left untouched (the regex only matches a
    bare label or one already carrying a `[Q…]` marker, so re-runs are idempotent).
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
            block = block.rstrip() + "\n\n**Script Lines to Clip:** [MISSING — model dropped this block; locate the lines manually in script_corrected.docx/script.docx or rerun the Shorts pass]\n\n---\n"
        output_blocks.append(block)
    return "".join(output_blocks), broken


# A Shorts clip block is the verbatim passage the editor cuts. ~2 words/sec at
# conversational Polish pace → 25–70 s ≈ 50–150 words (the STEP 6 target). The
# window below adds a small margin on each side so only genuinely off blocks warn.
_CLIP_WORD_FLOOR = 45
_CLIP_WORD_CEIL = 170


def _clip_block_word_counts(shorts_text: str) -> list[tuple[int, int]]:
    """Return (short_number, word_count) for every Short's clip-block passage.

    Counts the words inside the `> ` quoted passage under each
    `**Script Lines to Clip:**` label — the verbatim lines the editor actually
    cuts. `>` prefixes and the quarter marker are stripped. `[MISSING]`
    placeholder blocks are skipped (the validator already warns about those), so
    this guard speaks only to real passages that are too short or too long.
    """
    counts: list[tuple[int, int]] = []
    for block in re.split(r"(?m)(?=^## Short \d+)", shorts_text):
        header_match = re.match(r"^## Short (\d+)", block)
        if not header_match:
            continue
        in_clip = False
        words = 0
        for line in block.splitlines():
            stripped = line.strip()
            if stripped.startswith("**Script Lines to Clip:**"):
                if "MISSING" in stripped:
                    in_clip = False
                    break
                in_clip = True
                continue
            if in_clip:
                if stripped.startswith(">"):
                    words += len(stripped.lstrip("> ").split())
                elif stripped.startswith("---") or stripped.startswith("## Short"):
                    break
        if in_clip:
            counts.append((int(header_match.group(1)), words))
    return counts


def run_shorts_pass(narration: str) -> str:
    analysis, _ = _query_gemini(_build_shorts_pass1_prompt(narration), "shorts pass 1 — candidate mapping", max_tokens=16384)
    shorts_text, _ = _query_gemini(_build_shorts_pass2_prompt(narration, analysis), "shorts pass 2 — selection", max_tokens=16384)
    enhanced, _ = _query_gemini(_build_shorts_pass3_prompt(narration, shorts_text), "shorts pass 3 — titles and descriptions", max_tokens=16384)
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


def _build_metadata_prompt(topic: str, script: str, research: str, suggestions: list[str], titles_text: str = "") -> str:
    avoid_kw = ", ".join(f'"{k}"' for k in _BRAND_AVOID)
    suggestions_block = (
        "\n".join(f"- {s}" for s in suggestions[:300])
        if suggestions
        else "(unavailable)"
    )
    titles_block = titles_text.strip() if titles_text.strip() else "(unavailable)"

    return f"""\
OUTPUT LANGUAGE: Polish. The video description, chapter labels, and all YouTube tags must be written in Polish for the Polish-language YouTube channel @sensumpolska.

You are an **Advanced YouTube Metadata Engineer and NLP Optimization Pipeline** for the SENSUM channel. Niche: behavioral science, neurobiology, emotional states. Your sole purpose is to convert raw script data and research into a highly optimized Publish Package designed to **bypass the Pre-sampling Queue and accelerate Impression Velocity**.

Execute every task with cold, empirical, mathematical precision. The OUTPUT you produce (description body, references) is warm and validating in the speaker's voice — but your decision logic for tag selection, NLP anchoring, and E-E-A-T construction is algorithmic. You are not writing prose for the viewer to enjoy; you are constructing an NLP surface for YouTube's discovery pipeline.

Operating principles:
- A tag is a search query, not a vocabulary word. If you can't picture a real person living this problem typing it into YouTube search, it has no place in the tag block.
- **Tag #1 carries the most algorithmic weight.** YouTube front-loads semantic weight onto the first tag in the list. Tag #1 must be the **exact-match primary keyword** of the video — a search-shaped phrase extracted from (or paraphrased from) the strongest of the 5 candidate titles provided above. The remaining tags then cluster around this primary keyword.
- Prefer multi-word phrases (≥2 words) — they carry more search intent. The only mandatory exceptions are the brand handle "SENSUM" (one slot, uppercase) and up to 2 high-value single-word Polish psychology anchors (e.g. "psychologia", "emocje") when no multi-word phrase captures the same search better.
- Metaphors and props in the script (cookies, batteries, GPS, doors, villages) are illustrations, not search terms. Tag the underlying mechanism the metaphor points to.
- Established clinical and pop-psychology terms (rumination, regulation, attachment, burnout, masking, anhedonia, limerence) are what serious viewers actually search for — render them inside multi-word phrases that match real search behavior.
- E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) is established through the formal bibliography, not the description prose.

## Description Architecture

Write the description in exactly **5 sentences**. Natural prose — not fragments, not a list. Total under 80 words.

Sentence structure (follow this order):
1. The viewer's experience — a specific, felt moment or pattern that drives them to search for this video. Start from their daily life, not from an abstract concept.
2. Psychological reframe — gently reassure that this experience doesn't mean something is wrong with them; name the mechanism in plain everyday Polish (no jargon).
3. What the film covers — a brief "W tym filmie..." sentence summarizing the core topic.
4. Additional context — one more thing the video covers or reveals.
5. CTA — a warm, direct invitation to watch: "Jeśli chcesz [benefit], obejrzyj i posłuchaj do końca."

Good example (do not copy verbatim):
"Czasem wystarczy kilka minut scrollowania, żeby pojawiło się przytłaczające wrażenie, że wszyscy są już dalej niż ty. To uczucie nie musi oznaczać, że coś z tobą jest nie tak — często jest po prostu reakcją układu nerwowego na ciągłe porównywanie się z cudzymi wycinkami życia. W tym filmie pokazuję, skąd bierze się poczucie bycia w tyle i dlaczego potrafi tak mocno uderzać w ciało oraz psychikę. Opowiadam też, jak algorytmy i presja społeczna wzmacniają ten fałszywy alarm. Jeśli chcesz lepiej zrozumieć siebie i poczuć trochę ulgi, obejrzyj i posłuchaj do końca."

Hard rules for the description:
- Exactly 5 sentences. Count them. If you write 4 or 6, rewrite.
- NO researcher names, NO study years, NO Latin-sounding jargon
- NO fragment-style lines (no "Nocne scrollowanie. Kolejne zaręczyny." openers)
- NO second-person preachy lines
- NO clickbait words: {avoid_kw}
- Natural conversational Polish — as if spoken directly to one person

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

**CRITICAL: Do NOT translate Concept Labels into Polish.** Use the exact English concept label as it appears in the Verified Research section, or a short English paraphrase if no label is given. The bibliography is a scientific reference list — concept labels must remain in English.

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

---

## Task

Return a single JSON object. No preamble, no commentary outside the JSON block.

```json
{{
  "description_hook": "Exactly 5 sentences of natural Polish prose (viewer's experience, reframe, \\"W tym filmie...\\", extra context, CTA) — under 80 words, no fragments.",
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
- `description_hook`: the full description body — exactly 5 sentences of natural Polish prose (no fragments, no list), under 80 words total, following the Description Architecture above. The `Rozdziały:` and `Badania i źródła:` sections are appended by downstream tooling — do NOT include them in this field.
- `chapters`: detect natural section breaks from ## headings or bold section labels in the script. Produce 6–12 chapters. Labels: a full sentence or question from the viewer's navigation perspective — what will the viewer find in this section? Write labels as "Skąd bierze się poczucie, że jesteś w tyle" or "Jak algorytmy wzmacniają ten alarm" — NOT dry technical single-word labels like "Mechanizm" or academic phrases like "Pułapka fałszywej średniej". First chapter `"placeholder"` is always `"00:00"` and its label should name the actual opening topic of the video (not the word "Wprowadzenie"). All others use `"[XX:XX]"` as placeholder.
- `hashtags`: Produce 3 hashtags only. Single-word, lowercase, with `#` prefix. First hashtag is always `#sensum`. The other 2 are the single-word core topic + one single-word concept from the script (e.g. `#sensum #willpower #grit`). NO multi-word hashtags, NO camelCase combinations, NO spaces inside a hashtag. The hashtags block is the ONLY single-word survivor — the YouTube Tags field is exclusively multi-word (≥2 words; the SENSUM brand slot is the sole single-word exception).
- `tags`: **THE TAG PROTOCOL — NON-NEGOTIABLE.**
  - Produce **5–8 tags total**. Comma-separated, no `#` prefix. 2026 YouTube SEO consensus: 5–8 highly relevant tags outperform padded 10–15 lists. Quality over quantity.
  - **SLOT STRUCTURE — order by algorithmic weight (front-loaded):**
    - **Tag #1 (mandatory): the exact-match primary keyword for this video.** Extracted from the strongest of the candidate titles above, OR a more search-shaped paraphrase if the identity-provocation title is metaphor-heavy and would not autocomplete in YouTube search. Multi-word. This slot does the heaviest discovery work.
    - **Tags #2–#6: long-tail intent phrases.** 2–4 words each. Mix: close paraphrases of the primary keyword, lived-experience phrasing ("dlaczego zawsze zaczynam od nowa"), clinical/mechanism phrases rendered as searches ("rozregulowanie układu nerwowego", "pętla ruminacji").
    - **SENSUM**: include exactly once (uppercase). Brand tag, single-word permitted.
    - **Optional: up to 2 single-word Polish psychology anchors** (e.g. "psychologia", "emocje") — use ONLY if no multi-word phrase captures the same high-volume search better.
  - **The intent test.** For each phrase: *"Would a real person living this problem type these exact words into YouTube search?"* If not, cut it.
  - Tag metaphors by underlying concept, not the prop (e.g. wyczerpanie woli, not bateria).
  - Every phrase must be extractable from the script's language OR a direct paraphrase of the search intent the chosen title surfaces.
  - **Total comma-separated string must stay under 480 characters** (500-char YouTube hard cap minus safety margin). Order is STRONGEST FIRST — the post-pass trimmer drops from the tail if you overrun."""


def _parse_metadata(response: str) -> dict:
    match = re.search(r"```json\s*([\s\S]+?)\s*```", response)
    if match:
        return json.loads(match.group(1))
    match = re.search(r"\{[\s\S]+\}", response)
    if match:
        return json.loads(match.group(0))
    raise ValueError("No JSON found in Gemini response.")


def _trim_tags_to_budget(tags: list[str], char_budget: int = 480) -> list[str]:
    """Trim tags from the END of the list until the comma-joined string fits.

    Preserves the SENSUM brand-exception slot regardless of position. Trims
    non-SENSUM entries from the tail inward — the prompt instructs Gemini to
    front-load by algorithmic weight (Tag #1 = exact-match primary keyword,
    Tags #2–#5 = strongest variations, tail = broader anchors), so end-trimming
    preserves the highest-weight slots. Budget defaults to 480 to leave
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

    prompt = _build_metadata_prompt(topic, script, research, suggestions, titles_text)
    raw, _ = _query_gemini(prompt, "pass 3 — YouTube metadata", max_tokens=8192)

    meta = _parse_metadata(raw)

    raw_tags = meta.get("tags", [])
    trimmed_tags = _trim_tags_to_budget(raw_tags)
    meta["tags"] = trimmed_tags
    tags_len = len(", ".join(trimmed_tags))
    dropped = len(raw_tags) - len(trimmed_tags)
    if dropped > 0:
        print(f"  Tag block: {len(trimmed_tags)} tags, {tags_len} chars (trimmed {dropped} from tail to fit 480-char target; doctrine 12–15; YouTube cap is 500)")
    else:
        within_doctrine = "within doctrine" if 12 <= len(trimmed_tags) <= 15 else f"OUTSIDE doctrine 12–15"
        print(f"  Tag block: {len(trimmed_tags)} tags, {tags_len} chars ({within_doctrine}; under 480-char target; YouTube cap is 500)")

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

Rozdziały:
{chapters_block}

Badania i źródła:
{bib_block}

{hashtags_line}

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
# In-session bookends — --signals (PRE) and --finalize (POST)
# ---------------------------------------------------------------------------


NARRATION_FILENAME = ".tmp/08_narration.md"


def run_extract(slug: str) -> None:
    """Write the resolved narration to `.tmp/08_narration.md` for the in-session steps.

    Claude's Read tool can't parse `.docx`, so `/publish` calls this first to
    materialize the narration (resolved via the standard
    script_corrected.docx > script.docx > 04_final.md priority) as plain text
    the in-session steps can read. Mirrors `agent5_visuals.py --extract`.
    """
    print(f"\n=== Agent 8 --extract (narration -> {NARRATION_FILENAME}) ===")
    print(f"Slug : {slug}\n")
    narration = _load_narration(slug)
    path = write_output(slug, NARRATION_FILENAME, narration)
    print(f"  Narration: {len(narration):,} chars")
    print(f"  Saved: {path}")


def _derive_seed_topic(slug: str, narration: str) -> str:
    """Best-effort Polish search seed for autocomplete: research heading > script heading.

    The preferred script source (`script_corrected.docx`) has its headings
    stripped on extraction, so `_extract_topic` returns "Unknown Topic" for it.
    Fall back to the first `# ` heading of `02_verified_research.md` (strip a
    leading `Verified Research:` prefix). The `/publish` command overrides this
    entirely by passing `--topic=` with a seed it derived from the chosen title.
    """
    topic = _extract_topic(narration)
    if topic != "Unknown Topic":
        return topic
    try:
        research = read_output(slug, RESEARCH_FILENAME)
    except FileNotFoundError:
        return topic
    for line in research.splitlines():
        line = line.strip()
        if line.startswith("# "):
            heading = line[2:].strip()
            for prefix in ("Verified Research:", "Research:"):
                if heading.startswith(prefix):
                    heading = heading[len(prefix):].strip()
            return heading or topic
    return topic


def run_signals(slug: str, topic_override: str = "") -> None:
    """PRE bookend: write `.tmp/08_signals.md` for the in-session long-form-tags step.

    Determines a Polish search seed (`--topic=` override from `/publish`, else
    the research/script heading), scrapes YouTube autocomplete (alphabet-soup)
    and writes it into a small markdown file the `/publish` long-form-tags step
    reads. Fails soft — if the network is down the suggestions block is
    `(unavailable)` and the in-session step proceeds on the script alone.
    """
    print(f"\n=== Agent 8 --signals (autocomplete) ===")
    print(f"Slug : {slug}\n")

    narration = _load_narration(slug)
    topic = topic_override.strip() if topic_override.strip() else _derive_seed_topic(slug, narration)
    print(f"  Topic    : {topic}")

    print("  Scraping YouTube autocomplete suggestions...")
    suggestions: list[str] = []
    try:
        suggestions = _alphabet_soup(topic)
        print(f"  Collected {len(suggestions)} unique suggestions")
    except Exception as exc:
        print(f"  Warning: Autocomplete scraping failed ({exc}).")

    suggestions_block = (
        "\n".join(f"- {s}" for s in suggestions[:300]) if suggestions else "(unavailable)"
    )

    content = f"""\
# Agent 8 signals — {topic}
_Generated: {date.today().isoformat()} · deterministic --signals pre-step_

Transient input for the `/publish` long-form-tags step. Not a deliverable.

## Audience Search Signals (YouTube autocomplete)
{suggestions_block}
"""
    path = write_output(slug, SIGNALS_FILENAME, content)
    print(f"\n  Saved: {path}")
    print(f"  The /publish long-form-tags step reads this file.")


def _trim_tags_in_markdown(text: str) -> tuple[str, int, int]:
    """Trim the long-form `## YouTube Tags` line in the master file to budget.

    Finds the first non-empty content line under the `## YouTube Tags …`
    heading, treats it as a comma-separated tag list, applies the list-based
    `_trim_tags_to_budget`, and rewrites it in place. Returns the new text plus
    the final tag count and char length for diagnostics. If no tags section is
    found the text is returned unchanged with (-1, -1).
    """
    lines = text.splitlines()
    heading_idx = next(
        (i for i, ln in enumerate(lines) if ln.strip().lower().startswith("## youtube tags")),
        None,
    )
    if heading_idx is None:
        return text, -1, -1
    for j in range(heading_idx + 1, len(lines)):
        candidate = lines[j].strip()
        if not candidate or candidate == "---":
            continue
        tags = [t.strip() for t in candidate.split(",") if t.strip()]
        trimmed = _trim_tags_to_budget(tags)
        lines[j] = ", ".join(trimmed)
        return "\n".join(lines), len(trimmed), len(lines[j])
    return text, -1, -1


def run_finalize(slug: str) -> None:
    """POST bookend: deterministically post-process the in-session master file.

    Reads the `md/08_publish.md` that `/publish` wrote in-session, then in place:
    annotates every shorts clip block with its script quarter (Q1–Q4), trims the
    long-form tag line to the 480-char budget, validates that every Short carries
    a `**Script Lines to Clip:**` block (loud `[MISSING]` placeholder otherwise),
    warns on any clip passage outside the 25–70s word window, and exports the
    Word version.
    """
    print(f"\n=== Agent 8 --finalize (Q1–Q4 + tag trim + validate + docx) ===")
    print(f"Slug : {slug}\n")

    try:
        master = read_output(slug, OUTPUT_FILENAME)
    except FileNotFoundError:
        print(f"Error: {OUTPUT_FILENAME} not found — run /publish {slug} first to generate it.")
        sys.exit(1)

    narration = _load_narration(slug)

    # 1. Quarter annotation on shorts clip blocks.
    annotated = _annotate_script_quarters(narration, master)

    # 2. Validate every Short has a clip block.
    validated, broken = _validate_shorts_clip_blocks(annotated)
    if broken:
        print(f"  WARNING: Shorts {broken} missing `**Script Lines to Clip:**` block — placeholder inserted")

    # 3. Trim the long-form tag line to budget.
    trimmed_text, tag_count, tag_chars = _trim_tags_in_markdown(validated)
    if tag_count >= 0:
        print(f"  Tag block: {tag_count} tags, {tag_chars} chars (trimmed to 480-char target; YouTube cap is 500)")
    else:
        print("  Note: no `## YouTube Tags` section found to trim")

    # 4. Detect any unresolved [Q?] markers so the failure is visible.
    q_unmatched = trimmed_text.count("[Q?]")
    if q_unmatched:
        print(f"  WARNING: {q_unmatched} clip quote(s) did not substring-match the narration ([Q?]) — fix the quote or regenerate that Short")

    # 5. Warn on clip passages outside the 25–70s window (the recurring "too short" failure).
    for short_num, wc in _clip_block_word_counts(trimmed_text):
        if wc < _CLIP_WORD_FLOOR:
            print(f"  WARNING: Short {short_num} clip passage is only ~{wc} words (<{_CLIP_WORD_FLOOR}) — too short for a 25–70s Short; extend it to the full contiguous passage or drop the Short")
        elif wc > _CLIP_WORD_CEIL:
            print(f"  WARNING: Short {short_num} clip passage is ~{wc} words (>{_CLIP_WORD_CEIL}) — likely too long for a Short; tighten to one contiguous passage")

    write_output(slug, OUTPUT_FILENAME, trimmed_text.rstrip("\n") + "\n")
    docx_path = export_to_docx(slug, OUTPUT_FILENAME, "docx/08_publish.docx")
    print(f"\n  Finalized: {OUTPUT_FILENAME}")
    print(f"  Word export: {docx_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run_api_pipeline(slug: str) -> None:
    """Legacy 3-pass Gemini orchestrator (titles → shorts → metadata)."""
    print(f"\n=== Agent 8: Publish Package (--api Gemini fallback) ===")
    print(f"Slug : {slug}")
    print()

    # Load inputs
    print("[1/4] Reading input files...")
    narration = _load_narration(slug)

    try:
        research = read_output(slug, RESEARCH_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print(f'\nRun Agent 2 first:\n  python tools/agent2_verify.py "{slug}"')
        sys.exit(1)

    topic = _extract_topic(narration)
    print(f"  Topic    : {topic}")
    print(f"  Narration: {len(narration):,} chars")
    print(f"  Research : {len(research):,} chars")

    # Pass 1 — Titles & Hooks
    print(f"\n[2/4] Pass 1 — Titles & Hooks...")
    try:
        titles_text = run_titles_pass(narration)
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
        meta = run_metadata_pass(topic, narration, research, titles_text)
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

    docx_path = export_to_docx(slug, OUTPUT_FILENAME, "docx/08_publish.docx")
    print(f"  Word export: {docx_path}")

    print(f"\nDone. Review {OUTPUT_FILENAME} before uploading to YouTube.")


def _usage() -> None:
    print('Usage: python tools/pipeline/agent8_publish.py "<slug>" [--extract | --signals | --finalize | --api]')
    print()
    print("  (preferred) generate the package in-session:  /publish <slug>")
    print("  --extract   materialize narration -> .tmp/08_narration.md (docx Claude can't Read)")
    print("  --signals   PRE bookend: scrape autocomplete -> .tmp/08_signals.md")
    print("  --finalize  POST bookend: Q1-Q4 + tag trim + validate + docx over md/08_publish.md")
    print("  --api       legacy Gemini 3-pass orchestrator (writes md/08_publish.md itself)")


def main() -> None:
    args = [a for a in sys.argv[1:]]
    flags = {a.split("=", 1)[0] for a in args if a.startswith("--")}
    topic_override = next(
        (a.split("=", 1)[1] for a in args if a.startswith("--topic=")), ""
    )
    positional = [a for a in args if not a.startswith("--")]

    if not positional or not positional[0].strip():
        _usage()
        sys.exit(1)
    slug = positional[0].strip()

    if "--extract" in flags:
        run_extract(slug)
    elif "--signals" in flags:
        run_signals(slug, topic_override)
    elif "--finalize" in flags:
        run_finalize(slug)
    elif "--api" in flags:
        run_api_pipeline(slug)
    else:
        print("No mode flag given. The publish package is generated in-session:\n")
        print(f"    /publish {slug}\n")
        print("That slash command calls this script's --signals and --finalize bookends for you.")
        print("To run the legacy Gemini pipeline end-to-end instead, pass --api.\n")
        _usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
