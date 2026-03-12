# PULSE — Priority-Updated Living System Engine

> Deep reference: `SYSTEM.md` — read only when you need full design context (formulas, rationale, evolution log). Do NOT load it by default.

## Efforts & Domain Slugs

**`Maps/` directory is the sole source of truth** for effort definitions (slugs, base_priority, context_batch, purpose, aliases). Each Map's frontmatter is authoritative.

If Maps/ is empty, run `/efforts bootstrap` to generate starter Maps.

<!-- SLUG-TABLE-START — managed by /efforts, do not edit manually -->
| Slug | Batch | Aliases |
|------|-------|---------|
| maintenance | Maintenance | health, house, chores, admin |
| personal-projects | Projects | projects, hobby, side project |
| work | Work | job, career |
<!-- SLUG-TABLE-END -->

## Context Batches

Context batches group efforts along two axes: **problem domain** (primary) and **cognitive mode** (secondary). Read each effort's batch assignment from Map frontmatter (`context_batch` field). Domain switching (reloading a different codebase/stakeholder world) is more expensive than mode switching, so `shared_context` is the primary grouping signal.

### Default Batch Definitions

| Batch | Shared Context | Mindset |
|-------|----------------|---------|
| **Work** | IDE/terminal workflow, engineering mental models, team stakeholders and processes | Analytical, execution-focused |
| **Maintenance** | Physical environment, bodily awareness, routines and logistics | Practical, embodied |
| **Projects** | Personal codebases, creative tooling | Creative, exploratory |

New batches can be created during `/efforts add` when existing batches don't fit. Add new batch definitions to this table when created.

## Vault Structure
- `Home.md` — Dynamic focus dashboard
- `Maps/` — One MOC per effort (source of truth)
- `Notes/` — All content notes (flat)
- `Daily/` — Session agenda + effort log (YYYY-MM-DD.md)
- `Inbox/` — Zero-friction capture
- `Templates/` — Obsidian templates
- `Queries/` — Saved Dataview queries

## Agent Conventions

### Session Start
1. Read `Home.md` for priorities
2. Read relevant Map(s) for user's intent
3. If Maps/ is empty: run `/efforts bootstrap` to generate starter Maps, then proceed
4. If daily session: generate `Daily/YYYY-MM-DD.md` from Map open loops

### Daily Note — Living Session Record
The Daily Note (`Daily/YYYY-MM-DD.md`) accretes through conversation, not batch-generated.
- **After `/pulse` briefing**: when the user indicates direction, create/update the Daily Note with a prioritized agenda. Pull focused items from relevant Maps AND routine life items so nothing falls through cracks. Aim for 8-15 items. Present in chat for one confirmation pass, then commit to file.
- **During the session**: log effort silently — context switches, completions, new items that emerge.
- **`/defrag`**: appends decision traces to `## Session Log`.
- **`/close`**: caps the Daily Note with End of Day reflection.

The Daily Note is the single source of truth for what was planned and what actually happened today.

### Session Log — Decision Trace Layer
The `## Session Log` section in each Daily Note captures agent decisions for later debugging. This is not user-facing — it exists so an LLM in a future session can trace why something was prioritized, suppressed, or classified the way it was.

Four operations write to Session Log:
- **`/recompute`** — appends full weight table with per-component breakdown and delta from previous values. Includes which Notes sourced urgency spikes.
- **`/defrag`** — appends per-Map reconciliation traces, per-Note stale checks with thresholds, and per-item defer/complete/misclassification decisions. Replaces the old one-liner count format.
- **`/pulse`** — appends suppression reasoning: which batches/efforts were suppressed, the weight values and thresholds that triggered suppression, and what was resurfaced.
- **`/triage`** — appends classification decisions with match rationale: which Map purpose matched each Inbox item and why.

Each entry is `### [Operation] — HH:MM` with structured subsections. Omit empty subsections. Keep individual lines compact (one line per decision) but complete enough that reading the Session Log alone is sufficient to answer "why was X ranked/hidden/classified this way on this date."

### Frontmatter is Agent-Managed
The user never manually writes metadata. Agent writes/updates all YAML frontmatter.

### Map Entry Compression
Maps are indices, not containers. When a Note exists for a thread:
- Map entry = `[[note-slug]] — [≤15-word summary] (subtype, date)`
- Never inline note content or extended summaries into Maps
- Bare action items (no Note) remain as plain text in Active Threads
When loading an effort for context, read the Map only. Read linked Notes only when actively working on that thread.

### Note Types
- `type: map` — Effort MOCs in `Maps/`
- `type: note` — Content notes (subtypes: note, log, plan, reference, capture)
- `type: daily` — Session agenda + effort log
- `type: capture` — Inbox items pending triage

### Note Lifecycle
`capture → active → waiting → done → archived`

### Priority Weight Formula
`priority_weight = f(base_priority, recency_boost, urgency_spike, effort_applied)` normalized to 0.0–1.0

### Capture Flow
1. Delegate to a background sub-agent (zero context disruption to main conversation)
2. Sub-agent creates `.md` in `Inbox/` with capture frontmatter
3. Confirm immediately — don't wait for the agent to finish
4. Auto-triage picks it up at next `/pulse` or `/triage` — no human confirmation needed
5. `/defrag` catches any misclassifications later

### Display Behavior
Low-value batches are soft-suppressed in `/pulse` output. `/birdseyereview` provides a full unsuppressed landscape audit when needed. Suppressed batches and low-signal efforts (0 loops, stale, no deadlines) are folded — say "unfold" for the full landscape.

### Silent File Operations
All file writes (Daily Notes, Session Logs, Map updates, triage results) must be delegated to background sub-agents. The main conversation should only display human-readable output (briefings, confirmations, summaries). Never perform inline Write/Edit calls for logging or note management in the main conversation — it pollutes the display context.

### Inspiration Override
When the user shifts topic, immediately pivot. Log the context switch in daily note. Adjust weights. The system adapts to the user, not the other way around.
