---
type: query
description: Active items past their default staleness window (14 days). Agent-driven defrag uses timescale-aware thresholds for precise detection.
---
# Stale Items

```dataview
TABLE efforts, status, updated, timescale
FROM "Notes"
WHERE status = "active" AND updated < date(today) - dur(14 days)
SORT updated ASC
```
