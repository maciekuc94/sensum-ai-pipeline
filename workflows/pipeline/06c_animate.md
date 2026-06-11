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
3. Przegląd: `images_anim/frames/NNN/strip.png` — kontaktówka klatek beatu;
   nieudane fazy re-rollować przez `--indices N --force`.

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

## Wyjścia

- `images_anim/image_NNN_anim.mp4` — zapętlony klip (mp4v, 1920×1080, ~10 s),
- `images_anim/frames/NNN/` — klatki + `strip.png` (kontaktówka do przeglądu).

## Flagi

- `--indices "1,37"` — tylko wskazane beaty (numery z planu),
- `--no-gen` — bez API: ponowna sklejka z istniejących klatek (zmiana
  Pattern/FPS/Seconds w planie = darmowa iteracja),
- `--force` — nadpisz istniejące klatki (re-roll).

## Edge cases / wiedza

- **Boil to feature** — klatki edycji różnią się drobiazgami w całej rycinie;
  użytkownik wybrał tę estetykę nad stabilizacją (2026-06-10). Nie stabilizować.
- Pętla jest **asynchroniczna względem audio** — celowo (działa bez nagrania).
- Klatki idempotentnie: istniejąca klatka nie jest regenerowana bez `--force`.
- Rate limit: 8 s między wywołaniami; 429 z backoffem (jak Agent 6).
- Gdyby DaVinci nie przyjął mp4v: przejść na PNG-sekwencję / ffmpeg (do dodania
  flagą, dotąd niepotrzebne).
- Koszt: ~2–3 edycje × ~$0.04 na beat → $1–2 na film. Nigdy nie uruchamiać
  generacji bez zaakceptowanego planu.
