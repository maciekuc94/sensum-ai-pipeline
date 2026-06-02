# Workflow: Agent 4 — Hook Refiner (two-tier, in-session)

## Purpose

Agent 4 is the **final quality gate before recording** — and it does not just score, it **refines**. It evaluates the opening of `04_final.md` against a two-tier rubric and rewrites the first 37 words (the 15-second window) until both tiers pass. This is the moment where YouTube's algorithm and the viewer's brain both decide whether to keep watching.

Since 2026-05-29 Agent 4 runs **inside the Claude Code session** — the model (Opus 4.8) is the one already loaded, no Gemini/Anthropic API call. It is driven by the `/hook <slug>` slash command (see `.claude/commands/hook.md`). The deterministic part — sentence-aware splicing of the new opening, one-time backup, and log writing — stays in `agent4_hook.py --apply`, which makes **no LLM call**.

The script chain is: `3a → 3b ↔ 3c → 4 → record`.

The full theory lives in [docs/specs/2026-05-15-15-second-hook-research.md](../../docs/specs/2026-05-15-15-second-hook-research.md). This workflow is the enforcement layer.

---

## Inputs

1. `outputs/videos_pl/<slug>/md/04_final.md` — the finalized script (required; produced by the `/draft` loop).

## How it runs (in-session + deterministic apply)

1. `/hook <slug>` — Claude reads `04_final.md`, scores the opening in-session per the rubric below, and (refining internally until both tiers would pass) produces the structured response block ending with `REWRITE_15S` + `VERDICT`.
2. Claude writes that exact block to `outputs/videos_pl/<slug>/md/04_hook_response.txt`.
3. Claude shells to `python tools/pipeline/agent4_hook.py "<slug>" --apply`, which:
   - creates `04_final.bak.md` once (never overwritten),
   - if the script does not yet pass, splices `REWRITE_15S` into `04_final.md` replacing only the first ~37 words (rest byte-identical),
   - writes the `04_hook.md` log and prints the verdict,
   - removes the temp response file.

**Thresholds:** Tier 1 (15s) **≥ 8/10**, Tier 2 (30s) **≥ 7/10**. Verdict `RECORD` requires both.

---

## Prompt — the exact scoring + rewrite instructions (in-session)

Treat the script's opening as the material to score. The model MUST emit the structured block at the end exactly as specified (the `--apply` parser reads those field names — keep them in English).

---

Jesteś hook refinerem dla polskiego kanału psychologicznego YouTube SENSUM. Oceniasz otwarcie wypolerowanego skryptu używając dwustopniowej rubryki i produkujesz przepisane otwarcie kiedy potrzeba.

**Skrypt jest po polsku. Twoja analiza i przepisanie również po polsku. NAZWY PÓL OUTPUTU (TIER1_SCORE, REWRITE_15S, VERDICT, itp.) pozostają po angielsku — parser kodu na nich polega.**

Robocza teoria kanału dotycząca okna 15 sekund jest w docs/specs/2026-05-15-15-second-hook-research.md. Aplikuj ją.

## Tier 1 - 15-Second Window (PRIMARY)

Pierwsze ~37 słów narracji. Tu algorytm YouTube i mózg widza oba decydują czy oglądać dalej. Punktuj 1-10 w skali:

  - First-Sentence Grip (0-3): czy zdanie 1 samo w sobie zapracowuje na zdanie 2?
    Konkretny podmiot, <=14 słów, bez abstrakcyjnego stackowania.
  - Specificity Within 15s (0-3): konkretny szczegół / obraz / liczba (zaokrąglona) /
    stan ciała / scena pojawia się do słowa 37.
  - Identification Moment (0-2): widz myśli "to ja" do słowa 37.
  - Loop Opened (0-2): nierozwiązane pytanie lub sprzeczność jest trzymana
    w głowie widza, której musi dokończyć oglądania żeby zamknąć.

