---
name: test-evidence
description: Use when running a test suite, build or linter and reporting the result: before saying tests pass, in a PR or "ready for review" report, or when test output would flood the context. Runs the command, keeps the full log on disk, prints only totals and failures, and keeps the exit code.
---

# Test evidence

Long test output burns context, and "tests pass" without proof is a claim, not evidence. Run every suite through
the wrapper, and report what it prints.

## Run
```bash
<skill-dir>/test-summary.sh <command...>
# e.g.  test-summary.sh npm test
#       test-summary.sh node --test
#       test-summary.sh pytest -q
#       test-summary.sh go test ./...
#       TEST_LOG_DIR=.logs test-summary.sh cargo test
```
`<skill-dir>` is this skill's folder (Claude Code shows it as the base directory when the skill loads). It prints:
- the command;
- the exit code and the path to the full log;
- the totals lines it recognizes (node --test, pytest, jest/vitest, go test, cargo test, mocha);
- the first 80 failure or skip lines.

It exits with the command's own exit code. The full log stays in `$TEST_LOG_DIR`, by default
`${TMPDIR:-/tmp}/test-logs`.

## Report
Report in this shape and nothing longer:
```
<command>: exit <code>, <passed>/<total> passed, <failed> failed, <skipped> skipped. Full log: <path>
Failures: <test name — one-line reason>, … (max ~10)
```
- **Green means exit 0.** Never say "passing" from a partial run, an old run, or output you didn't see.
- **Skips count.** Name the skipped tests that matter, and why they skipped (a missing env var, no fixtures). Don't
  let a skip read as a pass.
- **Need more detail?** Read the failing part of the log with `grep -n` or line ranges. Don't rerun the suite
  unfiltered, and don't paste more than ~100 lines into a report.
- **For a red → green claim (TDD),** show both runs: the failing one before the fix, the passing one after.
- **Same failure twice?** Stop rerunning. Two identical red runs on the same hypothesis mean you need a new
  hypothesis, not a third run.

If the totals line is missing (an unknown runner), the summary shows only the exit code and failure lines. Read the
log's last lines for the totals and report them by hand.

Part of [claude-code-abyss-team](https://github.com/Suraba03/claude-code-abyss-team), a Claude Code team template.
