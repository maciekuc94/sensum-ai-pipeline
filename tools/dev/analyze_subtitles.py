"""Subtitle QA — rhythm + sync diagnostics for a slug's edit/alignment.json.

Reads the Align agent's debug payload and reports, without re-running Whisper:
  - alignment match stats;
  - the hook region (first N script words) with matched/interpolated flags, so an
    unspoken hook/title line (all-interpolated head) is obvious at a glance;
  - subtitle on-screen duration distribution (too short / ok / too long);
  - reading speed (CPS) outliers;
  - any cue that straddles a sentence boundary (a readability sin).

It validates only what is measurable from timestamps + text. Whether a cue lands
on the spoken word ("sync feel") is an ear check in preview.html / DaVinci.

Usage:
    PYTHONIOENCODING=utf-8 python tools/dev/analyze_subtitles.py "<slug>"
"""

import json
import re
import statistics
import sys
from pathlib import Path

# Thresholds mirror lib/subtitle_chunker.py (BBC / Netflix / Amara).
SHORT_S = 1.20        # below this a soft-break cue feels rushed
FLOOR_S = 0.85        # Netflix 5/6 s absolute floor — below this is a real flash
LONG_S = 5.00         # report cues this long (Netflix hard max is 7 s)
HIGH_CPS = 22.0       # above this is too fast to read comfortably


def main() -> None:
    slug = sys.argv[1] if len(sys.argv) > 1 else None
    if not slug:
        print("Usage: python tools/dev/analyze_subtitles.py \"<slug>\"")
        sys.exit(1)

    path = Path("outputs/videos_pl") / slug / "edit" / "alignment.json"
    if not path.exists():
        print(f"Error: {path} not found — run tools/pipeline/agent_align.py \"{slug}\" first.")
        sys.exit(1)

    data = json.loads(path.read_text(encoding="utf-8"))
    stats = data["stats"]
    words = data["aligned_words"]
    chunks = data["subtitle_chunks"]

    print(f"=== {slug} ===")
    print(f"audio_duration : {stats['audio_duration_s']:.2f}s")
    print(f"script_words   : {stats['script_words']}")
    print(f"matched        : {stats['matched']}  interpolated: {stats['interpolated']}  rate: {stats['match_rate'] * 100:.1f}%")
    print(f"chunks         : {len(chunks)}")
    print()

    print("--- HOOK REGION (first 25 script words) — all-interpolated head = unspoken line ---")
    for w in words[:25]:
        flag = "M" if w["matched"] else "i"
        print(f"  [{w['index']:>3}] {flag} {w['start']:>7.3f}-{w['end']:>7.3f}  {w['word']}")
    print()

    durs = [c["end"] - c["start"] for c in chunks]
    n_short = sum(1 for d in durs if d < SHORT_S)
    n_long = sum(1 for d in durs if d > LONG_S)
    n_floor = sum(1 for d in durs if d < FLOOR_S)
    print("--- CHUNK DURATION DISTRIBUTION ---")
    print(f"  min {min(durs):.2f}s  max {max(durs):.2f}s  median {statistics.median(durs):.2f}s  "
          f"mean {statistics.mean(durs):.2f}s  stdev {statistics.pstdev(durs):.2f}s")
    print(f"  below floor (<{FLOOR_S}s): {n_floor}   short (<{SHORT_S}s): {n_short}   "
          f"ok: {len(durs) - n_short - n_long}   long (>{LONG_S}s): {n_long}")
    print()

    gaps = [chunks[i + 1]["start"] - chunks[i]["end"] for i in range(len(chunks) - 1)]
    big = sorted((round(g, 2) for g in gaps if g > 0.05), reverse=True)
    print("--- GAPS between cues — screen clears during a pause (chain = no gap) ---")
    print(f"  chained (<=0.05s): {sum(1 for g in gaps if g <= 0.05)}/{len(gaps)}   "
          f"cleared (>0.05s): {len(big)}   gaps: {big}")
    print()

    print(f"--- SHORT (<{SHORT_S}s) — '*' marks below the {FLOOR_S}s floor (a real flash) ---")
    for c in chunks:
        d = c["end"] - c["start"]
        if d < SHORT_S:
            mark = "*" if d < FLOOR_S else " "
            print(f" {mark}#{c['index']:>3} {d:>5.2f}s  cps={len(c['text']) / max(d, 0.01):>5.1f}  \"{c['text']}\"")
    print()

    print(f"--- LONG (>{LONG_S}s) ---")
    for c in chunks:
        d = c["end"] - c["start"]
        if d > LONG_S:
            print(f"  #{c['index']:>3} {d:>5.2f}s  \"{c['text']}\"")
    print()

    print("--- SENTENCE-CROSSING (. ! ? not at the very end) — should be empty ---")
    crossing = 0
    for c in chunks:
        if re.search(r"[.!?][\"')\]]?\s+\S", c["text"]):
            crossing += 1
            print(f"  #{c['index']:>3}  \"{c['text']}\"")
    if crossing == 0:
        print("  (none)")
    print()

    print(f"--- HIGH CPS (>{HIGH_CPS}, too fast) — should be empty ---")
    high = 0
    for c in chunks:
        d = c["end"] - c["start"]
        cps = len(c["text"]) / max(d, 0.01)
        if cps > HIGH_CPS:
            high += 1
            print(f"  #{c['index']:>3} {d:>5.2f}s  cps={cps:>5.1f}  \"{c['text']}\"")
    if high == 0:
        print("  (none)")


if __name__ == "__main__":
    main()
