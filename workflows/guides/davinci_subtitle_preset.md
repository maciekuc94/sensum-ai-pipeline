# DaVinci Resolve — One-Time Subtitle Preset Setup

Agent 11 emits `subtitles.srt` with timing only. Visual styling is applied **once** in DaVinci as a saved preset, then reapplied per project. This guide walks through that one-time setup so every imported SRT matches the SENSUM brand.

Target style (matches the brown-italic look in shipped videos):

- **Font:** Lora — Italic
- **Color:** #582F0E (dark brown / espresso)
- **Position:** Bottom-center with generous margin from the lower edge
- **No background box, no shadow**
- **Size:** ~70-80 pt at 1080p (adjust to taste)

## Step-by-step (DaVinci Resolve Free, version 18+)

1. **Install the Lora font** on Windows if it isn't already.
   - The repo includes `outputs/channel_assets/fonts/Lora-Italic.ttf`. Right-click → Install for all users.
   - Restart DaVinci so the OS font cache refreshes.

2. **Import the SRT into a test project.**
   - File → Import → Subtitle → `subtitles.srt`
   - It lands on a subtitle track at the top of the timeline.

3. **Select a subtitle clip on the timeline** so its parameters appear in the Inspector panel (top-right).

4. In the Inspector, find the **Style** tab. Set:

   | Field | Value |
   |---|---|
   | Font Family | `Lora` |
   | Font Face | `Italic` |
   | Size | `72` (start here, tune by eye) |
   | Color | `#582F0E` |
   | Stroke | Off (no outline) |
   | Drop Shadow | Off |
   | Background | Off |

5. **Position the subtitle.**
   - Inspector → Position
   - Y offset: nudge upward from the bottom (try `100` if you're seeing too-low subtitles)
   - X offset: `0` (center)

6. **Save as preset.**
   - In the Inspector, click the **three-dot menu** in the upper right of the Style section
   - Choose **Save as Preset…**
   - Name: `SENSUM Lora Italic` (or whatever you prefer)
   - Click OK.

7. **Apply to all subtitles in this project:**
   - Select the first subtitle on the track
   - Right-click → Select All in This Track
   - In the Inspector, find your saved preset under the Styles dropdown → Apply.

## For every subsequent video

Once the preset is saved in your DaVinci user profile, the workflow is:

1. Drag `subtitles.srt` onto a subtitle track.
2. Select all subtitle clips.
3. Apply the `SENSUM Lora Italic` preset.

This takes ~10 seconds total per video.

## Optional: per-line italic vs regular weight

Shipped videos mix Lora Italic (descriptive / poetic lines) and Lora Regular (factual statements). Agent 11 v1 uses Italic for every line. To override individual lines, select that subtitle clip in DaVinci and switch its Font Face to Regular. This is a manual judgment call per line; if it becomes routine, the agent could be extended to classify lines automatically.

## Color hex reminder

The brand brown is `#582F0E`. In DaVinci's color picker, type the hex directly into the color field. The sage beige background `#F4E5CA` is also brand-locked — never use any third color in subtitles.

## Reference frame

Open any shipped video screenshot from past episodes (e.g., `outputs/videos_en/3_the_grief_for_the_versions_of_you_that_didn_t_happen/`) to eyeball the size and vertical position when calibrating.
