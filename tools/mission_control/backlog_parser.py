"""Mission Control — parser docs/research/topic_backlog_PL.md.

Dwa źródła: nagłówki `### N. „temat" — TIER (idx X, suma Y)` (rekomendowane,
z hookiem) i tabela `## Pełny ranking` (pełna lista). Status produkcji przez
fuzzy dopasowanie tematu do tytułów slugów — niepewne dopasowanie = brak
statusu (lepiej brak niż fałsz).
"""
import difflib
import re
import unicodedata

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
            # <11 kolumn pomija też 9-kolumnową podtabelę „Z flagą pułapki"
            # (tematy świadomie wyniesione poza ranking produkcyjny).
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
    s = s.lower().replace("ł", "l")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]", " ", s)


def _tokens(s: str) -> set:
    """Tokeny ≥4 znaków (odsiewa polskie słówka funkcyjne: się, nie, że, w)."""
    return {t for t in _norm(s).split() if len(t) >= 4}


def annotate_production(data: dict, slugs: list[dict]) -> None:
    """Dopisuje status 'nakręcony'/'w produkcji'/None do data['ranking'] in-place.

    Sygnał dopasowania = NAZWA FOLDERU sluga (powstaje z tematu przy starcie
    researchu), nie tytuł skryptu — tytuł to zdanie-hook/otwarcie, które nie
    dzieli słownictwa z tematem (a przed /draft to wręcz sama nazwa folderu).
    Metryka: pokrycie tokenów nazwy sluga przez temat. Greedy z dedupem: każdy
    slug i każdy temat wchodzą w co najwyżej jedną parę. Lepiej brak niż fałsz.
    """
    scored: list[tuple[float, dict, dict]] = []
    topic_tokens = [(_tokens(item["temat"]), item) for item in data["ranking"]]
    for s in slugs:
        stoks = _tokens(s.get("slug", ""))
        if not stoks:
            continue
        for ttoks, item in topic_tokens:
            shared = stoks & ttoks
            score = len(shared) / len(stoks)
            if score >= MATCH_THRESHOLD and len(shared) >= 2:
                scored.append((score, s, item))
    scored.sort(key=lambda p: p[0], reverse=True)
    used_slugs: set = set()
    used_topics: set = set()
    for _score, s, item in scored:
        if s["slug"] in used_slugs or id(item) in used_topics:
            continue
        used_slugs.add(s["slug"])
        used_topics.add(id(item))
        item["status"] = "nakręcony" if s["finished"] else "w produkcji"
