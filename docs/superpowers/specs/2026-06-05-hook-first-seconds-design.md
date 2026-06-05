# Design: Hook od pierwszych sekund — przesunięcie dyscypliny w górę

Data: 2026-06-05
Status: Spec do zatwierdzenia (przed planem wykonawczym)
Zakres zatwierdzony: **A** (odzyskanie + lokalizacja research doca + dyrektywa „zimne otwarcie" w drafterze; bramka Agenta 4 bez zmian w rubryce)

---

## Kontekst (dlaczego)

Cel użytkownika: **maksymalne utrzymanie widza w pierwszych sekundach filmu** — docisnąć hook „na zapas", bo to najważniejszy moment, mimo braku twardego dowodu problemu (brak sygnału ze spadającej retencji; to ruch prewencyjny, nie naprawczy).

Diagnoza po przeglądzie pipeline'u ujawniła dwie realne słabości w obecnym systemie hooka:

1. **Hook jest egzekwowany reaktywnie.** Drafter (3a) pisze otwarcie kierując się wyłącznie strukturalnym „punktem wejścia" wybranej architektury (`narrative_architectures.md`). Kryteria 15 sekund (zdanie 1 ≤14 słów + konkretny podmiot, moment identyfikacji „to ja" do słowa 37, jedna otwarta pętla) żyją **dopiero** w Agencie 4 (`/hook`), który **łata pierwsze ~37 słów po fakcie**. Splajs 37 słów na słabym otwarciu to plaster — otwarcie nie *rodzi się* mocne.

