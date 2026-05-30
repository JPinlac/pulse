---
name: migrate-graph
description: Interactive migration of vault items into the Neo4j graph — one effort or item at a time, dyad-enriched for full fidelity. Use when migrating vault content to the graph database.
user-invocable: true
model: opus
effort: max
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
argument-hint: <effort slug | item slug | "status">
srsa: Surface+Act (Dyad)
---

## Migrate — Dyad Graph Enrichment

Walk through vault items in conversation to migrate them into the graph with full semantic, temporal, narrative, and relational fidelity. This is Phase 2 of the migration plan in [[pulse-graph-migration]]. Node/edge schemas and transition metadata formats are defined in `pulse-cli/DESIGN.md`.

This skill is Dyad Surface + Act: the agent proposes nodes and edges, the user validates and enriches, then the agent writes to the graph. The pause between proposal and write is load-bearing — it's where fidelity comes from.

### Modes

**`/migrate <effort>`** — Migrate an entire effort: its nodes, items, edges, and cross-effort connections.
**`/migrate <item-slug>`** — Migrate or enrich a single item.
**`/migrate status`** — Show migration progress: which efforts are done, in progress, or untouched.

### Per-Effort Flow

#### Sense — Load Structural Skeleton

Read the Map file for the effort. Read all linked Notes (frontmatter + content). Read relevant Daily Notes and Session Logs for temporal context. Read `Done/DONE.md` for completed items in this effort.

Present to the user:
```
## Migrating: [Effort Name]

### Nodes to create
- Effort node: [slug] (weight, batch, purpose)
- Active items: [count] ([list with slugs])
- Done items: [count from DONE.md]
- Minor Actions: [count]

### Structural edges detected
- depends_on: [list]
- related: [list]

### Ready to begin. Start with the effort node?
```

#### Dyad Surface — Walk Each Node

**2. Effort Node**: Create the effort node via `pulse-cli add` or direct graph write. Capture all Map frontmatter properties, purpose, context batch, aliases, current priority weight. Confirm with user before writing.

**3. Walk Each Item**: For each item (Active Threads first, then Minor Actions, then Done items from DONE.md):

**a. Read the source.** Read the Note content (not just frontmatter). If it's a Minor Action with no Note, read the Map entry.

**b. Propose the node.** Present:
```
### [Item slug]
Status: [active/waiting/done]
Effort: [effort]
Importance: [high/medium/low]
Type: [note/item]

**Structural properties** (from frontmatter):
[list what was parsed]

**Proposed edges:**
- depends_on → [slug] — [reason]
- informs → [slug] — [reason]
- [any cross-effort edges detected from content]

**Temporal history** (from Daily Notes/Session Logs):
- [date]: created
- [date]: [status change] — [context]
- [date]: [completed/deferred/etc] — [context]

**Narrative metadata** (for done/transformed items):
- trajectory: [proposed]
- completion_type: [proposed]
- outflows: [proposed]

**Questions for you:**
- [anything the LLM can't infer — missing context, ambiguous edges, trajectory clarification]
```

**c. User validates.** The user confirms, corrects, or enriches. Common interactions:
- "That edge is wrong, it's actually [X]"
- "Add a connection to [Y], they're related because [Z]"
- "The trajectory was actually [narrative]"
- "Skip this one, it's trivial"

#### Act — Write to Graph

**d. Write to graph.** After user confirmation, run through normal transition commands — cascade activation during migration builds the graph's history organically:
```bash
# Create the node
pulse-cli add <effort> "<description>" --importance <level> --depends-on <slug>
# Then transition to current state (triggers cascade, builds activation counts)
pulse-cli complete <slug> --metadata '<json>'
```

If CLI commands aren't implemented yet, log the enriched data to a staging file (`Done/migration-staging/<effort>.json`) for later import. See pulse-cli/DESIGN.md for metadata schemas per transition type.

#### Sense + Dyad Surface — Cross-Effort Connections

After all items in the effort are migrated, scan for cross-effort connections:
- Notes with `efforts: [multiple]` — create edges between effort nodes
- Content that references items in other efforts — propose `informs` or `strongly_related` edges
- Patterns from Sati emergence log — propose `speculative` edges

Present all proposed cross-effort edges for validation.

#### Surface — Validate

```
## Migration Complete: [Effort Name]

Nodes created: [count]
Edges created: [count]
Cross-effort connections: [count]

Items skipped: [list if any]
Open questions: [list if any]

### Effort marked as migrated.
```

Update migration tracking (in `Done/migration-progress.md` or effort Map frontmatter).

### Per-Item Flow (`/migrate <item-slug>`)

Same as step 3 above but for a single item. Useful for:
- Enriching an item that was already structurally imported
- Migrating a new item created after the bulk effort migration
- Re-enriching an item after significant context emerged

### Migration Status (`/migrate status`)

Read migration tracking and report:
```
## Migration Progress

| Effort | Status | Nodes | Edges | Last Migrated |
|--------|--------|-------|-------|---------------|
| [slug] | done   | 12    | 8     | 2026-03-29    |
| [slug] | partial| 3/7   | 2     | 2026-03-29    |
| [slug] | —      | —     | —     | —             |
```

### Staging Mode (Pre-Neo4j)

If Neo4j isn't running yet, write enriched data to `Done/migration-staging/` as JSON files — one per effort. Each file contains the full node/edge data that will be imported once the graph is live. This lets the dyad do the enrichment work now without waiting for infrastructure.

Staging file format (aligned to `graph.py` `create_node`/`create_edge` signatures):
```json
{
  "effort": "slug",
  "migrated": "2026-03-29",
  "nodes": [
    {
      "slug": "item-slug",
      "type": "note",
      "effort": "effort-slug",
      "status": "active",
      "metadata": {},
      "strongly_related": [],
      "speculative": []
    }
  ],
  "edges": [
    {
      "source": "slug-a",
      "target": "slug-b",
      "type": "depends_on",
      "weight": 0.9,
      "context": "why this edge exists",
      "metadata": {}
    }
  ]
}
```

### Principles

- **Fidelity over speed.** A lossy migration is worse than no migration. Take the time to get edges and metadata right.
- **User is the authority.** The LLM proposes, the user validates. Don't write to the graph without confirmation.
- **One effort at a time.** Don't try to batch. The conversation focus enables depth.
- **Skip trivia.** Minor actions like "Dishes" don't need narrative metadata. Ask "skip?" for obvious trivia.
- **Record process learnings.** After the first 2-3 efforts, note what worked and what to change. The skill itself evolves.
- **Done log is an input.** `Done/DONE.md` provides the chronological completion data and priority weights. Use it as a source for temporal and narrative reconstruction.
