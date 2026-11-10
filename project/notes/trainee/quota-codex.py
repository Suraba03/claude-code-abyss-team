#!/usr/bin/env python3
"""Codex quota from the newest session log: weekly (and 5-hour, if any) usage, reset time, tokens of that run.
usage: python3 notes/trainee/quota-codex.py [--line]   (--line: one line for runs.log)"""
import glob, json, os, sys, datetime as dt

files = sorted(glob.glob(os.path.expanduser("~/.codex/sessions/**/*.jsonl"), recursive=True), key=os.path.getmtime)
last = None
for f in reversed(files[-20:]):
    with open(f) as fh:
        for line in fh:
            if '"token_count"' in line and '"rate_limits"' in line:
                last = (f, json.loads(line)["payload"])
    if last: break
if not last:
    sys.exit("no Codex quota data yet")
f, p = last
rl, info = p.get("rate_limits") or {}, p.get("info") or {}

def win(w):
    if not w: return None
    mins = w.get("window_minutes")
    name = "week" if mins == 10080 else "5h" if mins == 300 else f"{mins}min"
    reset = dt.datetime.fromtimestamp(w["resets_at"]).strftime("%d.%m %H:%M") if w.get("resets_at") else "?"
    return f"{name}: {w.get('used_percent', 0):.0f}% used, {100 - w.get('used_percent', 0):.0f}% left, resets {reset}"

parts = [x for x in (win(rl.get("primary")), win(rl.get("secondary"))) if x]
tot = (info.get("total_token_usage") or {})
run = f"last run {tot.get('total_tokens', 0)/1000:.0f}k tokens ({tot.get('cached_input_tokens', 0)/1000:.0f}k cached)"
plan = rl.get("plan_type", "?")
if rl.get("rate_limit_reached_type"): parts.append(f"LIMIT REACHED: {rl['rate_limit_reached_type']}")
print(("Codex " if "--line" in sys.argv else f"Codex quota (plan {plan})\n  ") + ("; " if "--line" in sys.argv else "\n  ").join(parts + [run]))
