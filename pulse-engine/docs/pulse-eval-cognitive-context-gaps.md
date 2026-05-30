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
tags: [meta, cognitive-load, system-design, evaluation]
informs: [[pulse-capacity-model]], [[pulse-architecture-improvements]], [[pulse-priority-proposals-2026-03-25]]
---
# PULSE Evaluation — Cognitive Context Manager Gaps

PULSE is well-built for organizing 9 efforts. It's not yet built for protecting your attention from them. Context batching is genuine insight. Computed priority removes real meta-work. But the system shows you the full landscape (even folded) when what your brain needs is permission to forget about 7 efforts while you're in 1.

The gap between design sophistication and operational use (empty Daily/, unused Inbox/, scaffolded Home.md) suggests the system may need to earn its complexity through daily use before adding more.

## Six specific gaps

1. **No session contracts** — /pulse shows everything; no way to say "Work session, nothing else exists right now"
2. **No ambient closure** — system knows what's open, not what's handled; no mechanism to park an effort with confidence
3. **No switch cost in the formula** — priority is effort-centric, not attention-centric; cross-batch items get elevated without accounting for context-switching cost
4. **No "enough for now" declarations** — no lightweight way to close the worry loop on an effort without marking all items done
5. **Too many focus points surfaced at once** — instead of 2 things that matter today, shows all loops ranked by weight
6. **Depth protection vs. breadth enablement** — system optimizes for maintaining many efforts; doesn't optimize for going deep on one

## Core tension

PULSE tries to be both a comprehensive tracking system and a cognitive load reducer. These are in tension: comprehensive tracking means the human sees everything — even folded. A cognitive load reducer needs to actively hide things and give confidence they're handled.

## What would address it

- Session contracts: declare a batch+scope; everything outside is invisible, not folded
- Ambient closure: proactively report "5 of 9 efforts need no action this week, here's why"
- Switch cost in priority formula: discount cross-batch items when already loaded into a context
- "Enough for now" / parked status: genuinely off the board, not soft-suppressed
- Fewer, stronger focus points: today, 2 things matter
- Depth protection: "you've been in Work 90 min and making progress — intentionally switch?"

## Informs
- [[pulse-capacity-model]] — the six gaps frame what a capacity-aware Surface filter must actively hide vs show
- [[pulse-architecture-improvements]] — session contracts, parked status, and switch cost are concrete candidate additions
- [[pulse-priority-proposals-2026-03-25]] — the "switch cost in the formula" gap is a direct priority-formula critique
