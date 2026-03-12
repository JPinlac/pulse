---
type: map
effort: {{effort-slug}}
context_batch: {{context-batch}}
priority_weight: 0.5
base_priority: 5
last_active: {{date}}
open_loops: 0
related_efforts: []
tags: []
---
# {{title}}

## Purpose
<!-- Why this effort matters -->

## Active Threads
<!-- Current open loops -->

## Sub-themes
<!-- Organized sections -->

## Related Maps
<!-- Cross-effort links -->

## Notes
```dataview
LIST
FROM "Notes"
WHERE contains(efforts, this.effort)
SORT updated DESC
```
