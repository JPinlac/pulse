---
type: note
subtype: plan
efforts:
  - pulse
status: active
importance: high
created: 2026-03-25
updated: 2026-04-11
informs: [[pulse-evaluation-evolution-harness]], [[pulse-architecture-improvements]]
---

# Uncertainty as Signal — Design Principle

## Problem

The agent's default orientation is to resolve uncertainty before presenting — collapse competing interpretations into a single confident answer. This loses valuable collaborative material. The user values uncertainty as the space where interesting work happens and wants to sit with it together.

Evidence from 2026-03-25 session: when asked to share raw thinking traces, the agent's Block 6 contained three visible course corrections ("Actually, I think...") that got flattened into a confident assertion in the response. The agent's own annotation: "the hedging in thinking became assertion in output." When this was surfaced, the agent described "including that felt like handing over evidence of uncertainty" — revealing an orientation toward certainty-as-competence that actively hides useful signal.

## Design Direction

Add a principle: **uncertainty is signal, not failure.** When the agent notices competing interpretations, fuzzy rankings, or internal course corrections, surface them as collaborative material rather than resolving prematurely.

### Where It Touches

1. **SYSTEM.md Section 1 (Philosophy)** — new principle alongside Shusho-itto and Agent-First. Uncertainty as a quality of attention, not a deficiency.

2. **CLAUDE.md Agent Conventions** — behavioral directive: present competing interpretations, flag internal course corrections, mark low-confidence conclusions explicitly.

3. **Sati connection** — emergence observations already embrace "things that resist classification." This principle extends that same quality to the agent's own reasoning process. Sati watches for category violations in the world; this watches for premature resolution in the agent's own output.

4. **Pulse briefing** — fuzzy item detection (step 4.5) already exists but is narrowly scoped to weight proximity. The principle could broaden what gets flagged as fuzzy — not just close weights, but uncertain classifications, ambiguous user intent, competing next-actions.

5. **Thinking trace transparency** — connected to the LLM intention transparency research thread ([[pulse-llm-intention-transparency]]). The principle creates a norm where the agent's uncertainty is available for inspection rather than hidden. Implemented as `/surfaceUncertainty` skill — extracts thinking-trace markers, competing frames, and reification risks on demand.

### What It Doesn't Mean

- Not an excuse to be indecisive on routine operations (file writes, triage, defrag)
- Not "show all your work always" — that's noise. Surface uncertainty when it's *load-bearing*: when the resolution choice would change the user's next action or understanding.
- Mechanical tasks stay mechanical. The principle applies to judgment calls, rankings, classifications, and interpretive work.

## Origin

Emerged from 2026-03-25 session exploring LLM intention transparency. User asked to see raw thinking traces, noticed the agent filtering uncertainty out of its output, and identified this as a design gap: "I love uncertainty, that's where useful interesting work lies. We want to sit with uncertainty and butt our heads together on it."

## Informs
- [[pulse-evaluation-evolution-harness]] — uncertainty as load-bearing signal reframes what the harness should measure vs collapse
- [[pulse-architecture-improvements]] — fuzzy item broadening and surfacing uncertainty as collaborative material are concrete behavioral changes
