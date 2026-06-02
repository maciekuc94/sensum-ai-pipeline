# Architektury Narracyjne — SENSUM Skrypt SOP

Ten dokument definiuje jak Agent 3 strukturyzuje skrypty. Zastępuje poprzedni 6-sekcyjny szablon. Zarówno Agent 3 (pisanie) jak i Agent 4 (edycja) egzekwują te zasady.

**Wersja angielska:** `narrative_architectures.en.md` (referencja, nie używana przez agenty).

---

## Ograniczenie tematyczne

Każdy skrypt musi wydobyć przepaść między *tym co mózg robi automatycznie* a *tym kim człowiek wierzy że jest*. To jest rdzenna tożsamość kanału. Widz powinien skończyć film rozumiejąc coś o sobie czego wcześniej nie potrafił nazwać.

---

## Zbanowane frazy

Zasady głosowe i językowe: patrz `style_guide.md`.

**Banowane wzorce strukturalne (obowiązujące od dnia 1):**

- Numerowane listy preskrypcyjne GDZIEKOLWIEK w skrypcie. (Permission Practice była kiedyś jedynym wyjątkiem; od 2026-05-29 jest płynącą prozą — patrz niżej — więc numerowane listy są teraz zakazane wszędzie bez wyjątku.) Ostatni beat po sekcji Permission Practice musi nadal lądować na rozpoznaniu — nigdy na poradzie.
- Kończenie całego skryptu na poradzie, kroku lub jakiejkolwiek instrukcji "zrób to". Recognition close ma ostatnie słowo.
- Homework framing — "w tym tygodniu spróbuj…", "twoje zadanie to…", "zrób listę…". Sekcja Permission Practice używa języka *teraźniejszego, w ciele* ("kiedy to uderza, połóż dłoń na klatce piersiowej…"), nigdy języka future-task.
- Jakikolwiek nagłówek sekcji **wypowiedziany jako narracja** (nie mów "Teraz spójrzmy na naukę" ani podobnie). To zakaz dotyczy *mówionego* tekstu — nie dotyczy cichych nagłówków `## ` (patrz niżej).

