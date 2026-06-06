# Hook od pierwszych sekund — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprawić, by otwarcie skryptu rodziło się hook-mocne — przez odzyskanie i lokalizację na polski biblioteki 6 wzorców hooka oraz wpięcie dyscypliny „pierwszych 15 sekund" do draftera (3a), zamiast łatania jej dopiero w bramce Agenta 4.

**Architecture:** Trzy zmiany na dokumentach, zero kodu. (1) Odzyskać skasowany research doc z gita do kanonicznej ścieżki, zlokalizować na polski i dodać przykład dla wstydu. (2) Dodać krótki blok „zimne otwarcie" do Etapu 1 draftera wskazujący na ten doc. (3) Zweryfikować/naprawić martwy link w Agencie 4 (rubryka bez zmian).

**Tech Stack:** Markdown, git (`git show` do odzysku), workflowy pipeline SENSUM. Brak kodu, brak testów jednostkowych — weryfikacja przez sprawdzenie linków + przebieg `/draft`/`/hook` na slug'u.

**Spec:** `docs/superpowers/specs/2026-06-05-hook-first-seconds-design.md` (zakres A).

---

## Struktura plików

| Plik | Odpowiedzialność | Akcja |
|---|---|---|
| `docs/specs/2026-05-15-15-second-hook-research.md` | Pojedyncze źródło prawdy: teoria 15 s + 6 wzorców hooka (polskie przykłady) | Utworzony (odzysk + lokalizacja) |
| `workflows/pipeline/03a_drafter.md` | Drafter — Etap 1 zyskuje dyrektywę „zimne otwarcie" | Modyfikowany |
| `workflows/pipeline/04_hook.md` | Bramka Agenta 4 — link do biblioteki wzorców | Modyfikowany (tylko link/nota) |

**Uwaga o commitach:** użytkownik commituje świadomie. Każde Task kończy się commitem — to zgodne z „frequent commits", ale jeśli użytkownik woli jeden zbiorczy commit, połącz kroki commitu na końcu. Nie pushować.

---

### Task 1: Odzyskaj skasowany research doc (surowy, angielski) do kanonicznej ścieżki

**Files:**
- Create: `docs/specs/2026-05-15-15-second-hook-research.md`

- [ ] **Step 1: Odzyskaj treść z gita i zapisz do pliku**

Treść istnieje w commitcie-rodzicu usunięcia (`99bab3e^`). Pobierz pełny plik i zapisz pod kanoniczną ścieżką (tą, na którą wskazują istniejące referencje):

```bash
git -C "D:\ClaudeCode\YouTube psychology" show 99bab3e^:"docs/specs/2026-05-15-15-second-hook-research.md" > "docs/specs/2026-05-15-15-second-hook-research.md"
```

(Jeśli redirect w PowerShell zepsuje kodowanie, użyj: `git show 99bab3e^:docs/specs/2026-05-15-15-second-hook-research.md` i zapisz output narzędziem Write z `encoding utf-8`.)

- [ ] **Step 2: Zweryfikuj, że plik jest kompletny**

Sprawdź obecność wszystkich 6 wzorców i sekcji red flagów:

Run: `grep -nE "Pattern [1-6]|Red Flags|15-Second Anatomy" "docs/specs/2026-05-15-15-second-hook-research.md"`
Expected: 6 linii `Pattern 1..6` + nagłówek „Six Hook Patterns" + „Red Flags".

- [ ] **Step 3: Zweryfikuj, że referencja z bramki się rozwiązuje**

Run: `grep -n "2026-05-15-15-second-hook-research.md" "workflows/pipeline/04_hook.md"`
Expected: ≥1 trafienie (link już istnieje w workflow; teraz wskazuje na realny plik).

- [ ] **Step 4: Commit**

