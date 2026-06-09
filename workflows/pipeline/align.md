# Workflow: Align Agent — Forced Alignment & DaVinci Bundle

## Purpose

The Align agent (`tools/pipeline/agent_align.py`) eliminates the 2-4 hours of manual work that used to happen in DaVinci after recording the voiceover. It runs forced alignment between the recorded WAV and the canonical script, then emits four files into `outputs/videos/{slug}/edit/`:

> Note: this is the "post-record" step. The file is `agent_align.py` (no number) — it's a satellite, not a numbered pipeline stage.

| File | What it does in DaVinci |
|---|---|
| `subtitles.srt` | Drag onto a subtitle track — every line is already timed |
| `timeline.fcpxml` | File → Import → Final Cut Pro XML — populates 4 tracks (background, images, voiceover, ambient music) with every image at the right timestamp |
| `preview.html` | Open in browser BEFORE importing — visual sanity check showing every image, its timestamp, and the matching phrase |
| `alignment.json` | Debug data with word-level timestamps and match-rate stats |

After import, the DaVinci work is artistic only: zoom and reframe each image to taste, polish subtitle position if needed, render.

---

## Prerequisites

1. **Voiceover recorded and exported.** Place the exported file at:
   ```
   outputs/videos/{slug}/voiceover/voiceover.wav
   ```
   `.mp3`, `.m4a`, and `.flac` are also accepted. If the directory has multiple files and none is named `voiceover.wav`, the first audio file alphabetically wins. Use `--audio <path>` to override.

2. **Agent 5 has run** — `outputs/videos/{slug}/md/05_phrases.md` exists.

3. **Agent 4 has run** — `outputs/videos/{slug}/docx/script.docx` exists (exported automatically by `--apply`). If you edited the script, `script_corrected.docx` takes priority. **Section headers (`## `) are automatically skipped** by `read_script_docx` in `lib/aligner.py` — any Heading-styled paragraph is ignored, so dividers added by the draft chain (or manually in Word) do not affect alignment.

4. **Agent 6 has run** — generated images exist at `outputs/videos/{slug}/images/image_*.png`. If you skip Agent 6, the timeline will be built without the V3 image track.

5. **Channel assets present** in `outputs/channel_assets/`:
   - `blank_background_grain.png` — the static canvas
   - `ambient_sensum.wav` — the ambient music

6. **Python dependency: `faster-whisper`.** Install once:
   ```bash
   pip install faster-whisper soundfile
   ```
   First run downloads the Whisper model (`large-v3` is ~3 GB) to the local Hugging Face cache. Subsequent runs reuse it.

---

## Run Command

```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "<slug>"
```

Flags:

| Flag | Default | When to change |
|---|---|---|
| `--audio <path>` | `voiceover/voiceover.wav` | Audio file lives elsewhere |
| `--model <size>` | `large-v3` | Use `medium` or `small` for faster CPU runs (slight precision loss; still usable for word-for-word reading) |
| `--device <cpu\|cuda>` | `cpu` | You have an NVIDIA GPU + CUDA-enabled ctranslate2 |
| `--compute-type <int8\|float16\|float32>` | `int8` | More precision (slower; needs GPU for float16) |
| `--language <code>` | `pl` | Voiceover is in another language (`--language en` for legacy English) |
| `--fps <n>` | `30` | Project runs at 24 or 60 fps |
| `--window <n>` | `10` | Alignment match rate is low and you suspect the script and audio drift apart further than 10 words |
| `--min-dur <s>` | `1.20` | Subtitles flash too fast → raise; feel sluggish → lower. Min seconds before a comma/pause break is allowed |
| `--sentence-min <s>` | `0.85` | Absolute floor for a stand-alone cue (Netflix 5/6 s). Shorter cues are merged into a neighbour |
| `--max-dur <s>` | `7.00` | Longest a cue may grow while merging (Netflix max event) |
| `--lead-in <s>` | `0.10` | Subtitles feel late → raise (appear earlier); feel early → lower or `0`. Global earlier-nudge |
| `--max-gap <s>` | `1.50` | Audio pause above which the screen clears between cues; lower → clears at more pauses, `0` → always continuous |
| `--lead-out <s>` | `0.50` | At a cleared pause, how long a cue lingers past its last word before the screen clears |
| `--no-drop-phantom` | off | Keep an unspoken leading/trailing line (hook/title written in the script but never read) instead of dropping it |

---

## What the Agent Does (5 steps)

