# Model routing

Goal: the strongest model where it changes the outcome, a cheaper one everywhere else, decided by our own numbers.

## Defaults (day one)
| Role | Model | Why |
|---|---|---|
| Lead session | Opus | judgment: grooming, handoffs, checking evidence |
| Lane sessions | Sonnet main + **Opus advisor** (`/advisor opus`, or `"advisorModel": "opus"` in settings) | Sonnet does routine turns; Claude consults Opus before committing to an approach, on a recurring error and before "done". Subagents inherit the advisor |
| Implementer | per task, from the ledger (below) | the experiment |
| Reviewer, scout | Sonnet | fixed during the experiment so results stay comparable |

Only the owner switches a session's model (`/model`, `/advisor`). Lanes set a subagent's model per call (`model` on the
Agent tool). The owner approved this policy, so Opus subagents inside it need no extra approval.

## The experiment (implementer: Sonnet vs Opus)
1. **Assign.** The lead runs `__ROOT__/scripts/ledger.py assign <task-id> <type> [--risk high]` and writes the printed
   model into the handoff. Types: `diagnosis`, `feature`, `refactor`, `tests`, `docs`, `research`.
   - `--risk high` (security, privacy, data loss, releases, migrations, anything irreversible) → always Opus, not counted.
   - Otherwise the script balances Sonnet and Opus within the type until each has 20 tasks.
2. **Name subagent runs after the task:** the Agent description starts with the task ID (`T-12 implement x`).
3. **Escalate.** Sonnet fails review twice or hits the stop rule → redo on Opus. The task counts as not accepted first
   time for Sonnet.
4. **Record the result** when the owner accepts or rejects:
   `ledger.py outcome <task-id> --accepted y|n --review-rounds N --owner-min M [--escaped-defect]`.
5. **Import usage:** `ledger.py scan` reads this project's subagent transcripts (tokens, models, start/end). Run it at
   each retro.
6. **Decide:** `ledger.py report`. Per type, Sonnet becomes the default only when both arms have ≥20 tasks,
   P(Sonnet's success rate is at most 5 points below Opus) > 0.9, and Sonnet uses ≥20% fewer tokens per accepted task.
   After a decision, 20% of eligible tasks stay randomized to catch drift. A new model version or an escaped defect
   restarts that type's comparison.

Expect months, not weeks: at 20–60 tasks a month, 20 per arm per type takes time. Start with one or two common types;
the advisor default gives adaptive escalation meanwhile.

Data: `notes/model-ledger/*.jsonl` (append-only, private). The transcript format is Claude Code 2.1.x internals, not a
public API; `scan` skips what it can't read.
