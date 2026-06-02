# Reversibility — powrót do angielskiego pipeline'u

Ten dokument opisuje jak wrócić do angielskiej wersji pipeline'u SENSUM po lokalizacji na polski.

## Mechanizm pierwotny — Git tag `en-pipeline-v1`

Tag `en-pipeline-v1` zawiera kompletny, działający angielski pipeline w stanie na 2026-05-25 (przed jakąkolwiek lokalizacją na polski). Wszystkie angielskie system prompts, style guides, agent configs i wzorce voice są w nim zachowane.

### Sprawdzenie zawartości tagu (bez modyfikacji bieżącego stanu)

```bash
# Podgląd pojedynczego pliku z taga:
git show en-pipeline-v1:tools/pipeline/agent3a_draft.py
git show en-pipeline-v1:workflows/guides/style_guide.md
git show en-pipeline-v1:workflows/guides/narrative_architectures.md
git show en-pipeline-v1:CLAUDE.md

# Lista plików w tagu:
git ls-tree -r en-pipeline-v1 --name-only

# Diff: co się zmieniło między tagiem a bieżącym stanem
git diff en-pipeline-v1 -- tools/pipeline/agent3a_draft.py
git diff en-pipeline-v1 --stat
```

### Przywrócenie pojedynczego pliku do stanu EN

```bash
# Przywrócenie 1 pliku (zostaje na bieżącej gałęzi, zmienia tylko ten plik):
git checkout en-pipeline-v1 -- tools/pipeline/agent3a_draft.py

# Przywrócenie konkretnej grupy plików:
git checkout en-pipeline-v1 -- tools/pipeline/agent3a_draft.py tools/pipeline/agent3b_critic.py tools/pipeline/agent3c_rewrite.py
git checkout en-pipeline-v1 -- workflows/guides/

# Po przywróceniu — commit żeby zachować zmianę:
git add -A && git commit -m "restore agent3a to english version"
```

### Pełny powrót do EN (cały pipeline angielski znowu)

```bash
# Opcja A — branch z taga (bezpieczne, działasz na nowej gałęzi):
git checkout -b restore-english en-pipeline-v1
# Teraz jesteś na branchu `restore-english` z pełnym EN pipelinem.
# Możesz mergować z powrotem do main jeśli chcesz EN jako mainline.

# Opcja B — revert lokalizacyjnych commitów na main:
git log --oneline en-pipeline-v1..HEAD  # lista commitów dodanych po tagu
git revert <commit-hash-of-polish-localization>  # cofnij konkretny commit
# Możesz też cofnąć zakres commitów jeśli polska lokalizacja była w wielu commitach.

# Opcja C — twardy reset (DESTRUCTIVE — używaj tylko jeśli wiesz że nie chcesz polskiej pracy):
# git reset --hard en-pipeline-v1
# UWAGA: traci wszystkie commity po tagu. Nie używaj jeśli polska praca ma jakąkolwiek wartość.
```

## Mechanizm wtórny — pliki `.en.md` na dysku

Polskie wersje style guides ZASTĘPUJĄ pliki pod tymi samymi nazwami. Angielskie wersje są zachowane jako sąsiednie pliki z sufiksem `.en.md`:

```
workflows/guides/style_guide.md             ← polski (aktualny)
workflows/guides/style_guide.en.md          ← angielska kopia (referencja)
workflows/guides/narrative_architectures.md ← polski (aktualny)
workflows/guides/narrative_architectures.en.md ← angielska kopia (referencja)
```

Pozwala to porównywać reguły side-by-side bez sięgania do Gita:

```bash
# Diff polskich vs angielskich reguł (na dysku, bez Git):
diff workflows/guides/style_guide.md workflows/guides/style_guide.en.md
```

Te pliki są obecne na dysku permanentnie — nie są usuwane po lokalizacji.

## Mechanizm trzeciorzędny — kanał YouTube `@hello.sensum`

