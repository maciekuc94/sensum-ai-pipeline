# Odchudzony /draft (3 agenty): Brainstorm / Discovery Notes
Date: 2026-06-07 · Goal: zaprojektować nowy, prosty schemat pisania skryptu SENSUM — 3 agenty (pisze → sprawdza polszczyznę do md → poprawia), radykalnie chudsze zasady, dobre prompty.

## Summary / key decisions
*(running synthesis — aktualizowane po każdej odpowiedzi)*

**Ustalone wcześniej dziś (kontekst wejściowy, nie do ponownego grillowania):**
- Stary łańcuch (Drafter → 2 czytelników ↔ Integrator → bramka + `/refine` panel) jest **przekombinowany i tłumi pisanie**. Dowód: Gemini jednym czystym promptem pobił łańcuch 5 agentów; luźny pojedynczy przebieg Claude'a wyszedł lepiej niż cała machina.
- **Blind-spot potwierdzony:** ten sam model słabo łapie własne dziwne zdania. `/refine` panel i czytelnicy okazali się no-opem (zostawili nawet udokumentowaną kalkę). → agent-2 (sprawdzający) to centralny problem projektu.
- **Rozluźniona bezrodzajowość:** naturalny rodzaj męski (generyczny) OK; wymuszona neutralność = źródło sztywnych zdań. slug-1 (shippnięty) jest męskoosobowy.
- **Nazywanie uczuć dozwolone:** wstyd, wina, lęk, wyrzuty sumienia to rdzeń SENSUM, NIE żargon. Research-invisible = bez badań/liczb/nazwisk/żargonu klinicznego („kwantyfikatory", „zniekształcenie poznawcze").
- **User chce Claude, nie Gemini.** Szukamy sposobu, żeby Claude działał.
- Szkielet zadany przez usera: **3 agenty — (1) pisze, (2) sprawdza polszczyznę → feedback do md, (3) wprowadza poprawki. „I tyle."** Chudsze zasady. Dobre prompty.

