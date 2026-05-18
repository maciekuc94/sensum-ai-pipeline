"""Tests for tools.agent7_tts — audio tag injection and chunk splitting."""
import pytest


def test_inject_audio_tags_em_dash_becomes_short_pause():
    from tools.agent7_tts import _inject_audio_tags
    result = _inject_audio_tags("She arrived — late as always.")
    assert "[short pause]" in result
    assert "—" in result  # original em-dash preserved


def test_inject_audio_tags_question_mark_becomes_medium_pause():
    from tools.agent7_tts import _inject_audio_tags
    result = _inject_audio_tags("Why now? The answer comes later.")
    assert "[medium pause]" in result


def test_inject_audio_tags_mid_sentence_colon_pause():
    from tools.agent7_tts import _inject_audio_tags
    result = _inject_audio_tags("Here is the truth: pain demands attention.")
    assert "[short pause]" in result


def test_inject_audio_tags_sigh_trigger_at_paragraph_start():
    from tools.agent7_tts import _inject_audio_tags
    result = _inject_audio_tags("This is about loneliness and what it does.")
    assert result.startswith("[sigh]")


def test_inject_audio_tags_no_sigh_when_no_trigger():
    from tools.agent7_tts import _inject_audio_tags
    result = _inject_audio_tags("A perfectly neutral statement about weather.")
    assert "[sigh]" not in result


def test_inject_audio_tags_paragraphs_separated_by_long_pause():
    from tools.agent7_tts import _inject_audio_tags
    text = "First paragraph.\n\nSecond paragraph."
    result = _inject_audio_tags(text)
    assert "[long pause]" in result


def test_split_chunks_respects_max_chars():
    from tools.agent7_tts import split_chunks
    paragraphs = "\n\n".join(["abc" * 100] * 10)  # 10 paragraphs ~300 chars each
    chunks = split_chunks(paragraphs, max_chars=500)
    assert all(len(c) <= 600 for c in chunks)  # allow some slack for paragraph boundaries
    assert len(chunks) > 1


def test_split_chunks_single_paragraph_under_limit():
    from tools.agent7_tts import split_chunks
    chunks = split_chunks("short text", max_chars=1000)
    assert chunks == ["short text"]


def test_split_chunks_empty_input_returns_original():
    from tools.agent7_tts import split_chunks
    chunks = split_chunks("", max_chars=1000)
    assert chunks == [""]


def test_split_chunks_default_under_gemini_limit():
    """Default max_chars must not exceed GEMINI_MAX_CHUNK_CHARS."""
    from tools.agent7_tts import split_chunks, GEMINI_MAX_CHUNK_CHARS
    # Build text well over the limit.
    para = "x" * 300
    text = "\n\n".join([para] * 20)
    chunks = split_chunks(text)
    # No chunk should be wildly over the limit (paragraph boundary may push slightly over).
    for c in chunks:
        assert len(c) <= GEMINI_MAX_CHUNK_CHARS + len(para)


def test_ensure_pcm_passes_through_non_wav():
    """Raw PCM bytes (not WAV-wrapped) should be returned as-is."""
    from tools.agent7_tts import _ensure_pcm
    raw = b"\x00\x01\x02\x03\x04\x05"
    assert _ensure_pcm(raw) == raw
