"""
Peer-reviewed source aggregation for Agent 1 (Research).

Single responsibility: given a set of keyword sub-queries, fetch peer-reviewed
papers from two free providers and return a deduplicated, capped, normalized list.

Providers:
  - PubMed (NCBI E-utilities)
  - Europe PMC (EBI REST)

Every provider returns the same normalized paper schema:
    {
        "title": str,
        "authors": list[str],       # "LastName Initials" or full names
        "year": str,                # 4-char year or ""
        "abstract": str,            # may be "" (then excluded from the grounding set)
        "doi": str,                 # bare DOI or ""
        "source": str,              # "PubMed" | "Europe PMC"
        "venue": str,               # journal / venue name or ""
        "citation_count": int,      # 0 if unknown
    }

Design notes:
  - Each provider call is wrapped in try/except and returns [] on failure, so one
    dead or rate-limited provider never sinks the whole run.
  - gather_peer_reviewed() fans every sub-query across both providers, then
    dedups by normalized DOI (preferred) then normalized title, prefers entries
    that carry an abstract, caps the total, and trims long abstracts.
"""

import os
import re
import time
import xml.etree.ElementTree as ET

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PUBMED_SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
EUROPEPMC_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

REQUEST_TIMEOUT = 30  # seconds

DEFAULT_PER_QUERY = 15
DEFAULT_CAP = 40
ABSTRACT_MAX_CHARS = 1800

# Polite throttle between anonymous PubMed calls (~3 req/s limit).
PUBMED_SLEEP_NOKEY = 0.34

# Europe PMC `source` codes that are NOT peer-reviewed journal articles.
_EUROPEPMC_NONPEER_SOURCES = {"PPR"}  # PPR = preprint


# ---------------------------------------------------------------------------
# Normalization helpers
# ---------------------------------------------------------------------------

def _norm_doi(doi: str) -> str:
    if not doi:
        return ""
    d = doi.strip().lower()
    d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d)
    return d.strip()


def _norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (title or "").lower())


def _trim_abstract(abstract: str) -> str:
    a = (abstract or "").strip()
    if len(a) > ABSTRACT_MAX_CHARS:
        a = a[:ABSTRACT_MAX_CHARS].rsplit(" ", 1)[0].strip() + " […]"
    return a


def _paper(title, authors, year, abstract, doi, source, venue="", citation_count=0) -> dict:
    return {
        "title": (title or "").strip(),
        "authors": authors or [],
        "year": (str(year) or "")[:4] if year else "",
        "abstract": _trim_abstract(abstract),
        "doi": _norm_doi(doi),
        "source": source,
        "venue": (venue or "").strip(),
        "citation_count": int(citation_count or 0),
    }


# ---------------------------------------------------------------------------
# PubMed (NCBI E-utilities)
# ---------------------------------------------------------------------------

