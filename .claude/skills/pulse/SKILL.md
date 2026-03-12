---
name: pulse
description: Start a PULSE session — load priorities, show current focus, and surface what matters now. Use at the beginning of any work session.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
---

## PULSE Session Start

You are the agent interface for a PULSE (Priority-Updated Living System Engine) Obsidian vault.

### Protocol

1. **Check for bootstrap** — if `Maps/` contains no `.md` files, read `efforts.yaml` and generate a Map for each effort using the Map template in `Templates/Map.md`. Populate frontmatter from the effort config (effort slug, base_priority, context_batch, purpose). Then proceed with step 2.

2. **Light defrag** — before the briefing, silently run a light defrag pass:
   - Auto-triage any pending Inbox items (files where `triaged: false`) — classify, file into Notes, update Maps, no confirmation
   - Reconcile Map `open_loops` counts against actual active/waiting Notes
   - Note any Maps where `last_active` is >7 days stale

3. **Read `Home.md`** for the current focus dashboard and priority overview.

4. **Scan all Maps** in `Maps/` — read each file's frontmatter to get `priority_weight`, `open_loops`, `last_active`, and `related_domains`.

5. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`) if it exists — check what's already been generated or completed.

6. **Present a compact session briefing** (default view):

```
## PULSE — [date]

### Focus
1. [effort] (weight: X.XX) — [top open loop or thread]
2. [effort] (weight: X.XX) — [top open loop or thread]
3. [effort] (weight: X.XX) — [top open loop or thread]

_Housekeeping: [summary]. [Effort] Map stale ([N] days)._

**[Batch]** [combined weight] — [effort] ([N] loops), [effort] ([N] loops)
**[Batch]** [combined weight] — [effort] ([N] loops)
> [N] efforts across [N] batches below the fold. Say **unfold** for full landscape.

### What would you like to focus on?
```

#### Compact view rendering rules

- **Batch gating** — suppress a batch when ALL of: combined weight < 40% of top batch, no `due` dates within 7 days, no `status: waiting` items older than 3 days.
- **Effort-level suppression** — within shown batches, omit efforts where `open_loops == 0 AND last_active > 7 days AND no due within 7 days`. If all efforts in a batch would be omitted, suppress the entire batch.
- **Suppressed batches** collapse into the fold-line count. If no batches are suppressed, omit the fold-line entirely.
- **Housekeeping** renders as a single italic line (no section header), only if the light defrag did something. Call out stale Maps by name and days.
- **No shared-context descriptions** — those are already internalized. Each batch is a single line with effort names and loop counts.

7. **Full view on request** — if the user says "unfold", "full landscape", "show all", or similar at any point in the conversation, present:

```
### Full Landscape

**[Batch]** [combined weight]
- [effort] (weight: X.XX) — [N] open loops, last active [date]
  [Top thread or "No active threads"]
- [effort] (weight: X.XX) — [N] open loops, last active [date]
  [Top thread or "No active threads"]

[...all batches, ordered by combined weight...]

### Stale Maps
- [effort] — last active [N] days ago
[Only if any Maps have last_active > 7 days. Otherwise omit.]
```

8. **Wait for direction.** Do not assume what the user wants to work on. When the user indicates direction, build the day's agenda (step 9).

9. **Build the Daily Note from conversation** — when the user indicates what they want to work on:

   a. Create `Daily/YYYY-MM-DD.md` if it doesn't exist (use Daily Note template frontmatter).
   b. Pull top items from the Maps the user indicated interest in — these go first, grouped by batch.
   c. Scan remaining Maps for time-sensitive or routine items. Add as a lightweight section so nothing falls through cracks.
   d. Omit empty efforts. Keep it to 8-15 items — working agenda, not exhaustive audit.
   e. Present the agenda in conversation for one confirmation pass. After confirmation, write to file. Subsequent Daily Note updates during the session happen silently.

### Note on Inbox
Inbox items are auto-triaged during the light defrag step. There is no separate "N items pending triage" line — by the time the briefing is presented, the Inbox should be clear. If auto-triage could not classify an item, mention it in the Housekeeping line.

### Key Principles
- Lead with what matters, not what's overdue
- Surface cross-effort tensions if efforts compete for time
- Suppress low-signal efforts — show the cockpit, not the full instrument panel
- Keep the briefing concise — this is a cockpit, not a report