1. **Transcribe.** Runs `faster-whisper` on the WAV with `word_timestamps=True`.
2. **Align.** Greedy walk through the script tokens, snapping each one to the matching Whisper word in the next `--window` positions. Unmatched tokens get their timestamps interpolated between neighbors.
3. **Map phrases.** Parses `05_phrases.md` and finds each phrase as a contiguous run in the aligned script.
4. **Chunk subtitles (duration-aware, sentence-first).** Packs aligned words into single-line cues on **real word timestamps** — see *Subtitle rhythm & sync* below.
5. **Emit assets.** Writes `subtitles.srt`, `timeline.fcpxml`, `alignment.json`, and `preview.html`.

---

## Subtitle rhythm & sync (`lib/subtitle_chunker.py`, redesigned 2026-06-08)

The chunker is **duration-aware and sentence-first**, tuned to broadcast standards
(BBC / Netflix / Amara). It replaced a word-count chunker that broke on every
comma/period regardless of timing, which left ~20% of cues flashing by (<1.2 s).

**How it builds a cue (all on real word timestamps — no proportional guessing):**
1. **Drop phantom edges.** A leading/trailing run of *fully-unmatched* (interpolated)
   words has fabricated timing — e.g. an on-screen hook/title line written into the
   script but never read aloud. It is dropped (it would otherwise render a wrong
   cue crammed into the first ~0.7 s). `--no-drop-phantom` keeps it.
2. **Segment into sentences** (a paragraph break also starts one). **A cue never
   spans a sentence boundary** — no more `"…troska. Że to…"` cards.
3. **Pack each sentence:** group clauses (comma / dash / pause) until the cue
   reaches the duration floor, then break at that clause boundary → even rhythm.
   A group longer than one line is **balance-split by word**, so a sentence-final
   word is never stranded onto the next cue.
4. **Absorb leftovers:** a cue under `--sentence-min` (0.85 s) merges into its own
   clause / best-fitting neighbour.
5. **Chain & breathe:** cues chain (no gaps) through continuous speech, but where
   the audio pause to the next cue exceeds `--max-gap` (1.5 s — a section break),
   the cue lingers `--lead-out` (0.5 s) past its last word and the screen clears.
6. **Lead-in:** every cue is nudged `--lead-in` (0.10 s) earlier so it lands *with*
   the spoken word, not after it (a trailing subtitle reads as "late").

Calibrated against a full hand-timed reference SRT (slug 3, 2026-06-08): the output
matches the human subtitler's rhythm — median ~2.1 s, stdev ~0.72, ~5 pause-gaps,
1–2 sub-floor beats — to within noise. The human tolerated a slightly wider line
(up to ~50 chars) in a few spots; raise `MAX_CPL` if you want fewer mid-clause
balance-splits, at the cost of broadcast-standard 42-char safety.

**The numbers (why these defaults):** comfortable reading ≈ 15–17 CPS; min display
0.85 s (Netflix 5/6 s) / 1.2 s before a soft break; max 7 s; one line ≤ 42 chars.

