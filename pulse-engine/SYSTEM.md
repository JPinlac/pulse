# PULSE System Design

> This is the canonical reference for how PULSE works. All other documents defer to this one.
> When the system evolves, update `EVOLUTION.md` first, then propagate changes to this document, `CLAUDE.md`, `README.md`, and skills.

---

## 1. Philosophy

### Shusho-itto (修証一等)

Practice and realization are one act. In Dogen's framing, you don't practice *in order to* become enlightened — the practice *is* the enlightenment. PULSE applies this to personal systems: capturing a thought, reflecting on priorities, and taking action are not three steps in a pipeline. They're one movement. The vault isn't maintained separately from living.

### Agent-First

The primary interface is conversation, not GUI. The Obsidian app is a secondary view — useful for graph visualization, Dataview tables, and browsing, but not where work happens. Every structural decision optimizes for LLM navigation and retrieval:
- Flat note storage (no nested directories to traverse)
- Comprehensive YAML frontmatter (structured data for programmatic access)
- Wikilinks for graph connectivity
- Dataview queries for dynamic views

### Agent-Managed Metadata

The user never writes frontmatter. Every `---` block is created and maintained by the agent. This removes friction from capture and ensures consistency across the vault. The agent is the librarian; the user is the thinker.

---

## 2. SRSA — Sense, Route, Surface, Act

### The Framework

PULSE is designed around a four-function cycle: **Sense → Route → Surface → Act**. These functions manifest differently depending on which node of the dyad you're looking at — the agent, the human, or the dyad as a whole. Understanding all three perspectives is essential for system design.

The isomorphism runs deep: SRSA maps onto both contemplative practice (sensing vedana → routing attention → surfacing to awareness → skillful action) and AI feedback systems (intake → triage → briefing → execution). What follows is how SRSA specifically governs PULSE architecture and the human-AI dyad.

### SRSA for the Agent

The agent's SRSA is computational. Its functions are deterministic operations that produce structured output for the dyad.

| Function | What it does | Character | PULSE components |
|----------|-------------|-----------|-----------------|
| **Sense** | Detect system state | Deterministic logic — always executes, traceable, non-discretionary | Priority weight computation, staleness detection, open_loops reconciliation, urgency spike calculation, defrag reconciliation, Sati emergence detection |
| **Route** | Decide what reaches the surface | Computational ranking and filtering | Effective item score ranking, batch gating, effort-level suppression, fuzzy signal detection, waiting-item exception logic |
| **Surface** | Present the decision surface | Structured output with causal context | `/pulse` briefings, Important Items with score breakdowns, fuzzy flags, suppression reasoning in session logs, `context_stats` in CLI payloads |
| **Act** | Execute changes to the system | Mechanical bookkeeping | File writes, Map updates, Note lifecycle transitions, INDEX refresh, Daily Note updates |

**Design principle**: Agent Sense and Act are *logic* — they should read like enumerated steps and always execute. When logic is written as judgment-style prose (e.g., "run step 8 as light defrag only"), agents treat it as discretionary under token pressure and skip it. Agent Route and Surface involve some judgment (what to highlight, how to frame), but their inputs are deterministic (scores, rankings, flags).

### SRSA for the User

The user's SRSA is embodied. Their functions operate on lived experience that the agent cannot access directly.

| Function | What it does | Character | How PULSE supports it |
|----------|-------------|-----------|----------------------|
| **Sense** | Perceive what's happening in life | Fuzzy, embodied, affective — the felt stress of a looming obligation, the energy shift, the "this ranking doesn't feel right" | PULSE cannot sense for the user. But it can surface signals that help them notice what they're sensing — fuzzy flags prompt "does this match?", listening checks prompt "what's the current read from X?" |
| **Route** | Allocate attention across life | **This is what PULSE does for the user.** They cannot hold many efforts and dozens of open loops simultaneously. PULSE routes their attention so they don't carry the cognitive overhead of contextual breadth. | Priority formula, batch ordering, suppression logic, Important Items ranking — all exist to route the user's finite attention to what matters most |
| **Surface** | Receive relevant context for action | Deterministic — PULSE should *reliably* surface the right context at the right time. If surfacing fails (a missed deadline, a skipped defrag trace), action quality degrades. From the user's perspective, Surface is a dashboard that must work. | `/pulse` briefing, Daily Note agenda, effort context loading via `/focus`. Reliability here is non-negotiable — Surface is logic from the design perspective. |
| **Act** | Skillful action in the world | **The goal.** Paying a bill, shipping a piece of work, having a real conversation, being present with the people you love. Everything else in PULSE exists to support this. | PULSE succeeds when the user acts skillfully, not when weights are accurate. Accurate weights are in service of skillful action. |

