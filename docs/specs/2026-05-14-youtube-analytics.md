# YouTube Analytics Agents — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two new agents to the WAT pipeline — Agent 11 fetches YouTube channel analytics into JSON, Agent 12 analyzes it with Claude and pushes results to Google Sheets.

**Architecture:** Agent 11 is deterministic (no AI, no cost) — it authenticates with the YouTube channel Google account, calls YouTube Data API v3 + YouTube Analytics API, and writes `outputs/channel/analytics_latest.json`. Agent 12 reads that JSON, calls Claude Opus 4.7 for analysis, writes results to a Google Sheets dashboard (5 tabs), and saves a markdown report locally.

**Tech Stack:** Python 3.11+, google-api-python-client, google-auth-oauthlib, anthropic SDK, pytest, python-dotenv

---

### Task 1: Auth module + requirements.txt

**Files:**
- Create: `tools/youtube_auth.py`
- Modify: `requirements.txt`
- Create: `tests/test_analytics.py` (skeleton only)

- [ ] **Step 1: Add dependencies to requirements.txt**

Add these two lines to `requirements.txt`:
```
google-api-python-client
google-auth-oauthlib
```

- [ ] **Step 2: Create `tools/youtube_auth.py`**

```python
"""OAuth 2.0 auth for YouTube channel account (token_youtube.json)."""

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

_PROJECT_ROOT = Path(__file__).parent.parent
_CREDENTIALS_PATH = _PROJECT_ROOT / "credentials.json"
_TOKEN_PATH = _PROJECT_ROOT / "token_youtube.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_youtube_credentials() -> Credentials:
    """Return valid credentials for the YouTube channel account.

    On first call: opens browser for user to sign in with their YouTube channel
    Google account. Saves token to token_youtube.json.
    On subsequent calls: loads and refreshes token silently.
    """
    creds = None
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not _CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {_CREDENTIALS_PATH}\n"
                    "Download it from Google Cloud Console → APIs & Services → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(_CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(port=0)
        _TOKEN_PATH.write_text(creds.to_json())

    return creds


def build_youtube(creds: Credentials):
    """Return a YouTube Data API v3 client."""
    return build("youtube", "v3", credentials=creds)


def build_analytics(creds: Credentials):
    """Return a YouTube Analytics API v2 client."""
    return build("youtubeAnalytics", "v2", credentials=creds)


def build_sheets(creds: Credentials):
    """Return a Google Sheets API v4 client."""
    return build("sheets", "v4", credentials=creds)
```

- [ ] **Step 3: Create test skeleton `tests/test_analytics.py`**

```python
"""Tests for agent11 analytics fetch functions."""
import pytest
```

- [ ] **Step 4: Install dependencies and verify import**

```bash
pip install google-api-python-client google-auth-oauthlib
python -c "from tools.youtube_auth import get_youtube_credentials, build_youtube, build_analytics, build_sheets; print('OK')"
```

Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add requirements.txt tools/youtube_auth.py tests/test_analytics.py
git commit -m "feat: add YouTube OAuth auth module and test skeleton"
```

---

### Task 2: Core fetch functions (duration parsing, channel info, video IDs, video details)

**Files:**
- Create: `tools/agent11_analytics_fetch.py` (partial — only these functions)
- Modify: `tests/test_analytics.py`

- [ ] **Step 1: Write failing tests for `_parse_duration` and `_is_short`**

In `tests/test_analytics.py`:

```python
"""Tests for agent11 analytics fetch functions."""
import pytest
from unittest.mock import MagicMock


def test_parse_duration_seconds_only():
    from tools.agent11_analytics_fetch import _parse_duration
    assert _parse_duration("PT45S") == 45


def test_parse_duration_minutes_seconds():
    from tools.agent11_analytics_fetch import _parse_duration
    assert _parse_duration("PT1M30S") == 90


def test_parse_duration_hours_minutes_seconds():
    from tools.agent11_analytics_fetch import _parse_duration
    assert _parse_duration("PT1H2M3S") == 3723


def test_parse_duration_minutes_only():
    from tools.agent11_analytics_fetch import _parse_duration
    assert _parse_duration("PT5M") == 300


def test_is_short_true():
    from tools.agent11_analytics_fetch import _is_short
    assert _is_short(45) is True


def test_is_short_exactly_60():
    from tools.agent11_analytics_fetch import _is_short
    assert _is_short(60) is True


def test_is_short_false():
    from tools.agent11_analytics_fetch import _is_short
    assert _is_short(61) is False


def test_get_channel_info():
    from tools.agent11_analytics_fetch import _get_channel_info
    mock_youtube = MagicMock()
    mock_youtube.channels().list().execute.return_value = {
        "items": [{
            "id": "UCtest123",
            "statistics": {
                "subscriberCount": "42",
                "viewCount": "1000",
            },
            "contentDetails": {
                "relatedPlaylists": {"uploads": "UUtest123"}
            }
        }]
    }
    result = _get_channel_info(mock_youtube)
    assert result["channelId"] == "UCtest123"
    assert result["uploadsPlaylistId"] == "UUtest123"
    assert result["subscribers"] == 42
    assert result["totalViews"] == 1000


