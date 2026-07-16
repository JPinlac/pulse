---
type: doc
subtype: reference
efforts: [pulse]
rubric_version: "1.1"
capacity_calc_version: "1.0"
created: 2026-07-15
updated: 2026-07-15
version: 1
informs:
  - capacity-proposer
  - pulse-priority-calibration
tags: [pulse, capacity, grader, rubric, versioned]
---

# PULSE Capacity Grader Rubric — v1.1

The versioned **Stage-A grader contract** for the public engine's capacity
proposer. A Sonnet grader sub-agent reads this rubric, the day's raw prose
capacity check-in (sleep / concentration-practice / insight-practice), the
recent multi-day trajectory, and the candidate item pool, and emits a single
normalized **graded JSON** object. Stage B
(`pulse-engine/scripts/pulse-calc.py --capacity-input`,
`CAPACITY_CALC_VERSION "1.0"`) consumes that object and does **all**
arithmetic. The grader assigns tiers and tags; the script computes budgets,
ranges, and costs. Neither stage does the other's job.

- **The grader does zero arithmetic.** No load tier, no multipliers, no
  costs, no budgets, no count ranges. Those are Stage B's, deterministic and
  versioned.
- **Both the raw prose and the graded object are retained**, so grader drift
  is itself auditable — a future `rubric_version` can re-grade historical
  prose and diff the tier assignments against the prior version. Any change
  to tier vocabularies, anchors, tag definitions, or output rules bumps
  `rubric_version`. Every capacity row written by the engine carries both
  `rubric=` and `calc=` so audits can segment cleanly across rework
  boundaries.

**Pipeline position:** raw prose → Stage A grader (this rubric) → graded
JSON → Stage B `pulse-calc.py --capacity-input [--propose]` → budget vector,
count range, flags, frozen rows. Invoked by `/pulse` before the agenda
conversation (so the draft can be capacity-sized), and re-runnable mid-day
against the committed set.

---

## Graded-JSON output contract (Stage A → Stage B)

Emit exactly this object and nothing else. `items` is the candidate pool the
grader was handed (top-ranked candidates + routine floor + deadline items).

```json
{
  "rubric_version": "1.1",
  "date": "2026-07-15",
  "sleep": {"hours": 6.5, "tier": "below-avg", "confidence": "high"},
  "sleep_3day_avg": 6.8,
  "sleep_trend": "declining",
  "samatha": {"minutes": 15, "tier": "sub-j1", "confidence": "medium"},
  "insight": {"minutes": 20, "tier": "good", "confidence": "high"},
  "day_context": {"sprint_tail": false, "fasting": false, "cold_start_days": 1, "override_streak": 0, "recovery": false},
  "items": [
    {"id": "pulse::note::example-slug", "label": "…", "effort": "writing",
     "layer_hint": "core", "depth_tier": "substantial", "resistance_tier": "low",
     "tags": ["generative"]}
  ],
  "raw_prose": {"sleep_quality": "…", "samatha_quality": "…", "insight_quality": "…"}
}
```

Tier vocabularies (closed sets — emit exactly these strings):

- **Sleep**: `excellent | good | fair | below-avg | poor | depleted`
- **Samatha** (concentration-practice depth): `none | access | sub-j1 |
  j1-j3 | j4-plus`
- **Insight** (insight-practice quality): `none | some | good`
- **Depth** (per item): `heavy | substantial | standard | light | minimal`
- **Resistance** (per item): `high | moderate | low`
- **Tags** (per item, subset): `generative | momentum | primed |
  partial-carry | embodied`
- **Confidence** (per graded dimension): `high | medium | low`

Absent/partial inputs: missing samatha/insight → omit the key entirely
(Stage B treats an omitted key as `none`, no lift applied). Missing sleep
entirely → do **not** fabricate a number; the caller skips capacity for the
day and the script exits with `{"skipped": "no sleep input"}`. An invented
sleep or practice number poisons the calibration substrate and is strictly
worse than a logged skip.

---

