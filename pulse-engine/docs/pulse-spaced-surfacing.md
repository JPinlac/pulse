---
type: note
subtype: note
efforts:
  - pulse
status: active
importance: medium
created: 2026-03-30
updated: 2026-04-11
timescale: weekly
tags: [spaced-repetition, cognition, surfacing, design]
informs: [[pulse-capacity-model]], [[pulse-priority-proposals-2026-03-25]], [[pulse-architecture-improvements]]
---

# Spaced Surfacing

PULSE's effort rotation isn't fragmentation — it's algorithmically optimal spacing. Context switching across efforts implements spaced repetition at life scale.

## The Insight

When you rotate through work → pulse → maintenance → learning → practice, each effort gets natural interleaving. Recency decay *is* the forgetting curve. Returning to an effort after days away forces retrieval — the strongest driver of consolidation. The system doesn't fight spaced repetition; it accidentally implements it.

The "Jack of All Trades" reframe: breadth isn't dilution, it's the spacing interval. Someone deep in one effort for weeks gets fluency but not durability. Someone juggling efforts with managed rotation gets retrieval practice on every re-entry.

## Spaced Surfacing as Intentional Mechanism

Beyond accidental spacing, PULSE could intentionally surface dormant efforts for lightweight re-engagement — not to create tasks, but to keep the possibility and opportunity field open.

**Use case**: a side project is waiting on an external consult (e.g. a legal review). No actionable work right now. But the effort has 11 open loops, momentum building, developments accumulating in the world. A periodic nudge — "what's changed in this project's landscape since you last looked?" — keeps pattern-matching active without creating false urgency.

**Modes of spaced surfacing**:
- **Recall nudge**: "What's the current state of [effort]?" — forces retrieval, surfaces what's changed
- **Daydreaming prompt**: "Any new connections between [effort] and what you're working on now?" — cross-pollination, keeps opportunity field open
- **Signal scan**: "Anything happening externally that affects [effort]?" — the listening check, but for dormant efforts

## Relationship to Existing Mechanisms

- **Resurfacing** (timescale-based) already nudges stale Notes — but it's item-level, not effort-level, and it's about staleness, not intentional spacing
- **Listening check** (external input staleness) catches when active efforts lack outside perspective — but skips dormant efforts (open_loops == 0 filter)
- **Spaced surfacing** would be a third layer: effort-level, dormancy-aware, optimized for retrieval rather than urgency

## Commitment Signal, Not Obligation

Responding to a spaced surfacing nudge is itself signal — it means the effort has marathon-level staying power. Ignoring it is equally valid data: the effort may be hibernating or genuinely done. The system should track response patterns, not enforce engagement.

Things are allowed to fall. The mentally tough part isn't dropping something — it's picking up the thread again after a long surfacing gap. A long-dormant skill — a language you were learning, say — is the canonical example: the re-entry cost isn't just "where was I" but the emotional weight of knowing how much ground was lost. Spaced surfacing could lower that re-entry cost by keeping the thread warm enough that returning doesn't feel like starting over.

**Design implication**: the nudge cadence should adapt based on response. Engaged → maintain cadence. Ignored → widen interval (not eliminate). Repeatedly ignored → let it go dormant naturally. The system mirrors what the user actually commits to, not what they think they should commit to.

## Design Questions

- What's the right cadence? Probably effort-specific — a project waiting on an external dependency might need weekly; a fully dormant hobby might need monthly
- Should this be a /pulse feature or a separate nudge mechanism?
- How to distinguish from noise? The nudge should feel like an invitation, not a task
- In pulse-cli graph model: dormant nodes with high connectivity (many edges) are prime candidates — the graph structure could identify which dormant efforts have the richest retrieval potential

## Cognitive Science Grounding

- Spaced repetition (Ebbinghaus): optimal retention from distributed practice
- Interleaving effect: mixing domains during practice improves transfer
- Incubation effect: stepping away from a problem allows unconscious processing — "daydreaming" about dormant efforts may yield insights that focused work wouldn't
- The psypost ChatGPT study (2026) found retention drops without re-engagement — spaced surfacing is the re-engagement mechanism for efforts where building isn't happening yet

## Informs
- [[pulse-capacity-model]] — dormant efforts and retrieval cost shape how the capacity filter handles re-entry
- [[pulse-priority-proposals-2026-03-25]] — spaced surfacing is a candidate mechanism for the priority/resurfacing layer
- [[pulse-architecture-improvements]] — effort-level surfacing (vs item-level resurfacing) is a structural addition
