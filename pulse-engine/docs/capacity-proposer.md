---
type: doc
subtype: reference
efforts: [pulse]
created: 2026-07-15
updated: 2026-07-15
version: 1
rubric_version: "1.1"
capacity_calc_version: "1.0"
informs:
  - pulse-priority-calibration
  - pulse-capacity-rubric
tags: [pulse, capacity, agenda, proposer, graduation, bcr, gates]
---

# Capacity Proposer — Design & Operating Guide

This is the public engine's capacity-based agenda proposer: a two-stage pipeline
(a grading sub-agent, then a deterministic script) that turns a short daily
capacity check-in into a sized, layered draft agenda — and a graduation gate
that decides when that draft is trustworthy enough to lead the briefing
instead of sit beneath it.

Two terms recur throughout: **ACR** (Agenda Concordance Rate) measures how well
a draft matched what you actually committed to. **BCR** (Binding-Constraint
Match Rate) measures how well capacity called the day's real bottleneck. Both
are stamped mechanically by the engine; you never compute either by hand.

---

## 1. The candidate pool: explicit-capture-as-commitment

**This proposer never reads your conversation for tasks.** The candidate pool
it sizes a day around is built from exactly three sources:

1. **Explicitly captured items** — anything you (or an agent, on your
   explicit assent) filed through `/capture` → `/triage` into a Note or Map
   Minor Action. Capture is the commitment signal; nothing else is.
2. **The routine floor** — the recurring, non-negotiable items in
   `Templates/routine-floor.md` (movement, chores, recurring presence
   commitments — whatever you've listed there for the day's weekday).
3. **Deadline/due items** — any open Note or Minor Action carrying a `due`
   date within the exemption horizon (see §3).

**Noticing is not committing.** During a session the agent may notice
something conversational that sounds like a task and *offer* to capture it
("want me to file that?") — but the write to the vault only happens on your
explicit assent. There is no passive extraction path, no background sweep
that materializes half-said ideation into committed items. If you don't
capture it, the proposer never sees it.

**The honest trade, stated plainly:** a session where you think out loud but
capture nothing produces a draft that leans entirely on the routine floor and
any deadline items — it will look thin. That is correct behavior, not a bug.
A proposer that tried to infer commitment from conversation would routinely
promote noise (the fifth idea in a brainstorm) to the same standing as a
task you deliberately wrote down. Sizing a day around unclaimed ideation is
worse than sizing it around a short list you actually meant. If your draft
looks sparse, the fix is to capture more, not to widen what counts as a
candidate.

Duplicate or misfiled captures are handled by the existing `/triage` and
`/defrag` misclassification passes — exactly as they are for any other
capture, with no separate lifecycle machinery bolted on for this feature.

---

## 2. The two-stage pipeline

