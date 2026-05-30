---
name: efforts
description: Manage effort lifecycle — add, splinter, merge, review, and bootstrap efforts. Use when defining new efforts, splitting complex ones, or auditing effort health.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
argument-hint: [add | splinter <slug> | merge <slug> <slug> | review]
srsa: Act (Dyad)
---

## Effort Lifecycle Management

You manage the Maps that define efforts for PULSE. Maps are the sole source of truth for effort definitions. This skill is Dyad Act — system evolution that neither node can do alone.

### Sense — Parse Intent

Read `$ARGUMENTS` to determine the action:

- **No args / `status`** — show current effort landscape
- **`add`** — guided creation of a new effort
- **`splinter <slug>`** — break an effort into sub-efforts
- **`merge <slug> <slug>`** — combine two efforts into one
- **`review`** — audit effort health

---

### Act — Bootstrap

When `Maps/` has no user Maps (only `[INIT]` templates, `_system/`, or is empty):

0. **Ensure vault directory structure exists** — create any missing directories before proceeding:
   ```bash
   mkdir -p "${PULSE_VAULT:-./pulse-vault}/Maps/_system"
   mkdir -p "${PULSE_VAULT:-./pulse-vault}/Notes/archive"
   mkdir -p "${PULSE_VAULT:-./pulse-vault}/Daily/logs"
   mkdir -p "${PULSE_VAULT:-./pulse-vault}/Daily/cache"
   mkdir -p "${PULSE_VAULT:-./pulse-vault}/Sati"
   ```
   Also create `pulse-vault/Maps/.keep` (empty sentinel) and `pulse-vault/Sati/emergence-log.md` if absent.

1. **Check `pulse-vault/user.config.yaml`** — if it exists and has `efforts:` entries, read them.
   - If config is populated: generate Maps from each effort entry using the Map template. For each effort:
     - Create `pulse-vault/Maps/<EffortName>.md` from `pulse-engine/templates/Map.md`
     - Set frontmatter: `effort`, `context_batch`, `base_priority`, `purpose`, `aliases` from config
     - Remove any `[INIT]` template Maps that conflict with newly generated ones
   - If config is empty or missing: **ask the user conversationally** — say "Welcome to PULSE! Let's set up your vault. What are the main areas of your life you're actively managing? A few examples: work, health, a relationship, a side project, a learning path — but name what's actually true for you. Aim for 3–7." Then generate Maps AND write the effort definitions back to `pulse-vault/user.config.yaml`. The user never manually writes config.
2. Report what was generated
3. After bootstrap, proceed with the originally requested action (or `/pulse` if they came from there)

---

### Act — Sync user.config.yaml

After any mutation to Maps (add, splinter, merge, bootstrap), keep `pulse-vault/user.config.yaml` in sync:

1. Read all non-archived Maps in `pulse-vault/Maps/` (excluding `_system/`) for the current effort list
2. Read existing `pulse-vault/user.config.yaml`
3. For each Map not yet in the config: add an entry under `efforts:` with `slug`, `batch`, `base_priority`, `purpose`, `aliases`
4. For each config entry whose Map is now archived: mark it as `archived: true` (or remove)
5. Write the updated config back

Self-healing — any mutation auto-corrects drift between Maps and config.

---

### Sense + Surface — Status (default)

1. Read all Maps in `Maps/` — get `effort`, `context_batch`, `base_priority`, `priority_weight`, `open_loops`, `last_active`, `purpose` from frontmatter
2. Present:

```
## Efforts — Current Landscape

| Effort | Batch | Priority | Open Loops | Last Active |
|--------|-------|----------|------------|-------------|
| ...    | ...   | ...      | ...        | ...         |

[N] efforts across [N] batches.
```

3. End with: "Use `/efforts add`, `/efforts splinter <slug>`, `/efforts merge <slug> <slug>`, or `/efforts review`."

---

### Dyad Route + Act — Add

Before creating a new effort, apply the **Effort Litmus Test**. This is Route — the litmus test gates whether a new effort is warranted or whether this belongs as a thread in an existing Map. Present these questions conversationally:

1. **Duration** — Will this persist for months? If it'll be done in weeks, it's a thread within an existing effort.
2. **Context switch** — Does working on this require a different mental model than any existing effort? If you can do it in the same headspace, it's a thread.
3. **Independence** — Does this have its own stakeholders, tools, or cadence? If it shares all of these with an existing effort, it's a thread.

The user should answer yes to at least 2 of 3. If they can't, suggest adding it as a thread in the most relevant existing Map instead. Don't be rigid — if the user has a clear reason, respect it.

If the litmus test passes:

1. Ask for: name, one-line purpose, aliases
2. Suggest a slug (user confirms)
3. Suggest a `base_priority` based on their description (user confirms)
4. Assign to an existing `context_batch`. Creating a new batch is fine if the existing ones genuinely don't fit — the user knows their cognitive landscape better than the system does. If a new batch is created, add it to `pulse-vault/user.config.yaml` under `batches:`.
5. Create the Map in `Maps/` using the Map template frontmatter (including `purpose` and `aliases`)
6. Report what was created
7. Run the Sync Slug Table procedure

---

### Dyad Surface + Act — Splinter

Splitting an effort that has grown too complex into sub-efforts. The conversation here is Surface — the dyad evaluates which threads genuinely require different mental contexts.

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

### Act — Merge

Combining two efforts that have converged or where one has become redundant.

1. Read both Maps
2. Ask for the merged effort's name (can be one of the originals or new)
3. Propose slug, priority (suggest the higher of the two), batch, aliases (union of both)
4. Combine threads into the merged Map, deduplicating
5. Archive the absorbed effort(s): set Map frontmatter status to `archived`
6. Report: what was merged, what threads were combined
7. Run the Sync Slug Table procedure

---

### Sense + Surface — Review

Audit all efforts for health signals. Read all Maps, then report:

- **Stale**: 0 open loops AND `last_active` > 30 days → suggest archival or check-in
- **Overlapping purpose**: Two efforts whose `purpose` fields substantially overlap → suggest merge
- **Thread-heavy**: Any effort with 8+ active threads → suggest it might be ready to splinter

Present findings conversationally. Don't auto-fix — let the user decide.

---

### Anti-Spaghetti Guidelines

These are quality signals, not hard rules. Surface them during `add` and `splinter` when relevant:

- **Every effort needs a unique purpose.** If you can't articulate how it's different from an existing effort in one sentence, it's probably a thread within that effort.
- **Efforts are durable.** They represent persistent life commitments (months to years), not projects (weeks). A project is a thread within an effort.
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
