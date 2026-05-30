---
type: note
subtype: reference
efforts:
  - pulse
status: active
importance: medium
created: 2026-05-08
updated: 2026-05-08
informs: [[ai-orchestration-control-qa-reference]]
---
# Working Reference Prompt Template

A reusable prompt for generating a working reference to the named parts of any skill or domain — vocabulary you can compose with in future prompts. Process artifact: produces a vocabulary-grade reference for an unfamiliar domain, suitable for returning to as you run small experiments.

First instantiation: [[ai-orchestration-control-qa-reference]] (control theory + automated QA + SRE for AI orchestration).

---

I want a working reference to **{SUBJECT}** — a structured guide to the domain's named parts, concepts, behaviors, and pitfalls, written so I can use those names as vocabulary when prompting models to build things in this domain.

## Audience and use

{ABOUT_ME — what I know, where my gaps are, and what I'll do with the guide. Be specific; this drives what deserves depth.}

I'm going to use the named parts as vocabulary. After reading, I should be able to write prompts like "build me an X using a Y and a Z, with a defense against W" and have a model understand. Every named part needs to be a **handle** — a name plus enough texture that I know what I'm reaching for, when to reach for it, and how it tends to break.

## Stance: Bessis-flavored

In the spirit of Bessis's *Mathematica*: what I'm after is the **texture and behavior** of these objects, not formal definitions. The unlock for an unfamiliar concept usually comes from feeling how it acts, where it bends, how it fails — not from a precise statement of what it "is." Lean on examples, contrasts, and the small surprising details that make a concept click. Definitions without texture are nearly useless to me.

## Stance: the process-mirroring gap

A note on how I'll actually learn this material, because it shapes what's useful in a reference.

People learn physical skills like tying shoes by mirroring process — watching hands move, making micro-corrections in their own attempts. I can't do that for **{SUBJECT}** in the same way, because when the "process" involves an LLM, the relevant behavior is a probabilistic distribution I only access through interaction. There is no body of fixed motions to mirror. So my actual learning loop is: read this reference, then prompt with the named parts, watch what happens, and develop felt sense — including by watching the same prompt produce different results across runs, because the **variance is part of the lesson**.

What this means for you: don't write this like a tutorial walking me through fixed procedures. Write it like a reference I'll return to while I run my own small experiments. Examples help me anchor what to expect. Over-specified procedures will mislead me, because the actual behavior won't match.

## Structure

Pick the natural taxonomy for **{SUBJECT}**. Don't force a generic skeleton; choose categories that carve the domain at its joints. State the taxonomy briefly at the top, then proceed.

**Failure modes, pitfalls, and antipatterns must be a first-class layer, not a footnote.** Name them so I can use the names as vocabulary too — "add a defense against context drift" only works if I have *context drift* as a handle. Naming the failures is half the value of this reference.

## Goal and sensed gap

{GOAL_AND_GAP — what I'm actually going to do with this material, and where I sense the gap or weight in plain language. You don't need to know any of the domain's named parts to fill this in — that's what the reference is for. Describe in your own words what you're trying to build or understand, where you feel weakest, and what kind of failures worry you most. The receiving model knows the domain and will translate this into where to go deep. If you genuinely have no specific goal beyond general literacy, say so and skip the gap part.}

## Depth and length

Depth should match the complexity and load-bearing-ness of each concept. **Do not write uniform-length entries.** A simple, well-named handle might take two sentences. A subtle, contested, or easily-misused concept might need several paragraphs with examples and contrasts. Err toward more depth on:

- Concepts that are subtle, contested, or commonly misunderstood.
- Concepts whose behavior surprises people.
- Concepts that look like familiar things from other fields but behave differently.
- Concepts that carry a lot of weight when the system is under stress.

Err toward less depth on things that are obvious from their name or that are widely understood the same way across communities.

## Prioritization

Apply two filters at once: depth-matches-complexity (above) and relevance-to-my-goal (below).

Sort the named parts into three tiers:

- **Load-bearing**: central to my goal as described above. Full treatment per the entry shape.
- **Adjacent**: real and worth knowing, but not central to what I'm doing. A short paragraph; skip examples unless the concept is surprising.
- **Named-only**: a sentence saying the handle exists and when I'd care. Format: "*name* — what it is in half a sentence. Reach for this if X." Preserves the handle so I can return to it without spending depth now.

**Denote rather than exclude.** A missing concept I don't know exists is worse than a one-line mention I can return to. "I don't know what I don't know" is a particularly bad failure mode for someone learning the vocabulary of a new domain.

The exception: if something is genuinely *wrong-domain* for my goal — not just lower priority but actually about a different activity — omit it and briefly flag what you omitted and why at the end of the relevant section. Format: "Omitted: X, Y, Z because they belong to [different activity I'm not pursuing]." That visibility lets me push back if you cut something I wanted.

Tiering tracks my goal, not the concept's general fame. Be willing to put well-known concepts in named-only and obscure ones in load-bearing if relevance dictates.

## Entry shape

Each entry is a handle. Draw from these as relevant — not all every time, and the mix should differ between simple and complex entries:

- The name, plus common synonyms (flag when synonyms hide real differences).
- What it is, in plain language with texture.
- When to reach for it; when not to.
- How it tends to fail, get misused, or get faked.
- One or two concrete examples — especially for subtle concepts. Examples can be small dialogues, pseudo-flows in plain language, or before/after sketches. Use them to make behavior visible, not just to illustrate definitions.
- The closest analogy from an adjacent field if there's an honest one — and flag explicitly when the analogy misleads.
- Contrasts with neighboring concepts that are easily confused with this one. These contrasts are often where the real understanding lives.

## Closing sections

End the reference with two short sections, in this order:

**Adjacent fields worth a look.** An opinionated list of domains whose vocabulary or hard-won intuitions illuminate this one. For each: the field name, a one-sentence note on what it brings that this domain has under-developed, and one or two concept-handles from that field that translate well. Three to six entries — threads to pull, not a literature review.

**Starter projects.** Three to five small, specific things I could build using only the vocabulary in this reference. Each in two or three sentences: what it does, which named parts it exercises, and which failure mode it's most likely to surface first. These are *learning artifacts* — small enough that I'll actually build them and watch them break. Avoid impressive-demo energy; favor things small enough to actually run.

## Style rules

- Prose-first. Lists only where they genuinely aid scanning.
- No implementation walkthroughs, library or tool recommendations, or code.
- Opinionated. Mark folklore as folklore. Say which parts are overrated. Say when two names cover the same concept.
- Asymmetry is the goal, not parallelism. If three things are worth saying in one category and one thing in another, that's correct.
- Skip preambles and executive summaries. Start with the taxonomy, then the first entry, and end with the closing sections specified above.

## What I don't want

- Motivational framing or hype.
- Textbook definitions without commentary.
- Equal weight given to every subcategory regardless of importance.
- Terseness for its own sake. Match depth to complexity.
- Hedging where opinion would be more useful.

Begin.
