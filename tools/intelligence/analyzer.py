"""Eight analytical dimensions for the niche intelligence report."""

import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# --------------------------------------------------------------------------- #
# Word lists
# --------------------------------------------------------------------------- #

STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "it", "its", "be", "was",
    "are", "were", "been", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "can", "you",
    "your", "we", "our", "i", "my", "me", "he", "she", "they", "them",
    "this", "that", "these", "those", "what", "why", "how", "when", "if",
    "not", "no", "more", "most", "all", "just", "so", "out", "about",
    "up", "into", "than", "then", "there", "here", "like", "know", "get",
    "make", "take", "think", "feel", "need", "want", "stop", "start",
    "going", "come", "new", "one", "two", "time", "never", "always",
    "actually", "really", "very", "much", "even", "also", "still", "back",
    "way", "life", "people", "things", "thing", "day", "every", "other",
    "its", "their", "them", "who", "which", "dont", "cant", "im", "ive",
    "youre", "theyre", "its", "doesnt", "isnt", "wasnt",
}

FEELING_WORDS = [
    "ashamed", "shame", "embarrassed", "guilty", "humiliated", "disgrace",
    "relieved", "relief", "lighter", "better", "okay", "fine",
    "seen", "understood", "validated", "heard", "recognized", "witnessed",
    "hopeful", "hope", "hopeless", "optimistic", "pessimistic",
    "broken", "damaged", "worthless", "failed", "failure", "useless",
    "grateful", "thankful", "appreciate", "appreciation",
    "confused", "lost", "overwhelmed", "stuck", "paralyzed",
    "angry", "anger", "frustrated", "frustration", "resentful", "rage",
    "sad", "grief", "grieving", "mourning", "depressed", "depression",
    "anxious", "anxiety", "worried", "worry", "fear", "scared", "panic",
    "lonely", "alone", "isolated", "disconnected", "abandoned",
    "loved", "love", "cared", "supported", "safe", "belonging",
    "numb", "empty", "hollow", "void", "detached",
    "crying", "tears", "cried", "weeping",
    "exhausted", "tired", "burnout", "burned", "drained",
    "healing", "healed", "recovered", "better", "growing",
    "hurt", "pain", "painful", "suffering", "wounded",
    "proud", "pride", "accomplished", "worthy", "enough",
]

EMOTIONAL_TRIGGER_WORDS = [
    "shame", "ashamed", "guilty", "broken", "wrong", "normal",
    "anxiety", "anxious", "worry", "fear", "panic",
    "depression", "depressed", "sad", "grief",
    "trauma", "hurt", "pain", "healing",
    "lonely", "alone", "isolated", "loneliness",
    "failure", "failed", "worthless", "enough", "valid",
    "love", "attachment", "connection", "belonging",
    "anger", "rage", "frustration", "resentment",
    "exhausted", "burnout", "overwhelmed", "tired",
    "sensitive", "emotional", "feeling", "feelings",
    "permission", "allowed", "okay", "normal", "human",
    "crying", "tears", "sensitive",
    "psychology", "science", "research", "brain",
    "why", "understand", "explain", "reason",
]


# --------------------------------------------------------------------------- #
# Dimension 1 — Trending topics
# --------------------------------------------------------------------------- #

def trending_topics(videos: list[dict], top_n: int = 40) -> Counter:
    """Word frequency across all video titles, stop-word filtered."""
    counts: Counter = Counter()
    for v in videos:
        words = re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", v.get("title", "").lower())
        for w in words:
            w = w.strip("'")
            if len(w) > 3 and w not in STOP_WORDS:
                counts[w] += 1
    return Counter(dict(counts.most_common(top_n)))


# --------------------------------------------------------------------------- #
# Dimension 2 — View velocity
# --------------------------------------------------------------------------- #

def view_velocity(videos: list[dict]) -> list[dict]:
    """Sort videos by views-per-day since publish (highest first)."""
    now = datetime.now(timezone.utc)
    scored = []
    for v in videos:
        pub = v.get("published_at", "")
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            days_live = max((now - dt).days, 1)
        except (ValueError, TypeError):
            days_live = 30
        velocity = v.get("views", 0) / days_live
        scored.append({**v, "velocity": round(velocity, 1), "days_live": days_live})
    return sorted(scored, key=lambda x: x["velocity"], reverse=True)


# --------------------------------------------------------------------------- #
# Dimension 3 — Engagement rate
# --------------------------------------------------------------------------- #

def engagement_rate(videos: list[dict]) -> dict[str, float]:
    """(likes + comments) / views per video. Returns {video_id: rate}."""
    rates = {}
    for v in videos:
        views = v.get("views", 0)
        if views == 0:
            rates[v["video_id"]] = 0.0
        else:
            rate = (v.get("likes", 0) + v.get("comment_count", 0)) / views
            rates[v["video_id"]] = round(rate * 100, 3)  # as percentage
    return rates


# --------------------------------------------------------------------------- #
# Dimension 4 — Content gaps
# --------------------------------------------------------------------------- #

