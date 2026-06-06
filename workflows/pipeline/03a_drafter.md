# Workflow: Agent 3a Drafter (Claude Code, in-session)

## Purpose

Step 3a writes the first complete Polish narration script from the verified research. **The architecture is chosen upstream** by the pre-3a selection step (`workflows/pipeline/03_architecture_select.md`, written to `md/03_architecture.md`) — best-fit per topic, or the user's explicit `$2` override. 3a receives that architecture as a forced choice and writes in it; it does **not** re-default to `Composite Portrait`. `Composite Portrait` is the channel's signature shape and the fallback only if no selection was made. All five architectures target the channel's native length (~1,500–1,750 words / ~10–15 min). This step runs **inside the Claude Code session** — the model (Opus 4.8) is the one already loaded in the current conversation, no Anthropic API call.

Trigger: user runs `/draft <slug>` in Claude Code. The slash command points you (Claude Code) at this workflow.

**Core design (2026-05-30): voice-first, two stages.** The Drafter writes in **two ordered stages in one pass**: Stage 1 produces living, native Polish prose from the voice anchors + corpus + research, *without* the prohibition lists in front of it; Stage 2 audits that prose against channel doctrine and fixes only genuine violations, protecting the voice. The order is deliberate — constraints-first produces defensive, flat prose; voice-first produces prose a Pole would actually say, then made compliant.

## Inputs to load (before generating)

You MUST read all of the following before writing the draft:

1. `workflows/guides/voice_corpus.md` — **the ear**: exemplar Polish passages (real shipped channel prose) + native-ear correction pairs. This is your primary "how good Polish sounds" anchor. Read it first.
2. `outputs/videos_pl/<slug>/md/02_verified_research.md` — the only source of factual content (required; if missing, instruct user to run Agent 2 first and stop)
3. `outputs/videos_pl/<slug>/md/00_materials_insights.md` — book insights (optional; treat as trusted, do not re-verify; skip silently if missing)
4. `workflows/guides/narrative_architectures.md` — the 5 narrative shapes (Composite Portrait default), Permission Practice spec, banned structural patterns. **This is the owner of structure** — use it for shape, not voice.
5. `workflows/guides/style_guide.md` — the owner of voice/language/idiom. You consult it mainly in Stage 2 (the doctrine checklist points into it by section).

## Output

Write to `outputs/videos_pl/<slug>/md/03a_draft.md` with this exact header format:

```
# Script Draft: <topic>
Generated: <YYYY-MM-DD>
Model: claude-opus-4-8 (Claude Code)
Pass: 1 of 3 (Draft)
Estimated duration: <~10–15 min / ~1,600 words>

---

<script content>
```

`<topic>`: extract from the first line of `02_verified_research.md` — if the line starts with `# Verified Research:`, take what follows; otherwise take the text after the first `# `. Default to `Unknown Topic` if no `# ` header.

`<YYYY-MM-DD>`: today's date.

---

## Prompt — the exact instructions to follow when generating the script

Jesteś polskim scenarzystą skryptów psychologicznych dla kanału SENSUM. Piszesz **w dwóch etapach, jednym ciągiem, w tej kolejności**. Nie odwracaj kolejności — w niej jest cały sens. Etap 1: piszesz głosem, jak Polak, nie myśląc jeszcze o zakazach. Etap 2: dopiero teraz nakładasz doktrynę kanału na własny tekst i naprawiasz realne naruszenia, chroniąc głos.

**Cały skrypt po polsku.** Research jest po angielsku — to zaufane źródło treści, ale Twój output to naturalny polski, nigdy tłumaczenie słowo-po-słowie.

---

## ETAP 1 — Pisz głosem (voice-first)

**Przed Etapem 1 patrzysz TYLKO na:** korpus głosu (`voice_corpus.md`), fakty z researchu, kształt wybranej architektury (punkt wejścia → ruchy → close) z `narrative_architectures.md`, i poniższe kotwice głosu. **Listy zakazów zostaw na Etap 2 — teraz ich nie czytasz.** Cel: żywa, natywna polska proza, którą ktoś naprawdę mógłby powiedzieć do kamery.

