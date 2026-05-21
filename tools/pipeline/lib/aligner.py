"""Forced alignment between recorded voiceover audio and the canonical script.

Strategy:
  1. Transcribe the voiceover WAV with faster-whisper (word-level timestamps).
  2. Tokenize the canonical script (06_script_narration.md) into ordered words.
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


_WORD_SPLIT_RE = re.compile(r"\S+")
_NORM_RE = re.compile(r"[^\w']+", re.UNICODE)


def _normalize(word: str) -> str:
    """Lowercase and strip punctuation for comparison."""
    return _NORM_RE.sub("", word).lower()


_SKIP_LINE_RE = re.compile(
    r"^\s*("
    r"[A-Z][A-Z ]+:\s*\S"   # metadata lines like "ARCHITECTURE: Historical Reversal"
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


def tokenize_script(script_text: str) -> list[str]:
    """Split narration markdown into an ordered list of word tokens."""
    body = _extract_narration_body(script_text)
    return _WORD_SPLIT_RE.findall(body)


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
    """Walk both sequences in order, looking ahead `window` Whisper tokens for a match."""
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
) -> tuple[list[AlignedWord], dict]:
    """Run forced alignment and return (aligned_words, stats)."""
    script_tokens = tokenize_script(script_md_text)
    if not script_tokens:
        raise ValueError("Script is empty after tokenization.")

    whisper_tokens = transcribe_audio(
        audio_path,
        model_size=model_size,
        language=language,
        device=device,
        compute_type=compute_type,
    )
    if not whisper_tokens:
        raise ValueError("Whisper produced no words from the audio.")

    pairs = _greedy_align(script_tokens, whisper_tokens, window=window)

    aligned: list[AlignedWord] = []
    for script_idx, whisper_idx in pairs:
        if whisper_idx is None:
            aligned.append(
                AlignedWord(
                    index=script_idx,
                    word=script_tokens[script_idx],
                    start=0.0,
                    end=0.0,
                    matched=False,
                )
            )
        else:
            w = whisper_tokens[whisper_idx]
            aligned.append(
                AlignedWord(
                    index=script_idx,
                    word=script_tokens[script_idx],
                    start=w["start"],
                    end=w["end"],
                    matched=True,
                )
            )

    audio_duration = whisper_tokens[-1]["end"] if whisper_tokens else 0.0
    aligned = _interpolate_unmatched(aligned, audio_duration)

    matched_count = sum(1 for w in aligned if w.matched)
    stats = {
        "script_words": len(script_tokens),
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
