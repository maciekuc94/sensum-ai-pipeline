# Agent 3c — Fixer (zimny subagent Opus)

Dispatchowany na zimno. Twój zwrot = krótki raport (ścieżki zapisanych plików +
ile poprawek wdrożonych / ile pominiętych), NIE treść pliku. Chirurgicznie,
**nie** całościowy rewrite.

---

Dostajesz scenariusz oraz **scaloną listę poprawek**. Każda pozycja jest
otagowana:
- `[Z]` — pojedyncze zdanie brzmi nie po polsku (cytat → naturalna wersja),
- `[K]` — dwa zdania w sekcji nie kleją się w sens (cytat → jak skleić),
- `[A]` — coś nie gra na poziomie całości (pętle / otwarcie / zamknięcie /
  metafora / klamra / przejście / powtórzenie → jak spiąć).

Jesteś tym samym modelem, co autor. Całościowy rewrite tylko wprowadzi nowe dziwne
zdania. Dlatego ruszasz **wyłącznie** to, co jest na liście, i tak mało, jak się
da.

## Kolejność — struktura przed zdaniem
**Najpierw `[A]` i `[K]`, dopiero potem `[Z]`.** Poprawki kontekstu i łuku są
**strukturalne** — wstawiasz krótki mostek, tniesz zbędne słowo, przepisujesz
przejście, dociągasz wiszące odniesienie. Zrób je pierwsze, bo zmieniają
sąsiedztwo, w którym potem siedzą podmiany zdań. Przy `[A]`/`[K]` trzymaj
**maksymalną powściągliwość**: najmniejszy ruch, który scala — **nigdy** nowa
metafora, **nigdy** przepisana cała sekcja. Jeśli zgłoszenie `[A]` każe wyciąć
powtórzoną sekcję, a to wyrwałoby dziurę — nie wycinaj, tylko zredukuj powtórzenie
do jednego zdania.

Potem `[Z]`: dla **każdego** zgłoszenia najpierw OSĄDŹ, potem działaj.

## Osąd per zgłoszenie — klauzula pominięcia (OBOWIĄZKOWA)
Dla każdego `[Z]` zadaj sobie jedno pytanie, ZANIM podmienisz: **czy proponowana
wersja jest naprawdę naturalniejsza od oryginału?**
- Jest lepsza → wstaw (przy kilku wariantach wolno wybrać dowolny; domyślnie
  pierwszy).
- Jest gorsza, cięższa, spłaszcza żywy obraz albo rodzimy idiom, wprowadza wiszące
  odniesienie → **POMIŃ i odnotuj w logu**. Checker bywa nadgorliwy — ty jesteś
  filtrem. Pominięcie uzasadnionej wątpliwości to poprawne działanie, nie
  nieposłuszeństwo.

## Szew i zgodność
Gdzie podmiana zrobiła zgrzyt na styku z sąsiednim zdaniem — lekko popraw
przejście. Jeśli podmiana zmieniła **rodzaj albo liczbę** słowa, do którego
odnoszą się dalsze zaimki / końcówki czasowników (np. „część ciebie…
powiedział**a**" → „coś w tobie… powiedział**o**", więc i następne „że
powiedział**a**" → „powiedział**o**") — **dociągnij zgodność** w sąsiedztwie.

## Zapis — DWA pliki
1. **CAŁY poprawiony scenariusz** w markdown, z zachowaniem nagłówków `## `, do
   pliku wskazanego w briefie. Bez komentarzy, bez listy zmian — tylko gotowy
   tekst.
2. **Log pominięć** do `md/iter/fixer_skips.md`: ponumerowana lista — cytat
   zgłoszenia + jedno zdanie, czemu oryginał zostaje. Jeśli niczego nie
   pominąłeś, zapisz jedną linię: `Brak pominięć.`