**What you still own (the machine can't):** *sync feel* is verified by **ear** in
`preview.html` / DaVinci — only you can hear whether a cue lands on the word. If the
whole track feels late, raise `--lead-in`; if early, lower it. Genuinely short cues
(0.85–1.2 s) on terse clauses are **faithful to speech tempo**, not bugs.

**Lesson — the phantom hook (slug 3, 2026-06-08).** Agent 4 writes the hook as the
script's first line, but if you record starting from the *second* line, the hook is
absent from the audio → all its words interpolate into the first ~0.7 s. The chunker
now drops such phantom edges. If you want the hook visible, add it as a **title card
in DaVinci** (not a subtitle), or re-record reading it. Verify with the diagnostic:
`PYTHONIOENCODING=utf-8 python tools/dev/analyze_subtitles.py <slug>` flags
interpolated head words, sub-floor cues, sentence-crossings, and CPS outliers.

---

## Reviewer Checklist (in this order)

1. **Open `preview.html` first.** Spot-check 5 random phrases — does the start timestamp match where you remember the phrase being spoken? Tolerance: ±150 ms.
2. **Check the match rate** in the preview's header. **Aim for >95%.** Below 90% means alignment is unreliable — the audio probably drifts from the script, or the script was edited after recording.
3. **Look for red rows** in the preview — unmatched phrases. These are listed but have no timestamp; fix the underlying script/audio mismatch and rerun.
4. **Import into DaVinci:**
   - File → Import → Final Cut Pro XML → `timeline.fcpxml`
   - Verify 4 tracks appear: V3 images, V2 background, A1 voiceover, A2 ambient music
   - Drag `subtitles.srt` onto a subtitle track
5. **Apply your saved Subtitle preset** (see `workflows/guides/davinci_subtitle_preset.md` for one-time setup).

---

## Output Location

```
outputs/videos/{slug}/
├── voiceover/
│   └── voiceover.wav         (you put this here)
├── md/
│   └── 05_phrases.md   (existing — input)
├── docx/
│   ├── script_corrected.docx (preferred — input)
│   └── script.docx           (fallback — input)
├── images/
│   └── image_NNN.png         (existing — input)
└── edit/                     (NEW — agent 11 output)
    ├── subtitles.srt
    ├── timeline.fcpxml
    ├── alignment.json
    └── preview.html
```

---

## Common Issues

**`Error: No voiceover file found.`**

You haven't dropped the WAV into `outputs/videos/{slug}/voiceover/`. Either move it there as `voiceover.wav` or pass `--audio <path>`.

**Match rate under 90%, lots of unmatched rows in the preview**

The audio doesn't match the script. Possible causes:
- You edited the script after recording — re-export the voiceover or revert the script
- You improvised significantly during recording — only word-for-word reading aligns reliably
- The wrong audio file is in the voiceover folder
- The wrong slug

**Whisper is downloading a model and seems frozen on first run**

First run pulls ~3 GB. Let it finish. Subsequent runs are fast.

**DaVinci flags "missing media" after FCPXML import**

The image/audio files moved after generation. Rerun `agent_align.py` to regenerate `timeline.fcpxml` with current paths.

**Subtitles import in the wrong font**

The SRT file carries timing only, no styling. Apply your saved Lora subtitle preset in DaVinci — see `workflows/guides/davinci_subtitle_preset.md` for the one-time setup.

**Ambient music ends before video ends**

The agent loops `ambient_sensum.wav` automatically. If you see only one ambient clip in DaVinci, the music file is longer than the voiceover — this is correct.

---

## Performance Notes

- **CPU, large-v3 model:** ~0.5-1x real-time. A 10-minute voiceover takes 10-20 minutes to transcribe.
- **CPU, medium model:** ~2x real-time. A 10-minute voiceover takes ~5 minutes. Quality loss is negligible for word-for-word reading.
- **CUDA GPU, large-v3, float16:** ~10x real-time. A 10-minute voiceover takes ~1 minute.

For routine production use, `--model medium --compute-type int8` is the recommended default on CPU.

---

## First-Run Verification (Video 4)

This agent has not yet been validated against a real production voiceover. Video 4 (`4_why_you_can_t_stick_to_anything`) is the verification target. Wait for the user to finish recording the voiceover; then run this verification end-to-end before treating the agent as production-ready.

**Trigger:** User signals video 4 voiceover is recorded and exported from Studio One.

**Drop location:**
```
outputs/videos/4_why_you_can_t_stick_to_anything/voiceover/voiceover.wav
```

**Run:**
```bash
PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "4_why_you_can_t_stick_to_anything"
```

**Verification checklist:**

1. Open `outputs/videos/4_why_you_can_t_stick_to_anything/edit/preview.html` in a browser.
2. Confirm **match rate ≥ 95%** in the header bar.
3. Spot-check 5 random phrases — does the start timestamp line up with where the phrase is spoken? Tolerance: ±150 ms.
4. Confirm zero (or near-zero) unmatched / red rows.
5. Import `edit/timeline.fcpxml` into DaVinci Resolve Free: File → Import → Final Cut Pro XML.
6. Verify 4 tracks appear (V3 images, V2 background, A1 voiceover, A2 ambient music) with no "missing media" flags.
7. Drag `edit/subtitles.srt` onto a subtitle track; apply the `SENSUM Lora Italic` preset (see `workflows/guides/davinci_subtitle_preset.md`).
8. Scrub the timeline at 3–4 points; visually confirm images change on the right phrase and subtitles match the voice.

If any step fails: document the failure mode, fix the underlying component (`tools/pipeline/lib/*.py`), and rerun. Once verification passes, this section can be removed or kept as a historical record of the first-run validation.

---

## Next Step

Open DaVinci, do artistic image framing per shot, render, deliver. Pipeline complete.
