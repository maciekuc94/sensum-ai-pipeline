"""Forced alignment between recorded voiceover audio and the canonical script.

Strategy:
  1. Transcribe the voiceover WAV with faster-whisper (word-level timestamps).
  2. Tokenize the canonical script (script_corrected.docx / script.docx / 04_final.md) into ordered words.
  3. Greedy align Whisper words to script words with a lookahead window
     (works well because reading is word-for-word).
  4. Interpolate timestamps for any unmatched script words from their neighbors.

The output is a list of AlignedWord — one per script token in order — that
downstream modules (phrase_mapper, subtitle_chunker) consume.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from pathlib import Path

from faster_whisper import WhisperModel


@dataclass
class AlignedWord:
    """A script word with its timestamp in the audio."""

    index: int       # 0-based position in the script
    word: str        # canonical script word (with punctuation preserved)
    start: float     # seconds
    end: float       # seconds
    matched: bool    # True if directly matched to a Whisper word; False if interpolated
    force_break_before: bool = False   # token was preceded by a newline in the source script


_WORD_SPLIT_RE = re.compile(r"\S+")
_NORM_RE = re.compile(r"[^\w']+", re.UNICODE)


def _normalize(word: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    return _NORM_RE.sub("", word).lower()


_SKIP_LINE_RE = re.compile(
    r"^\s*("
    r"[A-Z][A-Z ]+:.*"       # metadata lines like "ARCHITECTURE: Systems Audit"
    r"|"
    r"\[.*?\]"               # stage directions like "[Visual Pause]"
    r")\s*$"
)


def _extract_narration_body(md_text: str) -> str:
    """Skip the header block and non-spoken lines (metadata, stage directions)."""
    parts = md_text.split("\n---", 1)
    body = parts[1] if len(parts) == 2 else md_text
    filtered = [l for l in body.splitlines() if not _SKIP_LINE_RE.match(l)]
    return "\n".join(filtered)


def read_script_docx(docx_path: Path) -> str:
    """Read a narration script from a .docx file and return it as plain text.

    Skips Heading-styled paragraphs (title, subheadings). Joins remaining
    paragraphs with newlines so paragraph breaks are preserved for the
    force_break_before detection downstream.
    """
    from docx import Document  # lazy import — only needed when reading docx
    doc = Document(str(docx_path))
    lines: list[str] = []
    for p in doc.paragraphs:
        if p.style is not None and p.style.name and p.style.name.startswith("Heading"):
            continue
        lines.append(p.text)
    return "\n".join(lines)


def tokenize_script(script_text: str) -> list[tuple[str, bool]]:
    """Tokenize narration into (word, force_break_before) tuples.

    `force_break_before` is True when a newline character separates the token
    from its predecessor — i.e. a line / paragraph boundary in the source script.
    The first token always has `force_break_before=False`.
    """
    body = _extract_narration_body(script_text)
    tokens: list[tuple[str, bool]] = []
    last_end = 0
    for m in _WORD_SPLIT_RE.finditer(body):
        gap = body[last_end:m.start()]
        force_break = bool(tokens) and "\n" in gap
        tokens.append((m.group(0), force_break))
        last_end = m.end()
    return tokens


def transcribe_audio(
    audio_path: Path,
    model_size: str = "large-v3",
    language: str = "en",
    device: str = "cpu",
    compute_type: str = "int8",
) -> list[dict]:
    """Run faster-whisper on the audio and return word-level entries."""
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, _info = model.transcribe(
        str(audio_path),
        language=language,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    words: list[dict] = []
    for segment in segments:
        for w in (segment.words or []):
            words.append(
                {
                    "word": w.word.strip(),
                    "start": float(w.start),
                    "end": float(w.end),
                }
            )
    return words


def _greedy_align(
    script_tokens: list[str],
    whisper_tokens: list[dict],
    window: int = 10,
) -> list[tuple[int, int | None]]:
    """Walk both sequences in order, looking ahead `window` Whisper tokens for a match.

    Kept for reference / fallback. Production path uses `_dp_align`, which is robust
    to Whisper insertions/deletions that throw a pure greedy walker out of sync.
    """
    script_norm = [_normalize(t) for t in script_tokens]
    whisper_norm = [_normalize(t["word"]) for t in whisper_tokens]

    pairs: list[tuple[int, int | None]] = []
    j = 0
    for i, script_w in enumerate(script_norm):
        if not script_w:
            pairs.append((i, None))
            continue
        match_idx: int | None = None
        upper = min(j + window, len(whisper_norm))
        for k in range(j, upper):
            if whisper_norm[k] == script_w:
                match_idx = k
                break
        if match_idx is not None:
            pairs.append((i, match_idx))
            j = match_idx + 1
        else:
            pairs.append((i, None))
    return pairs


def _dp_align(
    script_tokens: list[str],
    whisper_tokens: list[dict],
    match_score: int = 2,
    gap_penalty: int = -1,
    mismatch_penalty: int = -2,
) -> list[tuple[int, int | None]]:
    """Global Needleman-Wunsch-style alignment.

    Finds the optimal alignment that maximizes script-word → whisper-word matches
    across the whole sequence. Resilient to local Whisper transcription errors:
    a misheard word or an inserted/dropped word does not knock subsequent words
    out of sync (which is what kills the greedy walker on long voiceovers).

    Returns one (script_idx, whisper_idx | None) tuple per script token, in order.
    """
    script_norm = [_normalize(t) for t in script_tokens]
    whisper_norm = [_normalize(t["word"]) for t in whisper_tokens]
    n = len(script_norm)
    m = len(whisper_norm)

    # DP matrix: dp[i][j] = best score aligning script[:i] against whisper[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + gap_penalty
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + gap_penalty

    for i in range(1, n + 1):
        s = script_norm[i - 1]
        row = dp[i]
        prev_row = dp[i - 1]
        for j in range(1, m + 1):
            if s and s == whisper_norm[j - 1]:
                diag = prev_row[j - 1] + match_score
            else:
                diag = prev_row[j - 1] + mismatch_penalty
            up = prev_row[j] + gap_penalty       # skip script word (no whisper consumed)
            left = row[j - 1] + gap_penalty      # skip whisper word (no script consumed)
            best = diag
            if up > best:
                best = up
            if left > best:
                best = left
            row[j] = best

    # Traceback to recover the alignment
    pairs_rev: list[tuple[int, int | None]] = []
    i, j = n, m
    while i > 0 and j > 0:
        s = script_norm[i - 1]
        w = whisper_norm[j - 1]
        diag = dp[i - 1][j - 1] + (match_score if s and s == w else mismatch_penalty)
        up = dp[i - 1][j] + gap_penalty
        left = dp[i][j - 1] + gap_penalty
        if dp[i][j] == diag:
            # Only count as a match if the words actually equal — otherwise it's a paired mismatch
            if s and s == w:
                pairs_rev.append((i - 1, j - 1))
            else:
                pairs_rev.append((i - 1, None))
            i -= 1
            j -= 1
        elif dp[i][j] == up:
            pairs_rev.append((i - 1, None))
            i -= 1
        else:  # left
            j -= 1
    while i > 0:
        pairs_rev.append((i - 1, None))
        i -= 1

    pairs_rev.reverse()
    return pairs_rev


def _interpolate_unmatched(aligned: list[AlignedWord], audio_duration: float) -> list[AlignedWord]:
    """Fill timestamps for unmatched words by interpolating between neighbors."""
    result = list(aligned)
    n = len(result)
    i = 0
    while i < n:
        if not result[i].matched:
            j = i
            while j < n and not result[j].matched:
                j += 1
            prev_end = result[i - 1].end if i > 0 else 0.0
            next_start = result[j].start if j < n else audio_duration
            span = max(next_start - prev_end, 0.001)
            count = j - i
            step = span / (count + 1)
            for k in range(count):
                start = prev_end + step * k
                end = prev_end + step * (k + 1)
                result[i + k] = AlignedWord(
                    index=result[i + k].index,
                    word=result[i + k].word,
                    start=start,
                    end=end,
                    matched=False,
                    force_break_before=result[i + k].force_break_before,
                )
            i = j
        else:
            i += 1
    return result


def align_script_to_audio(
    audio_path: Path,
    script_md_text: str,
    model_size: str = "large-v3",
    language: str = "en",
    device: str = "cpu",
    compute_type: str = "int8",
    window: int = 10,
    whisper_tokens: list[dict] | None = None,
) -> tuple[list[AlignedWord], dict]:
    """Run forced alignment and return (aligned_words, stats).

    If `whisper_tokens` is provided, skips Whisper and uses those tokens directly
    — useful for iterating on the alignment algorithm without re-transcribing.
    """
    script_pairs = tokenize_script(script_md_text)
    if not script_pairs:
        raise ValueError("Script is empty after tokenization.")
    script_words = [w for w, _ in script_pairs]
    force_breaks = [fb for _, fb in script_pairs]

    if whisper_tokens is None:
        whisper_tokens = transcribe_audio(
            audio_path,
            model_size=model_size,
            language=language,
            device=device,
            compute_type=compute_type,
        )
    if not whisper_tokens:
        raise ValueError("Whisper produced no words from the audio.")

    pairs = _dp_align(script_words, whisper_tokens)
    # `window` arg retained for CLI compatibility; greedy fallback is no longer used.
    _ = window

    aligned: list[AlignedWord] = []
    for script_idx, whisper_idx in pairs:
        if whisper_idx is None:
            aligned.append(
                AlignedWord(
                    index=script_idx,
                    word=script_words[script_idx],
                    start=0.0,
                    end=0.0,
                    matched=False,
                    force_break_before=force_breaks[script_idx],
                )
            )
        else:
            w = whisper_tokens[whisper_idx]
            aligned.append(
                AlignedWord(
                    index=script_idx,
                    word=script_words[script_idx],
                    start=w["start"],
                    end=w["end"],
                    matched=True,
                    force_break_before=force_breaks[script_idx],
                )
            )

    audio_duration = whisper_tokens[-1]["end"] if whisper_tokens else 0.0
    aligned = _interpolate_unmatched(aligned, audio_duration)

    matched_count = sum(1 for w in aligned if w.matched)
    stats = {
        "script_words": len(script_words),
        "whisper_words": len(whisper_tokens),
        "matched": matched_count,
        "interpolated": len(aligned) - matched_count,
        "match_rate": matched_count / len(aligned) if aligned else 0.0,
        "audio_duration_s": audio_duration,
    }
    return aligned, stats


def aligned_to_dict(aligned: list[AlignedWord]) -> list[dict]:
    """Serialize for JSON output."""
    return [asdict(w) for w in aligned]
