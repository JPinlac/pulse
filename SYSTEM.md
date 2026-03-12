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
3. **Triage** classifies, assigns efforts, creates or appends to Notes
4. **Notes** are the atomic units of content — linked to Maps via `efforts[]`
5. **Maps** aggregate notes per effort — they hold active threads, open loops, and purpose
6. **Home.md** is a computed view across all Maps — priorities, recent activity, tensions
7. **Daily notes** are living session records — agenda + effort log, built conversationally

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
├── Inbox/                   Zero-friction capture. Quick thoughts.
│   └── .keep
│
├── Maps/                    One MOC per effort. Source of truth. Ships with defaults.
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
│   ├── Active by Effort.md
│   ├── Open Loops.md
│   ├── Cross Effort.md
│   └── Stale Items.md
│
└── .claude/
    └── skills/              Slash command definitions.
        ├── pulse/
        ├── birdseyereview/
        ├── capture/
        ├── triage/
        ├── focus/
        ├── close/
        ├── recompute/
        ├── defrag/
        └── efforts/
```

---

## 4. Effort System

### Defining Your Efforts

Every endeavor in your life maps to exactly one effort. Each effort has a Map file that serves as its source of truth.

Efforts are defined by their Map files in `Maps/`. Each Map's frontmatter contains:

| Field | Description | Example |
|-------|-------------|---------|
| `effort` | Lowercase, hyphenated identifier (slug) | `my-job` |
| `base_priority` | Life-importance anchor, 1-10 | 9 |
| `context_batch` | Group name for context switching | "Work" |
| `purpose` | One-line description of why this matters | "Day job, pays the bills" |
| `aliases` | Optional flexible-match terms for `/focus` resolution | `[job, work]` |

### Effort Interconnections

Efforts are not siloed. They feed each other. When defining your efforts, consider how they relate:
- Which efforts fund or enable others?
- Which efforts share intellectual territory?
- Which efforts produce output that feeds into others?

These connections surface as `related_efforts` in Map frontmatter and help the agent identify cross-pollination opportunities.

### Managing Efforts

Use `/efforts` for all effort lifecycle operations — add, splinter, merge, review. The skill handles Map creation/migration and documentation updates.

| Command | What it does |
|---------|-------------|
| `/efforts` | Show current effort landscape |
| `/efforts add` | Guided creation with a litmus test to prevent bloat |
| `/efforts splinter <slug>` | Break a complex effort into sub-efforts |
| `/efforts merge <slug> <slug>` | Combine two efforts that have converged |
| `/efforts review` | Audit effort health — flag stale, overlapping, or orphaned efforts |

---

## 5. Context Batching

### Principle

Context switching has two distinct costs, and the system must account for both:

1. **Domain switching (primary)** — reloading a different problem domain: codebase, stakeholder relationships, terminology, toolchain. This is the dominant cost. Switching between two coding efforts in unrelated domains (work codebase vs. personal website) incurs a massive context reload even though both are "analytical."

2. **Mode switching (secondary)** — shifting cognitive energy state: from analytical execution to creative exploration, or from focused building to reflective review. This is real but cheaper than domain switching.

If switching between two efforts requires reloading a different mental model (codebase, stakeholder relationships, terminology), they belong in separate batches — even if they use the same skills.

### Defining Batches

Context batch definitions live in `CLAUDE.md` as agent guidance. Each effort's batch assignment is stored in its Map's `context_batch` frontmatter field. Each batch has two axes:

- **shared_context** — concrete elements shared across efforts in the batch: tools, codebases, environments, knowledge domains, stakeholder worlds. This is the primary grouping axis.
- **mindset** — the cognitive mode/energy state. This is the secondary axis.

Example:

| Batch | Shared Context | Mindset | Efforts |
|-------|----------------|---------|---------|
| **Work** | IDE/terminal, engineering models, team stakeholders | Analytical, execution-focused | my-job, freelance |
| **Projects** | Personal codebases, creative tooling | Creative, exploratory | side-project, open-source |
| **Personal** | Physical environment, bodily awareness | Reflective, embodied | health, learning |

### Batch Ordering

When generating daily checklists, batches are ordered by **combined priority weight** (sum of member effort weights). Within a batch, items are ordered by individual effort weight.

### Batch Gating (Soft Suppression)

Not every batch is worth a context switch on a given day. After ordering batches by combined weight, the checklist and pulse briefing soft-suppress low-value batches — visible but de-emphasized.

A batch is soft-suppressed when **all** of the following are true:
- Combined weight is below **40%** of the top batch's combined weight
- No items with `due` dates within 7 days
- No `status: waiting` items older than 3 days

In checklists, suppressed batches render as a single collapsed line:

```
> ~[Batch Name] [weight: X.XX] — N items, nothing urgent
```

In pulse, suppressed batches collapse into a fold-line count (e.g., "3 efforts across 2 batches below the fold"). Say "unfold" for the full landscape.

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

**recency_boost** — Each effort interaction in the last 7 days adds +0.03, capped at +0.15. "Interaction" means the effort appeared in a daily note's `efforts_touched`, or a note in that effort was created/updated. This rewards momentum — efforts you're actively working on stay visible.

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
- After significant vault changes (triage, defrag)

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
effort: <slug>                  # Canonical effort identifier
context_batch: <batch-name>     # Context batch for grouping
priority_weight: <0.0-1.0>     # Computed. Never manually set.
base_priority: <1-10>          # Life-importance anchor. Rarely changes.
purpose: <string>              # One-line description of why this effort matters
aliases: [<alias>, ...]        # Optional flexible-match terms for /focus resolution
last_active: <YYYY-MM-DD>      # Last date this effort was touched
open_loops: <int>              # Count of active/waiting items linked to this Map
related_efforts:               # Cross-effort connections
  - <slug>
tags: [<tag>, ...]
---
```

