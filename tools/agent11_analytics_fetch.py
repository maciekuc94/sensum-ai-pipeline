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
    """Convert ISO 8601 duration to total seconds. E.g. PT1H2M3S -> 3723."""
    pattern = r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?"
    m = re.match(pattern, iso)
    if not m:
        return 0
    hours = int(m.group(1) or 0)
    minutes = int(m.group(2) or 0)
    seconds = int(m.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


def _is_short(duration_seconds: int) -> bool:
    """Return True if the video qualifies as a YouTube Short (<=60 seconds)."""
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
            part="snippet,contentDetails",
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
    """Return traffic source breakdown as fractions summing to <=1.0."""
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


def _get_retention(yt_analytics, video_id: str, channel_id: str, is_short: bool) -> dict:
    """Return audience retention checkpoints. Shorts always return None values."""
    null_result = {"p25": None, "p50": None, "p75": None, "p100": None}

    if is_short:
        return null_result

    resp = yt_analytics.reports().query(
        ids=f"channel=={channel_id}",
        startDate="2000-01-01",  # retention curves require all-time range, not rolling window
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

    # deferred to avoid import-time OAuth side-effects during testing
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
