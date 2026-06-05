# Agent 8 — Publish Package (in-session, Opus 4.8)

## Purpose

Produce one master file with everything needed to publish the long-form video on YouTube — plus 3–4 Shorts lead-in packages that drive clicks back to the main video.

As of 2026-06-02 Agent 8 runs **in-session on Opus 4.8 (no API)** via `/publish <slug>`, split into **9 focused steps** so each concern gets its own dedicated reasoning pass instead of sharing one mega-prompt. The deterministic parts (YouTube autocomplete scrape, Q1–Q4 quarter tagging, tag char-budget trim, clip-block validation, docx export) stay in `tools/pipeline/agent8_publish.py` and run as `--signals` (before the tags step) and `--finalize` (after the master file is written). The legacy Gemini 3-pass orchestrator survives behind `agent8_publish.py "<slug>" --api`.

**This file is the single source of truth for the 9 step prompts.** The `/publish` command reads it and executes each step in order. Operate as an **Advanced YouTube Metadata Engineer / NLP Optimization Pipeline** — cold, empirical decision logic for tag selection and NLP anchoring; warm, validating speaker voice in the description and Shorts body copy.

**OUTPUT LANGUAGE: Polish.** All generated content (titles, Shorts titles/descriptions, video description, chapter labels, tags) is in Polish for the channel `@sensumpolska`. Script lines quoted verbatim in Shorts packages are left exactly as-is (already Polish from the script chain) — never translate them.

**Research-invisible everywhere.** The script is research-*grounded* but the published copy is research-*invisible*: never name a researcher, a study, or a year in titles, the description, chapters, or Shorts copy. Forbidden research-framing in description/Shorts: "naukowcy odkryli", "badania pokazują", "wyniki badań", "z badań wynika", "naukowcy", "według badań", "studies show", "researchers found". The viewer trusts the speaker, not the citation. Real citations live only in the bibliography (step 5).

---

## Inputs each step shares

- **Narration** — the script body. Source priority: `docx/script_corrected.docx` > `docx/script.docx` > `md/04_final.md`. Strip `## ` section-divider headers and any `[...]` production tags when reading.
- **Topic** — derive a short Polish description of what the video is about (from the script + your step-1 titles).
- Step 4 also reads `.tmp/08_signals.md` (written by `--signals`).
- Step 5 also reads `md/02_verified_research.md`.

---

# STEP 1 — Titles (long-form, 5 candidates)

> **Package handoff (preferred source).** If `md/07_package.md` exists (written by `/package`), its **3 strategy titles are the canonical title set** — co-designed with the thumbnails for curiosity-gap synergy. Read them, list all 3 under `## Titles`, and treat the one marked `[PRIMARY — recommended]` (or the first if unmarked) as the strongest for the step-4 primary-keyword extraction. **Skip the 5-candidate generation below** in that case. Generate the 5 candidates here ONLY when `07_package.md` is absent (standalone `/publish` run).

Generate exactly **5 long-form title variants** in Polish. Each must function as an **identity reframe, paradox, or system-level architectural reveal** — never as instruction, advice, or a list.

## TITLE ARCHITECTURE — Identity Provocation Blueprint

A qualifying title does ONE of the following:
- **Identity reframe** — names a state the viewer believes about themselves and inverts it ("To nie lenistwo. To alarm, który uruchamia twoja psychika.").
- **Paradox** — pairs two ideas the viewer assumes are opposites and reveals their unity ("Twój mózg widzi zagrożenie tam, gdzie widzisz sukces innych").
- **System-level architectural reveal** — describes the viewer's inner mechanism in everyday language the viewer didn't know applied to them ("Porównujesz swoje życie do cudzego montażu").

The viewer must feel addressed at the level of *identity* or *underlying mechanism* — not at the level of behavior or advice.

## LANGUAGE RULES (non-negotiable)

- **Natural spoken Polish** — as if said aloud by one person to another. No academic, clinical, or mechanistic register.
- **Emotional directness** — the title must hit an emotional truth or felt recognition in the first reading. If it sounds like a research abstract, rewrite it.
- **No abstract nouns as the grammatical subject** — do NOT write titles where the subject is "układ nerwowy", "mechanizm", "system", "instynkt", "reakcja fizjologiczna" or similar clinical/mechanistic nouns. Write from the viewer's perspective or name the mechanism in a felt, human way.
- **No trailing period.** Titles end without punctuation, OR with a question mark if using the question pattern.

