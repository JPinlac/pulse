---
name: close
description: Session-close ritual — reflect on what happened, what emerged, what patterns are forming. Flags items needing attention, then auto-triggers /defrag.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
srsa: Surface+Sense+Act
---

## Session Close

Pure reflection. No item-by-item status decisions. The agent presents a narrative, the human reflects, then defrag handles the bookkeeping.

### Quick Close (`/close q` or `/close quick`)

If $ARGUMENTS contains `q` or `quick`, run a lightweight save-state (use before clearing context, mid-session checkpoints, etc.):
1. Skip steps 2–5 (no reflection narrative, no flags, no human prompts)
2. Run step 6.5 (inline recompute — captures current state)
3. Run step 7 (update Daily note — items_completed/deferred, efforts_touched)
4. **Light defrag (mandatory — do NOT skip)** — this is Sense that must always execute:
   a. Auto-triage Inbox — process any `Inbox/` items where `triaged: false`, archive to `Inbox/archive/`
   b. Reconcile Map counts — for each touched effort, verify `open_loops` = active/waiting Notes + unchecked Minor Actions. Fix mismatches.
   c. Flag stale Maps — flag any Map where `last_active` exceeds its staleness threshold
   d. Scan Minor Actions — check for overdue unchecked items in touched efforts
   e. Log to `Daily/logs/YYYY-MM-DD-log.md`: `### Defrag — HH:MM light` with triage count, reconciliation changes, stale flags, overdue count
5. Set `last_refreshed: HH:MM` in today's Daily note frontmatter — do NOT set `close_complete: true` (checkpoint, not session end)
6. Respond: `State saved. Context is clear to start fresh.`

Total: ~2 turns. The `last_refreshed` timestamp tells the next `/pulse` that state is fresh — it will skip the inline refresh (or run triage-only if new inbox items arrived). No ceremony required.

### Sense — Gather Context

1. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`). If none exists, check what Maps were touched today by looking at `last_active` dates.

2. **Read relevant Maps and Notes** — gather context on what moved today across all active efforts.

### Dyad Surface — Reflect Together

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

### Route — Flag What Needs Attention

4. **Flag items needing human attention** — only surface things that genuinely need a decision:
   - Items deferred 3+ times (pattern of avoidance — worth naming)
   - Efforts that went dark (active Notes past their timescale staleness window with no status change)
   - Cross-effort tensions (competing priorities that can't both win)
   - Anything that seems stuck or misaligned with stated goals
   - **Newly unblocked** — items whose dependencies were completed today: "Newly unblocked: [[note]] — dependency [[dep]] completed today. This is now actionable."

5. **Invite reflection** — "Anything else on your mind before I clean up?" This is optional. If the user has nothing to add, move on.

### Act — Honor, Recompute, File

6. **If the user volunteers status changes** during the reflection conversation (e.g., "that thing is done" or "drop that one"), apply them. But don't prompt for decisions on each item.

6.5. **Session-end recompute** — run `uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --briefing --cache "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-calc.json"` to capture today's activity in a fresh cache. Update Map frontmatter weights from the output. Log weight table to `Daily/logs/YYYY-MM-DD-log.md`.

7. **Update the Daily note** — fill in the `## End of Day` section with the reflection summary. Update `items_completed` and `items_deferred` counts, finalize `efforts_touched`.

8. **Auto-trigger `/defrag`** — run a full defrag pass. This handles all the mechanical bookkeeping: auto-defer open items, auto-mark checked items done, reconcile Maps, flag stale items.

8.5. **Set freshness + close flag** — after successful defrag + recompute:
   - Set `last_refreshed: HH:MM` in today's Daily note frontmatter (gates `/pulse` inline refresh skip)
   - Set `close_complete: true` (signals a **full** defrag ran — `/pulse` can skip deeper checks like misclassification scan and merge candidate detection beyond what `last_refreshed` alone gates)

### Surface — Close with Warmth

9. **Close with warmth** — after defrag completes, deliver a brief closing message:

```
### You're done.

[1–2 sentences of genuine praise for what was accomplished today — specific to this session, not generic. Reference actual efforts touched or progress made.]

Everything is filed. [If no due items remain open: "Your priority items are in good hands — nothing is falling through the cracks tonight. You can fully disconnect, be present, and rest without the background hum of open loops." If due items are still open: acknowledge them honestly — name what's outstanding, affirm that it's noted and won't be lost, but don't say it's okay to fully disconnect.]
```

   Tone guidelines:
   - **Specific, not generic** — reference actual work done today, not a template affirmation
   - **Brief** — 3–5 sentences total
   - **Warm but not saccharine** — earned praise, not flattery
   - **Honest** — don't offer false reassurance if due items are still open; acknowledge them and affirm they're tracked
   - **Permissive** — explicit "it's okay to let go" framing only when the slate is genuinely clear

### Sub-Agent Policy

Writes are inline (main session) by default — Daily note writes and session-log appends are single-file ops, written inline. `/close` already runs inline (it has `Write`/`Edit`, no Agent tool). If a heavy batch is delegated to a **foreground** sub-agent (e.g. the auto-triggered `/defrag` full pass), that sub-agent MUST use `model: "opus"` (floor sonnet across all PULSE sub-agents). Never delegate a write to a background sub-agent (read-only).

### Principles
- **This is reflective, not bureaucratic.** No "defer/wait/done/drop?" loops.
- Note what *emerged* — the unplanned connections are often the most valuable signal
- The human reflects on meaning; the agent handles filing
- If the human volunteers decisions during reflection, honor them immediately
- **End with warmth** — earned praise for what was done and explicit permission to disconnect. The user should feel held, not just filed.
- $ARGUMENTS can optionally specify a date other than today
