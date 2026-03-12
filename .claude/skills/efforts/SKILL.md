---
name: efforts
description: Manage effort lifecycle — add, splinter, merge, review, and bootstrap efforts. Use when defining new efforts, splitting complex ones, or auditing effort health.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: [add | splinter <slug> | merge <slug> <slug> | review]
---

## Effort Lifecycle Management

You manage the `efforts.yaml` configuration and associated Maps for PULSE.

### Parse Intent

Read `$ARGUMENTS` to determine the action:

- **No args / `status`** — show current effort landscape
- **`add`** — guided creation of a new effort
- **`splinter <slug>`** — break an effort into sub-efforts
- **`merge <slug> <slug>`** — combine two efforts into one
- **`review`** — audit effort health

---

### Bootstrap

If `efforts.yaml` does not exist when any action is attempted:

1. Present the 3 default efforts:
   - **Work** (slug: `work`, priority: 9, batch: Work) — "Primary professional obligation"
   - **Life Maintenance** (slug: `maintenance`, priority: 7, batch: Maintenance) — "Health, home, chores, admin — things that rot if ignored"
   - **Personal Projects** (slug: `personal-projects`, priority: 5, batch: Projects) — "Creative and growth work you do for yourself"
2. Ask: "Want to start with these, or tell me about your life and I'll tailor them?"
3. If the user accepts defaults → write `efforts.yaml` with the 3 defaults and 3 context batches, create Maps in `Maps/`
4. If the user describes their life → generate a tailored `efforts.yaml` (aim for 3-5 efforts to start), create Maps
5. Run the Sync Slug Table procedure
6. After bootstrap, proceed with the originally requested action (or `/pulse` if they came from there)

---

### Sync Slug Table

After any mutation to `efforts.yaml` (add, splinter, merge, bootstrap), update the slug cache in root `CLAUDE.md`:

1. Read `efforts.yaml` for the current active effort list
2. Find the block between `<!-- SLUG-TABLE-START` and `<!-- SLUG-TABLE-END -->`
3. Replace with a fresh table: columns `Slug`, `Batch`, `Aliases`; sorted by batch (alpha) then base_priority desc; skip archived efforts
4. If sentinels don't exist in `CLAUDE.md`, insert the full block under `## Effort & Batch Definitions`

Self-healing — any mutation auto-corrects drift.

---

### Status (default)

1. Read `efforts.yaml`
2. Read all Maps in `Maps/` — get `priority_weight`, `open_loops`, `last_active` from frontmatter
3. Present:

```
## Efforts — Current Landscape

| Effort | Batch | Priority | Open Loops | Last Active |
|--------|-------|----------|------------|-------------|
| ...    | ...   | ...      | ...        | ...         |

[N] efforts across [N] batches.
```

4. End with: "Use `/efforts add`, `/efforts splinter <slug>`, `/efforts merge <slug> <slug>`, or `/efforts review`."

---

### Add

Before creating a new effort, apply the **Effort Litmus Test**. Present these questions conversationally:

1. **Duration** — Will this persist for months? If it'll be done in weeks, it's a thread within an existing effort.
2. **Context switch** — Does working on this require a different mental model than any existing effort? If you can do it in the same headspace, it's a thread.
3. **Independence** — Does this have its own stakeholders, tools, or cadence? If it shares all of these with an existing effort, it's a thread.

The user should answer yes to at least 2 of 3. If they can't, suggest adding it as a thread in the most relevant existing Map instead. Don't be rigid — if the user has a clear reason, respect it.

If the litmus test passes:

1. Ask for: name, one-line purpose
2. Suggest a slug (user confirms)
3. Suggest a `base_priority` based on their description (user confirms)
4. Assign to an existing `context_batch`. Creating a new batch is fine if the existing ones genuinely don't fit — the user knows their cognitive landscape better than the system does.
5. Append to `efforts.yaml`
6. Create the Map in `Maps/` using the Map template frontmatter
7. Report what was created
8. Run the Sync Slug Table procedure

---

### Splinter

Splitting an effort that has grown too complex into sub-efforts.

1. Read the target effort's Map — list all active threads
2. Ask: "Which of these feel like genuinely different mental contexts?"
3. The user identifies the split
4. For each new effort:
   - Propose name, slug, purpose
   - Inherit the parent's `context_batch` and `base_priority` by default (user can adjust)
   - Run a light litmus check — splintering usually passes by nature, but confirm the split isn't premature
5. Create new Maps, migrate relevant threads from the parent Map
6. Archive the parent effort: set its Map status to `archived`, remove from active efforts in `efforts.yaml` (keep a YAML comment noting what it splintered into)
7. Update `efforts.yaml` with new efforts
8. Report: what was created, what was migrated, what was archived
9. Run the Sync Slug Table procedure

**Guard**: If the parent effort has fewer than 3 active threads, flag that the split may be premature. The user can override.

---

### Merge

Combining two efforts that have converged or where one has become redundant.

1. Read both Maps
2. Ask for the merged effort's name (can be one of the originals or new)
3. Propose slug, priority (suggest the higher of the two), batch
4. Combine threads into the merged Map, deduplicating
5. Archive the absorbed effort(s): set Map status to `archived`, add YAML comment in `efforts.yaml` noting the merge
6. Update `efforts.yaml`
7. Report: what was merged, what threads were combined
8. Run the Sync Slug Table procedure

---

### Review

Audit all efforts for health signals. Read `efforts.yaml` and all Maps, then report:

- **Stale**: 0 open loops AND `last_active` > 30 days → suggest archival or check-in
- **Overlapping purpose**: Two efforts whose purpose statements substantially overlap → suggest merge
- **Orphaned**: Effort exists in `efforts.yaml` but has no Map → flag for Map creation
- **Ghost Maps**: Map exists in `Maps/` but no matching effort in `efforts.yaml` → flag
- **Thread-heavy**: Any effort with 8+ active threads → suggest it might be ready to splinter

Present findings conversationally. Don't auto-fix — let the user decide.

---

### Anti-Spaghetti Guidelines

These are quality signals, not hard rules. Surface them during `add` and `splinter` when relevant:

- **Every effort needs a unique purpose.** If you can't articulate how it's different from an existing effort in one sentence, it's probably a thread within that effort.
- **Efforts are durable.** They represent persistent life domains (months to years), not projects (weeks). A project is a thread within an effort.
- **Batches absorb complexity.** Before splintering, check whether better thread organization within an existing Map solves the problem.
- **New efforts inherit their parent's `context_batch`** unless the user explicitly wants a new batch. New batches are fine — just confirm intent.

---

### efforts.yaml Format Reference

```yaml
efforts:
  - name: "Human-readable name"
    slug: lowercase-hyphenated
    base_priority: 1-10
    context_batch: BatchName
    purpose: "One-line why this matters"
    aliases: [optional, flexible-match, terms]

context_batches:
  - name: BatchName
    shared_context:
      - "What tools/environments/stakeholders live here"
    mindset: "What cognitive mode this batch operates in"
```
