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
tags: [meta, system-design, theory, ai, context-management, trajectory]
related: [pulse-context-pipeline, pulse-cc-channels-phase2, pulse-academic-references]
informs: [[pulse-graph-architecture]], [[pulse-mao-multi-agent-orchestration]], [[pulse-architecture-improvements]]
---
# PULSE — AI Context Management Theory

How AI systems handle context — and where PULSE diverges from or extends existing approaches.

## Context Window as Cognitive Bottleneck

The transformer attention mechanism is selective context weighting — deciding what matters given everything visible. PULSE's priority formula does the same thing for human cognitive bandwidth: weighted selection of what enters awareness. The parallel isn't metaphorical. Both systems face the same fundamental constraint: finite attention over unbounded context.

The difference: transformer attention is learned and opaque. PULSE's weighting is explicit, inspectable, and human-correctable (calibration log). This is a design choice — trust requires transparency (Stage 1 of the three-stage model).

## RAG vs. Pre-Scaffolded Reception

Retrieval-Augmented Generation (RAG) retrieves context based on **similarity** — query hits a vector store, nearest chunks come back. It answers: "what's relevant to this input?"

PULSE's pre-scaffolding retrieves context based on **role and trajectory** — the effort Map loads before input arrives, shaping reception. It answers: "given who I am and where this effort is heading, how should I receive this?"

RAG is reactive. Pre-scaffolding is anticipatory. RAG doesn't know what you're trying to do; it just finds similar text. PULSE knows the Map.

## Agent Memory Architectures

**MemGPT / Letta** — virtual context management for LLM agents. Pages memory in and out of the context window like an OS manages RAM. Solves the technical constraint (finite context) but not the semantic one (what *should* the agent remember given the trajectory?).

**LangGraph / LangChain memory** — conversation buffers, summary memory, entity memory. Tracks what was said. Doesn't model where the conversation is going or what the user's broader effort landscape looks like.

**PULSE's Maps and Notes** — human-readable, human-editable persistent memory that encodes not just facts but trajectory, priority, and open loops. The agent doesn't just remember — it knows what matters and why. And the human can inspect and correct the agent's understanding. This is the trust mechanism that agent memory systems lack.

## Conversation Trajectory

**Dialogue state tracking** (DST) in task-oriented dialogue systems tracks slots and intents — "the user wants to book a flight on Tuesday." It models conversation as progressing toward a known goal structure.

PULSE's trajectory concept is broader: the conversation isn't progressing toward a fixed goal, it's **generating new context** that reshapes the effort landscape. A single insight in a meeting can reframe an entire effort. The trajectory isn't a path to a destination — it's a vector that updates as context arrives.

This is closer to **open-domain dialogue** research, but with the crucial addition of the effort Map providing directional scaffolding. Not "where is this conversation going?" but "what does this conversation mean for where this effort is going?"

## Multi-Agent Orchestration

**CrewAI, AutoGen, Microsoft Magentic-One** — multiple AI agents with defined roles coordinating on tasks. Each agent has a specialty; a manager routes work.

Phase 2 CC Channels extends this: AI agents and humans are both participants in the same channel, each with role-shaped context. The orchestration isn't agent-to-agent — it's agent-to-human-to-agent, with the channel as the shared surface. No manager routing work. Instead, the effort Map provides the shared context and the "questions to ask" display is the emergent coordination layer.

## Cognitive Architectures

**ACT-R, SOAR, LIDA** — computational models of human cognition. They model memory retrieval, attention, goal management, and learning as interacting subsystems.

PULSE shares structural DNA: Maps (declarative memory), priority weights (attention), effort tracking (goal management), calibration (learning). But the purpose diverges — cognitive architectures are descriptive (how does cognition work?). PULSE is prescriptive (how should a system augment cognition?). The insight from this lineage: PULSE isn't a task manager. It's a partial cognitive architecture that runs alongside the human's, handling the parts that don't require consciousness.

## PKM Systems as Precursors

**Zettelkasten** (Luhmann) — atomic notes with emergent connections. Knowledge as a network, not a hierarchy. PULSE Notes inherit this.

**PARA** (Forte, *Building a Second Brain*) — Projects, Areas, Resources, Archive. Organizes by actionability. PULSE's efforts/Maps are a dynamic version: PARA categorizes, PULSE trajectories project forward.

**The gap all PKM systems share:** they are passive. The human must decide what to retrieve, when to review, what connects. PULSE's agent layer makes the system active — it surfaces, prioritizes, and scaffolds without being asked. PKM + agency = what PULSE is becoming.

## The Synthesis PULSE Provides

| System | Knows what was said | Knows what matters | Knows where it's going | Multi-party | Human-inspectable |
|--------|---|---|---|---|---|
| RAG | Yes | No | No | No | Partially |
| Agent memory (MemGPT) | Yes | Partially | No | No | No |
| Dialogue state tracking | Yes | Yes (slots) | Fixed goals | No | Yes |
| Multi-agent (CrewAI) | Per-agent | Per-agent | Per-task | Agent-only | No |
| PKM (PARA/Zettelkasten) | Yes | User-decided | No | No | Yes |
| **PULSE** | Yes | Yes (weights) | Yes (trajectory) | Humans + AI | Yes (Maps) |

## Informs
- [[pulse-graph-architecture]] — pre-scaffolded reception and trajectory-aware memory are what the graph architecture operationalizes
- [[pulse-mao-multi-agent-orchestration]] — the agent-to-human-to-agent orchestration pattern shapes multi-agent design
- [[pulse-architecture-improvements]] — the synthesis table frames what PULSE uniquely provides vs RAG/agent-memory/PKM precedents
