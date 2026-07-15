---
type: note
subtype: reference
efforts: [pulse]
status: active
importance: medium
created: 2026-05-29
updated: 2026-07-02
informs: [[pulse-mao-multi-agent-orchestration]], [[pulse-execution-modes]]
tags: [meta, harness, claude-code, permissions, sub-agents]
---
# Background Sub-Agent Write Permissions — Investigation & Resolution

Verification report for a "sub-agents denied Write/Edit" issue that temporarily gated PULSE's Silent File Operations convention. Resolved as of Claude Code v2.1.186. This doc is the canonical writeup; `harness-model-changes.md` carries the one-line watch entry, and the MAO doc carries the corrected architecture.

## TL;DR

- **Symptom (pre-v2.1.186)**: background sub-agents (Agent tool, `run_in_background: true`) silently failed every vault write — captures didn't file, session logs didn't append, Map updates were lost.
- **Disproven**: the `worktree.bgIsolation` hypothesis. A background agent runs on the **main checkout**, not an isolated worktree — `bgIsolation: none` works, but was never the blocker.
- **Confirmed root cause (pre-fix)**: the local `allow` rules were **not honored in the detached background permission context**. A background agent had no interactive surface to approve a prompt, and the allow-list wasn't applied there, so any non-auto-allowed tool (Write/Edit) auto-denied.
- **RESOLVED AT THE HARNESS LEVEL (Claude Code v2.1.186+)** — see "Re-verification" below. This was a version-specific harness limitation, not a permanent architectural constraint. Background sub-agents can write again; the inline/foreground-only convention is lifted.
- **Open thread, now lower-priority**: a CLI-bypass write-insulation idea (routing vault mutations through a Bash-invoked CLI instead of the harness's Write/Edit tools) still has independent merit (determinism, atomic frontmatter validation, decoupling from harness behavior) but is no longer *urgent* — the specific blocker it was designed to route around no longer exists.

## Symptom

The Silent File Operations convention mandated that *background* sub-agents be the primary writers of all vault files (Daily Notes, Session Logs, Map updates, captures), for "zero context disruption." On harness versions before v2.1.186, delegated background writes were denied — a delegated write sub-agent would come back "fully WRITE-BLOCKED (read OK, Edit/Write/Bash denied)" despite running on the main checkout with the correct allow rules present. The initial working hypothesis was `worktree.bgIsolation`.

## Verification

Surface = agent behavior, so the test was to spawn real agents and observe Write/Edit outcomes on disk. Three probes (the third is the control that pins the cause):

| Probe | Agent | Path | Result |
|-------|-------|------|--------|
| 1 | **Background** (`run_in_background: true`) | dotfile at vault root | **Write DENIED** — `Permission to use Write has been denied`. But `pwd` + `git rev-parse --show-toplevel` confirmed **the main checkout, not a worktree.** |
| 2 | **Background** | non-dotfile in the vault **and** repo-root file (both matching a `Write(<vault>/**)` allow rule) | **both Write DENIED.** Dotfile-glob confound ruled out. `Bash` worked → only Write/Edit gated. |
| 3 | **Foreground** (synchronous) | non-dotfile (identical shape + rules as probe 2) | **Write SUCCESS.** |

Post-fix re-verification (implementation phase): a foreground sub-agent wrote a multi-file batch — all succeeded; an inline write from the main session succeeded; every inline edit landed.

## Root cause

The decisive contrast is probe 2 vs. probe 3: **identical path, identical allow rules**, opposite outcomes. The only difference is foreground vs. background. Therefore:

- It is **not** the worktree (probe 1: the background agent is on the main checkout).
- It is **not** a missing allow rule (rules are present; foreground honors them).
- It is **not** a dotfile-glob quirk (probe 2: non-dotfiles fail too).
- It **is** that the local `allow` rules were not applied in the **detached background permission context**. A background agent has no interactive surface to approve a prompt, and (pre-fix) the allow-list that should auto-allow the write wasn't honored there — so the tool auto-denied. A foreground sub-agent runs inside the live session's execution/permission context, where the same rules *are* applied.

**Caveat (honest scope)**: the *behavior* was verified by runtime observation. The *internal mechanism* was the inferred explanation at the time, not confirmed from Claude Code internals — see "Re-verification" below for the point where Claude Code's own docs confirmed it directly.

## Resolution (interim, pre-fix)

While the bug was present, the convention flipped to a safer fallback:

- **Inline by default** — the main session writes light/single-file ops directly (session-log appends, frontmatter bumps, single Map edits, calibration corrections, captures).
- **Foreground sub-agents** — reserved for genuinely heavy multi-file batches (full `/defrag` pass, `/pulse` Phase E Map+INDEX rewrite), where context isolation pays for the spawn cost.
- **Background sub-agents were read-only** — valid for read/analysis fan-out (e.g. Sati observation); their findings written back inline by the main session.

The cost paid at the time: the original async / non-blocking "filing in background" design intent was retired. "Silent" meant the *output* was clean (the conversation showed only human-readable summaries), not that the write was offloaded to a concurrent agent.

## Re-verification — Claude Code v2.1.186+ (RESOLVED)

Claude Code's public docs (`sub-agents` page, "Run subagents in foreground or background") now state:

> "Background subagents run concurrently while you continue working. As of v2.1.186, when a background subagent reaches a tool call that needs permission, the prompt surfaces in your main session and names the subagent that is asking. Approve to let the subagent continue, or press Esc to deny that one tool call without stopping the subagent. **Before v2.1.186, background subagents auto-denied any tool call that would have prompted.**"

That last sentence is a direct, named confirmation of the mechanism this doc's "Root cause" section inferred but couldn't confirm from internals — the harness itself has since changed it.

**Re-ran the original probe shape** (dotfile write on the main checkout, `run_in_background: true`, explicit):

| Probe | Agent | Path | Result |
|-------|-------|------|--------|
| 1′ | Background | `pwd` / `git rev-parse --show-toplevel` | confirmed still on main checkout, not a worktree |
| 2′ | Background | dotfile write | **SUCCESS** (was DENIED pre-fix) |
| 3′ | Background | same file, Edit | **SUCCESS** |
| 4′ | Background | `Bash echo` | SUCCESS (control, unaffected either way — matches original) |

No permission-approval prompt surfaced during the probe — the write went through silently, consistent with the session running under an auto-approving permission mode (e.g. `auto`'s background classifier, per the same docs page) rather than the interactive per-call approval described for other modes. Either way, the net effect for PULSE is what matters: **background sub-agent writes now succeed.**

Also corroborated by a real (non-probe) use in the same investigation: a full `/defrag` pass dispatched via the Agent tool without `run_in_background` set explicitly came back framed by the tool as "Async... working in the background," yet successfully edited multiple Map files, rewrote `Maps/INDEX.md`, and appended to the Session Log — no denials.

**Convention restored**: the Silent File Operations / Sub-Agent Model Policy / Agent Classification sections in `CLAUDE.md` now reflect this — background sub-agents are the default write dispatch target again. If you're running an older Claude Code build (pre-v2.1.186), verify with a small probe (background-dispatch a trivial file write and confirm it lands) before relying on background writes, and fall back to inline or a foreground sub-agent if it's still denied.

**Lesson**: don't assume a resolved harness finding is permanent. This flipped once already (denied → allowed); it could in principle flip back on a future harness change. Treat `docs/harness-model-changes.md`'s "What to watch" entries as living, re-checkable claims, not settled facts.

## Informs

- [[pulse-mao-multi-agent-orchestration]] — defines the sub-agent vs. dispatched-agent write boundary; this report supplies the verified foreground-writes / background-writes-restored distinction the MAO doc's design principles now encode.
- [[pulse-execution-modes]] — sub-agent/main-flow execution patterns; background writes being viable again widens execution-mode options beyond the inline-default/foreground-batch split.
