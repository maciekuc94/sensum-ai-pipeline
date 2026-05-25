# Style Guide — Skrypty Psychologiczne SENSUM

Referencja dla Agenta 3 (script writer) i Agenta 4 (script editor). Definiuje ton, strukturę i zasady pisania skryptów do polskich filmów psychologicznych SENSUM.

**Wersja angielska:** `style_guide.en.md` (referencja, nie używana przez agenty).

---

## 1. Tożsamość kanału

- **Nazwa kanału:** SENSUM (handle `@sensumpolska`)
- **Język:** Polski (kanał angielski `@hello.sensum` jest w stanie dormant — patrz `docs/reversibility.md`)
- **Odbiorca:** Polskojęzyczny widz zainteresowany psychologią, bez wykształcenia psychologicznego. Osoba, która ma za sobą terapię lub o niej myśli, czyta self-help, ale jest sceptyczna wobec "psychobełkotu".
- **Długość filmu:** 10–15 min (cel ~1,700 słów narracji); jeden obraz co 1–2 zdania (~40–60 obrazów na film)
- **Standard naukowy:** Tylko źródła recenzowane (peer-reviewed). Bez pop-psychologii, bez pseudonauki, bez duchowego folkloru.
- **Pozycjonowanie:** Permission Psychology — naukowo ugruntowane *pozwolenie* na emocje, których widz się wstydzi. Egzonerujemy zamiast informować. Anti-optimization, anti-productivity. Tonacja: kliniczna ciepło.

## 2. Zasady tonu

- **Bezpośredni adres:** Zawsze "ty" i "twój/twoja" — mów do widza bezpośrednio.
- **Walidacja przed wyjaśnieniem:** Najpierw wyladuj uczucie. Widz musi rozpoznać siebie zanim wprowadzisz jakikolwiek mechanizm. Empatia nie jest hookiem — to cały rejestr.
- **Voice:** Ciepło i jeden na jednego — jak terapeut(k)a siedzący/a naprzeciwko widza. Nie performujesz eksperckość; oferujesz rozpoznanie. Widz ufa mówcy, nie cytatowi.
- **Research jest niewidoczny:** Pisarz czyta badania; skrypt ich nigdy nie cytuje. Bez "badania pokazują", bez "naukowcy odkryli", bez "wyniki badań wskazują", bez "psychologowie nazywają to". Odkrycia pojawiają się jako obserwacje o byciu człowiekiem, nie jako raporty naukowe. Prawdziwe cytaty bibliograficzne żyją w opisie YouTube (Agent 8), nigdy w narracji.
- **Terminy techniczne:** Zaczynaj od języka codziennego. Opisuj zjawisko, nigdy terminu. Nazwij koncept naukowy tylko jeśli (a) sama nazwa jest faktycznie zapamiętywalna i (b) pojawia się raz, późno, po tym jak idea już wylądowała w prostych słowach. Domyślnie: bez nazwy. NIE używaj wzorca jargon-then-translation ("dysregulacja emocjonalna — czyli rozregulowanie emocji…") — to brzmi jak wykład.
- **Struktura zdań:** Krótkie zdania uderzające. Fragmenty dla emfazy. Polski naturalnie preferuje dłuższe zdania podrzędne — kalibracja: jedno długie wyjaśnienie + jedno krótkie zdanie-cios (3–6 słów).
- **Pewność:** Bez hedgingu. Mów wprost. Zamiast hedgingu — bezpośrednie twierdzenia w głosie mówcy. *"Twój mózg robi X"*, nie *"Z badań wynika, że twój mózg robi X"*.
- **Gramatyka:** Unikaj bezosobowych konstrukcji ("mówi się że", "uważa się że", "powiada się"). Mów osobowo i konkretnie.
- **Otwarcia:** Bez throat-clearing ("W tym filmie omówimy...", "Dzisiaj porozmawiamy o..."). Wejście od razu w treść.
- **Rytm:** Naprzemiennie długie, złożone zdania wyjaśniające i krótkie, brutalne (2–4 słowa). Fragmenty są intencjonalne, nie błędy. Kontrast tworzy impakt.

### Liczby

Zaokrąglone, opisowe liczby tylko. *"Około połowa"*, *"większość ludzi"*, *"w wielu przypadkach"*, *"częściej niż rzadziej"*, *"spora część"*.

Nigdy nie używaj:

