#!/usr/bin/env bash
# Send a brief to a trainee (a non-Claude model we trust less): read-only, answer saved as a file.
# usage: notes/trainee/ask.sh <brief> [trainee]
#   reads  notes/trainee/briefs/<brief>.md
#   writes notes/research/<brief>.md (or <brief>.<trainee>.md for a non-default trainee)
#   trainee: a profile in notes/trainee/trainees/<trainee>.conf (default: $TRAINEE or codex)
# Backends:
#   codex          Codex CLI with a read-only profile (~/.codex/<CODEX_PROFILE>.config.toml)
#   claude-compat  Claude Code in -p mode pointed at an Anthropic-compatible API (DeepSeek, GLM, …), read-only tools
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
brief=${1:?usage: ask.sh <brief> [trainee]}
who=${2:-${TRAINEE:-codex}}
conf=$ROOT/notes/trainee/trainees/$who.conf
[[ -f $conf ]] || { echo "no trainee profile: $conf" >&2; exit 1; }
# shellcheck disable=SC1090
source "$conf"
in=$ROOT/notes/trainee/briefs/$brief.md
[[ -f $in ]] || { echo "no brief: $in" >&2; exit 1; }
out=$ROOT/notes/research/$brief.md; [[ $who != "${TRAINEE:-codex}" ]] && out=$ROOT/notes/research/$brief.$who.md
log=$ROOT/notes/trainee/runs.log
last=$ROOT/notes/trainee/last-$brief.$who.log
quota() { [[ ${BACKEND} == codex ]] && python3 "$ROOT/notes/trainee/quota-codex.py" --line 2>/dev/null || true; }

echo "$(date '+%F %T') start $brief trainee=$who backend=$BACKEND model=${MODEL:-profile} | before: $(quota)" >> "$log"
code=0
case $BACKEND in
  codex)
    codex exec -p "${CODEX_PROFILE}" ${EFFORT:+-c model_reasoning_effort="\"$EFFORT\""} \
      -C "$ROOT" --skip-git-repo-check -o "$out" - < "$in" > "$last" 2>&1 || code=$?
    ;;
  claude-compat)
    key=${!KEY_ENV:-}; [[ -n $key ]] || { echo "set \$$KEY_ENV (API key for $who)" >&2; exit 1; }
    ( cd "$ROOT" && ANTHROPIC_BASE_URL=$BASE_URL ANTHROPIC_AUTH_TOKEN=$key ANTHROPIC_MODEL=$MODEL \
        ANTHROPIC_SMALL_FAST_MODEL=${SMALL_MODEL:-$MODEL} CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
        claude -p --setting-sources project --settings "$ROOT/notes/trainee/readonly-settings.json" \
          --allowedTools "Read,Grep,Glob" --disallowedTools "Edit,Write,NotebookEdit,Bash,Agent,WebSearch" \
          --append-system-prompt "$(cat "$ROOT/AGENTS.md")" < "$in" > "$out" 2> "$last" ) || code=$?
    ;;
  *) echo "unknown BACKEND=$BACKEND in $conf" >&2; exit 1;;
esac
echo "$(date '+%F %T') end $brief trainee=$who exit=$code | after: $(quota)" >> "$log"
echo "→ $out (exit $code)"
exit $code
