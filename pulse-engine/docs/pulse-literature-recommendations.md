---
title: "PULSE Literature Recommendations"
type: note
subtype: reference
effort: pulse
efforts: [pulse]
status: active
created: 2026-03-29
updated: 2026-04-11
informs: [[pulse-graph-architecture]], [[pulse-org-cascade-engine]], [[pulse-architecture-improvements]]
---

# PULSE Literature Recommendations

Organized by PULSE concept, not academic field. Tiered: **Essential** (read first, directly maps to what you've built), **Deep Dive** (formal grounding when you want to go rigorous), **Horizon** (speculative connections, future directions).

## 1. The Cascade Engine — Spreading Activation & Signal Propagation

What you built: weighted edges, signal attenuation with damping, activation thresholds, hot paths.

### Essential
- **Collins & Loftus (1975)** — "A Spreading-Activation Theory of Semantic Processing." *Psychological Review.* The original. Your cascade engine is this model with an LLM enrichment layer grafted onto the high-signal paths. Reading this will feel like reading a description of your own code.
- **Pattie Maes (1989)** — "How To Do the Right Thing." *Connection Science.* Behavior-based AI using activation networks for action selection. Weighted links, decay, threshold-based firing. Her "behavior network" is structurally isomorphic to your cascade engine — but she was selecting robot actions, you're propagating context. Same math, different domain.

### Deep Dive
- **Anderson (1983)** — *The Architecture of Cognition.* ACT* theory. Full cognitive architecture built on spreading activation. The activation equations (base-level activation + associative strength + context) map almost 1:1 to your `compute_signal(source_importance, edge_weight, hop, damping)`.
- **Shuman et al. (2013)** — "The Emerging Field of Signal Processing on Graphs." *IEEE Signal Processing Magazine.* Graph signal processing formalizes exactly what your cascade does: signals propagating on graph structures, filtered by topology. Graph Fourier transforms, spectral analysis of cascade dynamics. This would let you analyze *why* certain cascades propagate far and others die.

### Horizon
- **March (1991)** — "Exploration and Exploitation in Organizational Learning." *Organization Science.* The exploration/exploitation tradeoff maps to your dual threshold: mechanical cascades exploit known structure (cheap, deterministic), LLM enrichment explores new meaning (expensive, creative). March's math describes the optimal balance.

## 2. Stigmergy — Activation Counts as Coordination

What you built: activation counts accumulate on edges through use, shaping future traversal without explicit coordination.

### Essential
- **Heylighen (2016)** — "Stigmergy as a Universal Coordination Mechanism." *Cognitive Systems Research.* The modern synthesis. Argues stigmergy is the general mechanism behind wikis, version control, recommendation systems, markets. Your activation-count-based emergence detection is a textbook case. He distinguishes *quantitative stigmergy* (pheromone strength = your activation count) from *qualitative stigmergy* (artifact type = your edge type). You have both.
- **Parunak (2006)** — "A Survey of Environments and Mechanisms for Human-Human Stigmergy." *Environments for Multi-Agent Systems.* Specifically about digital stigmergy in human systems, not just insects. Directly relevant to PULSE-Org where the graph is the shared environment humans coordinate through.

### Deep Dive
- **Theraulaz & Bonabeau (1999)** — "A Brief History of Stigmergy." *Artificial Life.* Historical context from Grassé's original termite observations through computational models. The formalization of how local trace-leaving produces global structure is the formal version of "hot paths across org boundaries = latent initiative."

## 3. Distributed Cognition & Extended Mind

What you built: cognition distributed across human + LLM + graph + vault. The system thinks, not just the person.

### Essential
- **Hutchins (1995)** — *Cognition in the Wild.* MIT Press. Studies navigation on a Navy ship as a distributed cognitive system. The "system" remembers, computes, and decides — no single person holds the full picture. Replace "ship's bridge" with "PULSE graph" and this describes your architecture. The chapter on how tools carry computational state across time is especially relevant to how your graph persists and propagates context.
- **Clark & Chalmers (1998)** — "The Extended Mind." *Analysis.* The philosophical argument that cognitive processes extend into tools and environment. Your design commits to this: the graph isn't a record of cognition, it's part of the cognitive process itself. Cascades are thinking happening in the graph, not thinking recorded in the graph.

### Deep Dive
- **Hollan, Hutchins & Kirsh (2000)** — "Distributed Cognition: Toward a New Foundation for Human-Computer Interaction Research." *ACM ToCHI.* Formalizes the analytical framework. Useful for articulating what PULSE-Org is doing when you need to explain it to others.

## 4. Category Theory — The Formal Skeleton

What you built: enriched categories (weighted edges), functorial projections (per-node views), sheaf-like consistency.

### Essential
- **Fong & Spivak (2019)** — *An Invitation to Applied Category Theory: Seven Sketches in Compositionality.* Cambridge University Press. The most accessible entry. Chapter 3 (databases as categories) maps directly to your graph model. Chapter 4 (enriched categories) formalizes your weighted edges. Chapter 7 (sheaves) formalizes your progressive consistency. Written for practitioners, not pure mathematicians. **Start here.**
- **Ehresmann & Vanbremeersch (2007)** — *Memory Evolutive Systems: Hierarchy, Emergence, Cognition.* Elsevier. **This is the single most relevant work to PULSE as a whole.** They use category theory to model complex systems with memory, emergence, and hierarchical organization. They use colimits for binding (≈ your cascade aggregation), functors for observation levels (≈ your per-node projection), and natural transformations for system evolution (≈ your cascade-of-cascades). They were modeling biological/cognitive systems. You're building one. This book will feel like finding the mathematical version of your own architecture.

### Deep Dive
- **Spivak (2014)** — *Category Theory for the Sciences.* MIT Press. Databases as functors, schema migration as functor composition, queries as natural transformations. Your graph-to-vault projection is a functor. Schema evolution (field promotion) is functorial data migration. More formal than Fong & Spivak but comprehensive.
- **Robinson (2014)** — *Topological Signal Processing.* Springer. Applied sheaf theory for sensor networks and distributed data fusion. Chapter on detecting global inconsistency from local measurements directly maps to your Reconciliation Agent problem: each node has local data, sheaf theory tells you when the local pieces don't fit together globally.
- **Hansen & Ghrist (2019)** — "Toward a Spectral Theory of Cellular Sheaves." *Journal of Applied and Computational Topology.* Sheaf Laplacians — a way to compute "how inconsistent is the distributed data?" as a spectral property. If you ever need a formal measure of org-wide coherence, this is the tool.

### Horizon
- **Goguen (1992)** — "Sheaf Semantics for Concurrent Interacting Objects." *Mathematical Structures in Computer Science.* Sheaves for modeling concurrent distributed systems. Connects the categorical formalism directly to the distributed systems concerns.
- **Patterson (2017)** — "Knowledge Representation in Bicategories of Relations." Knowledge graphs through a categorical lens. Relevant if you want to formalize the relationship between the graph overlay and the embedding space as different categorical representations of the same knowledge.

## 5. CRDTs, CALM, and Monotonicity

What you built: append-only activation arrays (G-Sets), grow-only counters (G-Counters), threshold-gated non-monotonic operations.

### Essential
- **Shapiro et al. (2011)** — "Conflict-free Replicated Data Types." *SSS 2011.* The foundational CRDT paper. Your activation counts and append-only arrays are CRDTs. Reading this will show you that your data structures have formal convergence guarantees you didn't know you were getting.
- **Alvaro et al. (2011)** — "Consistency Analysis in Bloom: a CALM and Collected Approach." *CIDR.* The CALM theorem: monotonic programs are eventually consistent without coordination. Your mechanical cascade layer is monotonic. Your LLM enrichment layer is non-monotonic. The threshold between them is the CALM boundary. This paper gives you the formal justification for why the dual threshold works.

### Deep Dive
- **Kleppmann (2017)** — *Designing Data-Intensive Applications.* O'Reilly. The practical bible. Chapters on event sourcing, stream processing, consistency models, and distributed data. Your architecture's event-sourced metadata, CQRS-style graph-to-vault projection, and progressive consistency all have thorough treatment here.
- **Kleppmann et al. (2019)** — "Local-First Software: You Own Your Data, in Spite of the Cloud." *Onward! 2019.* The local-first manifesto. PULSE-Org's architecture (fully functional offline, sync on reconnect, CRDTs for conflict resolution) is a local-first system. This paper articulates the design principles you've been following intuitively.

### Horizon
- **Hellerstein (2010)** — "The Declarative Imperative." *SIGMOD.* The broader argument that monotonicity is the key to coordination-free distributed computing. Frames the CALM insight in a programming language context (Bloom/Dedalus). Relevant if you ever want to build a declarative query language for the org graph.

## 6. Small-World Networks & Emergent Graph Structure

What you built: activation-weighted edges that create navigable shortcuts through use.

### Essential
- **Kleinberg (2000)** — "The Small-World Phenomenon: An Algorithmic Perspective." *STOC.* Navigable small-world networks. Proves that a specific distribution of long-range links makes graphs efficiently searchable. Your activation counts are building exactly this distribution — frequently co-activated paths become the long-range links. The graph learns to be navigable.
- **Watts & Strogatz (1998)** — "Collective Dynamics of 'Small-World' Networks." *Nature.* The original small-world paper. Short path lengths + high clustering. Your effort-local edges provide clustering; cross-effort cascade activations provide shortcuts.

### Deep Dive
- **Barabási & Albert (1999)** — "Emergence of Scaling in Random Networks." *Science.* Preferential attachment — popular nodes get more popular. Your activation counts create preferential attachment: high-activation edges carry more signal, which triggers more cascades, which increments activation further. Rich-get-richer dynamics in the graph topology.

## 7. Sensemaking & Organizational Knowledge

What you built: emergence through use, not retrieval of pre-existing knowledge.

### Essential
- **Weick (1995)** — *Sensemaking in Organizations.* Sage. The foundational text. Seven properties of sensemaking, all present in PULSE: retrospective (cascade outcomes enrich upstream), social (multi-node), ongoing (continuous capture), driven by plausibility not accuracy (weighted edges, not binary truth). Your system operationalizes Weick.
- **Nonaka & Takeuchi (1995)** — *The Knowledge-Creating Company.* Oxford University Press. The SECI model: Socialization → Externalization → Combination → Internalization. Map to PULSE-Org: capture is externalization, membrane promotion is combination, per-node projection is internalization, cascade-mediated cross-node effects are socialization. The spiral model of knowledge creation matches your cascade-of-cascades across layers.

### Deep Dive
- **Weick (1993)** — "The Collapse of Sensemaking in Organizations: The Mann Gulch Disaster." *Administrative Science Quarterly.* Case study of what happens when distributed sensemaking fails. Useful framing for what PULSE-Org is designed to prevent: information existing in the system but not reaching the node that needs it.

## 8. Sati — Self-Observation, Cybernetics, Enactivism

What you built: a system that watches its own categorization, detects reification, notices emergence.

### Essential
- **Varela, Thompson & Rosch (1991)** — *The Embodied Mind: Cognitive Science and Human Experience.* MIT Press. The enactivist manifesto. Cognition as enacted through interaction, not computed from representations. Your anti-discretization principle is enactivism applied to system design. The book's integration of Buddhist mindfulness practice with cognitive science connects directly to naming the awareness layer "Sati."
- **Bateson (1972)** — *Steps to an Ecology of Mind.* University of Chicago Press. Levels of learning: Learning I (new responses), Learning II (learning to learn), Learning III (change in the process of Learning II). Sati operates at Learning III — it watches how the system categorizes and flags when categorization itself is becoming rigid. The "double bind" concept maps to your category violations.

### Deep Dive
- **Von Foerster (2003)** — *Understanding Understanding: Essays on Cybernetics and Cognition.* Springer. Second-order cybernetics — systems that include the observer. Sati makes PULSE a second-order system: it doesn't just process information, it observes its own processing. Von Foerster's "eigenvalues of cognitive operations" (stable self-reinforcing patterns) are what Sati's reification detection watches for.
- **Varela (1996)** — "Neurophenomenology: A Methodological Remedy for the Hard Problem." *Journal of Consciousness Studies.* Bridging first-person and third-person methods. Relevant to the deeper question of what it means for a human-LLM pair to have "awareness" of its own cognitive patterns.

### Horizon
- **Depraz, Varela & Vermersch (2003)** — *On Becoming Aware: A Pragmatics of Experiencing.* John Benjamins. A method for studying emergence of awareness in real-time. The "basic gesture" (suspend habitual patterns → redirect attention → let-come) maps to what Sati does at the system level: suspend categorization → attend to what doesn't fit → let emergence arrive.

## 9. The Whole System — Complex Adaptive Systems

What you built: a self-organizing system with local rules producing global structure.

### Essential
- **Simon (1962)** — "The Architecture of Complexity." *Proceedings of the American Philosophical Society.* Near-decomposability: complex systems are hierarchical, and the layers interact weakly. Your L0/L1+ separation with membrane is near-decomposable architecture. The formal argument for why this structure is evolutionarily stable.
- **Holland (1995)** — *Hidden Order: How Adaptation Builds Complexity.* Addison-Wesley. Tags, internal models, building blocks. Your edge types are tags, the cascade engine is an internal model, efforts are building blocks. Holland's framework for complex adaptive systems maps cleanly to PULSE.

### Deep Dive
- **Kauffman (1993)** — *The Origins of Order.* Oxford University Press. Self-organization in biological systems. Boolean networks, fitness landscapes, edge of chaos. The cascade threshold parameters (0.1, 0.4) determine whether your system is subcritical (cascades die too fast), critical (cascades propagate usefully), or supercritical (cascades explode). Kauffman's framework gives you the language for tuning this.

### Horizon
- **Mitchell (2009)** — *Complexity: A Guided Tour.* Oxford University Press. Accessible tour across the field. Good for seeing PULSE in the context of the broader complexity science program.

## 10. Modern Graph + LLM Systems

What exists now in adjacent territory.

- **Edge et al. (2024)** — "From Local to Global: A Graph RAG Approach to Query-Focused Summarization." Microsoft Research. GraphRAG. Static graph for retrieval. No cascades, no activation tracking, no stigmergy. Your system is what GraphRAG would be if the graph were alive.
- **Lewis et al. (2020)** — "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." The original RAG paper. Foundation for understanding what PULSE-Org's retrieval layer extends beyond.

## Reading Order

If starting from scratch, this sequence builds the conceptual stack:

1. **Fong & Spivak** (category theory foundations, accessible)
2. **Collins & Loftus** (spreading activation — recognize your cascade engine)
3. **Heylighen** (stigmergy — recognize your activation counts)
4. **Shapiro et al. + Alvaro et al.** (CRDTs + CALM — recognize your monotonicity boundary)
5. **Hutchins** (distributed cognition — recognize the whole system)
6. **Ehresmann & Vanbremeersch** (the categorical synthesis — see the formal skeleton of everything)
7. **Varela, Thompson & Rosch** (enactivism + Sati — the philosophical grounding)

## Informs
- [[pulse-graph-architecture]] — category theory, CRDTs, and small-world networks are formal grounding for graph structure and consistency
- [[pulse-org-cascade-engine]] — spreading activation, stigmergy, and complex adaptive systems are the theoretical stack behind the cascade engine
- [[pulse-architecture-improvements]] — distributed cognition and sensemaking frame what the architecture is doing at a systems level
