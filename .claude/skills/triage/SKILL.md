---
name: triage
description: Process untriaged Inbox items — assign domains, create Notes, update Maps. Use to clear the Inbox or process specific captures.
user-invocable: true
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

## Inbox Triage

Process untriaged items from `Inbox/` into the PULSE system.

### Steps

1. **Find untriaged items** — scan `Inbox/` for files where `triaged: false` in frontmatter.

2. **If no untriaged items**, report "Inbox clear" and stop.

3. **For each untriaged item**, present it to the user:

```
### [Capture title]
Captured: [date]
Content: [brief summary]

Suggested domains: [domain-slug, domain-slug]
Suggested status: [active/someday/waiting]
Suggested context_group: [batch-name]
Action: [Create new Note / Append to existing "[Note name]" / Discard]
```

Suggest domains by matching content against existing Maps in `Maps/` — read Map titles, domain slugs, and purpose descriptions to find the best fit.

4. **Wait for the user's confirmation or adjustment** on each item before proceeding.

5. **On confirmation**, execute the triage:

   a. **If creating a new Note**:
      - Create file in `Notes/` with proper frontmatter (type, domains, status, dates, effort_estimate, context_group, tags)
      - Filename: `Notes/[descriptive-slug].md`

   b. **If appending to existing Note**:
      - Read the target note
      - Append the captured content under the appropriate section
      - Update the note's `updated` date in frontmatter

   c. **Update relevant Maps**:
      - For each domain in the note's `domains[]`, read the corresponding Map
      - Add the note link under the appropriate Active Thread or Sub-theme section
      - Increment `open_loops` count in the Map's frontmatter
      - Update `last_active` to today

   d. **Mark capture as triaged**:
      - Update the Inbox file's frontmatter: set `triaged: true` and fill in `domains[]`

6. **Report summary** when done: N items triaged, notes created/updated, maps updated.

### Principles
- Always confirm before creating or modifying files
- Suggest but don't assume — the user decides the final domain assignment
- If a capture could go multiple ways, present the options clearly
- Cross-domain notes are encouraged — don't force single-domain assignment
- $ARGUMENTS can optionally specify a specific Inbox file to triage
