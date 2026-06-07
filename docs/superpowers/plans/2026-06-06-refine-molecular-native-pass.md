# `/refine` — molekularna warstwa native-polszczyzny — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Zbudować komendę `/refine <slug>`, która zdanie-po-zdaniu wyłapuje eseistyczną abstrakcję i jawne kalki w drafcie, proponuje mówione przepisania z dowodem, a człowiek zatwierdza każdą zmianę — z re-flow jedną ręką i pętlą do wyschnięcia.

**Architecture:** Cienki deterministyczny rdzeń w Pythonie (segmentacja zdań + wykrywanie chronionych szczytów, testowany przez `--selftest`) karmi orkiestrację `Workflow` (panel L1 back-translation + L2 forward-divergence per zdanie, fan-out na zimnych kontekstach). Komenda `.claude/commands/refine.md` spina to w pętlę: segment → panel → przegląd przez człowieka → re-flow jedną ręką (in-session Integrator) → powtórz na zmienionych, aż sucho. Maszyna proponuje + dowodzi; **człowiek decyduje, nigdy auto-replace.**

**Tech Stack:** Python 3 (stdlib only: `re`, `json`, `argparse`) · `Workflow` tool (JS, agenci LLM) · Markdown (komenda + raport kandydatów) · brak nowych zależności (pytest świadomie pominięty — projekt nie ma infry testowej, używamy `--selftest`).

**Geneza / kontekst dla wykonawcy:** Spec: `docs/superpowers/specs/2026-06-06-refine-molecular-native-pass-design.md` (czytaj §3 kryterium flagowania i §5 bezpieczniki — to one rządzą). POC, który zwalidował mechanizm i kalibrację: workflow `wrabcyj69` (wynik w transkrypcie sesji). Kluczowa kalibracja właściciela: **KONSERWATYWNA** — flaguj tylko abstrakcję-argument (typ „wyrok na całego człowieka") + jawną kalkę (PL sam koślawy); chroń crafted-concrete (typ „muzeum lenistwa") i twarde szczyty.

---

## File Structure

| Plik | Odpowiedzialność | Status |
|---|---|---|
| `tools/pipeline/refine_segment.py` | Deterministyczny rdzeń: segmentacja zdań (ID + sąsiedzi) + wykrywanie chronionych szczytów. Wbudowany `--selftest`. | Create |
| `.claude/workflows/refine_panel.js` | Workflow: panel L1+L2 per zdanie (fan-out), zwraca oflagowanych kandydatów. | Create |
| `.claude/commands/refine.md` | Komenda `/refine <slug>` — orkiestracja pętli (segment → panel → przegląd → re-flow → do wyschnięcia). | Create |
| `CLAUDE.md` | Wpięcie `/refine` w łańcuch (między 3a a czytelnikami, on-demand) + Quick Command Reference. | Modify |

Przepływ danych: `04_working.md` → `refine_segment.py` → `.tmp/refine_<slug>_segments.json` → `Workflow(refine_panel, args=segments)` → kandydaci → `md/refine_candidates_iter{N}.md` → decyzje człowieka → in-session re-flow → `04_working.md` → (pętla).

---

## Task 1: Segmentacja zdań (rdzeń deterministyczny)

**Files:**
- Create: `tools/pipeline/refine_segment.py`

- [ ] **Step 1: Napisz szkielet z `--selftest` i pierwszymi (failującymi) asercjami**

