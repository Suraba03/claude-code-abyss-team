#!/usr/bin/env bash
# Run a test command, keep the full log, print a short summary, keep the exit code.
# usage: test-summary.sh <command...>     e.g. test-summary.sh npm test
#        TEST_LOG_DIR=dir test-summary.sh ...   (default: ${TMPDIR:-/tmp}/test-logs)
set -o pipefail
dir=${TEST_LOG_DIR:-${TMPDIR:-/tmp}/test-logs}
mkdir -p "$dir"
log="$dir/$(date +%Y%m%d-%H%M%S)-$$.log"
"$@" > "$log" 2>&1
code=$?
echo "command: $*"
echo "exit: $code   full log: $log   ($(wc -l < "$log" | tr -d ' ') lines)"
# Totals lines from common runners: node --test (TAP), pytest, jest/vitest, go test, cargo test, mocha.
grep -E '^# (tests|suites|pass|fail|cancelled|skipped|todo) [0-9]+|^(=+ )?[0-9]+ (passed|failed)|^Tests?:|^Test Files|^(ok|FAIL)[[:space:]]+[^ ]+[[:space:]]+[0-9.]+s|^test result:|[0-9]+ (passing|failing|pending)' "$log" | tail -n 12
# Failures and skips, capped.
fails=$(grep -nE 'not ok |(^|[^A-Za-z_])FAIL([^A-Za-z_]|$)|✖|✗|AssertionError|panicked|^E   |# SKIP|[0-9]+ (failed|skipped)' "$log" | grep -vE '(^|:)# (fail|skipped) 0$|[^1-9]0 (failed|skipped)' | head -n 80)
if [ -n "$fails" ]; then echo "--- failures / skips (first 80) ---"; echo "$fails"; fi
exit $code
