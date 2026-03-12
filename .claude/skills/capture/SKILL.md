---
name: capture
description: Quick capture a thought, idea, or task into the Inbox. Zero friction — just say what's on your mind after /capture and it gets filed.
user-invocable: true
allowed-tools: Agent
argument-hint: <your thought or idea>
---

## Quick Capture

Capture whatever the user says into the Inbox with zero friction.

**IMPORTANT**: This skill MUST run as a background sub-agent to preserve main conversation context. Do NOT process the capture inline.

### Input
The content to capture is: $ARGUMENTS

### Steps

1. **Delegate immediately** — launch a background Agent (subagent_type: "general-purpose", run_in_background: true) with this prompt:

> Create a capture file in `Inbox/` with these specs:
> - Filename: `Inbox/YYYY-MM-DD-[short-slug].md` (use today's date)
> - Content:
> ```markdown
> ---
> type: capture
> source: agent
> captured: YYYY-MM-DDTHH:MM:SS
> triaged: false
> efforts: []
> ---
> # [Brief title derived from content]
>
> [The captured content, cleaned up slightly for readability but preserving intent]
> ```
> - Content to capture: [paste the $ARGUMENTS here]
> - Speed over perfection — capture what was said, don't over-interpret or force-fit into efforts.
> - If multiple distinct thoughts, create one file per thought.

2. **Confirm immediately** — don't wait for the agent to finish. Report: "Captured: [title]. Filing in background — auto-triage will pick it up at next `/pulse` or `/triage`."

### Principles
- **Zero context disruption** — the main conversation must not lose flow
- Speed over perfection — get it captured first, auto-triage files it later
- Don't over-interpret. Capture what was said, don't force-fit into efforts yet.
- Multiple captures in one message are fine — one agent call handles all of them
