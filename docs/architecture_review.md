# Architecture Review — WAT Framework

Generated 2026-06-02 as part of the maintenance audit.

---

## Decision 1: Dual in-session/API paths — keep intertwined vs. extract legacy

Six pipeline files (agent3.py, agent3b_revisor.py, agent3c_reviewer.py, agent4_hook.py, agent5_visuals.py, agent8_publish.py) carry both the current in-session default path and a `--api` legacy Gemini fallback in the same file.

| Approach | Pros | Cons |
|----------|------|------|
| **Current: `--api` flag inside same file** (recommended) | Single file per agent; fallback is co-located with its default; no extra imports | Files are larger; `--api` branches add ~50–100 lines of cognitive load per file |
| **Extract to `tools/pipeline/_legacy/`** | Clean main files; delete legacy dir when Gemini is no longer needed | 6 new files; callers must import from two places; migration effort for minimal gain |

**Recommendation: keep as-is.** Each legacy branch is 1–2 function calls, clearly marked with `# legacy` comments, and very rarely touched. Extraction would create 6 files with ~50 lines each for no functional benefit. Revisit when/if the Gemini API is formally retired.

---

## Decision 2: agent8_publish.py at ~1,090 lines — monolith vs. modular split

| Approach | Pros | Cons |
|----------|------|------|
| **Current monolith** | Single import; all 5 CLI modes co-located; no cross-file dependencies | ~1,090 lines requires scanning to navigate; all modes share one test surface |
| **Split by mode: `agent8_signals.py`, `agent8_finalize.py`, `agent8_core.py`** | Each file ~250–350 lines; easier to navigate; cleaner test boundaries | 3 files instead of 1; CLAUDE.md + workflow references need updating; no functional change; import complexity increases |
| **Internal section TOC comment (recommended)** | Zero migration cost; immediate navigability win; extensible if file grows | Doesn't reduce file size |

**Recommendation: add TOC comment (done — see `# ── Section Map ──` block at line ~89).** A structural split is appropriate if the file exceeds ~1,500 lines or a second contributor joins. The 10 sections are now clearly indexed; navigating to `--finalize` logic takes 2 seconds.

---

## Decision 3: Prompt management — all prompts now in `workflows/pipeline/`

As of this audit, all pipeline prompts are single-sourced in `workflows/`:

| Agent | Prompt source |
|-------|---------------|
| 0 | `workflows/pipeline/00_materials_prompt.md` (extracted 2026-06-02) |
| 1 | `workflows/pipeline/01_research_prompt.md` (extracted 2026-06-02) |
| 2 | `workflows/pipeline/02_verify_prompt.md` (extracted 2026-06-02) |
| 3a/3b/3c/3d | `workflows/pipeline/03a_drafter.md` etc. (pre-existing) |
| 4 | `workflows/pipeline/04_hook.md` (pre-existing) |
| 5 | `workflows/pipeline/05_visuals.md` (pre-existing) |
| 8 | `workflows/pipeline/08_publish.md` (pre-existing) |

**Loader pattern** (shared across agents 0, 1, 2): `_load_prompt()` reads the `.md` file, strips lines starting with `#` or `<!--`, and returns the clean prompt string. Placeholders use Python `.format()` syntax.

---

## Token Savings Achieved (2026-06-02 audit)

| Change | Estimated savings |
|--------|------------------|
| Prerequisites boilerplate consolidation (3 files) | ~1,200 tokens |
| Requirements.txt dead deps removed | 0 tokens (not loaded by LLMs) |
| Cross-reference added to narrative_architectures.md | Net 0 (added 1 line) |
| Prompts extracted from Python to workflows/ | Structural only — same text |
| **Total** | **~1,200 tokens direct; structural alignment for all 10 prompts** |

Note: The explore agent's initial estimate of ~8,700 tokens was based on duplicated block sizes that turned out to be contextual references, not true duplication. The actual savings are smaller but the structural improvements (cross-links, unified prompt location) have lasting maintenance value.
