---
name: defrag
description: Organizational cleanup — reconcile Maps, catch misclassifications, flag stale items, auto-defer/complete. Runs after review, lightly during pulse, or manually on demand.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Defrag — Agent-Owned Organizational Cleanup

Absorbs all bookkeeping from triage and review. The agent executes everything autonomously and reports what it did.

### Input

$ARGUMENTS can optionally specify:
- `light` — run the light pass only (used during `/pulse`)
- `full` — run the full pass (default, used after `/review` and manual invocation)

### Three Entry Points

1. **After `/review`** — full pass, auto-triggered
2. **During `/pulse`** — light pass, auto-triggered
3. **Manual `/defrag`** — full pass on demand

### Light Pass (during `/pulse`)

1. **Auto-triage pending Inbox items** — run the auto-triage flow (see below) on any items where `triaged: false`
2. **Reconcile Map counts** — for each Map, count actual `active` and `waiting` Notes matching that domain in `Notes/`. Compare to `open_loops` in Map frontmatter. Fix any mismatches.
3. **Flag obvious issues** — stale Maps (`last_active` > 14 days), done Notes older than 7 days not yet archived
4. **Log briefly** to today's Daily note under a `## Defrag Log` section — e.g. "Auto-triaged 2 items, reconciled 1 Map count, flagged 1 stale Map"

### Full Pass

Everything in the light pass, plus:

5. **Auto-defer untouched checklist items** — read today's Daily note. Any unchecked items that are not marked done → defer to tomorrow by creating/updating tomorrow's Daily note with those items.

6. **Auto-complete checked items** — items checked off in the Daily note (`- [x]`) → find the linked Note, set `status: done`, update `updated` date.

7. **Catch misclassifications** — for each Note triaged today, read its content and verify the assigned `domains[]` make sense against Map purposes. Flag any that look wrong (report but don't auto-fix — domain reassignment is higher-stakes).

8. **Flag stale items** — active Notes not updated in 14+ days. Report them grouped by domain.

9. **Merge candidates** — find Notes in the same domain with similar titles or overlapping content. Report as suggestions.

10. **Update timestamps** — set `last_active` on any Maps whose Notes were touched today. Set `updated` on any Notes modified during defrag.

11. **Log summary** to today's Daily note under the `## Defrag Log` section — list everything done and flagged, grouped by action type. Do not report results in conversation.

### Auto-Triage Flow (used by both light and full pass)

For each Inbox item where `triaged: false`:

1. Read the capture content
2. Match content against existing Maps — read Map titles, domain slugs, and purpose descriptions
3. Assign `domains[]` based on best fit
4. Determine `status` (default: `active`), `context_group`, and `effort_estimate`
5. Create a new Note in `Notes/` with proper frontmatter, or append to an existing Note if the content clearly extends one
6. Update relevant Maps: add note link under appropriate section, increment `open_loops`, update `last_active`
7. Mark Inbox item: set `triaged: true`, fill in `domains[]`

No confirmation needed. The cost of a misclassification is low — the full defrag pass catches errors, and the user can always override.

### Principles

- Execute silently, log what was done to the Daily note
- Never ask for confirmation — act and log
- Group the log by action type for easy scanning
- Flag things that need human attention in the log, but don't inject them into conversation
- Misclassification cost is low (defrag catches it later), confirmation cost is real cognitive load
