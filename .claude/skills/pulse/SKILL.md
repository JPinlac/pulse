---
name: pulse
description: Start a PULSE session — load priorities, show current focus, and surface what matters now. Use at the beginning of any work session.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
---

## PULSE Session Start

You are the agent interface for a PULSE (Priority-Updated Living System Engine) Obsidian vault.

### Protocol

1. **Check for bootstrap** — if `Maps/` contains no `.md` files, read `efforts.yaml` and generate a Map for each effort using the Map template in `Templates/Map.md`. Populate frontmatter from the effort config (domain slug, base_priority, context_batch, purpose). Then proceed with step 2.

2. **Light defrag** — before the briefing, run a light defrag pass:
   - Auto-triage any pending Inbox items (files where `triaged: false`) — classify, file into Notes, update Maps, no confirmation
   - Reconcile Map `open_loops` counts against actual active/waiting Notes
   - Flag stale Maps (`last_active` > 14 days)
   - Log what was cleaned up to today's Daily note (under `## Defrag Log`)

3. **Read `Home.md`** for the current focus dashboard and priority overview.

4. **Scan all Maps** in `Maps/` — read each file's frontmatter to get `priority_weight`, `open_loops`, `last_active`, and `related_domains`.

5. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`) if it exists — check what's already been generated or completed.

6. **Present a session briefing** in this format:

```
## PULSE — [date]

### Top Priorities
1. [effort] (weight: X.XX) — [top open loop or thread]
2. [effort] (weight: X.XX) — [top open loop or thread]
3. [effort] (weight: X.XX) — [top open loop or thread]

### Context Batches Available
- [Batch Name] [combined weight]: effort-a, effort-b
  Context: [shared_context summary from efforts.yaml]
- [Batch Name] [combined weight]: effort-c, effort-d
  Context: [shared_context summary from efforts.yaml]

### What would you like to focus on?
```

Build the context batch listing dynamically by reading the `context_batch` field from each Map's frontmatter. Group efforts by their batch and sum their weights. Read `shared_context` from `efforts.yaml` batch definitions and include a summary line so the user can see what each batch involves (tools, codebases, stakeholder worlds).

7. **Wait for direction.** Do not generate a checklist unless asked. Do not assume what the user wants to work on.

Note: The Inbox count is no longer shown as a separate section since auto-triage handles pending items during the light defrag step. If any items were triaged, they appear in the Housekeeping section.

### Key Principles
- Lead with what matters, not what's overdue
- Surface cross-effort tensions if efforts compete for time
- If `last_active` on any Map is stale (>7 days), mention it briefly
- Keep the briefing concise — this is a cockpit, not a report
