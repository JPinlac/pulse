---
type: doc
subtype: reference
efforts: [pulse]
created: 2026-04-15
updated: 2026-04-15
informs:
  - pulse-architecture-improvements
  - pulse-capacity-model
---

# Prioritization Algorithm — Pre-Script Archive

Historical reference for the inline LLM-estimated prioritization algorithm used prior to `scripts/pulse-calc.py` (2026-04-15). Preserved for calibration archaeology and to trace design decisions.

## Context

From system inception through 2026-04-14, all priority weight and effective item score computation happened inline in the LLM's reasoning trace during `/pulse` Phase D. The agent read Map/Note frontmatter, estimated arithmetic in prose, and produced a weight table. This was:
- **Unreliable** — LLM approximation introduced soft rounding and occasional miscounts
- **Fused** — deterministic math and fuzzy judgment ran in the same reasoning pass (SRSA violation: Sense conflated with Surface)
- **Non-auditable** — the thinking trace was the only record of how numbers were derived

The script extraction (2026-04-15) moved all deterministic computation to `scripts/pulse-calc.py`, preserving the same formulas but executing them as Python arithmetic. The agent now consumes structured JSON and applies judgment (fuzzy flags, suppression reasoning, display decisions) on top of reliable numbers.

## Formulas (as of extraction date)

### Priority Weight (per effort)
```
base_score     = base_priority / 10
recency_boost  = max(0, 0.12 × (1 - days_since_last_active / 7))
urgency_spike  = deadline_proximity + blocker_pressure    # capped 0.20
loop_factor    = sum(per_item_weight)                     # uncapped

priority_weight = base_score + recency_boost + urgency_spike + loop_factor + calibration_offset
```

**urgency_spike sub-components** (all sum, hard cap 0.20):
- Notes with `due` within 7d: +0.05 each, max +0.15. Waiting exception: suppress unless within 1d or overdue.
- Notes waiting >3d (no due): +0.02 each, max +0.05
- Minor Actions overdue/same-day: +0.05 each, max +0.15
- Minor Actions within 2d: +0.03 each

**loop_factor per item**: high +0.04, medium +0.02, low +0.01. Default medium. Uncapped.

### Effective Item Score (per item)
```
effective_item_score = effort_priority_weight
  + importance_modifier      # high: +0.08, medium: +0.04, low: +0.00
  + due_proximity_boost      # overdue: +0.10, within 3d: +0.06, within 7d: +0.03
  + status_modifier          # waiting >3d (no due): +0.02, unblocked: +0.02
```

**Waiting exception**: status=waiting AND due exists → suppress due_proximity_boost AND status_modifier unless within 1d of due or overdue.

### Calibration Offset Application
- Read `Notes/pulse-priority-calibration.md` at recompute time
- If effort has 3+ ordering corrections in same direction → offset of +/- 0.03–0.05
- Documented systematic biases in the Patterns section trigger formula-level adjustments
- Offsets applied after raw weight computation (formula uncapped)

### External Input Staleness
Per-effort nudge when activity is high but external input is stale. Cadence by `context_batch`:

| Batch | Cadence |
|-------|---------|
| Work | 7 days |
| Maintenance | 14 days |
| Contemplative | 30 days |
| Projects | 21 days |
| Leisure | 21 days |

Flag when: `last_active` within 7d AND `last_external_input` exceeds cadence (or null). Skip efforts with 0 open loops.

### Display Thresholds (as of extraction)
- Score threshold: >= 0.55
- Floor: 3 items minimum
- Ceiling: 12 items maximum
- No per-effort cap (single effort could dominate all 12 slots)

### Important Items Selection Logic (pre-script)
1. Collect all open items (active/waiting Notes + unchecked Minor Actions) across all Maps
2. Compute `effective_item_score` per item
3. Split waiting items: `status: waiting` excluded unless within 1d of due or overdue
4. Sort main pool by `effective_item_score` descending
5. Show items >= 0.55, floor 3, ceiling 12
6. No suppression piercing — score alone determines surfacing
7. User invokes `/focus` to narrow; Important Items is informational

