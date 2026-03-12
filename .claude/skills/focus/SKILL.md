---
name: focus
description: Pivot to a specific effort — inspiration override. Loads the relevant Map, shows active threads, and logs the context switch. Use when you want to work on something specific right now.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep
argument-hint: <effort name>
---

## Focus — Inspiration Override

The user wants to focus on a specific effort. Pivot immediately — no friction, no "but your schedule says..."

### Input
Target effort: $ARGUMENTS

### Steps

1. **Resolve the effort** — match $ARGUMENTS flexibly against effort names, slugs, and aliases (case-insensitive, partial match). If ambiguous, ask.

2. **Load the Map** — read the full Map file for the target effort.

3. **Show the effort context**:

```
## Focusing: [Effort Name] (weight: X.XX)

### Active Threads
- [thread 1 with linked notes]
- [thread 2 with linked notes]

### Related Notes
[Recent notes in this effort from Notes/]

### Related Maps: [list with weights]

### What do you want to work on?
```

4. **Log the context switch** in today's Daily note (create one if it doesn't exist):
   - Add the effort's domain to `domains_touched[]` in frontmatter
   - Add a line: `> Pivoted to [effort] at [time]`

5. **Apply recency boost** — update the Map's `last_active` to today.

### Principles
- Zero friction. The moment the user says "focus X", you're there.
- Show enough context to pick up where they left off, but don't overwhelm
- If the effort has related Maps with high-weight open loops, mention them briefly as potential cross-pollination — but don't redirect
- Strike when inspiration strikes
