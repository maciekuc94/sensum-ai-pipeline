# SENSUM Mission Control — spec designu (zatwierdzony 2026-06-12)

> Lokalna webowa aplikacja-kokpit nad pipeline: stan każdego sluga z automatyczną
> detekcją etapu i akcją „co dalej + komenda do skopiowania", podgląd artefaktów
> (skrypt / obrazy / miniatury / pliki) oraz przeglądarka backlogu tematów.
> **W 100% read-only wobec repo** — niczego nie zapisuje, niczego nie uruchamia.

## Decyzje usera (brainstorm 2026-06-12)

1. **Zakres v1:** read-only + gotowe komendy do skopiowania (przycisk „kopiuj").
   Launchery subprocess — dopiero ewentualnie v2. Slash-commandy (`/draft`,
   `/publish`) z natury żyją tylko w sesji Claude Code — apka ich nie odpala.
2. **Moduły v1:** tablica pipeline + podgląd artefaktów + backlog tematów.
   Metryki/trendy (ceiling, QA pass-rate) — poza v1, dojdą po danych
   z Redaktora-ucznia.
3. **Architektura:** lokalny serwer **FastAPI + uvicorn**; frontend vanilla JS
   (zero npm / build-chaina); markdown przez lokalną kopię `marked.js` (bez CDN).
4. **Layout tablicy (mockup):** **karty ze stepperem** — jedna karta = jeden film,
   poziomy stepper etapów, wyraźny czip „→ co dalej"; ukończone (z `.mov`)
   zwijane do sekcji na dole.
5. **Kompozycja (mockup):** **zakładki górne „Pipeline | Backlog" + pełna
   podstrona sluga** (klik karty → artefakty na pełną szerokość, breadcrumb wstecz).

## Struktura plików

```
tools/mission_control/
  server.py            # FastAPI app + uruchomienie (webbrowser.open, --port, domyślnie 7777)
  pipeline_state.py    # czysta logika: slug dir → etapy + co-dalej (testowalna osobno)
  backlog_parser.py    # topic_backlog_PL.md → JSON rankingu
  static/
    index.html         # SPA (zakładki Pipeline | Backlog + widok sluga)
    app.js             # vanilla JS (fetch API, render, lightbox, clipboard)
    style.css          # paleta SENSUM (#F4E5CA tło / #582F0E tusz)
    vendor/marked.min.js
```

`fastapi` + `uvicorn` dopisane do `requirements.txt`. Wpis `tools/mission_control/`
w sekcji File Structure CLAUDE.md (jedna linijka).

## API (4 endpointy, wszystkie GET)

| Endpoint | Zwraca |
|---|---|
| `/api/state` | wszystkie slugi: etapy ze statusem, „co dalej" (≤2 akcje równoległe) + komendy |
| `/api/slug/{slug}/files` | drzewo plików sluga |
| `/api/slug/{slug}/raw?path=…` | treść pliku (md/text/obraz) — **twarda sanityzacja**: `resolve()` + prefiks `outputs/videos_pl/{slug}/`, inaczej 403 |
| `/api/backlog` | sparsowany ranking tematów |

## Detekcja etapów (`pipeline_state.py`)

Mapowanie plik-marker → etap (kanon nazewnictwa z `file_naming.md`):

| Etap | Marker |
|---|---|
| research | `md/01_research.md` |
| weryfikacja | `md/02_verified_research.md` |
| skrypt | `md/04_final.md` |
| docx pass | `docx/script_corrected.docx` lub `md/script_corrected.md` |
| visuals | `md/05_image_prompts.md` |
| grafiki | `images/*.png` (≥1) |
| package | `md/07_package.md` + `thumbnails_no_grain/*.png` |
| publish | `md/08_publish.md` |
| nagranie | `voiceover/voiceover.wav` |
| align | `edit/timeline.fcpxml` |
| zmontowany ✦ | `*.mov` w katalogu sluga → karta do sekcji „ukończone" |
| animacje (opcjonalny) | `md/06c_animation_plan.md` / `images_anim/*.mp4` — wykrywany, nie blokuje „co dalej" |

**„Co dalej":** pierwszy brakujący etap w kolejności kanonicznej; mapa
etap → komenda do skopiowania (z prefiksem `PYTHONIOENCODING=utf-8` dla narzędzi
Python); kroki ręczne (docx pass, nagranie) dostają tekst zamiast komendy.
Po docx passie — **dwie akcje równoległe** (`/visuals` i `/package`), zgodnie
z regułą równoległości z CLAUDE.md. Stepper na karcie = fazy skondensowane;
pełna lista etapów na podstronie sluga.

## Podstrona sluga (4 zakładki)

- **Skrypt:** render markdown; przełącznik wersji gdy >1
  (`script_corrected` ▸ `04_final` ▸ `04_final_machine`), domyślnie najświeższa
  redakcyjnie.
- **Obrazy:** grid z `images_post/` (fallback `images/`), `loading="lazy"`,
  klik → lightbox z numerem (1-based — ten od `--indices`) i nazwą pliku.
- **Miniatury:** `thumbnails_no_grain/` + `thumbnails_grain/` obok siebie.
- **Pliki:** drzewo folderu sluga; `.md` → render, obraz → podgląd, inne →
  ścieżka do skopiowania; stąd wejście do `edit/preview.html` i raportów
  (`06_qa`, `07_package`, `08_publish`) — bez osobnej zakładki Raporty.

## Backlog (zakładka 2)

Parser `docs/research/topic_backlog_PL.md` → pozycje: tier (ZŁOTO/SREBRO),
tytuł roboczy, archetyp, zalążek hooka (rozwijany). **Status produkcji**
(„nakręcony / w produkcji / wolny"): dopasowanie do slugów najpierw po `idx`
z nagłówków backlogu, fuzzy po tytule jako fallback; dopasowanie niepewne →
pozycja bez statusu (lepiej brak niż fałsz). Wolny temat → przycisk kopiujący
komendę startu (`agent1_research.py "<temat>"`).

## Odporność

- Nieparsowalny md → surowy tekst zamiast błędu.
- Brak `topic_backlog_PL.md` → zakładka Backlog znika.
- Pusty/szczątkowy folder sluga → karta z tym, co jest, zamiast crasha.
- Path traversal → 403 (sanityzacja `resolve()` + prefiks).
- Duże galerie → natywny lazy-load, bez serwerowych miniaturek (YAGNI na localhost).

## Testy

- pytest `pipeline_state.py`: syntetyczne foldery slugów (świeży / w połowie /
  ukończony / z plikami-niespodziankami) → oczekiwane etapy i „co dalej".
- pytest `backlog_parser.py`: realny backlog jako fixture → liczba pozycji,
  tiery, idx.
- Smoke serwera: start, `/api/state` zwraca 5 slugów z poprawnymi etapami,
  `/api/slug/...{path traversal}` → 403.

## Poza zakresem v1 (świadomie)

- Metryki/trendy (v2 — po danych Redaktora-ucznia), launchery subprocess (v2),
  jakikolwiek zapis do repo, auto-refresh websocket (F5 wystarcza),
  status „opublikowany na YT" (stan zewnętrzny — poza detekcją plikową),
  Electron/build-chain frontendu.