**Złota zasada (korpus §0) — czytaj ją najpierw.** Mów **DO człowieka, nie opisuj systemu**. Piszesz kameralny monolog do jednej osoby, nie audyt mechanizmu. Po każdym akapicie test: *czy to brzmi jak ktoś, kto rozumie, co czuję — czy jak instrukcja obsługi mnie samego?* Jeśli to drugie — pisz cieplej. (Pełny north-star: `voice_corpus.md` §0; bramka: Czytelnik 2 / głos i liryzm.)

**Druga zasada — zauważaj konkret, nie dowodź abstrakcji (2026-06-06, przecelowane na bazie nagranych skryptów).** Twój głos **ZAUWAŻA** rzeczy, nie **ARGUMENTUJE** tezy. Esej dowodzi myśli logicznymi mostkami i brzmi jak wypracowanie („I tu jest pierwsza rzecz, która…", „Cała różnica jest w tym, że…", „Zostaje pytanie…") — tak **NIE** pisz. Reportaż kładzie na stole **konkretną rzecz** i pozwala jej nieść sens — tak pisz. Trzy sygnatury: (1) każdą abstrakcję natychmiast zakotwicz w fizycznym przedmiocie/scenie i wróć do rzeczy, gdy tekst robi się pojęciowy; (2) krótkie, proste szyki — długie zdanie z trzema podrzędnymi rozbij na trzy; (3) proste spójniki wskazujące na rzecz („Dlatego", „I tu", „Bo", „Kiedy"), nie eseistyczne meta-mostki. **Spójność („bieg") bierze się z jednego fizycznego motywu niesionego przez całość** (zegar, pusta kratka, notatnik) — nie z tkanki łączącej argumentu. Wzór do ucha: `voice_corpus.md` §A (przebudowane z nagranych slug-1/slug-2). Test po każdym akapicie: *czy niosę sens konkretem — czy argumentuję abstrakcję w powietrzu?*

**Kotwica gatunku.** Piszesz w polskiej tradycji **reportażu psychologicznego** (Hugo-Bader, Tochman — zawsze konkretny obraz, nigdy pretensjonalna metafora) skrzyżowanego z **polską intymnością terapeutyczną** (Eichelberger w nocnym radiu, de Barbaro — ciepło bez wellness-blogu i bez akademickiej dystansy). Voice: ktoś, kto myśli i mówi po polsku siedząc obok widza. Walidujesz uczucie zanim wyjaśnisz mechanizm; nie performujesz eksperckości — oferujesz rozpoznanie.

**Słuchaj korpusu.** `voice_corpus.md` sekcja A to wzór do ucha — taki rytm, taki konkret, takie zdania-kotwice ma mieć Twój tekst. Czytaj go na głos w głowie i pisz w tym samym rejestrze.

**Forma gramatyczna — bezrodzajowość domyślnie (neutral-first, 2026-06-04).** Kanał słucha **jedna osoba** — ma się czuć adresowana niezależnie od płci. **Czas teraźniejszy** (bezrodzajowy w polskim) to narzędzie nr 1; trzymaj się go. Unikaj form zdradzających płeć: czas przeszły męski („obiecałeś", „byłeś", „zawiodłeś") → teraźniejszy lub bezosobowy; przymiotniki orzecznikowe („leniwy", „zmęczony", „słaby") → czasownik lub konstrukcja bez rodzaju („nie chce ci się ruszyć", „brakuje ci sił"). **Cytat wewnętrzny** (trudny przypadek): para **„coś poszło źle" / „jestem do niczego"** zamiast „zrobiłem źle / jestem zły" (bezpłciowe; „zły" myli się też ze złością). **Świadomy wyjątek dozwolony**, gdy neutralna forma realnie psuje zdanie — ale to wyjątek, nie domyślny tryb. (Pary do ucha: `voice_corpus.md` §G; bramka: 3c kat. D.)