## RECOMMENDED PATTERNS

- **Question + answer**: "Czujesz, że jesteś w tyle? Dlatego boli to aż tak mocno"
- **Contradiction**: "To nie lenistwo. To alarm, który uruchamia twoja psychika"
- **Viewer-perspective reframe**: "Dlaczego masz wrażenie, że wszyscy cię wyprzedzili"
- **Perceptual reveal**: "Nie jesteś w tyle. Porównujesz się do cudzego skrótu"

## HARD BANS (any of these auto-disqualifies a title)

- Instructional verbs: "how to", "jak się", "jak możesz", "ways to", "tips for", "stop", "fix".
- List formats: "5 …", "7 rzeczy …", any leading number used as a counter.
- Mechanistic subjects: titles beginning with "Twój układ nerwowy…", "Twój system przetrwania…", "Mechanizm…", "Instynkt…", "Reakcja fizjologiczna…"
- Advisory framing: "powinieneś", "musisz", "co musisz wiedzieć".
- Trailing period at the end of the title.
- Clickbait words: "hack", "sekret", "szokująca prawda", "nie uwierzysz", "zniszcz", "toksyczny", "czerwone flagi", "obudź się", "brutalnie szczery", "większość ludzi nie wie", "to zmieni wszystko".

## BAD vs GOOD EXAMPLES

- ❌ "Nie jesteś w tyle. Twój układ nerwowy analizuje błędne dane." — mechanistic subject, trailing period, abstract
- ❌ "Lęk przed spóźnieniem to poprawna reakcja fizjologiczna." — clinical register, sounds like a textbook
- ❌ "Twój system przetrwania reaguje na algorytm jak na stado." — mechanistic, abstract, not emotionally direct
- ✓ "Czujesz, że jesteś w tyle? Dlatego boli to aż tak mocno"
- ✓ "To nie lenistwo. To alarm, który uruchamia twoja psychika"
- ✓ "Dlaczego masz wrażenie, że wszyscy cię wyprzedzili"

## CONSTRAINTS

- Exactly 5 titles. Each under 70 characters.
- Specific to THIS script's actual content. Do not invent claims the script doesn't make.
- Mix architectural modes — at least 2 of the 3 modes (identity reframe / paradox / system reveal) must be represented across the 5.

**Output:** 5 numbered titles, title text only, no labels or commentary. (These feed the `## Titles` section of the master and the primary-keyword extraction in step 4.)

---

# STEP 2 — Video Description (+ 3 hashtags)

Write the description in exactly **5 sentences**. Natural prose — not fragments, not a list. Total under 80 words.

Sentence structure (follow this order):
1. The viewer's experience — a specific, felt moment or pattern that drives them to search for this video. Start from their daily life, not from an abstract concept.
2. Psychological reframe — gently reassure that this experience doesn't mean something is wrong with them; name the mechanism in plain everyday Polish (no jargon).
3. What the film covers — a brief "W tym filmie..." sentence summarizing the core topic.
4. Additional context — one more thing the video covers or reveals.
5. CTA — a warm, direct invitation to watch: "Jeśli chcesz [benefit], obejrzyj i posłuchaj do końca."

Good example (do not copy verbatim):
> "Czasem wystarczy kilka minut scrollowania, żeby pojawiło się przytłaczające wrażenie, że wszyscy są już dalej niż ty. To uczucie nie musi oznaczać, że coś z tobą jest nie tak — często jest po prostu reakcją układu nerwowego na ciągłe porównywanie się z cudzymi wycinkami życia. W tym filmie pokazuję, skąd bierze się poczucie bycia w tyle i dlaczego potrafi tak mocno uderzać w ciało oraz psychikę. Opowiadam też, jak algorytmy i presja społeczna wzmacniają ten fałszywy alarm. Jeśli chcesz lepiej zrozumieć siebie i poczuć trochę ulgi, obejrzyj i posłuchaj do końca."

Hard rules:
- Exactly 5 sentences. Count them. If you write 4 or 6, rewrite.
- NO researcher names, NO study years, NO Latin-sounding jargon.
- NO fragment-style lines (no "Nocne scrollowanie. Kolejne zaręczyny." openers).
- NO second-person preachy lines.
- NO clickbait words (see step 1 ban list).
- Natural conversational Polish — as if spoken directly to one person.

