---
description: Agent 4 hook gate — score the script opening in-session on Opus 4.8 (no API), then apply the rewrite deterministically.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob
---

# /hook — Agent 4 Hook Refiner (in-session, Opus 4.8)

You run the **final quality gate before recording** in-session — scoring the opening of the script against the two-tier 15s/30s rubric and refining the first 37 words. **No Gemini, no Anthropic API.** Argument `$1` is the slug — a folder name under `outputs/videos_pl/`.

The scoring rubric, red-flag list, rewrite rules, and the mandatory output contract are the single source of truth in `workflows/pipeline/04_hook.md`. Read it and follow it exactly. The deterministic splice/backup/log lives in `agent4_hook.py --apply` (no LLM).

## Workflow

1. **Validate input.** Confirm `outputs/videos_pl/$1/md/04_final.md` exists. If missing, tell the user to run `/draft $1` first, and stop.

2. **Read the rubric.** Load `workflows/pipeline/04_hook.md` — the embedded prompt is exactly what you must execute (Tier 1 / Tier 2 dimensions, red flags, rewrite rules, output format).

3. **Read the script.** Load `outputs/videos_pl/$1/md/04_final.md`. The opening narration (skip the metadata header / `ARCHITECTURE:` line) is your material: the first ~37 words are the Tier 1 window, the first ~200 words are the Tier 2 window.

4. **Score and refine in-session** per the rubric:
   - Score the current opening (Tier 1, Tier 2), list any red flags.
   - If Tier 1 < 8 or Tier 2 < 7, rewrite the first 37 words (≤37 words, channel voice, research-invisible), then re-score the rewritten opening — up to 3 internal passes until both tiers would pass or improvement is exhausted.
   - Report the **final** scores (for the opening contained in `REWRITE_15S`). If the current opening already passes, return it verbatim in `REWRITE_15S`.

5. **Write the structured response** exactly per the `## Output Format - MANDATORY` block in `04_hook.md` (fields `TIER1_SCORE … REWRITE_15S … VERDICT`, English field names, `REWRITE_15S` between `<<<` and `>>>`). Save it verbatim to:
   ```
   outputs/videos_pl/$1/md/04_hook_response.txt
   ```

6. **Apply deterministically** via Bash:
   ```bash
   PYTHONIOENCODING=utf-8 python tools/pipeline/agent4_hook.py "$1" --apply
   ```
   This backs up the original opening once (`04_final.bak.md`), splices `REWRITE_15S` into `04_final.md` if it differs from the current opening, writes the `04_hook.md` log, and deletes the temp response file.
   - **Verify the docx export.** `--apply` also exports `outputs/videos_pl/$1/docx/script.docx`. Confirm that file now exists; if it is absent, the export failed — warn the user, because downstream `/package`, `/visuals`, and `/publish` would silently fall back to `04_final.md` (losing the user's Word/Copilot pass).

7. **Report back** to the user:
   - Final Tier 1 (15s) and Tier 2 (30s) scores
   - Verdict: `RECORD` (both pass) / `polish` / `rewrite`
   - Whether the opening was rewritten in place
   - Next step: edit `docx/script.docx` if needed (save as `script_corrected.docx`), then `/visuals $1` and Agent 8.

## Notes

- **You are the model.** Score and rewrite in this conversation — do NOT call any API and do NOT use the legacy `--api` path (that is the old Gemini fallback).
- Keep scoring honest: a `record` verdict means the opening genuinely clears Tier 1 ≥ 8 and Tier 2 ≥ 7. If you cannot get there in 3 passes, return `rewrite` and let the human take over.
- `04_final.md` is modified in place; the one-time backup at `04_final.bak.md` is the pre-hook state.
