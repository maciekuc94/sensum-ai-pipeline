"""Testy rdzenia Redaktora-ucznia (tools/pipeline/redaktor_pary.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.dev.draft_ceiling_report import sentence_diff_stats, split_sentences
import tools.pipeline.redaktor_pary as redaktor_pary
from tools.pipeline.redaktor_pary import (
    corpus_for_pair,
    detect_generation,
    ensure_extracted_all,
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


def _fake_pair(tmp_path):
    md = tmp_path / "md"
    md.mkdir()
    (md / "04_final_machine.md").write_text(
        "# Tytuł\n\n## Otwarcie\n\nZdanie zostaje bez żadnych zmian. "
        "To zdanie maszyna przegadała bardzo mocno.\n\n## Mechanizm\n\n"
        "To zdanie user usunie w całości. Drugie zdanie mechanizmu zostaje.\n",
        encoding="utf-8",
    )
    (md / "script_corrected.md").write_text(
        "Tytuł po redakcji bez kropki\n\nZdanie zostaje bez żadnych zmian. "
        "To zdanie maszyna przegadała mocno.\n\nDrugie zdanie mechanizmu zostaje. "
        "To zdanie user dopisał całkiem od siebie późnym wieczorem.\n",
        encoding="utf-8",
    )
    return {
        "slug": "9_testowy", "generation": "gen5",
        "machine": md / "04_final_machine.md", "human": md / "script_corrected.md",
    }


def test_corpus_for_pair(tmp_path):
    frag, stats = corpus_for_pair(_fake_pair(tmp_path))
    assert "## SLUG: 9_testowy [generacja: gen5]" in frag
    assert "[MOD] (sekcja: Otwarcie)" in frag
    assert "  D: To zdanie maszyna przegadała [-bardzo-] mocno." in frag
    assert "[DEL] (sekcja: Mechanizm)" in frag
    assert "  M: To zdanie user usunie w całości." in frag
    assert "[ADD] (po sekcji: Mechanizm)" in frag
    assert "  H: To zdanie user dopisał całkiem od siebie późnym wieczorem." in frag
    # identyczne zdania nie generują wpisów — dokładnie po jednym wpisie każdego typu
    assert frag.count("[MOD]") == 1
    assert frag.count("[DEL]") == 1
    assert frag.count("[ADD]") == 1
    assert stats["modified"] == 1 and stats["deleted"] == 1 and stats["added"] == 1


def test_ensure_extracted_all_odswieza_przeterminowane(tmp_path, monkeypatch):
    import docx as docx_lib

    monkeypatch.setattr(redaktor_pary, "VIDEOS_DIR", tmp_path)
    stale = tmp_path / "8_stale"
    (stale / "docx").mkdir(parents=True)
    (stale / "md").mkdir()
    d = docx_lib.Document()
    d.add_paragraph("Nowa wersja zdania.")
    d.save(stale / "docx" / "script_corrected.docx")
    (stale / "md" / "script_corrected.md").write_text("Stare.", encoding="utf-8")
    os.utime(stale / "md" / "script_corrected.md", (1, 1))  # md starszy niż docx

    fresh = tmp_path / "9_fresh"
    (fresh / "md").mkdir(parents=True)
    (fresh / "md" / "script_corrected.md").write_text("Bez docx.", encoding="utf-8")

    redaktor_pary.ensure_extracted_all()
    assert "Nowa wersja zdania." in (stale / "md" / "script_corrected.md").read_text(encoding="utf-8")
    assert (fresh / "md" / "script_corrected.md").read_text(encoding="utf-8") == "Bez docx."
