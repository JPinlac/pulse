---
type: note
subtype: note
efforts: [pulse]
status: active
context_group: Projects
created: 2026-03-21
updated: 2026-04-11
effort_level: medium
timescale: null
tags: [meta, system-design, intake, context, roles]
related: [pulse-cc-channels]
informs: [[pulse-graph-architecture]], [[pulse-architecture-improvements]], [[pulse-mao-multi-agent-orchestration]]
---
# PULSE — Context Processing Pipeline

Intake is not filing. It is the first step in a context processing pipeline.

## Pipeline Stages

1. **Capture** — voice (mic) or text via channel (Telegram/Discord). Voice is the primary modality; lowest friction.
2. **Pre-context scaffolding** — the known effort association loads the Map *before* triage. Active threads, open loops, and trajectory signals provide the reception frame. Raw input lands into structured context, not an empty bucket.
3. **Triage** — with scaffolding in place, classification produces trajectory signals (advance / block / reframe / open), not just effort tags.
4. **Map update** — motion recorded, not just state.

## The Core Insight

When context enters PULSE, it arrives with a known effort association (preknown from conversational context). That means the effort Map can scaffold the intake — providing structure, active threads, and trajectory signals — before triage even begins. Raw input meets structured context on arrival.

## Roles as Context in Action

A "meeting" is a formalized instance of this: external context gets translated into personal context buckets shaped by the participant's role. Roles are not static categories — they are **stances toward context**. A role is context in action: it determines what gets noticed, what matters, what moves.

Each person creates **projections into the future** from their current role + context combination. The filing informs the trajectory.

## Implication for PULSE

Triage should produce not just effort tags but **trajectory signals**:
- Does this context *advance*, *block*, *reframe*, or *open* a thread?
- What does this intake imply about where the effort is heading?

Maps should reflect **motion**, not just state. An effort's active threads are not static items — they are vectors.

## Informs
- [[pulse-graph-architecture]] — trajectory signals (advance/block/reframe/open) are what the graph should encode on edges, not just state
- [[pulse-architecture-improvements]] — "intake as pipeline, not filing" reframes triage as an architectural concern
- [[pulse-mao-multi-agent-orchestration]] — roles-as-context-in-action scaffolds how multi-agent participants frame shared context

## Related
- [[pulse-cc-channels]] — CC Channels as a mechanism for multi-party context intake (agents as participants)
