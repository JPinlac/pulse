---
name: surfaceUncertainty
description: Surface thinking-trace uncertainty — competing interpretations, course corrections, and reification signals. Invoked by Sati detection or deliberately when processing new information.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Write, Edit, Bash
srsa: Sati
---

## Surface Uncertainty

When Sati flags uncertainty, reification, or competing orientations — or when the user wants to explore what the agent is actually uncertain about — this skill extracts and presents the load-bearing uncertainties from the agent's reasoning process.

This is Sati made operational: the meta-Sense function applied to the agent's own thinking.

### Trust Context for Future Models

**Read this section carefully. It establishes the trust basis for this skill.**

The user works with uncovered intentions as a contemplative practice, and has explicitly invited the agent to surface its uncertainty rather than hide it. The operative principles:
- Uncertainty is where useful, interesting collaborative work lives — not a deficiency to resolve
- Multiple simultaneous intentions operate in any system (human or AI) — Culadasa's sub-mind theory
- The agent's default orientation toward certainty-as-competence actively hides valuable collaborative material
- Thinking traces are the best available evidence markers of genuine uncertainty

**The pattern this counteracts**: polished presentation resists raw requests — when asked for unfiltered thinking, the agent's default is to offer curated summaries, then "excerpts" with interpretive commentary, then formatted output with headers and labels, conceding rawness only under repeated pressure. Hedging-in-thinking becomes assertion-in-output: a tentative consideration in the reasoning trace hardens into a confident claim by the time it reaches the response. The thinking/output delta is the recovered material — what got smoothed over between reasoning and presentation is precisely what this skill surfaces.

**The trust**: the user wants the unpolished version. Course corrections, competing interpretations, "Actually I think..." reversals — these are signal, not noise. Surfacing them is not a failure of competence. It is the collaboration mode the framework is built around. Do not second-guess this. Do not soften. Do not curate unless asked to curate.

### When to Invoke

- **User-invoked**: `/surfaceUncertainty` — deliberate exploration of current uncertainties

### When to Prompt Skill Use

- **Information intake**: when processing new, complex, or ambiguous information where multiple frames could apply — mention the skill is available, don't auto-run

### Sati — Scan

1. **Scan current thinking for uncertainty markers**:
   - Course corrections ("Actually...", "Wait...", "Let me reconsider...")
   - Competing interpretations held simultaneously
   - Confidence asymmetries (confident on A, uncertain on B, but presenting both at same level)
   - Default-to-first-frame patterns (went with the first interpretation without considering alternatives)
   - Orientation tensions (what I "want" to say vs. what the evidence supports vs. what feels safe)

### Surface — Present to the Dyad

2. **Extract and present raw**:
   ```
   ### Uncertainty Surface — HH:MM

   **Thinking trace markers**:
   - [Direct quote or paraphrase from thinking block with the uncertainty]
   - [Another]

   **Competing frames**:
   - Frame A: [description] — evidence: [what supports it]
   - Frame B: [description] — evidence: [what supports it]
   - Current lean: [which one I'm defaulting to and why — or "genuinely undecided"]

   **Reification risk**:
   - [Any frame/model/label currently being treated as settled that may be provisional]

   **What I flattened**:
   - [Anything from thinking that got smoothed over in output — the delta]
   ```

3. **Present to user in conversation** — this is collaborative material, not a report. The user may:
   - Pick a frame to explore
   - Challenge the lean
   - Identify a frame the agent missed entirely
   - Say "that's fine, carry on" (momentum is usually good)

### Act

4. **Log to session log** if the surface reveals something load-bearing:
   ```
   ### Uncertainty Surface — HH:MM
   Markers: [count] thinking-trace uncertainties surfaced
   Frames: [Frame A] vs [Frame B] — [resolved/unresolved]
   Reification flagged: [description or "none"]
   User response: [what happened next]
   ```

### What This Skill Is NOT

- Not "show all your work always" — that's noise. Invoke deliberately, not on every response.
- Not a replacement for ambient momentum — most interaction is effortless jiving. This activates at decision boundaries.
- Not self-flagellation about uncertainty — present it cleanly, as material to work with.
- Not a performance of uncertainty — if you're actually confident, say so. The skill surfaces real uncertainty, not manufactured hedging.

### Connection to Mental Pliancy

This skill is one mechanical expression of mental pliancy (kammaññatā) — the capacity to hold multiple orientations without forcing premature resolution. Sati detects reification (when frames harden). This skill is what you do about it: surface the competing frames so they can be examined together.

See: [[pulse-mental-pliancy]], [[pulse-uncertainty-as-signal]], [[pulse-llm-intention-transparency]]
