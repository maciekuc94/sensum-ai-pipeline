# Workflow: Script Writing (B++ v2 chain)

## Purpose

Step 3 produces the production-ready Polish script via three agents:

1. **3a Drafter** (Opus 4.7) — writes the first complete draft from verified research
2. **3b Revisor** (Sonnet 4.6) — runs a full-script Copilot-style revision pass applying 8 diff-derived revision moves
3. **3c Reviewer** (Sonnet 4.6) — judges the revised script (PASS / FLAG) without rewriting

The Revisor and Reviewer run in a **loop** (max 2 iterations by default). If Reviewer flags critical issues, Revisor re-runs with the feedback. The loop **never returns to the Drafter** — caps cost at 1 Opus call + 2–4 Sonnet calls per script.

When the loop exits (PASS, or max iterations hit), the final revised draft is copied to `md/04_script_final.md` — same downstream interface as before.

| Agent | Pass | Model | Input | Output |
|-------|------|-------|-------|--------|
| 3a | Drafter | Opus 4.7 | `md/02_verified_research.md` | `md/03a_draft.md` |
| 3b | Revisor (iter N) | Sonnet 4.6 | `md/03a_draft.md` (+ `md/03_review.md` if iter > 1) | `md/03_script_draft.md` (overwrites per iter) |
| 3c | Reviewer | Sonnet 4.6 | `md/03_script_draft.md` | `md/03_review.md` |
| Orchestrator | Loop + finalize | — | — | copies `03_script_draft.md` → `04_script_final.md` |

---

## Prerequisites

- `outputs/videos_pl/{slug}/md/02_verified_research.md` must exist (Agent 2 output)
- `ANTHROPIC_API_KEY` set in `.env`
- `workflows/guides/style_guide.md` and `workflows/guides/narrative_architectures.md` present (Polish versions)

---

## Default invocation (full chain)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent3.py "<slug>"
```

The orchestrator runs:
1. Agent 3a (Drafter)
2. Loop iter 1: Agent 3b (Revisor) → Agent 3c (Reviewer)
3. If verdict FLAG and iter < max: Loop iter 2: Agent 3b (with Reviewer feedback) → Agent 3c
4. Copy revised draft → `04_script_final.md`. If still FLAG at max iter, prepend warning header.

### Flags

| Flag | Effect |
|------|--------|
| `--max-iterations N` | Cap on Revisor↔Reviewer loops (default 2) |
| `--skip-drafter` | Start from existing `md/03a_draft.md` (e.g. after manual edit) |

---

## Running individual agents (for inspection / manual gates)

### Agent 3a — Drafter

```bash
python tools/pipeline/agent3a_draft.py "<slug>"
```

Claude reads verified research + style guide + narrative architectures and writes a Polish narration script (~1,700 words / ~14 min). First line declares the architecture:

```
ARCHITECTURE: Systems Audit
```

Four architectures (defined in `workflows/guides/narrative_architectures.md`):
- **Forensic Case Study** — Opens with strange symptom → investigation → mechanism → ordinary implication
- **Historical Reversal** — Old "truth" → study that broke it → mechanism → what viewer now knows
- **Socratic Challenge** — Hard question → logical steps → answer → question reframed
- **Systems Audit** — Brain/behavior as system → failure mode → trigger → what system optimizes for

After the architecture body, every script ends with the **mandatory Permission Practice section** (exactly 4 numbered embodied micro-practices, header *"Cztery rzeczy, które możesz [czasownik], kiedy [wyzwalacz]:"*), then the architecture's recognition close. The recognition still has the final word — the tips are a beat before it.

**Review `md/03a_draft.md`:**
- Architecture declared on line 1?
- Hook opens with empathy, names viewer's specific experience?
- Written in second person ("ty/twój") throughout?
- Word count ~1,500–1,750?
- All claims from Verified Claims in `02_verified_research.md`?
- No `[IMAGE: ...]` markers (Agent 5 handles those)?
- Permission Practice section present, exactly 4 numbered items, embodied (somatic / noticing / naming / micro-threshold)?
- Recognition close after the Permission Practice section?

### Agent 3b — Revisor

```bash
python tools/pipeline/agent3b_revisor.py "<slug>"
python tools/pipeline/agent3b_revisor.py "<slug>" --iteration 2
```

Claude (Sonnet 4.6) re-reads the entire script and applies 8 revision moves on every sentence:

1. **Embodied clarity** (cut meta-language)
2. **Cut redundancy** (negative-positive duplicates)
3. **De-judging tone** ("złamane" → "nie tak")
4. **Generalize personal details** (categorical > biographical)
5. **Symbolic metaphor over numbered lists**
6. **Diagnostic over collapse-narrative**
7. **Agency in Permission Practice** (active verbs)
8. **Softening pressure** (temporal softeners)

Constraints: preserve length ±10%, voice, architecture choice. If a sentence is already good, leave it. No stage directions or `[EDITOR NOTE]` inline — Reviewer scans clean text.

**On iteration 2+:** Revisor also reads `md/03_review.md` (Reviewer's flagged issues from the previous iteration) and addresses only those issues — preserving everything else the Reviewer didn't flag.

**Output:** `md/03_script_draft.md` (overwritten each iteration).

### Agent 3c — Reviewer

```bash
python tools/pipeline/agent3c_reviewer.py "<slug>"
```

Claude (Sonnet 4.6) reads the revised script and judges against critical-issue categories. **Does not rewrite.** Outputs verdict + flagged issues:

```markdown
## VERDICT
PASS  (or FLAG)

