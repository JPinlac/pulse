---
name: capacity
description: Manual capacity backtest — re-run capacity sizing against a confirmed agenda. Grades raw sleep/practice prose with a Sonnet grader (per the rubric), writes graded JSON, then runs pulse-calc.py --capacity-input for the budget vector, count range, binding constraint, and flags. /pulse sizes the proposal inline (step 3.5); /capacity is the on-demand re-run against the committed set.
user-invocable: true
model: sonnet
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
srsa: Sense+Route+Surface+Act
---

## Capacity Backtest (manual)

`/pulse` capacity-sizes the day's draft **inline** during the proposal build (its step 3.5). `/capacity` is the **on-demand re-run** — backtest a *confirmed, committed* agenda against the day's capacity signals, mid-day or whenever the agenda has been edited since it was first sized. Same two-stage pipeline, run against the committed set instead of the candidate pool.

The agenda is built from intuition and dyadic negotiation; this protocol applies capacity math as a **backtest, not an input** — sizing and selection are independent signals, and collapsing them conflates two things the calibration record needs kept apart.

**Precondition**: an agenda exists in today's Daily Note. If none, respond: *"No agenda in today's Daily Note. Build the agenda first (`/pulse` → confirm direction), then run `/capacity`."*

### The two-stage pipeline

```
raw sleep/practice prose
  → Stage A: Sonnet grader sub-agent (rubric) → graded JSON
  → written to Daily/cache/YYYY-MM-DD-graded.json
  → Stage B: pulse-calc.py --capacity-input <graded.json>
  → budget vector · count range · binding constraint · flags
```

The division is strict: **the grader does zero arithmetic** (tiers, tags, day-context flags only); **the script does all arithmetic** (load derivation, multipliers, per-item costs, budgets, count range). Neither stage does the other's job.

**Reference docs** (read once per session):
- `pulse-engine/docs/pulse-capacity-rubric.md` — the versioned Stage-A grader contract and graded-JSON output shape. Canonical for tier vocabularies, tags, and day-context flags.
- `pulse-engine/docs/capacity-proposer.md` — the capacity proposer's design/operating guide (load model, layers, the graduation gate).

### Sense — Gather Raw Signals

**Step 1 — Parallel reads** (all independent, read simultaneously):

| Source | What to extract |
|--------|----------------|
| Today's Daily Note | **Committed agenda items** (the set to backtest); capacity frontmatter: `sleep_hours`, `sleep_quality`, `samatha_minutes`, `samatha_quality`, `insight_minutes`, `insight_quality`; `load_state` |
| Recent Daily Notes (last 2–3 days) | Sleep/practice frontmatter, `load_state`, completions/deferrals — the multi-day recovery trajectory |
| Recent session logs (last 2–3 days) | Prior `CAPACITY-FROZEN`/`CAPACITY-VERDICT` rows — running backtest accuracy and phase context |
| Today's cache (`Daily/cache/YYYY-MM-DD-calc.json`) | Due/deadline items, waiting items — ambient load sources |

The multi-day window is what lets the grader set `day_context` (`sprint_tail`, `cold_start_days`, `recovery`) and `sleep_3day_avg` / `sleep_trend`. A single day can't distinguish "start of a sprint" from "mid-recovery"; the window shows the arc.

**If sleep/practice not in frontmatter**: ask the user for a raw check-in, in their own words —
- Sleep: hours and how it felt (e.g. *"6.5, kept waking"*)
- Concentration practice (samatha): minutes and depth (e.g. *"15 min, settled but not absorbed"*)
- Insight practice: minutes and quality (e.g. *"5 min, one clear noticing"*)

Write the raw prose to today's Daily-note frontmatter under the field names above (`sleep_hours`, `sleep_quality`, `samatha_minutes`, `samatha_quality`, `insight_minutes`, `insight_quality`). **Never fabricate a sleep number** — a missing sleep signal means the day's capacity is *skipped*, and an invented number poisons the calibration substrate. These field names match the shipped code and rubric; do not rename or invent new ones.

**The model, plainly.** Concentration practice modulates **cognitive load tolerance** — a settled mind carries more attentional load without offsetting sleep debt, and the absorption ladder (`access → sub-j1 → j1-j3 → j4-plus`) graduates that dampener, with `j1-j3` the strongest and deeper attainments left deliberately unmapped (`deep-attainment-watch`). Insight practice thins resistance across life; in the current rubric it is a **candidate** signal — graded honestly, logged (`insight_lift_candidate`), but not yet given arithmetic weight. The practice dampener is cognitive-specific: it must **never** soften an embodied/physical-relational risk. Those axes are independent and graded independently.

### Route — Stage A: Grade (Sonnet sub-agent)

**Step 2 — Dispatch a Sonnet grader sub-agent** (`model: "sonnet"`) per `pulse-engine/docs/pulse-capacity-rubric.md`.

- **Grader input**: the raw sleep/practice prose + the **committed agenda items** (`id`, `label`, `effort`) + the multi-day trajectory context from Step 1.
- **Grader output**: exactly one graded-JSON object per the rubric — nothing else. It carries `sleep` / `samatha` / `insight` tiers (closed vocabularies), per-dimension `confidence`, `day_context` flags, `sleep_3day_avg`, `sleep_trend`, per-item `{layer_hint, depth_tier, resistance_tier, tags}`, and `raw_prose` echoed verbatim. `rubric_version` travels **inside** the JSON — there is no `--rubric` flag. The grader does **zero arithmetic**.
- **Backtest the committed set**: because `/capacity` scores what the user actually committed (not the `/pulse` candidate pool), the graded object's `items` array **must be the committed agenda items**. Stage B's standalone path scores exactly `items`.
- **Write** the graded object to `Daily/cache/YYYY-MM-DD-graded.json`. This overwrites any draft-time graded file `/pulse` wrote — harmless: the frozen proposal already captured the draft-time grade, and the committed-set grade is the more accurate backtest input.

