"""Generate an FCPXML 1.8 file that DaVinci Resolve imports as a full timeline.

Track layout (from user's existing workflow):
  V3 (lane 2)  — Images, one clip per phrase, runs until the next phrase begins
  V2 (lane 1)  — Static background texture (spans the entire video)
  V1 (spine)   — A transparent gap that anchors the connected clips
  A1 (lane -1) — Voiceover
  A2 (lane -2) — Ambient music (looped to cover full video duration)

DaVinci Resolve Free supports FCPXML 1.8 import. All file references use absolute
`file:///` URIs so DaVinci links the media on import.
"""

from __future__ import annotations

import math
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

import soundfile as sf

from .phrase_mapper import PhraseTiming


@dataclass
class FCPXMLInputs:
    """All the asset paths and timing data needed to render a timeline."""

    slug: str
    voiceover_wav: Path
    ambient_wav: Path
    background_png: Path
    image_paths: dict[int, Path]   # image_num -> Path
    phrase_timings: list[PhraseTiming]   # already shifted by trim_start_s when trimming
    fps: int = 30
    width: int = 1920
    height: int = 1080
    trim_start_s: float = 0.0      # head trim: voiceover clip in-point (timeline starts here)


def _file_uri(path: Path) -> str:
    """Convert an absolute path to a file:// URI suitable for FCPXML on Windows."""
    abs_path = path.resolve()
    posix = abs_path.as_posix()
    if not posix.startswith("/"):
        posix = "/" + posix  # Windows drive letter prefix
    return "file://" + urllib.parse.quote(posix, safe="/:")


def _seconds_to_frames(seconds: float, fps: int) -> int:
    return max(0, int(round(seconds * fps)))


def _frame_str(frames: int, fps: int) -> str:
    """Format a frame count as the FCPXML rational time string `N/fps s`."""
    if frames == 0:
        return "0s"
    return f"{frames}/{fps}s"


def _wav_duration_s(wav_path: Path) -> float:
    info = sf.info(str(wav_path))
    return info.frames / float(info.samplerate)


def _wav_sample_rate(wav_path: Path) -> int:
    return int(sf.info(str(wav_path)).samplerate)


def _wav_channels(wav_path: Path) -> int:
    return int(sf.info(str(wav_path)).channels)


