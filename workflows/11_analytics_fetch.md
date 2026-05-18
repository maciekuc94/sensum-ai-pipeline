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
