---
name: birdseyereview
description: Bird's-eye view of all efforts — scans all Maps for open loops, batches by context group, and produces a Daily note with everything visible. No suppression.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write
---

## Bird's-Eye Review

Generate or update today's daily overview at `Daily/YYYY-MM-DD.md`. Shows every effort — nothing compressed or suppressed.

### If no daily note exists for today:

1. **Scan all Maps** in `Maps/` — read each file to find open loops, active threads, and items with deadlines.

2. **Scan active Notes** — find notes in `Notes/` where `status: active` or `status: waiting`, especially those with `due` dates approaching.

3. **Group by context batch** to minimize context switching.

4. **Sort batches** by combined `priority_weight` of their efforts (highest batch first).

5. **Within each batch**, sort items by individual effort priority weight.

6. **Generate the Daily note** using the template structure:

```markdown
---
type: daily
date: YYYY-MM-DD
generated: true
domains_touched: []
items_completed: 0
items_deferred: 0
---
# YYYY-MM-DD

## Context A: [batch name] [combined weight: X.XX]
- [ ] Item from highest-priority effort [[linked note or Map]]
- [ ] Next item [[link]]

## Context B: [batch name] [combined weight: X.XX]
- [ ] Item [[link]]

## Context C: [batch name] [combined weight: X.XX]
- [ ] Item [[link]]

## Context D: [batch name] [combined weight: X.XX]
- [ ] Item [[link]]

---
## Annotations

## End of Day
```

7. **Write the file** to `Daily/YYYY-MM-DD.md`.

### If a daily note already exists:

1. Read the existing daily note.
2. Show current progress — how many items checked vs total.
3. Surface any new items that emerged since generation.
4. Ask if the user wants to add, remove, or reprioritize items.

### Principles
- Every batch is rendered fully — no suppression, no collapsed lines
- Each checklist item should link to a Note or Map section
- Keep items actionable and concrete, not vague
- If an effort has no open loops, omit it from the checklist
- $ARGUMENTS can optionally specify a date other than today

### Relationship to /pulse
/pulse builds a focused daily agenda conversationally (8-15 items). /birdseyereview shows EVERYTHING — useful when you need the full instrument panel, not the cockpit.
