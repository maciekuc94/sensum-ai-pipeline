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
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import make_slug, next_output_number, write_output, get_env

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
REQUEST_TIMEOUT = 30  # seconds


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
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                max_output_tokens=8192,
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
# PubMed API
# ---------------------------------------------------------------------------

def _pubmed_search(query: str, retmax: int = 10) -> list[str]:
    """Return a list of PubMed IDs for the query."""
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": retmax,
        "retmode": "json",
    }
    ncbi_key = os.getenv("NCBI_API_KEY")
    if ncbi_key:
        params["api_key"] = ncbi_key

    resp = requests.get(PUBMED_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    return data.get("esearchresult", {}).get("idlist", [])


def _pubmed_fetch(pmids: list[str]) -> list[dict]:
    """Fetch paper details for a list of PubMed IDs; returns list of dicts."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
    }
    ncbi_key = os.getenv("NCBI_API_KEY")
    if ncbi_key:
        params["api_key"] = ncbi_key

    resp = requests.get(PUBMED_FETCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    papers = []

    for article in root.iter("PubmedArticle"):
        paper: dict = {}

        # Title
        title_el = article.find(".//ArticleTitle")
        paper["title"] = (title_el.text or "").strip() if title_el is not None else ""

        # Authors
        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName", "")
            initials = author.findtext("Initials", "")
            if last:
                authors.append(f"{last} {initials}".strip())
        paper["authors"] = authors

        # Year
        year_el = article.find(".//PubDate/Year")
        if year_el is None:
            year_el = article.find(".//PubDate/MedlineDate")
        paper["year"] = (year_el.text or "")[:4] if year_el is not None else ""

        # Abstract
        abstract_parts = article.findall(".//AbstractText")
        paper["abstract"] = " ".join(
            (el.text or "") for el in abstract_parts if el.text
        ).strip()

        # DOI
        doi = ""
        for id_el in article.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text or ""
                break
        paper["doi"] = doi

        papers.append(paper)

    return papers


def _make_pubmed_query(topic: str) -> str:
    """Convert a colloquial topic string to a PubMed-appropriate 3-5 keyword query."""
    try:
        import google.genai as genai

        project = get_env("GOOGLE_CLOUD_PROJECT")
        location = "global"
        client = genai.Client(vertexai=True, project=project, location=location)

        prompt = (
            f"Convert this topic to a short PubMed search query using 3-5 academic keywords "
            f"or MeSH terms. No punctuation, no question marks, no stop words. "
            f"Return only the query string, nothing else.\n\nTopic: {topic}"
        )
        response = client.models.generate_content(model="gemini-3.1-pro-preview", contents=prompt)
        query = response.text.strip().strip('"').strip("'")
        print(f"  PubMed query derived: {query!r}")
        return query
    except Exception as exc:
        print(f"  [WARNING] Could not derive PubMed query ({exc}), using raw topic.")
        return topic


def query_pubmed(topic: str) -> list[dict]:
    """Search PubMed for the top 10 papers on a topic. Returns list of paper dicts."""
    print("  Searching PubMed...")
    pubmed_query = _make_pubmed_query(topic)
    try:
        pmids = _pubmed_search(pubmed_query, retmax=10)
        if not pmids:
            print("  [WARNING] PubMed returned no results.")
            return []
        print(f"  Found {len(pmids)} PubMed IDs — fetching details...")
        papers = _pubmed_fetch(pmids)
        print(f"  Retrieved {len(papers)} PubMed papers.")
        return papers
    except Exception as exc:
        print(f"  [WARNING] PubMed query failed: {exc}")
        return []


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
    pubmed_papers: list[dict],
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

    # Collect brief citation bullets from PubMed (use title + authors + year)
    finding_sources: list[dict] = []
    for p in pubmed_papers:
        if p.get("abstract"):
            finding_sources.append(p)

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
        lines.append("- See PubMed section below for paper-level findings.")

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

    def _add_row(p: dict, source_label: str) -> None:
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
        lines.append(f"| {safe_title} | {authors} | {year} | {doi} | {source_label} |")

    for p in pubmed_papers:
        _add_row(p, "PubMed")

    lines.append("")

    # ------------------------------------------------------------------
    # PubMed Results
    # ------------------------------------------------------------------
    lines.append("## PubMed Results")
    lines.append("")
    if pubmed_papers:
        for i, p in enumerate(pubmed_papers, start=1):
            title = p.get("title") or "Untitled"
            authors = _authors_str(p.get("authors") or [])
            year = p.get("year") or "n.d."
            doi = p.get("doi") or ""
            abstract = p.get("abstract") or "_No abstract available._"

            lines.append(f"### {i}. {title}")
            lines.append(f"**Authors:** {authors}  ")
            lines.append(f"**Year:** {year}  ")
            if doi:
                lines.append(f"**DOI:** <https://doi.org/{doi}>  ")
            lines.append("")
            lines.append(abstract)
            lines.append("")
    else:
        lines.append("_No PubMed results retrieved._")
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

    # Step 2 — PubMed
    print("[2/2] Querying PubMed API...")
    pubmed_papers = query_pubmed(topic)

    # Synthesize
    print("\nSynthesizing results into markdown...")
    content = build_markdown(topic, gemini_text, pubmed_papers)

    # Save
    output_path = write_output(slug, "md/01_research.md", content)
    print(f"\nSaved: {output_path}")
    print("\nDone. Review the output, then run Agent 2:")
    print(f"  python tools/agent2_verify.py \"{slug}\"")


if __name__ == "__main__":
    main()
