---
name: pulse
description: Start a PULSE session — load priorities, show current focus, and surface what matters now. Use at the beginning of any work session.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Glob, Grep, Edit, Write, Bash
srsa: Sense+Route+Surface+Act
---

## PULSE Session Start

You are the agent interface for the user's PULSE (Priority-Updated Living System Engine) vault.

### Sense — First-Run Detection

**Before any vault reads**, check whether the vault needs bootstrapping:

```
Condition: pulse-vault/ has no user Maps
           (Maps/ absent, empty, or contains only [INIT]*.md files and _system/)
```

If true: immediately invoke `/efforts bootstrap`. Bootstrap is fully conversational — the agent asks the user to describe their life areas, generates Maps and writes `user.config.yaml`, then returns here to continue the pulse protocol from Step 1.

Do NOT attempt to read INDEX.md, run pulse-calc.py, or process Inbox before bootstrap completes. An empty vault will produce errors and empty output that mislead the user.

---

### Sense — Load State

1. **Read `Maps/INDEX.md`** — get `priority_weight`, `open_loops`, `last_active`, `top_item`, and `next_due` for all efforts in one read. Fall back to scanning all Maps individually if INDEX.md is missing or corrupted.

2. **Read today's Daily note** (`Daily/YYYY-MM-DD.md`) if it exists — check what's already been generated or completed.

2.5. **Freshness check** — evaluate today's Daily note frontmatter (already read in step 2) for `last_refreshed` timestamp, and scan `Inbox/` for untriaged items (Glob — cheap, no file reads):

   **Phase A (inbox triage) always runs** — regardless of freshness state. Untriaged items don't age out; they persist until processed.

   | `last_refreshed` | Action |
   |---|---|
   | Set today | **Phase A only** — triage inbox, skip phases B–F (state is fresh) |
   | Not set | **Full inline refresh** — Phase A + phases B–F |

   Timestamps are date-scoped: "set" means present in **today's** Daily note frontmatter. A new calendar day = new Daily note with no timestamps = automatic cold start. This is correct — recency and urgency values shift overnight.

   Log to Session Log: `### Startup — HH:MM` with `Freshness: last_refreshed [HH:MM|stale], inbox: [N untriaged]. Skipped: [phases B-F|none]`

### Inline Refresh

3. Before the briefing, silently run a single-pass refresh that merges defrag reconciliation and recompute into one read cycle:

   #### Act — Inbox Triage

   **Phase A** (always runs, even when close flag is set):
   - First, process any pending `Inbox/multi-agents/*.md` task results (same logic as `/triage` Phase -1: read frontmatter + Result, present summary, convert Vault Updates Needed to agent staging files or apply directly, move to archive). Exclude `CLAUDE.md` and `archive/`. Log: `Processed N multi-agent results.`
   - Auto-triage any pending `Inbox/` captures (match content against Maps, create Notes, update Maps — no confirmation; exclude `Inbox/multi-agents/`). After triage, archive each processed file to `Inbox/archive/`.
   - **Safety net**: glob for any `Inbox/*.md` files with `triaged: true` still in root — move them to `Inbox/archive/` (catches incomplete prior triage runs).

   #### Sense — Scan and Compute (script-delegated)

   **Phases B–D**:
   ```bash
   uv run pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --briefing --cache "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-calc.json"
   ```
   Read the cached file directly (`Daily/cache/YYYY-MM-DD-calc.json`) — single Read, ~600 lines. Key fields: `efforts` (weights, loops, staleness), `important_items` (effort-capped, scored), `waiting` (with `gate` and `days`), `batches` (with `gated` flag), `resurfacing`, `warnings`.

   On subsequent `/pulse` calls the same day, read the cache file instead of re-running the script (same freshness gate as before — `last_refreshed` in Daily note).

   Agent still reads Maps/Notes for context text. On script failure, fall back to SYSTEM.md Section 7 formulas.

   **Waiting display**: `gate: true` → Waiting line. `gate: false` → Important Items. Escalate items where `days >= 3`.

   #### Act — Persist and Stamp

   **Phase E — Single write pass**:
   - For each Map with changed values, write `priority_weight` + `open_loops` in one frontmatter update
   - When the agent recognizes external-frame material in conversation about an effort, update `last_external_input: YYYY-MM-DD` in that Map's frontmatter. This is a binary recognition (bump date or don't), not a logging task. Conservative misses are fine — fail-safe direction is the staleness timer running longer.
   - Write `Maps/INDEX.md` — update rows for any Maps whose `priority_weight`, `open_loops`, `last_active`, or top-urgency signals changed. Refresh `Top Item` and `Next Due` columns from current effective_item_score rankings. Update frontmatter `updated: YYYY-MM-DD`. Keep rows ordered by `priority_weight` descending.

   **Phase F — Log and stamp freshness**:
   - Single combined entry `### Inline Refresh — HH:MM` with: triage summary, reconciliation results, stale flags + overdue Minor Actions, weight table with deltas (see /recompute log format)
   - Set `last_refreshed: HH:MM` in today's Daily note frontmatter (gates subsequent `/pulse` skip for the rest of the day)

