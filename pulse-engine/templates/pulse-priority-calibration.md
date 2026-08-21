---
title: "[INIT] Priority & Capacity Calibration"
type: note
subtype: reference
status: active
effort: pulse
capacity_phase: backtest
capacity_graduated_on: null
capacity_graduated_bcr: null
capacity_graduated_reliable_days: null
rubric_version: "1.0"
---

# Priority & Capacity Calibration

> **[INIT] scaffold — do not delete the section headers or table headers below.**
> The runtime reads named sections out of this note. A renamed header silently
> zeroes the signal that section feeds. Skills append rows; the user does not
> hand-edit metadata.

<!--
SIGNAL MAP — which table feeds which decision, and what actually gates.

  PAR  (## Accuracy Tracking)   → priority ORDERING calibration.
       Was the ranking right? Corrections=0 means the surfaced order stood.
       CALIBRATION-ONLY. Does NOT gate capacity graduation. Read by the
       script's _parse_par_table (PAR fallback) and by the /pulse validation step.

  ACR  (## ACR Tracking)        → agenda COMPOSITION floor.
       Did the proposed agenda survive contact with the user? c = coverage of
       the committed set; edits = how much reshaping was needed.
       Feeds the compound graduation gate (rolling_acr >= 0.60 AND
       median_edits <= 3) and the ACR revert. This table is the human-legible
       MIRROR; the authoritative rows are the `ACR-ROW` lines in
       Daily/logs/*-log.md, which compute_gates greps.

  BCR  (## Capacity Verdict Tracking) → the GRADUATION gate.
       Did the day's binding constraint (depth/resistance) land inside the
       predicted range? bcr = binding-HITs / reliable-days over 14d.
       ONLY BCR (compound) GRADUATES capacity from backtest to draft-leads:
         bcr >= 0.80 AND rolling_acr >= 0.60 AND median_edits <= 3
         AND reliable_days >= 10.
       This table is the human-legible MIRROR; the authoritative rows are the
       `CAPACITY-VERDICT` lines in Daily/logs/*-log.md, written by
       `pulse-calc.py --verdict` at /close and grepped by compute_gates.

  Only BCR graduates. PAR and ACR are retained as calibration health signals;
  PAR never gates, and ACR gates only as a *floor* inside the BCR-led compound.

PHASE STAMP (frontmatter capacity_phase) is skill-managed, not script-read.
  The script never reads frontmatter — the stamp is advanced ONLY at the /close
  graduation ceremony (when gates.capacity.gate_met AND stamp != "graduated")
  and never un-stamps. Reverts fire live from compute_gates, not from the stamp:
    post_gate = (capacity_phase == "graduated")
                AND NOT gates.capacity.revert_triggered
                AND NOT gates.agenda_composition.revert_triggered
-->

## Accuracy Tracking

<!--
Script-parsed. compute_gates / _parse_par_table read THIS section only
(regex: header must be exactly `## Accuracy Tracking`; rows must be
`| <YYYY-MM-DD> | <int session> | <int corrections> | <float PAR> | ...`).
PAR fallback = last matching row's PAR value. Corrections=0 → the ranking stood.
The `## ` header on the next section is what stops this parser, so the ACR
table below cannot pollute the PAR fallback. CALIBRATION-ONLY — does NOT gate.

Append one row per validated session, e.g.:
  | 2026-07-20 | 1 | 0 | 1.00 | backtest |
Placeholder rows using YYYY-MM-DD are ignored by the parser (they do not match
the date regex), so a fresh vault reports no PAR until the first real row lands.
-->

| Date | Session | Corrections | PAR (14-day rolling) | Phase |
|------|---------|-------------|----------------------|-------|
| YYYY-MM-DD | — | — | — | backtest |

## ACR Tracking

<!--
Human-legible mirror of the `ACR-ROW` session-log lines (Daily/logs/*-log.md),
which are what compute_gates actually greps for rolling_acr / median_edits /
the ACR revert. NOT script-parsed from this note. Written by /pulse step 8.
  c            = covered / committed (agenda coverage; feeds rolling_acr floor 0.60)
  Edits        = reshaping applied (feeds median_edits floor 3)
  Rejected     = full-agenda rejection (yes|no)
  Override     = user overrode the sized proposal (yes|no)
  Stretch S/K  = stretch shipped / stretch offered
Origin tags on the ACR-ROW use the deadline layer name: origin(ranked:N,floor:N,deadline:N,user:N).
-->

| Date | Proposal size | Committed | Covered | c | Acceptance | Edits | Rejected | Override | Stretch S/K | Notes |
|------|---------------|-----------|---------|---|------------|-------|----------|----------|-------------|-------|
| YYYY-MM-DD | — | — | — | — | — | — | no | no | 0/0 | — |

## Capacity Verdict Tracking

<!--
Human-legible mirror of the `CAPACITY-VERDICT` session-log lines
(Daily/logs/*-log.md), written by `pulse-calc.py --verdict` at /close and
grepped by compute_gates for bcr / reliable_days. NOT script-parsed from this
note. UNRELIABLE rows are excluded from reliable_days and bcr. THE graduation
signal — see the SIGNAL MAP above; only BCR (compound) graduates.
  range          = low-high predicted budget
  count          = HIT | DIR-HIT | MISS | UNRELIABLE
  binding_pred   = predicted binding constraint (depth|resistance|both|neither)
  binding_actual = observed binding constraint (committed BLIND at /close,
                   before the frozen binding_pred is opened — freeze discipline)
  binding        = HIT | MISS (the BCR numerator)
  stretch        = done/offered
-->

| Date | range | actual | count | binding_pred | binding_actual | binding | stretch | calc | rubric |
|------|-------|--------|-------|--------------|----------------|---------|---------|------|--------|
| YYYY-MM-DD | — | — | — | — | — | — | 0/0 | — | 1.0 |

<!--
The `## Corrections` section below is script-parsed by load_calibration, which
scans EVERY line in-section (HTML comments included) for the bold "Mis-ranked"
and "Expected" tokens. So the logging format is documented HERE, before the
header, where it cannot be mis-read as data — the bold markers are intentionally
omitted so this note does not inject a phantom correction:
  Inside the section, log a mis-ranking as two bold lines — a "Mis-ranked" line
  naming the effort slug + position, then an "Expected" line saying it should be
  higher or lower (with why). The effort slug + direction feed a per-effort
  calibration offset. Leave the section bare until the first real correction;
  load_calibration returns clean when empty.
-->
## Corrections

_No corrections logged yet._

## Patterns

<!--
Script-parsed by load_calibration — each `### ` subheading under this section
is collected as a named calibration pattern. Seed patterns as they are observed.
-->

_No patterns logged yet._
