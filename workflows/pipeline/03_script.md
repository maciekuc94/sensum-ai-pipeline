# Workflow: Script Writing (Agents 3a → 3n → 3b → 3c)

## Purpose

Step 3 is split into four separate agents so you have a review gate between each pass. Since the script is the most important output in the pipeline, each stage produces its own file that you can inspect — and optionally edit — before the next agent runs.

| Agent | Pass | Input | Output |
|-------|------|-------|--------|
| 3a | Draft | `md/02_verified_research.md` | `md/03a_draft.md` |
| 3n | Dedupe | `md/03a_draft.md` + `outputs/videos/*/md/06_script_narration.md` (corpus) | revised `md/03a_draft.md` + `md/03_novelty_report.md` (and `md/03a_draft.bak.md` on first run) |
| 3b | Critic | `md/03a_draft.md` | `md/03b_critique.md` |
| 3c | Rewrite | `md/03a_draft.md` + `md/03b_critique.md` | `md/03_script_draft.md` |

Agent 4 reads `md/03_script_draft.md` — same interface as before.

---

## Prerequisites

- `outputs/videos/{slug}/md/02_verified_research.md` must exist (Agent 2 output)
- `ANTHROPIC_API_KEY` set in `.env`
- `workflows/guides/style_guide.md` and `workflows/guides/narrative_architectures.md` present

---

## Agent 3a — Draft

```bash
python tools/pipeline/agent3a_draft.py "emotional-dysregulation-in-adhd"
```

Claude reads the verified research + style guide + narrative architectures and writes a ~1,850-word narration script. On the first line it declares the chosen architecture:

```
ARCHITECTURE: Forensic Case Study
```

The four architectures (defined in `workflows/guides/narrative_architectures.md`):

- **Forensic Case Study** — Opens with a strange symptom → investigation → mechanism → ordinary implication
- **Historical Reversal** — Old "truth" → study that broke it → mechanism → what viewer now knows
- **Socratic Challenge** — Opens with a hard question → logical steps → answer → question reframed
- **Systems Audit** — Brain/behavior as system → failure mode → trigger → what system optimizes for

After the architecture body, every script ends with a **mandatory Permission Practice section** (exactly 4 numbered embodied micro-practices, header *"Four things you can [verb], when [trigger]:"*), then the architecture's own recognition close. The recognition still has the final word — the tips are a beat before it. Full spec in `workflows/guides/narrative_architectures.md` under "Permission Practice closing section (universal)".

**Review `md/03a_draft.md`:**

- Architecture declared on line 1?
- Hook opens with empathy and names the viewer's specific experience?
- Written in second person throughout?
- Word count ~1,500–2,100 (bumped from prior ~1,400–2,000 to absorb the Permission Practice section)?
- All claims come from Verified Claims in `02_verified_research.md`?
- No `[IMAGE: ...]` markers (Agent 5 handles those separately)?
- **Permission Practice section present**, exactly 4 numbered items, header matches template, each tip is embodied (somatic / noticing / naming / micro-threshold — not scheduling, list-making, "talk to a therapist", or any productivity-blog-flavored advice)?
- **Recognition close still after** the Permission Practice section — the script does NOT end on a tip?

Edit the file directly before running 3n. The novelty agent reads whatever is in `03a_draft.md`.

---

## Agent 3n — Phrase & Structure De-duplication

```bash
python tools/pipeline/agent3n_novelty.py "emotional-dysregulation-in-adhd"
```

Catches reuse of phrases, metaphors, and structural beats from prior shipped scripts. Runs three passes:

- **Pass A — literal 4-gram match.** Deterministic Python. Tokenizes the draft and every prior `outputs/videos/*/md/06_script_narration.md`, builds a 4-token n-gram index, flags every span the draft shares with the corpus. Skips n-grams composed entirely of stopwords.
- **Pass B — Claude semantic / structural check.** One Claude call. Flags paraphrased sentences, reused metaphor templates, and reused opening / closing beat patterns that the n-gram pass misses.
- **Pass C — rewrite.** If anything was flagged, Claude rewrites ONLY the flagged spans in place and the agent loops back to Pass A. Up to **3 iterations**. The pre-novelty draft is preserved once at `md/03a_draft.bak.md`.