def content_gaps(videos: list[dict], corpus_dir: Path, top_n: int = 10) -> list[dict]:
    """
    Topics with high engagement in the niche that SENSUM hasn't covered yet.
    Compares top competitor title words against SENSUM corpus scripts.
    """
    corpus_words: set[str] = set()
    for slug_dir in corpus_dir.iterdir():
        if not slug_dir.is_dir():
            continue
        script = slug_dir / "md" / "script_corrected.md"
        if not script.exists():
            script = slug_dir / "md" / "04_final.md"
        if not script.exists():
            continue
        text = script.read_text(encoding="utf-8", errors="ignore").lower()
        words = re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", text)
        corpus_words.update(w.strip("'") for w in words if len(w) > 3)

    # Weight by engagement: views × (likes + comments) / views = likes + comments
    topic_scores: dict[str, float] = {}
    for v in videos:
        score = v.get("likes", 0) + v.get("comment_count", 0)
        words = re.findall(r"[^\W\d_]+(?:'[^\W\d_]+)?", v.get("title", "").lower())
        for w in words:
            w = w.strip("'")
            if len(w) > 4 and w not in STOP_WORDS and w not in corpus_words:
                topic_scores[w] = topic_scores.get(w, 0) + score

    sorted_gaps = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
    return [{"topic": w, "engagement_score": round(s)} for w, s in sorted_gaps[:top_n]]


# --------------------------------------------------------------------------- #
# Dimension 5 — Comment sentiment
# --------------------------------------------------------------------------- #

def comment_sentiment(comments: list[dict], top_n: int = 20) -> Counter:
    """Frequency of feeling-words across all comment texts."""
    counts: Counter = Counter()
    for c in comments:
        text = c.get("text", "").lower()
        words = re.findall(r"[^\W\d_]+", text)
        for w in words:
            if w in FEELING_WORDS:
                counts[w] += 1
    return Counter(dict(counts.most_common(top_n)))


# --------------------------------------------------------------------------- #
# Dimension 6 — Publish timing
# --------------------------------------------------------------------------- #

def publish_timing(videos: list[dict]) -> list[list[int]]:
    """
    Returns a 7×24 matrix (day × hour) of publish counts.
    Row 0 = Monday, row 6 = Sunday. UTC times.
    """
    matrix = [[0] * 24 for _ in range(7)]
    for v in videos:
        pub = v.get("published_at", "")
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            matrix[dt.weekday()][dt.hour] += 1
        except (ValueError, TypeError):
            pass
    return matrix


# --------------------------------------------------------------------------- #
# Dimension 7 — Evergreen split
# --------------------------------------------------------------------------- #

def evergreen_split(videos: list[dict], age_threshold_days: int = 730) -> dict[str, dict]:
    """
    Per channel: what fraction of total views comes from evergreen (>2yr) vs recent content.
    Returns {channel_id: {evergreen_views, trending_views, evergreen_pct}}.
    """
    now = datetime.now(timezone.utc)
    channel_data: dict[str, dict] = {}

    for v in videos:
        cid = v.get("channel_id", "")
        if cid not in channel_data:
            channel_data[cid] = {"evergreen_views": 0, "trending_views": 0}
        pub = v.get("published_at", "")
        try:
            dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            age_days = (now - dt).days
        except (ValueError, TypeError):
            age_days = 0
        views = v.get("views", 0)
        if age_days >= age_threshold_days:
            channel_data[cid]["evergreen_views"] += views
        else:
            channel_data[cid]["trending_views"] += views

    for cid, d in channel_data.items():
        total = d["evergreen_views"] + d["trending_views"]
        d["evergreen_pct"] = round(100 * d["evergreen_views"] / total, 1) if total else 0.0

    return channel_data


# --------------------------------------------------------------------------- #
# Dimension 8 — Title trigger words
# --------------------------------------------------------------------------- #

def top_title_words(videos: list[dict], top_n: int = 30) -> Counter:
    """Frequency of emotional trigger words in video titles."""
    trigger_set = set(EMOTIONAL_TRIGGER_WORDS)
    counts: Counter = Counter()
    for v in videos:
        words = re.findall(r"[^\W\d_]+", v.get("title", "").lower())
        for w in words:
            if w in trigger_set:
                counts[w] += 1
    return Counter(dict(counts.most_common(top_n)))


# --------------------------------------------------------------------------- #
# Duration bucketing (used by slide builder)
# --------------------------------------------------------------------------- #

DURATION_BUCKETS = ["<5 min", "5–10 min", "10–20 min", "20+ min"]


def duration_engagement(videos: list[dict], eng_rates: dict[str, float]) -> dict[str, float]:
    """Average engagement rate per duration bucket."""
    buckets: dict[str, list[float]] = {b: [] for b in DURATION_BUCKETS}
    for v in videos:
        sec = v.get("duration_seconds", 0)
        rate = eng_rates.get(v["video_id"], 0.0)
        if sec < 300:
            buckets["<5 min"].append(rate)
        elif sec < 600:
            buckets["5–10 min"].append(rate)
        elif sec < 1200:
            buckets["10–20 min"].append(rate)
        else:
            buckets["20+ min"].append(rate)
    return {
        b: round(sum(vals) / len(vals), 3) if vals else 0.0
        for b, vals in buckets.items()
    }
