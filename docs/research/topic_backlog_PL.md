# Backlog tematów SENSUM — ranking niszy A∩B∩C

> Synteza i ranking 40 kandydatów dla polskiego kanału `@sensumpolska`. Metoda: model **A∩B∩C** (A = udowodniony globalny evergreen pull; B rozszczepione na **B-popyt** = werbalizowany polski popyt z kotwicą wielkości × **B-podaż** = słabość/rzadkość polskiej podaży; C = SENSUM-fit głosu i architektury). Wszystkie sygnały **darmowe i triangulowane** — yt-dlp (realne `view_count`) + Google/YouTube autocomplete PL; żaden pojedynczy sygnał nie podnosi wyniku sam. Lista przeszła pełny scoring koniunkcyjny (bramka: każda noga ≥2), a następnie **adwersarialną weryfikację** dwóch niezależnych recenzentów wprost wobec `topic_signals.json` i rubryki `niche_research_design_PL.md`.
>
> **ZŁOTO = A=3 ∧ B-popyt=3 ∧ B-podaż=3 ∧ C≥2** (czysta luka). **SREBRO** = przeszedł bramkę, ale luka tylko jakościowa, register-served albo C wymaga przeramowania. Suma A+B-popyt+B-podaż+C podana jako pomocniczy ordinale — realnym rankerem są leksykograficzne tie-breaki (B-podaż → B-popyt → C). Pozycje z flagą pułapki (`bilingual-served` / `repeat` / `dwujęzyczni`) wyniesione do osobnej sekcji, poza ranking produkcyjny.

## Co zmieniła weryfikacja adwersarialna (wchłonięte korekty)

