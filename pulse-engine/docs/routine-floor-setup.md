---
type: doc
subtype: reference
efforts: [pulse]
created: 2026-07-15
updated: 2026-07-15
version: 1
---
# Routine Floor — Setup & Path Reference

## What this is

The **routine floor** is the deterministic, non-negotiable layer of the daily
capacity proposal — the recurring embodied/relational commitments (movement,
practice, family/relationship time, chores) that should appear on every draft
regardless of what else gets captured that day. It is Layer 2 of the
layered-assembly draft (`deadline → floor → core → stretch → slack`) built by
`build_proposal` in `pulse-engine/scripts/pulse-calc.py`.

A missing or empty floor silently degrades **every** draft — historically the
single biggest leak in proposal quality (~25% of committed items previously
fell through this gap). This doc exists so that gap does not reopen in the
public engine.

## The exact path the script reads

`parse_routine_floor()` in `pulse-calc.py` is called with:

```python
floor_path = vault_path / "Templates" / "routine-floor.md"
```

`vault_path` resolves per the standard engine rule (`--vault` flag >
`$PULSE_VAULT` env var > `./pulse-vault` default — see `pulse-calc.py`'s
`main()` and the "Vault Location" section of `pulse-engine/CLAUDE.md`).

**Concretely, for this repo layout**, with the script invoked from the
`pulse/` submodule root and no `--vault`/`$PULSE_VAULT` override, the file the
script reads is:

```
pulse/pulse-vault/Templates/routine-floor.md
```

If that file does not exist, `parse_routine_floor` returns an **empty floor
list plus a `missing_floor_template` warning** — it does not error, and
nothing downstream complains loudly. This is exactly the silent-degradation
failure mode: confirm the file is present at the path above before trusting
any `--propose`/`--candidates` output's floor layer.

## The template source (engine side, ships in the submodule)

The depersonalized example template lives at:

```
pulse/pulse-engine/templates/routine-floor.md
```

This is a **ship-time asset**, not a runtime-read path — the script never
reads `pulse-engine/templates/`. Something must copy (or generate from) this
file into `pulse-vault/Templates/routine-floor.md` before a floor layer will
populate. As of this doc, no wiring exists yet — see "Open: who copies this"
below.

## Format the parser accepts

`parse_routine_floor` strips YAML frontmatter, then matches each body line
against:

```
^-\s+(.*?)\s*\(\s*days:\s*([^;]+);\s*effort:\s*([^)]+)\)\s*$
```

i.e. one bullet per line:

```
- <item text> (days: <days-spec>; effort: <slug>)
```

- `<days-spec>` is either the literal `daily`, or a comma-separated list mixing
  3-letter weekday abbreviations (`mon,tue,wed,thu,fri,sat,sun`) and/or full
  weekday names (`monday,tuesday,…`). Matching is case-insensitive
  (`_floor_matches_day` lowercases before lookup against `_ABBREV_WEEKDAY` and
  `WEEKDAY_MAP`).
- `<slug>` must match an effort slug defined in the user's
  `pulse-vault/user.config.yaml` (see `ENGINE-SPEC.md` §"Bootstrapping a New
  Vault"). A slug that doesn't resolve to a Map still parses fine — it just
  won't classify against anything meaningful downstream.
- No other fields are parsed. Floor items do not carry `importance` — that
  field only applies to Map `## Minor Actions`, not the routine floor.
- Any line that doesn't match the regex exactly (wrong parens, missing
  `days:`/`effort:` labels, trailing text after the closing paren) is silently
  skipped, not warned on. Keep the format exact.

See `pulse-engine/templates/routine-floor.md` for a working example set.

## Open: who copies engine → vault (not resolved by this doc)

This doc fixes *where the script reads from* and *what the source template
looks like*. It does **not** wire the copy step — that is owned by whichever
skill seeds a new vault's `Templates/` directory (the natural owner is
`/efforts bootstrap`, which today only generates `Maps/*.md` and does not yet
touch `Templates/`; a first-`/pulse`-run seed is the other candidate). Until
that wiring lands, a new vault must have `pulse-vault/Templates/routine-floor.md`
placed by hand (copy the engine template above and edit the entries) or the
floor layer will silently stay empty on every `--propose`/`--candidates` call.

Flag this to whoever owns bootstrap/`/pulse` wiring: the fix is a one-line
copy-if-absent (engine template → vault path) at the point the vault is first
provisioned. This doc does not implement it — routine-floor is `pulse-vault/`
runtime content and out of this task's file-ownership scope
(`pulse-engine/templates/` + `pulse-engine/docs/` only).
