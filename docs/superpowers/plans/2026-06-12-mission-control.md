# SENSUM Mission Control — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lokalny, w 100% read-only webowy kokpit: karty slugów ze stepperem i „co dalej + kopiuj komendę", podstrona artefaktów (skrypt/obrazy/miniatury/pliki), zakładka backlogu tematów.

**Architecture:** FastAPI (`tools/mission_control/server.py`) czyta filesystem na żywo przy każdym request; czysta logika w `pipeline_state.py` i `backlog_parser.py` (testowalne bez serwera); frontend = jeden `index.html` + vanilla `app.js` + `style.css` (zero npm), markdown przez lokalny `vendor/marked.min.js`.

**Tech Stack:** Python 3, FastAPI + uvicorn (do zainstalowania), pytest + httpx (już są), vanilla JS, hash-routing.

**Spec:** `docs/superpowers/specs/2026-06-12-mission-control-design.md` — przeczytaj przed startem.

**Konwencje:** Bash z `PYTHONIOENCODING=utf-8`; commity z `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`; UI po polsku; paleta WYŁĄCZNIE `#F4E5CA` (tło) / `#582F0E` (tusz) + pochodne przezroczystości.

---

## Mapa plików

| Plik | Rola | Task |
|---|---|---|
| `requirements.txt` (modyfikacja) | + fastapi, uvicorn | 1 |
| `tools/mission_control/static/vendor/marked.min.js` | render markdownu (lokalnie) | 1 |
| `tests/test_mission_control.py` | testy logiki i API | 2–4 |
| `tools/mission_control/pipeline_state.py` | etapy + co-dalej + tytuł (czyste funkcje) | 2 |
| `tools/mission_control/backlog_parser.py` | parser rankingu + status produkcji | 3 |
| `tools/mission_control/server.py` | FastAPI: 4 endpointy + static + main | 4 |
| `tools/mission_control/static/index.html` | szkielet SPA | 5 |
| `tools/mission_control/static/style.css` | paleta SENSUM | 5 |
| `tools/mission_control/static/app.js` | router + widoki | 6–7 |
| `CLAUDE.md` (modyfikacja) | File Structure + Quick Command Reference | 8 |

---

### Task 1: zależności + szkielet + vendor

**Files:**
- Modify: `requirements.txt`
- Create: `tools/mission_control/static/vendor/marked.min.js`

- [ ] **Step 1: Instalacja i wpis do requirements**

