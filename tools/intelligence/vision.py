"""Gemini Flash Vision thumbnail classification via Vertex AI."""

import base64
import time
from pathlib import Path

THUMBNAIL_STYLES = ["face-forward", "text-heavy", "minimal", "illustrated", "mixed"]

_CLASSIFY_PROMPT = (
    "Classify this YouTube thumbnail into exactly one of these categories:\n"
    "- face-forward: a human face is the dominant element\n"
    "- text-heavy: large text or title overlay dominates the image\n"
    "- minimal: clean, simple design with little text or faces\n"
    "- illustrated: drawn, animated, or graphical (non-photographic) art\n"
    "- mixed: roughly equal combination of face and text\n\n"
    "Reply with ONLY the category name, nothing else."
)

REQUEST_DELAY = 3  # seconds between calls to stay under Gemini Flash QPM


def classify_thumbnails(thumbnail_paths: dict[str, Path], project: str) -> dict[str, str]:
    """
    Classify each thumbnail image.

    Args:
        thumbnail_paths: {video_id: local_path}
        project: GCP project ID

    Returns:
        {video_id: style_label}
    """
    if not thumbnail_paths:
        return {}

    try:
        from google import genai
        from google.genai import types as genai_types
        client = genai.Client(vertexai=True, project=project, location="global")
    except Exception as e:
        print(f"  Warning: Vertex AI init failed — {e}. Skipping thumbnail classification.")
        return {vid: "unknown" for vid in thumbnail_paths}

    results = {}
    total = len(thumbnail_paths)

    print(f"  Classifying {total} thumbnails via Gemini Flash Vision...")

    for i, (video_id, img_path) in enumerate(thumbnail_paths.items(), 1):
        try:
            img_bytes = Path(img_path).read_bytes()
            b64 = base64.b64encode(img_bytes).decode()

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    genai_types.Part.from_bytes(
                        data=base64.b64decode(b64),
                        mime_type="image/jpeg",
                    ),
                    _CLASSIFY_PROMPT,
                ],
            )
            label = response.text.strip().lower()
            if label not in THUMBNAIL_STYLES:
                label = "unknown"
            results[video_id] = label

            if i % 10 == 0:
                print(f"    {i}/{total} classified...")
        except Exception as e:
            print(f"  Warning: classification failed for {video_id} — {e}")
            results[video_id] = "unknown"

        if i < total:
            time.sleep(REQUEST_DELAY)

    print(f"  Classified {len(results)}/{total} thumbnails.")
    return results
