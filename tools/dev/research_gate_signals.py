# -*- coding: utf-8 -*-
"""
Gate-closing free-signal gatherer for SENSUM niche research (Wariant A) -- v3.
v3: Z3 kodowanie naprawione (oe=utf-8 + multi-charset), + KROK 3 non-fluke:
followers dla WSZYSTKICH kanalow z pasa EMO, breakout_ratio = max_views/followers,
data top-filmu dla kanalow przebijajacych sie (mlody/breakout = sygnatura PBS).
view_count z yt-dlp = realny licznik YouTube.
Wyjscie: docs/research/niche_gate_signals_PL.md + .tmp/niche_gate_raw.json
"""
import json, statistics, urllib.request, urllib.parse, datetime
import yt_dlp

ROOT = r"D:\ClaudeCode\YouTube psychology"
OUT_MD = ROOT + r"\docs\research\niche_gate_signals_PL.md"
OUT_JSON = ROOT + r"\.tmp\niche_gate_raw.json"

PAIN_SEEDS = [
    "dlaczego czuję pustkę w środku", "poczucie że jestem w tyle za innymi",
    "wstyd za swoje życie", "dlaczego nie potrafię się niczego trzymać",
    "czuję się gorszy od innych", "dlaczego czuję się samotny mimo ludzi",
    "dlaczego nic mnie nie cieszy", "jak przestać porównywać się z innymi",
    "czuję że marnuję swoje życie", "dlaczego ciągle się zamartwiam",
    "czuję się niewystarczający", "dlaczego boję się oceny innych",
    "poczucie braku sensu w życiu", "dlaczego odkładam wszystko na później",
    "czuję się jak oszust", "dlaczego nie umiem odpuścić",
]
AUTO_SEEDS = [
    "dlaczego czuję się", "czuję że", "dlaczego nie potrafię", "jak przestać",
    "wstydzę się", "czuję się jakby", "dlaczego ciągle", "boję się że",
    "mam wrażenie że", "dlaczego nic mnie", "dlaczego jestem", "czemu czuję",
    "dlaczego nie umiem", "boję się",
]

MUZ_KW = ["official video", "official music", "(official", "prod.", " ft.", " feat.",
          "lyric", "(audio", "teledysk", "vevo", "remix"]
MUZ_CH = ["label", "records", "vevo", " music"]
OPT_KW = ["produktyw", "nawyk", "dyscyplin", "motywacj", "sukces", "zarab", "pieniąd",
          "biznes", "protokół", "dopamin", "poranny", "rutyn", "jak osiągn", "milioner",
          "bogac", "kariera", "inwest", "3 techniki", "techniki na"]
EMO_KW = ["pustk", "samotn", "wstyd", "lęk", "smut", "czuj", "dlaczego", "strat",
          "żałob", "sens życia", "porówn", "gorsz", "niewystarcz", "oszust", "marnuj",
          "zamartw", "odrzuc", "wypal", "depresj", "anhedon", "nic ci się", "nic już",
          "beznadziej", "rozsta"]

def tag(title, channel):
    t = (title or "").lower(); c = (channel or "").lower()
    if any(k in t for k in MUZ_KW) or any(k in c for k in MUZ_CH):
        return "MUZ?"
    if any(k in t for k in OPT_KW):
        return "OPT?"
    if any(k in t for k in EMO_KW):
        return "EMO"
    return "?"

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
    return json.loads(b.decode("utf-8", errors="replace"))[1]

FLAT = {"quiet": True, "extract_flat": True, "skip_download": True,
        "no_warnings": True, "socket_timeout": 25}

def search(seed, n=25):
    with yt_dlp.YoutubeDL(FLAT) as y:
        info = y.extract_info(f"ytsearch{n}:{seed}", download=False)
    out = []
    for e in info.get("entries", []) or []:
        if not e:
            continue
        out.append({"id": e.get("id"), "title": e.get("title"),
                    "channel": e.get("channel") or e.get("uploader"),
                    "channel_url": e.get("channel_url") or e.get("uploader_url"),
                    "views": e.get("view_count"),
                    "url": e.get("url") or (f"https://youtube.com/watch?v={e.get('id')}" if e.get("id") else None)})
    return out

def channel_followers(url):
    if not url:
        return None
    if not url.rstrip("/").endswith("/videos"):
        url = url.rstrip("/") + "/videos"
    o = dict(FLAT); o["playlistend"] = 1
    with yt_dlp.YoutubeDL(o) as y:
        info = y.extract_info(url, download=False)
    return info.get("channel_follower_count")

