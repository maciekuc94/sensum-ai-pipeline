import unittest

from tools.dev.draft_ceiling_report import sentence_diff_stats, split_sentences


class TestCeiling(unittest.TestCase):
    def test_split_sentences_basic(self):
        self.assertEqual(
            split_sentences("Ala ma kota. Kot ma Alę! Serio?"),
            ["Ala ma kota.", "Kot ma Alę!", "Serio?"],
        )

    def test_stats_buckets(self):
        machine = "Ala ma kota. Kot ma Alę. To jest zdanie trzecie. Czwarte zdanie istnieje."
        human = "Ala ma kota. Kot ma Alę! Piąte, zupełnie nowe."
        s = sentence_diff_stats(machine, human)
        self.assertEqual(s["machine_total"], 4)
        self.assertEqual(s["identical"], 1)          # "Ala ma kota."
        self.assertEqual(s["modified"], 1)           # "Kot ma Alę." -> "Kot ma Alę!" (ratio ~0.91)
        self.assertEqual(s["deleted"], 2)            # zdania 3-4 znikły
        self.assertEqual(s["added"], 1)              # "Piąte, zupełnie nowe."
        self.assertAlmostEqual(s["pct_touched"], (4 - 1) / 4 * 100, places=1)


if __name__ == "__main__":
    unittest.main()