def test_get_video_ids():
    from tools.agent11_analytics_fetch import _get_video_ids
    mock_youtube = MagicMock()
    mock_youtube.playlistItems().list().execute.return_value = {
        "items": [
            {"contentDetails": {"videoId": "vid1"}},
            {"contentDetails": {"videoId": "vid2"}},
        ],
        "nextPageToken": None,
    }
    result = _get_video_ids(mock_youtube, "UUtest123")
    assert result == ["vid1", "vid2"]


def test_get_video_details():
    from tools.agent11_analytics_fetch import _get_video_details
    mock_youtube = MagicMock()
    mock_youtube.videos().list().execute.return_value = {
        "items": [{
            "id": "vid1",
            "snippet": {
                "title": "Test Video",
                "publishedAt": "2026-05-01T10:00:00Z",
            },
            "contentDetails": {"duration": "PT45S"},
        }]
    }
    result = _get_video_details(mock_youtube, ["vid1"])
    assert len(result) == 1
    assert result[0]["videoId"] == "vid1"
    assert result[0]["title"] == "Test Video"
    assert result[0]["durationSeconds"] == 45
    assert result[0]["isShort"] is True
    assert result[0]["publishedAt"] == "2026-05-01"
    assert result[0]["url"] == "https://youtu.be/vid1"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd "d:\ClaudeCode\YouTube psychology"
