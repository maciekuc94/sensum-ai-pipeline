"""Align Agent — Forced Alignment & DaVinci Asset Bundle

Reads the user's exported voiceover WAV plus the existing script + phrase
table, runs faster-whisper to get per-word timestamps, aligns those timestamps
to the canonical script, and writes everything DaVinci Resolve needs to import
the timeline:

  outputs/videos_pl/{slug}/edit/subtitles.srt    — drag onto a subtitle track
  outputs/videos_pl/{slug}/edit/timeline.fcpxml  — File → Import → Final Cut Pro XML
  outputs/videos_pl/{slug}/edit/alignment.json   — debug data
  outputs/videos_pl/{slug}/edit/preview.html     — visual sanity check

Usage:
    PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "<slug>"
    PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "<slug>" \
        --audio outputs/videos_pl/<slug>/voiceover/voiceover.wav \
        --model medium --fps 30
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.utils import get_output_dir, log_cost  # noqa: E402
from tools.pipeline.lib.aligner import (  # noqa: E402
    AlignedWord,
    align_script_to_audio,
    aligned_to_dict,
    read_script_docx,
    transcribe_audio,
)
from tools.pipeline.lib.phrase_mapper import (  # noqa: E402
    map_phrases_to_timings,
    parse_phrases_md,
    timings_to_dict,
)
from tools.pipeline.lib.subtitle_chunker import (  # noqa: E402
    build_chunks,
    chunks_to_dict,
    render_srt,
)
from tools.pipeline.lib.fcpxml_writer import FCPXMLInputs, render_fcpxml  # noqa: E402
from tools.pipeline.lib.preview_writer import render_preview  # noqa: E402


CHANNEL_ASSETS_DIR = PROJECT_ROOT / "outputs" / "channel_assets"
BACKGROUND_CANDIDATES = ("blank_background.png", "blank_background_grain.png", "blank_background_Grain.png")
AMBIENT_MUSIC_FILENAME = "ambient_sensum.wav"
AUDIO_EXTENSIONS = (".wav", ".mp3", ".m4a", ".flac")


def _find_default_audio(base_dir: Path) -> Path | None:
    voiceover_dir = base_dir / "voiceover"
    if not voiceover_dir.exists():
        return None
    # Prefer voiceover.wav if it exists; otherwise pick the first audio file
    preferred = voiceover_dir / "voiceover.wav"
    if preferred.exists():
        return preferred
    for entry in sorted(voiceover_dir.iterdir()):
        if entry.is_file() and entry.suffix.lower() in AUDIO_EXTENSIONS:
            return entry
    return None


def _find_background() -> Path:
    for name in BACKGROUND_CANDIDATES:
        candidate = CHANNEL_ASSETS_DIR / name
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Background texture not found. Looked for: "
        f"{', '.join(str(CHANNEL_ASSETS_DIR / n) for n in BACKGROUND_CANDIDATES)}"
    )


def _discover_images(images_dir: Path) -> dict[int, Path]:
    """Return {image_num: path} for image_NNN.png files in the directory."""
    discovered: dict[int, Path] = {}
    if not images_dir.exists():
        return discovered
    for entry in sorted(images_dir.iterdir()):
        if not entry.is_file() or entry.suffix.lower() != ".png":
            continue
        stem = entry.stem.lower()
        if not stem.startswith("image_"):
            continue
        try:
            num = int(stem.split("_", 1)[1])
        except (ValueError, IndexError):
            continue
        discovered[num] = entry
    return discovered


def main(args: argparse.Namespace) -> None:
    slug = args.slug
    base = get_output_dir(slug)
    edit_dir = base / "edit"
    edit_dir.mkdir(parents=True, exist_ok=True)

    # Script source priority: script_corrected.docx > script.docx > 04_final.md
    script_path = base / "md" / "04_final.md"
    for docx_name in ("docx/script_corrected.docx", "docx/script.docx"):
        candidate = base / docx_name
        if candidate.exists():
            script_path = candidate
            break
    phrases_path = base / "md" / "05_phrases.md"
    _grain_dir = base / "images_grain"
    images_dir = _grain_dir if (_grain_dir.exists() and any(_grain_dir.glob("image_*.png"))) else base / "images"

    audio_path: Path | None = None
    if not args.from_alignment:
        if args.audio:
            audio_path = Path(args.audio).resolve()
        else:
            audio_path = _find_default_audio(base)
            if audio_path is None:
                print(
                    f"Error: No voiceover file found.\n"
                    f"  Looked in: {base / 'voiceover'}\n"
                    f"  Drop your exported voiceover here as voiceover.wav, or pass --audio <path>."
                )
                sys.exit(1)
        if not audio_path.exists():
            print(f"Error: audio file not found: {audio_path}")
            sys.exit(1)

    if not script_path.exists():
        print(f"Error: script not found: {script_path}\n  Run Agent 4b first (--apply exports docx/script.docx).")
        sys.exit(1)
    if not phrases_path.exists():
        print(f"Error: phrase table not found: {phrases_path}\n  Run Agent 5 first.")
        sys.exit(1)

    background_path = _find_background()
    ambient_path = CHANNEL_ASSETS_DIR / AMBIENT_MUSIC_FILENAME
    if not ambient_path.exists():
        print(f"Error: ambient music not found: {ambient_path}")
        sys.exit(1)

    alignment_path = edit_dir / "alignment.json"

    if args.from_alignment:
        # ------------------------------------------------------------------
        # Fast path: rebuild SRT from existing alignment.json (skip Whisper)
        # ------------------------------------------------------------------
        if not alignment_path.exists():
            print(f"Error: --from-alignment requires {alignment_path} — run the full agent first.")
            sys.exit(1)
        print(f"=== Agent Align: Rebuild SRT + FCPXML from alignment.json ===")
        print(f"Slug : {slug}")
        payload = json.loads(alignment_path.read_text(encoding="utf-8"))
        align_stats = payload["stats"]
        if audio_path is None:
            payload_audio = payload.get("audio_path")
            if payload_audio:
                audio_path = Path(payload_audio)
        aligned = [
            AlignedWord(
                index=w["index"],
                word=w["word"],
                start=w["start"],
                end=w["end"],
                matched=w["matched"],
                # .get with default keeps backward-compat with alignment.json
                # files written before force_break_before existed.
                force_break_before=w.get("force_break_before", False),
            )
            for w in payload["aligned_words"]
        ]
        align_elapsed = 0.0
        print(f"  Loaded {len(aligned)} aligned words from alignment.json")

        phrases_md = phrases_path.read_text(encoding="utf-8")
        phrase_rows = parse_phrases_md(phrases_md)
        phrase_timings = map_phrases_to_timings(phrase_rows, aligned)
        matched_phrases = sum(1 for p in phrase_timings if p.matched)
    else:
        # ------------------------------------------------------------------
        # Full path: transcribe + align
        # ------------------------------------------------------------------
        print(f"=== Align Agent: Forced Alignment & DaVinci Bundle ===")
        print(f"Slug          : {slug}")
        print(f"Audio         : {audio_path}")
        print(f"Script        : {script_path}")
        print(f"Phrase table  : {phrases_path}")
        print(f"Whisper model : {args.model} ({args.device}/{args.compute_type})")
        print(f"FPS           : {args.fps}")
        print()

        # 1) Forced alignment
        whisper_cache_path = edit_dir / "whisper_words.json"
        if script_path.suffix.lower() == ".docx":
            script_md = read_script_docx(script_path)
        else:
            script_md = script_path.read_text(encoding="utf-8")
        whisper_tokens: list[dict] | None = None
        if not args.fresh_whisper and whisper_cache_path.exists():
            print(f"Step 1/5: Loading cached Whisper output from {whisper_cache_path.name}...")
            whisper_tokens = json.loads(whisper_cache_path.read_text(encoding="utf-8"))
            print(f"  Loaded {len(whisper_tokens)} cached whisper words (skip transcription; pass --fresh-whisper to override).")
        else:
            print("Step 1/5: Transcribing audio with faster-whisper...")
            t0 = time.time()
            whisper_tokens = transcribe_audio(
                audio_path,
                model_size=args.model,
                language=args.language,
                device=args.device,
                compute_type=args.compute_type,
            )
            t_transcribe = time.time() - t0
            whisper_cache_path.write_text(json.dumps(whisper_tokens), encoding="utf-8")
            print(f"  Transcribed {len(whisper_tokens)} whisper words in {t_transcribe:.1f}s → cached to {whisper_cache_path.name}")

        t0 = time.time()
        aligned, align_stats = align_script_to_audio(
            audio_path=audio_path,
            script_md_text=script_md,
            model_size=args.model,
            language=args.language,
            device=args.device,
            compute_type=args.compute_type,
            window=args.window,
            whisper_tokens=whisper_tokens,
        )
        align_elapsed = time.time() - t0
        print(
            f"  Aligned {align_stats['script_words']} script words against "
            f"{align_stats['whisper_words']} whisper words "
            f"({align_stats['matched']} matched / {align_stats['interpolated']} interpolated, "
            f"{align_stats['match_rate'] * 100:.1f}%) in {align_elapsed:.1f}s"
        )
        if align_stats["match_rate"] < 0.95:
            print(
                f"  WARNING: match rate {align_stats['match_rate'] * 100:.1f}% below 95% target — "
                "alignment may be unreliable. Verify preview.html before importing to DaVinci."
            )

        # 2) Phrase mapping
        print("Step 2/5: Mapping phrases from 05_phrases.md...")
        phrases_md = phrases_path.read_text(encoding="utf-8")
        phrase_rows = parse_phrases_md(phrases_md)
        phrase_timings = map_phrases_to_timings(phrase_rows, aligned)
        matched_phrases = sum(1 for p in phrase_timings if p.matched)
        print(f"  Mapped {matched_phrases}/{len(phrase_timings)} phrases to timestamps.")

    # ------------------------------------------------------------------
    # 3) Subtitle chunks
    # ------------------------------------------------------------------
    step = "Step 2/4" if args.from_alignment else "Step 3/5"
    print(f"{step}: Building subtitle chunks...")
    chunks = build_chunks(
        aligned,
        min_dur=args.min_dur,
        sentence_min=args.sentence_min,
        max_dur=args.max_dur,
        lead_in=args.lead_in,
        gap_clear=args.max_gap,
        lead_out=args.lead_out,
        drop_phantom=not args.no_drop_phantom,
    )
    srt_text = render_srt(chunks)
    srt_path = edit_dir / "subtitles.srt"
    srt_path.write_text(srt_text, encoding="utf-8")
    print(f"  Wrote {len(chunks)} subtitle chunks → {srt_path.name}")

    # ------------------------------------------------------------------
    # 4) FCPXML
    # ------------------------------------------------------------------
    # Re-discover images at the last possible moment — defends against a
    # grain/image job still writing into images_grain/ when this agent started.
    image_paths = _discover_images(images_dir)
    if not image_paths:
        print(f"Warning: no images found in {images_dir}. The timeline will have no V3 clips.")

    step = "Step 3/4" if args.from_alignment else "Step 4/5"
    print(f"{step}: Generating FCPXML timeline...")
    print(f"  Images found: {len(image_paths)} (from {images_dir.name}/)")
    fcpxml_inputs = FCPXMLInputs(
        slug=slug,
        voiceover_wav=audio_path,
        ambient_wav=ambient_path,
        background_png=background_path,
        image_paths=image_paths,
        phrase_timings=[p for p in phrase_timings if p.matched],
        fps=args.fps,
    )
    fcpxml_text = render_fcpxml(fcpxml_inputs)
    fcpxml_path = edit_dir / "timeline.fcpxml"
    fcpxml_path.write_text(fcpxml_text, encoding="utf-8")
    print(f"  Wrote timeline.fcpxml with {len([p for p in phrase_timings if p.matched])} image clips")

    # ------------------------------------------------------------------
    # 5) Debug + preview
    # ------------------------------------------------------------------
    step = "Step 4/4" if args.from_alignment else "Step 5/5"
    print(f"{step}: Writing alignment.json + preview.html...")
    alignment_payload = {
        "slug": slug,
        "audio_path": str(audio_path),
        "model": args.model,
        "fps": args.fps,
        "stats": align_stats,
        "aligned_words": aligned_to_dict(aligned),
        "phrase_timings": timings_to_dict(phrase_timings),
        "subtitle_chunks": chunks_to_dict(chunks),
    }
    alignment_path.write_text(json.dumps(alignment_payload, indent=2), encoding="utf-8")

    preview_path = edit_dir / "preview.html"
    preview_html = render_preview(
        html_path=preview_path,
        slug=slug,
        phrase_timings=phrase_timings,
        subtitle_chunks=chunks,
        image_paths=image_paths,
        audio_duration_s=align_stats["audio_duration_s"],
        stats=align_stats,
    )
    preview_path.write_text(preview_html, encoding="utf-8")

    log_cost(
        slug,
        "agent_align",
        {
            "runtime_s": round(align_elapsed, 2),
            "model": args.model,
            "device": args.device,
            "match_rate": round(align_stats["match_rate"], 4),
            "matched_phrases": matched_phrases,
            "total_phrases": len(phrase_timings),
            "subtitle_chunks": len(chunks),
        },
    )

    print()
    print(f"Done. Outputs in: {edit_dir}")
    print(f"  - subtitles.srt    → drag onto a subtitle track in DaVinci")
    print(f"  - timeline.fcpxml  → File → Import → Final Cut Pro XML")
    print(f"  - preview.html     → open in browser to spot-check before importing")
    print(f"  - alignment.json   → debug data (word-level timestamps)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Align voiceover audio to the canonical script and emit DaVinci import assets."
    )
    parser.add_argument("slug", help="Slug under outputs/videos_pl/")
    parser.add_argument(
        "--audio",
        help="Path to voiceover audio file (default: outputs/videos_pl/<slug>/voiceover/voiceover.wav)",
    )
    parser.add_argument("--model", default="large-v3", help="faster-whisper model size (default: large-v3)")
    parser.add_argument("--device", default="cpu", help="cpu or cuda (default: cpu)")
    parser.add_argument("--compute-type", dest="compute_type", default="int8", help="int8 / float16 / float32")
    parser.add_argument("--language", default="pl", help="Audio language code (default: pl). Use --language en for legacy English voiceovers.")
    parser.add_argument("--fps", type=int, default=30, help="Timeline frame rate (default: 30)")
    parser.add_argument("--window", type=int, default=10, help="Greedy alignment lookahead (default: 10)")
    # Subtitle rhythm / sync knobs — tune without editing subtitle_chunker.py.
    parser.add_argument(
        "--min-dur", dest="min_dur", type=float, default=1.20,
        help="Min on-screen seconds before a soft (comma/pause) break is allowed (default: 1.20)",
    )
    parser.add_argument(
        "--sentence-min", dest="sentence_min", type=float, default=0.85,
        help="Absolute min seconds for a sentence-end cue; shorter cues are merged (default: 0.85)",
    )
    parser.add_argument(
        "--max-dur", dest="max_dur", type=float, default=7.00,
        help="Max seconds a cue may grow to during merging (default: 7.00)",
    )
    parser.add_argument(
        "--lead-in", dest="lead_in", type=float, default=0.10,
        help="Seconds to nudge every cue earlier so it lands with the word (default: 0.10; 0 disables)",
    )
    parser.add_argument(
        "--max-gap", dest="max_gap", type=float, default=1.50,
        help="Audio pause (s) above which the screen clears between cues instead of chaining (default: 1.50; 0 = always continuous)",
    )
    parser.add_argument(
        "--lead-out", dest="lead_out", type=float, default=0.50,
        help="At a cleared pause, seconds a cue lingers past its last word before the screen clears (default: 0.50)",
    )
    parser.add_argument(
        "--no-drop-phantom", dest="no_drop_phantom", action="store_true",
        help="Keep leading/trailing fully-interpolated cues (unspoken hook/title lines) instead of dropping them",
    )
    parser.add_argument(
        "--from-alignment", dest="from_alignment", action="store_true",
        help="Skip Whisper transcription — rebuild SRT + FCPXML from existing alignment.json (fast, seconds)",
    )
    parser.add_argument(
        "--fresh-whisper", dest="fresh_whisper", action="store_true",
        help="Force re-transcription even if whisper_words.json cache exists",
    )
    return parser.parse_args()


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main(parse_args())
