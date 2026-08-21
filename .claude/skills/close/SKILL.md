---
name: close
description: Session-close ritual — reflect on what happened, what emerged, what patterns are forming. Produces the capacity verdict / BCR row and fires the graduation transition, then auto-triggers /defrag.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
srsa: Surface+Sense+Act+Route
---

## Session Close

Pure reflection over the day, plus the two deterministic producers no other skill can supply: the **capacity verdict** (today's committed agenda scored against the frozen proposal → the `CAPACITY-VERDICT` / BCR row) and the **graduation transition** (advance the phase stamp the first time the gate crosses). Without this skill no gate ever has data — the whole graduation loop is dark. The agent presents a narrative, the human reflects, then defrag handles the bookkeeping.

### Quick Close (`/close q` or `/close quick`)

If $ARGUMENTS contains `q` or `quick`, run a lightweight save-state (use before clearing context, mid-session checkpoints, etc.):
1. Skip steps 2–5 (no reflection narrative, no flags, no human prompts)
2. Run step 6.5 (inline recompute — captures current state)
3. Run step 6.7 (outcome verdict — cheap: checkboxes + one CLI call; **silent skip** if no frozen artifact for today) and step 6.8 (gate check + graduation transition — silent skip if 6.7 skipped). These produce data; they must not be skipped just because the close is quick, or BCR loses a day.
4. Run step 7's frontmatter updates only — update `items_completed`/`items_deferred` counts and `efforts_touched`. Do NOT fill the `## End of Day` reflection prose (Quick Close skips steps 2–5, so there is no reflection narrative to summarize).
5. **Light defrag (mandatory — do NOT skip)** — this is Sense that must always execute:
   a. Auto-triage Inbox — process any `Inbox/` items where `triaged: false`, archive to `Inbox/archive/`
   b. Reconcile Map counts — for each touched effort, verify `open_loops` = active/waiting Notes + unchecked Minor Actions. Fix mismatches.
   c. Flag stale Maps — flag any Map where `last_active` exceeds its staleness threshold
   d. Scan Minor Actions — check for overdue unchecked items in touched efforts
   e. Log to `Daily/logs/YYYY-MM-DD-log.md`: `### Defrag — HH:MM light` with triage count, reconciliation changes, stale flags, overdue count
6. Set `last_refreshed: HH:MM` in today's Daily note frontmatter — do NOT set `close_complete: true` (checkpoint, not session end)
7. Respond: `State saved. Context is clear to start fresh.`

Total: ~2 turns. The `last_refreshed` timestamp tells the next `/pulse` that state is fresh — it will skip the inline refresh (or run triage-only if new inbox items arrived). No ceremony required.

### Sense — Gather Context

1. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`). If none exists, check what Maps were touched today by looking at `last_active` dates.

2. **Read relevant Maps and Notes** — gather context on what moved today across all active efforts.

### Dyad Surface — Reflect Together

3. **Present a reflection narrative**:

```
## Reflection — [date]

### What Happened
[Narrative summary of the session — what efforts were touched, what work was done,
what conversations happened. Written as prose, not a checklist.]

### What Emerged
[New threads, ideas, or connections that surfaced during the session.
The unplanned stuff — often the most valuable signal.]

### Patterns
[Observations about recurring themes, cross-effort tensions, or shifts in energy.
Only include if genuinely noticed — don't fabricate patterns.]
```

### Route — Flag What Needs Attention

4. **Flag items needing human attention** — only surface things that genuinely need a decision:
   - Items deferred 3+ times (pattern of avoidance — worth naming)
   - Efforts that went dark (active Notes past their timescale staleness window with no status change)
   - Cross-effort tensions (competing priorities that can't both win)
   - Anything that seems stuck or misaligned with stated goals
   - **Newly unblocked** — items whose dependencies were completed today: "Newly unblocked: [[note]] — dependency [[dep]] completed today. This is now actionable."

5. **Invite reflection** — "Anything else on your mind before I clean up?" This is optional. If the user has nothing to add, move on.

### Act — Honor, Recompute, Verdict, File

6. **If the user volunteers status changes** during the reflection conversation (e.g., "that thing is done" or "drop that one"), apply them. But don't prompt for decisions on each item.

6.5. **Session-end recompute** — run `uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --briefing --cache "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-calc.json"` to capture today's activity in a fresh cache. Update Map frontmatter weights from the output. Log weight table to `Daily/logs/YYYY-MM-DD-log.md`.

6.7. **Outcome verdict — freeze-before-conversation (Sense/Act).** This is the **sole producer of the `CAPACITY-VERDICT` / BCR row**; runs in Quick Close too. **Discipline: commit `binding_actual` and the completion counts BLIND — from the user's own close-out words and the Daily Note checkboxes — BEFORE you open the frozen proposal or read `binding_pred`.** The agent that scores must not see the prediction it is grading, or it inflates the exact metric (BCR) that gates graduation. This mirrors the freeze-before-conversation discipline `/pulse` applies to the proposal, now applied to the outcome. Enumerated, in order — do NOT reorder:

   a. **Commit the actuals BLIND — do this FIRST, before ANY read of `Daily/cache/YYYY-MM-DD-proposal.json`, the `binding_pred` field, or the `CAPACITY-FROZEN` row.** From the user's close-out narrative + the Daily Note `## Agenda` checkboxes ONLY, determine and **write down in your response now**:
      - `binding_actual` ∈ {`depth` | `resistance` | `both` | `neither`} — which dimension actually bound the day, with one line of reasoning.
      - `completed_committed` = count of checked items **above** the `### Stretch` subsection (the core / floor / deadline / slack layers — everything committed).
      - `completed_stretch` = count of checked items **under** the `### Stretch` subsection.
      - `override_day` (true/false) — was today an inspiration-override pivot off the committed agenda?
      These four are **committed inputs**. The script never derives `binding_actual` — you commit it blind; the script only does the mechanical HIT/MISS arithmetic against the frozen range.

   b. **Only now** check for the frozen artifact `Daily/cache/YYYY-MM-DD-proposal.json`:
      - **No artifact → skip this step silently** (no row, no log entry, no message). Most days without a `/pulse` proposal hit this.
      - **Static-floor day** (artifact exists but was sized `sized_by: static-floor`, no `capacity` block — inputs were skipped): `--verdict` returns a `skipped` JSON rather than a row (the BCR-poisoning guard — no prediction ⇒ no row). Treat the same as a missing artifact — skip silently. There is nothing to verdict when nothing was predicted.

   c. Run the mechanical verdict — the script does the HIT/MISS/DIR-HIT arithmetic; `binding_actual` is your blind input, never derived:
      ```bash
      uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --date YYYY-MM-DD --verdict \
        --actual '{"completed_committed": N, "completed_stretch": S, "binding_actual": "depth|resistance|both|neither", "override_day": true|false}'
      ```
      (Default proposal path = `$PULSE_VAULT/Daily/cache/YYYY-MM-DD-proposal.json`; `--date` sets both the artifact lookup and the reference date.) If the output carries a `skipped` key → skip silently (static-floor / no-prediction).

   d. Append the CLI-emitted `capacity_verdict_row` **verbatim** under `### Capacity Verdict — HH:MM` in `Daily/logs/YYYY-MM-DD-log.md`, with your one-line `binding_actual` reasoning on the line above it. **Copy the row byte-for-byte** — `compute_gates` re-parses it (`date`, `count`, `binding`; `UNRELIABLE` rows are excluded from `reliable_days`/BCR); a reworded or reformatted column silently breaks the gate.
      - **Verdicts score the ORIGINAL frozen prediction, never a mid-day revision.** This step reads the artifact frozen at proposal time; it never re-runs `--propose`.

6.8. **Gate check + graduation transition (Route/Surface).** Runs only when step 6.7 wrote a real verdict row — today's outcome is then in-window, so the gate sees it. Skip entirely if 6.7 skipped (nothing changed in-window).

   a. Run the compute-only gate status (graph-free — greps the `CAPACITY-VERDICT` / `ACR-ROW` / `PAR-ROW` log rows + the calibration PAR table; no writes, no scheduling):
      ```bash
      uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --gates
      ```
      Read from the JSON:
      - `capacity.gate_met`, `capacity.bcr`, `capacity.reliable_days`, `capacity.rolling_acr`, `capacity.median_edits`
      - `capacity.revert_triggered`, `agenda_composition.revert_triggered`

   b. Read the phase stamp from `Notes/pulse-priority-calibration.md` frontmatter: `capacity_phase` (absent ⇒ treat as `backtest`). This stamp is skill-read only — the script never reads it; the gate is derived live from the log rows.

   c. **Graduation ceremony — asymmetric latch, advance-only.** If `capacity.gate_met == true` AND `capacity_phase != "graduated"`:
      - **Advance the stamp** — this is the ONLY place the stamp ever advances. Write to the calibration-note (`Notes/pulse-priority-calibration.md`) frontmatter:
        ```yaml
        capacity_phase: graduated
        capacity_graduated_on: YYYY-MM-DD
        capacity_graduated_bcr: <capacity.bcr>
        capacity_graduated_reliable_days: <capacity.reliable_days>
        ```
      - **The trigger is a transition detector — the FIRST `/close` on-or-after the crossing, NOT Friday-only.** A sparse user may not close on a Friday for weeks; a latched Friday-only flip would then never fire. Friday flavors the *summary copy*, not the trigger. Deliver the ceremony copy (substitute the live `bcr` and `reliable_days`):
        > 🎓 *Your capacity proposer has graduated — capacity called your day right (BCR `<bcr>` ≥ 0.80) over `<reliable_days>` reliable days, and your drafts held up (few edits). From now on `/pulse` leads with your draft agenda; your full ranked list is one command away: `/landscape`.*

        (If today is a Friday, you may open with a brief Friday flourish; otherwise fire the copy as-is — the crossing, not the weekday, is what matters.)
      - Log `### Graduation — HH:MM` to the session log with `bcr`, `reliable_days`, `rolling_acr`, `median_edits`.

   d. **Revert notice — live, never un-stamps.** If `capacity_phase == "graduated"` AND (`capacity.revert_triggered == true` OR `agenda_composition.revert_triggered == true`):
      - **Do NOT change the stamp.** The latch is asymmetric: graduation advances only at the ceremony and **never un-stamps**. The withdrawal is realized *live* in `/pulse`, whose post-gate branch is `(capacity_phase == "graduated") AND NOT capacity.revert_triggered AND NOT agenda_composition.revert_triggered` — so the ranked landscape leads again the instant a revert is live, with no stored state, and re-leads with the draft automatically once the bad rows age out of the window (the stateless anti-flap guarantee: one breach latches the revert for up to 14 days, so a BCR oscillating in the 0.70–0.80 hysteresis band can't flip the branch on consecutive closes). Both a **BCR** revert (`capacity.revert_triggered`) and an **ACR** revert (`agenda_composition.revert_triggered`) withdraw graduation.
      - Surface one honest line naming which substrate reverted (BCR dip / ACR dip) and that `/pulse` will lead with the ranked landscape until enough new reliable days recover it — no re-ceremony fires on recovery.
      - Log `### Gate Revert — HH:MM` to the session log (substrate, `bcr`/`rolling_acr`, `reliable_days`).

7. **Update the Daily note** — fill in the `## End of Day` section with the reflection summary. Update `items_completed` and `items_deferred` counts, finalize `efforts_touched`. `items_completed`/`items_deferred` count committed-layer items only — stretch completions are tracked separately via the `CAPACITY-VERDICT` row's `stretch=done/offered` field (step 6.7), not folded into these frontmatter counts.

8. **Auto-trigger `/defrag`** — run a full defrag pass. This handles all the mechanical bookkeeping: auto-defer open items, auto-mark checked items done, reconcile Maps, flag stale items.

8.5. **Set freshness + close flag** — after successful defrag + recompute:
   - Set `last_refreshed: HH:MM` in today's Daily note frontmatter (gates `/pulse` inline refresh skip)
   - Set `close_complete: true` (signals a **full** defrag ran — `/pulse` can skip deeper checks like misclassification scan and merge candidate detection beyond what `last_refreshed` alone gates)

### Surface — Close with Warmth

9. **Close with warmth** — after defrag completes, deliver a brief closing message:

```
### You're done.

[1–2 sentences of genuine praise for what was accomplished today — specific to this session, not generic. Reference actual efforts touched or progress made.]

Everything is filed. [If no due items remain open: "Your priority items are in good hands — nothing is falling through the cracks tonight. You can fully disconnect, be present, and rest without the background hum of open loops." If due items are still open: acknowledge them honestly — name what's outstanding, affirm that it's noted and won't be lost, but don't say it's okay to fully disconnect.]
```

   Tone guidelines:
   - **Specific, not generic** — reference actual work done today, not a template affirmation
   - **Brief** — 3–5 sentences total
   - **Warm but not saccharine** — earned praise, not flattery
   - **Honest** — don't offer false reassurance if due items are still open; acknowledge them and affirm they're tracked
   - **Permissive** — explicit "it's okay to let go" framing only when the slate is genuinely clear
   - If a **graduation ceremony** fired in step 6.8, let it lead the close — it is the milestone of the session; the warmth message follows it rather than competing with it.

### Session-Log Rows This Skill Touches

`/close` **writes** exactly one machine-parsed row — copy it verbatim from the CLI so `compute_gates` can re-read it:

- **`CAPACITY-VERDICT`** — emitted by `--verdict`, appended in step 6.7d. Columns:
  `date, range=low-high, actual, count(HIT|DIR-HIT|MISS|UNRELIABLE), binding_pred, binding_actual, binding(HIT|MISS), stretch=done/offered, calc, rubric`.
  `compute_gates` parses `date`, `count`, `binding`; `UNRELIABLE` rows are excluded from `reliable_days` and BCR.

The other capacity rows are produced elsewhere and are only *consumed* by the gate `/close` reads — do not write them here:
- **`ACR-ROW`** (`date, proposed, committed, covered, c, acceptance, edits, rejected(yes|no), override(yes|no), origin(ranked:N,floor:N,deadline:N,user:N)`) — written by `/pulse` step 8.
- **`PAR-ROW`** (`date, session, corrections, prompted(yes|no)`) — written by `/pulse` validation; calibration-only, does not gate.
- **`AGENDA-FROZEN`** (`date, core, floor, deadline, stretch, slack, confidence, sized_by, schema`) and **`CAPACITY-FROZEN`** (`date, rubric, calc, load, mult_depth, mult_res, range=low-high/total, binding, flags`) — emitted by `build_proposal` / `compute_capacity`, copied into the frozen log entry by `/pulse` step 3.5; `/close` reads the frozen artifact they mirror, never rewrites them.

### Sub-Agent Policy

Small single-file writes (Daily note updates, session-log appends, the calibration phase-stamp bump) stay inline — `/close` runs these directly in the main session. The auto-triggered `/defrag` full pass — the heavy multi-file batch — dispatches to a **background** sub-agent (`model: "opus"`) so it doesn't block the close ritual. Background-write policy and history are canonical in `CLAUDE.md` → "Silent File Operations".

### Principles
- **This is reflective, not bureaucratic.** No "defer/wait/done/drop?" loops.
- **The verdict is deterministic, the reflection is not.** Step 6.7's blind-commit discipline and byte-verbatim row are non-negotiable Sense/Act — the gate's integrity depends on the scoring agent not seeing what it grades. Everything around it is Dyad Surface.
- Note what *emerged* — the unplanned connections are often the most valuable signal
- The human reflects on meaning; the agent handles filing
- If the human volunteers decisions during reflection, honor them immediately
- **End with warmth** — earned praise for what was done and explicit permission to disconnect. The user should feel held, not just filed.
- $ARGUMENTS can optionally specify a date other than today
