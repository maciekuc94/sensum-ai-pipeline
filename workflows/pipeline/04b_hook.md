# Workflow: Agent 4b — Hook Refiner (two-tier, iterative)

## Purpose

Agent 4b is the **final quality gate before recording** — and it does not just score, it **refines**. It evaluates the opening of `04_script_final.md` against a two-tier rubric and iteratively rewrites the first 37 words (the 15-second window) in-place until both tiers pass or the attempt budget is exhausted.

This is the moment where YouTube's algorithm and the viewer's brain both decide whether to keep watching. The full theory lives in [docs/specs/2026-05-15-15-second-hook-research.md](../docs/specs/2026-05-15-15-second-hook-research.md). This workflow is the enforcement layer.

The script chain is: `3a → 3b → 3c → 4a → 4b → record`

---

## Prerequisites

1. **Agent 4a must have run successfully.** The file `outputs/videos/{slug}/md/04_script_final.md` must exist.
2. **Anthropic API key** in `.env`:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   ```
3. **Heads up:** the agent **modifies `04_script_final.md` in place**. On the first run it saves the original opening to `04_script_final.bak.md`. Backups are never overwritten on subsequent runs.

---

## Run Command

```bash
python tools/pipeline/agent4b_hook.py "why-you-can-t-just-relax-on-weekends"
```

Expected output:

```
=== Agent 4b: Hook Refiner (two-tier, iterative) ===
Slug : why-you-can-t-just-relax-on-weekends

[1] Reading md/04_script_final.md...
  Topic: Why You Can't Just Relax on Weekends
  Backup created: md/04_script_final.bak.md

[2.1] Scoring with Claude (attempt 1/3)...
  Tier 1 (15s): 6/10  [██████░░░░]
  Tier 2 (30s): 7/10  [███████░░░]
  Applied rewrite (35 words) to md/04_script_final.md.

[2.2] Scoring with Claude (attempt 2/3)...
  Tier 1 (15s): 8/10  [████████░░]
  Tier 2 (30s): 8/10  [████████░░]
  Both tiers pass thresholds — stopping.

[3] Final verdict: RECORD
  Attempts used: 2/3
  Final 15s score: 8/10
  Final 30s score: 8/10
  Original opening preserved at: md/04_script_final.bak.md
  To revert: copy md/04_script_final.bak.md over md/04_script_final.md

  Log saved: md/04b_hook_score.md

Next: proceed to Agent 5 (visuals) and Agent 6 (narration).
```

---

## The Two-Tier Rubric

### Tier 1 — The 15-Second Window (primary, gating)

First **37 words** of narration (~15 seconds at ~150 wpm). Pass threshold: **≥ 8/10**.

| Dimension | Max | What it asks |
|---|---|---|
| First-Sentence Grip | 3 | Does sentence 1 alone earn sentence 2? Concrete subject, ≤14 words, no abstract stacking. |
| Specificity Within 15s | 3 | Is there a concrete detail/image/number/scene by word 37? |
| Identification Moment | 2 | Has the viewer thought "this is me" by word 37? |
| Loop Opened | 2 | Is there an unresolved question/contradiction the viewer must stay to close? |

### Tier 2 — The 30-Second Hook (secondary)

First **150–200 words**. What happens after the 15s gate opens. Pass threshold: **≥ 7/10**.

| Dimension | Max | What it asks |
|---|---|---|
| Tension | 3 | The unresolved question/contradiction sustains. |
| Personal Relevance | 3 | The viewer keeps feeling this is about them. |
| Specificity | 2 | Concrete details continue; no abstract drift. |
| Forward Momentum | 2 | The last line makes stopping feel impossible. |

### Red flags (each one is a −1 penalty on Tier 1)

- Opens with a rhetorical question ("Have you ever…?")
- Leads with a statistic before any emotional setup
- First sentence > 14 words
- No specific detail by word 25
- "Many people" / "we all" / "most of us"
- Stacked abstract nouns in sentence 1
- Any clause that could be deleted without losing meaning
- Asks viewer to "subscribe", "like", or "stay tuned" in the opening
- Meta-framing ("today we're going to talk about")

The full catalogue and rewrite cheat sheet lives in the research doc, section 4.

---

## The Refine Loop

```
read 04_script_final.md
create backup (.bak.md) on first run only
for attempt in 1..3:
    extract 37-word and 200-word windows
    score both tiers + ask Claude for a ≤37-word rewrite
    log attempt
    if Tier1 ≥ 8 AND Tier2 ≥ 7: stop
    splice rewrite into 04_script_final.md, replacing only the first 37 words
final: write multi-attempt log to 04b_hook_score.md, print verdict
```

The splice is sentence-aware: it replaces the first complete sentences spanning ~37 words and leaves everything after byte-identical (editor notes, image markers, body paragraphs all untouched).

---

## Files Produced

| File | Behavior |
|---|---|
| `outputs/videos/{slug}/md/04_script_final.md` | **Modified in place** — opening replaced if any rewrite was applied. |
| `outputs/videos/{slug}/md/04_script_final.bak.md` | **Created once** on the first refine; never overwritten. |
| `outputs/videos/{slug}/md/04b_hook_score.md` | **Overwritten each run** — full multi-attempt log with both tier breakdowns. |

---

## How to Act on the Output

| Verdict | Meaning | Action |
|---|---|---|
| `record` | Both tiers passed (15s ≥ 8 AND 30s ≥ 7). | Move on to Agent 5 / Agent 6. |
| `polish` | Stopped before MAX_ATTEMPTS but did not pass. (Should not happen in normal flow; indicates a parsing or model issue.) | Re-run once. |
| `rewrite` | Used all 3 attempts and still under threshold. | Open the script and rewrite the opening by hand using the patterns in the research doc, then re-run this agent. |

### To revert the agent's changes

```bash
cp outputs/videos/{slug}/md/04_script_final.bak.md outputs/videos/{slug}/md/04_script_final.md
```

The backup is the untouched output of Agent 4a. Restoring it puts you back in the pre-refiner state without losing anything.

### To re-run after a manual edit

Just run the command again. The backup is preserved (not overwritten), and the loop will converge in fewer attempts once the opening is already strong.

---

## Reference

- Working theory and pattern library: [docs/specs/2026-05-15-15-second-hook-research.md](../docs/specs/2026-05-15-15-second-hook-research.md)
- Architecture choices for the hook shape: [workflows/guides/narrative_architectures.md](../guides/narrative_architectures.md)
- Prior step (script editing): [workflows/pipeline/04a_edit.md](04a_edit.md)

---

## Next Step

Once 4b returns verdict `record`, run visuals and narration in parallel:

```bash
python tools/pipeline/agent5_visuals.py "why-you-can-t-just-relax-on-weekends"
python tools/pipeline/agent6_narration.py "why-you-can-t-just-relax-on-weekends"
```
