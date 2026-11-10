# Team and trust grades

Private, not in git. A grade is what a worker may do without close control. Grades are
Cave Raider whistles: you earn a deeper one by coming back with verified finds. The owner raises or lowers grades; the
lead proposes from the journal below.

## Members
| Who | Grade | Works in | Gets tasks from |
|---|---|---|---|
| Owner | — | everything | — |
| __LEAD_CAP__, the lead (Claude Code session) | — | `notes/`: backlog, handoffs, research, checks | the owner |
| __LANE1_CAP__, lane (Claude Code session) | 10 | `__PROJECT_____LANE1__/` | board + handoff + __LEAD_CAP__'s message |
| __LANE2_CAP__, lane (Claude Code session) | 10 | `__PROJECT_____LANE2__/` | same |
| Implementer (subagent) | 5 | inside a lane's task | the lane |
| Reviewer (subagent) | review-only | reads the diff and the evidence, never edits | the lane, after the implementer |
| Trainee: codex | 1 | read-only, `notes/trainee/ask.sh <brief> codex` | __LEAD_CAP__ |
| Trainee: deepseek / glm / … (add a row per model) | 1 | read-only, `ask.sh <brief> <trainee>` | __LEAD_CAP__ |

## What each grade may do
| Grade (whistle) | May | Control |
|---|---|---|
| 1 · Bell | Research on the web and in the code, fact checks, second opinions. Read-only | lead checks everything against sources |
| 2 · Red | + grooming and brainstorm critique: backlog, handoffs, specs; own proposals | lead spot-checks |
| 3 · Blue | + document drafts: briefs, specs, store and post texts | lead edits and decides |
| 4 · Moon | + patches: small isolated changes as diff files in `notes/trainee/patches/`; a lane reviews and applies | lane review + tests |
| 5 · Black | implementer level: small tasks with tests (TDD) in a branch, no push, from a handoff | lane review + reviewer |
| 7 · Black, own camp | a small task end to end (branch, tests, report) in its own folder the owner sets up | lane review, owner check |
| 10 · White | lane: tasks from the board, own branches, PRs on the owner's word | owner check before PR |

At any grade, without the owner's word: no push, merge, deploy, release, or store changes.

## Raising and lowering
- **+1:** three tasks in a row at the current grade rated ✓ (facts match sources, inside the brief, rules kept). The
  lead proposes, the owner decides.
- **−1 or reset to 1:** a made-up fact or source presented as verified; an action outside the grade (writing files,
  git); a private name or secret in an answer.
- `~` (partly useful, honest about gaps) neither raises nor lowers.

## Journal
| Date | Trainee | Task | Brief → answer | Rating | Notes |
|---|---|---|---|---|---|
