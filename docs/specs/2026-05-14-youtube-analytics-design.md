# YouTube Analytics Agent — Design Spec
_Date: 2026-05-14 · SENSUM channel_

---

## Context

The SENSUM channel has published 1 long-form video and 4 Shorts. The creator wants to understand what's working, get AI-generated improvement recommendations, and track growth over time — without being a YouTube analytics expert. This spec adds two new agents to the WAT pipeline that fetch YouTube performance data and push an AI-analyzed report to a live Google Sheets dashboard.

---

## Architecture

Two agents following the existing Pass 1 / Pass 2 pattern (same as Agent 10):

```
python tools/agent11_analytics_fetch.py
  → YouTube Data API v3          ─┐
  → YouTube Analytics API         ├→ outputs/channel/analytics_2026-05-14.json
  → No AI, no cost, deterministic ┘   outputs/channel/analytics_latest.json

python tools/agent12_analytics_report.py
  → reads analytics_latest.json
  → Claude Opus 4.7             →  AI insights (what's working, recommendations)
  → Google Sheets API           →  "SENSUM Analytics" spreadsheet (YouTube account Drive)
                                    outputs/channel/12_report_2026-05-14.md
```

**New files created:**
- `tools/agent11_analytics_fetch.py`
- `tools/agent12_analytics_report.py`
- `workflows/11_analytics_fetch.md`
- `workflows/12_analytics_report.md`

**Modified files:**
- `requirements.txt` — add `google-api-python-client`

---

## Authentication

Two separate accounts, two separate token files, one shared `credentials.json`:

| File | Account | Used by |
|---|---|---|
| `token.json` | Vertex AI / GCP account | Existing pipeline — never touched |
| `token_youtube.json` | YouTube channel account | Agent 11 + Agent 12 only |

On first run of Agent 11, a browser tab opens. User signs in with their **YouTube channel account**. Token is saved as `token_youtube.json`. All subsequent runs are silent.

**OAuth scopes requested in `token_youtube.json`:**
- `https://www.googleapis.com/auth/youtube.readonly`
- `https://www.googleapis.com/auth/yt-analytics.readonly`
- `https://www.googleapis.com/auth/spreadsheets`

**One-time Google Cloud Console setup (before first run):**
1. Enable **YouTube Data API v3** in the existing GCP project
2. Enable **YouTube Analytics API** in the existing GCP project
3. Enable **Google Sheets API** (if not already on)
4. Add these three scopes to the OAuth consent screen → Scopes section

---

## Agent 11 — Analytics Fetch

**Input:** none (reads from YouTube APIs directly)  
**Output:** `outputs/channel/analytics_YYYY-MM-DD.json` + `analytics_latest.json`

**Data collected:**

| Category | Fields |
|---|---|
| Channel | subscribers, totalViews, totalWatchTimeMinutes |
| Per video | videoId, title, publishedAt, durationSeconds, isShort (≤60s), url |
| Per-video metrics | views, impressions, impressionCTR, avgViewDurationSeconds, watchTimeMinutes, subscribersGained, subscribersLost |
| Traffic sources | % from: SHORTS, YT_SEARCH, SUGGESTED, EXTERNAL, DIRECT, OTHER |
| Retention | % still watching at 25%, 50%, 75%, 100% of video |

**Short detection:** `durationSeconds ≤ 60` → `isShort: true`. YouTube Data API returns ISO 8601 duration (e.g., `PT45S`), parsed to seconds.

**Analytics date range:** last 28 days per run (sufficient for a new channel; configurable via `--days` flag).

**Output JSON shape:**
```json
{
  "fetched_at": "2026-05-14T10:00:00",
  "channel": { "subscribers": 0, "totalViews": 0, "totalWatchTimeMinutes": 0 },
  "videos": [
    {
      "videoId": "abc123",
      "title": "...",
      "publishedAt": "2026-05-01",
      "durationSeconds": 45,
      "isShort": true,
      "metrics": {
        "views": 0, "impressions": 0, "impressionCTR": 0.0,
        "avgViewDurationSeconds": 0, "watchTimeMinutes": 0,
        "subscribersGained": 0, "subscribersLost": 0
      },
      "trafficSources": { "SHORTS": 0.0, "YT_SEARCH": 0.0, "SUGGESTED": 0.0, "EXTERNAL": 0.0, "DIRECT": 0.0, "OTHER": 0.0 },
      "retention": { "p25": 0.0, "p50": 0.0, "p75": 0.0, "p100": 0.0 }
    }
  ]
}
```

