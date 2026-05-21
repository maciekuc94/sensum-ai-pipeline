# Agent 0: Materials Extraction SOP

## Purpose

Before running the main pipeline, extract relevant insights from a reference book (PDF) and save them as a trusted source for the scriptwriter. Agent 3 will incorporate these insights alongside the verified research — without fact-checking them, since you've curated the source.

This step is optional. If you have no book for the topic, skip it and run Agent 1 directly.

---

## When to Run

Run this **before Agent 1** whenever you have a relevant book in the `materials/` folder.

---

## Pre-Step: Choose a PDF

Before running the pipeline for any topic, list the available PDFs:

```
materials/
├── The Body Keeps the Score.pdf
├── The Fear Factor.pdf
└── Thinking Fast and Slow.pdf
```

Always ask: **"Which PDF should I use for this topic?"** Wait for an explicit selection before proceeding. If the answer is "none", skip this agent entirely.

---

## Usage

```bash
python tools/pipeline/agent0_materials.py --topic "psychology of fear" --pdf "materials/The Fear Factor.pdf"
```

The `--topic` argument should match exactly what you'll pass to Agent 1, so both agents produce the same slug and their outputs land in the same folder.

---

## What It Does

1. Extracts full text from the PDF using `pdfplumber`
2. Sends the full book text + topic to Gemini 3.1 Pro (1M context — handles any book size)
3. Gemini extracts: key frameworks, counterintuitive findings, concrete examples, quotable passages, and mechanisms most relevant to the topic
4. Saves output to `outputs/videos/{slug}/md/00_materials_insights.md`

---

## Review

Open `outputs/videos/{slug}/md/00_materials_insights.md`. Skim the extracted insights:

- Are the most relevant frameworks from the book captured?
- Are concrete examples present (not just abstract summaries)?
- Are there any quotable passages?

If the extraction looks thin or off-topic, you can re-run the agent — it overwrites the file each time.

---

## How It Feeds Into the Pipeline

Agent 3 automatically checks for `00_materials_insights.md` when building its prompt. If the file exists, it injects it as:

```
## Book Insights (Trusted Source — Do Not Verify)
[contents of 00_materials_insights.md]
```

Agent 3 treats these insights with the same weight as the verified research. The "Do Not Verify" label ensures the scriptwriter uses them directly without hedging.

Agent 2 (verification) never sees the book — it only verifies claims from Agent 1's research output.

---

## Outputs

| File | Description |
|------|-------------|
| `outputs/videos/{slug}/md/00_materials_insights.md` | Structured insights extracted from the book |
