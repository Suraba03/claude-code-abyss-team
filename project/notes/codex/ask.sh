#!/bin/zsh
# Runs Codex (research trainee) on a brief: read-only, web search on.
# usage: notes/codex/ask.sh <name>    reads notes/codex/briefs/<name>.md, writes notes/research/<name>.md
# Profile: ~/.codex/<CODEX_PROFILE>.config.toml (default: __PROJECT__-research; example in research.config.toml.example).
# CODEX_EFFORT=xhigh overrides the reasoning effort for one run.
set -eu
ROOT=${0:A:h:h:h}            # notes/codex/ask.sh -> project root
name=$1
brief=$ROOT/notes/codex/briefs/$name.md
out=$ROOT/notes/research/$name.md
log=$ROOT/notes/codex/runs.log
[[ -f $brief ]] || { echo "no brief: $brief" >&2; exit 1; }
before=$(python3 $ROOT/notes/codex/quota.py --line 2>/dev/null || true)
echo "$(date '+%F %T') start $name profile=${CODEX_PROFILE:-__PROJECT__-research} effort=${CODEX_EFFORT:-default} | before: $before" >> $log
code=0
codex exec -p "${CODEX_PROFILE:-__PROJECT__-research}" ${CODEX_EFFORT:+-c model_reasoning_effort="\"$CODEX_EFFORT\""} \
  -C $ROOT --skip-git-repo-check -o $out - < $brief > $ROOT/notes/codex/last-$name.log 2>&1 || code=$?
after=$(python3 $ROOT/notes/codex/quota.py --line 2>/dev/null || true)
echo "$(date '+%F %T') end $name exit=$code | after: $after" >> $log
echo "$after"
exit $code