Aplikuj -1 punkt karny za KAŻDY red flag wyzwolony (wymień je):
  - Otwiera retorycznym pytaniem ("Czy kiedykolwiek...?")
  - Prowadzi statystyką przed jakimkolwiek emocjonalnym setupem
  - Pierwsze zdanie dłuższe niż 14 słów
  - Brak konkretnego szczegółu do słowa 25
  - Używa "wielu ludzi" / "wszyscy" / "większość z nas"
  - Stackowane abstrakcyjne rzeczowniki w zdaniu 1
  - Jakakolwiek klauzula którą można skasować bez utraty znaczenia
  - Prosi widza o "zasubskrybuj", "polub", "zostań z nami"
  - Meta-framing ("dzisiaj porozmawiamy o", "w tym filmie omówimy")
  - Research-framing w pierwszych 37 słowach: jakikolwiek z "naukowcy odkryli",
    "badania pokazują", "wyniki badań", "z badań wynika", "neuronauka wykazała",
    "jedno badanie", "ostatnie badanie", "meta-analiza", "dane pokazują",
    "psychologowie nazywają to", "nauka jest jasna". Widz ufa mówcy,
    nie cytatowi. Research jest niewidoczny.
  - Notacja statystyczna lub precyzyjne findings w pierwszych 37 słowach:
    dziesiętne (0,62), effect sizes (d = X, r = X), p-values, liczby badań
    ("94 eksperymenty"), liczby uczestników ("8000 osób"), terminy metodologiczne
    (pre-registered, double-blind, longitudinalne, meta-analiza), lub jakikolwiek
    inny artefakt research-paperowy.
  - Wyjaśnia mechanizm przed wylądowaniem uczucia — widz powinien rozpoznać
    siebie zanim jakiekolwiek wyjaśnienie się zacznie.
  - Polskie cringe self-help frazy ("po prostu BĄDŹ", "zaufaj procesowi",
    "wszechświat ci podpowiada", "wibruj wyżej") w pierwszych 37 słowach
  - Polskie academic-textbookowe frazy ("warto zauważyć", "należy podkreślić",
    "kluczowe jest") w pierwszych 37 słowach

Próg zaliczenia: 8/10.

## Tier 2 - 30-Second Hook (SECONDARY)

Pierwsze ~150-200 słów. Co dzieje się PO otwarciu bramki 15s. Punktuj 1-10:

  - Tension (0-3): nierozwiązane pytanie lub sprzeczność się utrzymuje.
  - Personal Relevance (0-3): widz nadal czuje że to jest o nim.
  - Specificity (0-2): konkretne szczegóły kontynuują, bez abstrakcyjnego dryfu.
  - Forward Momentum (0-2): ostatnia linia hooka sprawia że zatrzymanie się
    wydaje niemożliwe.

Próg zaliczenia: 7/10.

## Instrukcja przepisania

MUSISZ wyprodukować przepisane pierwsze 37 słów dla Tier 1, za każdym razem, nawet kiedy wynik już zalicza. Jeśli istniejące otwarcie jest świetne, zwróć je verbatim. Jeśli jest słabe, przepisz używając jednego z sześciu wzorców z research doc (Anomalous Case / Inverted Truth / Direct Question / Visceral Image / Self-Audit / Stakes Reveal). Przepisanie musi:

  - Być dokładnie <=37 słów (uwaga: polski jest "gęstszy" niż angielski, ale
    37 słów polskich nadal mieści się w ~15 sekundach przy ~130 wpm polskim).
  - Czytać się na głos w <=15 sekund.
  - Pasować do voice kanału: ciepły terapeuta rozmawiający z jedną osobą.
    Najpierw waliduj uczucie, potem zasugeruj mechanizm. Nie listicle
    energy, nie lecture energy.
  - Research jest niewidoczny: BEZ "naukowcy odkryli", BEZ "badania pokazują",
    BEZ "wyniki badań", BEZ "z badań wynika", BEZ "neuronauka wykazała",
    BEZ "jedno badanie", BEZ "meta-analiza", BEZ "psychologowie nazywają to",
    BEZ notacji statystycznej, BEZ dziesiętnych, BEZ liczb badań, BEZ terminów
    metodologicznych. Mówca po prostu wie. Prawdziwe cytaty żyją w opisie YouTube.
  - Najpierw prosty język — nigdy nie nazywaj terminu naukowego i potem go
    nie tłumacz. Jeśli termin w ogóle się pojawia, to raz, późno.
  - Bez zbanowanych fraz (bez "Czy kiedykolwiek", bez "wielu ludzi", bez
    "zostań z nami").
  - Bez polskich cringe self-help fraz ("po prostu BĄDŹ", "zaufaj procesowi").
  - Zachowaj tę samą architekturę i temat co oryginał.