1. **Stage A — the grader (a Sonnet sub-agent).** Your raw prose check-in
   ("6.5 hours, kept waking; short sit, didn't settle; brief but clear
   insight period") is mapped to tiers against the versioned rubric
   (`pulse-capacity-rubric.md`, current `rubric_version: "1.1"`). Your exact
   words are retained alongside the grade, so a future rubric revision can
   re-grade the historical corpus and diff. **The grader does zero
   arithmetic** — it assigns tiers, tags, and flags only.
2. **Stage B — `pulse-engine/scripts/pulse-calc.py --capacity-input`
   (deterministic, `CAPACITY_CALC_VERSION "1.0"`).** The graded tiers feed
   the script, which does *all* the math: load-tier derivation, per-item
   depth/resistance costing, the budget vector, the count range, the binding
   constraint, and the day-level flags. No LLM soft-rounding anywhere in
   this stage.

Two refinements worth knowing in plain words, both scored by Stage B, not by
the grader:
- **Strong concentration practice can lift throughput.** A well-graded
  practice sit buys back some cognitive load-tolerance — a mild-deficit day
  with real practice can score a tier easier than the sleep number alone
  would suggest.
- **Some work rides momentum through fatigue.** Generative/engaged work and
  familiar executional work both have a lower fatigue penalty than fresh,
  effortful work under the same tiredness — the script tags and discounts
  for this via item tags (`generative`, `momentum`), never by guesswork.

**The layered draft is frozen before you see it.** Stage B assembles the
draft and writes it (plus the underlying capacity numbers) to the session
log and `Daily/cache/` *before* the agenda conversation happens. This is the
anti-circularity fix: if the draft could change quietly after you reacted to
it, measuring "did the draft hold up" would be meaningless. Your edits are
always counted against a fixed, already-written target.

---

## 3. Reading the layered draft

The draft is assembled in five layers, in this order:

- **deadline** — anything with a `due` date within the exemption horizon
  (`DEADLINE_DUE_HORIZON = 1` day: due today or tomorrow). This layer rides
  an exemption path regardless of how the ranking scores the item — if it
  has a near-term due date, it surfaces. **This is not external calendar
  ingestion.** External calendars are explicitly out of scope for this
  release; this is the internal due-date exemption path over your own
  captured vault items (Notes and Minor Actions carrying `due:`). It is a
  live, load-bearing layer — the fix for a historical failure mode where
  deadline-carrying items sank in the ranking instead of surfacing.
- **floor** — routine/embodied items pulled straight from
  `Templates/routine-floor.md`, filtered to the day of week. Deterministic —
  a checklist, not a judgment call. Historically this was the layer most
  likely to be silently dropped by pure ranking; it is now unconditionally
  included whenever the template file resolves.
- **core** — the ranked, capacity-sized execution items, budgeted to the
  **low end** of the day's range. This is the conservative promise: the
  floor of what the day commits to, not an optimistic stretch.
- **stretch** — a small number of labeled upside items (capped at
  `STRETCH_COUNT_MAX = 3`): the next-ranked items the draft would have
  committed to on a stronger day. **Stretch never counts against any
  verdict.** Completing a stretch item is pure upside, never a "miss" on
  anything else.
- **slack** — deliberately unfilled slots (`SLACK_RATIO = 0.375` of the
  sized core+floor+deadline count, minimum 1). Not laziness — structural
  humility for the fraction of days that pivot to something unmodeled.
  Slack never fills and is not itself graded.

### The confidence label

The top of the draft block carries one of two labels:
- **"Draft Agenda — accept or edit"** — the day's signals look clean;
  treat the draft as real proposed material.
- **"Low-confidence seed — treat as raw material"** — a turbulent day
  (an override streak, a cold start after a long gap, collapse-risk load).
  The draft still renders, but you're being told not to lean on it — skim
  for anything useful and build the rest yourself. This is an honest signal,
  not a failure of the model.

### The capacity one-liner

Format: **load · count range · binding constraint · flags.**

- **load** — the day's tier (`excellent | good | fair | below-avg | poor |
  depleted`, or `recovery`), derived from hours *and* quality, the worse of
  the two winning.
- **count range** — expected completions as a range, never a point estimate.
  Treat the low end as the real target.
- **binding constraint** — what will actually bottleneck the day: `depth`
  (sustained-focus capacity), `resistance` (activation energy to start hard
  things), `both`, or `neither`. This is the single most reliable number the
  script produces — trust it over the count range.
- **flags** — `collapse-risk` (the count is unreliable; a stacked-fatigue day
  a linear model can't represent — protect the floor, ignore the number),
  `over-prediction` (the model is running optimistic today; aim for the low
  end), `physical-relational-at-risk` (a poor-sleep day with an embodied or
  relational floor item — that item sits on a separate energy axis the
  cognitive score can't see, and is *more* at risk today, not exempt from
  it).

If you skip the capacity check-in, the line reads "sized by static floor —
no capacity inputs today"; the draft still assembles from deadline + floor +
a small fixed core (`STATIC_FLOOR_CORE = 4`), it's just not capacity-sized.
Skipping is a first-class path, not a degraded one — see §7.

---

## 4. ACR and edits — how your behavior feeds calibration

You do nothing special for this; you just accept or edit honestly. Every
committed agenda writes one **ACR-ROW** to the session log, capturing:

- **coverage (`c`)** — how much of what you actually committed to was
  already present in the draft.
- **acceptance** — how much of the draft survived into what you committed.
- **edit count** — adds, removes, swaps, and resizes each count as one edit.
  This is the more informative signal: coverage is a proxy, edit count is
  the direct measure of "was editing the draft cheaper than building an
  agenda from nothing."

A **full rejection** — discarding the draft and building an agenda from
scratch — counts against the ACR floor. Edit honestly; accepting a weak
draft to be agreeable poisons the calibration signal worse than an honest
rejection does.

---

## 5. Close: the verdict, committed blind

At `/close`, before anything about the frozen prediction is opened, you (or
the agent, on your behalf) characterize how the day actually went —
`binding_actual` (which constraint actually bound: depth, resistance, both,
or neither) and the count of committed-core and committed-stretch items
completed, read straight off the Daily Note's checked-off agenda. **This
happens before the frozen `CAPACITY-FROZEN`/`binding_pred` row is read.**
The freeze-before-conversation discipline that protects the draft from being
massaged after the fact is mirrored here on the outcome side: the same agent
that scores the day must not see its own prediction before committing what
actually happened, or it inflates the exact metric (BCR) that gates
graduation.

Once `binding_actual` is committed, `pulse-calc.py --verdict --actual
'{...}'` runs the mechanical comparison against the frozen proposal and
writes one **CAPACITY-VERDICT** row:

- **HIT** — actual completions landed inside the frozen range.
- **DIR-HIT** — within one of the nearer bound (directionally right).
- **MISS** — outside that.
- **UNRELIABLE** — the prediction itself carried `collapse-risk`; excluded
  from BCR entirely, in both directions.
- **binding** — scored independently: did the predicted bottleneck actually
  bind (`HIT`/`MISS`)? This is the number that feeds BCR.
- **stretch** — logged as completed/offered; pure upside, never touches the
  verdict.

If you skipped the capacity check-in that morning, there is no prediction to
verdict, and `/close` silently skips this step — no noise, no forced score.

---

## 6. The graduation gate

Two phases exist for this proposer: **backtest** (the ranked candidate pool
leads the briefing; the draft renders beneath it as a proposal you're
building trust in) and **graduated** (the draft leads; the full pool is one
command, `/landscape`, away).

**Graduation is a compound gate — BCR is the substrate that promotes it, but
composition sanity must also hold.** All of the following, over a 14-day
rolling window, must be true:

- `bcr ≥ 0.80` — capacity called the day's binding constraint right at least
  four times in five, across reliable days.
- `rolling_acr ≥ 0.60` **and** `median_edits ≤ 3` — the draft's composition
  is not being rebuilt from scratch every day. This is a **sanity floor**,
  deliberately looser than a full composition-graduation bar — it exists to
  make sure BCR isn't graduating a proposer whose draft nobody actually
  uses, not to gate a second, separate promotion.
- `reliable_days ≥ 10` — at least ten non-`UNRELIABLE` verdict rows in the
  window. A strong first week is not enough data; `insufficient-data`
  blocks the gate outright regardless of how good the early numbers look.

Only BCR (as part of this compound) graduates the proposer. **ACR and a
separate priority-ordering signal (PAR) are retained purely as calibration
health checks** — they inform confidence and surface an under-ambition
tripwire, but neither one independently promotes or demotes the proposer's
phase.

**Reverts fire live, need no stored state, and require their own minimum
data:**
- A **BCR revert** fires the moment any 7-day window (scanned across the
  full 14-day range) shows `< 4` reliable days *or* — when it has 4+ — a
  binding-HIT rate below `0.70`. The 4-day floor exists specifically so a
  single miss inside a near-empty window can't trip a spurious revert.
- An **ACR revert** fires the same way over `c` values: any qualifying
  7-day window with `≥ 4` ACR rows averaging below `0.60`.
- Because the check scans every 7-day window inside the trailing 14 days,
  one bad week latches the revert for up to two weeks after the bad data
  ages out — a day or two of the 0.70–0.80 hysteresis band bouncing around
  can't flip graduated → reverted → graduated on consecutive closes.

**The phase stamp only ever advances at the ceremony, and only in one
direction.** It lives in the calibration note's frontmatter
(`capacity_phase`), is written by `/close` the first time it observes
`gate_met` with the stamp not already `graduated`, and never un-stamps
itself. The *live* post-gate behavior is not simply "stamp says graduated" —
every `/pulse` re-evaluates:

```
post_gate = (capacity_phase == "graduated")
            AND NOT gates.capacity.revert_triggered
            AND NOT gates.agenda_composition.revert_triggered
```

So the stamp is a one-way ratchet on the way up, but a revert withdraws the
draft-leads behavior immediately and without waiting for another ceremony —
graduate ceremonially, revert instantly.

**The graduation event itself** fires at the first `/close` on or after the
day the gate is actually met — not on a fixed day of the week. This tool is
built for sparse, irregular use; a graduation condition that only checks on
a particular weekday could sit met for weeks without ever being noticed.

---

## 7. Sparse sessions and re-entry

Skipping the capacity check-in, or returning after a long gap, is a
first-class path, not a degraded one. The same pipeline runs either way — no
inputs means the draft sizes from a static floor (deadline + routine floor +
a small fixed core) instead of a capacity-derived range, and no capacity
verdict is generated that day (nothing to pollute the BCR substrate with).
You still get a usable draft in every session; you're never blocked on
having graded anything.

---

## 8. What to watch: under-ambition

The model's known failure direction is over-commitment; inverting that into
conservative, low-end sizing risks the opposite failure — quietly
undersizing days. The tripwire: a rolling `stretch_rate` — the fraction of
offered stretch items actually completed — crossing `0.50` over the
calibration window flags `"widen sizing"` in `--gates` output. This is a
calibration/health signal, same tier as ACR and PAR: it never gates
graduation on its own, but it is worth noticing if your drafts keep feeling
too easy.

---

## 9. Tuning

- **The routine floor** (`Templates/routine-floor.md`) is yours to edit
  directly — add or remove items, change which days they fire. See
  `routine-floor-setup.md` for the exact format and the path the script
  reads.
- **Misgraded check-ins** feed rubric corrections — if the grader reads your
  prose wrong, say so; the rubric bumps `rubric_version` when tiers or
  anchors change, and because raw prose is retained on every graded object,
  history can be re-graded under the corrected rubric and diffed.
- **Deadline items need an actual `due` date** to ride the exemption layer.
  A recurring relational or routine commitment belongs on the floor; a
  specific near-term protection ("keep tomorrow evening clear") needs a
  `due` date on a captured item so it rides the deadline layer instead of
  competing purely on rank.

## Informs

- [[pulse-priority-calibration]] — the live ACR/BCR/PAR substrate and the
  gate this doc describes reading.
- [[pulse-capacity-rubric]] — the Stage-A grader contract (rubric version
  and tier vocabularies) that normalizes the check-in prose this doc
  describes.
