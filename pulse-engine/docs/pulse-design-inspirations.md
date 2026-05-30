---
type: note
subtype: reference
efforts: [pulse]
status: active
created: 2026-03-24
updated: 2026-04-11
effort_level: null
timescale: quarterly
due: null
importance: medium
depends: []
related: [pulse-architecture-improvements]
informs: [[pulse-architecture-improvements]]
context_group: null
tags: [meta, design, philosophy]
---
# Design Inspirations

Principles, metaphors, and anti-patterns that shape how PULSE is designed. Not a task list — a living reference for design decisions.

## Metaphors That Work vs Metaphors That Constrain

Biological and contemplative metaphors are useful for initial design intuition but become traps when the system starts being designed *toward the metaphor* instead of toward the actual function.

**Test**: Does the metaphor describe *what the system does* (functional) or *what it's like* (analogical)?

- **Functional metaphors persist** — they name a quality or process that maps directly to a computational operation. They survive because removing the metaphor would lose meaning.
  - *Sati* — names a quality of attention (noticing without forcing into frames). The system literally does this: detect novelty without classifying it.
  - *Shusho-itto* — practice and realization are one act. The system literally does this: capture, reflection, and action are not a pipeline but a single movement.

- **Analogical metaphors constrain** — they name a biological structure and invite designing toward the structure's properties rather than the needed function. They're useful scaffolding but should be retired once the function is clear.
  - *DMN (Default Mode Network)* — useful for intuition ("the brain's background simulator") but pulls design toward neuroscience. The actual function is: **predictive modeling with divergence tracking**. Name the process, not the brain part.
  - *REM sleep* — useful for intuition ("consolidation during rest") but the actual function is: **cross-session pattern synthesis with staleness pruning**. Once you have that description, "REM" adds nothing and risks importing assumptions about sleep cycles, timing, passivity.

**Guideline**: When a biological metaphor has served its purpose as scaffolding, rename the system component to describe its process. Keep the metaphor in design notes (this file) for historical context, but don't let it appear in CLAUDE.md or skill definitions where it would shape agent behavior.

## External Content as Design Catalyst

External technical content (blog posts, papers, product launches) is most valuable when *composted* rather than adopted. The pattern observed (2026-03-24): Anthropic's Auto Dream feature was not copied — it was metabolized into something structurally different (typed persistence layers, multi-layer consolidation, emergence awareness). The value was in the contrast ("what problem does this solve that we don't have?") more than the solution itself.

## Mundane Operations as Architecture Signals

Simple operational friction ("can I archive a note?") often reveals structural gaps that are invisible at the design level. The pattern: when a routine action requires grep or manual checking, the system is missing a first-class concept. The dependency system emerged entirely from "why is archiving hard?" — the answer was "because dependencies are implicit."

**Guideline**: When the user hits friction on a simple operation, investigate whether the friction signals a missing abstraction before building a workaround.

## Informs
- [[pulse-architecture-improvements]] — metaphor-vs-function test and "mundane operations as architecture signals" are core design heuristics for proposed changes
