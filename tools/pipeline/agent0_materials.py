"""
Agent 0: Materials Extraction
Extracts relevant insights from a PDF book using Gemini 3.1 Pro.
Run this before Agent 1 when you have a reference book for the topic.

Usage:
    python tools/pipeline/agent0_materials.py --topic "psychology of fear" --pdf "materials/The Fear Factor.pdf"
"""

import sys
import os
import argparse
from datetime import date
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from tools.utils import make_slug, write_output, get_env

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GEMINI_MODEL = "gemini-3.1-pro-preview"
OUTPUT_FILENAME = "md/00_materials_insights.md"


def _load_prompt() -> str:
    """Load extraction prompt template from workflows/pipeline/00_materials_prompt.md."""
    path = Path(__file__).parent.parent.parent / "workflows" / "pipeline" / "00_materials_prompt.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    body = [l for l in lines if not l.startswith("#") and not l.startswith("<!--")]
    return "\n".join(body).strip()


_MATERIALS_PROMPT_TEMPLATE = _load_prompt()


# ---------------------------------------------------------------------------
# PDF extraction
# ---------------------------------------------------------------------------


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF using pdfplumber."""
    import pdfplumber

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"  Extracting text from {total} pages...")
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text()
            if text:
                texts.append(text)
            if i % 50 == 0:
                print(f"  ... {i}/{total} pages processed")

    return "\n\n".join(texts)


# ---------------------------------------------------------------------------
# Gemini extraction
# ---------------------------------------------------------------------------


def query_gemini_extraction(topic: str, book_text: str) -> tuple[str, dict]:
    """Send book text to Gemini 3.1 Pro and extract insights relevant to the topic."""
    import google.genai as genai
    from google.genai import types

    project = get_env("GOOGLE_CLOUD_PROJECT")
    location = "global"

    print(f"  Initializing Gemini client (project={project}, location={location})...")
    client = genai.Client(vertexai=True, project=project, location=location)

    prompt = _MATERIALS_PROMPT_TEMPLATE.format(topic=topic, book_text=book_text)

    print(f"  Querying {GEMINI_MODEL} for insight extraction...")
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=8192,
        ),
    )

    usage = {"model": GEMINI_MODEL, "input_tokens": 0, "output_tokens": 0}
    if hasattr(response, "usage_metadata") and response.usage_metadata:
        usage["input_tokens"] = getattr(response.usage_metadata, "prompt_token_count", 0) or 0
        usage["output_tokens"] = getattr(response.usage_metadata, "candidates_token_count", 0) or 0

    return response.text, usage


# ---------------------------------------------------------------------------
# Output building
# ---------------------------------------------------------------------------


def build_output(topic: str, pdf_name: str, insights: str) -> str:
    today = date.today().isoformat()
    return (
        f"# Book Insights: {topic}\n"
        f"Source: {pdf_name}\n"
        f"Extracted: {today}\n"
        f"Model: {GEMINI_MODEL}\n"
        f"\n"
        f"---\n"
        f"\n"
        f"{insights}\n"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract book insights for the pipeline.")
    parser.add_argument("--topic", required=True, help='Topic string, e.g. "psychology of fear"')
    parser.add_argument("--pdf", required=True, help="Path to the PDF file")
    args = parser.parse_args()

    topic = args.topic.strip()
    pdf_path = Path(args.pdf)
    slug = make_slug(topic)

    print(f"\n=== Agent 0: Materials Extraction ===")
    print(f"Topic : {topic}")
    print(f"Slug  : {slug}")
    print(f"PDF   : {pdf_path.name}")
    print()

    # Step 1 — Extract PDF text
    print("[1/3] Extracting PDF text...")
    try:
        book_text = extract_pdf_text(pdf_path)
    except FileNotFoundError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: PDF extraction failed — {exc}")
        sys.exit(1)

    print(f"  Extracted {len(book_text):,} characters ({len(book_text) // 4:,} tokens approx.)")

    # Step 2 — Query Gemini
    print(f"\n[2/3] Extracting insights with {GEMINI_MODEL}...")
    try:
        insights, usage = query_gemini_extraction(topic, book_text)
    except EnvironmentError as exc:
        print(f"\nError: {exc}")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: Gemini extraction failed — {exc}")
        sys.exit(1)

    print(f"  Insights received ({len(insights):,} characters)")

    # Step 3 — Save output
    print(f"\n[3/3] Saving to {OUTPUT_FILENAME}...")
    content = build_output(topic, pdf_path.name, insights)
    output_path = write_output(slug, OUTPUT_FILENAME, content)
    print(f"  Saved: {output_path}")

    print(f"\nDone. Book insights ready. Now run Agent 1:")
    print(f'  python tools/agent1_research.py "{topic}"')


if __name__ == "__main__":
    main()
