"""Audyt integralności odwołań doktryny (Layer 3, dev).

Deterministyczny szkielet audytu spójności: skanuje pliki-źródła doktryny
(CLAUDE.md, .claude/commands|skills|agents, workflows/) w poszukiwaniu odwołań
do plików/ścieżek i klasyfikuje je RESOLVEREM świadomym konwencji projektu:

- slug-relative szablony (md/…, docx/…, edit/… → outputs/videos_pl/{slug}/…),
- basename pod tools/ workflows/ .claude/ docs/ brainstorms/,
- zewnętrzna auto-pamięć (project_*.md / feedback_*.md) i lokalne configi,
- pliki robocze .tmp/ (ephemeral),
- placeholdery/przykłady.

Zostają tylko PRAWDZIWE martwe odwołania + realne sieroty. Detekcja sierot jest
name-aware ORAZ skanuje treść .py (żeby szablony promptów ładowane przez kod i
lib-moduły importowane przez agentów nie wyglądały na martwe — lekcja z audytu
2026-06-15).

To NIE jest audyt semantyczny (sprzeczności treści CLAUDE.md vs realne pliki) —
ten robi wachlarz agentów (`/workflows` audyt-spojnosci-claude). To deterministyczny
backbone: tani, wyczerpujący, zero LLM.

Uruchom:
    PYTHONIOENCODING=utf-8 python tools/dev/audit_consistency.py
    PYTHONIOENCODING=utf-8 python tools/dev/audit_consistency.py --json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SOURCE_GLOBS = ["CLAUDE.md", ".claude/commands", ".claude/skills",
                ".claude/agents", "workflows"]
SKIP_DIRS = {".git", ".tmp", "outputs", "__pycache__", "node_modules",
             ".venv", "venv", "materials"}
REAL_EXTS = {".py", ".md", ".json"}
BASENAME_ROOTS = ("tools/", "workflows/", ".claude/", "docs/", "brainstorms/")

PATH_RE = re.compile(
    r"(?<![\w/])"
    r"((?:\.claude/|tools/|workflows/|docs/|brainstorms/)[\w./-]*"
    r"|[\w./-]+\.(?:py|md|json|txt|wav|srt|fcpxml|png|docx|pdf|bat|html))"
)

MEMORY_RE = re.compile(r"^(project_|feedback_)[\w-]+\.md$")
CONFIG_LOCAL = {"settings.local.json", ".env", ".mcp.json"}
PLACEHOLDER_TOKENS = ("0N", "NN", "RRRR", "..", "path/to", "/plik", "plik.md",
                      "plik2.md", "image_00", "strip.png", "/The", "/Your",
                      "01..03", "_2col", "_final.png", "_grain.png", "_pdf_overview",
                      ".bak.md", "redaktor_kat_N", "raport_", "thumbnail.png",
                      "thumbnail_0", "agentN_", "agent3", "Book.pdf", "Factor.pdf",
                      "Score.pdf", "Slow.pdf")
SLUG_HINT = re.compile(r"(^0\d|^03[a-c]|^04_|^05_|^06|^07_|^08|script|"
                       r"subtitles|timeline|preview|alignment|voiceover|"
                       r"ambient|whisper|arc\.md|fixer_skips|iter/)")


def walk_files(rel_root):
    abs_root = os.path.join(ROOT, rel_root)
    if os.path.isfile(abs_root):
        yield rel_root
        return
    for dp, dns, fns in os.walk(abs_root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            yield os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/")


def all_real_files():
    out = set()
    for dp, dns, fns in os.walk(ROOT):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            out.add(os.path.relpath(os.path.join(dp, fn), ROOT).replace("\\", "/"))
    return out


def slug_artifact_exists(ref):
    base = ref.split("/")[-1]
    for depth in ("", "*/", "*/*/"):
        if glob.glob(os.path.join(ROOT, "outputs", "videos_pl", "*", depth,
                                  base.replace("/", os.sep))):
            return True
    return False


def classify(ref, bidx):
    ref = ref.rstrip("/")
    base = os.path.basename(ref)
    if os.path.exists(os.path.join(ROOT, ref)):
        return "ok", "exact"
    if MEMORY_RE.match(base):
        return "external", "auto-pamięć (poza repo)"
    if base in CONFIG_LOCAL:
        return "external", "lokalny/gitignored config"
    if any(t in ref for t in PLACEHOLDER_TOKENS):
        return "ok", "placeholder/przykład"
    if base in bidx:
        hits = [h for h in bidx[base] if h.startswith(BASENAME_ROOTS)]
        if hits:
            return "ok", f"basename→{hits[0]}"
    if ".tmp/" in ref:
        return "ephemeral", "plik roboczy .tmp/ (tworzony w trakcie)"
    if slug_artifact_exists(ref):
        return "ok", "slug-artefakt (istnieje pod ≥1 slug)"
    if SLUG_HINT.search(ref) or ref.startswith(("md/", "docx/", "edit/", "iter/")):
        return "slug_pending", "slug-artefakt bez instancji (norma, jeśli etap nieosiągnięty)"
    return "dead", "brak"


def scan():
    source_files = sorted({f for g in SOURCE_GLOBS for f in walk_files(g)
                           if f.endswith((".md", ".json"))})
    real = all_real_files()
    bidx = {}
    for r in real:
        bidx.setdefault(os.path.basename(r), []).append(r)

    docblob_parts = []
    buckets = {"dead": {}, "ephemeral": {}, "slug_pending": {}, "external": {}}
    for sf in source_files:
        try:
            text = open(os.path.join(ROOT, sf), encoding="utf-8").read()
        except Exception:
            continue
        docblob_parts.append(text)
        for m in PATH_RE.finditer(text):
            ref = m.group(1).strip().rstrip(".,);:`\"'").replace("\\", "/")
            if not ref:
                continue
            status, detail = classify(ref, bidx)
            if status in buckets:
                buckets[status].setdefault(ref, (set(), detail))[0].add(sf)

    # Blob referencyjny do detekcji sierot: dokumenty + treść .py (kod też
    # "wspomina" pliki, np. szablony promptów i importy lib).
    refblob = "\n".join(docblob_parts)
    for rel in real:
        if rel.endswith(".py"):
            try:
                refblob += "\n" + open(os.path.join(ROOT, rel), encoding="utf-8").read()
            except Exception:
                pass

    orphans = []
    for rel in sorted(real):
        if not rel.startswith(("tools/", "workflows/", ".claude/")):
            continue
        if os.path.splitext(rel)[1] not in REAL_EXTS:
            continue
        base = os.path.basename(rel)
        if base == "__init__.py":
            continue
        stem = os.path.splitext(base)[0]
        logical = os.path.basename(os.path.dirname(rel)) if base == "SKILL.md" else stem
        if rel in refblob or base in refblob or stem in refblob or logical in refblob:
            continue
        orphans.append(rel)

    def as_list(d):
        return [{"ref": k, "detail": v[1], "from": sorted(v[0])} for k, v in sorted(d.items())]

    return {
        "sources_scanned": len(source_files),
        "real_files": len(real),
        "dead_refs": as_list(buckets["dead"]),
        "ephemeral": as_list(buckets["ephemeral"]),
        "external": [{"ref": k, "detail": v[1]} for k, v in sorted(buckets["external"].items())],
        "slug_pending": sorted(buckets["slug_pending"].keys()),
        "orphans": orphans,
    }


def main():
    ap = argparse.ArgumentParser(description="Audyt integralności odwołań doktryny")
    ap.add_argument("--json", action="store_true", help="wynik jako JSON")
    args = ap.parse_args()

    r = scan()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return

    print("=" * 70)
    print(f"ŹRÓDŁA: {r['sources_scanned']} | realnych plików: {r['real_files']}")
    print("=" * 70)

    print(f"\n### MARTWE ODWOŁANIA (prawdziwe)  [{len(r['dead_refs'])}]\n")
    for it in r["dead_refs"] or [{"ref": "(brak)", "from": []}]:
        print(f"  ✗ {it['ref']}")
        if it.get("from"):
            print(f"      ← {', '.join(it['from'])}")

    print(f"\n### SIEROTY (realny plik kodu/SOP, 0 wzmianek — także w .py)  [{len(r['orphans'])}]\n")
    for o in r["orphans"] or ["(brak)"]:
        print(f"  ? {o}")

    print(f"\n### PLIKI ROBOCZE .tmp/ (ephemeral)  [{len(r['ephemeral'])}]")
    print(f"### AUTO-PAMIĘĆ / CONFIGI poza repo (info)  [{len(r['external'])}]")
    print(f"### slug-artefakty bez instancji (norma)  [{len(r['slug_pending'])}]")
    print("\nSemantyka (sprzeczności treści) — uruchom wachlarz: /workflows audyt-spojnosci-claude")


if __name__ == "__main__":
    main()
