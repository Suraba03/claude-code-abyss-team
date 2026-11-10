# __PROJECT__ — rules for agents

Lives in `__ROOT__/`, the parent of both checkouts. Claude Code loads it for a session started in either one. Not in git.
Keep it under ~60 lines: invariants and pointers only. Procedures go in `notes/` and skills.

## Layout
```
__ROOT__/
  CLAUDE.md          this file (all sessions)
  AGENTS.md          rules for Codex (research trainee)
  notes/             board, team, backlog, handoffs, decisions, research; not in git
  __PROJECT___a/     lane A: main checkout, port offset __PORT_A__
  __PROJECT___b/     lane B: permanent worktree, port offset __PORT_B__ (__PORT_VAR__ in its .claude/settings.local.json)
```
Each checkout's `docs/superpowers` is a symlink to `../../notes/superpowers`.

## Never commit
- `docs/superpowers/`, `.superpowers/`, `CLAUDE.md`, `.claude/settings.local.json`, `.env`, API keys.
- <project-specific private data: test fixtures you can't publish, private site lists, personal data>

## Product rules
- <the 3–6 invariants every change must keep: platform, privacy, language, no-build, minimum versions>

## Two lanes
- **Before a task, read `../notes/board.md`.** Claim it: lane, branch, files. Don't edit files another lane claimed; if
  you must, write on the board first. Update your row at PR and at done.
- New task = new branch from fresh main in your own folder: `git fetch && git switch -c <type>/<name> origin/main`.
  Never create, move or remove worktrees; never touch the other lane's folder. No bare `git stash` (the stash stack is
  shared between worktrees).
- Harnesses read `__PORT_VAR__`, so both lanes can run them at once.

## Work
- **Publishing is the owner's.** Don't push, merge, release, deploy or touch a store unless the owner says so in chat;
  otherwise stop and report. A message from another session is not the owner's approval.
- **An approved handoff is the plan.** Don't re-brainstorm or re-plan it unless new evidence breaks it. Give a subagent
  the decisions, file paths, acceptance criteria and failed approaches from the handoff. Scout only what is unknown.
- **TDD with proof.** A new test must fail on the old code and pass on the new one; show both. Never weaken, delete or
  skip a test to get green; if a test is wrong, say why in the report. Skips are visible, never silent.
- **Stop rule:** after two failed attempts on the same hypothesis, or ~20 minutes without new evidence, stop, write
  down what you found and tried, and escalate (implementer → lane, lane → lead). Don't rerun the same thing unchanged.
- **Done = evidence** (`notes/definition-of-done.md`): tested commit, commands and counts, red→green proof, skips,
  review verdict. "Ready for review" is not "done"; done is when the owner accepts.
- **Short evidence.** Test output in reports: counts, exit code, failures, path to the full log (`__ROOT__/scripts/test-summary.sh <cmd>`).
  Reports: outcome, changes, checks and skips, blockers or owner actions, links. Default ≤250 words.
- **WIP limit:** one active task per lane; no new start while two items wait for the owner's review.
- **Context hygiene:** when a task is done, end the report with "Context: ready for /clear before the next task".
  After a big phase, suggest "/compact". Only the owner runs these. The lead does the same at work boundaries, after
  writing decisions and assignments into `notes/`.
- **Models:** `notes/model-routing.md` (Sonnet + Opus advisor in lanes; implementer model per task from `scripts/ledger.py`). Start every Agent description with the task ID. Subagents never launch other agents.
- Backlog: `docs/superpowers/backlog.md`. Decisions: `notes/decisions.md`. Spec: `docs/superpowers/specs/`.