Run: `pip install fastapi uvicorn`
Expected: `Successfully installed ...` (albo „already satisfied").

Read `requirements.txt`, dopisz na końcu (zachowaj istniejące wpisy):

```
fastapi
uvicorn
```

- [ ] **Step 2: Katalogi + vendor marked.js (przypięta wersja)**

```bash
mkdir -p tools/mission_control/static/vendor
curl -L -o tools/mission_control/static/vendor/marked.min.js https://cdn.jsdelivr.net/npm/marked@12.0.2/marked.min.js
```

Run: `wc -c tools/mission_control/static/vendor/marked.min.js`
Expected: > 30000 bajtów. Jeśli curl padł — fallback: `https://unpkg.com/marked@12.0.2/marked.min.js`.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt tools/mission_control/static/vendor/marked.min.js
git commit -m "feat(mc): zależności FastAPI + vendor marked.js (Mission Control, szkielet)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 2: `pipeline_state.py` — etapy, „co dalej", tytuł (TDD)

**Files:**
- Create: `tests/test_mission_control.py`
- Create: `tools/mission_control/pipeline_state.py`

- [ ] **Step 1: Failing testy**

Utwórz `tests/test_mission_control.py`:

```python
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
```

- [ ] **Step 2: Uruchom — FAIL na imporcie**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_mission_control.py -v`
Expected: ERROR — `ModuleNotFoundError: tools.mission_control.pipeline_state`

- [ ] **Step 3: Implementacja**

Utwórz `tools/mission_control/pipeline_state.py`:

```python
"""Mission Control — detekcja etapów pipeline per slug. Czyste funkcje, read-only.

Markery plikowe wg kanonu file_naming + CLAUDE.md (Agent Chain). Kolejność
STAGES = kolejność kanoniczna; jedyna równoległość v1: po docx-passie
/visuals i /package idą obok siebie.
"""
from pathlib import Path

STAGES = [
    ("research", "Research", lambda d: (d / "md" / "01_research.md").exists()),
    ("weryfikacja", "Weryfikacja", lambda d: (d / "md" / "02_verified_research.md").exists()),
    ("skrypt", "Skrypt (/draft)", lambda d: (d / "md" / "04_final.md").exists()),
    ("docx", "Docx pass", lambda d: (d / "docx" / "script_corrected.docx").exists()
        or (d / "md" / "script_corrected.md").exists()),
    ("visuals", "Prompty (/visuals)", lambda d: (d / "md" / "05_image_prompts.md").exists()),
    ("grafiki", "Grafiki (agent6)", lambda d: any((d / "images").glob("*.png"))
        if (d / "images").exists() else False),
    ("package", "Package", lambda d: (d / "md" / "07_package.md").exists()),
    ("publish", "Publish", lambda d: (d / "md" / "08_publish.md").exists()),
    ("nagranie", "Nagranie", lambda d: (d / "voiceover" / "voiceover.wav").exists()),
    ("align", "Align", lambda d: (d / "edit" / "timeline.fcpxml").exists()),
    ("montaz", "Montaż (.mov)", lambda d: any(d.glob("*.mov"))),
]

OPTIONAL_STAGES = [
    ("animacje", "Animacje (6c)", lambda d: (d / "md" / "06c_animation_plan.md").exists()),
]

# Skondensowane fazy stepperów na kartach (podstrona sluga pokazuje pełne STAGES).
PHASES = [
    ("research", "research", ("research", "weryfikacja")),
    ("skrypt", "skrypt", ("skrypt",)),
    ("docx", "docx", ("docx",)),
    ("grafiki", "grafiki", ("visuals", "grafiki")),
    ("package", "package", ("package",)),
    ("publish", "publish", ("publish",)),
    ("nagranie", "nagranie", ("nagranie",)),
    ("montaz", "montaż", ("align", "montaz")),
]

COMMANDS = {
    "weryfikacja": 'PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "{slug}"',
    "skrypt": "/draft {slug}",
    "visuals": "/visuals {slug}",
    "grafiki": 'PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "{slug}" --generate',
    "package": "/package {slug}",
    "publish": "/publish {slug}",
    "align": 'PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "{slug}"',
}

MANUAL_HINTS = {
    "research": "Start tematu: agent1_research.py \"<temat>\" (slug powstaje z tematu)",
    "docx": "Edytuj docx/script.docx (Word/Copilot) i zapisz jako docx/script_corrected.docx",
    "nagranie": "Nagraj voiceover (Studio One) i wyeksportuj do voiceover/voiceover.wav",
    "montaz": "DaVinci: import edit/timeline.fcpxml + subtitles.srt, montaż, render .mov",
}


def _action(stage_id: str, label: str, slug: str) -> dict:
    cmd = COMMANDS.get(stage_id)
    return {
        "stage": stage_id,
        "label": label,
        "command": cmd.format(slug=slug) if cmd else None,
        "manual_hint": MANUAL_HINTS.get(stage_id),
    }


def slug_title(slug_dir: Path) -> str:
    """Tytuł karty: 1. linia script_corrected.md > '# ...' z 04_final.md > slug."""
    corrected = slug_dir / "md" / "script_corrected.md"
    if corrected.exists():
        for line in corrected.read_text(encoding="utf-8").splitlines():
            if line.strip():
                return line.strip().lstrip("# ").strip()
    final = slug_dir / "md" / "04_final.md"
    if final.exists():
        for line in final.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("# "):
                return line.strip()[2:].strip()
    return slug_dir.name


def detect(slug_dir: Path) -> dict:
    """Pełny stan sluga dla /api/state."""
    slug = slug_dir.name
    done = {sid for sid, _label, check in STAGES if check(slug_dir)}
    stages = [{"id": sid, "label": label, "done": sid in done}
              for sid, label, _check in STAGES]
    optional = [{"id": sid, "label": label, "done": check(slug_dir)}
                for sid, label, check in OPTIONAL_STAGES]
    phases = [{"id": pid, "label": label, "done": all(s in done for s in deps)}
              for pid, label, deps in PHASES]

    finished = "montaz" in done
    next_actions: list[dict] = []
    if not finished:
        for sid, label, _check in STAGES:
            if sid not in done:
                next_actions.append(_action(sid, label, slug))
                # jedyna równoległość v1: po docx — /visuals i /package obok siebie
                if sid in ("visuals", "grafiki") and "package" not in done:
                    pkg_label = dict((s, l) for s, l, _c in STAGES)["package"]
                    next_actions.append(_action("package", pkg_label, slug))
                break

    return {
        "slug": slug,
        "title": slug_title(slug_dir),
        "stages": stages,
        "optional": optional,
        "phases": phases,
        "next": next_actions,
        "finished": finished,
    }
```

- [ ] **Step 4: Testy przechodzą**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_mission_control.py -v`
Expected: 6 passed

- [ ] **Step 5: Sanity na realnych slugach**

Run: `PYTHONIOENCODING=utf-8 python -c "from pathlib import Path; from tools.mission_control.pipeline_state import detect; [print(i['slug'], '->', [a['stage'] for a in i['next']], 'finished' if i['finished'] else '') for i in (detect(d) for d in sorted(Path('outputs/videos_pl').iterdir()) if d.is_dir())]"`
Expected: slugi 1–3 `finished`; slug 4 → `['nagranie']`; slug 5 → `['docx']`. Jeśli inaczej — sprawdź markery na dysku zanim „naprawisz" logikę (stan plików = źródło prawdy).

- [ ] **Step 6: Commit**

```bash
git add tests/test_mission_control.py tools/mission_control/pipeline_state.py
git commit -m "feat(mc): pipeline_state — detekcja etapów, fazy stepperów, co-dalej z równoległością po docx

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 3: `backlog_parser.py` (TDD)

**Files:**
- Modify: `tests/test_mission_control.py`
- Create: `tools/mission_control/backlog_parser.py`

- [ ] **Step 1: Failing testy (fixture odtwarza oba formaty realnego pliku)**

Dopisz do `tests/test_mission_control.py`:

```python
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
```

- [ ] **Step 2: Uruchom — FAIL na imporcie**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_mission_control.py -k backlog -v`
Expected: ERROR — `ModuleNotFoundError: tools.mission_control.backlog_parser`

- [ ] **Step 3: Implementacja**

Utwórz `tools/mission_control/backlog_parser.py`:

```python
"""Mission Control — parser docs/research/topic_backlog_PL.md.

Dwa źródła: nagłówki `### N. „temat" — TIER (idx X, suma Y)` (rekomendowane,
z hookiem) i tabela `## Pełny ranking` (pełna lista). Status produkcji przez
fuzzy dopasowanie tematu do tytułów slugów — niepewne dopasowanie = brak
statusu (lepiej brak niż fałsz).
"""
import difflib
import re

HEAD_RE = re.compile(
    r'^###\s+\d+\.\s*[„"](?P<title>.+?)["”]\s*—\s*(?P<tier>ZŁOTO|SREBRO)'
    r'\s*\(idx\s+(?P<idx>\d+),\s*suma\s+(?P<suma>\d+)\)')
HOOK_RE = re.compile(r"\*\*Zalążek hooka:\*\*\s*(?P<hook>.+)")
MATCH_THRESHOLD = 0.6


def parse_backlog(text: str) -> dict:
    top: list[dict] = []
    current: dict | None = None
    in_table = False
    ranking: list[dict] = []

    for line in text.splitlines():
        m = HEAD_RE.match(line.strip())
        if m:
            current = {"title": m["title"], "tier": m["tier"],
                       "idx": int(m["idx"]), "suma": int(m["suma"]), "hook": ""}
            top.append(current)
            continue
        if current is not None:
            h = HOOK_RE.search(line)
            if h:
                current["hook"] = h["hook"].strip().strip("„”\"")
        if line.strip().startswith("## "):
            in_table = line.strip() == "## Pełny ranking"
            current = None
            continue
        if in_table and line.strip().startswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) < 11 or cells[0] in ("#", "---") or set(cells[0]) <= {"-"}:
                continue
            werdykt = cells[10]
            tier = ("ZŁOTO" if werdykt.startswith("ZŁOTO")
                    else "SREBRO" if werdykt.startswith("SREBRO") else None)
            if tier is None:
                continue
            ranking.append({"pos": cells[0], "temat": cells[1], "archetyp": cells[2],
                            "suma": cells[7], "architektura": cells[9],
                            "werdykt": werdykt, "tier": tier, "status": None})
    return {"top": top, "ranking": ranking}


def _norm(s: str) -> str:
    return re.sub(r"[^a-ząćęłńóśźż0-9 ]", "", s.lower()).strip()


def annotate_production(data: dict, slugs: list[dict]) -> None:
    """Dopisuje status 'nakręcony'/'w produkcji'/None do data['ranking'] in-place."""
    for item in data["ranking"]:
        best, best_slug = 0.0, None
        for s in slugs:
            r = difflib.SequenceMatcher(None, _norm(item["temat"]),
                                        _norm(s.get("title", ""))).ratio()
            if r > best:
                best, best_slug = r, s
        if best >= MATCH_THRESHOLD and best_slug is not None:
            item["status"] = "nakręcony" if best_slug["finished"] else "w produkcji"
```

- [ ] **Step 4: Testy przechodzą + sanity na realnym pliku**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_mission_control.py -v`
Expected: 8 passed

Run: `PYTHONIOENCODING=utf-8 python -c "from pathlib import Path; from tools.mission_control.backlog_parser import parse_backlog; d = parse_backlog(Path('docs/research/topic_backlog_PL.md').read_text(encoding='utf-8')); print('top:', len(d['top']), '| ranking:', len(d['ranking']))"`
Expected: `top: 5 | ranking: >= 10`. Mniej = parser nie łapie realnego formatu — porównaj regex z realnymi liniami, popraw parser (nie plik backlogu!).

- [ ] **Step 5: Commit**

```bash
git add tests/test_mission_control.py tools/mission_control/backlog_parser.py
git commit -m "feat(mc): backlog_parser — nagłówki + tabela pełnego rankingu + fuzzy status produkcji

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 4: `server.py` — API + sanityzacja (TDD)

**Files:**
- Modify: `tests/test_mission_control.py`
- Create: `tools/mission_control/server.py`

- [ ] **Step 1: Failing testy API**

Dopisz do `tests/test_mission_control.py`:

```python
import pytest
from fastapi.testclient import TestClient

import tools.mission_control.server as server


@pytest.fixture()
def client(tmp_path, monkeypatch):
    videos = tmp_path / "outputs" / "videos_pl"
    d = videos / "9_testowy"
    _mk(d, "md/01_research.md")
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


def test_api_unknown_slug_404(client):
    assert client.get("/api/slug/nie_ma/files").status_code == 404
```

- [ ] **Step 2: Uruchom — FAIL na imporcie**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_mission_control.py -k api -v`
Expected: ERROR — brak `tools.mission_control.server`

- [ ] **Step 3: Implementacja serwera**

Utwórz `tools/mission_control/server.py`:

```python
"""SENSUM Mission Control — lokalny read-only kokpit (FastAPI).