## Sleep tiers — anchored

`tier` weights the self-reported **quality descriptor**, not a raw hours
band — "poor" and "below-avg" both span overlapping hour ranges depending on
how the person describes the night. `hours` is carried separately, and Stage
B re-derives the day's load tier from hours *and* quality together, the
worse of the two winning. The grader never computes load itself.

| Tier | What it captures |
|------|-------------------|
| **excellent** | Clearly rested, no deficit — "8+ hours, deep, woke fully rested." |
| **good** | Rested, no meaningful deficit — "solid 7.5, refreshed." |
| **fair** | Neutral midpoint — mild-or-no deficit, no explicit tiredness language. |
| **below-avg** | Frames the day around mild tiredness without it being the worst of it — a real but modest deficit. |
| **poor** | Explicit poor sleep / repeated waking — a real deficit the day will feel. |
| **depleted** | Collapse-adjacent — a short night stacked on accumulated debt, often following a multi-day heavy stretch. |

Grader notes:
- **Ambiguous "better/worse than typical" phrasing anchors to the tiredness
  frame** (below the neutral midpoint) unless genuine restedness is
  explicitly reported. "Slightly better than my usual tiredness" grades
  `below-avg`, not `fair` — the baseline being described is tiredness, and
  "slightly better" only lifts it off the poor floor.
- **`below-avg` vs. `poor`**: `below-avg` reads as "less than usual, mildly
  tired"; `poor` reads as "bad sleep, clearly tired, kept waking." When the
  descriptor is a flat "poor," grade `poor` even at a moderate hour count —
  quality dominates the raw number.
