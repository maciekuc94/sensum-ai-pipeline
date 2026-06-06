# Pipeline Teardown — Design Spec

- **Data:** 2026-06-05
- **Autor:** maciekuc94 (+ Claude, brainstorming)
- **Status:** DRAFT — do akceptacji przed `writing-plans`
- **Powiązane:** `docs/architecture_review.md` (wąski audyt z 2026-06-02, wzorzec stylu „decyzja + tabela + werdykt"), `CLAUDE.md` (master-mapa WAT)

---

## 1. Cel i kontekst (dlaczego)

Pipeline SENSUM ma bogaty opis *intencji* (CLAUDE.md + 22 SOP-y w `workflows/pipeline/` + guides), ale **nie ma jednego miejsca, które**:
1. spina cały łańcuch end-to-end (czyta się z góry na dół),
2. opisuje co kod **naprawdę** robi (nie tylko co agent *ma* robić wg SOP),
3. mapuje zależności i koszty,
4. patrzy na to **krytycznie** — co wyciąć / uprościć / poprawić.

Cel właściciela: **przestudiować pipeline, żeby wychwycić to, czego nie potrzebuje, czego nie chce, i co da się poprawić.** Dokument jest narzędziem decyzyjnym, nie tylko referencją.

Kluczowa teza, która uzasadnia warstwę „prawda o kodzie": **SOP-y nie zawsze mówią prawdę.** SOP to intencja, kod to grunt prawdy; między nimi powstaje dryf. Dowód już istnieje: trwa migracja `thumbnails → package` (równolegle żyją `07_package.md` i `07_thumbnails.md`, komendy `/package` i `/thumbnails`, dwa skille — a skrypt to wciąż `agent7_thumbnails.py`).

## 2. Cele i nie-cele

**Cele:**
- Jeden dokument `docs/pipeline_teardown.md` pokrywający cały pipeline w czterech soczewkach: audyt + całość + prawda o kodzie + mapa zależności/kosztów.
- Każdy komponent dostaje jednoznaczny **werdykt**: `ZOSTAW` / `UPROŚĆ` / `WYTNIJ` + uzasadnienie wg stałej rubryki.
- Zbiorczy rejestr werdyktów posortowany wg zysku — gotowa lista decyzji do podjęcia.

**Nie-cele (tym razem):**
- **Nie modyfikujemy kodu pipeline'u** — to dokument analityczny (read-only wobec `tools/`). Realne cięcia to osobny, późniejszy krok, który ten dokument *informuje*.
- Nie opisujemy treści `outputs/` (gotowe wideo/teksty) — tylko maszynerię.
- Nie wprowadzamy frameworka GSD ani `.planning/` — zostajemy w konwencji WAT.
- Nie tłumaczymy researchu na PL ani nie ruszamy doktryny głosu — to poza zakresem.

## 3. Odbiorca i język

- **Odbiorca:** właściciel (solo), do studiowania i podejmowania decyzji o cięciach.
- **Język dokumentu:** polski. **Identyfikatory kodu, nazwy plików, flagi, ścieżki — w oryginale** (np. `agent8_publish.py`, `--finalize`, `_load_niche_signals()`).

## 4. Deliverable

Jeden plik: **`docs/pipeline_teardown.md`** (master doc, czytany z góry na dół). Szacowana długość ~2,5–3,5 tys. linii. Bez podziału na pliki per-agent.

## 5. Zakres — inwentarz (co dokładnie pokrywamy)

WAT oznacza, że „agent" to często **para: workflow (.md, logika/prompt in-session) + tool (.py, deterministyczne bookendy + legacy `--api`)**. Dokument pokrywa **obie warstwy** per agent.

**Warstwa 0 — core chain (priorytet):**
| Agent | Tool (`tools/pipeline/`) | Workflow(y) (`workflows/pipeline/`) | Wejście in-session |
|---|---|---|---|
| 0 materials | `agent0_materials.py` (132) | `00_materials.md`, `00_materials_prompt.md` | — |
| 1 research | `agent1_research.py` (273) | `01_research.md`, `01_research_prompt.md` | — |
| 2 verify | `agent2_verify.py` (336) | `02_verify.md`, `02_verify_prompt.md` | — |
| 3 chain | `agent3.py` (151), `agent3b_revisor.py` (253), `agent3c_reviewer.py` (202) | `03_script.md`, `03_architecture_select.md`, `03a_drafter.md`, `03b_revisor.md`, `03c_reviewer.md`, `03d_native_ear.md` | `/draft`, `/draft-team` |
| 4 hook | `agent4_hook.py` (544) | `04_hook.md` | `/hook` |
| 5 visuals | `agent5_visuals.py` (570) | `05_visuals.md` | `/visuals` |
| 6 images | `agent6_images.py` (484) | `06_images.md` | (manual) |
| 6b QA | `agent6b_image_qa.py` (334) | `06b_image_qa.md` | (manual) |
| 7 package/thumbs | `agent7_thumbnails.py` (216) | `07_package.md`, `07_thumbnails.md` | `/package`, `/thumbnails` |
| 8 publish | `agent8_publish.py` (835) | `08_publish.md`, `08d_native_copy.md` | `/publish`, `/publish-team` |

**Warstwa 1 — satelity:**
- Align: `agent_align.py` (333) + `align.md` (po nagraniu, faster-whisper, lokalnie).
- Intelligence: `tools/intelligence/` — `intelligence.py` (217), `analyzer.py` (229), `collector.py` (196), `db.py` (127), `slide_builder.py` (595), `vision.py` (63) + `intelligence.md`.
- Agent Teams: `.claude/agents/` (krytycy + specjaliści) + `docs/agent_teams_reference.md` + warianty `-team`.

**Warstwa 2 — współdzielone / wspierające:**
- `tools/utils.py` (453), `tools/research_sources.py` (216), `tools/dev/add_grain.py`.
- `00_master.md` (orkiestracja), guides (`style_guide.md`, `narrative_architectures.md`, `voice_corpus.md`, `style_guide_images.md` — opisane skrótowo jako kontekst, nie audytowane jak kod).

**Warstwa 3 — przekrojowe zjawiska (osobne sekcje, nie per-agent):**
- Legacy `--api` (Gemini) — w 6 plikach.
- Dryf SOP↔kod (thumbnails→package i inne).
- Reżim „No Claude API / wszystko in-session".

## 6. Struktura dokumentu (TOC)

**Część globalna:**
1. **Mapa pipeline'u** — diagram przepływu danych (`topic → 0/1/2 → 3 → 4 → 5 ∥ 8 → 6/6b → 7 → align`); oznaczenie core / satelita / legacy.
2. **Tabela kosztów** — per agent: model, in-session vs Gemini, koszt API, czas, manual/auto.
3. **Tabela zależności** — co każdy agent czyta / pisze (pliki `md/`, `docx/` jako interfejsy).
4. **Warstwy systemu** — core vs satelity vs legacy.

**Część szczegółowa:**
5. Sekcja per agent wg jednego szablonu (§7).

**Część decyzyjna:**
6. **Zbiorczy rejestr werdyktów** — tabela wszystkich `UPROŚĆ`/`WYTNIJ`, sortowana wg zysku.
7. **Dług i dryf** — lista rozjazdów do posprzątania.

## 7. Szablon sekcji per agent

Każdy agent opisany identycznie:
1. **Rola** — jedno zdanie.
2. **Wejście → wyjście** — kontrakt plikowy (co czyta, co pisze).
3. **Komenda + flagi** — wszystkie tryby uruchomienia.
4. **Przewodnik po kodzie** — funkcja po funkcji, gałęzie, co robi *naprawdę* (logika w pełni; boilerplate — importy/argparse/`__main__` — tylko zaznaczony).
5. **SOP vs kod** — zgodność czy dryf; konkretne rozjazdy.
6. **Koszt i zależności** — model, API $, czas, od czego zależy / co odblokowuje.
7. **Werdykt audytu** — `ZOSTAW` / `UPROŚĆ` / `WYTNIJ` + uzasadnienie wg rubryki (§8).

## 8. Rubryka audytu i słownik werdyktów

Stały yardstick dla każdego werdyktu (5 kryteriów):
1. **Używalność** — czy realnie używane w produkcji.
2. **Koszt API** — wydatek na uruchomienie.
3. **Utrzymanie** — linie / złożoność / liczba gałęzi.
4. **Redundancja** — czy nakłada się na inny komponent.
5. **Dryf SOP↔kod** — czy dokumentacja zgadza się z kodem.

Słownik werdyktów:
- `ZOSTAW` — komponent niesie wartość proporcjonalną do kosztu/złożoności.
- `UPROŚĆ` — wartościowy, ale przerośnięty/zdryfowany; konkretna propozycja odchudzenia.
- `WYTNIJ` — kandydat do usunięcia; uzasadnienie + co trzeba sprawdzić przed cięciem.

## 9. Kalibracja głębi

Pełny przewodnik po **logice** (każda funkcja niosąca decyzje + jej gałęzie). Mechaniczny boilerplate (importy, parsowanie argumentów, `if __name__ == "__main__"`) — tylko odnotowany jednym zdaniem, nie rozpisywany.

## 10. Strategia produkcji (template-first staging)

Realizacja etapami (szczegóły rozpisze `writing-plans`):
1. **Etap A — szkielet globalny:** części 1–4 (mapa, koszty, zależności, warstwy) + JEDNA sekcja agenta w pełnej formie jako **wzorzec**.
2. **Checkpoint:** właściciel akceptuje format wzorca (brama jakości).
3. **Etap B — masowa produkcja:** pozostałe sekcje per agent wg zaakceptowanego wzorca.
4. **Etap C — część decyzyjna:** rejestr werdyktów + lista długu/dryfu (po zebraniu wszystkich werdyktów).

Kandydat na agenta-wzorzec: **Agent 8 (publish)** — największy (835 linii), najwięcej trybów; jeśli szablon udźwignie 8, udźwignie każdego. (Do potwierdzenia w planie.)

## 11. Strategia czytania kodu (context-mode)

~7 tys. linii kodu czytamy **bez zaśmiecania sesji**: analiza przez context-mode (`ctx_execute_file` / `ctx_batch_execute`) w sandboxie — do kontekstu wpada tylko strukturalny wniosek (sygnatury, gałęzie, call-graph, koszty). `Read` punktowo tylko tam, gdzie logika jest subtelna i wymaga dosłownego wglądu.

## 12. Kryteria sukcesu

Dokument jest „gotowy", gdy:
- Każdy agent z inwentarza (§5) ma komplet 7 pól szablonu.
- Każdy agent ma jednoznaczny werdykt wg rubryki.
- Istnieje mapa przepływu, tabela kosztów i tabela zależności obejmujące cały łańcuch.
- Rejestr werdyktów daje gotową, posortowaną listę decyzji „co wyciąć/uprościć".
- Wszystkie twierdzenia o kodzie są zweryfikowane w kodzie (nie przepisane z SOP).

## 13. Ryzyka i ograniczenia

- **Dezaktualizacja:** dokument to zdjęcie stanu na 2026-06-05; po realnych cięciach trzeba go odświeżyć (data + sekcja „stan na" u góry).
- **Rozmiar:** ~3k linii to dużo; mityguje to staging (§10) i stały szablon.
- **Zakres in-session:** logika agentów 3/4/5/7/8 żyje częściowo w SOP-ach (prompty), nie w `.py` — dokument musi pokryć obie warstwy, inaczej „przewodnik po kodzie" minie sedno.

## 14. Otwarte pytania

- Agent-wzorzec: Agent 8 (proponowany) czy inny? — rozstrzygniemy na starcie planu.
- Czy guides (`style_guide` itd.) audytować werdyktem, czy tylko opisać jako kontekst? — domyślnie: opis jako kontekst (nie kod).
