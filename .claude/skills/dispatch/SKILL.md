---
name: dispatch
description: Dispatch a task to a sub-agent in a tmux pane. Seeds effort context from the relevant Map so the agent starts with full awareness.
user-invocable: true
model: sonnet
effort: high
allowed-tools: Read, Glob, Bash
argument-hint: <pane> <effort-slug> "<task description>" [extra-dir...]
srsa: Act
---

## Dispatch Sub-Agent

Spin up an interactive Claude Code session in a tmux pane, pre-seeded with task context from the PULSE vault.

### Input

$ARGUMENTS — parsed as: `<pane> <effort-slug> "<task description>" [extra-dir...]`

- `pane`: tmux pane identifier (e.g., `agent-1`, `agent-2`, or a tmux pane target like `pulse-multi:work.1`)
- `effort-slug`: PULSE effort slug (e.g., `work`, `personal-project`, `health`)
- `task description`: what the agent should do (quoted string)
- `extra-dir` (optional): additional directories the agent needs access to (e.g., `~/code/my-project`)

### Environment Isolation

Each agent runs in its own **git worktree** of the target codebase — fully isolated from the main repo and from other agents.

- **Main session** (`$PULSE_VAULT`): sole writer to Maps, Notes, Daily
- **Sub-agents** (worktree): own branch (`pulse/<agent-name>`), own working tree, write-only to `Inbox/multi-agents/`
- **No vault collision**: sub-agents never `cd` into the vault. All vault context is pre-seeded via `--append-system-prompt-file`.
- **No repo collision**: each agent gets a worktree at `/tmp/pulse-worktree-<agent-name>` on branch `pulse/<agent-name>`. Changes stay isolated until the main session reviews and merges.
- **Agent permissions**: each worktree gets `pulse-engine/scripts/agent-settings.local.json` copied to `.claude/settings.local.json` — pre-approved for exploration, git, npm, and result writing.

### Codebase Registry

Load the registry from `pulse-vault/user.config.yaml` under the `codebase_registry:` key:

```yaml
codebase_registry:
  - name: <effort-slug-or-project-name>
    path: /absolute/path/to/project
```

See `pulse-engine/user.config.example.yaml` for the format. Add entries as your efforts grow.

If an effort slug has no registered codebase and no `extra-dir` is provided, ask the user for the path before dispatching.

### Sense — Resolve Context

1. **Parse arguments** — extract pane, effort slug, task description, and any extra directories.

2. **Load effort context** — read the Map file for the effort slug. Extract:
   - Purpose (from `## Purpose` section)
   - Active Threads (titles + one-line summaries)
   - Unchecked Minor Actions
   - Related codebases (from `## Related Maps` or known aliases)

   If the effort slug doesn't match a Map, warn and proceed with the task description alone.

3. **Resolve pane target** — if the pane argument is a short name like `agent-1`, resolve it to tmux target `pulse-multi:work.1` (agent-1 → .1, agent-2 → .2, agent-3 → .3). If it already looks like a tmux target (contains `:` or `.`), use it directly.

4. **Resolve source repo** — look up the effort slug in the Codebase Registry from `pulse-vault/user.config.yaml`. Override with `extra-dir` if provided. If unknown, ask the user.

### Act — Build and Launch

5. **Build the agent name** — `<effort-slug>-<task-slug>` where task-slug is a 2-3 word kebab-case derived from the task description.

6. **Create git worktree** — isolate the agent's work from the main repo and other agents:

   ```bash
   git -C <source-repo> worktree add /tmp/pulse-worktree-<agent-name> -b pulse/<agent-name>
   ```

   Then copy agent permissions into the worktree:
   ```bash
   mkdir -p /tmp/pulse-worktree-<agent-name>/.claude
   cp pulse-engine/scripts/agent-settings.local.json /tmp/pulse-worktree-<agent-name>/.claude/settings.local.json
   ```

   The agent's working directory is now `/tmp/pulse-worktree-<agent-name>` — a clean branch off the current HEAD.

7. **Write system prompt to file** — write the prompt content to a temp file at `/tmp/pulse-dispatch-<agent-name>.md`. This avoids quote-escaping issues when passing through `tmux send-keys`. The file content:

   ```markdown
   You are a PULSE sub-agent working on the [effort name] effort.

   ## Your Task
   [task description]

   ## Effort Context: [effort name]
   Purpose: [from Map]

   Active Threads:
   [thread summaries from Map]

   Open Minor Actions:
   [unchecked items from Map]

   ## Result Protocol
   When your task is complete (or you hit a blocker), write a single file to:
   ${PULSE_VAULT}/Inbox/multi-agents/YYYY-MM-DD-HH-MM-[task-slug].md

   Use this format:
   ---
   type: task-result
   status: complete | blocked | partial
   effort: [slug]
   agent_name: [your --name value]
   task: [one-line description]
   started: YYYY-MM-DDTHH:MM
   completed: YYYY-MM-DDTHH:MM
   ---

   ## Result
   [What you accomplished — files changed, commands run, test results]

   ## Files Changed
   - path/to/file — [what and why]

   ## Open Items
   - [Anything unfinished or needing human decision]

   ## Vault Updates Needed
   [Optional: suggest Map/Note changes for main session to apply]

   ## Rules
   - Work in your codebase. Do NOT write to the vault except Inbox/multi-agents/.
   - Do NOT run /pulse, /triage, /capture, /defrag, /close, or any PULSE skills.
   - Print "TASK COMPLETE: [task-slug]" when finished.
   - Be autonomous. Log edge cases in Open Items rather than blocking.
   ```

8. **Dispatch via tmux** — send the launch command to the target pane:

   ```bash
   tmux send-keys -t "<pane-target>" "cd /tmp/pulse-worktree-<agent-name> && claude --model opus --name <agent-name> --add-dir \"${PULSE_VAULT:-./pulse-vault}/Inbox/multi-agents\" --append-system-prompt-file /tmp/pulse-dispatch-<agent-name>.md" Enter
   ```

   Using `--append-system-prompt-file` avoids quote/newline escaping through tmux. The `--add-dir` for `Inbox/multi-agents` gives write access for results only. The working directory is the worktree, not the source repo. The `--model opus` flag ensures dispatched agents run at full reasoning capacity.

### Surface — Confirm

9. **Confirm** — report to the user:
   ```
   Dispatched to [pane]: [agent-name]
   Worktree: /tmp/pulse-worktree-<agent-name> (branch: pulse/<agent-name>)
   Source: [source repo]
   Task: [task description]
   Effort: [effort name] — [N] threads, [N] open items seeded as context
   ```

### Act — Log

10. **Log dispatch** — append to `Daily/logs/YYYY-MM-DD-log.md`:
   ```
   ### Dispatch — HH:MM
   - Agent: [agent-name] → [pane-target]
   - Effort: [slug]
   - Worktree: /tmp/pulse-worktree-<agent-name> (branch: pulse/<agent-name>)
   - Source: [source repo]
   - Task: [task description]
   - Context seeded: [N] threads, [N] minor actions
   ```

### Examples

```
/dispatch agent-1 work "Automate test coverage report generation"
/dispatch agent-2 personal-project "Verify deployment pipeline and staging display"
/dispatch agent-1 pulse "Prototype new capture pipeline" ~/code/side-project
```

### Principles
- **Context is the value** — the Map read is what makes this better than manually typing a claude command. The sub-agent starts knowing what the effort is about, what's active, and what's open.
- **Interactive by default** — no `-p` flag. The user can watch and intervene. Add `-p` manually to the tmux command if headless is desired.
- **One pane, one task** — don't dispatch multiple tasks to the same pane.
