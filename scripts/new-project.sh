#!/usr/bin/env bash
# Create a lead + two-lane project from this template.
#
# usage: scripts/new-project.sh <name> [--remote <git-url>] [--dir <parent>] [--ports <base>] [--branch <main>]
#                               [--names <lead>,<lane1>,<lane2>]
#   <name>      project name: letters, digits, _ or - (folder and checkout prefix)
#   --remote    clone this repo into the first lane's folder (else a new local repo with one empty commit)
#   --dir       parent folder (default: $HOME/vibe)
#   --ports     port offset for lane 1; lane 2 gets base+100 (default 0). Give each project its own range.
#   --branch    default branch (default: main; detected from the remote when cloning)
#   --names     role names (default: riko,regu,nanachi — the lead and the two lanes)
#
# Result:
#   <dir>/<name>/                 CLAUDE.md, AGENTS.md, notes/, scripts/   (lead's folder, not in git)
#   <dir>/<name>/<name>_<lane1>/  lane 1: the main checkout
#   <dir>/<name>/<name>_<lane2>/  lane 2: a git worktree (detached at the default branch)
set -euo pipefail

TEMPLATE=$(cd "$(dirname "$0")/.." && pwd)
name=${1:-}; shift || true
[[ $name =~ ^[A-Za-z0-9_-]+$ ]] || { sed -n '2,12p' "$0"; exit 1; }
remote=""; parent="$HOME/vibe"; base=0; branch=""; names="riko,regu,nanachi"
while [[ $# -gt 0 ]]; do
  case $1 in
    --remote) remote=$2; shift 2;;
    --dir) parent=$2; shift 2;;
    --ports) base=$2; shift 2;;
    --branch) branch=$2; shift 2;;
    --names) names=$2; shift 2;;
    *) echo "unknown option $1" >&2; exit 1;;
  esac
done
IFS=, read -r lead lane1 lane2 <<< "$names"
for n in "$lead" "$lane1" "$lane2"; do [[ $n =~ ^[a-z0-9]+$ ]] || { echo "--names: lowercase letters/digits, 3 names" >&2; exit 1; }; done
cap() { echo "$(echo "${1:0:1}" | tr '[:lower:]' '[:upper:]')${1:1}"; }
root="$parent/$name"
[[ -e $root ]] && { echo "$root already exists" >&2; exit 1; }
port_1=$base; port_2=$((base + 100))
port_var="$(echo "$name" | tr '[:lower:]-' '[:upper:]_')_PORT_OFFSET"
dir1="$root/${name}_${lane1}"; dir2="$root/${name}_${lane2}"

echo "→ $root"
mkdir -p "$root"
cp -R "$TEMPLATE/project/." "$root/"
mkdir -p "$root/scripts" && cp "$TEMPLATE/scripts/test-summary.sh" "$TEMPLATE/scripts/ledger.py" "$root/scripts/"
find "$root/notes" -name .gitkeep -delete

# Fill placeholders in every text file we copied. __PROJECT__ first: "__PROJECT_____LANE1__" → "<name>_<lane1>".
while IFS= read -r -d '' f; do
  sed -i.bak -e "s#__PROJECT__#$name#g" -e "s#__ROOT__#$root#g" \
    -e "s#__LEAD_CAP__#$(cap "$lead")#g" -e "s#__LANE1_CAP__#$(cap "$lane1")#g" -e "s#__LANE2_CAP__#$(cap "$lane2")#g" \
    -e "s#__LEAD__#$lead#g" -e "s#__LANE1__#$lane1#g" -e "s#__LANE2__#$lane2#g" \
    -e "s#__PORT_A__#$port_1#g" -e "s#__PORT_B__#$port_2#g" -e "s#__PORT_VAR__#$port_var#g" "$f" && rm -f "$f.bak"
done < <(find "$root" -type f \( -name '*.md' -o -name '*.sh' -o -name '*.example' -o -name '*.py' -o -name '*.conf' \) -print0)

# Lane 1: clone or init.
if [[ -n $remote ]]; then
  git clone "$remote" "$dir1"
  [[ -z $branch ]] && branch=$(git -C "$dir1" symbolic-ref --short HEAD)
else
  branch=${branch:-main}
  git init -q -b "$branch" "$dir1"
  git -C "$dir1" commit -q --allow-empty -m "Initial commit"
fi

# Lane 2: a permanent worktree, detached so both lanes can branch freely.
git -C "$dir1" worktree add -q --detach "$dir2" "$branch"

for d in "$dir1" "$dir2"; do
  port=$port_1; [[ $d == "$dir2" ]] && port=$port_2
  mkdir -p "$d/.claude" "$d/docs"
  ln -s ../../notes/superpowers "$d/docs/superpowers"
  # Lanes: Sonnet with an Opus advisor (see notes/model-routing.md). The owner can change it with /model, /advisor.
  cat > "$d/.claude/settings.local.json" <<JSON
{
  "model": "sonnet",
  "advisorModel": "opus",
  "permissions": { "additionalDirectories": ["$root/notes"] },
  "env": { "$port_var": "$port" }
}
JSON
  # Keep local-only files out of git without touching the repo's .gitignore.
  exclude="$(git -C "$d" rev-parse --git-common-dir)/info/exclude"
  mkdir -p "$(dirname "$exclude")"
  for p in docs/superpowers .superpowers/ CLAUDE.md .claude/settings.local.json; do
    grep -qxF "$p" "$exclude" 2>/dev/null || echo "$p" >> "$exclude"
  done
done

L=$(cap "$lead"); A=$(cap "$lane1"); B=$(cap "$lane2")
cat <<EOF

Done. Team: $L (lead) in $root, $A in $dir1, $B in $dir2.
Next steps:
1. Subagents (once per machine, if you don't have them yet):
     mkdir -p ~/.claude/agents && cp -n "$TEMPLATE"/agents/*.md ~/.claude/agents/
2. Optional hook that blocks edits to protected paths, per checkout: see $TEMPLATE/hooks/
3. Trainees (optional): notes/trainee/trainees/*.conf
     codex:    cp "$root/notes/trainee/codex.config.toml.example" ~/.codex/${name}-research.config.toml  # set the model
     deepseek: export DEEPSEEK_API_KEY=…   glm: export GLM_API_KEY=…   (check base URLs in the .conf files)
4. Fill in CLAUDE.md: "Never commit" and "Product rules" (<…> placeholders), and AGENTS.md private paths.
5. Start three sessions (one terminal tab each):
     cd "$root" && claude --model opus     # $L: paste $TEMPLATE/prompts/lead-kickoff.md
     cd "$dir1" && claude                  # $A: paste $TEMPLATE/prompts/lane-kickoff.md
     cd "$dir2" && claude                  # $B: same
Ports: $A offset $port_1, $B offset $port_2 (\$$port_var).
EOF