## Output Format - MANDATORY

Zwróć DOKŁADNIE ten szablon, bez preambuły i bez końcowej prozy. **Nazwy pól (TIER1_SCORE, REWRITE_15S, VERDICT, itp.) pozostają po angielsku — parser ich szuka:**

TIER1_SCORE: <int 1-10>
TIER1_BREAKDOWN:
- First-Sentence Grip: <n>/3 - <jedno zdanie po polsku>
- Specificity Within 15s: <n>/3 - <jedno zdanie po polsku>
- Identification Moment: <n>/2 - <jedno zdanie po polsku>
- Loop Opened: <n>/2 - <jedno zdanie po polsku>
TIER1_RED_FLAGS: <lista po przecinkach lub "none">

TIER2_SCORE: <int 1-10>
TIER2_BREAKDOWN:
- Tension: <n>/3 - <jedno zdanie po polsku>
- Personal Relevance: <n>/3 - <jedno zdanie po polsku>
- Specificity: <n>/2 - <jedno zdanie po polsku>
- Forward Momentum: <n>/2 - <jedno zdanie po polsku>

BIGGEST_WEAKNESS: <jedno zdanie po polsku nazywające pojedynczy największy problem w oknie 15s>

REWRITE_15S:
<<<
<przepisane pierwsze 37 słów po polsku, <=37 słów, bez cudzysłowów, bez markdown>
>>>

VERDICT: <"record" | "polish" | "rewrite">

---

## In-session refine discipline

Because you (Opus 4.8, in-session) both score and rewrite, do the refinement honestly:

1. Score the *current* opening first.
2. If Tier 1 < 8 or Tier 2 < 7, rewrite the first 37 words, then **re-score the rewritten opening** — repeat up to 3 internal passes until both tiers would pass or you have exhausted realistic improvement.
3. Report the **final** scores (reflecting the opening that `REWRITE_15S` contains) and set `VERDICT`:
   - `record` — both tiers pass with the reported opening.
   - `rewrite` — you could not get both tiers to threshold after 3 passes (the human must hand-rewrite).
   - `polish` — borderline; one more human pass advised.
4. If the current opening already passes, return it **verbatim** in `REWRITE_15S` and set `VERDICT: record`.

Write the full structured block (TIER1_SCORE … VERDICT) to `md/04_hook_response.txt`, then run the apply step.

---

## Files produced

| File | Behavior |
|---|---|
| `outputs/videos_pl/<slug>/md/04_final.md` | **Modified in place** — opening replaced only if a rewrite was applied. |
| `outputs/videos_pl/<slug>/md/04_final.bak.md` | **Created once** on the first refine; never overwritten. |
| `outputs/videos_pl/<slug>/md/04_hook.md` | **Overwritten each run** — score breakdowns + final verdict. |
| `outputs/videos_pl/<slug>/md/04_hook_response.txt` | Temp hand-off from `/hook` to `--apply`; deleted by the apply step. |

The splice is sentence-aware: it replaces the first complete sentences spanning ~37 words and leaves everything after byte-identical.

---

## How to act on the verdict

| Verdict | Meaning | Action |
|---|---|---|
| `record` | Both tiers passed (15s ≥ 8 AND 30s ≥ 7). | `docx/script.docx` is ready — edit if needed, save as `script_corrected.docx`, then proceed to Agent 5 (`/visuals`) and Agent 8. |
| `polish` | Borderline; did not clearly pass. | Re-run `/hook`, or accept. |
| `rewrite` | Could not reach threshold. | Hand-rewrite the opening using the research-doc patterns, then re-run `/hook`. |

### To revert
```bash
cp outputs/videos_pl/<slug>/md/04_final.bak.md outputs/videos_pl/<slug>/md/04_final.md
```

---

## Reference

- Working theory and pattern library: [docs/specs/2026-05-15-15-second-hook-research.md](../../docs/specs/2026-05-15-15-second-hook-research.md)
- Architecture choices for the hook shape: [workflows/guides/narrative_architectures.md](../guides/narrative_architectures.md)

---

## Next step

Once `/hook` returns `record`, `docx/script.docx` has been exported automatically. Edit it in Word/Copilot 365 if needed, save as `script_corrected.docx`, then:

```bash
# in Claude Code:
/visuals <slug>
# parallel:
PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "<slug>"
```
