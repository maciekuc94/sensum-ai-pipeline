"""
Test harness: render visual-strategy variants of image prompts for comparison.

Two modes:

  1. Comparison mode — `--image-index N`
     Render all 5 strategies against ONE source row. Used to pick a winning
     visual direction. Output: `outputs/<slug>/visual_tests/strategy_<id>.png`.

  2. Validation-set mode — `--strategy <id> --image-indices "n1,n2,n3,..."`
     Render ONE strategy across MULTIPLE source rows. Used to confirm a
     chosen strategy holds up across varied moments before redesigning
     Agent 5. Output:
     `outputs/<slug>/visual_tests/strategy_<id>_set/image_NNN.png`.

The bichromatic + 19th-c. scientific etching contract is invariant across all
strategies — only the composition philosophy changes.

Usage:
    # Comparison
    PYTHONIOENCODING=utf-8 python tools/test_visual_approaches.py "<slug>" --image-index 12

    # Validation set
    PYTHONIOENCODING=utf-8 python tools/test_visual_approaches.py "<slug>" \\
      --strategy B_figure_conditional --image-indices "5,22,40,58,80"
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.utils import (
    read_output,
    get_output_dir,
    get_env,
    query_claude,
    STYLE_SUFFIX,
)
from tools.agent9_images import (
    _resize_to_target,
    _enforce_background_color,
    NEGATIVE_PROMPT,
    PROMPTS_FILENAME,
)


OPUS_MODEL = "claude-opus-4-7"
IMAGE_MODEL = "gemini-3-pro-image-preview"
REQUEST_DELAY = 20  # seconds between Vertex AI calls — match agent10_thumbnails


# Each strategy is (id, human_label, directive_for_claude_or_None).
# Strategy A has no directive — the baseline prompt is rendered verbatim.
STRATEGIES = [
    (
        "A_baseline",
        "Baseline — current Agent 9 output (figure prepended unconditionally)",
        None,
    ),
    (
        "B_figure_conditional",
        "Figure-conditional — faceless figure ONLY when the scene actually needs a human",
        (
            "Read the script sentence and the baseline prompt. Decide whether "
            "this scene meaningfully requires a human figure to convey what "
            "the sentence is about. If YES, keep the faceless mannequin "
            "figure exactly as described. If NO (e.g. the scene is really "
            "about an object, an environment, or an abstract concept), "
            "REMOVE the human figure entirely and rewrite the scene as a "
            "pure object/environment composition that carries the emotional "
            "weight directly. Do not invent a figure where the sentence "
            "does not call for one."
        ),
    ),
    (
        "C_object_symbolic",
        "Object-symbolic forward — meaningful objects dominate, figure used sparingly",
        (
            "Rewrite the scene to be OBJECT-FORWARD. The composition is "
            "dominated by one or two symbolic objects that carry the "
            "emotional meaning of the sentence — a chair, a book, a thread, "
            "a key, a window, a stone, a folded letter — chosen for "
            "metaphorical weight, not literal illustration of the words. "
            "If a figure appears at all, it is small, peripheral, and "
            "subordinated to the object. Aim for the visual register of a "
            "19th-century still-life plate."
        ),
    ),
    (
        "D_diagrammatic",
        "Diagrammatic / anatomical — psychological concept as 19th-c. scientific diagram",
        (
            "Rewrite the scene as a 19th-century scientific diagram or "
            "anatomical plate that renders the PSYCHOLOGICAL MECHANISM "
            "behind the sentence as a physical-looking system. Cross-"
            "sections, schematics, labelled-without-text arrows, branching "
            "structures, anatomical cutaways. No whole human bodies — only "
            "anatomical fragments (a heart, a hand, a sectioned skull, a "
            "nervous-system tree) if a body part is needed at all. Imagine "
            "an old neurology textbook plate. Still no readable text or "
            "numbers — the diagram is suggestive, not labelled."
        ),
    ),
    (
        "E_metaphorical_tableau",
        "Metaphorical tableau — figure inside a symbolic environment, narrative scale",
        (
            "Rewrite the scene as a METAPHORICAL TABLEAU — the faceless "
            "figure is placed inside a symbolic environment that "
            "externalises what the sentence is doing internally. Examples: "
            "a library of unlived lives, a cemetery of unmade choices, a "
            "theatre of possible selves, a corridor of doors that lead "
            "nowhere, an empty waiting room of the mind. The figure is "
            "centred but at small or medium scale — the environment "
            "dominates and tells the story. Single subject, clear silhouette, "
            "high negative space."
        ),
    ),
]


def _parse_image_block(content: str, image_index: int) -> dict:
    """Extract sentence + imagen-prompt for image NNN from 05_image_prompts.md."""
    # Each block starts at `## Image NNN` and ends at the next `## Image` or EOF.
    blocks = re.split(r"(?m)^## Image (\d+)\n", content)
    # blocks = [pre, num1, body1, num2, body2, ...]
    if len(blocks) < 3:
        raise ValueError("No image blocks found in prompts file.")

    found = None
    for i in range(1, len(blocks) - 1, 2):
        num = int(blocks[i])
        if num == image_index:
            found = blocks[i + 1]
            break

    if found is None:
        # Build a quick list of available indices for the error message.
        available = [int(blocks[i]) for i in range(1, len(blocks) - 1, 2)]
        raise ValueError(
            f"Image {image_index} not found. Available: "
            f"{available[0]}–{available[-1]} ({len(available)} prompts)."
        )

    sentence_match = re.search(r'\*\*Sentence:\*\*\s*"(.+?)"', found, re.DOTALL)
    if not sentence_match:
        raise ValueError(f"Sentence line not found for image {image_index}.")
    sentence = sentence_match.group(1).strip()

    prompt_match = re.search(
        r"\*\*Imagen prompt:\*\*\s*\n(.+?)(?:\n---|\Z)",
        found,
        re.DOTALL,
    )
    if not prompt_match:
        raise ValueError(f"Imagen prompt not found for image {image_index}.")
    prompt = " ".join(line.strip() for line in prompt_match.group(1).strip().splitlines() if line.strip())

    return {"index": image_index, "sentence": sentence, "prompt": prompt}


def _build_strategy_prompt(
    strategy_id: str,
    directive: str,
    sentence: str,
    baseline_prompt: str,
) -> str:
    """Ask Claude to rewrite the baseline Gemini prompt under a strategy directive."""
    rewrite_request = (
        "You are reshaping an image prompt for a YouTube video rendered in "
        "strict bichromatic 19th-century scientific etching style.\n\n"
        "INVARIANT STYLE CONTRACT (must remain enforced in your output):\n"
        "- Color palette: only #582F0E dark brown ink lines on flat white background. "
        "Background will be replaced with #F4E5CA in post-processing.\n"
        "- 19th-century scientific journal engraving style with fine-liner ink + "
        "cross-hatching. No photorealism, no 3D, no gradients, no glows.\n"
        "- If any figure appears, it is the faceless androgynous mannequin "
        "(blank oval head, no facial features, no hair, ambiguous body).\n"
        "- No readable text, words, letters, numbers, or labels anywhere.\n"
        "- 16:9 aspect ratio. Heavy negative space.\n"
        "- If a figure has a head, the full head must fit with headroom — never "
        "crop the top of the head.\n\n"
        f"STRATEGY DIRECTIVE — {strategy_id}:\n{directive}\n\n"
        f"SCRIPT SENTENCE this image illustrates:\n\"{sentence}\"\n\n"
        f"BASELINE PROMPT (current Agent 9 output):\n{baseline_prompt}\n\n"
        "Produce ONE complete replacement prompt suitable for direct "
        "submission to Gemini 3 Pro Image Preview. Output ONLY the prompt "
        "text — no preface, no explanation, no markdown fencing, no quotes "
        "around it. The prompt should be a single dense paragraph including "
        "(a) the strategy-specific scene description, (b) the style contract "
        "clauses listed above, and (c) the framing/aspect-ratio clause. "
        "Length: 150–250 words."
    )

    text, _usage = query_claude(
        rewrite_request,
        model=OPUS_MODEL,
        max_tokens=2000,
        step_label=f"rewrite-{strategy_id}",
    )
    # Strip stray fencing or quote wrappers if Claude added them anyway.
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()
    if (text.startswith('"') and text.endswith('"')) or (text.startswith("'") and text.endswith("'")):
        text = text[1:-1].strip()
    return text


def _render_with_gemini(client, types_module, prompt_text: str, out_path: Path) -> None:
    """Call Gemini 3 Pro Image Preview and save the PNG. Post-process for brand."""
    response = client.models.generate_content(
        model=IMAGE_MODEL,
        contents=prompt_text + "\n\nAvoid in this image: " + NEGATIVE_PROMPT,
        config=types_module.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    candidates = response.candidates or []
    if not candidates or not candidates[0].content:
        raise ValueError("Empty response (possible safety filter)")
    img_bytes = None
    for part in candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data:
            img_bytes = part.inline_data.data
            break
    if not img_bytes:
        raise ValueError("No image in response")

    out_path.write_bytes(img_bytes)
    _resize_to_target(out_path)
    _enforce_background_color(out_path)


def _write_readme(tests_dir: Path, slug: str, source: dict) -> None:
    lines = [
        f"# Visual Approach Tests — {slug}",
        "",
        f"**Source image:** {source['index']:03d} from `md/05_image_prompts.md`",
        f"**Script sentence:** \"{source['sentence']}\"",
        "",
        "## Strategies",
        "",
    ]
    for strategy_id, label, _directive in STRATEGIES:
        lines += [
            f"### Strategy {strategy_id[0]} — {label}",
            f"- Image: `strategy_{strategy_id}.png`",
            f"- Prompt: `strategy_{strategy_id}_prompt.txt`",
            "",
        ]
    lines += [
        "## How to compare",
        "",
        "Open all 5 PNGs side-by-side. For each, check:",
        "- Style contract held? (only #F4E5CA + #582F0E; no faces; no text; no head crop)",
        "- Does the image *say something* about the script sentence, beyond literal illustration?",
        "- Does this composition feel like one you'd want sustained across an entire video?",
        "",
        "After picking a winner (or asking for more variants), the next plan",
        "redesigns Agent 5's prompt-generation logic to use that strategy.",
        "",
    ]
    (tests_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def run(slug: str, image_index: int) -> None:
    print(f"\n=== Visual Approach Test ===")
    print(f"Slug         : {slug}")
    print(f"Image index  : {image_index:03d}")
    print()

    # Step 1 — Find the source row.
    print(f"[1/4] Reading {PROMPTS_FILENAME}...")
    content = read_output(slug, PROMPTS_FILENAME)
    source = _parse_image_block(content, image_index)
    print(f"  Sentence: \"{source['sentence'][:80]}{'...' if len(source['sentence']) > 80 else ''}\"")

    # Step 2 — Build the 5 strategy prompts.
    print(f"\n[2/4] Building strategy prompts...")
    strategy_prompts: dict[str, str] = {}
    for strategy_id, label, directive in STRATEGIES:
        if directive is None:
            strategy_prompts[strategy_id] = source["prompt"]
            print(f"  {strategy_id}: baseline (no rewrite)")
        else:
            print(f"  {strategy_id}: asking Claude to rewrite...")
            strategy_prompts[strategy_id] = _build_strategy_prompt(
                strategy_id=strategy_id,
                directive=directive,
                sentence=source["sentence"],
                baseline_prompt=source["prompt"],
            )

    # Step 3 — Set up Vertex AI.
    print(f"\n[3/4] Initialising Vertex AI Gemini 3 Pro Image Preview...")
    project = get_env("GOOGLE_CLOUD_PROJECT")
    from google import genai
    from google.genai import types as genai_types
    client = genai.Client(vertexai=True, project=project, location="global")
    print(f"  Project : {project}")
    print(f"  Model   : {IMAGE_MODEL}")

    # Step 4 — Output dir + write source + prompts + render.
    output_dir = get_output_dir(slug)
    tests_dir = output_dir / "visual_tests"
    tests_dir.mkdir(parents=True, exist_ok=True)
    (tests_dir / "source.txt").write_text(
        f"Image index: {source['index']:03d}\n"
        f"Script sentence: \"{source['sentence']}\"\n\n"
        f"Baseline prompt (Agent 9 verbatim):\n{source['prompt']}\n",
        encoding="utf-8",
    )

    print(f"\n[4/4] Rendering 5 strategies to {tests_dir} ...")
    total = len(STRATEGIES)
    for seq, (strategy_id, _label, _directive) in enumerate(STRATEGIES, start=1):
        png_path = tests_dir / f"strategy_{strategy_id}.png"
        txt_path = tests_dir / f"strategy_{strategy_id}_prompt.txt"
        prompt_text = strategy_prompts[strategy_id]

        # Always overwrite the prompt file so the side-by-side reflects this run.
        txt_path.write_text(prompt_text + "\n", encoding="utf-8")

        if png_path.exists():
            print(f"  [{seq}/{total}] {strategy_id}: PNG already exists, skipping render.")
            continue

        print(f"  [{seq}/{total}] {strategy_id}: rendering...")
        try:
            _render_with_gemini(client, genai_types, prompt_text, png_path)
            print(f"      Saved: {png_path}")
        except Exception as exc:
            print(f"      Warning: render failed — {exc}")

        if seq < total:
            print(f"      Waiting {REQUEST_DELAY}s (rate limit)...")
            time.sleep(REQUEST_DELAY)

    _write_readme(tests_dir, slug, source)
    print(f"\nDone. Inspect {tests_dir} for side-by-side comparison.")


def _write_set_readme(
    set_dir: Path,
    slug: str,
    strategy_id: str,
    label: str,
    directive: str | None,
    sources: list[dict],
) -> None:
    lines = [
        f"# Strategy {strategy_id} Validation Set — {slug}",
        "",
        f"**Strategy:** {label}",
        "",
        "**Directive given to Claude for each rewrite:**",
        "",
        "> " + (directive.replace("\n", "\n> ") if directive else "(baseline — no rewrite)"),
        "",
        f"**Source rows tested ({len(sources)}):**",
        "",
    ]
    for src in sources:
        lines += [
            f"- **Image {src['index']:03d}** — `image_{src['index']:03d}.png`",
            f'  - Sentence: "{src["sentence"]}"',
        ]
    lines += [
        "",
        "## How to evaluate",
        "",
        "Open all PNGs side-by-side. For each, check:",
        "",
        "- **Style contract held?** Only #F4E5CA + #582F0E; no faces; no readable text; no head crop.",
        "- **Did Claude make the right figure-vs-no-figure call** for this sentence's meaning?",
        "- **Does the image *say something*** about the sentence beyond literal illustration?",
        "",
        "Then look at the set as a whole:",
        "",
        "- Do these 5 images **feel like they belong to the same video** — same emotional register, same visual language?",
        "- Where the strategy chose differently (figure here, no figure there), does that variation feel intentional and right?",
        "",
        "If yes → next plan redesigns Agent 5 around this strategy.",
        "If no on specific moments → refine the directive or try a hybrid.",
        "",
    ]
    (set_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def run_set(slug: str, indices: list[int], strategy_id: str) -> None:
    """Validation-set mode: render ONE strategy across MULTIPLE source rows."""
    # Resolve strategy by id.
    match = next((s for s in STRATEGIES if s[0] == strategy_id), None)
    if match is None:
        available = ", ".join(s[0] for s in STRATEGIES)
        print(f"Error: unknown strategy '{strategy_id}'. Available: {available}")
        sys.exit(1)
    _, label, directive = match

    print(f"\n=== Visual Approach Validation Set ===")
    print(f"Slug        : {slug}")
    print(f"Strategy    : {strategy_id} — {label}")
    print(f"Indices     : {', '.join(f'{i:03d}' for i in indices)} ({len(indices)} images)")
    print()

    # Step 1 — Parse all source rows up front (fail fast on bad indices).
    print(f"[1/4] Reading {PROMPTS_FILENAME}...")
    content = read_output(slug, PROMPTS_FILENAME)
    sources: list[dict] = []
    for idx in indices:
        try:
            sources.append(_parse_image_block(content, idx))
        except ValueError as exc:
            print(f"  Error on index {idx}: {exc}")
            sys.exit(1)
    for src in sources:
        snippet = src["sentence"][:80] + ("..." if len(src["sentence"]) > 80 else "")
        print(f"  {src['index']:03d}: \"{snippet}\"")

    # Step 2 — Build strategy prompts (Claude rewrites unless baseline).
    print(f"\n[2/4] Building strategy prompts for {strategy_id}...")
    strategy_prompts: dict[int, str] = {}
    for src in sources:
        if directive is None:
            strategy_prompts[src["index"]] = src["prompt"]
            print(f"  {src['index']:03d}: baseline (no rewrite)")
        else:
            print(f"  {src['index']:03d}: asking Claude to rewrite...")
            strategy_prompts[src["index"]] = _build_strategy_prompt(
                strategy_id=strategy_id,
                directive=directive,
                sentence=src["sentence"],
                baseline_prompt=src["prompt"],
            )

    # Step 3 — Set up Vertex AI.
    print(f"\n[3/4] Initialising Vertex AI Gemini 3 Pro Image Preview...")
    project = get_env("GOOGLE_CLOUD_PROJECT")
    from google import genai
    from google.genai import types as genai_types
    client = genai.Client(vertexai=True, project=project, location="global")
    print(f"  Project : {project}")
    print(f"  Model   : {IMAGE_MODEL}")

    # Step 4 — Output dir + source.txt + render each.
    output_dir = get_output_dir(slug)
    set_dir = output_dir / "visual_tests" / f"strategy_{strategy_id}_set"
    set_dir.mkdir(parents=True, exist_ok=True)

    source_blocks = []
    for src in sources:
        source_blocks.append(
            f"--- Image {src['index']:03d} ---\n"
            f"Script sentence: \"{src['sentence']}\"\n\n"
            f"Baseline prompt (Agent 9 verbatim):\n{src['prompt']}\n"
        )
    (set_dir / "source.txt").write_text("\n".join(source_blocks), encoding="utf-8")

    print(f"\n[4/4] Rendering {len(sources)} images to {set_dir} ...")
    total = len(sources)
    for seq, src in enumerate(sources, start=1):
        idx = src["index"]
        png_path = set_dir / f"image_{idx:03d}.png"
        txt_path = set_dir / f"image_{idx:03d}_prompt.txt"
        prompt_text = strategy_prompts[idx]

        # Always overwrite the prompt file so the saved text matches this run.
        txt_path.write_text(prompt_text + "\n", encoding="utf-8")

        if png_path.exists():
            print(f"  [{seq}/{total}] {idx:03d}: PNG already exists, skipping render.")
            continue

        print(f"  [{seq}/{total}] {idx:03d}: rendering...")
        try:
            _render_with_gemini(client, genai_types, prompt_text, png_path)
            print(f"      Saved: {png_path}")
        except Exception as exc:
            print(f"      Warning: render failed — {exc}")

        if seq < total:
            print(f"      Waiting {REQUEST_DELAY}s (rate limit)...")
            time.sleep(REQUEST_DELAY)

    _write_set_readme(set_dir, slug, strategy_id, label, directive, sources)
    print(f"\nDone. Inspect {set_dir} for the validation set.")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render visual-strategy variants for one or many image prompts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  # Comparison: 5 strategies × 1 image\n"
            "  python tools/test_visual_approaches.py \"<slug>\" --image-index 12\n"
            "\n"
            "  # Validation set: 1 strategy × N images\n"
            "  python tools/test_visual_approaches.py \"<slug>\" \\\n"
            "    --strategy B_figure_conditional \\\n"
            "    --image-indices \"5,22,40,58,80\"\n"
        ),
    )
    parser.add_argument("slug", help="Output slug for outputs/<slug>/.")

    selector = parser.add_mutually_exclusive_group(required=True)
    selector.add_argument(
        "--image-index",
        type=int,
        help="1-based image index. Renders ALL 5 strategies against this image.",
    )
    selector.add_argument(
        "--image-indices",
        type=str,
        help="Comma-separated indices (e.g. '5,22,40'). Requires --strategy.",
    )

    parser.add_argument(
        "--strategy",
        type=str,
        default=None,
        help="Strategy id (e.g. 'B_figure_conditional'). Required with --image-indices.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    slug = args.slug.strip()
    if not slug:
        print("Error: slug argument is empty.")
        sys.exit(1)

    if args.image_indices:
        if not args.strategy:
            print("Error: --image-indices requires --strategy.")
            sys.exit(1)
        try:
            indices = [int(x.strip()) for x in args.image_indices.split(",") if x.strip()]
        except ValueError:
            print(f"Error: --image-indices must be comma-separated integers, got: {args.image_indices!r}")
            sys.exit(1)
        if not indices:
            print("Error: --image-indices is empty.")
            sys.exit(1)
        run_set(slug, indices, args.strategy)
    else:
        if args.strategy:
            print("Note: --strategy is ignored when --image-index is used (comparison mode renders all 5).")
        run(slug, args.image_index)


if __name__ == "__main__":
    main()
