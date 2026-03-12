---
name: review
description: End-of-session reflection — what happened, what emerged, what patterns are forming. Auto-triggers defrag at the end.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## End-of-Session Review

A reflective conversation about the session, not an item-by-item status update. The agent presents a narrative, flags things that need attention, and auto-triggers defrag for all bookkeeping.

### Steps

1. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`). If none exists, check what Maps were touched today by looking at `last_active` dates and recently updated Notes.

2. **Read all Maps** to understand current state — `priority_weight`, `open_loops`, `last_active`.

3. **Present a reflection narrative**:

```
## Review — [date]

### What Happened
[Narrative summary of the session: which efforts were touched, what moved forward, what got created. Written as prose, not a checklist.]

### What Emerged
[New items, ideas, or threads that came up during the session — the unplanned stuff is often the most valuable signal.]

### Patterns & Tensions
[Cross-effort insights, recurring themes, things that keep coming back.]
```

4. **Flag items that need human attention** — only surface these, don't ask for decisions:
   - Items deferred 3+ times (pattern of avoidance or misclassification)
   - Efforts that went dark — Maps with `last_active` > 14 days that used to be active
   - Cross-domain tensions — efforts competing for time or pulling in opposite directions
   - Waiting items older than 7 days without resolution

5. **Invite optional reflection**: "Anything else before I clean up?" — give the user space to add thoughts, adjust status on anything, or note what they want to carry forward. This is a conversation, not a form.

6. **If the user offers status changes** during the conversation (e.g., "that's done" or "defer X"), apply them:
   - Update Note status and `updated` date
   - Update Map `open_loops` and `last_active`
   - Update Daily note if relevant

7. **Auto-trigger defrag** — after the reflection conversation concludes, run a full defrag pass (invoke the defrag skill). This handles:
   - Auto-deferring unchecked items to tomorrow
   - Auto-completing checked items
   - Reconciling Map counts
   - Updating timestamps
   - Flagging stale items and merge candidates

### Principles
- This is reflective, not bureaucratic — no item-by-item "defer/wait/done/drop?" loops
- Present narrative, not checklists — the human reflects, the agent handles mechanics
- Note what *emerged* — the unplanned stuff is often the most valuable signal
- Only surface things that genuinely need human attention
- All bookkeeping goes to defrag — review is for thinking, defrag is for filing
- $ARGUMENTS can optionally specify a date other than today
