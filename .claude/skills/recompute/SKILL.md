---
name: recompute
description: Recalculate priority weights across all Maps based on base_priority, recency, urgency, and effort. Use to refresh the priority landscape after a period of activity.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Recompute Priority Weights

Recalculate `priority_weight` for every Map in `Maps/`.

### Formula

For each Map, compute:

```
base_score = base_priority / 10                    # normalize to 0-1
recency_boost = (interactions_last_7_days) × 0.03  # +0.03 per touch, max +0.15
urgency_spike = 0.0-0.2                            # from due dates or blockers in linked notes
effort_factor = 0.0-0.1                            # momentum from recent sustained work

raw_weight = base_score + recency_boost + urgency_spike + effort_factor
priority_weight = min(raw_weight, 1.0)              # cap at 1.0
```

### Steps

1. **Read all Maps** in `Maps/` — extract `base_priority`, `last_active`, `open_loops`, `related_efforts`.

2. **Scan Notes** for urgency signals:
   - Notes with `due` dates within 7 days → urgency_spike for their efforts
   - Notes with `status: waiting` that have been waiting >3 days → slight urgency bump

3. **Calculate recency** from `last_active` and Daily notes:
   - Count how many of the last 7 daily notes touched each effort (via `efforts_touched`)
   - Each touch = +0.03, capped at +0.15

4. **Calculate effort** from recent note activity:
   - Count notes in each effort updated in the last 7 days
   - Sustained work (3+ notes updated) = +0.05 to +0.10

5. **Compute and update** each Map's `priority_weight` in its frontmatter.

6. **Update `Home.md`** — refresh the Current Focus section with the top 3-5 items based on new weights.

7. **Present the results**:

```
## Priority Weights — [date]

| Effort | Base | Recency | Urgency | Effort | Weight |
|--------|------|---------|---------|--------|--------|
| [name] | X.XX | +X.XX   | +X.XX   | +X.XX  | X.XX   |
...

### Changes
- [effort] ↑ X.XX → X.XX (reason)
- [effort] ↓ X.XX → X.XX (reason)
```

8. **Log recompute snapshot** — append a timestamped weight table to `## Session Log` in today's Daily Note (`Daily/YYYY-MM-DD.md`). Create the section if it doesn't exist. This is the same table from step 7, persisted for later debugging.

   Format:
   ```
   ### Recompute — HH:MM

   | Effort | Base | Recency | Urgency | Effort | Weight | Δ |
   |--------|------|---------|---------|--------|--------|---|
   | [name] | X.XX | +X.XX   | +X.XX   | +X.XX  | X.XX   | ↑/↓/= X.XX |
   ...

   Urgency sources: [note-slug (due in N days)], [note-slug (waiting N days)]
   ```

   Include the delta column showing change from previous weight. Include the urgency sources line listing which specific Notes contributed urgency spikes. If no Daily Note exists yet, create one with minimal frontmatter and the Session Log section.

### Principles
- Weights reflect reality, not aspiration
- High base_priority efforts should almost always be near the top unless there's genuine urgency elsewhere
- Spikes are temporary — they decay if not reinforced by continued activity
- Transparent: always show the math so the user can challenge the weights
- $ARGUMENTS can optionally force a specific effort spike (e.g., "side-project critical bug")
