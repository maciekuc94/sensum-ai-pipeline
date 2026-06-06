# Workflow: Cienka bramka doktryny (Claude Code, in-session)

## Rola

**Ostatni, lekki check przed `04_final.md`** — NIE dawna triage-maszyna kategorii A–K. Lead (in-session, Opus 4.8) przepuszcza finalny `04_working.md` przez **listę nienegocjowalnych** raz. To NIE jest pętla i NIE liczy severity — to bezpiecznik łapiący twarde naruszenie doktryny, które mogło prześlizgnąć się przez czytelników (oni sądzą spójność i głos, nie politykę).

Uruchamiasz to **po** tym, jak panel czytelników dał „PŁYNIE" (albo po miękkim limicie rund).

## Checklist nienegocjowalnych (każde = twarde naruszenie)

Przejdź skrypt raz i sprawdź:

1. **Research-invisible.** Zero „badania pokazują / naukowcy odkryli / z badań wynika / meta-analiza / w [roku]", zero nazwisk badaczy, lat, cytatów w narracji. Wyjątek: **jedna** dozwolona kotwica kliniczna „Badania nad [efektem] pokazują…" (np. „efekt świeżego startu") + wyjątek Darwina w Historical Reversal. (`style_guide.md` §4, §10.)
2. **Bez liczb-findings / niecytowanego statu.** Zero dziesiętnych, effect sizes, p-values, liczb badań/uczestników, terminów metodologicznych. Nawet zaokrąglona liczba podana jak fakt („blisko połowy…") → opisz zjawisko bez liczby. (`style_guide.md` §11, §12.13.)
3. **Druga osoba, bezrodzajowo.** Całość w „ty"; zero „ja/my/oni"; zero prowadzenia postaci w 3. osobie. Formy bezpłciowe — brak form męskich zdradzających płeć poza świadomym wyjątkiem. (`voice_corpus.md` §G.)
4. **Zero numerowanych list** preskrypcyjnych gdziekolwiek. (Nagłówki `## ` to NIE listy — są dozwolone i oczekiwane.)
5. **Recognition close ma ostatnie słowo** — ostatnia linia ląduje na rozpoznaniu, nigdy na poradzie/kroku. PP opcjonalna; jeśli jest — proza (nie numerowana lista), przed close.
6. **Brak zakazanych fraz** — duchowo-rozwojowe („zaufaj procesowi", „wszechświat", „wibracje"), akademickie („warto zauważyć", „należy podkreślić", „kluczowe jest"), coachingowe („mindset", „narzędzia", „najlepsza wersja siebie"). (`style_guide.md` §10.)
7. **Jedna główna metafora** — bez stosu pobocznych domen (podatek + dom na wodzie + bak + loteria…). (`style_guide.md` §8 / §12.11.)

## Działanie

- **Czysto** → kopiuj `04_working.md` → `04_final.md`, **zdejmując wiodącą linię `ARCHITECTURE:`** (to metadane maszynowe; architektura zostaje w `md/03_architecture.md`). `04_final.md` zaczyna się od pierwszego nagłówka `## ` albo pierwszej linii sceny. Zachowaj dividery `## `.
- **Twarde naruszenie, które integrator umie czysto poprawić** → integrator poprawia **w miejscu** (jedno celowane przejście, bez ruszania reszty), potem ship. To NIE odpala pełnej pętli czytelników.
- **Naruszenie, którego nie da się czysto poprawić bez ryzyka dla głosu** → `AskUserQuestion`: (a) popraw w miejscu wg wskazówki, (b) przyjmij z nagłówkiem WARNING wskazującym naruszenie i plik.

## Uwaga (granica)

Bramka jest **cienka z założenia.** NIE przywracaj tu dawnych mechanizmów (iteration dampener, anti-sterility jako hamulec, severity-triage, skan kategorii A–K) — życie i spójność pilnują czytelnicy, a Ty pilnujesz **tylko** nienegocjowalnych. Over-policing tutaj zabija dokładnie to, co ten redesign naprawił (płynność i ciepło).
