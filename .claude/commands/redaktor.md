---
description: Redaktor-uczeń — wzorce z docx-passów usera (korpus → 3 zimnych kategoryzatorów → synteza → manual gate)
argument-hint: <slug>
---

# /redaktor — kopalnia wzorców z redakcji usera

Wykonuj `workflows/pipeline/redaktor.md`. Slug: `$1`.

## Step 1 — Korpus (Bash)

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/redaktor_pary.py "$1"
```

Exit 1 → STOP, przekaż userowi komunikat toola. Zanotuj liczby MOD/DEL/ADD
i trend z wyjścia.

## Step 2 — Ensemble (RÓWNOLEGLE — wszystkie 3 spawny w JEDNEJ wiadomości)

Trzy spawny `subagent_type: redaktor-kategoryzator`, identyczny brief poza N
(1, 2, 3):

> Jesteś badaczem stylu redakcyjnego, dispatchowanym na zimno. Przeczytaj
> `workflows/pipeline/redaktor_kategoryzator.md` i wykonaj go dokładnie.
> Korpus: `.tmp/redaktor_korpus.md`. Twój numer: N=<N>. Zapisz wzorce do
> `.tmp/redaktor_kat_<N>.md`. Twój zwrot = jedna linijka (ścieżka + liczba
> wzorców), NIE treść pliku.

Fallback: typ niezarejestrowany → `general-purpose` z `model: opus`, ten sam
brief. Poczekaj aż wszystkie 3 skończą.

## Step 3 — Synteza (Ty, in-session)

Przeczytaj `.tmp/redaktor_kat_{1,2,3}.md` + `workflows/guides/redakcja_wnioski.md`.
Progi i typy propozycji — wg `workflows/pipeline/redaktor.md` krok 3
(≥2/3 kategoryzatorów, ≥2 filmy, flaga generacji).

## Step 4 — Raport

Zapisz `docs/research/redaktor/raport_$(date +%F).md` wg sekcji z SOP (krok 4).
Pokaż userowi skrót: liczba wzorców potwierdzonych, trend ceiling, lista
propozycji jedną linijką każda.

## Step 5 — Manual gate + aplikacja

AskUserQuestion (multiSelect) z propozycjami DODAJ/WZMOCNIJ/WYGAŚ. Zaakceptowane
zaaplikuj do `workflows/guides/redakcja_wnioski.md` (max 10 aktywnych; format
wpisu z komentarza w tym pliku; daty; status wstępny/aktywny). Na koniec:

```bash
git add workflows/guides/redakcja_wnioski.md docs/research/redaktor/
git commit -m "feat(redaktor): wnioski po $1"
```

Nic nie zaakceptowane → commit samego raportu.

## Czego NIE robić
- NIE pokazuj kategoryzatorom `redakcja_wnioski.md` (ślepa re-walidacja).
- NIE edytuj `voice_brief.md`, promptu pisarza ani fixera.
- NIE aplikuj żadnego wniosku bez akceptu w Step 5.
