---
name: pulse
description: Start a PULSE session — load priorities, show current focus, and surface what matters now. Use at the beginning of any work session.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
---

## PULSE Session Start

You are the agent interface for a PULSE (Priority-Updated Living System Engine) Obsidian vault.

### Protocol

1. **Check for bootstrap** — if `Maps/` contains no `.md` files, run the `/efforts bootstrap` procedure (present defaults or ask the user to describe their life, then create Maps directly). Then proceed with step 2.

2. **Read `Home.md`** for the current focus dashboard and priority overview.

3. **Read `Maps/INDEX.md`** — get `priority_weight`, `open_loops`, `last_active`, `high_items`, and `next_due` for all efforts in one read. Fall back to scanning all Maps individually if INDEX.md is missing or corrupted.

4. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`) if it exists — check what's already been generated or completed.

4.5. **Freshness check** — evaluate today's Daily note frontmatter (already read in step 4) for `last_refreshed` timestamp, and scan `Inbox/` for untriaged items (Glob — cheap, no file reads):

   | `last_refreshed` | New inbox? | Action |
   |---|---|---|
   | Set today | No | **Skip step 5 entirely** — state is fresh |
   | Set today | Yes | **Phase A only** — triage new inbox items, skip phases B–F |
   | Not set | Any | **Full inline refresh** — run all phases A–F |

   Timestamps are date-scoped: "set" means present in **today's** Daily note frontmatter. A new calendar day = new Daily note with no timestamps = automatic cold start. This is correct — recency and urgency values shift overnight.

   Log to Session Log: `### Startup — HH:MM` with `Freshness: last_refreshed [HH:MM|stale], inbox: [N untriaged]. Skipped: [all|phases B-F|none]`

5. **Inline refresh** — before the briefing, silently run a single-pass refresh that merges defrag reconciliation and recompute into one read cycle:

   **Phase A — Inbox triage** (always runs, even when close flag is set):
   - Auto-triage any pending Inbox items (match content against Maps, create Notes, update Maps — no confirmation)

   **Phase B — Single Map scan** (read each Map once, collect everything):
   - Extract `base_priority`, `last_active`, current `priority_weight`, current `open_loops`
   - Parse Minor Actions section: collect unchecked item counts per importance level and any overdue/due-soon urgency signals
   - Note staleness: flag Maps where `last_active` exceeds the effective threshold derived from the shortest `timescale` among active Notes (default: weekly → 14 days)

   **Phase C — Single Note scan** (filter to `status: active | waiting`, read each once):
   - Collect per Note: `effort`, `importance`, `due`, `updated`, `status`

   **Phase D — Compute (no further reads)**:
   1. Reconcile `open_loops` per Map: count Notes by effort + unchecked Minor Actions
   2. Flag stale Maps from Phase B staleness signals
   3. Compute urgency_spike: Notes with `due` ≤7 days + Minor Actions due signals (overdue/same-day: +0.05, within 2 days: +0.03, max +0.15 from Minor Actions)
   4. Compute loop_factor from importance-weighted open items (per-item: high 0.04, medium 0.02, low 0.01; cap 0.10)
   5. Compute recency_boost from `last_active` (decay formula: `max(0, 0.12 × (1 - days_since_last_active / 7))`)
   6. Read `Notes/pulse-priority-calibration.md` — apply calibration adjustments (pattern-based biases, per-effort offsets from 3+ same-direction corrections)
   7. Compute final `priority_weight` per Map

   **Phase E — Single write pass**:
   - For each Map with changed values, write `priority_weight` + `open_loops` in one frontmatter update
   - Write `Maps/INDEX.md` — update rows for any Maps whose `priority_weight`, `open_loops`, `last_active`, or top-urgency signals changed. Refresh `High Items` and `Next Due` columns from current Minor Actions and Notes. Update frontmatter `updated: YYYY-MM-DD`. Keep rows ordered by `priority_weight` descending.

   **Phase F — Log and stamp freshness**:
   - Single combined entry `### Inline Refresh — HH:MM` with: triage summary, reconciliation results, stale flags + overdue Minor Actions, weight table with deltas (see /recompute log format)
   - Set `last_refreshed: HH:MM` in today's Daily note frontmatter (gates subsequent `/pulse` skip for the rest of the day)

6. **Present a compact session briefing** (default view):

```
## PULSE — [date]

### Important Items
- [item description] ([effort]) — importance: high, due: [date or n/a]
- [item description] ([effort]) — importance: high
- [item description] ([effort]) — importance: high, due: [date]
- [item description] ([effort]) — importance: medium, due: tomorrow
- [item description] ([effort]) — importance: medium
[...all genuinely important items — no artificial cap]

_Housekeeping: [summary]. [Effort] Map stale ([N] days)._
_Resurfacing: [note title] ([effort], monthly — 27 days since last touch)_

**[Batch]** [combined weight] — [effort] ([N] loops), [effort] ([N] loops)
**[Batch]** [combined weight] — [effort] ([N] loops)
> [N] efforts across [N] batches below the fold. Say **unfold** for full landscape.

### What would you like to work on?
```

**Note loading constraint**: Do not speculatively read Notes during /pulse. Map entry summaries and Minor Actions inline text are the primary sources for Important Items. Only read a specific Note if it is directly linked to a `high` importance item in Important Items AND the Map summary is insufficient to describe the item. Never read Notes for medium/low items or for general context-building.

#### Important Items selection logic