2. **Biblioteka wzorców hooka to martwy link.** `04_hook.md` (i instrukcja przepisania) odsyłają do `docs/specs/2026-05-15-15-second-hook-research.md` — pliku, który **istniał i został usunięty** (commit `99bab3e`, „chore: project maintenance"). Cała teoria + 6 wzorców (Anomalous Case / Inverted Truth / Direct Question / Visceral Image / Self-Audit / Stakes Reveal), na której opiera się bramka, jest osierocona.

Pożądany efekt: dyscyplina hooka zaczyna się w **słowie 1 pisania**, oparta o realną, polskojęzyczną bibliotekę wzorców. Agent 4 staje się **weryfikatorem**, a nie jedynym twórcą hooka.

### Notatka o intuicji „hook = pytanie do widza"

Pierwotna myśl użytkownika: dla filmu o wstydzie najlepszym hookiem byłoby pytanie („czy czułeś kiedyś wstyd?"). Doktryna **karze ogólne pytanie retoryczne** („Czy kiedykolwiek…?", red flag −1) jako niskostawkowe, ale „Direct Question" w wersji **konkretnej i presuponującej** jest jednym z 6 dozwolonych wzorców (parowanym z architekturą Socratic Challenge). Sedno nie brzmi „pytanie vs. nie-pytanie" — brzmi **konkret, w którym widz jest w środku, bije abstrakcję**. Ten design utrwala to rozróżnienie w bibliotece wzorców i w drafterze.

---

## Cel (co)

Bez przebudowy działającej bramki, sprawić, by **otwarcie skryptu rodziło się hook-mocne**:

- Przywrócić i **zlokalizować na polski** bibliotekę 6 wzorców + teorię 15 sekund jako pojedyncze źródło prawdy.
- Wpiąć skróconą dyscyplinę 15 sekund do **Etapu 1 draftera**, wskazując na tę bibliotekę.
- Naprawić martwy link w Agencie 4 (bez zmiany rubryki — jest mocna, dała 10/10 na filmie o wstydzie).

---

## Design (3 zmiany, zero kodu)

### Zmiana 1 — Odzyskaj i zlokalizuj research doc

**Plik:** `docs/specs/2026-05-15-15-second-hook-research.md` (dokładnie ta ścieżka — istniejące referencje wtedy się rozwiążą).

- Odzyskaj treść z gita: `git show 99bab3e^:docs/specs/2026-05-15-15-second-hook-research.md`.
- **Lokalizacja na polski:** przetłumacz/przepisz wszystkie przykłady i szablony na naturalny polski w głosie kanału (ciepły terapeuta, reportaż psychologiczny — nie kalka). Sekcje teoretyczne (mechanika algorytmu, psychologia uwagi) mogą zostać po polsku lub dwujęzycznie — priorytet to **6 wzorców + przykłady**.
- **Dodaj przykład dla tematu wstydu** (modelowy przypadek użytkownika) — pokazujący wzorzec Visceral Image / Self-Audit dla wstydu (np. wariant otwarcia „budzik o piątej" z `3_wstyd_za_wlasne_zycie`, które dostało 10/10), oraz kontrast: zbanowane ogólne „Czy czułeś kiedyś wstyd?" vs. mocna konkretna alternatywa.
- **Napraw wewnętrzne referencje:** `tools/agent4b_hook.py` → `tools/pipeline/agent4_hook.py`; `workflows/04b_hook.md` → `workflows/pipeline/04_hook.md`; `workflows/narrative_architectures.md` → `workflows/guides/narrative_architectures.md`.
- **Uzgodnij tempo:** doc mówi 145–155 wpm (angielski); kanał polski to ~130 wpm (`04_hook.md`). Budżet i tak ląduje na ~37 słowach — zostaw 37 jako cutoff, ale zaznacz polską gęstość (37 słów PL mieści się w ~15 s przy ~130 wpm).
- Zachowaj spójność red flagów z sekcją Tier 1 w `04_hook.md` (są z tego doca wyprowadzone — nie wprowadzaj rozjazdu).

### Zmiana 2 — Dyrektywa „zimne otwarcie" w drafterze (Etap 1)

**Plik:** `workflows/pipeline/03a_drafter.md`, w sekcji „ETAP 1 — Pisz głosem".

Dodaj **krótki** blok (akapit, nie wykład — Etap 1 ma zostać voice-first, nie constraint-first), który mówi pisarzowi, żeby **otwarcie pisał od razu pod pierwsze 15 sekund**:

- Zdanie 1: konkretny podmiot, **≤14 słów**, bez stackowania abstrakcji.
- Do słowa ~37: konkretny obraz/scena/stan ciała + moment **„to ja"** + jedna **otwarta pętla** (nierozwiązane pytanie trzymane w głowie).
- Dobierz **1 z 6 wzorców** dopasowany do narzuconej architektury (wskaż na odzyskany doc jako bibliotekę).
- Bez ogólnego pytania retorycznego („Czy kiedykolwiek…?"), bez statystyki przed emocją, bez meta-framingu, bez research-framingu (spójne z istniejącą doktryną Etapu 2).

Cel: otwarcie ma przejść bramkę Agenta 4 **bez przepisywania** — born-strong, nie patched.

### Zmiana 3 — Napraw link w Agencie 4 (bez zmiany rubryki)

**Plik:** `workflows/pipeline/04_hook.md`.

- Potwierdź/popraw linki do research doca, żeby wskazywały na przywrócony plik (są już `../../docs/specs/2026-05-15-15-second-hook-research.md` — zadziałają po przywróceniu pliku; zweryfikować).
- **Rubryka, progi i parser-kontrakt bez zmian.** Opcjonalnie: jedno zdanie w workflow notujące, że po dyrektywie z draftera Agent 4 powinien teraz zwykle zwracać otwarcie **verbatim** (weryfikacja), a nie zawsze przepisywać.

---

## Czego świadomie NIE robimy (YAGNI)

- **Nie zmieniamy rubryki ani progów Agenta 4** — działa, dał 10/10.
- **Nie dotykamy kodu** (`agent4_hook.py` itd.) — splajs i parser zostają.
- **Nie wpisujemy przykładów per architektura do `narrative_architectures.md`** (to było podejście C) — przy celu „na zapas" to puchnięcie doktryny; biblioteka wzorców żyje w jednym docu.
- **Nie ruszamy Agentów 0/1/2** (research po angielsku — intencjonalne).

---

## Pliki dotknięte

| Plik | Zmiana |
|---|---|
| `docs/specs/2026-05-15-15-second-hook-research.md` | **Utworzony** (odzyskany z gita + zlokalizowany na polski + naprawione ścieżki + przykład wstydu) |
| `workflows/pipeline/03a_drafter.md` | Dodany blok „zimne otwarcie" w Etapie 1 |
| `workflows/pipeline/04_hook.md` | Weryfikacja/poprawka linku; opcjonalna nota o roli weryfikatora |

---

## Weryfikacja (jak sprawdzić end-to-end)

1. **Link żyje:** ścieżka `docs/specs/2026-05-15-15-second-hook-research.md` istnieje; referencje w `04_hook.md` i `03a_drafter.md` rozwiązują się do realnego pliku (brak 404).
2. **Doc jest polski i kompletny:** 6 wzorców obecnych, każdy z polskim przykładem; jest przykład dla wstydu; brak martwych ścieżek `agent4b`/`04b`.
3. **Drafter wie o hooku:** Etap 1 zawiera dyrektywę 15 sekund wskazującą na doc; nie rozdmuchuje Etapu 1 do constraint-first (pozostaje voice-first).
4. **Test na żywym slug'u:** uruchom `/draft` na nowym temacie (lub przepisz istniejący draft), potem `/hook <slug>` — oczekiwane: Tier 1 ≥8 **bez** potrzeby przepisywania (otwarcie zaliczy verbatim), co potwierdza, że hook rodzi się mocny. Porównaj z `04_hook.md` slug'a — `VERDICT: record`, najlepiej `REWRITE_15S` ≈ oryginał.
5. **Brak regresji doktryny:** wygenerowane otwarcie nie łamie istniejących reguł (bez research-framingu, bez niecytowanego statu, bezrodzajowość zachowana).

---

## Następny krok

Po akceptacji tego spec'a → skill `writing-plans` tworzy plan wykonawczy (kolejność: odzyskanie doca → lokalizacja → dyrektywa draftera → link Agenta 4 → test na slug'u).