python -m pytest tests/test_analytics.py -v 2>&1 | head -30
```

Expected: All tests FAIL with ImportError or similar.

- [ ] **Step 3: Create `tools/agent11_analytics_fetch.py` with these functions**

```python
"""
Agent 11: YouTube Analytics Fetch
Collects channel + per-video metrics from YouTube APIs and writes JSON output.

Usage:
    python tools/agent11_analytics_fetch.py [--days 28]
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _parse_duration(iso: str) -> int:
    """Convert ISO 8601 duration to total seconds. E.g. PT1H2M3S → 3723."""
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    m = re.match(pattern, iso)
    if not m:
        return 0
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def _is_short(duration_seconds: int) -> bool:
    """Return True if the video qualifies as a YouTube Short (≤60 seconds)."""
    return duration_seconds <= 60


def _get_channel_info(youtube) -> dict:
    """Fetch channel ID, uploads playlist ID, subscriber count, total views."""
    resp = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        mine=True,
    ).execute()
    item = resp["items"][0]
    return {
        "channelId": item["id"],
        "uploadsPlaylistId": item["contentDetails"]["relatedPlaylists"]["uploads"],
        "subscribers": int(item["statistics"].get("subscriberCount", 0)),
        "totalViews": int(item["statistics"].get("viewCount", 0)),
    }


def _get_video_ids(youtube, uploads_playlist_id: str) -> list[str]:
    """Return all video IDs from the uploads playlist (paginated)."""
    video_ids: list[str] = []
    page_token = None

    while True:
        kwargs = dict(
            part="contentDetails",
            playlistId=uploads_playlist_id,
            maxResults=50,
        )
        if page_token:
            kwargs["pageToken"] = page_token

        resp = youtube.playlistItems().list(**kwargs).execute()
        for item in resp.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return video_ids


def _get_video_details(youtube, video_ids: list[str]) -> list[dict]:
    """Fetch metadata for video IDs in batches of 50."""
    videos: list[dict] = []

    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        resp = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=",".join(batch),
        ).execute()

        for item in resp.get("items", []):
            iso_duration = item["contentDetails"]["duration"]
            duration_sec = _parse_duration(iso_duration)
            published_raw = item["snippet"]["publishedAt"]  # e.g. "2026-05-01T10:00:00Z"
            published_date = published_raw[:10]  # keep YYYY-MM-DD only

            videos.append({
                "videoId": item["id"],
                "title": item["snippet"]["title"],
                "publishedAt": published_date,
                "durationSeconds": duration_sec,
                "isShort": _is_short(duration_sec),
                "url": f"https://youtu.be/{item['id']}",
            })

    return videos
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_analytics.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/agent11_analytics_fetch.py tests/test_analytics.py
git commit -m "feat: add agent11 core fetch functions with tests"
```

---

### Task 3: Analytics metrics functions (watch time, per-video metrics, traffic sources)

**Files:**
- Modify: `tools/agent11_analytics_fetch.py` (add three functions)
- Modify: `tests/test_analytics.py` (add tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/test_analytics.py`:

```python
def test_get_channel_watch_time():
    from tools.agent11_analytics_fetch import _get_channel_watch_time
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {
        "rows": [["2026-01-01", 12345.6]]
    }
    result = _get_channel_watch_time(mock_analytics, "UCtest123", 28)
    assert result == 12345.6


def test_get_channel_watch_time_no_data():
    from tools.agent11_analytics_fetch import _get_channel_watch_time
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {"rows": []}
    result = _get_channel_watch_time(mock_analytics, "UCtest123", 28)
    assert result == 0.0


def test_get_video_metrics():
    from tools.agent11_analytics_fetch import _get_video_metrics
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {
        "columnHeaders": [
            {"name": "views"}, {"name": "estimatedMinutesWatched"},
            {"name": "averageViewDuration"}, {"name": "impressions"},
            {"name": "impressionClickThroughRate"}, {"name": "subscribersGained"},
            {"name": "subscribersLost"},
        ],
        "rows": [[500, 1200.5, 144, 2000, 0.05, 3, 1]]
    }
    result = _get_video_metrics(mock_analytics, "vid1", "UCtest123", 28)
    assert result["views"] == 500
    assert result["watchTimeMinutes"] == 1200.5
    assert result["avgViewDurationSeconds"] == 144
    assert result["impressions"] == 2000
    assert abs(result["impressionCTR"] - 0.05) < 1e-6
    assert result["subscribersGained"] == 3
    assert result["subscribersLost"] == 1


def test_get_video_metrics_no_data():
    from tools.agent11_analytics_fetch import _get_video_metrics
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {}
    result = _get_video_metrics(mock_analytics, "vid1", "UCtest123", 28)
    assert result is None


def test_get_traffic_sources():
    from tools.agent11_analytics_fetch import _get_traffic_sources
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {
        "rows": [
            ["SHORTS", 300],
            ["YT_SEARCH", 100],
            ["SUGGESTED_VIDEOS", 50],
        ]
    }
    result = _get_traffic_sources(mock_analytics, "vid1", "UCtest123", 28)
    # Total = 450; SHORTS = 300/450 ≈ 0.667
    assert abs(result["SHORTS"] - 300 / 450) < 1e-6
    assert abs(result["YT_SEARCH"] - 100 / 450) < 1e-6
    assert abs(result["SUGGESTED"] - 50 / 450) < 1e-6
    assert result["EXTERNAL"] == 0.0
    assert result["DIRECT"] == 0.0
    assert result["OTHER"] == 0.0


def test_get_traffic_sources_empty():
    from tools.agent11_analytics_fetch import _get_traffic_sources
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {"rows": []}
    result = _get_traffic_sources(mock_analytics, "vid1", "UCtest123", 28)
    assert all(v == 0.0 for v in result.values())
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_analytics.py::test_get_channel_watch_time tests/test_analytics.py::test_get_video_metrics tests/test_analytics.py::test_get_traffic_sources -v
```

Expected: FAIL with ImportError or AttributeError.

- [ ] **Step 3: Add the three functions to `tools/agent11_analytics_fetch.py`**

Append after `_get_video_details`:

```python
def _get_channel_watch_time(yt_analytics, channel_id: str, days: int) -> float:
    """Fetch total channel watch time in minutes for the last `days` days."""
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()

    resp = yt_analytics.reports().query(
        ids=f"channel=={channel_id}",
        startDate=start_date,
        endDate=end_date,
        metrics="estimatedMinutesWatched",
        dimensions="day",
    ).execute()

    rows = resp.get("rows", [])
    if not rows:
        return 0.0
    return sum(float(row[1]) for row in rows)


def _get_video_metrics(yt_analytics, video_id: str, channel_id: str, days: int) -> dict | None:
    """Fetch per-video performance metrics for the last `days` days.

    Returns None if no data available (video too new or no impressions).
    """
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()

    resp = yt_analytics.reports().query(
        ids=f"channel=={channel_id}",
        startDate=start_date,
        endDate=end_date,
        metrics=(
            "views,estimatedMinutesWatched,averageViewDuration,"
            "impressions,impressionClickThroughRate,"
            "subscribersGained,subscribersLost"
        ),
        filters=f"video=={video_id}",
    ).execute()

    rows = resp.get("rows")
    if not rows:
        return None

    headers = [h["name"] for h in resp.get("columnHeaders", [])]
    row = rows[0]
    data = dict(zip(headers, row))

    return {
        "views": int(data.get("views", 0)),
        "watchTimeMinutes": float(data.get("estimatedMinutesWatched", 0)),
        "avgViewDurationSeconds": int(data.get("averageViewDuration", 0)),
        "impressions": int(data.get("impressions", 0)),
        "impressionCTR": float(data.get("impressionClickThroughRate", 0)),
        "subscribersGained": int(data.get("subscribersGained", 0)),
        "subscribersLost": int(data.get("subscribersLost", 0)),
    }


_TRAFFIC_SOURCE_MAP = {
    "SHORTS": "SHORTS",
    "YT_SEARCH": "YT_SEARCH",
    "SUGGESTED_VIDEOS": "SUGGESTED",
    "EXTERNAL": "EXTERNAL",
    "DIRECT": "DIRECT",
}


def _get_traffic_sources(yt_analytics, video_id: str, channel_id: str, days: int) -> dict:
    """Return traffic source breakdown as fractions summing to ≤1.0."""
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()

    resp = yt_analytics.reports().query(
        ids=f"channel=={channel_id}",
        startDate=start_date,
        endDate=end_date,
        metrics="views",
        dimensions="insightTrafficSourceType",
        filters=f"video=={video_id}",
    ).execute()

    raw: dict[str, int] = {}
    for row in resp.get("rows", []):
        source, views = row[0], int(row[1])
        raw[source] = views

    total = sum(raw.values())
    result = {"SHORTS": 0.0, "YT_SEARCH": 0.0, "SUGGESTED": 0.0, "EXTERNAL": 0.0, "DIRECT": 0.0, "OTHER": 0.0}

    if total == 0:
        return result

    for api_key, out_key in _TRAFFIC_SOURCE_MAP.items():
        if api_key in raw:
            result[out_key] = raw[api_key] / total

    # Aggregate everything not mapped into OTHER
    mapped_views = sum(raw.get(k, 0) for k in _TRAFFIC_SOURCE_MAP)
    result["OTHER"] = (total - mapped_views) / total

    return result
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/test_analytics.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/agent11_analytics_fetch.py tests/test_analytics.py
git commit -m "feat: add analytics metrics fetch functions with tests"
```

---

### Task 4: Retention function + run_agent11 orchestrator

**Files:**
- Modify: `tools/agent11_analytics_fetch.py` (add `_get_retention` + `run_agent11` + `main`)
- Modify: `tests/test_analytics.py` (add retention tests)

- [ ] **Step 1: Write failing tests for `_get_retention`**

Append to `tests/test_analytics.py`:

```python
def test_get_retention_short_returns_nulls():
    from tools.agent11_analytics_fetch import _get_retention
    mock_analytics = MagicMock()
    result = _get_retention(mock_analytics, "vid1", "UCtest123", is_short=True)
    assert result == {"p25": None, "p50": None, "p75": None, "p100": None}
    mock_analytics.reports().query.assert_not_called()


def test_get_retention_long_form():
    from tools.agent11_analytics_fetch import _get_retention
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {
        "rows": [
            [0.0, 1.0],
            [0.25, 0.72],
            [0.5, 0.55],
            [0.75, 0.41],
            [1.0, 0.28],
        ]
    }
    result = _get_retention(mock_analytics, "vid1", "UCtest123", is_short=False)
    assert abs(result["p25"] - 0.72) < 1e-6
    assert abs(result["p50"] - 0.55) < 1e-6
    assert abs(result["p75"] - 0.41) < 1e-6
    assert abs(result["p100"] - 0.28) < 1e-6


def test_get_retention_no_data():
    from tools.agent11_analytics_fetch import _get_retention
    mock_analytics = MagicMock()
    mock_analytics.reports().query().execute.return_value = {"rows": []}
    result = _get_retention(mock_analytics, "vid1", "UCtest123", is_short=False)
    assert result == {"p25": None, "p50": None, "p75": None, "p100": None}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python -m pytest tests/test_analytics.py::test_get_retention_short_returns_nulls tests/test_analytics.py::test_get_retention_long_form -v
```

Expected: FAIL.

- [ ] **Step 3: Add `_get_retention`, `run_agent11`, and `main` to `tools/agent11_analytics_fetch.py`**

Append to the file:

```python
def _get_retention(yt_analytics, video_id: str, channel_id: str, is_short: bool) -> dict:
    """Return audience retention checkpoints. Shorts always return None values."""
    null_result = {"p25": None, "p50": None, "p75": None, "p100": None}

    if is_short:
        return null_result

    resp = yt_analytics.reports().query(
        ids=f"channel=={channel_id}",
        startDate="2000-01-01",
        endDate=date.today().isoformat(),
        metrics="audienceWatchRatio",
        dimensions="elapsedVideoTimeRatio",
        filters=f"video=={video_id}",
    ).execute()

    rows = resp.get("rows", [])
    if not rows:
        return null_result

    # rows: [[ratio, watchFraction], ...] sorted by ratio ascending
    ratio_map = {float(r[0]): float(r[1]) for r in rows}

    def _closest(target: float) -> float | None:
        if not ratio_map:
            return None
        closest_key = min(ratio_map.keys(), key=lambda k: abs(k - target))
        return ratio_map[closest_key]

    return {
        "p25": _closest(0.25),
        "p50": _closest(0.50),
        "p75": _closest(0.75),
        "p100": _closest(1.00),
    }


def run_agent11(days: int = 28) -> None:
    """Fetch all channel analytics and write JSON output files."""
    print(f"\n=== Agent 11: YouTube Analytics Fetch ===")
    print(f"Date range: last {days} days\n")

    from tools.youtube_auth import get_youtube_credentials, build_youtube, build_analytics

    print("[1/5] Authenticating with YouTube account...")
    creds = get_youtube_credentials()
    youtube = build_youtube(creds)
    yt_analytics = build_analytics(creds)

    print("[2/5] Fetching channel info...")
    channel_info = _get_channel_info(youtube)
    channel_id = channel_info["channelId"]
    print(f"  Channel ID : {channel_id}")
    print(f"  Subscribers: {channel_info['subscribers']}")

    print("[3/5] Fetching video list...")
    video_ids = _get_video_ids(youtube, channel_info["uploadsPlaylistId"])
    video_details = _get_video_details(youtube, video_ids)
    print(f"  Videos found: {len(video_details)}")

    print("[4/5] Fetching channel watch time...")
    total_watch_time = _get_channel_watch_time(yt_analytics, channel_id, days)
    channel_info["totalWatchTimeMinutes"] = total_watch_time

    print("[5/5] Fetching per-video analytics...")
    videos: list[dict] = []
    for vd in video_details:
        vid = vd["videoId"]
        title_short = vd["title"][:40]
        print(f"  {title_short}{'...' if len(vd['title']) > 40 else ''}")

        metrics = _get_video_metrics(yt_analytics, vid, channel_id, days)
        if metrics is None:
            print(f"    Warning: no analytics data yet for {vid}")
            metrics = {
                "views": 0, "watchTimeMinutes": 0.0, "avgViewDurationSeconds": 0,
                "impressions": 0, "impressionCTR": 0.0,
                "subscribersGained": 0, "subscribersLost": 0,
            }

        traffic = _get_traffic_sources(yt_analytics, vid, channel_id, days)
        retention = _get_retention(yt_analytics, vid, channel_id, vd["isShort"])

        videos.append({**vd, "metrics": metrics, "trafficSources": traffic, "retention": retention})

    # Build output
    fetched_at = datetime.now().isoformat(timespec="seconds")
    output = {
        "fetched_at": fetched_at,
        "days": days,
        "channel": channel_info,
        "videos": videos,
    }

    # Write outputs
    output_base = Path(__file__).parent.parent / "outputs" / "channel"
    output_base.mkdir(parents=True, exist_ok=True)

    today_str = date.today().isoformat()
    dated_path = output_base / f"analytics_{today_str}.json"
    latest_path = output_base / "analytics_latest.json"

    json_content = json.dumps(output, indent=2, ensure_ascii=False)
    dated_path.write_text(json_content, encoding="utf-8")
    latest_path.write_text(json_content, encoding="utf-8")

    print(f"\nSaved: {dated_path}")
    print(f"Saved: {latest_path}")
    print(f"\nDone. {len(videos)} videos fetched.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch YouTube channel analytics.")
    parser.add_argument("--days", type=int, default=28, help="Analytics window in days (default: 28)")
    args = parser.parse_args()
    run_agent11(days=args.days)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run all tests**

```bash
python -m pytest tests/test_analytics.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/agent11_analytics_fetch.py tests/test_analytics.py
git commit -m "feat: add retention function and run_agent11 orchestrator"
```

---

### Task 5: Agent 12 — Claude prompt builder + API call

**Files:**
- Create: `tools/agent12_analytics_report.py` (partial — prompt builder + Claude call only)
- Modify: `tests/test_analytics.py` (add prompt test)

- [ ] **Step 1: Write failing test for `_build_analysis_prompt`**

Append to `tests/test_analytics.py`:

```python
def test_build_analysis_prompt_contains_required_sections():
    from tools.agent12_analytics_report import _build_analysis_prompt
    sample_data = {
        "fetched_at": "2026-05-14T10:00:00",
        "days": 28,
        "channel": {"channelId": "UCtest", "subscribers": 42, "totalViews": 500, "totalWatchTimeMinutes": 120.0},
        "videos": [
            {
                "videoId": "vid1",
                "title": "Test Video",
                "publishedAt": "2026-05-01",
                "durationSeconds": 600,
                "isShort": False,
                "metrics": {"views": 300, "impressions": 1000, "impressionCTR": 0.05,
                            "avgViewDurationSeconds": 180, "watchTimeMinutes": 90.0,
                            "subscribersGained": 2, "subscribersLost": 0},
                "trafficSources": {"SHORTS": 0.0, "YT_SEARCH": 0.5, "SUGGESTED": 0.3,
                                   "EXTERNAL": 0.1, "DIRECT": 0.1, "OTHER": 0.0},
                "retention": {"p25": 0.8, "p50": 0.6, "p75": 0.45, "p100": 0.3},
            }
        ]
    }
    prompt = _build_analysis_prompt(sample_data)
    assert "What's working" in prompt or "what's working" in prompt.lower()
    assert "recommendation" in prompt.lower()
    assert "watch" in prompt.lower()
    assert "vid1" in prompt or "Test Video" in prompt
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_analytics.py::test_build_analysis_prompt_contains_required_sections -v
```

Expected: FAIL with ImportError.

- [ ] **Step 3: Create `tools/agent12_analytics_report.py` with prompt builder and Claude call**

```python
"""
Agent 12: YouTube Analytics Report
Reads analytics_latest.json, calls Claude for insights, writes to Google Sheets
and a local markdown report.

