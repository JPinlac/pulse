---
type: note
subtype: note
efforts: [pulse]
status: active
importance: medium
created: 2026-03-26
updated: 2026-04-11
timescale: monthly
tags: [sati, architecture, meta-agent, separation-of-concerns]
related: [pulse-sati-batched-sensitivity, pulse-ab-testing-framework, pulse-mao-multi-agent-orchestration]
informs: [[pulse-execution-modes]], [[pulse-mao-multi-agent-orchestration]], [[pulse-agent-hook-traceability]], [[pulse-ab-testing-framework]]
---
# Sati as Meta-Agent

## The Problem

Sati instructions are currently loaded into the same agent that computes priority weights, triages inbox, and renders briefings. Asking that agent to simultaneously watch for reification is like asking someone to proofread while doing math. The concerns interfere in both directions:

- **Sati disrupts processing**: A reification observation mid-computation could derail the weight calculation or triage logic
- **Processing suppresses Sati**: Computational focus crowds out nascent observations because they "don't fit" the current step
- **Attention contamination**: Sati's watchlist (category violations, cross-pollination, reification) primes the agent toward pattern-seeking when the main chain needs to be executing

## Proposal: Sati as Parallel Observer

Sati becomes a meta-agent — runs alongside the main processing chain, observes the same data, but from outside the execution path.

### Properties
- **Read-only**: receives same input data (Maps, Notes, conversation) as observer, never touches main output
- **Focused context**: loaded with only the Sati watchlist + relevant data, no computational overhead
- **Decoupled timing**: can run during or after the main chain — results don't block output
- **Clean reporting**: observations logged to session log, surfaced to user after main output

### Execution Model

**During /pulse**:
1. Main chain runs phases A-F, renders briefing (no Sati instructions loaded)
2. Sati meta-agent spawns as background sub-agent with: today's conversation context + Map/Note data collected during Phase B/C + Sati watchlist
3. Sati agent reports observations → appended to session log
4. If high-signal observation, surfaced in next user-facing output

**During conversation**:
- Sati meta-agent could be a persistent background observer spawned at session start
- Receives conversation turns as they happen
- Flags observations asynchronously
- Main agent is free to execute without ambient sensitivity overhead

### What This Changes

Current CLAUDE.md Sati section becomes documentation of what the meta-agent watches for, not instructions to the main agent. The main agent's job is execution. The meta-agent's job is noticing.

### Open Questions
- Can a background sub-agent receive ongoing conversation context, or does it only get what it's spawned with?
- If spawn-only: should Sati run at session checkpoints (/pulse, /close, /defrag) rather than continuously?
- How does the meta-agent distinguish between observations worth surfacing immediately vs. logging quietly?
- Does this model extend beyond Sati? Could other "meta concerns" (work-capacity monitoring, calibration drift detection) run as parallel observers?

### Dharma Parallel

This mirrors the contemplative distinction between the mind that acts and the mind that observes the acting mind. Sati in practice is not part of the cognitive process — it's the awareness that watches cognition happen. Making it a separate agent is architecturally honest to the concept.

## Informs
- [[pulse-execution-modes]] — parallel observer vs in-chain execution is a core SRSA-mapped mode distinction
- [[pulse-mao-multi-agent-orchestration]] — meta-agent as read-only observer is a first-class MAO role
- [[pulse-agent-hook-traceability]] — async Sati reports must be traceable back to the main chain's data
- [[pulse-ab-testing-framework]] — meta-agent vs in-chain Sati is a testable variant
