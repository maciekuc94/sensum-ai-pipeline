# -*- coding: utf-8 -*-
"""
Etap 2 v2: twarde sygnaly popytu/podazy PER KANDYDAT (odszumione).
Popyt: autocomplete PL na STEMACH (2-4 slowa) -- bo autocomplete dziala na prefiksach.
Podaz: yt-dlp ytsearch, ale agregaty liczone TYLKO po wynikach ON-TOPIC
(nakladanie slow znaczacych >=1) -> ucina viral (piosenki/klipy 100M+ lapiace 1 slowo).
yt_top = realne wyniki on-topic (tytul/kanal/views/lang) do oceny przez scoring.
Wejscie: docs/research/topic_candidates.json   Wyjscie: docs/research/topic_signals.json
"""
import json, re, urllib.request, urllib.parse
import yt_dlp

ROOT = r"D:\ClaudeCode\YouTube psychology"
CAND = ROOT + r"\docs\research\topic_candidates.json"
OUT = ROOT + r"\docs\research\topic_signals.json"

PL_CHARS = set("ąćęłńóśźż")
EN_WORDS = {"the", "you", "your", "why", "how", "of", "and", "is", "what", "when", "feel",
            "stop", "life", "love", "people", "that", "this", "with", "for", "are", "not",
            "can", "do", "me", "my", "we", "they", "from", "about", "your", "yourself"}
STOP = set("dlaczego czemu czuję czuje się sie jak mimo że ze nie mam jestem jesteś jestes swoje swój swoj swoja swoją ciągle ciagle tak już juz coś cos kiedy gdy żeby zeby aby na do za po co to ten ta te tym mnie cię cie był była być jest są sa oraz albo ale więc wiec bardzo który która które o w u z a i nawet choć choc kiedy nigdy zawsze siebie sobie sam sama samego".split())

def cwords(s):
    return {w for w in re.findall(r"[a-ząćęłńóśźż]+", (s or "").lower()) if len(w) >= 4 and w not in STOP}

def is_en(t):
    t = (t or "").lower()
    if any(c in t for c in PL_CHARS):
        return False
    w = set(re.findall(r"[a-z]+", t))
    return len(w & EN_WORDS) >= 2

def autocomplete(q):
    u = "http://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "hl": "pl", "gl": "PL", "ie": "utf-8", "oe": "utf-8", "q": q})
    req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        b = r.read()
    for enc in ("utf-8", "cp1250", "iso-8859-2"):
        try:
            return json.loads(b.decode(enc))[1]
        except Exception:
            continue
    return []

def stems(phrase):
    w = phrase.split()
    out = []
    for k in (2, 3, 4):
        if len(w) >= k:
            out.append(" ".join(w[:k]))
    return out or [phrase]

def demand(phrase):
    seen, sugg = set(), []
    for st in stems(phrase):
        try:
            for s in autocomplete(st):
                if s not in seen:
                    seen.add(s); sugg.append(s)
        except Exception:
            pass
    # ile podpowiedzi dzieli slowo znaczace z fraza (popyt zblizony do tematu)
    pc = cwords(phrase)
    rel = [s for s in sugg if cwords(s) & pc]
    return sugg, rel

FLAT = {"quiet": True, "extract_flat": True, "skip_download": True, "no_warnings": True, "socket_timeout": 25}

def search(q, n=20):
    with yt_dlp.YoutubeDL(FLAT) as y:
        info = y.extract_info(f"ytsearch{n}:{q}", download=False)
    out = []
    for e in info.get("entries", []) or []:
        if not e:
            continue
        out.append({"title": e.get("title"), "channel": e.get("channel") or e.get("uploader"),
                    "views": e.get("view_count") or 0,
                    "url": e.get("url") or (f"https://youtube.com/watch?v={e.get('id')}" if e.get("id") else None)})
    return out

def main():
    cands = json.load(open(CAND, encoding="utf-8"))["candidates"]
    res = []
    for i, c in enumerate(cands):
        phrase = c.get("search_phrase_pl") or c.get("topic_pl")
        pc = cwords(phrase)
        sugg, rel = demand(phrase)
        try:
            vids = search(phrase)
        except Exception:
            vids = []
        for v in vids:
            v["is_en"] = is_en(v["title"])
            v["on_topic"] = len(cwords(v["title"]) & pc) >= 1
        ont = [v for v in vids if v["on_topic"]]
        ont_pl = [v for v in ont if not v["is_en"]]
        ont.sort(key=lambda x: x["views"], reverse=True)
        sig = {
            "topic_pl": c.get("topic_pl"),
            "search_phrase_pl": phrase,
            "archetype": c.get("archetype"),
            "architecture": c.get("architecture"),
            "emotional_core": c.get("emotional_core"),
            "a_rationale": c.get("a_rationale"),
            # POPYT
            "demand_sugg_total": len(sugg),
            "demand_sugg_related": len(rel),
            "demand_samples": rel[:8] if rel else sugg[:6],
            # PODAZ (on-topic, odszumione)
            "supply_ontopic_n": len(ont),
            "supply_pl_max_views": max([v["views"] for v in ont_pl], default=0),
            "supply_pl_over100k": sum(1 for v in ont_pl if v["views"] > 100000),
            "supply_en_share": round(sum(1 for v in ont if v["is_en"]) / len(ont), 2) if ont else 0,
            "supply_raw_max_views_NOISY": max([v["views"] for v in vids], default=0),
            "yt_top_ontopic": [{"t": v["title"], "ch": v["channel"], "v": v["views"], "en": v["is_en"], "url": v["url"]} for v in ont[:10]],
        }
        res.append(sig)
        print(f"{i+1}/{len(cands)} {phrase[:40]} | dem={len(rel)}/{len(sugg)} sup_n={len(ont)} sup_pl>100k={sig['supply_pl_over100k']} sup_max={sig['supply_pl_max_views']} en={sig['supply_en_share']}", flush=True)
    json.dump({"signals": res}, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("DONE", len(res), flush=True)

if __name__ == "__main__":
    main()
