# Redesign łańcucha skryptu: płynny esej-voiceover (proces „panel + jedna ręka")

- **Data:** 2026-06-06
- **Status:** Draft — do recenzji użytkownika przed planem implementacji
- **Branch:** feat/package-agent
- **Kontekst:** sesja brainstorm (Maciek + Claude). Punkt wyjścia: niezadowolenie z `outputs/videos_pl/3_wstyd_za_wlasne_zycie/md/04_final.md`.

---

## 1. Problem

Skrypty czytają się jak ciąg urywanych, niepołączonych fragmentów — „**nie klei się**" (słowa właściciela). Każde zdanie to osobne uderzenie; brakuje tkanki łączącej, która niosłaby myśl ze zdania w zdanie. Efekt: tekst brzmi jak lista aforyzmów, nie jak esej czytany na głos.

Trzy przyczyny źródłowe:

1. **Doktryna nagradza staccato.** `style_guide.md` §137–144 i §12.10 chwalą „krótkie zdanie — do uderzenia", „zdanie, które brzmi jak cios", „skróć przeładowane zdanie do uderzenia". Nie ma żadnej przeciwwagi premiującej spójność i przepływ. (DNA eseju jest — linia 21: „esejowo-popularnonaukowy z rytmem voice-overu" — ale przeważone w stronę cięcia.)
2. **Review jest defensywną maszyną triage.** Agent 3c skanuje kategorie A–K, klasyfikuje severity (BLOCKER/FIX/WATCH), liczy progi i wydaje binarny PASS/FLAG. Dwa mechanizmy **wprost każą odpuścić** szlifowanie: „iteration dampener" (od iteracji 3 flaguje tylko BLOCKER-y) i „anti-sterility guard / edit-guard" (boi się, że poprawianie spłaszczy prozę). Linia po prostu *słaba, ale czysta* (brak kalki, brak zakazanej frazy) jest **zaprojektowana, żeby przejść**. Nie istnieje kategoria „to się nie klei".
3. **Część praktyczna wymuszona.** `narrative_architectures.md` linia 198 czyni Permission Practice „zablokowaną regułą strukturalną — każdy skrypt musi zawierać sekcję PP". Agent dokleja ~4 mikropraktyki nawet gdy temat ich nie unosi → generyczne, przyklejone ćwiczenia (spalona rama „dłoń na klatce + trzy wydechy" powtórzona w slugach 1→2→3).

**Dowód (slug-3 „wstyd"):** linie, które przechodzą każdą regułę, a nie lądują:
- „Zostawia ci jakiś ruch." — abstrakcja zamiast konkretu.
- „Liczysz się o tyle, o ile dziś coś osiągniesz." — formuła logiczna, nie zdanie mówione.
- „…swój cały, prawdziwy, męczący środek." — koślawa abstrakcja („środek") + przeładowanie przymiotnikami.

Żadna nie łamie kategorii A–K. Dlatego system ich nie łapie.

---

## 2. Cel — głos docelowy

**Płynny esej psychologiczny czytany na głos, z nutą liryzmu, spójny.** Jeden obraz niesiony przez całą sekcję. Tkanka łącząca między zdaniami. Krótkie uderzenia zostają — ale jako **przyprawa zasłużona płynnością**, nie jako domyślna tekstura.

Wzorzec „przed/po" (zatwierdzony przez właściciela jako „to jest to") — sekcja „Zawsze ktoś jest dalej":

**PRZED (urywane fragmenty):**
> Otwierasz telefon i widzisz cudze poranki, cudze treningi, cudze sukcesy.
> Ktoś młodszy już to ma. Ktoś zmęczony i tak daje radę. Ktoś inny „ogarnia".
>
> Tylko że widzisz wyłącznie to, co ludzie postanowili pokazać. Gotowy efekt. Nigdy wysiłku, zmęczenia, dni, w których im też się nie chciało.
> A ty zestawiasz z tym swój cały, prawdziwy, męczący środek.
>
> Nie porównujesz życia z życiem.
> Porównujesz je z czyimś najlepszym kadrem.

