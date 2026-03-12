---
type: query
description: Notes that span multiple domains
---
# Cross Domain

```dataview
TABLE domains, status, updated
FROM "Notes"
WHERE length(domains) > 1
SORT updated DESC
```
