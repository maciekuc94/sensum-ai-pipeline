"""Tests for tools.agent9_images — prompt extraction and parsing helpers."""
import pytest


SAMPLE_PROMPTS_FILE = """\
# Image Prompts: A topic
Generated: 2026-05-18
Source: md/04_script_final.md
Total images: 2

Review and edit these prompts before generating. Each prompt feeds directly into Vertex AI Imagen.

---

## Image 001
**Sentence:** "A faceless figure stands alone."
**Imagen prompt:**
a clean ink drawing of a faceless figure standing alone, fine line work, 16:9

---

## Image 002
**Sentence:** "Hands holding a phone."
**Imagen prompt:**
close up of two hands holding a phone, cross-hatched shading,
no facial features visible

---
"""


def test_parse_prompts_from_file_returns_all_prompts():
    from tools.agent9_images import _parse_prompts_from_file
    prompts = _parse_prompts_from_file(SAMPLE_PROMPTS_FILE)
    assert len(prompts) == 2
    assert prompts[0].startswith("a clean ink drawing of a faceless figure")
    assert "16:9" in prompts[0]


def test_parse_prompts_joins_multiline_prompts():
    """Multi-line prompts are joined with a space, not lost."""
    from tools.agent9_images import _parse_prompts_from_file
    prompts = _parse_prompts_from_file(SAMPLE_PROMPTS_FILE)
    assert prompts[1] == "close up of two hands holding a phone, cross-hatched shading, no facial features visible"


def test_parse_prompts_empty_input_returns_empty_list():
    from tools.agent9_images import _parse_prompts_from_file
    assert _parse_prompts_from_file("") == []
    assert _parse_prompts_from_file("# Just a heading\nno prompts here") == []


def test_extract_image_markers_returns_descriptions():
    from tools.agent9_images import _extract_image_markers
    script = (
        "Some narration. [IMAGE: a hand holding a phone] More narration. "
        "[IMAGE: two figures side by side] End."
    )
    markers = _extract_image_markers(script)
    assert markers == ["a hand holding a phone", "two figures side by side"]


def test_extract_image_markers_no_markers_returns_empty():
    from tools.agent9_images import _extract_image_markers
    assert _extract_image_markers("Plain narration with no markers.") == []


def test_extract_topic_from_script_final_heading():
    from tools.agent9_images import _extract_topic_from_script
    script = "# Script Final: Why You Can't Relax\nbody text\n"
    assert _extract_topic_from_script(script) == "Why You Can't Relax"


def test_extract_topic_from_script_plain_h1():
    from tools.agent9_images import _extract_topic_from_script
    script = "# Just A Topic\nbody\n"
    assert _extract_topic_from_script(script) == "Just A Topic"


def test_extract_topic_from_script_no_heading_fallback():
    from tools.agent9_images import _extract_topic_from_script
    assert _extract_topic_from_script("body with no heading") == "Unknown Topic"


def test_build_imagen_prompt_includes_character_and_style():
    from tools.agent9_images import _build_imagen_prompt
    from tools.utils import CHARACTER_DESCRIPTION, STYLE_SUFFIX
    result = _build_imagen_prompt("a figure on a bed")
    assert CHARACTER_DESCRIPTION in result
    assert "a figure on a bed" in result
    assert STYLE_SUFFIX in result


def test_build_imagen_prompt_extracts_scene_from_structured_marker():
    """If the description carries a legacy `scene=...` form, only the scene is used."""
    from tools.agent9_images import _build_imagen_prompt
    result = _build_imagen_prompt("character=ignored, scene=a quiet kitchen at dawn")
    assert "a quiet kitchen at dawn" in result
    assert "character=ignored" not in result
