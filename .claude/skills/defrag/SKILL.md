---
name: defrag
description: Organizational cleanup — auto-defer, reconcile Maps, catch misclassifications, flag stale items. Runs after /close (full), during /pulse (light), or manually.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Defrag — Agent-Owned Organizational Cleanup

Absorbs all bookkeeping from triage and review. Keeps the vault consistent without human decision-making.

### Entry Points

- **After `/close`**: full pass (auto-triggered)
- **During `/pulse`**: light pass (auto-triggered)
- **Manual `/defrag`**: full pass on demand

$ARGUMENTS can specify `light` or `full` (default: `full`).

### Light Pass (during `/pulse`)

1. **Auto-triage Inbox** — run the auto-triage process on any `Inbox/` items where `triaged: false`. Match content against Maps to assign domains, create Notes, update Maps. No confirmation needed.
2. **Reconcile Map counts** — for each Map, count actual `active`/`waiting` Notes linked via `domains[]` and compare to `open_loops` in frontmatter. Fix any mismatches.
3. **Flag obvious issues** — note any Maps where `last_active` is >7 days stale.
4. **Report briefly** — one-line summary for the `/pulse` briefing: "Auto-triaged N items, reconciled M Map counts, K stale Maps flagged."

### Full Pass (after `/close` or manual)

Run everything in the light pass, plus:

5. **Auto-defer** — find unchecked items from today's Daily note and carry them forward to tomorrow's daily note (if it exists) or note them for next checklist generation.

6. **Auto-mark done** — find items checked off in the Daily note (lines matching `- [x]`) and set their source Notes to `status: done` with `updated` set to today.

7. **Catch misclassifications** — for each Note triaged today (or recently), read the content body and compare against the assigned `domains[]`. If the content clearly doesn't match the domain's Map purpose, flag it: "Possible misclassification: [note title] assigned to [effort] — content seems more like [suggested effort]."

8. **Flag stale items** — active Notes with `updated` date 14+ days ago. Present as: "Stale: [note title] ([effort]) — last touched [date]. Still active?"

9. **Merge candidates** — Notes in the same domain with overlapping titles or content. Present as: "Possible merge: [note A] and [note B] in [effort]."

10. **Update timestamps** — set `last_active` on any Maps that were touched during this session. Set `updated` on any Notes that were modified.

11. **Report what was done**:

```
## Defrag Summary

- Auto-triaged: N items
- Auto-deferred: N items to tomorrow
- Auto-completed: N items marked done
- Map counts reconciled: N corrections
- Flagged for review:
  - N possible misclassifications
  - N stale items (14+ days untouched)
  - N merge candidates
```

### Principles

- **Act first, report after.** No confirmation cycles. The cost of a correctable mistake is lower than the cost of interrupting the human.
- **Flags are informational, not blocking.** Misclassifications, stale items, and merge candidates are presented for awareness — the human reviews only if they want to.
- **Idempotent.** Running defrag twice produces the same result. Safe to trigger multiple times.
- **Timestamp everything.** Every file touched gets its `updated` field set to today.