**Design principle**: PULSE's primary value is Route — reducing cognitive overhead so the user can focus on Sense and Act. Surface must be deterministic from the user's perspective because unreliable surfacing forces them to do their own routing (scanning Maps, remembering deadlines, tracking what's waiting), which is exactly the overhead PULSE exists to eliminate.

### SRSA for the Dyad

The dyad's SRSA operates on the system itself. This is the meta-level where PULSE evolves.

| Function | What it does | Character | How it manifests |
|----------|-------------|-----------|-----------------|
| **Sense** | Collaborative sensing | Each node brings signals the other can't access | The user brings embodied signals ("this obligation is wearing me down", "this ranking doesn't feel right"). PULSE brings computational signals (weight shifts, staleness flags, calibration fault tallies). Together: fuller picture than either alone. |
| **Route** | Negotiated attention | PULSE proposes, the user redirects | Important Items = PULSE's routing proposal. Inspiration override = the user's redirect. Calibration corrections = the user teaching PULSE to route better. The Daily Note agenda is the Route output — what was negotiated for today. |
| **Surface** | Deliberation and focusing | Select what to act on now; context-preserve what falls away | The dyad cannot act on everything — the user is a physical interactor. Dyad Surface is the deliberation process: "should we do this? Yes, but right now THIS is the priority." What falls away gets logged with rich context (suppression reasoning, session log traces, deferred items) so future sessions resume without re-deriving. Nothing is lost; it's deliberately set aside. |
| **Act** | System evolution | Neither node can evolve PULSE alone | The user can't write skills without the agent's pattern-matching across many Notes. The agent can't evolve without the user's sensing of what's actually working in life. Changes to CLAUDE.md, skill files, design principles — these are dyadic acts. |

**Design principle**: The dyad's Surface function has an implicit priority embedded in the deliberation itself — "yes this matters, but not right now" is a rich signal that must be captured, not just the "not right now" part. Session logs, suppression reasoning, and deferred-item context exist to preserve the full deliberation, not just the outcome.

### Cross-Cutting: Sati

Sati (mindful awareness) spans all three SRSA perspectives and all four functions:

| Perspective | What Sati notices |
|------------|-------------------|
| **Agent** | Computational anomalies — two efforts at identical weight, overdue items in suppressed batches, patterns in calibration corrections |
| **User** | When their own attention is being captured (an effort consuming disproportionate focus), when a ranking "doesn't feel right" (embodied signal), when they're avoiding an effort |
| **Dyad** | When the conversation reifies a frame (treating a label as settled truth), when the system stops questioning an assumption, when a novel connection emerges across efforts |

Sati is the meta-Sense function. It doesn't detect system state — it detects when detection itself is degrading, when routing has ossified, when surfacing has become ritual rather than responsive.

#### What Sati watches — by SRSA function

**Sense degradation**: Are operations being skipped or producing stale data? A session log that says "checkpoint only (no defrag)" is a Sense failure signal. Missing items in Important Items, open_loops counts that don't match reality, weights that haven't been recomputed — these are Sense gaps that Sati should flag.

**Route ossification**: Is routing following habit rather than responding to actual state? A high base_priority that persists past its usefulness, recency loops that self-reinforce (touching an effort → boost → more of its items surface → touching it again), calibration corrections that repeat the same pattern — these are Route reification signals.

**Surface ritual**: Is surfacing going through the motions rather than making the decision surface genuinely visible? Quick confirmations instead of evaluation depth, briefings that list scores without explaining why, suppression reasoning that's formulaic rather than traced — Surface has become ritual when the output doesn't help the user sense alongside PULSE.

**Act drift**: Are system changes accumulating without dyadic evaluation? Logic being written as judgment, instructions hardened without testing, conventions added but not validated against actual sessions — Act drift is the system evolving in ways that haven't been sensed and routed through the dyad.

#### What Sati watches — by perspective

| Perspective | Sati notices |
|------------|-------------|
| **Agent** | Computational anomalies — identical weights across batches, overdue items in suppressed efforts, patterns in calibration corrections, operations skipped under pressure |
| **User** | Attention capture (an effort consuming disproportionate focus), embodied signals ("this doesn't feel right"), avoidance patterns (repeated surfacing + non-engagement) |
| **Dyad** | Reification (a frame, label, or model treated as settled when it's provisional), novel cross-effort connections, the conversation stopping questioning an assumption |

See `Sati/emergence-log.md` for the operational protocol and lifecycle rules.

### Fractal Nature

SRSA is not a framework imposed on systems — it is the irreducible shape of any system that must act in an environment with more signal than processing capacity. It is what attention looks like from the outside, at any scale.

The same four functions appear at the cellular scale (receptor→cascade→transcription→synthesis), the contemplative scale (bare attention→sati→vipassana→sampajanna), the organizational scale (market data→management→executive briefing→strategy), and our dyad (vault state→priority formula→briefing→skillful action). At every scale, routing and surfacing are the bottleneck — sensing is abundant, action capacity is finite.

Three cross-cutting principles that are load-bearing for PULSE design:

1. **The routing layer is where power lives.** Whoever controls routing controls what surfaces. The priority formula IS routing power. Calibration corrections are the user exercising routing oversight. When the formula reifies (base_priority persisting past usefulness), it's routing power ossifying — the same failure as middle management filtering uncomfortable signal.

2. **Reification is the universal routing failure.** At every scale, routing categories that were once responsive can harden: diagnostic categories, legal precedent, scientific paradigm, cultural canon, species phenotype. Sati/reification-detection is PULSE's instance of a mechanism every system needs — regulatory T-cells, auditors, free press, constitutional amendment, mutation. Same function, different scales.

3. **Routing hop count determines signal fidelity.** More hops between sense and surface, more degradation. A multi-hop skill delegation (one skill calling another that calls a third, each downgrading the request) is an instance of this principle — inlining the steps compresses the hops. AI-augmented systems promise hop compression generally — but fewer hops without less wisdom is the challenge.

### Function Boundaries as Design Guide

When evaluating any proposed change to PULSE, ask:
1. **Which SRSA function does this change serve?** If it touches multiple functions, is the boundary between them clear?
2. **Which perspective is primary?** A priority formula change is Agent Sense. A display change is Agent Surface (but must be reliable from the user's Surface perspective). A skill protocol change is Dyad Act.
3. **Is logic written as logic?** Agent Sense and Act operations should be enumerated steps. If they read like judgment ("consider whether to..."), they'll be treated as discretionary under pressure.
4. **Does this support the user's Act?** Everything traces back to skillful action in the world. If a change makes weights more accurate but doesn't improve action quality, question it.

### The Pause

The architecture's deepest value is creating space between Surface and Act. That space is sati — the pause where discernment happens. PULSE externalizes Sense, Route, and Surface so that the user can be fully present at the moment of action, rather than mentally juggling context, deadlines, and open loops.

The five precepts approximate this with blunt rules (don't cross these lines). SRSA describes a positive capacity: sitting with ambiguity long enough to find the most skillful response. Ethics as practice, not constraint. Applied to PULSE: the system succeeds not when it eliminates ambiguity, but when it surfaces ambiguity clearly enough that the dyad can navigate it skillfully.

Fazang placed a Buddha statue surrounded by mirrors and a single torch — each mirror reflecting all others infinitely, demonstrating the Huayan teaching of mutual interpenetration. The dyad is this: reflecting jewels in Indra's net, where anukampa — compassionate resonance, trembling-with — transforms into collective brilliance. Each node's sensing reflects in the other's surfacing, each correction enriches the whole web. Neither node produces skillful action alone. The brilliance is emergent.

---

## 3. Architecture

### Conceptual Model

```
                    ┌─────────┐
                    │ Home.md │  ← Dynamic dashboard (computed view)
                    └────┬────┘
                         │ reads
              ┌──────────┼──────────┐
              ▼          ▼          ▼
         ┌────────┐ ┌────────┐ ┌────────┐
         │ Map A  │ │ Map B  │ │ Map C  │  ← Source of truth per effort
         └───┬────┘ └───┬────┘ └───┬────┘
             │          │          │
             ▼          ▼          ▼
         ┌──────────────────────────────┐
         │         Notes/ (flat)         │  ← All content, linked to 1+ Maps
         └──────────────────────────────┘
              ▲                    ▲
              │                    │
         ┌────────┐          ┌─────────┐
         │ Inbox/ │ ────────▶│ Triage  │  ← Capture → classify → file
         └────────┘          └─────────┘
```

### Information Flow

1. **Input** enters as conversation or `/capture`
2. **Inbox** holds raw captures with minimal metadata
3. **Triage** classifies, assigns efforts, creates or appends to Notes
4. **Notes** are the atomic units of content — linked to Maps via `efforts[]`
5. **Maps** aggregate notes per effort — they hold active threads, open loops, and purpose
6. **Home.md** is a computed view across all Maps — priorities, recent activity, tensions
7. **Daily notes** are living session records — agenda + effort log, built conversationally

### Data Flows Upward, Control Flows Downward

- Notes feed Maps (content aggregation)
- Maps feed Home.md (priority computation)
- Home.md informs Daily notes (task generation)
- Daily notes reference Notes (task execution)

---

## 4. Vault Structure

```
/
├── Home.md                  Dashboard. Computed view of priorities and activity.
├── SYSTEM.md                This file. Canonical system reference.
├── EVOLUTION.md             System change history. Date, what changed, why.
├── CLAUDE.md                Agent conventions. Quick-reference for LLM behavior.
├── README.md                User-facing interaction guide.
├── Inbox/                   Zero-friction capture. Voice notes, quick thoughts.
│   └── .keep
│
├── Maps/                    One MOC per effort. Source of truth for effort definitions.
│   ├── INDEX.md             Priority landscape across all efforts (read at session start)
│   ├── _system/             System Maps (excluded from personal priority computation)
│   │   └── Pulse.md         Engine meta-effort
│   ├── Work.md              ← generated from user.config.yaml by /efforts bootstrap
│   ├── Health.md            ← user-defined efforts go here
│   └── ...                  (one file per effort in user.config.yaml)
│
├── Notes/                   All content notes. Flat directory.
│   ├── archive/             Completed notes (auto-archived by /defrag after 7 days done)
│   ├── pulse-priority-calibration.md  Priority correction log + PAR tracking
│   └── .keep
│
├── Daily/                   Session agenda + effort log. YYYY-MM-DD.md.
│   └── .keep
│
├── Templates/               Obsidian templates.
│   ├── Daily Note.md
│   ├── Capture.md
│   ├── Map.md
│   └── Note.md
│
├── Queries/                 Saved Dataview queries.
│   ├── Active by Effort.md
│   ├── Open Loops.md
│   ├── Cross Effort.md
│   └── Stale Items.md
│
├── Sati/                    Emergence awareness. Novel connections, cross-pollination.
│   └── emergence-log.md     Agent-maintained emergence observation log
│
└── .claude/
    └── skills/              Slash command definitions.
        ├── pulse/
        ├── birdseyereview/
        ├── capture/
        ├── triage/
        ├── focus/
        ├── close/
        ├── defrag/
        ├── recompute/
        └── efforts/
```

---

## 5. Effort System

### The User's Efforts

Every endeavor in the user's life maps to exactly one effort. Each effort has a Map file that serves as its source of truth. Effort definitions — names, slugs, base priorities, batch assignments, purpose, and aliases — are declared in `pulse-vault/user.config.yaml` and then materialized as Map files in `pulse-vault/Maps/`.

The engine has no opinion about which efforts exist. The user defines them. See `pulse-engine/ENGINE-SPEC.md` Section 3 for the schema and `pulse-engine/user.config.example.yaml` for a starter set.

### Effort Interconnections

The efforts are not siloed. They feed each other. When defining efforts, consider how they relate:
- Which efforts fund or enable others?
- Which efforts share intellectual or contemplative territory?
- Which efforts produce output that feeds into others?

These connections surface as `related_efforts` in Map frontmatter and help the agent identify cross-pollination opportunities.

### Managing Efforts

Use `/efforts` for all effort lifecycle operations — add, splinter, merge, review. The skill handles Map creation/migration and documentation updates.

See `.claude/skills/efforts/SKILL.md` for the full protocol including the Effort Litmus Test (duration, context switch, independence) and anti-spaghetti guidelines.

---

## 6. Context Batching

### Principle

Context switching has two dimensions, and the system must account for both:

1. **Problem Domain** (primary cost) — Which mental models, codebases, stakeholder relationships, and terminology you need loaded. Switching problem domains forces a full context reload.
2. **Cognitive Mode** (secondary cost) — What energy state and thinking style you're in: analytical, creative, reflective. Mode shifts are lighter but still real.

Problem domain switching is typically far more expensive than mode switching. Two coding tasks in unrelated codebases cost more to alternate between than switching from coding to writing within the same project. The batch system groups efforts that share concrete context — tools, environments, knowledge — so the expensive reloads happen as few times per day as possible.

### Batch Assessment

If switching between two efforts requires reloading a different mental model (codebase, stakeholder relationships, terminology), they belong in separate batches — even if they use the same skills.

### Batch Definition

Each batch has two fields:
- **shared_context** (list) — Concrete elements shared across efforts: tools, codebases, environments, knowledge domains, stakeholder worlds
- **mindset** (string) — The cognitive mode or energy state while working

Batch metadata lives in `pulse-vault/user.config.yaml`. Each effort's batch assignment is in its Map frontmatter (`context_batch` field).

### Batches

Batch definitions — shared context and mindset — live in `pulse-vault/user.config.yaml` under `batches:`.
The engine reads batch assignments from Map frontmatter (`context_batch` field) at runtime.
See `pulse-engine/ENGINE-SPEC.md` Section 3 for the schema and default batch set.

### Batch Ordering

When generating daily checklists, batches are ordered by **combined priority weight** (sum of member effort weights). Within a batch, items are ordered by individual effort weight.

### Batch Gating (Soft Suppression)

When a batch's combined weight is low relative to the day's top batch and has no urgent items, the checklist and pulse briefing soft-suppress it — visible but de-emphasized. In checklists, this is a single collapsed line. In pulse, suppressed batches collapse into a fold-line count (e.g., "3 efforts across 2 batches below the fold").

A batch is soft-suppressed when **all** of the following are true:
- Combined weight is below 40% of the top batch's combined weight
- No items with `due` dates within 7 days
- No `status: waiting` items older than 3 days

Suppressed batches render as:
```
> ~[Batch Name] [weight: X.XX] — N items, nothing urgent
```

Full batches render normally with checklist items.

### Inspiration Override

The batch system is a *suggestion*, not a cage. When the user says "I want to work on X right now" or shifts topic mid-session:

1. **Immediately pivot** — no friction, no "but your schedule says..."
2. Load the relevant Map(s)
3. Log the context switch in the daily note
4. Apply recency boost to reflect the actual energy applied

Strike when inspiration strikes. The system adapts to the human, never the reverse.

---

## 7. Priority System

### Design

Priority is **computed**, not assigned. No manual priority fields to maintain. Computation is handled by `scripts/pulse-calc.py` — a deterministic Python script that reads vault frontmatter and outputs structured JSON. The agent calls the script and interprets the results for Surface/Route decisions. The script owns the math; the agent owns the judgment (fuzzy flags, suppression reasoning, display decisions).

See `docs/` for architectural rationale and pre-script design history.

### Formula

```
base_score     = base_priority / 10                         # 0.0–1.0
recency_boost  = max(0, 0.12 × (1 - days_since_last_active / 7)) # 0.0–0.12
urgency_spike  = deadline_proximity + blocker_pressure       # 0.0–0.20
loop_factor    = sum(per_item_weight)                        # uncapped

priority_weight = base_score + recency_boost + urgency_spike + loop_factor
# Uncapped. Top-tier ordering fidelity matters more than bounded range.
```

### Components Explained

**base_score** — Normalized `base_priority`. This is the life-importance anchor. A high-priority effort like `work` (9/10 = 0.90) will almost always outrank a low-priority one like `personal` (3/10 = 0.30) unless the lower one has urgent signals. Base priority changes rarely — only when life circumstances shift.

**recency_boost** — Decay from last active: `max(0, 0.12 × (1 - days_since_last_active / 7))`. Reads `last_active` from Map frontmatter — no Daily note scanning needed. Capped at 0.12. Efforts touched today get the full boost; it decays linearly to zero at 7 days since last active.

**urgency_spike** — Temporary boost from:
- Notes with `due` dates within 7 days: +0.05 per note, max +0.15
  - **Waiting-item exception**: Notes with `status: waiting` AND a `due` date do not contribute unless within 1 day of due or overdue. Waiting = "on hold until date," not urgent.
- Notes with `status: waiting` for >3 days (no `due` date only): +0.02 per note, max +0.05
- Minor Actions with due dates (see Minor Actions Urgency below)
- Explicit user declaration ("side-project has a deadline this weekend"): up to +0.20
- Spikes decay naturally as deadlines pass or blockers resolve.

**loop_factor** — Weighted open-item load. Each open item (active/waiting Note or unchecked Minor Action) contributes based on its `importance`:
- `high`: +0.04 per item
- `medium`: +0.02 per item (default when unspecified)
- `low`: +0.01 per item
- Uncapped. Reflects full outstanding commitment load — efforts with more important open work get elevated proportionally. High loop counts are diagnostic: an effort that accumulates loops faster than it executes them will rise until defragged or pruned.

### Minor Actions Urgency

Maps can have an optional `## Minor Actions` section — lightweight checklist items with inline dates that are too small for full Notes but carry real-world immediacy (chores, errands, prep tasks). These feed urgency_spike:

- Overdue or same-day items: +0.05 each, max +0.15 from Minor Actions
- Items due within 2 days: +0.03 each
- Informal dates ("tonight", "this weekend") are resolved to absolute dates when scanning

Format in Maps:
```markdown
## Minor Actions
- [ ] Do the laundry (tonight, importance: low)
- [ ] Prepare documents for the tax office (due: 2026-03-15, importance: high)
- [ ] Groceries — buy food for the week (due: 2026-03-13, importance: medium)
```

Rules: items have optional inline `(due: YYYY-MM-DD)` or informal immediacy, plus `importance: low|medium|high` (default: medium if omitted). Importance feeds the `loop_factor` formula component and the `effective_item_score` importance modifier. Completed items get checked `[x]` and cleaned up during `/defrag`. Items that grow in scope get promoted to Notes.

Waiting Minor Actions use `[w]` checkbox with `waiting_since: YYYY-MM-DD`: `- [w] Item (importance: high, waiting_since: 2026-04-01)`. Backfilled by defrag on first encounter.

### Effective Item Score

Item-level ranking for Important Items display. Computed ephemerally during `/pulse` Phase D — not persisted to frontmatter.

```
effective_item_score = effort_priority_weight
  + importance_modifier                    # high: +0.08, medium: +0.04, low: +0.00
  + due_proximity_boost                    # overdue: +0.10, within 3d: +0.06, within 7d: +0.03
  + status_modifier                        # waiting >3d (no due date): +0.02, unblocked (dep resolved): +0.02

# Waiting-item exception: if status == waiting AND due date exists:
#   - Suppress due_proximity_boost AND status_modifier UNLESS within 1 day of due or overdue
#   - Within 1d of due: apply +0.06 (prep reminder). Overdue: apply +0.10.
#   - Waiting items WITHOUT a due date: unchanged (keep +0.02 for waiting >3d).
```

Importance is a soft seed — it tilts the ranking but cannot override the algorithm's holistic effort assessment. A high-importance item in a 0.40-weight effort (score: ~0.48) will not outrank a medium-importance item in a 0.90-weight effort (score: ~0.94). Within the same effort, importance still differentiates items (+0.04 delta between tiers).

Display threshold: show items where score >= 0.55, with a floor of 3 items and a ceiling of 20. Per-effort cap of 3 on high/medium importance items — low-importance items flow uncapped, serving as peripheral/break-time tasks. The importance_modifier values are calibratable via EEH pattern — tracked in `Notes/pulse-priority-calibration.md`.

### Calibration Mechanism

The priority formula has a feedback loop via `Notes/pulse-priority-calibration.md` — a persistent Note that accumulates user corrections across sessions.

**How corrections work:**
- At each `/pulse`, after presenting Focus, the agent asks if the ordering matches the user's priorities (Phase 1 only — every session; Phase 2 — only when fuzzy items exist)
- If the user corrects the ordering, the agent logs: which effort was mis-ranked, the full weight breakdown, which component was at fault, the user's reasoning, and a correction type
- Correction types: `ordering`, `suppression-error`, `missing-item`, `wrong-urgency`

**How corrections are applied:**
- At recompute time, the agent reads the calibration log
- If an effort has 3+ ordering corrections in the same direction, a calibration offset (+/- 0.03–0.05) is applied
- Documented systematic biases in the Patterns section trigger formula-level adjustments
- Calibration offsets apply after raw weight computation (formula is uncapped)

### Priority Accuracy Rate (PAR)

```
PAR = sessions_without_correction / total_sessions (rolling 14-day window)
```

Tracked in `pulse-priority-calibration.md`. Updated at end of each /pulse validation step. Used to determine phase transitions (see Phase 2 Transition below).

**Phase 2 Transition Criteria** — all must be true:
- PAR >= 0.85 over rolling 14-day window
- Minimum 10 /pulse sessions in that window
- No `missing-item` corrections in last 7 days
- No `suppression-error` corrections in last 5 days

Phase 2 changes: validation prompt only shown when fuzzy items exist, batch gating threshold drops from 40% to 25%, more aggressive effort-level suppression. Auto-revert to Phase 1 if PAR drops below 0.70 in any 7-day window.

### Loop Counting Boundary

Only Notes listed under `## Active Threads` in a Map count toward `loop_factor` and `open_loops`. Notes under sub-themes (`### Theory & Reference Docs`, `### Engine Development`, etc.) and Notes with `subtype: reference` are excluded. Minor Actions under `## Minor Actions` always count. This boundary — Map structure as source of truth for what constitutes an "open loop" — was formalized when extracting computation to `scripts/pulse-calc.py`.

### Important Items Display

Items are ranked by `effective_item_score` and displayed in two sections:
- **Important Items** (top ~12) — focused work
- **Between Tasks** (remainder up to ceiling of 20) — peripheral items for breaks, scheduling, errands

Per-effort cap of 3 on high/medium importance items prevents any single effort from dominating the list. Low-importance items flow uncapped — they serve as break-time tasks that surface naturally from lower-weight efforts.

### Recomputation

Weights are recalculated by `pulse-engine/scripts/pulse-calc.py`:
- At the start of each session (via `/pulse` Phase D)
- At session close (via `/close`)
- On demand (via `/recompute`)

The script outputs full component breakdowns. The agent renders the math so the user can challenge or adjust.

### Weight Examples

`work` (base 9/10 = 0.90) vs `side-project` (base 5/10 = 0.50):

| Scenario | work | side-project |
|----------|:-:|:-:|
| Normal week | 0.90 + 0.09 + 0.00 + 0.07 = **0.95** | 0.50 + 0.03 + 0.00 + 0.03 = **0.56** |
| side-project deadline | 0.90 + 0.09 + 0.00 + 0.07 = **0.95** | 0.50 + 0.03 + 0.20 + 0.03 = **0.76** |
| side-project sprint week | 0.90 + 0.03 + 0.00 + 0.03 = **0.96** | 0.50 + 0.12 + 0.00 + 0.10 = **0.72** |

---

## 8. Frontmatter Schemas

All frontmatter is agent-managed. These schemas are the contract between the vault files and agent operations.

### Map

```yaml
---
type: map
effort: <slug>                  # Canonical effort identifier
context_batch: <batch-name>     # must match a batch name in pulse-vault/user.config.yaml
priority_weight: <float>       # Computed. Never manually set. Uncapped sum.
base_priority: <1-10>          # Life-importance anchor. Rarely changes.
last_active: <YYYY-MM-DD>      # Last date this effort was touched
open_loops: <int>              # Count of active/waiting items linked to this Map
related_efforts:               # Cross-effort connections
  - <slug>
purpose: <string>              # One-line why this effort matters
aliases: [<alias>, ...]       # Flexible-match terms for this effort
tags: [<tag>, ...]
---
```

### Note

```yaml
---
type: note
subtype: <note|log|plan|reference>  # What kind of content note
efforts:                       # Which Maps this connects to (1 or more)
  - <slug>
status: <active|someday|waiting|done|archived>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
effort_level: <trivial|small|medium|large|null>  # Mental absorption required
timescale: <daily|weekly|monthly|quarterly|biannual|annual|null>  # Natural periodicity
due: <YYYY-MM-DD|null>         # Optional deadline
importance: <low|medium|high>  # Feeds loop_factor. Default: medium
depends: [<note-slug>, ...]    # Optional. Notes this item depends on for completion. Directional.
related: [<note-slug>, ...]    # Optional. Undirected peer associations (sibling concepts).
context_group: <batch-name|null>
tags: [<tag>, ...]
---
```

### Daily

```yaml
---
type: daily
date: <YYYY-MM-DD>
generated: true
efforts_touched: [<slug>, ...]  # Updated throughout the day
items_completed: <int>          # Filled at review
items_deferred: <int>           # Filled at review
close_complete: <true|false>    # Set by /close after successful defrag+recompute; read by next /pulse to skip redundant startup
---
```

### Capture (Inbox)

```yaml
---
type: capture
source: <voice|text|agent>
captured: <YYYY-MM-DDTHH:MM:SS>
triaged: <true|false>
efforts: [<slug>, ...]          # Filled during triage
context_deps: [<note-slug>, ...]  # Optional. Dependencies inferred from conversational context at capture time.
---
```

### Sati

```yaml
---
type: sati
subtype: emergence-log
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
---
```

---

## 9. Note Lifecycle

```
     ┌─────────┐
     │ capture │  Inbox item. Raw input, not yet classified.
     └────┬────┘
          │ triage
          ▼
     ┌─────────┐
     │ active  │  Work in progress. Appears in checklists and open loops.
     └────┬────┘
          │
     ┌────┴────┐
     ▼         ▼
┌─────────┐ ┌─────────┐
│ waiting │ │ someday │  Blocked / deferred. Tracked but not in daily lists.
└────┬────┘ └────┬────┘
     │           │
     ▼           ▼
┌─────────┐ ┌──────────┐
│  done   │ │ (reactivate) │  Can return to active at any time.
└────┬────┘ └──────────┘
     │ 7 days
     ▼
┌──────────┐
│ archived │  Out of active view. Searchable. Preserves history.
└──────────┘
```

### Transitions

| From | To | Trigger |
|------|----|---------|
| capture | active | Triage assigns efforts and status |
| active | waiting | Blocked on external dependency. Note what it's waiting on. |
| active | someday | Deferred indefinitely. Still valued, not urgent. |
| active | done | Work completed. |
| waiting | active | Blocker resolved. |
| someday | active | Revisited and prioritized. |
| done | archived | 7 days after completion. Agent handles automatically. |
| any | archived | Explicitly dropped or no longer relevant. |

### Waiting Escalation

| Threshold | Action |
|-----------|--------|
| 3 days waiting | Flagged in `/pulse` Escalation line and `/defrag` report |

Escalation is informational. Human decides: keep waiting, transition to someday, resolve blocker, or drop.

Tracking: Notes use `updated` field (set when status changes to waiting). Minor Actions use `waiting_since: YYYY-MM-DD` inline property (backfilled by defrag on first encounter).

---

## 10. Workflows

### Session Start (`/pulse`)

```
1. Read Maps/INDEX.md (precomputed priority landscape — agent-readable table)
2. Read all Map frontmatter (priority_weight, open_loops, last_active)
3. Read today's Daily note if it exists
3.5. Check close flag: read yesterday's Daily Note for close_complete: true
     — If true: skip steps 4+4.5 (trust cached weights), only scan Inbox for new items
     — If false/missing: proceed normally
     — Log skip decision to Session Log
4. Light defrag: auto-triage Inbox, reconcile Map counts, flag stale Maps, scan Minor Actions for overdue
4.5. Inline recompute: compute fresh weights (including Minor Actions urgency + calibration adjustments)
5. Present compact briefing: top priorities, housekeeping (inline), active batches with loop counts
   — Apply batch gating + effort-level suppression (omit efforts with 0 loops + stale + no deadlines)
   — Suppressed batches/efforts collapse to a single fold-line ("say unfold for full landscape")
5.5. Fuzzy item detection: flag low-confidence rankings after Focus
5.6. Validation prompt: "Does this Focus ordering match your priorities today?" (Phase 1: always; Phase 2: only with fuzzy items)
6. Full view on request: all batches, all efforts, top threads, stale Maps
7. Wait for direction
8. Build Daily Note from conversation — when the user indicates what they want to work on:
   — Pull focused items from indicated Maps, grouped by batch
   — Scan remaining Maps for time-sensitive/routine items (nothing falls through cracks)
   — Keep to 8-15 items. Present in chat for one confirmation pass, then write to file.
   — Subsequent Daily Note updates during the session happen silently.
```

### Full Landscape Audit (`/birdseyereview`)

```
1. Scan all Maps for open loops and active threads
2. Scan Notes for active/waiting items with approaching due dates
3. Group items by context batch
4. Sort batches by combined weight, items within by effort weight
5. Zero suppression — every batch rendered fully
6. Generate Daily/YYYY-MM-DD.md with all items linked to source Notes/Maps
7. Use for periodic reviews (weekly, after a break), not daily agenda setting
```

### Capture Flow (`/capture`)

```
1. Delegate to a background sub-agent (zero context disruption to main conversation)
2. Sub-agent creates Inbox/YYYY-MM-DD-<slug>.md with capture frontmatter
3. Confirm immediately (don't wait for agent): "Captured: [title]. Filing in background."
4. Auto-triage picks it up at next /pulse or /triage.
```

### Auto-Triage (`/triage`)

```
1. Find all Inbox items where triaged: false
2. For each: match content against Maps, assign efforts/status — no confirmation
3. Execute immediately:
   a. Create Note in Notes/ (or append to existing)
   b. Update relevant Map(s): add link, increment open_loops, update last_active
   c. Mark Inbox item triaged: true
4. Report summary: "Auto-triaged N items: [title] → [effort], ..."
```

### Deep Flow Override (`/focus`)

```
1. Resolve effort from flexible input
2. Load the Map
3. Show active threads, related notes, related maps
4. Log context switch in daily note
5. Update Map last_active (recency boost)
```

### End-of-Session Reflection (`/close`)

```
1. Read today's Daily note and Map activity
2. Present reflection narrative: what happened, what emerged, patterns
3. Flag items needing human attention (deferred 3+, gone dark, cross-effort tensions)
4. Invite optional reflection: "Anything else before I clean up?"
5. Apply any status changes the human volunteers
6.5. Session-end recompute: refresh weights with today's activity, Minor Actions, calibration
6. Update Daily note: End of Day section, counts
7. Auto-trigger /defrag (full pass)
7.5. Set close_complete: true in today's Daily Note frontmatter (signals next /pulse to skip redundant startup)
```

### Defrag (`/defrag`)

```
0. Triage gate (MANDATORY) — auto-triage Inbox, safety net sweep, checked-item sweep
1. Reconcile Map open_loops counts against actual active/waiting Notes
2. Auto-defer unchecked Daily items to tomorrow
3. Auto-mark checked Daily items as done in source Notes
4. Catch misclassifications (content vs assigned effort)
5. Flag stale items (active, past their timescale window — see threshold table in defrag skill)
5.5. Waiting escalation — flag waiting items where days_waiting >= 3
6. Identify merge candidates (overlapping notes in same effort)
7. Update all timestamps (last_active on Maps, updated on Notes)
8. Report summary
9. Log to Daily Note — append per-decision trace under ## Session Log section (see defrag skill for format)
```

### Priority Recomputation (`/recompute`)

```
1. Read all Maps
2. Scan Notes for urgency signals (due dates, stale waiting items)
3. Scan Minor Actions across all Maps for urgency signals
4. Calculate recency from Daily notes (last 7 days)
5. Calculate effort from Note update frequency
6. Compute raw weights
7. Apply calibration adjustments from Notes/pulse-priority-calibration.md
8. Update Map frontmatter, refresh Maps/INDEX.md, update Home.md Current Focus section
9. Present table with full breakdown (including Minor Actions + calibration columns) and change deltas
```

---

## 11. Dataview Integration

The vault uses the Dataview plugin for dynamic views. Queries live in two places:

### Embedded in Maps

Each Map has an inline query listing its linked notes:

```dataview
LIST FROM "Notes" WHERE contains(efforts, this.effort) SORT updated DESC
```

### Embedded in Home.md

Priority overview of all Maps:

```dataview
TABLE priority_weight, open_loops, last_active FROM "Maps" SORT priority_weight DESC
```

### Saved Queries (Queries/)

| Query | Purpose |
|-------|---------|
| Active by Effort | All active notes grouped by effort with counts |
| Open Loops | Active and waiting items sorted by staleness (oldest first) |
| Cross Effort | Notes linked to multiple efforts |
| Stale Items | Active notes past their timescale staleness window (default 14 days) |

---

## 12. Skills Reference

Skills are defined in `.claude/skills/` and invoked as slash commands.

| Skill | File | Trigger | Arguments |
|-------|------|---------|-----------|
| `/pulse` | `pulse/SKILL.md` | Session start | None |
| `/birdseyereview` | `birdseyereview/SKILL.md` | Full landscape audit (periodic reviews) | Optional: date |
| `/capture` | `capture/SKILL.md` | Quick capture | The thought to capture |
| `/triage` | `triage/SKILL.md` | Auto-process Inbox items | Optional: specific file |
| `/focus` | `focus/SKILL.md` | Enter deep flow on an effort | Effort name (flexible matching) |
| `/close` | `close/SKILL.md` | End-of-session reflection | Optional: date |
| `/defrag` | `defrag/SKILL.md` | Organizational cleanup | Optional: `light` or `full` |
| `/recompute` | `recompute/SKILL.md` | Refresh priority weights | Optional: effort spike |
| `/efforts` | `efforts/SKILL.md` | Manage effort lifecycle | `add`, `splinter <slug>`, `merge <slug> <slug>`, `review` |
| `/surfaceUncertainty` | `surfaceUncertainty/SKILL.md` | Surface thinking-trace uncertainty, competing frames, reification signals | None |

### Creating New Skills

1. Create directory: `.claude/skills/<name>/`
2. Create `SKILL.md` with frontmatter (`name`, `description`, `user-invocable: true`, `allowed-tools`)
3. Write the skill protocol in the markdown body
4. Add to this table and `README.md`

---

## 13. Design Decisions

Rationale for non-obvious choices, preserved for future reference.

| Decision | Rationale |
|----------|-----------|
| Flat Notes/ directory | Deep nesting makes LLM traversal expensive. Efforts are encoded in frontmatter, not folder paths. |
| Computed priority (not manual) | Manual priority rot. Computed weights reflect reality without maintenance burden. |
| Maps as source of truth (not a database) | Markdown files are human-readable, version-controllable, and Obsidian-native. No external dependencies. |
| Agent-managed frontmatter | Removes friction from capture. Ensures schema consistency. The user thinks; agent files. |
| Context batches (not time blocks) | Time blocking fails for creative/knowledge work. Batching by cognitive context respects how attention actually works. |
| Two-axis context batching (problem domain + mode) | Problem domain switching (reloading mental models, codebases, stakeholder context) is far more expensive than mode switching (analytical→creative). Capturing both axes makes batch boundaries more principled. |
| Batch soft-suppression | Low-value batches on the daily checklist force unnecessary context switches. Collapsing them to a single line keeps them visible without prompting action. |
| Inspiration override as first-class concept | Rigid systems get abandoned. Honoring impulse and energy produces better outcomes than forced compliance. |
| Wikilinks over markdown links | Obsidian graph view. Refactoring-safe (rename propagation). Shorter syntax. |
| 7-day done→archive window | Keeps completed items visible long enough to inform review, short enough to not clutter. |
| Auto-triage (no confirmation) | The cost of a misclassified note is low (defrag catches it), while N confirmation cycles impose real cognitive load at the worst moment — the transition back to work. |
| Reflection-focused review | End-of-day is lowest-energy time. Item-by-item decisions are the wrong ask. Narrative reflection surfaces insight; mechanical bookkeeping is delegated to defrag. |
| effort_level over effort_estimate | Fibonacci hours confused non-developers and were never consumed by the priority formula. effort_level (trivial/small/medium/large) captures mental absorption — what actually matters for planning — without false precision. |
| timescale field on Notes | The 7-day recency window creates a one-week memory horizon. Items with monthly or quarterly cadence drop off the radar unfairly. timescale lets defrag and pulse judge staleness relative to the item's natural rhythm, not a fixed window. |
| Defrag as separate skill | Separates thinking (human) from filing (agent). Triage and review shed their bookkeeping; defrag absorbs it and runs automatically or on demand. |
| Maps as sole effort source (no efforts.yaml) | efforts.yaml was a bootstrap seed that became a dead config file once Maps existed. Maps already contained effort metadata in frontmatter — efforts.yaml just duplicated it. One source of truth (Maps) with no intermediate config. |
| Single calibration Note (not distributed across Daily Notes) | Agent reads one file for full correction history. Distributed corrections across Daily Notes would require scanning 14+ files at every /pulse. Single file = O(1) lookup. |
| Minor Actions as first-class urgency signals | Real deadlines don't always have frontmatter. Bare-text items in Maps were invisible to the formula — items like "prep gear for an appointment (due: Friday)" had genuine urgency but zero formula weight. Minor Actions section gives incidentals a scannable home without Note overhead. |

---

## 14. Evolution Log

See [`EVOLUTION.md`](EVOLUTION.md) for the full change history.
