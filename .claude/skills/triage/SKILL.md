---
name: triage
description: Auto-process Inbox items into Notes and Maps — no confirmation needed. Assigns domains, creates Notes, updates Maps, reports what was done.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Auto-Triage

Process untriaged items from `Inbox/` into the PULSE system. Execute immediately, report what was done.

### Steps

1. **Find untriaged items** — scan `Inbox/` for files where `triaged: false` in frontmatter.

2. **If no untriaged items**, report "Inbox clear" and stop.

3. **For each untriaged item**, analyze the content and execute:

   a. **Match against Maps** — read the content and compare against Map purposes and active threads to determine the best `domains[]` assignment, `status`, and `context_group`.

   b. **Create or append**:
      - If the content is a new thread: create a Note in `Notes/` with proper frontmatter (type, domains, status, dates, effort_estimate, context_group, tags). Filename: `Notes/[descriptive-slug].md`
      - If the content clearly extends an existing Note: read the target note, append content, update `updated` date.

   c. **Update relevant Maps (compressed pointer)**:
      - For each domain in the note's `domains[]`, read the corresponding Map
      - Add a compressed pointer under the appropriate section:
        `- [[note-slug]] — [≤15-word summary] (subtype, date)`
      - Do NOT inline note content or extended summaries into the Map
      - Increment `open_loops` count in the Map's frontmatter
      - Update `last_active` to today

   d. **Mark capture as triaged**:
      - Update the Inbox file's frontmatter: set `triaged: true` and fill in `domains[]`

4. **Report summary**:

```
Auto-triaged N items:
- [title] → [domain(s)] (new note / appended to "[existing note]")
- [title] → [domain(s)] (new note / appended to "[existing note]")
...
```

### Principles
- **No confirmation cycles.** Execute immediately. The cost of a misclassified note is low — `/defrag` catches mistakes later.
- Cross-domain notes are encouraged — don't force single-domain assignment
- If a capture could go multiple ways, pick the best match. Defrag will flag misclassifications.
- $ARGUMENTS can optionally specify a specific Inbox file to triage