Usage:
    PYTHONIOENCODING=utf-8 python tools/mission_control/server.py [--port 7777] [--no-browser]

Czyta filesystem na żywo przy każdym request. Niczego nie zapisuje i niczego
nie uruchamia (komendy tylko do skopiowania w UI).
"""
import argparse
import os
import sys
import threading
import webbrowser
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.mission_control.backlog_parser import annotate_production, parse_backlog
from tools.mission_control.pipeline_state import detect

BASE = Path(__file__).resolve().parents[2]
VIDEOS = BASE / "outputs" / "videos_pl"
BACKLOG = BASE / "docs" / "research" / "topic_backlog_PL.md"
STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="SENSUM Mission Control")


def _slug_root(slug: str) -> Path:
    root = (VIDEOS / slug).resolve()
    if not root.is_dir() or root.parent != VIDEOS.resolve():
        raise HTTPException(status_code=404, detail="nieznany slug")
    return root


@app.get("/api/state")
def api_state() -> dict:
    dirs = sorted(p for p in VIDEOS.iterdir() if p.is_dir()) if VIDEOS.exists() else []
    return {"slugs": [detect(d) for d in dirs]}


@app.get("/api/slug/{slug}/files")
def api_files(slug: str) -> dict:
    root = _slug_root(slug)
    files = [{"path": p.relative_to(root).as_posix(), "size": p.stat().st_size}
             for p in sorted(root.rglob("*")) if p.is_file()]
    return {"files": files}


@app.get("/api/slug/{slug}/raw")
def api_raw(slug: str, path: str):
    root = _slug_root(slug)
    target = (root / path).resolve()
    if not target.is_relative_to(root):
        raise HTTPException(status_code=403, detail="poza katalogiem sluga")
    if not target.is_file():
        raise HTTPException(status_code=404, detail="brak pliku")
    return FileResponse(target)


@app.get("/api/backlog")
def api_backlog() -> dict:
    if not BACKLOG.exists():
        return {"available": False, "top": [], "ranking": []}
    data = parse_backlog(BACKLOG.read_text(encoding="utf-8"))
    dirs = sorted(p for p in VIDEOS.iterdir() if p.is_dir()) if VIDEOS.exists() else []
    infos = [detect(d) for d in dirs]
    annotate_production(data, [{"slug": i["slug"], "title": i["title"],
                                "finished": i["finished"]} for i in infos])
    return {"available": True, **data}


app.mount("/", StaticFiles(directory=STATIC, html=True), name="static")


def main() -> None:
    import uvicorn

    parser = argparse.ArgumentParser(description="SENSUM Mission Control (read-only)")
    parser.add_argument("--port", type=int, default=7777)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    url = f"http://127.0.0.1:{args.port}"
    if not args.no_browser:
        threading.Timer(0.8, webbrowser.open, args=(url,)).start()
    print(f"Mission Control: {url}  (Ctrl+C aby zatrzymać)")
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")


if __name__ == "__main__":
    main()
```

Uwaga: `StaticFiles` wymaga istniejącego katalogu — `static/` istnieje od Task 1 (vendor). `html=True` poda `index.html` (powstanie w Task 5; do tego czasu `/` zwraca 404 — testy API tego nie dotykają).

- [ ] **Step 4: Testy przechodzą**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/test_mission_control.py -v`
Expected: 12 passed

- [ ] **Step 5: Commit**

```bash
git add tests/test_mission_control.py tools/mission_control/server.py
git commit -m "feat(mc): FastAPI — /api/state, files, raw (403 na traversal), backlog

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 5: `index.html` + `style.css`

**Files:**
- Create: `tools/mission_control/static/index.html`
- Create: `tools/mission_control/static/style.css`

- [ ] **Step 1: index.html**

```html
<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SENSUM · Mission Control</title>
<link rel="stylesheet" href="/style.css">
<script src="/vendor/marked.min.js" defer></script>
<script src="/app.js" defer></script>
</head>
<body>
<header>
  <div class="brand">SENSUM · MISSION CONTROL</div>
  <nav>
    <a href="#/" id="nav-pipeline">Pipeline</a>
    <a href="#/backlog" id="nav-backlog">Backlog</a>
  </nav>
</header>
<main id="app"><p class="muted">Ładowanie…</p></main>
<div id="lightbox" hidden>
  <img id="lightbox-img" alt="">
  <div id="lightbox-cap"></div>
</div>
</body>
</html>
```

- [ ] **Step 2: style.css**

```css
:root {
  --bg: #F4E5CA;
  --ink: #582F0E;
  --ink33: rgba(88, 47, 14, .33);
  --ink12: rgba(88, 47, 14, .12);
  --paper: #fffdf7;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--ink);
  font: 15px/1.5 Georgia, 'Times New Roman', serif;
}
header {
  display: flex; justify-content: space-between; align-items: baseline;
  padding: 14px 22px; border-bottom: 2px solid var(--ink);
}
.brand { font-weight: bold; letter-spacing: 3px; font-size: 13px; }
nav a {
  color: var(--ink); text-decoration: none; margin-left: 18px;
  padding-bottom: 3px; opacity: .55;
}
nav a.active { opacity: 1; border-bottom: 2px solid var(--ink); font-weight: bold; }
main { max-width: 980px; margin: 0 auto; padding: 22px; }
.muted { opacity: .55; }
h2 { font-size: 19px; margin: 4px 0 14px; }

/* karty pipeline */
.card {
  background: var(--paper); border: 1px solid var(--ink33); border-radius: 6px;
  padding: 13px 16px; margin-bottom: 11px; cursor: pointer;
}
.card:hover { border-color: var(--ink); }
.card .row { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.card .title { font-weight: bold; }
.card .slug-name { font-size: 12px; opacity: .55; font-family: ui-monospace, monospace; }
.chip {
  background: var(--ink); color: var(--bg); border-radius: 999px;
  padding: 2px 11px; font-size: 12.5px; white-space: nowrap;
}
.chip.manual { background: transparent; color: var(--ink); border: 1.5px dashed var(--ink); }
.copy-btn {
  border: 1px solid var(--ink); background: transparent; color: var(--ink);
  border-radius: 4px; font: 12px ui-monospace, monospace; padding: 2px 8px; cursor: pointer;
}
.copy-btn:active { background: var(--ink); color: var(--bg); }
.stepper { display: flex; align-items: center; gap: 3px; margin: 10px 0 2px; }
.dot { font-size: 13px; }
.dot.todo { opacity: .3; }
.bar { flex: 1; border-top: 1.6px solid var(--ink); }
.bar.todo { border-top-style: dotted; opacity: .45; }
.phase-labels { display: flex; justify-content: space-between; font-size: 10.5px; opacity: .6; }
details.finished { margin-top: 20px; }
details.finished summary { cursor: pointer; opacity: .65; }
details.finished .card { opacity: .75; }

/* podstrona sluga */
.back { display: inline-block; margin-bottom: 10px; color: var(--ink); }
.tabs { display: flex; gap: 16px; border-bottom: 1.5px solid var(--ink33); margin: 8px 0 16px; }
.tabs a { color: var(--ink); text-decoration: none; opacity: .5; padding-bottom: 5px; }
.tabs a.active { opacity: 1; font-weight: bold; border-bottom: 2.5px solid var(--ink); }
.prose { background: var(--paper); border: 1px solid var(--ink12); border-radius: 6px; padding: 18px 22px; }
.prose h1, .prose h2 { font-size: 1.15em; }
.version-switch { margin-bottom: 10px; font-size: 13px; }
.version-switch a { color: var(--ink); margin-right: 12px; }
.version-switch a.active { font-weight: bold; text-decoration: none; }
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 8px; }
.gallery figure { margin: 0; cursor: zoom-in; }
.gallery img { width: 100%; border: 1px solid var(--ink33); border-radius: 3px; display: block; }
.gallery figcaption { font-size: 11px; opacity: .6; text-align: center; }
.filelist { list-style: none; padding: 0; font-family: ui-monospace, monospace; font-size: 13px; }
.filelist li { padding: 3px 6px; border-bottom: 1px solid var(--ink12); display: flex; justify-content: space-between; gap: 8px; }
.filelist a { color: var(--ink); }
.filelist .size { opacity: .45; font-size: 11px; }

/* backlog */
.topic { background: var(--paper); border: 1px solid var(--ink33); border-radius: 6px; padding: 11px 14px; margin-bottom: 9px; }
.tier { font-size: 11px; letter-spacing: 1.5px; font-weight: bold; }
.status-chip { font-size: 11.5px; border: 1px solid var(--ink); border-radius: 999px; padding: 1px 9px; margin-left: 8px; }
table.ranking { width: 100%; border-collapse: collapse; background: var(--paper); font-size: 13.5px; }
table.ranking th, table.ranking td { border-bottom: 1px solid var(--ink12); padding: 6px 8px; text-align: left; }

/* lightbox */
#lightbox {
  position: fixed; inset: 0; background: rgba(88, 47, 14, .88);
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  cursor: zoom-out; z-index: 50;
}
#lightbox img { max-width: 92vw; max-height: 86vh; border: 3px solid var(--bg); }
#lightbox-cap { color: var(--bg); margin-top: 8px; font-size: 13px; }
```

- [ ] **Step 3: Weryfikacja ręczna szkieletu**

Run (tło lub osobny terminal): `PYTHONIOENCODING=utf-8 python tools/mission_control/server.py --no-browser`
Run: `curl -s http://127.0.0.1:7777/ | head -5` → ma zwrócić `<!DOCTYPE html>`; `curl -s http://127.0.0.1:7777/api/state | head -c 200` → JSON ze slugami. Zatrzymaj serwer.

- [ ] **Step 4: Commit**

```bash
git add tools/mission_control/static/index.html tools/mission_control/static/style.css
git commit -m "feat(mc): szkielet SPA + paleta SENSUM

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 6: `app.js` — router, tablica pipeline, clipboard

**Files:**
- Create: `tools/mission_control/static/app.js`

- [ ] **Step 1: Pełny plik (część 1 — board)**

```javascript
/* SENSUM Mission Control — vanilla JS, hash-routing. Read-only. */
'use strict';

const $app = document.getElementById('app');
let STATE = null;     // /api/state cache (odświeżany przy każdym wejściu na board)
let BACKLOG = null;   // /api/backlog cache (per sesja strony)

const esc = (s) => String(s).replace(/[&<>"]/g,
  (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

async function getJSON(url) {
  const r = await fetch(url);
  if (!r.ok) throw new Error(`${url} -> HTTP ${r.status}`);
  return r.json();
}

function copyCmd(btn, cmd) {
  navigator.clipboard.writeText(cmd).then(() => {
    const old = btn.textContent;
    btn.textContent = 'skopiowano ✓';
    setTimeout(() => { btn.textContent = old; }, 1200);
  });
}

/* ---------- widok: tablica pipeline ---------- */

function stepperHTML(phases) {
  const dots = phases.map((p) =>
    `<span class="dot ${p.done ? '' : 'todo'}">${p.done ? '●' : '○'}</span>`);
  const bars = phases.slice(1).map((p) =>
    `<span class="bar ${p.done ? '' : 'todo'}"></span>`);
  let row = '';
  dots.forEach((d, i) => { row += d; if (bars[i]) row += bars[i]; });
  const labels = phases.map((p) => `<span>${esc(p.label)}</span>`).join('');
  return `<div class="stepper">${row}</div><div class="phase-labels">${labels}</div>`;
}

function nextHTML(slug, next) {
  if (!next.length) return '<span class="chip">✦ ukończony</span>';
  return next.map((a) => {
    if (a.command) {
      return `<span class="chip">→ ${esc(a.label)}</span>
        <button class="copy-btn" data-cmd="${esc(a.command)}">kopiuj komendę</button>`;
    }
    return `<span class="chip manual" title="${esc(a.manual_hint || '')}">→ ${esc(a.label)} (ręczne)</span>`;
  }).join(' ');
}

function cardHTML(s) {
  return `<div class="card" data-slug="${esc(s.slug)}">
    <div class="row">
      <div><div class="title">${esc(s.title)}</div>
        <div class="slug-name">${esc(s.slug)}</div></div>
      <div>${nextHTML(s.slug, s.next)}</div>
    </div>
    ${stepperHTML(s.phases)}
  </div>`;
}

async function renderPipeline() {
  STATE = await getJSON('/api/state');
  const active = STATE.slugs.filter((s) => !s.finished);
  const done = STATE.slugs.filter((s) => s.finished);
  $app.innerHTML = `
    <h2>Pipeline (${active.length} w toku)</h2>
    ${active.map(cardHTML).join('') || '<p class="muted">Wszystko ukończone.</p>'}
    <details class="finished" ${done.length ? '' : 'hidden'}>
      <summary>Ukończone (${done.length})</summary>
      ${done.map(cardHTML).join('')}
    </details>`;
  $app.querySelectorAll('.card').forEach((el) => {
    el.addEventListener('click', (ev) => {
      if (ev.target.closest('.copy-btn')) return;
      location.hash = `#/slug/${el.dataset.slug}/skrypt`;
    });
  });
  $app.querySelectorAll('.copy-btn').forEach((b) =>
    b.addEventListener('click', () => copyCmd(b, b.dataset.cmd)));
}

/* ---------- router ---------- */

function setNav(tab) {
  document.getElementById('nav-pipeline').classList.toggle('active', tab === 'pipeline');
  document.getElementById('nav-backlog').classList.toggle('active', tab === 'backlog');
}

async function router() {
  const h = location.hash || '#/';
  try {
    if (h.startsWith('#/slug/')) {
      const [, , slug, tab] = h.split('/');
      setNav('pipeline');
      await renderSlug(decodeURIComponent(slug), tab || 'skrypt');
    } else if (h === '#/backlog') {
      setNav('backlog');
      await renderBacklog();
    } else {
      setNav('pipeline');
      await renderPipeline();
    }
  } catch (e) {
    $app.innerHTML = `<p class="muted">Błąd: ${esc(e.message)} — czy serwer działa?</p>`;
  }
}

window.addEventListener('hashchange', router);
router();
```

Funkcje `renderSlug` i `renderBacklog` powstają w Task 7 — na razie dopisz NA KOŃCU pliku tymczasowe zaślepki, żeby router działał (Task 7 je ZASTĘPUJE):

```javascript
async function renderSlug(slug) { $app.innerHTML = `<p class="muted">${esc(slug)} — widok w Task 7</p>`; }
async function renderBacklog() { $app.innerHTML = '<p class="muted">Backlog — widok w Task 7</p>'; }
```

- [ ] **Step 2: Weryfikacja ręczna**

Run: `PYTHONIOENCODING=utf-8 python tools/mission_control/server.py` (otworzy przeglądarkę).
Checklist: karty 4 i 5 widoczne z tytułami i stepperami; slugi 1–3 w zwiniętym „Ukończone (3)"; przycisk „kopiuj komendę" przy slugu 5 kopiuje (wklej gdziekolwiek — ma być komenda docx/`/visuals`...; dla sluga 5 czip „docx (ręczne)" z hintem w title); klik karty → zaślepka widoku sluga; nawigacja Backlog → zaślepka. Zatrzymaj serwer.

- [ ] **Step 3: Commit**

```bash
git add tools/mission_control/static/app.js
git commit -m "feat(mc): tablica pipeline — karty ze stepperem, co-dalej, clipboard, hash-router

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 7: `app.js` — podstrona sluga + backlog

**Files:**
- Modify: `tools/mission_control/static/app.js` (zastąp zaślepki z Task 6)

- [ ] **Step 1: Zastąp obie zaślepki pełnymi widokami**

Usuń dwie linie zaślepek `renderSlug`/`renderBacklog` i wklej:

```javascript
/* ---------- widok: podstrona sluga ---------- */

const TABS = [['skrypt', 'Skrypt'], ['obrazy', 'Obrazy'],
              ['miniatury', 'Miniatury'], ['pliki', 'Pliki']];
const SCRIPT_VERSIONS = [
  ['md/script_corrected.md', 'po redakcji'],
  ['md/04_final.md', '04_final'],
  ['md/04_final_machine.md', 'machine'],
];

const rawURL = (slug, path) =>
  `/api/slug/${encodeURIComponent(slug)}/raw?path=${encodeURIComponent(path)}`;

async function fetchText(slug, path) {
  const r = await fetch(rawURL(slug, path));
  if (!r.ok) throw new Error(`${path} -> HTTP ${r.status}`);
  return r.text();
}

function galleryHTML(slug, paths) {
  if (!paths.length) return '<p class="muted">Brak obrazów.</p>';
  return `<div class="gallery">${paths.map((p, i) => `
    <figure data-path="${esc(p)}" data-n="${i + 1}">
      <img loading="lazy" src="${rawURL(slug, p)}" alt="${esc(p)}">
      <figcaption>#${i + 1} · ${esc(p.split('/').pop())}</figcaption>
    </figure>`).join('')}</div>`;
}

async function renderSlug(slug, tab) {
  if (!STATE) STATE = await getJSON('/api/state');
  const info = STATE.slugs.find((s) => s.slug === slug);
  const files = (await getJSON(`/api/slug/${encodeURIComponent(slug)}/files`)).files;
  const have = new Set(files.map((f) => f.path));

  const tabsHTML = TABS.map(([id, label]) =>
    `<a href="#/slug/${encodeURIComponent(slug)}/${id}"
        class="${id === tab ? 'active' : ''}">${label}</a>`).join('');
  let body = '';

  if (tab === 'skrypt') {
    const versions = SCRIPT_VERSIONS.filter(([p]) => have.has(p));
    if (!versions.length) {
      body = '<p class="muted">Brak skryptu (przed /draft).</p>';
    } else {
      const current = versions[0][0];
      const sw = versions.map(([p, label]) =>
        `<a href="#" data-ver="${esc(p)}" class="${p === current ? 'active' : ''}">${label}</a>`).join('');
      body = `<div class="version-switch">${sw}</div><div class="prose" id="prose"></div>`;
      queueMicrotask(async () => {
        const load = async (p) => {
          document.getElementById('prose').innerHTML =
            marked.parse(await fetchText(slug, p));
        };
        await load(current);
        $app.querySelectorAll('.version-switch a').forEach((a) =>
          a.addEventListener('click', async (ev) => {
            ev.preventDefault();
            $app.querySelectorAll('.version-switch a').forEach((x) => x.classList.remove('active'));
            a.classList.add('active');
            await load(a.dataset.ver);
          }));
      });
    }
  } else if (tab === 'obrazy') {
    const post = files.filter((f) => f.path.startsWith('images_post/') && f.path.endsWith('.png'));
    const base = files.filter((f) => f.path.startsWith('images/') && f.path.endsWith('.png'));
    body = galleryHTML(slug, (post.length ? post : base).map((f) => f.path));
  } else if (tab === 'miniatury') {
    const groups = ['thumbnails_no_grain/', 'thumbnails_grain/', 'thumbnails/'];
    body = groups.map((g) => {
      const paths = files.filter((f) => f.path.startsWith(g) && f.path.endsWith('.png'))
        .map((f) => f.path);
      return paths.length ? `<h2>${esc(g)}</h2>${galleryHTML(slug, paths)}` : '';
    }).join('') || '<p class="muted">Brak miniatur (przed /package).</p>';
  } else {
    body = `<ul class="filelist">${files.map((f) => `
      <li><a href="#" data-path="${esc(f.path)}">${esc(f.path)}</a>
          <span class="size">${(f.size / 1024).toFixed(0)} KB</span></li>`).join('')}</ul>
      <div class="prose" id="prose" hidden></div>`;
  }

  $app.innerHTML = `
    <a class="back" href="#/">← Pipeline</a>
    <h2>${esc(info ? info.title : slug)} <span class="slug-name">${esc(slug)}</span></h2>
    <div class="tabs">${tabsHTML}</div>${body}`;

  $app.querySelectorAll('.gallery figure').forEach((fig) =>
    fig.addEventListener('click', () => showLightbox(
      rawURL(slug, fig.dataset.path), `#${fig.dataset.n} · ${fig.dataset.path}`)));

  $app.querySelectorAll('.filelist a').forEach((a) =>
    a.addEventListener('click', async (ev) => {
      ev.preventDefault();
      const p = a.dataset.path;
      const prose = document.getElementById('prose');
      if (/\.(png|jpg|jpeg|gif)$/i.test(p)) {
        showLightbox(rawURL(slug, p), p);
      } else if (/\.(md|txt|srt|json|html|fcpxml)$/i.test(p)) {
        prose.hidden = false;
        const text = await fetchText(slug, p);
        prose.innerHTML = p.endsWith('.md')
          ? marked.parse(text)
          : `<pre>${esc(text.slice(0, 20000))}</pre>`;
        prose.scrollIntoView({behavior: 'smooth'});
      } else {
        prompt('Ścieżka pliku (Ctrl+C):', `outputs/videos_pl/${slug}/${p}`);
      }
    }));
}

/* ---------- lightbox ---------- */

const $lb = document.getElementById('lightbox');
function showLightbox(src, caption) {
  document.getElementById('lightbox-img').src = src;
  document.getElementById('lightbox-cap').textContent = caption;
  $lb.hidden = false;
}
$lb.addEventListener('click', () => { $lb.hidden = true; });

/* ---------- widok: backlog ---------- */

async function renderBacklog() {
  if (!BACKLOG) BACKLOG = await getJSON('/api/backlog');
  if (!BACKLOG.available) {
    $app.innerHTML = '<p class="muted">Brak docs/research/topic_backlog_PL.md.</p>';
    return;
  }
  const startCmd = (temat) =>
    `PYTHONIOENCODING=utf-8 python tools/pipeline/agent1_research.py "${temat}"`;
  const statusChip = (s) => s ? `<span class="status-chip">${esc(s)}</span>` : '';

  const top = BACKLOG.top.map((t) => `
    <div class="topic">
      <span class="tier">${esc(t.tier)}</span> · idx ${t.idx} · suma ${t.suma}
      <div class="title">${esc(t.title)}</div>
      ${t.hook ? `<details><summary class="muted">zalążek hooka</summary>
        <p>„${esc(t.hook)}"</p></details>` : ''}
      <button class="copy-btn" data-cmd="${esc(startCmd(t.title))}">kopiuj start (agent1)</button>
    </div>`).join('');

  const rows = BACKLOG.ranking.map((r) => `
    <tr><td>${esc(r.pos)}</td>
      <td>${esc(r.temat)} ${statusChip(r.status)}</td>
      <td>${esc(r.tier)}</td><td>${esc(r.architektura)}</td>
      <td>${r.status ? '' :
        `<button class="copy-btn" data-cmd="${esc(startCmd(r.temat))}">start</button>`}</td>
    </tr>`).join('');

  $app.innerHTML = `
    <h2>Backlog — rekomendowane</h2>${top}
    <h2>Pełny ranking</h2>
    <table class="ranking">
      <tr><th>#</th><th>Temat</th><th>Tier</th><th>Architektura</th><th></th></tr>
      ${rows}
    </table>`;
  $app.querySelectorAll('.copy-btn').forEach((b) =>
    b.addEventListener('click', () => copyCmd(b, b.dataset.cmd)));
}
```

- [ ] **Step 2: Weryfikacja ręczna pełnej apki**

Run: `PYTHONIOENCODING=utf-8 python tools/mission_control/server.py`
Checklist:
1. Karta sluga 3 → Skrypt: render „po redakcji", przełącznik wersji działa (3 wersje? slug 3 ma corrected + 04_final).
2. Obrazy: galeria z `images_post/`, lazy-load, lightbox z numerem #N.
3. Miniatury: sekcje no_grain/grain.
4. Pliki: klik `md/08_publish.md` → render pod listą; klik `.png` → lightbox; klik `.wav` → prompt ze ścieżką.
5. Backlog: top 5 z hookami, tabela rankingu, status „w produkcji"/„nakręcony" przy tematach slugów 4/5, „start" kopiuje komendę agent1.
6. F5 na `#/slug/...` wraca w to samo miejsce (hash-routing).
Zatrzymaj serwer.

- [ ] **Step 3: Commit**

```bash
git add tools/mission_control/static/app.js
git commit -m "feat(mc): podstrona sluga (skrypt/obrazy/miniatury/pliki) + widok backlogu

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

### Task 8: smoke E2E + CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Pełny test suite**

Run: `PYTHONIOENCODING=utf-8 python -m pytest tests/ -v`
Expected: wszystkie testy projektu zielone (12 z MC + 9 z Redaktora, jeśli plan 1 już wykonany).

- [ ] **Step 2: CLAUDE.md**

(a) W File Structure, pod linią `  dev/ ...`, dodaj:

```
  mission_control/       # Read-only web kokpit (FastAPI + vanilla JS): stan slugów, artefakty, backlog — python tools/mission_control/server.py
```

(b) W Quick Command Reference dodaj:

```
PYTHONIOENCODING=utf-8 python tools/mission_control/server.py   # Mission Control — kokpit na localhost:7777 (read-only; nic nie odpala, komendy do kopiowania)
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: CLAUDE.md — Mission Control (kokpit read-only) w strukturze i Quick Reference

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>"
```

---

## Self-review (wykonany przy pisaniu planu)

- **Pokrycie specu:** decyzje 1–5 ✓ (read-only+copy: Task 6; moduły: Task 6/7; FastAPI: Task 4; karty+stepper: Task 6; zakładki+podstrona: Task 7), API 4 endpointy ✓ (Task 4), detekcja etapów wg tabeli specu ✓ (Task 2), backlog+fuzzy „lepiej brak niż fałsz" ✓ (Task 3), odporność ✓ (403 test, brak backlogu → `available:false`, surowy tekst dla nie-md w zakładce Pliki), testy ✓ (Task 2–4), poza zakresem ✓ (zero zapisu, zero subprocess).
- **Placeholdery:** brak — pełny kod każdego pliku; jeden celowo oznaczony artefakt `'t` z instrukcją usunięcia.
- **Spójność typów:** `detect()` zwraca klucze używane przez `app.js` (`slug/title/stages/phases/next/finished`; `next[].command|manual_hint`) ✓; `parse_backlog` zwraca `top[].title/tier/idx/suma/hook` i `ranking[].pos/temat/tier/architektura/status` — zgodne z `renderBacklog` ✓; `server.VIDEOS` monkeypatchowalne (funkcje czytają moduł-level zmienną w call-time) ✓.
