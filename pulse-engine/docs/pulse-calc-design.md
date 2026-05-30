---
type: doc
subtype: reference
efforts: [pulse]
created: 2026-04-15
updated: 2026-04-15
informs:
  - pulse-graph-migration
  - pulse-graph-architecture
  - pulse-cli-surfacing-boundary
  - pulse-architecture-improvements
  - pulse-capacity-model
---

# pulse-calc.py — Design & Architecture

Deterministic priority computation extracted from LLM reasoning into a Python script. This document covers why, how, and what transfers to the graph CLI.

## Problem

Prior to 2026-04-15, all priority computation happened inline in the LLM's reasoning trace during `/pulse` Phase D. Three compounding failures:

1. **Arithmetic unreliability** — LLMs approximate math. Soft rounding accumulated across the full effort set and 60+ items, producing weights that were directionally correct but numerically imprecise. A maintenance-effort urgency was missed by +0.05 because the agent's mental arithmetic dropped a component.

2. **Sense/Surface fusion** — the same reasoning pass that computed `priority_weight` also made display decisions (which items to show, how to describe them). Under token pressure, the deterministic math was the first thing compressed because it *looked like* reasoning rather than mandatory logic. This is the SRSA violation: Sense (deterministic) was written as Surface (judgment-style prose).

3. **Non-auditability** — the thinking trace was the only record of how numbers were derived. When a weight was wrong, there was no structured path to trace which component miscalculated. Calibration corrections identified *what* was wrong but couldn't reliably identify *which formula component* produced the error.

## Design Decision: Script, Not Server

Options considered:

| Approach | Pros | Cons |
|----------|------|------|
| Another markdown skill | Easy to write | Still LLM-estimated, same problems |
| Python script via `uv run` | Deterministic, zero infra, auditable JSON | Reads files each run (slow for large vaults) |
| pulse-cli (graph) | Canonical long-term solution | Multi-phase project, Neo4j dependency, unclear timeline |
| Local API server | Fast after startup, persistent state | Over-engineered for the problem, server lifecycle |

Chose the script. Key constraints: no server (low weight), `uv run` handles dependencies (PEP 723, single file), formulas transfer directly to graph CLI Phase 3.

## Boundary: Script Computes, Agent Interprets

The script owns:
- Frontmatter parsing (Maps, Notes, Minor Actions, calibration)
- All formula arithmetic (base_score, recency_boost, urgency_spike, loop_factor, calibration_offset)
- Effective item scoring with waiting-item exception
- Per-effort cap enforcement and ceiling application
- Dependency resolution
- Batch aggregate computation and gating
- Resurfacing candidate detection
- External input staleness flagging

The agent owns:
- Fuzzy flags (efforts within 0.05, high recency on low base, overdue in suppressed)
- Suppression reasoning (why something was *not* shown — the hardest class of bug)
- Display decisions (how to describe items, section headers, context hints)
- Calibration pattern *interpretation* (the script counts corrections; the agent decides what they mean)
- Validation prompts and correction logging
- Session log entries

This boundary maps to SRSA: the script is pure Sense (deterministic logic), the agent does Route and Surface (judgment on computed inputs). See `[[pulse-cli-surfacing-boundary]]` for the generalized version of this boundary — `pulse-calc.py` is the first concrete implementation of the "CLI computes, skill layer interprets" pattern.

## Key Discoveries During Extraction

### Active Threads as Loop Boundary

The formula spec said "each open item (active/waiting Note or unchecked Minor Action)." But Notes with `efforts: [pulse]` included 45 items — theory docs, reference notes, sub-theme entries. The agent had been implicitly filtering to ~20 by only counting Notes under `## Active Threads`, but this filtering lived in the LLM's judgment, not in the formula.

Formalizing the boundary: **only Notes listed under `## Active Threads` in a Map count as open loops**. Notes under sub-themes, `### Theory & Reference Docs`, or with `subtype: reference` are excluded. This is enforced by `parse_active_threads()` in the script, which returns `{slug: summary}` from the Map's Active Threads section.

This is the same insight that produced the `docs/` separation (2026-04-11) — structural boundaries are more reliable than filter logic. The Map structure *is* the classification.

