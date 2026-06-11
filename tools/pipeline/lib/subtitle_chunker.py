"""Subtitle chunking for the SENSUM pipeline — fit-first single-line cards.

Redesigned 2026-06-10 against the user's hand-finished film (slug 3): every
burned-in card was extracted frame-accurately from the final .mov, matched to
script words, and the chunker was rebuilt to reproduce that de-facto style.

Segmentation (fit-first, seam-split):
  1. Drop phantom edges — leading/trailing runs of fully-unmatched
     (interpolated) words (an on-screen hook/title never read aloud).
  2. Split into SENTENCES (paragraph breaks also split). A cue never spans a
     sentence boundary.
  3. FIT-FIRST: a sentence that fits one line (<= MAX_CPL) is ONE card —
     duration floors never force extra cuts (the user keeps "taki, jaki
     jesteś, to za mało" whole even though it has two commas).
  4. An over-line sentence is split recursively at the strongest SEAM:
       class 3 — after a colon, after a closing quote, before an opening
                 quote (quote = atomic unit; this class even strands a
                 sticky word: the user writes "Ale po chwili z" | "„spóźniłem
                 się…"),
       class 2 — after a comma / dash,
       class 1 — at an audio pause (>= PAUSE_GAP_S),
       class 0 — plain word boundary.
     With a punctuation/quote seam available: cut at the LONGEST left piece
     that still fits the line (late cut = his rhythm). With only plain
     boundaries: cut at the most BALANCED point. Never after a forward-sticky
     function word, never before a backward clitic (ci/się/mi…).
  5. Tiny-quote pairing: consecutive whole-quote sentences each <= ~1.3 s
     merge onto one card ("„Rozwijaj się.” „Pracuj nad sobą.”").
  6. Sub-minimum absorb: a fragment under SENTENCE_MIN_S merges into its
     sentence neighbour. Short standalone sentences SURVIVE (the user keeps
     a 0.6 s "Optymalizuj" card).

Timing (switch-delay model — measured from the user's hand-timed film):
  The user's switch points track the NEXT phrase's first-word onset plus
  ~0.45 s (sigma 0.24 s — the tightest of the tested models), and after a
  cleared pause the new card appears ~0.35 s past the word onset. A card
  before a long pause lingers ~1.5 s, then the screen clears. Pauses up to
  ~1.9 s do NOT clear (his film keeps chaining through a 1.8 s pause; clears
  start at 2.1 s).
    - cue N start = its first word start + SWITCH_DELAY (chained & post-clear)
    - cue N-1 end = cue N start (chain), or last word end + CLEAR_LINGER at
      a cleared pause
    - first cue starts FIRST_PREROLL_S before its first word (with the
      trim-head feature in agent_align this lands at t=0, like his films)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .aligner import AlignedWord


# Layout limit — single line only
MAX_CPL = 42                 # max characters per cue (user's p90 is 38; 2 hand-made cards reach 46)

# Timing thresholds (calibrated on the slug-3 finished film, 2026-06-10)
PAUSE_GAP_S = 0.30           # audio gap that counts as a natural pause (seam class 1)
SENTENCE_MIN_S = 0.35        # fragments shorter than this merge into a neighbour
MAX_DUR_S = 7.00             # hard ceiling for any single cue
LEAD_IN_S = 0.0              # extra global earlier-nudge (legacy knob; default off)
GAP_CLEAR_S = 1.90           # audio pause above which the screen clears (film: 1.8 chains, 2.1 clears)
CLEAR_LINGER_S = 1.50        # how long a cue lingers past its last word at a cleared pause
SWITCH_DELAY_S = 0.40        # chained cue appears this long after its first word's onset
POST_CLEAR_DELAY_S = 0.35    # delay after a cleared pause (film: +0.29..+0.41)
FIRST_PREROLL_S = 0.15       # first cue leads its word by this much
MIN_CLEAR_GAP_S = 0.25       # minimum off-screen time at a cleared pause
QUOTE_PAIR_MAX_S = 1.30      # quote-sentences up to this long may pair onto one card

MIN_SIDE_CHARS = 6           # a seam may not strand fewer display chars than this


# Punctuation detectors -------------------------------------------------------
_TERMINAL_RE = re.compile(r"[.!?][\"”'»)\]]?$")
_COMMA_END_RE = re.compile(r",[\"”'»)\]]?$")
_COLON_END_RE = re.compile(r":[\"”'»)\]]?$")
_STANDALONE_DASH_RE = re.compile(r"^[—–\-]+$")
_TRAILING_DASH_RE = re.compile(r"[—–]$")     # em / en dash at end (true dash, not hyphen)
_QUOTE_OPENERS = ("„", "“", "«", "\"")
_QUOTE_CLOSE_RE = re.compile(r"[”\"»][,.;:!?]*$")

# Sticky-word lexicons (lowercase, normalized) — words that bind FORWARD and
# must never end a line.
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
# Polish sticky words — Polish typography HARD RULE: one-letter words must
# never end a line; short prepositions/conjunctions stick forward too.
_POLISH_ONE_LETTER = {"w", "z", "i", "a", "o", "u"}
_POLISH_SHORT_FUNCTION = {
    # prepositions
    "do", "na", "za", "od", "po", "we", "ze", "ku", "nad", "pod", "bez",
    "przez", "przed", "oraz", "dla", "ponad", "spod", "znad", "między",
    "przy", "obok", "wobec",
    # conjunctions / particles
    "lub", "albo", "ani", "czy", "że", "by", "bo", "więc",
    "lecz", "gdyż", "aby", "żeby", "iż", "jako",
    # negation that should not strand the verb
    "nie",
    # copulas / light verbs that bind to their complement
    "jest", "są", "był", "była", "było", "być", "będzie", "jestem", "jesteś",
    "ma", "masz", "mam",
    # binding particles/adverbs that glue forward ("już tylko porażką")
    "już", "tylko", "jeszcze", "też", "także", "bardzo", "zbyt",
}
_POLISH_STICKY = _POLISH_ONE_LETTER | _POLISH_SHORT_FUNCTION

# Function-onset words — a new line STARTING with one of these reads as a
# natural phrase onset (the user's favourite seam: "… ludzi | z ich
# najlepszej strony", "… wartości | na czymś się opiera"). Additive
# conjunctions (i/oraz/lub…) glue their conjuncts — they don't open a line.
_FUNC_ONSET = (_POLISH_ONE_LETTER | _POLISH_SHORT_FUNCTION | {
    "kim", "czym", "który", "która", "które", "którym", "której", "których",
    "jak", "gdy", "kiedy", "gdzie",
}) - {"nie", "i", "oraz", "lub", "albo", "ani",
      "jest", "są", "był", "była", "było", "być", "będzie", "jestem", "jesteś",
      "ma", "masz", "mam", "już", "tylko", "jeszcze", "też", "także",
      "bardzo", "zbyt"}

# Backward clitics — bind to the PREVIOUS word; a line must not start with one.
_POLISH_CLITICS_BACK = {"się", "ci", "cię", "mi", "mu", "go", "je", "ją",
                        "im", "nam", "wam", "tu"}

_WORD_NORM_RE = re.compile(r"[^\w']+", re.UNICODE)


@dataclass
class SubtitleChunk:
    index: int
    text: str
    start: float                 # first word start (word-anchored until the timing pass)
    end: float                   # last word end (word-anchored until the timing pass)
    forced_start: bool = False   # first cue of a sentence
    forced_end: bool = False     # last cue of a sentence
    w2_start: float | None = None  # second word's start (Whisper-glue guard)


# Word-shape helpers ----------------------------------------------------------

def _normalize_word(word: str) -> str:
    return _WORD_NORM_RE.sub("", word).lower()


def _ends_sentence(word: str) -> bool:
    return bool(_TERMINAL_RE.search(word))


def _ends_comma(word: str) -> bool:
    return bool(_COMMA_END_RE.search(word))


def _ends_colon(word: str) -> bool:
    return bool(_COLON_END_RE.search(word))


def _is_standalone_dash(word: str) -> bool:
    return bool(_STANDALONE_DASH_RE.match(word.strip()))


def _ends_with_dash(word: str) -> bool:
    s = word.strip()
    if _is_standalone_dash(s):
        return True
    return bool(_TRAILING_DASH_RE.search(s))


def _starts_quote(word: str) -> bool:
    return word.strip().startswith(_QUOTE_OPENERS)


def _ends_quote(word: str) -> bool:
    return bool(_QUOTE_CLOSE_RE.search(word.strip()))


def _is_sticky(word: str) -> bool:
    """Words that must never be the last word of a line (bind forward).

    A word ending in punctuation is never sticky — punctuation marks a
    deliberate boundary regardless of part of speech.
    """
    s = word.strip()
    if _ends_comma(s) or _ends_sentence(s) or _ends_with_dash(s) or _ends_colon(s):
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


def _is_back_clitic(word: str) -> bool:
    """Words that bind to the PREVIOUS word — a line must not start with one."""
    return _normalize_word(word) in _POLISH_CLITICS_BACK


def _clean_word_for_display(word: str) -> str:
    word = word.strip()
    word = re.sub(r"^[*_]+|[*_]+$", "", word)   # strip markdown emphasis markers
    return re.sub(r"[.!]+$", "", word)          # drop sentence-final period/exclam (kept inside quotes)


def _chunk_text(words: list[AlignedWord]) -> str:
    return " ".join(_clean_word_for_display(w.word) for w in words)


def _card_len(words: list[AlignedWord]) -> int:
    return len(_chunk_text(words))


# Phantom-edge trimming -------------------------------------------------------

def _strip_phantom_edges(aligned: list[AlignedWord]) -> list[AlignedWord]:
    """Drop leading/trailing runs of fully-unmatched (interpolated) words.

    A run of unmatched words at the head or tail of the script has no real
    audio anchor on one side, so its timestamps are fabricated — e.g. an
    on-screen hook/title line written into the script but never spoken.
    Interior unmatched words are kept (they interpolate sensibly).
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


