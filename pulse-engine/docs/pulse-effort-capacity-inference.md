---
type: doc
subtype: reference
template: true
efforts: [pulse]
created: 2026-04-15
updated: 2026-05-30
informs:
  - pulse-capacity-model
related:
  - pulse-intention-alignment-vectors
---

# Effort & Capacity Inference — Method and Baseline

> **Template / example doc.** This is the public engine reference the `/capacity` skill points at. The methodology, tier definitions, budget caps, multipliers, and formulas are real and load-bearing. The *numbers, dates, effort names, and day-by-day examples below are illustrative* — they show the shape of a baseline analysis you would run against your own vault, not anyone's actual data. Replace the example effort slugs (`alpha`, `cold-start`, `home`, etc.) with your own efforts and the example baseline figures with what your own `/capacity` backtests produce.

Framework for inferring per-item effort from existing vault data, the resulting capacity profile, and the agenda validation protocol built from both. A working baseline is derived by analyzing a multi-week window of completed items, Daily Notes, and session logs (the illustrative baseline below assumes ~35 days, ~100 completed items, ~33 Daily Notes, ~29 session logs).

## Context

PULSE's capacity model identifies the "effort-as-exertion" gap: items are treated as equal cost when they're not. A 3-hour deep architecture session and a 5-minute errand both count as "1 item completed." This doc formalizes what effort actually looks like across a vault and how to infer it from data already being captured.

The central observation from baseline analysis: **effort is not one dimension**. It decomposes into three distinct signals that move independently and interact nonlinearly.

## Three Dimensions of Effort

### Depth — sustained cognitive load per item

How much concentrated work an item required. Proxied by:

- **Note existence** — items with Notes are heavier on average than bare items
- **Note content scope** — line count, section count, subtype (plan > note > log > reference > capture)
- **Duration span** — created-to-updated delta on the Note (sustained engagement signal)
- **Cross-effort scope** — Notes with multiple efforts in frontmatter span more domains
- **Explicit `effort_level` field** — rare (present on a minority of traced Notes) but directionally accurate where it exists

Items range from 3-line bookmarks to multi-hundred-line strategic proposals. The strongest single signal for depth is Note existence + subtype + line count.

### Resistance — activation energy to start

How hard an item is to begin, independent of complexity. Proxied by:

