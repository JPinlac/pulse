---
name: recompute
description: Recalculate priority weights across all Maps. Use to force-refresh after vault changes or to inspect the current weight landscape.
user-invocable: true
model: sonnet
effort: high
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
srsa: Sense
---

## Recompute Priority Weights

Force-refresh priority computation. Thin wrapper around `pulse-engine/scripts/pulse-calc.py` — use when vault state has changed mid-session and you want updated numbers without waiting for the next day's `/pulse`.

### Sense — Compute

Run the script (always fresh — ignore any existing cache):
```bash
uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --briefing --cache "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-calc.json"
```

This overwrites today's cache file so subsequent `/pulse` calls pick up the new values.

**If the script fails**, fall back to inline computation using SYSTEM.md Section 7 formulas.

### Act — Persist

1. **Update** each Map's `priority_weight` and `open_loops` in frontmatter (from script's `efforts` output).
2. **Update `Maps/INDEX.md`** — rebuild table from script output, ordered by `priority_weight` descending.

### Surface — Show the Math

3. Present the weight table with component breakdowns and deltas from previous values:
```
## Priority Weights — [date]

| Effort | Weight | Loops | Base | Rec | Urg | Loop | Cal | Δ |
|--------|--------|-------|------|-----|-----|------|-----|---|
...

### Changes
- [effort] ↑ X.XX → X.XX (reason)
```

### Act — Log

4. Append weight table to `Daily/logs/YYYY-MM-DD-log.md`:
```
### Recompute — HH:MM

[same table as above with urgency sources and calibration notes]
```

### Principles
- Weights reflect reality, not aspiration
- Transparent: always show the math
- `$ARGUMENTS` can force a specific effort spike (e.g., "work critical bug")
