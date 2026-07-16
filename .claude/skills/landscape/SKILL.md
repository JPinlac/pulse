---
name: landscape
description: Recall the full ranked committed candidate pool suppressed behind a graduated /pulse — cache-first veneer over today's folded landscape, introduced by the graduation event. Boundary vs. /birdseyereview — that skill is a full zero-suppression audit across all Maps for periodic review; /landscape is a same-day recall of the ONE pool /pulse already computed and folded today. Use /landscape to see what today's draft left out; use /birdseyereview for a weekly/after-a-break full sweep.
user-invocable: true
model: sonnet
allowed-tools: Read, Glob, Bash
srsa: Surface
---

## /landscape — Recall the Suppressed Pool

Read-only. `/landscape` exists **only because graduation exists** — pre-gate, `/pulse` already leads with the full ranked pool, so there is nothing to recall. Post-gate, `/pulse` leads with the Draft Agenda and folds the ranked committed pool to a cache file with the line `Full candidate list folded — say /landscape.` This skill is that recall.

**Boundary vs. `/birdseyereview` (state this so the two don't drift):**
- `/landscape` = cache-first veneer over **today's** suppressed pool — the exact candidate pool `/pulse` computed and folded this session. It does not recompute the priority landscape from scratch unless the cache is missing.
- `/birdseyereview` = a **full, zero-suppression audit across all Maps**, any day, independent of whether `/pulse` ran or folded anything today. Use it for periodic review, not to recover what today's `/pulse` hid.
- If both would show the same thing today, prefer `/landscape` — it's cheaper (cache read, not a fresh Map scan) and reflects exactly what was folded, including layer_hint/due/carry framing the proposer used.

### Sense

1. **Determine the reference date.** Default to today (`YYYY-MM-DD`). `$ARGUMENTS` may override with an explicit date to recall a past day's fold.

2. **Read the suppression cache**: `Daily/cache/YYYY-MM-DD-landscape.json` (the exact path `/pulse` writes at fold time — see its Suppression-cache write step). Schema `landscape-1.0`:
   ```json
   {
     "schema_version": "landscape-1.0",
     "reference_date": "YYYY-MM-DD",
     "computed_at": "<ISO-8601>",
     "suppressed_by": "post-gate",
     "candidate_pool": [ {"id": "...", "label": "...", "effort": "...", "layer_hint": "deadline|floor|core", "due": "...|null", "carry": null} ],
     "important_items": [ {"id": "...", "description": "...", "effort": "...", "score": 0.00, "due": "..."} ],
     "batches": [ /* optional, folded landscape context */ ]
   }
   ```

3. **Cache-miss handling** — the cache is absent when either:
   - **Pre-gate**: nothing has been suppressed yet (`/pulse` is still leading with the ranked pool directly — there's nothing to recall; say so plainly rather than presenting an empty landscape).
   - **No `/pulse` proposal ran today**: post-gate but the session hasn't opened `/pulse` yet for this reference date.

   In either case, **compute live** rather than error:
   ```bash
   python3 pulse-engine/scripts/pulse-calc.py --vault "${PULSE_VAULT:-./pulse-vault}" --date <reference-date> --candidates
   ```
   This emits `{"reference_date", "candidates", "warnings"}` read-only, no vault writes. Render `candidates` in place of `candidate_pool` below. If this live path is taken, say so explicitly ("no fold recorded for today — computed live") so the user isn't misled into thinking a graduation-era fold happened when it didn't.

### Route

4. **No re-filtering, no re-ranking.** The candidate pool (cached or live) is already the exact set `/pulse` drew from or would draw from — deadline items first, then floor, then top-ranked core (`CANDIDATE_POOL_RANKED`). Render it as-is; do not apply a new suppression pass on top of an already-suppressed-and-now-recalled list. That would be suppression squared.

5. **No residue field.** The candidate pool has no near-miss/residue concept (dropped from the port — pulse-cli-only). Do not fabricate a "just missed the cut" line; the pool is either in or not in.

### Surface

6. **Render, grouped by `layer_hint`** (mirrors the proposer's own layering so the recall reads as "what the draft saw," not a generic list):

```
## Landscape — [reference-date]
_[Recalled from today's fold | Computed live — no fold recorded for today]_

### Deadline / due
- [label] ([effort], due [date])

### Floor
- [label] ([effort])

### Core (ranked)
- [label] ([effort], score: X.XX)   ← from important_items when available, else candidate label only

[If batches present in cache: fold context — one line per gated batch, e.g. "Home batch folded (weight 0.31)."]
```

7. **If `candidate_pool`/`candidates` is empty**, say so plainly — an empty pool (sparse capturer day: no committed items, no floor template, no due items) is a real state, not an error. Do not pad with anything not in the source.

8. **Never write.** This skill reads the cache or runs `--candidates` (a read-only script mode) and renders. It does not touch the Daily Note, Session Log, Maps, or the landscape cache itself.

### Act

None. `/landscape` is pure Surface — no Act phase, no file writes, nothing to log.
