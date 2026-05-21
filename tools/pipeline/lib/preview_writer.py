"""Render an HTML sanity-check page summarizing the alignment results.

Shows each phrase with its image thumbnail, start/end timestamps, duration,
and the matching script text. Also lists subtitle chunks below. Opens in any
browser; no external dependencies, no JS frameworks. Use this to spot-check
before importing the FCPXML into DaVinci.
"""

from __future__ import annotations

import html
import urllib.parse
from pathlib import Path

from .phrase_mapper import PhraseTiming
from .subtitle_chunker import SubtitleChunk


def _format_ts(seconds: float) -> str:
    total_ms = int(round(seconds * 1000))
    h, rem = divmod(total_ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, ms = divmod(rem, 1000)
    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}.{ms:03d}"
    return f"{m:02d}:{s:02d}.{ms:03d}"


def _image_uri(image_path: Path, html_path: Path) -> str:
    """Relative file URI from the HTML location to the image."""
    try:
        rel = image_path.resolve().relative_to(html_path.parent.resolve())
        return urllib.parse.quote(rel.as_posix())
    except ValueError:
        # Different drive — fall back to absolute file:// URI
        abs_posix = image_path.resolve().as_posix()
        if not abs_posix.startswith("/"):
            abs_posix = "/" + abs_posix
        return "file://" + urllib.parse.quote(abs_posix, safe="/:")


def render_preview(
    html_path: Path,
    slug: str,
    phrase_timings: list[PhraseTiming],
    subtitle_chunks: list[SubtitleChunk],
    image_paths: dict[int, Path],
    audio_duration_s: float,
    stats: dict,
) -> str:
    """Build the HTML preview document as a string."""
    image_rows: list[str] = []
    for idx, phrase in enumerate(phrase_timings):
        duration = phrase.end - phrase.start
        img_uri = ""
        if phrase.image_num in image_paths:
            img_uri = _image_uri(image_paths[phrase.image_num], html_path)
        warn = "" if phrase.matched else ' class="unmatched"'
        image_rows.append(
            f'<tr{warn}>'
            f'<td class="num">{phrase.image_num:03d}</td>'
            f'<td class="thumb">'
            + (f'<img src="{img_uri}" loading="lazy" alt="img {phrase.image_num}"/>' if img_uri else "")
            + "</td>"
            f'<td class="time">{_format_ts(phrase.start)}</td>'
            f'<td class="time">{_format_ts(phrase.end)}</td>'
            f'<td class="dur">{duration:.2f}s</td>'
            f'<td class="text">{html.escape(phrase.text)}</td>'
            "</tr>"
        )

    sub_rows: list[str] = []
    for chunk in subtitle_chunks:
        duration = chunk.end - chunk.start
        sub_rows.append(
            f'<tr>'
            f'<td class="num">{chunk.index}</td>'
            f'<td class="time">{_format_ts(chunk.start)}</td>'
            f'<td class="time">{_format_ts(chunk.end)}</td>'
            f'<td class="dur">{duration:.2f}s</td>'
            f'<td class="text">{html.escape(chunk.text)}</td>'
            "</tr>"
        )

    matched_pct = stats.get("match_rate", 0.0) * 100

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Alignment Preview — {html.escape(slug)}</title>
<style>
  :root {{
    --beige: #F4E5CA;
    --ink: #582F0E;
    --soft: #B89878;
  }}
  body {{
    font-family: 'Georgia', 'Lora', serif;
    background: var(--beige);
    color: var(--ink);
    margin: 0;
    padding: 2rem;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
  }}
  h1 {{ font-size: 1.4rem; margin-bottom: 0.25rem; }}
  .meta {{
    font-size: 0.85rem;
    color: var(--ink);
    opacity: 0.8;
    margin-bottom: 2rem;
  }}
  .meta span {{ margin-right: 1.5rem; }}
  h2 {{
    font-size: 1.1rem;
    margin-top: 2.5rem;
    border-bottom: 1px solid var(--soft);
    padding-bottom: 0.25rem;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }}
  th, td {{
    text-align: left;
    padding: 0.35rem 0.5rem;
    border-bottom: 1px solid var(--soft);
    vertical-align: middle;
  }}
  th {{
    background: rgba(88, 47, 14, 0.08);
    font-weight: 600;
  }}
  td.num {{ width: 3rem; font-variant-numeric: tabular-nums; opacity: 0.7; }}
  td.time {{ width: 5.5rem; font-variant-numeric: tabular-nums; font-family: 'Menlo', monospace; font-size: 0.82rem; }}
  td.dur {{ width: 4rem; font-variant-numeric: tabular-nums; opacity: 0.7; }}
  td.thumb {{ width: 90px; }}
  td.thumb img {{ width: 80px; height: 45px; object-fit: cover; border: 1px solid var(--soft); display: block; }}
  td.text {{ font-style: italic; }}
  tr.unmatched {{ background: rgba(220, 80, 60, 0.12); }}
  tr.unmatched td.text::before {{ content: "[UNMATCHED] "; font-weight: bold; color: #993322; }}
</style>
</head>
<body>
  <h1>Alignment Preview — {html.escape(slug)}</h1>
  <div class="meta">
    <span><strong>Audio duration:</strong> {_format_ts(audio_duration_s)}</span>
    <span><strong>Script words:</strong> {stats.get("script_words", 0)}</span>
    <span><strong>Match rate:</strong> {matched_pct:.1f}%</span>
    <span><strong>Phrases:</strong> {len(phrase_timings)}</span>
    <span><strong>Subtitle chunks:</strong> {len(subtitle_chunks)}</span>
  </div>

  <h2>Image timings (V3 track)</h2>
  <table>
    <thead><tr><th>#</th><th>Image</th><th>Start</th><th>End</th><th>Dur</th><th>Phrase</th></tr></thead>
    <tbody>
      {''.join(image_rows)}
    </tbody>
  </table>

  <h2>Subtitle chunks (Lora, bottom-center in DaVinci)</h2>
  <table>
    <thead><tr><th>#</th><th>Start</th><th>End</th><th>Dur</th><th>Text</th></tr></thead>
    <tbody>
      {''.join(sub_rows)}
    </tbody>
  </table>
</body>
</html>
"""
