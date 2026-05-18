# Subtitle Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tools/transcribe_audio.py` that transcribes a recorded voiceover using Google Cloud Speech-to-Text and outputs `.tmp/subtitles.srt` ready to import into DaVinci Resolve.

**Architecture:** Upload audio to GCS → async Speech-to-Text with word-level timestamps → chunk words into subtitle blocks (≤8 words or ≤4 seconds) → write SRT file. User imports SRT into DaVinci Resolve and sets Lora font once in the inspector (applies to all subtitles).

**Tech Stack:** `google-cloud-speech`, `google-cloud-storage`, `wave` (stdlib), `python-dotenv` (already installed via `utils.py`)

---

## File Map

| File | Action | Responsibility |
|------|--------|----------------|
| `tools/transcribe_audio.py` | Create | GCS upload, Speech-to-Text, SRT generation, CLI entry point |
| `tests/__init__.py` | Create | Makes `tests/` a package so pytest discovers it |
| `tests/test_transcribe_audio.py` | Create | Unit tests for pure functions and mocked API calls |
| `workflows/07_subtitles.md` | Create | End-to-end workflow documentation |
| `.env` | Modify | Add `GCS_BUCKET_NAME` |

---

### Task 1: Install Dependencies and Configure .env

**Files:**
- Modify: `.env`

- [ ] **Step 1: Install Google Cloud packages**

Run from the project root:
```
pip install google-cloud-speech google-cloud-storage
```
Expected: both packages install without errors.

- [ ] **Step 2: Add GCS_BUCKET_NAME to .env**

Open `.env` and add this line (the name must be globally unique across all of Google Cloud — add a random suffix if needed):
```
GCS_BUCKET_NAME=youtube-psychology-audio
```

- [ ] **Step 3: Verify Application Default Credentials are active**

Run:
```
gcloud auth application-default print-access-token
```
Expected: prints a long token string. If it says "not logged in", run `gcloud auth application-default login` first and follow the browser prompt.

- [ ] **Step 4: Create tests directory**

Run:
```
mkdir tests
```
Create `tests/__init__.py` as an empty file.

- [ ] **Step 5: Commit**

```bash
git add .env tests/__init__.py
git commit -m "config: add GCS_BUCKET_NAME and tests directory for subtitle automation"
```

---

### Task 2: SRT Generation Utilities (Pure Functions)

**Files:**
- Create: `tools/transcribe_audio.py` (skeleton + pure functions only)
- Create: `tests/test_transcribe_audio.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_transcribe_audio.py`:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.transcribe_audio import chunk_words, format_timestamp, format_srt

SAMPLE_WORDS = [
    {"word": "The",       "start": 0.0, "end": 0.3},
    {"word": "human",     "start": 0.3, "end": 0.7},
    {"word": "brain",     "start": 0.7, "end": 1.0},
    {"word": "is",        "start": 1.0, "end": 1.2},
    {"word": "remarkable","start": 1.2, "end": 1.8},
    {"word": "in",        "start": 1.8, "end": 2.0},
    {"word": "many",      "start": 2.0, "end": 2.3},
    {"word": "ways",      "start": 2.3, "end": 2.6},
    {"word": "that",      "start": 2.6, "end": 2.8},
    {"word": "science",   "start": 2.8, "end": 3.2},
    {"word": "is",        "start": 3.2, "end": 3.4},
    {"word": "still",     "start": 3.4, "end": 3.7},
    {"word": "exploring", "start": 3.7, "end": 4.2},
]


def test_chunk_words_respects_max_words():
    chunks = chunk_words(SAMPLE_WORDS, max_words=8, max_seconds=100.0)
    assert all(len(c) <= 8 for c in chunks)
    assert sum(len(c) for c in chunks) == len(SAMPLE_WORDS)


def test_chunk_words_respects_max_seconds():
    chunks = chunk_words(SAMPLE_WORDS, max_words=100, max_seconds=2.0)
    for chunk in chunks:
        duration = chunk[-1]["end"] - chunk[0]["start"]
        assert duration <= 2.0


def test_chunk_words_empty():
    assert chunk_words([]) == []


def test_format_timestamp_zero():
    assert format_timestamp(0.0) == "00:00:00,000"


def test_format_timestamp_hours():
    assert format_timestamp(3661.5) == "01:01:01,500"


def test_format_timestamp_minutes():
    assert format_timestamp(90.123) == "00:01:30,123"


def test_format_srt_structure():
    words = [
        {"word": "Hello", "start": 1.0, "end": 1.5},
        {"word": "world", "start": 1.5, "end": 2.0},
    ]
    srt = format_srt(chunk_words(words))
    assert "1\n" in srt
    assert "00:00:01,000 --> 00:00:02,000" in srt
    assert "Hello world" in srt
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_transcribe_audio.py -v`
Expected: `ImportError` — `transcribe_audio` module does not exist yet.

- [ ] **Step 3: Create tools/transcribe_audio.py with pure functions**

Create `tools/transcribe_audio.py`:
```python
import sys
import os
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import get_env


