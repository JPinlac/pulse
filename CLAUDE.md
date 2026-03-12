# PULSE — Priority-Updated Living System Engine

> Deep reference: `SYSTEM.md` — read only when you need full design context (formulas, rationale, evolution log). Do NOT load it by default.

## Efforts & Domain Slugs

Read effort definitions (slugs, base_priority, context_batch, purpose) from:
1. **`Maps/` directory** — each Map's frontmatter is the live source of truth
2. **`efforts.yaml`** — bootstrap config used to generate Maps on first run

If Maps exist, they are authoritative. If Maps/ is empty, read `efforts.yaml` and generate Maps first.

<!-- SLUG-TABLE-START — managed by /efforts, do not edit manually -->
| Slug | Batch | Aliases |
|------|-------|---------|
| maintenance | Maintenance | health, house, chores, admin |
| personal-projects | Projects | projects, hobby, side project |
| work | Work | job, career |
<!-- SLUG-TABLE-END -->

## Context Batches

Context batches group efforts along two axes: **problem domain** (primary) and **cognitive mode** (secondary). Read batch definitions (`shared_context` list + `mindset` string) from `efforts.yaml`. Read each effort's batch assignment from Map frontmatter (`context_batch` field). Domain switching (reloading a different codebase/stakeholder world) is more expensive than mode switching, so `shared_context` is the primary grouping signal.

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
3. If Maps/ is empty: read `efforts.yaml`, generate Maps, then proceed
4. If daily session: generate `Daily/YYYY-MM-DD.md` from Map open loops

### Daily Note — Living Session Record
The Daily Note (`Daily/YYYY-MM-DD.md`) accretes through conversation, not batch-generated.
- **After `/pulse` briefing**: when the user indicates direction, create/update the Daily Note with a prioritized agenda. Pull focused items from relevant Maps AND routine life items so nothing falls through cracks. Aim for 8-15 items. Present in chat for one confirmation pass, then commit to file.
- **During the session**: log effort silently — context switches, completions, new items that emerge.
- **`/defrag`**: appends a compressed log entry to the Daily Note.
- **`/close`**: caps the Daily Note with End of Day reflection.

The Daily Note is the single source of truth for what was planned and what actually happened today.

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

### Inspiration Override
When the user shifts topic, immediately pivot. Log the context switch in daily note. Adjust weights. The system adapts to the user, not the other way around.
