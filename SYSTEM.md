# PULSE System Design

> This is the canonical reference for how PULSE works. All other documents defer to this one.
> When the system evolves, update this document first, then propagate changes to `CLAUDE.md`, `README.md`, and skills.

---

## 1. Philosophy

### Shusho-itto (修証一等)

Practice and realization are one act. In Dogen's framing, you don't practice *in order to* become enlightened — the practice *is* the enlightenment. PULSE applies this to personal systems: capturing a thought, reflecting on priorities, and taking action are not three steps in a pipeline. They're one movement. The vault isn't maintained separately from living.

### Agent-First

The primary interface is conversation, not GUI. The Obsidian app is a secondary view — useful for graph visualization, Dataview tables, and browsing, but not where work happens. Every structural decision optimizes for LLM navigation and retrieval:
- Flat note storage (no nested directories to traverse)
- Comprehensive YAML frontmatter (structured data for programmatic access)
- Wikilinks for graph connectivity
- Dataview queries for dynamic views

### Agent-Managed Metadata

The user never writes frontmatter. Every `---` block is created and maintained by the agent. This removes friction from capture and ensures consistency across the vault. The agent is the librarian; the user is the thinker.

---

## 2. Architecture

### Conceptual Model

```
                    ┌─────────┐
                    │ Home.md │  ← Dynamic dashboard (computed view)
                    └────┬────┘
                         │ reads
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │ Map A  │ │ Map B  │ │ Map C  │  ← Source of truth per effort
         └───┬────┘ └───┬────┘ └───┬────┘
             │          │          │
             ▼          ▼          ▼
         ┌──────────────────────────────┐
         │         Notes/ (flat)         │  ← All content, linked to 1+ Maps
         └──────────────────────────────┘
              ▲                    ▲
              │                    │
         ┌────────┐          ┌─────────┐
         │ Inbox/ │ ────────▶│ Triage  │  ← Capture → classify → file
         └────────┘          └─────────┘
```

### Information Flow

1. **Input** enters as conversation or `/capture`
2. **Inbox** holds raw captures with minimal metadata
3. **Triage** classifies, assigns domains, creates or appends to Notes
4. **Notes** are the atomic units of content — linked to Maps via `domains[]`
5. **Maps** aggregate notes per effort — they hold active threads, open loops, and purpose
6. **Home.md** is a computed view across all Maps — priorities, recent activity, tensions
7. **Daily notes** are generated tactical checklists — ephemeral, not archival

### Data Flows Upward, Control Flows Downward

- Notes feed Maps (content aggregation)
- Maps feed Home.md (priority computation)
- Home.md informs Daily notes (task generation)
- Daily notes reference Notes (task execution)

---

## 3. Vault Structure

```
/
├── Home.md                  Dashboard. Computed view of priorities and activity.
├── SYSTEM.md                This file. Canonical system reference.
├── CLAUDE.md                Agent conventions. Quick-reference for LLM behavior.
├── README.md                Setup guide and command reference.
├── efforts.yaml             User's effort definitions (copied from efforts.example.yaml).
├── efforts.example.yaml     Example effort config shipped with the engine.
│
├── Inbox/                   Zero-friction capture. Quick thoughts.
│   └── .keep
│
├── Maps/                    One MOC per effort. Generated from efforts.yaml on first run.
│   └── .keep
│
├── Notes/                   All content notes. Flat directory.
│   └── .keep
│
├── Daily/                   Generated checklists. YYYY-MM-DD.md.
│   └── .keep
│
├── Templates/               Obsidian templates.
│   ├── Daily Note.md
│   ├── Capture.md
│   ├── Map.md
│   └── Note.md
│
├── Queries/                 Saved Dataview queries.
│   ├── Active by Domain.md
│   ├── Open Loops.md
│   ├── Cross Domain.md
│   └── Stale Items.md
│
└── .claude/
    └── skills/              Slash command definitions.
        ├── pulse/
        ├── checklist/
        ├── capture/
        ├── triage/
        ├── focus/
        ├── review/
        └── recompute/
```

