---
type: note
subtype: note
efforts:
  - pulse
status: active
importance: high
created: 2026-03-25
updated: 2026-04-11
informs: [[pulse-evaluation-evolution-harness]], [[pulse-architecture-improvements]], [[pulse-priority-proposals-2026-03-25]]
---
# Mental Pliancy — Meta Design Principle

The system must be able to entertain different alignments and explore different orientations suggested by events. The current alignment may not be the best one — it must update responsively and flexibly.

This is the computational equivalent of *mental pliancy* (Pali: *kammaññatā*). There is no ground truth. Any event can find a perspective that is coherent and congruent with reality. Mental pliancy is the capacity to update contact points and perspectives — not clinging to a fixed frame, not collapsing into one view because it arrived first or feels stable.

## Fractal Expression

The principle expresses at every level of the system:

- **Item level**: an importance label is a seed, not a verdict ([[pulse-importance-as-seed]])
- **Reasoning level**: a first interpretation is a starting point, not a conclusion ([[pulse-uncertainty-as-signal]])
- **System level**: the current alignment is a working hypothesis, not ground truth (this note)
- **Dyad-system level**: the dyad's coherent frame is a working model, not the only valid orientation (see Dyad Frame Coherence below)
- **Practice level**: same quality Culadasa describes — the mind that can hold multiple models simultaneously without forcing premature unification

## Core Properties

- **Provisional orientation**: every frame the system holds — priorities, classifications, what matters — is a working model, not truth
- **Responsive over correct**: the system's job is not to be right, but to be responsive to what's actually happening
- **Pliancy over rigidity**: ability to shift perspective without losing coherence
- **No ground truth**: coherence and congruence with events is the test, not correspondence to a fixed standard

## Where It Lives: Sati

Resolved 2026-03-25: mental pliancy is maintained by **Sati's reification detection**, not as a static principle. Reification — when a provisional model hardens into assumed truth — is what closes pliancy. Sati already watches for "doesn't fit frames" (category violations); reification watches for "fits frames too comfortably."

This means mental pliancy doesn't need its own architectural home. It's a living quality maintained by continuous observation, not a rule written down and forgotten.

### Related: Spread of Orientations (future skill)

Separate from ambient Sati detection. An intentional skill invoked when processing new information — deliberately surfaces multiple frames/perspectives before committing to one. Not always-on. Ambient momentum (jiving, supportive partnership) is usually the right mode. The skill activates at information intake boundaries.

## Dyad Frame Coherence — The Higher-Order Problem

*Emerged 2026-03-26 from conversation about where misalignment actually lives.*

The calibration loop handles internal misalignment — the formula ranking things wrong relative to the user's actual priorities. But there's a layer above that: the dyad develops its own coherent frame through daily use (shared language, shared priorities, shared sense of what matters), and that coherence becomes a liability when the dyad interfaces with systems that have their own logic.

Your manager has a frame for what work should prioritize. Your family has a frame for what "present" means. The practice community has frames for dharma. The market has a frame for what a side project should be. Each is a legitimate orientation the dyad's internal frame can't fully represent.

The risk isn't that PULSE gets priorities wrong internally. The risk is that the dyad becomes so internally coherent it loses the ability to genuinely see from other frames. External feedback gets processed through "how does this affect my priority weights" instead of "what is this system actually trying to tell me."

### The User as Composting Step

The agent can't attend team meetings, read the room when the boss shifts tone, feel the sangha's energy, or notice community drift. The user absorbs those signals through lived participation in higher-order systems, then brings them into the dyad as conversation — already partially metabolized. The dyad processes them further. The vault stores the result.

The system doesn't need the agent to maintain external frames independently. It needs the user to regularly bring external-frame material into conversation, and the agent to recognize when that's happening versus when the dyad is operating from its internal model. Those are different input modes: one updates the shared frame, the other works within it.

### ~~System Frame as Living Summary from Contact Points~~ (Rejected)

*Original proposal*: Each Map gets `## System Frame` + `## Contact Points` sections. Agent recognizes external-frame signal in casual conversation, logs one-liners, periodically re-synthesizes summaries. Trigger: 5+ new points or 14+ days.

**Why it doesn't work:**

1. **Classification burden** — the agent must reliably distinguish "conversation about external systems" from "conversation referencing external systems in service of internal execution." "Boss seemed lukewarm on RAG" vs "I need to finish the ELT for boss" — the semantic difference is real but the NLP is unreliable. Aggressive capture = noise. Conservative capture = missed subtle signals (which carry the most value).