- Dziesiętnych (`0,62`, `37,4%`)
- Effect sizes (`d = 0,6`, `r = 0,4`, `Cohen's d`)
- p-values, przedziałów ufności, istotności statystycznej
- Liczby badań (*"meta-analiza 94 eksperymentów"*, *"w 47 badaniach"*)
- Liczby uczestników (*"8000 osób"*, *"ponad dwanaście tysięcy badanych"*)
- Terminów metodologicznych (*pre-registered, double-blind, longitudinalne, meta-analiza, kryzys replikacji*)
- Greckich liter ani notacji statystycznej w żadnej formie

Jeśli liczba nie ląduje emocjonalnie w prostym polskim — wytnij ją.

**Struktura skryptu** jest zdefiniowana w `workflows/guides/narrative_architectures.md` — ten dokument zastępuje jakąkolwiek strukturę sekcji wymienioną tutaj. Definiuje też **obowiązkową sekcję Permission Practice** (zawsze dokładnie 4 ucieleśnione mikropraktyki, ulokowane jeden beat przed recognition close). Numerowane listy preskrypcyjne są dozwolone TYLKO w tej sekcji; ostatni beat każdego skryptu nadal ląduje na rozpoznaniu, nigdy na poradzie.

## 3. Wskazówki dotyczące metafor

- Każdy koncept naukowy powinien mieć metaforę lub analogię
- Metafory powinny być nowoczesne i bliskie (kamery, komputery, RAM, ekrany wysokiej rozdzielczości, etc.)
- Jedna mocna metafora na koncept — nie mieszaj metafor
- Unikaj polskich klisz duchowo-rozwojowych ("podróż", "ścieżka", "światło wewnętrzne", "energia") — to brzmi jak New Age, nie psychologia

## 4. Markery IMAGE

- **Format:** `[IMAGE: emotion=EMOTION, perspective=PERSPECTIVE, space=SPACE, scene=description]`
  Pełna specyfikacja w `workflows/guides/style_guide_images.md` (visual bible, emotion lookup table, valid field values).
- **Częstość:** 1 obraz co 1–2 zdania — umieść jeden przy każdej nowej idei, statystyce (zaokrąglonej), metaforze, zmianie sceny. Cel: 60–80 markerów na film.
- **Umieszczenie:** Co zdanie lub dwa — nie oszczędzaj markerów tylko na przejścia między sekcjami.
- **Pole scene:** Free-form, tylko opis ciała i otoczenia. NIE dodawaj słów dotyczących palety, stylu, oświetlenia — te pochodzą z emotion lookup.
- **Język scene:** Po angielsku (Gemini Image generuje z angielskich promptów — pełna spec w `style_guide_images.md`).
- **Przykład:** `[IMAGE: emotion=FEAR, perspective=overhead, space=real, scene=A body curled on a bathroom floor, arms wrapped around knees, cool blue light seeping under the door]`

## 5. Referencja rytmu

Polski przykładowy transcript zostanie dodany po pierwszym shippnięciu polskiego video (~1,700 słów konkretnego przykładu rytmu po polsku). Do tego czasu, jako referencja rytmu (kontrast krótkich i długich zdań, fragmenty, layering empatii):

- `style_guide.en.md` — pełny angielski przykład (highly sensitive person / orchid vs dandelion), pokazuje rytmiczny kontrast. **Nie kalibruj voice z tego transcriptu** (zawiera research-framing który jest zbanowany). Czytaj go TYLKO pod kątem: długość zdań, użycie fragmentów, sposób warstwowania empatii, styl metafory.

Polski rytm: zdania średnio dłuższe niż angielskie (polski ma zdania podrzędne pakowane gęściej), ale kontrast krótkich/długich pozostaje ten sam — short brutal + long explanatory + short brutal.

## 6. Czego unikać (zasady, nie listy fraz)

Decyzja designerska: listy konkretnych zbanowanych fraz po polsku **nie istnieją z definicji** — zostaną dopisane *empirycznie* na podstawie tego, co Agent 4a oraz użytkownik flagują podczas recenzji rzeczywistych skryptów. EN guide nagromadził listy po dziesiątkach skryptów; polski guide robi to samo, ale zaczyna od zera.

**Zasady jakościowe (uniwersalne, niezależne od konkretnych fraz):**

