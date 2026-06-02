# Agent Teams — Master Reference Guide

> **Experimental feature.** Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings and Claude Code v2.1.32+.

---

## Quick-Start Checklist

1. Set `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in `.claude/settings.local.json` (done)
2. Verify version: `claude --version` (need ≥ 2.1.32)
3. Prompt the lead with task + team structure in natural language
4. Use **Shift+Down** to cycle teammates in in-process mode
5. Clean up when done: *"Clean up the team"*

---

## What Agent Teams Are (and Aren't)

Agent teams let you run **multiple independent Claude Code sessions** that coordinate through a shared task list and direct messaging. One session is the **lead**; the rest are **teammates**.

Key distinctions:
- Each teammate has its **own context window** — the lead's conversation history does NOT carry over
- Teammates can **message each other directly** (not just report to the lead)
- Teammates **self-claim tasks** from the shared list autonomously
- You can **interact with any teammate directly**, bypassing the lead

---

## Agent Teams vs. Subagents — When to Use Which

| | Subagents | Agent Teams |
|---|---|---|
| **Context** | Own window; results return to caller | Own window; fully independent |
| **Communication** | Report back to main agent only | Teammates message each other directly |
| **Coordination** | Main agent manages all work | Shared task list + self-coordination |
| **Token cost** | Lower (results summarized) | Higher (each teammate = separate Claude) |
| **Best for** | Focused tasks where only the result matters | Complex work needing discussion + collaboration |

**Rule of thumb:**
- Use **subagents** when workers are siloed (parallel research, isolated file edits, verification tasks).
- Use **agent teams** when workers need to share findings, challenge each other, or unblock each other.

---

## Architecture

```
Lead Session
├── Spawns teammates
├── Manages task list
├── Receives idle notifications automatically
└── Synthesizes results

Teammate A          Teammate B          Teammate C
├── Own context     ├── Own context     ├── Own context
├── Claims tasks    ├── Claims tasks    ├── Claims tasks
└── Messages any    └── Messages any    └── Messages any
   other teammate      other teammate      other teammate

Shared Infrastructure
├── Task list:   ~/.claude/tasks/{team-name}/
├── Team config: ~/.claude/teams/{team-name}/config.json  ← DO NOT HAND-EDIT
└── Mailbox:     messaging system (automatic delivery)
```

Task states: `pending` → `in progress` → `completed`

Tasks can have **dependencies**: a blocked task auto-unblocks when its dependency completes. Task claiming uses **file locking** to prevent race conditions.

---

## Enabling Agent Teams

In `.claude/settings.local.json` (project-local, gitignored):

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Or set in the shell environment before launching Claude Code.

---

## Display Modes

| Mode | How it works | Requirements |
|---|---|---|
| `auto` (default) | Split panes if already in tmux; otherwise in-process | None |
| `in-process` | All teammates in main terminal; Shift+Down to cycle | Any terminal |
| `tmux` | Each teammate in its own pane | tmux or iTerm2 + it2 CLI |

Override globally in `~/.claude/settings.json`:
```json
{ "teammateMode": "in-process" }
```

Override for one session:
```bash
claude --teammate-mode in-process
```

**Note:** Split panes do NOT work in VS Code integrated terminal, Windows Terminal, or Ghostty.

---

## Spawning a Team — Prompt Patterns

### Basic team with role descriptions
```
Create an agent team to [task]. Spawn three teammates:
- One focused on [role A]
- One focused on [role B]
- One playing devil's advocate
```

### Explicit size + model
```
Create a team with 4 teammates to refactor these modules in parallel.
Use Sonnet for each teammate.
```

### Using a named subagent definition
```
Spawn a teammate using the security-reviewer agent type to audit the auth module.
```
The teammate honors that definition's `tools` allowlist and `model`. Team coordination tools (`SendMessage`, task tools) are always available regardless of `tools` restrictions.

### With plan approval gate
```
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```
Approval flow: teammate plans → sends request to lead → lead approves or rejects with feedback → if approved, teammate implements.

---

## Controlling the Team

### Navigate teammates (in-process mode)
- **Shift+Down** — cycle to next teammate
- **Enter** — view a teammate's session
- **Escape** — interrupt a teammate's current turn
- **Ctrl+T** — toggle the task list

### Assign vs. self-claim tasks
- **Lead assigns**: "Give the database schema task to the backend teammate"
- **Self-claim**: after finishing, a teammate automatically picks the next unblocked task

### Tell lead to wait
If the lead starts doing work instead of delegating:
```
Wait for your teammates to complete their tasks before proceeding
```

### Shut down a teammate
```
Ask the researcher teammate to shut down
```
The teammate can approve (exits gracefully) or reject with explanation.

### Clean up the entire team
```
Clean up the team
```
**Always use the lead for cleanup** — not a teammate. The lead checks for active teammates and fails if any are still running (shut them down first).

---

## Context and Communication

### What teammates get at spawn
- Project `CLAUDE.md` files (from their working directory — works normally)
- MCP servers (from project + user settings)
- Skills (from project + user settings)
- The spawn prompt from the lead
- **NOT**: the lead's conversation history

### What teammates do NOT get
- Lead's conversation history
- Skills/MCP servers from a subagent definition's frontmatter (use project settings instead)

### Messaging
- Messages are **delivered automatically** — lead doesn't need to poll
- Send to one specific teammate by name
- To reach everyone: send one message per recipient
- Idle notifications: when a teammate stops, it automatically notifies the lead

### Predictable teammate names
Tell the lead what to call each teammate in the spawn instruction to get names you can reference later:
```
Spawn a teammate named "backend" for the API layer and one named "frontend" for the UI.
```

---

## Permissions

- Teammates start with the **lead's permission settings**
- If lead runs with `--dangerously-skip-permissions`, all teammates do too
- You can change individual teammate modes **after spawning** only
- Cannot set per-teammate permission modes at spawn time
- **Pre-approve common operations** before spawning to reduce permission prompt friction

---

## Hooks for Quality Gates

| Hook | When it fires | Exit code 2 effect |
|---|---|---|
| `TeammateIdle` | Teammate about to go idle | Sends feedback, keeps teammate working |
| `TaskCreated` | Task being created | Prevents creation, sends feedback |
| `TaskCompleted` | Task being marked complete | Prevents completion, sends feedback |

Use hooks to enforce: test coverage, code review sign-off, style compliance, etc.

---

## Token Cost Guidance

- Token usage **scales linearly** with active teammates
- Each teammate has its own context window
- **3–5 teammates** is the sweet spot for most workflows
- **5–6 tasks per teammate** keeps everyone productive
- For routine tasks: single session is more cost-effective
- For research, review, parallel implementation: extra tokens usually worthwhile

---

## Best Practices

### Team size
- Start with **3–5 teammates** for most tasks
- 5–6 tasks per teammate is optimal
- More teammates ≠ faster; coordination overhead grows non-linearly
- Scale up only when work genuinely parallelizes

### Task sizing
- **Too small**: coordination overhead > benefit
- **Too large**: risk of wasted effort before check-in
- **Just right**: self-contained unit with a clear deliverable (a function, a test file, a review)

### File conflict avoidance
**Two teammates must never edit the same file.** Structure work so each teammate owns a distinct set of files. When designing team structure, map teammate → files explicitly.

### Context in spawn prompts
Since teammates don't inherit conversation history, include everything task-specific in the spawn prompt:
```
Spawn a security reviewer with the prompt: "Review src/auth/ for security vulnerabilities.
Focus on token handling, session management, and input validation. The app uses JWT
tokens stored in httpOnly cookies. Report issues with severity ratings."
```

### Starting fresh with teams
For your first agent team tasks, prefer **read-only work** (PR review, research, bug investigation) over parallel code writing. Clearer value, fewer coordination pitfalls.

### Monitoring
- Check in regularly — don't let a team run fully unattended for long
- Redirect approaches that aren't working
- Synthesize findings as they arrive

---

## Use Case Patterns

### Parallel code review (3 reviewers, distinct lenses)
```
Create an agent team to review PR #142. Spawn three reviewers:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```