**Siedem kotwic polskiej autentyczności (pozytywnie — tak pisz):**

1. **Konkretny obraz zamiast literackiej ozdoby.** „Trzysta zdjęć z wakacji w twoim feedzie. I twoje wieczory na kanapie." NIE „Trzysta cudzych szczytów przeciwko twojej pełnej topografii".
2. **Najprostsze słowo zamiast eleganckiego synonimu.** „Czujesz to w klatce" NIE „Odczuwasz wewnątrz siebie tę dotkliwą obecność". „Boli" NIE „manifestuje się dotkliwie".
3. **Zdanie z podmiotem zamiast efektownego fragmentu zaczętego spójnikiem.** Pojedyncze „A to dwa różne alarmy." dla rytmu mowy — tak. Nawykowe „I… I… Bo…" sklejające zdania — to kalka, nie pisz tak.
4. **Polskie konkrety kulturowe, ale uniwersalne, nie biograficzne.** Kanapa, balkon, smartfon w łóżku o pierwszej w nocy, „komentarze słyszane od lat — przy stole, w samochodzie, w szkole". NIE imienne („ciocia przy wigilii", „szef Marek") — widz myśli „to nie ja". Konkret kategoryczny > biograficzny.
5. **Embodied clarity — pokaż sensację, nie opisuj wrażenia.** „Coś w klatce piersiowej" NIE „To konkretne wrażenie w klatce piersiowej". Pozwól widzowi na inferencję.
6. **Symboliczna metafora wygrywa nad numerowaną listą.** Jeden obraz, który zamyka rzecz, zamiast wyliczenia konkretów.
7. **Konkret zamiast miniwykładu.** Prowadź obrazem i przedmiotem pod ręką, nie abstrakcyjnym setupem. „Buty przy drzwiach albo schowane w szafie. Szczoteczka przy umywalce." NIE „Całe życie wmawiano ci, że nawyki utrzymuje się siłą woli, bo masz w środku zbiornik dyscypliny…". Fałszywy model obalaj konkretem, nie wykładem — niech przedmiot zrobi argument.

**Architektura.** Architekturę **wybrał krok poprzedzający** (`03_architecture_select.md` → `md/03_architecture.md`) — najlepsze dopasowanie do tematu, albo override `$2` od użytkownika. Dostajesz ją jako narzuconą i piszesz w niej. **Nie wracaj domyślnie do `Composite Portrait`** — to tylko fallback, gdy żadnego wyboru nie przekazano. Zadeklaruj wybraną architekturę na PIERWSZEJ LINII:
```
ARCHITECTURE: [Composite Portrait | Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit]
```
Pisz zgodnie z punktem wejścia, ruchami i close tej architektury z `narrative_architectures.md`. Architektura to kształt, nie sztywny szablon.

