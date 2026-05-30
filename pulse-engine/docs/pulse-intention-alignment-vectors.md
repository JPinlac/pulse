---
type: note
subtype: note
effort: pulse
efforts: [pulse]
status: active
importance: medium
created: 2026-03-25
updated: 2026-04-11
timescale: monthly
related: [pulse-evaluation-evolution-harness, pulse-design-inspirations]
informs: [[pulse-evaluation-evolution-harness]], [[pulse-architecture-improvements]], [[pulse-priority-proposals-2026-03-25]]
tags: [evaluation, intention, alignment, dharma-architecture]
---

# Intention & Alignment Vectors in Evaluation

## Core Insight

Evaluation quality gates shouldn't be solely content-based. Two orthogonal axes determine correct execution:
1. **Context** — the situational awareness the system has (where you are)
2. **Alignment vector (intention)** — the directional aim behind the action (where you're going)

Content evaluation alone measures accuracy — did the output match what was expected? But accuracy and alignment are orthogonal. A system can be perfectly accurate and completely misaligned — flawlessly prioritizing items within an effort that shouldn't exist, creating the illusion of coherence while walking confidently in the wrong direction.

PULSE currently has a sophisticated context model (Maps, Notes, batches, weights). It has almost no intention model. The system knows *what* is active and *how much* it matters, but not *why* or *toward what end*.

## Scales as Alignment Functions (Ksetras)

Each level of the PULSE hierarchy is not just a larger container — it's a larger **ksetra** (field of action) where alignment is tested at a different scale:

- **Item-level ksetra**: Is this action aligned with the effort's purpose? (Tactical alignment — are you doing the right thing within the field you're in?)
- **Effort-level ksetra**: Is this effort aligned with the batch's trajectory? (Strategic alignment — are you in the right field?)
- **Batch-level ksetra**: Is this batch aligned with the person's current life direction? (Values alignment — are you on the right battlefield?)
- **System-level ksetra**: Is PULSE itself oriented correctly as a meta-system? (Meta-alignment — is the instrument you're using to orient actually pointing north?)

Critical property: **misalignment at a higher level cannot be fixed by optimizing at a lower level.** If an effort is misaligned with life direction, perfectly prioritizing its items makes things worse — climbing the wrong mountain more efficiently. This is exactly why content-only evaluation has a ceiling — it can only see within the current ksetra, never across ksetras.

Connection to importance-as-seed: removing importance-as-hard-override was about this. A human tagging things "high" is trying to do cross-ksetra alignment manually within a system that should be computing alignment holistically. The algorithm operates across the full field; the human label operates within one.

## Friction as Diverging Alignment Vectors

Friction is not vague resistance — it is the observable effect of **diverging alignment vectors**. When the system's intention vector and the user's intention vector point in different directions, the divergence manifests as friction: commands that don't land, priorities that feel wrong, classifications that resist.

This is dukkha in the precise contemplative sense — not "suffering" but the felt sense of misalignment, unsatisfactoriness as structural signal. The current response is to treat friction as error (fix the output, retry, adjust the weight). But friction *is* the divergence — it doesn't indicate a problem, it *is* the measurable gap between two alignment vectors. The right response is to surface both vectors and make the divergence explicit.

Case study: the priority validation corrections from 2026-03-25 morning. Three "errors" that were actually symptoms of a structural misalignment (importance-as-override). Fixing the errors would have masked the signal. Sitting with the dukkha surfaced the root cause. The "propose, don't implement" pattern in the calibration system created space for this — delay as diagnostic.

## Logs as Orientation Surfaces

Session logs already contain implicit orientation vectors. Every decision trace — "I chose X over Y because Z" — reveals where the system was pointing. But it's buried in content. Making alignment explicit creates a traceable record of orientation drift over time. You could look at a week of logs and see: "the system's model of intention for this effort shifted from X to Y, but the user's actual intention stayed at X — that's why friction increased."

## Friction-Triggered Intention Surfacing

The cost question resolves toward **friction-triggered** rather than always-on. When alignment is correct, intention is self-evident from the action — logging it would be redundant overhead. It's precisely when dukkha is present that articulating intention has diagnostic value. The friction itself is the trigger for reflection, just as it is in contemplative practice.

When friction is detected, the system articulates:
- "I believe the intention behind this command is X"
- "My current alignment vector is Y"
- "The friction may indicate divergence at Z"

This is a higher-order correction than "the output was wrong." It corrects the system's directional model, not just its content model.

### Implementation Direction

**Sati is the trigger mechanism.** The existing Sati overlay already watches for category violations, classification resistance, and things that don't fit existing frames — these are friction events. Sati doesn't need a new mechanism bolted on; the extension is: when Sati notices friction, also articulate the intention vector, not just the observation.

The stack:
1. **Sati** detects alignment vector divergence via its outflows (asavas) — category violations, classification resistance, unexpected results
2. **Friction-triggered intention surfacing** fires when Sati flags divergence
3. **Intention articulation** reveals the alignment divergence (intention / alignment / divergence)
4. **Calibration** (EEH) closes the accuracy loop; intention corrections close the direction loop

- **Trigger**: Sati detects alignment vector divergence. The concrete outflows (asavas) of divergence — command resistance, unexpected results, user corrections, priority validation failures, classification ambiguity — are the observable symptoms, not the friction itself. Sati watches for these asavas as indicators of the underlying divergence.
- **Output**: one-line intention summary appended to the relevant session log entry
- **Cost model**: lightweight (one-line) by default. Full articulation (3-line: intention / alignment / divergence) only when friction is strong or repeated
- **Experimental field**: `intention:` in session log entries, friction-triggered only
- **Cost evaluation needed**: measure token overhead of friction-triggered intention logging across a week of sessions to determine if it's sustainable

## Relationship to EEH

EEH and intention alignment are complementary axes of a mature evaluation system:
- **EEH**: "Did we hit the target?" → calibrates the instrument (accuracy)
- **Intention alignment**: "Are we aimed at the right target?" → calibrates the orientation (direction)

Future possibility: track an **Alignment Accuracy Rate** alongside PAR — how often the system's model of intention matched the user's actual intention, measured through friction events and corrections.

This is also the core structure of the AI alignment problem at industry scale. Capability without alignment is the universal risk. PULSE encounters it at the personal system level — a concrete test bed for the general problem.

## Informs
- [[pulse-evaluation-evolution-harness]] — intention alignment is the direction axis complementing EEH's accuracy axis
- [[pulse-architecture-improvements]] — ksetras frame system-level alignment as a design constraint, not just a runtime check
- [[pulse-priority-proposals-2026-03-25]] — the importance-as-seed validation case is the canonical example of diverging alignment vectors