Closed tier vocabularies (grader emits exactly these — full anchors in the rubric):

- **Sleep**: `excellent | good | fair | below-avg | poor | depleted`
- **Samatha** (concentration depth): `none | access | sub-j1 | j1-j3 | j4-plus`
- **Insight**: `none | some | good`
- **Depth** (per item): `heavy | substantial | standard | light | minimal`
- **Resistance** (per item): `high | moderate | low`
- **Tags** (per item, subset): `generative | momentum | primed | partial-carry | embodied`

Missing samatha/insight → the grader omits that key (Stage B treats it as `none`). Missing sleep → the grader does not fabricate; Stage B will return `{"skipped": "no sleep input"}`.

### Route — Stage B: Compute (deterministic script)

**Step 3 — Run the standalone capacity backtest.** No `--propose` — this scores the committed set; it does **not** rebuild or re-freeze the draft proposal:

```bash
uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" \
  --capacity-input "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-graded.json"
```

The script consumes the graded JSON and does **all** the arithmetic — load-tier derivation (from `hours` *and* `quality`, worse-of-the-two winning), the samatha depth-lift, per-item depth/resistance costs (tier → cost, the "resistance paid once per effort" discount, the one-high-resistance-per-day cap, tag mechanics), the budget vector, count range, and flags. Read from its JSON:

- **Budget vector**: `depth_budget` / `resistance_budget`, `depth_used` / `resistance_used`, `depth_ratio` / `resistance_ratio`, `depth_status` / `resistance_status` (`within | edge | over`).
- **Load**: `load`, `load_base`, `samatha_lift`, `mult_depth` / `mult_res`.
- **Binding constraint**: `binding` ∈ `depth | resistance | both | neither`.
- **Count range**: `count_low`–`count_high` / `committed_total`, `count_unreliable`.
- **Flags**: `flags` (e.g. `over-prediction`, `collapse-risk`, `physical-relational-at-risk`, `deep-attainment-watch`, `fatigue-exempt`), `physical_relational_ids`, `insight_lift_candidate`, and per-item `item_costs[]` (`depth_cost` / `resistance_cost` + per-item flags like `fatigue-exempt`, `depth-underscore`).

If the script returns `{"skipped": "no sleep input"}`, report that capacity can't run today (no sleep signal) and stop. Do not fabricate an input to force a number.

**Two commands this is NOT.** Do **not** run `--propose` here — that rebuilds and re-freezes the day's proposal artifact, clobbering the frozen prediction `/close` scores against. And `--verdict` is close-time outcome scoring (it reads the frozen proposal + `--actual` and does **not** take `--capacity-input`) — it belongs to `/close`, not to a manual backtest.

### Surface — Present the Backtest

**Step 4 — Concise interpretation** (present the reading, not the raw JSON):

- **Load state** — the derived `load`, and if the samatha lift moved it off `load_base`, say so ("high, lifted to effective moderate-depth by a `j1-j3` sit").
- **Budget status** — `within` / `edge` / `over` on each dimension, and which is `binding`.
- **Count range vs. committed** — "sized for N–M, agenda commits K" → over / at / under budget. Note `count_unreliable` if the collapse-risk flag is up.
- **Flags that matter** — `collapse-risk`, `over-prediction`, `physical-relational-at-risk` (name the at-risk items by label), `deep-attainment-watch`.
- **Watch condition** — the item most likely to slip (highest-cost or flagged in `item_costs`), and what would open or close budget mid-day.

### Act — Log

**Step 5 — Append to the session log** (inline — single-file append). Add `### Capacity Backtest — HH:MM` to `Daily/logs/YYYY-MM-DD-log.md`:

1. Graded tiers — sleep / samatha / insight + per-dimension confidence
2. `rubric_version` + `calc_version` (both carried on the CapacityResult — segment audits across rework boundaries)
3. Load + `samatha_lift`
4. Budget vector (both dimensions — budget, used, ratio, status)
5. Count range / committed total + binding constraint
6. Flags + `physical_relational_ids` + per-item `item_costs`

Reading the log alone must answer "how was capacity sized for the committed agenda on this date." Also write `load_state` (low / moderate / high / recovery) to today's Daily-note frontmatter.

Do **not** write BCR / `CAPACITY-VERDICT` / freeze rows here. Freezing the prediction is `/pulse`'s job (step 3.5); scoring the outcome is `/close`'s (`--verdict`). `/capacity` is a **read-only backtest** over an already-frozen day — a sanity re-check, not a gating write.

### Integration

- **After `/pulse`**: `/pulse` sizes and freezes the draft inline at step 3.5 (its own Sonnet-grader dispatch + `--propose`). Suggest `/capacity` when the user wants to re-check a committed or since-edited agenda against the day's real signals. Convention, not a hook — the agent prompts, the system doesn't force it.
- **Before `/close`**: `/close` scores the frozen proposal (`--verdict`: predicted vs. actual, binding constraint, whether the prediction held) — that feeds the graduation gate (BCR / reliable-days). `/capacity` does **not** feed that path; it is an on-demand sanity re-run, not a calibration write.
