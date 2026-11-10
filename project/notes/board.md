# Board

Who is doing what. Claim a row before you start; update it at PR and at done. Remove rows once merged.
WIP limit: one active task per lane; no new start while two items wait for the owner's review.

Sessions: __LEAD_CAP__ (lead) = `<session name>`, __LANE1_CAP__ = `<session name>`, __LANE2_CAP__ = `<session name>`.
Trainees (other models, see `team.md`) never edit files or claim rows.
__LEAD_CAP__ assigns tasks under "Assigned" with a handoff file and pings the lane. When you pick one, move it into the
table as your row.

| ID | Lane | Task | Branch @ base SHA | Files claimed | Model:effort | State | Updated |
|---|---|---|---|---|---|---|---|

States: `claimed` → `in progress` → `blocked: <why>` → `ready for review (PR #N)` → `done (owner accepted)`.

## Assigned (not started)
| ID | Lane | Task | Handoff | Note |
|---|---|---|---|---|

## Not claimed
Tasks live in `superpowers/backlog.md`. Lanes don't pick from it directly; __LEAD_CAP__ assigns them here.