- A fasting or metabolic-stress cue in the prose sets `day_context.fasting:
  true` (feeds Stage B's over-prediction flag).

---

## Samatha tiers — concentration-practice depth

Quality tier dominates minutes — a short, well-settled sit is a different
grade from an equally short, unsettled one. Echo any practice-specific term
the person uses (e.g. a named jhana) into `raw_prose` verbatim.

| Tier | What it captures |
|------|-------------------|
| **none** | Missed or skipped — as informative a signal as a completed sit; no lift applied by Stage B. |
| **access** | Concentration gathered but not absorbed — settled, not dropped in. |
| **sub-j1** | Below the first-absorption threshold — more than mere settling, not yet a full absorption state. |
| **j1-j3** | First through third absorption — the strongest practice dampener in the model; Stage B applies a half-step depth lift that can re-grade the effective load a tier easier. |
| **j4-plus** | Fourth absorption and beyond. Ceiling intentionally unmapped — deeper states' correlation with load tolerance is still an open, individually-varying question. Stage B logs a `deep-attainment-watch` note rather than assuming a stronger lift than the data supports. |

Grader note: the practice dampener is **cognitive-specific** — it offsets
mental/attentional load, not bodily fatigue. A strong practice tier should
never soften an embodied/physical-relational risk flag; those two axes are
independent and must be graded independently.

---

## Insight tiers

Quality dominates duration — a brief but clear insight-practice period can
outgrade a longer, more ordinary one.

| Tier | What it captures |
|------|-------------------|
| **none** | No insight-practice period, or explicitly skipped. No lift applied. |
| **some** | Present but ordinary or indirect noticing. |
| **good** | Clear, quality insight regardless of duration. |

Grader note: insight-practice quality is tracked as a **candidate** signal
for a future resistance-budget refinement. In the current rubric version it
carries **no arithmetic effect** — Stage B logs
`insight_lift_candidate: true` for the audit trail only. Grade the tier
honestly regardless; the record is what justifies promoting this to an
active refinement once enough clean instances accumulate.

---

## Day-context flags

Derived from the prose plus the recent multi-day trajectory (load history,
which efforts were touched, gaps between sessions). Booleans/ints under
`day_context`; Stage B consumes them for load re-grading, day-type
confidence, and mandatory flags.

| Field | Set when | Feeds (Stage B) |
|-------|----------|-----------------|
| `sprint_tail` | Today follows several consecutive heavy-depth days | over-prediction + collapse-risk |
| `fasting` | Prose cues a fasting/metabolic-stress day | over-prediction |
| `cold_start_days` | Consecutive days since the last session (0 = ran yesterday) | day-type confidence |
| `override_streak` | Consecutive recent inspiration-override days | day-type confidence |
| `recovery` | Explicit recovery/decompression day | forces the `recovery` load tier |

Also carry `sleep_3day_avg` (mean hours across today + prior two days) and
`sleep_trend` (`improving | flat | declining`) — Stage B's collapse-risk
flag reads both (roughly: a declining trend under 7 hours average, combined
with a sprint-tail context, trips collapse-risk).

---

## Item classification

For each candidate item the grader assigns `layer_hint`, `depth_tier`,
`resistance_tier`, and `tags`. Grade from vault signals (Note existence,
subtype, length, history) — not from how large the item looks on the page.

**`layer_hint`** — an advisory guess at where the item belongs: `core`
(ranked execution), `floor` (routine/embodied checklist item), or
`deadline` (due-dated / near-deadline). Stage B's `--propose` makes the
final layer assignment; the grader's hint only informs it.

### Depth tiers (qualitative — Stage B maps tier → cost)

| Tier | What it looks like |
|------|-------------------|
| **heavy** | Sustained, multi-hour or multi-day, high complexity — a substantial plan-type Note, cross-effort or multi-stakeholder scope, consumes the day's entire deep-focus window. |
| **substantial** | Significant single- or multi-session scope — moderate-scope plan/note content, or several accumulated partial sessions on the same thread. |
| **standard** | A single-session finished item — a PR, an article, a demo, a meeting. |
| **light** | A minor action — a short errand or admin task. |
| **minimal** | A bookmark, reference stub, or trivial log entry. |

Classification patterns:
- **Time-boxed → standard**: a substantial-looking topic constrained to a
  fixed window costs `standard` depth, not `substantial` — the window caps
  what actually gets spent.
- A long-running plan-type Note with real accumulated length is the
  `heavy` signature; a bare minor action is `light`/`minimal`.

### Resistance tiers (grade intrinsic resistance)

Grade each item's resistance **as if it were the only item that day** — do
not pre-zero a second item just because it shares an effort with the first.
Stage B applies the "resistance paid once per effort per day" discount
itself (second-and-later item in the same effort scores zero), plus a strict
cap of one high-resistance item per day.

| Tier | What it looks like |
|------|-------------------|
| **high** | Multiple-session carry-forward with a late completion, an effort with inherited high resistance (a cold, hard-to-restart context), or something externally accountable and emotionally loaded. |
| **moderate** | A couple of sessions' carry-forward, a scheduled-but-deferred item (an appointment, a coordination task), a moderate cold-start. |
| **low** | Intrinsic-pull items — anything that draws engagement rather than demanding it (design work you're excited about, urgent problem-solving, reflective writing). The pull removes most of the activation cost even when the item is deep. |

Classification patterns:
- **Intrinsic pull → low resistance**: items that get done *because* they
  attract engagement carry near-zero resistance even at high depth.
- **Resistance is an effort-level property**: a small-looking item can
  inherit a whole effort's resistance (a cold, avoided codebase; a
  historically difficult relationship). Score the inheritance, not the
  item's surface size.
- **Paid once per effort-session**: the first item touched in a
  high-resistance effort is the hard one to start; later items in the same
  effort that day flow more easily. The grader still tags each item's
  *intrinsic* tier honestly — the script, not the grader, zeroes the
  second-and-later discount.

---

## Tags

Zero or more per item. These drive Stage B's refinement mechanics
(fatigue-exemption, priming discount, depth escalation, embodied-risk
flagging).

| Tag | Meaning | Stage B mechanic (reference — the script's math, not the grader's) |
|-----|---------|------------------------------------------------------------------|
| **generative** | Intrinsic-pull generative/ideation work (brainstorming, strategy, design). Draws on engagement rather than the depleted reserve, so it lands cleanly even on a tired day. **Requires genuine intrinsic pull, not merely generative-shaped content** — generative work aimed *against* resistance (persuading a skeptical audience, advocating into pushback) draws on the depleted reserve like any other effortful task and should **not** carry this tag. Ask: does the item attract engagement, or demand it? | Fatigue-exemption: on a fatigue-driven high/recovery load day, the item's depth cost is exempted from the fatigue discount. |
| **momentum** | Rep/executional work that flows under fatigue via accumulated familiarity, even when fresh ideation would stall under the same tiredness. | Same fatigue-exemption as `generative`, for execution riding momentum rather than intrinsic-pull generation. |
| **primed** | An item that compiles *completed* accumulated thinking from prior sessions — costs less same-day depth than its nominal tier suggests. | Priming discount: depth cost reduced, floored one tier below nominal. |
| **partial-carry** | An item carried 3+ sessions as partial/incomplete — these were partial payments on a heavier item never given a full slot. | Depth bumped one tier up, plus a `depth-underscore` flag. |
| **embodied** | A physical or relational item (movement, chores, recurring presence commitments) — zero cognitive cost, but on a *separate*, sleep-gated physical/relational energy axis; more at risk on a poor-sleep day, not exempt from it. | On a sleep-driven high/recovery load day, the item is listed under the `physical-relational-at-risk` flag. |

**The `primed` / `partial-carry` disambiguator** — they pull in opposite
directions on the same item, so tag exactly one:

> priming discount = *completed* accumulated thinking (cheaper today);
> depth-underscore = *unfinished* heavy work with accumulated partial
> payments (dearer today).

If both seem to apply, tag `partial-carry` — the script lets partial-carry
win and warns. `generative` and `momentum` are the fatigue-exemption pair
(intrinsic-pull generation vs. momentum-carried execution); an item is
usually one or the other, rarely both.

---

## Grader output rules

1. **Always echo raw prose verbatim** into `raw_prose`
   (`sleep_quality`, `samatha_quality`, `insight_quality`). This is what
   makes grader drift auditable — the corpus can be re-graded under a
   future `rubric_version` and diffed against the original.
2. **Per-dimension confidence** (`high | medium | low`) on sleep, samatha,
   and insight — how cleanly the prose mapped to a tier. Sparse or
   ambiguous prose grades `medium`/`low`; a clear, specific statement grades
   `high`.
3. **Never do arithmetic.** Emit tiers, tags, flags, and layer hints only.
   No load tier, no multipliers, no item costs, no budgets, no count
   ranges — all of that belongs to Stage B
   (`pulse-calc.py`, `CAPACITY_CALC_VERSION "1.0"`). The mechanic
   references above are shown for context, not as grader output.
4. **Carry `rubric_version: "1.1"`** on every object. Missing samatha/
   insight → omit those keys. Missing sleep → do not fabricate; the caller
   skips capacity for the day.
5. **Output only the graded JSON object** — no prose wrapper, no
   explanation, no surrounding code-fence commentary. It is piped directly
   into `--capacity-input`.

---

## Versioning & re-grade discipline

`rubric_version` bumps on any change to tier vocabularies, anchors, tag
definitions, or output rules. `capacity_calc_version` bumps independently on
Stage-B arithmetic changes. Every capacity row carries both (`rubric=` /
`calc=`), so an audit can segment grades and computations across rework
boundaries without ambiguity. Because `raw_prose` is retained on every
graded object, a rubric change is directly testable: re-grade the historical
prose under the new version and diff the tier assignments — the delta *is*
the measured grader drift.

**Changelog**:
- **v1.1** — `generative` tag definition tightened to require genuine
  intrinsic pull; generative-shaped work performed against resistance no
  longer qualifies.
- **v1.0** — initial contract.

## Informs

- [[capacity-proposer]] — the design/operating guide this rubric's Stage-A
  contract feeds.
- [[pulse-priority-calibration]] — where graded-object outcomes accrue as
  calibration rows.