```python
"""refine_segment.py — deterministyczna segmentacja skryptu na zdania
(ID + sąsiedzi) + wykrywanie chronionych szczytów. Stdlib only.

Użycie:
  python tools/pipeline/refine_segment.py <slug>            # → .tmp/refine_<slug>_segments.json
  python tools/pipeline/refine_segment.py x --selftest      # testy
"""
import re, json, argparse, os, sys

_ABBREV = {"np", "itd", "itp", "tj", "tzn", "tzw", "ok", "por", "wg", "nr", "godz", "min"}


def split_into_paragraphs(text):
    raise NotImplementedError


def split_sentences(paragraph):
    raise NotImplementedError


def _selftest():
    # — split_sentences: nie tnie wewnątrz „ ”, ani na em-dashu —
    s = split_sentences('Mówisz „znowu mi nie wyszło”. Idziesz dalej.')
    assert s == ['Mówisz „znowu mi nie wyszło”.', 'Idziesz dalej.'], s
    s = split_sentences('To był jeden dzień — nie wyrok na to, kim jesteś.')
    assert s == ['To był jeden dzień — nie wyrok na to, kim jesteś.'], s
    s = split_sentences('Pierwsze pytanie. Drugie pytanie. Trzecie.')
    assert len(s) == 3, s
    print("OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--infile", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest(); return


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Uruchom selftest — ma FAILOWAĆ**

Run: `python tools/pipeline/refine_segment.py x --selftest`
Expected: FAIL — `NotImplementedError` (funkcje to szkielety).

- [ ] **Step 3: Zaimplementuj `split_into_paragraphs` i `split_sentences`**

```python
def split_into_paragraphs(text):
    """Markdown skryptu → lista akapitów (bez nagłówków '## ' — nie są mówione)."""
    paras = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        paras.append(re.sub(r"\s*\n\s*", " ", block))   # zlej miękkie łamania w akapicie
    return paras


def split_sentences(paragraph):
    """Akapit → zdania. Respektuje „ ” (nie tnie w cudzysłowie), em-dash i skróty."""
    out, buf, depth, i, n = [], "", 0, 0, len(paragraph)
    while i < n:
        ch = paragraph[i]
        buf += ch
        if ch == "„":
            depth += 1
        elif ch == "”":
            depth = max(0, depth - 1)
        elif ch in ".!?…" and depth == 0:
            j = i + 1
            while j < n and paragraph[j].isspace():
                j += 1
            nxt = paragraph[j] if j < n else ""
            last = re.split(r"[\s(„]", buf[:-1])[-1].strip(".").lower()
            is_abbrev = ch == "." and last in _ABBREV
            ends = (nxt == "" or nxt.isupper() or nxt == "„")
            if ends and not is_abbrev:
                out.append(buf.strip()); buf = ""
        i += 1
    if buf.strip():
        out.append(buf.strip())
    return out
```

- [ ] **Step 4: Uruchom selftest — ma PRZEJŚĆ**

Run: `python tools/pipeline/refine_segment.py x --selftest`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add tools/pipeline/refine_segment.py
git commit -m "feat(refine): deterministyczna segmentacja zdań PL z selftest"
```

---

## Task 2: ID, sąsiedzi i wykrywanie chronionych szczytów

**Files:**
- Modify: `tools/pipeline/refine_segment.py`

- [ ] **Step 1: Dopisz failujące asercje do `_selftest` (nad `print("OK")`)**

```python
    # — segment_script: ID + sąsiedzi —
    text = "## Tytuł\n\nPierwsze zdanie sceny. Drugie zdanie.\n\nDrugi akapit z myślą.\n\nNie końcem."
    sents = segment_script(text)
    assert [x["id"] for x in sents] == ["s001", "s002", "s003", "s004"], sents
    assert sents[0]["prev"] == "" and sents[0]["next"] == "Drugie zdanie."
    assert sents[1]["prev"] == "Pierwsze zdanie sceny."
    # — chronione szczyty: cold open (akapit 0) + close (ostatni akapit) —
    assert sents[0]["is_peak"] is True   # cold open
    assert sents[3]["is_peak"] is True   # close
    assert sents[2]["is_peak"] is False  # środek
```

- [ ] **Step 2: Uruchom selftest — nowe asercje mają FAILOWAĆ**

Run: `python tools/pipeline/refine_segment.py x --selftest`
Expected: FAIL — `NameError: name 'segment_script' is not defined`.

