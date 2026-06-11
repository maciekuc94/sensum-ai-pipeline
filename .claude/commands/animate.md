---
description: Agent 6c planner — typuje beaty do obiektowych pętli animacyjnych (hook/metafora/puenta), pisze 06c_animation_plan.md, manual gate przed generacją.
argument-hint: <slug>
allowed-tools: Read, Write, Bash, Glob, Grep
---

# /animate — Agent 6c Ożywiacz (planner, in-session)

You are running the Agent 6c planning step of the SENSUM pipeline. Argument `$1` is the slug — a folder name under `outputs/videos_pl/`. Full SOP: `workflows/pipeline/06c_animate.md`; design rationale: `brainstorms/2026-06-10-agent6c-ozywiacz.md`.

Your job: read the film's image prompts and script, pick 10–15 beats worth animating, write `md/06c_animation_plan.md` — and **STOP before any generation** (manual gate: the user must accept the list and cost first).

## Workflow

1. **Validate inputs**:
   - Confirm `outputs/videos_pl/$1/md/05_image_prompts.md` exists. If missing: tell the user to run `/visuals $1` first, and stop.
   - Confirm `outputs/videos_pl/$1/images/` (or `images_post/`) contains PNGs. If empty: tell the user to run Agent 6 first (`agent6_images.py "$1" --generate`), and stop.

2. **Load sources**: read `md/05_image_prompts.md` (every `## Image NNN` block: Sentence + Imagen prompt) and the script (`md/script_corrected.md` if present, else `md/04_final.md`) for dramaturgy context.

3. **Pick beats — directing rule, not randomness.** Target **10–15 beats**, prioritised:
   - **hook** (first ~30 s of the script — highest stakes),
   - **central-metaphor beats** (the film's load-bearing image, every time it returns),
   - **the puenta / recognition close**,
   - then at most a few mid-film beats where an object has a *natural* micro-motion.
   A beat qualifies only if the motion is **meaning-bound** (the object moves the way the narration speaks about it: budzik dzwoni, kropla kapie, postać idzie, para unosi się, płomień drga, tkanina faluje). Skip beats where motion would be decorative noise. Statics between animated beats are the contrast that makes this work — do not exceed ~15.

4. **Write the plan** to `outputs/videos_pl/$1/md/06c_animation_plan.md`, one `## Beat NNN` block per pick (NNN = image number), exactly in the format from `workflows/pipeline/06c_animate.md`:
   - `**Image:**` / `**Mode:**` (`edit` default; `sheet` only when the shot is *designed around* a figure cycle and the scene composition allows compositing — use sparingly) / `**Motion:**` (ring/walk/drip/steam/flicker/breathe/sway/custom) / `**FPS:**` / `**Seconds:** 10` / `**Pattern:**` / `**Scope:**` / `**Phase a/b/c:**`.
   - Phase descriptions are **edit instructions in English** (they go verbatim into the GUARD prompt): concrete, small, limited to the Scope area — write them the way the budzik pilot did (hammer LEFT / hammer RIGHT / centered with arcs).
   - Pattern cadence per motion type: ring `a,b,a,b,c,a,b,base,base,base` @ 8 fps; walk `base,a,b,a` @ 4.5–5 fps; drip/steam 3–4 fps with longer `base` holds; breathe/sway 2–3 fps.
   - 2–3 phases per beat (more only if truly needed — each phase costs ~$0.04).

5. **Present the gate — and stop.** Show the user a compact table: beat number, sentence fragment (Polish), motion, mode, phase count, and the **estimated total cost** (phases × ~$0.04). Then ask for acceptance. Do **not** run `agent6c_animate.py` yourself unless the user explicitly confirms (e.g. "generuj"). After confirmation, the command is:

   `PYTHONIOENCODING=utf-8 python tools/pipeline/agent6c_animate.py "$1"`

   After generation, review `images_anim/frames/NNN/strip.png` contact sheets (Read) and re-roll failures via `--indices NNN --force`. Free iteration on rhythm: edit Pattern/FPS in the plan and re-run with `--no-gen`.

## Hard rules

- **Boil is the chosen aesthetic** — never add frame stabilisation.
- Loops are **asynchronous to audio** — never promise lip-sync/beat-sync.
- Output clips are **drop-in replacements** for the PNG on the user's DaVinci timeline; never touch `agent_align` / FCPXML.
- Only new slugs (4+) get animation as part of production; older slugs only on explicit user request (testing).