Angielski kanał `@hello.sensum` (15 subów, 5 video + 22 shorts) pozostaje **dormant**:
- Żadnych nowych uploadów na angielskim kanale
- 5 EN videos zostają (publiczne lub unlisted — decyzja użytkownika)
- Kanał nie jest usunięty, tylko nieaktywny

### Reaktywacja angielskiego kanału

Reaktywacja nie wymaga żadnych zmian kodu (jeśli kod został przywrócony przez Git):
1. Przywróć kod EN przez Git (sekcja powyżej)
2. Wybierz temat → uruchom polski pipeline po angielsku (po Git restore agenty są znowu angielskie)
3. Nagraj angielski voiceover
4. Wyślij na `@hello.sensum` jak normalnie

### Bilingual flow (oba kanały aktywne)

Jeśli zechcesz prowadzić **oba kanały równolegle** w przyszłości, wracamy do oryginalnego planu mirror (`tools/pipeline/pl/` + `outputs/videos_pl/`) — pełna specyfikacja w pierwszej wersji planu w `C:\Users\maciej\.claude\plans\wlasnie-przypadkowo-trafilem-na-rosy-elephant.md` (historia Git planu zachowuje wcześniejsze wersje).

## Czego NIE da się przywrócić automatycznie

Te elementy są poza zakresem Git/file backup — są wynikiem świadomych decyzji, nie regresji kodu:

- **Polskie outputy w `outputs/videos_pl/`** — polskie skrypty, voiceovery, napisy wyprodukowane podczas pracy z polską wersją. Pozostają na dysku, oddzielone od EN legacy w `outputs/videos_en/`.
- **Polski 3n corpus** — buduje się od pierwszego polskiego video. Po powrocie do EN, korpus pozostaje (zawiera polskie skrypty), ale Agent 3n na EN będzie porównywał angielski draft z polskim korpusem — false-negatives nieuniknione. Rozwiązanie: po reaktywacji EN, podzielić korpus przez język lub usunąć polskie skrypty z indeksu nowości.
- **YouTube algorithm momentum** na angielskim kanale — jeśli `@hello.sensum` był dormant przez dłuższy czas, algorytm wycofał creator model. Reaktywacja oznacza algorytmiczny restart (pierwsze EN video po pauzie może mieć słabsze zasięgi).

## Mechanizm czwartorzędny — Git tag `agent-chain-v1-prerevisor`

Niezależnie od EN/PL lokalizacji, **script chain** (Agent 3a → 3n → 3b → 3c → 4a) został zrefaktorowany do B++ v2 (3a Drafter → 3b Revisor → 3c Reviewer loop) w 2026-05-25. Stara architektura jest zachowana w tagu `agent-chain-v1-prerevisor`.

Zmiany:
- **Usunięte:** `agent3n_novelty.py`, `agent3b_critic.py`, `agent3c_rewrite.py`, `agent4a_edit.py`, `workflows/pipeline/04a_edit.md`
- **Dodane:** `agent3b_revisor.py` (Sonnet, full-script revision), `agent3c_reviewer.py` (Sonnet, PASS/FLAG judge)
- **Zmodyfikowane:** `agent3.py` (loop orchestrator), `agent3a_draft.py` (3 nowe wzorce w promptie), `workflows/guides/style_guide.md` (sekcja Anti-patterns), `workflows/pipeline/03_script.md` (nowy SOP)

### Sprawdzenie zawartości tagu

```bash
git show agent-chain-v1-prerevisor:tools/pipeline/agent3b_critic.py
git show agent-chain-v1-prerevisor:tools/pipeline/agent4a_edit.py
git ls-tree -r agent-chain-v1-prerevisor --name-only | grep -E "agent3|agent4a"
git diff agent-chain-v1-prerevisor -- tools/pipeline/
```

### Przywrócenie starego chainu (Drafter + Critic + Rewrite + Edit)

