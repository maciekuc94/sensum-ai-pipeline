"""
Agent 1: Research
Researches a psychology topic using:
  - Vertex AI Gemini 3.1 Pro with Google Search Grounding
  - PubMed API (NCBI E-utilities)

Usage:
    python tools/pipeline/agent1_research.py "emotional dysregulation in ADHD"
"""

import sys
import os
import re
import json
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import make_slug, next_output_number, write_output, get_env, query_gemini_text
from tools.research_sources import gather_peer_reviewed


# ---------------------------------------------------------------------------
# Vertex AI / Gemini
# ---------------------------------------------------------------------------

GEMINI_MODEL = "gemini-3.1-pro-preview"


def _load_prompt() -> str:
    """Load research prompt template from workflows/pipeline/01_research_prompt.md."""
    path = Path(__file__).parent.parent.parent / "workflows" / "pipeline" / "01_research_prompt.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [l for l in lines if not l.startswith("#") and not l.startswith("<!--")]
    return "\n".join(body).strip()


_RESEARCH_PROMPT_TEMPLATE = _load_prompt()


def query_gemini(topic: str) -> tuple[str, dict]:
    """Query Gemini 3.1 Pro with Google Search Grounding for a research overview.
    Uses google-genai SDK (required for grounding on Gemini 2.5+).
    Returns (text, usage_dict)."""
    try:
        import google.genai as genai
        from google.genai import types

        project = get_env("GOOGLE_CLOUD_PROJECT")
        location = "global"

        print(f"  Initializing google-genai client (project={project}, location={location})...")
        client = genai.Client(vertexai=True, project=project, location=location)

        prompt = _RESEARCH_PROMPT_TEMPLATE.format(topic=topic)

        print(f"  Querying {GEMINI_MODEL} with Google Search Grounding...")
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            # gemini-3.1-pro-preview emits variable thinking tokens; 8192 was too tight
            # and could silently truncate the answer to empty (MAX_TOKENS). 16384 leaves
            # room for both thinking and a richer grounded research summary.
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                max_output_tokens=16384,
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
        print(f"  [WARNING] Gemini query failed: {exc}")
        return "", {}


# ---------------------------------------------------------------------------
# Peer-reviewed sources (multi-query across PubMed + Europe PMC)
# ---------------------------------------------------------------------------

def _derive_subqueries(topic: str) -> list[str]:
    """
    Break a colloquial topic into 4-6 short keyword sub-queries, one per mechanism,
    so the peer-reviewed search spans the whole topic instead of one narrow ANDed
    query. Each sub-query is 3-5 academic keywords / MeSH terms, no punctuation.
    Falls back to [topic] on any failure.
    """
    prompt = (
        "Break the following research topic into 4-6 distinct sub-topics, one per "
        "underlying mechanism or construct. For each, write a short academic search "
        "query of 3-5 keywords or MeSH terms (no punctuation, no stop words, no "
        "question marks). Return ONLY a JSON array of query strings, nothing else.\n\n"
        f"Topic: {topic}"
    )
    try:
        text, _ = query_gemini_text(
            prompt, model=GEMINI_MODEL, max_tokens=2048, step_label="deriving sub-queries"
        )
        queries = _parse_query_list(text)
        if queries:
            print(f"  Derived {len(queries)} sub-queries:")
            for q in queries:
                print(f"    - {q}")
            return queries
        print("  [WARNING] Could not parse sub-queries — falling back to raw topic.")
    except Exception as exc:
        print(f"  [WARNING] Sub-query derivation failed ({exc}) — using raw topic.")
    return [topic]


def _parse_query_list(text: str) -> list[str]:
    """Parse a Gemini response into a list of query strings (JSON array or newlines)."""
    if not text:
        return []
    # Strip code fences if present.
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    # Try JSON first.
    try:
        start, end = cleaned.find("["), cleaned.rfind("]")
        if start != -1 and end != -1:
            arr = json.loads(cleaned[start : end + 1])
            qs = [str(q).strip() for q in arr if str(q).strip()]
            if qs:
                return qs[:6]
    except Exception:
        pass
    # Fall back to newline / bullet list.
    lines = []
    for line in cleaned.splitlines():
        q = re.sub(r'^[\s\-\*\d\.\)"]+', "", line).strip().strip('"').strip("'")
        if q and len(q.split()) <= 8:
            lines.append(q)
    return lines[:6]


def gather_research_papers(topic: str) -> list[dict]:
    """Derive sub-queries and gather deduplicated peer-reviewed papers across providers."""
    print("  Deriving mechanism sub-queries...")
    subqueries = _derive_subqueries(topic)
    print("  Searching PubMed + Europe PMC...")
    papers = gather_peer_reviewed(subqueries)
    print(f"  Total peer-reviewed papers gathered: {len(papers)}")
    return papers


# ---------------------------------------------------------------------------
# Markdown synthesis
# ---------------------------------------------------------------------------

def _authors_str(authors: list[str], max_names: int = 3) -> str:
    if not authors:
        return "Unknown"
    if len(authors) <= max_names:
        return ", ".join(authors)
    return ", ".join(authors[:max_names]) + " et al."


def _doi_link(doi: str) -> str:
    if not doi:
        return "—"
    return f"[{doi}](https://doi.org/{doi})"