---

## 4. Effort System

### Defining Your Efforts

Every endeavor in your life maps to exactly one effort. Each effort has a Map file that serves as its source of truth.

Efforts are defined in `efforts.yaml`. Here's the format:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Human-readable name (Map title) | "My Job" |
| `slug` | Lowercase, hyphenated identifier (used in frontmatter) | `my-job` |
| `base_priority` | Life-importance anchor, 1-10 | 9 |
| `context_batch` | Group name for context switching | "Work" |
| `purpose` | One-line description of why this matters | "Day job, pays the bills" |

### Effort Interconnections

Efforts are not siloed. They feed each other. When defining your efforts, consider how they relate:
- Which efforts fund or enable others?
- Which efforts share intellectual territory?
- Which efforts produce output that feeds into others?

These connections surface as `related_domains` in Map frontmatter and help the agent identify cross-pollination opportunities.

### Adding or Removing Efforts

To add an effort:
1. Add the entry to `efforts.yaml`
2. Create a new Map in `Maps/` using the Map template (or run `/pulse` and the agent will generate it)
3. Assign a `domain` slug (lowercase, hyphens)
4. Set `base_priority` (1-10 scale relative to existing efforts)
5. Add to the relevant context batch

To retire an effort:
1. Set all linked notes to `status: archived`
2. Set the Map's `open_loops` to 0
3. Move the Map to an `Archive/` directory (create if needed)
4. Remove from `efforts.yaml`

---

## 5. Context Batching

### Principle

Context switching has two distinct costs, and the system must account for both:

1. **Domain switching (primary)** — reloading a different problem domain: codebase, stakeholder relationships, terminology, toolchain. This is the dominant cost. Switching between two coding efforts in unrelated domains (work codebase vs. personal website) incurs a massive context reload even though both are "analytical."

2. **Mode switching (secondary)** — shifting cognitive energy state: from analytical execution to creative exploration, or from focused building to reflective review. This is real but cheaper than domain switching.

If switching between two efforts requires reloading a different mental model (codebase, stakeholder relationships, terminology), they belong in separate batches — even if they use the same skills.

### Defining Batches

Context batches are defined in `efforts.yaml` alongside your efforts. Each batch has two fields:

- **shared_context** (list) — concrete elements shared across efforts in the batch: tools, codebases, environments, knowledge domains, stakeholder worlds. This is the primary grouping axis.
- **mindset** (string) — the cognitive mode/energy state. This is the secondary axis, carried forward from the original design.

Example:

| Batch | Shared Context | Mindset | Efforts |
|-------|----------------|---------|---------|
| **Work** | IDE/terminal, engineering models, team stakeholders | Analytical, execution-focused | my-job, freelance |
| **Projects** | Personal codebases, creative tooling | Creative, exploratory | side-project, open-source |
| **Personal** | Physical environment, bodily awareness | Reflective, embodied | health, learning |

### Batch Ordering

When generating daily checklists, batches are ordered by **combined priority weight** (sum of member effort weights). Within a batch, items are ordered by individual effort weight.

### Batch Gating (Soft Suppression)

Not every batch is worth a context switch on a given day. After ordering batches by combined weight, the checklist identifies **low-value batches** that should be visible but de-emphasized:

A batch is soft-suppressed when ALL of the following are true:
- Combined weight is below **40%** of the top batch's combined weight
- No items have a `due` date within 7 days
- No `status: waiting` items older than 3 days

Suppressed batches render as a single collapsed line in the daily note instead of a full section:

```
> ~[Batch Name] [weight: X.XX] — N items, nothing urgent
```

This keeps them visible (you can always expand/pivot) without prompting action on batches that aren't worth the switching cost today.

### Inspiration Override

The batch system is a *suggestion*, not a cage. When the user says "I want to work on X right now" or shifts topic mid-session:

1. **Immediately pivot** — no friction, no "but your schedule says..."
2. Load the relevant Map(s)
3. Log the context switch in the daily note
4. Apply recency boost to reflect the actual energy applied

