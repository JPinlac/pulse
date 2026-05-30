---
type: system-map
effort: pulse
context_batch: System
priority_weight: 0.7
base_priority: 7
last_active: 2026-05-30
open_loops: 0
related_efforts: []
purpose: The PULSE engine itself — meta-effort for designing, building, and refining the system
aliases: [assistant, pulse-engine, meta]
tags: [meta, system]
---

# Pulse

The meta-effort: PULSE's own design and development. Work *on* the system rather than *with* it — formula changes, skill authoring, architecture, depersonalization, and the theory that informs them.

> base_priority is held at 7 deliberately: the engine that routes attention should not outrank the livelihood and life efforts it serves.

## Active Threads

*None currently — populated as engine work is captured.*

```dataview
LIST FROM "Notes" WHERE contains(efforts, this.effort) SORT updated DESC
```

### Theory & Reference Docs

Perennial reference in `docs/` that informs this effort (excluded from loop counting):

- [[pulse-calc-design]] — pulse-calc.py design: deterministic compute extracted from LLM reasoning
- [[prioritization-pulse-archive]] — pre-script prioritization algorithm, preserved for calibration archaeology
- [[pulse-ai-context-theory]] — context as the scarce resource PULSE manages
- [[pulse-context-pipeline]] — how context moves through capture → triage → surface
- [[pulse-design-inspirations]] — sources and analogies shaping the design
- [[pulse-three-stage-development-model]] — overview → scope reduction → attention protection
- [[pulse-mental-pliancy]] — provisional orientation; reification as the failure mode
- [[pulse-uncertainty-as-signal]] — surfacing uncertainty rather than hiding it
- [[pulse-predictions-uncertainty-and-pliancy]] — prediction, uncertainty, and staying pliant
- [[pulse-intention-alignment-vectors]] — aligning system behavior with actual intention
- [[pulse-eval-cognitive-context-gaps]] — evaluation gaps in cognitive context handling
- [[pulse-spaced-surfacing]] — effort rotation as life-scale spaced repetition
- [[pulse-sati-meta-agent]] — Sati as the meta-agent watching for reification
- [[pulse-sati-batched-sensitivity]] — batched emergence sensitivity
- [[pulse-literature-recommendations]] — reading that informs the design
- [[pulse-academic-references]] — academic grounding
- [[ai-orchestration-control-qa-reference]] — control theory + QA/SRE vocabulary for LLM systems
- [[working-reference-template]] — reusable prompt for generating domain working-references
- [[harness-model-changes]] — observational log of Claude Code harness behavior shifts

## Minor Actions

*None.*