**Nagłówki sekcji `## ` (2026-06-01):** skrypt dzielisz na ~6–12 tytułowanych sekcji nagłówkiem markdown `## ` (krótka rzeczownikowa fraza: „Obietnica czystego początku", „Praktyka powrotu", „Właściwe pytanie"). To **ciche pomoce edytorsko-czytelnicze i punkty pauzy** — nie są wypowiadane, nie są obrazami, nie wchodzą do alignmentu (downstream je pomija; eksport docx renderuje je jako Heading 2). Stawiaj je na naturalnych granicach pauz; PP i recognition close dostają własne sekcje. Nie numeruj ich i nie zamieniaj w zdania narracji.

**Wyjątek Darwin:** Skrypty Historical Reversal mogą wymieniać Darwina jako strukturalnego antagonistę ("błędny pogląd" który jest odwracany). To narracyjny zabieg, nie cytat. Wszyscy inni historyczni figurzy, badacze i badania pozostają niewidoczni.

**Wyjątek kotwicy klinicznej (2026-06-01, analog Darwina):** **dokładnie jedna** utrwalona kotwica kliniczna na skrypt (np. „efekt świeżego startu" / fresh-start effect) może być nazwana i oprawiona „Badania nad [efektem] pokazują, że…" — świadomy zabieg. To jedyny dozwolony wyłom w research-invisible; druga taka ramka, autorzy, lata czy liczby pozostają zakazane.

**Zastępstwo to nie inna fraza — to nieobecność.** Nie zamieniaj "badania pokazują X" na "z analiz wynika X". Stwierdź X. Mówca po prostu wie.

---

## Zbanowane wzorce strukturalne (z polskiego pisania, dopisywane empirycznie)

**Identyfikowane 2026-05-25 z pierwszego polskiego skryptu testowego** — to są wzorce które emergują kiedy model "tłumaczy" angielską strukturę zdania na polski zamiast pisać polski natywnie. Egzekwowane przez 3a (nie pisz), 3b (flaguj), 4a (przepisz).

**1. Spójnik na początku zdania — OSZCZĘDNIE, nie nawykowo** (`I`, `Bo`, `A`, `Ale`, `Bowiem`, `Albowiem`)
- DOZWOLONE świadomie, dla rytmu mowy: *"A to dwa różne alarmy."* (kontrast-uderzenie) / *"I tu jest problem."* (zwrot na granicy beatu). Mowa na głos znosi pojedynczy spójnik tam, gdzie tekst pisany by go nie zniósł.
- ŹLE jako nawyk-kalka sklejający kolejne zdania: *"I jest to wrażenie. I to konkretne. I coś się włączyło."* / *"Bo coś się włączyło w twojej głowie."* — to kalka z "And.../Because..." i sygnalizuje tłumaczenie.
- TEST: czy to świadome uderzenie rytmiczne na granicy beatu (OK), czy leniwe sklejenie zdań spójnikiem (źle)? Jeśli pojawia się więcej niż okazjonalnie — przepisz. Domyślnie nadal preferuj zdanie bez spójnika na początku.

**2. Zakaz anthropomorfizacji uczuć i pojęć abstrakcyjnych**
- ŹLE: *"To wrażenie ma imię w twojej głowie."* / *"Lęk mieszka w twojej klatce piersiowej."* / *"Wstyd krzyczy w tobie."*
- DOBRZE: *"To wrażenie nazywasz w głowie 'jestem w tyle'."* / *"Lęk czujesz w klatce piersiowej."* / *"Wstyd uderza w tobie głośno."*
- DLACZEGO: Anthropomorfizacja uczuć ("ma imię", "mieszka", "krzyczy") brzmi po polsku jak Tumblr poetry albo Instagram caption coacha. Polska intymność terapeutyczna mówi *co robisz z uczuciem* (czujesz, nazywasz, zauważasz), nie *co uczucie robi z tobą*.

**3. Zakaz kalk strukturalnych [rzeczownik abstrakcyjny] + [rzeczownik abstrakcyjny]**
- ŹLE: *"wadą charakteru"* (← character flaw) / *"twoim charakterem"* (← your character) / *"twoja siła woli"* (← your willpower) / *"jakość twojego życia"* (← quality of your life)
- DOBRZE: *"wadą"* / *"twoją cechą"* lub po prostu *"tobą"* / *"silna wola"* / *"jak żyjesz"*
- DLACZEGO: Polski nie układa rzeczowników w pary tak jak angielski. "Character flaw" tłumaczy się jako "wada", nie "wada charakteru". Sprawdź każdy genitiv — czy ten drugi rzeczownik faktycznie cokolwiek dodaje, czy jest tłumaczeniem angielskiego rzeczownik+rzeczownik.

**4. Zakaz mieszania semantycznych kategorii w listach uderzających**
- ŹLE: *"Wyżej. Niżej. Bezpiecznie. Niebezpiecznie."* (hierarchia + stan bezpieczeństwa = różne wymiary)
- DOBRZE: *"Wyżej. Niżej. Na równi. Daleko."* (wszystko hierarchia/odległość) lub *"Bezpiecznie. Niebezpiecznie. Czujnie. Spokojnie."* (wszystko stan)
- DLACZEGO: Listy uderzające (krótkie zdania jedno po drugim) działają tylko jeśli wszystkie elementy są tej samej kategorii. Mieszanie kategorii sprawia że widz podświadomie czuje że coś nie pasuje, traci uderzenie.

**5. Zakaz pretensjonalnych metafor mieszających różne domeny**
- ŹLE: *"Trzysta cudzych szczytów przeciwko twojej pełnej topografii."* (szczyty + topografia + "przeciwko" = trzy domeny niespójnie połączone)
- DOBRZE: *"Trzysta cudzych zdjęć z wakacji. I twoje wszystkie wieczory na kanapie."* (jedna konkretna domena: zdjęcia vs codzienność)
- DLACZEGO: Mieszane metafory ("szczyty topografii", "ocean myśli", "labirynt serca") brzmią po polsku jak licealny esej maturalny. Polski reportaż psychologiczny używa JEDNEJ konkretnej domeny per metafora — nigdy nie miesza. Konkret bije ozdobę.

**6. Zakaz literackich ozdobników i "eleganckich synonimów"**
- ŹLE: *"odczuwa wewnątrz siebie ten ciężar"* / *"doświadcza tej dotkliwej obecności"* / *"manifestuje się w tobie ten stan"*
- DOBRZE: *"czujesz ten ciężar"* / *"to cię uderza"* / *"to się w tobie dzieje"*
- DLACZEGO: Polski ma tendencję do "elegantyzacji" — sięgania po dłuższe, bardziej literackie synonimy. To brzmi jak referat semestralny, nie jak ciepły terapeuta. Najprostsze słowo jest zawsze najmocniejsze.

**7. Zakaz meta-zapowiedzi**
- ŹLE: *"Teraz patrzymy gdzie ten system się psuje."* / *"Teraz spojrzmy na mechanizm."* / *"Zobaczmy razem co się dzieje."* / *"Przyjrzyjmy się temu."*
- DOBRZE: Po prostu otwórz treść następnej sekcji bez zapowiadania jej. *"System psuje się w jednym miejscu."*
- DLACZEGO: Meta-zapowiedź zatrzymuje narrację żeby powiedzieć widzowi co za chwilę nastąpi — zamiast żeby to po prostu nastąpiło. Brzmi jak nauczyciel który mówi "teraz omówimy". Skrypt nie zapowiada — działa.

**8. Jedna główna metafora na skrypt — nie nakładaj pobocznych** (dopisane 2026-05-29 z pilota slug 2)
- ŹLE: centralny motyw (notatnik) + obok niego *podatek, dom na wodzie, bak paliwa, loteria charakteru, konto zaufania, cmentarz, maszyna* — siedem pobocznych obrazów na jeden skrypt. Każdy osobno bywa OK; razem dają przeładowanie i widz gubi centralny obraz.
- DOBRZE: jeden centralny motyw (notatnik / krzesło / nić) niesie cały skrypt; poboczne metafory rzadkie i tylko gdy naprawdę potrzebne. Jeśli zdanie da się powiedzieć prosto, bez kolejnej metafory — powiedz prosto.
- DLACZEGO: przeładowanie metaforami brzmi jak popisywanie się, nie jak rozmowa. W Composite Portrait przedmiot-motyw JEST tą jedną metaforą — chroń go, nie zagłuszaj.
- TEST: policz odrębne domeny metafor. Więcej niż ~2 (centralny motyw + najwyżej jedna load-bearing poboczna) = tnij.

**Test lakmusowy dla całego skryptu:** Czy ten skrypt mógłby napisać ktoś kto myśli po polsku, czy brzmi jak ktoś tłumaczący angielską strukturę? Jeśli choć raz na akapit pojawia się wzorzec 1-8 — to jest tłumaczenie, nie polskie pisanie.

---

## Pięć Architektur Narracyjnych

Agent 3 deklaruje architekturę na **pierwszej linii** outputu skryptu. **Domyślną architekturą jest `Composite Portrait`** — Agent 3 używa jej, chyba że wywołanie `/draft` jawnie poda nazwę innej architektury. Wszystkie pięć architektur pisze się na natywną długość kanału **~10–15 min**:

```
ARCHITECTURE: [Composite Portrait | Forensic Case Study | Historical Reversal | Socratic Challenge | Systems Audit]
```

(Nazwy architektur pozostają po angielsku jako wewnętrzne identyfikatory używane przez agenty downstream.)

Architektura to **kształt**, nie sztywny szablon. Używaj jej do określenia punktu wejścia i przewodniej osi — nie jako checklisty.

---

### Architektura 1 — Forensic Case Study (Studium Kryminalistyczne)

**Kiedy używać:** Temat ma dziwną, kontrintuicyjną lub ekstremalną manifestację — symptom, studium przypadku, zachowanie które wydaje się niemożliwe dopóki nie zrozumiesz mechanizmu.

**Punkt wejścia:** Otwórz konkretnym dziwnym symptomem, udokumentowanym przypadkiem lub anomalią biologiczną. Czymś co sprawia że widz myśli: *to nie może być prawda*.

**Wymagane węzły treściowe:**
1. Symptom lub przypadek — opisany w precyzyjnym, konkretnym szczególe
2. Mechanizm wewnątrz — co naprawdę dzieje się w mózgu lub ciele, opisane jako zwykła rzeczywistość. Nie *"co naukowcy odkryli"*; mówca po prostu wie.
3. Sprawca — konkretna przyczyna, wyjaśniona językiem codziennym, bez jargon-first translations.
4. Zwyczajna implikacja — co ten ekstremalny przypadek ujawnia o codziennym doświadczeniu widza

**Ograniczenie close:** Po sekcji Permission Practice (patrz universal section niżej), zakończ implikacją dla życia widza. Moment rozpoznania jest OSTATNIM beatem — tipy są beatem przed nim, nie destynacją.

---

### Architektura 2 — Historical Reversal (Odwrócenie Historyczne)

**Kiedy używać:** Istnieje przekonanie traktowane jako ustalona prawda 30–50 lat temu, które zostało znacząco obalone przez badania 2020–2026.

**Punkt wejścia:** Stwierdź starą "prawdę" jakby nadal była prawdziwa — potem ujawnij że nie jest. Szok tego odwrócenia jest hookiem.

**Wymagane węzły treściowe:**
1. Stare przekonanie — wypowiedziane prosto, tak jak większość ludzi nadal je trzyma
2. Prawda która je obala — wypowiedziana jako nieuchronny fakt, nie jako ostatnie odkrycie. Nie *"badanie z 2019 ujawniło"* ani *"badania teraz pokazują"* — po prostu nowa prawda, wypowiedziana wprost. (Wyjątek Darwin: *historyczna* postać która jest obalana może być nazwana jako narracyjny zabieg.)
3. Jak to naprawdę działa — opisane jako codzienna obserwacja, nigdy jako *"co nowe badania ujawniają"*. Mechanizm pojawia się jako oczywisty z perspektywy czasu.
4. Przepisanie — co widz teraz rozumie co przeczy temu czego go uczono

**Ograniczenie close:** Po sekcji Permission Practice, zakończ na tym co widz teraz wie czego większość ludzi nie wie. Ciężar wiedzy o tym jest OSTATNIM beatem — tipy są beatem przed nim.

---

### Architektura 3 — Socratic Challenge (Wyzwanie Sokratejskie)

**Kiedy używać:** Temat ma pytanie w rdzeniu — coś co widz prawdopodobnie zadawał sobie ale nigdy nie dostał satysfakcjonującej odpowiedzi. Pytanie wystarczająco trudne że nie można na nie odpowiedzieć od razu.

**Punkt wejścia:** Zadaj pytanie bezpośrednio. Nie łagodź go. Nie zaczynaj natychmiast odpowiadać.

**Wymagane węzły treściowe:**
1. Pytanie — postawione czysto i pozostawione otwarte
2. Krok logiczny 1 — pierwsza rzecz którą musisz zrozumieć żeby zbliżyć się do odpowiedzi
3. Krok logiczny 2 — następna warstwa
4. Krok logiczny 3 — element który sprawia że odpowiedź jest nieuchronna
5. Odpowiedź — powinna wyglądać jakby widz sam ją wypracował
6. Pytanie przeformułowane — wróć do pytania otwierającego, teraz z innym znaczeniem

**Ograniczenie close:** Po sekcji Permission Practice, ostatnia linia powinna echo otwierającego pytania, ale odpowiedź jest teraz oczywista. Przeformułowane pytanie jest OSTATNIM beatem — tipy są beatem przed nim.

---

### Architektura 4 — Systems Audit (Audyt Systemu)

**Kiedy używać:** Temat dotyczy powtarzającego się wzorca, pętli sprzężenia zwrotnego, lub mechanizmu behawioralnego który można zrozumieć jako system z wejściami, wyjściami i trybami awarii.

**Punkt wejścia:** Opisz mózg lub zachowanie jako złożony system. Używaj terminów inżynieryjnych w prostym polskim — opóźnienie (latency), pętla rekurencyjna, cache, przepustowość, tryb awarii, sygnał, override. Trzymaj ton precyzyjny i chłodny, nie kliniczny.

**Wymagane węzły treściowe:**
1. Opis systemu — czym jest i co jest zaprojektowany żeby robić
2. Tryb awarii pod lupą — co się psuje i jak
3. Wyzwalacz — co aktywuje tryb awarii
4. Co system *naprawdę* optymalizuje — często inne niż osoba myśli
5. Diagnostyczna konkluzja — co zachowanie systemu ujawnia

**Ograniczenie close:** Po sekcji Permission Practice, zakończ tym czego system *potrzebuje* — nie tym co *osoba powinna zrobić*. System ma własną logikę. Uszanuj ją. To stwierdzenie logiki systemu jest OSTATNIM beatem — tipy są beatem przed nim.

---

### Architektura 5 — Composite Portrait (Portret Złożony) — DOMYŚLNA

**To jest DOMYŚLNA architektura kanału.** Pozostałe cztery wybierasz tylko gdy wywołanie `/draft` poda nazwę architektury jawnie.

**Kiedy używać:** Domyślnie. Temat da się ucieleśnić w jednej rozpoznawalnej postaci — kimś, kogo zachowanie widz zna z siebie. Śledzimy tę jedną postać przez cały film; widz rozpoznaje w niej siebie.

**Punkt wejścia:** Wejdź w postać w trakcie konkretnego, drobnego, rozpoznawalnego zachowania, które wygląda jak wada. Hook to **„no wonder"** — dziwne zachowanie, które za chwilę okaże się sensowne. Tu wprowadź **przedmiot-motyw**: jeden konkretny obiekt (krzesło, drzwi, kamień, nić), który będzie wracał przez cały film.

**Głos — pełne „ty" (zmiana 2026-05-29):** Cała architektura w **drugiej osobie**, jak reszta kanału. Postać-archetyp to *ty* — widz jest tą postacią od pierwszego zdania (*„Kupujesz nowy notatnik…"*), nie obserwujesz jej z zewnątrz. **Nie prowadź postaci w 3. osobie** („ktoś", „ta osoba", „on/ona") — to brzmi po polsku dystansująco i sztucznie (zweryfikowane na pilocie slug 2). Poprzedni „splot" (3. osoba + fold-backi „ty") został **wycofany**. Postać pozostaje **archetypem/kompozytem** — bez imienia, bez biografii realnej osoby (wyjątek Darwin nadal dotyczy tylko Historical Reversal); po prostu prowadzona przez „ty".

**Cztery ruchy (wymagane węzły treściowe):**
1. **The Surface (Powierzchnia)** — konkretne, rozpoznawalne zachowanie wyglądające jak wada. Wprowadzenie przedmiotu-motywu. Tu żyje hook „no wonder".
2. **The Cost (Koszt)** — co to zachowanie kosztuje postać; cichy ciężar pod spodem. Jeszcze nie mechanizm — odczuwalna waga. Budujemy więź z postacią (= z widzem).
3. **The Origin (Źródło)** — skąd to się bierze; mechanizm opowiedziany jako historia/biologia postaci, nigdy jako research. Wypłata „no wonder": zachowanie przestaje być wadą — jest adaptacją. Moment exoneracji.
4. **The Reframe (Przepisanie)** — postać (i widz) widzi wzorzec inaczej. Nie naprawiony — zrozumiany. Wstyd opada.

**Spoiwo (lek na „mulisty środek"):** Jedna powracająca postać (ta sama sylwetka, ewoluująca postura) + jeden powracający przedmiot-motyw, który wraca transformowany w każdym ruchu i przy close. To zamienia pokaz slajdów w wizualną narrację — oś, która trzyma narracyjny łuk i nie pozwala mu obwisnąć w środku.

**Długość:** ~1,500–1,750 słów polskich = ~10–15 min (natywna długość kanału; gęstość obrazów bez zmian — jedno zdjęcie na zdanie → ~140–180 obrazów).

**Ograniczenie close:** Po sekcji Permission Practice, zakończ postacią w spoczynku, z przedmiotem-motywem rozwiązanym — echo Ruchu 1 (Powierzchni), ale jeden element zmieniony. Ostatni beat to rozpoznanie / lustro do widza, nigdy porada. Permission Practice jest beatem przed nim.

**Rozwiąż na TYM SAMYM motywie (kalibracja 2026-05-30).** „Echo Ruchu 1" znaczy: ten sam przedmiot, jeden element zmieniony — **nie świeża instancja motywu**. Jeśli Reframe zwrócił widza ku staremu obiektowi („wyjmij ten notatnik z szuflady"), to close, który wprowadza nową kopię („pewnego dnia kupisz nowy notatnik"), rozmywa puentę „zostań przy starym". Zamknij na tym samym egzemplarzu — co się zmieniło, to nie obiekt, tylko to, co z nim robisz.

---

## Sekcja Permission Practice (uniwersalna, zamykająca)

**Każdy skrypt — niezależnie od architektury — musi zawierać sekcję Permission Practice między korpusem architektury a końcowym recognition close.** To zablokowana reguła strukturalna kanału. Sekcja daje widzowi coś konkretnego do zabrania do swojego tygodnia bez łamania anti-optimization pozycjonowania kanału.

### Umieszczenie

```
Korpus architektury (Forensic / Historical / Socratic / Systems)
  ↓
Sekcja Permission Practice  ← (ta sekcja)
  ↓
Recognition close (własny close constraint architektury — OSTATNI beat)
```

### Specyfikacja (proza — NIE numerowana lista)

**Format zmieniony 2026-05-29:** sekcja jest teraz **płynącą prozą**, nie numerowaną listą „1. 2. 3. 4.". Wzorzec wzięty z ręcznej korekty użytkownika — zmiękczone zaproszenia zamiast rozkazów. Numerowana lista w PP jest teraz ZAKAZANA (Reviewer flaguje).

- **Wejście (zmiękczone, nie nagłówek-lista):** otwórz uznaniem, że tego nie da się wyłączyć, ale czasem da się uciszyć — np. *"Kiedy [wyzwalacz powiązany z mechanizmem skryptu] uderza, nie zawsze da się go wyłączyć. Ale czasem da się go trochę uciszyć."* Wyzwalacz wiąże się ze zjawiskiem skryptu (*"kiedy unik uderza"*, *"kiedy to ląduje w ciele"*, *"kiedy pętla się włącza"*).
- **Forma = proza, zależna od rejestru (2026-06-01).** Około czterech praktyk + krótka linia unpack przy każdej. W **rejestrze somatycznym** forma to miękka anafora *"Czasem wystarczy [bezokolicznik]…"* (wariuj otwarcie ostatniej, *"A czasem wystarczy po prostu…"*, żeby nie brzmiała mechanicznie). W **rejestrze strategicznym** forma **może prowadzić trybem rozkazującym** (*"Spójrz na to, co już jest. Zrób wersję mniejszą, niż planowałeś. Zostaw rzecz na widoku."*) — pod warunkiem zachowania softenerów pozwolenia („nie musisz", „wystarczy") i ramy anty-optymalizacyjnej. W obu rejestrach: **proza, nigdy numerowana lista; zaproszenia/pozwolenie, nigdy harmonogram.**
- **Voice = ucieleśniona mikropraktyka.** Akty somatyczne (oddech, dłoń, postawa), zauważanie (lokalizowanie wrażenia w ciele), nazywanie (jedno słowo na głos), mikro-progi (napisz pierwsze zdanie, potem przestań). Rzeczy które ciało może zrobić w danym momencie, nie plany na później.
- **Softening pressure.** Każda praktyka z imperatywem ma temporalny softener: *czasem / teraz / na chwilę / tylko jedną minutę / wystarczy że / nie musisz / tam gdzie*. Bez softenerów brzmi jak prescripcja, nie pozwolenie.
- **Dociśnij, nie rozmywaj (kalibracja 2026-05-30; doprecyzowane 2026-06-01).** PP może być ostrzejsza i bardziej konkretna — tnij watę, wybieraj mocniejszy aktywny czasownik. W rejestrze strategicznym „dociśnięcie" może iść aż do trybu rozkazującego (Spójrz/Zrób/Zostaw) — ale **softener pozwolenia i rama anty-optymalizacyjna zostają zawsze**. Granica nie biegnie między „zaproszenie" a „rozkaz" (tryb rozkazujący w rejestrze strategicznym jest OK), tylko między **pozwoleniem a harmonogramem/optymalizacją**: „Zrób wersję mniejszą, niż planowałeś" = pozwolenie (OK); „Zaplanuj tydzień w blokach" = optymalizacja (zakaz). Rejestr somatyczny zostaje miękki („Czasem wystarczy…").
- **Wszystkie istniejące voice rules nadal obowiązują:** bez nazwisk badaczy, bez "badania pokazują" (poza jedną dozwoloną kotwicą kliniczną w korpusie skryptu — patrz „Zbanowane frazy", wyjątek kotwicy klinicznej; w samej PP zwykle jej nie ma), bez dziesiętnych, tylko zaokrąglone liczby, najpierw prosty język.
- **Recognition close nadal ma ostatnie słowo.** Praktyki są beatem, nie destynacją.

### Dwa rejestry — somatyczny (domyślny) / strategiczny (2026-05-31)

Permission Practice ma **dwa rejestry**. Wspólne w obu: proza (nigdy numerowana lista), ~4 praktyki, softenery pozwolenia, rama anty-optymalizacyjna, recognition close po sekcji. Różni się *treść* mikropraktyk **oraz forma** (2026-06-01): somatyczny → miękka anafora „Czasem wystarczy…"; strategiczny → może tryb rozkazujący z softenerami. Który rejestr wybierasz, zależy od tematu, nie od gustu.

- **Reguła wyzwalacza:** *Czy temat daje widzowi realny ruch zewnętrzny, który mógłby zrobić w tym tygodniu — wybrać, przeramować, zbudować prosty system, świadomie coś odłożyć?*
  - **NIE** (jedyny prawdziwy ruch jest wewnętrzny — pozwolić sobie poczuć, przestać walczyć, zauważyć) → **rejestr somatyczny**. To domyślny, dotychczasowy rejestr: oddech, dłoń, postawa, nazywanie, mikro-progi. Większość tematów kanału (zazdrość, wstyd, lęk) tu należy.
  - **TAK** (temat ma genuine mapę — kariera „za dużo zainteresowań", paraliż decyzji, układanie życia wokół czegoś) → **rejestr strategiczny**: mikropraktyki **behawioralne** — wybór jednej rzeczy na sezon, odłożenie-nie-wyrzucenie, przeramowanie pracy jako gruntu, zapisanie zajawki, świadome odpuszczenie reszty.
- **Granica anty-self-help (krytyczna — rejestr strategiczny ≠ optymalizacja):** test lakmusowy poniżej obowiązuje bez zmian. Różnica między pozwoleniem a poradą: rejestr strategiczny daje *prawo* do ruchu — w prozie „Czasem wystarczy…" albo trybem rozkazującym z softenerem („Zrób wersję mniejszą, niż planowałeś. Nie chodzi o rozmiar, chodzi o powrót.") — a **nigdy** harmonogramu, listy ani zadania domowego („zaplanuj tydzień w blokach", „zrób audyt w tabeli", „w tym tygodniu spróbuj…"). Softener i rama pozwolenia zostają — to wciąż permission, nie productivity. Forma (tryb rozkazujący vs anafora) jest dozwolona; harmonogram/audyt nie.
- **Research-invisible bez wyjątku:** ruch praktyczny podajesz jako zwykłe ludzkie zaproszenie, nigdy jako nazwany framework, nazwisko ani żargon (żadnego „serial mastery / far transfer / second brain").
- **Recognition close nadal zamyka — także w rejestrze strategicznym.** Mapa jest beatem przed rozpoznaniem, nie ostatnim słowem. Nawet film, który zainspirował ten rejestr (M-shaped), kończy na rozpoznaniu („to ty łączysz rzeczy, których inni nie łączą"), nie na strategii.

### Test lakmusowy

Dla każdej praktyki zapytaj: *"Czy ta linia mogłaby pojawić się niezmieniona na blogu o produktywności lub w generycznym self-help wątku?"* Jeśli tak — źle. Przepisz jako somatyczny, zauważający lub mikro-progowy akt, w prozie *"Czasem wystarczy…"*.

### Poprawny przykład (proza, anafora „Czasem wystarczy")

```
Kiedy ten alarm uderza, nie zawsze da się go wyłączyć. Ale czasem da się go trochę uciszyć.

Czasem wystarczy zatrzymać się przy jednej rzeczy i powiedzieć sobie, że nie widzisz całej historii. Nie po to, żeby oceniać.

Czasem wystarczy położyć dłoń na klatce piersiowej, tam gdzie czujesz ten ciężar, i zrobić trzy wydechy dłuższe niż wdechy. Układ nerwowy nie słucha argumentów, ale wolny wydech odczytuje jako sygnał, że w tej chwili nic ci nie grozi.

Czasem wystarczy nazwać jednym słowem, czego ci brakuje — nie „wszystkiego", tylko jednej rzeczy. Samo nazwanie zwykle trochę porządkuje chaos.

A czasem wystarczy po prostu zauważyć, gdzie jesteś, kiedy to wraca. Nie musisz nic z tym teraz robić.
```

### Poprawny przykład — rejestr strategiczny (temat z ruchem zewnętrznym, np. „za dużo zainteresowań")

Ta sama proza i softenery co wyżej; mikropraktyki są behawioralne (wybór, odłożenie, przeramowanie), ale wciąż **pozwolenie**, nie harmonogram. Recognition close idzie PO tej sekcji.

```
Kiedy znów łapiesz się na tym, że chcesz robić wszystko naraz, nie musisz tego w sobie dusić. Ale czasem da się to trochę ułożyć.

Czasem wystarczy wybrać jedną rzecz na ten jeden sezon — nie na zawsze, na ten sezon — i dać sobie prawo odłożyć resztę. Nie wyrzucić. Odłożyć.

Czasem wystarczy zapisać gdzieś tę zajawkę, która właśnie cię złapała, i wrócić do tego, co już zacząłeś. Zapisana nie ucieka. Czeka.

Czasem wystarczy spojrzeć na to, z czego się utrzymujesz, nie jak na klatkę, tylko jak na grunt — coś, co trzyma cię stabilnie na tyle, żebyś mógł próbować dalej.

A czasem wystarczy zauważyć, że to, co braliś za rozproszenie, bywa po prostu tym, jak twoja głowa łączy rzeczy, których inni nie łączą.
```

### Poprawny przykład — rejestr strategiczny, forma rozkazująca (slug-2 „Praktyka powrotu", 2026-06-01)

Ta sama rama (pozwolenie, softenery, recognition close po sekcji), ale praktyki prowadzone **trybem rozkazującym** zamiast anaforą „Czasem wystarczy…". To wzorzec z ręcznej redakcji użytkownika — dozwolony w rejestrze strategicznym.

```
Kiedy ta pusta kratka znowu się pojawi — bo pojawi się prędzej czy później — nie musisz od razu uciszać głosu, który mówi, że wszystko przepadło. Wystarczy zrobić coś mniejszego.

Spójrz na to, co już jest. Nie po to, żeby się pocieszać, tylko żeby zobaczyć, że wcześniejsze pełne kratki nigdzie nie zniknęły.

Zrób wersję mniejszą, niż planowałeś. Jedno zdanie zamiast całej strony. Pięć minut zamiast godziny. W tej chwili nie chodzi o rozmiar — chodzi o to, żeby wrócić do następnej kratki, zamiast czekać na kolejny idealny początek.

Zostaw rzecz na widoku. Notatnik otwarty na biurku. Buty przy drzwiach. Nie musisz pamiętać o wszystkim sam, jeśli otoczenie pamięta trochę za ciebie.
```

Zwróć uwagę: „nie musisz", „wystarczy", „nie chodzi o rozmiar" — softenery pozwolenia trzymają to po stronie permission mimo trybu rozkazującego. Recognition close idzie PO tej sekcji.

### Złe przykłady (Reviewer flaguje — nie pisz)

- *"Cztery rzeczy, które możesz zrobić: 1. … 2. … 3. … 4. …"* ← stary numerowany format, zastąpiony prozą
- *"Zaplanuj tę rozmowę — nie czekaj na właściwy moment."* ← scheduling tip, optimization framing
- *"Zapisz 3 rzeczy za które jesteś wdzięczny/a."* ← list-making tip, generic self-help
- *"Porozmawiaj o tym z terapeutą."* ← outsourced action, not embodied
- *"Ustal jasne granice z szefem."* ← generic advice, not somatic
- *"W tym tygodniu spróbuj raz dziennie powiedzieć nie."* ← homework framing
- *"Praktykuj uważność 10 minut dziennie."* ← prescriptive routine, not in-the-moment
- *"Zaplanuj swój tydzień w blokach po 90 minut."* ← rejestr strategiczny ZEŚLIZGNĄŁ się w optymalizację/scheduling — to już productivity, nie pozwolenie
- *"Zrób audyt swoich zainteresowań w tabeli i oceń każde od 1 do 10."* ← homework + list-making; pozwolenie nie wystawia zadań domowych

---

## Marker `[Visual Pause]`

Używaj `[Visual Pause]` w osobnej linii żeby oznaczyć moment w którym cisza niesie więcej wagi niż słowa. Narracja milknie. Obraz trzyma.

- Maksymalnie **3–4 na skrypt**
- Umieść między zdaniami, w osobnej linii
- Używaj tylko w momentach prawdziwej wagi — objawienie, brutalna prawda, przesunięcie perspektywy
- Agent 9 (generowanie obrazów) ignoruje ten marker całkowicie; służy tylko do timingu narracji i montażu wideo

**Format:**
```
[Visual Pause]
```

---

## Mapy Rejestru Wizualnego — przeniesione

**Pełne mapy rejestru wizualnego (Mood / Compositions / Metaphor families / Scale / Avoid dla każdego beatu wszystkich pięciu architektur) żyją wyłącznie w `workflows/pipeline/05_visuals.md`** — czyta je tylko Agent 5 (wizualny). Drafter (3a), Revisor (3b) i Reviewer (3c) ich NIE potrzebują: piszą i oceniają narrację po polsku, nie prompty obrazów. Trzymanie tej kopii tutaj tylko obciążało agentów piszących tekst ~200 liniami angielskiego słownictwa wizualnego nie dla nich. Ten plik (`narrative_architectures.md`) jest teraz właścicielem **struktury narracyjnej** (kształt, ruchy, umiejscowienie Permission Practice, banowane wzorce strukturalne) — nie warstwy wizualnej.
