# Workflow 11: Weekly Niche Intelligence

## Objective

Collect YouTube data from the psychology/mental-health niche, run 8 analytical
dimensions, and output a branded 16-slide PPTX intelligence report every Sunday.

## Inputs

- `YOUTUBE_API_KEY` in `.env`
- `SENSUM_CHANNEL_ID` in `.env`
- `GOOGLE_CLOUD_PROJECT` in `.env` (already set for Vertex AI)

## Output

`outputs/intelligence/YYYY-WNN_niche_intelligence.pptx`

## Standard invocation

```bash
PYTHONIOENCODING=utf-8 python tools/intelligence/intelligence.py
```

## Flags

| Flag | Effect |
|---|---|
| `--skip-vision` | Skip Gemini thumbnail classification (saves ~$0.05, faster) |
| `--skip-comments` | Skip comment collection (saves ~20 API units) |
| `--days N` | Look-back window for videos (default: 30) |

## File structure

```
outputs/intelligence/
  intelligence.db              SQLite — grows weekly for trend comparison
  thumbnails/                  Cached thumbnail JPEGs (re-used on subsequent runs)
  YYYY-WNN_niche_intelligence.pptx   Weekly output
  cost_log.json                API usage log per run
```

## Pipeline steps

1. **Discover channels** — `search.list` × 5 keyword queries → ~50 channel IDs
2. **SENSUM self-stats** — always included for in-context comparison
3. **Fetch channel stats** — `channels.list` for all discovered channels
4. **Fetch recent videos** — `playlistItems.list` + `videos.list` per channel, last 30 days
5. **Fetch comments** — `commentThreads.list`, top 50 per top-20 view-velocity videos
6. **Download thumbnails** — HTTP GET of `hqdefault.jpg` per video (cached locally)
7. **Classify thumbnails** — Gemini 2.0 Flash Vision via Vertex AI
8. **Store** — upsert all data into SQLite; save weekly subscriber snapshot
9. **Analyse** — 8 dimensions (see below)
10. **Generate deck** — python-pptx + matplotlib → 16-slide PPTX

## Analytical dimensions

| # | Dimension | Method |
|---|---|---|
| 1 | Trending topics | Word frequency on video titles (stop-word filtered) |
| 2 | View velocity | views ÷ days since publish |
| 3 | Engagement rate | (likes + comments) ÷ views |
| 4 | Content gaps | Topic clusters absent from SENSUM corpus |
| 5 | Comment sentiment | Curated feeling-word frequency list |
| 6 | Publish timing | publishedAt → 7×24 day/hour matrix |
| 7 | Evergreen split | Views from content >2yr vs <2yr old |
| 8 | Title trigger words | Emotional keyword frequency in titles |

## Quota estimate (per weekly run)

| Call | Units |
|---|---|
| `search.list` × 5 | 500 |
| `channels.list` × ~51 | 51 |
| `playlistItems.list` × 51 | ~153 |
| `videos.list` × ~51 batches | ~51 |
| `commentThreads.list` × 20 | 20 |
| **Total** | **~775 / 10,000 free** |

Gemini Flash Vision: ~$0.03–0.05 per run.

## Scheduling

One-time setup (run as Administrator):

```bash
python setup_scheduler.py
```

Remove:
```bash
python setup_scheduler.py --remove
```

## Error recovery

**Zero videos collected for a channel**
Likely the channel has no uploads in the last 30 days. Normal — no action needed.

**YouTube API quota exceeded (HTTP 403)**
Reduce channels by narrowing discovery queries, or reduce `--days` to 14.
Check quota usage: Google Cloud Console → APIs & Services → YouTube Data API v3 → Quotas.

**Gemini Vision failures**
Classification falls back to `"unknown"` per video. Deck still generates.
Run with `--skip-vision` if Vertex AI is unavailable.

**`YOUTUBE_API_KEY` not set**
Follow setup tutorial in `.planning/` or plan file. Takes ~5 minutes in Google Cloud Console.

**Thumbnail download failures**
Thumbnails are cached in `outputs/intelligence/thumbnails/`. Failed downloads are
silently skipped; the video still appears in all non-thumbnail slides.

**PPTX font fallback**
If EB Garamond or Lora aren't found at `outputs/channel_assets/fonts/`, matplotlib
falls back to system serif. The deck still generates; fonts may differ visually.

## Week-over-week trend data

The SQLite database accumulates one snapshot per week per channel.
- Week 1: No growth delta (no prior snapshot) — slide 4 shows a notice.
- Week 2+: Real subscriber deltas appear on slide 4.
- Month 2+: Evergreen split becomes statistically meaningful.
