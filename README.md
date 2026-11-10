# claude-code-abyss-team

**A Claude Code multi-agent team template for one person.** A lead session, two parallel lanes in git worktrees,
review subagents and read-only trainee models (Codex, DeepSeek, GLM). "Done" means evidence, model and effort routing
learns from your own tasks, and the rules keep cost and rework down. Themed after *Made in Abyss*: a project is a
descent, and you gather your party on the way down.

Built for [Claude Code](https://code.claude.com/docs) and works with the
[Superpowers](https://github.com/obra/superpowers) plugin.

**Field-tested.** This setup was developed in practice on
[anki_manga](https://github.com/Suraba03/anki_manga), which ships as
[Manga OCR & Mining for Anki](https://chromewebstore.google.com/detail/manga-ocr-mining-for-anki/bgfnpifeeclmpfdcahphaiahgafjppeo)
in the Chrome Web Store. That project uses a Chrome MV3 extension, on-device OCR, a Cloudflare Worker and CI.
A lead and two lanes took it from 0.2 to 0.3 in five days. The work included 14 merged PRs, a privacy audit by a
research apprentice, a real-site test lab and a release.

```
                      you: the owner. Decides, reads the evidence, pushes / merges / deploys
                        │
        Riko (lead) ─── briefs ──▶ Marulk & other apprentices: Codex / DeepSeek / GLM (read-only)
  holds the map: backlog · handoffs · board · Ozen's verdict (definition of done) · retros
        │                               │
  Regu (lane)                     Nanachi (lane)              two Claude Code sessions,
  <name>_regu  (checkout)         <name>_nanachi (worktree)   own ports, own branches
        │                               │
  implementer → reviewer          implementer → reviewer      subagents; the reviewer never edits
        └──── Lyza (Opus advisor) is consulted at the hard moments ────┘
```

## The descent
Every project starts the same way: Riko at the edge of the Abyss, with a map and a goal. You don't need the whole
party on day one: you gather it as you go deeper, in the order the story does.

| Layer | Project phase | Who joins | What the template gives you there |
|---|---|---|---|
| 1 · Edge of the Abyss | idea, kickoff, first features | **Riko**, the lead, and soon **Regu**, the first lane | `CLAUDE.md`, the backlog, handoffs, the board, TDD with red→green proof |
| 2 · Forest of Temptation (Seeker Camp) | the work has to prove itself | **Marulk**, the apprentice (Codex), and **Ozen's verdict** | read-only research briefs; whistles as trust grades; nothing is done until it passes Ozen's verdict (`definition-of-done.md`) |
| 3 · Great Fault | the climb gets steep | CI and the owner-only publish rule | tests on every PR, protected paths, deploy by button |
| 4 · Goblets of Giants | parallel work | **Nanachi**, the second lane (a git worktree) | separate ports, file claims, WIP limit: two climbers, one rope |
| 5 and below | hard bugs, scale, rework; more apprentices (DeepSeek, GLM) | **Lyza**'s advice (the Opus advisor) when it matters | stop rule, postmortems, decisions log, the model:effort ledger |

**The Curse of the Abyss:** the deeper you go, the more it costs to come back up. For us that's context: a session that
has forgotten everything has to climb back through the whole project to re-derive it. So everything lives in `notes/`,
sessions `/clear` at task boundaries, and nobody climbs back up to re-plan an approved handoff.

## Your party
| Name | Role | Model | Lives in |
|---|---|---|---|
| **Riko** | Lead: sets the course, holds the map (backlog, board, handoffs), gives Ozen's verdict on evidence, runs retros | Opus | the project root |
| **Regu** | Lane 1: implements, the first companion | Sonnet + Lyza | `<name>_regu/` (main checkout) |
| **Nanachi** | Lane 2: implements in parallel | Sonnet + Lyza | `<name>_nanachi/` (git worktree) |
| **Lyza** | The advisor: the lanes consult Opus before committing to an approach, on a recurring error and before "done" | Opus | inside the lanes |
| **Marulk** & apprentices | Trainees: other models (Codex, DeepSeek, GLM), read-only, earn whistles | their own | `notes/trainee/` |

**Ozen's verdict** is the definition of done, and Ozen the Immovable doesn't budge without evidence:
- the tested commit;
- red→green proof for every new test;
- counts and skips;
- the reviewer's findings resolved;
- no weakened tests.

The workers inside a lane stay plain `scout`, `implementer` and `reviewer` subagents, with no names and no lore. The
names are defaults: `--names riko,regu,nanachi`.

**Whistles = trust grades.** In the Abyss, the deeper you're trusted to go, the higher your whistle. White Whistles
dive deepest. Here the same holds: the higher the whistle, the deeper into the project a worker may act on its own.

| Whistle | Grade | May |
|---|---|---|
| Bell | 1 | read-only research; every find checked against sources (every apprentice starts here) |
| Red | 2 | + critique of backlog, specs and plans |
| Blue | 3 | + document drafts |
| Moon | 4 | + patches as diff files that a lane applies |
| Black | 5–7 | + small implementation tasks with tests |
| White | 10 | the lanes: own branches, PRs on the owner's word |

Three verified finds in a row earn the next whistle. A made-up fact or a step outside the whistle sends a worker back
up (`notes/team.md`).

## Why this shape
- **Files, not chatter.** The board, handoffs, backlog and decisions live in `notes/`. Sessions read files after a
  `/clear` instead of re-deriving context. Messages carry only "assigned", "blocked" and "ready".
- **Two lanes, not ten agents.** Your review time is the bottleneck. Two worktrees with separate ports let two tasks
  run in parallel without stepping on each other. A WIP limit stops work from piling up unreviewed.
- **Done means evidence.** A lane reports:
  - the tested commit;
  - red→green proof for each new test;
  - counts and skips;
  - the reviewer's findings and how each was resolved.

  This is Ozen's verdict (`notes/definition-of-done.md`).

  You read a packet instead of re-checking by hand.
- **Guardrails against known agent failures:**
  - weakened tests: the reviewer audits every test change;
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
Click **Use this template** (or clone it), then:
```bash
~/vibe/claude-code-abyss-team/scripts/new-project.sh my_app --remote git@github.com:<you>/my_app.git --ports 200
~/vibe/my_app/riko
```
That's the whole path. Riko opens on Opus with her role already loaded, reads `notes/`, asks what you're building and
fills in the project rules with you. When she has put the first tasks on the board, start the lanes:
```bash
~/vibe/my_app/regu        # and, in another tab:
~/vibe/my_app/nanachi
```
The same three commands resume a session after `/clear` or a restart; extra arguments go to `claude`
(`~/vibe/my_app/riko --continue`).

Already know what you're building? Write it down and pass `--kickoff idea.md`: it lands in `notes/kickoff.md`, and
Riko starts from it instead of asking.

What the script creates in `~/vibe/my_app/`:
- `CLAUDE.md`, `AGENTS.md` and `notes/` (the map), the launchers `riko`, `regu`, `nanachi`;
- `my_app_regu` (a clone; it needs at least one commit, e.g. a README) and `my_app_nanachi` (a worktree), with port
  offsets 200 and 300;
- lanes set to Sonnet with the Opus advisor; local-only files excluded from git.

Once per machine, copy the subagents: `cp -n agents/*.md ~/.claude/agents/`. Optional: the protected-paths hook
(`hooks/`) and apprentices (`notes/trainee/trainees/*.conf`: a Codex profile, a DeepSeek or GLM key).

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
| `project/notes/prompts/` | Role prompts the launchers open each session with (lead, lane) |

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
3. **Build:** the lane claims the row and branches from fresh main. The implementer does TDD, then the reviewer checks the
   diff and the evidence with a fresh context.
4. **Ozen's verdict:** the lane sends the evidence packet and Riko checks it against the definition of done. You read it, say "push", look at CI and merge.
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
