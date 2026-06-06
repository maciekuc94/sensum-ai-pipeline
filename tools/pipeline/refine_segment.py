"""refine_segment.py — deterministyczna segmentacja skryptu na zdania
(ID + sąsiedzi) + wykrywanie chronionych szczytów. Stdlib only.

Użycie:
  python tools/pipeline/refine_segment.py <slug>            # → .tmp/refine_<slug>_segments.json
  python tools/pipeline/refine_segment.py x --selftest      # testy
"""
import re, json, argparse, os, sys

_ABBREV = {"np", "itd", "itp", "tj", "tzn", "tzw", "ok", "por", "wg", "nr", "godz", "min"}


def split_into_paragraphs(text):
    paras = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        if re.fullmatch(r"[-*_=]{3,}", block):      # dywizor markdown (---, ***, ___)
            continue
        if block.startswith("ARCHITECTURE:"):        # maszynowa metadana (zdejmowana w 04_final)
            continue
        paras.append(re.sub(r"\s*\n\s*", " ", block))
    return paras


def split_sentences(paragraph):
    out, buf, depth, i, n = [], "", 0, 0, len(paragraph)
    while i < n:
        ch = paragraph[i]
        buf += ch
        if ch == "„":
            depth += 1
        elif ch == "”":
            depth = max(0, depth - 1)
        elif ch in ".!?…" and depth == 0:
            j = i + 1
            while j < n and paragraph[j].isspace():
                j += 1
            nxt = paragraph[j] if j < n else ""
            last = re.split(r"[\s(„]", buf[:-1])[-1].strip(".").lower()
            is_abbrev = ch == "." and last in _ABBREV
            ends = (nxt == "" or nxt.isupper() or nxt == "„")
            if ends and not is_abbrev:
                out.append(buf.strip()); buf = ""
        i += 1
    if buf.strip():
        out.append(buf.strip())
    return out


def segment_script(text):
    paras = split_into_paragraphs(text)
    sents = []
    for p_idx, para in enumerate(paras):
        for s in split_sentences(para):
            sents.append({"para": p_idx, "text": s})
    for k, s in enumerate(sents):
        s["id"] = f"s{k+1:03d}"
        s["prev"] = sents[k - 1]["text"] if k > 0 else ""
        s["next"] = sents[k + 1]["text"] if k + 1 < len(sents) else ""
    _mark_peaks(sents, len(paras))
    return sents


def _mark_peaks(sents, n_paras):
    last = n_paras - 1
    for s in sents:
        s["is_peak"] = bool(s["para"] == 0 or s["para"] == last)


def _selftest():
    s = split_sentences('Mówisz “znowu mi nie wyszło”. Idziesz dalej.')
    assert s == ['Mówisz “znowu mi nie wyszło”.', 'Idziesz dalej.'], s
    s = split_sentences('To był jeden dzień — nie wyrok na to, kim jesteś.')
    assert s == ['To był jeden dzień — nie wyrok na to, kim jesteś.'], s
    s = split_sentences('Pierwsze pytanie. Drugie pytanie. Trzecie.')
    assert len(s) == 3, s
    text = "## Tytuł\n\nPierwsze zdanie sceny. Drugie zdanie.\n\nDrugi akapit z myślą.\n\nNie końcem."
    sents = segment_script(text)
    assert [x["id"] for x in sents] == ["s001", "s002", "s003", "s004"], sents
    assert sents[0]["prev"] == "" and sents[0]["next"] == "Drugie zdanie."
    assert sents[1]["prev"] == "Pierwsze zdanie sceny."
    assert sents[0]["is_peak"] is True
    assert sents[3]["is_peak"] is True
    assert sents[2]["is_peak"] is False
    # — pomija nagłówek/dywizor/metadane (realny format 04_working.md) —
    wf = "# Script Draft\nGenerated: x\n\n---\n\nARCHITECTURE: Forensic Case Study\n\n## Tytuł\n\nPrawdziwy cold open. Druga linia.\n\nZamknięcie."
    ws = segment_script(wf)
    assert ws[0]["text"] == "Prawdziwy cold open.", ws[0]
    assert ws[0]["is_peak"] is True, ws
    assert all("ARCHITECTURE" not in x["text"] and x["text"] != "---" for x in ws), ws
    print("OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--infile", default=None)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest(); return
    base = os.path.join("outputs", "videos_pl", args.slug, "md")
    infile = args.infile or os.path.join(base, "04_working.md")
    if not os.path.exists(infile):
        print(f"BŁĄD: brak {infile}", file=sys.stderr); sys.exit(1)
    with open(infile, encoding="utf-8") as f:
        sents = segment_script(f.read())
    os.makedirs(".tmp", exist_ok=True)
    out = os.path.join(".tmp", f"refine_{args.slug}_segments.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(sents, f, ensure_ascii=False, indent=2)
    n_peak = sum(1 for s in sents if s["is_peak"])
    print(f"{len(sents)} zdań, {n_peak} chronionych szczytów → {out}")


if __name__ == "__main__":
    main()
