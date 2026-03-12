---
type: query
description: All active or waiting items sorted by staleness
---
# Open Loops

```dataview
TABLE efforts, status, updated, effort_estimate, effort_actual
FROM "Notes"
WHERE status = "active" OR status = "waiting"
SORT updated ASC
```
