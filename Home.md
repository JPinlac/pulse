---
type: home
updated: 2026-03-11
---
# PULSE — Home

## Current Focus
<!-- Agent-maintained: top 3-5 items across all efforts, optimized for minimal context switching -->
*No items yet. Agent will populate this section based on Map open loops and priority weights.*

## Effort Overview
```dataview
TABLE priority_weight, open_loops, last_active
FROM "Maps"
SORT priority_weight DESC
```

## Recent Activity
```dataview
TABLE domains, status, updated
FROM "Notes"
SORT updated DESC
LIMIT 5
```

## Cross-Effort Tensions
<!-- Agent surfaces where efforts compete for time -->
*No tensions identified yet.*