Usage:
    python tools/agent12_analytics_report.py
"""

import json
import os
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.utils import get_env, log_cost

CLAUDE_MODEL = "claude-opus-4-7"
_PROJECT_ROOT = Path(__file__).parent.parent
_ANALYTICS_PATH = _PROJECT_ROOT / "outputs" / "channel" / "analytics_latest.json"


def _build_analysis_prompt(data: dict) -> str:
    """Build the Claude prompt from analytics JSON data."""
    channel = data["channel"]
    videos = data["videos"]
    days = data.get("days", 28)

    video_summaries = []
    for v in videos:
        m = v["metrics"]
        r = v["retention"]
        t = v["trafficSources"]
        kind = "Short" if v["isShort"] else "Long-form"
        retention_str = (
            f"retention p25={r['p25']:.0%} p50={r['p50']:.0%} p75={r['p75']:.0%} p100={r['p100']:.0%}"
            if r["p25"] is not None else "retention=N/A (Short)"
        )
        top_traffic = sorted(t.items(), key=lambda x: x[1], reverse=True)[:3]
        traffic_str = ", ".join(f"{k}={v2:.0%}" for k, v2 in top_traffic if v2 > 0)
        video_summaries.append(
            f"- [{kind}] \"{v['title']}\" ({v['videoId']})\n"
            f"  published={v['publishedAt']} duration={v['durationSeconds']}s\n"
            f"  views={m['views']} impressions={m['impressions']} CTR={m['impressionCTR']:.1%}\n"
            f"  avgViewDuration={m['avgViewDurationSeconds']}s watchTime={m['watchTimeMinutes']:.0f}min\n"
            f"  subscribersGained={m['subscribersGained']} subscribersLost={m['subscribersLost']}\n"
            f"  {retention_str}\n"
            f"  traffic: {traffic_str or 'no data'}"
        )

    videos_block = "\n\n".join(video_summaries)

    return f"""\
