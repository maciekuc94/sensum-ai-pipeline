"""Smart subtitle chunking matching the user's adaptive-pacing style.

Break rules (in priority order):
  1. After sentence-ending punctuation (. ! ?)
  2. After a natural pause (gap ≥ PAUSE_GAP_S)
  3. After a comma — comma always ends its chunk
  4. When chunk reaches MAX_WORDS_PER_CHUNK
  5. Held single word (duration > SOLO_DURATION_S)

Sticky words — never end a chunk on these (always attach to the next word):
  - Articles: "the", "a", "an"
  - Standalone dashes: "-", "—"

Post-processing passes (applied after streaming build):
  - Orphan merge: chunks of 1-2 words merge into the previous chunk
    when the combined word count stays ≤ MAX_MERGED_WORDS
  - Quote protection: opening-quote chunks with ≤ MAX_QUOTE_WORDS total
    merge forward until the closing quote
  - Gap fill: each chunk's end is extended to the next chunk's start
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .aligner import AlignedWord


PAUSE_GAP_S = 0.30
SOLO_DURATION_S = 0.45
MAX_WORDS_PER_CHUNK = 6
MAX_MERGED_WORDS = 7
MAX_QUOTE_WORDS = 8

_TERMINAL_RE = re.compile(r"[.!?][\"')\]]?$")
_COMMA_END_RE = re.compile(r",$")
_DASH_ONLY_RE = re.compile(r"^[—\-]+$")
_ARTICLE_RE = re.compile(r"^(the|a|an)$", re.IGNORECASE)


@dataclass
class SubtitleChunk:
    index: int
    text: str
    start: float
    end: float


def _ends_sentence(word: str) -> bool:
    return bool(_TERMINAL_RE.search(word))


def _ends_comma(word: str) -> bool:
    return bool(_COMMA_END_RE.search(word))


def _is_sticky(word: str) -> bool:
    """Words that must never be the last word in a chunk."""
    w = word.strip()
    return bool(_ARTICLE_RE.match(w)) or bool(_DASH_ONLY_RE.match(w))


def _clean_word_for_display(word: str) -> str:
    word = word.strip()
    word = re.sub(r"^[*_]+|[*_]+$", "", word)  # strip markdown emphasis markers
    return re.sub(r"[.!]+$", "", word)


def _word_count(text: str) -> int:
    return len(text.split())


def build_chunks(aligned: list[AlignedWord]) -> list[SubtitleChunk]:
    if not aligned:
        return []

    chunks: list[SubtitleChunk] = []
    current: list[AlignedWord] = []

    def flush() -> None:
        if not current:
            return
        text = " ".join(_clean_word_for_display(w.word) for w in current)
        chunks.append(SubtitleChunk(
            index=0,
            text=text,
            start=current[0].start,
            end=current[-1].end,
        ))
        current.clear()

    prev: AlignedWord | None = None
    for w in aligned:
        if prev is not None:
            gap = max(0.0, w.start - prev.end)
            duration = max(0.0, w.end - w.start)
            last_sticky = current and _is_sticky(current[-1].word)

            if not last_sticky:
                if prev.end - prev.start > SOLO_DURATION_S and len(current) == 1:
                    flush()
                elif _ends_sentence(prev.word):
                    flush()
                elif _ends_comma(prev.word):
                    flush()
                elif gap >= PAUSE_GAP_S:
                    flush()
                elif len(current) >= MAX_WORDS_PER_CHUNK:
                    flush()
                elif duration > SOLO_DURATION_S and len(current) >= 1:
                    flush()
                    current.append(w)
                    flush()
                    prev = w
                    continue

        current.append(w)
        prev = w

    flush()

    # --- Post-processing pass 1: merge orphan chunks (1-2 words) into previous ---
    i = 1
    while i < len(chunks):
        wc_i = _word_count(chunks[i].text)
        wc_prev = _word_count(chunks[i - 1].text)
        if wc_i <= 2 and wc_prev + wc_i <= MAX_MERGED_WORDS:
            chunks[i - 1].text = chunks[i - 1].text + " " + chunks[i].text
            chunks[i - 1].end = chunks[i].end
            chunks.pop(i)
        else:
            i += 1

    # --- Post-processing pass 2: quote protection ---
    # If a chunk opens a quote but has no closing quote, merge forward while
    # total word count stays ≤ MAX_QUOTE_WORDS.
    i = 0
    while i < len(chunks) - 1:
        t = chunks[i].text
        opens = t.count('"')
        if opens % 2 == 1:  # unbalanced — inside a quote
            combined = t + " " + chunks[i + 1].text
            if _word_count(combined) <= MAX_QUOTE_WORDS:
                chunks[i].text = combined
                chunks[i].end = chunks[i + 1].end
                chunks.pop(i + 1)
                continue  # re-check same index with new next chunk
        i += 1

    # --- Re-number ---
    for idx, chunk in enumerate(chunks, 1):
        chunk.index = idx

    # --- Gap fill: extend each end to next start ---
    for i, chunk in enumerate(chunks[:-1]):
        chunk.end = chunks[i + 1].start

    return chunks


def _format_srt_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0.0
    total_ms = int(round(seconds * 1000))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, ms = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{ms:03d}"


def render_srt(chunks: list[SubtitleChunk]) -> str:
    lines: list[str] = []
    for chunk in chunks:
        lines.append(str(chunk.index))
        lines.append(f"{_format_srt_time(chunk.start)} --> {_format_srt_time(chunk.end)}")
        lines.append(chunk.text)
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def chunks_to_dict(chunks: list[SubtitleChunk]) -> list[dict]:
    return [
        {
            "index": c.index,
            "text": c.text,
            "start": round(c.start, 3),
            "end": round(c.end, 3),
        }
        for c in chunks
    ]