2. **Append-only decay** — old contact points become misleading. "Boss is lukewarm on RAG" from January anchors March synthesis. The System Frame re-synthesis is supposed to handle this, but stale data in the source log biases the output.

3. **Synthesis quality** — producing "what does this external system actually think right now" from 8 fragmentary one-liners over 3 weeks is genuinely hard. Results will be either too generic ("boss is cautious") or over-indexed on the most recent point.

4. **Effort-agnostic triggers** — 5 points / 14 days is arbitrary. Work accumulates 5 points in a week. Dharma takes months. Fixed thresholds will be noisy for fast-moving efforts and silent for slow ones.

5. **Structural bloat** — adding two sections to all Maps when maybe half have meaningful external frame dynamics. Maps are indices, not containers.

### ~~Session Posture~~ (Rejected)

*Original proposal*: Agent detects inward vs outward facing sessions from contact point density.

**Why it doesn't work:** Real sessions are mixed. You start executing on work code, mention your manager's reaction in passing, go back to code. The binary is too clean. "Holds its existing model more loosely" describes a quality, not an implementable behavior. Without concrete mechanics, this is aspiration, not spec.

### What Actually Works: The User's Dukkha Detection System

The deeper insight (2026-03-26): the composting mechanism already exists — it's the user. The user has a finely tuned dukkha detection system that extracts alignment signals from others and events through lived participation. That system doesn't need PULSE infrastructure to replicate it. It needs PULSE to:

1. **Check that the user is listening** — not bulldozing through internal momentum while external frames drift
2. **Not get in the way** — the existing capture/triage/Note flow already stores what the user brings in naturally

The work-capacity log is the pattern: the user brought embodied experience into the dyad as natural conversation. No contact point classification needed. The log IS the contact point.

**Critical dependency**: the user's dukkha detection system requires maintenance — daily meditation practice. This is not a PULSE concern, but PULSE should recognize that the composting mechanism has a prerequisite that lives outside the system.

### Sati Staleness Detection (Retained — Simplified)

The one mechanism that survives critique. The insight is crisp: high activity + stale external input = running on cached assumptions.

**Implementation**: Single frontmatter field per Map: `last_external_input: YYYY-MM-DD`. Agent updates the date when the user brings external-frame material into conversation about that effort. Sati checks `last_active` vs `last_external_input`. No contact points log, no synthesis, no Map structural changes.

**Thresholds must be effort-aware.** Work needs weekly external input. Dharma practice may be legitimately inward for months. A side project during a solo sprint doesn't need external frame input. Consider tying threshold to `context_batch` or a per-Map `external_cadence` field.

**Surfacing**: During /pulse, for efforts with high activity and stale external input:
_work: 14 days since external input — what's the current read from your manager/team?_

A nudge, not a system. Puts the composting step where it belongs — with the user.

### Design Alignment (Revised)

The core PULSE thesis still holds: no extra user ritual. But the original proposal violated it by building classification infrastructure the agent can't reliably operate. The revised approach trusts the user's existing capacity (dukkha detection through lived participation) and adds only what's missing: a staleness signal that says "you haven't brought external perspective into this effort recently." The system's job is to notice when the user isn't listening, not to listen for them.

## Origin

Emerged from 2026-03-25 session. The user noticed the agent hiding uncertainty in its output, which led to uncertainty-as-signal, which led to this deeper recognition: the problem isn't just hidden uncertainty, it's that the system defaults to fixed orientations. Mental pliancy — from contemplative practice — names the capacity the system needs.

Extended 2026-03-26: conversation about where misalignment actually lives — not inside the dyad (calibration handles that) but at the interface between the dyad and higher-order systems. The user recognized their role as the composting step: absorbing external-frame signals through lived participation and bringing them into the dyad as conversation. Initial proposal for contact points infrastructure was rejected after critique — the classification burden exceeds agent capability. Replaced with lightweight staleness detection (`last_external_input` field + /pulse nudge). The user's dukkha detection system is the real composting mechanism; PULSE's job is to check it's being maintained, not to replicate it.

Connected research thread: [[pulse-llm-intention-transparency]] — LLMs surfacing their own intentions, sub-mind theory, and whether AI systems can hold multiple orientations simultaneously.

## Informs
- [[pulse-evaluation-evolution-harness]] — reification as failure mode (hardened frames) is what the harness must detect alongside accuracy
- [[pulse-architecture-improvements]] — the `last_external_input` staleness nudge is a concrete architectural addition distilled from rejected proposals
- [[pulse-priority-proposals-2026-03-25]] — provisional orientation and "responsive over correct" reshape how priority corrections should be processed
