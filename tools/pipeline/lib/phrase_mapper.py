"""Map each phrase in 05_image_phrases.md to start/end timestamps from the alignment.

The phrases listed in 05_image_phrases.md are contiguous chunks of the canonical
script in order — Agent 5 wrote them in the same sequence the words appear. So
we walk the script tokens with a pointer that advances past each matched
phrase. For each phrase, we record the start timestamp of its first token and
the end timestamp of its last token.

Matching strategy (three passes, first success wins):
  Pass 1 — Exact contiguous: phrase tokens == script[i:i+plen]
  Pass 2 — Loose contiguous: ≤10% of tokens mismatched in the window
  Pass 3 — Subsequence: non-empty phrase words appear in order within a
            bounded span (≤3× phrase length). Handles em-dashes, parentheticals,
            and any extra tokens interspersed between phrase words.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .aligner import AlignedWord, _normalize


@dataclass
class PhraseTiming:
    """A phrase row mapped to audio timestamps."""

    image_num: int       # the 1-based image number (matches image_NNN.png)
    text: str            # the raw quoted phrase text
    start: float         # seconds — start of the first word of the phrase
    end: float           # seconds — end of the last word of the phrase
    start_idx: int       # script token index where the phrase starts
    end_idx: int         # script token index where the phrase ends (inclusive)
    matched: bool        # True if found via any pass; False only when all three fail


_ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*$")
_WORD_SPLIT_RE = re.compile(r"\S+")


def parse_phrases_md(md_text: str) -> list[tuple[int, str]]:
    """Parse the phrase table from 05_image_phrases.md.

    Returns a list of (image_num, phrase_text) tuples in document order.
    Header row (`| # | Phrase |`) and separator row (`|---|---|`) are skipped.
    """
    rows: list[tuple[int, str]] = []
    for line in md_text.splitlines():
        m = _ROW_RE.match(line.strip())
        if not m:
            continue
        num_str, text = m.group(1), m.group(2)
        try:
            num = int(num_str)
        except ValueError:
            continue
        cleaned = text.strip().strip('"').strip()
        if not cleaned:
            continue
        rows.append((num, cleaned))
    return rows


def _tokenize(text: str) -> list[str]:
    return _WORD_SPLIT_RE.findall(text)


def map_phrases_to_timings(
    phrase_rows: list[tuple[int, str]],
    aligned: list[AlignedWord],
) -> list[PhraseTiming]:
    """Match each phrase to aligned script tokens using a 3-pass strategy."""
    script_norm = [_normalize(w.word) for w in aligned]
    timings: list[PhraseTiming] = []
    cursor = 0
    n = len(script_norm)

    for image_num, raw_text in phrase_rows:
        phrase_tokens = [_normalize(t) for t in _tokenize(raw_text)]
        # Keep empty tokens (from em-dashes etc.) — they match the same empty
        # tokens in script_norm, preserving positional alignment.
        # Only skip if the entire phrase tokenized to nothing.
        if not any(phrase_tokens):
            continue

        result = _find_phrase(script_norm, phrase_tokens, cursor)
        if result is None:
            # Fall back: search from the very start (rare; phrase ordering broken)
            result = _find_phrase(script_norm, phrase_tokens, 0)
        if result is None:
            timings.append(
                PhraseTiming(
                    image_num=image_num,
                    text=raw_text,
                    start=0.0,
                    end=0.0,
                    start_idx=-1,
                    end_idx=-1,
                    matched=False,
                )
            )
            continue

        start_idx, end_idx = result
        end_idx = min(end_idx, n - 1)
        timings.append(
            PhraseTiming(
                image_num=image_num,
                text=raw_text,
                start=aligned[start_idx].start,
                end=aligned[end_idx].end,
                start_idx=start_idx,
                end_idx=end_idx,
                matched=True,
            )
        )
        cursor = end_idx + 1

    return timings


def _find_phrase(
    script_norm: list[str],
    phrase_tokens: list[str],
    from_idx: int,
) -> tuple[int, int] | None:
    """Find phrase_tokens in script_norm at or after from_idx.

    Returns (start_idx, end_idx) — inclusive indices into script_norm.
    Returns None only when all three passes fail.

    Pass 1 — Exact contiguous.
    Pass 2 — Loose contiguous: ≤10% mismatched tokens.
    Pass 3 — Subsequence: non-empty phrase words found in order within a
              bounded span. Handles em-dashes, parentheticals, and any extra
              tokens interspersed between phrase words.
    """
    n = len(script_norm)
    plen = len(phrase_tokens)
    if plen == 0 or n == 0:
        return None

    # --- Pass 1: exact contiguous ---
    for i in range(from_idx, n - plen + 1):
        if script_norm[i : i + plen] == phrase_tokens:
            return i, i + plen - 1

    # --- Pass 2: loose contiguous (≤10% mismatches) ---
    max_mismatch = max(1, plen // 10)
    for i in range(from_idx, n - plen + 1):
        mismatches = sum(
            1 for k in range(plen) if script_norm[i + k] != phrase_tokens[k]
        )
        if mismatches <= max_mismatch:
            return i, i + plen - 1

    # --- Pass 3: subsequence within a bounded span ---
    # Use only non-empty tokens so em-dash placeholders don't act as wildcards.
    non_empty = [t for t in phrase_tokens if t]
    if not non_empty:
        return None
    max_span = max(plen * 3, len(non_empty) + 10)

    for start in range(from_idx, n):
        if script_norm[start] != non_empty[0]:
            continue
        j = start
        end = start
        all_found = True
        for tok in non_empty[1:]:
            found = False
            for k in range(j + 1, min(start + max_span, n)):
                if script_norm[k] == tok:
                    j = k
                    end = k
                    found = True
                    break
            if not found:
                all_found = False
                break
        if all_found:
            return start, end

    return None


def timings_to_dict(timings: list[PhraseTiming]) -> list[dict]:
    """Serialize phrase timings for JSON output."""
    return [
        {
            "image_num": t.image_num,
            "text": t.text,
            "start": round(t.start, 3),
            "end": round(t.end, 3),
            "start_idx": t.start_idx,
            "end_idx": t.end_idx,
            "matched": t.matched,
        }
        for t in timings
    ]