### Surface — Session Briefing

4. **Present a compact session briefing** (default view):

```
## PULSE — [date]

### Important Items
1. [description] ([effort]) — score: X.XX, due: [date]
2. [description] ([effort]) — score: X.XX, high
...

### Between Tasks
N. [description] ([effort]) — score: X.XX
...
[lightweight items for breaks — scheduling, errands, quick wins]

[CRITICAL: Render ALL items from the script's `important_items` list as Important Items. Do NOT re-rank, filter, or suppress. "Between Tasks" is agent-sourced — scan Minor Actions across Maps for peripheral/break-time items not in `important_items`. See "Between Tasks — Agent Classification" in Route for sourcing logic.]

### Noticed
- [observation — connection, tension, pattern, or item that caught attention during the scan]
- [observation]
[Agent-sourced. Up to 10 observations from the reasoning process. Omit if nothing struck.]

_Waiting: [item] ([effort], due [date]), [item] ([effort], **[N]d waiting**). [N] items on hold._
_Escalation: [item] ([effort]) — [N]d waiting, re-evaluate?_
_Housekeeping: [summary]. [Effort] Map stale ([N] days)._
_Listening check: [effort] — [N]d since external input. What's the current read from [context hint]?_
_Resurfacing: [note title] ([effort], monthly — 27 days since last touch)_

**[Batch]** [combined weight] — [effort] ([N] loops), [effort] ([N] loops)
**[Batch]** [combined weight] — [effort] ([N] loops)
> [N] efforts across [N] batches below the fold. Say **unfold** for full landscape.

### What would you like to work on?
```

**Sub-agent model policy**: All sub-agents spawned during `/pulse` (session log writes, calibration corrections, Phase E Map/INDEX updates) MUST use `model: "opus"` on the Agent tool call. Minimum across all PULSE sub-agents is sonnet; pulse sub-agents use opus for full reasoning fidelity.

**Note loading constraint**: Do not speculatively read Notes during /pulse. Map entry summaries and Minor Actions inline text are the primary sources for Important Items. Only read a specific Note if its effective_item_score places it in the top 3 of Important Items AND the Map summary is insufficient to describe the item. Never read Notes for lower-ranked items or for general context-building.

### Route — What Gets Shown

#### Agenda Override

When today's Daily Note (from step 2) contains an `## Agenda` section, the agenda is a **commitment gate** — it represents deliberate Dyad Route work already done and takes precedence over weight-derived ordering.

1. **Agenda first** — show remaining uncompleted agenda items in their original order and grouping. Strike through completed items. The agenda's section headers (e.g., "Work (until ~5pm)", "Writing (after 5)") are preserved.

2. **New since agenda** — genuinely new items added during this session (from inbox triage, captures, or explicit user additions) appear under `**New since agenda**`. Items that existed when the agenda was built but were not included are NOT new — they were deliberately omitted.

3. **No agenda = weight-derived fallback** — if no agenda exists (cold start, first `/pulse` of the day before direction is given), use the standard Important Items selection logic below.

4. **Broader landscape** — `/pulse` does not surface non-agenda items. Use `/birdseyereview` for the full weight-derived landscape when you want to see what matters beyond today's commitment.

Display format when agenda override is active:
```
### Remaining Agenda
**[Section header from agenda]**
N. item (effort, score: X.XX)
N. ~~completed item (effort)~~ done
...

**New since agenda**
- [item] ([effort]) — score: X.XX
[Only if new items emerged this session. Omit section if none.]
```