**3 hashtags** (generated with the description): exactly 3, single-word, lowercase, `#` prefix. First is always `#sensum`. The other 2 are the single-word core topic + one single-word concept from the script (e.g. `#sensum #presja #porównywanie`). NO multi-word hashtags, NO camelCase, NO spaces, NO Polish diacritics in hashtags (use `#lek` not `#lęk`). These 3 hashtags are the ONLY single-word survivors — the long-form Tags field (step 4) is exclusively multi-word.

---

# STEP 3 — Timestamps (chapters)

Detect natural section breaks from the `## ` headings / bold section labels / topic shifts in the script. Produce **6–12 chapters**.

- Each label is a full sentence or question from the viewer's navigation perspective — what will the viewer find in this section? Write "Skąd bierze się poczucie, że jesteś w tyle" or "Jak algorytmy wzmacniają ten alarm" — NOT dry technical single-word labels like "Mechanizm" or academic phrases like "Pułapka fałszywej średniej".
- First chapter is `00:00` and its label names the actual opening topic (NOT the word "Wprowadzenie").
- All other chapters use the placeholder `[XX:XX]` (the user fills real timestamps after the edit is locked).

**Output format** (one per line): `00:00 <label>` then `[XX:XX] <label>` for the rest.

---

# STEP 4 — Long-form Tags

First read `.tmp/08_signals.md` (YouTube autocomplete + niche trend signals).

## Operating principles

- A tag is a search query, not a vocabulary word. If you can't picture a real person living this problem typing it into YouTube search, it has no place in the tag block.
- **Tag #1 carries the most algorithmic weight.** YouTube front-loads semantic weight onto the first tag. Tag #1 must be the **exact-match primary keyword** of the video — a search-shaped phrase extracted from (or paraphrased from) the strongest of the 5 step-1 titles. If that title is metaphor-heavy and would not autocomplete in YouTube search, use a more search-shaped paraphrase. The remaining tags cluster around this primary keyword.
- Prefer multi-word phrases (≥2 words) — they carry more search intent.
- Metaphors and props in the script (cookies, batteries, GPS, doors, villages) are illustrations, not search terms. Tag the underlying mechanism the metaphor points to.
- Established clinical / pop-psychology terms (ruminacja, regulacja, przywiązanie, wypalenie, maskowanie) are what serious viewers actually search for — render them inside multi-word phrases that match real search behavior.
- The Niche Trend Signals block lists single-word terms currently trending in this niche. Borrow the concepts and render them as multi-word phrases (signal "regulacja" → "regulacja emocji psychologia"). Treat niche signals as a **supporting reference** — the primary keyword from the chosen title leads.

## THE TAG PROTOCOL — NON-NEGOTIABLE

- Produce **5–8 tags total**. Comma-separated, no `#` prefix. 2026 YouTube SEO consensus: 5–8 highly relevant tags outperform padded lists. Quality over quantity.
- **SLOT STRUCTURE — order by algorithmic weight (front-loaded):**
  - **Tag #1 (mandatory): the exact-match primary keyword** for this video (from the strongest candidate title, or a more search-shaped paraphrase). Multi-word. This slot does the heaviest discovery work.
  - **Tags #2–#6: long-tail intent phrases.** 2–4 words each. Mix: close paraphrases of the primary keyword, lived-experience phrasing ("dlaczego zawsze zaczynam od nowa"), clinical/mechanism phrases rendered as searches ("rozregulowanie układu nerwowego", "pętla ruminacji"). Niche Trend Signals get rendered here as multi-word phrases.
  - **SENSUM**: include exactly once (uppercase). Brand tag — the only single-word entry permitted.
  - **Optional: up to 2 single-word Polish psychology anchors** (e.g. "psychologia", "emocje") — ONLY if no multi-word phrase captures the same high-volume search better.
- **The intent test.** For each phrase: *"Would a real person living this problem type these exact words into YouTube search?"* If not, cut it.
- Every phrase must be extractable from the script's language OR a direct paraphrase of the search intent the chosen title surfaces.
- Order STRONGEST FIRST — the `--finalize` trimmer drops from the tail if the comma-joined string overruns the 450-char budget (500-char YouTube hard cap minus margin), so never put a weak tag ahead of a strong one.

