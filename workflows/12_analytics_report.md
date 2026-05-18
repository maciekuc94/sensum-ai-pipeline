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

~$0.11 per run (1x Claude Opus 4.7 call, ~2,000 input + ~1,000 output tokens).