You are analyzing YouTube performance data for SENSUM, a new psychology education channel.
Brand promise: "You are not broken. Here's what the science says."
The creator is not a YouTube analytics expert — use plain language, no jargon.

## Channel Overview (last {days} days)
Subscribers: {channel['subscribers']}
Total views (all time): {channel['totalViews']}
Watch time this period: {channel['totalWatchTimeMinutes']:.0f} minutes
Data fetched: {data['fetched_at']}

## Videos
{videos_block}

---

## Your Task

Analyze the data above and provide:

1. **What's Working** — identify the single strongest-performing video or Short and explain specifically WHY it's doing well (point to CTR, retention, or traffic source driving it). Be specific about the numbers.

2. **What Needs Attention** — flag the single weakest metric across all content and name the most likely cause. Be specific.

3. **Shorts vs Long-Form** — given the data, which format is getting more traction right now? Give a direct opinion the creator can act on.

4. **3 Concrete Recommendations** — for the NEXT upload specifically. Each recommendation must be actionable (title direction, thumbnail angle, topic, format, or length). Reference the data to justify each.

5. **Watch-Time Flag** — if any video has audience retention below 40% at the 50% mark, call it out by name and suggest one structural fix (e.g., move the hook earlier, cut the intro, add a chapter break).

Write in plain English. No bullet-point headers without content. No "it's too early to tell" hedging — give your best read of the data as it stands.
"""


def _call_claude(prompt: str) -> str:
    """Call Claude Opus 4.7 and return the response text."""
    import anthropic
    client = anthropic.Anthropic(api_key=get_env("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text, message.usage
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_analytics.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/agent12_analytics_report.py tests/test_analytics.py
git commit -m "feat: add agent12 prompt builder and Claude API call"
```

---

### Task 6: Agent 12 — Google Sheets integration

**Files:**
- Modify: `tools/agent12_analytics_report.py` (add all Sheets functions)

NOTE: This task does not require new tests — the Sheets functions involve complex API interactions that are better verified end-to-end. The existing test suite covers the logic-heavy parts.

- [ ] **Step 1: Add Sheets helper functions to `tools/agent12_analytics_report.py`**

After the `_call_claude` function, append:

```python
def _get_or_create_sheet(sheets_service) -> str:
    """Return ANALYTICS_SHEET_ID from .env, or create a new spreadsheet and save the ID."""
    from dotenv import set_key

    sheet_id = os.getenv("ANALYTICS_SHEET_ID", "").strip()
    if sheet_id:
        return sheet_id

    # Create new spreadsheet in the user's YouTube account Drive
    body = {"properties": {"title": "SENSUM Analytics"}}
    resp = sheets_service.spreadsheets().create(
        body=body, fields="spreadsheetId,spreadsheetUrl"
    ).execute()
    sheet_id = resp["spreadsheetId"]
    sheet_url = resp.get("spreadsheetUrl", f"https://docs.google.com/spreadsheets/d/{sheet_id}")

    # Persist to .env so future runs reuse the same sheet
    env_path = str(_PROJECT_ROOT / ".env")
    set_key(env_path, "ANALYTICS_SHEET_ID", sheet_id)
    os.environ["ANALYTICS_SHEET_ID"] = sheet_id

    print(f"  Created new spreadsheet: {sheet_url}")
    return sheet_id


_TAB_NAMES = ["Overview", "Videos", "Traffic Sources", "Retention", "AI Insights"]


def _ensure_tabs(sheets_service, sheet_id: str) -> None:
    """Create any missing tabs in the spreadsheet."""
    meta = sheets_service.spreadsheets().get(spreadsheetId=sheet_id).execute()
    existing = {s["properties"]["title"] for s in meta.get("sheets", [])}

    requests = []
    for tab in _TAB_NAMES:
        if tab not in existing:
            requests.append({"addSheet": {"properties": {"title": tab}}})

    if requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=sheet_id,
            body={"requests": requests},
        ).execute()


def _clear_and_write(sheets_service, sheet_id: str, tab: str, rows: list[list]) -> None:
    """Clear a tab and write rows starting at A1."""
    range_name = f"'{tab}'!A1"
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=sheet_id, range=f"'{tab}'"
    ).execute()
    sheets_service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()


def _write_overview(sheets_service, sheet_id: str, data: dict) -> None:
    channel = data["channel"]
    rows = [
        ["SENSUM Analytics — Overview"],
        ["Last updated", data["fetched_at"]],
        ["Days window", data["days"]],
        [],
        ["Metric", "Value"],
        ["Subscribers", channel["subscribers"]],
        ["Total views (all time)", channel["totalViews"]],
        ["Watch time this period (min)", round(channel["totalWatchTimeMinutes"], 1)],
        ["Videos tracked", len(data["videos"])],
    ]
    _clear_and_write(sheets_service, sheet_id, "Overview", rows)


def _write_videos(sheets_service, sheet_id: str, data: dict) -> None:
    header = [
        "Video ID", "Title", "Published", "Duration (s)", "Type",
        "Views", "Impressions", "CTR", "Avg View Duration (s)",
        "Watch Time (min)", "Subs Gained", "Subs Lost", "URL",
    ]
    rows = [header]
    for v in data["videos"]:
        m = v["metrics"]
        rows.append([
            v["videoId"], v["title"], v["publishedAt"], v["durationSeconds"],
            "Short" if v["isShort"] else "Long-form",
            m["views"], m["impressions"], round(m["impressionCTR"], 4),
            m["avgViewDurationSeconds"], round(m["watchTimeMinutes"], 1),
            m["subscribersGained"], m["subscribersLost"], v["url"],
        ])
    _clear_and_write(sheets_service, sheet_id, "Videos", rows)


def _write_traffic_sources(sheets_service, sheet_id: str, data: dict) -> None:
    header = ["Video ID", "Title", "Shorts", "YT Search", "Suggested", "External", "Direct", "Other"]
    rows = [header]
    for v in data["videos"]:
        t = v["trafficSources"]
        rows.append([
            v["videoId"], v["title"],
            round(t["SHORTS"], 4), round(t["YT_SEARCH"], 4), round(t["SUGGESTED"], 4),
            round(t["EXTERNAL"], 4), round(t["DIRECT"], 4), round(t["OTHER"], 4),
        ])
    _clear_and_write(sheets_service, sheet_id, "Traffic Sources", rows)


def _write_retention(sheets_service, sheet_id: str, data: dict) -> None:
    header = ["Video ID", "Title", "Type", "p25", "p50", "p75", "p100"]
    rows = [header]
    for v in data["videos"]:
        r = v["retention"]
        rows.append([
            v["videoId"], v["title"],
            "Short" if v["isShort"] else "Long-form",
            r["p25"] if r["p25"] is not None else "N/A",
            r["p50"] if r["p50"] is not None else "N/A",
            r["p75"] if r["p75"] is not None else "N/A",
            r["p100"] if r["p100"] is not None else "N/A",
        ])
    _clear_and_write(sheets_service, sheet_id, "Retention", rows)


def _append_ai_insights(sheets_service, sheet_id: str, insights: str, run_date: str) -> None:
    """Append a date-stamped AI insights block to the AI Insights tab (never overwrite)."""
    rows = [
        [f"=== Analysis run: {run_date} ==="],
        [insights],
        [""],  # blank spacer row
    ]
    sheets_service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range="'AI Insights'!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()
```

- [ ] **Step 2: Run all existing tests to confirm nothing broke**

```bash
python -m pytest tests/test_analytics.py -v
```

Expected: All tests PASS.

- [ ] **Step 3: Commit**

```bash
git add tools/agent12_analytics_report.py
git commit -m "feat: add Google Sheets integration functions to agent12"
```

---

### Task 7: Agent 12 — run_agent12 orchestrator + markdown report writer

**Files:**
- Modify: `tools/agent12_analytics_report.py` (add `_write_markdown_report`, `run_agent12`, `main`)

- [ ] **Step 1: Append to `tools/agent12_analytics_report.py`**

```python
def _write_markdown_report(insights: str, data: dict, run_date: str) -> Path:
    """Write a markdown mirror of the Claude analysis to outputs/channel/."""
    channel = data["channel"]
    n_videos = len(data["videos"])
    n_shorts = sum(1 for v in data["videos"] if v["isShort"])
    n_longform = n_videos - n_shorts

    content = f"""\
