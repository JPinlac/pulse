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

3. **Suggest triage** — based on the content, suggest:
   - Which `domains[]` it likely belongs to (match against existing Maps in `Maps/`)
   - Whether it should become a new Note or append to an existing one
   - A suggested `status` and `context_group`

4. **Ask if the user wants to triage now** or leave it in the Inbox for later.

### Principles
- Speed over perfection — get it captured first
- Don't over-interpret. Capture what was said, suggest domains, but don't force-fit.
- If the content clearly maps to an existing active thread in a Map, mention that connection
- Multiple captures in one message are fine — create one file per distinct thought
