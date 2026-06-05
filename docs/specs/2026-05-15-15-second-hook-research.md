# Hook 15 sekund: research i zasady robocze

Generated: 2026-05-15 (PL localization: 2026-06-05)
Status: Living doc — aktualizuj, gdy kanał uczy się, co utrzymuje widza.
Owner: SENSUM (kanał psychologiczny) — system hooka.
Used by: [tools/pipeline/agent4_hook.py](../../tools/pipeline/agent4_hook.py), [workflows/pipeline/04_hook.md](../../workflows/pipeline/04_hook.md), [workflows/pipeline/03a_drafter.md](../../workflows/pipeline/03a_drafter.md).

> **Lokalizacja PL (2026-06-05).** Przykłady przepisane na polski w głosie kanału (ciepły terapeuta / reportaż psychologiczny), z usuniętym research-framingiem (mówca po prostu wie — żadnego „naukowcy odkryli / badania pokazują" w hooku) i z zachowaną bezrodzajowością (czas teraźniejszy / formy bezosobowe). Teoria (sekcje 1–2) zlokalizowana. Egzekucja reguł żyje w `04_hook.md` — ten doc jest źródłem teorii i wzorców.

---

## TL;DR

Pierwsze **15 sekund** to moment, w którym YouTube decyduje, czy pokaże film większej liczbie osób, a mózg widza decyduje, czy zostaje, czy scrolluje dalej. Obie decyzje zapadają, zanim podasz choć jeden fakt. Ten dokument to robocza teoria, której hook refiner (Agent 4) używa do punktowania i przepisywania otwarcia każdego skryptu.

- Budżet czasu: **15 sekund ≈ 37 słów** przy tempie narracji kanału (~130 wpm po polsku).
- Otwarcie 15 sekund musi zrobić cztery rzeczy w tej kolejności: **przyciągnij uwagę → otwórz pętlę → wyląduj konkretem → wyzwól identyfikację**.
- Wszystko, co w pierwszych 37 słowach nie służy tym czterem ruchom — wytnij.

---

## 1. Dlaczego 15 sekund (mechanika algorytmu)

### Co YouTube faktycznie nagradza

System rekomendacji YouTube nie „czyta" twojego skryptu. Czyta zachowanie widzów na twoim filmie i używa go do przewidzenia, jak zachowa się następny widz. Okno 0–15 sekund dominuje w tej prognozie z trzech powiązanych powodów:

**CTR daje wyświetlenie. Retencja je utrzymuje.** Miniatura i tytuł zarabiają na kliknięcie. Ale w chwili, gdy widz włącza odtwarzanie, system zaczyna mierzyć inny sygnał: czy zostaje? Jeśli znacząca część widzów odpływa w pierwszych 15 sekundach, system czyta to jako „ta treść nie dostarcza tego, co obiecało kliknięcie" — i tłumi przyszłe wyświetlenia, niezależnie od tego, jak dobra jest reszta filmu.

**Średni czas oglądania to krzywa, nie średnia.** YouTube nie patrzy tylko na średni czas — patrzy na kształt krzywej retencji. Filmy, które utrzymują widzów przez sekundy 0–15, mają krzywą „front-loaded" i są systematycznie preferowane w Browse i Suggested. Filmy, które tracą 30%+ w pierwszych 15 sekundach, są czytane jako mające „zepsute intro", nawet jeśli ich retencja w dalszej części jest świetna.

**Wkład w sesję liczy się bardziej niż sam czas oglądania.** YouTube optymalizuje pod łączny czas spędzony na platformie, nie tylko na twoim filmie. Film, który utrzymuje widza w pierwszych 15 sekundach, podtrzymuje sesję — widz jest już dość zaangażowany, żeby obejrzeć coś po tobie. To właśnie awansuje film z Suggested do Home / Browse.

### Jak próg 15 s waży się na różnych powierzchniach

- **Browse (Home).** Widzowie są w stanie najniższego zaangażowania — niczego nie szukali. Dominuje odpływ w 0–15 s. Słabe intro jest tu zabójcze.
- **Suggested (panel boczny / „Następny").** Widzowie właśnie skończyli inny film. Są bardziej wyrozumiali przez pierwsze ~5 sekund, ale mocno karzą wolne rozwijanie do sekundy 15.
- **Wyszukiwarka.** Widzowie chcieli dokładnie tego, czego szukali. Tolerują wolniejsze otwarcie, ale tylko jeśli pierwsze 15 s potwierdza, że są we właściwym miejscu. Hook, który grzebie temat, traci ich.

### Mity do odrzucenia

Poniższe **nie** pomagają realnie w pierwszych 15 sekundach. Przestań pod nie optymalizować:

- Gęstość słów kluczowych w intro (system nie transkrybuje-i-rankuje w czasie rzeczywistym pod ranking).
- Branding kanału (watermark, plansza z logo, animacja intro). Wszystko to konkuruje z hookiem o budżet uwagi, którego nie masz.
- Liczba subów, wiek kanału, staż w niszy. Żadne z nich nie jest wejściem do sygnału retencji pierwszych 15 s.
- Mówienie „zasubskrybuj", „polub", „zostań z nami" w otwarciu. To aktywnie szkodzi retencji, bo sygnalizuje transakcyjnego twórcę, a nie opowiadaną historię.

---

## 2. Dlaczego 15 sekund (psychologia uwagi)

Algorytm karze odpływ w 15 sekundzie, bo mózg widza już zdecydował. Tę decyzję napędza pięć mechanizmów.

### Odruch orientacyjny

Gdy pojawia się nowy bodziec, mózg uruchamia mimowolny skan 0,5–2 s, by odpowiedzieć na jedno pytanie: *czy to warte przetwarzania?* Tętno spada, uwaga się zawęża, wzrok się blokuje. Werdykt zapada, zanim język zostanie w pełni przetworzony. To znaczy, że pierwszy **dźwięk** i pierwszy **obraz** ważą więcej niż pierwsze zdanie — ale pierwsze zdanie musi wylądować, zanim werdykt orientacyjny wygaśnie (~2 s). Jeśli twoja linia otwarcia w 2. sekundzie wciąż ładuje abstrakcyjne pojęcia, werdykt idzie przeciw tobie.

### Luka ciekawości

Mózg odruchowo zamyka luki informacyjne. Jeśli podasz fakt, mózg go kataloguje i odpuszcza. Jeśli podasz fakt z dziurą — sprzeczność, nazwa bez desygnatu, skutek bez przyczyny — mózg *nie może* go skatalogować, a odpuszczenie staje się fizycznie niewygodne. Hook otwiera pętlę, którą ciało chce zamknąć.

Konkretnie: do słowa 37 widz powinien trzymać w głowie nierozwiązane pytanie, którego 15 sekund wcześniej nie miał. Nie mgliste „ciekawe, co dalej" — konkretne pytanie o określonym kształcie.

### Błąd predykcji i nowość

Dopamina uwalnia się, gdy wynik łamie przewidywanie. Hook powinien złamać przewidywanie w pierwszych 5 sekundach — stwierdzając coś, co widz uważał za prawdę, i ujawniając, że nie jest; nazywając objaw, o którym widz nie wiedział, że ma nazwę; albo łącząc dwie rzeczy, o których widz nie wiedział, że są połączone. Sygnałem jest nowość *przeciw istniejącemu przekonaniu*, nie nowość w izolacji.

### Identyfikacja

Widz nie utrzyma uwagi przy treści, którą czyta jako „o innych ludziach". Do końca 15 sekund (słowo 37) widz musi mieć co najmniej jeden moment *to ja, dokładnie ja*. Wyzwalaczem jest zwykle konkretny szczegół — postawa, pora dnia, wewnętrzny monolog — który widz rozpoznaje z własnego życia. Statystyki nie wyzwalają identyfikacji. „Wielu ludzi" nie wyzwala identyfikacji. Konkretna scena — tak.

### Sufit obciążenia poznawczego

Mowa jest przetwarzana inaczej niż tekst pisany. Widz słucha, nie czyta ponownie. Pierwsze zdanie musi zmieścić się w jednym kawałku pamięci roboczej:

- **≤ 14 słów.**
- **Konkretny podmiot** (osoba, moment, miejsce, część ciała) — nie abstrakcyjny rzeczownik.
- **Bez stackowanych abstrakcji** (unikaj „relacji między obciążeniem poznawczym a regulacją emocji").
- **Jedna klauzula na zdanie**, najwyżej dwie.

Poniżej tego sufitu widz przetwarza zdanie jednym tchem i jest gotów na następne. Powyżej — zostaje w tyle, a zostać w tyle w pierwszych 5 sekundach to funkcjonalnie scroll dalej.

### Stos „zatrzymaj scrolla"

W praktyce mechanizmy się kumulują. Najmocniejsze hooki dostarczają w 5 sekund:

1. Obraz, który trzyma — twarz, dłoń, pojedynczy przedmiot, cokolwiek, co przeżyje odruch orientacyjny.
2. Atak audio — głos w pierwszych 1,5 sekundy, bez intro muzycznego, bez ciszy.
3. Zdanie, które ląduje sprzecznością lub konkretną sceną — konkret, ≤14 słów, bez preambuły.

Gdy wszystkie trzy odpalają razem, werdykt orientacyjny wraca *tak*, a kolejne 30 sekund spędzasz na zarabianiu retencji, a nie na walce o kliknięcie.

---

## 3. Anatomia 15 sekund (sześć wzorców hooka)

Każdy wzorzec to szablon strukturalny, nie skrypt. Każdy jest sparowany z architekturą z [workflows/guides/narrative_architectures.md](../../workflows/guides/narrative_architectures.md). Przykłady są w głosie kanału — nisza psychologiczna, estetyka dwubarwnego sztychu, bez listicle energy, bez research-framingu (mówca po prostu wie).

### Wzorzec 1 — Anomalia (The Anomalous Case)

**Parowanie:** Forensic Case Study.

**Kiedy użyć:** temat ma dziwny objaw lub skrajną manifestację. Widz ma pomyśleć „to nie może być prawda" w pierwszych trzech sekundach.

**Szablon:**
> [Konkretna pora / miejsce / stan ciała]. [Konkretny objaw fizyczny]. [Banalne wyjaśnienie, które zawodzi]. [Nazwa tego, co naprawdę się dzieje].

**Przykład (≈34 słowa, zdanie 1 = 2 słowa):**
> Sobotni poranek. Budzisz się z bólem głowy, jakby ktoś naciskał kciukami za oczami. Myślisz, że się rozchorowujesz. Nie rozchorowujesz się. To, co się dzieje, nie ma nic wspólnego z wirusem — i ma swoją nazwę.

### Wzorzec 2 — Odwrócona prawda (The Inverted Truth)

**Parowanie:** Historical Reversal.

**Kiedy użyć:** istnieje przekonanie, które większość widzów wciąż trzyma, a które wiedza obaliła. Szok odwrócenia jest hookiem.

**Szablon:**
> [Postaw starą „prawdę", jakby nadal była prawdą]. [Beat pauzy]. [Linia, która ją łamie]. [Konkretna konsekwencja, którą widz czuje].

**Przykład (≈30 słów, zdanie 1 = 9 słów):**
> Przez lata powtarzano, że złość trzeba z siebie wyrzucić — wykrzyczeć, rozładować, żeby nie zatruwała od środka. To nieprawda. Wyrzucanie złości jej nie rozładowuje. Ćwiczy ją. A ciało się tego uczy.

### Wzorzec 3 — Pytanie wprost (The Direct Question)

**Parowanie:** Socratic Challenge.

**Kiedy użyć:** widz zadawał sobie to pytanie w głowie. Postawienie go czysto jest hookiem. **Nie łagodź go. Nie zaczynaj na nie odpowiadać.**

> **Uwaga (kluczowe rozróżnienie).** Pytanie ma być **konkretne i presuponujące** — takie, które zakłada konkretną scenę, w której widz już był. **Nie** ogólne tak/nie. Zbanowane: „Czy czułeś kiedyś wstyd?" (niskostawkowe — widz odpowiada w pół sekundy i nic go nie ciągnie dalej; red flag −1). Mocne: pytanie, które od razu sadza widza w konkrecie.

**Szablon:**
> [Pytanie, ≤12 słów]. [Dlaczego większość odpowiedzi jest błędna]. [Wskazówka, że istnieje inna odpowiedź].

**Przykład (≈34 słowa, zdanie 1 = 8 słów):**
> Dlaczego pamiętasz każdy wstydliwy moment ze swojego życia? Powiedzą ci, że mózg po prostu trzyma się bólu. To prawda tylko w połowie. Druga połowa jest dziwniejsza — i robi to celowo.

### Wzorzec 4 — Obraz cielesny (The Visceral Image)

**Parowanie:** Forensic Case Study lub Systems Audit.

**Kiedy użyć:** temat ma konkretną manifestację fizyczną. Hookiem jest sam obraz, opisany na tyle precyzyjnie, że widz go czuje.

**Szablon:**
> [Konkretna scena — ciało, gest, przedmiot]. [Wewnętrzne wrażenie]. [Rama: co naprawdę dzieje się pod spodem].

**Przykład (≈33 słowa, zdanie 1 = 5 słów):**
> Twoja szczęka jest teraz napięta. Mięśnie tuż pod uszami trzymają stały, drobny nacisk, którego nie zauważasz, dopóki ktoś go nie nazwie. To napięcie to nie nawyk. To coś, co twój mózg przewidział.

### Wzorzec 5 — Autotest (The Self-Audit)

**Parowanie:** Systems Audit.

**Kiedy użyć:** temat to wzorzec, który widz prawdopodobnie już przejawia. Każ mu przetestować się na żywo.

**Szablon:**
> [Konkretne zachowanie do sprawdzenia]. [Drugie zachowanie]. [Trzecie zachowanie]. [Wzorzec, który ta trójka ujawnia].

**Przykład (≈35 słów, zdanie 1 = 10 słów):**
> Policz, ile razy w ciągu najbliższej minuty sięgniesz po telefon. Zauważ, czy robisz to, gdy nic nie zawibrowało. Czy odblokowujesz go i od razu blokujesz z powrotem. Ta pętla ma swój mechanizm — i to nie nuda.

### Przykład dla tematu: wstyd (Obraz cielesny + Autotest)

Modelowy przypadek — pokazuje, dlaczego konkretna scena bije ogólne pytanie „czy czułeś kiedyś wstyd?".

**Mocny (≈35 słów, zdanie 1 = 12 słów):**
> Wracasz myślą do czegoś sprzed lat i ciało reaguje, zanim zdążysz pomyśleć.
> Gorąco w twarzy, ucisk w klatce.
> Nikogo nie ma w pokoju, a ty kulisz się tak, jakby ktoś właśnie to zobaczył.

Otwarta pętla: dlaczego ciało wstydzi się przed pustym pokojem? Identyfikacja: widz rozpoznaje własną reakcję. Słowo „wstyd" nie pada — scena robi robotę.

**Referencyjny (Autotest, 10/10 z `3_wstyd_za_wlasne_zycie`):**
> Budzik dzwoni o piątej. Wczoraj obiecałeś sobie, że dziś wstaniesz i pobiegniesz. Wyłączasz go i śpisz dalej.

**Zbanowane (dwa red flagi: pytanie retoryczne + „większość z nas"):**
> ~~Czy czułeś kiedyś wstyd? Większość z nas dobrze go zna.~~

Ogólne pytanie tak/nie jest niskostawkowe — widz odpowiada w pół sekundy i nic go nie ciągnie dalej. Konkretna scena, w której widz JEST, bije abstrakcyjne pytanie.

### Wzorzec 6 — Ujawnienie stawki (The Stakes Reveal)

**Parowanie:** dowolna architektura, zwłaszcza Systems Audit i Historical Reversal.

**Kiedy użyć:** temat dotyczy czegoś, co widz po cichu traci, nie zdając sobie sprawy — sen, pojemność, czas, dynamika w relacji. Nazwij stratę precyzyjnie.

**Szablon:**
> [Rzecz, którą widz uważa za w porządku]. [Konkretny sposób, w jaki się psuje]. [Fakt, że jest niewidoczna, dopóki jej nie nazwać]. [Koszt].

**Przykład (≈30 słów, zdanie 1 = 10 słów):**
> Wydaje ci się, że jedną dobrą nocą nadrobisz tę nieprzespaną. Tak to nie działa. Deficyt się sumuje, narasta po cichu, i pod koniec zwykłego tygodnia myślisz wolniej, niż ci się zdaje.

---

## 4. Red flagi i bezpieczniki 15 sekund

Każdy z poniższych w pierwszych 37 słowach wyzwala **karę −1** w refinerze i jest podstawą do przepisania.

> **Źródło prawdy egzekucji:** pełna, autorytatywna lista red flagów Tier 1 (z research-framingiem, notacją statystyczną, polskimi frazami cringe self-help i academic-textbook) żyje w `workflows/pipeline/04_hook.md`. Poniższa tabela to rdzeń teorii — jeśli kiedykolwiek się rozjadą, **bramka (`04_hook.md`) jest prawdą**, ten doc się do niej dostosowuje.

| Red flag | Dlaczego zawodzi | Kara |
|---|---|---|
| Otwiera pytaniem retorycznym („Czy kiedykolwiek…?") | Ogólne, listicle energy, uchyla się od commitmentu. | −1 |
| Prowadzi statystyką przed jakimkolwiek setupem emocjonalnym | Liczby nie wyzwalają identyfikacji. | −1 |
| Pierwsze zdanie >14 słów | Przekracza sufit obciążenia poznawczego słuchania. | −1 |
| Brak konkretnego szczegółu do słowa 25 | Widz wciąż czeka na coś konkretnego do złapania. | −1 |
| „Wielu ludzi" / „wszyscy" / „większość z nas" | Mgliste, przeciwieństwo identyfikacji. | −1 |
| Stackowane abstrakcyjne rzeczowniki w zdaniu 1 | Mózg nie przetworzy dwóch abstrakcji jednym tchem. | −1 |
| Jakakolwiek klauzula, którą można skasować bez utraty znaczenia | Wata. Budżet 15 sekund jej nie udźwignie. | −1 |
| Prosi widza o „zasubskrybuj", „polub", „zostań z nami" | Łamie immersję, sygnalizuje transakcyjnego twórcę. | −1 |
| Wspomina kanał, prowadzących, „dziś porozmawiamy o…" | Meta-framing zabija hook. | −1 |
| Research-framing („naukowcy odkryli", „badania pokazują", „z badań wynika"…) | Widz ufa mówcy, nie cytatowi. Research jest niewidoczny. | −1 |
| Notacja statystyczna / precyzyjne findings (dziesiętne, effect sizes, liczby badań/uczestników, terminy metodologiczne) | Artefakt research-paperowy zabija ciepło i identyfikację. | −1 |

### Ściąga: przepisanie w miejscu

Gdy refiner musi naprawić otwarcie, próbuje tych transformacji w kolejności:

1. **Wytnij pytanie.** „Czy zastanawiałeś się kiedyś, dlaczego X?" → „X przytrafia się prawie każdemu, a powód nie jest taki, jak myślisz."
2. **Zamień statystykę na objaw.** Prowadź *doświadczeniem* tej liczby, nie liczbą.
3. **Utnij pierwszą klauzulę.** Druga klauzula zdania otwierającego to zwykle prawdziwe otwarcie.
4. **Zamień abstrakcyjny rzeczownik na konkretną scenę.** „Regulacja emocji" → „moment, w którym czujesz ucisk w klatce, zanim w ogóle zdecydujesz, że coś czujesz".
5. **Dodaj konkretną porę lub stan ciała.** „Sobotni poranek." „Trzecia w nocy." „Twoja szczęka, teraz."

---

## 5. Załącznik kalibracyjny

### Matematyka budżetu słów

| Zmienna | Wartość |
|---|---|
| Tempo narracji kanału (polski) | ~130 wpm |
| Budżet czasu | 15 sekund |
| **Budżet słów** | **~37 słów → 37 jako cutoff** |
| Miękkie maksimum pierwszego zdania | 14 słów |
| Miękkie maksimum dowolnego zdania w pierwszych 37 słowach | 18 słów |

> **Gęstość polskiego.** Polski jest gęstszy niż angielski — 37 słów PL nadal mieści się w ~15 sekundach przy ~130 wpm. Cutoff 37 słów zostaje; zdanie 1 ≤14 słów.

### Tabela wynik → akcja

| Wynik 15 s | Akcja |
|---|---|
| 9–10 | Nagrywaj. Otwarcie robi swoje. |
| 8 | Nagrywaj. Pass refinera zakończony; bez dalszych zmian. |
| 6–7 | Refiner próbuje przepisać. Jeśli wyląduje ≥8 — nagrywaj. Inaczej eskaluj. |
| ≤5 | Refiner zużył wszystkie próby; człowiek przepisuje otwarcie ręcznie. |

### Bramka dwustopniowa (refiner)

Refiner akceptuje skrypt tylko, gdy **oba**:

- Tier 1 (okno 15 sekund, 37 słów) ma **≥ 8/10**.
- Tier 2 (hook 30 sekund, 150–200 słów) ma **≥ 7/10**.

Jeśli któryś zawiedzie po `MAX_ATTEMPTS = 3` passach przepisania, werdykt to **rewrite** i oczekuje się interwencji człowieka.

---

## Jak ten doc się aktualizuje

Gdy refiner wyprodukuje wysokopunktowy hook, który dobrze performuje w pierwszych 24 h analityki (wysoka absolutna retencja na znaczniku 15 s na publicznej krzywej retencji), skopiuj wzorzec do sekcji 3 jako nowy opracowany przykład. Gdy „zaliczający" hook *underperformuje*, dodaj tryb awarii do sekcji 4 jako nowy red flag i zaostrz odpowiednią karę w refinerze.

Doc jest prawdą teorii; refiner (`04_hook.md`) jest egzekucją.
