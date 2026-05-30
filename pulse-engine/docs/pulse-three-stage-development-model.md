---
type: note
subtype: reference
efforts: [pulse]
status: active
context_group: Projects
created: 2026-03-12
updated: 2026-04-11
effort_level: medium
timescale: null
tags: [meta, system-design, roadmap, trust-building]
informs: [[pulse-architecture-improvements]], [[pulse-capacity-model]], [[pulse-evaluation-evolution-harness]]
---
# PULSE — Three-Stage Development Model

A development model for PULSE as a cognitive context manager, derived from examining the trust-building requirement before cognitive load reduction can work.

## Stage 1 (current): Comprehensive ground truth
Show everything — full landscape, all domains, all loops. The user verifies the system against their own mental model. Discrepancies get caught. Over weeks, the system proves it's reliable: nothing slips through triage, weights track reality, Maps stay current. The cognitive cost of seeing all 9 domains is the price of building trust. The /pulse output isn't bad now at ~13 loops. The problem is 30 loops, or 3 simultaneous urgency spikes.

**Optimizing for:** completeness (don't miss anything)
**Cost:** cognitive breadth

## Stage 2 (earned): Active scope reduction
Once trust is established, the system can hide things. Session contracts and "enough for now" declarations activate. /pulse shifts from "here's everything" to "here's what needs you today; 5 domains are handled — here's why." The user stops checking because weeks of operation have proven the system's "handled" judgment matches theirs.

**Optimizing for:** relevance (show only what matters now)
**Cost:** surrendering oversight

## Stage 3 (mature): Attention protection
The system becomes opinionated. Pushes back on context switches. Factors switch cost into the priority formula. Manages cognitive budget as a resource, not just a task list. Only works if Stage 2 trust is deep — the user must believe the system would interrupt if something truly needed it.

**Optimizing for:** protection (guard attention as a resource)
**Cost:** ceding judgment about your own focus

## Key transitions

- **1→2** is the hardest: requires the user to stop verifying. Not a system design problem — a trust calibration that only daily operational use can build. The empty Daily/ directory means the trust cycle hasn't started yet.
- **Value scales nonlinearly:** at 2 efforts, humans manage fine alone. At 5, organization helps. At 9+, the human cannot hold the full picture and must delegate — but only if trust exists.

## For the concurrent usage valuation
Stage 1 is table stakes. Stage 2 is where actual value unlocks. Stage 3 is where it becomes indispensable.

## Informs
- [[pulse-architecture-improvements]] — stages frame which proposed changes belong to current (Stage 1) vs earned (Stage 2/3) trust levels
- [[pulse-capacity-model]] — capacity-as-filter is a Stage 2 mechanism that assumes Stage 1 trust has been built
- [[pulse-evaluation-evolution-harness]] — trust calibration requires accuracy feedback; EEH is how Stage 1→2 transition is earned
