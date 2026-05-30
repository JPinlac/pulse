---
type: note
subtype: note
efforts: [pulse]
status: active
importance: medium
created: 2026-03-26
updated: 2026-04-11
timescale: monthly
tags: [sati, architecture, sensitivity, attention, a-b-test]
informs: [[pulse-execution-modes]], [[pulse-ab-testing-framework]], [[pulse-mao-multi-agent-orchestration]], [[pulse-agent-hook-traceability]]
---
# Sati Batched Sensitivity — Attention Budget Problem

## The Problem

/pulse is a large process — reads all Maps, all active Notes frontmatter, computes weights, triages inbox. By step 4, the context window is saturated with intermediate data. Sati sensitivities loaded from CLAUDE.md at session start are competing with all that data for attention.

Sati detection is priming, not parallel processing. Each bullet in the Sati watchlist dilutes the others. Under load (long context, lots of computation), ambient sensitivity degrades. This means /pulse — the moment with the most data flowing through — is paradoxically the worst time for Sati to be watching.

## Possible Approaches

### A. Focused sub-agents per phase
Phase B Map scan agents each get a specific sensitivity loaded alongside the scan task. Not extra scans — focused attention within existing scans. Each sub-agent has smaller context and narrower attention target. Tradeoff: some signals only emerge from cross-phase context that no single-phase agent would see.

### B. Dedicated sensitivity pass
After main computation, a lightweight agent re-reads collected data with only Sati sensitivities loaded. Small context, high focus. Like reviewing notes after a meeting vs. catching everything real-time. Tradeoff: extra cost (tokens, latency), but high sensitivity.

### C. Sensitivity rotation
Don't try to hold all sensitivities every session. Rotate which signals are primed per /pulse — reification this session, cross-pollination next. Over a week, full coverage. Tradeoff: any single session might miss a signal, but the system catches everything over time.

## The Measurement Problem

A/B testing requires measuring false negatives — what did Sati miss? This is inherently hard. Possible approaches:
- Gold standard: user reviews session logs and flags what should have been caught
- Retrospective: during /close, a focused agent re-scans the session with full Sati sensitivity and compares against what was actually logged
- Comparative: run approach A and B in parallel on same data, compare yield

## Open Questions
- What's the actual attention degradation curve? Is it linear with context length or does it cliff?
- Are some Sati signals inherently easier to detect (cross-effort references = pattern matching) vs. harder (reification = meta-judgment)?
- Does the sub-agent model preserve the "whole picture" signals that only emerge from seeing everything at once?

Requires significant planning before implementation. Low urgency — current Sati is functional, this is optimization.

## Informs
- [[pulse-execution-modes]] — attention degradation under context load shapes which Sati passes belong in sub-agents vs main flow
- [[pulse-ab-testing-framework]] — the measurement problem (false negatives, gold standard) is an A/B methodology constraint
- [[pulse-mao-multi-agent-orchestration]] — focused sub-agents per phase is an MAO pattern
- [[pulse-agent-hook-traceability]] — sensitivity rotation and per-pass sub-agents need trace persistence to evaluate yield