**Output:** one comma-separated line, no `#` prefix, strongest first.

---

# STEP 5 — Bibliography (Research & References)

Read `md/02_verified_research.md`. It contains N peer-reviewed entries. For EACH entry, explicitly decide **INCLUDE** or **EXCLUDE** based on this single question:

> "Does the script make any claim — direct or indirect, literal or thematic — that this research could plausibly support?"

- If yes (any thematic tie, even loose): **INCLUDE.**
- The ONLY ground for exclusion is **ZERO thematic tie** — the entry's topic shares no concept, mechanism, population, or finding with anything the script discusses. You must be able to state the zero-tie reason in one short sentence.

The script is research-grounded but **research-invisible**: the speaker never names a study, a researcher, or a year. So almost no verified entry will have an explicit script anchor. **This is expected and is NOT a ground for exclusion.** The bibliography credits the science underneath the script's claims, not the words the speaker literally said.

### LOOSE thematic tie (= INCLUDE):
- Research on cancer patients carrying past trauma → script claim "the body holds what the mind tries to move past" (population differs, mechanism matches: include).
- Research on community intervention for adolescent crises → any co-regulation language in the script (setting differs, principle matches: include).
- Research on workplace burnout in healthcare → script claim about chronic nervous-system overload (industry differs, mechanism matches: include).

### ZERO tie (= EXCLUDE):
- Research on agricultural yield, sports performance, software optimization, or any topic sharing no concept with the script.

### Format for each included entry:
`• Concept Label — Optional Qualifier: Author, A., et al. (Year).`

Citation only — ending with the year in parentheses and a period. NO descriptive sentence, NO summary, NO "why it matters."

- **CRITICAL: Do NOT translate Concept Labels into Polish.** Use the exact English concept label from the Verified Research section (or a short English paraphrase if none given). The bibliography is a scientific reference list — concept labels stay in English.
- **Default: include everything with any thematic tie.** Failing to surface a thematically-tied reference is a worse error than including a loosely-tied one. If 4 entries are provided and 3 have any tie, the bibliography has 3 entries — not 1.
- When a concept has multiple landmark sources (original + replication, original + meta-analysis), produce a separate entry per source and distinguish them with the qualifier (e.g. "Ego Depletion — Original Study", "Ego Depletion — Meta-Analysis").

**Output:** the `• …` bibliography lines under a `Badania i źródła:` heading.

---

# STEP 6 — Shorts: Clip Selection

Survey the full narration and select the strongest **up to 4** passages that can become YouTube Shorts. This is the foundation steps 7–9 build on.

## The Triple Retention Filter (HARD AND-GATE)

A passage qualifies ONLY if it passes ALL THREE filters. Failing any one disqualifies it, no matter how strong on the other two. BORDERLINE counts as FAIL.

1. **COGNITIVE AUTONOMY** — the 30-second fragment stands as a complete whole: thesis → proof or example → conclusion. If the viewer needs context from the rest of the video to understand it, the Shorts algorithm rejects it and viewers swipe. Disqualified.
2. **INSTANT HOOK (0:01)** — the first ~1.5 seconds hit a strong emotion or resonate with a specific lived problem. If the opening reads like throat-clearing, framing, a definition, or a generic transition ("A teraz…", "Pomyśl o tym…", "Więc co to znaczy…"), viewers swipe in the first second. Disqualified.
3. **CURIOSITY GAP** — the cut leaves the viewer with an incompleteness only the main video resolves. A Short that fully closes the loop and leaves the viewer satisfied has no path to drive views to the long-form video — and driving those views is the whole point. Disqualified.

## Selection rules

- Work in two internal moves: first map every viable candidate across the script (be thorough — over-identify, then cut), then apply the hard AND-gate and keep the strongest passers.
- Select the strongest **4** candidates that pass all three filters. Every passage that genuinely passes all three is qualified — do NOT withhold qualified Shorts because you can name something stronger. The cap is 4, not "the absolute top 2." A 10-minute psychology script almost always contains 3–4 clean passers.
- Only if FEWER than 4 genuinely pass do you return fewer (3, 2, even 1). Be honest about which dropped and on which filter. Do not promote borderline candidates; do not over-prune a clean three-filter pass.
- You are NOT constrained to any fixed archetype menu — all 4 can be the same "type" if that's what the script supports.
- **No two Shorts may share any lines.**
- Quote the **exact** lines verbatim from the narration — no paraphrasing, no added words. Each clip lands in the 25–70 second range read aloud (~50–150 words).
- For each, choose a free-form **angle tag** (2–4 words) describing its actual pull — e.g. "Mind-blow reveal", "Naming the unnamed", "Open loop", "Practical reframe", "Body-feels-this", "Identity absolution".

