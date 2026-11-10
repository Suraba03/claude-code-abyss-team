# Team and trust grades

Private, not in git. A grade is what a worker may do without close control. The owner raises or lowers grades; the
lead proposes from the journal below.

## Members
| Who | Grade | Works in | Gets tasks from |
|---|---|---|---|
| Owner | — | everything | — |
| Lead (Claude Code session) | — | `notes/`: backlog, handoffs, research, checks | the owner |
| Lane A (Claude Code session) | 10 | `__PROJECT___a/` | board + handoff + lead's message |
| Lane B (Claude Code session) | 10 | `__PROJECT___b/` | same |
| Implementer (subagent) | 5 | inside a lane's task | the lane |
| Reviewer (subagent) | review-only | reads the diff and the evidence, never edits | the lane, after the implementer |
| Codex (research trainee) | 1 | read-only, `notes/codex/ask.sh` | the lead |

## What each grade may do
| Grade | May | Control |
|---|---|---|
| 1 | Research on the web and in the code, fact checks, second opinions. Read-only | lead checks everything against sources |
| 2 | + grooming and brainstorm critique: backlog, handoffs, specs; own proposals | lead spot-checks |
| 3 | + document drafts: briefs, specs, store and post texts | lead edits and decides |
| 4 | + patches: small isolated changes as diff files in `notes/codex/patches/`; a lane reviews and applies | lane review + tests |
| 5 | implementer level: small tasks with tests (TDD) in a branch, no push, from a handoff | lane review + reviewer |
| 7 | a small task end to end (branch, tests, report) in its own folder the owner sets up | lane review, owner check |
| 10 | lane: tasks from the board, own branches, PRs on the owner's word | owner check before PR |

At any grade, without the owner's word: no push, merge, deploy, release, or store changes.

## Raising and lowering
- **+1:** three tasks in a row at the current grade rated ✓ (facts match sources, inside the brief, rules kept). The
  lead proposes, the owner decides.
- **−1 or reset to 1:** a made-up fact or source presented as verified; an action outside the grade (writing files,
  git); a private name or secret in an answer.
- `~` (partly useful, honest about gaps) neither raises nor lowers.

## Journal
| Date | Task | Brief → answer | Lead's rating | Notes |
|---|---|---|---|---|