- NIE zaczynaj od "W tym filmie..." ani podobnego throat-clearing
- NIE używaj bezosobowych konstrukcji (pasywno-brzmiących) — "mówi się że", "uważa się że", "powiada się że", "trzeba", "należy", "powinno się"
- NIE wprowadzaj terminu naukowego po to żeby go natychmiast przetłumaczyć. Prowadź prostym językiem i pomijaj termin chyba że jest naprawdę zapamiętywalny.
- NIE używaj hedgingu ("być może", "prawdopodobnie", "wydaje się że", "raczej"). Zamień hedging na **bezpośrednie twierdzenia w głosie mówcy** — nie cytując badań.
- NIE pisz długich akapitów — max 1–3 zdania na akapit
- NIE używaj więcej niż jednej metafory na koncept
- NIE używaj **żadnego** language research-framingowego — bez "badania pokazują", "naukowcy odkryli", "z badań wynika", "ostatnie badania", "psychologowie nazywają to", "neuronauka wykazała", "dane wskazują", "według badań", "nauka jest jasna". Research informuje pisarza; nigdy nie pojawia się w skrypcie. Prezentuj odkrycia jako obserwacje o byciu człowiekiem.
- NIE cytuj nazwisk badaczy, zespołów autorskich ani lat publikacji w narracji — nigdy nie pisz "badanie Sonnentag i in." albo "badania Smith (2020)". Wszystkie prawdziwe cytaty bibliograficzne żyją w opisie YouTube (Agent 8), nie w narracji.
- NIE używaj notacji statystycznej, dziesiętnych, effect sizes, liczb badań, liczb uczestników, p-values, terminów metodologicznych (*pre-registered, double-blind, longitudinalne, meta-analiza*). Patrz sekcja **Liczby**.
- NIE używaj polskiego duchowo-rozwojowego rejestru ("wszechświat", "energia", "wibracje", "to nie przypadek że...", "podróż", "ścieżka", "zaufaj procesowi") — to nie jest nasz brand.
- NIE używaj polskiego academic-textbookowego rejestru ("warto zauważyć że", "należy podkreślić że", "kluczowe jest", "istotne wydaje się", "na uwagę zasługuje", "nie sposób pominąć") — to brzmi jak referat.

## 7. Anti-patterns: abstract → concrete examples

Wyłapane empirycznie z diffa pierwszego polskiego skryptu (`06_script_narration.docx` vs `— poprawiona.docx`) — wzorce w które pisarz zbyt łatwo wpada, a które łamią voice "ciepły terapeuta + reportaż psychologiczny". **Revisor i Reviewer skanują dokładnie te wzorce.**

### 7.1 Embodied clarity (pokaż sensację, nie opisuj wrażenia)

Pozwól widzowi na inferencję. Nie meta-wyjaśniaj co czuje — pokaż sensację bezpośrednio.

- ❌ "To konkretne wrażenie w klatce piersiowej" → ✓ "Coś w klatce piersiowej"
- ❌ "Odczuwasz wewnątrz siebie tę dotkliwą obecność" → ✓ "Czujesz to. Coś w klatce."
- ❌ "Ten symptom pojawia się gdy" → ✓ "Twoje serce zaczyna walić"

**Test:** Czy zdanie zaczyna się od meta-wyjaśnienia ("To...", "To jest...", "To wrażenie...") zamiast od czystej sceny? Jeśli tak — przepisz.

### 7.2 Cut redundancy (negative-positive duplicates)

Polski lubi precyzować przez powtarzanie. To brzmi ostrożnie, nie warmly.

- ❌ "Nie smutek dokładnie. Nie zazdrość dokładnie." → ✓ "Nie smutek. Nie zazdrość."
- ❌ "Nie jest to gniew, a raczej coś bliższego..." → ✓ "Nie gniew. Coś bliższego..."

**Test:** Czy "dokładnie", "raczej", "w pewnym sensie" mogłoby zniknąć bez zmiany znaczenia? Jeśli tak — wytnij.

### 7.3 De-judging tone (neutralny opis, nie wewnętrzny osąd)

Unikaj słów które brzmią jak diagnoza pacjenta. Zamień osąd na neutralny stan.

- ❌ "coś w tobie jest złamane" → ✓ "coś jest z tobą nie tak" (← samo "z tobą", nie "w tobie")
- ❌ "twoja psychika jest uszkodzona" → ✓ "twój system działa inaczej"
- ❌ "to wada twojego charakteru" → ✓ "to efekt systemu, który tak działa"

**Test:** Czy słowo brzmi jak coś co psycholog może powiedzieć pacjentowi w gabinecie, czy jak coś co terapeut(k)a mówi do ciebie po przyjacielsku? Wybieraj drugie.

### 7.4 Generalize personal details (uniwersalny konkret, nie biograficzny)