- [ ] **Step 3: Zaimplementuj `segment_script` i `mark_peaks`**

```python
def segment_script(text):
    paras = split_into_paragraphs(text)
    sents = []
    for p_idx, para in enumerate(paras):
        for s in split_sentences(para):
            sents.append({"para": p_idx, "text": s})
    for k, s in enumerate(sents):
        s["id"] = f"s{k+1:03d}"
        s["prev"] = sents[k - 1]["text"] if k > 0 else ""
        s["next"] = sents[k + 1]["text"] if k + 1 < len(sents) else ""
    _mark_peaks(sents, len(paras))
    return sents


def _mark_peaks(sents, n_paras):
    """Chronione szczyty: cold open (akapit 0) + close (ostatni akapit).
    (Kotwice/motyw — semantyczne — chroni konserwatywny panel + człowiek, nie heurystyka.)"""
    last = n_paras - 1
    for s in sents:
        s["is_peak"] = bool(s["para"] == 0 or s["para"] == last)
```

- [ ] **Step 4: Uruchom selftest — ma PRZEJŚĆ**

Run: `python tools/pipeline/refine_segment.py x --selftest`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add tools/pipeline/refine_segment.py
git commit -m "feat(refine): ID, sąsiedzi i wykrywanie chronionych szczytów"
```

---

## Task 3: CLI — czytaj `04_working.md`, zapisz segmenty do `.tmp/`

**Files:**
- Modify: `tools/pipeline/refine_segment.py`

- [ ] **Step 1: Rozbuduj `main()` o realny odczyt/zapis**

```python
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--infile", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest(); return
    base = os.path.join("outputs", "videos_pl", args.slug, "md")
    infile = args.infile or os.path.join(base, "04_working.md")
    if not os.path.exists(infile):
        print(f"BŁĄD: brak {infile}", file=sys.stderr); sys.exit(1)
    with open(infile, encoding="utf-8") as f:
        sents = segment_script(f.read())
    os.makedirs(".tmp", exist_ok=True)
    out = os.path.join(".tmp", f"refine_{args.slug}_segments.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sents, f, ensure_ascii=False, indent=2)
    n_peak = sum(1 for s in sents if s["is_peak"])
    print(f"{len(sents)} zdań, {n_peak} chronionych szczytów → {out}")
```

- [ ] **Step 2: Smoke-test na realnym slug-3**

Run: `PYTHONIOENCODING=utf-8 python tools/pipeline/refine_segment.py 3_wstyd_za_wlasne_zycie`
Expected: wypis typu `~40 zdań, ~10 chronionych szczytów → .tmp/refine_3_wstyd_za_wlasne_zycie_segments.json`; otwórz JSON, sprawdź że cold open i „Ten poranek był tylko porankiem." są `is_peak: true`.

- [ ] **Step 3: Commit**

```bash
git add tools/pipeline/refine_segment.py
git commit -m "feat(refine): CLI segmentacji — 04_working.md → .tmp segments.json"
```

---

## Task 4: Workflow `refine_panel.js` — panel L1+L2 per zdanie

**Files:**
- Create: `.claude/workflows/refine_panel.js`

Bazuje na sprawdzonym POC (`wrabcyj69`), z trzema zmianami produkcyjnymi: (a) wejście z `args` (segmenty z Taska 3) zamiast hardcode; (b) **pomija `is_peak`**; (c) sędzia stosuje **konserwatywne** kryterium §3 specu (flaguj abstrakcję-argument + koślawy PL; crafted-concrete wygrywa); (d) intent **wymuszony polski**; (e) L1 z **podniesionym progiem** (sama ładna metafora to NIE kalka).

- [ ] **Step 1: Utwórz workflow z pełną treścią**

```javascript
export const meta = {
  name: 'refine_panel',
  description: 'Panel native-polszczyzny per zdanie: L2 forward-divergence + L1 back-translation. Zwraca oflagowanych kandydatow (czlowiek decyduje).',
  phases: [{ title: 'Intent' }, { title: 'Generate' }, { title: 'Judge' }],
}

const STYLE = 'Kanal SENSUM: cieply monolog do JEDNEJ osoby, druga osoba ("ty"), reportaz mowiony — konkret niesie sens, krotkie proste zdania, bezrodzajowo (czas terazniejszy). Mowione, nie pisane. Bez liczb, nazwisk, zargonu.'
const FLAG_RULE = 'KRYTERIUM (konserwatywne): flaguj TYLKO gdy zdanie (a) ARGUMENTUJE ABSTRAKCJE — unosi pojecie bez fizycznej kotwicy / odwraca sie od "ty" w generyczna rame / pietrzy zmiekczacze pisanego dowodu; ALBO (b) jest JAWNA KALKA — polski SAM W SOBIE brzmi koslawo/nie-natywnie. CHRON crafted-concrete: dopracowany konkretny obraz, gramatycznie natywny, nawet literacki, ZOSTAJE (keepOriginal=true). Crafted-concrete wygrywa. W razie watpliwosci: keepOriginal=true.'

// args = tablica zdan {id, text, prev, next, is_peak} z refine_segment.py
// (toleruj args podany jako tablica LUB jako string JSON — komenda/harness moze przekazac jedno lub drugie)
let _args = args
if (typeof _args === 'string') { try { _args = JSON.parse(_args) } catch (e) { _args = [] } }
const sentences = (Array.isArray(_args) ? _args : []).filter(s => s && !s.is_peak)

const INTENT = { type:'object', additionalProperties:false, properties:{ intent:{type:'string'} }, required:['intent'] }
const GEN = { type:'object', additionalProperties:false, properties:{ variants:{type:'array', items:{type:'string'}, minItems:5, maxItems:5} }, required:['variants'] }
const JUDGE = { type:'object', additionalProperties:false, properties:{ flag:{type:'boolean'}, keepOriginal:{type:'boolean'}, reason:{type:'string'}, candidate:{type:'string'} }, required:['flag','keepOriginal','reason','candidate'] }
const BT = { type:'object', additionalProperties:false, properties:{ literalEN:{type:'string'}, calqueSignal:{type:'boolean'}, note:{type:'string'} }, required:['literalEN','calqueSignal','note'] }

const out = await pipeline(
  sentences,
  (s) => agent(
    'Wydobadz SAM KOMUNIKACYJNY CEL tego zdania — co ma sprawic, ze sluchacz poczuje/zrozumie — opisany NEUTRALNIE, PO POLSKU, bez metafory i bez frazowania oryginalu. Nie cytuj oryginalnych slow. 1-2 zdania.\n\nZDANIE: "' + s.text + '"\nPRZED: "' + s.prev + '"\nPO: "' + s.next + '"',
    { label: 'intent:' + s.id, phase: 'Intent', schema: INTENT }
  ),
  async (intentRes, s) => {
    const cel = intentRes ? intentRes.intent : (s.text)
    const gen = await agent(
      STYLE + '\n\nNapisz to na glos, naturalna mowiona polszczyzna — 5 ROZNYCH sposobow do jednej osoby. Masz TYLKO cel (nie widzisz gotowego sformulowania). Kazdy 1-2 zdania, konkret zamiast abstrakcji.\n\nCEL: ' + cel,
      { label: 'generate:' + s.id, phase: 'Generate', schema: GEN }
    )
    return { cloud: gen ? gen.variants : [] }
  },
  async (genRes, s) => {
    const cloud = genRes ? genRes.cloud : []
    const [judge, bt] = await parallel([
      () => agent(
        'ORYGINAL: "' + s.text + '"\nCHMURA (5 slepych natywnych wypowiedzi tego samego sensu):\n' + cloud.map((v,k)=>(k+1)+'. '+v).join('\n') + '\n\n' + FLAG_RULE + ' Jesli flagujesz — podaj najlepsze mowione przepisanie (mozesz zlac warianty), inaczej candidate="". ' + STYLE,
        { label: 'judge:' + s.id, phase: 'Judge', schema: JUDGE }
      ),
      () => agent(
        'Przetlumacz DOSLOWNIE na angielski (slowo po slowie, szyk zachowany). Potem: czy POLSKI SAM W SOBIE brzmi koslawo/nie-natywnie, a angielski naturalniej? UWAGA: sama ladna metafora, ktora "czysto przechodzi" na angielski, to NIE kalka — kalka jest tylko gdy polski jest niezgrabny. calqueSignal=true tylko przy realnie koslawym polskim.\n\nPOLSKI: "' + s.text + '"',
        { label: 'backtrans:' + s.id, phase: 'Judge', schema: BT }
      ),
    ])
    return { id: s.id, draft: s.text, cloud, judge, bt }
  }
)

// Zwroc tylko oflagowane (czlowiek przeglada); plus surowe do sladu.
return {
  flagged: out.filter(r => r && r.judge && r.judge.flag && !r.judge.keepOriginal),
  all: out.filter(Boolean),
}
```

- [ ] **Step 2: Smoke-validate na 3-zdaniowym fixture (T1/T2/T3 z POC)**

Wywołaj `Workflow({ name: "refine_panel", args: [ {id:"s001",text:"Bo jedno drobne potknięcie to przecież jeszcze nie wyrok na całego człowieka.",prev:"",next:"",is_peak:false}, {id:"s002",text:"Szuflada z porzuconymi rzeczami to nie jest muzeum lenistwa.",prev:"",next:"",is_peak:false}, {id:"s003",text:"Ten poranek był tylko porankiem.",prev:"",next:"",is_peak:true} ] })`.
Expected: `s001` w `flagged` (abstrakcja → „kim jesteś"); `s002` **NIE** w `flagged` (crafted-concrete, keepOriginal); `s003` w ogóle pominięte (is_peak). Jeśli `s002` wpadnie do `flagged` — wzmocnij `FLAG_RULE` (kalibracja zbyt agresywna) i powtórz.

- [ ] **Step 3: Commit**

```bash
git add .claude/workflows/refine_panel.js
git commit -m "feat(refine): workflow panelu L1+L2 per zdanie (konserwatywny, pomija szczyty)"
```

---

## Task 5: Komenda `/refine <slug>` — orkiestracja pętli

**Files:**
- Create: `.claude/commands/refine.md`

Komenda jest wykonywana przez Claude in-session (jak `/draft`). Pętla i checkpoint człowieka żyją w orkiestracji (Workflow nie umie pauzować na człowieka); re-flow to in-session Integrator (jak 3b).

- [ ] **Step 1: Utwórz komendę z pełną treścią**

````markdown
# /refine — molekularna warstwa native-polszczyzny (segment → panel → przegląd → re-flow → do wyschnięcia)

Czytasz zdanie po zdaniu, łapiesz **abstrakcję-argument** i **jawne kalki**, proponujesz mówione przepisania **z dowodem** (chmura 5 ślepych wariantów + back-translation). **Człowiek decyduje każdą flagę — nigdy auto-replace.** Konserwatywnie: crafted-concrete i twarde szczyty zostają. Spec: `docs/superpowers/specs/2026-06-06-refine-molecular-native-pass-design.md` (§3 + §5 rządzą).

`<slug>` = katalog pod `outputs/videos_pl/`. Wejście: `md/04_working.md` (po Drafterze, przed czytelnikami) — albo wskazany plik.

## Step 1 — Walidacja
Potwierdź `outputs/videos_pl/<slug>/md/04_working.md`. Brak → powiedz userowi, żeby najpierw uruchomił `/draft <slug>`, stop.

## Step 2 — Segmentacja (`N = 1`)
Uruchom `PYTHONIOENCODING=utf-8 python tools/pipeline/refine_segment.py "<slug>"`. Wczytaj `.tmp/refine_<slug>_segments.json` (zdania z `id`, `text`, `prev`, `next`, `is_peak`).

## Step 3 — Panel (Workflow)
Wywołaj `Workflow({ name: "refine_panel", args: <tablica segmentów> })`. Workflow pomija `is_peak`, panelu L1+L2 per zdanie. Odbierz `{ flagged, all }`.

## Step 4 — Przegląd przez człowieka (NIE auto)
Jeśli `flagged` puste → przejdź do Step 6 (sucho). Inaczej zapisz `md/refine_candidates_iter{N}.md`: per flaga **oryginał → powód → chmura 5 wariantów → proponowany rewrite (candidate)**. Pokaż userowi zwięzłe podsumowanie i **poproś o decyzje** (accept / keep / wybierz-wariant / własna). Czekaj na odpowiedź. **Nie zmieniaj niczego bez decyzji.**

## Step 5 — Re-flow jedną ręką (in-session Integrator)
Z przyjętymi zmianami przepisz **CAŁY** `04_working.md` jako jeden bieg (jak 3b): wpleć zatwierdzone rewrite'y, popraw przejścia, **nieś fizyczny motyw**, **nie ruszaj** odrzuconych/keepOriginal ani twardych szczytów. Zapisz `04_working.md`. (Atomizacja bez kustosza = 60 idealnych zdań, które się nie kleją — tego unikasz.)

## Step 6 — Pętla do wyschnięcia
Jeśli w tej rundzie była ≥1 przyjęta zmiana **i** runda dała flagi: `N = N + 1`, wróć do Step 2 (segmentacja zmienionego tekstu) — ale w Step 4 re-challenge’uj tylko **zmienione + sąsiadów + nowe kalki**, nie otwieraj drobiazgów. Stop, gdy pełny przebieg nie daje nowej flagi w pozycji impaktowej, albo gdy user mówi „dość". Miękki limit ~4 rundy.

## Step 7 — Raport
- Liczba rund, ile flag / ile przyjętych / ile keepOriginal.
- Gdzie ślad: `md/refine_candidates_iter*.md`.
- Następny krok: czytelnicy (`/draft` panel) albo nagranie; przypomnij, że Twoje ucho na `script_corrected.docx` to ostateczny sufit.

## Notes
- **Ty jesteś modelem** dla intentu? Nie — panel (L1/L2) robi `Workflow(refine_panel)`. Ty robisz segmentację (Python), przegląd z człowiekiem, re-flow (Integrator) i pętlę.
- **Bezpieczniki nienegocjowalne (spec §5):** człowiek decyduje każdą flagę; szczyty i crafted-concrete chronione; re-flow jedną ręką; stop gdy sucho. Oryginał może wygrać.
- Koszt/czas nieistotny (on-demand). To NIE zastępuje czytelników ani Twojego ucha — to warstwa molekularna przed nimi.
````

- [ ] **Step 2: Walidacja czytelności**

Przeczytaj `.claude/commands/refine.md` — potwierdź, że kroki są jednoznaczne, ścieżki zgodne z Taskami 1–4, i że nigdzie nie ma auto-replace bez Step 4.

- [ ] **Step 3: Commit**

```bash
git add .claude/commands/refine.md
git commit -m "feat(refine): komenda /refine — orkiestracja segment→panel→przegląd→re-flow→pętla"
```

---

## Task 6: Walidacja empiryczna na slug-3 (kryterium akceptacji)

**Files:** (brak — przebieg end-to-end)

To nie jest unit-test (warstwa LLM jest niedeterministyczna) — to **akceptacja** z jawnymi oczekiwaniami ze specu §7.

- [ ] **Step 1: Odpal `/refine 3_wstyd_za_wlasne_zycie`** (pełna pętla).

- [ ] **Step 2: Sprawdź kryteria sukcesu (spec §7):**
  - (a) **łapie** eseistyczne abstrakcje typu „…wyrok na całego człowieka", „Cała różnica jest w tym…", „To jest umowa, której…" — z mówionymi rewrite'ami w `refine_candidates_iter1.md`;
  - (b) **NIE** flaguje crafted-concrete — jeśli w slug-3 jest linia typu „muzeum lenistwa", zostaje;
  - (c) po re-flow `04_working.md` **klei się** w jeden bieg (przeczytaj na głos w głowie — niesiony motyw, brak 60 rozsypanych zdań);
  - (d) zostało realnie mało do roboty dla ludzkiego ucha.

- [ ] **Step 3: Jeśli (a)–(d) spełnione — commit wyniku; jeśli nie — zanotuj rozjazd i wróć do Taska 4 (kalibracja `FLAG_RULE`) lub Taska 5 (re-flow).**

```bash
git add outputs/videos_pl/3_wstyd_za_wlasne_zycie/md/
git commit -m "test(refine): walidacja /refine na slug-3 (T1 flaguje, crafted-concrete zostaje)"
```

---

## Task 7: Wpięcie w CLAUDE.md i Agent Chain

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Dodaj `/refine` do Quick Command Reference** (sekcja z `/draft`, `/hook`…):

```text
/refine <slug>   # molekularna warstwa native-polszczyzny (segment→panel L1+L2→przegląd→re-flow→do wyschnięcia); on-demand, między 3a a czytelnikami
```

- [ ] **Step 2: Dodaj wiersz do tabeli Agent Chain** (po 3a, przed czytelnikami), zaznaczając: opcjonalna, on-demand, człowiek decyduje, silnik Workflow + `refine_segment.py`.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(refine): wpięcie /refine w Quick Reference i Agent Chain"
```

---

## Self-Review

**1. Spec coverage:**
- §1 cel → Tasks 4–6. ✓
- §2 maszyna-proponuje/człowiek-decyduje → Task 5 Step 4 (przegląd bez auto-replace). ✓
- §3 kalibracja konserwatywna → Task 4 `FLAG_RULE` + Task 6 (b). ✓
- §4 architektura (segment→panel→przegląd→re-flow→pętla) → Tasks 1–5. ✓
- §5 bezpieczniki (człowiek decyduje / szczyty / re-flow jedną ręką / stop gdy sucho) → Task 2 (`is_peak`), Task 4 (pomija peaks), Task 5 (Step 4, 5, 6). ✓
- §6 poza MVP (turniej/L5/persony) → świadomie pominięte. ✓
- §7 walidacja → Task 6. ✓
- §8 ryzyka: intent-leak → Task 4 intent „PO POLSKU, bez frazowania oryginału"; re-flow najtrudniejszy → Task 5 + Task 6 (c). ✓
- §9 trigger `/refine` on-demand → Task 5 + Task 7. ✓

**2. Placeholder scan:** brak TBD/TODO; każdy krok z kodem ma kod; kryteria akceptacji konkretne. ✓

**3. Type consistency:** `segment_script`/`split_sentences`/`split_into_paragraphs`/`_mark_peaks` spójne między Taskami 1–3; pola zdania (`id`,`text`,`prev`,`next`,`is_peak`,`para`) zgodne z `args` konsumowanym w `refine_panel.js` (Task 4) i komendą (Task 5). Workflow zwraca `{flagged, all}` — konsumowane w Task 5 Step 3. ✓

---

## Uwaga o testowaniu (świadoma decyzja)

Projekt nie ma pytest ani `tests/`. Rdzeń deterministyczny (segmentacja + szczyty) testujemy przez wbudowany `--selftest` (plain `python`, zero nowych zależności) — to pasuje do ethosu „skrypty, które się odpala". Warstwa LLM (panel, re-flow) jest niedeterministyczna i walidowana empirycznie (Task 6) z jawnymi kryteriami — nie udajemy unit-testów tam, gdzie ich nie ma.