### Note

```yaml
---
type: <note|log|plan|reference|capture>
efforts:                       # Which Maps this connects to (1 or more)
  - <slug>
status: <active|someday|waiting|done|archived>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
effort_level: <trivial|small|medium|large|null>  # Mental absorption required
timescale: <daily|weekly|monthly|quarterly|biannual|annual|null>  # Natural periodicity
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
efforts_touched: [<slug>, ...]  # Updated throughout the day
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
efforts: [<slug>, ...]          # Filled during triage
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
| capture | active | Triage assigns efforts and status |
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
1. If Maps/ has no .md files, bootstrap by creating default Maps (see Bootstrap section)
2. Light defrag: auto-triage pending Inbox items, reconcile Map counts, flag stale Maps
3. Read Home.md
4. Read all Map frontmatter (priority_weight, open_loops, last_active)
5. Read today's Daily note if it exists
6. Present compact briefing: top priorities, housekeeping (inline), active batches with loop counts
   — Apply batch gating + effort-level suppression (omit efforts with 0 loops + stale + no deadlines)
   — Suppressed batches/efforts collapse to a single fold-line ("say unfold for full landscape")
7. Full view on request: all batches, all efforts, top threads, stale Maps
8. Wait for direction
9. Build Daily Note from conversation — when the user indicates what they want to work on:
   — Pull focused items from indicated Maps, grouped by batch
   — Scan remaining Maps for time-sensitive/routine items (nothing falls through cracks)
   — Keep to 8-15 items. Present in chat for one confirmation pass, then write to file.
   — Subsequent Daily Note updates during the session happen silently.
```

### Bootstrap (first run)

```
1. Check if Maps/ directory has any .md files
2. If empty, present 3 default efforts (Work, Life Maintenance, Personal Projects)
3. Ask: "Want to start with these, or tell me about your life and I'll tailor them?"
4. Create Maps directly with full frontmatter (effort, base_priority, context_batch, purpose, aliases)
5. Proceed with normal pulse briefing
```

### Full Landscape Audit (`/birdseyereview`)

```
1. Scan all Maps for open loops and active threads
2. Scan Notes for active/waiting items with approaching due dates
3. Group items by context batch to minimize context switching
4. Sort batches by combined weight, items within by effort weight
5. Zero suppression — every batch rendered fully
6. Generate Daily/YYYY-MM-DD.md with all items linked to source Notes/Maps
7. Use for periodic reviews (weekly, after a break), not daily agenda setting
```

### Capture Flow (`/capture`)

```
1. Delegate to a background sub-agent (zero context disruption to main conversation)
2. Sub-agent creates Inbox/YYYY-MM-DD-<slug>.md with capture frontmatter
3. Confirm immediately (don't wait for agent): "Captured: [title]. Filing in background."
4. Auto-triage picks it up at next /pulse or /triage.
```

### Auto-Triage (`/triage`)

```
1. Find all Inbox items where triaged: false
2. For each: match content against Maps, assign efforts/status — no confirmation
3. Execute immediately:
   a. Create Note in Notes/ (or append to existing)
   b. Update relevant Map(s): add link, increment open_loops, update last_active
   c. Mark Inbox item triaged: true
4. Report summary: "Auto-triaged N items: [title] → [effort], ..."
```

### Focus Pivot (`/focus`)

```
1. Resolve effort from flexible input (match against names, slugs, and aliases — case-insensitive, partial match)
2. Load the Map
3. Show active threads, related notes, related maps
4. Log context switch in daily note
5. Update Map last_active (recency boost)
```

### End-of-Session Reflection (`/close`)

```
1. Read today's Daily note and Map activity
2. Read relevant Maps and Notes for context on what moved today
3. Present reflection narrative: what happened, what emerged, patterns
4. Flag items needing human attention (deferred 3+ times, efforts gone dark, cross-effort tensions)
5. Invite optional reflection — user can volunteer status changes
6. Apply any status changes the user offers
7. Update Daily note: End of Day section, counts
8. Auto-trigger /defrag (full pass) for all bookkeeping
```

### Defrag (`/defrag`)

