# Model routing

Goal: the strongest model **and effort** where it changes the outcome, something cheaper everywhere else, decided by
our own numbers. A cheaper model at higher effort can beat a stronger model at lower effort; we measure it.

## Defaults (day one)
| Role | Model | Why |
|---|---|---|
| __LEAD_CAP__ (lead session) | Opus | judgment: grooming, handoffs, checking evidence |
| __LANE1_CAP__, __LANE2_CAP__ (lane sessions) | Sonnet main + **Opus advisor** (set in each lane's `.claude/settings.local.json`: `"model": "sonnet"`, `"advisorModel": "opus"`) | Sonnet does routine turns; Claude consults Opus before committing to an approach, on a recurring error and before "done". Subagents inherit the advisor |
| Implementer | per task: an **arm** = `model:effort` from the ledger | the experiment |
| Reviewer, scout | Sonnet, default effort | fixed during the experiment so results stay comparable |

Only the owner switches a session's model or advisor (`/model`, `/advisor`, `/effort`). Lanes pass `model` and
`effort` on each implementer call (Agent tool). The owner approved this policy, so Opus subagents and effort settings
inside it need no extra approval.

## The experiment
Arms live in `notes/model-ledger/config.json` (default `sonnet:high`, `sonnet:max`, `opus:high`). Keep 2–3 arms: each
needs ~20 tasks per type before its numbers mean anything.

1. **Assign.** __LEAD_CAP__ runs `__ROOT__/scripts/ledger.py assign <task-id> <type> [--risk high]` and writes the
   printed arm in the handoff. Types: `diagnosis`, `feature`, `refactor`, `tests`, `docs`, `research`.
   - `--risk high` (security, privacy, data loss, releases, migrations, anything irreversible) → `high_risk_arm`
     (default `opus:high`), not counted.
   - Otherwise the script balances the arms within the type until each has 20 tasks.
2. **Run as assigned.** The lane passes the arm's model and effort to the implementer, and the Agent description
   starts with the task ID (`T-12 implement x`). `report` flags runs whose actual model or effort differ.
3. **Escalate.** A cheaper arm fails review twice or hits the stop rule → redo on `opus:high`. The task counts as not
   accepted first time for the original arm.
4. **Record the result** when the owner accepts or rejects:
   `ledger.py outcome <task-id> --accepted y|n --review-rounds N --owner-min M [--escaped-defect]`.
5. **Import usage:** `ledger.py scan` reads this project's subagent transcripts (tokens, model, effort, start/end).
   Run it at each retro.
6. **Decide:** `ledger.py report`. Per type, once every arm has ≥20 tasks: take the arm with the best success rate; switch
   to a cheaper arm only if P(it is at most 5 points worse) > 0.9 and it costs ≥20% less per accepted task (tokens ×
   model weight). After that, 20% of eligible tasks stay randomized to catch drift. A new model version or an escaped
   defect restarts that type's comparison.

Expect months, not weeks: at 20–60 tasks a month, 20 per arm per type takes time. Start with one or two common types;
the advisor default gives adaptive escalation meanwhile.

Data: `notes/model-ledger/` (private). The transcript format is Claude Code 2.1.x internals, not a public API; `scan`
skips what it can't read.