```bash
git add "docs/specs/2026-05-15-15-second-hook-research.md"
git commit -m "docs: recover deleted 15-second hook research doc

Restored from 99bab3e^ to the canonical path referenced by 04_hook.md
and 03a_drafter.md. Raw English content; Polish localization follows.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: Zlokalizuj doc na polski + napraw martwe ścieżki + uzgodnij tempo

**Files:**
- Modify: `docs/specs/2026-05-15-15-second-hook-research.md`

- [ ] **Step 1: Napraw wewnętrzne referencje (stare ścieżki → obecne)**

W odzyskanym docu podmień, wszędzie gdzie występują:
- `tools/agent4b_hook.py` → `tools/pipeline/agent4_hook.py`
- `workflows/04b_hook.md` → `workflows/pipeline/04_hook.md`
- `workflows/narrative_architectures.md` → `workflows/guides/narrative_architectures.md`

Run (weryfikacja, że nic starego nie zostało): `grep -nE "agent4b_hook|workflows/04b_hook|workflows/narrative_architectures\.md" "docs/specs/2026-05-15-15-second-hook-research.md"`
Expected: brak trafień.

- [ ] **Step 2: Uzgodnij tempo narracji na polskie**

W sekcji „Calibration Appendix" / „Word budget math" zmień tempo z `145–155 wpm` na polskie realia i dodaj notę o gęstości. Zachowaj `37 słów` jako cutoff. Wstaw zdanie:
> Tempo narracji kanału (polski): ~130 wpm. Polski jest gęstszy niż angielski — 37 słów PL nadal mieści się w ~15 sekundach. Cutoff 37 słów zostaje; zdanie 1 ≤14 słów.

- [ ] **Step 3: Zlokalizuj 6 wzorców na polski (szablony + przykłady)**

Dla każdego z 6 wzorców (Anomalous Case → *Anomalia*, Inverted Truth → *Odwrócona prawda*, Direct Question → *Pytanie wprost*, Visceral Image → *Obraz cielesny*, Self-Audit → *Autotest*, Stakes Reveal → *Ujawnienie stawki*) przepisz **template** i **example** na naturalny polski w głosie kanału (ciepły terapeuta / reportaż psychologiczny, nie kalka z angielskiego). Zachowaj parowanie z architekturą i regułę „przykład ≈37 słów, zdanie 1 ≤14 słów". Sekcje teoretyczne (mechanika algorytmu, psychologia uwagi) zostaw po polsku lub dwujęzycznie — priorytet to wzorce + przykłady.

Dla wzorca **Pytanie wprost (Direct Question)** dodaj jawną notę:
> Pytanie ma być **konkretne i presuponujące**, nie ogólne tak/nie. Zbanowane: „Czy czułeś kiedyś wstyd?" (niskostawkowe, red flag −1). Mocne: pytanie, które zakłada konkretną scenę, w której widz już był.

- [ ] **Step 4: Zachowaj spójność red flagów z bramką**

Porównaj tabelę red flagów w docu (sekcja „Red Flags & 15-Second Kill Switches") z listą Tier 1 w `workflows/pipeline/04_hook.md` (linie ~57–82). Upewnij się, że nie ma rozjazdu reguł (doc jest źródłem, bramka egzekucją). Jeśli doc ma red flag nieobecny w bramce lub odwrotnie — zostaw bramkę jako prawdę i dostosuj opis w docu, NIE zmieniaj rubryki bramki.

Run: `grep -nE "rhetorical|Have you ever|retoryczn|Czy kiedykolwiek" "docs/specs/2026-05-15-15-second-hook-research.md" "workflows/pipeline/04_hook.md"`
Expected: oba pliki zawierają zakaz pytania retorycznego (spójność).

- [ ] **Step 5: Commit**

```bash
git add "docs/specs/2026-05-15-15-second-hook-research.md"
git commit -m "docs: localize hook research doc to Polish + fix stale paths

6 patterns + templates/examples rewritten in channel voice; agent4b/04b
paths updated to pipeline/ layout; narration pace reconciled to ~130 wpm PL.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: Dodaj przykład hooka dla tematu wstydu (modelowy przypadek) + kontrast zbanowane vs mocne

**Files:**
- Modify: `docs/specs/2026-05-15-15-second-hook-research.md`

- [ ] **Step 1: Wstaw przykład dla wstydu do sekcji wzorców**

W sekcji „Six Hook Patterns" (po wzorcu Obraz cielesny / Autotest) dodaj zaznaczony przykład dla tematu wstydu. Użyj poniższej treści (możesz dopieścić rytm, ale zachowaj: zdanie 1 ≤14 słów, ~37 słów łącznie, otwarta pętla, moment „to ja"):

```markdown
### Przykład dla tematu: wstyd (Obraz cielesny + Autotest)

**Mocny (≈35 słów, zdanie 1 = 12 słów):**
> Wracasz myślą do czegoś sprzed lat i ciało reaguje, zanim zdążysz pomyśleć.
> Gorąco w twarzy, ucisk w klatce.
> Nikogo nie ma w pokoju, a ty kulisz się tak, jakby ktoś właśnie to zobaczył.

Otwarta pętla: dlaczego ciało wstydzi się przed pustym pokojem? Identyfikacja: widz rozpoznaje własną reakcję. Bez nazwania „wstydu" wprost — scena robi robotę.

**Referencyjny (Autotest, 10/10 z `3_wstyd_za_wlasne_zycie`):**
> Budzik dzwoni o piątej. Wczoraj obiecałeś sobie, że dziś wstaniesz i pobiegniesz. Wyłączasz go i śpisz dalej.

**Zbanowane (dwa red flagi: pytanie retoryczne + „większość z nas"):**
> ~~Czy czułeś kiedyś wstyd? Większość z nas dobrze go zna.~~

Ogólne pytanie tak/nie jest niskostawkowe — widz odpowiada w pół sekundy i nic go nie ciągnie dalej. Konkretna scena, w której widz JEST, bije abstrakcyjne pytanie.
```