---

## Agent 12 — Analytics Report

**Input:** `outputs/channel/analytics_latest.json`  
**Output:** Google Sheets dashboard + `outputs/channel/12_report_YYYY-MM-DD.md`

### Google Sheets Dashboard — "SENSUM Analytics"

Spreadsheet created automatically on first run in the YouTube account's Google Drive. Spreadsheet ID saved to `.env` as `ANALYTICS_SHEET_ID` for subsequent runs.

| Tab | Behavior | Contents |
|---|---|---|
| **Overview** | Overwrite each run | Channel totals, last-updated timestamp |
| **Videos** | Overwrite each run | One row per video/short, all metrics |
| **Traffic Sources** | Overwrite each run | Per-video traffic breakdown |
| **Retention** | Overwrite each run | Per-video retention at 25/50/75/100% |
| **AI Insights** | Append each run (new rows at bottom) | Date-stamped Claude analysis block |

### Claude Prompt — What Agent 12 asks

Claude receives the full JSON and is asked to produce:

1. **What's working** — identify the strongest-performing video/short and explain why (CTR, retention, traffic source that's driving it)
2. **What needs attention** — flag the weakest metric across all content and name the likely cause
3. **Shorts vs long-form read** — compare the two formats given the data; which is getting more traction?
4. **3 concrete recommendations** — specific, actionable for the *next* upload (title direction, thumbnail angle, topic, format, length)
5. **One watch-time flag** — if any video has retention <40% at 50% runtime, call it out and suggest a structural fix

Tone: plain language, no jargon. The creator is not an analytics expert.

---

## File & Directory Layout

```
outputs/
  channel/
    analytics_2026-05-14.json     ← date-stamped archive
    analytics_latest.json         ← always current (Agent 12 reads this)
    12_report_2026-05-14.md       ← markdown mirror of Sheets insights

tools/
  agent11_analytics_fetch.py
  agent12_analytics_report.py

workflows/
  11_analytics_fetch.md
  12_analytics_report.md
```

---

## Error Handling

| Situation | Behaviour |
|---|---|
| `token_youtube.json` missing | Agent 11 opens browser for YouTube account auth, saves token, continues |
| YouTube Analytics returns no data (video too new) | Logs warning per video, stores `null` for that metric, continues |
| `analytics_latest.json` missing when Agent 12 runs | Exits with message to run Agent 11 first |
| `ANALYTICS_SHEET_ID` missing from `.env` | Agent 12 creates a new spreadsheet, prints the URL, saves ID to `.env` automatically |
| Claude returns malformed response | Saves raw response to `12_debug_response.txt`, exits with instructions |

---

## Cost

| Agent | API calls | Approximate cost |
|---|---|---|
| Agent 11 | YouTube APIs only (free, quota-based) | $0.00 |
| Agent 12 | 1× Claude Opus 4.7 (~2,000 input + ~1,000 output tokens) | ~$0.11 |
| **Per run** | | **~$0.11** |

YouTube Data API quota: 10,000 units/day (default). Each run uses ~50–100 units. No concerns at this scale.

---

## Verification

End-to-end test after implementation:
1. Run `python tools/agent11_analytics_fetch.py` — browser opens, sign in with YouTube account, check `outputs/channel/analytics_latest.json` exists and contains your 5 videos
2. Run `python tools/agent12_analytics_report.py` — check Google Sheets URL is printed, open it, verify all 5 tabs populated
3. Run Agent 12 a second time — verify **AI Insights** tab has two entries (appended, not overwritten)
4. Check `outputs/channel/12_report_2026-05-14.md` exists with Claude's analysis
