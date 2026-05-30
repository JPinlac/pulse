---
name: capacity
description: Capacity prediction — backtest agenda against sleep/practice/load signals. Run after agenda is confirmed. Asks for inputs, classifies items, computes budget vector, logs to session log.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
srsa: Sense+Surface+Act
---

## Capacity Prediction

Backtest a confirmed agenda against capacity signals. The agenda is built from intuition; this protocol applies capacity math as a backtest, not an input (per 2026-04-16 methodology correction — collapsing these conflates two independent signals).

**Precondition**: Agenda exists in today's Daily Note. If no agenda, respond: "No agenda in today's Daily Note. Build the agenda first (`/pulse` → confirm direction), then run `/capacity`."

**Reference doc**: `docs/pulse-effort-capacity-inference.md` — tier definitions, budget caps, load multipliers, avoidance patterns, resistance completion modes. Read once per session (Step 1); do not re-derive from scratch.

**Backtest day number**: Read `Notes/pulse-priority-calibration.md` for the current capacity backtest day count. Increment by 1 for today's entry.

### Sense — Gather Inputs

**Step 1 — Parallel reads** (all independent, read simultaneously):

| Source | What to extract |
|--------|----------------|
| Today's Daily Note | Agenda items, frontmatter: `sleep_hours`, `sleep_quality`, `samatha_minutes`, `samatha_quality`, `insight_minutes`, `insight_quality` |
| Prior 3 Daily Notes (D-1, D-2, D-3) | `load_state`, `items_completed`, `items_deferred`, `efforts_touched`, sleep/samatha/insight frontmatter — 3-day recovery trajectory |
| Prior 3 session logs (D-1, D-2, D-3) | Capacity inferences, recompute deltas, Sati entries — running structural comparison and backtest accuracy |
| Today's session log | Existing entries (avoid duplication) |
| Today's cache (`Daily/cache/YYYY-MM-DD-calc.json`) | Weight landscape, important items with due dates, waiting items — ambient load sources |
| `docs/pulse-effort-capacity-inference.md` | Framework reference: tier definitions, budget caps, load multipliers |

The 3-day window captures the burst-and-rest rhythm (doc: "2-3 days heavy depth -> 1-3 days recovery"). A single prior day can't distinguish "start of sprint" from "mid-recovery" — 3 days shows the arc.

**If sleep/samatha not in frontmatter**: Ask the user for capacity inputs:
- Sleep: hours and quality (e.g., "6 hours, fair")
- Samatha: minutes and quality (e.g., "15 min, high")
- Insight: minutes and quality (e.g., "5 min, good")

After receiving, write to today's Daily Note frontmatter: `sleep_hours`, `sleep_quality`, `samatha_minutes`, `samatha_quality`, `insight_minutes`, `insight_quality`.

### Sense — Assess Load Multiplier

**Step 2 — Load state assessment**:

