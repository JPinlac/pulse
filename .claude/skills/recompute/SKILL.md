---
name: recompute
description: Recalculate priority weights across all Maps based on base_priority, recency, urgency, and importance-weighted open loops. Use to refresh the priority landscape after a period of activity.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Recompute Priority Weights

Recalculate `priority_weight` for every Map in `Maps/`.

### Formula

For each Map, compute:

```
base_score = base_priority / 10                    # normalize to 0-1
recency_boost = max(0, 0.12 × (1 - days_since_last_active / 7))  # from Map frontmatter only
# Examples: 0 days → +0.12, 1 day → +0.10, 3 days → +0.07, 5 days → +0.03, 7+ days → 0
urgency_spike = 0.0-0.2                            # from due dates or blockers in linked notes
loop_factor = min(sum(per_item_weight), 0.10)       # importance-weighted open items

raw_weight = base_score + recency_boost + urgency_spike + loop_factor
priority_weight = min(raw_weight, 1.0)              # cap at 1.0
```

Per-item weights for loop_factor: `high: 0.04`, `medium: 0.02`, `low: 0.01`. Default importance is `medium` when unspecified.

### Steps

1. **Read all Maps** in `Maps/` — extract `base_priority`, `last_active`, `open_loops`, `related_efforts`.

2. **Scan Notes** for urgency signals:
   - Notes with `due` dates within 7 days → urgency_spike for their efforts
   - Notes with `status: waiting` that have been waiting >3 days → slight urgency bump

3. **Scan Minor Actions** across all Maps:
   - For each Map, read its `## Minor Actions` section (if present)
   - Resolve informal dates to absolute dates: "tonight" = today, "this weekend" = next Saturday, "before Friday" = Thursday, etc.
   - Overdue or same-day items: +0.05 each to urgency_spike (max +0.15 from Minor Actions)
   - Items due within 2 days: +0.03 each
   - Minor Actions are first-class urgency signals — they feed the formula without requiring Note overhead

4. **Calculate recency** from `last_active` in Map frontmatter:
   - Compute `days_since_last_active = today - last_active`
   - Apply decay formula: `recency_boost = max(0, 0.12 × (1 - days_since_last_active / 7))`
   - No Daily note reads needed for recency — `last_active` is the authoritative signal

5. **Calculate loop_factor** from importance-weighted open items:
   - For each effort, collect open items: active/waiting Notes + unchecked Minor Actions
   - Read `importance` from each item (Note frontmatter or Minor Action inline property). Default: `medium`
   - Sum per-item weights: `high: 0.04`, `medium: 0.02`, `low: 0.01`
   - Cap at 0.10

6. **Compute raw weights** for each Map.

7. **Apply calibration adjustments** — read `Notes/pulse-priority-calibration.md`:
   - Check the **Patterns** section for documented systematic biases. If a pattern identifies a formula component consistently over/under-weighting a class of effort, apply the described adjustment.
   - Check the **Corrections** log: if an effort has 3+ ordering corrections in the same direction (consistently ranked too high or too low), apply a calibration offset of +/- 0.03–0.05 in the correction direction.
   - Calibration offsets are applied after raw weight computation but before capping at 1.0.

8. **Update** each Map's `priority_weight` in its frontmatter.

8.5. **Update `Maps/INDEX.md`** — write-behind after all Map frontmatter updates. Rebuild the full table from current Map values:
   - `slug` from Map `effort` field
   - `weight` from newly computed `priority_weight`
   - `loops` from reconciled `open_loops`
   - `last_active` from Map frontmatter
   - `high_items` — first unchecked `importance: high` Minor Action text; else highest-importance active Note title; else "—"
   - `next_due` — nearest due date across unchecked Minor Actions + active Notes; else "—"
   - Update frontmatter `updated: YYYY-MM-DD`
   - Order rows by `priority_weight` descending

9. **Update `Home.md`** — refresh the Current Focus section with the top 3-5 items based on new weights.

10. **Present the results**:

```
## Priority Weights — [date]

| Effort | Base | Recency | Urgency | Minor | Loops | Calibration | Weight |
|--------|------|---------|---------|-------|--------|-------------|--------|
| [name] | X.XX | +X.XX   | +X.XX   | +X.XX | +X.XX  | +/-X.XX     | X.XX   |
...

### Changes
- [effort] ↑ X.XX → X.XX (reason)
- [effort] ↓ X.XX → X.XX (reason)
```

11. **Log recompute snapshot** — append a timestamped weight table to `Daily/logs/YYYY-MM-DD-log.md`. Create the file (and `Daily/logs/` directory) if they don't exist. Do NOT write to the Daily note itself. This is the same table from step 10, persisted for later debugging.

   Format:
   ```
   ### Recompute — HH:MM

   | Effort | Base | Recency | Urgency | Minor | Loops | Cal | Weight | Δ |
   |--------|------|---------|---------|-------|--------|-----|--------|---|
   | [name] | X.XX | +X.XX   | +X.XX   | +X.XX | +X.XX  | +/-X.XX | X.XX | ↑/↓/= X.XX |
   ...

   Urgency sources: [note-slug (due in N days)], [note-slug (waiting N days)]
   Minor Action sources: [item description (effort, due date/immediacy)]
   Calibration applied: [effort: +/-X.XX (reason)] or "none"
   ```

   Include the delta column showing change from previous weight. Include the urgency sources line listing which specific Notes contributed urgency spikes. If no Daily Note exists yet, create one with minimal frontmatter (no Session Log section — that goes in `Daily/logs/`).

### Implicit Invocation

The /recompute formula runs inline during `/pulse` (step 5, Phase D) and `/close` (step 6.5). When invoked inline, skip the presentation step (step 10), the Home.md update (step 9), and the INDEX.md update (step 8.5) — those are handled by the calling skill. The Session Log entry is always written regardless of invocation mode.

### Principles
- Weights reflect reality, not aspiration
- High base_priority efforts should almost always be near the top unless there's genuine urgency elsewhere
- Spikes are temporary — they decay if not reinforced by continued activity
- Transparent: always show the math so the user can challenge the weights
- $ARGUMENTS can optionally force a specific effort spike (e.g., "side-project critical bug")
