"""Shared utilities for all agent scripts in the WAT framework."""

import json
import os
import re
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from slugify import slugify


# Load environment variables from .env file at project root
# ---------------------------------------------------------------------------
# Shared visual brand constants (used by agent5_visuals and agent9_images)
# ---------------------------------------------------------------------------

STYLE_SUFFIX = (
    "minimalist high-contrast ink illustration on clean flat white background, "
    "color palette strictly limited to #582F0E dark brown ink lines on white — no other colors whatsoever, "
    "technique: detailed cross-hatching for depth and shadow, fine-liner ink sketch, 2D perspective, heavy negative space, "
    "style: 19th-century scientific journal engraving, zero photorealism, no 3D effects, no gradients, no glows, no blurs, "
    "no green, no golden ochre, no moss green, no watercolor, no color fills, "
    "absolutely no text, no words, no letters, no numbers, no labels, no captions anywhere in the image, "
    "framing rule: if any human figure appears, the entire head must be fully visible inside the frame with generous headroom above — "
    "never crop the top of the head, never let the head touch or extend past the top edge of the frame, "
    "if the scene calls for a hand or close-up detail only, show ONLY the hand or detail with no head or body visible, "
    "16:9 aspect ratio"
)

CHARACTER_DESCRIPTION = (
    "a completely androgynous faceless gender-neutral human mannequin figure with a smooth featureless blank oval head — "
    "the head is a plain empty oval shape like an unpainted mannequin or blank egg, "
    "absolutely no facial features of any kind on the head, "
    "no eyes, no nose, no mouth, no ears, no hair, "
    "the body is fully androgynous: narrow symmetrical shoulders equal in width to the hips, slim flat chest with no breast or pectoral definition whatsoever, "
    "straight waist with no curve or hip flare, legs equal length, completely ambiguous gender with no masculine or feminine body markers, "
    "drawn entirely in fine-liner ink lines in deep espresso brown (#582F0E), "
    "cross-hatching used for depth and shading on the body, no color fills, "
    "19th-century scientific illustration style, 2D flat"
)


def _load_env():
    """Load .env file from project root."""
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path, override=False)


_load_env()


def get_env(key: str) -> str:
    """
    Get an environment variable with validation.

    Args:
        key: The environment variable name

    Returns:
        The environment variable value

    Raises:
        EnvironmentError: If the variable is missing or empty
    """
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Environment variable '{key}' is missing or empty. "
            f"Please set it in .env file at project root or in your shell."
        )
    return value


def make_slug(topic: str) -> str:
    """
    Convert a topic string to a filesystem-safe slug.

    Examples:
        "emotional dysregulation in ADHD" -> "emotional-dysregulation-in-adhd"
        "What is depression?" -> "what-is-depression"

    Args:
        topic: The topic string to slugify

    Returns:
        A filesystem-safe slug
    """
    return slugify(topic, separator="-", lowercase=True)


def get_output_dir(slug: str) -> Path:
    """
    Get the output directory for a given slug, creating it if needed.

    Creates the slug directory and standard subdirectories on first access.

    Args:
        slug: The slug identifier for this task

    Returns:
        Path to the output directory (e.g., outputs/emotional-dysregulation-in-adhd)
    """
    output_dir = Path(__file__).parent.parent / "outputs" / slug
    for subdir in ("images", "md", "docx", "tts"):
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)
    return output_dir


def write_output(slug: str, filename: str, content: str) -> Path:
    """
    Write content to a file in the output directory.

    Args:
        slug: The slug identifier for this task
        filename: The filename to write (e.g., "summary.md", "images/thumb.png")
        content: The content to write (string)

    Returns:
        Path to the written file
    """
    output_dir = get_output_dir(slug)
    file_path = output_dir / filename

    # Create parent directories if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_text(content, encoding="utf-8")
    return file_path


def read_output(slug: str, filename: str) -> str:
    """
    Read content from a file in the output directory.

    Args:
        slug: The slug identifier for this task
        filename: The filename to read (e.g., "summary.md")

    Returns:
        The file contents as a string

    Raises:
        FileNotFoundError: If the file doesn't exist with a helpful message
    """
    output_dir = get_output_dir(slug)
    file_path = output_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(
            f"Output file not found: {file_path}\n"
            f"Expected file in outputs/{slug}/{filename}\n"
            f"Make sure the file was created by a previous step."
        )

    return file_path.read_text(encoding="utf-8")



def load_style_guide(filename: str = "style_guide.md") -> str:
    """Load a style guide from the workflows/ directory relative to the project root.

    Args:
        filename: The filename inside workflows/ (default: style_guide.md)

    Returns:
        File contents as a string.

    Raises:
        FileNotFoundError: If the file doesn't exist, with a helpful message.
    """
    project_root = Path(__file__).parent.parent
    path = project_root / "workflows" / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Style guide not found at: {path}\n"
            f"Expected file: workflows/{filename} in the project root."
        )
    return path.read_text(encoding="utf-8")