# Sentence segmentation --------------------------------------------------------

def _segment_sentences(words: list[AlignedWord]) -> list[list[AlignedWord]]:
    """Split the word stream into sentence units.

    A unit ends after any word carrying a terminator (. ! ?). A source
    paragraph break (force_break_before) also starts a new unit.
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


# Seam-split -------------------------------------------------------------------

def _seam_class(words: list[AlignedWord], i: int) -> int:
    """Strength of the boundary AFTER words[i-1] / BEFORE words[i].

    3 — colon end, closing-quote end, or opening quote next (quote atomicity;
        overrides the sticky rule),
    2 — comma / dash end,
    1 — audio pause >= PAUSE_GAP_S or a source paragraph break,
    0 — plain word boundary.
    -1 — forbidden (sticky word left of the seam, or clitic right of it).
    """
    prev, nxt = words[i - 1], words[i]
    quote_edge = _ends_quote(prev.word) or _starts_quote(nxt.word) or _ends_colon(prev.word)
    if not quote_edge:
        if _is_sticky(prev.word) or _is_back_clitic(nxt.word):
            return -1
    elif _is_back_clitic(nxt.word):
        return -1
    if quote_edge:
        return 3
    if _ends_comma(prev.word) or _ends_with_dash(prev.word):
        return 2
    if (nxt.start - prev.end) >= PAUSE_GAP_S or nxt.force_break_before:
        return 1
    return 0


def _seam_split(words: list[AlignedWord], max_cpl: int) -> list[list[AlignedWord]]:
    """Split an over-line sentence at its strongest seam, recursively.

    Selection mirrors the user's hand style:
      a) seams whose LEFT side fits the line — punctuation/quote seams and
         function-onset seams (next line starts with a preposition /
         conjunction / relative) — pick the one closest to a full line
         (min |left - min(right, max_cpl)|);
      b) no fitting seam: cut at the strongest punctuation seam by balance
         and recurse (the comma decides, recursion fixes the overflow);
      c) only plain boundaries: most balanced valid cut.
    A seam never strands fewer than MIN_SIDE_CHARS, never sits after a
    forward-sticky word (quote/colon seams excepted) and never before a
    backward clitic. Punctuation seams of class <= 2 also require >= 12
    chars on the left (a 7-char "Zobacz," stub is not his rhythm).
    """
    if _card_len(words) <= max_cpl or len(words) < 2:
        return [words]

    candidates: list[tuple[int, int, int, int, bool]] = []  # (cls, L, R, i, onset)
    for i in range(1, len(words)):
        cls = _seam_class(words, i)
        if cls < 0:
            continue
        left_len = _card_len(words[:i])
        right_len = _card_len(words[i:])
        if left_len < MIN_SIDE_CHARS or right_len < MIN_SIDE_CHARS:
            continue
        onset = _normalize_word(words[i].word) in _FUNC_ONSET
        candidates.append((cls, left_len, right_len, i, onset))

    if not candidates:
        # no valid seam at all — fall back to a mid split ignoring stickiness
        mid = len(words) // 2
        return [words[:mid], words[mid:]]

    def min_left(cls: int) -> int:
        return MIN_SIDE_CHARS if cls >= 3 else 12

    def rank(c) -> float:
        return c[0] if c[0] >= 1 else (0.5 if c[4] else 0.0)

    # t0) quote atomicity: the EARLIEST fitting colon/quote seam closes the
    #     narration intro / the quote card ("Ono mówi:" | "„przestań, …")
    t0 = [c for c in candidates if c[0] >= 3 and c[1] <= max_cpl]
    # t1) one cut, both sides fit: strongest seam class first, then fullest left
    t1 = [c for c in candidates
          if rank(c) > 0 and c[1] <= max_cpl and c[2] <= max_cpl
          and c[1] >= min_left(c[0]) and c[2] >= 12]
    # t2) left fits, right gets recursed: strongest class, fullest left
    t2 = [c for c in candidates
          if rank(c) > 0 and c[1] <= max_cpl
          and c[1] >= min_left(c[0]) and c[2] >= 12]
    # t3) plain cut that makes both sides fit — most balanced
    t3 = [c for c in candidates
          if c[1] <= max_cpl and c[2] <= max_cpl and c[1] >= 8 and c[2] >= 8]
    # t4) any punctuation seam, recursion fixes the overflow
    t4 = [c for c in candidates if c[0] >= 1 and c[1] >= min_left(c[0])]

    if t0:
        _, _, _, i, _ = min(t0, key=lambda c: c[1])
    elif t1:
        _, _, _, i, _ = max(t1, key=lambda c: (rank(c), c[1]))
    elif t2:
        _, _, _, i, _ = max(t2, key=lambda c: (rank(c), c[1]))
    elif t3:
        _, _, _, i, _ = min(t3, key=lambda c: abs(c[1] - c[2]))
    elif t4:
        best_cls = max(c[0] for c in t4)
        pool = [c for c in t4 if c[0] == best_cls]
        _, _, _, i, _ = min(pool, key=lambda c: abs(c[1] - c[2]))
    else:
        _, _, _, i, _ = min(candidates, key=lambda c: abs(c[1] - c[2]))

    out: list[list[AlignedWord]] = []
    for part in (words[:i], words[i:]):
        out.extend(_seam_split(part, max_cpl))
    return out


# Build + merge passes ----------------------------------------------------------

def _is_whole_quote(text: str) -> bool:
    t = text.strip()
    return t.startswith(_QUOTE_OPENERS) and bool(_QUOTE_CLOSE_RE.search(t))


def _merge_quote_pairs(chunks: list[SubtitleChunk], max_cpl: int) -> list[SubtitleChunk]:
    """Pair consecutive tiny whole-quote sentences onto one card.

    The user merges "„Rozwijaj się.” „Pracuj nad sobą.”" (0.84 s + 1.24 s) but
    keeps "„Jestem leniwy.”" (next quote runs 1.9 s) standalone.
    """
    out: list[SubtitleChunk] = []
    for c in chunks:
        if out:
            p = out[-1]
            if (
                p.forced_end and c.forced_start
                and _is_whole_quote(p.text) and _is_whole_quote(c.text)
                and (p.end - p.start) <= QUOTE_PAIR_MAX_S
                and (c.end - c.start) <= QUOTE_PAIR_MAX_S
                and (c.start - p.end) < PAUSE_GAP_S * 2
                and len(p.text) + 1 + len(c.text) <= max_cpl
            ):
                p.text = p.text + " " + c.text
                p.end = c.end
                p.forced_end = c.forced_end
                continue
        out.append(c)
    return out


def _merge_subminimum(chunks: list[SubtitleChunk], *, sentence_min: float,
                      max_cpl: int) -> list[SubtitleChunk]:
    """Absorb fragments shorter than sentence_min into a same-sentence
    neighbour (never across sentences — short standalone sentences are a
    deliberate beat in the user's style)."""
    changed = True
    while changed and len(chunks) > 1:
        changed = False
        for i, c in enumerate(chunks):
            if (c.end - c.start) >= sentence_min:
                continue
            if i > 0 and not c.forced_start:
                p = chunks[i - 1]
                if len(p.text) + 1 + len(c.text) <= max_cpl:
                    p.text = p.text + " " + c.text
                    p.end = c.end
                    p.forced_end = c.forced_end
                    chunks.pop(i)
                    changed = True
                    break
            if i < len(chunks) - 1 and not c.forced_end:
                n = chunks[i + 1]
                if len(c.text) + 1 + len(n.text) <= max_cpl:
                    n.text = c.text + " " + n.text
                    n.start = c.start
                    n.forced_start = c.forced_start
                    n.w2_start = None
                    chunks.pop(i)
                    changed = True
                    break
    return chunks


def _split_overlong_duration(word_lists: list[list[AlignedWord]],
                             max_dur: float) -> list[list[AlignedWord]]:
    """Guard: a cue spanning more than max_dur seconds splits at its biggest
    internal audio pause."""
    out: list[list[AlignedWord]] = []
    for wl in word_lists:
        if len(wl) < 2 or (wl[-1].end - wl[0].start) <= max_dur:
            out.append(wl)
            continue
        gaps = [(wl[i].start - wl[i - 1].end, i) for i in range(1, len(wl))]
        _, i = max(gaps)
        out.extend(_split_overlong_duration([wl[:i], wl[i:]], max_dur))
    return out


# Timing pass --------------------------------------------------------------------

def _apply_switch_timing(chunks: list[SubtitleChunk], *, switch_delay: float,
                         gap_clear: float, clear_linger: float,
                         lead_in: float) -> None:
    """Rewrite cue boundaries with the switch-delay model (see module docstring).

    On entry every chunk carries word-anchored times (start = first word start,
    end = last word end).
    """
    if not chunks:
        return
    anchors = [(c.start, c.end, c.w2_start) for c in chunks]

    starts = [0.0] * len(chunks)
    ends = [0.0] * len(chunks)
    starts[0] = max(0.0, anchors[0][0] - FIRST_PREROLL_S)

    for i in range(1, len(chunks)):
        a_start, _, a_w2 = anchors[i]
        prev_end = anchors[i - 1][1]
        # Whisper-glue guard: a tiny first word glued to the previous breath
        # with a long internal gap to the second word ("I … [2 s] … tu") —
        # anchor on the real phrase onset instead.
        if a_w2 is not None and (a_w2 - chunks[i].start) > 1.2 and (a_start - prev_end) < 0.3:
            first_dur = min(0.3, a_w2 - a_start)
            a_start = a_w2 - first_dur
        pause = a_start - prev_end
        if pause > gap_clear:
            starts[i] = a_start + POST_CLEAR_DELAY_S
            ends[i - 1] = min(prev_end + clear_linger, starts[i] - MIN_CLEAR_GAP_S)
        else:
            starts[i] = a_start + switch_delay
            ends[i - 1] = starts[i]
        # monotonic safety
        if starts[i] <= starts[i - 1] + 0.2:
            starts[i] = starts[i - 1] + 0.2
            if pause <= gap_clear:
                ends[i - 1] = starts[i]
        if ends[i - 1] <= starts[i - 1]:
            ends[i - 1] = starts[i - 1] + 0.1

    ends[-1] = anchors[-1][1] + clear_linger

    for c, s, e in zip(chunks, starts, ends):
        c.start = max(0.0, s - lead_in)
        c.end = max(c.start + 0.1, e - lead_in)


# Main chunk builder ----------------------------------------------------------

def build_chunks(
    aligned: list[AlignedWord],
    *,
    sentence_min: float = SENTENCE_MIN_S,
    max_dur: float = MAX_DUR_S,
    lead_in: float = LEAD_IN_S,
    gap_clear: float = GAP_CLEAR_S,
    lead_out: float = CLEAR_LINGER_S,
    switch_delay: float = SWITCH_DELAY_S,
    drop_phantom: bool = True,
) -> list[SubtitleChunk]:
    """Group aligned words into fit-first single-line subtitle cues.

    Sentence-first and fit-first: a sentence that fits one line is one card;
    over-line sentences split at the strongest seam. Timing follows the
    switch-delay model calibrated on the user's hand-timed film. See the
    module docstring.
    """
    aligned = _strip_phantom_edges(aligned) if drop_phantom else list(aligned)
    if not aligned:
        return []

    chunks: list[SubtitleChunk] = []
    for sentence in _segment_sentences(aligned):
        word_lists = _seam_split(sentence, MAX_CPL)
        word_lists = _split_overlong_duration(word_lists, max_dur)
        for j, wl in enumerate(word_lists):
            chunks.append(SubtitleChunk(
                index=0,
                text=_chunk_text(wl),
                start=wl[0].start,
                end=wl[-1].end,
                forced_start=(j == 0),
                forced_end=(j == len(word_lists) - 1),
                w2_start=wl[1].start if len(wl) > 1 else None,
            ))

    chunks = _merge_quote_pairs(chunks, MAX_CPL)
    chunks = _merge_subminimum(chunks, sentence_min=sentence_min, max_cpl=MAX_CPL)

    # quote protection: keep an opening quote with its content
    i = 0
    while i < len(chunks) - 1:
        cur = chunks[i]
        nxt = chunks[i + 1]
        # straight quotes are ambiguous (opener == closer) — guard typographic pairs only
        if cur.text.count("„") > cur.text.count("”"):
            combined = cur.text + " " + nxt.text
            if len(combined) <= MAX_CPL:
                cur.text = combined
                cur.end = nxt.end
                cur.forced_end = nxt.forced_end
                chunks.pop(i + 1)
                continue
        i += 1

    for idx, chunk in enumerate(chunks, 1):
        chunk.index = idx

    _apply_switch_timing(chunks, switch_delay=switch_delay, gap_clear=gap_clear,
                         clear_linger=lead_out, lead_in=lead_in)
    return chunks


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