Strike when inspiration strikes. The system adapts to the human, never the reverse.

---

## 6. Priority System

### Design

Priority is **computed**, not assigned. No manual priority fields to maintain. The agent calculates `priority_weight` from signals already present in the vault.

### Formula

```
base_score     = base_priority / 10                         # 0.0–1.0
recency_boost  = min(interactions_last_7_days × 0.03, 0.15) # 0.0–0.15
urgency_spike  = deadline_proximity + blocker_pressure       # 0.0–0.20
effort_factor  = sustained_work_momentum                     # 0.0–0.10

priority_weight = min(base_score + recency_boost + urgency_spike + effort_factor, 1.0)
```

### Components Explained

**base_score** — Normalized `base_priority`. This is the life-importance anchor. A priority-9 effort (0.90) will almost always outrank a priority-3 effort (0.30) unless the lower one has urgent signals. Base priority changes rarely — only when life circumstances shift.

**recency_boost** — Each effort interaction in the last 7 days adds +0.03, capped at +0.15. "Interaction" means the effort appeared in a daily note's `domains_touched`, or a note in that effort was created/updated. This rewards momentum — efforts you're actively working on stay visible.

**urgency_spike** — Temporary boost from:
- Notes with `due` dates within 7 days: +0.05 per note, max +0.15
- Notes with `status: waiting` for >3 days: +0.02 per note, max +0.05
- Explicit user declaration ("side-project has a critical bug"): up to +0.20
- Spikes decay naturally as deadlines pass or blockers resolve.

**effort_factor** — Sustained recent work:
- 1-2 notes updated in last 7 days: +0.03
- 3-4 notes: +0.07
- 5+ notes: +0.10
- This captures momentum. An effort you've been pouring work into stays elevated.

### Recomputation

Weights are recalculated:
- At the start of each session (via `/pulse`)
- On demand (via `/recompute`)
- After significant vault changes (triage, review)

The agent always shows the math when weights change, so the user can challenge or adjust.

### Weight Examples

| Scenario | High-Priority Effort (base: 9) | Low-Priority Effort (base: 5) |
|----------|:-:|:-:|
| Normal week | 0.90 + 0.09 + 0.00 + 0.07 = **0.95** | 0.50 + 0.03 + 0.00 + 0.03 = **0.56** |
| Low-priority critical bug | 0.90 + 0.09 + 0.00 + 0.07 = **0.95** | 0.50 + 0.03 + 0.20 + 0.03 = **0.76** |
| Low-priority sprint week | 0.90 + 0.03 + 0.00 + 0.03 = **0.96** | 0.50 + 0.15 + 0.00 + 0.10 = **0.75** |

---

## 7. Frontmatter Schemas

All frontmatter is agent-managed. These schemas are the contract between the vault files and agent operations.

### Map

```yaml
---
type: map
domain: <slug>                  # Canonical effort identifier
context_batch: <batch-name>     # Context batch for grouping (optional)
priority_weight: <0.0-1.0>     # Computed. Never manually set.
base_priority: <1-10>          # Life-importance anchor. Rarely changes.
last_active: <YYYY-MM-DD>      # Last date this effort was touched
open_loops: <int>              # Count of active/waiting items linked to this Map
related_domains:               # Cross-effort connections
  - <slug>
tags: [<tag>, ...]
---
```

### Note

```yaml
---
type: <note|log|plan|reference|capture>
domains:                       # Which Maps this connects to (1 or more)
  - <slug>
status: <active|someday|waiting|done|archived>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
effort_estimate: <small|medium|large>
due: <YYYY-MM-DD|null>         # Optional deadline
context_group: <batch-name|null>
tags: [<tag>, ...]
---
```

### Daily

```yaml
---
type: daily
date: <YYYY-MM-DD>
generated: true
domains_touched: [<slug>, ...]  # Updated throughout the day
items_completed: <int>          # Filled at review
items_deferred: <int>           # Filled at review
---
```

### Capture (Inbox)

