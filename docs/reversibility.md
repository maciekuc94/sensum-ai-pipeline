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

- **Polskie outputy w `outputs/videos/`** — polskie skrypty, voiceovery, napisy wyprodukowane podczas pracy z polską wersją. Pozostają na dysku i nie kolidują z EN (EN zapisuje do tych samych ścieżek).
- **Polski 3n corpus** — buduje się od pierwszego polskiego video. Po powrocie do EN, korpus pozostaje (zawiera polskie skrypty), ale Agent 3n na EN będzie porównywał angielski draft z polskim korpusem — false-negatives nieuniknione. Rozwiązanie: po reaktywacji EN, podzielić korpus przez język lub usunąć polskie skrypty z indeksu nowości.
- **YouTube algorithm momentum** na angielskim kanale — jeśli `@hello.sensum` był dormant przez dłuższy czas, algorytm wycofał creator model. Reaktywacja oznacza algorytmiczny restart (pierwsze EN video po pauzie może mieć słabsze zasięgi).

## Tag inventory

Dla referencji — wszystkie tagi związane z reversibility:

```bash
git tag -l 'en-pipeline-*'
# en-pipeline-v1  ← obecny baseline (przed polską lokalizacją)
```

Przyszłe tagi (jeśli zostaną dodane):
- `en-pipeline-v2` — gdyby angielski pipeline został zaktualizowany niezależnie od polskiego
- `pl-pipeline-v1` — gdyby chcieć tagować stabilną wersję polskiego pipeline'u dla łatwego powrotu z eksperymentów
