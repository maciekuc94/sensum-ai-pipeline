# Workflow: Script Writing (B++ v2 chain — in-session on Opus 4.8)

## Purpose

Step 3 produces the production-ready Polish script via three passes, **all running in-session in Claude Code on Opus 4.8 (no API)** since 2026-05-29:

1. **3a Drafter** — writes the first complete draft from verified research, **voice-first (two stages: write native Polish, then apply doctrine)** (prompt: `03a_drafter.md`)
2. **3b Revisor** — full-script revision pass: **MOVE 0 naturalness sweep (open-ended)** + 11 named diff-derived moves (prompt: `03b_revisor.md`)
3. **3c Reviewer** — judges the revised script (PASS / FLAG) without rewriting, **incl. category J (translationese / native-ear gate)** (prompt: `03c_reviewer.md`)

The Revisor and Reviewer run in a **loop** (max 5 iterations, exits on PASS). If the Reviewer flags critical issues, the Revisor re-runs with that feedback. The loop **never returns to the Drafter** — the Drafter runs once. The whole chain is orchestrated by the `/draft` slash command in one session, at zero API cost.

When the loop exits (PASS, or max iterations hit), the final revised draft is copied to `md/04_final.md`. If it exited on FLAG at max iterations, a warning header is prepended.

| Agent | Pass | Model | Input | Output |
|-------|------|-------|-------|--------|
| 3a | Drafter | Opus 4.8 (Claude Code, in-session) | `md/02_verified_research.md` | `md/03a_draft.md` |
| 3b | Revisor (iter N) | Opus 4.8 (in-session) | `md/03a_draft.md` (+ `md/03c_review_iter{N-1}.md` if iter > 1) | `md/03b_revised_iter{N}.md` |
| 3c | Reviewer | Opus 4.8 (in-session) | `md/03b_revised_iter{N}.md` | `md/03c_review_iter{N}.md` |
| Finalize | Loop exit | — | latest `03b_revised_iter{N}.md` | `md/04_final.md` |

**Legacy fallback:** the former Gemini-3.1-Pro path still exists behind `agent3.py` (orchestrator) + `agent3b_revisor.py` / `agent3c_reviewer.py` for `--api` runs. It is not the default and not needed in normal operation.

---

## Prerequisites

- `outputs/videos_pl/{slug}/md/02_verified_research.md` must exist (Agent 2 output)
- `workflows/guides/style_guide.md`, `workflows/guides/narrative_architectures.md`, and `workflows/guides/voice_corpus.md` present (Polish versions; `voice_corpus.md` is the native-ear anchor read by 3a/3b/3c)
- An active Claude Code session on Opus 4.8 (the model that runs all three passes)
- No API key needed for the default path. (`GOOGLE_CLOUD_PROJECT` + `gcloud` auth are only needed for the legacy `--api` Gemini fallback.)

---

## Default invocation (full chain, in-session)

In Claude Code:

```text
/draft <slug>
```

That slash command (see `.claude/commands/draft.md`) does everything in-session (default architecture `Composite Portrait`; pass `/draft <slug> "<name>"` to force a short-form architecture):

1. **3a Drafter** — reads research + style guides + `03a_drafter.md`, writes the Polish narration script, saves `md/03a_draft.md`.
2. **Loop (3b ↔ 3c)** — for each iteration N:
   - 3b Revisor (per `03b_revisor.md`) → `md/03b_revised_iter{N}.md`
   - 3c Reviewer (per `03c_reviewer.md`, fresh critical pass) → `md/03c_review_iter{N}.md`
   - read the `## VERDICT` line: PASS → finalize; FLAG and N < max → loop with feedback; FLAG at max → finalize with warning header.
3. **Finalize** — copy the last `03b_revised_iter{N}.md` → `md/04_final.md`.

No Python orchestrator is involved in the default path. (`agent3.py` remains only as the legacy Gemini `--api` fallback over an existing `md/03a_draft.md`.)

---

## The three prompt specs (single source of truth)

- **3a Drafter** → `workflows/pipeline/03a_drafter.md`
- **3b Revisor** → `workflows/pipeline/03b_revisor.md`
- **3c Reviewer** → `workflows/pipeline/03c_reviewer.md`

Read the matching spec at each pass and follow it exactly. The summaries below are orientation only — the specs are authoritative.

### Agent 3a — Drafter

First line declares the architecture:

```text
ARCHITECTURE: Composite Portrait
```

Five architectures (defined in `workflows/guides/narrative_architectures.md`). **`Composite Portrait` is the default**; all five are written at the channel's native length (~10–15 min / ~1,500–1,750 Polish words), and the other four are only used when `/draft <slug> "<name>"` forces them:
- **Composite Portrait** (default) — one archetype figure through Surface → Cost → Origin → Reframe; **full second person „ty"** (voice braid retired 2026-05-29); recurring object-motif
- **Forensic Case Study** — strange symptom → investigation → mechanism → ordinary implication
- **Historical Reversal** — old "truth" → study that broke it → mechanism → what the viewer now knows
- **Socratic Challenge** — hard question → logical steps → answer → question reframed
- **Systems Audit** — brain/behavior as system → failure mode → trigger → what the system optimizes for

