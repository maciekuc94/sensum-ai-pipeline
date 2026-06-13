"""Testy Mission Control: pipeline_state, backlog_parser, API."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.mission_control.pipeline_state import detect, slug_title


def _mk(d, rel, content="x"):
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def _fresh_slug(tmp_path):
    d = tmp_path / "9_testowy"
    _mk(d, "md/01_research.md")
    _mk(d, "md/02_verified_research.md")
    return d


def test_detect_fresh_slug_next_is_draft(tmp_path):
    info = detect(_fresh_slug(tmp_path))
    assert info["slug"] == "9_testowy"
    done = {s["id"] for s in info["stages"] if s["done"]}
    assert done == {"research", "weryfikacja"}
    assert [a["stage"] for a in info["next"]] == ["skrypt"]
    assert info["next"][0]["command"] == "/draft 9_testowy"
    assert info["finished"] is False


def test_detect_po_docx_dwie_akcje_rownolegle(tmp_path):
    d = _fresh_slug(tmp_path)
    _mk(d, "md/04_final.md", "# Tytul probny\n\n## Otwarcie\n\nZdanie.\n")
    _mk(d, "md/script_corrected.md", "Tytul po redakcji\n\nZdanie.\n")
    info = detect(d)
    assert [a["stage"] for a in info["next"]] == ["visuals", "package"]
    assert info["next"][0]["command"] == "/visuals 9_testowy"
    assert info["next"][1]["command"] == "/package 9_testowy"


def test_detect_manual_step_bez_komendy(tmp_path):
    d = _fresh_slug(tmp_path)
    _mk(d, "md/04_final.md", "# T\n")
    info = detect(d)
    assert [a["stage"] for a in info["next"]] == ["docx"]
    assert info["next"][0]["command"] is None
    assert "script_corrected" in info["next"][0]["manual_hint"]


def test_detect_finished_mov(tmp_path):
    d = _fresh_slug(tmp_path)
    for rel in ("md/04_final.md", "md/script_corrected.md", "md/05_image_prompts.md",
                "images/image_001.png", "md/07_package.md", "md/08_publish.md",
                "voiceover/voiceover.wav", "edit/timeline.fcpxml", "Final.mov"):
        _mk(d, rel)
    info = detect(d)
    assert info["finished"] is True
    assert info["next"] == []
    assert all(p["done"] for p in info["phases"])


def test_phases_condensed_eight(tmp_path):
    info = detect(_fresh_slug(tmp_path))
    assert [p["id"] for p in info["phases"]] == [
        "research", "skrypt", "docx", "grafiki", "package", "publish",
        "nagranie", "montaz"]
    assert info["phases"][0]["done"] is True   # research+weryfikacja
    assert info["phases"][1]["done"] is False


def test_slug_title_z_corrected(tmp_path):
    d = tmp_path / "9_t"
    _mk(d, "md/04_final.md", "# Tytul z final\n\ntekst.\n")
    assert slug_title(d) == "Tytul z final"
    _mk(d, "md/script_corrected.md", "Tytul po redakcji\n\ntekst.\n")
    assert slug_title(d) == "Tytul po redakcji"


def test_detect_pusty_katalog_nie_wybucha(tmp_path):
    info = detect(tmp_path / "pustka")
    assert info["next"][0]["stage"] == "research"
    assert info["finished"] is False
    assert all(not s["done"] for s in info["stages"])