# SENSUM Analytics Report — {run_date}

**Channel:** {channel.get('channelId', 'unknown')}  
**Subscribers:** {channel['subscribers']}  
**Total views (all time):** {channel['totalViews']}  
**Watch time this period:** {channel['totalWatchTimeMinutes']:.0f} min  
**Videos tracked:** {n_videos} ({n_longform} long-form, {n_shorts} Shorts)  
**Data fetched:** {data['fetched_at']}

---

## AI Analysis

{insights}

---

_Generated by Agent 12 · SENSUM WAT pipeline_
"""
    output_path = _PROJECT_ROOT / "outputs" / "channel" / f"12_report_{run_date}.md"
    output_path.write_text(content, encoding="utf-8")
    return output_path


def run_agent12() -> None:
    """Read analytics JSON, call Claude, write Sheets dashboard + markdown report."""
    print(f"\n=== Agent 12: YouTube Analytics Report ===\n")

    # Step 1 — Load analytics data
    if not _ANALYTICS_PATH.exists():
        print(f"Error: {_ANALYTICS_PATH} not found.")
        print("Run Agent 11 first:  python tools/agent11_analytics_fetch.py")
        sys.exit(1)

    data = json.loads(_ANALYTICS_PATH.read_text(encoding="utf-8"))
    print(f"[1/4] Loaded analytics: {len(data['videos'])} videos, fetched {data['fetched_at']}")

    # Step 2 — Call Claude
    print(f"\n[2/4] Calling {CLAUDE_MODEL} for analysis...")
    prompt = _build_analysis_prompt(data)
    try:
        insights, usage = _call_claude(prompt)
    except Exception as exc:
        print(f"\nError: Claude API call failed — {exc}")
        sys.exit(1)

    log_cost("channel", "agent12", {
        "model": CLAUDE_MODEL,
        "input_tokens": usage.input_tokens,
        "output_tokens": usage.output_tokens,
    })
    print(f"  Response: {len(insights):,} chars")

    # Step 3 — Write Google Sheets
    print(f"\n[3/4] Writing Google Sheets dashboard...")
    from tools.youtube_auth import get_youtube_credentials, build_sheets

    creds = get_youtube_credentials()
    sheets_service = build_sheets(creds)

    sheet_id = _get_or_create_sheet(sheets_service)
    print(f"  Sheet ID: {sheet_id}")

    _ensure_tabs(sheets_service, sheet_id)
    _write_overview(sheets_service, sheet_id, data)
    _write_videos(sheets_service, sheet_id, data)
    _write_traffic_sources(sheets_service, sheet_id, data)
    _write_retention(sheets_service, sheet_id, data)

    run_date = date.today().isoformat()
    _append_ai_insights(sheets_service, sheet_id, insights, run_date)
    print(f"  All 5 tabs written.")
    print(f"  Open: https://docs.google.com/spreadsheets/d/{sheet_id}")

    # Step 4 — Write markdown report
    print(f"\n[4/4] Writing markdown report...")
    report_path = _write_markdown_report(insights, data, run_date)
    print(f"  Saved: {report_path}")

    print(f"\nDone.")


def main() -> None:
    run_agent12()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run all tests**

```bash
python -m pytest tests/test_analytics.py -v
```

Expected: All tests PASS.

- [ ] **Step 3: Verify the scripts are importable**

```bash
python -c "import tools.agent11_analytics_fetch; import tools.agent12_analytics_report; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add tools/agent12_analytics_report.py
git commit -m "feat: add run_agent12 orchestrator and markdown report writer"
```

---

### Task 8: Workflow documentation

**Files:**
- Create: `workflows/11_analytics_fetch.md`
- Create: `workflows/12_analytics_report.md`

- [ ] **Step 1: Create `workflows/11_analytics_fetch.md`**

```markdown
# Agent 11: Analytics Fetch — SOP

## Objective

Fetch YouTube channel and per-video performance data and write it to
`outputs/channel/analytics_latest.json`. Deterministic, no AI, no cost.

---

## Prerequisites

- Google Cloud Console: YouTube Data API v3, YouTube Analytics API, and
  Google Sheets API must be enabled in your GCP project
- `credentials.json` in project root (download from GCP → APIs & Services → Credentials)
- Python environment with `pip install -r requirements.txt`

---

## First Run (browser auth)

On the first run, a browser window opens. Sign in with your **YouTube channel Google account**
(not your Vertex AI / GCP account). This creates `token_youtube.json`.
All subsequent runs are silent.

---

## Usage

```bash
python tools/agent11_analytics_fetch.py
# OR with custom window:
python tools/agent11_analytics_fetch.py --days 90
```

**Output:**
- `outputs/channel/analytics_YYYY-MM-DD.json` — date-stamped archive
- `outputs/channel/analytics_latest.json` — always current (Agent 12 reads this)

---

## Edge Cases

| Situation | Behaviour |
|---|---|
| Video has no analytics yet | Logs warning, stores zeros for that video |
| Shorts | `isShort: true`; retention returns null values (API limitation) |
| Rate limit | Google APIs will throw; re-run after a few minutes |
| `token_youtube.json` expired | Auto-refreshes silently |

---

## Cost

YouTube Data API and Analytics API are free (quota-based).
Default quota: 10,000 units/day. Each run uses ~50–100 units.
```

- [ ] **Step 2: Create `workflows/12_analytics_report.md`**

```markdown
# Agent 12: Analytics Report — SOP

## Objective

Read `analytics_latest.json` (from Agent 11), call Claude Opus 4.7 for analysis,
and push results to a "SENSUM Analytics" Google Sheets dashboard.

---

## Prerequisites

- Agent 11 must have run successfully
- `ANTHROPIC_API_KEY` in `.env`
- Google authentication via Agent 11 (shares `token_youtube.json`)

---

## Usage

```bash
python tools/agent12_analytics_report.py
```

**Output:**
- Google Sheets dashboard (URL printed on first run, ID saved to `.env` as `ANALYTICS_SHEET_ID`)
- `outputs/channel/12_report_YYYY-MM-DD.md` — markdown mirror

---

## Google Sheets Structure

| Tab | Updated | Contents |
|---|---|---|
| Overview | Overwrite | Channel totals |
| Videos | Overwrite | One row per video |
| Traffic Sources | Overwrite | Traffic breakdown |
| Retention | Overwrite | Retention checkpoints |
| AI Insights | Append | Date-stamped Claude analysis |

---

## Running the Full Pipeline

```bash
python tools/agent11_analytics_fetch.py
python tools/agent12_analytics_report.py
```

---

## Cost

~$0.11 per run (1× Claude Opus 4.7 call, ~2,000 input + ~1,000 output tokens).
```

- [ ] **Step 3: Commit**

```bash
git add workflows/11_analytics_fetch.md workflows/12_analytics_report.md
git commit -m "docs: add workflow SOPs for Agent 11 and Agent 12"
```