### Competing hypotheses debugging
```
Users report [symptom]. Spawn 5 agent teammates to investigate different hypotheses.
Have them talk to each other to try to disprove each other's theories, like a
scientific debate. Update the findings doc with whatever consensus emerges.
```
*Why this works:* sequential investigation suffers from anchoring; adversarial teammates self-correct for it.

### Multi-angle exploration (new feature/design)
```
I'm designing [feature]. Create an agent team to explore this from different angles:
one teammate on UX, one on technical architecture, one playing devil's advocate.
```

### Cross-layer parallel implementation
```
Implement [feature] across the stack. Spawn three teammates:
- "backend" owns src/api/ and src/services/
- "frontend" owns src/components/ and src/pages/
- "tests" owns tests/ (waits for backend + frontend to finish first)
```

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Teammates not appearing | Press Shift+Down; check task complexity; verify tmux is in PATH |
| Too many permission prompts | Pre-approve in permission settings before spawning |
| Teammate stops on error | Give direct instructions via Shift+Down, or spawn replacement |
| Lead shuts down early | "Keep going — wait for teammates to finish" |
| Task appears stuck | Check if work is done; tell lead to nudge the teammate or mark it complete manually |
| Orphaned tmux session | `tmux ls` then `tmux kill-session -t <name>` |

---

## Known Limitations (Experimental)

| Limitation | Workaround |
|---|---|
| `/resume` and `/rewind` don't restore in-process teammates | Spawn new teammates after resuming |
| Task status can lag (task not marked complete) | Tell lead to nudge teammate or update manually |
| Shutdown can be slow | Teammates finish current request first; wait |
| One team at a time | Clean up current team before creating another |
| No nested teams | Only the lead can manage the team |
| Lead is fixed for team's lifetime | Cannot promote or transfer leadership |
| Split panes: tmux or iTerm2 only | Use in-process mode in unsupported terminals |

---

## Design Principles for Effective Teams

1. **Independence first**: structure tasks so teammates rarely need to coordinate. Coordination is overhead.
2. **Explicit file ownership**: map each teammate to specific files/directories in the spawn prompt.
3. **Front-load context**: the spawn prompt is the only briefing a teammate gets — make it complete.
4. **Adversarial review beats parallel agreement**: when finding problems, design teams where teammates actively try to disprove each other.
5. **Lead as synthesizer, not implementer**: the lead's job is coordination and synthesis, not doing work itself.
6. **Hooks as quality gates**: use `TeammateIdle` + `TaskCompleted` hooks to enforce standards automatically, not through manual review.
7. **Named teammates for predictability**: give teammates predictable names you can reference in follow-up prompts.

---

*Source: https://code.claude.com/docs/en/agent-teams — Retrieved 2026-06-02*
