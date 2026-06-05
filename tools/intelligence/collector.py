"""YouTube Data API v3 data collection."""

import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DISCOVERY_QUERIES = [
    "psychology shame",
    "mental health feelings",
    "emotional wellbeing",
    "anxiety psychology",
    "therapy psychology",
]

_ISO_RE = re.compile(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")


def _yt(api_key: str):
    return build("youtube", "v3", developerKey=api_key, cache_discovery=False)


def _parse_duration(iso: str) -> int:
    m = _ISO_RE.match(iso or "")
    if not m:
        return 0
    h, mn, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mn * 60 + s


def discover_channels(api_key: str, queries: list[str] | None = None) -> set[str]:
    """Search for channels matching each query, return unique channel IDs."""
    yt = _yt(api_key)
    queries = queries or DISCOVERY_QUERIES
    found = set()
    for q in queries:
        print(f"  Searching: {q!r}...")
        try:
            resp = yt.search().list(
                part="snippet",
                q=q,
                type="channel",
                maxResults=10,
                relevanceLanguage="pl",
                regionCode="PL",
            ).execute()
            for item in resp.get("items", []):
                found.add(item["snippet"]["channelId"])
        except HttpError as e:
            print(f"  Warning: search failed for {q!r} — {e}")
        time.sleep(0.3)
    return found


def fetch_channel_stats(api_key: str, channel_ids: list[str], sensum_id: str = "") -> dict:
    """Return {channel_id: dict} with subscriber count, name, etc."""
    yt = _yt(api_key)
    results = {}
    # API allows up to 50 IDs per call
    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i + 50]
        try:
            resp = yt.channels().list(
                part="snippet,statistics",
                id=",".join(batch),
            ).execute()
            for item in resp.get("items", []):
                cid = item["id"]
                stats = item.get("statistics", {})
                results[cid] = {
                    "channel_id": cid,
                    "name": item["snippet"]["title"],
                    "description": item["snippet"].get("description", "")[:500],
                    "subscribers": int(stats.get("subscriberCount", 0)),
                    "video_count": int(stats.get("videoCount", 0)),
                    "is_sensum": 1 if cid == sensum_id else 0,
                }
        except HttpError as e:
            print(f"  Warning: channels.list failed — {e}")
        time.sleep(0.2)
    return results


def _get_uploads_playlist(yt, channel_id: str) -> str | None:
    try:
        resp = yt.channels().list(
            part="contentDetails",
            id=channel_id,
        ).execute()
        items = resp.get("items", [])
        if items:
            return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    except HttpError:
        pass
    return None


def fetch_recent_videos(api_key: str, channel_id: str, days: int = 30) -> list[dict]:
    """Return videos published within the last `days` days for a channel."""
    yt = _yt(api_key)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    playlist_id = _get_uploads_playlist(yt, channel_id)
    if not playlist_id:
        return []

    video_ids = []
    next_page = None
    while True:
        try:
            kwargs = dict(part="snippet", playlistId=playlist_id, maxResults=50)
            if next_page:
                kwargs["pageToken"] = next_page
            resp = yt.playlistItems().list(**kwargs).execute()
        except HttpError as e:
            print(f"  Warning: playlistItems failed for {channel_id} — {e}")
            break

        reached_cutoff = False
        for item in resp.get("items", []):
            pub = item["snippet"].get("publishedAt", "")
            if pub < cutoff:
                reached_cutoff = True
                break
            vid = item["snippet"]["resourceId"].get("videoId")
            if vid:
                video_ids.append(vid)

        # Uploads playlists are newest-first: once we cross the cutoff every
        # later page is older still — stop paging instead of burning API quota.
        if reached_cutoff:
            break
        next_page = resp.get("nextPageToken")
        if not next_page:
            break
        time.sleep(0.2)

    if not video_ids:
        return []

    videos = []
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        try:
            resp = yt.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch),
            ).execute()
            for item in resp.get("items", []):
                stats = item.get("statistics", {})
                snippet = item["snippet"]
                thumbs = snippet.get("thumbnails", {})
                thumb_url = (
                    thumbs.get("high", thumbs.get("medium", thumbs.get("default", {}))).get("url", "")
                )
                videos.append({
                    "video_id": item["id"],
                    "channel_id": channel_id,
                    "title": snippet.get("title", ""),
                    "views": int(stats.get("viewCount", 0)),
                    "likes": int(stats.get("likeCount", 0)),
                    "comment_count": int(stats.get("commentCount", 0)),
                    "duration_seconds": _parse_duration(
                        item.get("contentDetails", {}).get("duration", "")
                    ),
                    "published_at": snippet.get("publishedAt", ""),
                    "tags": snippet.get("tags", []),
                    "thumbnail_url": thumb_url,
                    "thumbnail_style": "unknown",
                })
        except HttpError as e:
            print(f"  Warning: videos.list failed — {e}")
        time.sleep(0.2)

    return videos


def fetch_comments(api_key: str, video_ids: list[str], max_per_video: int = 50) -> list[dict]:
    """Fetch top comments for a list of video IDs."""
    yt = _yt(api_key)
    comments = []
    for vid in video_ids:
        try:
            resp = yt.commentThreads().list(
                part="snippet",
                videoId=vid,
                maxResults=min(max_per_video, 100),
                order="relevance",
                textFormat="plainText",
            ).execute()
            for item in resp.get("items", []):
                top = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "comment_id": item["id"],
                    "video_id": vid,
                    "text": top.get("textDisplay", ""),
                })
        except HttpError as e:
            if "commentsDisabled" not in str(e):
                print(f"  Warning: comments failed for {vid} — {e}")
        time.sleep(0.2)
    return comments


def download_thumbnails(videos: list[dict], dest_dir: Path) -> dict[str, Path]:
    """Download thumbnail JPEGs; return {video_id: local_path}."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for v in videos:
        url = v.get("thumbnail_url", "")
        vid = v["video_id"]
        if not url:
            url = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        dest = dest_dir / f"{vid}.jpg"
        if dest.exists():
            paths[vid] = dest
            continue
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                dest.write_bytes(r.content)
                paths[vid] = dest
        except Exception as e:
            print(f"  Warning: thumbnail download failed for {vid} — {e}")
    return paths
