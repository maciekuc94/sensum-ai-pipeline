# Agent 6c — Ożywiacz (obiektowe pętle animacyjne)

## Cel

Zamienić kilkanaście wybranych ilustracji filmu w **zapętlone klipy MP4**, w których
obiekt lub postać żyje wewnątrz własnej sceny (budzik dzwoni, kropla kapie, postać
idzie w miejscu). Klip jest **drop-in** na timeline DaVinci — wstawiany zamiast
statycznego PNG; ruchy kamery użytkownika (zoomy/pany/tilty) pozostają bez zmian.

Decyzje i rationale: `brainstorms/2026-06-10-agent6c-ozywiacz.md`.
**Dotyczy wyłącznie nowych slugów (4+).** Istniejących filmów nie modyfikujemy.

## Wejścia

- `md/05_image_prompts.md` + `md/04_final.md` (lub `script_corrected`) — do typowania beatów,
- `images_post/image_NNN.png` (fallback `images/`) — bazy scen,
- `md/06c_animation_plan.md` — plan beatów (pisze `/animate`, akceptuje użytkownik).

## Przebieg

1. **`/animate <slug>`** (in-session): typuje 10–15 beatów wg zasady reżyserskiej
   **hook / metafora centralna / puenta** (pan/zoom habituuje — mikro-ruch działa,
   bo jest rzadki i związany znaczeniowo z narracją). Pisze plan i **zatrzymuje się**:
   lista + szacowany koszt idą do użytkownika. Generacja tylko po jego akceptacji
   (manual gate jak Agent 6).
2. **`python tools/pipeline/agent6c_animate.py "<slug>"`**: czyta plan i dla
   każdego beatu generuje fazy + skleja pętlę:
   - tryb `edit` (domyślny, ~80% beatów): edycje bazowej ilustracji
     w `gemini-2.5-flash-image` z GUARD-promptem ograniczającym zmianę do
     `Scope`; każda klatka przechodzi `two_color`;
   - tryb `sheet`: arkusz 3 faz od zera (CHARACTER_DESCRIPTION + V8) → cięcie
     na sprite'y (alpha z flood-fill; odłączone komponenty dotykające krawędzi
     cropu = wycieki z sąsiedniej figury → odrzucane) → kompozycja na scenie
     w punkcie `Anchor` (x,y = punkt stóp).
3. **Stabilizacja (obowiązkowa po KAŻDEJ generacji/re-rollu):**
   `python tools/dev/anim_lock_static.py "<slug>" [--beats "N,M"]`, potem sklejka
   `agent6c_animate.py "<slug>" --no-gen [--indices ...]`. Każda faza to niezależne
   przerysowanie sceny — obiekty lądują nawet 19–35 px obok (zmierzone, slug 4)
   i statyka „telepie się" w pętli. Narzędzie wyrównuje fazę do bazy (korelacja
   fazowa FFT) i zamraża wszystko poza automatyczną maską ruchu (gęstość diffu) —
   statyka staje się pikselami bazy 1:1, boil kreski zostaje w strefie ruchu.
   Oryginały Gemini trafiają do `frames/NNN/raw/` (pełny rollback: `--restore`).
   **Po re-rollu beatu skasuj jego stare `frames/NNN/raw/`** — inaczej narzędzie
   przetworzy poprzednie klatki zamiast świeżych.
4. Przegląd: `images_anim/frames/NNN/strip.png` — kontaktówka klatek beatu;
   nieudane fazy re-rollować przez `--indices N --force`. Przed re-rollem beatu,
   w którym część faz wyszła dobrze, zabezpiecz udane `raw/{faza}.png` (np. do
   `frames/_keep/`) — po re-rollu można je przywrócić do `raw/` i przekleić
   beat lokalnie (`anim_lock_static` + `--no-gen`, zero API).

## Format planu (`md/06c_animation_plan.md`)

