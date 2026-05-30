---
type: note
subtype: reference
efforts: [pulse]
status: active
context_group: Projects
created: 2026-03-21
updated: 2026-04-11
effort_level: low
timescale: null
tags: [meta, system-design, theory, academic, references]
related: [pulse-context-pipeline, pulse-cc-channels-phase2]
informs: [[pulse-graph-architecture]], [[pulse-mao-multi-agent-orchestration]], [[pulse-architecture-improvements]]
---
# PULSE — Academic & Theoretical References

Background literature relevant to the context processing pipeline, trajectory mapping, and multi-layered team synchronicity model.

## Directly Relevant

### Nonaka & Takeuchi — SECI Model (1995)
*The Knowledge-Creating Company*
Tacit-to-explicit knowledge spiral. Knowledge transforms as it moves between individuals, teams, and organizations. Maps onto PULSE's layered context (personal → relationship → small team → company). Gap: models knowledge states, not knowledge vectors/trajectories.

### Weick — Sensemaking Theory (1995)
*Sensemaking in Organizations*
Organizational understanding is enacted, not retrieved — people create meaning through role-shaped engagement. Closest to PULSE's "roles as context in action" and pre-scaffolding concept. Gap: retrospective (sensemaking after the fact); PULSE describes prospective sensemaking — trajectory, not just interpretation.

### Hutchins — Distributed Cognition (1995)
*Cognition in the Wild*
Cognition spread across people, tools, and artifacts. A team thinks collectively through instruments and communication. The Discord + questions-to-ask screen is a distributed cognition system with AI as cognitive artifact. Hutchins would recognize it immediately.

### Wegner — Transactive Memory Systems (1987)
Groups develop shared knowledge of who knows what. The system is the index of knowing, not the knowledge itself. Effort Maps function like formalized transactive memory, but also encode trajectory and priority — not just "where does this knowledge live."

### Engeström — Activity Theory / Expansive Learning
Models human activity as mediated by tools, rules, community, and division of labor simultaneously. "Expansive learning" — the activity system transforms through contradictions — resonates with trajectory concept. Closest to the multi-layered dynamic view. Gap: research framework, not system design.

## The Gap

No existing work unifies:
1. **Layered context** (personal / relational / team / org)
2. **Trajectory** (forward-looking projection from role-context)
3. **Real-time synthesis** (AI integrating across participants' contexts simultaneously)

Existing work is typically retrospective, static-layered, and descriptive. PULSE Phase 2 is prospective, dynamic, and prescriptive — describing the mechanism, not just the phenomenon.

## Priority Reading
- Nonaka & Takeuchi — will sharpen vocabulary for articulating what PULSE Phase 2 does
- Hutchins — the distributed cognition frame is the most natural theoretical home

## Informs
- [[pulse-graph-architecture]] — distributed cognition and transactive memory provide formal grounding for the graph model
- [[pulse-mao-multi-agent-orchestration]] — SECI and activity theory inform multi-party orchestration patterns
- [[pulse-architecture-improvements]] — the layered/trajectory/real-time gap frames which architecture changes are theoretically novel
