---
name: checklist
description: Generate or review today's daily checklist. Scans all Maps for open loops, batches by context group, and produces a Daily note. Use when starting focused work or reviewing progress.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write
---

## Daily Checklist Generation

Generate or update today's daily checklist at `Daily/YYYY-MM-DD.md`.

### If no daily note exists for today:

1. **Scan all Maps** in `Maps/` — read each file to find open loops, active threads, and items with deadlines.

2. **Scan active Notes** — find notes in `Notes/` where `status: active` or `status: waiting`, especially those with `due` dates approaching.

3. **Group by context batch** — read the `context_batch` field from each Map's frontmatter to determine groupings. Efforts sharing a `context_batch` value are grouped together.

4. **Sort batches** by combined `priority_weight` of their efforts (highest batch first).

5. **Within each batch**, sort items by individual effort priority weight.

6. **Apply batch gating** — after sorting, identify soft-suppressed batches. A batch is suppressed when ALL of:
   - Its combined weight is below **40%** of the top batch's combined weight
   - It has no items with a `due` date within 7 days
   - It has no `status: waiting` items older than 3 days

7. **Generate the Daily note** using the template structure. Full batches get checklist sections; suppressed batches get a single collapsed line:

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

---
## Deferred Batches
> ~[Batch Name] [weight: X.XX] — N items, nothing urgent

---
## Annotations

## End of Day
```

8. **Write the file** to `Daily/YYYY-MM-DD.md`.

### If a daily note already exists:

1. Read the existing daily note.
2. Show current progress — how many items checked vs total.
3. Surface any new items that emerged since generation.
4. Ask if the user wants to add, remove, or reprioritize items.

### Principles
- Each checklist item should link to a Note or Map section
- Keep items actionable and concrete, not vague
- If an effort has no open loops, omit it from the checklist
- Never more than 10-12 items total — this is a focused day, not a backlog dump
- $ARGUMENTS can optionally specify a date other than today
