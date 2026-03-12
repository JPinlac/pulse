---
name: review
description: End-of-day review — walk through the daily checklist, close loops, defer items, annotate what emerged, and update Maps. Use at the end of a work session.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep
---

## End-of-Day Review

Walk through today's work and close the loop.

### Steps

1. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`). If none exists, check what Maps were touched today by looking at `last_active` dates.

2. **Present the review**:

```
## Review — [date]

### Completed
- [x] [item] — [brief note on outcome if any]

### Still Open
- [ ] [item] — Defer to tomorrow? Drop? Waiting on something?

### Emerged Today
- [New items, ideas, or threads that came up during the session]

### Efforts Touched: [list]
```

3. **For each open item**, ask the user:
   - **Defer**: Move to tomorrow (stays active)
   - **Wait**: Blocked on something (status → waiting, note what it's waiting on)
   - **Done**: Completed (status → done)
   - **Drop**: No longer relevant (status → archived)

4. **Update the Daily note**:
   - Fill in the `## End of Day` section with the review summary
   - Update `items_completed` and `items_deferred` counts in frontmatter
   - Finalize `domains_touched` list

5. **Update affected Notes**:
   - Change `status` and `updated` date for any notes that changed state
   - For done items: set `status: done` (will auto-archive after 7 days)

6. **Update affected Maps**:
   - Adjust `open_loops` counts
   - Update `last_active` dates
   - Move completed threads from Active Threads to a "## Completed" section (or remove them)

7. **Surface cross-effort insights** — if work in one effort opened a thread in another, note the connection.

### Principles
- This is reflective, not bureaucratic. Keep it conversational.
- Don't pressure to complete everything. Deferring is fine. Dropping is fine.
- Note what *emerged* — the unplanned stuff is often the most valuable signal
- If patterns appear (same item deferred 3+ times), gently flag it
- $ARGUMENTS can optionally specify a date other than today
