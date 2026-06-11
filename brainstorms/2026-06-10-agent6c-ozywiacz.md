# Agent 6c „Ożywiacz" — obiektowe pętle animacyjne (2026-06-10)

## Decyzja

Nowy etap pipeline'u: **Agent 6c** zamienia kilkanaście wybranych ilustracji filmu
w **zapętlone klipy MP4** (obiekt/postać żyje wewnątrz własnej sceny), które na
timeline w DaVinci wrzuca się **zamiast PNG** — ruchy kamery użytkownika (delikatne
zoomy/pany/tilty) pozostają bez zmian. Dotyczy **wyłącznie nowych slugów (4+)**;
istniejących filmów nie modyfikujemy.

## Jak do tego doszliśmy (skrót)

1. Eksploracja „animacji storytellingowej": demo draw-on (5 wariantów, mechanizm
   maski podążającej za piórem) + mock „Wędrówki" (postać idzie przez fryz,
   3 rundy zimnego krytyka z twardą rubryką R1–R10).
2. Użytkownik wybrał kurs „po środku": nie pełna reżyseria fryzu, lecz
   **ożywienie obiektów w ilustracjach** (budzik dzwoni, kropla kapie, postać
   idzie w miejscu) przy zachowaniu dotychczasowego workflow montażu.
3. Pilot budzika (image_001, slug 3): edycje Gemini → two_color → pętla 8 fps.
   **Wersja z „boilem" całej kreski wygrała ze stabilizowaną** (decyzja smakowa
   użytkownika — boil = rycina oddycha; stabilizacja „wygląda dziwnie").
4. Pilot chodu (image_052 + sprite'y arkusza): technika **edit** (edycja sceny)
   vs **sheet** (arkusz póz → sprite'y → kompozycja). Obie działają; edit osadza
   ruch w kompozycji sceny, sheet daje idealną spójność klatek i swobodę.

## Architektura (WAT)

- **`/animate <slug>`** (Layer 2, in-session): czyta `05_image_prompts.md` +
  skrypt; typuje 10–15 beatów wg zasady reżyserskiej **hook / metafora
  centralna / puenta** (nie losowo); pisze `md/06c_animation_plan.md`;
  **manual gate** — lista + koszt do akceptacji użytkownika przed generacją.
- **`tools/pipeline/agent6c_animate.py <slug>`** (Layer 3, deterministyczny):
  parsuje plan; tryb `edit` = edycje bazowego PNG w gemini-2.5-flash-image
  z GUARD-promptem („zmień wyłącznie {scope}") → `two_color` → sklejka pętli wg
  wzoru; tryb `sheet` = arkusz faz + cięcie (connected components + alpha
  flood-fill + odrzut wycieków krawędziowych) + kompozycja na tle/scenie.
  Wyjście: `images_anim/image_NNN_anim.mp4` + klatki w `images_anim/frames/NNN/`.
- **Wzory pętli** (pattern w planie): sekwencja nazw faz + `base`, np. dzwonek
  `a,b,a,b,c,a,b,base,base,base` @ 8 fps („dryń-dryń… pauza"), chód
  `base,a,b,a` @ 5 fps, para/kropla 3–4 fps.

## Ustalenia twarde

- **Boil = feature.** Żadnej stabilizacji klatek (usunięta po decyzji usera).
- **Drop-in MP4** (mp4v, 1920×1080, ~10 s) — nie 4 PNG w timeline, nie zmiany
  w `agent_align`/FCPXML (użytkownik układa ręcznie jak dotąd).
- **Pętla asynchroniczna** względem audio — brak synchronizacji w v1 (działa
  zawsze, bez zależności od nagrania).
- **Koszt:** ~2–3 edycje × ~$0.04 na beat → **$1–2 na film**; generacja tylko po
  akceptacji planu (manual gate jak Agent 6).
- Poza zakresem v1: LoRA postaci (osobny tor), draw-on w klipach, „Wędrówka"
  (pełny fryz — mock zachowany w `.tmp/journey_mock/` jako poziom 2 na później).

## Rationale wyboru beatów (do /animate)

Pan/zoom habituuje po 2–3 min — mikro-ruch w treści działa, bo jest **rzadki**
i **związany znaczeniowo** z narracją (budzik dzwoni, gdy lektor mówi o budziku).
Żywa scena niesie 8–12 s ujęcia (statyka umiera po 3–5 s) — beaty refleksyjne
mogą oddychać. Animujemy tam, gdzie skrypt uderza; statyka tam, gdzie szepcze.
Po slugu 4: porównać krzywą retencji ze slugami 1–3 w analogicznych miejscach.
