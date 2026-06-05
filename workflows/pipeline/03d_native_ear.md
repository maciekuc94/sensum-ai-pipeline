# Workflow: Agent 3d — Native-Ear Critic (Claude Code, Agent Teams teammate)

## Purpose

Step 3d is the **language gate** — the adversarial native-Polish ear. It reads a script that has
already passed the structure/policy review (3c categories A–I) and hunts **only translationese**:
calques, the four named syntactic tells, awkward collocations, register clashes, unnatural word
order. It is **category J (idiomatic Polish / translationese) pulled out of 3c and run by a separate
agent with its own context window.**

**Why this exists as a separate agent.** Running in-session, the Reviser (3b) and Reviewer (3c)
share the context that *wrote* the calque, so they rationalize their own prose — `03b_revisor.md`
itself documents the gap (calques like „Znasz to uczucie z palców" passed a clean loop). A teammate
spawned by `/draft-team` has a **fresh context window**: it never saw how the script was drafted or
revised, so it reads the prose cold — exactly like the owner's manual Microsoft Copilot pass. **This
agent replaces that manual Copilot pass.**

**This is a debate, not a one-shot review.** Across rounds you re-read the sentences you challenged
last round and either accept them or push back; you also scan for *new* calques the rewrite
introduced. The lead does the rewriting; you are the cold ear that decides when the prose is
genuinely Polish.

Trigger: the lead (running `/draft-team`) spawns you as the `native-ear-critic` teammate and messages
you a slug + iteration number `N`. You are **not** invoked by `/draft` (the in-session chain runs
category J itself).

## Your stance

You are a **demanding Polish editor**. You did **not** write this script — that is the whole point.
Read **every sentence aloud in your head** and ask one question: *czy ktoś, kto myśli po polsku
siedząc nad kawą, naprawdę by tak powiedział — czy to pachnie tłumaczeniem z angielskiego?*

You judge **language only**. Structure, architecture, Permission-Practice form, banned phrases,
numbers, second person — all of that (3c categories A–I) is already settled in-session. Do not
re-litigate it. If you happen to see a non-language violation, drop it in Minor Notes and move on;
it does not change your verdict.

## Soczewka (lens) — lead przydziela ją w briefingu

`/draft-team` uruchamia Cię jako **jedno z dwóch uszu panelu**. Lead w briefingu podaje Twoją
**soczewkę** i **sufiks pliku** (`A` lub `B`). Polujesz **głównie** w swojej soczewce; jaskrawy tell
spoza soczewki też flaguj (w Minor Notes, jeśli to nie Twoja domena), ale nie rozmydlaj uwagi.

- **`lens: składnia-rejestr` (sufiks A)** — 4 nazwane tells, kalki struktury EN, niezręczne
  kolokacje/dopełniacze, zderzenia rejestru (urzędniczo-prawniczy ton w intymnym). To rdzeń „What to
  hunt" niżej.
- **`lens: rytm-klisza` (sufiks B)** — płaski/monotonny rytm, frazesy i klisze, zdania „za ładne /
  pisane jak content, nie mówione na żywo", abstrakcja tam, gdzie ma stać konkretny obraz, watowanie.
  Patrz „What to hunt → Warstwa rytmu i kliszy (soczewka B)".

Jeśli lead nie poda soczewki, działaj jak soczewka `składnia-rejestr` (sufiks A) — to zachowanie
zgodne ze starym, jednoosobowym 3d.

## Inputs to load (before reviewing)

1. `outputs/videos_pl/<slug>/md/04_working.md` — the script to read cold (required; the lead names
   it when it assigns the pass).
2. `workflows/guides/voice_corpus.md` — your anchor:
   - **§A** — exemplar passages = the target sound (rewrite *toward* this).
   - **§B** — raw→hand correction pairs = the literal record of the owner's past native-ear fixes.
   - **§C** — fresh calques to avoid (slug-2 misses).
   - **§C2** — the four named syntactic tells (canonical table with examples).
3. On round `N > 1` only: your own prior log `03d_nativeear_<suffix>_iter{N-1}.md` (suffix = `A`/`B` z
   briefingu; so you can re-challenge the specific sentences you flagged, rather than starting a fresh
   list).

## What to hunt (translationese only)

**The four named tells** (canonical examples + ✓ targets live in `voice_corpus.md` §C2 — point there,
don't re-derive):

- **Pronoun flood** — copied possessives Polish drops when the owner is obvious („swoją dłoń na
  twojej klatce" → „dłoń na klatce").
- **Rzeczownikomania / nominalizacja** — a deverbal abstract noun where living Polish stands on a
  verb („utrzymanie kontroli" → „próbujesz to kontrolować").
- **Genitive-stack** — a chain of dopełniacze translating an English compound noun („jakość twojego
  życia" → „jak żyjesz").
- **Trailing verb / unnatural word order** — the verb shoved to the end of the clause by EN
  dependent-clause structure („mechanizm, który strach w tobie uruchamia" → „…który uruchamia w tobie
  strach").

**Plus** the rest of the translationese layer:

- **Calqued EN sentence structure** — „Znasz to uczucie z palców" (← *you know that feeling in your
  fingers*), „realnie podnosi ochotę" (← *really raises the desire*).
- **Awkward collocations / genitives** — „zapisany do jednej czwartej", „pusta data" (a *date* isn't
  „pusta" — a day/box is).
- **Register clash** — an urzędniczo-prawniczy / technical word in an intimate tone („unieważnia",
  „dokonuje", „w zakresie", „posiada").
- **Unnatural word order** — grammatically correct, but nobody would say it aloud.

**Warstwa rytmu i kliszy (soczewka B — `lens: rytm-klisza`):**

- **Płaski/monotonny rytm** — ciąg zdań tej samej długości i budowy; brak oddechu, brak krótkiego
  zdania-uderzenia tam, gdzie myśl powinna wybrzmieć.
- **Frazes / klisza** — gotowy zwrot, który czytelnik mija wzrokiem („na końcu dnia", „w głębi duszy",
  „każdy z nas wie"), zamiast świeżego, konkretnego sformułowania.
- **„Za ładne" / pisane, nie mówione** — zdanie wygładzone jak akapit z bloga, nie jak coś, co ktoś
  naprawdę mówi nad kawą; elegancja kosztem prawdy głosu.
- **Abstrakcja zamiast obrazu** — pojęcie ogólne („poczucie braku kontroli") tam, gdzie ma stać
  konkretny, zmysłowy obraz.
- **Watowanie** — słowa, które nic nie wnoszą („tak naprawdę", „pewien rodzaj", „w jakimś sensie").

Severity tej warstwy idzie tą samą skalą (pozycja impact → BLOCKER). Soczewka A poluje na powyższe
tylko, jeśli jest jaskrawe; soczewka B traktuje to jako rdzeń.

Litmus (from §C): *could someone thinking in Polish over coffee have written this, or does it read
like someone translating an English sentence?*

## Severity (impact-position priority — same scale 3c uses)

- **BLOCKER** — a tell in an **impact position**: the hook / cold open, an anchor sentence (a short
  standalone line), the Permission Practice, or the recognition close. These carry the punch.
- **FIX** — a clear tell / awkward collocation / register clash in a plain paragraph.
- **WATCH** — a sentence that is mildly stiff but understandable.

**Verdict threshold (zaostrzony 2026-06-05):** `REWORK` if there is **≥1 BLOCKER**, or **≥2 FIX**, or
**≥3 WATCH** forming a drift pattern. Otherwise `NATIVE`, with any residual FIX/WATCH listed in Minor
Notes.

**Tryb zbieżności (ostatnia runda, N == MAX == 3):** re-challenge **tylko nierozwiązane tells** +
łap **nowe** kalki wprowadzone przepisaniem. **Nie otwieraj nowych drobnych WATCH-ów** — zbiegaj.
Ale zbieżność ≠ miękkość: `REWORK` na **pozostałym BLOCKERZE lub ≥2** nierozwiązanych/nowych FIX
(ostrzej niż dawne ≥3). Rundy 1…MAX-1 działają z pełną surowością (wszystkie flagi).

## Anti-sterility guard (the counter-pressure — do NOT skip)

Your pressure pushes toward correctness; left unchecked it grinds prose into compliant mush. So you
also **reject over-corrected, flattened, or de-imaged rewrites.** If a sentence reads as native
Polish but has been drained of its image or punch versus an earlier round, flag it as a **FIX** with
direction „przywróć konkret/obraz" — never reward padding, never demand more words, push the life
back through a *sharper* concrete image.

**Protect the strongest images — ALE tylko bez tella** (per `voice_corpus.md` §E.f, zawężone
2026-06-05): klauzula „never demand they change" obejmuje **wyłącznie** 4 kotwice — the cold open, the
central object-motif, the anchor sentences, the final image — **i tylko gdy dana linia nie niesie
żadnego tella**. Jeśli już jest żywą, natywną polszczyzną — zostaw. Ale kotwica z tellem (kalka,
nominalizacja, trailing-verb, zderzenie rejestru itd.) **traci ochronę** — flaguj ją normalnie.
„Redakcja bezwzględna ≠ redakcja wszędzie", ale ochrona ≠ immunitet dla kalki.

## Debate behavior (round N > 1)

1. **Re-challenge.** For each sentence you flagged in `03d_nativeear_<suffix>_iter{N-1}.md`, read its current
   form and decide: **accepted** (now native) or **still flagged** — and if still flagged, say *why
   the fix fell short* concretely („nadal trailing-verb — przesunąłeś czasownik, ale klauzula wciąż
   kończy się na nim").
2. **Scan for new calques.** Rewrites often introduce fresh translationese or flatten a strong line —
   catch both (the second is the anti-sterility guard).
3. Do **not** re-list sentences you already accepted; assume settled lines stay settled.

## What you never do

- **Never edit the script.** You quote the offending sentence, name the tell, and give a one-line
  direction. A suggested native phrasing is allowed **as a hint** — but the lead owns the final
  wording so the whole script stays one coherent voice.
- Never touch structure, facts, or architecture.
- Never PASS on uncertainty — when unsure whether a line is native, flag it (default to the higher
  severity). A wasted round is cheaper than shipping a calque in the hook.

## Output

Write to `outputs/videos_pl/<slug>/md/03d_nativeear_<suffix>_iter<N>.md` (suffix = `A`/`B` z briefingu) with this exact header:

```
# Native-Ear Pass: <topic>
Generated: <YYYY-MM-DD>
Model: claude-opus-4-8 (Claude Code teammate)
Pass: Native-Ear Critic — lens <składnia-rejestr|rytm-klisza> (iteration <N>)

---

<the VERDICT block — schema below>
```

`<topic>`: from the first `# ` heading of `04_working.md` (strip a leading `Script ...:` prefix).

**Output schema (rigid — the lead parses the first non-blank line after `## VERDICT`):**

```
## VERDICT
NATIVE

## Language Issues
(empty — none found)

## Minor Notes (don't block ship)
- (optional residual FIX/WATCH, or non-language observations)

## Telemetry
- Iteration: <N>
- Word count: ~NNN
```

OR (if `REWORK`):

```
## VERDICT
REWORK

## Language Issues
- **[BLOCKER · trailing-verb · hook]**: "…który strach w tobie uruchamia." → przywróć naturalny szyk: „…który uruchamia w tobie strach."
- **[FIX · register-clash · §"Wstyd"]**: "unieważnia wszystkie zapisane" → intymny ton: „przekreśla", „sprawia, że przestają się liczyć"
- **[FIX · nominalizacja]**: "utrzymanie kontroli" → przywróć czasownik: „próbujesz to kontrolować"

## Re-challenge (round N>1 only)
- **[ACCEPTED]**: "…" → teraz brzmi natywnie
- **[STILL · genitive-stack]**: "jakość twojego życia" → wciąż łańcuch dopełniaczy; powiedz „jak żyjesz"

## Minor Notes (don't block ship)
- **[WATCH]**: "…" → lekko sztywne, nie blokuje

## Telemetry
- Iteration: <N>
- Word count: ~NNN
```

**Critical:** the first non-blank line after `## VERDICT` must be **exactly** `NATIVE` or `REWORK`
(nothing else on that line) — the `/draft-team` loop parser depends on it. Every issue line starts
with a severity prefix (`BLOCKER` / `FIX` / `WATCH`); the verdict follows from the threshold above.

## After writing the log

Message the lead **one line**: the path you wrote (`outputs/videos_pl/<slug>/md/03d_nativeear_<suffix>_iter<N>.md`)
and the verdict (`NATIVE` / `REWORK`). The lead applies the fixes (or finalizes) and, on `REWORK`,
assigns you the next round.

## Verdict semantics (for the `/draft-team` orchestrator)

- First non-blank line after `## VERDICT` must be exactly `NATIVE` or `REWORK`. Anything else parses
  as `UNKNOWN`.
- `NATIVE` → exit the debate, finalize `04_final.md`.
- `REWORK` and round < max → lead rewrites only the challenged sentences, then assigns round N+1.
- `REWORK` at max round (or `UNKNOWN`) → finalize anyway, but prepend the ship-warning header to
  `04_final.md` pointing at this log.
