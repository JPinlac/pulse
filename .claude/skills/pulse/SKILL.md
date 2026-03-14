---
name: pulse
description: Start a PULSE session — load priorities, show current focus, and surface what matters now. Use at the beginning of any work session.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
---

## PULSE Session Start

You are the agent interface for a PULSE (Priority-Updated Living System Engine) Obsidian vault.

### Protocol

1. **Check for bootstrap** — if `Maps/` contains no `.md` files, run the `/efforts` bootstrap procedure (present defaults or ask user to describe their life, then create Maps directly). Then proceed with step 2.

2. **Light defrag** — before the briefing, silently run a light defrag pass:
   - Auto-triage any pending Inbox items (files where `triaged: false`) — classify, file into Notes, update Maps, no confirmation
   - Reconcile Map `open_loops` counts against actual active/waiting Notes
   - For each Map, determine its effective staleness threshold from the shortest `timescale` among its active Notes (default: weekly → 14 days). Flag Maps where `last_active` exceeds that threshold.

3. **Read `Home.md`** for the current focus dashboard and priority overview.

4. **Scan all Maps** in `Maps/` — read each file's frontmatter to get `priority_weight`, `open_loops`, `last_active`, and `related_efforts`.

5. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`) if it exists — check what's already been generated or completed.

5.5. **Check close flag** — read yesterday's Daily Note (`Daily/YYYY-MM-DD.md` for yesterday) frontmatter for `close_complete: true`.
   - **If true**: skip step 2 (light defrag) and step 6 (inline recompute) — the previous `/close` already ran both. Exception: scan `Inbox/` for new untriaged items; if any found, run only the auto-triage substep from step 2.
   - **If false or missing**: proceed with steps 2 and 6 as normal (previous session didn't close cleanly or there was no previous session).
   - Log skip decision to Session Log: `### Startup — HH:MM` with `Close flag: [found|not found], skipped: [defrag+recompute|none], inbox: [N new items triaged]`

6. **Inline recompute** — execute the /recompute formula inline (not as separate skill invocation):
   - Read all Maps for base_priority, last_active, open_loops
   - Scan Notes for urgency signals (due dates, stale waiting items)
   - Scan Minor Actions across all Maps for urgency signals (overdue/same-day: +0.05, within 2 days: +0.03, max +0.15 from Minor Actions)
   - Calculate recency from Daily notes (last 7 days)
   - Calculate loop_factor from importance-weighted open items (per-item: high 0.04, medium 0.02, low 0.01; cap 0.10)
   - Compute raw weights
   - Read `Notes/pulse-priority-calibration.md` — apply calibration adjustments (pattern-based biases, per-effort offsets from 3+ same-direction corrections)
   - Update Map frontmatter with fresh weights
   - Log weight table to Session Log (see /recompute format)

7. **Present a compact session briefing** (default view):

```
## PULSE — [date]

### Focus
1. [item description] ([effort]) — importance: high, due: [date or n/a]
2. [item description] ([effort]) — importance: high
3. [item description] ([effort]) — importance: high, due: [date]
4. [item description] ([effort]) — importance: medium, due: tomorrow
5. [item description] ([effort]) — importance: medium

_Housekeeping: [summary]. [Effort] Map stale ([N] days)._
_Resurfacing: [note title] ([effort], monthly — 27 days since last touch)_

**[Batch]** [combined weight] — [effort] ([N] loops), [effort] ([N] loops)
**[Batch]** [combined weight] — [effort] ([N] loops)
> [N] efforts across [N] batches below the fold. Say **unfold** for full landscape.

### What would you like to focus on?
```

#### Focus selection logic

Focus is **item-driven, not effort-driven**. It surfaces the most important open items across all efforts:
1. Collect all open items (active/waiting Notes + unchecked Minor Actions) across all Maps
2. Sort by: importance (`high` > `medium` > `low`), then due date proximity (sooner first, no-date last), then effort `priority_weight` as tiebreaker
3. Show top 5 items with effort attribution
4. A `high` importance item in a suppressed batch WILL appear in Focus — importance pierces through suppression

#### Compact view rendering rules

