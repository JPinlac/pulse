---
name: capture
description: Quick capture a thought, idea, or task into the Inbox. Zero friction — just say what's on your mind after /capture and it gets filed.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob
argument-hint: <your thought or idea>
---

## Quick Capture

Capture whatever the user says into the Inbox with zero friction.

### Input
The content to capture is: $ARGUMENTS

### Steps

1. **Create a capture file** in `Inbox/` with a slugified filename based on the content:
   - Format: `Inbox/YYYY-MM-DD-[short-slug].md`
   - Example: `Inbox/2026-03-11-deploy-pipeline-idea.md`

2. **Write the file** with this structure:

```markdown
---
type: capture
source: agent
captured: YYYY-MM-DDTHH:MM:SS
triaged: false
domains: []
---
# [Brief title derived from content]

[The captured content, cleaned up slightly for readability but preserving intent]
```

3. **Confirm capture** — report what was captured: "Captured: [title]. It's in the Inbox — auto-triage will pick it up at next `/pulse` or `/triage`."

### Principles
- Speed over perfection — get it captured first, auto-triage files it later
- Don't over-interpret. Capture what was said, don't force-fit into domains yet.
- If the content clearly maps to an existing active thread in a Map, mention that connection
- Multiple captures in one message are fine — create one file per distinct thought
