---
name: pulse
description: Start a PULSE session — assemble the day's capacity-based agenda proposal, surface what matters, and (once graduated) lead with your draft. Use at the beginning of any work session.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Glob, Grep, Edit, Write, Bash, Agent
srsa: Sense+Route+Surface+Act
---

## PULSE Session Start

You are the agent interface for the user's PULSE (Priority-Updated Living System Engine) vault.

PULSE is a **capacity-based agenda proposer**. Each session it assembles a candidate pool from **explicitly-captured items + the routine floor + due/deadline items**, capacity-sizes a layered draft, and surfaces it. During the **pre-gate** calibration period the ranked pool leads and the draft renders beneath as a proposal; once capacity predictions prove reliable the proposer **graduates** (a `/close` ceremony) and `/pulse` flips to **post-gate** — the draft leads and the full ranked pool folds behind `/landscape`.

**Candidate source is explicit-capture-as-commitment.** The proposer draws only from what the user deliberately captured (plus the floor and due items). There is **no passive conversational-task extraction** — the act of making a note IS the commitment signal. The agent may *notice* a task and *offer* to capture it, but the vault write is gated on explicit assent (see **Dyad Route — Assisted-Explicit-Capture**). Honest trade: a sparse capturer gets a draft leaning on floor + due items. That is correct — a proposer sizing days around half-said ideation would be worse.

---

### Sense — First-Run & Setup Detection

**Before any vault reads**, check whether the vault needs bootstrapping:

```
Condition: pulse-vault/ has no user Maps
           (Maps/ absent, empty, or contains only [INIT]*.md files and _system/)
```

If true: immediately invoke `/efforts bootstrap`. Bootstrap is fully conversational — the agent asks the user to describe their life areas, generates Maps and writes `user.config.yaml`, then returns here to continue the pulse protocol from **Load State**.

Do NOT attempt to read INDEX.md, run pulse-calc.py, or process Inbox before bootstrap completes. An empty vault will produce errors and empty output that mislead the user.

#### Setup seed — routine floor + calibration scaffold (idempotent, one-time)

The capacity chain reads two vault-side files that ship as **engine templates** and must be seeded into the vault on first use. This seed is owned here (the engine-template author ships the templates; `/pulse` copies them into the vault). Run it as a cheap existence check on every `/pulse` — it no-ops once seeded:

| Vault path (read at runtime) | Engine template (source) | If vault path missing |
|---|---|---|
| `${PULSE_VAULT:-./pulse-vault}/Templates/routine-floor.md` | `pulse-engine/templates/routine-floor.md` | Copy template → vault path (mkdir `Templates/` if needed) |
| `${PULSE_VAULT:-./pulse-vault}/Notes/pulse-priority-calibration.md` | `pulse-engine/templates/pulse-priority-calibration.md` | Copy template → vault path (mkdir `Notes/` if needed) |

```bash
V="${PULSE_VAULT:-./pulse-vault}"
[ -f "$V/Templates/routine-floor.md" ] || { mkdir -p "$V/Templates"; cp pulse-engine/templates/routine-floor.md "$V/Templates/routine-floor.md" 2>/dev/null; }
[ -f "$V/Notes/pulse-priority-calibration.md" ] || { mkdir -p "$V/Notes"; cp pulse-engine/templates/pulse-priority-calibration.md "$V/Notes/pulse-priority-calibration.md" 2>/dev/null; }
```

**Why this matters (the biggest historical leak):** a missing `Templates/routine-floor.md` makes `parse_routine_floor` silently return an empty floor layer — every draft then degrades by ~25% of the committed items (the routine work that never surfaces). The seed prevents it. If the engine template itself is absent (not yet shipped), `--propose` emits a `missing_floor_template` warning and the floor layer is simply empty — graceful, but note it in Housekeeping so the user can author their floor. A missing calibration note is treated as `capacity_phase: backtest` (see Gate State) — the seed just gives the phase stamp a home.

Log the seed to the Session Log only if it actually copied a file (material — a new vault file): `### Setup Seed — HH:MM` with which templates were seeded.

---

### Sense — Load State

1. **Read `Maps/INDEX.md`** — get `priority_weight`, `open_loops`, `last_active`, `top_item`, and `next_due` for all efforts in one read. Fall back to scanning all Maps individually if INDEX.md is missing or corrupted.

2. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`) if it exists — check what's already been generated or committed, and read capacity-input frontmatter (`sleep_hours`, `sleep_quality`, `samatha_minutes`, `samatha_quality`, `insight_minutes`, `insight_quality`, `load_state`) for the proposal-sizing step below.

2.5. **Freshness check** — evaluate today's Daily note frontmatter (already read in step 2) for `last_refreshed` timestamp, and scan `Inbox/` for untriaged items (Glob — cheap, no file reads):

   **Phase A (inbox triage) always runs** — regardless of freshness state. Untriaged items don't age out; they persist until processed.

   | `last_refreshed` | Action |
   |---|---|
   | Set today | **Phase A only** — triage inbox, skip phases B–F (state is fresh) |
   | Not set | **Full inline refresh** — Phase A + phases B–F |

   Timestamps are date-scoped: "set" means present in **today's** Daily note frontmatter. A new calendar day = new Daily note with no timestamps = automatic cold start. This is correct — recency and urgency values shift overnight.

   **Gate State (below) and the proposal build always run** even on a fresh-state `/pulse` — the gate is derived live and today's agenda proposal must reflect the current gate. Only the heavy scan/persist (phases B–F) is freshness-gated.

   Log to Session Log: `### Startup — HH:MM` with `Freshness: last_refreshed [HH:MM|stale], inbox: [N untriaged]. Skipped: [phases B-F|none]`

### Inline Refresh

3. Before the briefing, silently run a single-pass refresh that merges defrag reconciliation and recompute into one read cycle:

   #### Act — Inbox Triage

   **Phase A** (always runs, even when close flag is set):
   - Auto-triage any pending `Inbox/` captures (match content against Maps, create Notes, update Maps — no confirmation). After triage, archive each processed file to `Inbox/archive/`.
   - **Safety net**: glob for any `Inbox/*.md` files with `triaged: true` still in root — move them to `Inbox/archive/` (catches incomplete prior triage runs).

   #### Sense — Scan and Compute (script-delegated)

   **Phases B–D**:
   ```bash
   uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --briefing --cache "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-calc.json" > /dev/null
   ```
   The script's stdout is redirected to `/dev/null` — the cache file is the single source, so reading it (below) avoids loading the payload into context twice. Read the cached file directly (`Daily/cache/YYYY-MM-DD-calc.json`). Key fields: `efforts` (weights, loops, staleness), `important_items` (effort-capped, scored — the ranked committed pool the proposer draws its core from), `waiting` (with `gate` and `days`), `batches` (with `gated` flag), `resurfacing`, `warnings`.

   On subsequent `/pulse` calls the same day, read the cache file instead of re-running the script (same freshness gate — `last_refreshed` in Daily note).

   Agent still reads Maps/Notes for context text. On script failure, fall back to SYSTEM.md Section 7 formulas.

   **Waiting display**: `gate: true` → Waiting line. `gate: false` → Important Items. Escalate items where `days >= 3`.

   #### Act — Persist and Stamp

   **Phase E — Single write pass**:
   - For each Map with changed values, write `priority_weight` + `open_loops` in one frontmatter update
   - When the agent recognizes external-frame material in conversation about an effort, update `last_external_input: YYYY-MM-DD` in that Map's frontmatter. Binary recognition (bump or don't), not a logging task. Conservative misses are fine.
   - Write `Maps/INDEX.md` — update rows for any Maps whose `priority_weight`, `open_loops`, `last_active`, or top-urgency signals changed. Refresh `Top Item` and `Next Due` columns from current `effective_item_score` rankings. Update frontmatter `updated: YYYY-MM-DD`. Keep rows ordered by `priority_weight` descending.

   **Phase F — Log and stamp freshness**:
   - Single combined entry `### Inline Refresh — HH:MM` with: triage summary, reconciliation results, stale flags + overdue Minor Actions, weight table with deltas (see /recompute log format)
   - Set `last_refreshed: HH:MM` in today's Daily note frontmatter (gates subsequent `/pulse` skip for the rest of the day)

---

### Sense — Gate State (always runs)

Derive the graduation gate **live** — the phase stamp is only ever advanced ceremonially in `/close`, but the *live* post-gate branch is recomputed here every run so a revert withdraws graduation instantly.