def chunk_words(words, max_words=8, max_seconds=4.0):
    if not words:
        return []
    chunks = []
    current = []
    for word in words:
        if current:
            duration = word["end"] - current[0]["start"]
            if len(current) >= max_words or duration > max_seconds:
                chunks.append(current)
                current = []
        current.append(word)
    if current:
        chunks.append(current)
    return chunks


def format_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int(round((seconds % 1) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def format_srt(chunks):
    blocks = []
    for i, chunk in enumerate(chunks, 1):
        start = format_timestamp(chunk[0]["start"])
        end = format_timestamp(chunk[-1]["end"])
        text = " ".join(w["word"] for w in chunk)
        blocks.append(f"{i}\n{start} --> {end}\n{text}")
    return "\n\n".join(blocks) + "\n"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_transcribe_audio.py -v`
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/transcribe_audio.py tests/test_transcribe_audio.py
git commit -m "feat: add SRT generation utilities for subtitle automation"
```

---

### Task 3: GCS Upload Functions

**Files:**
- Modify: `tools/transcribe_audio.py` (add 3 GCS functions after `format_srt`)
- Modify: `tests/test_transcribe_audio.py` (add 4 GCS tests)

- [ ] **Step 1: Write failing tests**

Add to the bottom of `tests/test_transcribe_audio.py`:
```python
from unittest.mock import MagicMock
from tools.transcribe_audio import ensure_bucket_exists, upload_audio, delete_audio


def test_ensure_bucket_creates_if_missing():
    client = MagicMock()
    client.get_bucket.side_effect = Exception("Not found")
    ensure_bucket_exists(client, "my-bucket", "my-project", "us-central1")
    client.create_bucket.assert_called_once()


def test_ensure_bucket_skips_if_present():
    client = MagicMock()
    client.get_bucket.return_value = MagicMock()
    ensure_bucket_exists(client, "my-bucket", "my-project", "us-central1")
    client.create_bucket.assert_not_called()


def test_upload_audio_returns_gcs_uri(tmp_path):
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(b"fake audio")
    client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob

    gcs_uri, blob_name = upload_audio(client, "my-bucket", audio_file)

    assert gcs_uri == f"gs://my-bucket/{blob_name}"
    blob.upload_from_filename.assert_called_once_with(str(audio_file))


def test_delete_audio_removes_blob():
    client = MagicMock()
    bucket = MagicMock()
    blob = MagicMock()
    client.bucket.return_value = bucket
    bucket.blob.return_value = blob

    delete_audio(client, "my-bucket", "audio/test.wav")

    blob.delete.assert_called_once()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_transcribe_audio.py::test_ensure_bucket_creates_if_missing -v`
Expected: `ImportError` — `ensure_bucket_exists` not defined yet.

- [ ] **Step 3: Add GCS functions to tools/transcribe_audio.py**

Add after the `format_srt` function:
```python
def ensure_bucket_exists(storage_client, bucket_name, project, location):
    try:
        storage_client.get_bucket(bucket_name)
    except Exception:
        bucket = storage_client.bucket(bucket_name)
        bucket.storage_class = "STANDARD"
        storage_client.create_bucket(bucket, project=project, location=location)
        print(f"Created GCS bucket: {bucket_name}")


def upload_audio(storage_client, bucket_name, file_path):
    blob_name = f"audio/{Path(file_path).name}"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(str(file_path))
    return f"gs://{bucket_name}/{blob_name}", blob_name


def delete_audio(storage_client, bucket_name, blob_name):
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.delete()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_transcribe_audio.py -v`
Expected: all 11 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/transcribe_audio.py tests/test_transcribe_audio.py
git commit -m "feat: add GCS upload/delete functions for audio transcription"
```

---

### Task 4: Speech-to-Text Function

**Files:**
- Modify: `tools/transcribe_audio.py` (add `get_audio_encoding` and `transcribe_gcs_audio`)
- Modify: `tests/test_transcribe_audio.py` (add 3 transcription tests)

- [ ] **Step 1: Write failing tests**

Add to the bottom of `tests/test_transcribe_audio.py`:
```python
from tools.transcribe_audio import get_audio_encoding, transcribe_gcs_audio
import wave
import struct


def test_get_audio_encoding_wav(tmp_path):
    wav_path = tmp_path / "test.wav"
    with wave.open(str(wav_path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(struct.pack("<h", 0) * 16000)
    encoding, sample_rate = get_audio_encoding(wav_path)
    assert sample_rate == 16000


def test_get_audio_encoding_mp3(tmp_path):
    mp3_path = tmp_path / "test.mp3"
    mp3_path.write_bytes(b"fake")
    encoding, sample_rate = get_audio_encoding(mp3_path)
    assert sample_rate is None


def test_transcribe_gcs_audio_returns_word_list():
    word_info = MagicMock()
    word_info.word = "hello"
    word_info.start_time.total_seconds.return_value = 0.0
    word_info.end_time.total_seconds.return_value = 0.5

    alternative = MagicMock()
    alternative.words = [word_info]

    result = MagicMock()
    result.alternatives = [alternative]

    operation = MagicMock()
    operation.result.return_value = MagicMock(results=[result])

    speech_client = MagicMock()
    speech_client.long_running_recognize.return_value = operation

    words = transcribe_gcs_audio(
        speech_client, "gs://bucket/audio.mp3", "en-US", Path("test.mp3")
    )

    assert len(words) == 1
    assert words[0] == {"word": "hello", "start": 0.0, "end": 0.5}
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_transcribe_audio.py::test_transcribe_gcs_audio_returns_word_list -v`
Expected: `ImportError` — `transcribe_gcs_audio` not defined yet.

- [ ] **Step 3: Add transcription functions to tools/transcribe_audio.py**

Add after the `delete_audio` function:
```python
def get_audio_encoding(file_path):
    from google.cloud import speech
    ext = Path(file_path).suffix.lower()
    if ext == ".wav":
        import wave
        with wave.open(str(file_path), "rb") as wf:
            sample_rate = wf.getframerate()
        return speech.RecognitionConfig.AudioEncoding.LINEAR16, sample_rate
    elif ext == ".mp3":
        return speech.RecognitionConfig.AudioEncoding.MP3, None
    elif ext == ".flac":
        return speech.RecognitionConfig.AudioEncoding.FLAC, None
    else:
        raise ValueError(f"Unsupported format: {ext}. Use WAV, MP3, or FLAC.")


def transcribe_gcs_audio(speech_client, gcs_uri, language_code, audio_path):
    from google.cloud import speech
    encoding, sample_rate = get_audio_encoding(audio_path)
    config_kwargs = dict(
        encoding=encoding,
        language_code=language_code,
        enable_word_time_offsets=True,
        model="latest_long",
    )
    if sample_rate is not None:
        config_kwargs["sample_rate_hertz"] = sample_rate
    config = speech.RecognitionConfig(**config_kwargs)
    audio = speech.RecognitionAudio(uri=gcs_uri)
    operation = speech_client.long_running_recognize(config=config, audio=audio)
    print("Transcribing (this takes ~1-2 min for 12-min audio)...", flush=True)
    result = operation.result(timeout=600)
    words = []
    for r in result.results:
        for word in r.alternatives[0].words:
            words.append({
                "word": word.word,
                "start": word.start_time.total_seconds(),
                "end": word.end_time.total_seconds(),
            })
    return words
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_transcribe_audio.py -v`
Expected: all 14 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/transcribe_audio.py tests/test_transcribe_audio.py
git commit -m "feat: add Speech-to-Text transcription function"
```

---

### Task 5: Main CLI Entry Point

**Files:**
- Modify: `tools/transcribe_audio.py` (add `main()` and `if __name__` block at the bottom)

- [ ] **Step 1: Add main() to tools/transcribe_audio.py**

Add at the very bottom of `tools/transcribe_audio.py`:
```python
def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/transcribe_audio.py <audio_file>")
        print("Example: python tools/transcribe_audio.py .tmp/voiceover.wav")
        sys.exit(1)

    audio_path = Path(sys.argv[1])
    if not audio_path.exists():
        print(f"Error: file not found: {audio_path}")
        sys.exit(1)

    from google.cloud import storage, speech as speech_module

    bucket_name = get_env("GCS_BUCKET_NAME")
    project = get_env("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    language_code = os.environ.get("SPEECH_LANGUAGE_CODE", "en-US")

    storage_client = storage.Client(project=project)
    speech_client = speech_module.SpeechClient()

    print(f"Uploading {audio_path.name} to GCS bucket '{bucket_name}'...")
    ensure_bucket_exists(storage_client, bucket_name, project, location)
    gcs_uri, blob_name = upload_audio(storage_client, bucket_name, audio_path)
    print(f"Uploaded: {gcs_uri}")

    try:
        words = transcribe_gcs_audio(speech_client, gcs_uri, language_code, audio_path)
        print(f"Got {len(words)} words from transcript.")

        chunks = chunk_words(words)
        srt_content = format_srt(chunks)

        out_path = Path(".tmp") / "subtitles.srt"
        out_path.parent.mkdir(exist_ok=True)
        out_path.write_text(srt_content, encoding="utf-8")

        print(f"\nDone! Subtitles saved to {out_path}")
        print(f"  {len(chunks)} subtitle blocks created.")
    finally:
        print("Cleaning up GCS...")
        delete_audio(storage_client, bucket_name, blob_name)


if __name__ == "__main__":
    main()
```

Also add `import os` to the top of the file (after `import sys`).

- [ ] **Step 2: Run all tests to confirm nothing broke**

Run: `pytest tests/test_transcribe_audio.py -v`
Expected: all 14 tests PASS.

- [ ] **Step 3: Smoke test with a short audio clip**

Export ~30 seconds of audio from DaVinci Resolve as WAV to `.tmp/test_short.wav`, then run:
```
python tools/transcribe_audio.py .tmp/test_short.wav
```

Expected terminal output:
```
Uploading test_short.wav to GCS bucket 'youtube-psychology-audio'...
Uploaded: gs://youtube-psychology-audio/audio/test_short.wav
Transcribing (this takes ~1-2 min for 12-min audio)...
Got 47 words from transcript.

Done! Subtitles saved to .tmp/subtitles.srt
  8 subtitle blocks created.
Cleaning up GCS...
```

Open `.tmp/subtitles.srt` and verify the format looks like:
```
1
00:00:00,100 --> 00:00:02,300
The first subtitle line here

2
00:00:02,400 --> 00:00:04,800
Second subtitle line here
```

- [ ] **Step 4: Commit**

```bash
git add tools/transcribe_audio.py
git commit -m "feat: add main CLI entry point for subtitle transcription tool"
```

---

### Task 6: Workflow Documentation

**Files:**
- Create: `workflows/07_subtitles.md`

- [ ] **Step 1: Create the workflow file**

Create `workflows/07_subtitles.md`:
```markdown
# 07 — Subtitles

## Objective
Transcribe a recorded voiceover and generate a `.srt` subtitle file ready to import into DaVinci Resolve.

## Prerequisites
- `.env` contains `GCS_BUCKET_NAME` (e.g. `youtube-psychology-audio`)
- `GOOGLE_CLOUD_PROJECT` already set in `.env`
- Application Default Credentials active — run `gcloud auth application-default login` if unsure
- `google-cloud-speech` and `google-cloud-storage` installed (`pip install google-cloud-speech google-cloud-storage`)

## Inputs
- Recorded voiceover audio exported from DaVinci Resolve as WAV or MP3

## Steps

### 1. Export audio from DaVinci Resolve
**File > Export Audio** (or right-click the audio track > Export).  
Save as WAV to `.tmp/voiceover.wav`. WAV gives the best transcription accuracy.

### 2. Run the transcription tool
```
python tools/transcribe_audio.py .tmp/voiceover.wav
```
Takes ~1-2 minutes for a 12-minute voiceover.  
Output: `.tmp/subtitles.srt`

### 3. Import SRT into DaVinci Resolve
**File > Import > Subtitles** and select `.tmp/subtitles.srt`.  
Or drag-drop the `.srt` file directly onto the DaVinci timeline — it creates a subtitle track automatically.

### 4. Apply Lora font
Click the subtitle track, open **Inspector** (top-right panel), set **Font** to **Lora**.  
This applies to all subtitles at once. Adjust size, color, and position here as needed.

## Outputs
- `.tmp/subtitles.srt` — timed subtitle file for DaVinci import

## Edge Cases
- **Bucket name already taken:** GCS bucket names are globally unique. Change `GCS_BUCKET_NAME` in `.env` to a different name and rerun.
- **Different language:** Set `SPEECH_LANGUAGE_CODE=pl-PL` (or other BCP-47 code) in `.env`.
- **Subtitles out of sync:** Ensure the exported audio starts from the same point as your timeline. Export from the very beginning of the voiceover clip.
- **Transcription timeout:** For audio longer than ~20 minutes, increase `timeout=600` in `transcribe_gcs_audio()` to a higher value (e.g. `timeout=1200`).
```

- [ ] **Step 2: Commit**

```bash
git add workflows/07_subtitles.md
git commit -m "docs: add subtitle workflow documentation"
```

---

## Verification Checklist

After all tasks are complete:

- [ ] `pytest tests/test_transcribe_audio.py -v` — all 14 tests pass
- [ ] Short smoke test (30-sec clip) produces valid `.srt` with correct structure
- [ ] Full 12-minute voiceover runs through without errors or timeout
- [ ] `.tmp/subtitles.srt` imports into DaVinci Resolve without errors
- [ ] Setting Lora font in DaVinci inspector applies to all subtitle blocks simultaneously
- [ ] GCS bucket is empty after each run (no leftover audio files)
