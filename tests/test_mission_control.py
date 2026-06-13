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


from tools.mission_control.backlog_parser import annotate_production, parse_backlog

BACKLOG_FIXTURE = """# Backlog tematów SENSUM — ranking niszy A∩B∩C

## Rekomendowane pierwsze 5 (produkcja teraz)

### 1. „Boję się, że stanę się swoją matką (albo swoim ojcem)" — ZŁOTO (idx 22, suma 12)
**Archetyp:** becoming-the-parent. **Architektura:** Composite Portrait.
**Zalążek hooka:** „Łapiesz się na zdaniu, które mówiła twoja matka."

### 2. „Nie umiesz płakać, choć bardzo byś chciał" — ZŁOTO (idx 24, suma 12)
**Archetyp:** frozen-feeling / numbness. **Architektura:** Forensic Case Study.
**Zalążek hooka:** „Są łzy, które nigdy nie spadły."

## Pełny ranking

| # | Temat (PL, język bólu) | Archetyp | A | B_pop | B_pod | C | Suma | ZŁOTO | Architektura | Werdykt |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Boję się, że stanę się swoją matką (albo swoim ojcem) | becoming-the-parent | 3 | 3 | 3 | 3 | 12 | ✅ | Composite Portrait | ZŁOTO — bogaty popyt |
| 2 | Nie umiesz płakać, choć bardzo byś chciał | frozen-feeling | 3 | 3 | 3 | 3 | 12 | ✅ | Forensic Case Study | ZŁOTO — evergreen |
| 3 | Czujesz, że marnujesz życie | drift | 3 | 2 | 2 | 3 | 10 | — | Socratic | SREBRO — luka jakościowa |
"""


def test_parse_backlog_top_i_ranking():
    data = parse_backlog(BACKLOG_FIXTURE)
    assert len(data["top"]) == 2
    t = data["top"][0]
    assert t["title"].startswith("Boję się")
    assert t["tier"] == "ZŁOTO" and t["idx"] == 22 and t["suma"] == 12
    assert "matka" in t["hook"] or "matki" in t["hook"]
    assert len(data["ranking"]) == 3
    r = data["ranking"][2]
    assert r["tier"] == "SREBRO" and r["temat"].startswith("Czujesz")
    assert r["architektura"] == "Socratic"


def test_annotate_production_fuzzy():
    data = parse_backlog(BACKLOG_FIXTURE)
    slugs = [
        {"slug": "4_stane_sie_swoim_rodzicem",
         "title": "Boję się, że stanę się swoją matką", "finished": False},
        {"slug": "5_nie_umiesz_plakac",
         "title": "Nie umiesz płakać, choć bardzo byś chciał", "finished": True},
    ]
    annotate_production(data, slugs)
    by_temat = {r["temat"]: r for r in data["ranking"]}
    assert by_temat["Boję się, że stanę się swoją matką (albo swoim ojcem)"]["status"] == "w produkcji"
    assert by_temat["Nie umiesz płakać, choć bardzo byś chciał"]["status"] == "nakręcony"
    assert by_temat["Czujesz, że marnujesz życie"]["status"] is None


def test_annotate_production_dopasowuje_po_nazwie_sluga():
    """Tytuł to hook (nie temat) — dopasowanie musi działać po NAZWIE folderu."""
    data = parse_backlog(BACKLOG_FIXTURE)
    slugs = [
        {"slug": "4_stane_sie_swoim_rodzicem",
         "title": "Powiedziałeś to, zanim zdążyłeś pomyśleć.", "finished": False},
        {"slug": "5_nie_umiesz_plakac",
         "title": "5_nie_umiesz_plakac", "finished": True},
    ]
    annotate_production(data, slugs)
    by_temat = {r["temat"]: r for r in data["ranking"]}
    assert by_temat["Boję się, że stanę się swoją matką (albo swoim ojcem)"]["status"] == "w produkcji"
    assert by_temat["Nie umiesz płakać, choć bardzo byś chciał"]["status"] == "nakręcony"
    assert by_temat["Czujesz, że marnujesz życie"]["status"] is None


def test_parse_backlog_pomija_wiersze_spoza_tieru():
    table = (
        "## Pełny ranking\n\n"
        "| # | Temat | Archetyp | A | B_pop | B_pod | C | Suma | ZŁOTO | Architektura | Werdykt |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| 1 | Realny temat | x | 3 | 3 | 3 | 3 | 12 | OK | Socratic | ZŁOTO — ok |\n"
        "| 2 | Odrzucony temat | x | 1 | 1 | 1 | 1 | 4 | — | — | BRĄZ — poza niszą |\n"
    )
    data = parse_backlog(table)
    temats = [r["temat"] for r in data["ranking"]]
    assert "Realny temat" in temats
    assert "Odrzucony temat" not in temats


import pytest
from fastapi.testclient import TestClient

import tools.mission_control.server as server


@pytest.fixture()
def client(tmp_path, monkeypatch):
    videos = tmp_path / "outputs" / "videos_pl"
    d = videos / "9_testowy"
    _mk(d, "md/01_research.md")
    _mk(d, "md/02_verified_research.md")
    _mk(d, "md/04_final.md", "# Tytul\n\nZdanie.\n")
    _mk(d, "tajny.txt", "sekret")
    monkeypatch.setattr(server, "VIDEOS", videos)
    return TestClient(server.app)


def test_api_state(client):
    data = client.get("/api/state").json()
    assert [s["slug"] for s in data["slugs"]] == ["9_testowy"]
    assert data["slugs"][0]["next"][0]["stage"] == "docx"


def test_api_files_i_raw(client):
    files = client.get("/api/slug/9_testowy/files").json()["files"]
    assert any(f["path"] == "md/04_final.md" for f in files)
    r = client.get("/api/slug/9_testowy/raw", params={"path": "md/04_final.md"})
    assert r.status_code == 200 and "Tytul" in r.text


def test_api_raw_traversal_403(client):
    r = client.get("/api/slug/9_testowy/raw", params={"path": "../../../.env"})
    assert r.status_code == 403


def test_api_raw_traversal_warianty(client):
    """Dodatkowe wektory traversal: ścieżka bezwzględna, backslash, URL-encoded.
    Żaden nie może zwrócić 200 ani treści spoza katalogu sluga (blokada = 403/404)."""
    for path in ("C:/Windows/win.ini", "..\\..\\..\\.env",
                 "%2e%2e/%2e%2e/.env", "/etc/passwd"):
        r = client.get("/api/slug/9_testowy/raw", params={"path": path})
        assert r.status_code in (403, 404), f"{path!r} -> {r.status_code}"


def test_api_unknown_slug_404(client):
    assert client.get("/api/slug/nie_ma/files").status_code == 404