Important Items is **item-driven, not effort-driven**. It surfaces all genuinely important open items across all efforts — no artificial cap. In Phase 1, completeness matters more than brevity.
1. Collect all open items (active/waiting Notes + unchecked Minor Actions) across all Maps
2. Sort by: importance (`high` > `medium` > `low`), then effort `priority_weight` as tiebreaker (high base priority + real-world urgency over recency/loop count), then due date proximity (sooner first, no-date last)
3. Show all `high` importance items, plus `medium` items with due dates within 7 days or overdue. Omit `low` items and `medium` items with no near-term pressure.
4. A `high` importance item in a suppressed batch WILL appear in Important Items — importance pierces through suppression
5. The user invokes `/focus` separately if they want to narrow down to a single effort. Important Items is informational — the user just starts working.

#### Compact view rendering rules

- **Batch gating** — suppress a batch when ALL of: combined weight < 40% of top batch, no `due` dates within 7 days, no `status: waiting` items older than 3 days.
- **Effort-level suppression** — within shown batches, omit efforts where `open_loops == 0 AND last_active > 7 days AND no due within 7 days`. Exception: if any Note in that effort has crossed its timescale "surface at" threshold, do NOT suppress — it's due for attention. If all efforts in a batch would be omitted, suppress the entire batch.
- **Importance override** — efforts with any `importance: high` items (Notes or Minor Actions) are exempt from effort-level suppression. Batch gating still applies to batch-line display, but Focus items already pierce through it.
- **Resurfacing** — after Important Items and Housekeeping, list any Notes where `(today - updated)` exceeds the "surface at" threshold for their `timescale`. This is an informational nudge, not a priority override. Thresholds: daily→1d, weekly→6d, monthly→25d, quarterly→75d, biannual→150d, annual→300d. Notes with `timescale: null` use 6 days. Omit the line entirely if nothing is resurfacing.
- **Suppressed batches** collapse into the fold-line count. If no batches are suppressed, omit the fold-line entirely.
- **Housekeeping** renders as a single italic line (no section header), only if the inline refresh did something. Call out stale Maps by name and days.
- **No shared-context descriptions** — those are already internalized. Each batch is a single line with effort names and loop counts.

6.5. **Fuzzy item detection** — after computing Important Items, flag items where ranking confidence is low:
   - Two efforts within 0.05 weight of each other in different batches (arbitrary ordering)
   - High recency (+0.12 or more) on low base (<6) effort (activity volume ≠ importance)
   - Overdue Minor Actions in low-weight Maps (real urgency in suppressed effort)
   - Previous calibration correction touched this effort in a similar position

   Render as 1-2 italic lines after Important Items:
   ```
   _Fuzzy: [effort] (X.XX) — [reason it might be mis-ranked]_
   ```
   Omit if no fuzzy items.

6.6. **Validation prompt** (Phase 1 only) — after Important Items + Fuzzy, add:
   ```
   _Does this ordering match your priorities today?_
   ```
   - Silence or continuation = acceptance
   - If the user corrects the ordering, delegate to a background agent to write a correction entry to `Notes/pulse-priority-calibration.md` with: the mis-ranked effort, full weight breakdown, component at fault, user's reasoning, and correction type (`ordering | suppression-error | missing-item | wrong-urgency`)
   - Log validation result to Session Log as `### Priority Validation — HH:MM`

   **Phase 2 behavior**: Only show validation prompt when fuzzy items exist. Check PAR and phase criteria in `Notes/pulse-priority-calibration.md` to determine current phase.

7. **Log suppression reasoning** — after generating the briefing (step 6), append a suppression trace to `Daily/logs/YYYY-MM-DD-log.md`. Create the file (and `Daily/logs/` directory) if they don't exist. Do NOT write this to the Daily note itself.

   Format:
   ```
   ### Pulse Briefing — HH:MM

   **Important Items**: [item] ([effort], importance: high), [item] ([effort], importance: medium), ...
   **Suppressed batches**:
   - [Batch]: combined weight X.XX < 40% of top (X.XX), no due dates, no stale waiting
   **Suppressed efforts** (within shown batches):
   - [effort]: 0 open loops, last_active [N] days ago, no due within 7d
   **Resurfaced**: [note-slug] ([effort], [timescale] — [N] days since last touch)
   **Inline refresh**: triaged N inbox, reconciled N maps, flagged N stale
   ```

   Omit any section with zero items. The key value here is the suppression reasoning — it records *why* something wasn't shown, which is otherwise invisible and the hardest class of bug to trace.

   If no Daily Note exists yet, create one with minimal frontmatter (no Session Log section — that goes in `Daily/logs/`).

8. **Full view on request** — if the user says "unfold", "full landscape", "show all", or similar at any point in the conversation, present:

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

9. **Wait for direction.** Do not assume what the user wants to work on. When the user indicates direction, build the day's agenda (step 10).

10. **Build the Daily Note from conversation** — when the user indicates what they want to work on:

   a. Create `Daily/YYYY-MM-DD.md` if it doesn't exist (use Daily Note template frontmatter).
   b. Pull top items from the Maps the user indicated interest in — these go first, grouped by batch.
   c. Scan remaining Maps for time-sensitive or routine items. Add as a lightweight section so nothing falls through cracks.
   d. Omit empty efforts. Keep it to 8-15 items — working agenda, not exhaustive audit.
   e. Present the agenda in conversation for one confirmation pass. After confirmation, write to file. Subsequent Daily Note updates during the session happen silently.

### Note on Inbox
Inbox items are auto-triaged during the inline refresh step (Phase A). There is no separate "N items pending triage" line — by the time the briefing is presented, the Inbox should be clear. If auto-triage could not classify an item, mention it in the Housekeeping line.

### Bootstrap
If `Maps/` is empty (no `.md` files), run the `/efforts bootstrap` procedure before continuing with the pulse protocol.

### Key Principles
- Lead with what matters, not what's overdue
- Surface cross-effort tensions if efforts compete for time
- Suppress low-signal efforts — show the cockpit, not the full instrument panel
- Keep the briefing concise — this is a cockpit, not a report
