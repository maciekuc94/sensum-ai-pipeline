"""
Agent 7 — TTS Voice Reference Generator

Generates audio reference files from 04_script_narration.md to check
pronunciation and pacing before recording your own voiceover.

Default: generates only the preferred voice (Gemini Flash TTS — Puck).
Use --all to generate all 3 voices for A/B comparison on a new video.

Audio tags injected automatically for pacing and expressiveness:
  [short pause]   — after em-dashes and colons mid-sentence
  [medium pause]  — after rhetorical questions
  [long pause]    — between paragraphs
  [sigh]          — before empathy/struggle phrases (sparingly)

Output: outputs/{slug}/tts/

Usage:
    python tools/agent7_tts.py <slug>          # default voice only
    python tools/agent7_tts.py <slug> --all    # all 3 voices for A/B
"""

import argparse
import base64
import io
import os
import re
import sys
import wave
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import get_env, read_output

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GEMINI_VOICES = ["Puck", "Kore", "Charon"]
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"

# `GEMINI_TTS_MODEL` was authored speculatively — Gemini has no 3.1 family per docs.
# Set MODEL_VERIFIED = True once you've confirmed the current Flash TTS preview model
# name against Vertex docs (e.g. `gcloud ai models list` or the Vertex console) and
# updated `GEMINI_TTS_MODEL` above. Until then, main() refuses to run to avoid 404s.
MODEL_VERIFIED = False

DEFAULT_VOICE = "Puck"          # chosen after A/B comparison — use --all to re-compare

SAMPLE_RATE = 24000
GEMINI_MAX_CHUNK_CHARS = 1000   # Gemini is generative — long inputs cause voice drift/silence

# Phrases that warrant a [sigh] before them — empathy/struggle moments common in psychology scripts
_SIGH_TRIGGERS = [
    "struggle", "suffering", "pain", "loneliness", "anxiety", "depression",
    "feel trapped", "feel alone", "feel broken", "feel worthless",
]


# ---------------------------------------------------------------------------
# Audio tag preprocessing
# ---------------------------------------------------------------------------

def _inject_audio_tags(text: str) -> str:
    """
    Insert Gemini TTS audio tags into narration text for pacing and expressiveness.

    Rules tuned for psychology YouTube narration:
    - [short pause]  after em-dashes and mid-sentence colons
    - [medium pause] after rhetorical questions (? at sentence end)
    - [long pause]   between paragraphs (paragraph separator)
    - [sigh]         before sentences containing empathy/struggle phrases
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    processed: list[str] = []

    for para in paragraphs:
        # [sigh] before paragraphs that open with struggle/empathy language
        first_sentence_lower = para[:120].lower()
        if any(trigger in first_sentence_lower for trigger in _SIGH_TRIGGERS):
            para = "[sigh] " + para

        # [short pause] after em-dashes
        para = re.sub(r"—\s*", "— [short pause] ", para)

        # [short pause] after mid-sentence colons (not at end of line)
        para = re.sub(r":\s+(?=[a-z])", ": [short pause] ", para)

        # [medium pause] after rhetorical questions
        para = re.sub(r"\?\s+", "? [medium pause] ", para)

        processed.append(para)

    # [long pause] between paragraphs
    return "\n\n[long pause]\n\n".join(processed)


# ---------------------------------------------------------------------------
# Text splitting
# ---------------------------------------------------------------------------

def split_chunks(text: str, max_chars: int = GEMINI_MAX_CHUNK_CHARS) -> list[str]:
    """Split at paragraph boundaries into chunks of at most max_chars each."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in paragraphs:
        if current and current_len + len(para) + 2 > max_chars:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para) + 2

    if current:
        chunks.append("\n\n".join(current))

    return chunks or [text]


# ---------------------------------------------------------------------------
# WAV helpers
# ---------------------------------------------------------------------------

def _extract_pcm(wav_bytes: bytes) -> bytes:
    """Strip the WAV header and return raw PCM frames."""
    with wave.open(io.BytesIO(wav_bytes)) as wf:
        return wf.readframes(wf.getnframes())


def _write_wav(path: Path, pcm_frames: bytes) -> None:
    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm_frames)


def _ensure_pcm(data: bytes) -> bytes:
    """Extract raw PCM from data that may be WAV-wrapped or bare PCM.

    Only `wave.Error` and `EOFError` are treated as "not a WAV, treat as raw PCM" —
    anything else (e.g. a JSON error payload from the API surfacing as a UnicodeDecodeError
    inside the wave module) propagates so we never write garbage to a .wav.
    """
    try:
        return _extract_pcm(data)
    except (wave.Error, EOFError):
        return data


def _rms_normalize(pcm: bytes, target_rms: float = 6000.0) -> bytes:
    """RMS-normalize 16-bit mono PCM so all chunks have consistent loudness."""
    import array as _array
    samples = _array.array('h', pcm)
    if len(samples) < 100:
        return pcm
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    if rms < 10:
        return pcm
    scale = min(target_rms / rms, 6.0)
    normalized = _array.array('h', (max(-32768, min(32767, int(s * scale))) for s in samples))
    return normalized.tobytes()


