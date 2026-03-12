---
type: query
description: Notes that span multiple efforts
---
# Cross Effort

```dataview
TABLE efforts, status, updated
FROM "Notes"
WHERE length(efforts) > 1
SORT updated DESC
```