def query_claude(
    prompt: str,
    model: str,
    max_tokens: int,
    step_label: str = "",
) -> tuple[str, dict]:
    """Call Claude via direct Anthropic API and return (response_text, usage_dict).

    Retries up to 3 times on HTTP 429/503 with exponential backoff at 15s, 30s, 60s.
    All other errors are re-raised immediately.
    """
    import time
    import anthropic

    client = anthropic.Anthropic(api_key=get_env("ANTHROPIC_API_KEY"))
    label = f" — {step_label}" if step_label else ""
    print(f"  Querying {model}{label}...")

    for attempt in range(1, 5):
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = next(b.text for b in message.content if b.type == "text")
            usage = {
                "model": model,
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens,
            }
            return text, usage
        except anthropic.APIStatusError as exc:
            if exc.status_code in (429, 503) and attempt < 4:
                wait = 15 * (2 ** (attempt - 1))
                print(f"  API rate limited — waiting {wait}s before retry {attempt}/3...")
                time.sleep(wait)
                continue
            raise


def log_cost(slug: str, agent: str, data: dict) -> None:
    """Append a cost record to outputs/[slug]/cost_log.json."""
    output_dir = get_output_dir(slug)
    log_path = output_dir / "cost_log.json"

    record = {"agent": agent, "timestamp": datetime.now().isoformat(), **data}

    records: list[dict] = []
    if log_path.exists():
        try:
            records = json.loads(log_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError):
            records = []

    # Replace existing record for this agent so re-runs don't double-count
    records = [r for r in records if r.get("agent") != agent]
    records.append(record)

    log_path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def export_to_docx(slug: str, md_filename: str, docx_filename: str) -> Path:
    """Convert a markdown file in the output dir to a .docx Word document.

    Handles: H1/H2/H3 headings, bullet lines (- ...), bold (**text**), GFM
    pipe tables, and plain paragraphs. Horizontal rules (---) are skipped.

    Returns the path to the written .docx file.
    """
    from docx import Document

    md_text = read_output(slug, md_filename)
    doc = Document()

    # Remove default empty paragraph Word adds
    for para in doc.paragraphs:
        p = para._element
        p.getparent().remove(p)

    def _add_inline(paragraph, text: str) -> None:
        """Add text to a paragraph, converting **bold** and <u>underline</u> spans."""
        parts = re.split(r"(\*\*[^*]+\*\*|<u>[^<]+</u>)", text)
        for part in parts:
            if part.startswith("**") and part.endswith("**"):
                run = paragraph.add_run(part[2:-2])
                run.bold = True
            elif part.startswith("<u>") and part.endswith("</u>"):
                run = paragraph.add_run(part[3:-4])
                run.underline = True
            elif part:
                paragraph.add_run(part)

    # GFM table separator: each cell must contain >=3 dashes (optionally with colons for alignment).
    # Prior pattern `^[\|\s:\-]+$` also swallowed empty data rows like `| | |`.
    _separator_re = re.compile(r"^\s*\|?(\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")

    def _parse_row(line: str) -> list[str]:
        # Strip leading/trailing pipe, split on |, trim cells.
        inner = line.strip()
        if inner.startswith("|"):
            inner = inner[1:]
        if inner.endswith("|"):
            inner = inner[:-1]
        return [c.strip() for c in inner.split("|")]

    table_buffer: list[list[str]] = []

    def _flush_table() -> None:
        if not table_buffer:
            return
        col_count = max(len(r) for r in table_buffer)
        # Pad short rows so every row has col_count cells.
        padded = [r + [""] * (col_count - len(r)) for r in table_buffer]
        header = padded[0]
        body = padded[1:]
        try:
            table = doc.add_table(rows=1 + len(body), cols=col_count)
            table.style = "Light Grid Accent 1"
        except KeyError:
            # Style may not exist on minimal docx templates; fall back to default.
            table = doc.add_table(rows=1 + len(body), cols=col_count)
        # Header row — bold.
        for i, cell_text in enumerate(header):
            cell = table.rows[0].cells[i]
            cell.text = ""
            para = cell.paragraphs[0]
            run = para.add_run(cell_text)
            run.bold = True
        # Body rows.
        for r, row in enumerate(body, start=1):
            for i, cell_text in enumerate(row):
                cell = table.rows[r].cells[i]
                cell.text = ""
                para = cell.paragraphs[0]
                _add_inline(para, cell_text)
        doc.add_paragraph()  # spacer after table
        table_buffer.clear()

    for line in md_text.splitlines():
        stripped = line.strip()

        # Table line (must come before the --- check so separator rows aren't dropped).
        if stripped.startswith("|") and stripped.endswith("|") and "|" in stripped[1:]:
            if _separator_re.match(stripped):
                # GFM header separator — discard, don't add as a row.
                continue
            table_buffer.append(_parse_row(stripped))
            continue

        # Anything non-table flushes any in-progress table.
        _flush_table()

        if stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("- ") or stripped.startswith("* "):
            para = doc.add_paragraph(style="List Bullet")
            _add_inline(para, stripped[2:])
        elif stripped.startswith("---"):
            # Horizontal rule — skip
            continue
        elif stripped == "":
            # Blank line — skip
            continue
        else:
            para = doc.add_paragraph()
            _add_inline(para, stripped)

    _flush_table()  # in case the file ends with a table

    output_dir = get_output_dir(slug)
    output_path = output_dir / docx_filename
    doc.save(str(output_path))
    return output_path
