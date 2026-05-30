---
name: defrag
description: Organizational cleanup — auto-defer, reconcile Maps, catch misclassifications, flag stale items. Runs after /close (full), during /pulse (light), or manually.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
srsa: Sense+Act
---

## Defrag — Agent-Owned Organizational Cleanup

Absorbs all bookkeeping from triage and review. Keeps the vault consistent without human decision-making.

### Entry Points

- **After `/close`**: full pass (auto-triggered)
- **During `/pulse`**: light pass (auto-triggered)
- **Manual `/defrag`**: full pass on demand

$ARGUMENTS can specify `light` or `full` (default: `full`).

### Act — Triage Gate (MANDATORY — runs before any pass type)

This is a hard precondition. Triage MUST complete before any reconciliation or cleanup.

0. **Auto-triage Inbox** — process any `Inbox/` items where `triaged: false`. Match content against Maps, create Notes, update Maps. No confirmation. Archive each to `Inbox/archive/`.

0.1. **Safety net sweep** — glob `Inbox/*.md` for files with `triaged: true` still in root. Move each to `Inbox/archive/`. MUST run even if step 0 found nothing.

0.2. **Checked-item sweep** — scan each Map's `## Minor Actions` and sub-theme sections for `- [x]` items. Move to the Map's `## Completed` section with `(done YYYY-MM-DD)`. If the item has a backing Note, set that Note's `status: done` and `updated` to today. This prevents checked items from accumulating across sessions.

### Sense — Light Pass (during `/pulse`)

1. _(Triage handled by mandatory gate steps 0–0.2 above.)_ Proceed to reconciliation.
2. **Reconcile Map counts** — for each Map, compute `open_loops` as the sum of:
   - Active/waiting Note files in `Notes/` where `effort:` matches this Map's slug (status: active or waiting)
   - Unchecked Minor Actions (`- [ ]` items in the `## Minor Actions` section)

   Plain-text bullets in Active Threads are NOT counted — they should be promoted to Minor Actions (see full pass step 10.5). Compare the sum to `open_loops` in frontmatter. Fix any mismatches.
3. **Flag obvious issues** — for each Map, determine its effective staleness threshold from the shortest `timescale` among its active Notes (default: weekly → 14 days if no Notes have timescale set). Flag Maps where `last_active` exceeds that threshold.
4. **Scan Minor Actions** — check each Map's `## Minor Actions` section for overdue unchecked items. Include overdue count in the housekeeping summary.
4.5. **Waiting escalation** — flag waiting items where `days_waiting >= 3`. Backfill `waiting_since` on `[w]` items missing it. Include in report and session log.

### Surface — Light Pass Report

5. **Report** — summary for the `/pulse` briefing: "Auto-triaged N items, reconciled M Map counts, K stale Maps flagged, J overdue minor actions, L waiting items escalated." Include per-item detail for triage, reconciliation corrections, and escalation flags.

### Sense — Full Pass Detection (after `/close` or manual)

Run everything in the light pass, plus:

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

### Act — Full Pass Bookkeeping

6. **Auto-defer** — find unchecked items from today's Daily note and carry them forward to tomorrow's daily note (if it exists) or note them for next checklist generation.

7. **Auto-mark done** — find items checked off in the Daily note (lines matching `- [x]`) and set their source Notes to `status: done` with `updated` set to today.

10. **Merge candidates** — Notes in the same effort with overlapping titles or content. Present as: "Possible merge: [note A] and [note B] in [effort]."

10.5. **Dependency integrity check** — scan for resolved and broken dependencies:
   - For each Note with `status: done` or `status: archived`, grep all Maps for `depends:: [[note-slug]]` in Active Thread and Minor Action entries. If found, surface: "Dependency resolved: [[done-note]] — these items are unblocked: [list]"
   - For each Note with `depends:` in frontmatter, check that all referenced Notes exist and are not archived. If a dependency target is `done`/`archived`, flag: "Dependency satisfied: [[this-note]] depended on [[done-note]] (now done). Review whether [[this-note]] is unblocked."
   - For Minor Actions with `depends::` pointing to `done`/`archived` Notes, flag as unblocked and remove the `depends::` annotation from the line
   - Detect circular dependencies (A depends on B, B depends on A) and flag them

