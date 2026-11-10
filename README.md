# claude-code-team-template

**A file-based AI dev team for one person: a lead session, two parallel lanes in git worktrees, review subagents and
a research trainee — with evidence-based "done" and rules that keep cost and rework down.**

Built for [Claude Code](https://code.claude.com/docs) (works with the [Superpowers](https://github.com/obra/superpowers)
plugin), with optional [Codex](https://developers.openai.com/codex) as a read-only researcher. Extracted from a real
project that shipped a Chrome extension with this setup.

```
            owner (you): decides, reviews evidence, pushes/merges/deploys
                 │
             lead session ─── briefs ──▶ Codex trainee (read-only research)
     backlog · handoffs · board · checks evidence · retros
          │                         │
     lane A session            lane B session          (two Claude Code sessions,
     <name>_a (checkout)       <name>_b (worktree)      own ports, own branches)
          │                         │
   implementer → reviewer    implementer → reviewer    (subagents; reviewer never edits)
```

## Why this shape
- **Files, not chatter.** The board, handoffs, backlog and decisions live in `notes/`. Sessions read files after a
  `/clear` instead of re-deriving context; messages are only for "assigned", "blocked" and "ready".
- **Two lanes, not ten agents.** Your review time is the bottleneck. Two worktrees with separate ports let two tasks
  run in parallel without stepping on each other; a WIP limit stops work from piling up unreviewed.
- **Done means evidence.** A lane reports a tested commit, red→green proof for each new test, counts, skips and a
  fresh-context review verdict (`notes/definition-of-done.md`). You read a packet instead of re-checking by hand.
- **Guardrails against known agent failures:** weakened tests (reviewer audits test changes), loops (stop rule:
  two failed attempts or ~20 min without new evidence → escalate), re-planning approved work (the handoff is the plan),
  log floods (`scripts/test-summary.sh`), publishing without you (only the owner pushes, merges, deploys).
- **Trust grades** for the research trainee: it earns more scope after three verified tasks in a row.
- **Model routing that learns:** lanes run Sonnet with an Opus advisor; the implementer's model is assigned per task by
  `scripts/ledger.py` (balanced Sonnet/Opus per task type, high-risk work always Opus), outcomes and token usage are
  logged from Claude Code's own transcripts, and the default flips only when the numbers say so
  (`notes/model-routing.md`).

## Quick start
```bash
git clone https://github.com/<you>/claude-code-team-template ~/vibe/claude-code-team-template
~/vibe/claude-code-team-template/scripts/new-project.sh my_app --remote git@github.com:<you>/my_app.git --ports 200
```
The script creates `~/vibe/my_app/` with `CLAUDE.md`, `AGENTS.md`, `notes/`, lane A (clone) and lane B (worktree), port
offsets 200/300, local-only files excluded from git, and prints the next steps:
1. copy `agents/*.md` to `~/.claude/agents/` (once per machine);
2. optionally add the protected-paths hook (`hooks/`);
3. optionally add the Codex profile;
4. fill the `<…>` placeholders in `CLAUDE.md` ("Never commit", "Product rules");
5. start three sessions and paste `prompts/lead-kickoff.md` and `prompts/lane-kickoff.md`.

Give each project its own `--ports` range so several projects' lanes can run at once.

## What's inside
| Path | What |
|---|---|
| `project/CLAUDE.md` | Rules for every session, ~50 lines: layout, never-commit, lanes, work rules |
| `project/AGENTS.md` | Rules for the Codex trainee: read-only, sources and `[verified]` marks |
| `project/notes/board.md` | Claims: task ID, lane, branch @ base SHA, files, state, updated |
| `project/notes/definition-of-done.md` | The evidence packet a lane sends before "ready for review" |
| `project/notes/templates/` | Handoff, retro (one change per retro), blameless postmortem |
| `project/notes/team.md` | Roles, trust grades, the trainee's journal |
| `project/notes/model-routing.md` | Explore → exploit policy and the outcome ledger |
| `project/notes/decisions.md` | Short decision records |
| `project/notes/codex/` | `ask.sh` (brief → answer, logs quota before/after), `quota.py`, profile example |
| `agents/` | `scout`, `implementer`, `reviewer` subagents (Sonnet, no recursion; reviewer read-only) |
| `hooks/` | PreToolUse hook that blocks edits to protected paths |
| `scripts/` | `new-project.sh`, `test-summary.sh` (short test output, full log kept, exit code preserved), `ledger.py` (model routing: assign, scan transcripts, outcome, report) |
| `prompts/` | Kickoff messages for the lead and the lanes |

## Working loop
1. **Groom** with the lead: backlog by urgency and points; product vs tech debt.
2. **Assign:** the lead writes a handoff (why, scope, out of scope, acceptance criteria, known facts and failed
   approaches, files, model) and pings a lane.
3. **Build:** the lane claims the row, branches from fresh main, has the implementer do TDD, and the reviewer check
   the diff and evidence with a fresh context.
4. **Evidence:** the lane sends the packet. The lead checks it; you read it, say "push", look at CI, merge.
5. **Clear:** the lane ends with "Context: ready for /clear before the next task"; you run `/clear`.
6. **Retro** after an iteration: pick one change (a rule, test, hook or template), apply it, check it next time.

## What we learned (and where it comes from)
- Multi-agent systems spend far more tokens than a single chat (Anthropic measured ~15× for its research system);
  split work only where workers don't need the same context.
  [Anthropic, 2025](https://www.anthropic.com/research/multi-agent-research-system)
- Keep `CLAUDE.md` short (Anthropic suggests under ~200 lines); move procedures into files and skills.
  [Memory docs](https://code.claude.com/docs/en/memory)
- A separate evaluator with a fresh context and no write access catches what the builder talks itself past.
  [anthropics/cwc-long-running-agents](https://github.com/anthropics/cwc-long-running-agents)
- Agile ceremonies between agents haven't shown measured gains; tests and iteration with feedback have. Daily
  stand-ups are replaced by board events here.
  [AgileCoder](https://arxiv.org/abs/2406.11912), [Agent Scrum](https://daveremy.github.io/agent-scrum/)
- Learned routers (RouteLLM, FrugalGPT cascades) save a lot on benchmarks, but with 20–60 tasks a month you need
  ~20 tasks per arm before trusting a switch; until then a cheap main model with a strong advisor is the safe default.
  [RouteLLM](https://www.lmsys.org/blog/2024-07-01-routellm/), [FrugalGPT](https://arxiv.org/abs/2305.05176),
  [Claude Code advisor](https://code.claude.com/docs/en/advisor)
- Human review capacity, not agent count, limits parallel work.
  [Simon Willison, 2025](https://simonwillison.net/2025/Oct/5/parallel-coding-agents/)

## Credits and license
Workflow skills: [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent. MIT license (see `LICENSE`).
