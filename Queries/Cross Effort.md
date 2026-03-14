---
type: query
description: Notes that span multiple efforts
---
# Cross Effort

```dataview
TABLE domains, status, updated
FROM "Notes"
WHERE length(domains) > 1
SORT updated DESC
```