10.6. **Auto-archive** — Notes with `status: done` where `updated` is 7+ days ago:
   - Before moving: run the dependency reverse-lookup from step 9.5 (already computed)
   - Remove the Map entry (Active Thread pointer) for the archived note
   - Clean up any `depends::` annotations referencing the archived note in other Map entries
   - Move the file to `Notes/archive/[filename]`
   - Decrement `open_loops` count in the Map's frontmatter
   - Log: `Archived: [[note-slug]] (done since YYYY-MM-DD) — cleaned N dependents`

11. **Minor Actions cleanup** — for each Map's `## Minor Actions` section:
    - Remove checked (`[x]`) items older than 3 days
    - Flag unchecked items with no date that have been sitting for 7+ days (based on git history or session context)
    - Flag overdue unchecked items in the report
    - Items that have grown in scope during the session should be promoted to Notes (create Note, add to Active Threads, remove from Minor Actions)

11.5. **Promote plain-text bullets** — for each Map's `## Active Threads` section, find remaining plain-text bullets (lines starting with `- ` that are NOT linked Notes `[[...]]`, NOT strikethrough, NOT checked, NOT indented). Move each to the Map's `## Minor Actions` section as `- [ ] [text] (importance: medium)`. Remove the original bullet from Active Threads. If `## Minor Actions` doesn't exist, create it. Log each promotion.

12. **Update timestamps** — set `last_active` on any Maps that were touched during this session. Set `updated` on any Notes that were modified.

12.5. **Update `Maps/INDEX.md`** — write-behind for any Maps whose `open_loops` or `last_active` changed during this pass. Refresh `High Items` and `Next Due` columns for affected efforts (re-scan their Minor Actions). Update frontmatter `updated: YYYY-MM-DD`. Keep rows ordered by `priority_weight` descending.

### Surface — Full Pass Report

13. **Report what was done**:

```
## Defrag Summary

- Auto-triaged: N items
- Auto-deferred: N items to tomorrow
- Auto-completed: N items marked done
- Map counts reconciled: N corrections
- Dependencies: N resolved, N unblocked, N circular flagged
- Archived: N notes (done 7+ days)
- Minor Actions: N cleaned, N overdue flagged
- Promoted: N plain-text bullets → Minor Actions
- Waiting escalation: N items (>= 3d waiting)
- Flagged for review:
  - N possible misclassifications
  - N stale items (past their timescale window)
  - N merge candidates
```

### Act — Log

14. **Log to session log file** — append a timestamped decision trace to `Daily/logs/YYYY-MM-DD-log.md`. Create the file and directory if they don't exist. Do NOT write to the Daily note itself.

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
   **Dependencies**:
   - [note-slug] depends on [dep-slug] (status: done) → unblocked
   - Minor: "[task text]" in [effort] depends on [dep-slug] (status: done) → unblocked
   - Circular: [note-a] ↔ [note-b]
   **Archived**: [note-slug] (done since YYYY-MM-DD) → Notes/archive/, cleaned N dependents
   **Waiting Escalation**:
   - [item] ([effort]): [N]d waiting

   Summary: triaged N, deferred N, reconciled N, promoted N bullets, flagged N stale, N merge candidates, N minor actions cleaned, N deps resolved, N archived, N waiting escalated
   ```

   Omit any section that has zero items (e.g., skip **Merge candidates** if none found). The summary line at the end is still compact for scanning, but the per-item traces above it make each decision traceable.

   Light pass uses the same format but only includes sections relevant to the light pass (Triage, Reconciled Maps, Stale checks).

   If no Daily Note exists yet, create one with minimal frontmatter (no Session Log section — that goes in `Daily/logs/`).

### Sub-Agent Policy

`/defrag` writes inline (main session — it has `Write`/`Edit`, no Agent tool): file writes, INDEX updates, and archive moves all run inline. The full defrag pass *is* the canonical heavy multi-file batch; if any sub-batch is delegated to a **foreground** sub-agent, that sub-agent MUST use `model: "opus"` (floor sonnet across all PULSE sub-agents). Never delegate a write to a background sub-agent (read-only).

### Principles

- **Act first, report after.** No confirmation cycles. The cost of a correctable mistake is lower than the cost of interrupting the human.
- **Flags are informational, not blocking.** Misclassifications, stale items, and merge candidates are presented for awareness — the human reviews only if they want to.
- **Idempotent.** Running defrag twice produces the same result. Safe to trigger multiple times.
- **Timestamp everything.** Every file touched gets its `updated` field set to today.
