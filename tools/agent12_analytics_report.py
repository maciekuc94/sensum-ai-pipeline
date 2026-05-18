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

from tools.utils import get_env, log_cost, query_claude

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
            f"  views={m['views']} avgViewDuration={m['avgViewDurationSeconds']}s watchTime={m['watchTimeMinutes']:.0f}min\n"
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

1. **What's Working** — identify the single strongest-performing video or Short and explain specifically WHY it's doing well (point to retention, watch time, or traffic source driving it). Be specific about the numbers.

2. **What Needs Attention** — flag the single weakest metric across all content and name the most likely cause. Be specific.

3. **Shorts vs Long-Form** — given the data, which format is getting more traction right now? Give a direct opinion the creator can act on.

4. **3 Concrete Recommendations** — for the NEXT upload specifically. Each recommendation must be actionable (title direction, thumbnail angle, topic, format, or length). Reference the data to justify each.

5. **Watch-Time Flag** — if any video has audience retention below 40% at the 50% mark, call it out by name and suggest one structural fix (e.g., move the hook earlier, cut the intro, add a chapter break).

Write in plain English. No bullet-point headers without content. No "it's too early to tell" hedging — give your best read of the data as it stands.
"""


def _call_claude(prompt: str) -> tuple[str, object]:
    return query_claude(prompt, CLAUDE_MODEL, 4096, "analytics analysis")


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
        "Views", "Avg View Duration (s)", "Watch Time (min)",
        "Subs Gained", "Subs Lost", "URL",
    ]
    rows = [header]
    for v in data["videos"]:
        m = v["metrics"]
        rows.append([
            v["videoId"], v["title"], v["publishedAt"], v["durationSeconds"],
            "Short" if v["isShort"] else "Long-form",
            m["views"], m["avgViewDurationSeconds"], round(m["watchTimeMinutes"], 1),
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
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def run_agent12() -> None:
    """Read analytics JSON, call Claude, write Sheets dashboard + markdown report."""
    print("\n=== Agent 12: YouTube Analytics Report ===\n")

    # Step 1 — Load analytics data
    if not _ANALYTICS_PATH.exists():
        print(f"Error: {_ANALYTICS_PATH} not found.")
        print("Run Agent 11 first:  python tools/agent11_analytics_fetch.py")
        sys.exit(1)

    data = json.loads(_ANALYTICS_PATH.read_text(encoding="utf-8"))
    run_date = date.today().isoformat()
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
        "input_tokens": usage["input_tokens"],
        "output_tokens": usage["output_tokens"],
    })
    print(f"  Response: {len(insights):,} chars")

    # Step 3 — Write Google Sheets
    print(f"\n[3/4] Writing Google Sheets dashboard...")
    from tools.youtube_auth import get_youtube_credentials, build_sheets  # deferred to avoid import-time OAuth side-effects

    creds = get_youtube_credentials()
    sheets_service = build_sheets(creds)

    sheet_id = _get_or_create_sheet(sheets_service)
    print(f"  Sheet ID: {sheet_id}")

    _ensure_tabs(sheets_service, sheet_id)
    _write_overview(sheets_service, sheet_id, data)
    _write_videos(sheets_service, sheet_id, data)
    _write_traffic_sources(sheets_service, sheet_id, data)
    _write_retention(sheets_service, sheet_id, data)

    _append_ai_insights(sheets_service, sheet_id, insights, run_date)
    print(f"  All 5 tabs written.")
    print(f"  Open: https://docs.google.com/spreadsheets/d/{sheet_id}")

    # Step 4 — Write markdown report
    print(f"\n[4/4] Writing markdown report...")
    report_path = _write_markdown_report(insights, data, run_date)
    print(f"  Saved: {report_path}")

    print("\nDone.")


def main() -> None:
    run_agent12()


if __name__ == "__main__":
    main()
