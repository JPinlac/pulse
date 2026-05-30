# PULSE Engine Interface Specification

> This document defines the contract between the PULSE engine and the user's vault. The engine
> reads and writes the vault according to these specifications. A conforming vault will work with
> the engine; a non-conforming vault will produce undefined behavior.

---

## 1. Runtime Environment Contract

### Vault Path Resolution

The engine resolves the vault path in this priority order:

1. `--vault <path>` CLI argument (highest priority)
2. `$PULSE_VAULT` environment variable
3. `pulse-vault/` relative to the repo root (default)

**Recommendation**: Set `PULSE_VAULT` in your shell profile once:
```bash
export PULSE_VAULT=/absolute/path/to/your/pulse-vault
```

### Engine Boundary Guarantee

The engine (`pulse-engine/` and `.claude/skills/`) **never writes outside the vault path**. All
file writes are contained within `$PULSE_VAULT/`. The only exception is temporary files in
`/tmp/pulse-*` created by `/dispatch` for inter-agent communication.

---

## 2. Required Vault Directory Structure

```
$PULSE_VAULT/
├── user.config.yaml          ← effort definitions, aliases, batches (required)
├── Maps/                     ← effort MOCs (required, agent-managed)
│   ├── INDEX.md              ← precomputed priority landscape (agent-generated)
│   └── _system/              ← system-type Maps (not user efforts)
│       └── Pulse.md          ← engine meta-effort (shipped, do not delete)
├── Notes/                    ← content notes (flat, agent-managed)
│   └── archive/              ← auto-archived completed notes
├── Daily/                    ← session agendas (YYYY-MM-DD.md)
│   ├── logs/                 ← decision traces (YYYY-MM-DD-log.md)
│   └── cache/                ← script computation cache (YYYY-MM-DD-calc.json)
├── Inbox/                    ← zero-friction captures (.md, triaged: false)
│   └── multi-agents/         ← inter-agent result boundary
└── Sati/                     ← emergence awareness log
```

**The engine does not require** `Home.md`, `Templates/`, or `Queries/` — these are optional
Obsidian-facing files. The engine reads and writes only the directories above.

---

## 3. user.config.yaml Schema

See `user.config.schema.json` for the machine-readable JSON Schema. Summary:

```yaml
# Required fields:
efforts:          # list of user effort definitions
  - slug:         # string, kebab-case, unique, not "pulse" (reserved for system)
    batch:        # string, must match a name in batches[]
    base_priority: # integer 1–10
    purpose:      # string, one-sentence description
    aliases:      # list of strings (optional)

# Optional fields:
batches:          # override or extend the default batch set
  - name:         # string, unique
    shared_context: # string, describes the cognitive domain
    mindset:      # string, describes the cognitive mode

codebase_registry: # for /dispatch skill
  - name:         # string (effort slug or project name)
    path:         # string, absolute path to the project directory
```

**Reserved slugs**: `pulse` is reserved for the engine's system Map and must not appear in
`efforts[]`. The engine will reject a config that lists `pulse` as a user effort.

**Default batches** (used when `batches:` is omitted):

| Name | Shared Context | Mindset |
|------|---------------|---------|
| Work | Professional environment, tools, stakeholders | Analytical, execution-focused |
| Projects | Creative tools, structured goals, artifacts | Creative, hyperfocus-compatible |
| Maintenance | Obligations, routines, logistics | Practical, deliberate |
| Leisure | Personal media, hobbies, recharge | Receptive, restorative |

---

## 4. Map Frontmatter Contract

The engine reads these fields from each Map file (`pulse-vault/Maps/*.md`):

```yaml
---
type: map                          # required: "map" or "system-map"
effort: <slug>                     # required: must match user.config.yaml
context_batch: <batch-name>        # required: must match a batch name
priority_weight: <float>           # agent-managed (computed by pulse-calc.py)
base_priority: <1-10>              # required: matches user.config.yaml
last_active: <YYYY-MM-DD>          # agent-managed
last_external_input: <YYYY-MM-DD>  # agent-managed
open_loops: <int>                  # agent-managed (computed by pulse-calc.py)
related_efforts: [<slug>, ...]     # optional
purpose: <string>                  # required: one-sentence description
aliases: [<string>, ...]           # optional: alternative names for /focus resolution
---
```

