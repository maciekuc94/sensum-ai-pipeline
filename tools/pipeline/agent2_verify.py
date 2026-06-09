"""
Agent 2: Science Verification
Reads the research document produced by Agent 1 and uses Vertex AI Gemini 3.1
Pro to verify every factual claim against peer-reviewed sources.

Usage:
    python tools/pipeline/agent2_verify.py "emotional-dysregulation-in-adhd"

Takes the SLUG (not the topic) because research was already done by Agent 1.
"""

import sys
import os
import re
from pathlib import Path
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import read_output, write_output, get_env

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESEARCH_FILENAME = "md/01_research.md"
OUTPUT_FILENAME = "md/02_verified_research.md"

VERIFY_TEMPERATURE = 0.0  # deterministic — verification is a correctness gate

# ---------------------------------------------------------------------------
# Vertex AI / Gemini
# ---------------------------------------------------------------------------

def _load_prompt() -> str:
    """Load verification prompt from workflows/pipeline/02_verify_prompt.md."""
    path = Path(__file__).parent.parent.parent / "workflows" / "pipeline" / "02_verify_prompt.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [l for l in lines if not l.startswith("#") and not l.startswith("<!--")]
    return "\n".join(body).strip()

VERIFICATION_PROMPT_TEMPLATE = _load_prompt()


GEMINI_MODEL = "gemini-3.1-pro-preview"