```
Light pass (during /pulse):
1. Auto-triage pending Inbox items
2. Reconcile Map open_loops counts against actual Notes
3. Flag stale Maps (last_active > 7 days)
4. Report briefly — one-line summary for the pulse briefing

Full pass (after /close or manual):
All of the above, plus:
5. Auto-defer unchecked Daily note items to tomorrow
6. Auto-complete checked items (update Note status)
7. Catch misclassifications from auto-triage (flag, don't auto-fix)
8. Flag stale items (active Notes past their timescale window — see threshold table in defrag skill)
9. Identify merge candidates (overlapping Notes in same effort)
10. Update all timestamps (last_active on Maps, updated on Notes)
11. Report structured summary of everything done and flagged
12. Log to Daily Note — append timestamped one-liner under ## Defrag Log section
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
LIST FROM "Notes" WHERE contains(efforts, this.effort) SORT updated DESC
```

### Embedded in Home.md

Priority overview of all Maps:

```dataview
TABLE priority_weight, open_loops, last_active FROM "Maps" SORT priority_weight DESC
```

### Saved Queries (Queries/)

| Query | Purpose |
|-------|---------|
| Active by Effort | All active notes grouped by effort with counts |
| Open Loops | Active and waiting items sorted by staleness (oldest first) |
| Cross Effort | Notes linked to multiple efforts |
| Stale Items | Active notes past their timescale staleness window (default 14 days) |

---

## 11. Skills Reference

Skills are defined in `.claude/skills/` and invoked as slash commands.

| Skill | File | Trigger | Arguments |
|-------|------|---------|-----------|
| `/pulse` | `pulse/SKILL.md` | Session start (includes light defrag) | None |
| `/birdseyereview` | `birdseyereview/SKILL.md` | Full landscape audit (periodic reviews) | Optional: date |
| `/capture` | `capture/SKILL.md` | Quick capture | The thought to capture |
| `/triage` | `triage/SKILL.md` | Auto-process inbox (no confirmation) | Optional: specific file |
| `/focus` | `focus/SKILL.md` | Pivot to effort | Effort name (flexible matching) |
| `/close` | `close/SKILL.md` | End-of-session reflection + auto-defrag | Optional: date |
| `/recompute` | `recompute/SKILL.md` | Refresh priority weights | Optional: effort spike |
| `/defrag` | `defrag/SKILL.md` | Organizational cleanup (full pass) | Optional: `light` or `full` |
| `/efforts` | `efforts/SKILL.md` | Manage effort lifecycle | `add`, `splinter <slug>`, `merge <slug> <slug>`, `review` |

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
| Auto-triage (no confirmation) | Confirmation cycles impose cognitive load at exactly the wrong moment — transitioning back to work. Misclassification cost is low (defrag catches it); confirmation cost is real. |
| Reflection-only review | Item-by-item "defer/wait/done/drop?" loops are bureaucratic, not reflective. The human's end-of-session energy is better spent on narrative reflection. All bookkeeping moves to defrag. |
| Defrag as separate skill | Separates thinking (human) from filing (agent). Review is for reflection; defrag handles mechanics. Three entry points (post-review, pulse light pass, manual) ensure cleanup happens without human effort. |
| Wikilinks over markdown links | Obsidian graph view. Refactoring-safe (rename propagation). Shorter syntax. |
| 7-day done→archive window | Keeps completed items visible long enough to inform review, short enough to not clutter. |
| Maps as sole effort source | Effort definitions live in Map frontmatter. No intermediate config file. Ships with pre-built default Maps. |

---

## 13. Evolution Log

Record significant changes to the system here. Date, what changed, why.

| Date | Change | Reason |
|------|--------|--------|
| 2026-03-12 | Redesign: auto-triage, reflective review, defrag | Triage drops confirmation loops, review becomes pure reflection, new /defrag skill absorbs all bookkeeping. Separates thinking (human) from filing (agent). |
| 2026-03-12 | Two-axis context batching with soft suppression | Batches now defined by shared_context (domain) and mindset (cognitive mode). Low-value batches are soft-suppressed in daily checklists and pulse briefings. Batch definitions live in CLAUDE.md. |
| 2026-03-12 | Compact pulse briefing with fold-line suppression | Pulse now shows a compact view by default — batch gating + effort-level suppression collapse low-signal items into a fold-line. Full landscape on request ("unfold"). |
| 2026-03-12 | Conversational Daily Note flow + defrag logging | Daily Note now accretes through /pulse conversation (not batch-generated). /defrag logs to Daily Note. /birdseyereview repositioned as periodic audit. /focus clarified as deep flow tool. |
| 2026-03-12 | Background sub-agent capture | /capture now delegates to a background agent for zero context disruption. Main conversation flow is preserved. |
| 2026-03-12 | /efforts skill + pre-built default Maps | Engine ships with 3 default Maps. /efforts skill handles add, splinter, merge, review with litmus test and anti-spaghetti guidelines. |
| 2026-03-12 | Eliminated efforts.yaml | Maps are the sole source of truth for effort definitions. Context batch definitions moved to CLAUDE.md. Pre-built default Maps replace YAML bootstrap. |
