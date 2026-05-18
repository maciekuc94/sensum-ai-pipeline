# Agent 7 — TTS Voice Reference

## Objective

Generate AI voice reference audio from the narration script so you can check English pronunciation and pacing before recording your own voiceover in DaVinci Resolve.

This step is **optional**. Run it between Agent 6 (narration script) and your manual recording session.

---

## Required Inputs

- `outputs/{slug}/md/06_script_narration.md` — produced by Agent 5
- `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` in `.env`
- Application Default Credentials active (`gcloud auth application-default login`)

---

## Steps

### 1. Install dependency (first time only)

```bash
pip install google-cloud-texttospeech
```

### 2. Run the agent

```bash
python tools/agent7_tts.py what-porn-does-to-your-brain
```

Replace the slug with the current video's slug.

### 3. Listen and choose

Open `outputs/{slug}/tts/` in File Explorer. You will find 11 WAV files (default mode generates only `gemini_Puck.wav`; use `--all` for all 11):

**Chirp 3: HD** (Google Cloud TTS — professional voiceover quality):
- `chirp3_Aoede.wav` — warm, expressive
- `chirp3_Charon.wav` — deep, authoritative
- `chirp3_Fenrir.wav` — energetic, clear
- `chirp3_Kore.wav` — calm, informative
- `chirp3_Leda.wav` — bright, friendly
- `chirp3_Orus.wav` — smooth, measured
- `chirp3_Puck.wav` — lively, engaging
- `chirp3_Zephyr.wav` — conversational, natural

**Gemini Flash TTS** (Google AI — most expressive, designed for long-form narration):
- `gemini_Kore.wav`
- `gemini_Charon.wav`
- `gemini_Puck.wav` ← default

Pick the voice that best helps you with:

1. **Pronunciation** — how to say specific words and names
2. **Rhythm** — natural pauses and sentence flow
3. **Pacing** — estimated video duration at that speaking speed

---

## Expected Outputs

```
outputs/{slug}/
  tts/
    gemini_Puck.wav          (default mode)
    chirp3_Aoede.wav         (--all mode only)
    chirp3_Charon.wav
    chirp3_Fenrir.wav
    chirp3_Kore.wav
    chirp3_Leda.wav
    chirp3_Orus.wav
    chirp3_Puck.wav
    chirp3_Zephyr.wav
    gemini_Kore.wav
    gemini_Charon.wav
```

These files are temporary reference only — they do not go into the video. Delete them after recording.

---

## Cost

| Model | Voices | Approx. cost per ~1,700-word script |
|-------|--------|-------------------------------------|
| Chirp 3: HD | 8 | ~$0.24 |
| Gemini Flash TTS | 3 | ~$0.30 |
| **Total (--all)** | **11** | **~$0.54** |
| **Default only** | **1** | **~$0.01** |

---

## Edge Cases

| Situation | Fix |
|-----------|-----|
| `md/06_script_narration.md not found` | Run `agent6_narration.py` first |
| `google-cloud-texttospeech not installed` | Run `pip install google-cloud-texttospeech` |
| Chirp 3 voice fails with `404 Not Found` | Voice name may have changed; check Google Cloud TTS voice list |
| Gemini TTS fails with model not found | Update `GEMINI_TTS_MODEL` in `tools/agent7_tts.py` |

---

## After Listening

Record your voiceover in DaVinci Resolve using the AI audio as a reference guide. The `outputs/{slug}/tts/` files can be deleted after recording.