- **Klaster anhedonii rozplątany.** Cztery tematy odrętwienia (10/24/31/39) wisiały na tym samym zestawie kotwic EN (HealthyGamer 735K / Kati Morton 610K / Eilers 348K). idx 39 („przestałeś się ekscytować") i idx 31 („nic nie czujesz") ciągnęły z **tego samego** klastra Z3 i tych samych kotwic — jedna żyła popytu nie może podpierać dwóch ZŁOT. **idx 39 → flaga `repeat`** wobec idx 31 (rozróżnienie „pragnienie vs radość" to dokładnie free-text-furtka, którą doktryna anti-repeat odrzuca). **idx 31 → SREBRO** z flagą `bilingual-served`: anhedonia jest obsłużona po polsku przez **dubbingowane** eseje kliniczne 348–735K; doktryna nakazuje przy register-ambiwalencji domyślnie SREBRO. Pozostają **dwa** złota odrętwienia: idx 10 (okazywać uczuć — podaż off-angle, porada o partnerze) i idx 24 (płakać — najostrzejszy objaw, podaż to piosenka + mikro-eseje).
- **Reguła „szum-podaży ≠ kotwica-popytu".** Pozycji, której dużą liczbę odsiewamy jako muzykę dla B-podaży, **nie wolno** używać jako kotwicy wielkości dla B-popytu. To zbiło **idx 33** („mijają lata"): jedyne ≥50k to piosenki (Perfect 80M itd.), brak nie-muzycznego eseju ≥50k na percepcję czasu → **B-popyt 3→2, ZŁOTO→SREBRO**; dodatkowo C 3→2 (egzystencjalna percepcja czasu słabiej trafia w rdzeń C „bycie-zauważonym" niż rany childhood/wstyd).
- **idx 6 („wstydzisz się siebie") → SREBRO.** Po odsianiu teledysku 246K (Langusta/Musiał — piosenka) zostaje realny SENSUM-adjacentny esej (Jola Szymańska 20K, Brené Brown) → **B-podaż 3→2** (luka jakościowa, nie czysta). Dodatkowo `repeat-risk`: objaw-powierzchniowy „chroniczny wstyd za siebie" mocno zachodzi na istniejący „wstyd za własne życie" — rozróżnia tylko niuans metafory. Kotwica 512K („Dlaczego odczuwamy wstyd?") nie występuje w datasetcie → **wymaga ręcznej weryfikacji z UI** (Z3 „wstydzę się siebie", related=10, niezależnie trzyma B-popyt=3).
- **idx 22 („stanę się matką") → HOLD ZŁOTO** (najbardziej obronne złoto, benchmark reguły muzycznej). 601K to teledysk (Adult Contemporary), po odsianiu pole cienkie (Natalia Tur 11765 typologia, ≤2/5). Bilingual-concern (najsilniejszy EN-evergreen + szukana KSIĄŻKA w autocomplete) realny, ale brak polskiej podaży z trakcją na kąt → flaga tylko jako **manualny check Trends PL-vs-EN przed produkcją**, nie zmiana tieru.
- **Kalibracja B-popytu (idx 1 jako wzorzec).** related=1 + jeden literalny sample + kotwica tylko kategoryjna = B-popyt 2. Zastosowane spójnie: idx 39 → 2. idx 31 utrzymuje B-popyt=3, bo jego sample „dlaczego nic mnie nie cieszy" stoi na czele **bogatego, nie-somatycznego** klastra Z3 (cieszy/interesuje/obchodzi/śmieszy) — w przeciwieństwie do somatycznie skażonych klastrów idx 1/39.
- **idx 9 („mur/odpychasz")** — demand_sugg_total=4 graniczne, ale 3 zgodne on-angle samples → B-popyt=2 utrzymane; **przed produkcją reseed** („dlaczego odpycham bliskich", „uciekam gdy ktoś się zbliża").

---

## Rekomendowane pierwsze 5 (produkcja teraz)

Trzy ZŁOTA + dwa najmocniejsze SREBRA o czystej podaży (B-podaż=3) i różnych objawach/architekturach (anti-repeat + różnorodność architektur jako tie-break). Klaster odrętwienia świadomie ograniczony do **jednego** z dwóch złot odrętwienia w pierwszej piątce (idx 24), by nie kanibalizować widza serią pod rząd.

### 1. „Boję się, że stanę się swoją matką (albo swoim ojcem)" — ZŁOTO (idx 22, suma 12)
**Archetyp:** becoming-the-parent-you-feared. **Architektura:** Composite Portrait.
**Dlaczego:** Najmocniejszy evergreen w całym lane (Crappy Childhood Fairy / Teahan / HealthyGamer, flagowce 500k+). B-popyt=3 wzorcowy: demand_sugg_related=21, „boję się że będę jak matka" w wielu wariantach Z3, w tym jako **szukana książka** („…książka", „…empik") — twardy dowód natywnej werbalizacji bólu. B-podaż=3: jedyny 100k+ (601K) to teledysk Matyldy/Łukasiewicz, po odsianiu pole puste (typologia 11K). Idealnie trafia w hipotezę widowni (45+, kobiety, cluster rodzinny — tie-break 6). *Manualnie sprawdź Trends „jak nie być jak matka" PL-vs-EN przed nagraniem.*
**Zalążek hooka:** „Łapiesz się na geście, na tonie głosu — na czymś, czego przysięgłaś sobie nigdy nie powtórzyć. I przez sekundę w lustrze widzisz nie siebie, tylko osobę, przed którą całe życie uciekałaś."

### 2. „Nie umiesz płakać, choć bardzo byś chciał" — ZŁOTO (idx 24, suma 12)
**Archetyp:** frozen-feeling / emocjonalne odrętwienie z dzieciństwa. **Architektura:** Forensic Case Study.
**Dlaczego:** Udowodniony wielokanałowy evergreen odrętwienia (HealthyGamer 735K, Morton 610K, Eilers 348K). B-popyt=3: „dlaczego nie potrafię płakać" to druga podpowiedź bogatego klastra „nie potrafię…" (Z3 l.124-134, related=10). B-podaż=3: jedyny 100k+ to **piosenka** „Pozwól mi płakać" 223K (szum), realne eseje mikroskopijne (Tandem 11K, CICHE RANY 106) — czysta luka. Najostrzejszy, najbardziej rozpoznawalny objaw z całego klastra odrętwienia.
**Zalążek hooka:** „Coś w tobie zamknęło się dawno temu. Patrzysz na własny smutek jakby zza szyby — widzisz go, a nie możesz dosięgnąć; jakby płacz był pozwoleniem, którego nigdy ci nie wydano."

### 3. „Dlaczego nie umiesz okazywać uczuć — nawet tym, których kochasz" — ZŁOTO (idx 10, suma 12)
**Archetyp:** emotional inexpressiveness / wyuczona czujność. **Architektura:** Forensic Case Study.
**Dlaczego:** Evergreen (Teahan/HealthyGamer, alexytymia/numbness). B-popyt=3: „dlaczego nie potrafię okazywać uczuć" **dosłownie** w demand_samples (Z3, related=10). B-podaż=3 — najczystsza luka w zestawie: wszystkie 5 on-topic to **porada relacyjna obwiniająca partnera** („dziewczyna nie okazuje uczuć", „jak zdobyć kobietę", max 17K), ZERO ciepłego pierwszoosobowego rozpoznania. Różny objaw (twarz zastyga / słowa nie wychodzą) od idx 24 (smutek-zza-szyby) — produkować z wyraźnie inną metaforą centralną.
**Zalążek hooka:** „Czujesz mnóstwo — naprawdę. Ale w chwili, gdy trzeba to pokazać, twarz zastyga, a słowa zostają w gardle. To nie chłód. To coś, czego nauczyłeś się dawno temu: że pokazać uczucie znaczy zaryzykować."

### 4. „Twoje życie nie zatrzymało się nagle — osuwało się tak wolno, że tego nie zauważyłeś" — SREBRO (idx 19, suma 11)
**Archetyp:** slow-drift stagnation / niewidzialne utknięcie. **Architektura:** Forensic Case Study.
**Dlaczego:** Najmocniejsze SREBRO blisko złota — A/B-podaż/C wszystkie 3, jedyny hamulec to cieńsza werbalizacja frazy (B-popyt=2). „Powolny dryf" to flagowy egzystencjalny lane (Einzelgänger, PoW). B-podaż=3 wzorcowa: supply_ontopic_n=0 przy realnym popycie („czuję że przegrałem życie" w Z3 + „jak nie odkładać życia na jutro" 235K jako kotwica). Inny objaw/metafora niż „wstyd za własne życie" — nie repeat.
**Zalążek hooka:** „To nie był jeden dramatyczny dzień. Twoje życie osuwało się po cichu — suma tysiąca małych „jutro", których nikt nie zauważył. Łącznie z tobą."

### 5. „Wciąż starasz się zasłużyć na miłość, której nigdy nie dostałeś za darmo" — SREBRO (idx 26, suma 11)
**Archetyp:** earning-love / nigdy-niewygrana walka o uznanie rodzica. **Architektura:** Systems Audit.
**Dlaczego:** Flagowy archetyp rany dzieciństwa (Teahan, HealthyGamer, conditional love). B-podaż=3: jedyny 100k+ to **piosenka** „Nie muszę być idealna" 390K (szum), realne eseje mikro (560/52/14) — czysta luka. B-popyt=2 (fraza-ból literalna/cieńsza, kotwica pośrednia) trzyma poniżej złota. Inny objaw (zarabianie pracą) niż idx 29 (czekanie na słowo) — nie repeat; Systems Audit różnicuje architekturę względem trzech Composite/Forensic powyżej.
**Zalążek hooka:** „Pracujesz, osiągasz, dajesz z siebie wszystko — a w środku wciąż słychać to samo: że to nie wystarcza. Bo gonisz uznanie kogoś, kto już dawno przestał patrzeć."

---

## Pełny ranking

> Pozycje z flagą pułapki (idx 31 `bilingual-served`, idx 6 `repeat-risk`) ujęte w rankingu z oznaczeniem, ale **poza produkcją** — szczegóły w sekcji „Pułapki / odrzucone". Sortowanie: ZŁOTO → suma malejąco → tie-breaki (B-podaż, B-popyt, C).

| # | Temat (PL, język bólu) | Archetyp | A | B_pop | B_pod | C | Suma | ZŁOTO | Architektura | Werdykt |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Boję się, że stanę się swoją matką (albo swoim ojcem) | becoming-the-parent | 3 | 3 | 3 | 3 | 12 | ✅ | Composite Portrait | ZŁOTO — bogaty natywny popyt (nawet szukana książka), 601K to teledysk; *manual bilingual-check* |
| 2 | Nie umiesz płakać, choć bardzo byś chciał | frozen-feeling / numbness | 3 | 3 | 3 | 3 | 12 | ✅ | Forensic Case Study | ZŁOTO — evergreen odrętwienia, podaż to piosenka + mikro-eseje |
| 3 | Dlaczego nie umiesz okazywać uczuć — nawet tym, których kochasz | emotional inexpressiveness | 3 | 3 | 3 | 3 | 12 | ✅ | Forensic Case Study | ZŁOTO — dosłowny popyt z Z3, cała podaż off-angle (porada o partnerze) |
| 4 | Twoje życie nie zatrzymało się nagle — osuwało się tak wolno | slow-drift stagnation | 3 | 2 | 3 | 3 | 11 | — | Forensic Case Study | SREBRO mocne — pusta podaż, hamulec to cieńsza werbalizacja frazy |
| 5 | Boisz się, że twoje życie już się nie zmieni | quiet resignation | 3 | 2 | 3 | 3 | 11 | — | Historical Reversal | SREBRO — pusta podaż na kąt (1M to off-topic hazard), B-popyt=2 |
| 6 | Patrzysz na siebie i czujesz, że marnujesz swój potencjał | wasted potential | 3 | 2 | 3 | 3 | 11 | — | Forensic Case Study | SREBRO — 9 filmów ale wszystkie clickbait-optymalizacja (max 39K), czysta luka jakościowa |
| 7 | Mur, który miał cię chronić — odpychasz ludzi, których chcesz blisko | avoidant push-pull | 3 | 2 | 3 | 3 | 11 | — | Systems Audit | SREBRO — pusta podaż; popyt cienki (total=4), reseed przed produkcją |
| 8 | Dlaczego trzymasz wszystkich na dystans — i nazywasz to niezależnością | counter-dependence | 3 | 2 | 3 | 3 | 11 | — | Historical Reversal | SREBRO — pusta on-topic podaż, kąt o krok od Z3; różny od #7 |
| 9 | Dlaczego nie potrafisz po prostu przyjąć, że ktoś cię kocha | cant-accept-love | 3 | 2 | 3 | 3 | 11 | — | Socratic Challenge | SREBRO — kąt przyjmowania miłości pusty, fraza o krok od Z3 |
| 10 | Ciągle przepraszasz za to, że w ogóle jesteś | self-erasure | 3 | 2 | 3 | 3 | 11 | — | Composite Portrait | SREBRO blisko złota — czysta luka (100k+ to piosenki), popyt zdławiony somatycznym seedem |
| 11 | Wstydzisz się tego, skąd jesteś — domu, rodziny, dzieciństwa | origin-shame | 3 | 2 | 3 | 3 | 11 | — | Composite Portrait | SREBRO — mocne A, czysta luka, dokładny kąt origin-shame niedoprecyzowany w AC |
| 12 | Wciąż starasz się zasłużyć na miłość, której nigdy nie dostałeś za darmo | earning-love | 3 | 2 | 3 | 3 | 11 | — | Systems Audit | SREBRO — flagowy archetyp, czysta luka; kotwica wielkości to piosenka |
| 13 | Boisz się mieć dziecko, żeby nie skrzywdzić go tak, jak ciebie skrzywdzono | breaking-the-cycle | 3 | 2 | 3 | 3 | 11 | — | Composite Portrait | SREBRO — pusta podaż; klaster „boję się" zdominowany health-anxiety |
| 14 | Dlaczego czujesz się niepotrzebny, choć nikt cię nie odrzucił | feeling worthless | 3 | 2 | 3 | 3 | 11 | — | Composite Portrait | SREBRO — popyt realny w Z3, bez pełnej kotwicy wielkości na kąt |
| 15 | Dlaczego nie potrafisz kochać — chociaż bardzo chcesz | blocked attachment | 3 | 3 | 2 | 3 | 11 | — | Socratic Challenge | SREBRO — twardy popyt, ale 206K inkumbent (Langusta) cofa B-podaż do luki jakościowej |
| 16 | Samotny w pełnym pokoju — najbardziej sam wśród ludzi | loneliness alone-in-crowd | 3 | 3 | 2 | 3 | 11 | — | Composite Portrait | SREBRO — 9 on-topic + sąsiad 111K (JASNA STRONA); dzieli objaw z #17 |
| 17 | Tłumacz, który nigdy nie odpoczywa — samotny, choć ciągle z ludźmi | people-pleasing loneliness | 3 | 3 | 2 | 3 | 11 | — | Composite Portrait | SREBRO — generyczny inkumbent 111K; różny od #16 (maska vs tłum), produkować rozłącznie |
| 18 | Nie jesteś leniwy — po prostu nie masz już z czego czerpać | depletion not defect | 3 | 3 | 2 | 3 | 11 | — | Composite Portrait | SREBRO — twardy popyt (kotwica 233K), ten sam 233K inkumbent (Trojanowski) cofa B-podaż |
| 19 | Wstajesz rano i nie wiesz, po co | loss of meaning | 3 | 3 | 2 | 3 | 11 | — | Socratic Challenge | SREBRO — popyt mocny, duża podaż na „sens życia" (Sasana 436K) kapuje lukę do jakościowej |
| 20 | Dlaczego cudza pochwała spływa po tobie, a krytyka zostaje na tygodnie | negativity bias | 2 | 2 | 3 | 3 | 10 | — | Systems Audit | SREBRO — A=2 (mid-tier evergreen), solidna luka na wąskim, realnym objawie |
| 21 | Mijają lata, a ty czujesz, że ich nie przeżyłeś | unremembered years | 3 | 2 | 3 | 2 | 10 | — | Socratic Challenge | SREBRO (korekta z ZŁOTA) — kotwica popytu to muzyka (nie liczy się), C cofnięte do 2 (percepcja czasu) |
| 22 | Ciągle czekasz, aż rodzic wreszcie powie „jestem z ciebie dumny" | waiting child | 3 | 2 | 2 | 3 | 10 | — | Historical Reversal | SREBRO — flagowy archetyp + mocna kotwica, ale pole rodzicielskie szeroko zajęte |
| 23 | Dlaczego czekasz, aż będziesz gotowy, zanim pozwolisz sobie zacząć | chronic unreadiness | 3 | 2 | 2 | 3 | 10 | — | Socratic Challenge | SREBRO — 7 słabych on-topic = tylko luka jakościowa, B-popyt=2 |
| 24 | Czekasz na dzień, w którym wreszcie ci się zachce — a on nie przychodzi | waiting-for-motivation | 3 | 2 | 2 | 3 | 10 | — | Historical Reversal | SREBRO — mocne A/C, fraza-popyt cienka, przyległa nisza motywacji ma 233k gracza |
| 25 | Czekasz, aż życie się w końcu zacznie | deferred life | 3 | 2 | 2 | 3 | 10 | — | Composite Portrait | SREBRO — luka tylko jakościowa (16 słabych filmów), B-popyt umiarkowany |
| 26 | Dlaczego rano już jesteś zmęczony tym, czego jeszcze nie zacząłeś | anticipatory fatigue | 2 | 2 | 3 | 2 | 9 | — | Forensic Case Study | SREBRO — realny gap, ale popyt skażony somatyką i A mid-tier |
| 27 | Stoisz w miejscu — każda droga oznacza stratę reszty | decision-paralysis | 2 | 2 | 3 | 2 | 9 | — | Socratic Challenge | SREBRO — czysta luka, ale A mid-tier i C wymaga obrony przed ramą poradnika kariery |
| 28 | Im dłużej zwlekasz, tym trudniej zacząć — i wiesz o tym | shame-procrastination loop | 2 | 2 | 2 | 2 | 8 | — | Systems Audit | SREBRO graniczne — seed mocno zaszumiony, A i B-podaż mid-tier |
| 29 | Nie odpoczywasz, kiedy odpoczywasz | guilty-rest | 2 | 2 | 2 | 2 | 8 | — | Forensic Case Study | SREBRO najsłabsze — popyt prawie somatyczny, podaż zatłoczona zdrowiem/snem |

**Z flagą pułapki (przeszły bramkę arytmetycznie, wyniesione poza ranking produkcyjny):**

| Temat | Archetyp | A | B_pop | B_pod | C | Suma | Flaga | Werdykt |
|---|---|---|---|---|---|---|---|---|
| Robisz wszystko jak należy, a w środku nic nie czujesz (idx 31) | anhedonia jako ochrona | 3 | 3 | 2 | 3 | 11 | `bilingual-served` | SREBRO — anhedonia obsłużona po polsku dubbingiem klinicznym 348–735K (inny rejestr → ambiwalencja → SREBRO); B-podaż cap 2 |
| Dlaczego wstydzisz się samego siebie, choć nikt cię nie ocenia (idx 6) | core shame | 3 | 3 | 2 | 3 | 11 | `repeat-risk` | SREBRO — objaw zachodzi na „wstyd za własne życie"; realny esej-adjacent (Szymańska 20K) → B-podaż 2; kotwica 512K do ręcznej weryfikacji |

---

## Pułapki / odrzucone

### Repeat (pokryte przez mocniejszy temat — w mapie jako „pokryte", nie do produkcji)

- **„Przestałeś się czymkolwiek ekscytować" (idx 39)** — `repeat` wobec idx 31. Ten sam klaster Z3 („nic mnie nie cieszy/interesuje/obchodzi"), te same kotwice EN (HealthyGamer/Morton/Eilers), ten sam rdzeń-objaw odrętwienia. Rozróżnienie „zanik pragnienia vs radości" to free-text-furtka, którą anti-repeat odrzuca. B-popyt skalibrowane do 2 (related=1, cienki własny seed). Pole podaży faktycznie puste, ale kolizja popytu/objawu z idx 31 wyklucza z produkcji.

### Dwujęzyczni (bilingual-served — najwyżej SREBRO; tu pod progiem/flagą)

- **„Wypaliłeś się i nawet odpoczynek już nie pomaga" (idx 35)** — `dwujęzryczni`. „Burnout" współ-dominuje w polskich wyszukiwaniach (head-to-head „wypalenie" vs „burnout"), a kąt somatyczny obsadzony dużą kliniką (Dr Kulczyński STRES/KORTYZOL 516K+467K). Seed somatyczny niesie szum intencji medycznej; C tylko żółte (rama ciągnie ku poradzie snu). Najwyżej SREBRO, capowane.

### Odrzucone na bramce (B-popyt=1 — niedowerbalizowany kąt / cmentarz-ryzyko)

- **„Dlaczego czujesz się jak oszust…" (idx 0)** — B-popyt=1: demand_sugg_related=0, próbki to somatyczny szum („gorycz w ustach", „zapachy których nie ma"); kąt „oszust" nie werbalizuje się w Z3, brak kotwicy. A i C mocne, ale bramka pada.
- **„Dlaczego czujesz, że musisz zasłużyć na to, żeby istnieć" (idx 4)** — B-popyt=1: somatyczny szum, zerowa trakcja on-topic (25/13 wyświetleń), brak kotwicy. Bliskie cmentarz-ryzyku.
- **„Dlaczego twoje osiągnięcia nigdy nie czują się twoje" (idx 5)** — B-popyt=1: próbki to czysty szum generyczny; bliski kuzyn idx 0, dubluje rdzeń.
- **„Ludzie, którzy wolą być sami — wybór czy blizna" (idx 11)** — B-popyt=1: seed „czy to normalne" skażony szumem somatyczno-zwierzęcym (kot chrapie, noworodek kicha); werbalizacja kąta emocjonalnego cienka.
- **„Powtarzasz w głowie zdania, które usłyszałeś jako dziecko" (idx 27)** — B-popyt=1: kąt krytyka-wewnętrznego niedowerbalizowany w PL (autocomplete somatyczne), brak kotwicy. Niedowerbalizowany kąt, nie martwa kategoria.
- **„Czujesz się winny, gdy jest ci dobrze" (idx 28)** — B-popyt=1: fraza nie werbalizowana (somatyczny klaster „dlaczego czuję"), brak pokrewnego filmu ≥50k na temat.

### Odrzucone na bramce (B-podaż=1 — pole obsadzone bezpośrednim hitem)

- **„Masz wszystko, a i tak czujesz, że czegoś brakuje" (idx 36)** — B-podaż=1: Kasia Sawicka „Dlaczego czuję wewnętrzną pustkę" 181K to bezpośrednie on-topic trafienie z dużym zasięgiem i przyzwoitym rejestrem psych (3-4/5) — luka pozorna.
