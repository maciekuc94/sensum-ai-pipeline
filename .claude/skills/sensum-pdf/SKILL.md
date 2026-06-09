---
name: sensum-pdf
description: Use when the user asks in plain language to turn / convert / export a Markdown (.md) file into a PDF in the SENSUM brand style — Polish triggers like "zrób z tego md pdf", "wyeksportuj do pdf w stylu sensum", "przerób md na pdf", "te md na pdf", "pdf z brandem sensum", "jeden długi pdf z researchu", "skonwertuj research do pdf", or English "export md to pdf / convert markdown to a SENSUM-styled PDF", optionally naming one file, several, or a folder ("wszystkie md w docs/research"). Routes to the canonical branded PDF converter (jedna długa strona, bez paginacji).
user-invocable: false
---

# SENSUM pdf — naturalny router eksportu Markdown → branded PDF

Pozwala wyeksportować dowolny `.md` do **jednego długiego PDF-a (bez podziału na strony)**
w stylu marki SENSUM mówiąc po ludzku („zrób z tego md pdf"), bez pamiętania komendy.
Routuje do **jednego kanonicznego narzędzia** — jedynego źródła prawdy o brandowym PDF.

## Krok 0 — Ustal, które pliki
User wskazuje plik(i): ścieżką, nazwą, opisem („te md z researchu", „backlog", „wszystkie
md w `docs/research`"). Rozwiąż do konkretnych ścieżek `.md`.
- Wiele plików / folder → przekaż wszystkie naraz (narzędzie bierze listę albo glob).
- Niejednoznaczne / brak trafienia → wylistuj kandydatów (`ls` / glob) i zapytaj który.
  (To jedyne dozwolone dopytanie.)

## Krok 1 — Uruchom kanoniczne narzędzie
Z korzenia repo:
```bash
PYTHONIOENCODING=utf-8 python tools/dev/md_to_pdf_sensum.py <plik.md> [<plik2.md> ...] --out outputs/channel_assets/research [--no-logo]
# glob też działa:  ... tools/dev/md_to_pdf_sensum.py "docs/research/*.md" --out outputs/channel_assets/research
```
- **Domyślny katalog wyjściowy: `outputs/channel_assets/research/`** (tam żyją brandowe PDF-y;
  ten katalog jest poza gitem). Bez `--out` PDF ląduje obok źródła — dla researchu **zawsze
  podawaj `--out`**, żeby nie zaśmiecać `docs/research/`. Jeśli user wskaże inny cel, użyj jego.
- Wymaga **systemowego Chrome + Playwright** (render md → HTML → PDF). Jest już w repo.
- Styl marki (tło #F4E5CA, atrament #582F0E, Cormorant + EB Garamond, logo, ziarno papieru,
  podwójne linie, ornament ❧, brązowe nagłówki tabel, **jedna długa strona bez paginacji**)
  jest **zaszyty w narzędziu** — **nie odtwarzaj go ręcznie i nie pisz własnego konwertera.**
- Kolorowe emoji (✅ / ⚠️ / 🟢…) są **automatycznie zamieniane na brązowe glify** (✓ / ⚠ / ●) —
  dwukolorowa paleta zachowana. Uszkodzone znaki `�` ze źródła są usuwane przy renderze, ale to
  **dziura w źródłowym `.md`** — wspomnij userowi, żeby je naprawił u źródła.
- Lokalne i darmowe (Playwright + systemowy Chrome, bez API/kredytów) → **nie pytaj o zgodę
  na koszt**, po prostu odpal.

## Krok 2 — Zweryfikuj
Narzędzie wypisuje dla każdego pliku: `OK <plik> -> <pdf>  (SZERxWYS px, KB)`. Sprawdź, że
plik powstał i że to **jedna wysoka strona** (wysokość = cała treść). Opcjonalny podgląd przez
PyMuPDF (fitz) — overview całości do PNG:
```bash
PYTHONIOENCODING=utf-8 python -c "import fitz,sys; d=fitz.open(sys.argv[1]); p=d[0]; print('strony=',d.page_count,'pt=%dx%d'%(p.rect.width,p.rect.height)); z=700/p.rect.width; p.get_pixmap(matrix=fitz.Matrix(z,z)).save('.tmp/_pdf_overview.png')" outputs/channel_assets/research/<plik>.pdf
```
Oczekiwane: `strony= 1`, bardzo wysoka strona. (Do oceny detali typografii: tnij na pionowe pasy.)

## Krok 3 — Zaraportuj
Podaj userowi ścieżki wynikowych `.pdf` i potwierdź: jedna długa strona + styl SENSUM
(beż #F4E5CA + brąz #582F0E, antyczna monografia).

## Uwagi
- **Jedna strona = brak paginacji** to CEL, nie błąd — nie „napraw" tego dzieląc na A4.
- **Przeznaczenie:** czytanie na ekranie. PDF bywa bardzo wysoki (np. ~7000–17000 px), nie pod druk A4.
- **Tylko PDF** — kanał nie używa już Worda; nie ma konwertera docx (świadomie usunięty).
- Paleta/fonty marki: spec mieszka w narzędziu (i `CLAUDE.md` Design Standards) — ten skill ich nie powiela.
- `.tmp/` jest jednorazowe — pliki podglądu możesz tam zostawić.