```md
## Beat 001
**Image:** image_001.png
**Mode:** edit
**Motion:** ring
**FPS:** 8
**Seconds:** 10
**Pattern:** a,b,a,b,c,a,b,base,base,base
**Scope:** the alarm clock bells and hammer area
**Phase a:** the tiny hammer tilted LEFT, two short vibration strokes left of the left bell.
**Phase b:** the tiny hammer tilted RIGHT, two short vibration strokes right of the right bell.
**Phase c:** the hammer centered and motion-blurred, paired vibration arcs on both sides.
```

Pola trybu `sheet` dodatkowo: `**Sheet-poses:**` (opis trzech faz arkusza),
`**Anchor:** x,y`. `Pattern` odwołuje się do nazw faz i `base`.

Wzory pętli wg ruchu: dzwonek/wibracja `a,b,a,b,c,a,b,base,base,base` @ 8 fps;
chód `base,a,b,a` @ 4.5–5 fps; kropla/para 3–4 fps z dłuższymi pauzami na `base`.

**Standard amplitudy (rewizja slug 4, 2026-06-12).** Fazy pisać jako **dyskretne,
mechaniczne stany obiektu o DUŻEJ, czytelnej amplitudzie** — dzwonek wyraźnie
w LEWO / wyraźnie w PRAWO, kłąb pary na 1/3 kadru, łańcuch struna vs luźny zwis.
Zakazane słowa: „slightly", „a hair", „a touch", „subtle" — model wykonuje je
za drobno i ruch **nie czyta się** na 1080p w 10-sekundowej pętli (zmierzone:
beaty pisane asekuracyjnie user ocenił „nic się nie dzieje"). Wzorce: dzwonek 059,
bojler 060 (slug 4). Do opisu fazy dopisywać twarde inwarianty sceny („the tear
must NEVER be repaired", „stays INSIDE the chamber", „no sleeve, no cuff") —
typowe wykolejenia modelu to: naprawienie uszkodzenia zamiast pogłębienia,
wyjście ruchu poza Scope, skasowanie obiektu, dorysowanie ubrania, solid fill
zamiast szrafowania (tusz +100% = stroboskop).

## Wyjścia

- `images_anim/image_NNN_anim.mp4` — zapętlony klip (mp4v, 1920×1080, ~10 s),
- `images_anim/frames/NNN/` — klatki + `strip.png` (kontaktówka do przeglądu).

## Flagi

- `--indices "1,37"` — tylko wskazane beaty (numery z planu),
- `--no-gen` — bez API: ponowna sklejka z istniejących klatek (zmiana
  Pattern/FPS/Seconds w planie = darmowa iteracja),
- `--force` — nadpisz istniejące klatki (re-roll).

## Edge cases / wiedza

- **Boil kreski = feature, misrejestracja obiektów = bug (doprecyzowane 2026-06-12).**
  Drobne różnice rysunku w całej rycinie zostają (decyzja usera 2026-06-10); ale
  przesunięcia CAŁYCH obiektów między fazami (do 35 px) to wada — korygowana
  deterministycznie przez `tools/dev/anim_lock_static.py` (krok 3 Przebiegu).
  Nie wygładzać samego boilu (żadnego deflickera/morphingu klatek).
- **Beaty, gdzie nieruchomość jest treścią, tnij zamiast wymuszać ruch** —
  miażdżący ciężar, zatrzymanie w puencie, pulsowanie gęstości kreski (echo)
  nie zagrają; statyczne PNG między pętlami to celowy kontrast. Koncepty z ruchem
  na drobnym detalu małej sceny (płomień w komorze piersiowej, slug 4) padały
  3× z rzędu — po 2 nieudanych re-rollach tego samego konceptu: wytnij.
- Pętla jest **asynchroniczna względem audio** — celowo (działa bez nagrania).
- Klatki idempotentnie: istniejąca klatka nie jest regenerowana bez `--force`.
- Rate limit: 8 s między wywołaniami; 429 z backoffem (jak Agent 6).
- Gdyby DaVinci nie przyjął mp4v: przejść na PNG-sekwencję / ffmpeg (do dodania
  flagą, dotąd niepotrzebne).
- Koszt: ~2–3 edycje × ~$0.04 na beat → $1–2 na film. Nigdy nie uruchamiać
  generacji bez zaakceptowanego planu.
