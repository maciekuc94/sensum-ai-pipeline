"""Testy rdzenia Redaktora-ucznia (tools/pipeline/redaktor_pary.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.dev.draft_ceiling_report import sentence_diff_stats, split_sentences
from tools.pipeline.redaktor_pary import (
    detect_generation,
    machine_sentences_with_sections,
    pair_sentences,
    strip_title,
    word_diff,
)

MS = [
    "To zdanie zostaje bez zmian.",
    "To zdanie maszyna przegadała bardzo mocno.",
    "To zdanie user usunie w całości.",
    "Drugie zdanie mechanizmu zostaje.",
]
HS = [
    "To zdanie zostaje bez zmian.",
    "To zdanie maszyna przegadała mocno.",
    "Drugie zdanie mechanizmu zostaje.",
    "To zdanie user dopisał całkiem od siebie późnym wieczorem.",
]


def test_pair_sentences_buckets():
    res = pair_sentences(MS, HS)
    assert res["identical"] == [(0, 0), (3, 2)]
    assert [(i, j) for i, j, _r in res["modified"]] == [(1, 1)]
    assert res["deleted"] == [2]
    assert res["added"] == [3]


def test_pair_sentences_zgodne_z_ceiling_report():
    """Te same teksty → te same liczby co sentence_diff_stats (kontrakt zgodności)."""
    machine_text = " ".join(MS)
    human_text = " ".join(HS)
    stats = sentence_diff_stats(machine_text, human_text)
    res = pair_sentences(split_sentences(machine_text), split_sentences(human_text))
    assert len(res["identical"]) == stats["identical"]
    assert len(res["modified"]) == stats["modified"]
    assert len(res["deleted"]) == stats["deleted"]
    assert len(res["added"]) == stats["added"]


MACHINE_MD = """# Tytuł roboczy

## Otwarcie

Pierwsze zdanie otwarcia. Drugie zdanie otwarcia.

## Mechanizm

Zdanie mechanizmu.
"""


def test_machine_sentences_with_sections():
    got = machine_sentences_with_sections(MACHINE_MD)
    assert got == [
        ("Pierwsze zdanie otwarcia.", "Otwarcie"),
        ("Drugie zdanie otwarcia.", "Otwarcie"),
        ("Zdanie mechanizmu.", "Mechanizm"),
    ]


def test_machine_sections_zgodne_ze_split_sentences():
    """Konkatenacja zdań z sekcji == split_sentences całości (zgodność liczb)."""
    assert [s for s, _ in machine_sentences_with_sections(MACHINE_MD)] == \
        split_sentences(MACHINE_MD)


def test_word_diff_markup():
    assert word_diff("ala ma kota w domu", "ala ma psa w domu") == \
        "ala ma [-kota-] {+psa+} w domu"
    assert word_diff("ala ma kota", "ala ma kota i psa") == "ala ma kota {+i psa+}"


def test_strip_title_usuwa_tytul_bez_interpunkcji():
    text = "Dlaczego jedna wpadka rozwala dzień\n\nPrzespałeś budzik.\n"
    assert strip_title(text).strip() == "Przespałeś budzik."


def test_strip_title_zostawia_zwykle_zdanie():
    text = "Przespałeś budzik.\nDruga linia.\n"
    assert strip_title(text) == text


def test_strip_title_zostawia_zdanie_z_typograficznym_cudzyslowem():
    text = "„Jestem do niczego.”\nDruga linia.\n"
    assert strip_title(text) == text


def test_detect_generation(tmp_path):
    md = tmp_path / "md"
    md.mkdir()
    (md / "04_final.md").write_text("x", encoding="utf-8")
    assert detect_generation(md) == "lean"
    (md / "04_final_presqueeze.md").write_text("x", encoding="utf-8")
    assert detect_generation(md) == "sciskacz"
    (md / "04_final_machine.md").write_text("x", encoding="utf-8")
    assert detect_generation(md) == "gen5"
