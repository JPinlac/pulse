---
type: note
subtype: reference
efforts: [pulse]
status: active
importance: medium
created: 2026-05-12
updated: 2026-05-12
informs: [[pulse-execution-modes]], [[pulse-mao-multi-agent-orchestration]], [[pulse-agent-hook-traceability]]
tags: [meta, harness, claude-code, tooling]
---
# Claude Code Harness — Behavior & Workflow Changes

Observational log of behavior shifts in the Claude Code harness as they manifest in PULSE workflow. The harness is the substrate PULSE skills run on — when it changes, skill behavior changes, often without explicit signaling. This doc exists so the dyad doesn't re-derive "wait, did this used to work differently?" each time.

## Why this matters

PULSE skills assume harness semantics: tool result formats, sub-agent permission inheritance, hook firing timing, context window management, deferred-tool loading, skill triggering conventions. When those shift, skills either (a) silently degrade or (b) gain new affordances we haven't yet exploited. Either way the dyad needs to notice and adapt — and the noticing has to be written down, because behavioral shifts feel "normal" within a session and only become diagnosable across sessions.

This is the harness analogue of `EVOLUTION.md` — but for changes we *didn't* make to PULSE; rather, changes the substrate made to us.

## How to use this doc

When you notice the harness behaving differently than expected — or differently than past sessions — append an observation below with date, what changed, and (if known) which skills or workflows are affected. Don't try to be exhaustive in a single entry; observations accrete.

When a behavior shift makes a PULSE convention obsolete, update the relevant skill/CLAUDE.md and add a back-reference here.

## Observations

### 2026-05-12 — Update noticed, workflow shift in progress

Harness updated; workflow noticeably changed. Specific shifts not yet enumerated — this is the seed entry. Things felt this session that may be harness-driven (verify before treating as confirmed):

- Tool surfacing changed: many tools (TaskCreate, WebSearch, EnterPlanMode, AskUserQuestion, MCP tools, etc.) now appear as **deferred tools** — listed by name in a system-reminder, callable only after fetching their schema via `ToolSearch`. Implies the harness is being selective about what loads into context by default. PULSE skills that assume "TaskCreate is always available" may now incur a ToolSearch round-trip first.
- Skills surfaced via system-reminder listing rather than always-loaded — agent must invoke via the `Skill` tool by name from that list, not assume availability.
- Auto-memory system explicitly disabled at the CLAUDE.md level (PULSE has its own); harness-level memory features may have changed in ways that conflict with PULSE's persistence model.

## What to watch

- **Sub-agent write permissions** — open Minor Action in pulse Map flags sub-agents denied Write/Edit; harness updates may resolve or worsen this. If sub-agent permissions changed, the MAO inter-agent boundary needs re-checking.
- **Hook firing timing and payload** — `/close`, `/defrag`, and Stop-hook patterns depend on specific firing semantics.
- **Tool batching and parallel call behavior** — PULSE relies heavily on parallel tool calls for file ops; any throttling or serialization changes would slow `/defrag` and `/triage`.
- **Context management** — auto-compaction triggers, system-reminder cadence, prompt cache TTL (the `ScheduleWakeup` tool description notes a 5-minute cache TTL, useful constraint to remember).
- **Skill triggering** — what auto-fires vs what requires explicit `/<name>` invocation. The `Skill` tool's instructions are explicit that skills should not be guessed; this constrains how PULSE can hand off across skills.
- **Background sub-agents** — the `run_in_background` parameter on Agent and Bash tools; PULSE's silent file ops convention assumes this is available and reliable.

## Informs

- [[pulse-execution-modes]] — hook/sub-agent/main-flow execution patterns are defined by harness semantics; shifts here cascade into SRSA function placement
- [[pulse-mao-multi-agent-orchestration]] — sub-agent vs dispatched-agent capability boundaries are harness-defined; permission changes change the boundary
- [[pulse-agent-hook-traceability]] — trace persistence depends on what the harness surfaces about sub-agent and hook activity
