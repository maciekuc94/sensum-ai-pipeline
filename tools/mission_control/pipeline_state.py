"""Mission Control — detekcja etapów pipeline per slug. Czyste funkcje, read-only.

Markery plikowe wg kanonu file_naming + CLAUDE.md (Agent Chain). Kolejność
STAGES = kolejność kanoniczna; jedyna równoległość v1: po docx-passie
/visuals i /package idą obok siebie.
"""
from pathlib import Path

STAGES = [
    ("research", "Research", lambda d: (d / "md" / "01_research.md").exists()),
    ("weryfikacja", "Weryfikacja", lambda d: (d / "md" / "02_verified_research.md").exists()),
    ("skrypt", "Skrypt (/draft)", lambda d: (d / "md" / "04_final.md").exists()),
    ("docx", "Docx pass", lambda d: (d / "docx" / "script_corrected.docx").exists()
        or (d / "md" / "script_corrected.md").exists()),
    ("visuals", "Prompty (/visuals)", lambda d: (d / "md" / "05_image_prompts.md").exists()),
    ("grafiki", "Grafiki (agent6)", lambda d: any((d / "images").glob("*.png"))
        if (d / "images").exists() else False),
    ("package", "Package", lambda d: (d / "md" / "07_package.md").exists()),
    ("publish", "Publish", lambda d: (d / "md" / "08_publish.md").exists()),
    ("nagranie", "Nagranie", lambda d: (d / "voiceover" / "voiceover.wav").exists()),
    ("align", "Align", lambda d: (d / "edit" / "timeline.fcpxml").exists()),
    ("montaz", "Montaż (.mov)", lambda d: any(d.glob("*.mov"))),
]

OPTIONAL_STAGES = [
    ("animacje", "Animacje (6c)", lambda d: (d / "md" / "06c_animation_plan.md").exists()),
]

# Skondensowane fazy stepperów na kartach (podstrona sluga pokazuje pełne STAGES).
PHASES = [
    ("research", "research", ("research", "weryfikacja")),
    ("skrypt", "skrypt", ("skrypt",)),
    ("docx", "docx", ("docx",)),
    ("grafiki", "grafiki", ("visuals", "grafiki")),
    ("package", "package", ("package",)),
    ("publish", "publish", ("publish",)),
    ("nagranie", "nagranie", ("nagranie",)),
    ("montaz", "montaż", ("align", "montaz")),
]

COMMANDS = {
    "weryfikacja": 'PYTHONIOENCODING=utf-8 python tools/pipeline/agent2_verify.py "{slug}"',
    "skrypt": "/draft {slug}",
    "visuals": "/visuals {slug}",
    "grafiki": 'PYTHONIOENCODING=utf-8 python tools/pipeline/agent6_images.py "{slug}" --generate',
    "package": "/package {slug}",
    "publish": "/publish {slug}",
    "align": 'PYTHONIOENCODING=utf-8 python tools/pipeline/agent_align.py "{slug}"',
}

MANUAL_HINTS = {
    "research": "Start tematu: agent1_research.py \"<temat>\" (slug powstaje z tematu)",
    "docx": "Edytuj docx/script.docx (Word/Copilot) i zapisz jako docx/script_corrected.docx",
    "nagranie": "Nagraj voiceover (Studio One) i wyeksportuj do voiceover/voiceover.wav",
    "montaz": "DaVinci: import edit/timeline.fcpxml + subtitles.srt, montaż, render .mov",
}


def _action(stage_id: str, label: str, slug: str) -> dict:
    cmd = COMMANDS.get(stage_id)
    return {
        "stage": stage_id,
        "label": label,
        "command": cmd.format(slug=slug) if cmd else None,
        "manual_hint": MANUAL_HINTS.get(stage_id),
    }


def slug_title(slug_dir: Path) -> str:
    """Tytuł karty: 1. linia script_corrected.md > '# ...' z 04_final.md > slug."""
    corrected = slug_dir / "md" / "script_corrected.md"
    if corrected.exists():
        for line in corrected.read_text(encoding="utf-8").splitlines():
            if line.strip():
                return line.strip().lstrip("# ").strip()
    final = slug_dir / "md" / "04_final.md"
    if final.exists():
        for line in final.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("# "):
                return line.strip()[2:].strip()
    return slug_dir.name


def detect(slug_dir: Path) -> dict:
    """Pełny stan sluga dla /api/state."""
    slug = slug_dir.name
    done = {sid for sid, _label, check in STAGES if check(slug_dir)}
    stages = [{"id": sid, "label": label, "done": sid in done}
              for sid, label, _check in STAGES]
    optional = [{"id": sid, "label": label, "done": check(slug_dir)}
                for sid, label, check in OPTIONAL_STAGES]
    phases = [{"id": pid, "label": label, "done": all(s in done for s in deps)}
              for pid, label, deps in PHASES]

    finished = "montaz" in done
    next_actions: list[dict] = []
    if not finished:
        for sid, label, _check in STAGES:
            if sid not in done:
                next_actions.append(_action(sid, label, slug))
                # jedyna równoległość v1: po docx — /visuals i /package obok siebie
                if sid in ("visuals", "grafiki") and "package" not in done:
                    pkg_label = dict((s, l) for s, l, _c in STAGES)["package"]
                    next_actions.append(_action("package", pkg_label, slug))
                break

    return {
        "slug": slug,
        "title": slug_title(slug_dir),
        "stages": stages,
        "optional": optional,
        "phases": phases,
        "next": next_actions,
        "finished": finished,
    }
