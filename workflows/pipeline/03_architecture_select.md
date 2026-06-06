# Workflow: Architecture Selection (pre-3a, Claude Code, in-session)

## Purpose

Before the Drafter (3a) writes anything, pick the **best-fit narrative architecture** for this
topic. This step exists to stop the channel defaulting to `Composite Portrait` on every script —
the failure mode that made slugs 2/3/4 read alike (same one-figure „ty" shape, same
Surface→Cost→Origin→Reframe, same recognition close). It runs **inside the Claude Code session**
(Opus 4.8) — no Anthropic API, no Gemini.

Trigger: `/draft <slug>` runs this step after input validation and before
3a. **Skipped entirely when the user passed an explicit architecture as `$2`** (the override wins).

## Inputs to load (before deciding)

1. `outputs/videos_pl/<slug>/md/02_verified_research.md` — the topic (first `# ` heading) + the
   Verified Claims. Required; if missing, instruct the user to run Agent 2 first and stop. This is
   what you match an architecture against.
2. `outputs/videos_pl/<slug>/md/00_materials_insights.md` — book insights (optional; skip silently
   if missing).
3. `workflows/guides/narrative_architectures.md` — read the five **„Kiedy używać"** blocks. Those
   are the selection criteria; do not invent your own.

## Anti-repeat memory (read the recent slugs)

Scan `outputs/videos_pl/*/md/03a_draft.md`. Each one declares its architecture on the first body
line as `ARCHITECTURE: <name>`. Read that line from every slug **except the current one**, sort the
slugs by their leading numeric prefix (`1_…`, `2_…`, …), and take the **latest 1–2** as the
"recently used" set. (This is reliable — every existing 03a carries the line; `04_final.md`
sometimes does not, so always read 03a.) If no prior slugs exist, the recently-used set is empty.

## The five architectures and their fit signals

Match the topic's shape to the architecture whose „Kiedy używać" it actually fits:

- **Historical Reversal** — the topic rests on a belief once treated as settled truth that has since
  been overturned. The hook is the reversal.
- **Socratic Challenge** — there is a real question at the core that the viewer has asked themselves
  and never got a satisfying answer to.
- **Systems Audit** — the topic is a repeating loop / feedback mechanism / behavior best understood
  as a system with inputs, outputs, and a failure mode.
- **Forensic Case Study** — there is a strange, extreme, or counterintuitive symptom or case that
  reads as *impossible* until the mechanism is explained.
- **Composite Portrait** — the topic embodies cleanly in one recognizable figure whose behavior the
  viewer knows from themselves (followed through four movements in full „ty").

## Selection logic

1. Score all five against the topic on genuine fit (which signals above actually match the Verified
   Claims and the topic). Be honest — most topics fit two or three architectures to some degree.
2. Pick the **best fit on merit**. **`Composite Portrait` is eligible but is NOT the automatic
   default — it must win on merit like any other.** It is the channel's signature shape, so it will
   often be a strong fit; that is fine when it genuinely is.
3. **Anti-repeat tiebreak (only when the top two are close):** if your top two are within a close
   margin of fit, break the tie *against* whatever architecture(s) the recently-used set contains.
   Do **not** force a clearly worse-fitting shape just to avoid repetition — anti-repeat is a
   tiebreaker, not an override. If Composite Portrait is the clear best fit despite a recent streak,
   choose it and say so explicitly in the rationale.
4. **Tone-fit (north-star, 2026-06-04):** tender, self-worth topics — wstyd, samokrytyka, poczucie
   bycia „nie dość", lęk o własną wartość — want a **warm monologue**, not a cold mechanism audit
   (the channel's golden rule, `voice_corpus.md` §0). For such topics, weight **against**
   `Systems Audit` (the coldest shape) unless it is the clear best fit; warm shapes (Composite
   Portrait, Forensic Case Study) usually carry tenderness better. This is a fit consideration, not
   an override — and even when `Systems Audit` wins, its cold register must describe the *mechanism,
   never the person* (3a + 3c cat. K enforce this). Origin: slug-3 (wstyd) was sent to Systems Audit
   and read as a diagnostic of the *person*.

## Output

Write `outputs/videos_pl/<slug>/md/03_architecture.md`:

```
ARCHITECTURE: <one of: Composite Portrait | Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit>

Wybór: <2–3 sentence rationale — which fit signals in this topic drove the choice>
Runner-up: <second-best architecture> — <one line on why it lost>
Ostatnie slugi: <recently-used architectures, e.g. "4_… Composite Portrait; 3_… Composite Portrait"> (anti-repeat <broke tie against / not triggered — best fit was clear>)
```

The **first line must be exactly `ARCHITECTURE: <name>`** so the command can parse it the same way
it parses 03a. Then hand that chosen name to 3a as the forced architecture.

## Override path (user passed `$2`)

If the command reached this step only to record a forced choice (user passed a valid `$2`), do **not**
run the selection logic. Write instead:

```
ARCHITECTURE: <forced name>

Wybór: forced by user (override) — selection step skipped.
```

## Self-check before saving

- [ ] First line is exactly `ARCHITECTURE: ` + one of the five exact names
- [ ] Rationale names the specific fit signals in *this* topic (not generic boilerplate)
- [ ] Recently-used set was actually read from prior `03a_draft.md` files (or noted empty)
- [ ] If a recent streak exists and you still chose the streak architecture, the rationale says why
      it is the clear best fit despite the streak