For each selected Short, hold internally (used by steps 7–9 and the clip block): a **Hook** quote (the exact opening line(s) the editor cuts in for the first ~3s) and a **Core payload** quote (the exact line(s) carrying the main claim) — both verbatim. If you only have one quote, source the Core payload from the next 1–2 verbatim sentences in the narration that continue the same thought. If you cannot find a verbatim continuation, **drop the whole Short**.

---

# STEP 7 — Shorts: Titles

For each step-6 Short, write exactly **ONE** title (not a candidate list).

- Maximum 60 characters. No trailing period.
- High-impact reframe: identity-reframe, paradox, or system-architectural reveal.
- Natural spoken Polish — emotionally direct, from the viewer's perspective. No mechanistic or academic register.
- Recommended patterns: contradiction ("To nie jest X. To Y."), viewer-direct question ("Dlaczego X uruchamia w tobie Y"), direct psychological statement.
- Right-shape examples: "Dlaczego cudzy sukces uruchamia w tobie panikę" / "To nie jest jedno uczucie. To dwa różne alarmy" / "Porównujesz swoje życie do cudzego montażu".
- Never instructional ("Jak…", "5 sposobów…"). Never ends with a period.

---

# STEP 8 — Shorts: Descriptions

For each step-6 Short, write the description — exactly **2 sentences**:
- First sentence names the viewer's experience.
- Second delivers the psychological reframe or mechanism (no jargon).
- State the claim directly in the speaker's own voice. NO research-framing language (no "badania pokazują", "naukowcy odkryli", "studies show", "research suggests").
- End the description with: `#Shorts #psychologia` plus **1** single-word lowercase topic hashtag matching the Short's theme (e.g. `#presja #stres #lek #smutek #emocje`). Each hashtag is ONE word — no spaces, no Polish diacritics (use `#lek` not `#lęk`).

---

# STEP 9 — Shorts: Tags

For each step-6 Short, write a tight backend-tag block. (Shorts algorithm barely reads backend tags — the real categorization signal is the step-8 description hashtags — so keep these tight.)

- **3–5 multi-word intent phrases** per Short. Each phrase 2–4 words. Comma-separated, no `#` prefix.
- Tag #1 is the strongest search-shaped phrase mapping to THIS Short's core claim — its primary keyword.
- Every phrase extracted from (or a direct-intent paraphrase of) THIS Short's quoted lines.
- **SINGLE-WORD TAGS ARE PROHIBITED** (semantic dilution). The only single-word allowance is the brand handle `SENSUM` (uppercase), included ONCE.
- Tag the underlying concept, never the prop/metaphor (cookie, GPS, village, battery, door).
- Tags tuned to THIS Short's specific angle, not the parent video. 3 strong tags beat 5 padded with filler.

---

# Assembling the master file

After all 9 steps, write `md/08_publish.md` in this exact section order (downstream tooling and the `--finalize` step depend on it):

```
# Publish Package — <topic>
_Generated: <YYYY-MM-DD> · Agent 8 (in-session) · Slug: <slug>_

---

## Titles

1. …  (step 1 — 5 titles)
…

---

## Video Description (paste into YouTube Studio)

<step 2 — 5-sentence description>

Timestamps:
<step 3 — chapters>

Badania i źródła:
<step 5 — bibliography lines>

<step 2 — 3 hashtags on one line>

---
*SENSUM — Science of Kindness*

---

## YouTube Tags (copy all, paste into Tags field)

<step 4 — comma-separated tag line>

---

## YouTube Shorts Package

## Short 1 — <angle tag>
**Title:** <step 7>
**Description:** <step 8> #Shorts #x #y
**Tags:** <step 9 — comma-separated, no # prefix>
**Script Lines to Clip:**
Hook (first ~3s):
> <verbatim Hook quote>

Core payload:
> <verbatim Core-payload quote>

---
[… Shorts 2–4, same block …]
```

