# Design Spec: `/refine` — molekularna warstwa native-polszczyzny

**Data:** 2026-06-06
**Status:** zaakceptowany kierunek + zakres (MVP), kalibracja konserwatywna. Do implementacji przez writing-plans.
**Geneza:** slug-3 wychodził „pisaną" (eseistyczną) polszczyzną mimo poprawnego łańcucha. Diagnoza: blind-spot (jeden model pisze i ocenia) + cel „esej". Łańcuch przecelowano na reportaż mówiony (`voice_corpus.md` §A, `style_guide.md` §2.5, `03a`/`03d`). Ta warstwa to **drugi front**: molekularne, zdanie-po-zdaniu domknięcie, odpalane świadomie, przy nielimitowanym budżecie tokenów.

---

## 1. Cel

Wyłapać zdania, które **argumentują abstrakcję bez fizycznej kotwicy** (reportaż-vs-esej) **albo niosą jawną kalkę składniową**, i zaproponować mówione przepisania **z dowodem**. **Człowiek zatwierdza każdą zmianę.** Nigdy cichego auto-replace.

## 2. Zasada naczelna (z POC `wrabcyj69`)

Maszyna jest **generatorem kandydatów + dowodów**, nie auto-przepisywaczem. POC pokazał: na zdaniu eseistycznym (T1) miała rację i dała lepszy rewrite; na **opublikowanym, świadomie dopracowanym** zdaniu (T3 „muzeum lenistwa") oflagowała i zaproponowała **bledszą** wersję. Wniosek: kryterium „outlier vs chmura" jest **stronnicze ku prostocie** (ślepa chmura zawsze regresuje do mowy, więc każdy crafted-concrete wygląda na outlier). Dlatego chmura = **materiał i dowód**, a nie wyrok; **decyduje człowiek.**

## 3. Kalibracja: KONSERWATYWNA (decyzja właściciela, 2026-06-06)

- **Flaguj** tylko: (a) **abstrakcję-argument** — zdanie unoszące pojęcie bez fizycznej kotwicy / odwracające się od „ty" w generyczną ramę / piętrzące zmiękczacze pisanego dowodu (= T1: „wyrok na całego człowieka"); (b) **jawną kalkę składniową** — 4 nazwane tells z `voice_corpus.md` §C2 (pronoun flood, nominalizacja, genitive-stack, trailing verb) **oraz** gdy polski *sam w sobie* brzmi nie-natywnie.
- **Chroń** (nigdy nie flaguj „za ładne"): **dopracowany konkretny obraz**, gramatycznie natywny, nawet literacki (= T3: „muzeum lenistwa"). Crafted-concrete **wygrywa**.
- **Twarde szczyty** (domyślnie poza rewrite, co najwyżej FYI niska-pewność): cold open, centralny fizyczny motyw, zdania-kotwice, recognition close.

Dyskryminator T1-flag vs T3-keep: *czy zdanie unosi pojęcie (flaga), czy kładzie fizyczną rzecz (zostaw)?* + *czy polski jest sam w sobie koślawy (flaga), czy w pełni natywny (zostaw)?*

## 4. Architektura MVP (silnik: `Workflow`)

Warstwa **między Drafterem (3a) a czytelnikami (3c/3d)**. Wejście: `md/04_working.md`. Wyjście: zaktualizowany `md/04_working.md` + `md/refine_candidates_iter{N}.md` (ślad decyzji).

0. **Segmentacja** — zdania ze stabilnym ID + sąsiedzi (kontekst dla sądu). Oznacz **twarde szczyty** (heurystyka pozycji: 1. akapit, ostatnie 2 akapity, linie-kotwice w osobnych liniach) → domyślnie nietykane.
1. **Panel per-zdanie** (`parallel`, zimne konteksty, każdy zwraca `{flaga, powód, dowód, kandydat}`):
   - **L2 forward-divergence** (klejnot): intent-extract (**wymuszony polski** — fix buga T3) → **ślepy** generator pisze 5 mówionych wersji z samego intentu (NIE widzi draftu) → sędzia ocenia draft kryterium z §3 (abstrakcja-argument?), chmura jako dowód/kandydaci; **crafted-concrete może wygrać**.
   - **L1 back-translation**: PL→EN dosłownie; flaga **tylko** gdy polski sam brzmi koślawo a angielski naturalniej (**podniesiony próg po T3** — sama „czysto przechodząca" metafora to NIE kalka).
2. **Prezentacja człowiekowi (NIE auto):** `md/refine_candidates_iter{N}.md` — per flaga: oryginał → powód → chmura 5 wariantów → proponowany rewrite. Właściciel: accept / keep / wybierz-wariant / własny.
3. **Re-flow jedną ręką** (nienegocjowalne): przyjęte zmiany → **jeden Integrator** przepisuje CAŁOŚĆ (przejścia, niesiony motyw, chronione szczyty) → `04_working.md`. Atomizacja bez kustosza = 60 lokalnie idealnych zdań, które się nie kleją = powrót do „nie klei się".
4. **Pętla do wyschnięcia**: powtórz 1–3 na **zmienionych + sąsiadach**, aż brak nowej flagi w pozycji impaktowej (nie „N rund").

## 5. Bezpieczniki (nienegocjowalne)

1. **Człowiek decyduje każdą flagę** — zero cichego auto-replace.
2. **Chronione szczyty** poza rewrite (FYI maks.).
3. **Konserwatywny próg** — crafted-concrete wygrywa; oryginał może wygrać.
4. **Re-flow jedną ręką** po każdej rundzie (spójność > lokalna poprawność).
5. **Stop gdy sucho** — przeciw mieleniu prozy na papkę.

## 6. Świadomie POZA MVP (faza 2, po walidacji)

Turniej wielowariantowy z selektorem · L5 grounding w korpusie (Twoje nagrania + reportaż-książki) · wiele person per soczewka · auto-wpięcie w `/draft`. MVP = L1 + L2 + re-flow + pętla ≈ 80% efektu.

## 7. Walidacja (definicja sukcesu)

Odpal na całym `slug-3`. Sukces, gdy łącznie:
- (a) łapie eseistyczne abstrakcje (typ T1) z mówionymi rewrite'ami;
- (b) **NIE** flaguje crafted-concrete (typ T3 / „muzeum lenistwa");
- (c) re-flow utrzymuje spójność (jeden bieg, niesiony motyw);
- (d) Twoje ucho na `script_corrected.docx` ma realnie mało do roboty.

## 8. Otwarte ryzyka

- **Intent-leak** — ekstraktor może przeciekać frazowanie do ślepego generatora. Mitygacja: intent jako **opis celu komunikacyjnego po polsku**, nie zdanie-do-przetłumaczenia; sędzia traktuje chmurę jako dowód, nie wzorzec-do-skopiowania.
- **Re-flow to najtrudniejszy element** — dostaje najwięcej uwagi w planie i w teście (c).
- **Koszt/czas** — akceptowalny: on-demand `/refine`, budżet tokenów nieistotny (decyzja właściciela).
- **Sufit** — wszystkie soczewki to wciąż ten sam model; realnie blind-spot obchodzą tylko L1/L2. Twoje ucho zostaje sufitem, ale lekkim. Bez obietnicy 100% automatu.

## 9. Trigger

Osobna komenda **`/refine <slug>`** (nie auto w `/draft`) — długi, kosztowny przebieg odpalany świadomie.