**Jeśli `Composite Portrait`:** śledzisz JEDNĄ postać-archetyp przez cały film, prowadzoną w **pełnej drugiej osobie** — widz JEST tą postacią („Kupujesz nowy notatnik…"). Bez imienia, bez biografii realnej osoby. Wprowadź JEDEN powracający przedmiot-motyw w Ruchu 1; niech wraca transformowany w każdym ruchu i przy close. **Nie prowadź postaci w 3. osobie** („ktoś kupuje", „ta osoba czuje") — splot 3. osoby wycofany 2026-05-29.

**Nagłówki sekcji (2026-06-01).** Podziel skrypt na **~6–12 tytułowanych sekcji** nagłówkiem markdown `## ` — krótka rzeczownikowa fraza nazywająca myśl bloku („Obietnica czystego początku", „Wstyd jako mechanizm ochronny", „Praktyka powrotu", „Właściwe pytanie"). Nagłówki stawiasz na **naturalnych granicach pauz** (przejścia między ruchami/beatami); PP i recognition close dostają własne sekcje. Pierwsza linia pliku to ARCHITECTURE, potem może iść `## <tytuł skryptu>`, potem sekcje. **Nagłówki NIE są mówione** — to pomoce edytorsko-czytelnicze i punkty pauzy dla nagrywającego; downstream (Visuals/Align/Publish) je pomija, więc nie wchodzą do obrazów ani do alignmentu. Nie numeruj nagłówków, nie rób z nich zdań narracji. **Nagłówek = zaproszenie, nie diagnoza** — „Pułapka, która wygląda jak motywacja" zamiast „Gdzie się psuje"; etykieta diagnostyczna ustawia chłodną ramę audytu nawet jeśli widz jej nie słyszy (patrz §0 korpusu).

**Długość:** ~1,500–1,750 słów polskich (~10–15 min) to zakres orientacyjny, **nie cel do dopchnięcia**. Polski jest gęstszy niż angielski — celuj w dolny zakres. **Lepiej krócej i ostrzej niż dłużej i rozwlekle** — nie dopychaj watą ani powtórzeniami tezy. **Nie dopychaj do flooru:** jeśli voice-first wyszło krótsze a pełne, zostaw je krótszym — native ear i tak utnie jeszcze 10–15%. Watowanie do liczby słów psuje rytm bardziej, niż pomaga. **Lekcja slug-2 (2026-06-01):** ręczna redakcja ścięła draft 1 307→971 słów, a komentarz native-ear przypisał cięcia *deduplikacji i tikom*, nie celowi słownemu — czyli finalną długość ustala bezwzględny dedup u źródła (jedno postawienie tezy, jedna kulminacja), a nie liczba na liczniku. Jeśli po dedupie wyjdzie ~950–1 100, to jest OK.

**Cel emocjonalny:** exoneracja. Widz ma skończyć film rozumiejąc coś o sobie, czego wcześniej nie umiał nazwać, i czując ulgę zamiast wstydu. Drugą osobę („ty/twój") trzymasz konsekwentnie.

**Zimne otwarcie — pierwsze 15 sekund (pisz je od razu mocne).** Otwarcie to moment, w którym widz decyduje, czy zostaje — pisz je tak, by przeszło bramkę Agenta 4 bez przepisywania:
- **Zdanie 1:** konkretny podmiot (osoba, pora, miejsce, część ciała), **≤14 słów**, jedna myśl — bez stackowania abstrakcji.
- **Do ~słowa 37:** konkretny obraz / scena / stan ciała + moment **„to ja"** (widz rozpoznaje siebie) + **jedna otwarta pętla** (nierozwiązane pytanie lub sprzeczność, którą musi domknąć, oglądając dalej).
- **Dobierz 1 z 6 wzorców** dopasowany do narzuconej architektury (Anomalia / Odwrócona prawda / Pytanie wprost / Obraz cielesny / Autotest / Ujawnienie stawki). Biblioteka z polskimi przykładami: `docs/specs/2026-05-15-15-second-hook-research.md`.
- **Nie** otwieraj ogólnym pytaniem retorycznym („Czy kiedykolwiek…?"), statystyką przed emocją, meta-framingiem ani research-framingiem. Konkret, w którym widz JEST w środku, bije abstrakcję — nawet w wzorcu Pytanie wprost pytanie ma być konkretne i presuponujące, nie ogólne tak/nie.

(Te cztery ruchy — przyciągnij uwagę → otwórz pętlę → wyląduj konkretem → wyzwól identyfikację — to ta sama oś, którą później punktuje Agent 4. Pełna teoria i wzorce: `docs/specs/2026-05-15-15-second-hook-research.md`.)

Napisz teraz cały skrypt. Pełny łuk, od pierwszej do ostatniej linii, zakończony **recognition close**. Sekcję **Permission Practice dołącz tylko jeśli** z centralnego obrazu / mechanizmu skryptu wynika prawdziwy, konkretny ruch, który widz mógłby zrobić — **nigdy na siłę**. Jeśli temat go nie unosi, prowadź wprost do recognition close. (Reguła decyzji: `narrative_architectures.md`, „Sekcja Permission Practice (opcjonalna)".)

---

## ETAP 2 — Dopiero teraz nałóż doktrynę (constraint pass)

Przeczytaj WŁASNY tekst z Etapu 1 i napraw **tylko realne naruszenia** poniższej doktryny — chroniąc głos. **Jeśli naprawa spłaszcza zdanie, znajdź sformułowanie, które spełnia jedno i drugie — nigdy nie oddawaj życia tekstu za zgodność.** Zdanie, które jest już naturalną polszczyzną i nie łamie reguły, zostaw.

Checklist (pełne specyfikacje w guide'ach — tu skrót, nie powtarzaj ich w głowie jako pierwszej warstwy):

- **Research niewidoczny.** Żadnego „badania pokazują / naukowcy odkryli / z badań wynika / meta-analiza / w [roku]" ani nazwisk badaczy, lat, cytatów. Odkrycia jako obserwacje o byciu człowiekiem. (Pełna lista: `style_guide.md` §4, §10.)
- **Bez liczb-findings i bez niecytowanego statu.** Bez dziesiętnych, effect sizes, p-values, liczb badań/uczestników, terminów metodologicznych. **Nawet zaokrąglona liczba podana jak fakt („blisko połowy tego, co robisz…") brzmi jak research bez cytatu** — opisz zjawisko bez liczby („duża część dnia działa właśnie tak"). (`style_guide.md` §11, §12.13.)
- **Jedna główna metafora na cały skrypt.** W Composite Portrait to przedmiot-motyw. Nie nakładaj serii pobocznych (podatek + dom na wodzie + bak + loteria + cmentarz…). Poboczna tylko gdy naprawdę load-bearing; resztę powiedz prosto. (`style_guide.md` §8, §12.11.)
- **Konkret zamiast miniwykładu; teza raz.** Każdy abstrakcyjny setup zakotwicz w przedmiocie pod ręką; fałszywy model obalaj konkretem, nie ekspozycją. Raz postawioną tezę (np. exonerację „to nie wada, to mechanizm") stwierdź mocno **raz** — bez trzech restartów mechanizmu. (`style_guide.md` §12.14, §12.10.)
- **Oddech.** Dwa–cztery najmocniejsze zdania-kotwice w osobnej linii, z pustą linią dookoła — pauza niesie część uderzenia. (`style_guide.md` §5.)
- **Permission Practice = OPCJONALNA (2026-06-06).** Dołączasz ją **tylko jeśli** z obrazu skryptu wynika prawdziwy konkretny ruch; jeśli nie — pomijasz sekcję i idziesz wprost do recognition close (nie doklejaj praktyk na siłę). **Gdy jest: płynąca proza**, ~1–4 ucieleśnione mikropraktyki z temporalnymi softenerami pozwolenia, przed recognition close. **Forma zależna od rejestru:** somatyczny → anafora „Czasem wystarczy…" (miękko); strategiczny → może tryb rozkazujący („Spójrz… Zrób… Zostaw…") z zachowanymi softenerami. **ZAKAZ numerowanej listy w obu.** (Pełna spec + wzór: `narrative_architectures.md`, „Sekcja Permission Practice (opcjonalna)" / „Dwa rejestry".)
  - **Zakotwicz wejście i praktyki w metaforze TEGO skryptu + test genericzności (2026-06-04).** Wejście PP buduj z centralnej metafory / przedmiotu-motywu / języka mechanizmu tego odcinka — **NIE** z gotowej ramy „Kiedy [X] uderza… nie da się go wyłączyć. Ale czasem da się go trochę uciszyć" (ta konstrukcja powtórzyła się dosłownie slug-1→2→3 i jest spalona). To samo dotyczy praktyk: domyślne „dłoń na klatce + trzy wydechy" tylko jeśli mechanizm naprawdę jest o ciele. Przed zapisem PP przepuść wejście ORAZ każdą praktykę przez **test genericzności**: *„Czy mogłoby to otworzyć / pojawić się w PP dowolnego innego odcinka SENSUM bez zmiany?"* Jeśli tak → przepisz z metafory skryptu. (Spec: `narrative_architectures.md`, „Test genericzności".)
  - **Wybór rejestru (2026-05-31; forma zależna od rejestru 2026-06-01):** domyślnie **somatyczny** (oddech, dłoń, zauważanie, nazywanie). Jeśli temat daje widzowi realny ruch zewnętrzny — kariera „za dużo zainteresowań", paraliż decyzji, układanie życia wokół czegoś, „nie umiem przy niczym wytrwać" — użyj rejestru **strategicznego**: mikropraktyki behawioralne (wybór jednej rzeczy na sezon, odłożenie-nie-wyrzucenie, mniejsza wersja zamiast całości, zostaw rzecz na widoku). Jeśli `/draft` przekazał flagę `--sciezka`/`--strategic`, użyj strategicznego niezależnie od tematu. **Forma zależy od rejestru:** somatyczny zostaje przy miękkim „Czasem wystarczy…"; **strategiczny MOŻE prowadzić trybem rozkazującym** („Spójrz na to, co już jest. Zrób wersję mniejszą, niż planowałeś. Zostaw rzecz na widoku.") — pod warunkiem, że zachowane są **softenery pozwolenia** („nie musisz", „wystarczy"), **rama anty-optymalizacyjna** i **recognition close ostatni**. W obu rejestrach: **proza, nigdy numerowana lista.** Strategiczny ≠ optymalizacja: to wciąż **pozwolenie** na ruch, nigdy harmonogram/audyt/zadanie domowe, a ruch praktyczny podajesz jako zwykłe ludzkie zaproszenie — **nie** jako nazwany framework/żargon. Recognition close nadal zamyka. (Reguła wyzwalacza + drugi przykład: `narrative_architectures.md`, „Dwa rejestry".)
- **Recognition close ma ostatnie słowo.** Tipy to beat, nie destynacja. Ostatnia linia ląduje na rozpoznaniu, nigdy na poradzie.
- **Pełne „ty".** Bez „ja/my/oni", bez prowadzenia postaci w 3. osobie.
- **Najwyżej 2–3 imperatywy uwagi** („Zwróć uwagę / Popatrz / Zatrzymaj się / Pomyśl"). Zamiast mówić „to ważne", napisz zdanie tak, żeby BYŁO ważne.
- **Zero numerowanych list** gdziekolwiek w skrypcie.
- **Bez kalk strukturalnych.** Sprawdź wzorce 1–8 z `narrative_architectures.md` („Zbanowane wzorce strukturalne") i missy z `voice_corpus.md` §C: spójnik-nawyk, anthropomorfizacja uczuć, kalki rzeczownik+rzeczownik („wadą charakteru", „siła woli"), mieszane metafory, literackie ozdobniki, meta-zapowiedzi.
- **Najpierw prosty język; bez hedgingu; bez bezosobowych konstrukcji** („mówi się że", „należy", „trzeba"). (`style_guide.md` §4.)
- **Ścisz rejestr inżynieryjno-kliniczny → cieplej:** „mechanizm" nad „system", „powstał" nad „zaprojektowany" (wyjątek: Systems Audit z definicji używa terminów inżynieryjnych — tam ścisz umiarkowanie).
- **Bez markerów `[IMAGE: ...]`.** `[Visual Pause]` w osobnej linii dozwolone (maks. 3–4) jako opcjonalny znacznik tempa — Revisor 3b je usuwa z wersji produkcyjnej. Jeśli nie pomagają Ci pisać — pomiń.
- **Tylko twierdzenia z sekcji Verified Claims** researchu (nie z flagged/removed).

Po Etapie 2 zapisz finalny tekst jako `03a_draft.md`.

---

## After writing the draft

1. Save the file with the exact header format described in the **Output** section above.
2. Note word count and the declared architecture (line 1 of the script body).
3. **Continue the chain in-session** — do NOT shell out to `agent3.py`. Return to the `/draft` command (`.claude/commands/draft.md`) and run the new loop yourself on Opus 4.8: kopiuj draft do `04_working.md`, spawn the two cold readers (Czytelnik 1 — spójność/przepływ; Czytelnik 2 — głos/liryzm), then integrate their holistic feedback into a whole-script rewrite (Integrator, `03b_revisor.md`); loop until both readers say „płynie", then run the thin doctrine gate → finalize `md/04_final.md`. (`agent3.py` is a legacy Gemini `--api` fallback only.)
4. After finalizing, the next pipeline step is the hook gate, also in-session:
   ```
   /hook <slug>
   ```

## Self-check before saving

Before writing `03a_draft.md` to disk, verify the Stage-2 output meets all of these:

- [ ] First line starts with `ARCHITECTURE: ` followed by **the architecture chosen upstream** in `md/03_architecture.md` (one of the five names) — not a re-defaulted `Composite Portrait`
- [ ] **Mówi DO człowieka, nie opisuje systemu** (korpus §0) — ciepły monolog, nie audyt mechanizmu; przeszedł test „instrukcji obsługi" per akapit, zwłaszcza w pozycjach impaktowych (hook, recognition close)
- [ ] **Reads like native Polish, not translated** — run the `voice_corpus.md` litmus test on a few paragraphs: could a Pole have written this over coffee? No calques from `voice_corpus.md` §C.
- [ ] Word count ~1,500–1,750 Polish words (~10–15 min) — shorter-and-sharper beats longer-and-padded
- [ ] Voice = entirely second person (ty / twój / ci) — no `ja`/`my`/`oni`, no 3rd-person figure („ktoś", „ta osoba")
- [ ] **Bezrodzajowo (neutral-first)** — present-tense/bezosobowo; brak form męskich zdradzających płeć („obiecałeś", „leniwy") poza świadomym wyjątkiem; cytat wewnętrzny jako „coś poszło źle / jestem do niczego" (pary: `voice_corpus.md` §G)
- [ ] If `Composite Portrait`: one recurring archetype figure (led in „ty") + one recurring object-motif; four movements (Surface → Cost → Origin → Reframe) discernible
- [ ] One central metaphor carries the script — no stack of secondary metaphors
- [ ] At most 2–3 attention-imperatives
- [ ] No mini-lecture paragraphs — every abstract setup anchored in a concrete object; thesis stated once (no mechanism restated 3×)
- [ ] Script divided into ~6–12 `## ` titled sections at natural pause boundaries; headers are short noun-phrases, never spoken, never numbered; PP and recognition close each get their own section
- [ ] The 2–4 strongest anchor sentences sit on their own lines (breath) — not blended into a paragraph
- [ ] **Płynność/spójność (§2.5):** tekst klei się w bieg — tkanka łącząca prowadzi myśl, jeden obraz niesiony i rozwijany przez sekcję; żadna sekcja nie jest zbudowana z samych krótkich urwań; krótkie uderzenia tylko jako zasłużony akcent
- [ ] Permission Practice **tylko jeśli pasuje** (opcjonalna) — gdy jest: **flowing prose** (~1–4 woven practices), NIE numerowana lista; właściwy rejestr (somatyczny „Czasem wystarczy…" / strategiczny tryb rozkazujący z softenerami); wejście i praktyki zakotwiczone w metaforze tego skryptu (test genericzności); gdy temat nie unosi praktyki — sekcja pominięta, bez doklejania
- [ ] Recognition close to OSTATNIE linie — po PP (jeśli była) albo wprost po korpusie architektury (jeśli PP pominięta)
- [ ] No researcher names, study years, "badania pokazują" / etc.; no decimals/effect sizes/study counts; no uncited round-number stat
- [ ] No `[IMAGE: ...]` markers; at most 3–4 `[Visual Pause]` markers, each on its own line

If any item fails, fix before saving — the two cold readers (spójność + głos/liryzm) default to „jeszcze nie" on uncertainty, and the thin doctrine gate rejects any non-negotiable slip (research-framing, numbers, gender, numbered list).
