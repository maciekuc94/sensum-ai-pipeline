"""Testy rdzenia Redaktora-ucznia (tools/pipeline/redaktor_pary.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.dev.draft_ceiling_report import sentence_diff_stats, split_sentences
from tools.pipeline.redaktor_pary import pair_sentences

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