## Critical Issues
- **[Category]**: "exact quote" → suggestion direction
- ...

## Minor Notes (informational, don't block ship)
- ...

## Telemetry
- Iteration: N
- Word count: ~NNN
- Architecture: <declared>
```

Critical-issue categories (each triggers FLAG):
- **A.** Permission Practice integrity (4 items / embodied / agency verb / softeners / recognition close after)
- **B.** Banned phrases (research-framing, Polish self-help, academic-textbook)
- **C.** Abstract-meta language patterns
- **D.** Voice inconsistency (kalki z angielskiego, bezosobowe konstrukcje, hedging)
- **E.** Numbered list outside Permission Practice
- **F.** Research-numbers (decimals, effect sizes, study counts)
- **G.** Imienne biograficzne szczegóły

Reviewer is **calibrated to default-FLAG when uncertain** — better an extra iteration than a lenient PASS.

**Output:** `md/03_review.md`.

---

## Output Folder

```
outputs/videos_pl/{slug}/
  md/
    02_verified_research.md    (Agent 2 — input)
    03a_draft.md               (Agent 3a — first draft, immutable after creation)
    03_script_draft.md         (Agent 3b — revised draft, overwritten per iteration)
    03_review.md               (Agent 3c — latest verdict + flagged issues)
    04_script_final.md         (Orchestrator — copy of 03_script_draft.md after PASS or max-iter)
```

If `04_script_final.md` was shipped after a FLAG at max iterations, the orchestrator prepends a warning header — review `md/03_review.md` before recording voiceover.

---

## Common Issues

| Error | Fix |
|-------|-----|
| `md/02_verified_research.md not found` | Run Agent 2: `python tools/pipeline/agent2_verify.py "{slug}"` |
| `md/03a_draft.md not found` | Run Agent 3a or full chain: `python tools/pipeline/agent3.py "{slug}"` |
| `md/03_script_draft.md not found` | Run Agent 3b after 3a |
| `md/03_review.md not found` | Run Agent 3c after 3b |
| Verdict is `FLAG` after 2 iterations | Read `md/03_review.md` flagged issues. Either manually edit `md/03_script_draft.md` and copy to `md/04_script_final.md`, or re-run with `--max-iterations 3` to allow one more loop |
| `ANTHROPIC_API_KEY is missing` | Add key to `.env` |
| Word count well under 1,500 | Topic too broad — narrow the research and re-run 3a |

---

## Next Step

```bash
python tools/pipeline/agent4b_hook.py "<slug>"
```

Then in parallel: Agents 5 (visuals), 6 (narration), 8 (publish).