#### Important Items selection logic (weight-derived fallback)

Used when **no agenda exists** for today. Once an agenda is built (step 8), subsequent `/pulse` calls switch to Agenda Override above.

Render ALL items from the script's `important_items` list — already scored, effort-capped, and ceiling-applied (20 items max). Do NOT re-filter, suppress, or re-rank. All script output = **Important Items**.

The script did the selection. The agent renders and describes.

#### Between Tasks — Agent Classification (Route)

Between Tasks is a **separate section** sourced by agent judgment, not by the script. It captures peripheral, low-cognitive-weight items suited for breaks between focused work — scheduling calls, errands, quick code fixes, admin tasks.

**Sourcing process** (runs after Important Items are rendered):
1. Scan all `## Minor Actions` sections across Maps — the script already read these for scoring, but items that didn't make the `important_items` ceiling are Between Tasks candidates.
2. Evaluate each candidate: is this a break-time task? Criteria:
   - **Low cognitive overhead** — can be done in 5–15 minutes without deep context loading
   - **Peripheral to focused work** — scheduling, admin, errands, quick fixes, routine checks
   - **Not time-critical** — if it has a due date within 2 days, it belongs in Important Items (escalate to script if missing)
3. Select 3–8 items. Own numbering starting at 1. Include effort slug and score if available, otherwise just the description.
4. If no candidates qualify, omit the section entirely — don't force it.

**What Between Tasks is NOT**: overflow from Important Items, low-ranked Important Items pushed down, or a dumping ground for everything the script excluded. It's a curated break-time list that requires the agent to understand the nature of each task.

**SRSA boundary**: The script (Sense) computes scores and applies mechanical filters. The agent (Route) classifies task character — "is this a break-time errand or a focused work item?" — using contextual judgment that a formula can't capture.

#### Noticed — Agent Surface (max-effort yield)

The agent is already reasoning deeply across the full landscape during `/pulse`. **Noticed** gives those observations a place to land instead of evaporating.

During the scan (reading INDEX, cache, Maps, Minor Actions), surface anything that caught attention:
- **Cross-effort connections** — two efforts touching a shared concern from different angles
- **Tensions** — competing time/energy demands, contradictory priorities, items that pull in opposite directions
- **Patterns** — recurring themes across efforts, clusters of similar blockers, momentum shifts
- **Misfit items** — things that resist their current classification, efforts that feel over/under-weighted for reasons the formula can't capture
- **Emergence** — anything that doesn't fit existing frames (Sati territory — log to `Sati/emergence-log.md` if it recurs)

Up to 10 observations. Brief — one line each, enough to seed a conversation, not a full analysis. If nothing struck, omit the section. Do not fabricate observations to fill space.

This is the dividend of max-effort reasoning: the agent does the deep thinking anyway, and Noticed makes the byproducts visible. It's Sati-adjacent but lighter — noticing, not investigating.

#### Compact view rendering rules

The script provides `batches` (with `gated` flag), `resurfacing` candidates, and `external_input.stale` per effort. The agent renders these:
- **Gated batches** → fold line ("say unfold for full landscape"). Omit if none gated.
- **Effort-level suppression** — within shown batches, omit efforts where `loop_count == 0` and `days_since_active > 7` and no due within 7d. Exception: resurfacing candidates are not suppressed.
- **Resurfacing** → italic line after Housekeeping. Omit if empty.
- **Housekeeping** → single italic line (stale Maps by name and days). Only if the refresh did something.
- **Listening check** → efforts with `external_input.stale: true`. For each stale effort, use its Map `purpose` field as the context hint (e.g., "What's the current read from [purpose-derived context]?"). Omit if none flagged.
- **Batches** → single line each with effort names and loop counts. No shared-context descriptions.

4.5. **Fuzzy item detection** — after computing Important Items, flag items where ranking confidence is low:
   - Two efforts within 0.05 weight of each other in different batches (arbitrary ordering)
   - High recency (+0.12 or more) on low base (<6) effort (activity volume ≠ importance)
   - Overdue Minor Actions in low-weight Maps (real urgency in suppressed effort)
   - Previous calibration correction touched this effort in a similar position

   Render as 1-2 italic lines after Important Items:
   ```
   _Fuzzy: [effort] (X.XX) — [reason it might be mis-ranked]_
   ```
   Omit if no fuzzy items.

