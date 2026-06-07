# Mapa niszy A∩B∩C dla SENSUM — projekt researchu

> Dokument decyzyjny. Definiuje, jak — **bez płatnego YouTube Data API** — udowodnić istnienie polskojęzycznej widowni w niszy SENSUM, sformalizować model arbitrażu A∩B∩C, zrankingować kandydatów na tematy i wykonać pełny research jako zatwierdzalny, wielo-agentowy workflow. Wszystkie sygnały są darmowe i **triangulowane**; żaden pojedynczy sygnał nie podnosi wyniku samodzielnie. Dokument przeszedł red-team; jego ustalenia (zwłaszcza HIGH/MED) są wchłonięte w treść poniżej — nie ma osobnego „erraty".

---

## 0. PYTANIE ZEROWE — czy polskojęzyczna widownia w niszy w ogóle istnieje?

Zanim ocenimy JAKIKOLWIEK temat, musimy odpowiedzieć na pytanie kategorii, nie tematu: *czy istnieje polskojęzyczna widownia psychologiczno-rozwojowa typu SENSUM (ciepły esej-rozpoznanie, „nie jesteś zepsuty"), która OGLĄDA po polsku — z dowodem na zasięgach?* Negatywna odpowiedź unieważnia cały projekt; pozytywna odblokowuje fazy tematyczne. **To jest twardy gate blokujący — Faza 1 nie wydaje ani jednego tokena, dopóki gate nie przejdzie na zweryfikowanych ręcznie liczbach.**

### Metoda weryfikacji (triangulacja 3 darmowych dowodów)

| # | Dowód | Jak pozyskać (bez płatnego API) | Co potwierdza |
|---|---|---|---|
| Z1 | **Census polskich kanałów-sąsiadów** (psychologia / rozwój / „rozpoznanie siebie") — rzędy wielkości subów + mediana wyświetleń | Ręcznie (incognito) jako ścieżka podstawowa; `yt-dlp --flat-playlist "https://www.youtube.com/@KANAL/videos"` jako przyspieszenie **po smoke-teście** (Faza −1) | Czy kategoria ma w PL kanały 6–7-cyfrowe (widownia istnieje i się skaluje) |
| Z2 | **Istnienie polskich filmów 100k+ wyświetleń** na tematy emocjonalno-egzystencjalne (nie optymalizacyjne) — **liczby zweryfikowane ręcznie z UI, nie proxy Social Blade** | Wyszukiwanie YT incognito + filtr „liczba wyświetleń"; `yt-dlp "ytsearch40:<polska fraza-ból>"` tylko do ENUMERACJI istniejącej podaży, nie jako miara popytu | Czy FORMAT/temat rozpoznania chwyta po polsku, nie tylko optymalizacja |
| Z3 | **Bogactwo Google-WEB autocomplete PL** na pytania-bóle | `suggestqueries.google.com/complete/search?client=firefox&q=<seed>&hl=pl&gl=PL` (osobna ścieżka parsowania — patrz §4 Faza −1) | Czy ból jest WERBALIZOWANY po polsku (popyt na problem istnieje natywnie) |

Reguła interpretacji: **popyt (Z3) BEZ dobrej podaży = okazja; brak Z1+Z2+Z3 = „cmentarz"** (kategoria martwa, projekt wstrzymać). Z2 musi dowodzić zasięgów na tematach EMOCJONALNYCH, nie optymalizacyjnych — duży kanał optymalizacyjny (Rozwojowiec) nie jest dowodem na widza SENSUM.

### TWARDE kryterium pass / weak / fail (liczby weryfikowane ręcznie)

- **PASS** — istnieje ≥1 polski kanał w niszy z **medianą wyświetleń ≥6-cyfrową** **LUB** ≥3 polskie kanały 5–6-cyfrowe; **ORAZ** **≥3 RÓŻNE** polskie filmy, każdy z **zweryfikowanym ręcznie z UI** licznikiem **>100k** na tematy emocjonalno-egzystencjalne (nie optymalizacyjne); **ORAZ** ≥1 młody kanał (<12 mies.) z outlierem **>100k** na temacie-rdzeniu SENSUM (dowód, że browse/suggested działa dla nowicjusza), potwierdzony jako **nie-fluke** drugim sygnałem (≥1 kolejny młody kanał rozpoznania-emocji z trakcją). → Uruchom fazy tematyczne. **Uwaga dyscyplinarna: 99k ≠ 100k.** Liczby tuż-pod-progiem liczą się jako FAIL danej linii, nie jako „w przybliżeniu pass". Jeden kanał z jednym outlierem **nie** spełnia warunku „≥3 różne filmy 100k+".
- **WEAK** — kategoria istnieje (Z1 spełnione), ale tematy emocjonalne robią głównie 4–5-cyfrowe zasięgi, a 6-cyfrowe są tylko optymalizacyjne. → Ryzyko, że PL widz tej niszy = optymalizacyjny; ogranicz pilotaż do 2–3 filmów-sond, mierz własnym YouTube Studio przed skalowaniem.
- **FAIL** — wszystkie polskie kanały w niszy 4-cyfrowe / martwe, brak filmów emocjonalnych >100k, ubogi web-autocomplete. → „Cmentarz": wstrzymać projekt; powtórnie ocenić pozycjonowanie.

### Status werdyktu: **NIE PRZETESTOWANY — gate oczekuje na domknięcie**

Grounding (zwiadowca B) dostarczył *przesłanek* na PASS, ale **nie spełnia jeszcze własnego progu**, więc werdykt roboczy NIE brzmi „PASS warunkowy" — brzmi **„gate pending"**. Co grounding pokazał i czego nie:

- **Kategoria prawdopodobnie skaluje w PL (przesłanka, nie dowód):** Przeciętny Człowiek 476K / 72,6 mln, PsychoLoszka 280K / 27,2 mln, Rozwojowiec 277K / 34,4 mln, Strefa Psyche SWPS 210K / 28,9 mln — to proxy Social Blade (rzędy wielkości), spełnia Z1 *kierunkowo*. Demografia tych kanałów ≠ dokładnie hipoteza widza SENSUM (patrz §5, ryzyko 9).
- **Najmocniejsza przesłanka Z2+Z3 dla rdzenia niszy, ale NIEDOMKNIĘTA:** **Psychologia Bez Spiny** — kanał uruchomiony 22.01.2026 (~4 mies.), 6,21K subów, z outlierami podawanymi jako 183K / 99K / 94K / 43K / 25K wyświetleń na dystrybucji browse/suggested (model SENSUM), tytuły dosłownie w lane SENSUM („Psychologia ludzi którzy myślą że nic nie potrafią", „Ludzie, którzy lubią być sami…"). **Dlaczego to NIE wystarcza do PASS:** (a) to JEDEN kanał, a PASS wymaga ≥3 różnych filmów >100k LUB kanału z 6-cyfrową medianą; (b) z podanych liczb **tylko jedna (183K) realnie przekracza 100k** — 99K i 94K to FAIL tej linii; (c) ton/warsztat oceniono z TYTUŁÓW i opisów, nie z obejrzenia wideo.
- **Luka rzemieślnicza — przesłanka spójna:** żaden gracz nie zajmuje pełnego przecięcia (wysoki warsztat eseju-lektora × ciepły rejestr rozpoznania × doktryna research-invisible). Wysoki warsztat ma zły ton (Przeciętny Człowiek — optymalizacja), dobry ton ma słaby warsztat/skalę (PBS — listicle clickbait; Przystanek Samotność 610 subów — format wywiadowy).

**Trzy kroki domknięcia gate'u (wykonać PRZED Fazą 1, dosłownie, ręcznie):**
1. **Obejrzeć** po 2–3 filmy Przeciętnego Człowieka i Psychologii Bez Spiny — kalibracja warsztatu z obrazu, nie z tytułu.
2. **Potwierdzić z UI** (incognito, ręcznie odczytane liczniki) ≥3 RÓŻNE emocjonalne, nie-optymalizacyjne PL filmy, każdy realnie **>100k**.
3. **Potwierdzić nie-fluke:** znaleźć ≥1 dodatkowy młody kanał rozpoznania-emocji z trakcją browse/suggested, by wzorzec PBS nie wisiał na jednym kanale.

Dopóki te trzy kroki nie są zaliczone na ręcznie zweryfikowanych liczbach, gate jest **CLOSED** — żadnej pracy tematycznej.

---

## 1. MODEL A∩B∩C — formalizacja

Każda noga jest oceniana w skali **0–3** osobno; **Noga B jest rozszczepiona na dwa niezależnie oceniane wymiary** (B-popyt 0–3 i B-podaż 0–3), bo „popyt" i „podaż" to przeciwne dźwignie i mieszanie ich w jednej liczbie ukrywa, która zawiodła (poprawka red-team). Arbitraż to PRZECIĘCIE (koniunkcja z progiem minimalnym na każdej nodze/wymiarze), nie suma — wysokie A nie ratuje zerowego B.

### Noga A — udowodniony, UNIWERSALNY, evergreen pull

- **Definicja:** temat wygrywa na anglojęzycznym YouTube psych/rozwój w lane SENSUM (warm essayistic emotional-recognition), jest evergreen (nie chwilowa moda), a jego rdzeniem jest emocja, nie protokół.
- **Co mierzy:** globalny, ponadkulturowy popyt na EMOCJĘ + dowód, że format eseju-rozpoznania ją unosi.
- **Źródło/sygnał:** archetypy i creatorzy z groundingu A (Pursuit of Wonder, School of Life, Einzelgänger jako format+temat; HealthyGamer/Teahan/Crappy Childhood Fairy jako dowód TEMATU) + uzupełniające WebSearch na konkretną frazę (tytuły + rzędy wyświetleń z agregatorów). **Evergreen jest dowodzony PRZEDE WSZYSTKIM strukturą archetypu** (te rany powtarzają się latami w katalogach lane-kanałów); Google Trends jest tu tylko *potwierdzeniem dla finalistów*, nie per-kandydat gate'em (Trends wymaga token-handshake i bywa 429 — patrz §5).
- **Skala 0–3:**
  - **3** — ≥2 lane-channele (w tym ≥1 format-anchor: PoW/SoL/Einzelgänger) mają flagowy film 500k+ na tym archetypie; jawnie evergreen.
  - **2** — proven u ≥1 format-anchora **lub** wielokanałowo u topic-channeli; mid-high performer.
  - **1** — pojawia się, ale głównie u topic-only (talking-head) lub jako pochodna; słabszy ceiling.
  - **0** — brak dowodu pull **lub** rdzeniem jest optymalizacja/protokół (lane wykluczony: Improvement Pill / Better Ideas / Huberman) **lub** chwilowa moda.
- **Reguła klasyfikacji:** wymagany **A ≥ 2**, żeby kandydat przeszedł dalej. A=0 z powodu rejestru optymalizacyjnego = twarde wykluczenie (łamie pozycjonowanie kanału, nawet przy popycie).

### Noga B — rozszczepiona: B-popyt × B-podaż (REALNY polski popyt × SŁABA polska podaż)

> **Dlaczego rozszczepiona.** Stary „kombinowany" B=1 odpalał się ZARÓWNO na „słaby popyt", JAK i na „już dobra podaż" — dwie przeciwne sytuacje w jednej liczbie. Rozdzielenie usuwa tę dwuznaczność i — kluczowe — **rozdziela cmentarz od pułapki-dwujęzycznych**: cmentarz to niski B-popyt, pułapka-dwujęzycznych to wysoki B-popyt zaspokojony gdzie indziej. Gate wymaga **B-popyt ≥ 2 AND B-podaż ≥ 2**.

#### B-popyt (0–3) — czy Polacy WERBALIZUJĄ ten ból po polsku, z kotwicą wielkości

Autocomplete-presence **nie ma podłogi wolumenu**: fraza podpowiada się tak samo, gdy wpisuje ją 200 osób/rok (prawdziwy cmentarz: popyt realny-ale-pomijalny), jak gdy wpisuje 200 tys./rok. Dlatego **sama obecność w autocomplete jest warunkiem koniecznym, nie wystarczającym** — B-popyt wymaga TRZECH skorelowanych dowodów, z czego co najmniej jeden niesie wielkość (poprawka red-team „magnitude anchor"):

1. **Sygnał frazy (obecność/bogactwo):** Google-WEB autocomplete PL (`client=firefox`) na seedy-pytania w języku problemu (prefiksy *dlaczego/jak/czemu/czy/co zrobić gdy* × rdzeń-emocja) — główny detektor; YT-autocomplete (`client=youtube&ds=yt`) jako wtórny. Surowe listy zapisywane do `brainstorms/` dla audytowalności.
2. **Kotwica kategorii w Trends:** szeroki seed kategorii (rodzic-emocja, np. „samotność", „wstyd", „poczucie że jestem w tyle") MUSI przekroczyć próg widoczności w Google Trends geo=PL, nawet jeśli wąska fraza jest pod progiem próbkowania. „Brak danych" dla *wąskiej* frazy ≠ brak popytu — ale rodzic-emocja musi się rejestrować, inaczej to cmentarz.
3. **Dowód-wielkości kategorii (Z2-style):** ≥1 polski film (DOWOLNY kanał, dowolna jakość) na pokrewną emocję z **realnym progiem wyświetleń (≥50k)**, dowodzący, że *kategoria monetyzuje uwagę po polsku*, nawet jeśli TEN kąt jest nieobsłużony.

- **Skala B-popyt:**
  - **3** — bogaty PL web-autocomplete na seed-ból **ORAZ** rodzic-emocja przekracza próg Trends geo=PL **ORAZ** istnieje pokrewny PL film ≥50k. Wszystkie trzy zielone.
  - **2** — sygnał frazy bogaty + JEDEN z dwóch dowodów-wielkości (Trends-kategoria lub film ≥50k), drugi słaby/niedostępny.
  - **1** — sygnał frazy obecny, ale CIENKI (po reseedingu językiem problemu nadal ubogi) **lub** brak obu dowodów-wielkości.
  - **0** — brak werbalizacji po polsku (cmentarz): cienki web+YT-autocomplete, rodzic-emocja poniżej progu Trends, brak pokrewnego filmu ≥50k.

#### B-podaż (0–3) — czy istnieje DOBRA polska wersja (ilość ORAZ jakość)

- **Źródło:** census `yt-dlp "ytsearch40:<fraza>"` / `--flat-playlist` **tylko do enumeracji istniejących filmów** (NIE jako miara popytu — `ytsearchN:` zwraca ranking trafności/popularności YT, nie wolumen). Jakość oceniana ręcznie rubryką SENSUM 1–5 (głos/rozpoznanie, produkcja, dopasowanie do bólu).
- **Skala B-podaż (im wyższa, tym SŁABSZA/rzadsza podaż = większa okazja):**
  - **3 — ZŁOTO podażowe:** 0–2 polskie filmy, wszystkie ≤2/5 SENSUM-fit lub stare/clickbait/AI-lektor.
  - **2:** podaż istnieje, ale przeciętna (kilka filmów, najlepszy ≤3/5 SENSUM-fit) — luka jakościowa realna.
  - **1:** podaż częściowo dobra (jest film 3–4/5 z umiarkowanymi zasięgami).
  - **0:** pole zajęte — istnieje polski film **≥4/5 SENSUM-fit z dużymi zasięgami**.

**Zapis B w tabeli:** `B-popyt=N / B-podaż=M` (np. `B-popyt=3 / B-podaż=3`). Gate: oba ≥2.

**JAWNIE — jak rozszczepiony B odróżnia „cmentarz" od realnej okazji:**
Okazja = **B-popyt wysoki × B-podaż wysoka** (= słaba/rzadka podaż). Cmentarz = **B-popyt 0** (niezależnie od podaży: zero filmów + zero popytu = martwo). Reguła operacyjna: *najpierw udowodnij popyt trzema dowodami B-popyt (w tym kotwicą wielkości), dopiero potem census B-podaż.* „Zero filmów" **nigdy** nie podnosi wyniku samo z siebie — bez B-popyt≥2 zero filmów znaczy cmentarz, nie lukę. Bez kotwicy wielkości filtr cmentarza jest teatrem; dlatego B-popyt=3 jest niemożliwe na samej obecności w autocomplete.

**JAWNIE — jak B łapie „dwujęzycznych" (oglądają po angielsku):**
Decyzja bilingual opiera się na **dwóch ROBUSTNYCH sygnałach, nie na udziale komentarzy** (poprawka red-team — udział PL komentarzy jest systematycznie zaniżony, demograficznie ślepy i porównywany do wymyślonego progu):

1. **Trends head-to-head w geo=PL (sygnał główny, niesie skalę):** porównaj polski termin vs jego angielski odpowiednik W POLSCE (np. „wypalenie" vs „burnout", „samotność" vs „loneliness"). Jeśli angielski termin współ-dominuje lub dominuje w polskich wyszukiwaniach — TO jest sygnał „bilingual-served", wprost i na skali.
2. **Obecność/brak polskiej podaży z trakcją (sygnał główny):** jeśli istnieje polski film realnie obsługujący ten kąt z zasięgami — luka jest pozorna NIEZALEŻNIE od konsumpcji EN. (To pokrywa się z B-podaż, więc B-podaż i bilingual czytają ten sam fakt z dwóch stron.)
3. **Udział PL komentarzy pod dużymi anglo-filmami — TYLKO miękki korroborator/tie-break** (yt-dlp `--write-comments` + `langdetect`/heurystyka diakrytyczna; *best-effort, finalists-only*). **Bez progu 3–5%** (był wymyślony). Demografia docelowa SENSUM (45+, mniejsze miasta, TV) to grupa NAJMNIEJ skłonna komentować na YouTube — dlatego komentarze są niemal ślepe na dokładnie tego widza i z definicji nie mogą być bramką. Eksplicytne „czy jest po polsku?" liczy się jako jakościowa wskazówka, nie jako procent.

4. **Interpretacja (decyzja JUDGEMENTOWA z Trends + podaży, nie zmierzony procent):**
   - (A) bogaty PL B-popyt + Trends pokazuje EN-współdominację w geo=PL **i/lub** istnieje słaba-ale-obecna polska podaż = popyt realny, ZASPOKOJONY po angielsku → **luka POZORNA dla biegłych, PRAWDZIWA dla docelowej widowni SENSUM** (funkcjonalny-ale-nie-emocjonalny angielski, 45+, mniejsze miasta) → **flaga `bilingual-served`**, B-podaż capowane na max 2 → maksymalnie SREBRO.
   - (B) bogaty PL B-popyt + Trends pokazuje przewagę polskiego terminu + brak/słaba polska podaż = **czysta luka → ZŁOTO podażowe (B-podaż 3).**
   - (C) ubogi PL B-popyt (temat żyje tylko po angielsku) → B-popyt=0, odrzuć.
   - **Reguła rozstrzygania wątpliwości:** *gdy dowód bilingual jest niejednoznaczny, domyślnie SREBRO, nie ZŁOTO.* Błąd „produkcja w rynek już zaspokojony" jest droższy niż błąd „pominęliśmy okazję", więc przy ambiwalencji przechylaj ku ostrożności.

### Noga C — SENSUM-fit (głos + architektura + przekładalność kulturowa)

- **Definicja:** jeśli temat wejdzie do PL, czy WYLĄDUJE emocjonalnie, złapie jedną z 5 architektur i zabrzmi natywnie (nie „amerykańsko").
- **Co mierzy:** filtr JAKOŚCIOWY (nie popytowy) — przekładalność emocji vs opakowania, fit z głosem „ciepły terapeuta do jednej osoby" i z selektorem architektur.
- **Źródło/sygnał:** checklista przekładalności D (testy A–H), zakotwiczona w doktrynie (`voice_corpus.md` §0/§C/§C2, `style_guide.md` §Pozycjonowanie/12.4, `03_architecture_select.md`). Ocena tekstowa „uchem i rozumem", wsparta YT-autocomplete (test B: czy polski idiom w ogóle pojawia się vs tylko anglicyzm). **Każde czerwone/żółte/zielone wymaga jednej linii uzasadnienia** (audytowalność); przy C=2→przeramowanie wymagane potwierdzenie drugiej osoby/właściciela, bo to przeramowanie staje się briefem dla `/draft`.
- **Skala 0–3 (mapuje na agregację checklisty D):**
  - **3 — ZIELONE czyste:** testy A,B,D,E,H zielone, brak czerwonego w F,G; istnieje naturalny polski idiom; jasno łapie ≥1 z 5 architektur; rdzeniem jest bycie-zauważonym/zdjęcie wstydu.
  - **2 — ŻÓŁTE uratowalne:** czerwony tylko w B/C/E/F, ale po schowaniu etykiety zostaje prawdziwa emocja z A — **zapisz KONKRETNE przeramowanie** (etykieta→mechanizm, np. „postaw granice"→„dlaczego nie umiesz powiedzieć nie, kiedy chcesz"). To często najcenniejsza klasa (emocja uwięziona w anglosaskim opakowaniu = niedoobsłużona luka B).
  - **1:** wymaga ciężkiego przeramowania; ryzyko, że zostaje sama etykieta; słaby fit architektury.
  - **0 — CZERWONE:** czerwony w **A** (rdzeniem skrypt społeczny/instytucja USA, nie emocja) **LUB** w **H** (opiera się ciepłu/rozpoznaniu, ciągnie ku poradzie/wykładowi) **LUB** ≥3 czerwone łącznie.
- **Reguła klasyfikacji:** wymagany **C ≥ 2**. Czerwony w A lub H jest **dyskwalifikujący niezależnie od A i B** (brak uniwersalnej emocji albo brak głosu kanału).

---

## 2. REGUŁA ŁĄCZENIA, „ZŁOTO", FILTRY PUŁAPEK, REMISY, ANTI-REPEAT

### Składanie A, B-popyt, B-podaż, C w jeden werdykt

Model jest **koniunkcyjny z bramką progową**, nie sumacyjny:

1. **Bramka (gate):** kandydat musi mieć **A≥2 AND B-popyt≥2 AND B-podaż≥2 AND C≥2**. Jakiekolwiek 0 lub 1 na którejkolwiek nodze/wymiarze → odpada z rankingu (ląduje w archiwum „odrzucone + powód").
2. **Tier (kubełek porządkowy, NIE liczba):** SCORE to **etykieta kubełka** (ZŁOTO/SREBRO), nie zmierzona wielkość. Sumy A+B+C **nie publikujemy jako headline'u** — to ordinale o różnej rzetelności (A = snapshoty wyświetleń; B = autocomplete + ręczna rubryka; C = subiektywny odczyt doktryny „uchem"), więc ich dodawanie udaje precyzję, której sygnały nie mają. **Realnym rankerem są leksykograficzne tie-breaki** poniżej, nie suma kardynalna.

### Jednoznaczna definicja **ZŁOTA**

> **ZŁOTO = A=3 ∧ B-popyt=3 ∧ B-podaż=3 ∧ C∈{2,3}.**
> Tzn.: udowodniony evergreen pull globalny (A=3), werbalizowany PL popyt z kotwicą wielkości (B-popyt=3), czysta słaba/rzadka polska podaż bez zaspokojenia po angielsku (B-podaż=3, brak flagi `bilingual-served`), oraz fit kanału co najmniej uratowalny przeramowaniem (C≥2; przy C=2 wymagane zapisane i potwierdzone przeramowanie). To są kandydaci „do produkcji w pierwszej kolejności".

Druga półka — **SREBRO**: przeszedł bramkę (wszystkie ≥2), ale nie jest ZŁOTEM — typowo `bilingual-served` (B-podaż capowane na 2), albo B-podaż=2 (luka tylko jakościowa), albo C=2 z cięższym przeramowaniem. Produkcja w drugiej kolejności. **Reguła domyślna: gdy dowód bilingual jest ambiwalentny → SREBRO, nie ZŁOTO.**

### JAWNE filtry wykluczające OBIE pułapki (stosowane wewnątrz bramki B)

- **Filtr cmentarza:** B-popyt=0 (cienki web+YT-autocomplete, rodzic-emocja pod progiem Trends, brak pokrewnego filmu ≥50k) → odrzuć, niezależnie od podaży. „Zero filmów" nigdy samo nie podnosi wyniku. **Kotwica wielkości (Trends-kategoria + film ≥50k) jest tym, co czyni ten filtr realnym, a nie deklaratywnym.**
- **Filtr dwujęzycznych:** decyzja z Trends head-to-head geo=PL + obecności polskiej podaży (nie z procentu komentarzy). Wynik „bilingual-served" → flaga + B-podaż max 2 → najwyżej SREBRO. Ambiwalencja → domyślnie SREBRO.
- **Filtr opakowania (fałszywe ZIELONE w C):** temat z uniwersalną emocją (A wysokie), ale przyszły owinięty w anglo-etykietę tak mocno, że PL widz zna go PO ANGIELSKU — łapany łącznie przez flagę bilingual i C-test B/C (anglicyzm zamiast idiomu).

### Obsługa remisów (tie-break, kolejno) — to jest właściwy ranker

Przy równym tierze:
1. **Wyższe B-podaż** (siła/rzadkość luki podażowej) — bezpośrednia okazja arbitrażowa.
2. **Wyższe B-popyt** (siła werbalizowanego popytu).
3. **Wyższe C** (czystość głosu/architektury).
4. **Brak flagi `bilingual-served`** > z flagą.
5. **Fit z niedoreprezentowaną architekturą** (anti-repeat architektur — `03_architecture_select.md`: Composite Portrait NIE jest już domyślny; różnorodność architektur to plus).
6. **Bliżej hipotezy widowni docelowej** (45+, skos ku kobietom, mniejsze miasta, relacyjny/rodzinny rdzeń wg testu D — preferuj cluster childhood-wound / people-pleasing / samotność / „nie jesteś zepsuty" nad framingiem Gen-Z/online).

### Anti-repeat względem 3 istniejących tematów — klucz dedup MECHANICZNY, nie „archetyp emocji"

Stary klucz („pokrycie emocjonalnego rdzenia/archetypu") był **nieoperacyjny dla kanału jednego meta-uczucia**: skoro całe pozycjonowanie SENSUM to „nie jesteś zepsuty / bycie-zauważonym", to PRAWIE KAŻDY on-brand kandydat dzieli rdzeń z trójką istniejących — ściśle stosowany, zabijał cały lejek; luźno stosowany (przez furtkę „odrębny kąt" + free-text), nigdy nie wiązał. Zastępujemy go **mechanicznym kluczem dedup** (poprawka red-team):

> **Repeat = TEN SAM {centralny obraz/metafora} ALBO TEN SAM {behawioralny objaw-powierzchniowy, który widz wpisuje w wyszukiwarkę}.**
> Dwa tematy dzielące meta-uczucie „nie jesteś zepsuty", ale o RÓŻNYCH objawach-powierzchniowych (prokrastynacja vs people-pleasing vs samotność) i różnych centralnych metaforach — **NIE są repeatem.**

Istniejące, wyprodukowane tematy SENSUM (lane-confirmation, NIE do ponownej produkcji), z ich kluczami dedup:
- „czujesz że jesteś w tyle" — objaw: *porównywanie się / bycie-z-tyłu względem rówieśników*.
- „dlaczego nie potrafisz się niczego trzymać" — objaw: *zaczynanie-i-porzucanie / brak wytrwałości*.
- „wstyd za własne życie" — objaw: *chroniczny wstyd za to, gdzie/kim jestem*.

Reguła operacyjna (mechaniczna): kandydat z **innym objawem-powierzchniowym ORAZ inną centralną metaforą = dozwolony**, bez free-text wyjątku. Kandydat z tym samym objawem LUB tą samą metaforą = flaga `repeat`, wykluczony z rankingu produkcyjnego (zostaje w mapie jako „pokryte"). Przykład: nowy temat „odkładam rzeczy, na których mi zależy" dzieli objaw „zaczynanie-i-porzucanie" z „niczego się nie trzymać" → repeat. Temat „nie umiem powiedzieć nie" (objaw: people-pleasing) → NIE repeat, mimo wspólnego meta-uczucia.

---

## 3. SCHEMAT OUTPUTU — tabela rankingowa

**Lejek:** generujemy **30–40 kandydatów** (archetypy A × przeramowania D), przepuszczamy przez bramkę, rankujemy przeszłe tie-breakami, dostarczamy **TOP 12** finalistów (oznaczone ZŁOTO/SREBRO) + osobny załącznik „odrzucone + powód" (pamięć instytucjonalna przeciw powtarzaniu martwych tematów).

**Zakres pomiarów (scoping kosztownych sygnałów):** kolumny **B-podaż** i **flaga bilingual** są WYMAGANE tylko dla kandydatów, którzy już przeszli **A≥2 ∧ B-popyt≥2 ∧ C≥2** (finaliści). Dla kandydatów odrzuconych wcześniej na demand/fit te komórki czytają `n/a — gated out (demand/fit)`. To trzyma drogie ręczne sygnały (census jakości podaży, test bilingual) tam, gdzie zmieniają decyzję, i dopasowuje lejek 30–40 → bramka → ~12.

### Kolumny finalnej tabeli rankingowej

| Kolumna | Zawartość |
|---|---|
| **#** | Pozycja w rankingu (po tie-breakach) |
| **Temat (PL, język bólu)** | Robocza fraza w języku problemu widza, nie metaforyczny tytuł SENSUM (np. „dlaczego ciągle czuję, że muszę wszystkim dogadzać") |
| **Objaw-powierzchniowy + metafora** | Klucz dedup: searchowany objaw + centralny obraz (do anti-repeat) |
| **Archetyp A** | Nazwa archetypu z groundingu A (np. „people-pleaser's trap / self-erasure") |
| **A-score + dowód** | 0–3 + 1 linia dowodu (creator + flagowy tytuł + rząd wyświetleń, np. „PoW „The Paradox of Being Nice" 812K") |
| **B-popyt + sygnały** | 0–3 + skrót: `web-AC=bogaty/cienki`, `YT-AC=n podp.`, `Trends-kategoria=nad/pod progiem`, `film-kategorii≥50k=tak/nie` |
| **B-podaż + sygnały** | 0–3 + `podaż=N filmów / best SENSUM-fit X/5` (lub `n/a — gated out`) |
| **C-fit + architektura** | 0–3 (ZIELONE/ŻÓŁTE) + wskazana architektura z 5 (Composite/Forensic/Historical Reversal/Socratic/Systems Audit); przy ŻÓŁTYM: **zapisane (i potwierdzone) przeramowanie** etykieta→mechanizm |
| **Flaga-pułapki** | jedna/kilka z: `—` / `bilingual-served` / `cmentarz-ryzyko` / `repeat` / `opakowanie-anglo` |
| **Tier** | `ZŁOTO` / `SREBRO` (kubełek, nie suma liczbowa) |
| **Werdykt** | `ZŁOTO` / `SREBRO` / `ODRZUCONE: <powód>` + ewentualne uzasadnienie wyjątku anti-repeat (mechaniczne: inny objaw + inna metafora) |

Dodatkowo przy każdym ZŁOCIE: **1-zdaniowy „kąt SENSUM"** (jak temat schodzi do „jednej osoby wieczorem w słuchawkach", test H) — pomost do `/draft`.

---

## 4. PLAN EGZEKUCJI — wielo-agentowy workflow (do ZATWIERDZENIA)

Wszystko bez płatnego YouTube Data API. **Plan zaczyna się od Fazy −1 (tooling bootstrap + smoke-testy), bo trzy load-bearing narzędzia nie są dziś gotowe** (zweryfikowane: `yt-dlp`, `pytrends`, `langdetect` nieobecne; `requirements.txt` ma z istotnych zależności tylko `requests`). Artefakty zapisywane w `brainstorms/` (jak istniejące `2026-06-*.md`), wersjonowane.

### FAZA −1 — Tooling bootstrap (NOWA, blokująca; ~0,5 dnia)

Cel: zamienić deklaracje narzędziowe na zweryfikowane fakty, zanim którakolwiek faza na nich polegnie.

1. **Standalone autocomplete (usuwa fałszywą zależność od `--signals`).** Zweryfikowane w kodzie: `run_signals(slug, topic_override)` (`agent8_publish.py` L823) woła `_load_narration(slug)` (L835→L104), które **wymaga istniejącego `script_corrected.docx`/`script.docx`/`md/04_final.md` pod `outputs/videos_pl/{slug}/`** — inaczej `FileNotFoundError` — i zapisuje wynik do katalogu sluga. Badany *temat* nie ma sluga, skryptu ani katalogu; `--topic=` zmienia tylko seed, nie znosi wymogu sluga. **Wniosek: `--signals` jest strukturalnie związany z już-wyprodukowanymi filmami i NIE da się go wycelować w gołą frazę-kandydata.** Jedyne reużywalne aktywa to **czyste funkcje** `_scrape_suggestions(query)` (L482) + `_alphabet_soup` (L502), które biorą surowy string i nie mają zależności od sluga/plików. Działanie: wydzielić je do małego standalone `tools/niche_signals.py`, który bierze listę seed-fraz i zrzuca autocomplete do `brainstorms/`. (~15 linii; usuwa fałszywą zależność.) **Tabela narzędzi i każde odwołanie w tym dokumencie wskazują na ten standalone, nie na `--signals`.**
2. **Wariant Google-WEB autocomplete to OSOBNA ścieżka parsowania, nie „jedna linijka".** Zweryfikowane: żywy parser `_scrape_suggestions` (L492–496) robi regex `\((\[.+\])\)` i czyta `data[1]` — to kształt JSONP specyficzny dla `client=youtube`. `client=firefox` zwraca **goły JSON** `[query,[suggestions]]` (bez JSONP-wrappera) → istniejący regex zwróci `[]` po cichu (a cichy pusty wynik dokument sam ostrzega, by czytać jako „brak popytu" — czyli najgorszy możliwy fałsz). Działanie: dodać osobną gałąź fetch+parse dla `client=firefox` (parsuj jako zwykły JSON), **plus naprawić dekodowanie**: oba endpointy ślą mieszane kodowanie — strict utf-8 daje mojibake na ą/ć/ę/ł/ó/ś/ż/ź (zweryfikowane: `jak przestać się martwić`). Spróbuj utf-8 strict → fallback cp1252, albo użyj endpointu zwracającego czyste utf-8. **Dopóki dekodowanie nie jest naprawione, traktuj podpowiedzi jako ASCII-folded keywords (OK na obecność/kolejność popytu, NIE OK dla diakrytycznego testu bilingual.)** Smoke-test: znana akcentowana podpowiedź musi round-trippować do poprawnych glifów; web-AC musi zwrócić ~10 bogatych podpowiedzi na seed przykładowy, zanim cokolwiek na nim polegnie.
3. **Instalacja + smoke-test pozostałych narzędzi.** `pip install yt-dlp pytrends langdetect` (dopisać do `requirements.txt`). Następnie SMOKE-TEST każdego na realnym celu z TEGO środowiska, z zapisem realnej latencji i odsetka porażek: (a) `yt-dlp --flat-playlist` na 1 polskim kanale; (b) `yt-dlp --write-comments` na 1 dużym anglo-filmie (uwaga: komentarze są wolne — minuty/film — i łamliwe; traktować jako manualny, finalists-only krok); (c) `pytrends` na 1 zapytaniu (oczekiwać 429 — wymagany backoff/retry, częściowe pokrycie). **Fallbacky jeśli narzędzie zawiedzie:** Z1/Z2/census → ręczne przeglądanie incognito (Faza 0 i tak zakłada ręczne oglądanie); test komentarzy → best-effort, zdegradowany do miękkiego korroboratora (spójnie z fiksem bilingual). **`ytsearchN:` to ranking trafności/popularności, NIE miara popytu — używać wyłącznie do ENUMERACJI istniejącej podaży.**
4. **Sprostowanie cytatu o diakrytykach.** Dawne odwołanie do „logiki diakrytyków, commit 07e885d" jest **usunięte**: ten commit dotyczył wyłącznie `tools/intelligence/analyzer.py`, a całe drzewo `tools/intelligence/` jest skasowane (git status: `D analyzer.py` itd. — ten sam moduł Intelligence, który projekt odrzucił). Co więcej, była to logika EKSTRAKCJI SŁÓW z czystego skryptu, nie detektor języka, a sam commit ostrzegał, że angielskie STOP_WORDS „nie dopasują polskiego". **Detekcja języka komentarzy opiera się na `langdetect`** (po instalacji) **albo na samodzielnej heurystyce diakrytyk+stop-słowa napisanej świeżo** dla tego workflow (jeśli potrzebny regex — skopiować wzorzec `[^\W\d_]+` inline, nie odwoływać się do martwego pliku). Żadnego „reużycia" skasowanego kodu.

Gate Fazy −1: wszystkie smoke-testy zielone (lub jawnie udokumentowany fallback) → dopiero wtedy Faza 0.

### FAZA 0 — Domknięcie Pytania Zerowego (gate całego projektu; ~0,5 dnia + obejrzenie filmów)

~1 agent (lead in-session) + **ręczne obejrzenie 2–3 filmów przez właściciela (twardy gate na OBEJRZANYM wideo, nie na tytułach)**.
- Census Z1 (`--flat-playlist` na 6–8 polskich kanałach-sąsiadach lub ręcznie), potwierdzenie Z2 (**≥3 RÓŻNE emocjonalne PL filmy >100k, liczniki odczytane ręcznie z UI**), Z3 (web-autocomplete na 10 seed-bólów), oraz potwierdzenie nie-fluke (≥1 dodatkowy młody kanał rozpoznania).
- Wyjście: werdykt PASS/WEAK/FAIL z twardymi, ręcznie zweryfikowanymi liczbami. **STOP-gate:** FAIL → projekt wstrzymany; *conditional/„prawie" → traktować jak FAIL danej linii (99k ≠ 100k), nie odblokowywać Fazy 1.*

### FAZA 1 — Generowanie kandydatów (A-leg + przeramowania). 2 agenty równolegle.
- Agent 1a (Archetyp-Miner): z 18 archetypów A + WebSearch tytuły/wyświetlenia → ~30–40 kandydatów z A-score+dowód.
- Agent 1b (Translatability-Filter / Noga C wstępna): przepuszcza każdego przez checklistę D (A–H), nadaje C-score wstępny z jedną linią uzasadnienia per test, dla ŻÓŁTYCH pisze przeramowanie, odrzuca CZERWONE w A/H. Przypisuje też **klucz dedup** (objaw + metafora) do anti-repeat.
- Wyjście: lista ~25 kandydatów po pre-filtrze C, z kandydackimi seedami-bólami PL.

### FAZA 2 — Pomiar Nogi B (B-popyt × B-podaż × test dwujęzyczny). 3 agenty równolegle, każdy na ~1/3 listy.
- Każdy agent dla swojej puli: (a) **B-popyt:** standalone `niche_signals.py` (web-AC główny + YT-AC wtórny) na **stałym szablonie seedów** (zamknięta lista prefiksów-pytań × rdzeń-emocja — patrz niżej), z zapisem surowych list do `brainstorms/`; + **intent-filter PASS przed liczeniem** (odsiej medyczno-somatyczne/literalne); + kotwica wielkości (Trends-kategoria + film ≥50k). (b) **B-podaż:** census `ytsearch40:` + ręczna rubryka SENSUM 1–5 top10. (c) **test dwujęzyczny:** Trends head-to-head PL-vs-EN geo=PL + obecność polskiej podaży; komentarze tylko jako miękki korroborator (best-effort). (d) flaga-pułapki.
- **Protokół anty-gameowania B-popyt:** seed-grammar ustalona Z GÓRY i identyczna dla WSZYSTKICH kandydatów; surowe wyniki logowane (audytowalne/odtwarzalne); cienki wynik wyzwala **reseed-then-recount**, nie niski score; B-popyt nigdy nie stoi na pojedynczym „najlepszym" seedzie — wymagane ≥2 zgodne źródła (web-AC + YT-AC, albo AC + Trends) per reguła triangulacji.
- Wyjście: `B-popyt=N / B-podaż=M` + sygnały + flaga-pułapki per kandydat (finalists-only dla B-podaż/bilingual).

### FAZA 3 — Synteza, bramka, ranking. 1 agent (lead).
- Łączy A / B-popyt / B-podaż / C, stosuje bramkę (wszystkie ≥2), leksykograficzne tie-breaki, mechaniczny anti-repeat vs 3 istniejące tematy, oznacza tier ZŁOTO/SREBRO (kubełek, nie suma). Trends-evergreen sprawdzany tu, finalists-only.
- Wyjście: finalna tabela TOP 12 + załącznik „odrzucone + powód" + 1-zdaniowe „kąty SENSUM" dla ZŁOTA, zapisane w `brainstorms/2026-06-NN-mapa-niszy-abc.md`.

### (Opcjonalnie) FAZA 4 — Pętla własnych danych.
Po publikacji pierwszych ZŁOTYCH tematów: CTR/retencja/search-traffic z YouTube Studio (darmowe, własne dane, nie wymaga Data API) → potwierdzone trafienia stają się nowymi seedami następnej rundy; faktyczne zapytania widzów ze Studio zasilają listę seedów. To także **ostateczny weryfikator demografii** (czy realny widz = hipoteza 45+/kobiety/mniejsze miasta).

| Faza | Agenty | Narzędzia | ~Tokeny | ~Czas |
|---|---|---|---|---|
| −1 | 1 + ręczne | pip, standalone niche_signals, smoke-testy | 20–40k | 0,5 dnia |
| 0 | 1 + ręczne (obejrzenie wideo) | yt-dlp/incognito, web-AC, WebSearch | 30–60k | 0,5 dnia + obejrzenie |
| 1 | 2 (równolegle) | WebSearch/WebFetch, checklista D | 120–180k | 1–2 h pracy agentów |
| 2 | 3 (równolegle) | niche_signals (web+yt AC), Trends/pytrends, yt-dlp search; komentarze finalists-only | 250–400k | **manualnie cięższa** (census jakości + Trends 429 + komentarze) — rzędu 1 dnia człowieka, nie 2–4 h |
| 3 | 1 | synteza in-session | 60–100k | 1 h |
| **Razem** | **~8 ról** (max 3 równolegle) | — | **~0,5–0,8 mln tokenów** | **~2–3 dni kalendarzowe** |

Koszt tokenów to rząd wielkości (research tekstowy, in-session Opus, zero Anthropic API per doktryna kanału). **Główne wąskie gardło to PRACA RĘCZNA w Fazach 0/2** (ocena jakości podaży, Trends pod rate-limitem, komentarze), nie tokeny — poprzednia wycena „2–4 h" dla Fazy 2 milcząco zakładała gotowe i niezawodne narzędzia; po Fazie −1 budżetujemy uczciwie godziny człowieka. **Każda faza ma osobny gate zatwierdzenia przez właściciela** — Faza 2 (najdroższa) rusza dopiero po akceptacji listy kandydatów z Fazy 1; Faza 1 rusza dopiero po PASS Fazy 0; Faza 0 rusza dopiero po zielonych smoke-testach Fazy −1.

**Stały szablon seedów B-popyt (ustalony z góry, identyczny dla wszystkich):** prefiksy `{dlaczego, czemu, jak przestać, czy to normalne że, co zrobić gdy, dlaczego czuję że}` × `{rdzeń-emocja w języku problemu}`. Web-AC = główny detektor; YT-AC = wtórny. Każdy kandydat przez ten sam szablon; surowe listy do `brainstorms/`.

---

## 5. RYZYKA I OGRANICZENIA DANYCH

1. **Brak wolumenu bezwzględnego.** Żaden darmowy sygnał (autocomplete, Trends, Social Blade) nie podaje liczby wyszukiwań/widzów — wszystko to proxy: obecność/kolejność (AC, **bez podłogi wolumenu w obie strony**), wartości względne 0–100 (Trends), point-in-time agregaty (Social Blade). Ranking jest porządkowy, nie ilościowy. Mitygacja: triangulacja ≥2 sygnałów na nogę; **kotwica wielkości** (Trends-kategoria + film ≥50k) w B-popyt; nigdy jeden sygnał.
2. **Pułapka cmentarza (fałszywa luka) — bez kotwicy wielkości była nierozróżnialna od okazji.** Sama obecność w autocomplete nie odróżnia „200 osób/rok" od „200 tys./rok". Mitygacja: B-popyt=3 wymaga AC-obecność **+** Trends-kategoria nad progiem **+** pokrewny film ≥50k. „Zero filmów" / „brak danych w Trends" nigdy samo nie podnosi wyniku.
3. **Pułapka dwujęzycznych (fałszywe złoto) — przeniesiona z komentarzy na Trends+podaż.** Udział PL komentarzy jest zaniżony, demograficznie ślepy (45+/TV nie komentują) i był porównywany do wymyślonego progu 3–5%. Mitygacja: decyzja bilingual z Trends head-to-head geo=PL + obecności polskiej podaży; komentarze tylko miękki tie-break; **ambiwalencja → domyślnie SREBRO** (błąd „rynek już zaspokojony" jest droższy).
4. **Personalizacja/lokalizacja wyszukiwań.** AC i wyniki YT są personalizowane. Mitygacja: incognito/wylogowany + `hl=pl&gl=PL` (i VPN-PL dla census) dla powtarzalności między tematami.
5. **Skąpość i wrażliwość AC na seed — ORAZ gameowalność.** Empirycznie metaforyczny seed dał z ds=yt 1 podpowiedź, web-AC 10 bogatych; ten sam seed daje 1 vs 14 zależnie od frazowania. Cienki wynik ≠ brak popytu (zły seed), ALE bogactwo zależy od jakości seeda i szumu intencji, nie od prawdziwego popytu — więc operator może przesunąć B-popyt 1→3 samym reseedingiem. Mitygacja: **stały szablon seedów dla wszystkich kandydatów**, surowe listy logowane (audyt), **intent-filter przed liczeniem**, cienki wynik = reseed-then-recount (nie niski score), ≥2 zgodne źródła.
6. **Subiektywność ocen jakościowych.** C-fit (checklista D) i SENSUM-fit podaży (1–5) to oceny tekstowe „uchem". Mitygacja: standaryzowana rubryka, jedna linia uzasadnienia per test, zakotwiczenie w doktrynie (`voice_corpus.md`, `style_guide.md`, `03_architecture_select.md`), ręczne obejrzenie kanałów-benchmarków, **druga para oczu/właściciel na C=2→przeramowanie** (bo staje się briefem `/draft`). Tier traktować jako kubełek, nie liczbę.
7. **Kruchość i ToS yt-dlp / nieoficjalnych endpointów + brak weryfikacji w tym środowisku.** Census Z1/Z2 (`--flat-playlist`), census podaży (`ytsearch40:`) i komentarze (`--write-comments`) wiszą na yt-dlp, który **nie jest zainstalowany** i bywa blokowany/wolny. Mitygacja: Faza −1 instaluje i smoke-testuje; **jawne fallbacki** (ręczne incognito dla census; komentarze best-effort, finalists-only); backoff/retry; `ytsearchN:` tylko do enumeracji podaży, nigdy jako miara popytu.
8. **Mylące „cienkie tagi" sygnału.** Cienki/pusty wynik AC zwykle = scraper zawiódł, nie = brak popytu. Mitygacja: traktować pusty wynik jako awarię narzędzia (nie dane); retest innym seedem/klientem; po naprawie dekodowania sprawdzić round-trip diakrytyków.
9. **Niedopasowanie demografii sąsiadów.** Duży polski kanał psych nie dowodzi DOKŁADNIE hipotezy widowni SENSUM (45+, mniejsze miasta, TV, skos ku kobietom). Mitygacja: w Z2/tie-breakach preferować dowody na clusterze relacyjnym/rodzinnym; pętla własnych danych ze Studio (Faza 4) jako ostateczny weryfikator demografii po publikacji.
10. **Ograniczenie narzędziowe (skasowany Intelligence).** Płatne YouTube Data API niedostępne (moduł `tools/intelligence/*` usunięty, potwierdzone w git status) — brak danych retencji/demografii/velocity na cudzych filmach. Cały model jest świadomie zbudowany na darmowych substytutach; cytat o reużyciu commita 07e885d wycofany (kod skasowany i był i tak ekstraktorem słów, nie detektorem języka). Domknięcie pętli przez WŁASNE dane YouTube Studio (darmowe, nie wymaga Data API).
11. **Google Trends nie jest swobodnie scrapowalny (token-handshake; gołe GET → 400) i bywa 429.** Mitygacja: Trends zdegradowany z per-kandydat gate'u do **finalists-only** checku; „evergreen" dowodzony przede wszystkim strukturą archetypu A (rany evergreen w katalogach lane-kanałów), Trends jako potwierdzenie tam, gdzie osiągalne; `pytrends` z obowiązkowym backoff/retry i oczekiwanym częściowym pokryciem; gdy Trends-head-to-head niedostępny dla testu bilingual — fallback do porównania obecności PL-idiomu vs anglicyzmu w AC.

---

### Załącznik: pliki kodu istotne dla wykonalności (zweryfikowane)

- `tools/pipeline/agent8_publish.py`: `_load_narration` (L104–115, wymusza istniejący slug+skrypt → `--signals` niewycelowalny w kandydata), `_scrape_suggestions` (L482–499, hardcoded `client=youtube&ds=yt`, regex JSONP `\((\[.+\])\)`), `_alphabet_soup` (L502–507), `run_signals` (L823–862). **Reużywalne standalone: tylko `_scrape_suggestions` + `_alphabet_soup`** → wydzielić do `tools/niche_signals.py`.
- Skasowane (git status `D`): całe `tools/intelligence/*` (w tym `analyzer.py` z commita 07e885d) — **nie istnieje w żywym drzewie, nie cytować jako reużywalne.**
- `requirements.txt`: z istotnych zależności obecny tylko `requests` — `yt-dlp`, `pytrends`, `langdetect` do dopisania i smoke-testu w Fazie −1.
