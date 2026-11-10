# claude-code-abyss-team

**A Claude Code multi-agent team template for one person.** A lead session, two parallel lanes in git worktrees,
review subagents and read-only trainee models (Codex, DeepSeek, GLM). "Done" means evidence, model and effort routing
learns from your own tasks, and the rules keep cost and rework down. Themed after *Made in Abyss*: a project is a
descent, and you gather your party on the way down.

Built for [Claude Code](https://code.claude.com/docs) and works with the
[Superpowers](https://github.com/obra/superpowers) plugin. Extracted from a real project that shipped a Chrome
extension this way.

```
                      you: the owner. Decides, reads the evidence, pushes / merges / deploys
                        │
        Riko (lead) ─── briefs ──▶ Marulk & other apprentices: Codex / DeepSeek / GLM (read-only)
  holds the map: backlog · handoffs · board · evidence checks · retros
        │                               │
  Regu (lane)                     Nanachi (lane)              two Claude Code sessions,
  <name>_regu  (checkout)         <name>_nanachi (worktree)   own ports, own branches
        │                               │
  implementer → Ozen (reviewer)   implementer → Ozen          subagents; Ozen never edits
        └──── Lyza (Opus advisor) is consulted at the hard moments ────┘
```

## The descent
Every project starts the same way: Riko alone at the edge of the Abyss, with a map and a goal. You don't need the whole
party on day one. You gather it as you go deeper.

| Layer | Project phase | Who joins | What the template gives you there |
|---|---|---|---|
| 1 · Edge of the Abyss | idea, kickoff | **Riko**, the lead | `CLAUDE.md`, the backlog, the kickoff prompt: what we're building and why |
| 2 · Forest of Temptation | first features | **Regu**, the first lane | handoffs, the board, TDD with red→green proof, Ozen's reviews |
| 3 · Great Fault | parallel work | **Nanachi**, the second lane (a worktree) | separate ports, file claims, WIP limit: two climbers, one rope |
| 4 · Goblets of Giants | first release | **Marulk**, the apprentice (Codex), plus other apprentices | read-only research briefs, trust grades as whistles, CI and the owner-only publish rule |
| 5 and below | hard bugs, scale, rework | **Lyza**'s advice (the Opus advisor) when it matters | stop rule, postmortems, decisions log, the model:effort ledger |

**The Curse of the Abyss:** the deeper you go, the more it costs to come back up. For us that's context. A session
that has forgotten everything has to climb back through the whole project to re-derive it. So everything lives in
`notes/`, sessions `/clear` at task boundaries, and nobody climbs back up to re-plan an approved handoff.

## Your party
| Name | Role | Model | Lives in |
|---|---|---|---|
| **Riko** | Lead: sets the course, holds the map (backlog, board, handoffs), checks evidence, runs retros | Opus | the project root |
| **Regu** | Lane 1: implements, the first companion | Sonnet + Lyza (Opus advisor) | `<name>_regu/` (main checkout) |
| **Nanachi** | Lane 2: implements in parallel | Sonnet + Lyza | `<name>_nanachi/` (git worktree) |
| **Ozen** the Immovable | `reviewer` subagent: fresh context, never edits, won't budge on weakened tests | Sonnet | a lane's task |
| implementer, scout | subagents doing the digging | per task, from the ledger | a lane's task |
| **Marulk** & apprentices | Trainees: other models (Codex, DeepSeek, GLM), read-only, earn whistles | their own | `notes/trainee/` |
| **Lyza** | The advisor: Claude consults Opus before committing to an approach, on a recurring error, before "done" | Opus | inside the lanes |

The names are defaults (`--names riko,regu,nanachi`). Subagent files keep plain names (`scout`, `implementer`,
`reviewer`) so they work with any setup.

**Whistles = trust grades.** Every apprentice starts with a Bell whistle: read-only research, every find checked
against sources. Three verified finds in a row earn the next whistle: Red (critique), Blue (document drafts), Moon
(patches as diff files), Black (small implementation tasks). The lanes carry White whistles. A made-up fact or a step
outside the whistle sends the apprentice back up (`notes/team.md`).

## Why this shape
- **Files, not chatter.** The board, handoffs, backlog and decisions live in `notes/`. Sessions read files after a
  `/clear` instead of re-deriving context. Messages carry only "assigned", "blocked" and "ready".
- **Two lanes, not ten agents.** Your review time is the bottleneck. Two worktrees with separate ports let two tasks
  run in parallel without stepping on each other. A WIP limit stops work from piling up unreviewed.
- **Done means evidence.** A lane reports:
  - the tested commit;
  - red→green proof for each new test;
  - counts and skips;
  - Ozen's verdict (`notes/definition-of-done.md`).

  You read a packet instead of re-checking by hand.
- **Guardrails against known agent failures:**
  - weakened tests: Ozen audits test changes;
  - loops: the stop rule escalates after two failed attempts or ~20 min without new evidence;
  - re-planning approved work: the handoff is the plan;
  - log floods: `scripts/test-summary.sh`;
  - publishing without you: only the owner pushes, merges and deploys.
- **Model and effort routing that learns.** Lanes run Sonnet with Lyza (Opus) as advisor. `scripts/ledger.py` gives
  the implementer an arm (`model:effort`, e.g. `sonnet:max` vs `opus:high`) per task: balanced per task type at first,
  with high-risk work always on the strong arm. Token usage, model and effort come from Claude Code's own transcripts.
  The default flips only when the numbers say so (`notes/model-routing.md`).
- **Any model can be an apprentice.** `notes/trainee/ask.sh <brief> [codex|deepseek|glm]` runs Codex natively.
  DeepSeek or GLM run through Claude Code pointed at their Anthropic-compatible APIs, with read-only tools and `.env`
  and `~/.ssh` denied.

## Quick start
```bash
git clone https://github.com/<you>/claude-code-abyss-team ~/vibe/claude-code-abyss-team
~/vibe/claude-code-abyss-team/scripts/new-project.sh my_app --remote git@github.com:<you>/my_app.git --ports 200
```
The script creates `~/vibe/my_app/`:
- `CLAUDE.md`, `AGENTS.md` and `notes/`;
- `my_app_regu` (a clone) and `my_app_nanachi` (a worktree), with port offsets 200 and 300;
- lanes set to Sonnet with the Opus advisor;
- local-only files excluded from git.

Then it prints the next steps:
1. Copy `agents/*.md` to `~/.claude/agents/` (once per machine).
2. Optionally, add the protected-paths hook (`hooks/`).
3. Optionally, set up apprentices (`notes/trainee/trainees/*.conf`: a Codex profile, a DeepSeek or GLM key).
4. Fill the `<…>` placeholders in `CLAUDE.md` ("Never commit", "Product rules").
5. Start Riko (`claude --model opus` in the root) and the two lanes. Paste `prompts/lead-kickoff.md` and
   `prompts/lane-kickoff.md`.

Give each project its own `--ports` range, so several expeditions' lanes can run at once.

## What's inside
| Path | What |
|---|---|
| `project/CLAUDE.md` | Rules for every session, ~55 lines: layout, team, never-commit, lanes, work rules |
| `project/AGENTS.md` | Rules for apprentices (any non-Claude model): read-only, sources and `[verified]` marks |
| `project/notes/board.md` | Claims: task ID, lane, branch @ base SHA, files, model:effort, state, updated |
| `project/notes/definition-of-done.md` | The evidence packet a lane sends before "ready for review" |
| `project/notes/templates/` | Handoff, retro (one change per retro), blameless postmortem |
| `project/notes/team.md` | Party, whistles (trust grades) per apprentice, the apprentices' journal |
| `project/notes/model-routing.md` | Model, advisor and effort defaults; explore → exploit policy |
| `project/notes/decisions.md` | Short decision records |
| `project/notes/trainee/` | `ask.sh` (brief → answer, read-only), apprentice profiles, Codex quota logger |
| `agents/` | `scout`, `implementer`, `reviewer` subagents: Sonnet, no recursion, reviewer read-only |
| `hooks/` | A PreToolUse hook that blocks edits to protected paths |
| `scripts/` | See below |
| `prompts/` | Kickoff messages for Riko and the lanes |

The scripts:
- `new-project.sh` sets up a new project;
- `test-summary.sh` gives short test output, keeps the full log and preserves the exit code;
- `ledger.py` does the routing: assign, scan transcripts, outcome, report.

## Working loop
1. **Groom** with Riko: the backlog by urgency and points, product vs tech debt.
2. **Assign:** Riko writes a handoff and pings Regu or Nanachi. A handoff covers:
   - why, scope and out of scope;
   - acceptance criteria;
   - known facts and failed approaches;
   - files;
   - the `model:effort` from the ledger.
3. **Build:** the lane claims the row and branches from fresh main. The implementer does TDD, then Ozen checks the
   diff and the evidence with a fresh context.
4. **Evidence:** the lane sends the packet and Riko checks it. You read it, say "push", look at CI and merge.
5. **Clear:** the lane ends with "Context: ready for /clear before the next task", and you run `/clear`.
6. **Retro** after an iteration: pick one change (a rule, test, hook or template), apply it, and check it next time.

## What we learned (and where it comes from)
- Multi-agent systems spend far more tokens than a single chat: Anthropic measured ~15× for its research system.
  Split work only where workers don't need the same context.
  [Anthropic, 2025](https://www.anthropic.com/research/multi-agent-research-system)
- Keep `CLAUDE.md` short (Anthropic suggests under ~200 lines). Move procedures into files and skills.
  [Memory docs](https://code.claude.com/docs/en/memory)
- A separate evaluator with a fresh context and no write access catches what the builder talks itself past.
  [anthropics/cwc-long-running-agents](https://github.com/anthropics/cwc-long-running-agents)
- Agile ceremonies between agents haven't shown measured gains, while tests and iteration with feedback have. Here,
  board events replace daily stand-ups.
  [AgileCoder](https://arxiv.org/abs/2406.11912), [Agent Scrum](https://daveremy.github.io/agent-scrum/)
- Learned routers (RouteLLM, FrugalGPT cascades) save a lot on benchmarks. But at 20–60 tasks a month, you need ~20
  tasks per arm before trusting a switch. Until then, a cheap main model with a strong advisor is the safe default.
  [RouteLLM](https://www.lmsys.org/blog/2024-07-01-routellm/), [FrugalGPT](https://arxiv.org/abs/2305.05176),
  [Claude Code advisor](https://code.claude.com/docs/en/advisor)
- Human review capacity, not agent count, limits parallel work.
  [Simon Willison, 2025](https://simonwillison.net/2025/Oct/5/parallel-coding-agents/)

## Credits and license
- Workflow skills: [Superpowers](https://github.com/obra/superpowers) by Jesse Vincent.
- The names and the descent are an affectionate nod to *Made in Abyss* by Akihito Tsukushi. This is a fan reference
  only, with no affiliation and no official assets.
- MIT license (see `LICENSE`).
