---
type: query
description: All active notes grouped by effort
---
# Active by Effort

```dataview
TABLE length(rows) as "Count", map(rows, (r) => r.file.link) as "Notes"
FROM "Notes"
WHERE status = "active"
GROUP BY domains
```
