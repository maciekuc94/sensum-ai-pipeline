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