**PO (płynący głos, jeden obraz — „kadr" — niesiony przez całość):**
> Otwierasz telefon i świat od razu pokazuje ci ludzi, którzy są już dalej — czyjś poranek, czyjś trening, czyjś spokój, który wygląda, jakby nic nie kosztował. A ty patrzysz na to wszystko z samego środka swojego zwykłego, jeszcze niegotowego dnia. I porównujesz. Tyle że porównujesz dwie rzeczy, których porównać się nie da: ich dopięty, wybrany kadr — i całą swoją resztę, tę, której nikt nigdy nie zobaczy. Zmęczenie. Poranki, w których tobie też się nie chciało wstać. Cały wysiłek, który u nich został po prostu wycięty z kadru.
>
> Więc nie porównujesz życia z życiem. Porównujesz je z czyimś najlepszym kadrem. I zawsze przegrywasz — bo zawsze jest gdzieś jakaś spokojniejsza, bardziej poukładana wersja ciebie, którą rzekomo wciąż masz dopiero przed sobą. Nigdy nie jesteś u siebie. Zawsze w drodze do kogoś lepszego.

Co robi wzorzec (= zasady nowego stylu):
- **Tkanka łącząca** („A ty…", „Tyle że…", „Więc…", „I zawsze…") niesie myśl, nie skacze.
- **Jeden obraz rozwijany** (kadr → wycięty z kadru → najlepszy kadr) zamiast nowej metafory co dwie linie.
- **Mocne krótkie domknięcia zostają — na końcu, zasłużone** przez płynność, która je ładuje.

---

## 3. Czego NIE zmieniamy (non-goals)

- **Reszta pipeline'u nietknięta:** research (0/1/2), hook (`/hook`), visuals (`/visuals`), package (`/package`), publish (`/publish`), align.
- **Szkielet zostaje:** 5 architektur narracyjnych, selektor architektury (Step 1.6), dividery sekcji `##`.
- **Nienegocjowalne doktryny zostają:** research-invisible, druga osoba „ty", bezrodzajowość + ciepło, polityka liczb, polityka żargonu, jedna główna metafora, zero numerowanych list, recognition close jako ostatnie słowo.
- **Nazwy wyjść bez zmian:** `04_final.md`, `04_working.md`, `docx/script.docx` — downstream na nich stoi.

---

## 4. Nowy proces `/draft`

```
Selektor architektury        (zostaje — Step 1.6, wybiera kształt narracji pod temat)
        │
   ┌────▼────┐
   │ DRAFTER │  jedna ręka (lead in-session) — pisze CAŁY skrypt celując od razu
   └────┬────┘  w płynny esej-voiceover. Osądza, czy Permission Practice pasuje (§5).
        │
   ┌────▼─────────────────────────────┐
   │  PANEL 2 CZYTELNIKÓW (zimny       │  każdy czyta całość na świeżo (nie pisał),
   │  kontekst — Agent Teams teammates)│  daje CAŁOŚCIOWY redakcyjny feedback:
   │                                  │  cytat → dlaczego nie gra → podpowiedź
   │  • Czytelnik 1: SPÓJNOŚĆ i        │  brzmienia (hint). Kończy prostym werdyktem
   │    przepływ                       │  „PŁYNIE / JESZCZE NIE".
   │  • Czytelnik 2: GŁOS i liryzm     │
   │    (wchłania native-ear/kalki)    │
   └────┬─────────────────────────────┘
        │
   ┌────▼──────┐
   │ INTEGRATOR│  jedna ręka (lead) — czyta oba feedbacki i przepisuje CAŁY skrypt
   └────┬──────┘  na nowo (scala, nie łata) → jeden głos, bez szwów.
        │
        ├──◄ pętla: aż OBAJ czytelnicy „PŁYNIE" (miękki bezpiecznik ~5 rund)
        │
   ┌────▼──────────────┐
   │ BRAMKA DOKTRYNY   │  cienki checklist nienegocjowalnych (§6). Raz, na końcu.
   │ (raz, na końcu)   │  Twarde naruszenie → integrator poprawia w miejscu.
   └────┬──────────────┘  To NIE jest dawna triage-maszyna A–K.
     04_final.md
```

### Format feedbacku (kluczowa zmiana filozofii)

Czytelnicy dają **całościowy feedback redakcyjny** — jak doświadczony redaktor czytający całość („tu sekcja czyta się jak lista, zlej ją w jeden bieg"; „tu obraz umiera w połowie"; „ta linia sięga za daleko, ląduje na zgrzycie") — **nie** skan kategorii z progami severity. Werdykt na wyjściu jest binarny dla orkiestratora (`PŁYNIE` / `JESZCZE NIE`), ale **ciało** to proza redakcyjna, nie tabela naruszeń.

Czytelnik **nie edytuje** skryptu — cytuje, diagnozuje, podpowiada brzmienie jako hint. Integrator (jedna ręka) jest jedynym, który pisze. To gwarantuje spójny głos.

### Soczewki czytelników

- **Czytelnik 1 — Spójność i przepływ:** Czy całość trzyma się jako jeden esej? Czy sekcje wpływają jedna w drugą? Sieroce fragmenty stojące samotnie bez powodu? Czy centralny obraz jest niesiony, czy porzucony? **Czy Permission Practice (jeśli jest) wyrasta naturalnie, czy brzmi jak doklejony szew?** (przejmuje ducha redakcyjnego po dawnym 3c).
- **Czytelnik 2 — Głos i liryzm:** Czy każda linia jest żywa, mówiona, piękna? Koślawe abstrakcje, sięganie za daleko, kalki/translationese (wchłania robotę dawnego native-ear 3d — 4 nazwane tells, kalki struktury EN, zderzenia rejestru), płaski rytm, watowanie, frazesy.

### Zbieżność / stop

- Pętla działa, **aż oba** werdykty = `PŁYNIE`.
- **Miękki bezpiecznik ~5 rund:** jeśli po ~5 wciąż nie ma zbieżności, finalizuj mimo to z **nagłówkiem WARNING** w `04_final.md` wskazującym na ostatnie logi czytelników (jak dzisiejszy mechanizm hard-stop).

---

## 5. Permission Practice → opcjonalna

**Zmiana reguły.** PP przestaje być obowiązkowa. Drafter osądza redakcyjnie: czy z **centralnego obrazu tego skryptu** wynika prawdziwy, konkretny ruch, który widz mógłby zrobić?

- **Jeśli tak** → wplata go płynnie (proza, język pozwolenia, **nigdy** numerowana lista). Mogą to być 1–4 mikropraktyki — tyle, ile temat unosi, nie sztywne „4 na siłę".
- **Jeśli nie** → skrypt idzie **prosto do recognition close**, bez doklejania ćwiczeń.

**Recognition close zostaje obowiązkowy** — zawsze dostaje ostatnie słowo (to serce, nie część praktyczna).

**Kto egzekwuje „nie na siłę":**
- Drafter nie wymusza PP.
- Czytelnik 1 (spójność) flaguje doklejoną/generyczną praktykę jako szew („brzmi jak przyklejone — odpuść").
- Bramka doktryny **przestaje wymagać** PP; sprawdza tylko: *jeśli* praktyka jest, to płynna proza (nie lista) i recognition close po niej.

---

## 6. Zmiany w doktrynie (guide'y)

1. **`style_guide.md` — rebalans, nie wyrzucenie.** Dodać spójność/przepływ jako **wartość #1** (sekcja „tkanka łącząca / nieś jeden obraz / domyślnie łącz, nie tnij"), z wzorcem przed/po z §2. Zdemować staccato-punch (§137–144, §12.10) do **przyprawy zasłużonej płynnością** (nie domyślnej tekstury). „Oddech — najmocniejsze zdania na osobnej linii" (§163) zostaje, ale jako rzadki akcent.
2. **`voice_corpus.md` §A** — dodać **płynne** wzorce (dłuższe, niosące zdania), nie tylko urywane. §C/§C2 (kalki, 4 tells) zostają jako referencja Czytelnika 2.
3. **`narrative_architectures.md`** — PP opcjonalna: przepisać linię 198 („zablokowana reguła" → „opcjonalna, gdy pasuje"), poluzować „Ograniczenie close" w każdej architekturze (PP staje się *jeśli obecna* beatem-przed-ostatnim), zachować „Dwa rejestry" i test genericzności jako kryteria *gdy PP jest obecna*.
4. **`CLAUDE.md`** — zaktualizować: „Permission Practice (mandatory close…)" → opcjonalna; opis łańcucha 3a→3b↔3c→3d → nowy proces (Drafter → panel 2 czytelników → integrator → bramka); tabela Agent Chain.
5. **Usunąć z review (nie przenoszą się do nowego panelu):** iteration dampener, anti-sterility guard, edit-guard, binarna triage-maszyna kategorii A–K. Ich **nienegocjowalne** jądra (B/D/E/F/G — research-framing, rodzaj/osoba, numerowane listy, liczby-findings, imienne szczegóły) destylują się do **cienkiej bramki doktryny** (§4).

---

## 7. Mapowanie plików (stare → nowe)

| Stare | Nowe | Charakter zmiany |
|---|---|---|
| `03a_drafter.md` | **Drafter** | przestawiony na płynny cel; osądza fit PP |
| `03b_revisor.md` | **Integrator** | całościowy rewrite jedną ręką (nie łatanie zaznaczeń) |
| `03c_reviewer.md` | **wygaszony** jako bramka-kategorii | nienegocjowalne → cienka bramka doktryny; duch redakcyjny → Czytelnik 1 |
| `03d_native_ear.md` | **Czytelnik 2** | głos + liryzm + kalki (rozszerzony z samego translationese) |
| (nowy) | **Czytelnik 1** | spójność/przepływ + „PP nie na siłę" |
| (nowy) | **bramka doktryny** | cienki checklist nienegocjowalnych |
| `.claude/commands/draft.md` | przepisany | orkiestruje nowy kształt |

Artefakty logów review (`03c_review_iter*.md`, `03d_nativeear_*_iter*.md`) → nowe nazwy logów czytelników (np. `03_read_cohesion_iter{N}.md`, `03_read_voice_iter{N}.md`) — **dokładne nazwy ustala plan implementacji**. Wyjścia `04_working.md` / `04_final.md` / `docx/script.docx` **bez zmian**.

---

## 8. Komponenty (izolacja i odpowiedzialność)

- **Drafter** — *co:* pisze cały skrypt pod cel z §2, decyduje o PP. *Wejście:* `02_verified_research.md`, `03_architecture.md`, guide'y. *Wyjście:* `03a_draft.md`. *Zależność:* selektor architektury.
- **Czytelnik 1 (spójność)** — *co:* całościowy feedback o przepływie + „PP nie na siłę"; werdykt PŁYNIE/JESZCZE NIE. *Wejście:* `04_working.md`, `voice_corpus.md` §A. *Wyjście:* własny log. *Zależność:* żadna na Czytelnika 2 (niezależny).
- **Czytelnik 2 (głos/liryzm)** — *co:* całościowy feedback o życiu linii + kalki; werdykt. *Wejście:* `04_working.md`, `voice_corpus.md` §A/§C/§C2. *Wyjście:* własny log. *Zależność:* niezależny od Czytelnika 1.
- **Integrator** — *co:* czyta oba logi, przepisuje cały skrypt jedną ręką. *Wejście:* `04_working.md` + dwa logi. *Wyjście:* nowy `04_working.md`. *Zależność:* oba logi z rundy.
- **Bramka doktryny** — *co:* checklist nienegocjowalnych raz na końcu; twarde naruszenie → poprawka w miejscu. *Wejście:* finalny `04_working.md`. *Wyjście:* `04_final.md` (+ ewentualny WARNING).

Niezmienna zasada: **dwóch agentów nigdy nie edytuje jednego pliku.** Czytelnicy tylko czytają `04_working.md` i piszą własne logi; integrator jest jedynym, który edytuje `04_working.md`.

---

## 9. Obsługa błędów

- **Agent Teams niedostępny** → auto-fallback w pełni in-session: lead odgrywa obu czytelników jako świeże przejścia (dyscyplina „czytaj na zimno, default do JESZCZE NIE przy niepewności"), potem integruje. Bez osobnej komendy, bez flagi (jak dzisiejszy fallback).
- **Brak zbieżności po ~5 rundach** → ship z nagłówkiem WARNING wskazującym ostatnie logi czytelników.
- **Bramka łapie twarde naruszenie, którego integrator nie umie czysto poprawić** → `AskUserQuestion`: (a) popraw w miejscu, (b) przyjmij z ostrzeżeniem.
- **Teardown teamu** — zawsze (Agent Teams pozwala na jeden team naraz; zwisający blokuje `/draft` i `/publish`).

---

## 10. Jak sprawdzimy, że działa (definition of done)

- **Test regeneracji:** przepuść istniejący temat (slug-3 „wstyd") przez nowy łańcuch; porównaj wyjście — czy czyta się jak płynny esej zamiast staccato; czy zniknęły 3 zacytowane linie-zgrzyty.
- **Sygnał wewnętrzny:** oba czytelnicy `PŁYNIE`; bramka doktryny czysta.
- **Finalne ucho:** właściciel czyta i potwierdza „klei się".
- **Brak regresji doktryny:** nowy skrypt dalej research-invisible, druga osoba, bezrodzajowy, zero zakazanych fraz, zero numerowanych list.

---

## 11. Ryzyka / otwarte kwestie

- **Spójność vs beat-struktura architektur.** Architektury (zwłaszcza Composite Portrait) mają wbudowane „ruchy", które sprzyjają cięciu. Integrator musi nieść przepływ *wewnątrz* ruchów. Do obserwacji na pierwszych skryptach.
- **Niezależność czytelników w fallbacku in-session.** Gdy lead odgrywa obu, traci „zimny kontekst". Mitygacja: dyscyplina świeżego czytania; preferuj Agent Teams gdy dostępny.
- **Migracja.** Nie retrofitujemy starych skryptów — nowy łańcuch obowiązuje od kolejnych. (Opcjonalnie: regeneracja slug-3 jako test + ewentualny re-record.)
- **Koszt.** Panel = 2 dodatkowe konteksty × do ~5 rund. Akceptowalny (jakość > koszt dla rdzenia kanału).

---

## 12. Odwracalność

- Stary łańcuch żyje w historii Gita (tag `en-pipeline-v1` już istnieje dla wersji EN). **Przed wygaszeniem 3c** dodać tag/branch znacznikowy (np. `pl-triage-chain-v1`) i wpis w `docs/reversibility.md` z gotowymi `git checkout … -- <path>`.
- Zmiana jest plikowa (guide'y + prompty + komenda) — w pełni odwracalna per plik.

---

## 13. Następny krok

Po akceptacji tego spec → `writing-plans` (plan implementacji): kolejność = (1) guide'y/doktryna, (2) prompty agentów (Drafter/Czytelnik 1/Czytelnik 2/Integrator/bramka), (3) `/draft`, (4) `CLAUDE.md`, (5) test regeneracji slug-3.