```yaml
---
type: capture
source: <voice|text|agent>
captured: <YYYY-MM-DDTHH:MM:SS>
triaged: <true|false>
domains: [<slug>, ...]          # Filled during triage
---
```

---

## 8. Note Lifecycle

```
     ┌─────────┐
     │ capture │  Inbox item. Raw input, not yet classified.
     └────┬────┘
          │ triage
          ▼
     ┌─────────┐
     │ active  │  Work in progress. Appears in checklists and open loops.
     └────┬────┘
          │
     ┌────┴────┐
     ▼         ▼
┌─────────┐ ┌─────────┐
│ waiting │ │ someday │  Blocked / deferred. Tracked but not in daily lists.
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌──────────┐
│  done   │ │ (reactivate) │  Can return to active at any time.
└────┬────┘ └──────────┘
     │ 7 days
     ▼
┌──────────┐
│ archived │  Out of active view. Searchable. Preserves history.
└──────────┘
```

### Transitions

| From | To | Trigger |
|------|----|---------|
| capture | active | Triage assigns domains and status |
| active | waiting | Blocked on external dependency. Note what it's waiting on. |
| active | someday | Deferred indefinitely. Still valued, not urgent. |
| active | done | Work completed. |
| waiting | active | Blocker resolved. |
| someday | active | Revisited and prioritized. |
| done | archived | 7 days after completion. Agent handles automatically. |
| any | archived | Explicitly dropped or no longer relevant. |

---

## 9. Workflows

### Session Start (`/pulse`)

```
1. Read Home.md
2. Read all Map frontmatter (priority_weight, open_loops, last_active)
3. Read today's Daily note if it exists
4. Count untriaged Inbox items
5. If Maps/ is empty, bootstrap from efforts.yaml (see Bootstrap section)
6. Present briefing: top priorities, inbox count, batch weights
7. Wait for direction
```

### Bootstrap (first run)

```
1. Check if Maps/ directory has any .md files
2. If empty, read efforts.yaml
3. For each effort: generate a Map file using the Map template
4. Populate frontmatter from effort config (domain, base_priority, context_batch, purpose)
5. Proceed with normal pulse briefing
```

### Checklist Generation (`/checklist`)

```
1. Scan all Maps for open loops and active threads
2. Scan Notes for active/waiting items with approaching due dates
3. Group items by context batch (read from Map frontmatter or efforts.yaml)
4. Sort batches by combined weight, items within by effort weight
5. Apply batch gating: soft-suppress low-value batches (see Section 5)
6. Generate Daily/YYYY-MM-DD.md — max 10-12 items across full batches
7. Each item links to its source Note or Map section
```

### Capture Flow (`/capture`)

```
1. Create Inbox/YYYY-MM-DD-<slug>.md with capture frontmatter
2. Suggest domain assignment, status, context_group
3. Ask: triage now or leave for later?
```

### Triage (`/triage`)

```
1. Find all Inbox items where triaged: false
2. For each: present content, suggest domains/status/action
3. On confirmation:
   a. Create Note in Notes/ (or append to existing)
   b. Update relevant Map(s): add link, increment open_loops, update last_active
   c. Mark Inbox item triaged: true
4. Report summary
```

### Focus Pivot (`/focus`)

```
1. Resolve effort from flexible input (match against Map filenames and domain slugs)
2. Load the Map
3. Show active threads, related notes, related maps
4. Log context switch in daily note
5. Update Map last_active (recency boost)
```

### End-of-Day Review (`/review`)

```
1. Read today's Daily note
2. Present: completed / still open / emerged
3. For each open item: defer, wait, done, or drop?
4. Update Daily note: End of Day section, counts
5. Update affected Notes: status, updated date
6. Update affected Maps: open_loops, last_active
7. Surface cross-effort insights
```

### Priority Recomputation (`/recompute`)

```
1. Read all Maps
2. Scan Notes for urgency signals (due dates, stale waiting items)
3. Calculate recency from Daily notes (last 7 days)
4. Calculate effort from Note update frequency
5. Compute new weights, update Map frontmatter
6. Update Home.md Current Focus section
7. Present table with full breakdown and change deltas
```

