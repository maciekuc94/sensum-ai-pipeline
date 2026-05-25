"""Subtitle chunking for the SENSUM pipeline — single-line cards only.

Output discipline:
  - Every cue is exactly one line of text (no 2-line cards).
  - Max MAX_CPL characters per line (default 42).
  - Break only at natural pauses; never end a line on an article, common
    preposition, or auxiliary verb (would orphan it from its noun/main verb),
    unless the word ends in punctuation (which marks a clause boundary).

Break rules in priority order (highest → lowest):
  1. force_break_before on the next word        — paragraph / newline in source
  2. previous word ends a sentence (.!?)         — sentence terminator
  3. previous word ends with a comma             — comma pause
  4. previous word is or ends in a standalone dash (— or -)
  5. natural pause in audio (gap ≥ PAUSE_GAP_S)
  6. adding the next word would exceed MAX_CPL
  7. solo held word (duration > SOLO_DURATION_S)

A break is suppressed if the chunk's current last word is "sticky" — sticky
words (articles, prepositions, aux verbs) must always attach to the next word.

Post-processing passes:
  - Orphan merge: 1–2 word chunks merge into the previous chunk EXCEPT when
    the boundary was created by a forced break (rules 1–4).
  - Forward fragment absorb: 1–2 word leading fragments merge into the next
    chunk (handles a paragraph's first word being flushed alone due to a
    speaker pause).
  - Quote protection: opening-quote chunks merge forward until quote closes,
    bounded by MAX_CPL.
  - Overflow split: any chunk still longer than MAX_CPL is greedily split
    into multiple single-line cues with proportionally-distributed timestamps.
  - Gap fill: each chunk's end is extended to the next chunk's start.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .aligner import AlignedWord


# Layout limit — single line only
MAX_CPL = 42                                # max characters per cue

# Timing thresholds
PAUSE_GAP_S = 0.30
SOLO_DURATION_S = 1.00       # only really-held words deserve their own cue

# Merge bounds — never grow a cue past one line
MAX_MERGED_CHARS = MAX_CPL
MAX_QUOTE_CHARS = MAX_CPL


# Punctuation detectors -------------------------------------------------------
_TERMINAL_RE = re.compile(r"[.!?][\"')\]]?$")
_COMMA_END_RE = re.compile(r",[\"')\]]?$")
_STANDALONE_DASH_RE = re.compile(r"^[—–\-]+$")
_TRAILING_DASH_RE = re.compile(r"[—–]$")     # em / en dash at end (true dash, not hyphen)

# Sticky-word lexicons (lowercase, normalized)
_ARTICLES = {"the", "a", "an"}
_POSSESSIVES = {"my", "your", "his", "her", "our", "their", "its"}
_PREPOSITIONS = {
    "in", "on", "at", "to", "for", "with", "of", "by", "from", "about",
    "as", "into", "than", "over", "under", "between", "through", "across",
    "after", "before", "during", "without", "within", "upon", "onto",
    "against", "toward", "towards",
}
_AUX_VERBS = {
    "is", "are", "was", "were", "be", "been", "being", "am",
    "have", "has", "had",
    "do", "does", "did",
    "will", "would", "shall", "should", "can", "could", "may", "might", "must",
}
_CONJUNCTIONS_SPLIT_PREFERRED = {"and", "or", "but", "so", "yet", "because", "while", "when"}

_WORD_NORM_RE = re.compile(r"[^\w']+", re.UNICODE)


@dataclass
class SubtitleChunk:
    index: int
    text: str
    start: float
    end: float
    forced_start: bool = False
    forced_end: bool = False


# Word-shape helpers ----------------------------------------------------------

def _normalize_word(word: str) -> str:
    return _WORD_NORM_RE.sub("", word).lower()


def _ends_sentence(word: str) -> bool:
    return bool(_TERMINAL_RE.search(word))


def _ends_comma(word: str) -> bool:
    return bool(_COMMA_END_RE.search(word))


def _is_standalone_dash(word: str) -> bool:
    return bool(_STANDALONE_DASH_RE.match(word.strip()))


def _ends_with_dash(word: str) -> bool:
    """True for a standalone em/en/hyphen-as-pause, OR a word ending in em/en dash."""
    s = word.strip()
    if _is_standalone_dash(s):
        return True
    return bool(_TRAILING_DASH_RE.search(s))


def _is_sticky(word: str) -> bool:
    """Words that must never be the last word of a line.

    A word ending in punctuation (comma / period / dash / etc.) is never sticky —
    the punctuation marks a deliberate clause boundary, regardless of part of
    speech. ("do," can end a line; bare "do" cannot.)
    """
    s = word.strip()
    if _ends_comma(s) or _ends_sentence(s) or _ends_with_dash(s):
        return False
    w = _normalize_word(s)
    if not w:
        return False
    return (
        w in _ARTICLES
        or w in _POSSESSIVES
        or w in _PREPOSITIONS
        or w in _AUX_VERBS
    )


def _clean_word_for_display(word: str) -> str:
    word = word.strip()
    word = re.sub(r"^[*_]+|[*_]+$", "", word)   # strip markdown emphasis markers
    return re.sub(r"[.!]+$", "", word)          # drop sentence-final period/exclam


def _chunk_text(words: list[AlignedWord]) -> str:
    return " ".join(_clean_word_for_display(w.word) for w in words)


# Main chunk builder ----------------------------------------------------------

def build_chunks(aligned: list[AlignedWord]) -> list[SubtitleChunk]:
    if not aligned:
        return []

    chunks: list[SubtitleChunk] = []
    current: list[AlignedWord] = []
    next_chunk_forced_start = False

    def projected_card_len(extra: AlignedWord | None = None) -> int:
        words = current + ([extra] if extra is not None else [])
        return len(_chunk_text(words))

    def flush(reason_forced: bool) -> None:
        nonlocal next_chunk_forced_start
        if not current:
            return
        text = _chunk_text(current)
        chunks.append(SubtitleChunk(
            index=0,
            text=text,
            start=current[0].start,
            end=current[-1].end,
            forced_start=next_chunk_forced_start,
            forced_end=reason_forced,
        ))
        current.clear()
        next_chunk_forced_start = reason_forced

    prev: AlignedWord | None = None
    for w in aligned:
        if prev is not None and current:
            last_word = current[-1].word
            last_sticky = _is_sticky(last_word)
            gap = max(0.0, w.start - prev.end)
            prev_duration = max(0.0, prev.end - prev.start)

            # Standalone-dash protection: never flush a chunk whose only
            # content is a bare dash — it would render as a single "—" cue.
            current_is_just_dash = (
                len(current) == 1 and _is_standalone_dash(current[0].word)
            )

            # Rule 1: forced break before this word (paragraph in source).
            # This bypasses sticky — if the script intentionally broke the line,
            # we honor it even at the cost of an orphaned article.
            if w.force_break_before and not current_is_just_dash:
                flush(reason_forced=True)
            elif current_is_just_dash:
                pass  # let the dash attach to the next word
            elif not last_sticky:
                # Rule 2: previous word ends a sentence.
                if _ends_sentence(last_word):
                    flush(reason_forced=True)
                # Rule 3: previous word ends with a comma.
                elif _ends_comma(last_word):
                    flush(reason_forced=True)
                # Rule 4: previous word is/ends with a dash.
                elif _ends_with_dash(last_word):
                    flush(reason_forced=True)
                # Rule 5: natural pause in audio.
                elif gap >= PAUSE_GAP_S:
                    flush(reason_forced=False)
                # Rule 6: solo held word (only fires for very held words).
                elif prev_duration > SOLO_DURATION_S and len(current) == 1:
                    flush(reason_forced=False)
            # Note: no MAX_CPL flush here — the _enforce_single_line post-pass
            # greedy-splits oversized chunks at non-sticky word boundaries,
            # which avoids orphans like a stranded sentence-final word.

        current.append(w)
        prev = w

    flush(reason_forced=False)

    # --- Post-processing pass 1: merge orphan chunks (≤2 words) backward ---
    # Skip across forced boundaries (intentional punctuation breaks).
    i = 1
    while i < len(chunks):
        cur = chunks[i]
        prev_c = chunks[i - 1]
        wc_cur = len(cur.text.split())
        boundary_forced = prev_c.forced_end or cur.forced_start
        combined_chars = len(prev_c.text) + 1 + len(cur.text)
        if (
            not boundary_forced
            and wc_cur <= 2
            and combined_chars <= MAX_MERGED_CHARS
        ):
            prev_c.text = prev_c.text + " " + cur.text
            prev_c.end = cur.end
            prev_c.forced_end = cur.forced_end
            chunks.pop(i)
        else:
            i += 1

    # --- Post-processing pass 1b: forward-absorb leading fragments ---
    # If chunk i is a 1–2 word fragment that does NOT end with deliberate
    # punctuation (comma / dash / sentence terminator), absorb it forward into
    # chunk i+1. Handles cases like a paragraph's first word being flushed as
    # a singleton due to a speaker pause ("Most" → merge into "of the time,").
    i = 0
    while i < len(chunks) - 1:
        cur = chunks[i]
        nxt = chunks[i + 1]
        wc_cur = len(cur.text.split())
        cur_last_word = cur.text.rsplit(" ", 1)[-1] if cur.text else ""
        ends_with_punct = (
            _ends_comma(cur_last_word)
            or _ends_sentence(cur_last_word)
            or _ends_with_dash(cur_last_word)
        )
        combined_chars = len(cur.text) + 1 + len(nxt.text)
        # Allow forward-merge to overflow a single line; the single-line
        # enforcement pass will re-split the merged chunk cleanly. Cap at
        # 2 × MAX_CPL so a fragment never absorbs a giant chunk.
        if (
            wc_cur <= 2
            and not ends_with_punct
            and not cur.forced_end
            and combined_chars <= MAX_CPL * 2
        ):
            nxt.text = cur.text + " " + nxt.text
            nxt.start = cur.start
            # Preserve forced_start from the fragment (e.g. paragraph break)
            nxt.forced_start = cur.forced_start or nxt.forced_start
            chunks.pop(i)
            # Do NOT increment i — re-check the merged chunk against its new neighbor
        else:
            i += 1

    # --- Post-processing pass 2: quote protection ---
    i = 0
    while i < len(chunks) - 1:
        cur = chunks[i]
        nxt = chunks[i + 1]
        opens = cur.text.count('"')
        if opens % 2 == 1:  # unbalanced — inside a quote
            combined = cur.text + " " + nxt.text
            if len(combined) <= MAX_QUOTE_CHARS:
                cur.text = combined
                cur.end = nxt.end
                cur.forced_end = nxt.forced_end
                chunks.pop(i + 1)
                continue  # re-check same index with new next chunk
        i += 1

    # --- Post-processing pass 3: enforce single-line cards ---
    # Any chunk still exceeding MAX_CPL (rare — happens only when sticky-word
    # protection prevented earlier flushes) is split into multiple single-line
    # cues with proportionally-distributed timestamps.
    chunks = _enforce_single_line(chunks)

    # --- Re-number ---
    for idx, chunk in enumerate(chunks, 1):
        chunk.index = idx

    # --- Gap fill: extend each end to next start ---
    for i, chunk in enumerate(chunks[:-1]):
        chunk.end = chunks[i + 1].start

    return chunks


# Single-line enforcement ----------------------------------------------------

def _enforce_single_line(chunks: list[SubtitleChunk]) -> list[SubtitleChunk]:
    """Ensure every chunk's text fits on a single line (≤ MAX_CPL chars).

    Any chunk exceeding MAX_CPL is split into multiple single-line cues with
    proportionally-distributed timestamps.
    """
    out: list[SubtitleChunk] = []
    for chunk in chunks:
        if len(chunk.text) <= MAX_CPL:
            out.append(chunk)
        else:
            out.extend(_split_into_cues(chunk))
    return out


def _split_into_cues(chunk: SubtitleChunk) -> list[SubtitleChunk]:
    """Split an overflowing chunk into multiple single-line cues.

    Greedily pack words onto a line until the next word would exceed MAX_CPL,
    then start a new cue. Timestamps are distributed proportionally by the
    character length of each cue.

    Repair pass: if a cue ends on a sticky word (article / preposition / aux
    verb), shift those sticky words forward to the next cue so they bind to
    their following noun/main verb. (Skipped for the final cue.)
    """
    words = chunk.text.split()
    if not words:
        return [chunk]

    cue_word_lists: list[list[str]] = []
    current: list[str] = []
    current_len = 0
    for w in words:
        added_len = len(w) if not current else current_len + 1 + len(w)
        if added_len > MAX_CPL and current:
            # Standalone dashes bind backward (left-sticky): include them on
            # the current line even if it exceeds MAX_CPL by a few chars,
            # rather than starting the next cue with a bare "—".
            if _is_standalone_dash(w):
                current.append(w)
                current_len = added_len
                continue
            cue_word_lists.append(current)
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len = added_len
    if current:
        cue_word_lists.append(current)

    def list_len(wl: list[str]) -> int:
        return sum(len(w) for w in wl) + max(0, len(wl) - 1)

    # Balance repair: if any cue has only 1–2 words AND the cue before it has
    # room to spare, shift words from the previous cue forward to balance.
    # This avoids orphan tails like "hotter" alone after "...needs to run".
    for i in range(1, len(cue_word_lists)):
        cur_list = cue_word_lists[i]
        prev_list = cue_word_lists[i - 1]
        while len(cur_list) <= 2 and len(prev_list) > 1:
            popped = prev_list[-1]
            projected_cur_len = len(popped) + 1 + list_len(cur_list)
            projected_prev_len = list_len(prev_list) - len(popped) - 1
            if projected_cur_len <= MAX_CPL and projected_prev_len >= 1:
                # Only shift if it actually helps balance — i.e., new prev still
                # has at least ~half the chars of the new current.
                if projected_prev_len >= projected_cur_len // 2:
                    prev_list.pop()
                    cur_list.insert(0, popped)
                else:
                    break
            else:
                break

    # Repair: shift sticky-ending words forward (if the next cue can fit them).
    for i in range(len(cue_word_lists) - 1):
        cur_list = cue_word_lists[i]
        next_list = cue_word_lists[i + 1]
        while len(cur_list) > 1 and _is_sticky(cur_list[-1]):
            popped = cur_list[-1]
            projected_next_len = len(popped) + 1 + list_len(next_list)
            if projected_next_len <= MAX_CPL:
                cur_list.pop()
                next_list.insert(0, popped)
            else:
                break

    cue_texts = [" ".join(wl) for wl in cue_word_lists if wl]

    if len(cue_texts) == 1:
        chunk.text = cue_texts[0]
        return [chunk]

    total_chars = sum(len(t) for t in cue_texts)
    span = max(0.001, chunk.end - chunk.start)
    new_chunks: list[SubtitleChunk] = []
    cursor = chunk.start
    for i, t in enumerate(cue_texts):
        if i == len(cue_texts) - 1:
            end = chunk.end
        else:
            end = cursor + span * (len(t) / total_chars)
        new_chunks.append(SubtitleChunk(
            index=0,
            text=t,
            start=cursor,
            end=end,
            forced_start=chunk.forced_start if i == 0 else False,
            forced_end=chunk.forced_end if i == len(cue_texts) - 1 else False,
        ))
        cursor = end
    return new_chunks


# SRT rendering ---------------------------------------------------------------

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
            "forced_start": c.forced_start,
            "forced_end": c.forced_end,
        }
        for c in chunks
    ]
