# Model routing

Which model does a task: decided per task by the lead, written in the handoff, logged in the ledger below.
Mechanics: a lane's **subagents** take a `model` per call (Agent tool); a **session's** own model is switched only by
the owner with `/model`. Opus for subagents only within this policy, which the owner approved.

## Phase 1: explore (first ~3 weeks or ~30 tasks)
- Task types: `diagnosis`, `feature`, `refactor`, `tests`, `docs`, `research`.
- Alternate Sonnet and Opus for the implementer within each type (the lead writes which in the handoff).
- **Never explore** on: security, privacy, data loss, releases, migrations. Those get Opus.
- **Escalate:** Sonnet fails review twice or hits the stop rule → redo on Opus, and log both rows.
- Reviewer: Sonnet. Scout: Sonnet (Haiku trial allowed on pure lookups).

## Phase 2: exploit
Per task type, pick the model with the best **accepted-first-time rate**; break ties by lower usage. Re-explore one
task in five to notice drift (new models, new task mix).

## Ledger
| Date | Task ID | Type | Model (impl) | Accepted first time? | Review rounds | Blockers found | Usage (tokens or % of plan) | Owner minutes | Notes |
|---|---|---|---|---|---|---|---|---|---|