def video_date(url):
    o = {"quiet": True, "skip_download": True, "no_warnings": True, "socket_timeout": 25}
    with yt_dlp.YoutubeDL(o) as y:
        info = y.extract_info(url, download=False)
    return info.get("upload_date")

def main():
    raw = {"generated": datetime.datetime.now().isoformat(timespec="minutes"), "z3": {}, "z2": [], "z1": {}}

    print("== Z3 ==", flush=True)
    for s in AUTO_SEEDS:
        try:
            raw["z3"][s] = autocomplete(s); print(f"  {s} -> {len(raw['z3'][s])}", flush=True)
        except Exception as ex:
            raw["z3"][s] = []; print(f"  {s} FAIL {ex}", flush=True)

    print("== Z2 ==", flush=True)
    byid = {}
    for s in PAIN_SEEDS:
        try:
            for v in search(s):
                if not v["id"]:
                    continue
                cur = byid.get(v["id"])
                if cur:
                    cur["seeds"].append(s)
                else:
                    v["seeds"] = [s]; byid[v["id"]] = v
            print(f"  {s}", flush=True)
        except Exception as ex:
            print(f"  {s} FAIL {ex}", flush=True)
    vids = list(byid.values())
    for v in vids:
        v["views"] = v["views"] or 0
        v["tag"] = tag(v["title"], v["channel"])
    vids.sort(key=lambda x: x["views"], reverse=True)
    raw["z2"] = vids

    print("== Z1 agg ==", flush=True)
    chan = {}
    for v in vids:
        c = v["channel"] or "?"
        d = chan.setdefault(c, {"channel": c, "url": v["channel_url"], "appearances": 0, "max": 0,
                                "views_list": [], "titles": [], "has_emo": False,
                                "top_views": 0, "top_url": None, "top_title": ""})
        d["appearances"] += 1
        d["max"] = max(d["max"], v["views"])
        d["views_list"].append(v["views"])
        if v["tag"] == "EMO":
            d["has_emo"] = True
        if v["views"] > d["top_views"]:
            d["top_views"] = v["views"]; d["top_url"] = v["url"]; d["top_title"] = v["title"]
        if len(d["titles"]) < 3:
            d["titles"].append(v["title"])
        if not d["url"] and v["channel_url"]:
            d["url"] = v["channel_url"]
    chans = list(chan.values())
    for d in chans:
        d["median_in_results"] = int(statistics.median(d["views_list"])) if d["views_list"] else 0
    chans.sort(key=lambda x: (x["has_emo"], x["max"], x["appearances"]), reverse=True)

    print("== Z1b: followers WSZYSTKIE kanaly EMO ==", flush=True)
    emo_chans = [d for d in chans if d["has_emo"]][:30]
    for d in emo_chans:
        try:
            f = channel_followers(d["url"]); d["followers"] = f
            d["breakout_ratio"] = round(d["max"] / f, 2) if f else None
            print(f"  {d['channel']} subs={f} ratio={d['breakout_ratio']}", flush=True)
        except Exception as ex:
            d["followers"] = None; d["breakout_ratio"] = None
            print(f"  {d['channel']} FAIL {ex}", flush=True)

    print("== Krok3: daty top-filmow dla breakout ==", flush=True)
    young = [d for d in emo_chans if (d.get("breakout_ratio") and d["breakout_ratio"] >= 2.0)
             or (d.get("followers") and d["followers"] < 60000 and d["max"] > 100000)]
    young = young[:12]
    for d in young:
        try:
            d["top_date"] = video_date(d["top_url"]); print(f"  {d['channel']} top_date={d['top_date']}", flush=True)
        except Exception as ex:
            d["top_date"] = None; print(f"  {d['channel']} FAIL {ex}", flush=True)
    raw["z1"] = chans

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=2)

    over100 = [v for v in vids if v["views"] > 100000]
    emo100 = [v for v in over100 if v["tag"] == "EMO"]
    emo100_ch = sorted(set(v["channel"] for v in emo100 if v["channel"]))
    sixfig = [d for d in emo_chans if (d.get("followers") or 0) >= 100000]
    breakout = sorted([d for d in young if d.get("breakout_ratio")], key=lambda x: x["breakout_ratio"], reverse=True)

    L = []
    L.append("# Arkusz domknięcia gate'u — sygnały niszy SENSUM (Wariant A) · v3")
    L.append("")
    L.append(f"> Wygenerowano: {raw['generated']} · yt-dlp (realny `view_count`) + Google autocomplete PL. Darmowe, bez płatnego YT API.")
    L.append(">")
    L.append("> Tagi: `EMO` pas SENSUM · `OPT?` optymalizacja · `MUZ?` muzyka · `?` sprawdź sam. `view_count` = realny licznik YouTube.")
    L.append("")
    L.append("## Auto-werdykt gate'u (PRZESŁANKI — potwierdź ręcznie obejrzeniem)")
    L.append("")
    L.append(f"- **Z1** kanały z pasa EMO i **≥100K subów**: **{len(sixfig)}** — *próg: ≥1 sześciocyfrowy*. → {'✅' if len(sixfig) >= 1 else '❌'}")
    L.append(f"- **Z2** filmy **EMO >100K** z różnych kanałów: **{len(emo100)}** z **{len(emo100_ch)}** kanałów — *próg: ≥3 różne*. → {'✅' if len(emo100_ch) >= 3 else '❌'}")
    L.append(f"- **Krok 3** kanały młode/przebijające się (breakout_ratio ≥2, czyli top-film >> subów): **{len(breakout)}** — *próg: ≥1 nie-fluke*. → {'✅' if len(breakout) >= 1 else '❌ (sprawdź ręcznie)'}")
    L.append("")
    L.append("> ⚠️ To PRZESŁANKI z automatu. Ostateczny gate: obejrzyj 2–3 filmy lidera (emce□) + młodego kanału, potwierdź ton/warsztat. 99K ≠ 100K.")
    L.append("")

    L.append("## Krok 3 — młode / przebijające się kanały (non-fluke: top-film >> subskrypcji)")
    L.append("")
    L.append("Wysoki `breakout_ratio` = pojedynczy film zrobił dużo więcej niż liczba subów → algorytm (browse/suggested) dowozi widza, także nowicjuszowi. To najsilniejszy dowód „nowy kanał da radę\".")
    L.append("")
    L.append("| Kanał | Subskrypcje | Top film (views) | breakout_ratio | Data top-filmu | Tytuł |")
    L.append("|---|---|---|---|---|---|")
    for d in breakout:
        subs = f"{d.get('followers'):,}" if d.get("followers") else "—"
        dt = d.get("top_date") or "—"
        if dt != "—" and len(dt) == 8:
            dt = f"{dt[:4]}-{dt[4:6]}-{dt[6:]}"
        L.append(f"| {(d['channel'] or '?').replace('|','/')} | {subs} | {d['top_views']:,} | {d['breakout_ratio']} | {dt} | {(d.get('top_title') or '').replace('|','/')[:48]} |")
    if not breakout:
        L.append("| — | — | — | — | — | brak wyraźnych breakoutów w tej próbce |")
    L.append("")

    L.append("## Z2 — filmy EMO >100K (pas SENSUM)")
    L.append("")
    L.append("| Views | Kanał | Tytuł | Link |")
    L.append("|---|---|---|---|")
    for v in emo100:
        L.append(f"| {v['views']:,} | {(v['channel'] or '?').replace('|','/')} | {(v['title'] or '').replace('|','/')} | {v['url']} |")
    L.append("")

    L.append("## Z1 — kanały-sąsiedzi z pasa EMO")
    L.append("")
    L.append("| Kanał | Subskrypcje | Max video | breakout_ratio | Przykładowy tytuł |")
    L.append("|---|---|---|---|---|")
    for d in emo_chans:
        subs = f"{d.get('followers'):,}" if d.get("followers") else "—"
        br = d.get("breakout_ratio") if d.get("breakout_ratio") else "—"
        ex_t = (d["titles"][0] if d["titles"] else "").replace("|", "/")[:46]
        L.append(f"| {(d['channel'] or '?').replace('|','/')} | {subs} | {d['max']:,} | {br} | {ex_t} |")
    L.append("")

    L.append("## Z3 — popyt werbalizowany po polsku (Google autocomplete)")
    L.append("")
    for s, sugg in raw["z3"].items():
        L.append(f"**„{s}…\"**")
        for x in (sugg or ["(brak)"]):
            L.append(f"- {x}")
        L.append("")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(L))

    print("DONE", flush=True)
    print(f"emo100={len(emo100)} emo_ch={len(emo100_ch)} sixfig={len(sixfig)} breakout={len(breakout)}", flush=True)

if __name__ == "__main__":
    main()
