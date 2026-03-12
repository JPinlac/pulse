# PULSE — Priority-Updated Living System Engine

PULSE is an agent-first personal knowledge system built on Obsidian and Claude Code. You talk, the agent does the bookkeeping — capturing thoughts, computing priorities, and surfacing what matters now.

## Quick Setup

1. **Clone this repo** as your vault root (or add as a git submodule):
   ```bash
   git clone <repo-url> my-vault
   cd my-vault
   ```

2. **Define your efforts** — tell Claude about the areas of your life you want to track:
   ```
   Create my efforts.yaml based on @efforts.example.yaml. Here are my efforts:
   - Software engineering job (highest priority)
   - Learning Japanese
   - Fitness and nutrition
   - A side project building a recipe app
   ```
   Claude will generate your `efforts.yaml` with proper slugs, priorities, context batches, and aliases.

3. **Start a session** — open Claude Code in this directory and run:
   ```
   /pulse
   ```
   The agent reads your efforts, generates a Map for each one, and gives you a priority briefing. You're live.

4. **Open in Obsidian** (optional) — point Obsidian at this directory for graph view, Dataview tables, and browsing. Install the [Dataview](https://github.com/blacksmithgu/obsidian-dataview) plugin for dynamic queries.

## Commands

| Command | What it does |
|---------|-------------|
| `/pulse` | Start a session — auto-triages Inbox, loads priorities, shows what matters now |
| `/checklist` | Generate or review today's daily checklist |
| `/capture` | Capture a thought, idea, or task to Inbox |
| `/triage` | Auto-process Inbox items into Notes and Maps |
| `/focus [effort]` | Pivot to a specific effort — inspiration override |
| `/review` | End-of-session reflection — what happened, what emerged. Auto-triggers defrag. |
| `/recompute` | Recalculate all priority weights across Maps |
| `/defrag` | Organizational cleanup — reconcile, defer, flag stale items |

## How It Works

Each life effort gets a **Map** — a markdown file that serves as the source of truth for that effort. **Notes** are flat files linked to one or more Maps. **Daily checklists** are generated from open loops across all Maps, batched by context group to minimize cognitive switching.

**Priority is computed, not assigned.** Each Map has a `base_priority` (how important this effort is in your life) and a dynamic `priority_weight` that fluctuates with recency, urgency, and momentum. High-priority efforts stay near the top, but a deadline or critical bug can temporarily spike anything.

**Inspiration override** is a first-class concept. When you say "I want to work on X," the agent pivots immediately — no friction, no guilt. The shift is logged, weights adjust, and you're in flow.

You never touch frontmatter. You never manually file things. You say what's on your mind and the system organizes around you.

## Vault Layout

```
Home.md              ← Dashboard with priorities and recent activity
Maps/                ← One file per effort. Source of truth.
Notes/               ← All content. Flat. Linked from Maps.
Daily/               ← Generated checklists. One per day.
Inbox/               ← Quick capture. Agent triages into Notes.
Templates/           ← Obsidian templates for each file type.
Queries/             ← Saved Dataview queries.
efforts.yaml         ← Your effort definitions (created from example).
efforts.example.yaml ← Example config shipped with the engine.
CLAUDE.md            ← Agent conventions and protocol.
SYSTEM.md            ← Full system design spec.
```

## Customization

### Adding an effort
Add an entry to `efforts.yaml` and run `/pulse` — the agent will generate the new Map automatically.

### Removing an effort
Run `/focus [effort]`, mark remaining items as done or archived, then delete the Map file and remove the entry from `efforts.yaml`.

### Adjusting context batches
Edit the `context_batches` section in `efforts.yaml` and update the `context_batch` field in relevant Maps. The agent reads batches dynamically.

### Changing priorities
Edit `base_priority` in `efforts.yaml` or directly in the Map's frontmatter (the Map is authoritative). Run `/recompute` to recalculate weights.

## Typical Session

```
> /pulse
  Agent reads Maps, shows top priorities.

> /capture automate the deploy pipeline
  Agent files it to Inbox. Auto-triage picks it up next pulse.

> /checklist
  Agent generates today's Daily note — tasks batched by context.

> "Actually, I want to work on the side project first"
  Agent pivots. Loads the Map. Logs the switch.

> /review
  Agent reflects on what happened, what emerged, what patterns are forming.
  Then auto-runs defrag to handle all bookkeeping.
```

## Full Reference

See `SYSTEM.md` for the complete design spec: priority formula, frontmatter schemas, workflows, and design decisions.