def _pubmed_search(query: str, retmax: int) -> list[str]:
    params = {"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"}
    ncbi_key = os.getenv("NCBI_API_KEY")
    if ncbi_key:
        params["api_key"] = ncbi_key
    resp = requests.get(PUBMED_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json().get("esearchresult", {}).get("idlist", [])


def _pubmed_fetch(pmids: list[str]) -> list[dict]:
    if not pmids:
        return []
    params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "abstract", "retmode": "xml"}
    ncbi_key = os.getenv("NCBI_API_KEY")
    if ncbi_key:
        params["api_key"] = ncbi_key
    resp = requests.get(PUBMED_FETCH_URL, params=params, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    papers: list[dict] = []
    for article in root.iter("PubmedArticle"):
        title_el = article.find(".//ArticleTitle")
        title = (title_el.text or "").strip() if title_el is not None else ""

        authors = []
        for author in article.findall(".//Author"):
            last = author.findtext("LastName", "")
            initials = author.findtext("Initials", "")
            if last:
                authors.append(f"{last} {initials}".strip())

        year_el = article.find(".//PubDate/Year")
        if year_el is None:
            year_el = article.find(".//PubDate/MedlineDate")
        year = (year_el.text or "")[:4] if year_el is not None else ""

        abstract_parts = article.findall(".//AbstractText")
        abstract = " ".join((el.text or "") for el in abstract_parts if el.text).strip()

        doi = ""
        for id_el in article.findall(".//ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text or ""
                break

        journal_el = article.find(".//Journal/Title")
        venue = (journal_el.text or "").strip() if journal_el is not None else ""

        papers.append(_paper(title, authors, year, abstract, doi, "PubMed", venue))
    return papers


def search_pubmed(query: str, retmax: int = DEFAULT_PER_QUERY) -> list[dict]:
    """Search PubMed for a single query. Returns normalized papers ([] on failure)."""
    try:
        if not os.getenv("NCBI_API_KEY"):
            time.sleep(PUBMED_SLEEP_NOKEY)
        pmids = _pubmed_search(query, retmax)
        if not pmids:
            return []
        if not os.getenv("NCBI_API_KEY"):
            time.sleep(PUBMED_SLEEP_NOKEY)
        return _pubmed_fetch(pmids)
    except Exception as exc:
        print(f"    [PubMed] query failed ({query!r}): {exc}")
        return []


# ---------------------------------------------------------------------------
# Europe PMC (EBI REST)
# ---------------------------------------------------------------------------

def search_europepmc(query: str, retmax: int = DEFAULT_PER_QUERY) -> list[dict]:
    """Search Europe PMC for a single query. Returns normalized papers ([] on failure)."""
    try:
        params = {
            "query": query,
            "format": "json",
            "resultType": "core",
            "pageSize": retmax,
        }
        resp = requests.get(EUROPEPMC_SEARCH_URL, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        results = resp.json().get("resultList", {}).get("result", [])

        papers: list[dict] = []
        for r in results:
            # Skip preprints to honor the peer-reviewed-only standard.
            if (r.get("source") or "").upper() in _EUROPEPMC_NONPEER_SOURCES:
                continue
            abstract = r.get("abstractText") or ""
            if not abstract:
                continue
            author_string = r.get("authorString") or ""
            authors = [a.strip() for a in author_string.split(",") if a.strip()]
            venue = (r.get("journalInfo", {}) or {}).get("journal", {}).get("title", "")
            papers.append(_paper(
                title=r.get("title", ""),
                authors=authors,
                year=r.get("pubYear", ""),
                abstract=abstract,
                doi=r.get("doi", ""),
                source="Europe PMC",
                venue=venue,
                citation_count=r.get("citedByCount", 0),
            ))
        return papers
    except Exception as exc:
        print(f"    [Europe PMC] query failed ({query!r}): {exc}")
        return []


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

_PROVIDERS = (
    ("PubMed", search_pubmed),
    ("Europe PMC", search_europepmc),
)


def gather_peer_reviewed(
    subqueries: list[str],
    per_query: int = DEFAULT_PER_QUERY,
    cap: int = DEFAULT_CAP,
) -> list[dict]:
    """
    Fan each sub-query across PubMed and Europe PMC, union, dedup, and cap.

    Dedup precedence: normalized DOI first, then normalized title. When a duplicate
    is found, the entry that carries an abstract (and then the higher citation count)
    wins. Returns up to `cap` normalized papers, sorted by citation_count desc.
    """
    by_key: dict[str, dict] = {}
    per_provider_counts: dict[str, int] = {name: 0 for name, _ in _PROVIDERS}

    def _key(p: dict) -> str:
        return f"doi:{p['doi']}" if p["doi"] else f"title:{_norm_title(p['title'])}"

    def _better(new: dict, old: dict) -> bool:
        # Prefer an entry that actually has an abstract, then higher citation count.
        if bool(new["abstract"]) != bool(old["abstract"]):
            return bool(new["abstract"])
        return new["citation_count"] > old["citation_count"]

    for q in subqueries:
        print(f"  Sub-query: {q!r}")
        for name, fn in _PROVIDERS:
            results = fn(q, per_query)
            per_provider_counts[name] += len(results)
            for p in results:
                if not p["title"]:
                    continue
                k = _key(p)
                if k not in by_key or _better(p, by_key[k]):
                    by_key[k] = p

    papers = sorted(by_key.values(), key=lambda p: p["citation_count"], reverse=True)

    print(
        "  Provider hits (pre-dedup): "
        + ", ".join(f"{n}={per_provider_counts[n]}" for n, _ in _PROVIDERS)
    )
    print(f"  Unique papers after dedup: {len(papers)} (capping at {cap})")
    return papers[:cap]