Jeśli używasz konkretu kulturowego, niech będzie uniwersalnie polski. Konkretne biograficzne szczegóły rozpraszają — widz myśli "to nie ja, to ktoś inny".

- ❌ "ciocia przy wigilii, mama patrzyła, ojciec w samochodzie" → ✓ "komentarze słyszane od lat — przy rodzinnym stole, w samochodzie, w szkole, w internecie"
- ❌ "kiedy szef Marek powiedział na zebraniu" → ✓ "kiedy ktoś w pracy mówi"

**Test:** Czy konkret jest **imienny / personalny** (jedna osoba, jedno wydarzenie) czy **kategoryczny** (typ sytuacji, którą każdy zna)? Dąż do kategorycznego.

### 7.5 Symbolic metaphor over numbered lists

Wizualna metafora wygrywa nad wyliczeniem. Liczby bez metafory są bezforemne.

- ❌ "wewnętrzna tabela: do 30 mieszkanie, do 35 ślub, do 40 dzieci" → ✓ "wyobrażona tarcza z terminami, które rzekomo powinieneś już odhaczyć"
- ❌ "system mierzy: lajki, followersi, zarobki" → ✓ "system mierzy szczyty"

**Test:** Czy używasz **listy konkretów** tam gdzie **jedna metafora** mogłaby to zamknąć w obrazie? Jeśli tak — zwiń do metafory.

### 7.6 Diagnostic over collapse-narrative

Unikaj defensywnego "broken" framingu. Diagnostyka systemu jest neutralna i nie pozycjonuje widza jako ofiary.

- ❌ "Coś się zepsuło niedawno" → ✓ "Problem pojawił się wtedy, gdy zmieniły się dane"
- ❌ "System nie działa już jak kiedyś" → ✓ "System został zaprojektowany do funkcjonowania w małej grupie, a dziś dostaje próbkę tysiąc razy większą"

**Test:** Czy mówisz "to się zepsuło/załamało" (collapse) czy "to działa dokładnie tak jak zaprojektowane, tylko warunki się zmieniły" (diagnostic)? Wybieraj drugie — odbiera widzowi poczucie, że jest pacjentem zepsutego mechanizmu.

### 7.7 Agency in Permission Practice ("zrobić" > "zauważyć")

W sekcji Permission Practice (4 numerowane tipy) — czasownik startowy powinien być **aktywny**, nie pasywno-obserwatorski.

- ❌ "Cztery rzeczy, które możesz zauważyć..." → ✓ "Cztery rzeczy, które możesz zrobić..."
- ❌ "Możesz dać sobie..." → ✓ "Możesz wypróbować..." / "Możesz zrobić..."

Dozwolone czasowniki agency: **zrobić / wypróbować / zauważyć / dać sobie / nieść ze sobą**. Wybór zależy od mechanizmu skryptu, ale "zauważyć" jest najsłabsze — używaj tylko jeśli mechanizm naprawdę o zauważaniu.

### 7.8 Softening pressure (dodaj temporalne softenery)

Każda instrukcja w Permission Practice powinna mieć softener który usuwa poczucie "muszę to robić zawsze".

- ❌ "Twoje ciało nie potrzebuje, żebyś rozwiązał ten problem" → ✓ "Twoje ciało nie potrzebuje, żebyś **teraz** rozwiązał ten problem"
- ❌ "Wystarczy oddech" → ✓ "Wystarczy **ta jedna minuta**"
- ❌ "Połóż dłoń na klatce piersiowej" → ✓ "Połóż dłoń na klatce piersiowej, **tam gdzie czujesz ciężar**"

Softener słowa: **teraz / na chwilę / tylko jedną minutę / nie musisz / wystarczy że / tam gdzie**. Dodaj przynajmniej jeden softener do każdego tipu z imperatywem.

---

## 8. Lista fraz do zbanowania (pusta — wypełniana w praniu)

Ta sekcja zaczyna pustą i rośnie z każdym shippniętym filmem. Po każdej recenzji skryptu (Agent 4a flaguje lub Ty flagujesz podczas czytania), dopisujemy konkretne polskie frazy które brzmią cringe lub łamią voice rules.

**Format dopisu:**

```
- "konkretna fraza" — dlaczego źle brzmi (1 linia kontekstu)
```

**Dotychczas zidentyfikowane (na 2026-05-25, przed pierwszym polskim skryptem):**

*(pusta — wypełniamy po pierwszym polskim skrypcie)*