def render_fcpxml(inputs: FCPXMLInputs) -> str:
    """Build the FCPXML 1.8 XML string."""
    fps = inputs.fps

    # ------------------------------------------------------------------
    # Audio + duration probing
    # ------------------------------------------------------------------
    vo_duration_s = _wav_duration_s(inputs.voiceover_wav)
    ambient_duration_s = _wav_duration_s(inputs.ambient_wav)
    vo_sr = _wav_sample_rate(inputs.voiceover_wav)
    ambient_sr = _wav_sample_rate(inputs.ambient_wav)
    vo_ch = _wav_channels(inputs.voiceover_wav)
    ambient_ch = _wav_channels(inputs.ambient_wav)

    # Head trim: the timeline starts trim_start_s into the voiceover media.
    trim_s = max(0.0, min(inputs.trim_start_s, vo_duration_s - 0.1))
    vo_clip_s = vo_duration_s - trim_s

    # Sequence length = trimmed voiceover length (round to nearest frame)
    total_frames = _seconds_to_frames(vo_clip_s, fps)

    # ------------------------------------------------------------------
    # Build XML tree
    # ------------------------------------------------------------------
    fcpxml = ET.Element("fcpxml", {"version": "1.8"})
    resources = ET.SubElement(fcpxml, "resources")

    # Format
    ET.SubElement(
        resources,
        "format",
        {
            "id": "r0",
            "name": f"FFVideoFormat{inputs.height}p{fps}",
            "frameDuration": f"1/{fps}s",
            "width": str(inputs.width),
            "height": str(inputs.height),
            "colorSpace": "1-1-1 (Rec. 709)",
        },
    )

    # Voiceover asset
    vo_id = "r_vo"
    ET.SubElement(
        resources,
        "asset",
        {
            "id": vo_id,
            "name": inputs.voiceover_wav.stem,
            "src": _file_uri(inputs.voiceover_wav),
            "hasAudio": "1",
            "audioSources": "1",
            "audioChannels": str(vo_ch),
            "audioRate": str(vo_sr),
            "duration": f"{_seconds_to_frames(vo_duration_s, fps)}/{fps}s",
            "start": "0s",
        },
    )

    # Ambient music asset
    ambient_id = "r_ambient"
    ET.SubElement(
        resources,
        "asset",
        {
            "id": ambient_id,
            "name": inputs.ambient_wav.stem,
            "src": _file_uri(inputs.ambient_wav),
            "hasAudio": "1",
            "audioSources": "1",
            "audioChannels": str(ambient_ch),
            "audioRate": str(ambient_sr),
            "duration": f"{_seconds_to_frames(ambient_duration_s, fps)}/{fps}s",
            "start": "0s",
        },
    )

    # Background asset (still image — duration="0s" means indefinite)
    bg_id = "r_bg"
    ET.SubElement(
        resources,
        "asset",
        {
            "id": bg_id,
            "name": inputs.background_png.stem,
            "src": _file_uri(inputs.background_png),
            "hasVideo": "1",
            "duration": "0s",
            "start": "0s",
        },
    )

    # Per-image assets
    image_asset_ids: dict[int, str] = {}
    for image_num in sorted(inputs.image_paths.keys()):
        path = inputs.image_paths[image_num]
        asset_id = f"r_img_{image_num:03d}"
        image_asset_ids[image_num] = asset_id
        ET.SubElement(
            resources,
            "asset",
            {
                "id": asset_id,
                "name": path.stem,
                "src": _file_uri(path),
                "hasVideo": "1",
                "duration": "0s",
                "start": "0s",
            },
        )

    # ------------------------------------------------------------------
    # Library / event / project / sequence
    # ------------------------------------------------------------------
    library = ET.SubElement(fcpxml, "library")
    event = ET.SubElement(library, "event", {"name": "WAT Pipeline"})
    project = ET.SubElement(event, "project", {"name": f"{inputs.slug}_aligned"})
    sequence = ET.SubElement(
        project,
        "sequence",
        {
            "format": "r0",
            "duration": f"{total_frames}/{fps}s",
            "tcStart": "0s",
            "tcFormat": "NDF",
            "audioLayout": "stereo",
            "audioRate": "48k",
        },
    )

    spine = ET.SubElement(sequence, "spine")

    # Spine container: a single gap spanning the full sequence with all
    # video/audio connected to it.
    gap = ET.SubElement(
        spine,
        "gap",
        {
            "name": "timeline-gap",
            "offset": "0s",
            "duration": f"{total_frames}/{fps}s",
            "start": "0s",
        },
    )

    # V2 (lane 1): Background — full duration
    ET.SubElement(
        gap,
        "video",
        {
            "ref": bg_id,
            "lane": "1",
            "offset": "0s",
            "duration": f"{total_frames}/{fps}s",
            "start": "0s",
            "name": "background",
        },
    )

    # V3 (lane 2): One image per phrase
    n_phrases = len(inputs.phrase_timings)
    for idx, phrase in enumerate(inputs.phrase_timings):
        if phrase.image_num not in image_asset_ids:
            continue
        start_frames = _seconds_to_frames(phrase.start, fps)
        if idx + 1 < n_phrases:
            end_frames = _seconds_to_frames(inputs.phrase_timings[idx + 1].start, fps)
        else:
            end_frames = total_frames
        duration_frames = max(1, end_frames - start_frames)
        ET.SubElement(
            gap,
            "video",
            {
                "ref": image_asset_ids[phrase.image_num],
                "lane": "2",
                "offset": f"{start_frames}/{fps}s",
                "duration": f"{duration_frames}/{fps}s",
                "start": "0s",
                "name": f"image_{phrase.image_num:03d}",
            },
        )

    # A1 (lane -1): Voiceover (in-point = trim_s into the media)
    ET.SubElement(
        gap,
        "audio",
        {
            "ref": vo_id,
            "lane": "-1",
            "offset": "0s",
            "duration": f"{_seconds_to_frames(vo_clip_s, fps)}/{fps}s",
            "start": _frame_str(_seconds_to_frames(trim_s, fps), fps),
            "name": "voiceover",
        },
    )

    # A2 (lane -2): Ambient music — loop sequential clips to fill duration
    ambient_clip_frames = max(1, _seconds_to_frames(ambient_duration_s, fps))
    offset_frames = 0
    loop_idx = 1
    while offset_frames < total_frames:
        clip_frames = min(ambient_clip_frames, total_frames - offset_frames)
        ET.SubElement(
            gap,
            "audio",
            {
                "ref": ambient_id,
                "lane": "-2",
                "offset": f"{offset_frames}/{fps}s",
                "duration": f"{clip_frames}/{fps}s",
                "start": "0s",
                "name": f"ambient_loop_{loop_idx}",
            },
        )
        offset_frames += clip_frames
        loop_idx += 1
        if loop_idx > 100:
            break  # safety guard

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------
    ET.indent(fcpxml, space="  ")
    xml_body = ET.tostring(fcpxml, encoding="unicode")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE fcpxml>\n'
        + xml_body
        + "\n"
    )
