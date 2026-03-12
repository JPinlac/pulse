# PULSE — Priority-Updated Living System Engine

PULSE is an agent-first personal knowledge system built on Obsidian and Claude Code. You talk, the agent does the bookkeeping — capturing thoughts, computing priorities, and surfacing what matters now.

## Workflow

The entire interface is two commands:

```
/pulse                    ← start here
  talk, plan, do, capture
/close                    ← end here
```

Everything between `/pulse` and `/close` is conversation. You talk about what you're working on, what's on your mind, what needs to happen. The agent captures, organizes, updates priorities, and manages Notes and Maps behind the scenes.

Optionally, `/focus [effort]` drops you into deep flow on a single effort — inspiration override. The context switch is logged, weights adjust, and the system reorganizes around your new focus.

## Quick Setup

1. **Clone this repo** as your vault root (or add as a git submodule):
   ```bash
   git clone <repo-url> my-vault
   cd my-vault
   ```

2. **Start a session** — open Claude Code in this directory and run:
   ```
   /pulse
   ```
   That's it. The repo ships with 3 default efforts — **Work**, **Life Maintenance**, and **Personal Projects** — as pre-built Maps covering the universal domains of any knowledge worker. The agent gives you a priority briefing. You're live.

   When you're ready to tailor efforts to your life, see [Customization](#customization).

3. **Open in Obsidian** (optional) — point Obsidian at this directory for graph view, Dataview tables, and browsing. Install the [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin for dynamic queries.

## How It Works

Each life effort gets a **Map** — a markdown file that serves as the source of truth for that effort. **Notes** are flat files linked to one or more Maps. **Daily checklists** are generated from open loops across all Maps, batched by context group to minimize cognitive switching.

**Priority is computed, not assigned.** Each Map has a `base_priority` (how important this effort is in your life) and a dynamic `priority_weight` that fluctuates with recency, urgency, and momentum. High-priority efforts stay near the top, but a deadline or critical bug can temporarily spike anything.

**Inspiration override** is a first-class concept. When you say "I want to work on X," the agent pivots immediately — no friction, no guilt. The shift is logged, weights adjust, and you're in flow.

You never touch frontmatter. You never manually file things. You say what's on your mind and the system organizes around you.

## Commands

### Core

| Command | What it does |
|---------|-------------|
| `/pulse` | Start a session — loads priorities, surfaces what matters now |
| `/close` | End a session — reflection, then auto-cleanup |

### Optional

| Command | What it does |
|---------|-------------|
| `/focus [effort]` | Deep flow on one effort — inspiration override |
| `/capture` | Quick-capture a thought or task to Inbox |
| `/birdseyereview` | Full landscape audit — zero suppression |
| `/efforts` | Manage efforts — add, splinter, merge, review |

### Automatic

Bookkeeping that runs as part of other commands. Safe to invoke manually — they're idempotent.

| Command | What it does |
|---------|-------------|
| `/triage` | Process Inbox items into Notes and Maps (runs during `/pulse`) |
| `/defrag` | Reconcile, defer, flag stale items (runs after `/close`) |
| `/recompute` | Recalculate priority weights across Maps |

## Development Roadmap

PULSE is built in three stages. Each unlocks after the previous one earns trust through use.

| Stage | Focus | Status |
|-------|-------|--------|
| **1. Structured Overview** | Batched, prioritized view of the full landscape. You verify the system tracks reality. | **Current** |
| **2. Scope Reduction** | System earns the right to hide things. Shows only what needs you today. | Planned |
| **3. Attention Protection** | System manages cognitive budget as a resource. Pushes back on unnecessary switches. | Planned |

Stage 1→2 is the hardest transition — it requires you to stop verifying. That trust only comes from daily use.

## Vault Layout

```
Home.md              ← Dashboard with priorities and recent activity
Maps/                ← One file per effort. Source of truth.
Notes/               ← All content. Flat. Linked from Maps.
Daily/               ← Generated checklists. One per day.
Inbox/               ← Quick capture. Agent triages into Notes.
Templates/           ← Obsidian templates for each file type.
Queries/             ← Saved Dataview queries.
CLAUDE.md            ← Agent conventions and protocol.
SYSTEM.md            ← Full system design spec.
```

## Customization

### Managing efforts
Use `/efforts` for all effort lifecycle operations:

| Command | What it does |
|---------|-------------|
| `/efforts` | Show current effort landscape |
| `/efforts add` | Guided creation with a litmus test to prevent bloat |
| `/efforts splinter <slug>` | Break a complex effort into sub-efforts |
| `/efforts merge <slug> <slug>` | Combine two efforts that have converged |
| `/efforts review` | Audit effort health — flag stale, overlapping, or orphaned efforts |

### Changing priorities
Edit `base_priority` in the Map's frontmatter. Run `/recompute` to recalculate weights.

## Full Reference

See `SYSTEM.md` for the complete design spec: priority formula, frontmatter schemas, workflows, and design decisions.