### Compact View Rendering Rules (pre-script)
- **Batch gating** — suppress when ALL: combined weight < 40% of top batch, no `due` within 7d, no `status: waiting` >3d
- **Effort-level suppression** — within shown batches, omit efforts where `open_loops == 0 AND last_active > 7 days AND no due within 7d`. Exception: resurfacing candidates not suppressed. If all efforts in a batch would be omitted, suppress entire batch.
- **Resurfacing** — Notes where `(today - updated)` exceeds timescale threshold. Thresholds: daily→1d, weekly→6d, monthly→25d, quarterly→75d, biannual→150d, annual→300d, null→6d. Informational nudge, not priority override.
- **Suppressed batches** → fold-line count. Omit fold-line if none suppressed.
- **Housekeeping** → single italic line, stale Maps by name and days. Only if refresh did something.
- **Listening check** → efforts flagged for external input staleness. Context hints: work→"manager/team", learning→"study group/instructor", relationships→"family/friends", practice→"practice community", home→"contractors/admin", side-project→"collaborators/stakeholders". Omit if none.

### Inline Refresh Phases (pre-script)
The agent performed B–D inline in one reasoning pass:

**Phase B — Single Map scan** (read each Map once):
- Extract `base_priority`, `last_active`, `last_external_input`, current `priority_weight`, `open_loops`
- Parse Minor Actions section: unchecked counts per importance, overdue/due-soon urgency
- Staleness: flag Maps where `last_active` exceeds threshold from shortest Note `timescale` (default: weekly → 14d)

**Phase C — Single Note scan** (filter `status: active|waiting`, read each once):
- Collect per Note: `effort`, `importance`, `due`, `updated`, `status`, `depends`

**Phase D — Compute** (no further reads):
1. Reconcile `open_loops` per Map (Notes by effort + unchecked Minor Actions)
2. Flag stale Maps
3. Compute urgency_spike (Notes + Minor Actions, with waiting exception)
4. Compute loop_factor (importance-weighted open items)
5. Compute recency_boost
6. Read calibration file, apply adjustments
7. Compute final priority_weight per Map
8. Resolve dependency states (unblocked +0.02)
9. Compute effective_item_score per item (with waiting-item display split)
10. Compute external input staleness per effort
11. Flag waiting items where days_waiting >= 3

### Post-extraction changes (same session)
- Ceiling raised to 20
- Per-effort cap of 3 introduced for high/medium items — low flows uncapped as peripheral/break-time tasks
- Only Notes under `## Active Threads` count toward loop_factor (reference/theory Notes excluded)

## Known Issues at Time of Extraction

1. **Loop overcounting** — agent manually counted ~20 open loops for pulse; honest count of all active Notes with `efforts: [pulse]` was 45. The agent was implicitly filtering to Active Threads + Minor Actions but the formula spec said "all active/waiting Notes."
2. **Batch inflation** — agent counted sub-theme Notes (theory docs, community notes) as loops; these weren't under Active Threads.
3. **Effort domination** — with 12-item ceiling and no per-effort cap, pulse plan Notes filled positions 3–12 and crowded out actionable items from other efforts.
4. **Maintenance urgency miss** — an appointment deadline (2 days out) was underweighted because the agent's arithmetic missed the urgency boost.

## Calibration History

See `Notes/pulse-priority-calibration.md` for the full correction log. Key patterns at extraction:
- **urgency_spike** had 3 corrections (most-faulted component) — waiting items with future due dates received false urgency
- **base_score** correction: pulse base_priority 9→7 (meta-system shouldn't match livelihood efforts)
- **item_selection**: reference/vision Notes surfacing as actionable tasks

## Informs

- `pulse-architecture-improvements` — the extraction revealed the Sense/Surface boundary more precisely than design docs predicted
- `pulse-capacity-model` — effort cap is a capacity-aware display decision, not just a formula change
