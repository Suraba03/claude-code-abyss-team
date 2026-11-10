#!/usr/bin/env bash
# Create a lead + two-lane project from this template.
#
# usage: scripts/new-project.sh <name> [--remote <git-url>] [--dir <parent>] [--ports <base>] [--branch <main>]
#   <name>      project name: letters, digits, _ or - (folder and checkout prefix)
#   --remote    clone this repo into <name>_a (else a new local repo with one empty commit)
#   --dir       parent folder (default: $HOME/vibe)
#   --ports     port offset for lane A; lane B gets base+100 (default 0). Give each project its own range.
#   --branch    default branch (default: main; detected from the remote when cloning)
#
# Result:
#   <dir>/<name>/            CLAUDE.md, AGENTS.md, notes/, scripts/   (not in git)
#   <dir>/<name>/<name>_a/   lane A: the main checkout
#   <dir>/<name>/<name>_b/   lane B: a git worktree (detached at the default branch)
set -euo pipefail

TEMPLATE=$(cd "$(dirname "$0")/.." && pwd)
name=${1:-}; shift || true
[[ $name =~ ^[A-Za-z0-9_-]+$ ]] || { sed -n '2,10p' "$0"; exit 1; }
remote=""; parent="$HOME/vibe"; base=0; branch=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --remote) remote=$2; shift 2;;
    --dir) parent=$2; shift 2;;
    --ports) base=$2; shift 2;;
    --branch) branch=$2; shift 2;;
    *) echo "unknown option $1" >&2; exit 1;;
  esac
done
root="$parent/$name"
[[ -e $root ]] && { echo "$root already exists" >&2; exit 1; }
port_a=$base; port_b=$((base + 100))
port_var="$(echo "$name" | tr '[:lower:]-' '[:upper:]_')_PORT_OFFSET"
a="$root/${name}_a"; b="$root/${name}_b"

echo "→ $root"
mkdir -p "$root"
cp -R "$TEMPLATE/project/." "$root/"
mkdir -p "$root/scripts" && cp "$TEMPLATE/scripts/test-summary.sh" "$TEMPLATE/scripts/ledger.py" "$root/scripts/"
find "$root/notes" -name .gitkeep -delete

# Fill placeholders in every text file we copied.
while IFS= read -r -d '' f; do
  sed -i.bak -e "s#__PROJECT__#$name#g" -e "s#__ROOT__#$root#g" -e "s#__PORT_A__#$port_a#g" \
             -e "s#__PORT_B__#$port_b#g" -e "s#__PORT_VAR__#$port_var#g" "$f" && rm -f "$f.bak"
done < <(find "$root" -type f \( -name '*.md' -o -name '*.sh' -o -name '*.example' -o -name '*.py' \) -print0)

# Lane A: clone or init.
if [[ -n $remote ]]; then
  git clone "$remote" "$a"
  [[ -z $branch ]] && branch=$(git -C "$a" symbolic-ref --short HEAD)
else
  branch=${branch:-main}
  git init -q -b "$branch" "$a"
  git -C "$a" commit -q --allow-empty -m "Initial commit"
fi

# Lane B: a permanent worktree, detached so both lanes can branch freely.
git -C "$a" worktree add -q --detach "$b" "$branch"

for lane in a b; do
  dir="${root}/${name}_${lane}"; port=$port_a; [[ $lane == b ]] && port=$port_b
  mkdir -p "$dir/.claude" "$dir/docs"
  ln -s ../../notes/superpowers "$dir/docs/superpowers"
  cat > "$dir/.claude/settings.local.json" <<JSON
{
  "permissions": { "additionalDirectories": ["$root/notes"] },
  "env": { "$port_var": "$port" }
}
JSON
  # Keep local-only files out of git without touching the repo's .gitignore.
  exclude="$(git -C "$dir" rev-parse --git-common-dir)/info/exclude"
  mkdir -p "$(dirname "$exclude")"
  for p in docs/superpowers .superpowers/ CLAUDE.md .claude/settings.local.json; do
    grep -qxF "$p" "$exclude" 2>/dev/null || echo "$p" >> "$exclude"
  done
done

cat <<EOF

Done. Next steps:
1. Subagents (once per machine, if you don't have them yet):
     mkdir -p ~/.claude/agents && cp -n "$TEMPLATE"/agents/*.md ~/.claude/agents/
2. Optional hook that blocks edits to protected paths, per checkout:
     see $TEMPLATE/hooks/ (settings.example.json, protected-paths.example)
3. Codex research profile (optional):
     cp "$root/notes/codex/research.config.toml.example" ~/.codex/${name}-research.config.toml   # then set the model
4. Fill in CLAUDE.md: "Never commit" and "Product rules" (<…> placeholders), and AGENTS.md private paths.
5. Start three sessions (one terminal tab each):
     cd "$root" && claude          # lead: paste $TEMPLATE/prompts/lead-kickoff.md
     cd "$a" && claude             # lane A: paste $TEMPLATE/prompts/lane-kickoff.md
     cd "$b" && claude             # lane B: same
Ports: lane A offset $port_a, lane B offset $port_b (\$$port_var).
EOF