# ---------------------------------------------------------------------------
# Gemini Flash TTS
# ---------------------------------------------------------------------------

def _make_client():
    import google.genai as genai
    project = get_env("GOOGLE_CLOUD_PROJECT")
    client = genai.Client(vertexai=True, project=project, location="global")
    return genai, client


def _synth_voice_to_file(voice_name: str, chunks: list[str], out_dir: Path, client, types) -> bool:
    """Synthesize one voice's audio across all chunks and write a single .wav. Returns success."""
    out_path = out_dir / f"gemini_{voice_name}.wav"
    print(f"  {voice_name:<8} ({len(chunks)} chunks)", end=" ", flush=True)
    try:
        pcm_parts: list[bytes] = []
        for chunk in chunks:
            resp = client.models.generate_content(
                model=GEMINI_TTS_MODEL,
                contents=chunk,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice_name
                            )
                        )
                    ),
                ),
            )
            raw = resp.candidates[0].content.parts[0].inline_data.data
            if isinstance(raw, str):
                raw = base64.b64decode(raw)
            pcm_parts.append(_rms_normalize(_ensure_pcm(raw)))

        _write_wav(out_path, b"".join(pcm_parts))
        size_kb = out_path.stat().st_size // 1024
        print(f"OK ({size_kb} KB)")
        return True
    except Exception as exc:
        print(f"FAIL  {exc}")
        return False


def synthesize_voices(text: str, out_dir: Path, voices: list[str]) -> float:
    """Synthesize each named voice from text. Returns estimated cost in USD."""
    label = f"all {len(voices)} voices" if len(voices) > 1 else f"{voices[0]} (default voice)"
    print(f"[1/1] Gemini Flash TTS — {label}...")
    try:
        _genai, client = _make_client()
        from google.genai import types
    except ImportError:
        print("  [SKIP] google-genai not installed.")
        return 0.0
    except Exception as exc:
        print(f"  [ERROR] Client init failed: {exc}")
        return 0.0

    tagged = _inject_audio_tags(text)
    chunks = split_chunks(tagged, max_chars=GEMINI_MAX_CHUNK_CHARS)

    for voice in voices:
        _synth_voice_to_file(voice, chunks, out_dir, client, types)

    # Cost model: $10 per 1M chars × number of voices synthesized.
    return round((len(text) / 1_000_000) * 10.0 * len(voices), 4)


# Backward-compatible wrappers (older imports may reference these names).
def generate_gemini_voices(text: str, out_dir: Path) -> float:
    return synthesize_voices(text, out_dir, GEMINI_VOICES)


def generate_default_voice(text: str, out_dir: Path) -> float:
    return synthesize_voices(text, out_dir, [DEFAULT_VOICE])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agent 7: Generate TTS voice reference audio from 06_script_narration.md.",
    )
    parser.add_argument("slug", help="Output slug for outputs/<slug>/.")
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"Generate all {len(GEMINI_VOICES)} voices for A/B comparison. Default: only {DEFAULT_VOICE}.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    if not MODEL_VERIFIED:
        print(
            "Agent 7 disabled pending TTS model verification — see CLAUDE.md note.\n"
            f"  Current GEMINI_TTS_MODEL = {GEMINI_TTS_MODEL!r}\n"
            "  Verify the model name against Vertex AI docs, then set\n"
            "  MODEL_VERIFIED = True in tools/agent7_tts.py to re-enable."
        )
        sys.exit(1)

    voices = GEMINI_VOICES if args.all else [DEFAULT_VOICE]
    print(f"\n=== Agent 7: TTS Voice Reference ===")
    print(f"Slug : {slug}")
    print(f"Mode : {'all 3 Gemini voices' if args.all else f'default only (gemini_{DEFAULT_VOICE})'}")

    try:
        raw = read_output(slug, "md/06_script_narration.md")
    except FileNotFoundError:
        print(f"Error: outputs/{slug}/md/06_script_narration.md not found.")
        print("Run agent6_narration.py first.")
        sys.exit(1)

    # Strip markdown headers and separators for clean TTS input
    text = "\n".join(
        line for line in raw.splitlines()
        if not line.startswith("#") and line.strip() != "---"
    ).strip()

    print(f"Words: {len(text.split()):,}   Chars: {len(text):,}")

    out_dir = Path(__file__).parent.parent / "outputs" / slug / "tts"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Out  : {out_dir}\n")

    total_cost = synthesize_voices(text, out_dir, voices)

    files = sorted(out_dir.glob("*.wav"))
    print(f"\nDone — {len(files)} file(s) in {out_dir}")
    for f in files:
        print(f"  {f.name:<35}  {f.stat().st_size // 1024:>5} KB")
    print(f"Estimated cost: ~${total_cost:.2f}")
    print(f"\nListen and use as reference, then record in DaVinci Resolve.")


if __name__ == "__main__":
    main()
