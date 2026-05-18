# What Porn Does to Your Brain — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the full SENSUM production pipeline for the video "What Porn Does to Your Brain?" and produce a publish-ready package: verified script, ~60–75 brand-style images, YouTube metadata, and thumbnails.

**Architecture:** Six sequential pipeline agents (Research → Verify → Script → Edit → Images → Publish) with three mandatory manual review gates. Each agent reads the previous agent's output from `outputs/what-porn-does-to-your-brain/`. No code is written — all tools already exist in `tools/`.

**Tech Stack:** Python 3.10+, Gemini 2.5 Pro (research/verify), Claude Opus 4.7 (script/edit/metadata), Vertex AI Imagen 3.0 (images), PubMed API (research)

---

## Slug Reference

All commands use this slug: `what-porn-does-to-your-brain`

All outputs land in: `outputs/what-porn-does-to-your-brain/`

---

## Task 1: Research

**Files:**
- Reads: *(nothing — first step)*
- Creates: `outputs/what-porn-does-to-your-brain/01_research.md`

- [ ] **Step 1: Run Agent 1**

```bash
python tools/agent1_research.py "What Porn Does to Your Brain?"
```

Expected runtime: 60–120 seconds. You'll see Gemini and PubMed queries printed to stdout.

- [ ] **Step 2: Verify output passes quality bar**

Open `outputs/what-porn-does-to-your-brain/01_research.md` and check all three:

1. The **Studies Referenced** table contains entries with real DOIs (not "N/A" throughout)
2. The raw research section names specific authors and years (e.g. "Grubbs et al., 2015")
3. At least one paper is relevant to each of the three mechanisms: reward circuits, moral incongruence, relationship/intimacy effects

If the Studies table is mostly empty or only pop-science sources appear, re-run with a narrower topic string: `"moral incongruence pornography use psychology"` — then merge results manually.

- [ ] **Step 3: Commit research output**

```bash
git add outputs/what-porn-does-to-your-brain/01_research.md
git commit -m "research: agent1 output for what-porn-does-to-your-brain"
```

---

## Task 2: Verify Claims

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/01_research.md`
- Creates: `outputs/what-porn-does-to-your-brain/02_verified_research.md`

- [ ] **Step 1: Run Agent 2**

```bash
python tools/agent2_verify.py "what-porn-does-to-your-brain"
```

Note: Agent 2 takes the **slug** (not the topic string) as its argument.

Expected runtime: 60–90 seconds.

- [ ] **Step 2: Review verified claims — CRITICAL GATE**

Open `outputs/what-porn-does-to-your-brain/02_verified_research.md`.

Check the summary line at the top, e.g.: `Verified: 14 claims | Flagged: 3 claims | Removed: 1 claim`

**Pass criteria:**
- `Verified` count ≥ 10 claims
- At least 2 VERIFIED claims covering each mechanism:
  - Mechanism 1 (reward circuits / dopamine / attentional bias)
  - Mechanism 2 (moral incongruence / perceived addiction / religiosity)
  - Mechanism 3 (relationship satisfaction / partner effects / intimacy)
- `Removed` count = 0 ideally; if any claims are removed, read them — they must not appear in the script
- Read every FLAGGED claim and decide: acceptable risk or needs stronger source?

**If Verified count < 10:** Re-run Agent 1 with a more specific query targeting the weakest mechanism, then re-run Agent 2.

**If moral incongruence claims are absent:** This is the most important mechanism. Add this directly to `01_research.md` under Studies Referenced and re-run Agent 2:
- Grubbs JB, Volk F, Exline JJ, Pargament KI (2015). Internet pornography use: Perceived addiction, psychological distress, and the validation of a brief measure. *Journal of Sex & Marital Therapy*, 41(1), 83–106. DOI: 10.1080/0092623X.2013.842192

- [ ] **Step 3: Commit verified research**

```bash
git add outputs/what-porn-does-to-your-brain/02_verified_research.md
git commit -m "verify: agent2 output for what-porn-does-to-your-brain"
```

---

## Task 3: Write Script

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/02_verified_research.md`
- Creates: `outputs/what-porn-does-to-your-brain/03_script_draft.md`

- [ ] **Step 1: Run Agent 3**

```bash
python tools/agent3_script.py "what-porn-does-to-your-brain"
```

Expected runtime: 3–5 minutes (3-pass: draft → critic → rewrite via Claude Opus 4.7). You'll see pass labels printed to stdout.

- [ ] **Step 2: Review script quality**

Open `outputs/what-porn-does-to-your-brain/03_script_draft.md` and check:

1. **Word count:** Target 1,600–1,900 words. Count via `wc -w` or manually estimate.
2. **Hook:** First 150 words should name the viewer's experience (shame, curiosity) — not start with "In this video..." or a statistic.
3. **Three mechanisms present:** Confirm reward sensitization, moral incongruence, and intimacy/relationship effects each get their own named section.
4. **Moral incongruence framing:** The word "incongruence" or "values gap" should appear. Mechanism 2 must not reduce shame purely to biology — the Grubbs framework (values mismatch, not frequency) must be present.
5. **IMAGE markers:** Count `[IMAGE: ...]` occurrences — expect 40–75. If fewer than 30, script is too short or markers were dropped.
6. **"Addiction" usage:** Search for the word "addiction". Every instance must be qualified (e.g. "what researchers call perceived addiction", "not classified as addiction in the DSM-5").
7. **Controversy acknowledgment:** The hook or opening section should name the scientific debate — "porn addiction" is not in the DSM-5, and researchers disagree. This must appear before Mechanism 1, not buried later.
8. **Outro:** Last paragraph should address the viewer's agency, not their behavior. Should not end on a statistic.

