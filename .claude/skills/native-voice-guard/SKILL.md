---
name: native-voice-guard
description: Use when about to write, rewrite, tighten, translate, or "improve" ANY spoken SENSUM script prose OUTSIDE the /draft and /publish commands — freeform Polish requests like "napisz/przepisz/popraw akapit", "napisz inne intro", "przepisz zakończenie", "skróć ten fragment", "napisz alternatywną wersję", or English "rewrite this paragraph / write a new opening". Loads the binding SENSUM voice brief (v2, 7 rules) so a one-off rewrite stays on-voice instead of drifting — /draft runs the writer→checker→fixer chain, but freeform prose has no other backstop.
user-invocable: false
---

# Native Voice Guard

Edycje prozy SENSUM robione poza `/draft` nie przechodzą przez łańcuch
**pisarz → checker → fixer** (on biegnie tylko w `/draft`). Ten skill jest jedynym,
co stoi między doraźnym przepisaniem a dryfem głosu. To **cienki wskaźnik**, nie
kopia reguł — żywy kanon żyje w `workflows/guides/voice_brief.md` (v2, 2026-06-07).

## Kanon (każda wolna edycja prozy) — 7 reguł v2 z `voice_brief.md`
1. **Ciepło, do jednej osoby — ale wolno też wyjaśnić zjawisko.** „Ty", jak mądry
   przyjaciel. Głównie DO człowieka — czasem jednak wolno trochę wytłumaczyć
   mechanizm; zrozumienie pogłębia to, do czego prowadzisz.
2. **Uczucia nazywaj wprost.** Wstyd, wina, lęk, wyrzuty sumienia — rdzeń kanału,
   **NIE** żargon. Wolno je nazywać po imieniu.
3. **Bez żargonu trudnego dla zwykłego człowieka.** Czego przeciętny człowiek nie
   rozumie („dysonans poznawczy", „kwantyfikator") — wytnij. Zrozumiałe („układ
   nerwowy") — wolno. Test: czy zwykły człowiek to rozumie.
4. **Mechanizm — tak; atrybucja do badań — nie.** Mechanizm wolno wyjaśnić, ale
   jak rzecz, którą po prostu wiesz — **bez** „badania pokazują" w narracji
   (atrybucja żyje tylko w opisie Agenta 8; ściskacz 3d i tak ją tnie). Wciąż
   **bez** nazwisk badaczy, lat, decymali, effect-size, p-value, liczby badań.
   Liczba bez emocji — wytnij.
5. **Otwórz hookiem, zamknij rozpoznaniem.** Recognition close zawsze ostatni —
   pokazuje człowiekowi coś o nim samym, nie porada, nie lista.
6. **Część praktyczna — opcjonalna i lekka.** Tylko jeśli wynika z treści; płynna
   proza, **nigdy** numerowana lista.
7. **Naturalny mówiony polski + naturalny rodzaj.** Jak Polak mówi na głos. Rodzaj
   męski generyczny zawsze OK — używaj go, kiedykolwiek trzeba.

**Nadrzędne:** pisz luźno, naturalność > ozdobność. **Metafora — wolność:** nie
musisz trzymać się jednej; wolno kilka obrazów, jeśli ożywiają tekst.

**Test nadrzędny:** czy Polak powiedziałby to na głos drugiej osobie — czy to
tylko coś, co dało się napisać?

## Jeśli user wprost prosi o coś poza kanonem
Instrukcje usera biją ten skill. Jeśli *wprost* chce nazwanej liczby/statystyki,
nazwiska badacza, roku, terminu metodologicznego, atrybucji „badania pokazują" albo
numerowanej listy: nie milcz i nie odmawiaj — zgłoś konflikt **raz** („to poza
doktryną głosu SENSUM — potwierdzasz?"), potwierdź, jedź. (Zrozumiały termin jest
w kanonie — bez pytania; „badania pokazują" NIE — zgłoś jak resztę.)

## Źródło prawdy
- `workflows/guides/voice_brief.md` — kanon v2, 7 reguł (ten plik tylko go streszcza)
- `CLAUDE.md` → „### Script voice — the non-negotiables"

## Czego ten skill NIE robi
Nie zastępuje `/draft` (pisarz → checker → fixer) ani Twojego ucha na
`script_corrected.docx`. Trzyma tylko wolną, jednorazową edycję na głosie od
pierwszego podejścia.