**System Maps** (`type: system-map`) in `Maps/_system/`:
- Excluded from personal priority computation, batch gating, and loop_factor
- Excluded from `user.config.yaml` effort list
- Appear in a separate `system_efforts` key in `pulse-calc.py` JSON output
- Never suppressed by batch gating — always shown in their own section

---

## 5. Note Frontmatter Contract

The engine reads these fields from each Note file (`pulse-vault/Notes/*.md`):

```yaml
---
type: note                         # required
subtype: note|log|plan|reference   # required
efforts: [<slug>, ...]             # required: list of effort slugs this note belongs to
status: active|waiting|someday|done|archived  # required
created: <YYYY-MM-DD>              # agent-managed
updated: <YYYY-MM-DD>              # agent-managed
due: <YYYY-MM-DD>                  # optional
importance: low|medium|high        # required (default: medium)
effort_level: trivial|small|medium|large  # optional
timescale: daily|weekly|monthly|quarterly|biannual|annual  # optional
depends: [<note-slug>, ...]        # optional
related: [<note-slug>, ...]        # optional
---
```

**Loop counting**: Only `status: active` or `status: waiting` Notes with `subtype: note|log|plan`
count as open loops. `subtype: reference` Notes are excluded.

---

## 6. Priority Computation Contract

All priority weights and effective item scores are computed by `pulse-engine/scripts/pulse-calc.py`.
The engine never computes scores inline — always delegates to the script.

**CLI invocation**:
```bash
uv run pulse-engine/scripts/pulse-calc.py \
  --vault "${PULSE_VAULT:-./pulse-vault}" \
  --briefing \
  --cache "${PULSE_VAULT:-./pulse-vault}/Daily/cache/$(date +%Y-%m-%d)-calc.json"
```

**JSON output schema** (key fields):
```json
{
  "efforts": [
    {
      "slug": "work",
      "priority_weight": 1.05,
      "open_loops": 3,
      "last_active": "2026-05-30",
      "context_batch": "Work",
      "top_item": "description",
      "next_due": "2026-06-01"
    }
  ],
  "system_efforts": [
    {
      "slug": "pulse",
      "type": "system-map",
      "priority_weight": 0.70
    }
  ],
  "important_items": [...],
  "waiting": [...],
  "batches": [...],
  "resurfacing": [...],
  "warnings": [...]
}
```

---

## 7. File Lifecycle Contract

| Operation | Who does it | Where |
|-----------|-------------|-------|
| Create Map | Agent (`/efforts add` or `/efforts bootstrap`) | `pulse-vault/Maps/` |
| Update Map frontmatter | Agent (pulse-calc.py output + skill logic) | `pulse-vault/Maps/*.md` |
| Create Note | Agent (`/triage`, `/capture`) | `pulse-vault/Notes/` |
| Archive Note | Agent (`/defrag`, 7+ days after `status: done`) | `pulse-vault/Notes/archive/` |
| Create Daily Note | Agent (`/pulse`, `/birdseyereview`) | `pulse-vault/Daily/YYYY-MM-DD.md` |
| Write Session Log | Agent (6 operations: /recompute, /defrag, /pulse, /triage, validation, Sati) | `pulse-vault/Daily/logs/YYYY-MM-DD-log.md` |
| Write Cache | `pulse-calc.py --cache` | `pulse-vault/Daily/cache/YYYY-MM-DD-calc.json` |
| Create Capture | Agent (`/capture`) | `pulse-vault/Inbox/YYYY-MM-DD-[slug].md` |
| Write Sub-Agent Result | Dispatched agent | `pulse-vault/Inbox/multi-agents/YYYY-MM-DD-HH-MM-[slug].md` |

**The user never writes frontmatter.** All YAML blocks are created and maintained by the agent.

---

## 8. Bootstrapping a New Vault

1. Copy `pulse-engine/user.config.example.yaml` → `pulse-vault/user.config.yaml`
2. Edit `user.config.yaml` — replace example efforts with your own
3. Run `/efforts bootstrap` — generates `Maps/*.md` from your config
4. Run `/pulse` — starts your first session

The `[INIT]` template Maps in `pulse-vault/Maps/` are placeholders. `/efforts bootstrap`
replaces them with Maps generated from your `user.config.yaml`.
