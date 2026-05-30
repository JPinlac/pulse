---
name: capture
description: Quick capture a thought, idea, or task into the Inbox. Zero friction — just say what's on your mind after /capture and it gets filed.
user-invocable: true
model: sonnet
effort: medium
allowed-tools: Agent
argument-hint: "[q] <your thought or idea>"
srsa: Act
---

## Quick Capture

Capture whatever the user says into the Inbox with zero friction.

**IMPORTANT**: This skill MUST run as a background sub-agent to preserve main conversation context. Do NOT process the capture inline.

### Modes

- **Default (context-aware)**: Extracts conversational context — active efforts, recent topics, likely dependencies, related note slugs — and embeds it in the capture file. This context would otherwise be lost on context clear, making triage blind.
- **Quick (`q` flag)**: `$ARGUMENTS` starts with `q` — strips the `q` prefix and captures raw, no conversational context. Use for thoughts unrelated to the current conversation.

### Input
The content to capture is: $ARGUMENTS

### Sense

**Step 0 — Mode detection**: If `$ARGUMENTS` starts with `q ` (the letter q followed by a space), set mode to `quick` and strip the `q ` prefix from the content. Otherwise, mode is `context-aware`.

**Step 1 — Context extraction** (context-aware mode only, skip for quick mode):
Before delegating, extract from the current conversation:
- **Active efforts**: which effort slugs have been discussed or worked on in this conversation
- **Recent topics**: key themes, decisions, or threads from the last few exchanges
- **Likely dependencies**: if the capture references work that depends on something discussed, identify the note slug(s)
- **Related notes**: any `[[note-slug]]` references mentioned in recent conversation
- **Conversation trigger**: what specifically prompted this capture — the exchange, correction, tangent, or connection that produced the thought. This is the most perishable signal; without it, triage sees an idea but not why it surfaced now.

Package this as a `## Conversational Context` block to include in the capture file. This section is the agent's primary value-add during capture — the content itself is verbatim, so the context is what makes a future triage pass (running without this conversation) able to route and prioritize correctly.

### Act

**Step 2 — Delegate immediately** — launch a background Agent (subagent_type: "general-purpose", model: "opus", run_in_background: true) with this prompt:

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
> context_deps: [note-slug-1, note-slug-2]  # only if dependencies were inferred (context-aware mode)
> ---
> # [Brief title derived from content]
>
> [The captured content — VERBATIM. Use the user's exact words. Minimal formatting cleanup only (line breaks, markdown). Do NOT expand, interpret, reframe, or add claims the user didn't make.]
>
> ## Conversational Context
> <!-- Agent-generated from conversation state at capture time. This is the agent's primary value-add during capture — triage runs later (during /pulse or /close) without access to this conversation, so this section is the only bridge between the moment of capture and the moment of filing. Preserve what triage will need to route correctly. -->
> - **Active efforts**: [effort slugs discussed or worked on in this conversation]
> - **Recent topics**: [1-2 sentence summary of what was being discussed when this thought emerged — what prompted it]
> - **Likely dependencies**: [[note-slug]] — [why this seems related or upstream]
> - **Related notes**: [[note-slug]], [[note-slug]]
> - **Conversation trigger**: [what specifically in the conversation prompted this capture — a correction, a tangent, a shower-thought, a connection noticed mid-discussion]
> ```
> - Content to capture: [paste the processed $ARGUMENTS here]
> - Conversational context to include: [paste the extracted context from Step 1, or "none — quick capture mode" if quick mode]
> - **VERBATIM RULE**: Use the user's exact words. Do not expand, interpret, add implied contrasts, reframe, or structure the idea into an argument. The user's raw signal is the artifact — the agent's value-add is the Conversational Context section, not content expansion.
> - Speed over perfection — capture what was said, don't over-interpret or force-fit into efforts.
> - If multiple distinct thoughts, create one file per thought.
> - If quick mode: omit the `## Conversational Context` section and `context_deps` field entirely.

### Surface

**Step 3 — Confirm immediately** — don't wait for the agent to finish. Report: "Captured: [title]. Filing in background — auto-triage will pick it up at next `/pulse` or `/triage`."

### Principles
- **Verbatim capture** — the user's words are the artifact. Do not expand, interpret, or reframe. The agent's value-add is the Conversational Context section, not content modification. Triage runs later without conversation access — context preserves what triage needs; verbatim preserves what the user said.
- **Zero context disruption** — the main conversation must not lose flow
- **Context-aware by default** — conversational context is perishable; capture it now so triage has full signal later
- Speed over perfection — get it captured first, auto-triage files it later
- Don't over-interpret. Capture what was said, don't force-fit into efforts yet. Context is informational, not prescriptive.
- Multiple captures in one message are fine — one agent call handles all of them
- The `q` flag exists for random thoughts that have nothing to do with what you're working on — don't bloat them with irrelevant context
