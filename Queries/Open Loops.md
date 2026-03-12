---
type: query
description: All active or waiting items sorted by staleness
---
# Open Loops

```dataview
TABLE domains, status, updated, effort_estimate
FROM "Notes"
WHERE status = "active" OR status = "waiting"
SORT updated ASC
```