- [ ] **Step 2: Zweryfikuj, że przykład wstydu jest w pliku**

Run: `grep -nE "Przykład dla tematu: wstyd|kulisz się|Budzik dzwoni o piątej" "docs/specs/2026-05-15-15-second-hook-research.md"`
Expected: trafienia dla mocnego, referencyjnego i (osobno) zbanowanego wariantu.

- [ ] **Step 3: Commit**

```bash
git add "docs/specs/2026-05-15-15-second-hook-research.md"
git commit -m "docs: add shame-topic hook example (strong vs banned contrast)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: Wpnij dyrektywę „zimne otwarcie" do Etapu 1 draftera

**Files:**
- Modify: `workflows/pipeline/03a_drafter.md`

- [ ] **Step 1: Wstaw blok dyrektywy tuż przed „Napisz teraz cały skrypt."**

Kotwica (istniejąca linia w Etapie 1):
```
Napisz teraz cały skrypt. Pełny łuk, od pierwszej do ostatniej linii, włącznie z sekcją Permission Practice i recognition close.
```

Wstaw **bezpośrednio przed** tą linią poniższy blok (drop-in, voice-first — krótki, nie rozdmuchuj Etapu 1 do constraint-first):

```markdown
**Zimne otwarcie — pierwsze 15 sekund (pisz je od razu mocne).** Otwarcie to moment, w którym widz decyduje, czy zostaje — pisz je tak, by przeszło bramkę Agenta 4 bez przepisywania:
- **Zdanie 1:** konkretny podmiot (osoba, pora, miejsce, część ciała), **≤14 słów**, jedna myśl — bez stackowania abstrakcji.
- **Do ~słowa 37:** konkretny obraz / scena / stan ciała + moment **„to ja"** (widz rozpoznaje siebie) + **jedna otwarta pętla** (nierozwiązane pytanie lub sprzeczność, którą musi domknąć, oglądając dalej).
- **Dobierz 1 z 6 wzorców** dopasowany do narzuconej architektury (Anomalia / Odwrócona prawda / Pytanie wprost / Obraz cielesny / Autotest / Ujawnienie stawki). Biblioteka z polskimi przykładami: `docs/specs/2026-05-15-15-second-hook-research.md`.
- **Nie** otwieraj ogólnym pytaniem retorycznym („Czy kiedykolwiek…?"), statystyką przed emocją, meta-framingiem ani research-framingiem. Konkret, w którym widz JEST w środku, bije abstrakcję — nawet w wzorcu Pytanie wprost pytanie ma być konkretne i presuponujące, nie ogólne tak/nie.

(Te cztery ruchy — przyciągnij uwagę → otwórz pętlę → wyląduj konkretem → wyzwól identyfikację — to ta sama oś, którą później punktuje Agent 4. Pełna teoria i wzorce: `docs/specs/2026-05-15-15-second-hook-research.md`.)
```

- [ ] **Step 2: Zweryfikuj wstawienie i kolejność**

Run: `grep -nE "Zimne otwarcie|Napisz teraz cały skrypt" "workflows/pipeline/03a_drafter.md"`
Expected: „Zimne otwarcie" pojawia się tuż PRZED „Napisz teraz cały skrypt" (numer linii dyrektywy < numer linii kotwicy), wewnątrz Etapu 1.

- [ ] **Step 3: Zweryfikuj, że link do doca jest poprawny**

Run: `grep -n "docs/specs/2026-05-15-15-second-hook-research.md" "workflows/pipeline/03a_drafter.md"`
Expected: ≥1 trafienie; ścieżka identyczna z plikiem utworzonym w Task 1.

- [ ] **Step 4: Commit**

```bash
git add "workflows/pipeline/03a_drafter.md"
git commit -m "feat(drafter): push 15-second hook discipline into Stage 1

Adds a voice-first 'zimne otwarcie' directive so openings are born
hook-strong (sentence 1 <=14 words, identification by word 37, one open
loop, one of 6 patterns) instead of being patched by the Agent 4 gate.

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Zweryfikuj/napraw link w Agencie 4 + opcjonalna nota o roli weryfikatora

**Files:**
- Modify: `workflows/pipeline/04_hook.md`

- [ ] **Step 1: Potwierdź, że oba odwołania do research doca są poprawne**

Run: `grep -n "2026-05-15-15-second-hook-research.md" "workflows/pipeline/04_hook.md"`
Expected: trafienia w sekcji „Prompt" (linia ~43, polska) i „Reference" (linia ~196). Ścieżka względna `../../docs/specs/2026-05-15-15-second-hook-research.md` rozwiązuje się do pliku z Task 1 — sprawdź, że tak jest; jeśli ścieżka się różni, popraw na poprawną względną.

- [ ] **Step 2: (Opcjonalnie) Dodaj jedno zdanie o roli weryfikatora**

W sekcji „## Purpose" (po pierwszym akapicie) dodaj zdanie:
> Od 2026-06-05 dyscyplina 15 sekund zaczyna się już w drafterze (3a, Etap 1) — Agent 4 działa więc głównie jako **weryfikator**: dobrze napisane otwarcie zwykle zalicza Tier 1 i wraca w `REWRITE_15S` verbatim, a przepisanie jest wyjątkiem, nie regułą.

- [ ] **Step 3: Commit**

```bash
git add "workflows/pipeline/04_hook.md"
git commit -m "docs(hook): confirm research-doc link + note verifier role post-3a

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 6: Weryfikacja end-to-end na żywym slug'u

**Files:** brak zmian — to test zachowania.

- [ ] **Step 1: Wybierz slug do testu**

Run: `ls outputs/videos_pl/`
Expected: lista slugów. Wybierz jeden z istniejącym `md/02_verified_research.md` (np. ponów draft) LUB użyj nowego tematu. Zanotuj slug.

- [ ] **Step 2: Wygeneruj draft i przepuść przez bramkę**

Uruchom w sesji Claude Code:
```
/draft <slug>
/hook <slug>
```
(Jeśli testujesz tylko hook na istniejącym `04_final.md`, sam `/hook <slug>` wystarczy.)

- [ ] **Step 3: Sprawdź wynik bramki**

Run: `grep -nE "Final 15s score|Verdict|Red flags triggered" "outputs/videos_pl/<slug>/md/04_hook.md"`
Expected: `Final 15s score: >=8`, `Verdict: record`, `Red flags triggered: none`. Najlepszy sygnał sukcesu: `REWRITE_15S` ≈ oryginalne otwarcie (otwarcie urodziło się mocne, bramka tylko potwierdziła) — porównaj otwarcie w `04_final.md` z `04_final.bak.md` (jeśli backup powstał, znaczy że jednak przepisano).

- [ ] **Step 4: Sprawdź brak regresji doktryny w otwarciu**

Ręcznie przeczytaj pierwsze ~37 słów `04_final.md`: brak research-framingu, brak niecytowanego statu, bezrodzajowość zachowana, zdanie 1 ≤14 słów. Jeśli OK — design działa end-to-end.

- [ ] **Step 5: (Bez commitu testowych outputów, chyba że to realny film)**

Outputy slug'a commituj tylko jeśli to produkcyjny film. Test na istniejącym slug'u: przywróć otwarcie z backupu, jeśli nie chcesz zmiany:
```bash
# tylko jeśli to był test i chcesz cofnąć:
cp "outputs/videos_pl/<slug>/md/04_final.bak.md" "outputs/videos_pl/<slug>/md/04_final.md"
```

---

## Self-Review (wykonane przy pisaniu planu)

**Pokrycie spec'a:**
- Zmiana 1 (odzysk + lokalizacja + przykład wstydu + ścieżki + wpm) → Task 1 (odzysk), Task 2 (lokalizacja/ścieżki/wpm), Task 3 (przykład wstydu). ✓
- Zmiana 2 (dyrektywa „zimne otwarcie" w 3a) → Task 4. ✓
- Zmiana 3 (link w Agencie 4, bez zmiany rubryki) → Task 5. ✓
- Weryfikacja end-to-end ze spec'a → Task 6. ✓

**Placeholdery:** brak — dyrektywa draftera i przykład wstydu podane jako gotowa treść drop-in.

**Spójność nazw/ścieżek:** kanoniczna ścieżka `docs/specs/2026-05-15-15-second-hook-research.md` użyta identycznie w Task 1/2/3/4/5. Nazwy 6 wzorców (PL) spójne między Task 2 (definicja) a Task 4 (lista w drafterze). Zakaz pytania retorycznego spójny: doc (Task 2/3) ↔ drafter (Task 4) ↔ bramka (Task 5, bez zmian).

**YAGNI:** brak zmian w kodzie i rubryce bramki; `narrative_architectures.md` nietknięty (to było podejście C, odrzucone).

---

## Następny krok / Execution Handoff

Po zatwierdzeniu planu — wybór trybu wykonania (poniżej).
