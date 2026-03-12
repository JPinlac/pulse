---
type: query
description: Active items not touched in 14+ days
---
# Stale Items

```dataview
TABLE domains, status, updated
FROM "Notes"
WHERE status = "active" AND updated < date(today) - dur(14 days)
SORT updated ASC
```