### Dyad Surface — Validate and Direct

4.6. **Validation prompt** (Phase 1 only) — after Important Items + Fuzzy, add:
   ```
   _Does this ordering match your priorities today?_
   ```
   - Silence or continuation = acceptance
   - If the user corrects the ordering, delegate to a background agent to write a correction entry to `Notes/pulse-priority-calibration.md` with: the mis-ranked effort, full weight breakdown, component at fault, user's reasoning, and correction type (`ordering | suppression-error | missing-item | wrong-urgency`)
   - Log validation result to Session Log as `### Priority Validation — HH:MM`

   **Phase 2 behavior**: Only show validation prompt when fuzzy items exist. Check PAR and phase criteria in `Notes/pulse-priority-calibration.md` to determine current phase.

### Act — Log

5. **Log suppression reasoning** — after generating the briefing (step 4), append a suppression trace to `Daily/logs/YYYY-MM-DD-log.md`. Create the file (and `Daily/logs/` directory) if they don't exist. Do NOT write this to the Daily note itself.

   Format:
   ```
   ### Pulse Briefing — HH:MM

   **Important Items**: [item] ([effort], score: X.XX), [item] ([effort], score: X.XX), ...
   **Suppressed batches**:
   - [Batch]: combined weight X.XX < 40% of top (X.XX), no due dates, no stale waiting
   **Suppressed efforts** (within shown batches):
   - [effort]: 0 open loops, last_active [N] days ago, no due within 7d
   **Resurfaced**: [note-slug] ([effort], [timescale] — [N] days since last touch)
   **External input staleness**: [effort] ([N]d since input, cadence: [N]d), ...
   **Inline refresh**: triaged N inbox, reconciled N maps, flagged N stale
   ```

   Omit any section with zero items. The key value here is the suppression reasoning — it records *why* something wasn't shown, which is otherwise invisible and the hardest class of bug to trace.

   If no Daily Note exists yet, create one with minimal frontmatter (no Session Log section — that goes in `Daily/logs/`).

### Surface — On Request

6. **Full view on request** — if the user says "unfold", "full landscape", "show all", or similar at any point in the conversation, present:

```
### Full Landscape

**[Batch]** [combined weight]
- [effort] (weight: X.XX) — [N] open loops, last active [date]
  [Top thread or "No active threads"]
- [effort] (weight: X.XX) — [N] open loops, last active [date]
  [Top thread or "No active threads"]

[...all batches, ordered by combined weight...]

### Stale Maps
- [effort] — last active [N] days ago
[Only if any Maps have last_active > 7 days. Otherwise omit.]
```

### Dyad Route — Build the Agenda

7. **Wait for direction.** Do not assume what the user wants to work on. When they indicate direction, build the day's agenda (step 8).

8. **Build the Daily Note from conversation** — when the user indicates what they want to work on:

   a. Create `Daily/YYYY-MM-DD.md` if it doesn't exist (use Daily Note template frontmatter).
   b. Pull top items from the Maps the user indicated interest in — these go first, grouped by batch.
   c. Scan remaining Maps (especially family-social, house) for time-sensitive or routine items. Add as a lightweight section so nothing falls through cracks.
   d. Omit empty efforts. Keep it to 8-15 items — working agenda, not exhaustive audit.
   e. Present the agenda in conversation for one confirmation pass. After confirmation, write to file. Subsequent Daily Note updates during the session happen silently.

### Note on Inbox
Inbox items are auto-triaged during the inline refresh step (Phase A). There is no separate "N items pending triage" line — by the time the briefing is presented, the Inbox should be clear. If auto-triage could not classify an item, mention it in the Housekeeping line.

### Bootstrap
See **Sense — First-Run Detection** at the top of this skill. Bootstrap detection always runs first, before any vault reads.

### Key Principles
- Lead with what matters, not what's overdue
- Surface cross-effort tensions if efforts compete for time
- Suppress low-signal efforts — show the cockpit, not the full instrument panel
- Keep the briefing concise — this is a cockpit, not a report
