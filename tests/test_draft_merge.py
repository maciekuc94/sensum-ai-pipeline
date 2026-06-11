import unittest
from pathlib import Path
import tempfile

from tools.pipeline.draft_merge import merge_corrections, count_tags

ARC = """## Mapa pętli
- Otwarcie: pytanie o budzik -> domknięte w sekcji 06.

## Zgłoszenia [A]
1. [A] gdzie: Otwarcie + Zamknięcie · co nie gra: klamra niespłacona · jak spiąć: dopowiedz obraz budzika.
2. [A] gdzie: sekcje 03-04 · co nie gra: powtórzenie · jak spiąć: zredukuj do zdania.
"""

SEK_01 = """1. [Z] cytat: „ma ciało" · czemu zgrzyta: kalka · naturalna wersja: „jest namacalny".
2. [K] cytat: „Pomyśl. Bo to nie ty." · co się nie klei: fałszywe „bo" · jak skleić: usuń spójnik.
"""

SEK_02 = "Brak zgłoszeń w tej sekcji.\n"


class TestMerge(unittest.TestCase):
    def _build_iter(self, tmp: Path) -> Path:
        it = tmp / "iter"
        it.mkdir()
        (it / "arc.md").write_text(ARC, encoding="utf-8")
        (it / "sek_01.md").write_text(SEK_01, encoding="utf-8")
        (it / "sek_02.md").write_text(SEK_02, encoding="utf-8")
        return it

    def test_merge_order_and_skip(self):
        with tempfile.TemporaryDirectory() as td:
            body, counts = merge_corrections(self._build_iter(Path(td)))
            self.assertLess(body.index("[A]"), body.index("[Z]"))  # arc przed sekcjami
            self.assertNotIn("Mapa pętli", body)                    # mapa NIE wchodzi do korekt
            self.assertNotIn("Brak zgłoszeń", body)                 # sek_02 pominięta
            self.assertIn("sek_01", body)
            self.assertEqual(counts, {"A": 2, "Z": 1, "K": 1})

    def test_count_tags_ignores_prose_mentions(self):
        body = "naglowek o zgloszeniach [Z] i [K]\n1. [Z] cytat · x · y\n2. [K] cytat · x · y\n"
        self.assertEqual(count_tags(body), {"A": 0, "Z": 1, "K": 1})


if __name__ == "__main__":
    unittest.main()
