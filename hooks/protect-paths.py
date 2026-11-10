#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write/NotebookEdit on protected paths.

Patterns: one glob per line in <project>/.claude/protected-paths (fnmatch, relative to the project dir; '#' comments).
Blocked edits exit 2 with a reason on stderr, which Claude Code shows to the agent.
Shell writes (Bash) are not covered: keep permissions and CI diff review as the backstop.
"""
import fnmatch, json, os, sys

try:
    event = json.load(sys.stdin)
except Exception:
    sys.exit(0)  # never break the session on a malformed event
inp = event.get("tool_input") or {}
path = inp.get("file_path") or inp.get("notebook_path")
if not path:
    sys.exit(0)
project = os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()
listfile = os.path.join(project, ".claude", "protected-paths")
if not os.path.isfile(listfile):
    sys.exit(0)
rel = os.path.relpath(os.path.abspath(path), os.path.abspath(project))
with open(listfile) as fh:
    patterns = [l.strip() for l in fh if l.strip() and not l.startswith("#")]
for pat in patterns:
    if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
        print(f"Blocked: {rel} is protected ({pat} in .claude/protected-paths). "
              "Ask the lead or the owner; don't work around this with shell writes.", file=sys.stderr)
        sys.exit(2)
sys.exit(0)