If any check fails, note the specific issue and re-run Agent 3. Agent 3 is non-deterministic — a second run often resolves structural problems.

- [ ] **Step 3: Commit script draft**

```bash
git add outputs/what-porn-does-to-your-brain/03_script_draft.md
git commit -m "script: agent3 draft for what-porn-does-to-your-brain"
```

---

## Task 4: Copy-Edit Script

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/03_script_draft.md`
- Creates: `outputs/what-porn-does-to-your-brain/04_script_final.md`

- [ ] **Step 1: Run Agent 4**

```bash
python tools/agent4_edit.py "what-porn-does-to-your-brain"
```

Expected runtime: 2–3 minutes.

- [ ] **Step 2: Review edits**

Open `outputs/what-porn-does-to-your-brain/04_script_final.md`.

Check:
1. `[EDITOR NOTE: ...]` annotations are present (confirms edit pass ran)
2. No EDITOR NOTE touches a scientific claim (edits should be prose-only: passive → active, hedging → confident)
3. All `[IMAGE: ...]` markers are intact and unchanged
4. The "addiction" qualification check from Task 3 still holds in the edited version

- [ ] **Step 3: Run Agent 4.5 (Titles)**

```bash
python tools/agent4_titles.py "what-porn-does-to-your-brain"
```

Open `outputs/what-porn-does-to-your-brain/045_titles_hooks.md`. Pick your preferred title — you'll need it in Task 7 when Agent 6 generates thumbnails.

- [ ] **Step 4: Commit final script**

```bash
git add outputs/what-porn-does-to-your-brain/04_script_final.md outputs/what-porn-does-to-your-brain/045_titles_hooks.md
git commit -m "edit: agent4 final script + titles for what-porn-does-to-your-brain"
```

---

## Task 5: Extract Image Prompts — REVIEW GATE

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/04_script_final.md`
- Creates: `outputs/what-porn-does-to-your-brain/image_prompts.md`

- [ ] **Step 1: Run Agent 5 Phase 1**

```bash
python tools/agent5_images.py "what-porn-does-to-your-brain"
```

This extracts `[IMAGE: ...]` markers and expands them into full Imagen prompts. Does NOT generate images yet.

- [ ] **Step 2: Review and edit image_prompts.md — CRITICAL GATE**

Open `outputs/what-porn-does-to-your-brain/image_prompts.md`.

This is your only chance to edit prompts before images are generated. Read every prompt and apply these rules:

**For shame/distress scenes:**
- Good: `"A faceless mannequin figure seated on the floor, knees pulled to chest, cross-hatched shadows pressing in from all sides, heavy negative space above, scientific etching style, #F4E5CA background, #582F0E ink"`
- Bad: `"a person feeling ashamed"` — too vague, will produce generic output

**For brain/neuroscience scenes:**
- Good: `"Anatomical cross-section diagram of a human brain with reward pathway highlighted in dense cross-hatching, arrow indicating dopamine release pathway, scientific journal engraving style, #582F0E on #F4E5CA"`
- Bad: `"brain with dopamine"` — Imagen needs spatial and stylistic specificity

**For relationship/intimacy scenes:**
- Good: `"Two faceless mannequin silhouettes seated at opposite ends of a long bench, space between them filled with dense cross-hatching, one figure's hand extended toward the other but not reaching, #582F0E on #F4E5CA"`
- Bad: `"couple with distance between them"` — no style anchor

**Brand rules to enforce on any weak prompt:**
- Must specify: `scientific etching style` or `19th-century scientific journal engraving`
- Must specify: `#F4E5CA background` and `#582F0E ink`
- Must specify: `faceless mannequin` for any human figure
- No text, labels, or words in any scene
- No color other than the two brand colors

Edit directly in `image_prompts.md` before proceeding.

- [ ] **Step 3: Commit reviewed prompts**

```bash
git add outputs/what-porn-does-to-your-brain/image_prompts.md
git commit -m "prompts: reviewed image_prompts for what-porn-does-to-your-brain"
```

---

