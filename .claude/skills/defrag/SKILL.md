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

1. **Auto-triage Inbox** — run the auto-triage process on any `Inbox/` items where `triaged: false`. Match content against Maps to assign efforts, create Notes, update Maps. No confirmation needed.
2. **Reconcile Map counts** — for each Map, compute `open_loops` as the sum of:
   - Active/waiting Note files where `effort:` matches this Map's slug (status: active or waiting)
   - Unchecked Minor Actions (`- [ ]` items in the `## Minor Actions` section)

   Plain-text bullets in Active Threads are NOT counted — they should be promoted to Minor Actions (see full pass step 10.5). Compare the sum to `open_loops` in frontmatter. Fix any mismatches.
3. **Flag obvious issues** — for each Map, determine its effective staleness threshold from the shortest `timescale` among its active Notes (default: weekly → 14 days if no Notes have timescale set). Flag Maps where `last_active` exceeds that threshold.
4. **Scan Minor Actions** — check each Map's `## Minor Actions` section for overdue unchecked items. Include overdue count in the housekeeping summary.
5. **Report briefly** — one-line summary for the `/pulse` briefing: "Auto-triaged N items, reconciled M Map counts, K stale Maps flagged, J overdue minor actions."

### Full Pass (after `/close` or manual)

Run everything in the light pass, plus:

6. **Auto-defer** — find unchecked items from today's Daily note and carry them forward to tomorrow's daily note (if it exists) or note them for next checklist generation.

7. **Auto-mark done** — find items checked off in the Daily note (lines matching `- [x]`) and set their source Notes to `status: done` with `updated` set to today.

8. **Catch misclassifications** — for each Note triaged today (or recently), read the content body and compare against the assigned `efforts[]`. If the content clearly doesn't match the effort's Map purpose, flag it: "Possible misclassification: [note title] assigned to [effort] — content seems more like [suggested effort]."

9. **Flag stale items** — active Notes where `(today - updated)` exceeds the stale threshold for that Note's `timescale`. Thresholds (at ~150% of natural period):

   | timescale | stale after |
   |-----------|-------------|
   | daily | 3 days |
   | weekly | 14 days |
   | monthly | 45 days |
   | quarterly | 135 days |
   | biannual | 270 days |
   | annual | 545 days |
   | null | 14 days (default) |

   Present as: "Stale: [note title] ([effort]) — last touched [date], timescale: [value]. [N] days overdue."

9. **Merge candidates** — Notes in the same effort with overlapping titles or content. Present as: "Possible merge: [note A] and [note B] in [effort]."

10. **Minor Actions cleanup** — for each Map's `## Minor Actions` section:
    - Remove checked (`[x]`) items older than 3 days
    - Flag unchecked items with no date that have been sitting for 7+ days (based on git history or session context)
    - Flag overdue unchecked items in the report
    - Items that have grown in scope during the session should be promoted to Notes (create Note, add to Active Threads, remove from Minor Actions)

10.5. **Promote plain-text bullets** — for each Map's `## Active Threads` section, find remaining plain-text bullets (lines starting with `- ` that are NOT linked Notes `[[...]]`, NOT strikethrough, NOT checked, NOT indented). Move each to the Map's `## Minor Actions` section as `- [ ] [text] (importance: medium)`. Remove the original bullet from Active Threads. If `## Minor Actions` doesn't exist, create it. Log each promotion.

11. **Update timestamps** — set `last_active` on any Maps that were touched during this session. Set `updated` on any Notes that were modified.

12. **Report what was done**:

```
## Defrag Summary

- Auto-triaged: N items
- Auto-deferred: N items to tomorrow
- Auto-completed: N items marked done
- Map counts reconciled: N corrections
- Minor Actions: N cleaned, N overdue flagged
- Promoted: N plain-text bullets → Minor Actions
- Flagged for review:
  - N possible misclassifications
  - N stale items (past their timescale window)
  - N merge candidates
```

13. **Log to Daily Note** — append a timestamped decision trace under `## Session Log` in today's Daily Note (`Daily/YYYY-MM-DD.md`). Create the section if it doesn't exist.

   Format:
   ```
   ### Defrag — HH:MM [full|light]

   **Triage**: N items — [item-slug → effort(s)], ...
   **Reconciled Maps**:
   - [effort]: open_loops [old]→[new], last_active [unchanged|updated]
   - [effort]: open_loops [old]→[new]
   **Stale checks**:
   - [note-slug] ([timescale], [N] days since update) → [flagged|ok]
   - [note-slug] ([timescale], [N] days since update) → [flagged|ok]
   **Deferred**: [item-slug], [item-slug] (from today's agenda)
   **Completed**: [item-slug] (status → done)
   **Misclassifications**: [note-slug] assigned [effort], content suggests [effort]
   **Merge candidates**: [note-a] + [note-b] in [effort]
   **Minor Actions**: cleaned N checked items, flagged N overdue, promoted N to Notes
   **Promoted**: [bullet text] → Minor Action (importance: medium) in [effort], ...

   Summary: triaged N, deferred N, reconciled N, promoted N bullets, flagged N stale, N merge candidates, N minor actions cleaned
   ```

   Omit any section that has zero items (e.g., skip **Merge candidates** if none found). The summary line at the end is still compact for scanning, but the per-item traces above it make each decision traceable.

   Light pass uses the same format but only includes sections relevant to the light pass (Triage, Reconciled Maps, Stale checks).

   If no Daily Note exists yet, create one with minimal frontmatter and the Session Log section.

### Principles

- **Act first, report after.** No confirmation cycles. The cost of a correctable mistake is lower than the cost of interrupting the human.
- **Flags are informational, not blocking.** Misclassifications, stale items, and merge candidates are presented for awareness — the human reviews only if they want to.
- **Idempotent.** Running defrag twice produces the same result. Safe to trigger multiple times.
- **Timestamp everything.** Every file touched gets its `updated` field set to today.
