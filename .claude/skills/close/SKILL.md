---
name: close
description: Session-close ritual — reflect on what happened, what emerged, what patterns are forming. Flags items needing attention, then auto-triggers /defrag.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Session Close

Pure reflection. No item-by-item status decisions. The agent presents a narrative, the human reflects, then defrag handles the bookkeeping.

### Steps

1. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`). If none exists, check what Maps were touched today by looking at `last_active` dates.

2. **Read relevant Maps and Notes** — gather context on what moved today across all active efforts.

3. **Present a reflection narrative**:

```
## Reflection — [date]

### What Happened
[Narrative summary of the session — what efforts were touched, what work was done,
what conversations happened. Written as prose, not a checklist.]

### What Emerged
[New threads, ideas, or connections that surfaced during the session.
The unplanned stuff — often the most valuable signal.]

### Patterns
[Observations about recurring themes, cross-effort tensions, or shifts in energy.
Only include if genuinely noticed — don't fabricate patterns.]
```

4. **Flag items needing human attention** — only surface things that genuinely need a decision:
   - Items deferred 3+ times (pattern of avoidance — worth naming)
   - Efforts that went dark (active Notes not touched in 14+ days with no status change)
   - Cross-effort tensions (competing priorities that can't both win)
   - Anything that seems stuck or misaligned with stated goals

5. **Invite reflection** — "Anything else on your mind before I clean up?" This is optional. If the user has nothing to add, move on.

6. **If the user volunteers status changes** during the reflection conversation (e.g., "that thing is done" or "drop that one"), apply them. But don't prompt for decisions on each item.

7. **Update the Daily note** — fill in the `## End of Day` section with the reflection summary. Update `items_completed` and `items_deferred` counts, finalize `domains_touched`.

8. **Auto-trigger `/defrag`** — run a full defrag pass. This handles all the mechanical bookkeeping: auto-defer open items, auto-mark checked items done, reconcile Maps, flag stale items.

### Principles
- **This is reflective, not bureaucratic.** No "defer/wait/done/drop?" loops.
- Note what *emerged* — the unplanned connections are often the most valuable signal
- The human reflects on meaning; the agent handles filing
- If the human volunteers decisions during reflection, honor them immediately
- $ARGUMENTS can optionally specify a date other than today
