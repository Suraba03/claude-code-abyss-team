# Definition of done (Ozen's verdict)

Ozen the Immovable doesn't budge without evidence. Neither does this list.

A lane reports **ready for review** with this packet (≤250 words plus links). The task is **done** only when the owner
accepts it.

1. **Commit:** branch, tested commit SHA, base SHA (after `git fetch && git rebase origin/main`). Rebased or changed
   after testing → test again.
2. **Acceptance:** each criterion from the handoff → the test or check that proves it (✓ / ✗ / not checkable, why).
3. **Red → green:** for each new test, show that it failed on the old code and passes now (one line each).
4. **Checks:** commands, counts, exit codes, path to full logs. Skipped suites listed with the reason.
5. **Extra verification** the project requires (e.g. a lab run on real data, a browser smoke, evals for LLM-facing
   changes), with its summary and diff against the previous run.
6. **Review:** reviewer verdict and how each finding was resolved (fixed / rejected with reason).
7. **Test integrity:** were any tests deleted, weakened, re-baselined or skipped? If yes, why.
8. **Leftovers:** known limits, follow-ups proposed for the backlog, owner actions (with exact steps).
9. Last line: "Context: ready for /clear before the next task".