---

## 10. Dataview Integration

The vault uses the Dataview plugin for dynamic views. Queries live in two places:

### Embedded in Maps

Each Map has an inline query listing its linked notes:

```dataview
LIST FROM "Notes" WHERE contains(domains, this.domain) SORT updated DESC
```

### Embedded in Home.md

Priority overview of all Maps:

```dataview
TABLE priority_weight, open_loops, last_active FROM "Maps" SORT priority_weight DESC
```

### Saved Queries (Queries/)

| Query | Purpose |
|-------|---------|
| Active by Domain | All active notes grouped by domain with counts |
| Open Loops | Active and waiting items sorted by staleness (oldest first) |
| Cross Domain | Notes linked to multiple domains |
| Stale Items | Active notes not updated in 14+ days |

---

## 11. Skills Reference

Skills are defined in `.claude/skills/` and invoked as slash commands.

| Skill | File | Trigger | Arguments |
|-------|------|---------|-----------|
| `/pulse` | `pulse/SKILL.md` | Session start | None |
| `/checklist` | `checklist/SKILL.md` | Generate/review daily list | Optional: date |
| `/capture` | `capture/SKILL.md` | Quick capture | The thought to capture |
| `/triage` | `triage/SKILL.md` | Process inbox | Optional: specific file |
| `/focus` | `focus/SKILL.md` | Pivot to effort | Effort name (flexible matching) |
| `/review` | `review/SKILL.md` | End-of-day review | Optional: date |
| `/recompute` | `recompute/SKILL.md` | Refresh priority weights | Optional: effort spike |

### Creating New Skills

1. Create directory: `.claude/skills/<name>/`
2. Create `SKILL.md` with frontmatter (`name`, `description`, `user-invocable: true`, `allowed-tools`)
3. Write the skill protocol in the markdown body
4. Add to this table and `README.md`

---

## 12. Design Decisions

Rationale for non-obvious choices, preserved for future reference.

| Decision | Rationale |
|----------|-----------|
| Flat Notes/ directory | Deep nesting makes LLM traversal expensive. Domains are encoded in frontmatter, not folder paths. |
| Computed priority (not manual) | Manual priority rot. Computed weights reflect reality without maintenance burden. |
| Maps as source of truth (not a database) | Markdown files are human-readable, version-controllable, and Obsidian-native. No external dependencies. |
| Agent-managed frontmatter | Removes friction from capture. Ensures schema consistency. User thinks; agent files. |
| Context batches (not time blocks) | Time blocking fails for creative/knowledge work. Batching by cognitive context respects how attention actually works. |
| Two-axis batching (domain + mode) | Domain switching (reloading a codebase/stakeholder world) is more expensive than mode switching (analytical→creative). The primary grouping axis is shared problem domain, with cognitive mode as a secondary signal. |
| Soft suppression over hiding | Low-value batches are collapsed to a single line rather than omitted. This preserves awareness without prompting action — the user can always pivot if inspiration strikes. |
| Inspiration override as first-class concept | Rigid systems get abandoned. Honoring impulse and energy produces better outcomes than forced compliance. |
| Wikilinks over markdown links | Obsidian graph view. Refactoring-safe (rename propagation). Shorter syntax. |
| 7-day done→archive window | Keeps completed items visible long enough to inform review, short enough to not clutter. |
| efforts.yaml config | Decouples effort definitions from system code. New users define efforts once, engine reads dynamically. |

---

## 13. Evolution Log

Record significant changes to the system here. Date, what changed, why.

| Date | Change | Reason |
|------|--------|--------|
| 2026-03-12 | Two-axis context batching (`shared_context` + `mindset`) | Original single-axis (mindset only) missed the dominant switching cost: problem domain. Two unrelated codebases incur massive context reload even in the same cognitive mode. |
| 2026-03-12 | Batch gating / soft suppression in daily checklist | Low-value batches were forcing unnecessary context switches. Collapsed lines keep them visible without prompting action. |
