# Subtitle Automation Design

**Date:** 2026-05-09  
**Status:** Approved

## Context

The current subtitle workflow requires manually copying script text into individual DaVinci Resolve title clips — tedious and error-prone at scale. The voiceover is already recorded (~12 minutes), so timing can be derived automatically from the audio via speech-to-text. The goal is a single command that produces a ready-to-import SRT file with accurate timestamps, leaving font/styling as a one-time DaVinci setting.

## Approach

**Option A selected:** Transcribe audio → SRT file → import into DaVinci Resolve subtitle track.

Uses Google Cloud Speech-to-Text (already configured in the project) with async processing via Google Cloud Storage for long audio files. SRT import into DaVinci lets the user set Lora font once in the inspector and it applies to all subtitles.

## Components

### New tool: `tools/transcribe_audio.py`

**Input:** Audio file path (CLI argument)  
**Output:** `.tmp/subtitles.srt`

**Steps:**
1. Read `GCS_BUCKET_NAME` from `.env`; auto-create the bucket on first run if it doesn't exist
2. Upload audio file to GCS bucket
3. Submit async Speech-to-Text job with `enable_word_time_offsets: True`, language `en-US` (overridable via `SPEECH_LANGUAGE_CODE` in `.env`)
4. Poll until job completes (~1-2 min for 12-min audio), print progress
5. Group transcript words into subtitle chunks: max 8 words OR max 4 seconds per chunk, whichever comes first
6. Write `.tmp/subtitles.srt` in standard SRT format
7. Delete audio file from GCS (cleanup)

**Usage:**
```
python tools/transcribe_audio.py .tmp/voiceover.wav
```

Supported formats: WAV (recommended for accuracy), MP3, FLAC.

### `.env` additions

```
GCS_BUCKET_NAME=youtube-psychology-audio
SPEECH_LANGUAGE_CODE=en-US   # optional, defaults to en-US
```

### New workflow: `workflows/07_subtitles.md`

Documents the full process end-to-end:
- Export audio from DaVinci Resolve (WAV recommended)
- Run `transcribe_audio.py`
- Import `.tmp/subtitles.srt` into DaVinci (File > Import > Subtitles, or drag-drop)
- Set Lora font once in the subtitle inspector (applies to all subtitles)
- Adjust size, color, position as needed

## Data Flow

```
voiceover.wav (.tmp/)
    → GCS upload
    → Speech-to-Text async job
    → word timestamps
    → chunked into SRT blocks (≤8 words, ≤4s)
    → subtitles.srt (.tmp/)
    → DaVinci Resolve subtitle track
    → Lora font set once in inspector
```

## Dependencies

- `google-cloud-speech` Python package
- `google-cloud-storage` Python package
- Existing Google Cloud project credentials (`credentials.json` / `token.json` or service account)

## Verification

1. Export a short audio clip (~1 min) from DaVinci as WAV to `.tmp/test.wav`
2. Run `python tools/transcribe_audio.py .tmp/test.wav`
3. Confirm `.tmp/subtitles.srt` is created with correct format and reasonable chunk sizes
4. Import SRT into DaVinci Resolve, verify subtitles appear on timeline with correct timing
5. Set Lora font in subtitle inspector, confirm it applies to all subtitle entries
6. Run full 12-minute voiceover through the tool, verify timing accuracy
