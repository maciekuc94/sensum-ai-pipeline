"""Subtitle chunking for the SENSUM pipeline — duration-aware single-line cards.

Architecture (sentence-first, real word timings throughout):
  1. Drop phantom edges — leading/trailing runs of fully-unmatched (interpolated)
     words, e.g. an on-screen hook/title line that was never spoken aloud. Their
     timestamps are fabricated, so emitting them produces a wrong cue.
  2. Segment the words into SENTENCES (a paragraph break also starts one). A cue
     never spans a sentence boundary — so no cue ever reads "...troska. Że to...".
  3. Pack each sentence into cues (`_pack_sentence`):
       - split the sentence into clauses (comma / dash / pause / paragraph);
       - greedily group clauses into a cue until it reaches the duration floor
         (MIN_DUR_S), then break at that clause boundary — even rhythm, breaks on
         real linguistic boundaries with real word timestamps;
       - if a group would exceed one line (MAX_CPL) it is balance-split BY WORD
         (again real timestamps), so a sentence-final word is never stranded onto
         the next cue and no clause flashes by.
  4. Absorb leftovers (`_merge_subminimum`): a cue still under SENTENCE_MIN_S
     (0.85s, Netflix 5/6 s) is merged into its own clause / best-fitting neighbour.
  5. Quote protection, single-line safety net, gap fill, and a small lead-in so
     each cue lands with — not after — the spoken word.

Layout & sticky discipline:
  - Every cue is one line, <= MAX_CPL chars.
  - Never end a line on an article / preposition / aux verb (sticky words bind
    forward to their noun/verb), unless the word carries clause punctuation.

Research-backed thresholds (BBC / Netflix / Amara; see workflows/pipeline/align.md):
  - soft pause / paragraph break commits a cut only past MIN_DUR_S (1.2s) — this
    is what kills comma-flashes like "pobiegac," (0.78s);
  - a sentence stands at >= SENTENCE_MIN_S (0.85s), so deliberate one-word beats
    ("Oczywiscie.") survive but 0.38s tags are absorbed;
  - one line <= MAX_CPL (42); reading speed stays comfortable (~15-17 CPS).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .aligner import AlignedWord


# Layout limit — single line only
MAX_CPL = 42                 # max characters per cue (Netflix/BBC line cap)

# Timing thresholds (research-backed — BBC / Netflix / Amara; see align.md)
PAUSE_GAP_S = 0.30           # audio gap that counts as a natural pause
MIN_DUR_S = 1.20             # preferred floor: a soft pause won't break below this
SENTENCE_MIN_S = 0.85        # absolute floor (Netflix 5/6 s): a standalone cue may be this short
MAX_DUR_S = 7.00             # ceiling for merge growth (Netflix max event)
LEAD_IN_S = 0.10             # nudge every cue this many seconds earlier (lands with the word)
GAP_CLEAR_S = 1.50           # an audio pause longer than this clears the screen (no chain)
LEAD_OUT_S = 0.50            # at such a pause, how long the cue lingers after its last word
SOLO_DURATION_S = 1.00       # retained for reference; superseded by the duration floors

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
# Polish sticky words — the channel ships Polish subtitles, so Polish function
# words must bind to the following word and never dangle at a line end.
# Polish typography HARD RULE: one-letter words (w, z, i, a, o, u) must never
# end a line. Common short prepositions / conjunctions stick too. Stored
# lowercase with correct UTF-8 diacritics (matches _normalize_word output).
_POLISH_ONE_LETTER = {"w", "z", "i", "a", "o", "u"}
_POLISH_SHORT_FUNCTION = {
    # prepositions
    "do", "na", "za", "od", "po", "we", "ze", "ku", "nad", "pod", "bez",
    "przez", "przed", "oraz", "dla", "ponad", "spod", "znad",
    # conjunctions / particles
    "lub", "albo", "ani", "czy", "że", "by", "bo", "więc",
    "lecz", "gdyż", "aby", "żeby", "iż",
    # negation / reflexive that should not strand the verb
    "nie", "się",
}
_POLISH_STICKY = _POLISH_ONE_LETTER | _POLISH_SHORT_FUNCTION

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
        or w in _POLISH_STICKY
    )


def _clean_word_for_display(word: str) -> str:
    word = word.strip()
    word = re.sub(r"^[*_]+|[*_]+$", "", word)   # strip markdown emphasis markers
    return re.sub(r"[.!]+$", "", word)          # drop sentence-final period/exclam


def _chunk_text(words: list[AlignedWord]) -> str:
    return " ".join(_clean_word_for_display(w.word) for w in words)


def _card_len(words: list[AlignedWord]) -> int:
    """Rendered single-line length of a word list (display text, as shown)."""
    return len(_chunk_text(words))


# Phantom-edge trimming -------------------------------------------------------

def _strip_phantom_edges(aligned: list[AlignedWord]) -> list[AlignedWord]:
    """Drop leading/trailing runs of fully-unmatched (interpolated) words.

    A run of unmatched words at the very head or tail of the script has no real
    audio anchor on one side, so its timestamps are fabricated (crammed between
    0.0 and the first real word, or between the last real word and the audio
    end). Emitting them produces a wrong cue — e.g. an on-screen hook / title
    line written into the script but never spoken aloud. Interior unmatched
    words are kept: they sit between two matched neighbours and interpolate
    sensibly. If nothing matched at all, the list is returned untouched so the
    failure is visible rather than silently swallowed.
    """
    if not any(w.matched for w in aligned):
        return list(aligned)
    start = 0
    while start < len(aligned) and not aligned[start].matched:
        start += 1
    end = len(aligned)
    while end > start and not aligned[end - 1].matched:
        end -= 1
    return list(aligned[start:end])


# Sentence / clause segmentation ----------------------------------------------

def _segment_sentences(words: list[AlignedWord]) -> list[list[AlignedWord]]:
    """Split the word stream into sentence units.

    A unit ends after any word carrying a terminator (. ! ?). A source paragraph
    break (force_break_before on the next word) also starts a new unit. Cues are
    built per-unit and never merged across one in the builder, so a cue can never
    straddle two sentences.
    """
    sentences: list[list[AlignedWord]] = []
    cur: list[AlignedWord] = []
    for w in words:
        if cur and w.force_break_before:
            sentences.append(cur)
            cur = []
        cur.append(w)
        if _ends_sentence(w.word):
            sentences.append(cur)
            cur = []
    if cur:
        sentences.append(cur)
    return sentences


def _segment_clauses(words: list[AlignedWord]) -> list[list[AlignedWord]]:
    """Split one sentence's words into clauses at commas / dashes / audio pauses.

    A clause boundary is suppressed when the boundary word is sticky (a function
    word that must bind forward) so we never strand an article/preposition at a
    line end.
    """
    clauses: list[list[AlignedWord]] = []
    cur: list[AlignedWord] = []
    n = len(words)
    for i, w in enumerate(words):
        cur.append(w)
        nxt = words[i + 1] if i + 1 < n else None
        if nxt is None:
            boundary = True
        else:
            boundary = (
                _ends_comma(w.word)
                or _ends_with_dash(w.word)
                or (nxt.start - w.end) >= PAUSE_GAP_S
                or nxt.force_break_before
            )
        if boundary and not _is_sticky(w.word):
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    return clauses


def _balance_split_words(words: list[AlignedWord], max_cpl: int) -> list[list[AlignedWord]]:
    """Split an over-line run of words into balanced <= max_cpl word-lists.

    Greedy pack to max_cpl, then balance a thin tail backward and shift sticky
    line-enders forward. Operates on AlignedWord lists so each resulting cue
    keeps the real start/end of its own words (no proportional approximation).
    """
    lists: list[list[AlignedWord]] = []
    cur: list[AlignedWord] = []
    for w in words:
        disp = _clean_word_for_display(w.word)
        added = len(disp) if not cur else _card_len(cur) + 1 + len(disp)
        if added > max_cpl and cur:
            if _is_standalone_dash(w.word):
                cur.append(w)   # a bare dash binds backward — keep it on this line
                continue
            lists.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lists.append(cur)

    # Balance: pull a trailing word from the previous line into a 1–2 word tail.
    for i in range(1, len(lists)):
        while len(lists[i]) <= 2 and len(lists[i - 1]) > 1:
            popped = lists[i - 1][-1]
            proj_cur = _card_len([popped] + lists[i])
            proj_prev = _card_len(lists[i - 1][:-1])
            if proj_cur <= max_cpl and proj_prev >= 1 and proj_prev >= proj_cur // 2:
                lists[i - 1] = lists[i - 1][:-1]
                lists[i] = [popped] + lists[i]
            else:
                break

    # Shift a sticky line-ender forward so it binds to its noun/verb.
    for i in range(len(lists) - 1):
        while len(lists[i]) > 1 and _is_sticky(lists[i][-1].word):
            popped = lists[i][-1]
            if _card_len([popped] + lists[i + 1]) <= max_cpl:
                lists[i] = lists[i][:-1]
                lists[i + 1] = [popped] + lists[i + 1]
            else:
                break

    return [wl for wl in lists if wl]


def _pack_sentence(words: list[AlignedWord], min_dur: float, max_cpl: int) -> list[list[AlignedWord]]:
    """Pack one sentence into cue word-lists with real timestamps.

    Clauses are grouped until the cue reaches min_dur, then broken at that clause
    boundary. A group that would overrun one line is balance-split by word; if
    the running cue is still too short to stand alone when an overrun looms, the
    short head is folded into the balance-split rather than stranded.
    """
    clauses = _segment_clauses(words)
    if not clauses:
        return []

    cues: list[list[AlignedWord]] = []
    cur: list[AlignedWord] = []
    last_idx = len(clauses) - 1
    for ci, cl in enumerate(clauses):
        if cur and _card_len(cur + cl) > max_cpl:
            cur_dur = cur[-1].end - cur[0].start
            if cur_dur < min_dur:
                # Too short to stand alone — combine with this clause and split
                # the combination by word so nothing is stranded. All but the
                # last piece are final; the last stays open for further grouping.
                pieces = _balance_split_words(cur + cl, max_cpl)
                cues.extend(pieces[:-1])
                cur = pieces[-1]
            else:
                cues.append(cur)
                cur = list(cl)
        else:
            cur = cur + cl
        dur = cur[-1].end - cur[0].start
        if ci != last_idx and dur >= min_dur:
            cues.append(cur)
            cur = []
    if cur:
        cues.append(cur)

    # Any cue that is still a single over-line clause → balance-split by word.
    out: list[list[AlignedWord]] = []
    for cue in cues:
        if _card_len(cue) <= max_cpl:
            out.append(cue)
        else:
            out.extend(_balance_split_words(cue, max_cpl))
    return out


# Sub-minimum merge -----------------------------------------------------------

def _merge_subminimum(
    chunks: list[SubtitleChunk],
    *,
    sentence_min: float,
    max_dur: float,
) -> list[SubtitleChunk]:
    """Absorb any cue shorter than sentence_min, keeping it with its own clause.

    Sentence-first packing already keeps mid-sentence cues at/above the floor, so
    a short cue is usually a complete short sentence with no same-clause
    neighbour: merge it into whichever neighbour fits one line (shorter first),
    or leave it as a deliberate beat rather than force a sentence-crossing
    overflow. A rare mid-sentence remainder (``forced_start``/``forced_end``
    False) is merged into its own clause, allowing a brief overflow that the
    single-line pass re-splits inside the sentence.
    """
    def dur(c: SubtitleChunk) -> float:
        return c.end - c.start

    changed = True
    while changed and len(chunks) > 1:
        changed = False
        for i, c in enumerate(chunks):
            if dur(c) >= sentence_min:
                continue
            same_clause_prev = i > 0 and not c.forced_start
            same_clause_next = i < len(chunks) - 1 and not c.forced_end

            if same_clause_prev:
                p = chunks[i - 1]
                if (c.end - p.start) <= max_dur and len(p.text) + 1 + len(c.text) <= 2 * MAX_CPL:
                    p.text = p.text + " " + c.text
                    p.end = c.end
                    p.forced_end = c.forced_end
                    chunks.pop(i)
                    changed = True
                    break
            if same_clause_next:
                n = chunks[i + 1]
                if (n.end - c.start) <= max_dur and len(c.text) + 1 + len(n.text) <= 2 * MAX_CPL:
                    n.text = c.text + " " + n.text
                    n.start = c.start
                    n.forced_start = c.forced_start
                    chunks.pop(i)
                    changed = True
                    break

            options: list[tuple[float, str]] = []  # (neighbour_dur, side)
            if i > 0:
                p = chunks[i - 1]
                if len(p.text) + 1 + len(c.text) <= MAX_MERGED_CHARS and (c.end - p.start) <= max_dur:
                    options.append((dur(p), "prev"))
            if i < len(chunks) - 1:
                n = chunks[i + 1]
                if len(c.text) + 1 + len(n.text) <= MAX_MERGED_CHARS and (n.end - c.start) <= max_dur:
                    options.append((dur(n), "next"))
            if not options:
                continue
            options.sort()
            if options[0][1] == "prev":
                p = chunks[i - 1]
                p.text = p.text + " " + c.text
                p.end = c.end
                p.forced_end = c.forced_end
                chunks.pop(i)
            else:
                n = chunks[i + 1]
                n.text = c.text + " " + n.text
                n.start = c.start
                n.forced_start = c.forced_start
                chunks.pop(i)
            changed = True
            break
    return chunks


# Main chunk builder ----------------------------------------------------------

def _gap_fill(chunks: list[SubtitleChunk], *, gap_clear: float, lead_out: float) -> None:
    """Chain each cue's end to the next cue's start — except across a real pause.

    Continuous speech → cues chain (no gaps), so a subtitle is always on screen.
    But where the audio pause to the next cue exceeds ``gap_clear`` (a section
    break), the cue lingers only ``lead_out`` seconds past its last word and then
    the screen clears, letting it breathe — matching how a human subtitler times
    section transitions. ``gap_clear <= 0`` restores fully-continuous behaviour.
    """
    for i in range(len(chunks) - 1):
        nxt = chunks[i + 1].start
        pause = nxt - chunks[i].end
        if gap_clear > 0 and pause > gap_clear:
            chunks[i].end = min(nxt, chunks[i].end + lead_out)
        else:
            chunks[i].end = nxt


def build_chunks(
    aligned: list[AlignedWord],
    *,
    min_dur: float = MIN_DUR_S,
    sentence_min: float = SENTENCE_MIN_S,
    max_dur: float = MAX_DUR_S,
    lead_in: float = LEAD_IN_S,
    gap_clear: float = GAP_CLEAR_S,
    lead_out: float = LEAD_OUT_S,
    drop_phantom: bool = True,
) -> list[SubtitleChunk]:
    """Group aligned words into duration-aware single-line subtitle cues.

    Sentence-first: each sentence is packed independently (so no cue spans a
    sentence boundary), clauses are grouped to the duration floor, and over-line
    groups are balance-split by word — all on real word timestamps. See the
    module docstring for the full pipeline.
    """
    aligned = _strip_phantom_edges(aligned) if drop_phantom else list(aligned)
    if not aligned:
        return []

    chunks: list[SubtitleChunk] = []
    for sentence in _segment_sentences(aligned):
        word_lists = _pack_sentence(sentence, min_dur, MAX_CPL)
        for j, wl in enumerate(word_lists):
            chunks.append(SubtitleChunk(
                index=0,
                text=_chunk_text(wl),
                start=wl[0].start,
                end=wl[-1].end,
                forced_start=(j == 0),                       # first cue of a sentence
                forced_end=(j == len(word_lists) - 1),       # last cue of a sentence
            ))

    # --- Post-pass 1: absorb any cue still under the absolute minimum ---------
    chunks = _merge_subminimum(chunks, sentence_min=sentence_min, max_dur=max_dur)

    # --- Post-pass 2: quote protection — keep an opening quote with content ---
    i = 0
    while i < len(chunks) - 1:
        cur = chunks[i]
        nxt = chunks[i + 1]
        if cur.text.count('"') % 2 == 1:  # unbalanced — inside a quote
            combined = cur.text + " " + nxt.text
            if len(combined) <= MAX_QUOTE_CHARS:
                cur.text = combined
                cur.end = nxt.end
                cur.forced_end = nxt.forced_end
                chunks.pop(i + 1)
                continue  # re-check same index with new next chunk
        i += 1

    # --- Post-pass 3: single-line safety net (should be a no-op after packing) -
    chunks = _enforce_single_line(chunks)

    # --- Re-number + final chain (clearing the screen at real pauses) --------
    for idx, chunk in enumerate(chunks, 1):
        chunk.index = idx
    _gap_fill(chunks, gap_clear=gap_clear, lead_out=lead_out)

    # --- Lead-in: nudge every cue slightly earlier so it lands with (not after)
    # the spoken word. A subtitle that trails speech reads as "late"; leading by
    # ~0.1s reads as on-time. Per-cue duration and the chain are preserved.
    if lead_in > 0:
        for chunk in chunks:
            chunk.start = max(0.0, chunk.start - lead_in)
            chunk.end = max(chunk.start + 0.05, chunk.end - lead_in)

    return chunks


# Single-line enforcement ----------------------------------------------------

def _enforce_single_line(chunks: list[SubtitleChunk]) -> list[SubtitleChunk]:
    """Ensure every chunk's text fits on a single line (≤ MAX_CPL chars).

    Any chunk exceeding MAX_CPL is split into multiple single-line cues with
    proportionally-distributed timestamps. With sentence-first packing this is a
    safety net only — the builder already balance-splits over-line groups by word.
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