def build_markdown(
    topic: str,
    gemini_text: str,
    papers: list[dict],
) -> str:
    today = date.today().isoformat()
    lines: list[str] = []

    lines.append(f"# Research: {topic}")
    lines.append(f"Generated: {today}")
    lines.append("")

    # ------------------------------------------------------------------
    # Key Findings — pull from union of all sources
    # ------------------------------------------------------------------
    lines.append("## Key Findings")
    lines.append("")

    # Collect brief citation bullets from the gathered papers (title + authors + year)
    finding_sources: list[dict] = [p for p in papers if p.get("abstract")]

    if finding_sources:
        for p in finding_sources[:5]:
            first_author = p["authors"][0] if p["authors"] else "Unknown"
            year = p.get("year", "n.d.")
            # Use first two sentences of abstract as the "finding"
            abstract = p.get("abstract", "")
            sentences = abstract.split(". ")
            snippet = ". ".join(sentences[:2]).strip()
            if snippet and not snippet.endswith("."):
                snippet += "."
            lines.append(f"- {snippet} ({first_author}, {year})")
    else:
        lines.append("- See Peer-Reviewed Sources section below for paper-level findings.")

    lines.append("")

    # ------------------------------------------------------------------
    # Scientific Concepts — placeholder (Gemini fills this well)
    # ------------------------------------------------------------------
    lines.append("## Scientific Concepts")
    lines.append("")
    lines.append(
        "_Key concepts are described in the Raw Gemini Research Summary below. "
        "Edit this section to extract and restate them in plain language for your audience._"
    )
    lines.append("")

    # ------------------------------------------------------------------
    # Studies Referenced — combined deduplicated table
    # ------------------------------------------------------------------
    lines.append("## Studies Referenced")
    lines.append("")
    lines.append("| Title | Authors | Year | DOI | Source |")
    lines.append("|-------|---------|------|-----|--------|")

    seen_titles: set[str] = set()

    def _add_row(p: dict) -> None:
        title = (p.get("title") or "").strip()
        norm = title.lower()
        if norm in seen_titles or not title:
            return
        seen_titles.add(norm)
        authors = _authors_str(p.get("authors") or [])
        year = p.get("year") or "—"
        doi = _doi_link(p.get("doi") or "")
        # Escape pipe characters in title
        safe_title = title.replace("|", "\\|")
        lines.append(f"| {safe_title} | {authors} | {year} | {doi} | {p.get('source', '—')} |")

    for p in papers:
        _add_row(p)

    lines.append("")

    # ------------------------------------------------------------------
    # Peer-Reviewed Sources — abstracts (Agent 2 reads this as its grounding pool)
    # ------------------------------------------------------------------
    lines.append("## Peer-Reviewed Sources")
    lines.append("")
    if papers:
        for i, p in enumerate(papers, start=1):
            title = p.get("title") or "Untitled"
            authors = _authors_str(p.get("authors") or [])
            year = p.get("year") or "n.d."
            doi = p.get("doi") or ""
            source = p.get("source") or "—"
            venue = p.get("venue") or ""
            abstract = p.get("abstract") or "_No abstract available._"

            lines.append(f"### {i}. {title}")
            lines.append(f"**Authors:** {authors}  ")
            lines.append(f"**Year:** {year}  ")
            lines.append(f"**Source:** {source}{f' — {venue}' if venue else ''}  ")
            if doi:
                lines.append(f"**DOI:** <https://doi.org/{doi}>  ")
            lines.append("")
            lines.append(abstract)
            lines.append("")
    else:
        lines.append("_No peer-reviewed results retrieved._")
        lines.append("")

    # ------------------------------------------------------------------
    # Raw Gemini Research Summary
    # ------------------------------------------------------------------
    lines.append("## Raw Gemini Research Summary")
    lines.append("")
    if gemini_text:
        lines.append(gemini_text)
    else:
        lines.append("_Gemini query was not run or failed. See console output for details._")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Agent 1: Research")
    parser.add_argument("topic", help="Research topic (in English for best results)")
    parser.add_argument("--slug", help="Override auto-generated slug (e.g. Polish slug for a Polish video)")
    args = parser.parse_args()

    topic = args.topic.strip()
    if not topic:
        print("Error: topic argument is empty.")
        sys.exit(1)

    slug = args.slug.strip() if args.slug else f"{next_output_number()}_{make_slug(topic)}"
    print(f"\n=== Agent 1: Research ===")
    print(f"Topic : {topic}")
    print(f"Slug  : {slug}")
    print()

    # Step 1 — Vertex AI / Gemini
    print(f"[1/2] Querying {GEMINI_MODEL} with Google Search Grounding...")
    gemini_text, gemini_usage = query_gemini(topic)

    # Step 2 — Peer-reviewed sources (multi-query, 2 providers)
    print("[2/2] Gathering peer-reviewed sources (PubMed + Europe PMC)...")
    papers = gather_research_papers(topic)

    # Synthesize
    print("\nSynthesizing results into markdown...")
    content = build_markdown(topic, gemini_text, papers)

    # Save
    output_path = write_output(slug, "md/01_research.md", content)
    print(f"\nSaved: {output_path}")
    print("\nDone. Review the output, then run Agent 2:")
    print(f"  python tools/agent2_verify.py \"{slug}\"")


if __name__ == "__main__":
    main()