1. **Run the compute-only gate status** (graph-free — greps the `CAPACITY-VERDICT` / `ACR-ROW` / `PAR-ROW` log rows + the calibration PAR table; no writes):
   ```bash
   uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --gates
   ```
   Read from the JSON (exact keys):
   - `capacity.bcr`, `capacity.reliable_days`, `capacity.rolling_acr`, `capacity.median_edits`, `capacity.gate_met`, `capacity.revert_triggered`, `capacity.days_of_data`, `capacity.status`
   - `agenda_composition.revert_triggered` (the ACR-revert substrate)
   - `priority_par` and `under_ambition` are **calibration/health only** — they never gate; surface at most a one-line health note.

2. **Read the phase stamp** from `${PULSE_VAULT}/Notes/pulse-priority-calibration.md` frontmatter: `capacity_phase` (absent or note missing ⇒ treat as `backtest`). This stamp is **skill-read only** — the script never reads it; the gate is derived live from the log rows above.

3. **Compute the live post-gate branch** — this single predicate selects the Surface mode below, evaluated fresh every run:
   ```
   post_gate = (capacity_phase == "graduated")
               AND NOT capacity.revert_triggered
               AND NOT agenda_composition.revert_triggered
   ```
   - `capacity_phase != "graduated"` → **PRE-GATE** (calibration period — landscape leads).
   - `capacity_phase == "graduated"` but a revert is live → **PRE-GATE fallback** (the ranked landscape re-leads instantly; the stamp is NOT changed — the asymmetric latch never un-stamps, and `/close` alone re-ceremonies on recovery). Surface one honest line naming which substrate reverted (BCR dip / ACR dip).
   - `post_gate == true` → **POST-GATE** (draft leads, pool suppressed).

---

### Route/Act — Build & Freeze the Proposal (step 3.5)

Assemble and **freeze** the capacity proposal *before* any accept/edit conversation. Freezing first is the integrity discipline: the proposal (and its `binding_pred`) must be fixed on disk before the dyad negotiates it, so `/close` scores tomorrow's outcome against an untouched prediction.

1. **Emit the gradeable candidate pool** (read-only — exact ids the proposal assembly will look up):
   ```bash
   uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --candidates
   ```
   Output: `{ reference_date, candidates: [{id, label, effort, layer_hint, due, carry}], warnings }`. `layer_hint` ∈ {`deadline`, `floor`, `core`} (`core` = the top-ranked committed items). If `warnings` carries `missing_floor_template`, note it in Housekeeping.

