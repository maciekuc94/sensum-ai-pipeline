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
    mock_response = {
        "items": [
            {"contentDetails": {"videoId": "vid1"}},
            {"contentDetails": {"videoId": "vid2"}},
        ],
        "nextPageToken": None,
    }
    mock_youtube.playlistItems.return_value.list.return_value.execute.return_value = mock_response
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
    # Total = 450; SHORTS = 300/450, YT_SEARCH = 100/450, SUGGESTED = 50/450
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


def test_get_retention_short_returns_nulls():
    from tools.agent11_analytics_fetch import _get_retention
    mock_analytics = MagicMock()
    result = _get_retention(mock_analytics, "vid1", "UCtest123", is_short=True)
    assert result == {"p25": None, "p50": None, "p75": None, "p100": None}
    mock_analytics.reports.assert_not_called()


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
    assert "what's working" in prompt.lower() or "What's Working" in prompt
    assert "recommendation" in prompt.lower()
    assert "watch" in prompt.lower()
    assert "vid1" in prompt or "Test Video" in prompt
