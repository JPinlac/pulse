# PULSE — Priority-Updated Living System Engine

PULSE is an agent-first personal knowledge system built to **reduce the human context load**. You talk, the agent does the bookkeeping — capturing thoughts, computing priorities, and surfacing what matters now. Built on Claude Code's CLI interface and portable markdown files. 

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

1. **Clone this repo**:
   ```bash
   git clone <repo-url> pulse
   cd pulse
   ```

2. **Open Claude Code** in this directory and run:
   ```
   /pulse
   ```
   On first launch, the agent detects an empty vault and walks you through setup conversationally — no config editing, no manual steps. You describe your life; the agent builds the vault.

3. **Close the session** — run `/close` at the end of each session for reflection and cleanup.
   ```
   /close
   ```

**(Optional) Set the vault path** — if your vault lives outside the repo, add to your shell profile:
```bash
export PULSE_VAULT=/path/to/your/pulse-vault
```

## Migrating from a Pre-Separation Vault

The Pulse 1.0 version separated the PULSE engine (`pulse-engine/`) from your personal vault (`pulse-vault/`). If you cloned PULSE before that date, your vault data is in the repo root alongside the engine files. Here's how to upgrade:

**1. Back up your existing vault:**
```bash
cp -r . ../pulse-backup-$(date +%Y-%m-%d)
```

**2. Pull the latest engine:**
```bash
git pull
```

**3. Run `/migrate` in a Claude Code session:**
```
/migrate ../pulse-backup-2026-05-30
```

That's it. The skill will:
- Copy your Maps, Notes, Daily logs, Inbox captures, and Sati entries into `pulse-vault/`
- Move `Maps/Pulse.md` to `Maps/_system/Pulse.md` (new location for system maps)
- Generate `pulse-vault/user.config.yaml` from your effort definitions
- Port any personal overrides from your old `CLAUDE.md` to `pulse-vault/CLAUDE.md`
- Remove conflicting `[INIT]` template Maps
- Run `pulse-calc.py` to validate everything loaded correctly

After migration, your vault data lives in `pulse-vault/` (gitignored) and the engine stays in `pulse-engine/` (public). Future `git pull` updates won't touch your personal data.

> **Note:** `/migrate-graph` is a separate skill for migrating vault items into a Neo4j knowledge graph. That's a different operation — don't confuse the two.

---

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
| **2. Scope Reduction** | System earns the right to hide things. Shows only what needs you today. | Simple/partial |
| **3. Attention Protection** | System manages cognitive budget as a resource. Pushes back on unnecessary switches. | Planned |

Stage 1→2 is the hardest transition — it requires you to stop verifying. That trust only comes from daily use.

## Repository Layout

```
pulse/
├── CLAUDE.md                  ← Thin loader (imports engine + vault config)
├── README.md                  ← This file
├── pulse-engine/              ← Public engine (redistributable, zero personal data)
│   ├── CLAUDE.md              ← Agent conventions
│   ├── SYSTEM.md              ← Full system design spec
│   ├── ENGINE-SPEC.md         ← Engine ↔ vault interface contract
│   ├── user.config.schema.json ← JSON Schema for user.config.yaml
│   ├── user.config.example.yaml ← Starter config (copy to pulse-vault/)
│   ├── scripts/pulse-calc.py  ← Deterministic priority computation
│   ├── docs/                  ← Design theory and reference
│   ├── templates/             ← Obsidian templates
│   └── queries/               ← Saved Dataview queries
└── pulse-vault/               ← Your personal vault (gitignored)
    ├── user.config.yaml       ← Your efforts, batches, codebase registry
    ├── Maps/                  ← One file per effort. Source of truth.
    │   └── _system/Pulse.md   ← Engine meta-effort (system map)
    ├── Notes/                 ← All content. Flat. Linked from Maps.
    ├── Daily/                 ← Session agendas and logs.
    ├── Inbox/                 ← Quick capture. Agent triages into Notes.
    └── Sati/                  ← Emergence awareness log.
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

### Obsidian integration
Point Obsidian at this directory for graph view, Dataview tables, and browsing. Install the [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin for dynamic queries.

## Full Reference

See `SYSTEM.md` for the complete design spec: priority formula, frontmatter schemas, workflows, and design decisions.