```bash
# Opcja A — przywrócenie samych python skryptów (zostaje na bieżącej gałęzi):
git checkout agent-chain-v1-prerevisor -- tools/pipeline/agent3.py tools/pipeline/agent3a_draft.py tools/pipeline/agent3n_novelty.py tools/pipeline/agent3b_critic.py tools/pipeline/agent3c_rewrite.py tools/pipeline/agent4a_edit.py workflows/pipeline/04a_edit.md workflows/pipeline/03_script.md

# Następnie usuń nowe agenty (które już są niepotrzebne w v1):
rm tools/pipeline/agent3b_revisor.py tools/pipeline/agent3c_reviewer.py

# Commit:
git add -A && git commit -m "restore agent chain v1 (drafter+critic+rewrite+edit)"
```

```bash
# Opcja B — branch z taga (bezpieczne, działasz na nowej gałęzi):
git checkout -b restore-chain-v1 agent-chain-v1-prerevisor
# Teraz jesteś na branchu `restore-chain-v1` z pełnym v1 chainem.

# Opcja C — twardy reset (DESTRUCTIVE):
# git reset --hard agent-chain-v1-prerevisor
# UWAGA: traci wszystkie commity po tagu.
```

Style guide też trzeba cofnąć (sekcja Anti-patterns została dodana w v2):

```bash
git checkout agent-chain-v1-prerevisor -- workflows/guides/style_guide.md
```

Po restore pipeline znowu używa starego flow: `python tools/pipeline/agent3.py "<slug>"` uruchamia 3a → 3n → 3b → 3c (jak przed), a `agent4a_edit.py` znowu istnieje jako osobny krok po Agent 3.

## Mechanizm piątorzędny — split Agenta 8 (publish) na 9 kroków in-session (2026-06-02)

Agent 8 został podzielony z 3 mega-promptów (Gemini: titles / shorts / metadata) na **9 osobnych kroków in-session na Opus 4.8** (`/publish <slug>`), z deterministycznymi „bookendami" w Pythonie (`--extract`, `--signals`, `--finalize`). Stary orchestrator Gemini **nie został usunięty** — żyje za flagą `--api`.

### Najszybszy powrót — flaga `--api` (bez restore)

```bash
# Uruchom stary, pełny pipeline Gemini end-to-end (titles → shorts → metadata, jak przed splitem):
PYTHONIOENCODING=utf-8 python tools/pipeline/agent8_publish.py "<slug>" --api
```

Nic nie trzeba cofać — `--api` produkuje to samo `md/08_publish.md` co dawny `agent8_publish.py "<slug>"` (bez flagi). Split dodaje tylko nowe ścieżki (`/publish`, `--extract/--signals/--finalize`), nie kasuje starej.

### Pełny powrót do stanu sprzed splitu (gdyby flaga `--api` nie wystarczyła)

```bash
# Commit sprzed splitu (znajdź go w logu — opis: „split publishing agent"):
git log --oneline -- tools/pipeline/agent8_publish.py | head

# Przywróć skrypt, prompt SOP i usuń slash command:
git checkout <pre-split-commit> -- tools/pipeline/agent8_publish.py workflows/pipeline/08_publish.md
rm .claude/commands/publish.md

git add -A && git commit -m "restore agent 8 to pre-split (3-pass Gemini) version"
```

Stara wersja `agent8_publish.py` miała `main()` jako orchestrator Gemini bez flag — uruchamiana przez `python tools/pipeline/agent8_publish.py "<slug>"`.

---

## Tag inventory

Dla referencji — wszystkie tagi związane z reversibility:

```bash
git tag -l 'en-pipeline-*' 'agent-chain-*'
# en-pipeline-v1            ← angielski pipeline baseline (przed polską lokalizacją)
# agent-chain-v1-prerevisor ← stary script chain (Drafter+Critic+Rewrite+Edit, przed B++ v2)
# agent-chain-v2-revisor    ← (TBA) nowy script chain (Drafter+Revisor+Reviewer) — taguje się po pomyślnej weryfikacji
```

Przyszłe tagi (jeśli zostaną dodane):
- `en-pipeline-v2` — gdyby angielski pipeline został zaktualizowany niezależnie od polskiego
- `pl-pipeline-v1` — gdyby chcieć tagować stabilną wersję polskiego pipeline'u dla łatwego powrotu z eksperymentów