**Decyzje z tego grilla:**
- **6-regułowy brief przyjęty:** (1) ciepło, do jednej osoby; (2) o uczuciach nazwanych wprost; (3) bez badań/liczb/nazwisk/żargonu klinicznego; (4) jeden centralny obraz przez całość; (5) recognition close na końcu; (6) naturalny mówiony język + naturalny rodzaj (męski generyczny OK).
- **Architektury (5 kształtów) USUNIĘTE.** User: „może to przez nie są powtórzenia". Pisarz dobiera kształt sam, per temat.
- **Permission Practice: opcjonalna + lekka.** Chce zostawić część praktyczną, ale NIE generyczną; jeśli totalnie nie pasuje → pomija.
- **Pod nóż:** reportaż-vs-esej / §2.5 tekstura, bezrodzajowość-gimnastyka (§G), 60-regułowy checklist Etapu 2 (03a), limity imperatywów / zakaz numerowanych list jako osobne reguły, banned-phrase doktryny.
- **Agent 1 (pisarz):** luźny pojedynczy przebieg; input = research + temat + 6 reguł (nic więcej); brief „pisz naturalnie jak ciepły mądry człowiek tłumaczący to drugiej osobie, nie defensywnie". Minimalny szkielet: **hook-rozpoznanie (czasem od pytania) + recognition close**, środek wolny, jeden centralny obraz. **Długość 1000–1500 słów.**
- **Agent 2 (checker polszczyzny) — replikuje warunki ZWYKŁEGO CZATU, nie /refine panel:** (a) czyta **CAŁOŚĆ naraz** (holistycznie; izolacja zdanie-po-zdaniu zabiła /refine — w izolacji każde zdanie wygląda OK), (b) framing **„to prawdopodobnie źle napisany AI-tekst — znajdź dziwne zdania"** (tryb szukania wad, nie zatwierdzania), (c) **bez „keep when in doubt"**, (d) zimny/świeży kontekst. **BEZ przykładów-kalibracji** (user odrzucił; „ani Gemini ani Opus w czacie nie dostali przykładów a wyłapali"). Output do md: cytat + czemu zgrzyta + naturalna wersja. Floated, opcjonalne/zbędne: „niech zrobi research jak dobra polszczyzna wygląda".
- **Agent 3 (fixer): surgical.** Wstawia naturalne wersje od checkera w miejsce oflagowanych zdań + lekko wygładza przejścia; **NIE przepisuje całości ani zdań nieoflagowanych** (fixer to ten sam model — całościowy rewrite ryzykuje nowe dziwne). **Jeden przebieg, bez pętli** (pisze→sprawdza→poprawia→koniec; finalną redakcję user robi na docx). „tak, sprawdzimy czy to działa".
- **Orkiestracja:** **3 zimne subagenty Opus** (pisarz / checker / fixer), każdy świeży kontekst; lead (in-session) tylko przekazuje pliki między nimi. Wszyscy zimni — także pisarz (pisze naturalnie, nie zatruty sesyjną doktryną). Zero API (subagenty Claude Code).
- **Czysty start — KASUJEMY stare (nie archiwum).** „Zacznijmy po prostu od nowa." Git trzyma historię (commit 768372d) → odwracalne. Kasujemy: prompty 03a–03e + 03_script + 03_architecture_select, narrative_architectures.md, cały /refine (refine_segment.py + refine_panel.js + refine.md + spec + plan), .claude/agents/script-reader.md, stary draft.md. Budujemy od zera: **voice_brief.md + 3 prompty + nowy /draft**.
- **Do obsłużenia przy kasacji:** style_guide.md / voice_corpus.md są referencjonowane też przez skill `native-voice-guard` i może /publish — sprawdzić i przekierować/poprawić odwołania, żeby nie zepsuć tamtego.
- **Poza zakresem (nietknięte):** research 0/1/2, /hook, /visuals, /publish, /package, align, export docx, opublikowane skrypty w outputs/.

## Q&A log

### Q1 — Nieredukowalny zestaw zasad + architektury + Permission Practice
- Asked: czy 6-regułowy brief jest właściwy; co z selektorem 5 architektur i z PP.
- Captured: 6 reguł przyjęte bez zmian. **Architektury usunięte** („może to przez nie są powtórzenia"). **PP opcjonalna i lekka** — „chciałbym zostawić jakąś część praktyczną, ale nie chcę żeby brzmiała generycznie i jeśli totalnie nie pasuje to nie chcę".
- Flags: brak.

### Q2 — Agent 1 (pisarz): input, brief, struktura, długość
- Asked: co dostaje pisarz, jak ma pisać, czy minimalny szkielet, jaka długość.
- Captured: luźny pojedynczy przebieg; input = research+temat+6 reguł; brief naturalny (nie defensywny). Szkielet: **hook-rozpoznanie — „może nawet czasami zaczynać od pytania"** + recognition close; środek wolny; jeden centralny obraz. **Długość 1000–1500 słów.**
- Flags: brak.

### Q3 — Agent 2 (checker polszczyzny): mechanizm
- Asked: kształt checkera; examples-kalibracja tak/nie; co poza „tak się nie mówi".
- Captured: **NIE dawać przykładów.** „Ani Gemini ani Opusowi w zwykłym czacie nie dawałem przykładów a wyłapali te zdania." → checker replikuje warunki czatu: **holistyczny odczyt CAŁOŚCI** (nie zdanie-po-zdaniu — izolacja zabiła /refine), framing **„to prawdopodobnie źle napisany AI-tekst, znajdź dziwne zdania"**, bez „keep when in doubt", zimny kontekst. Floated: „niech zrobi research jak dobra polszczyzna wygląda czy coś.. nie wiem" — opcjonalne, prawdopodobnie zbędne.
- Flags: brak.

### Q4 — Agent 3 (fixer) + pętla
- Asked: fixer surgical vs całościowy rewrite; pętla czy jeden przebieg.
- Captured: **surgical** (wstawia naturalne wersje + lekkie wygładzenie, bez całościowego rewrite, bez ruszania nieoflagowanych). **Jeden przebieg, bez pętli.** „tak, sprawdzimy czy to działa".
- Flags: brak.

### Q5 — Orkiestracja + model
- Asked: 3 zimne subagenty vs lead-in-loop; model.
- Captured: **3 zimne subagenty Opus** (pisarz/checker/fixer); lead tylko przekazuje pliki. Wszyscy zimni (pisarz też — pisze naturalnie). Zero API. „Tak".
- Flags: brak.

### Q6 — Gdzie żyje nowe, co znika
- Asked: nowe pliki + archiwum-vs-kasacja + command.
- Captured: **„chcę skasować stare rzeczy, zacznijmy po prostu od nowa"** — kasacja, nie archiwum (git trzyma → odwracalne). Nowe: `voice_brief.md` + 3 prompty + przepisany `/draft`.
- Flags: sprawdzić odwołania do style_guide/voice_corpus (native-voice-guard, /publish) przed kasacją.

### Q7 — „może po prostu przekombinowaliśmy" (user /btw)
- Raised: user — może nawet lean-3 to kolejne przekombinowanie.
- Captured: **zgoda.** Nieredukowalny rdzeń = **dobry prompt pisarza → jeden przebieg → ucho usera**. REWIZJA KOLEJNOŚCI: build minimal-first — **najpierw przetestować sam zimny prompt pisarza jednym przebiegiem** (warunki czatu/Gemini, ale Claude). Jeśli pisarz + edit usera wystarczy → checker/fixer NIEpotrzebne. Dodajemy checker tylko jeśli zostaje za dużo dziwnego (wtedy widać, że zarabia na miejsce). „najtańszy test to jeden przebieg, zanim cokolwiek zbudujemy."
- Flags: brak.

## Open flags (pending input)
*(brak na razie)*