1. Map `sleep_hours` + `sleep_quality` to baseline load
2. Read `samatha_minutes` + `samatha_quality` — modulates absorption capacity, not throughput (practice doesn't offset sleep debt but supports load tolerance)
   Read `insight_minutes` + `insight_quality` — modulates resistance budget. Insight thins hindrances across life, reducing activation energy for resistant items. Samatha enables insight; insight reduces resistance. The pair is the unit.
3. Scan for ambient load sources:
   - Active adversarial threads (contractor, overdue-with-visibility items)
   - Upcoming time-sensitive items (due dates in cache, radar items in Daily Note)
   - Prior day's `load_state` and recovery trajectory (sprint tail, multi-day accumulation)
4. Read the 3-day trajectory:
   - Sleep trend (improving / degrading / flat)
   - Load state trend (D-3 -> D-2 -> D-1 -> today)
   - Completion rate trend (are outcomes degrading despite similar agendas? = accumulating load)
   - Sprint/rest phase detection: 2-3 heavy days -> expect recovery need; 1-2 recovery days -> capacity returning
   - Practice consistency (misses in the window = disruption markers per doc)
5. Assign multiplier:

| Load | Depth mult | Resistance mult |
|------|-----------|----------------|
| Low | 1.0 | 1.0 |
| Moderate | 0.7 | 0.6 |
| High | 0.4 | 0.3 |
| Recovery | 0.1 | 0.0 |

6. State rationale — include trajectory signal, not just today's snapshot. What pulled toward/away from the chosen level.

### Route — Classify and Compute

**Step 3 — Per-item classification**:

For each agenda item assign:
- **Depth tier**: Heavy 0.85 / Substantial 0.50 / Standard 0.20 / Light 0.08 / Minimal 0.00
- **Resistance tier**: High 0.85 / Moderate 0.40 / Low-None 0.00
- Rationale for non-obvious classifications. Common patterns:
  - "Resistance cost paid once per effort-session" (second item in same effort = 0.00)
  - "Time-boxed to Standard" (substantial topic constrained by window)
  - "Intrinsic pull = low resistance" (pulse design, crisis response)
  - "Effort-level resistance inheritance" (new-codebase cold-start, unfamiliar domain)
- Separate committed items from stretch items (agenda already marks these)
- **Between Tasks items are nudges, not commitments.** They appear on the agenda for visibility but do not count toward the prediction denominator, are not classified in the budget vector, and are never logged as "deferred" when they don't happen. The completion rate, budget math, and per-item predictions apply only to committed agenda items.

Output as a table:

| Item | Effort | Depth | D cost | Resistance | R cost |
|------|--------|-------|--------|------------|--------|

**Step 4 — Budget vector**:

```
depth_budget      = 1.0 x load_multiplier_depth
resistance_budget = 1.0 x load_multiplier_resistance

depth_used       = sum(committed item depth costs)
resistance_used  = sum(committed item resistance costs)
```

- Check both constraints independently — overflow in either is a fail
- If stretch items exist, compute a second vector including them
- Flag >=80% as "edge", >100% as "over_budget"
- Output both vectors (committed-only and with-stretch)

**Step 5 — Structural comparison (3-day window)**:

- D-3 -> D-2 -> D-1: What was the trajectory? (escalating depth, recovery arc, flat maintenance)
- Binding constraints across the window: Was it the same dimension each day, or shifting? (persistent resistance bottleneck = effort-level pattern; rotating = compositional)
- Backtest accuracy across the window: How many predictions matched outcomes? Running hit rate builds the backtest signal for phase graduation (doc: "30+ backtested days with structured capture")
- Rhythm detection: Are we in sprint, recovery, or steady-state? Does today's agenda match the phase? (Sprint agenda on recovery day = collapse risk per doc)
- Load accumulation: Did load_state escalate across the 3 days despite similar agendas? (= ambient or baseline load building, not visible from a single day)

Output as a structured comparison table:

| Day | Sleep | Practice | Load | Predicted | Actual | Bottleneck |
|-----|-------|----------|------|-----------|--------|------------|

**Step 6 — Day character**:

- Map to day mode: Recovery / High-load / Normal low-load / Sprint
- Cognitive vs physical item ratio
- Efforts touched (batch spread — 4+ = wishlist flag)
- Name the day's depth slot occupant
- Name the day's resistance slot occupant (if any)

### Surface — Present Prediction

**Step 7 — Disruption tolerance (30% derailment check)**:

- Which items absorb disruption gracefully? (flexible timing, low-depth, parallelizable with life)
- Which items are the hard floor? (externally accountable, time-sensitive, deadline-forced)
- What acute load vectors exist? (active adversarial threads, approaching events, waiting items that could unblock mid-day)
- Does the agenda degrade gracefully (tiered) or catastrophically (flat)?

**Step 8 — Per-item prediction**:

For each item, predict: **complete** / **defer** / **at risk**
- Apply resistance completion modes where relevant (deadline / momentum / reframe)
- Name the most likely deferred item(s) if any dimension is over-budget
- State expected completions as N/M

**Step 9 — Watch conditions**:

- **Upside**: what would open budget? (depth item finishes early, load lifts)
- **Downside**: what would close budget? (acute event, ambient load escalation)
- **Mid-day signals**: anything that would change the prediction if observed

**Present to the user**: Concise summary — load state, budget status (within/edge/over and which dimension), expected completions N/M, key watch condition. Not the full log — just the prediction and what would change it.

### Act — Log

**Step 10 — Write to session log**:

Write inline (main session — single-file session-log append). Append `### Capacity Prediction — HH:MM` to `Daily/logs/YYYY-MM-DD-log.md` with all sections structured as:

1. Backtest day number
2. Load state inputs + rationale
3. Per-item classification table
4. Budget vector(s) — committed and with-stretch
5. Structural comparison (3-day table + trajectory narrative)
6. Day character
7. Disruption tolerance
8. Per-item predictions + expected N/M
9. Watch conditions (upside / downside / mid-day signals)

Write `load_state` to today's Daily Note frontmatter (low / moderate / high / recovery).

### Integration

- **After `/pulse`**: agent knows to suggest `/capacity` once agenda is confirmed and sleep/samatha inputs are available. This is convention, not a hook — the agent prompts, not the system.
- **During `/close`**: backtest outcome is logged — predicted N/M vs actual, which dimension was the binding constraint, whether the prediction matched. This feeds the running accuracy signal for phase graduation.
