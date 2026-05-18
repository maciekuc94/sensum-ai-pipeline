# Workflow: Agent 2 — Science Verification

## Purpose

Before a single word of the video script is written, every factual claim in the
research document must be evaluated against a strict peer-reviewed standard.
This step exists to protect the channel from two specific risks:

1. **The replication crisis.** Prominent psychology findings (ego depletion,
   power poses, certain priming effects) have failed to replicate. A claim from
   one study, however famous, is not the same as settled science.

2. **Pop-science contamination.** Sources like Psychology Today, Verywell Mind,
   and WebMD are readable and often accurate in spirit, but they are not
   peer-reviewed. Citing them as scientific evidence misleads viewers. Agent 2
   flags them automatically so you can decide whether to remove, rephrase, or
   find a primary source to replace them.

Agent 2 reads the `01_research.md` file produced by Agent 1, sends it to
Vertex AI Gemini 2.5 Pro, and asks the model to categorise every factual
claim as VERIFIED, FLAGGED, or REMOVED. The result is saved as
`02_verified_research.md`.

---

## Science Standard

**Peer-reviewed only.**

A claim is considered VERIFIED only when it traces to a published journal
article with an identifiable author/year citation — e.g., `Barkley et al.,
2008 — Journal of Attention Disorders`.

| Category | Meaning |
|----------|---------|
| VERIFIED | Clear peer-reviewed citation; confidence rated High (multiple studies) or Medium (one or two studies) |
| FLAGGED | Weak or absent citation; pop-science source; single study that may not have replicated; needs human review |
| REMOVED | No scientific backing; speculation presented as fact; source entirely absent |

Single-study findings are noted as "single study — not yet replicated" even
when they are VERIFIED, so the script writer knows to caveat them.

---

## Prerequisites

1. **Agent 1 must have run successfully.** The file
   `outputs/[slug]/md/01_research.md` must exist.

2. **Google Cloud authentication** — run once per machine if not already done:
   ```
   gcloud auth application-default login
   ```

3. **Environment variables** — set in `.env` at the project root:
   ```
   GOOGLE_CLOUD_PROJECT=your-gcp-project-id
   GOOGLE_CLOUD_LOCATION=us-central1   # optional, defaults to us-central1
   ```

4. **Dependencies installed:**
   ```
   pip install -r requirements.txt
   ```

---

## How to Run

```bash
python tools/agent2_verify.py "emotional-dysregulation-in-adhd"
```

Note: the argument is the **slug** (hyphenated, lowercase), not the original
topic string. The slug is printed at the end of Agent 1's output.

The script prints progress as it runs through three steps:

```
=== Agent 2: Science Verification ===
Slug : emotional-dysregulation-in-adhd

[1/3] Reading 01_research.md...
  Topic: emotional dysregulation in ADHD
  Research file length: 12,345 characters

[2/3] Verifying claims with Gemini 2.5 Pro...
  Initializing Vertex AI (project=my-project, location=us-central1)...
  Querying Gemini 2.5 Pro for claim verification...

[3/3] Parsing verification results and building output document...
  Verified: 8 | Flagged: 3 | Removed: 1

Saved: outputs/emotional-dysregulation-in-adhd/md/02_verified_research.md

Done. Review the output, then run Agent 3:
  python tools/agent3_chain.py "emotional-dysregulation-in-adhd"
```

---

## Output Location

```
outputs/
└── emotional-dysregulation-in-adhd/
    └── md/
        ├── 01_research.md              (input)
        └── 02_verified_research.md     (output)
```

---

## Output Format

```markdown
# Verified Research: [Topic]
Source: 01_research.md
Verified: [date]
Science standard: Peer-reviewed only

## Summary
Verified: X claims | Flagged: Y claims | Removed: Z claims

## Verified Claims (safe to use in script)
- [Claim text] ✓
  Source: Author et al., Year — Journal
  Confidence: High
  Note: [optional]

## Flagged Claims (review before use)
- [Claim text] ⚠
  Source: [what exists]
  Reason: [why flagged]

## Removed Claims (do not use)
- [Claim text] ✗
  Reason: [why removed]

## Raw Verification Analysis
[Full Gemini response]
```

---

## How to Review the Output

Open `outputs/[slug]/md/02_verified_research.md` in any markdown viewer or text
editor.

### Verified Claims

These are safe to use as the factual backbone of the script. Before trusting
them completely:

- Check that the cited journal is real and the paper year is plausible.
- If confidence is **Medium**, consider whether you want to add a qualifier in
  the script (e.g., "research suggests…" rather than "research proves…").
- Claims marked "single study — not yet replicated" should be presented to
  viewers as preliminary findings, not consensus.

### Flagged Claims

Each flagged claim requires a decision:

| Option | When to use it |
|--------|---------------|
| **Keep with caveat** | The claim is directionally correct and useful, but the source is weak. Reword in the script to hedge ("some research suggests…") and note in the file that a caveat was added. |
| **Find a primary source** | You believe the claim is well-supported but Agent 2 could not locate a peer-reviewed citation. Search PubMed or Google Scholar manually, then update the claim's source in the file. |
| **Remove** | You cannot find peer-reviewed backing and the claim is not essential to the video. Delete it from the file. |

To act on a flagged claim, edit `02_verified_research.md` directly: move the
bullet to the appropriate section, update the source line, and adjust the
reason.

### Removed Claims

Do not use these in the script. If a removed claim seems important and you
believe there is genuine research behind it, search for a primary source and
re-add it to the Verified section manually with the citation.

### Raw Verification Analysis

The full unstructured Gemini response is preserved at the bottom of the file.
If the automated parsing failed to extract individual claims (the Summary will
show all zeros), read this section manually and categorise claims yourself.

---

## Common Issues

**"Output file not found" error on startup**

Agent 1 has not been run yet for this slug, or the slug is misspelled.

```bash
# Run Agent 1 first:
python tools/agent1_research.py "emotional dysregulation in ADHD"
# Then run Agent 2 with the slug Agent 1 printed:
python tools/agent2_verify.py "emotional-dysregulation-in-adhd"
```

**All counts are zero / parsing warning in output**

Gemini returned a response but it did not follow the expected structured
format. The full raw response is still saved in the `## Raw Verification
Analysis` section. Read it there and manually promote claims to the
appropriate sections.

**Gemini verification failed (warning in console)**

Vertex AI credentials are missing or expired. Re-authenticate:

```bash
gcloud auth application-default login
```

Check that `GOOGLE_CLOUD_PROJECT` is set in `.env`. A fallback document is
still saved containing the original research content so you can continue
manually.

---

## Known Limitations

- **Gemini may miss claims.** Long research documents may exceed the effective
  attention span of the model. Skim the Raw Verification Analysis section to
  spot anything that looks like a factual claim but did not appear in a
  structured block.

- **Gemini cannot verify citations it was not trained on.** If Agent 1 found a
  paper published after Gemini's training cutoff, it may still assess the claim
  as VERIFIED based on the citation format, not actual knowledge of the study.
  Always do a spot-check on key statistics.

- **False VERIFIED ratings are possible.** The model can be confidently wrong.
  A High-confidence rating reflects the model's internal assessment, not an
  independent database lookup. For any claim you plan to state as a definitive
  fact on camera, verify the underlying paper directly.

---

## Next Step

Once you are satisfied that the verified research is solid and flagged/removed
claims have been reviewed, run Agent 3 to produce the first draft of the video
script:

```bash
python tools/agent3_chain.py "emotional-dysregulation-in-adhd"
```