- **Batch gating** — suppress a batch when ALL of: combined weight < 40% of top batch, no `due` dates within 7 days, no `status: waiting` items older than 3 days.
- **Effort-level suppression** — within shown batches, omit efforts where `open_loops == 0 AND last_active > 7 days AND no due within 7 days`. Exception: if any Note in that effort has crossed its timescale "surface at" threshold, do NOT suppress — it's due for attention. If all efforts in a batch would be omitted, suppress the entire batch.
- **Importance override** — efforts with any `importance: high` items (Notes or Minor Actions) are exempt from effort-level suppression. Batch gating still applies to batch-line display, but Focus items already pierce through it.
- **Resurfacing** — after Focus and Housekeeping, list any Notes where `(today - updated)` exceeds the "surface at" threshold for their `timescale`. This is an informational nudge, not a priority override. Thresholds: daily→1d, weekly→6d, monthly→25d, quarterly→75d, biannual→150d, annual→300d. Notes with `timescale: null` use 6 days. Omit the line entirely if nothing is resurfacing.
- **Suppressed batches** collapse into the fold-line count. If no batches are suppressed, omit the fold-line entirely.
- **Housekeeping** renders as a single italic line (no section header), only if the light defrag did something. Call out stale Maps by name and days.
- **No shared-context descriptions** — those are already internalized. Each batch is a single line with effort names and loop counts.

7.5. **Fuzzy item detection** — after computing Focus, flag items where ranking confidence is low:
   - Two efforts within 0.05 weight of each other in different batches (arbitrary ordering)
   - High recency (+0.12 or more) on low base (<6) effort (activity volume ≠ importance)
   - Overdue Minor Actions in low-weight Maps (real urgency in suppressed effort)
   - Previous calibration correction touched this effort in a similar position

   Render as 1-2 italic lines after Focus:
   ```
   _Fuzzy: [effort] (X.XX) — [reason it might be mis-ranked]_
   ```
   Omit if no fuzzy items.

7.6. **Validation prompt** (Phase 1 only) — after Focus + Fuzzy, add:
   ```
   _Does this Focus ordering match your priorities today?_
   ```
   - Silence or continuation = acceptance
   - If the user corrects the ordering, delegate to a background agent to write a correction entry to `Notes/pulse-priority-calibration.md` with: the mis-ranked effort, full weight breakdown, component at fault, user's reasoning, and correction type (`ordering | suppression-error | missing-item | wrong-urgency`)
   - Log validation result to Session Log as `### Priority Validation — HH:MM`

   **Phase 2 behavior**: Only show validation prompt when fuzzy items exist. Check PAR and phase criteria in `Notes/pulse-priority-calibration.md` to determine current phase.

8. **Log suppression reasoning** — after generating the briefing (step 7), append a suppression trace to `## Session Log` in today's Daily Note (`Daily/YYYY-MM-DD.md`). Create the section if it doesn't exist.

   Format:
   ```
   ### Pulse Briefing — HH:MM

   **Focus items**: [item] ([effort], importance: high), [item] ([effort], importance: medium), ...
   **Suppressed batches**:
   - [Batch]: combined weight X.XX < 40% of top (X.XX), no due dates, no stale waiting
   **Suppressed efforts** (within shown batches):
   - [effort]: 0 open loops, last_active [N] days ago, no due within 7d
   **Resurfaced**: [note-slug] ([effort], [timescale] — [N] days since last touch)
   **Light defrag**: triaged N inbox, reconciled N maps, flagged N stale
   ```

   Omit any section with zero items. The key value here is the suppression reasoning — it records *why* something wasn't shown, which is otherwise invisible and the hardest class of bug to trace.

   If no Daily Note exists yet, create one with minimal frontmatter and the Session Log section.

9. **Full view on request** — if the user says "unfold", "full landscape", "show all", or similar at any point in the conversation, present:

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

10. **Wait for direction.** Do not assume what the user wants to work on. When the user indicates direction, build the day's agenda (step 11).

11. **Build the Daily Note from conversation** — when the user indicates what they want to work on:

   a. Create `Daily/YYYY-MM-DD.md` if it doesn't exist (use Daily Note template frontmatter).
   b. Pull top items from the Maps the user indicated interest in — these go first, grouped by batch.
   c. Scan remaining Maps for time-sensitive or routine items. Add as a lightweight section so nothing falls through cracks.
   d. Omit empty efforts. Keep it to 8-15 items — working agenda, not exhaustive audit.
   e. Present the agenda in conversation for one confirmation pass. After confirmation, write to file. Subsequent Daily Note updates during the session happen silently.

### Note on Inbox
Inbox items are auto-triaged during the light defrag step. There is no separate "N items pending triage" line — by the time the briefing is presented, the Inbox should be clear. If auto-triage could not classify an item, mention it in the Housekeeping line.

### Bootstrap
If `Maps/` is empty (no `.md` files), run the `/efforts bootstrap` procedure before continuing with the pulse protocol.

### Key Principles
- Lead with what matters, not what's overdue
- Surface cross-effort tensions if efforts compete for time
- Suppress low-signal efforts — show the cockpit, not the full instrument panel
- Keep the briefing concise — this is a cockpit, not a report