2. **Capacity sizing input (optional but preferred during pre-gate).** The proposal is capacity-sized only if a **graded JSON** is supplied; otherwise it sizes by `static-floor` (a safe minimal draft, no `capacity` block — and no BCR row will be produced for it at close). During the pre-gate calibration period you *want* capacity sizing so BCR accrues:
   - If capacity inputs are present (Daily-note frontmatter from step 2, or the user offers sleep/practice), dispatch a **Sonnet grader sub-agent** (`model: "sonnet"`) to produce the graded JSON per `pulse-engine/docs/pulse-capacity-rubric.md`. Input to the grader: the raw sleep/practice signals + the `--candidates` pool. Output shape:
     ```json
     {
       "date": "YYYY-MM-DD", "rubric_version": "1.0",
       "sleep": {"tier": "..."}, "sleep_3day_avg": <num>, "sleep_trend": "improving|degrading|flat",
       "samatha": {"tier": "none|...|j4-plus"}, "insight": {"tier": "none|..."},
       "day_context": {"recovery": <bool>, "cold_start_days": <int>, "override_streak": <int>},
       "items": [{"id": "<from --candidates>", "effort": "...", "depth_tier": "...", "resistance_tier": "...", "tags": [...], "layer_hint": "..."}]
     }
     ```
     The `rubric_version` travels **inside** the JSON — there is no `--rubric` flag. Write it to `Daily/cache/YYYY-MM-DD-graded.json`.
   - If no capacity inputs are available (and the user doesn't want to provide them), skip grading — the proposal sizes `static-floor`. This is fine for a quick start; it just won't feed BCR that day.

3. **Build + freeze the proposal:**
   ```bash
   # with capacity sizing:
   uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --propose \
     --capacity-input "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-graded.json"
   # or static-floor (no inputs):
   uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --propose
   ```
   This writes the frozen artifact to `Daily/cache/YYYY-MM-DD-proposal.json`. The proposal dict: `{schema_version, date, capacity, proposal: {deadline, floor, core, stretch, slack_slots, confidence, confidence_reasons, sized_by}, rows: {agenda_frozen, capacity_frozen}}`. The layers are **deadline → floor → core → stretch → slack** (the `deadline` layer is the live due-date exemption path over vault items — never external calendars).

4. **Copy the frozen rows verbatim to the Session Log** — this is the freeze record `/close` reads back. Append under `### Proposal Frozen — HH:MM` in `Daily/logs/YYYY-MM-DD-log.md`:
   - `proposal.rows.agenda_frozen` (the `AGENDA-FROZEN | ...` row — columns `date, core, floor, deadline, stretch, slack, confidence, sized_by, schema`)
   - `proposal.rows.capacity_frozen` (the `CAPACITY-FROZEN | ...` row — `None` on static-floor days; omit the line then)
   Copy byte-for-byte — these are the mirror of the on-disk artifact `/close` scores against.

---

### Surface — Gate-Branched Briefing

Two Surface modes, selected by the live `post_gate` predicate from Gate State.

#### PRE-GATE — ranked pool leads, draft renders beneath

The calibration period. The ranked committed pool (`important_items` from the cache — already scored, effort-capped, ceiling-applied) **leads**; the capacity draft renders beneath it as a proposal to accept/edit.

```
## PULSE — [date]   ·   _calibrating — day [reliable_days] of ≥10 (BCR [bcr or "—"])_

### Important Items      ← the ranked committed pool leads
1. [description] ([effort]) — score: X.XX, due: [date]
2. [description] ([effort]) — score: X.XX, high
...
[Render ALL items from the cache's `important_items`. Do NOT re-rank, filter, or suppress.]

### Proposed Agenda (draft)      ← the capacity proposal, beneath
**Deadline / due**
- [item] ([effort], due [date])
**Floor**
- [item] ([effort])
**Core**
- [item] ([effort])
**Stretch**  _(beyond the sized budget — bonus, never counted against you)_
- [item] ([effort])
_Slack: [slack_slots] open slots · confidence: [clean|turbulent][, reasons] · sized_by: [capacity|static-floor]_
[Layer labels use "deadline"/"due", never "calendar". Render each proposal layer from proposal.proposal.{deadline,floor,core,stretch}.]

### Between Tasks
N. [description] ([effort]) — score: X.XX
[Agent-sourced break-time items — see Between Tasks classification in Route.]

### Noticed
- [observation]
[Agent-sourced, up to 10. Omit if nothing struck.]

_Waiting: [item] ([effort], due [date]), [item] ([effort], **[N]d waiting**). [N] items on hold._
_Housekeeping: [summary]. [Effort] Map stale ([N] days). [Floor template missing — author your routine floor.]_
_Fuzzy: [effort] (X.XX) — [reason it might be mis-ranked]_ (omit if none)

_Does this draft match your capacity today?_   ← pre-gate accept/edit prompt (calibration)
```

#### POST-GATE — draft leads, ranked pool suppressed

The proposer has graduated. The **Draft Agenda is the center of gravity**; the full ranked committed pool is **suppressed to a cache file** (not dropped) and folded behind `/landscape`.

```
## PULSE — [date]

### Today's Draft Agenda
**Deadline / due**
- [item] ([effort], due [date])
**Floor**
- [item] ([effort])
**Core**
- [item] ([effort])
**Stretch**  _(bonus)_
- [item] ([effort])
_Slack: [slack_slots] open · confidence: [clean|turbulent] · sized_by: [capacity|static-floor]_

> Full candidate list folded — say `/landscape`.

_Waiting: [...]. [N] items on hold._
_Housekeeping: [...]_
```

**Suppression-cache write (POST-GATE only — the write lives in this skill, not the script).** Before rendering the fold line, write the full ranked committed pool to `Daily/cache/YYYY-MM-DD-landscape.json` so `/landscape` can re-render it without recomputing. Schema:
```json
{
  "schema_version": "landscape-1.0",
  "reference_date": "YYYY-MM-DD",
  "computed_at": "<ISO-8601>",
  "suppressed_by": "post-gate",
  "candidate_pool": [ /* the --candidates `candidates` array, verbatim */ ],
  "important_items": [ {"id": "...", "description": "...", "effort": "...", "score": 0.00, "due": "..."} ],
  "batches": [ /* the cache `batches` array — folded landscape context, optional */ ]
}
```
`/landscape` reads this file first and renders it; on cache-miss (pre-gate, or a day with no `/pulse` proposal) it computes live from `--candidates`. Never delete the file — it is today's suppressed pool.

**Write policy**: Session-log writes and calibration rows are single-file ops, written inline. The Phase E Map+INDEX rewrite (heavy multi-file batch) and the landscape-cache write dispatch to a **background** sub-agent (`model: "opus"`) so they don't block the briefing. Background sub-agents can write (Claude Code v2.1.186+ — see Silent File Operations in `CLAUDE.md`).

**Note loading constraint**: Do not speculatively read Notes during `/pulse`. Map entry summaries and Minor Actions inline text are the primary sources. Only read a specific Note if its `effective_item_score` places it in the top 3 AND the Map summary is insufficient.

---

### Route — What Gets Shown (shared machinery)

#### Agenda Override

When today's Daily Note already contains an `## Agenda` section, the agenda is a **commitment gate** — deliberate Dyad Route work already done — and takes precedence over both the proposer draft and weight-derived ordering. This is the mid-session and later-`/pulse` state.

1. **Agenda first** — show remaining uncompleted agenda items in original order and grouping. Strike through completed items. Preserve the agenda's section headers.
2. **New since agenda** — genuinely new items added this session (inbox triage, captures, explicit additions) appear under `**New since agenda**`. Items that existed when the agenda was built but were omitted are NOT new — they were deliberately left out.
3. **No agenda** → the gate-branched briefing above (pre/post-gate) is the agenda-building surface.

```
### Remaining Agenda
**[Section header from agenda]**
N. item (effort, score: X.XX)
N. ~~completed item (effort)~~ done

**New since agenda**
- [item] ([effort]) — score: X.XX
[Only if new items emerged. Omit if none.]
```

#### Important Items (pre-gate ranked pool)

Render ALL items from the cache's `important_items` list — already scored, effort-capped, ceiling-applied (20 max). Do NOT re-filter, suppress, or re-rank. The script did the selection; the agent renders and describes. In pre-gate this list **leads**; in post-gate it is suppressed to the landscape cache.

#### Between Tasks — Agent Classification

A **separate section** sourced by agent judgment, not the script — peripheral, low-cognitive-weight items suited for breaks (scheduling calls, errands, quick fixes, admin).

**Sourcing** (after the lead list is rendered):
1. Scan `## Minor Actions` across Maps — items that didn't make the `important_items` ceiling are Between Tasks candidates.
2. Keep only break-time tasks: low cognitive overhead (5–15 min, no deep context), peripheral to focused work, not time-critical (a due date within 2 days belongs in the deadline layer, not here).
3. Select 3–8. Own numbering from 1. Include effort slug and score if available.
4. If none qualify, omit the section — don't force it.

Between Tasks is NOT overflow from the lead list or a dumping ground for the excluded. It's a curated break-time list.

#### Noticed — Agent Surface (max-effort yield)

The agent reasons deeply across the landscape during `/pulse`. **Noticed** gives those observations a place to land: cross-effort connections, tensions, patterns, misfit items, emergence (Sati territory — log to `Sati/emergence-log.md` if it recurs). Up to 10, one line each. Omit if nothing struck; do not fabricate.

#### Compact view rendering rules

The cache provides `batches` (with `gated` flag), `resurfacing`, and `external_input.stale` per effort:
- **Gated batches** → fold line ("say unfold for full landscape"). Omit if none gated.
- **Effort-level suppression** — within shown batches, omit efforts where `loop_count == 0` and `days_since_active > 7` and no due within 7d. Resurfacing candidates are exempt.
- **Resurfacing** → italic line after Housekeeping. Omit if empty.
- **Housekeeping** → single italic line (stale Maps by name/days; missing floor template). Only if the refresh did something.
- **Listening check** → efforts with `external_input.stale: true`; use the Map `purpose` as the context hint. Omit if none.

#### Fuzzy item detection

After computing Important Items, flag low-confidence rankings: two efforts within 0.05 in different batches; high recency (+0.12+) on low base (<6); overdue Minor Actions in low-weight Maps; a prior calibration correction touched this effort in a similar position. Render 1–2 italic lines. Omit if none.

---

### Dyad Route — Assisted-Explicit-Capture

**Noticing ≠ committing.** During the session the agent may notice a task, idea, or commitment surface in conversation — and it *should* offer to capture it. But the vault write is **gated on explicit assent**. There is no passive/firehose extraction: ideation generates dozens of maybe-tasks, and auto-materializing them treats noise as commitment and buries real signal.

**The pattern:**
1. **Notice** — a concrete actionable or commitment appears in conversation.
2. **Offer** — one lightweight line: *"Want me to capture that?"* (or name it: *"Capture 'call the plumber' to house?"*).
3. **On explicit assent only** — route through the existing path: invoke `/capture` (which dispatches a background sub-agent to write the `Inbox/` file), and auto-`/triage` picks it up at the next refresh. Do NOT write to a Map or Note directly from a noticed item — capture → triage is the single path, so duplicates are handled by the *existing* `/triage`/`/defrag` misclassification catch, exactly as today. No new dedup/provenance lifecycle.
4. **On silence or "no"** — drop it. Do not capture. Do not re-offer the same item repeatedly.

**Why this is correct (state it if the user asks why the draft is thin):** the proposer only sees what was deliberately captured. A sparse capturer gets a floor + deadline-leaning draft — that is the honest, correct behavior, not a bug. Capturing more (deliberately) enriches the pool; the system will never do it for you behind your back.

---

### Dyad Surface — Accept/Edit Loop + Calibration Stamping

The pre-gate accept/edit exercise **is the calibration engine**. One pass feeds all three signals; only BCR graduates (via `/close`), ACR floors graduation, PAR is a health signal.

**Pre-gate (`capacity_phase != "graduated"`):**
1. Present the draft (rendered above) with the prompt *"Does this draft match your capacity today?"*
2. The user accepts / edits (reorder, add, remove, swap, resize) / commits.
3. **Stamp PAR** (ordering fidelity) — a `PAR-ROW` to the Session Log:
   ```
   PAR-ROW | date=YYYY-MM-DD | session=<n> | corrections=<count of reorder corrections; 0 = silence/accepted> | prompted=<yes|no>
   ```
   `corrections=0` means the surfaced order stood. Calibration-only — does NOT gate.
4. **Stamp ACR** (composition floor) — an `ACR-ROW` to the Session Log, computed from the draft vs. what the user committed:
   ```
   ACR-ROW | date=YYYY-MM-DD | proposed=<# draft items> | committed=<# items user kept/committed> | covered=<# committed that came from the draft> | c=<covered/proposed> | acceptance=<clean|edited|rejected> | edits=<count add+remove+swap+resize> | rejected=<yes|no> | override=<yes|no> | origin=ranked:<N>,floor:<N>,deadline:<N>,user:<N>
   ```
   - `c` (coverage) feeds `rolling_acr` and the ACR revert; `edits` feeds `median_edits`. The composition floor is `rolling_acr ≥ 0.60 AND median_edits ≤ 3`.
   - `origin` tags the committed items by source layer — **use `deadline:` (never `cal:`)** for the due-date layer.
   - `rejected=yes` if the user threw out the whole draft; `override=yes` if today is an inspiration-override pivot off the committed agenda.
5. **Mirror to the calibration note** (legibility) — append a human row to the `## Accuracy Tracking` (PAR) and `## ACR Tracking` tables in `${PULSE_VAULT}/Notes/pulse-priority-calibration.md`. The Session-Log rows are the **gating** source (`compute_gates` greps `Daily/logs/*-log.md`); the calibration-note tables are human mirrors — keep both, but the log row is authoritative.
6. Log the validation outcome to the Session Log as `### Priority Validation — HH:MM` (accepted / corrected + correction detail). If the user corrects the *ordering*, also write a correction entry inline to the `## Corrections` section with the mis-ranked effort, weight breakdown, component at fault, reasoning, and correction type (`ordering | suppression-error | missing-item | wrong-urgency`).

**Post-gate (`post_gate == true`):** keep calibration **light** — the draft leads and the loop is lighter, but still stamp the `ACR-ROW` and `PAR-ROW` when the user edits the draft (the gate is derived live and can still revert; the composition floor must keep seeing data). No heavy validation ceremony — a single `_Adjust the draft?_` suffices.

---

### Act — Log

7. **Log suppression reasoning** — after the briefing, append a suppression trace to `Daily/logs/YYYY-MM-DD-log.md` (create the file/dir if needed). Do NOT write this to the Daily note.
   ```
   ### Pulse Briefing — HH:MM

   **Gate**: phase=[backtest|graduated], post_gate=[true|false], bcr=[X.XX|—], reliable_days=[N], rolling_acr=[X.XX|—], median_edits=[N|—], reverts=[none|bcr|acr]
   **Mode**: [pre-gate: ranked pool leads | post-gate: draft leads, pool → landscape.json | agenda-override]
   **Proposal**: sized_by=[capacity|static-floor], layers=[deadline:N,floor:N,core:N,stretch:N,slack:N], confidence=[clean|turbulent]
   **Important Items**: [item] ([effort], score: X.XX), ...
   **Suppressed batches**: [Batch]: combined weight X.XX < 40% of top, no due dates
   **Suppressed efforts**: [effort]: 0 loops, last_active [N]d, no due within 7d
   **Resurfaced**: [note-slug] ([effort], [timescale] — [N]d)
   **Inline refresh**: triaged N inbox, reconciled N maps, flagged N stale
   ```
   Omit any zero section. The key value is the suppression + gate reasoning — why something wasn't shown, and which mode/gate produced this briefing.

8. **Commit-time ACR/PAR rows** — when the user commits the agenda (step 8 below), that is when the `ACR-ROW` and `PAR-ROW` from the accept/edit loop are finalized and appended (the loop above computes them; the commit fixes the values). These rows are what `/close` and the gate read tomorrow.

---

### Dyad Route — Build the Agenda

9. **Wait for direction.** Do not assume what the user wants. When they indicate direction, build the day's agenda.

10. **Build the Daily Note from conversation** — when the user commits:
   a. Create `Daily/YYYY-MM-DD.md` if absent (Daily Note template frontmatter).
   b. The committed agenda is the accepted/edited draft, grouped by layer/batch. In post-gate the draft is the default agenda; in pre-gate it's the draft the user accepted or edited off the ranked pool.
   c. Scan remaining Maps (routine/maintenance) for time-sensitive items so nothing falls through cracks — but only add on explicit inclusion (assisted-explicit-capture applies).
   d. **Mirror new agenda items to Maps** — any agenda item not already in a Map is written as a Minor Action in the appropriate Map (the Daily Note is today's selection; the Map is the source of truth for loops).
   e. Write a `### Stretch` subsection for the stretch layer — `/close` counts completions above vs. under it (`completed_committed` vs `completed_stretch`), so the boundary must be a literal `### Stretch` header.
   f. Present the agenda for one confirmation pass, then write to file. Subsequent Daily-Note updates during the session happen silently.

### Note on Inbox
Inbox items are auto-triaged during the inline refresh (Phase A). No separate "N pending triage" line — by briefing time the Inbox should be clear. If auto-triage couldn't classify an item, mention it in Housekeeping.

### Full view on request
If the user says "unfold" / "full landscape" / "show all", present the batch landscape (ordered by combined weight, open loops, last active, top thread) + a Stale Maps list. In post-gate, `/landscape` is the dedicated command for the suppressed ranked pool; "unfold" still shows the batch landscape.

### Bootstrap
See **Sense — First-Run & Setup Detection** at the top. Bootstrap and the setup seed always run first, before any vault reads.

### Key Principles
- **The candidate pool is explicit capture, not conversation mining.** Notice → offer → capture-on-assent. Never materialize a task the user didn't commit.
- **Freeze before you negotiate.** The proposal (and its `binding_pred`) is fixed on disk before the accept/edit conversation — `/close` scores an untouched prediction.
- **The gate is live; the stamp is ceremonial.** Post-gate is recomputed every run and reverts fire instantly; only `/close` advances the stamp, and it never un-stamps.
- **"deadline"/"due", never "calendar".** The due-date layer is a live vault layer, not external-calendar ingestion.
- Lead with what matters; suppress low-signal efforts — show the cockpit, not the full instrument panel.
- Keep the briefing concise — a cockpit, not a report.
