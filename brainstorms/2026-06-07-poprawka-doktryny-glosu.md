# Poprawka doktryny głosu (reguły SENSUM): Brainstorm / Discovery Notes
Date: 2026-06-07 · Goal: Zaprojektować poprawkę kanonu głosu (6 reguł żyjących w `voice_brief.md` = źródło, `03a_writer.md` = wklejka, `CLAUDE.md` = destylat) tak, by reguły miały ZĘBY — celując w defekty dające się ująć w konkretne, policzalne reguły, a nie mgliste oceny jakości (które Opus i tak ignoruje jako pisarz i jako checker).

Cross-ref: `2026-06-07-context-checker-ensemble.md` (ensemble checker), `2026-06-07-lean-draft-redesign.md` (lean 3-agent chain).

## Summary / key decisions
(aktualizowane na bieżąco)

### Pre-loaded context (ustalone wcześniej w tej sesji — fundament, nie odpowiedzi z grilla)
- **Centralne odkrycie sesji:** model nie potrafi skorygować WŁASNEGO rejestru z mglistej reguły. Opus przeczytał 6 reguł jako pisarz i i tak wyprodukował tiki; checker czyta te same reguły i je przepuszcza. Mglista reguła jakościowa = no-op (jak stary reader-panel / `/refine`). Hipoteza robocza: **reguła KONKRETNA i POLICZALNA** (np. „nie otwieraj zdań od »Bo«/»A«") mogłaby mieć zęby tam, gdzie mglista („nie piętrz metafor") ich nie ma.
- **Lewar 1 (swap pisarza) ZAMKNIĘTY.** Gemini (ręczny test) i Sonnet 4.6 (test in-session, ten sam `03a_writer.md`) — oba piszą płynnie, ale POZA doktryną: wymieniają tiki Opusa na tiki własnego rejestru i łamią reguły, które Opus trzyma. **Opus zostaje pisarzem.** Lewar 2 (detektor z innej rodziny) to osobna, wciąż żywa ścieżka.
- **Co Sonnet odsłonił (test in-session, slug 3):** spójnikowe otwarcia spadły o połowę (21 vs 42), ALE złamał 3 jawne reguły, które Opus utrzymał: R3 („układ nerwowy", wykład „poczucie winy vs wstyd"), R4 (4 piętrzone metafory: teatr/akumulator/więzienie/maszyna). Plus 1 defekt BEZ reguły: współczesne realia (Instagram/social media/„markę osobistą") — Opus tego nie robi mimo braku reguły.
- **4 klastry przewinień (z ~25 ręcznych flag usera na drafcie Opusa):** (A) centralna metafora wyciekła w ukute kolokacje; (B) tiki spójnikowe („Bo"/„I to"/„To dlatego"/„Więc"); (C) przekombinowane / nadkonstrukcja; (D) fałszywa oralność.
- **Twarde liczby z draftu Opusa (slug 3, 1204 słowa):** 42 spójnikowe otwarcia (Bo ×10, A ×9, I ×10, Ale ×5, Więc ×3, I to ×3, To dlatego ×2); ~18 trafień słownictwa-buchalterii.

### Aktualny stan 6 reguł (voice_brief.md — kanon)
1. Ciepło, do jednej osoby (DO człowieka, nie O zjawisku).
2. Uczucia nazywane wprost (wstyd/wina/lęk = rdzeń, NIE żargon).
3. Bez badań / liczb / nazwisk / żargonu klinicznego (research niewidzialny).
4. Jeden centralny obraz (nie piętrz metafor).
5. Recognition close na końcu.
6. Naturalny mówiony polski + naturalny rodzaj.
+ test nadrzędny: „czy Polak powiedziałby to na głos drugiej osobie?"
+ część praktyczna opcjonalna i lekka.

### Fork na wejściu do grilla
- **(A)** domknąć lukę o realiach w R3 (zakaz marek/Instagrama/bezczasowości) — wąskie, ubezpieczenie dla off-family, niski zwrot skoro zostaje Opus.
- **(B)** obrona przed własnymi tikami Opusa (spójniki / buchalteria / przekombinowanie) — celuje w prawdziwego sprawcę, ale działają tylko tiki ujmowalne w konkretną regułę.

## Q&A log

### Q1 — cel poprawki (A realia / B własne tiki / oba)
- Asked: bierzemy (A) lukę o realiach, (B) obronę przed tikami Opusa, czy oba?
- Captured: **REDIRECT / PIVOT.** User: „chciałbym chyba opuścić gardę z doktryną" — zamiast DODAWAĆ reguły (B), chce krok wstecz i **poluzować** doktrynę. Poprosił o spisanie WSZYSTKICH reguł, jakie mamy, żeby odnieść się do każdej. Kierunek grilla odwrócony: z „co dodać" → „co zostawić / poluzować / wyciąć".
- Flags: pivot kierunku → cel sesji teraz = przegląd+rozluźnienie, nie zacieśnienie.

## Inwentarz reguł — pełna doktryna (union: voice_brief.md + 03a_writer.md + CLAUDE.md), do reakcji usera
Tag: 🔒 = tożsamość (kanał umiera bez tego, moja rekomendacja: pilnować) · 🔓 = guardrail/kraft (gardа do opuszczenia) · ⚙️ = mechanika.

- **R1 Ciepło, do jednej osoby** 🔒 — „ty", mądry przyjaciel; nigdy wykładowca. → **werdykt: ZOSTAJE, ale poluzować absolut „nie O zjawisku".** Czasem o zjawisku wolno napisać — zjawiska są ciekawe, nie ograniczać się. Default = DO człowieka; O zjawisku dozwolone okazjonalnie.
- **R2 Naturalny rodzaj** → **werdykt: USUNĄĆ jako regułę.** Męski generyczny kiedykolwiek trzeba. Koniec tematu — żadnej reguły o rodzaju.
- **R3a Uczucia wprost** 🔒 — wstyd/wina/lęk/wyrzuty po imieniu. → **werdykt: ZOSTAJE.**
- **R3b Zero żargonu** 🔒 → **werdykt: PRZEDEFINIOWAĆ.** Zakaz tylko żargonu TRUDNEGO dla zwykłego człowieka. „Układ nerwowy" = OK (zrozumiały). Wciąż zakazane: dysonans poznawczy, kwantyfikator (trudne). Test = zrozumiałość, nie kliniczność.
- **R3c Termin naukowy tylko raz, późno** → **werdykt: USUNĄĆ.**
- **R4a Research niewidzialny** → **werdykt: zero nazwisk i lat ZOSTAJE; ale „badania pokazują" DOZWOLONE.** (Research lekko widzialny — wolno powiedzieć „badania pokazują", byle bez nazwisk/lat.)
- **R4b Polityka liczb** 🔓 — okrągłe/oprawione; zakaz decymali/effect-size/p-value/liczby badań. → **werdykt: ZOSTAJE.**
- **R4c Jeden wyjątek research-frame** → **werdykt: USUNĄĆ.** (Zbędne — „badania pokazują" i tak teraz dozwolone ogólnie.)
- **R5a Jeden centralny obraz** 🔒 — jedna metafora, nie piętrz. → **werdykt: USUNĄĆ (cały R5).** Uzasadnienie usera: przez jedną metaforę jest jednostajnie, nudno; Opus ma trudność napisać ciekawy skrypt na bazie jednej metafory. → Hipoteza (moja, do walidacji): R5a mógł BYĆ przyczyną Klastra A (metafora rozciągana na siłę przez 1200 słów → ukute kolokacje „prowadzisz na sobie konto", „zmontowany brzeg"). Usunięcie R5a może ten klaster ZMNIEJSZYĆ, nie zwiększyć.
- **R5b Max 2–3 imperatywy uwagi** 🔓 → **werdykt: USUNĄĆ (część „cały R5").**
- **R5c Żadnej niecytowanej okrągłej statystyki** 🔓 (dubluje R4b) → **werdykt: USUNĄĆ (i tak dubluje R4b).**
- **R6a Otwarcie sceną/pytaniem** 🔒 → **werdykt: ZOSTAJE** („ma być taki Hook").
- **R6b Recognition close ZAWSZE ostatni** 🔒 → **werdykt: ZOSTAJE.**
- **R6c Permission Practice opcjonalna+lekka, nigdy numerowana lista** 🔓 → **werdykt: ZOSTAJE.**
- **R7 Naturalny mówiony polski (test nadrzędny)** 🔒 → **werdykt: ZOSTAJE — „to musi być".**
- **R8 Pisz luźno, nie broniąc się przed listą** 🔒 (anty-sztywność) → **werdykt: ⏳ ODŁOŻONE.** User: „może jak usuniemy to co wyżej, to też nie będzie potrzebne". Rewizja na końcu, po zobaczeniu skróconej listy.
- **M1 Długość 1000–1500 słów** ⚙️ → **werdykt: zostaje (nie ruszane).**
- **M2 Format: markdown, `## `, zero metadanych** ⚙️ → **werdykt: zostaje (nie ruszane).**

### Q3 — R5 (cały) + dryf rejestru
- Captured R5: **cały R5 USUNĄĆ.** Powód: jedna metafora → jednostajnie/nudno + Opus ma trudność z ciekawym skryptem na jednej metaforze.
- Captured dryf: **ŚWIADOMY i CHCIANY.** User: „chcę zobaczyć, w którą stronę pójdzie SENSUM. Mam wrażenie, że zrozumieć pozwala bardziej, jeśli wytłumaczy się trochę mechanizm — dochodzi się wtedy do tego SENSUM." → Teza kierunkowa: wyjaśnienie mechanizmu = ścieżka do wglądu, nie zdrada ciepła. To EKSPERYMENT — oceniamy po następnym drafcie.

## Key decision — kierunkowy pivot SENSUM v2
**SENSUM staje się odrobinę bardziej WYJAŚNIAJĄCY i SWOBODNIEJSZY formalnie.** Mechanizm wolno trochę wytłumaczyć; „badania pokazują" OK; zrozumiały termin (układ nerwowy) OK; o zjawisku czasem OK; **koniec przymusu jednej metafory** (wolno kilka obrazów). Niezmienne 🔒: ciepło/„ty", uczucia wprost, hook na otwarciu, recognition close na końcu, naturalny mówiony polski, dyscyplina liczb (R4b). To świadomy eksperyment — „zobaczmy, w którą stronę pójdzie".

### Q4 — R8 + permisja metafory (domknięcie)
- Captured: **R8 ZOSTAJE (odchudzona)** — „r8 zostaw". **Permisja metafory WCHODZI** — „metafora - tak jak radzisz". Completeness backstop: user nie zgłosił nic więcej do ruszenia.

## Status: v2 ZATWIERDZONE i WPISANE (2026-06-07)
Wszystkie werdykty zamknięte. Doktryna v2 wpisana w 4 pliki:
1. `workflows/guides/voice_brief.md` — pełny rewrite (kanon, 7 reguł + zasady nadrzędne + permisja metafory).
2. `workflows/pipeline/03a_writer.md` — rewrite wklejki na 7 reguł v2 + linia permisji metafory.
3. `CLAUDE.md` — destylat „### Script voice — the non-negotiables" zaktualizowany (research lightly visible / jargon=comprehensibility / gender rule dropped / craft: metaphor freed; usunięty bullet research-frame exception).
4. `workflows/pipeline/03b_arc_checker.md` — **sync (ripple)**: check „jeden centralny obraz" zamieniony na „spójność obrazów" (flaguje tylko niespójność / realny zgrzyt, nie samą wielość). Bez tego arc-checker sabotowałby eksperyment, flagując dozwoloną wielość metafor.

### Niezmienne 🔒 (przeniesione z v1 bez zmian)
Ciepło/„ty", uczucia wprost, hook na otwarciu, recognition close ostatni, naturalny mówiony polski (test nadrzędny), dyscyplina liczb (R4b: bez decymali/effect-size/p-value/liczby badań), część praktyczna opcjonalna+nigdy numerowana.

### Hipotezy do walidacji na następnym drafcie (eksperyment „w którą stronę pójdzie SENSUM")
- H1: zdjęcie przymusu jednej metafory → mniej Klastra A (ukute koślawości z rozciągania jednego obrazu), więcej żywości, mniej nudy.
- H2: „badania pokazują" + odrobina mechanizmu → głębsze zrozumienie BEZ utraty ciepła (teza usera). Ryzyko: dryf w rejestr wyjaśniający, który user skrytykował u Sonneta — obserwować, czy nie przechyla za daleko.
- H3: R8 (naturalność > ozdobność) jako jedyny hamulec utrzyma przekombinowanie w ryzach mimo zdjęcia R5.

## WALIDACJA na realnym drafcie (slug 3, v2) — 2026-06-07
Metoda: `/draft` v2 na slug 3 → user docx-pass (`script_corrected.docx`) → diff maszyna vs poprawione.

**Kwantyfikacja:** podobieństwo linii 46% (przepisana >połowa) · słowa 1081→911 (−16%) · otwarcia spójnikowe Bo/A/I/Ale **38→25** (−13) · „badania" **2→0** (100% wycięte).

**Wyniki hipotez:**
- **H1 (metafora uwolniona) — POTWIERDZONA.** Cztery obrazy (deska/grunt, okładka/strony, deszcz, ból-ogień) zadziałały; arc-checker NIE flagował wielości; zniknęły koślawości Klastra A („prowadzisz na sobie konto" itp.). Mniej nudy, żywiej.
- **H2 (research lekko widzialny) — ODWRÓCONA przez usera.** User wyciął „badania pokazują" OBA RAZY, ale ZOSTAWIŁ całe wyjaśnianie mechanizmu. **Rafinacja: wyjaśniaj mechanizm TAK, powołuj się na badania NIE.** To była dobra połowa v2 (tłumaczenie pogłębia) i zła połowa (atrybucja academizuje).
- **H3 (R8 sam trzyma przekombinowanie) — CZĘŚCIOWO.** User skompresował −16%, R8 niewystarczające; przekombinowanie + konkretyzacja zostają jego sufitem (sąd, nie reguła).

**Wzorce edycji (maszyna→user):** nagłówki robocze→widzowe (7/7); „badania pokazują"→opis zjawiska (2/2); spójniki Bo/A/I cięte (−13); chrząknięcia/antytezy→prosto; abstrakt→konkret; cięcie dodatków fixera (most [A]).

**Uwaga anty-overfitting (n=1):** H2 (badania out) i spójniki SĄ skorroborowane wcześniejszą ewidencją (v1 research-invisible + liczniki tików całej sesji) → bezpieczne do kodyfikacji. Nagłówki i heurystyka kompresji są tej-jednej-skryptowe → poczekać na 2. skrypt.

## Propozycja v2.1 (do zatwierdzenia)
- **(a) R4 — „badania pokazują" z powrotem out z narracji**, ale ZOSTAJE „wolno wyjaśnić mechanizm". Brzmienie: „Wyjaśniaj mechanizm jak rzecz, którą po prostu wiesz — BEZ »badania pokazują« w narracji; atrybucja żyje w opisie Agenta 8." (rewert złej połowy v2, zachowanie dobrej).
- **(b) Nowa konkretna reguła otwarć (lever B z grilla):** „Nie otwieraj zdań pod rząd tym samym spójnikiem. Trzy »Bo«/»A«/»I« z rzędu = przepisz." → do `03a_writer.md` (źródło) + opcjonalnie [K] w section-checkerze. Policzalna = ma zęby.
- **Odłożone (n=1):** nagłówki widzowe (workflow/packaging, może zostać userowi), heurystyka kompresji zdań.

## v2.1 — ZBUDOWANE (2026-06-07, zatwierdzone przez usera)
User odrzucił „tylko dwie drobnostki" — słusznie. Główny wniosek z diffu: **maszyna systematycznie PRZEGADUJE** w 5+1 nazwanych trybach (zapowiadanie ruchu / powtórzenie abstrakt+konkret / watowanie / antyteza-rusztowanie / serie spójników / „badania pokazują"). To są te −16% słów, które user wycina ręcznie na docx. Odpowiedź: nie reguły na pisarza (Opus przegaduje z natury), tylko **zimny pass-ściskacz, który TYLKO tnie** (cut-only = zero thrashu).

**Zbudowane:**
1. `workflows/pipeline/03d_compressor.md` — **NOWY** prompt ściskacza (6 trybów cięcia + zasada zachowawcza + szew; nigdy nie dopisuje).
2. `.claude/commands/draft.md` — **Step 6.5** (ściskacz po fixerze, na końcu; backup `04_final_presqueeze.md`; raport pre/post słów). Łańcuch: pisarz → ensemble → fixer → **ściskacz**.
3. **Rewert „badania" w R4** (voice_brief + 03a_writer + CLAUDE.md destylat): „badania pokazują" out z narracji, mechanizm-wyjaśnianie ZOSTAJE.
4. **Sync CLAUDE.md**: bullet flow (3→4 agentów, ensemble+ściskacz), tabela Agent Chain (section/arc + nowy wiersz 3d), Quick Reference, single-source prompts list, file-structure linijka. Domknięty też zaległy sync ensemble (section+arc zamiast pojedynczego 03b_checker).

**Pozycja ściskacza:** NA KOŃCU (3d), bo (1) ostatni dotyk = cut-only = nic po nim nie dopisze dziwactwa, (2) pracuje na czystej odkalkowanej prozie, (3) replikuje docx-pass usera.

**Odłożone (n=1, czekać na 2. skrypt):** nagłówki widzowe (pisarz vs packaging), heurystyka kompresji jako reguła pisarza (ściskacz to subsumuje).

## Walidacja ściskacza — WYNIK (2026-06-07)
Test na maszynowym `04_final.md` slug-3 (1109 słów) → `04_final_squeezetest.md`.
- **Przebieg 1 (prompt v1):** −44 słowa (−4%). Cele ✅ (oba „badania", meta-narracja, most-restatement), zero damage. Ale za płytko — przepuścił bliźniaka abstrakt+konkret w środku akapitu i hedge „I wiesz co".
- **Tuning promptu:** mode 2 (bliźniaki w biegu + przykład), mode 3 („I wiesz co" + każda instancja), brake „o sens, nie o tłuszcz", podłoga ~10% / re-pass jeśli <5%.
- **Przebieg 2 (tuned):** −62 słowa (−5,6%). Złapał oba wcześniejsze pudła. Drobny dryf: przeformułował jedno pytanie retoryczne (lekkie wyjście poza czyste cut-only — akceptowalne).
- **Werdykt:** koncept zwalidowany — celne, bezpieczne, teraz dokładne. **5–6% to uczciwy sufit cut-only** na tym (już odkalkowanym) drafcie; reszta różnicy do usera (−18%) to **kondensacja przez rewrite** (np. „Zawaliłeś jedną drobną rzecz. Przespałeś budzik."), której cut-only z założenia NIE robi (thrash). Ta warstwa zostaje sufitem usera na docx — i dobrze. Wartość ściskacza = usuwa **powtarzalne, najbardziej irytujące tiki** (meta-narracja / „badania" / hedge), które inaczej tniesz ręcznie co skrypt.

## Open flags (pending input)
- Niezacommitowane: cała sesja (v2 doktryna + v2.1 + ściskacz 3d zbudowany i zwalidowany + slug 3 record-ready). Commit na słowo usera.