def query_gemini_verify(research_content: str) -> tuple[str, dict]:
    """Send the research document to Gemini for claim-by-claim verification.
    Returns (text, usage_dict)."""
    try:
        import google.genai as genai
        from google.genai import types

        project = get_env("GOOGLE_CLOUD_PROJECT")
        location = "global"

        print(f"  Initializing google-genai client (project={project}, location={location})...")
        client = genai.Client(vertexai=True, project=project, location=location)

        # Extract the peer-reviewed abstracts as the grounding source.
        # Agent 1 now writes "## Peer-Reviewed Sources" (PubMed + Europe PMC);
        # fall back to the legacy "## PubMed Results" heading
        # so older research files still verify.
        pubmed_abstracts = ""
        for heading in ("## Peer-Reviewed Sources", "## PubMed Results"):
            if heading in research_content:
                pubmed_abstracts = research_content.split(heading)[1].split("\n##")[0].strip()
                break

        prompt = VERIFICATION_PROMPT_TEMPLATE.format(
            pubmed_abstracts=pubmed_abstracts or "_No PubMed abstracts available — flag all claims._",
            research_content=research_content,
        )

        print(f"  Querying {GEMINI_MODEL} for claim verification...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            # gemini-3.1-pro-preview emits variable thinking tokens (~5k+ observed).
            # 8192 was too tight: when thinking spiked it consumed the whole budget,
            # truncating the answer to empty (MAX_TOKENS) — a nondeterministic failure.
            # With the larger multi-source grounding pool there are more claims to
            # verify, so 24576 gives headroom for thinking + a longer claim list.
            config=types.GenerateContentConfig(
                max_output_tokens=24576,
                temperature=VERIFY_TEMPERATURE,
            ),
        )

        usage = {"model": GEMINI_MODEL, "input_tokens": 0, "output_tokens": 0}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
            usage["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

        return response.text, usage

    except EnvironmentError as exc:
        print(f"  [WARNING] Gemini skipped — missing env var: {exc}")
        return "", {}
    except Exception as exc:
        print(f"  [WARNING] Gemini verification failed: {exc}")
        return "", {}


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _extract_topic_from_research(research_content: str) -> str:
    """Extract the topic from the first heading of the research file."""
    for line in research_content.splitlines():
        line = line.strip()
        if line.startswith("# Research:"):
            return line[len("# Research:"):].strip()
        if line.startswith("# "):
            return line[2:].strip()
    return "Unknown Topic"


def _split_blocks(raw: str) -> list[str]:
    """
    Split the raw Gemini response into individual claim blocks.
    Each block starts with one of the three recognised headers.
    """
    pattern = re.compile(
        r"(?=(?:VERIFIED CLAIM:|FLAGGED CLAIM:|REMOVED CLAIM:))",
        re.IGNORECASE,
    )
    parts = pattern.split(raw)
    # Discard leading whitespace / preamble (anything before the first header)
    return [p.strip() for p in parts if p.strip()]


def _field(block: str, key: str) -> str:
    """Extract a single-line field value from a claim block, e.g. SOURCE: ..."""
    pattern = re.compile(rf"^{re.escape(key)}:?\s*(.+)$", re.IGNORECASE | re.MULTILINE)
    m = pattern.search(block)
    return m.group(1).strip() if m else ""


def _claim_text(block: str, header: str) -> str:
    """
    Extract the free-text claim body that follows the header line and precedes
    the first labelled field (SOURCE:, REASON:, CONFIDENCE:, NOTE:).
    """
    # Remove the header line itself
    body = re.sub(
        rf"^{re.escape(header)}:?\s*", "", block, count=1, flags=re.IGNORECASE
    ).strip()
    # Keep only lines up to (but not including) the first field marker
    lines: list[str] = []
    for line in body.splitlines():
        if re.match(r"^(SOURCE|REASON|CONFIDENCE|NOTE):?\s*", line, re.IGNORECASE):
            break
        lines.append(line)
    return " ".join(lines).strip()


def parse_gemini_response(raw: str) -> dict:
    """
    Parse the structured Gemini response into three lists:
      verified  — list of dicts: {claim, source, confidence, note}
      flagged   — list of dicts: {claim, source, reason}
      removed   — list of dicts: {claim, reason}

    Returns a dict with those three keys plus 'parse_succeeded' bool.
    """
    verified: list[dict] = []
    flagged: list[dict] = []
    removed: list[dict] = []

    try:
        blocks = _split_blocks(raw)
        if not blocks:
            return {"verified": verified, "flagged": flagged, "removed": removed, "parse_succeeded": False}

        for block in blocks:
            upper = block.upper()
            if upper.startswith("VERIFIED CLAIM"):
                verified.append({
                    "claim": _claim_text(block, "VERIFIED CLAIM"),
                    "source": _field(block, "SOURCE"),
                    "confidence": _field(block, "CONFIDENCE"),
                    "note": _field(block, "NOTE"),
                })
            elif upper.startswith("FLAGGED CLAIM"):
                flagged.append({
                    "claim": _claim_text(block, "FLAGGED CLAIM"),
                    "source": _field(block, "SOURCE"),
                    "reason": _field(block, "REASON"),
                })
            elif upper.startswith("REMOVED CLAIM"):
                removed.append({
                    "claim": _claim_text(block, "REMOVED CLAIM"),
                    "reason": _field(block, "REASON"),
                })

        parse_succeeded = bool(verified or flagged or removed)
        return {
            "verified": verified,
            "flagged": flagged,
            "removed": removed,
            "parse_succeeded": parse_succeeded,
        }

    except Exception as exc:
        print(f"  [WARNING] Parsing failed: {exc}")
        return {"verified": verified, "flagged": flagged, "removed": removed, "parse_succeeded": False}


# ---------------------------------------------------------------------------
# Markdown synthesis
# ---------------------------------------------------------------------------

def build_markdown(
    topic: str,
    parsed: dict,
    raw_gemini: str,
) -> str:
    today = date.today().isoformat()
    verified = parsed["verified"]
    flagged = parsed["flagged"]
    removed = parsed["removed"]
    parse_succeeded = parsed["parse_succeeded"]

    lines: list[str] = []

    lines.append(f"# Verified Research: {topic}")
    lines.append(f"Source: {RESEARCH_FILENAME}")
    lines.append(f"Verified: {today}")
    lines.append("Science standard: Peer-reviewed only")
    lines.append("")

    # ------------------------------------------------------------------
    # Summary counts
    # ------------------------------------------------------------------
    lines.append("## Summary")
    lines.append(
        f"Verified: {len(verified)} claims | "
        f"Flagged: {len(flagged)} claims | "
        f"Removed: {len(removed)} claims"
    )
    lines.append("")

    if not parse_succeeded:
        lines.append(
            "> **Parsing warning:** The structured response from Gemini could not be "
            "parsed into individual claims. The raw analysis is included at the bottom "
            "of this document. Review it manually and categorise claims as needed."
        )
        lines.append("")

    # ------------------------------------------------------------------
    # Verified Claims
    # ------------------------------------------------------------------
    lines.append("## Verified Claims (safe to use in script)")
    lines.append("")
    if verified:
        for item in verified:
            claim = item.get("claim") or "—"
            source = item.get("source") or "—"
            confidence = item.get("confidence") or "—"
            note = item.get("note") or ""

            lines.append(f"- {claim} ✓")
            lines.append(f"  Source: {source}")
            lines.append(f"  Confidence: {confidence}")
            if note:
                lines.append(f"  Note: {note}")
            lines.append("")
    else:
        lines.append("_No verified claims identified._")
        lines.append("")

    # ------------------------------------------------------------------
    # Flagged Claims
    # ------------------------------------------------------------------
    lines.append("## Flagged Claims (review before use)")
    lines.append("")
    if flagged:
        for item in flagged:
            claim = item.get("claim") or "—"
            source = item.get("source") or "—"
            reason = item.get("reason") or "—"

            lines.append(f"- {claim} ⚠")
            lines.append(f"  Source: {source}")
            lines.append(f"  Reason: {reason}")
            lines.append("")
    else:
        lines.append("_No flagged claims._")
        lines.append("")

    # ------------------------------------------------------------------
    # Removed Claims
    # ------------------------------------------------------------------
    lines.append("## Removed Claims (do not use)")
    lines.append("")
    if removed:
        for item in removed:
            claim = item.get("claim") or "—"
            reason = item.get("reason") or "—"

            lines.append(f"- {claim} ✗")
            lines.append(f"  Reason: {reason}")
            lines.append("")
    else:
        lines.append("_No claims removed._")
        lines.append("")

    # ------------------------------------------------------------------
    # Raw Verification Analysis
    # ------------------------------------------------------------------
    lines.append("## Raw Verification Analysis")
    lines.append("")
    if raw_gemini:
        lines.append(raw_gemini)
    else:
        lines.append(
            "_Gemini verification was not run or failed. "
            "See console output for details._"
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/pipeline/agent2_verify.py \"<slug>\"")
        print("Example: python tools/pipeline/agent2_verify.py \"emotional-dysregulation-in-adhd\"")
        sys.exit(1)

    slug = sys.argv[1].strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    print(f"\n=== Agent 2: Science Verification ===")
    print(f"Slug : {slug}")
    print()

    # Step 1 — Read the research document
    print(f"[1/3] Reading {RESEARCH_FILENAME}...")
    try:
        research_content = read_output(slug, RESEARCH_FILENAME)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        print("\nRun Agent 1 first:")
        print(f'  python tools/pipeline/agent1_research.py "<topic>"')
        sys.exit(1)

    topic = _extract_topic_from_research(research_content)
    print(f"  Topic: {topic}")
    print(f"  Research file length: {len(research_content):,} characters")

    # Step 2 — Query Gemini for verification
    print(f"\n[2/3] Verifying claims with {GEMINI_MODEL}...")
    raw_gemini, gemini_usage = query_gemini_verify(research_content)

    if not raw_gemini:
        # Gemini failed — save a fallback document and exit gracefully
        print("\n  [WARNING] Gemini returned no response. Saving fallback document.")
        fallback_content = (
            f"# Verified Research: {topic}\n"
            f"Source: {RESEARCH_FILENAME}\n"
            f"Verified: {date.today().isoformat()}\n"
            f"Science standard: Peer-reviewed only\n\n"
            f"## Summary\n"
            f"Verified: 0 claims | Flagged: 0 claims | Removed: 0 claims\n\n"
            f"> **Warning:** Gemini verification failed. Review the raw research manually.\n\n"
            f"## Raw Research (unverified)\n\n"
            f"{research_content}\n"
        )
        output_path = write_output(slug, OUTPUT_FILENAME, fallback_content)
        print(f"\nFallback saved: {output_path}")
        sys.exit(0)

    # Step 3 — Parse and synthesize
    print("\n[3/3] Parsing verification results and building output document...")
    parsed = parse_gemini_response(raw_gemini)

    v = len(parsed["verified"])
    f = len(parsed["flagged"])
    r = len(parsed["removed"])
    print(f"  Verified: {v} | Flagged: {f} | Removed: {r}")

    if not parsed["parse_succeeded"]:
        print("  [WARNING] Structured parsing found no claim blocks — raw response will be included.")

    content = build_markdown(topic, parsed, raw_gemini)

    # Save
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"\nSaved: {output_path}")
    print("\nDone. Review the output, then run Agent 3:")
    print(f'  /draft "{slug}"   (Agent 3 runs in Claude Code, no Python script)')


if __name__ == "__main__":
    main()
