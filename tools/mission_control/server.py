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
