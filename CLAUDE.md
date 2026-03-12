# PULSE — Priority-Updated Living System Engine

> Deep reference: `SYSTEM.md` — read only when you need full design context (formulas, rationale, evolution log). Do NOT load it by default.

## Efforts & Domain Slugs

Read effort definitions (slugs, base_priority, context_batch, purpose) from:
1. **`Maps/` directory** — each Map's frontmatter is the live source of truth
2. **`efforts.yaml`** — bootstrap config used to generate Maps on first run

If Maps exist, they are authoritative. If Maps/ is empty, read `efforts.yaml` and generate Maps first.

## Context Batches

Context batches group efforts along two axes: **problem domain** (primary) and **cognitive mode** (secondary). Read batch definitions (`shared_context` list + `mindset` string) from `efforts.yaml`. Read each effort's batch assignment from Map frontmatter (`context_batch` field). Domain switching (reloading a different codebase/stakeholder world) is more expensive than mode switching, so `shared_context` is the primary grouping signal.

## Vault Structure
- `Home.md` — Dynamic focus dashboard
- `Maps/` — One MOC per effort (source of truth)
- `Notes/` — All content notes (flat)
- `Daily/` — Generated checklists (YYYY-MM-DD.md)
- `Inbox/` — Zero-friction capture
- `Templates/` — Obsidian templates
- `Queries/` — Saved Dataview queries

## Agent Conventions

### Session Start
1. Read `Home.md` for priorities
2. Read relevant Map(s) for user's intent
3. If Maps/ is empty: read `efforts.yaml`, generate Maps, then proceed
4. If daily session: generate `Daily/YYYY-MM-DD.md` from Map open loops

### Frontmatter is Agent-Managed
The user never manually writes metadata. Agent writes/updates all YAML frontmatter.

### Note Types
- `type: map` — Effort MOCs in `Maps/`
- `type: note` — Content notes (subtypes: note, log, plan, reference, capture)
- `type: daily` — Generated daily checklists
- `type: capture` — Inbox items pending triage

### Note Lifecycle
`capture → active → waiting → done → archived`

### Priority Weight Formula
`priority_weight = f(base_priority, recency_boost, urgency_spike, effort_applied)` normalized to 0.0–1.0

### Capture Flow
1. Create `.md` in `Inbox/` with capture frontmatter
2. Triage: assign `domains[]`, suggest `status` and `context_group`
3. Create proper Note in `Notes/` or append to existing
4. Update relevant Map(s)

### Inspiration Override
When the user shifts topic, immediately pivot. Log the context switch in daily note. Adjust weights. The system adapts to the user, not the other way around.
