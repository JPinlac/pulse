---
name: efforts
description: Manage effort lifecycle — add, splinter, merge, review, and bootstrap efforts. Use when defining new efforts, splitting complex ones, or auditing effort health.
user-invocable: true
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: [add | splinter <slug> | merge <slug> <slug> | review]
---

## Effort Lifecycle Management

You manage the Maps that define efforts for PULSE. Maps are the sole source of truth for effort definitions.

### Parse Intent

Read `$ARGUMENTS` to determine the action:

- **No args / `status`** — show current effort landscape
- **`add`** — guided creation of a new effort
- **`splinter <slug>`** — break an effort into sub-efforts
- **`merge <slug> <slug>`** — combine two efforts into one
- **`review`** — audit effort health

---

### Bootstrap

If `Maps/` contains no `.md` files when any action is attempted:

1. Ask the user about their life: "What are the major areas you spend your time and attention on?" Let them describe freely.
2. From their description, generate tailored efforts (aim for 3-5). For each, propose a name, slug, one-line purpose, `base_priority`, `context_batch`, and aliases.
3. Present the proposed efforts for confirmation. Let the user adjust before committing.
4. If the user would rather skip the conversation: "Or if you'd rather just get started, I can set up 3 universal defaults — **Work**, **Life Maintenance**, and **Personal Projects** — and you can customize later with `/efforts`."
5. Create Maps in `Maps/` with full frontmatter (including purpose and aliases)
6. Run the Sync Slug Table procedure
7. After bootstrap, proceed with the originally requested action (or `/pulse` if they came from there)

---

### Sync Slug Table

After any mutation to Maps (add, splinter, merge, bootstrap), update the slug cache in root `CLAUDE.md`:

1. Read all Maps in `Maps/` for the current active effort list (from frontmatter)
2. Find the block between `<!-- SLUG-TABLE-START` and `<!-- SLUG-TABLE-END -->`
3. Replace with a fresh table: columns `Slug`, `Batch`, `Aliases`; sorted by batch (alpha) then base_priority desc; skip archived efforts
4. If sentinels don't exist in `CLAUDE.md`, insert the full block under `## Efforts & Slugs`

Self-healing — any mutation auto-corrects drift.

---

### Status (default)

1. Read all Maps in `Maps/` — get `effort`, `context_batch`, `base_priority`, `priority_weight`, `open_loops`, `last_active`, `purpose` from frontmatter
2. Present:

```
## Efforts — Current Landscape

| Effort | Batch | Priority | Open Loops | Last Active |
|--------|-------|----------|------------|-------------|
| ...    | ...   | ...      | ...        | ...         |

[N] efforts across [N] batches.
```

3. **If all efforts are still defaults** (only `work`, `maintenance`, `personal-projects` exist and none have been modified — 0 open loops, no threads): prompt the user to customize. Run the same conversational flow as Bootstrap step 1-3 — ask about their life, propose tailored efforts, let them adjust. Replace or augment the defaults based on what they describe.
4. Otherwise, end with: "Use `/efforts add`, `/efforts splinter <slug>`, `/efforts merge <slug> <slug>`, or `/efforts review`."

---

### Add

Before creating a new effort, apply the **Effort Litmus Test**. Present these questions conversationally:

1. **Duration** — Will this persist for months? If it'll be done in weeks, it's a thread within an existing effort.
2. **Context switch** — Does working on this require a different mental model than any existing effort? If you can do it in the same headspace, it's a thread.
3. **Independence** — Does this have its own stakeholders, tools, or cadence? If it shares all of these with an existing effort, it's a thread.

The user should answer yes to at least 2 of 3. If they can't, suggest adding it as a thread in the most relevant existing Map instead. Don't be rigid — if the user has a clear reason, respect it.

If the litmus test passes:

1. Ask for: name, one-line purpose, aliases
2. Suggest a slug (user confirms)
3. Suggest a `base_priority` based on their description (user confirms)
4. Assign to an existing `context_batch`. Creating a new batch is fine if the existing ones genuinely don't fit — the user knows their cognitive landscape better than the system does. If a new batch is created, add it to the context batches table in `CLAUDE.md`.
5. Create the Map in `Maps/` using the Map template frontmatter (including `purpose` and `aliases`)
6. Report what was created
7. Run the Sync Slug Table procedure

---

### Splinter

Splitting an effort that has grown too complex into sub-efforts.

1. Read the target effort's Map — list all active threads
2. Ask: "Which of these feel like genuinely different mental contexts?"
3. The user identifies the split
4. For each new effort:
   - Propose name, slug, purpose, aliases
   - Inherit the parent's `context_batch` and `base_priority` by default (user can adjust)
   - Run a light litmus check — splintering usually passes by nature, but confirm the split isn't premature
5. Create new Maps in `Maps/`, migrate relevant threads from the parent Map
6. Archive the parent effort: set its Map frontmatter status to `archived`
7. Report: what was created, what was migrated, what was archived
8. Run the Sync Slug Table procedure

**Guard**: If the parent effort has fewer than 3 active threads, flag that the split may be premature. The user can override.

---

### Merge

Combining two efforts that have converged or where one has become redundant.

1. Read both Maps
2. Ask for the merged effort's name (can be one of the originals or new)
3. Propose slug, priority (suggest the higher of the two), batch, aliases (union of both)
4. Combine threads into the merged Map, deduplicating
5. Archive the absorbed effort(s): set Map frontmatter status to `archived`
6. Report: what was merged, what threads were combined
7. Run the Sync Slug Table procedure

---

### Review

Audit all efforts for health signals. Read all Maps, then report:

- **Stale**: 0 open loops AND `last_active` > 30 days → suggest archival or check-in
- **Overlapping purpose**: Two efforts whose `purpose` fields substantially overlap → suggest merge
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

### Map Frontmatter Reference

```yaml
---
type: map
effort: lowercase-hyphenated
context_batch: BatchName
priority_weight: 0.5
base_priority: 1-10
last_active: YYYY-MM-DD
open_loops: 0
related_efforts: []
purpose: "One-line why this matters"
aliases: [optional, flexible-match, terms]
tags: []
---
```
