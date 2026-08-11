# PULSE — Agent Rules (opencode)

PULSE is an agent-first personal knowledge system: the user talks, the agent does the bookkeeping — capturing thoughts, computing priorities, and surfacing what matters now. Everything is plain markdown; the vault is the runtime.

## Repo layout

- `pulse-engine/` — the engine: system rules (`pulse-engine/CLAUDE.md`), spec (`ENGINE-SPEC.md`), formulas (`SYSTEM.md`), templates, scripts, docs.
- `pulse-vault/` — the user's content: `Maps/` (one MOC per effort — the source of truth for effort definitions) and `Notes/` (flat content notes).
- `.claude/skills/` — command procedures (Claude Code skill format, reused directly by opencode via the rule below).

## Rules loading

The full engine rules load from `pulse-engine/CLAUDE.md` via the `instructions` array in `opencode.json` — they are already in your context alongside this file. The root `CLAUDE.md` exists for Claude Code (it @-imports the same engine rules); under opencode, do not read it — you'd duplicate what's already loaded.

## Commands (skills)

The interface is two commands — `/pulse` to start a session, `/close` to end it — plus support commands. opencode does not auto-register Claude-format skills, so resolve them on demand:

**When the user invokes a command** — `/pulse`, `/close`, `/capture <thought>`, `/recompute`, `/defrag`, `/triage`, `/focus <effort>`, `/capacity`, `/efforts`, `/birdseyereview`, `/landscape`, `/surfaceUncertainty`, `/migrate`, with or without the leading slash — **read `.claude/skills/<name>/SKILL.md` and follow it exactly.** List `.claude/skills/` for the authoritative command set: the directory, not the sentence above, is the source of truth.

Read skill files lazily — only the one invoked, never speculatively.

All paths in this file are relative to the repo root (the directory containing this `AGENTS.md`) — resolve them from there even when the working directory is a subdirectory like `pulse-vault/`.