## Task 6: Generate Images

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/image_prompts.md`
- Creates: `outputs/what-porn-does-to-your-brain/images/image_001.png` … `image_NNN.png`

- [ ] **Step 1: Run Agent 5 Phase 2**

```bash
python tools/agent5_images.py "what-porn-does-to-your-brain" --generate
```

Expected runtime: 5–15 minutes depending on image count. Cost: ~$0.04 per image (60–75 images ≈ $2.40–$3.00).

- [ ] **Step 2: Verify image output**

Open `outputs/what-porn-does-to-your-brain/images/`.

Check:
1. Image count matches the prompt count in `image_prompts.md`
2. Spot-check 10 random images — confirm #F4E5CA background and #582F0E ink (no other colors present)
3. Confirm no text or labels appear in any image
4. Confirm faceless mannequin is used for all human-figure scenes (no faces rendered)

**To regenerate a specific image:** Edit its prompt in `image_prompts.md` and re-run Phase 2 — already-generated images are overwritten by filename, others are skipped.

- [ ] **Step 3: Commit images**

```bash
git add outputs/what-porn-does-to-your-brain/images/
git commit -m "images: generated visuals for what-porn-does-to-your-brain"
```

---

## Task 7: YouTube Metadata — REVIEW GATE

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/04_script_final.md`, `outputs/what-porn-does-to-your-brain/images/`
- Creates: `outputs/what-porn-does-to-your-brain/06_publish_draft.md`

- [ ] **Step 1: Run Agent 6 Pass 1**

```bash
python tools/agent6_publish.py "what-porn-does-to-your-brain"
```

Expected runtime: 3–5 minutes. Generates title options, description, chapters (timestamps), bibliography, tags.

- [ ] **Step 2: Review publish draft — REVIEW GATE**

Open `outputs/what-porn-does-to-your-brain/06_publish_draft.md`.

Check and decide:
1. **Title:** Pick one of the 5 generated options (or write your own). Keep it under 60 characters. Confirm it doesn't use banned language ("shocking truth", "hack", "toxic").
2. **Description:** First 150 characters (above the fold) should hook the viewer, not summarize the video. Edit if needed.
3. **Chapters:** Timestamps should align with the three-mechanism structure. Verify chapter names don't use "addiction" without qualification.
4. **Bibliography:** Check that every cited paper has a DOI and is peer-reviewed (not Psychology Today, WebMD, or news sources).
5. **Tags:** Should include psychology-relevant and YouTube-searchable terms. Add any obviously missing terms.

Edit `06_publish_draft.md` directly before proceeding to thumbnails.

- [ ] **Step 3: Commit publish draft**

```bash
git add outputs/what-porn-does-to-your-brain/06_publish_draft.md
git commit -m "publish: agent6 pass1 metadata for what-porn-does-to-your-brain"
```

---

## Task 8: Thumbnails

**Files:**
- Reads: `outputs/what-porn-does-to-your-brain/06_publish_draft.md`
- Creates: `outputs/what-porn-does-to-your-brain/thumbnails/thumbnail_01–05.png`
- Creates: `outputs/what-porn-does-to-your-brain/06_publish_package.md`

- [ ] **Step 1: Run Agent 6 Pass 2**

```bash
python tools/agent6_publish.py "what-porn-does-to-your-brain" --thumbnails
```

Generates 5 thumbnail compositions via Imagen + PIL text overlay with EB Garamond title text in SENSUM brand colors.

- [ ] **Step 2: Review thumbnails**

Open `outputs/what-porn-does-to-your-brain/thumbnails/`.

Check:
1. Title text is readable at small sizes (YouTube thumbnail renders at ~168×94px in search)
2. Background is #F4E5CA (sage beige), text/ink is #582F0E (dark brown)
3. No other colors present
4. Pick your preferred thumbnail

- [ ] **Step 3: Commit final package**

```bash
git add outputs/what-porn-does-to-your-brain/thumbnails/ outputs/what-porn-does-to-your-brain/06_publish_package.md
git commit -m "thumbnails: final publish package for what-porn-does-to-your-brain"
```

---

## Verification Checklist (End-to-End)

Before calling the video complete, confirm all of the following:

- [ ] `02_verified_research.md` has ≥10 VERIFIED claims, 0 REMOVED claims
- [ ] At least 2 verified sources each for: reward circuits, moral incongruence, relationship effects
- [ ] `04_script_final.md` uses "addiction" only with qualification throughout
- [ ] Moral incongruence / values-gap framing is the emotional center of Mechanism 2
- [ ] Hook names the shame experience within the first 90 seconds
- [ ] Outro addresses viewer agency, not behavior
- [ ] Image count ≥ 40 and all images pass brand color check (#F4E5CA + #582F0E only)
- [ ] No faces in any image (faceless mannequin only)
- [ ] Publish package includes: title, description, chapters, bibliography, 5 thumbnail options

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Agent 2 returns `Verified: 0 claims` | Topic too broad for PubMed. Re-run Agent 1 with `"moral incongruence pornography Grubbs"` |
| Agent 3 script has no IMAGE markers | Re-run Agent 3 — the model occasionally drops markers; second run almost always fixes it |
| Agent 5 Phase 1: `No [IMAGE: ...] markers found` | Run Agent 4 edit again — check that `04_script_final.md` still contains `[IMAGE:` strings |
| Imagen generates faces on mannequin figures | Add `"smooth featureless blank oval head, no eyes nose mouth ears hair, NO FACE"` to the affected prompt |
| Background color is white not beige | This is post-processed in code by `agent5_images.py` — check that script ran without errors |
| `Vertex AI error: Application Default Credentials not found` | Run `gcloud auth application-default login` in terminal |
