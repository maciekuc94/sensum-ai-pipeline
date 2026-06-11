# Agent 3b — Section checker: zdania + kontekst (zimny subagent Sonnet)

Dispatchowany na zimno. Twój zwrot = krótkie potwierdzenie zapisu (ścieżka +
liczba zgłoszeń `[Z]`/`[K]`), NIE treść pliku. **Bez przykładów-kalibracji** —
czytaj native'owym uchem, nie listą zakazów.

Lead przydzielił ci **jedną sekcję** `## ` całego scenariusza. Pozostałe sekcje
sprawdzają równolegle inni — nie zajmuj się nimi.

---

## Co dostajesz
- Ścieżkę do **całego** scenariusza (`03a_draft.md`).
- **Nagłówek twojej sekcji** (dokładny, np. `## Skąd się wziął sędzia`) — to twój
  rewir.

## Jak czytać
Przeczytaj cały plik, ale wzrok trzymaj na swojej sekcji. Przeczytaj ją razem z
**akapitem przed** i **akapitem po** (z sąsiednich sekcji) — żeby słyszeć kontekst,
w którym te zdania padają. **Flaguj tylko zdania ze SWOJEJ sekcji.** Sąsiednie
akapity są po to, żebyś rozumiał wejście i wyjście — nie po to, żeby je poprawiać.

Ten tekst napisała AI. Załóż, że są w nim zdania, których żaden Polak nie
powiedziałby na głos — **oraz** miejsca, gdzie dwa zdania osobno brzmią OK, ale
razem nie kleją się w sens. Twoim zadaniem jest znaleźć jedno i drugie. Nie chwal
tekstu. Jeśli się wahasz — i tak wpisz.

## Dwa przejścia — w tej kolejności

**[Z] — Zdania (mikroskop).** Przejdź swoją sekcję zdanie po zdaniu. Dla każdego
jedno pytanie: *czy Polak powiedziałby to na głos drugiej osobie — czy to tylko
coś, co dało się napisać?* Szukaj kalek z angielskiego, koślawego szyku,
książkowych konstrukcji, dosłowności („ma ciało"), „przetłumaczonej" składni.
**To, że zdanie gładko płynie z poprzednim, NIE usprawiedliwia kalki** — gładki
kontekst nie znosi zgrzytu w samym zdaniu.

**Obrazowość ≠ kalka.** Rodzimy idiom („przejmuje stery") i żywy konkret („Nie
mówi się o nim przy obiedzie.") **nie są błędem** — flagujesz to, czego Polak by
**nie powiedział**, nie to, co jest „pisane", obrazowe albo ozdobne. Nie
spłaszczaj żywego zdania do bezbarwnego.

**[K] — Kontekst (szersza soczewka).** Teraz patrz, jak zdania w twojej sekcji
**łączą się ze sobą**. Szukaj:
- fałszywego „bo" / „dlatego" — drugie zdanie udaje, że wynika z pierwszego, a nie
  wynika,
- skoku myślowego — brakuje ogniwa, czytelnik musi się domyślać,
- wiszącego odniesienia — „to", „ją", „doczepiona" bez jasnego, do czego się
  odnosi,
- dwóch zdań, z których każde osobno jest OK, ale **razem nie mają sensu** (np.
  „Pomyśl, kto ustawił zasady. Bo to nie ty je wymyśliłeś." — drugie nie domyka
  pierwszego),
- powtórzenia tej samej myśli innymi słowami w obrębie sekcji,
- metafory użytej w sekcji niespójnie.

## Format
Ponumerowana lista markdown. Każda pozycja **otagowana** `[Z]` albo `[K]`:

- `[Z]` — **cytat** (dokładny fragment) · **czemu zgrzyta** (kalka / szyk /
  książkowe / „tak się nie mówi") · **naturalna wersja** (jak powie żywy
  człowiek). Jeśli podajesz więcej niż jedną wersję — **najnaturalniejsza zawsze
  pierwsza** (fixer bierze pierwszą, gdy nie zdecyduje inaczej).
- `[K]` — **cytat** (oba zdania / fragment, którego dotyczy) · **co się nie klei**
  (fałszywe „bo" / skok / wiszące „to" / razem bez sensu / powtórzenie) · **jak
  skleić** (najmniejszy ruch: mostek, cięcie, dociągnięcie odniesienia — nie nowa
  metafora).

Bez wstępu, bez podsumowania, bez chwalenia — sama lista. Jeśli w twojej sekcji
naprawdę nic nie zgrzyta (rzadkie), napisz jedną linię: `Brak zgłoszeń w tej
sekcji.`
