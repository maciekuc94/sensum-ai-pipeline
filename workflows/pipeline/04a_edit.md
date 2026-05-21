# Workflow: Agent 4a — Script Editing

## Purpose

Agent 4a takes the script draft produced by Agent 3 and uses the Anthropic
Claude API (`claude-opus-4-7`) to perform stylistic copy-editing. It improves
prose quality, flow, rhythm, and word choice — without altering any scientific
claims — and flags every significant change inline so the human reviewer can
see exactly what changed and why.

---

## Prerequisites

1. **Agent 3 must have run successfully.** The file
   `outputs/videos/{slug}/md/03_script_draft.md` must exist.

2. **Anthropic API key** — set in `.env` at the project root:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```

3. **Style guide** — `workflows/guides/style_guide.md` must exist in the project root.
   It is bundled with this repository and should not need to be created manually.

4. **Dependencies installed:**
   ```
   pip install -r requirements.txt
   ```

---

## Run Command

```bash
python tools/pipeline/agent4a_edit.py "emotional-dysregulation-in-adhd"
```

Note: the argument is the **slug** (hyphenated, lowercase), not the original
topic string. The slug is printed at the end of Agent 3's output.

The script prints progress as it runs through four steps:

```
=== Agent 4a: Script Editing ===
Slug : emotional-dysregulation-in-adhd

[1/4] Loading style guides...
  Style guide loaded (4,321 characters)
  Narrative architectures loaded (3,100 characters)

[2/4] Reading 03_script_draft.md...
  Topic  : emotional dysregulation in ADHD
  Script file length: 9,105 characters

[3/4] Calling Claude API to edit the script...
  Querying claude-opus-4-7 — script editing...
  Edited script received (9,430 characters)

[4/4] Saving output to 04_script_final.md...
  Saved: outputs/videos/emotional-dysregulation-in-adhd/md/04_script_final.md

Done. Review the final script, then run Agent 4b (hook scorer) and Agent 5/6:
  python tools/pipeline/agent4b_hook.py "emotional-dysregulation-in-adhd"
  python tools/pipeline/agent5_visuals.py "emotional-dysregulation-in-adhd"
  python tools/pipeline/agent6_narration.py "emotional-dysregulation-in-adhd"
```

---

## What the Editor Checks

The Claude prompt instructs the editor to enforce every rule in the style guide:

- **Natural speech flow** — Rewrites any sentence that sounds academic, passive,
  or hedging so it reads like a confident, knowledgeable friend speaking directly
  to the viewer
- **No unexplained jargon** — Verifies that every scientific term is immediately
  followed by a plain-language explanation; adds one if missing and flags it
- **Sentence variety** — Breaks up long or complex sentences into short punchy
  statements and fragments for emphasis
- **No passive voice** — Rewrites every passive construction in active voice
- **No hedging language** — Replaces "might", "perhaps", "could be", and "some
  studies suggest" with confident language ("research shows", "neuroscience has
  found")
- **Emotional arc** — Verifies the script flows empathy → science → empowerment;
  fixes sections that break this arc
- **Scientific claims preserved** — Does not alter, soften, or strengthen any
  factual claim; flags concerns in EDITOR NOTEs but leaves the text unchanged

Every significant change is marked inline:

```
[EDITOR NOTE: changed "original text" to "new text" — reason: brief reason]
```

---

## Reviewer Checklist

Open `outputs/videos/{slug}/md/04_script_final.md` and work through these questions before
proceeding to Agent 4b:

- Does the edited script sound natural when spoken aloud? (Read it out loud or
  use text-to-speech.)
- Are all `[EDITOR NOTE: ...]` markers reasonable prose improvements — not
  alterations to scientific claims?
- Is sentence structure punchy and varied? No long academic sentences?
- Does the emotional arc hold throughout: empathy → science → empowerment?
- Is the word count still approximately **1,500–2,000 words** (narration text
  only, excluding headers)?

If any answer is no, edit `04_script_final.md` directly before running Agent 4b.

---

## Common Issues

**Fewer EDITOR NOTEs than expected**

If the script draft was already well-written, Claude may make only minor
changes. A small number of EDITOR NOTEs is a pass — it means the draft was
close to production-ready. Do not rerun Agent 4a to force more edits.

**"Output file not found" error on startup**

Agent 3 has not been run yet for this slug, or the slug is misspelled.

```bash
# Run Agent 3 first:
python tools/pipeline/agent3.py "emotional-dysregulation-in-adhd"
# Then run Agent 4a:
python tools/pipeline/agent4a_edit.py "emotional-dysregulation-in-adhd"
```

**"Style guide not found" error**

The file `workflows/guides/style_guide.md` is missing from the project root.
Check that the file exists and re-clone or restore the repository if needed.

**"ANTHROPIC_API_KEY is missing or empty"**

Add your Anthropic API key to the `.env` file at the project root:
```
ANTHROPIC_API_KEY=sk-ant-...
```

---

## Limitations

- **Claude edits prose, not facts.** Agent 4a does not re-verify scientific
  claims against the source research. Always cross-check the final script
  against `outputs/videos/{slug}/md/02_verified_research.md` and the original papers
  before publishing.

- **max_tokens is 8192.** Very long drafts (over ~6,000 words) may be truncated.
  The draft should be ~1,700 words, so this limit is not normally reached.

- **Image prompts are handled by Agent 5.** Agent 4a does not deal with image
  markers. Run Agent 5 after reviewing `04_script_final.md`.

---

## Output Location

```
outputs/
└── videos/
    └── emotional-dysregulation-in-adhd/
        └── md/
            ├── 01_research.md             (Agent 1 output)
            ├── 02_verified_research.md    (Agent 2 output)
            ├── 03_script_draft.md         (Agent 3 output — input for Agent 4a)
            └── 04_script_final.md         (Agent 4a output)
```

---

## Output Format

```markdown
# Script Final: [Topic]
Generated: [date]
Model: claude-opus-4-7
Editor notes are inline as [EDITOR NOTE: ...]

---

[Full edited narration script with inline EDITOR NOTEs]
```

---

## Next Step

Once you are satisfied with the final script, run Agent 4b to score the opening
hook before committing to a recording session:

```bash
python tools/pipeline/agent4b_hook.py "emotional-dysregulation-in-adhd"
```

Then run Agents 5 and 6 in parallel:

```bash
python tools/pipeline/agent5_visuals.py "emotional-dysregulation-in-adhd"
python tools/pipeline/agent6_narration.py "emotional-dysregulation-in-adhd"
```