### Effort Domination and the Per-Effort Cap

With uncapped loop_factor and a 12-item ceiling, pulse plan Notes (all `importance: high` or `medium`) filled positions 3-12 in Important Items, crowding out actionable items from other efforts entirely. Three maintenance items (appointments and admin), two practice items, and an urgent deadline were invisible.

Fix: per-effort cap of 3 on high/medium items. Low-importance items flow uncapped — they serve as break-time/peripheral tasks that surface from lower-weight efforts. Ceiling raised to 20 to accommodate the broader spread. Display splits into "Important Items" (top ~12) and "Between Tasks" (remainder).

This is a capacity-aware display decision. See `[[pulse-capacity-model]]` — the effort cap is a simple form of "attention budget" that the capacity model will eventually generalize.

### Map Entry Summaries as Descriptions

Note-type items initially displayed as raw slugs (`deploy-pipeline-proposal`, `pulse-capacity-model`). Map entries have human-readable summaries: `[[deploy-pipeline-proposal]] — proposal updated: project-specific problem + opportunity sections`. The script now extracts these summaries from `## Active Threads` and uses them as item descriptions. Minor Actions already had human descriptions.

This means Map entry summaries serve double duty: navigation in Obsidian *and* display in the `/pulse` briefing. The ≤15-word Map entry convention matters more now.

## Relationship to Graph Migration

`scripts/pulse-calc.py` is a bridge to `[[pulse-graph-migration]]` Phase 3 (Computation Bootstrap). The formulas are identical — what changes is the data source:

| | pulse-calc.py (current) | pulse-cli recompute (future) |
|---|---|---|
| Data source | Markdown files (Maps/*.md, Notes/*.md) | Neo4j graph |
| Parsing | Regex + YAML | Cypher queries |
| Open loop boundary | `parse_active_threads()` on Map body | `belongs_to` edge type in graph |
| Reference exclusion | `subtype: reference` check | Node property or label |
| Summary text | Extracted from Map entry text | Node `summary` property |
| Output | JSON to stdout | JSON to stdout (same schema) |

The output schema is designed to be the same — the `/pulse` skill's consumption code shouldn't change when the backend switches. The graph adds capabilities the script can't provide (temporal queries, cascade effects, rich cross-effort traversal), but for priority computation the formulas are the same.

Relevant graph notes:
- `[[pulse-graph-architecture]]` — graph data model, node/edge schemas
- `[[pulse-graph-migration]]` — Phase 3 = computation bootstrap (where this script's logic migrates)
- `[[pulse-cli-surfacing-boundary]]` — CLI computes, skill layer interprets (the pattern this implements)
- `[[pulse-cli-skill-interface-design]]` — contract between CLI and skill layer
- `[[pulse-migration-file-map]]` — inventory of files for migration

## Script Architecture

Single file: `scripts/pulse-calc.py`, ~700 lines, PEP 723 with `pyyaml>=6.0`.

```
CLI args → load_maps() + load_notes() + load_calibration()
         → compute_effort_weights()
             → compute_recency_boost()
             → compute_urgency_spike()
             → compute_loop_factor()
         → resolve_dependencies()
         → compute_effective_item_scores()
         → apply_effort_cap()
         → compute_batch_aggregates()
         → compute_resurfacing()
         → JSON output
```

Key data flow: `parse_active_threads()` returns `dict[str, str]` (slug → summary). This dict gates which Notes count as loops AND provides human-readable descriptions for display. One parse, two purposes.

CLI: `uv run scripts/pulse-calc.py --vault . [--date YYYY-MM-DD] [--effort-cap N] [--calibration-offsets JSON]`

## Informs

- `[[pulse-graph-migration]]` — Phase 3 computation bootstrap uses same formulas
- `[[pulse-graph-architecture]]` — script output schema prefigures graph query results
- `[[pulse-cli-surfacing-boundary]]` — first concrete implementation of compute/interpret boundary
- `[[pulse-architecture-improvements]]` — Sense/Surface boundary more precisely defined
- `[[pulse-capacity-model]]` — effort cap as simple attention budget