After the architecture body, every script ends with the **mandatory Permission Practice section** (~4 embodied micro-practices as flowing prose — "Czasem wystarczy…" — NOT a numbered list), then the architecture's recognition close — which still has the final word.

**Review `md/03a_draft.md`:** architecture on line 1; empathy-first hook naming the viewer's experience; **voice = full second person „ty" in all architectures including Composite Portrait** (no 3rd-person figure); word count ~1,500–1,750 Polish words (~10–15 min) for all architectures; one central metaphor; claims only from Verified Claims; no `[IMAGE: ...]` markers; Permission Practice present as prose; recognition close after it.

### Agent 3b — Revisor (in-session; legacy `agent3b_revisor.py --api`)

Re-reads the entire script. **MOVE 0 — naturalness sweep (open-ended, primary):** read every sentence aloud in your head; if it doesn't sound like natural spoken Polish (calque, awkward genitive, register clash) rewrite it for fluency even if it matches none of the named patterns. Reference: `voice_corpus.md` §A (target) / §C (calques to avoid). Then the 11 named moves:

1. **Embodied clarity** (cut meta-language)
2. **Cut redundancy** (negative-positive duplicates)
3. **De-judging tone** ("złamane" → "nie tak")
4. **Generalize personal details** (categorical > biographical)
5. **Symbolic metaphor over numbered lists**
6. **Diagnostic over collapse-narrative**
7. **Agency in Permission Practice** (active verbs)
8. **Softening pressure** (temporal softeners)
9. **Full „ty"** — convert residual 3rd-person figure
10. **Thin secondary metaphors** (one central metaphor)
11. **Thin attention-imperatives** (≤2–3)

Constraints: preserve length ±10%, voice, architecture choice. Leave a sentence untouched **only if it is already natural Polish** (MOVE 0), not merely because it matches no named pattern. No stage directions or `[...]` markers — the Reviewer scans clean text. On iteration 2+, address only the issues the Reviewer flagged, preserving everything else. **Output:** `md/03b_revised_iter{N}.md`.

### Agent 3c — Reviewer (in-session; legacy `agent3c_reviewer.py --api`)

Reads the revised script and judges against critical-issue categories. **Does not rewrite.** Emits the rigid schema (first line after `## VERDICT` is exactly `PASS` or `FLAG`):

```markdown
## VERDICT
PASS  (or FLAG)

## Critical Issues
- **[Category]**: "exact quote" → suggestion direction

## Minor Notes (informational, don't block ship)
- ...

## Telemetry
- Iteration: N
- Word count: ~NNN
- Architecture: <declared>
```

Critical-issue categories (each triggers FLAG): **A.** Permission Practice integrity (now prose, not numbered) · **B.** Banned phrases · **C.** Abstract-meta language · **D.** Voice inconsistency (kalki, bezosobowe, hedging; **full „ty" required everywhere — 3rd-person figure „ktoś" now FLAGs**) · **E.** Numbered list anywhere (incl. PP) · **F.** Research-numbers (incl. uncited round-number stats) · **G.** Imienne biograficzne szczegóły · **H.** Composite Portrait integrity (4 movements, figure+motif, full „ty") · **I.** Metaphor overload (one central metaphor only) · **J.** Idiomatic Polish / translationese — the native-ear gate that replaces the owner's manual Copilot pass; FLAG at ≥2 calque/awkward sentences (ref `voice_corpus.md` §C). Reviewer **defaults to FLAG when uncertain** — better an extra iteration than a lenient PASS. **Output:** `md/03c_review_iter{N}.md`.

---

## Output Folder

```text
outputs/videos_pl/{slug}/
  md/
    02_verified_research.md         (Agent 2 — input)
    03a_draft.md                    (Agent 3a — first draft, immutable after creation)
    03b_revised_iter{N}.md          (Agent 3b — one file per iteration)
    03c_review_iter{N}.md           (Agent 3c — verdict + flagged issues, per iteration)
    04_final.md                     (copy of the latest 03b_revised_iter{N}.md after PASS or max-iter)
```

If `04_final.md` was shipped after a FLAG at max iterations, the warning header points at `md/03c_review_iter{N}.md` (highest N) — review it before recording voiceover.

---

## Common Issues

| Error / situation | Fix |
|---|---|
| `md/02_verified_research.md not found` | Run Agent 2: `python tools/pipeline/agent2_verify.py "{slug}"` |
| Loop won't converge (FLAG every iteration) | Read the highest `md/03c_review_iter{N}.md`. Apply its fixes by hand in `md/04_final.md`, or re-run `/draft` after tightening the draft. |
| Want fewer/more loop passes | The in-session loop default is max 5; stop earlier if PASS. (Legacy `agent3.py --max-iterations N` applies to the `--api` fallback only.) |
| Word count well under 1,500 | Topic too broad — narrow the research and re-run `/draft` |
| Need the legacy Gemini path | `python tools/pipeline/agent3.py "{slug}"` (requires `md/03a_draft.md`; uses Vertex AI / `GOOGLE_CLOUD_PROJECT`) |

---

## Next Step

The hook gate, also in-session:

```text
/hook <slug>
```

Then in parallel: Agents 5 (`/visuals`), 6 (narration), 8 (publish).
