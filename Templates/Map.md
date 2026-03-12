---
type: map
domain: {{domain-slug}}
context_batch: {{context-batch}}
priority_weight: 0.5
base_priority: 5
last_active: {{date}}
open_loops: 0
related_domains: []
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
WHERE contains(domains, this.domain)
SORT updated DESC
```
