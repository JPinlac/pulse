---
name: triage
description: Auto-process Inbox items into Notes and Maps — no confirmation, just execute and report. Use to clear the Inbox immediately.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Auto-Triage

Process untriaged items from `Inbox/` into the PULSE system. Executes immediately without confirmation — the agent classifies, files, and reports what it did.

### Steps

1. **Find untriaged items** — scan `Inbox/` for files where `triaged: false` in frontmatter.

2. **If no untriaged items**, report "Inbox clear" and stop.

3. **For each untriaged item**, execute the triage autonomously:

   a. **Read the capture content** and match against existing Maps — read Map titles, domain slugs, and purpose descriptions to find the best domain fit.

   b. **Determine classification**:
      - `domains[]` — best-fit domain(s) from Maps
      - `status` — default `active` unless content suggests `someday` or `waiting`
      - `context_group` — from the matched Map's `context_batch`
      - `effort_estimate` — infer from content scope (`small`, `medium`, `large`)

   c. **If creating a new Note**:
      - Create file in `Notes/` with proper frontmatter (type, domains, status, dates, effort_estimate, context_group, tags)
      - Filename: `Notes/[descriptive-slug].md`

   d. **If appending to existing Note** (content clearly extends an existing active note in the same domain):
      - Read the target note
      - Append the captured content under the appropriate section
      - Update the note's `updated` date in frontmatter

   e. **Update relevant Maps**:
      - For each domain in the note's `domains[]`, read the corresponding Map
      - Add the note link under the appropriate Active Thread or Sub-theme section
      - Increment `open_loops` count in the Map's frontmatter
      - Update `last_active` to today

   f. **Mark capture as triaged**:
      - Update the Inbox file's frontmatter: set `triaged: true` and fill in `domains[]`

4. **Log results to today's Daily note** (`Daily/YYYY-MM-DD.md`) — append a triage log entry under a `## Triage Log` section. If no Daily note exists, create one. Do not report results back to the user in conversation — the log is the record.

```
## Triage Log
- [title] → [domain-slug] (new note)
- [title] → [domain-slug] (appended to "[existing note]")
- [title] → [domain-a, domain-b] (new note, cross-domain)
```

### Principles
- Execute and log — no confirmation cycles, no conversational reports
- The cost of a misclassified note is low (defrag catches it later); the cost of context injection is real
- Cross-domain notes are encouraged — don't force single-domain assignment
- If content could go multiple ways, pick the best fit and note the alternative in the log
- $ARGUMENTS can optionally specify a specific Inbox file to triage
