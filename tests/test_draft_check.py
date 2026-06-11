import unittest

from tools.pipeline.draft_check import validate_script

DRAFT = """## Otwarcie

Przespałeś budzik. To nie koniec świata.

## Zamknięcie

Może problem nigdy nie był w tobie.
"""

GOOD_FINAL = DRAFT  # te same sekcje, czysta narracja


class TestValidate(unittest.TestCase):
    def test_clean_script_passes(self):
        findings = validate_script(DRAFT, GOOD_FINAL, min_words=5, max_words=50)
        self.assertEqual(findings, [])

    def test_missing_section_flagged(self):
        final = GOOD_FINAL.replace("## Zamknięcie", "## Inny tytuł")
        findings = validate_script(DRAFT, final, min_words=5, max_words=50)
        self.assertTrue(any("Zamknięcie" in f for f in findings))

    def test_banned_attribution_flagged(self):
        final = GOOD_FINAL + "\nBadania pokazują, że to działa.\n"
        findings = validate_script(DRAFT, final, min_words=5, max_words=50)
        self.assertTrue(any("badania pokazują" in f.lower() for f in findings))

    def test_digits_and_tags_flagged(self):
        final = GOOD_FINAL + "\nAż 73 procent ludzi. [Z] artefakt.\n"
        findings = validate_script(DRAFT, final, min_words=5, max_words=60)
        self.assertTrue(any("cyfr" in f.lower() for f in findings))
        self.assertTrue(any("artefakt" in f.lower() or "[Z]" in f for f in findings))

    def test_word_window(self):
        findings = validate_script(DRAFT, GOOD_FINAL, min_words=1500, max_words=2200)
        self.assertTrue(any("words" in f.lower() or "słów" in f.lower() for f in findings))


if __name__ == "__main__":
    unittest.main()
