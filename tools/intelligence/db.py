"""SQLite storage for the weekly intelligence pipeline."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path


def init_db(db_path: Path) -> None:
    con = sqlite3.connect(str(db_path))
    con.executescript("""
        CREATE TABLE IF NOT EXISTS channels (
            channel_id   TEXT PRIMARY KEY,
            name         TEXT,
            subscribers  INTEGER,
            video_count  INTEGER,
            description  TEXT,
            is_sensum    INTEGER DEFAULT 0,
            first_seen   TEXT,
            last_updated TEXT
        );

        CREATE TABLE IF NOT EXISTS videos (
            video_id         TEXT PRIMARY KEY,
            channel_id       TEXT,
            title            TEXT,
            views            INTEGER,
            likes            INTEGER,
            comment_count    INTEGER,
            duration_seconds INTEGER,
            published_at     TEXT,
            tags             TEXT,
            thumbnail_url    TEXT,
            thumbnail_style  TEXT,
            collected_at     TEXT,
            FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
        );

        CREATE TABLE IF NOT EXISTS comments (
            comment_id   TEXT PRIMARY KEY,
            video_id     TEXT,
            text         TEXT,
            collected_at TEXT,
            FOREIGN KEY (video_id) REFERENCES videos(video_id)
        );

        CREATE TABLE IF NOT EXISTS weekly_snapshots (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            week_label   TEXT,
            channel_id   TEXT,
            subscribers  INTEGER,
            total_videos INTEGER,
            snapshot_at  TEXT
        );
    """)
    con.commit()
    con.close()


def upsert_channel(db_path: Path, ch: dict) -> None:
    con = sqlite3.connect(str(db_path))
    now = datetime.utcnow().isoformat()
    con.execute("""
        INSERT INTO channels (channel_id, name, subscribers, video_count, description,
                              is_sensum, first_seen, last_updated)
        VALUES (:channel_id, :name, :subscribers, :video_count, :description,
                :is_sensum, :first_seen, :last_updated)
        ON CONFLICT(channel_id) DO UPDATE SET
            name         = excluded.name,
            subscribers  = excluded.subscribers,
            video_count  = excluded.video_count,
            description  = excluded.description,
            last_updated = excluded.last_updated
    """, {**ch, "first_seen": now, "last_updated": now})
    con.commit()
    con.close()


def upsert_video(db_path: Path, v: dict) -> None:
    con = sqlite3.connect(str(db_path))
    con.execute("""
        INSERT INTO videos (video_id, channel_id, title, views, likes, comment_count,
                            duration_seconds, published_at, tags, thumbnail_url,
                            thumbnail_style, collected_at)
        VALUES (:video_id, :channel_id, :title, :views, :likes, :comment_count,
                :duration_seconds, :published_at, :tags, :thumbnail_url,
                :thumbnail_style, :collected_at)
        ON CONFLICT(video_id) DO UPDATE SET
            views           = excluded.views,
            likes           = excluded.likes,
            comment_count   = excluded.comment_count,
            thumbnail_style = excluded.thumbnail_style,
            collected_at    = excluded.collected_at
    """, {
        **v,
        "tags": json.dumps(v.get("tags", [])),
        "collected_at": datetime.utcnow().isoformat(),
    })
    con.commit()
    con.close()


def insert_comments(db_path: Path, comments: list[dict]) -> None:
    if not comments:
        return
    con = sqlite3.connect(str(db_path))
    now = datetime.utcnow().isoformat()
    con.executemany("""
        INSERT OR IGNORE INTO comments (comment_id, video_id, text, collected_at)
        VALUES (:comment_id, :video_id, :text, :collected_at)
    """, [{**c, "collected_at": now} for c in comments])
    con.commit()
    con.close()


def save_snapshot(db_path: Path, week_label: str, channels: dict) -> None:
    con = sqlite3.connect(str(db_path))
    now = datetime.utcnow().isoformat()
    rows = [
        (week_label, cid, ch["subscribers"], ch.get("video_count", 0), now)
        for cid, ch in channels.items()
    ]
    con.executemany("""
        INSERT INTO weekly_snapshots (week_label, channel_id, subscribers, total_videos, snapshot_at)
        VALUES (?, ?, ?, ?, ?)
    """, rows)
    con.commit()
    con.close()


def get_prev_snapshot(db_path: Path, week_label: str) -> dict:
    """Return subscriber counts from the snapshot immediately before week_label."""
    con = sqlite3.connect(str(db_path))
    rows = con.execute("""
        SELECT channel_id, subscribers FROM weekly_snapshots
        WHERE week_label < ? ORDER BY snapshot_at DESC
    """, (week_label,)).fetchall()
    con.close()
    seen = {}
    for cid, subs in rows:
        if cid not in seen:
            seen[cid] = subs
    return seen
