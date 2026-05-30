---
type: query
description: Notes with dependencies and their resolution status
---
# Dependency Graph

## Notes with Dependencies

```dataview
TABLE depends, status, efforts
FROM "Notes"
WHERE depends AND length(depends) > 0
SORT efforts ASC
```

## Reverse Dependencies (What Depends on Each Note)

```dataview
TABLE file.link as "Depended On By"
FROM "Notes"
WHERE contains(depends, this.file.name)
```