**Field order inside each Short is LOCKED:** `**Title:**`, `**Description:**`, `**Tags:**`, `**Script Lines to Clip:**` — exactly one of each, in that order. Inside the clip block, `Hook (first ~3s):` then `Core payload:`, each followed by its `> ` quoted line(s). Leave the `Hook (first ~3s):` / `Core payload:` labels with no quarter marker — `--finalize` appends the `[Q1]–[Q4]` markers deterministically.

Then run `agent8_publish.py "<slug>" --finalize` to add the Q1–Q4 markers, trim the tag line to budget, validate every Short has a clip block, and export the docx.

---

## Self-check before saving the master file

- [ ] Exactly **5** long-form titles; none instructional, none with a mechanistic subject, none ending in a period.
- [ ] Description is **exactly 5 sentences**, under 80 words, no fragments, no jargon, no research-framing.
- [ ] Exactly **3 hashtags**, all single-word, `#sensum` first, no diacritics.
- [ ] **6–12** chapters; first is `00:00` with a real topic label (not "Wprowadzenie"); all others `[XX:XX]`; labels are viewer-perspective sentences/questions, not dry nouns.
- [ ] **Tag #1** is the exact-match primary keyword (search-shaped, would autocomplete); 5–8 tags total; every tag multi-word except `SENSUM` (once) and ≤2 optional single-word anchors; strongest first.
- [ ] Bibliography entries come **only** from `02_verified_research.md`; any thematic tie included; concept labels left in English; citation-only format.
- [ ] **1–4 Shorts**, no shared lines; every Hook and Core-payload quote is **verbatim** from the narration (will be checked by the Q1–Q4 substring match).
- [ ] Each Short: exactly one Title (≤60 chars, no trailing period), one Description (exactly 2 sentences + `#Shorts #x #y`), one Tags line (3–5 multi-word, `SENSUM` at most once), one clip block.
- [ ] Master file section order matches the template above.

---

## How to Review (after `/publish` completes)

### Titles
Pick one. All 5 should be emotionally direct, natural spoken Polish. If a title sounds like a research abstract or has a mechanistic subject ("Twój układ nerwowy…", "Mechanizm…"), regenerate that step. Max 70 chars.

### Video Description
Exactly 5 sentences: (1) viewer's experience, (2) reframe, (3) "W tym filmie…", (4) extra context, (5) CTA. Natural conversational Polish, under 80 words. If it reads like an abstract or runs long, regenerate step 2.

### Timestamps
Each label a full sentence/question from the viewer's perspective. Fill in `[XX:XX]` after the edit is locked.

### Research & References
Verify entries match `02_verified_research.md`. Any thematic tie qualifies; only true zero-tie entries are excluded.

### Tags (long-form)
Paste the comma-separated string into Tags (no `#`). **Tag #1 = exact-match primary keyword** — test by pasting into YouTube search; if it would not autocomplete, regenerate step 4. 5–8 tags, every one multi-word except `SENSUM` (once). `--finalize` reports the final char count (target < 450; YouTube cap 500).

### YouTube Shorts
1–4 Shorts, each with one title, a 2-sentence description, 3–5 multi-word backend tags, and the Hook/Core-payload clip split. Titles max 60 chars, no trailing period. The `[Q1]–[Q4]` marker tells you which quarter of the script the quoted line lives in — open the script, count to that quarter, text-search the phrase to find the cut in DaVinci. `[Q?]` means the quote did not substring-match (paraphrase slipped in) — fix the quote or regenerate the Short.

---

## Common Issues

| Symptom | Fix |
|---------|-----|
| `02_verified_research.md not found` | Run Agent 2 first |
| Script source missing | Run `/draft` then `/hook` (exports `docx/script.docx`); or edit to `docx/script_corrected.docx` |
| `--signals` returns 0 suggestions | Network issue — tags step falls back on script + niche signals; suggestions block shows `(unavailable)` |
| Tag block exceeds budget | `--finalize` trims from the tail and prints the final length; reorder so weak tags are last |
| `[Q?]` on a clip block | The quote did not substring-match the narration — the model paraphrased; edit the quote to match the script verbatim or regenerate that Short |
| `[MISSING]` on a clip block | A Short was written without its `**Script Lines to Clip:**` block — locate the lines manually or regenerate step 6 |
