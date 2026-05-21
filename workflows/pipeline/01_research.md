# Workflow: Agent 1 — Research

## Purpose

Gather peer-reviewed scientific evidence on a psychology topic and produce a
structured markdown research brief that feeds every downstream agent in the
pipeline.

The agent combines two independent sources:

| Source | What it provides |
|--------|-----------------|
| Vertex AI Gemini 3.1 Pro + Google Search Grounding | Narrative overview, key concepts, researcher names, cited studies from the live web |
| PubMed (NCBI E-utilities) | Top 10 peer-reviewed paper records with abstracts and DOIs |

---

## When to Use It

Run this agent first — at the very beginning of a new video project, before any
scripting, fact-checking, or visual work. The output file (`01_research.md`)
is the single source of truth that all later agents read from.

---

## Required Inputs

| Input | Type | Description |
|-------|------|-------------|
| `topic` | String | The psychology topic to research. Be specific for better results. |

Good topic examples:
- `"emotional dysregulation in ADHD"`
- `"cognitive distortions in depression"`
- `"attachment styles in adults"`

Vague examples to avoid:
- `"mental health"` — too broad
- `"why people are sad"` — not a scientific framing

---

## Prerequisites

1. **Google Cloud authentication** — run once per machine:
   ```
   gcloud auth application-default login
   ```
2. **Environment variables** — set in `.env` at the project root:
   ```
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   GOOGLE_CLOUD_LOCATION=us-central1   # optional, defaults to us-central1
   NCBI_API_KEY=your-ncbi-key          # optional but recommended for rate limits
   ```
3. **Dependencies installed:**
   ```
   pip install -r requirements.txt
   ```

---

## How to Run

```bash
python tools/pipeline/agent1_research.py "emotional dysregulation in ADHD"
```

The script prints progress to the console as it runs through two steps:

```
=== Agent 1: Research ===
Topic : emotional dysregulation in ADHD
Slug  : emotional-dysregulation-in-adhd

[1/2] Querying Gemini 3.1 Pro with Google Search Grounding...
[2/2] Querying PubMed API...

Synthesizing results into markdown...

Saved: outputs/videos/emotional-dysregulation-in-adhd/md/01_research.md

Done. Review the output, then run Agent 2:
  python tools/pipeline/agent2_verify.py "emotional-dysregulation-in-adhd"
```

If one of the sources fails (network error, missing credentials, rate limit),
the script logs a warning and continues — the output is saved with whatever
was successfully retrieved.

---

## Output Location

```
outputs/
└── videos/
    └── emotional-dysregulation-in-adhd/
        └── md/
            └── 01_research.md
```

The slug is auto-generated from the topic string (lowercase, hyphen-separated).

---

## Output Format

```markdown
# Research: [Topic]
Generated: [date]

## Key Findings
- [Specific finding — first 2 sentences of abstract] (Author, Year)
- ...

## Scientific Concepts
[Placeholder — edit manually from Gemini section below]

## Studies Referenced
| Title | Authors | Year | DOI | Source |
|-------|---------|------|-----|--------|
| ...   | ...     | ...  | ... | PubMed |

## PubMed Results
### 1. [Paper Title]
**Authors:** ...
**Year:** ...
**DOI:** ...

[Full abstract]

## Raw Gemini Research Summary
[Full Gemini narrative response with grounding citations]
```

---

## How to Review the Output

Open `outputs/videos/{slug}/md/01_research.md` in any markdown viewer or text editor.

**What to look for:**

1. **Key Findings** — Do the auto-extracted findings make sense for the topic?
   Remove any that are off-topic (e.g., papers about a different population).

2. **Scientific Concepts section** — This is left as a placeholder. Read the
   Raw Gemini Summary and manually extract 3–6 key concepts to fill in this
   section before passing to Agent 2.

3. **Studies Referenced table** — Check that DOI links resolve. A broken DOI
   means the paper record may be malformed; remove those rows or fix the DOI.

4. **Abstracts** — Skim the PubMed abstracts. If a paper is clearly irrelevant
   (wrong topic, wrong population, animal study when you need human), delete
   that entry from the table and PubMed Results section.

5. **Gemini summary** — Read it critically. Verify any specific statistics or
   effect sizes it cites against the actual papers before using them in the
   script.

**What to edit:**

- Fill in the `## Scientific Concepts` section with 3–6 concepts from the
  Gemini summary.
- Remove off-topic papers from the Studies Referenced table.
- Add a brief `Key Finding` note to each table row if not already present.

---

## Known Limitations

- **Gemini may misattribute citations.** It sometimes invents plausible-sounding
  author names or years. Always cross-check statistics and quotes against the
  actual PubMed records before including them in the script.

- **DOIs are not guaranteed to be correct.** Always click through each DOI link
  before treating a paper as verified. PubMed records are generally reliable;
  Gemini-generated references are not.

- **PubMed search is keyword-based.** It may miss relevant papers that use
  different terminology. Consider running a second search with synonyms if the
  results look thin.

- **Rate limits.** Without an NCBI API key you are limited to 3 requests/second
  on PubMed. Set `NCBI_API_KEY` in `.env` to raise this limit.

- **Gemini grounding requires valid Google Cloud credentials.** If Gemini fails,
  the script continues with PubMed only, and the Gemini section in the output
  will say so explicitly.

---

## Next Step

Once you are satisfied with the reviewed and edited `01_research.md`, run
Agent 2:

```bash
python tools/pipeline/agent2_verify.py "emotional-dysregulation-in-adhd"
```

Agent 2 will fact-check claims and flag anything that needs further verification
before the script is written.