Final verdict written to `md/03_novelty_report.md`:
- `PASS` — no duplicates found, draft unchanged
- `PASS_AFTER_REWRITE` — duplicates found and resolved
- `RESIDUAL_AFTER_3_ATTEMPTS` — some semantic / structural findings survive after 3 rewrite passes; needs manual review

**Review `md/03_novelty_report.md`:**
- Verdict line at the top
- Per-iteration literal duplicates with source slug + line
- Per-iteration semantic findings with `type` (paraphrase / metaphor / structure), the echoed corpus phrase, and the reason
- If verdict is `RESIDUAL_AFTER_3_ATTEMPTS`, decide whether to manually rewrite the residual spans in `md/03a_draft.md` before Agent 3b, or accept the residual

If the corpus is empty (first video in the channel), the agent short-circuits, writes a `SKIPPED` report, and exits cleanly. Agent 3b reads the (possibly unchanged) `md/03a_draft.md`.

To revert to the pre-novelty draft: `copy outputs/{slug}/md/03a_draft.bak.md outputs/{slug}/md/03a_draft.md`.

---

## Agent 3b — Critic

```bash
python tools/pipeline/agent3b_critic.py "emotional-dysregulation-in-adhd"
```

Claude re-reads the draft as "a first-time viewer who will close the tab if bored." Identifies the single weakest moment and produces:

```markdown
## Weakest Moment
[exact quoted passage from the draft]

## Why It's Weak
[one sentence from the viewer's perspective]

## Suggested Rewrite
[critic's proposed replacement prose]
```

**Review `md/03b_critique.md`:**
- Does the identified weakness match your own reading of the draft?
- Is the suggested rewrite actually better?

You can **edit the Suggested Rewrite section** before running 3c. Agent 3c applies whatever is in this file — so if you want to steer the rewrite in a different direction, change it here.

---

## Agent 3c — Rewrite

```bash
python tools/pipeline/agent3c_rewrite.py "emotional-dysregulation-in-adhd"
```

Claude applies the critique's rewrite to the original draft. Only the identified weak section is replaced — everything else stays exactly as written. Returns the complete script.

Output is `md/03_script_draft.md` — this is the file Agent 4 reads.

**Review `md/03_script_draft.md`:**
- Does the rewritten section flow naturally with the rest?
- Word count still ~1,400–2,000?
- No new claims introduced that aren't in the verified research?

---

## Output Folder

```
outputs/{slug}/
  md/
    02_verified_research.md    (Agent 2 — input)
    03a_draft.md               (Agent 3a — first draft; possibly rewritten by 3-Novelty)
    03a_draft.bak.md           (Agent 3n — pre-novelty backup, first run only)
    03_novelty_report.md       (Agent 3n — per-iteration duplicate log + verdict)
    03b_critique.md            (Agent 3b — critic analysis, editable)
    03_script_draft.md         (Agent 3c — final draft, feeds Agent 4)
```

---

## Common Issues

| Error | Fix |
|-------|-----|
| `md/02_verified_research.md not found` | Run Agent 2: `python tools/pipeline/agent2_verify.py "{slug}"` |
| `md/03a_draft.md not found` | Run Agent 3a before 3-Novelty / 3b |
| `md/03b_critique.md not found` | Run Agent 3b before 3c |
| `3n` verdict is `RESIDUAL_AFTER_3_ATTEMPTS` | Review residual semantic findings in `md/03_novelty_report.md`; either manually rewrite the spans in `md/03a_draft.md` and re-run `agent3n_novelty.py`, or accept and proceed to 3b |
| `ANTHROPIC_API_KEY is missing` | Add key to `.env` |
| Word count well under 1,400 | Topic too broad — narrow the research and re-run 3a |

---

## Next Step

```bash
python tools/pipeline/agent4a_edit.py "emotional-dysregulation-in-adhd"
```