- **Carry-forward count** — appearances on Daily Note agendas before completion
- **Late-completion pattern** — items completed late at night despite planning to front-load
- **Effort-level inheritance** — resistance is an effort-level property that colors every item in the effort (items in a low-pull volunteer effort inherit that effort's resistance; items in an externally-evaluated work effort inherit "maintaining appearances" pressure)
- **Explicit avoidance annotations** — session log notes like "4th carry — approaching avoidance threshold"

Resistance items get done, but at a cost: late nights, deferral of adjacent items, momentum requirements. They complete by deadline pressure, accumulated momentum, or reframing (e.g., delegating to agents as a way to engage without direct engagement).

### Load — ongoing drain from open state

Background cognitive/emotional weight an item imposes regardless of whether it's being actively worked on. This is the dimension least captured by existing signals. Proxies:

- **Sati density** in session logs (more Sati entries correlate with higher reflective engagement, often under load)
- **Somatic language** in end-of-day reflections (chest tightness, exhaustion, decompression)
- **Adversarial or physical-consequence waiting items** (a contractor dispute, a home-repair hazard, overdue items with team visibility)
- **Sleep-debt annotations**
- **Session character** when explicitly logged (decompression, zero-output)

Load accumulates across days and forces recovery periods. As an illustrative example: an adversarial dispute might carry only a moderate `priority_weight` (e.g. ~0.7) yet produce emotional weight disproportionate to that weight across many days, because the drain is ambient rather than scheduled.

## Inference Method

### Data sources

| Signal | Source | Availability |
|--------|--------|-------------|
| Item existed, completed, effort, date | Map `## Completed` sections + archived Notes | High |
| Type (finished/minor-action/delegated/effective) | Note frontmatter / Map annotation | Where annotated |
| Weight at completion | `Daily/cache/*-calc.json` (historical) | Where cache exists |
| Unblocked dependency | `depends::` annotations resolved during `/defrag` | Sparse |
| Note metadata + content scope | `Notes/*.md` + `Notes/archive/*.md` | For items with wikilinks |
| Carry-forward count | `Daily/*.md` agenda checkboxes across days | Requires fuzzy matching |
| Session character, somatic signals | `Daily/logs/*.md` Sati entries, end-of-day reflections | Present but unstructured |
| Capacity observations | `Daily/logs/*.md` Capacity Prediction entries + calibration log | Builds with each backtest |

All paths above are relative to `${PULSE_VAULT}` (default `pulse-vault/`).

### Inference rules

**Depth tier** (from the signals above):

- **Heavy** — Note with plan subtype + duration ≥ 7 days + line count ≥ 100 OR implemented same-day subsystems OR multi-day strategic work with stakeholder loops
- **Substantial** — Note exists with plan/note subtype + moderate scope OR carried ≥ 5 agendas OR cross-effort scope
- **Standard** — finished type, single-session, code PR / article / demo / meeting
- **Light** — minor-action type OR short description OR errand/admin
- **Minimal** — bookmark, reference stub, trivial log

**Resistance tier**:

- **High** — carry-forward ≥ 3 AND late-completion pattern OR effort-level resistance inheritance (low-pull volunteer effort, externally-evaluated work effort for cold-start items)
- **Moderate** — carry-forward 2 OR scheduled-deferred items (health appts, social scheduling)
- **Standard** — single-agenda completion, no carry-forward
- **Low** — intrinsic-pull items (system design, crisis response, deep reflection)

**Load dimension** (daily, not per-item): inferred from the day's session log patterns, not from completed items directly. Load is a state variable on days, modifying capacity for everything else.

### Known limitations

- **Delegated ≠ low effort.** Items marked `delegated` (via agent) may represent *higher* effort if the delegation mechanism itself was novel. Early multi-agent-orchestration items are a typical example — low personal execution, high orchestration cost.
- **Resistance is effort-level, not item-level.** Items in a resistant effort that look small in isolation inherit the effort's resistance. Scoring items independently loses this.
- **Load has no reliable proxy.** Sati density and somatic language capture it partially but inconsistently. This is the gap structured capture is designed to close.
- **Capacity ground-truth is thin early on.** Validation data for agenda sizing accumulates one backtest per day; the first weeks are directional only.

## Capacity Profile

Qualified through the three-dimension lens, not item counts (which hide everything).

### Depth capacity — high, concentrated

Sustained intense cognitive depth happens in concentrated windows (commonly a 2-3 hour evening block). One heavy-depth item per session is the shape — not multiple. Deep-single days (one batch, no external disruption) produce landmark output. Days with 6-7 "completed items" are almost always standard/light depth. **High item count is inversely correlated with per-item depth.**

Depth capacity is typically not the bottleneck.

### Resistance capacity — 1 per day with cost

High-resistance items complete, but under one of three conditions:
1. **Deadline forces it** — sprint pressure on an externally-accountable effort
2. **Momentum carries it** — resistance item follows a productive morning on other items
3. **Reframing removes it** — a "skillful discernment" reframe, or delegation as indirect engagement

The budget is **1 high-resistance item per day**. Asking for 2 produces deferral on both. Resistance cost is paid once per effort-session — the first item in a high-resistance effort is hard to start; subsequent items in the same effort flow.

### Load capacity — the actual bottleneck

Load accumulates across days and gates everything else. When low, depth is available and resistance is manageable. When high, both degrade.

Multi-day sprint pattern: 2-3 days heavy depth → 1-3 days recovery. This is the natural shape. Decompression clusters are rhythm, not failure.

Load is the dimension samatha practice appears to modulate most directly (see Load Dampeners below).

### Load sources — three distinct modes

Load isn't homogeneous. It arrives through three distinct pathways with different predictability and different response strategies:

**Baseline load** — physiological/state-based. Sleep quality, illness, energy level, hydration, diet. Present from the start of the day; mostly predictable; persists until the underlying state resolves. Captured by `sleep_quality` structured input. Slow-moving.

**Ambient load** — accumulated from ongoing situations. An adversarial dispute that's been active for many days. An overdue item with team visibility. A stuck waiting item with physical consequences. These are the "open loops that drain" — they don't require active engagement to consume cognitive bandwidth. Such a thread might carry only a moderate `priority_weight` yet produce load disproportionate to that weight because it is ambient, not scheduled. Predictable from the vault state; persists until the situation resolves.

**Acute load** — unforeseen SRSA trajectory misalignment events. **This is the signal of real engagement with the world, not a failure mode.** Acute load arrives because trajectories — yours and others' — actually meet: contractors, colleagues, family, strangers, systems not fully under your control. A day with zero acute load usually means you didn't engage with anything uncertain or adversarial. The goal isn't to prevent acute load (which would require disengagement); it's to have enough capacity to absorb it without collapse.

Sources:
- **Trajectory collision** with another person (e.g. a repair confrontation where a new inspection reveals a problem that escalates a passive waiting-item into an active adversarial pursuit mid-day, producing evidence that strengthens your position)
- **Alignment divergence discovered** in external parties (e.g. encountering unexpected defensiveness — a shared frame turning out to be unshared; the divergence itself is valuable calibration data about the audience)
- **Sudden realization** that a trajectory you were committed to isn't landing the way you modeled it
- **External imposition** of a new constraint (legal, medical, family obligation)

Dynamics:
- **Unpredictable** — agenda planning cannot account for it, but also doesn't need to prevent it
- **Transforms the day mid-stream** — a low-load morning can become a high-load afternoon when an acute event hits
- **Carries a tail** — cognitive residue persists for hours or the rest of the day even if the event itself was brief
- **Partially mediated by practice** — samatha appears to dampen the tail (stress noted but redirected rather than consuming the day) but doesn't prevent the initial hit, and shouldn't

**Acute vs ambient — the engagement vs avoidance trade**:

Acute and ambient load can produce the same total load with very different outcomes:

| Type    | Valence         | Movement                                                 | Cost                                        |
| ------- | --------------- | -------------------------------------------------------- | ------------------------------------------- |
| Acute   | Engagement cost | Moves things forward; produces information and decisions | Discrete, visible, often productive         |
| Ambient | Avoidance cost  | Extends situations; accumulates without resolution       | Continuous, invisible, usually unproductive |

A dispute in its passive waiting phase is ambient (draining without motion). The confrontation that activates it is acute (draining but productive — evidence gathered, a concession extracted). Same underlying situation, different load modes, different outcomes. **Acute load often converts ambient load into resolution.** Avoiding the acute event to prevent a load-spike usually preserves the ambient load indefinitely — a worse trade.

A canonical productive-acute-load day stacks two acute events (e.g. a repair confrontation plus an unexpected alignment-divergence encounter): the day's capacity shifts mid-stream, but both events produce real data and movement — one converts a stuck situation into active pursuit, the other calibrates understanding of audience resistance. Agenda planning couldn't have anticipated these, nor would it have wanted to prevent them.

**Implication for the budget vector**: load is not a single state variable set at the start of the day. It's a time-varying field with two component dynamics — slow-moving baseline + ambient, plus unpredictable acute spikes. The load multiplier in the budget arithmetic is an *expected value* given baseline + ambient; acute events are a variance term the validation protocol handles via buffer room (the 30% disruption tolerance question), not by trying to predict them. The target isn't low acute load — it's enough budget reserve to absorb acute events gracefully.

**Implication for practice**: samatha's contribution is load *absorption capacity*, not load *prevention*. A practitioner with strong load tolerance stays engaged with acute events, lets them produce their information and movement, and returns to baseline. A practitioner without that tolerance either avoids acute-producing situations (accumulating ambient load instead) or gets consumed by acute events when they arrive. Neither pre-event avoidance nor mid-event collapse produces the acute event's potential value.

**Dharma correspondence — apratiṣṭhita-nirvāṇa** (non-abiding nirvana): the bodhisattva position maps directly onto this engagement structure. Abiding in nirvana = avoiding acute events to prevent load spikes, accumulating ambient load as the cost of disengagement. Bound in samsara = consumed by each acute event, no absorption capacity. Non-abiding = engaged with trajectory collisions, present for them, not bound by their tail. Samatha is ground for non-abiding, not escape from it. This is the ethical/stance correspondence for why the design target is absorption capacity rather than load minimization.

### Interaction model

| Condition | Depth Available | Resistance Tolerance | Typical Output |
|-----------|----------------|---------------------|----------------|
| Low load, no resistance items planned | Full | N/A | 1 heavy item OR 5-6 standard items |
| Low load, 1 resistance item | Partial (resistance consumes some) | Manageable | Resistance item (late) + 2-3 standard |
| High load | Degraded | Collapses | Minor actions, closure, crisis response |
| Multi-day sprint → recovery | Depleted | Unavailable | Decompression (0-2 items) |

### Capacity Scenarios (elaborated)

The table above compresses the full dynamics. Each row unpacks into a distinct mode of engagement:

**Low-load day, no high-resistance items planned**

Depth capacity is fully available. This is where landmark work happens — a subsystem designed and implemented in one evening, an entire phase built in a single session, a session that produces many conceptual notes at once. The depth budget is **fungible within a day**: it can be spent on **1 heavy-depth item** (the evening window fully consumed) OR **5-6 standard-depth items** distributed across the day. Not both. Attempting both produces a half-built heavy item and a stressful standard list that compounds the next day's load. The trade is real — one heavy item eats the budget that 5-6 standard items would have eaten.

**Low-load day with 1 high-resistance item planned**

Depth capacity is available but partially consumed by the resistance cost. The resistance item gets done — usually late (a recurring late-night pattern on the resistant effort), usually after momentum-building on lower-resistance items earlier in the day — plus 2-3 standard items around it. A substantial-depth item can also fit, but not comfortably alongside a high-resistance item in the same day. Typical shape: 1 resistance item (completed late) + 2-3 standard items. The key constraint: **1 high-resistance item per day**. A second high-resistance item in the same day produces deferral on both, not completion of both.

**High-load day** (adversarial dispute active, sleep debt, sick, multi-stressor stack)

Depth and resistance capacity both degrade. Output shifts toward **minor actions, closure items, and crisis response** — work that advances state without requiring new cognitive load. The clearest illustration: a day that is sick + dispute-escalating + carrying a multi-day blocked item, where everything *clears* (backlog resolved) but zero new depth is initiated. The work is clearing the backlog, not opening new work.

Attempting deep or high-resistance work on high-load days doesn't just fail — it **compounds load for the next day** by adding deferred-item friction to existing load. The counterintuitive move is to pre-defer during agenda creation, not retroactively. A 3-item agenda of closure/resolution items completes cleanly on a high-load day; a 7-item agenda of ambitious work collapses and leaves residue that taxes tomorrow.

**Multi-day sprint → recovery cycle**

2-3 days of heavy-depth output followed by 1-3 days of recovery. This is the natural cycle, not a failure mode. A decompression cluster is correctly named "rhythm, not avoidance." Recovery days look like low-output administrative/family days — the load capacity is replenishing. Attempting sprint-level output during recovery produces exhaustion without progress.

The sprint produced the landmark; the rest completes the cycle. Forcing more sprint extends the recovery tail, not the sprint. A useful reframe: recovery days are not time *lost* to productivity — they are the mechanism by which the sprint becomes sustainable rather than destructive.

## Capacity as Budget Vector

The three dimensions don't compress to a single effort score. Capacity is a **vector** with coupled-but-distinct components:

```
state = (depth_used, resistance_used, load_multiplier)
```

Validation is two independent checks, not a single sum:

```
depth_used       ≤ depth_budget       × load_multiplier
resistance_used  ≤ resistance_budget  × load_multiplier
```

Both must pass. Either one failing collapses the day regardless of the other's margin.

### The two budgets

**Depth budget** — ~1.0 per day at low load. Item consumption:

| Tier | Depth cost | Items to fill budget |
|------|-----------|---------------------|
| Heavy | 0.7-1.0 | 1 |
| Substantial | 0.4-0.6 | 2 |
| Standard | 0.15-0.25 | 4-6 |
| Light | 0.05-0.10 | 10+ |

So one heavy item consumes the same depth as ~6 standards or ~10 lights. This is the fungibility within the depth dimension.

**Resistance budget** — ~1.0 per day at low load. Item consumption:

| Tier | Resistance cost | Items to fill budget |
|------|----------------|---------------------|
| High-resistance | 0.7-1.0 | 1 (strict cap) |
| Moderate-resistance | 0.3-0.5 | 2 (stackable within session) |
| Low/no resistance | ~0 | unbounded |

A high-resistance item fills the resistance budget AND consumes 0.3-0.5 of depth budget (cognitive engagement cost). The two budgets overlap at resistance items but are otherwise independent.

### Load as multiplier

Load is not a budget — it's a multiplier on both budgets:

| Load state | Multiplier | Effective depth | Effective resistance |
|-----------|------------|----------------|---------------------|
| Low (post-practice, good sleep) | 1.0 | 1.0 | 1.0 |
| Moderate | 0.7 | 0.7 | 0.6 |
| High (sick, adversarial dispute, sleep debt) | 0.4 | 0.4 | 0.3 (deadline-forced only) |
| Recovery | 0.1 | 0.1 | 0.0 |

### Why scalar compression fails

Three agendas with similar total-effort sums fail or succeed for different reasons:

| Agenda | Items | Total sum | Depth used | Resistance used | Outcome |
|--------|-------|-----------|------------|-----------------|---------|
| A | 2 heavy + 1 light | ~1.85 | 1.7-2.0 **over** | 0.0 | **Collapses on depth**; 1 heavy carries |
| B | 1 high-resistance + 4 standards | ~1.60 | 0.8 | 1.0 | **Near cap on both**, risky |
| C | 7 standards | ~2.10 | 1.4 slight over | 0.0 | **Works** — standards absorb disruption gracefully |

Agenda C has the highest total sum but works because depth is mildly over and resistance is untouched. Agenda A has lower total but fails because two heavies compete for one depth slot. The sum hides the structure.

**Nutritional-macros analogy**: you can hit your total-calorie target and be completely unbalanced on protein/carbs/fat. A scalar hides what actually matters. Capacity validation needs per-budget checks, not a total.

### Implications for the capacity script

The script should output a vector, not a scalar:

```json
{
  "depth_used": 0.75,
  "depth_budget": 1.0,
  "depth_ratio": 0.75,
  "resistance_used": 0.50,
  "resistance_budget": 1.0,
  "resistance_ratio": 0.50,
  "load_multiplier": 0.9,
  "status": "within_budget"
}
```

Agenda validation becomes: sum per-item contributions into each budget, apply load multiplier, check both constraints. Overflow in either dimension is a fail.

### Relationship to slot framing

Slots and budgets are the same idea at different resolutions:

- **"1 depth slot"** = up to 1.0 depth budget consumed
- **"1 resistance slot"** = up to 1.0 resistance budget consumed
- **"standard slots"** = the remaining depth budget after depth/resistance items are placed

Slots are the quick mental model for agenda conversation. Budgets are the arithmetic that makes slots concrete.

## Avoidance Patterns

Avoidance is a distinct signal from general resistance. The things that get avoided share characteristics that the resistance dimension alone doesn't capture:

**What gets avoided** (illustrative effort archetypes):
- **Externally-evaluated work items** — consistent late-night completion pattern; a "maintaining appearances" frame adds social-evaluative pressure beyond task weight; a "hard to start" dynamic explicitly flagged in logs
- **Low-pull volunteer engagement** — multi-carry tracking on a recurring obligation, avoidance threshold explicitly named in session logs; even an agent-delegation mechanism can function partly as indirect engagement
- **Health appointments** — blood work, checkup, dermatologist; 4+ agenda appearances, no deadline, no external accountability
- **Administrative enrollments** — program sign-ups carried across multiple agendas, still open
- **Interesting-but-never-started experiments** — an appealing idea deferred on each agenda appearance

**What doesn't get avoided**:
- **Intrinsic-pull systems work** — design and build work you're drawn to
- **Deep design sessions** — intrinsic pull
- **Crisis response** — physical consequences force engagement

**The common thread in avoided items**: not complexity. The hardest *completed* items (a major architecture separation, a governance proposal, a high-stakes meeting prep) get done. Avoidance targets are either:
1. **Externally accountable but emotionally loaded** (team visibility, "maintaining appearances")
2. **Not externally accountable at all** (volunteer, health, admin enrollments — no one is waiting)

A dispute thread is the telling exception — externally loaded, but physical consequences (e.g. a home hazard) force engagement despite high affective cost.

## Resistance Completion Modes

High-resistance items complete under exactly three conditions:

1. **Deadline forces it** — sprint pressure on an externally-accountable effort, a filing due date
2. **Momentum carries it** — resistance item follows a productive morning on other items
3. **Reframing removes it** — "procrastination was actually skillful discernment"; delegating to agents as indirect engagement

The budget is **1 high-resistance item per day**. Within a single session, resistance cost is paid once per effort: the first item in a high-resistance effort is hard to start; subsequent items in the same effort flow (a typical pattern: three items in a resistant effort completed in sequence after the first broke through).

## Agenda Validation Protocol

Use before committing to an agenda — the frame that replaces item-counting.

### Core principle: composition beats item count

The agenda shouldn't count items — it should account for the depth/resistance/load mix. Item count is a misleading metric because effort is not uniform across items. Two agendas with the same item count can have wildly different effort loads; two agendas with different item counts can represent the same actual capacity use.

An item's weight in the agenda isn't its visual size, it's the **slot it occupies** in the depth/resistance budget:
- **Heavy-depth items** take the single daily depth slot
- **High-resistance items** take the single daily resistance slot
- **Standard/light items** take general capacity that absorbs disruption gracefully

A well-sized agenda respects the slots. An overloaded agenda competes for scarce slots and produces deferral.

**Concrete examples**:

| Agenda | Composition | Verdict |
|--------|------------|---------|
| 5 items, overloaded | 2 heavy-depth + 1 high-resistance + 2 standard | **Fails** — two heavies compete for one depth slot; resistance item competes with both for cognitive bandwidth |
| 7 items, fine | 1 substantial-depth + 1 moderate-resistance + 5 standard/light | **Works** — one slot occupied in each scarce dimension; standards absorb disruption |
| 3 items, appropriate for high-load | 3 closure/resolution items | **Works** — small count but matches degraded capacity; no new depth attempted |
| 5 items, well-calibrated for normal day | 1 substantial-depth + 1 moderate-resistance + 2-3 standard | **Works** — baseline shape for productive non-sprint day |
| 10 items, wishlist | Mixed, spanning 5+ efforts | **Fails** — batch spread alone guarantees under-delivery regardless of composition |

The validation question isn't "can I do 5 things today?" It's "which dimension does each thing occupy, and do the occupied slots fit the day's load state?"

### Questions to evaluate a proposed agenda

1. **Depth budget**: How many heavy/substantial items? (More than 1 = overbooked)
2. **Resistance budget**: How many high-resistance items? (More than 1 = deferral likely)
3. **Load state today**: What's load coming in? Is today already constrained?
4. **Batch spread**: How many batches? (4+ = wishlist, not agenda)
5. **Disruption tolerance**: If the day gets derailed 30% in, does the agenda degrade gracefully? (Tiered agendas do; flat lists don't)

### Well-calibrated agenda (baseline shape)

For a low-load day:
- **Active now**: 1 substantial-depth item (or 1 high-resistance item, not both)
- **Main focus**: 2-3 standard-depth items
- **Don't-drop**: 1-2 time-sensitive items (appointments, meetings)
- **If time/energy**: 2-3 light items that gracefully defer

Total: 6-8 items planned, 4-5 realistic, 1-2 gracefully deferred.

For a high-load day:
- **Active now**: 1 closure/resolution item (not new depth)
- **Main focus**: 1-2 standard items with momentum
- **Don't-drop**: only what's externally forced
- **Everything else**: pre-defer

Total: 3-4 items. Expecting 2-3 completed.

### Warning patterns

- Agenda with 10+ efforts touched → wishlist, not agenda
- Agenda with 2+ heavy-depth items → overbooked
- Agenda with 2+ high-resistance items (same effort) → one will carry
- Agenda ignoring load state ("I'll push through") → collapse risk

### Arithmetic check

The quick mental calculation for agenda sizing:

1. **Estimate load multiplier** from samatha/insight/sleep signals and known external stressors (active dispute, overdue-with-visibility items, illness). Low=1.0, Moderate=0.7, High=0.4, Recovery=0.1.
2. **Sum depth cost** across all items using tier midpoints (heavy 0.85, substantial 0.50, standard 0.20, light 0.08). Compare to `1.0 × load_multiplier`.
3. **Sum resistance cost** (high 0.85, moderate 0.40, low 0.0). Compare to `1.0 × load_multiplier`.
4. **Both must be within budget**. Overflow in either dimension is a fail — you can't trade depth slack for resistance overflow or vice versa.

If one budget is 80%+ used, the agenda is at the edge. If either is over 100%, drop items until both fit. Drop from the dimension that's overflowing, not just by item count.

## Load Dampener Signals

Structured captures that formalize load inference and test the practice hypothesis.

### samatha_minutes (daily)

Capture in Daily Note frontmatter:
```yaml
samatha_minutes: 15
samatha_quality: high
```

Hypothesis: practice minutes correlate with **load tolerance**, not throughput. Days with practice are not more productive — they degrade less under load. Samatha modulates load *absorption capacity*.

Baseline observation (illustrative, from a post-practice-restart window):
- Qualitative shift in Sati entries (retrospective reframe → real-time course correction)
- Somatic awareness appeared ("chest tightness", "smriti as detection dye")
- High-load days didn't collapse (sick + dispute escalation + a multi-day blocked item, yet the backlog still cleared)
- Pre-practice high-load days consistently collapsed (a dispute-consumed 0/7 day; a sleep-debt + deferral day)

The capture pattern: minimum 15 min default, 20/30 min annotations when longer. Zero when missed. The zero is as informative as the positive — miss-days correlate with known disruption (a chaotic day, a social-drinking day).

### insight_minutes (daily)

Capture in Daily Note frontmatter:
```yaml
insight_minutes: 5
insight_quality: good
```

Hypothesis: insight practice modulates the **resistance budget**. Insight thins the hindrances across life, reducing the activation energy for resistant items. Samatha enables insight; insight reduces resistance. The pair is the unit — capture both. (This is a refinement of the original samatha-only model: samatha → load tolerance, insight → resistance reduction.)

### sleep_quality (daily)

Capture in Daily Note frontmatter:
```yaml
sleep_quality: good  # or: poor, fair, excellent
```

Or numeric if preferred:
```yaml
sleep_hours: 7.5
sleep_quality_self_report: 7  # 1-10
```

Sleep debt is often informally annotated ("low energy from sleep debt"). Structured capture lets the capacity script correlate sleep → load → same-day degradation patterns.

### The dual purpose

The agenda validation conversation at the start of each day naturally surfaces load state. Asking "what's load today?" prompts the samatha, insight, and sleep inputs — not as a tracking burden, but as inputs to a decision already being made. The validation protocol doubles as the capture mechanism.

## Informs

> The `[[wikilink]]` targets below are illustrative — wire `informs:` to the actual notes in your vault that consume this framework.

- [[pulse-capacity-model]] — the capacity script spec and architecture reference this framework for inference rules

---

# Baseline Analysis (illustrative)

> Everything below this line is an **example reference dataset** that shows the *shape* of a baseline analysis. The dates, effort slugs, item names, and counts are illustrative — generated to teach the methodology, not to report real activity. Run the same analysis against your own vault to produce your own baseline; expect the *structure* (two budgets, a load multiplier, burst-and-rest rhythm, tier consumption rates) to hold while the *numbers* shift to fit you.

The illustrative window: ~35 days, ~100 completed items, ~33 Daily Notes, ~29 session logs, a handful of capacity-log entries.

## Budget Calibration (the quantitative baseline)

The calibrated numbers that come out of a ~35-day analysis. These are the example baseline — the items and daily profiles below are the (illustrative) evidence; these numbers are what such evidence produces.

### Observed daily totals by mode

| Day mode | Total effort range | Depth used | Resistance used | Composition example |
|----------|-------------------|------------|-----------------|---------------------|
| Recovery | 0.0-0.3 | 0.0-0.2 | 0.0 | 0-2 light items |
| High-load | 0.5-1.2 | 0.3-0.7 | 0.0-0.5 | 1 closure/resistance + 2-3 standards/lights |
| Normal low-load | 1.0-1.8 | 0.6-1.0 | 0.0-1.0 | 1 substantial OR 1 resistance + 2-4 standards + lights |
| Sprint day | 1.8-2.5 | 0.9-1.2 **over** | 0.0-0.5 | 1 heavy + momentum items (produces recovery debt) |

### Budget caps (low-load baseline)

- **Depth budget**: ~1.0 per day
- **Resistance budget**: ~1.0 per day
- **Sustainable daily total**: ~1.4 effort units averaged
- **Weekly total**: ~8-10 effort units (5-6 active days at ~1.4 + 1-2 recovery days at ~0.1)

### Tier consumption rates (midpoints)

**Depth cost per item**:
- Heavy: 0.85 (range 0.7-1.0)
- Substantial: 0.50 (range 0.4-0.6)
- Standard: 0.20 (range 0.15-0.25)
- Light: 0.08 (range 0.05-0.10)

**Resistance cost per item**:
- High-resistance: 0.85 (range 0.7-1.0)
- Moderate-resistance: 0.40 (range 0.3-0.5)
- Low/no resistance: 0.0

**Load multipliers**:
- Low: 1.0
- Moderate: 0.7 (depth) / 0.6 (resistance)
- High: 0.4 (depth) / 0.3 (resistance)
- Recovery: 0.1 (depth) / 0.0 (resistance)

### Why these numbers are rough

These midpoints are approximations fit to ~35 days of qualitative observation. They sharpen with more data — particularly once `samatha_minutes`, `insight_minutes`, and `sleep_quality` are structured captures that allow load-multiplier and resistance-budget calibration against real throughput rather than post-hoc inference. The tier boundaries are also fuzzy: a "standard PR review" vs "hefty PR review" differ in depth cost but both sit in the standard tier.

Treat these as v1 calibration. The shape (two budgets, load multiplier, rough consumption rates) is load-bearing; the exact midpoints refine with each backtested day.

### Imbalance failure examples (illustrative)

Three agenda types that fail differently despite similar totals:

| Day | Planned | Composition | Total sum | Depth | Resistance | Outcome |
|------|---------|------------|-----------|-------|------------|---------|
| Example A | 7 items | Mixed with 2 resistance (work US1, US2) + dispute + meeting prep | ~1.9 | 1.1 | 1.5 **over** | 0/7 — resistance overload + dispute took the day |
| Example B | 15 items | Spread across 10 efforts | ~2.2 | 0.9 | 0.4 | 7/15 — batch-spread killed it, not total sum |
| Example C | 7 items (Sunday) | 7 minor actions | ~1.1 | 0.6 | 0.0 | 7/7 clean close |

Same nominal 7-item agenda, wildly different outcomes. The vector check predicts this; the sum alone doesn't.

## Item Inventory by Depth Tier (illustrative archetypes)

### Heavy (sustained, multi-day, high-complexity)

| Item archetype | Effort archetype | Signals |
|------|--------|---------|
| Multi-function architecture separation — designed + implemented in one evening | system | 176-line Note, plan subtype, design+code in 1 day, implemented field |
| Governance/policy proposal with mid-course correction | community | 17-day span, 7 sections, political navigation, stance shift |
| Week-long strategic prep for a high-stakes meeting | work | 7-day span, plan subtype, 6 sections, boundary strategy |
| Full phase build — workstream split, frontend, DB, migration | system | 9 items in one session, evening sprint |
| Multi-week physical crisis management (repair/dispute) | home | 19-day span, 10 open loops, physical labor + legal + contractors |
| Annual taxes + amended prior year — financial complexity with deadline | maintenance | 23-day span, due date, amended-return discovery |

### Substantial (multi-session or significant single-session)

| Item archetype | Effort archetype | Signals |
|------|--------|---------|
| Multi-agent workflow orchestration design | system | 153-line ref doc, 7 sections, architectural design |
| Automate scoring + verify leaderboard (via agents) | volunteer | Delegated but orchestration was the hard work — proving ground for new system |
| Org-specific proposal sections | work | Part of a 251-line Note, plan subtype, high importance |
| Diagnose circular logic, propose architectural changes | system | Single-day but deep analytical work, plan subtype, high importance |
| Build demo → integration + POC frontend | work | Carried 5 agendas, evolved scope mid-carry |
| User-story PRs pushed and approved | cold-start | Carried 7 days, multiple PRs |
| Overnight build spec + execution | side-project | High-pressure 1-day deadline, 7-section spec |
| CI/CD card — bare minimum for weekend | cold-start | Carried 4 agendas, explicit avoidance pattern, completed while sick |
| Recurring-obligation scoring published | volunteer | **5 carries**, explicit avoidance threshold |

### Standard (single-session finished items)

Work PRs (articles, cards, audits, user-story PRs, CI/CD), writing articles, volunteer comment system + picks, proposal sections, hardware install, a student meeting, an issue-reframing resolution, a public-extraction task, tech-decision notes.

### Light (minor actions, quick admin)

Dishes, groceries, cooked meals, stretch + reading, basement prep, parts assembly, social links, subscription setup, bottle returns, supply returns, attending an event, vendor calls.

### Minimal

A 4-line reference bookmark.

**Note on "delegated"**: early agent-delegated volunteer items are reclassified from Minimal → Substantial after review. Delegation of a novel mechanism + volunteer-project avoidance + compounding resistance across the effort shifts these into Substantial despite their surface appearance.

## Per-Effort Aggregates (illustrative)

| Effort archetype | Total Done | With Note | Bare | Avg/Active Day | Top Type | Carry-Fwd Items |
|--------|-----------|-----------|------|----------------|----------|-----------------|
| home | 41 | 1 | 40 | 2.3 | minor-action | dispute (11d!) |
| cold-start | 20 | 0 | 20 | 1.8 | finished | User story 1 (7d), CI/CD (4d) |
| system | 16 | 8 | 8 | 1.1 | finished | — |
| volunteer | 13 | 0 | 13 | 1.6 | mixed (3 delegated) | Scoring (5d) |
| writing | 8 | 2 | 6 | 1.3 | finished | — |
| family | 6 | 0 | 6 | 1.0 | minor-action | An event (6d) |
| work | 5 | 3 | 2 | 1.0 | finished | Demo (5d) |
| side-project | 4 | 1 | 3 | 1.0 | finished | Site live (6d) |
| maintenance | 3 | 1 | 2 | 1.0 | minor-action | — |
| community | 2 | 1 | 1 | 1.0 | finished/effective | — |
| practice | 2 | 0 | 2 | 1.0 | minor-action | — |

Interpretation: **home** = high-frequency low-depth-per-item + high cumulative load. **system** = low frequency, high depth, most Notes. **cold-start** = carry-forward leader for discrete work items; resistance signature. **volunteer** = effort-level resistance inheritance.

## Carry-Forward Inventory (illustrative)

| Item archetype | Days Carried | Resolution | Why It Resisted |
|------|-------------|------------|-----------------|
| Adversarial dispute (home) | 11 | Ongoing | External + adversarial + escalating |
| User story 1 (cold-start) | 7 | Completed | Code PR sustained focus |
| Social event (family) | 6 | Completed | Low urgency, scheduling |
| Side-project site live | 6 | Completed | Scope underestimated |
| Volunteer scoring | 5 | Completed | **Explicit avoidance tracking** |
| Build demo | 5 | Completed | Scope evolved mid-carry |
| CI/CD card (cold-start) | 4 | Completed | Disruption + avoidance |
| Meeting prep | 5 | Completed | Strategic complexity |
| Taxes | 4 | Completed | Administrative friction |
| Health appointments | 4+ | Unresolved | Scheduling, no deadline |
| Program enrollment | 4 | Unresolved | Admin, low-stakes |
| Interesting POC | 3 | Deferred | Interesting but never starts |
| Cook for a guest | 3 | Completed | Scheduling |
| Prep basement | 3 | Completed | Physical labor required |
| Plumbing check valve | 3 | Completed | Physical + technical |
| Community invites | 2 | Unknown | Dropped from agendas |
| Fix a DNS record | 2 | Completed | Technical friction |
| Volunteer picks | 2 | Completed | Volunteer resistance |
| Stretching + walk | 1 | Deferred | — |
| Supply returns | 2 rounds | Completed | Physical errand |

Three distinct causes of carry-forward — **complexity**, **external dependency**, **low-urgency deferrability** — produce the same raw count but represent different effort profiles.

## Pattern Findings (illustrative)

### Context-switch cost (nonlinear)

| Batch Spread | Days | Avg Completed | Avg Completion Rate |
|--------------|------|---------------|---------------------|
| 1-2 batches | 12 | 3.7 | 75% |
| 3 batches | 12 | 4.2 | 68% |
| 4+ batches | 9 | 3.4 | 53% |

3 batches is the sweet spot, not 1-2. But the highest-output days are 2-batch deep-single days — the correlation isn't linear.

### Burst-and-rest rhythms

| Effort archetype | Max Burst | Avg Burst | Max Gap | Pattern |
|--------|-----------|-----------|---------|---------|
| system | 10 days | 4.2 days | 4 days | Long sprints, short rests |
| cold-start | 5 days | 2.8 days | 8 days | Short bursts, long gaps |
| home | 7 days | 3.1 days | 6 days | Crisis-driven bursts |
| volunteer | 3 days | 1.5 days | 9 days | Sporadic, agent-delegated |
| writing | 4 days | 2.0 days | 14 days | Single sprint, then dormant |

### Agenda sizing reality

| Agenda Size | Occurrences | Completion Pattern |
|-------------|-------------|-------------------|
| 1-4 items | 5 days | Almost always hit — best-calibrated |
| 5-7 items | 10 days | 60-80% — disruptions absorbed |
| 8-9 items | 6 days | 25-63% — generates carry-forward |
| 10-15 items | 3 days | 47-60% — wishlist, not agenda |

## High-Load Day Comparison (Pre vs Post Practice — illustrative)

| Day | Load | Practice? | Depth | Resistance | Load Effect |
|-----|------|-----------|-------|------------|-------------|
| Dispute day | Max | No | Zero attempted | Zero overcome | **Collapsed everything** |
| Sleep-debt day | Moderate | No | Continuation only | Immediately abandoned | **Eliminated friction tolerance** |
| Disruption day | High | Yes | Standard | 1 deferred, 1 engaged productively | **Fragmented but navigated** |
| Triple-stress day | High | Yes | One substantial (a PR review) | A hard email taken | **Acknowledged and redirected** |
| Sick + dispute day | Max | Yes | None new, closure focus | **4-day blocked carry broken** | **Active load reduction** |

Pre-practice: load collapses depth and eliminates resistance capacity entirely.
Post-practice: load degrades depth but doesn't eliminate it; resistance is still overcome even on the highest-load days; the relationship to load shifts from endurance to engagement.

## Post-Practice Qualitative Shifts (illustrative)

Practice period after a restart (small sample). Observed changes:

- **Sati density**: increased dramatically (multiple entries on a single day vs sparse pre-practice)
- **Sati quality**: shifted from retrospective reframe ("procrastination was skillful discernment") to real-time course correction ("trust-first principle corrected premature optimization three times")
- **Somatic awareness**: appeared for the first time (chest tightness, "smriti as detection dye")
- **Capacity estimation**: the first predictive estimate in the dataset was directionally accurate
- **Recovery window**: tentatively shortened (2 days post-sprint vs 4 days pre-practice)

What didn't change: the late-night cold-start pattern persisted, overplanning continued, health-appointment avoidance unresolved.

## Session Log Signatures

Empirically-derived fingerprints (illustrative). Useful for retroactive day-type inference.

### High-effort day signature
- Section count ≥12, file size ≥10KB
- Build/Design/System Evolution sections present (unique to high-effort days)
- Multiple Recompute blocks (2-3 per day)
- Sati reflections present
- Evening-weighted time spans — actual build work in the evening window
- Multiple Startup blocks indicate iterative build-test-refine
- Explicit effort observations: somatic signals, emotional weight, sleep debt, avoidance detection

### Low-effort day signature
- Section count ≤5, file size ≤8KB
- Only Startup + Inline Refresh + Defrag blocks — no Build/Design/Progress/Completions/Sati
- Zero or one Recompute — weights barely move
- "Checkpoint only" closes
- No evening session
- Effort touches are administrative (date corrections, waiting-status changes)

### Broad-shallow signature
- High section count (12-17) but moderate file size (11-12KB) — many small blocks rather than few dense ones
- Many efforts touched (7-10)
- Multiple light defrags (quick check-ins, not deep structural work)
- Corrections blocks appear (many items touched lightly, some wrong)
- Completions are external (meetings, visits, errands) rather than code/design artifacts

### Conflict/tension day signature
- Moderate section count (7-12) with external disruptions explicitly logged
- Deferred items present with named cause ("repair derailment")
- Emotional/somatic Sati reflections
- Weight volatility in the affected effort within the same day

## Temporal Rhythm (illustrative)

Daily cadence reconstructed from timestamped session log entries:

- **Morning**: Startup → Inline Refresh → Pulse Briefing → Priority Validation (15-30 min)
- **Midday gap**: No PULSE activity (day job, life)
- **Evening**: The actual session — build, design, completions
- **Close**: Recompute → Defrag → Sati (when present)

High-effort days extend the evening window and add density within it. Low-effort days either skip the evening entirely or reduce it to a single defrag. The most intense sessions show 2-3 hours of continuous dense creation in the evening; the build-test-iterate pattern shows many short cycles instead.

Explicit duration annotations are extremely rare — the vault doesn't track time-on-task; the cadence must be reconstructed from section timestamps.

## Practice Cadence Observed (illustrative)

Samatha practice recommitted after a gap. A couple of days missed (a chaotic day, a social-drinking day), then consistent with occasional misses.

Session lengths: predominantly 15 min (the minimum set), with occasional 20- and 30-min sessions. Miss-day information is as signal-bearing as practice-day information — miss-days correlate with known disruption vectors (social drinking, chaos). Structured capture should preserve zeros.

## Known Gaps

- Capacity ground-truth is thin until enough backtested days accumulate
- A small post-practice sample is too few for causal claims
- Load signal is qualitative only — Sati density and somatic language, no structured capture yet
- No time-on-task data at the item level anywhere in the vault
- `effort_level` field present on only a minority of archived Notes
- Carry-forward detection requires fuzzy matching across Daily Notes — automation-pending
- An explicit `### Context Switch` section type was abandoned early; context switches are now inferred from startup multiplicity or section-type transitions

---

## Sati — Emergence Observation

**The analysis that produces this framework is itself a system win.**

Several weeks of rich content logging — Daily Notes with agendas, Session Logs with timestamps and Sati entries, Map completed sections with strikethrough dates, archived Notes with duration spans, capacity log entries with qualitative observation, a priority calibration log — are sufficient to surface a **multi-dimensional model of effort that was invisible before the analysis began**. The methodology does not exist pre-analysis; it emerges from the data.

Several moments in the dyad conversation demonstrate the system critiquing itself:

- An initial effort classification treated `delegated` items as minimal effort. The correction — that delegation of a novel mechanism plus volunteer-project avoidance produces *substantial* effort — came from reading the Notes (a 153-line orchestration design doc created the same day as the "minimal" delegations). The data corrected the frame.

- An initial capacity analysis defaulted to item-count throughput. The correction — that plans are made to fail and completion is not the measure — came explicitly. But the reframe through depth/resistance/load was only possible because the conversation had *already established those dimensions*. The framework built up incrementally across the conversation enabled its own application.

- The load dimension emerged as "the dimension least captured by existing signals" — which is why samatha minutes, insight minutes, and sleep quality were proposed as structured capture. The gap was visible precisely because the other dimensions had been concretely mapped.

- The post-practice shift was detectable because pre-practice data existed for contrast. Without weeks of pre-practice logging, the Sati density increase, somatic awareness appearance, and load-tolerance shift would have been unverifiable claims rather than observable patterns.

**What this means for the system**: the rich logging that sometimes feels like overhead is the substrate for this kind of reflective analysis. Daily Notes with agenda checkboxes enable carry-forward detection. Session Logs with Sati entries enable load inference. Archived Notes with created/updated dates enable duration-span signals. Even a sparse capacity log provides ground-truth validation that anchors the depth/resistance/load interpretation.

The lesson is **not** that more logging is needed. The lesson is that **the existing logging shape, continued with discipline, produces increasingly useful analysis the longer it runs**. A ~35-day baseline is already rich enough to derive a framework. A 90-day baseline with structured samatha/insight/sleep capture will be dramatically richer.

Logged as a Sati observation: the system now has a tool for looking at itself that the system's own logging produced. That's the isomorphism working in both directions — PULSE surfaces the work, and the surfaced work surfaces PULSE.
