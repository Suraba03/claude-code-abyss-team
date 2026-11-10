#!/usr/bin/env python3
"""Model-routing ledger: which model:effort gets a task, what it cost, whether it was accepted.

Data lives in <root>/notes/model-ledger/ (JSONL, append-only, private):
  config.json        arms, cost weights, thresholds (created with defaults on first use)
  assignments.jsonl  the lead's choice per task (assign)
  attempts.jsonl     subagent runs read from Claude Code transcripts (scan)
  outcomes.jsonl     the result per task after the owner accepts or rejects it (outcome)

An arm is "model:effort", e.g. "sonnet:max" or "opus:high". Convention: every Agent description starts with the task
ID ("T-12 implement x" or "[T-12] implement x"), and the lane passes the arm's model and effort on the Agent call.

usage:
  ledger.py assign  <task_id> <type> [--risk high]   -> prints the arm (model:effort) and logs it
  ledger.py scan    [--since YYYY-MM-DD]             -> imports this project's subagent runs (tokens, model, effort)
  ledger.py outcome <task_id> --accepted y|n [--review-rounds N] [--owner-min M] [--escaped-defect] [--notes TEXT]
  ledger.py report                                   -> per type x arm: success, cost, recommendation
Root: --root DIR or $LEDGER_ROOT, else the folder above this script's folder.
Transcript format: Claude Code 2.1.x (~/.claude/projects/<encoded path>/<session>/subagents/agent-*.jsonl + .meta.json).
It isn't a documented API, so scan skips files it can't read instead of failing.
"""
import argparse, collections, glob, json, os, random, re, sys, datetime as dt

TYPES = ["diagnosis", "feature", "refactor", "tests", "docs", "research"]
DEFAULTS = {
    "policy": "v1",
    # Few arms: every extra arm needs its own ~20 tasks per type before the numbers mean anything.
    "arms": ["sonnet:high", "sonnet:max", "opus:high"],
    "high_risk_arm": "opus:high",
    # Relative cost per token by model family (API price ratios; update when prices change).
    "weights": {"haiku": 0.33, "sonnet": 1.0, "opus": 1.67, "fable": 5.0},
    "min_per_arm": 20,        # tasks per arm per type before exploiting
    "margin": 0.05,           # a cheaper arm may be up to 5 points worse in success rate...
    "confidence": 0.90,       # ...with this posterior probability...
    "min_saving": 0.20,       # ...and must cost >=20% less per accepted task
    "explore_after": 0.20,    # share of eligible tasks still randomized after a decision
}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def setup(root):
    d = os.path.join(root, "notes", "model-ledger")
    os.makedirs(d, exist_ok=True)
    cfg_path = os.path.join(d, "config.json")
    if not os.path.exists(cfg_path):
        with open(cfg_path, "w") as fh:
            json.dump(DEFAULTS, fh, indent=2)
    cfg = {**DEFAULTS, **json.load(open(cfg_path))}
    P = {k: os.path.join(d, f"{k}.jsonl") for k in ("assignments", "attempts", "outcomes")}
    return P, cfg


def load(p):
    if not os.path.exists(p):
        return []
    with open(p) as fh:
        return [json.loads(l) for l in fh if l.strip()]


def append(p, row):
    with open(p, "a") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def task_id_of(text):
    m = re.match(r"\s*\[?([A-Za-z][A-Za-z0-9]*-\d+[A-Za-z0-9.-]*)\]?[\s:]", (text or "") + " ")
    return m.group(1) if m else None


def family(model):
    m = (model or "").lower()
    return next((f for f in ("haiku", "sonnet", "opus", "fable") if f in m), m)


# ---------- stats ----------
def beta_draws(k, n, size=4000, rng=random.Random(7)):
    return [rng.betavariate(1 + k, 1 + n - k) for _ in range(size)]


def summarize(rows):
    """rows: one per finished task, with type, arm, accepted, cost. -> {(type, arm): stats}"""
    out = {}
    for r in rows:
        s = out.setdefault((r["type"], r["arm"]), {"n": 0, "k": 0, "cost": 0.0})
        s["n"] += 1
        s["k"] += 1 if r["accepted"] else 0
        s["cost"] += r["cost"]
    for s in out.values():
        s["rate"] = (1 + s["k"]) / (2 + s["n"])           # posterior mean, Beta(1,1) prior
        s["cost_per_accepted"] = s["cost"] / s["k"] if s["k"] else None
    return out


def decide(stats, typ, cfg):
    arms = cfg["arms"]
    have = {a: stats.get((typ, a), {"n": 0, "k": 0, "cost_per_accepted": None, "rate": 0.5}) for a in arms}
    short = [f"{a} {have[a]['n']}" for a in arms if have[a]["n"] < cfg["min_per_arm"]]
    if short:
        return None, f"explore: need {cfg['min_per_arm']} tasks per arm (have {', '.join(short)})"
    best = max(arms, key=lambda a: have[a]["rate"])
    draws = {a: beta_draws(have[a]["k"], have[a]["n"]) for a in arms}
    best_cost = have[best]["cost_per_accepted"] or float("inf")
    for a in sorted(arms, key=lambda a: have[a]["cost_per_accepted"] or float("inf")):
        if a == best:
            break
        p_ok = sum(x >= y - cfg["margin"] for x, y in zip(draws[a], draws[best])) / len(draws[a])
        saving = 1 - (have[a]["cost_per_accepted"] or float("inf")) / best_cost
        if p_ok > cfg["confidence"] and saving >= cfg["min_saving"]:
            return a, (f"{a}: P(at most {cfg['margin']:.0%} worse than {best})={p_ok:.2f}, "
                       f"{saving:.0%} cheaper per accepted task")
    return best, f"{best}: best success rate; no cheaper arm is safely close enough"


def joined(P, cfg):
    assigns = {a["task_id"]: a for a in load(P["assignments"])}
    cost = collections.Counter()
    for at in load(P["attempts"]):
        if at.get("task_id"):
            fam = family((at.get("models") or [at.get("requested_model")])[0])
            cost[at["task_id"]] += at.get("tokens_total", 0) * cfg["weights"].get(fam, 1.0)
    rows = []
    for o in load(P["outcomes"]):
        a = assigns.get(o["task_id"])
        if not a or a.get("forced") or a.get("arm") not in cfg["arms"]:
            continue                          # high-risk and retired arms don't count
        rows.append({"type": a["type"], "arm": a["arm"], "accepted": o["accepted_first_time"],
                     "cost": cost.get(o["task_id"], 0.0)})
    return rows


# ---------- commands ----------
def cmd_assign(args, P, cfg):
    if args.type not in TYPES:
        sys.exit(f"type must be one of {TYPES}")
    if any(a["task_id"] == args.task_id for a in load(P["assignments"])):
        sys.exit(f"{args.task_id} already assigned (see assignments.jsonl)")
    arms = cfg["arms"]
    if args.risk == "high":
        arm, prob, why, forced = cfg["high_risk_arm"], 1.0, "high risk: never explore", True
    else:
        forced = False
        best, why = decide(summarize(joined(P, cfg)), args.type, cfg)
        if best is None:                       # explore: balance the arms within the type
            counts = {a: 0 for a in arms}
            for a in load(P["assignments"]):
                if a["type"] == args.type and not a.get("forced") and a.get("arm") in counts:
                    counts[a["arm"]] += 1
            low = min(counts.values())
            cands = [a for a in arms if counts[a] == low]
            arm, prob = random.choice(cands), 1 / len(cands)
        elif random.random() < cfg["explore_after"]:
            arm, prob = random.choice(arms), cfg["explore_after"] / len(arms)
            why += "; exploring"
        else:
            arm, prob = best, 1 - cfg["explore_after"] + cfg["explore_after"] / len(arms)
    model, effort = arm.split(":")
    append(P["assignments"], {"ts": now(), "task_id": args.task_id, "type": args.type, "risk": args.risk,
                              "arm": arm, "model": model, "effort": effort, "probability": round(prob, 3),
                              "forced": forced, "policy": cfg["policy"], "why": why})
    print(arm)
    print(why, file=sys.stderr)


def encoded(path):
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


def cmd_scan(args, P, cfg):
    seen = {a["agent_id"] for a in load(P["attempts"])}
    prefix = encoded(args.root)
    base = os.path.expanduser(os.environ.get("CLAUDE_PROJECTS_DIR", "~/.claude/projects"))
    added = skipped = 0
    for meta in glob.glob(os.path.join(base, prefix + "*", "*", "subagents", "agent-*.meta.json")):
        agent_id = os.path.basename(meta)[len("agent-"):-len(".meta.json")]
        if agent_id in seen:
            continue
        try:
            m = json.load(open(meta))
            if not m.get("finished", True):
                continue                       # still running; pick it up next scan
            usage, models, efforts, stamps = {}, set(), collections.Counter(), []
            for line in open(meta[:-len(".meta.json")] + ".jsonl"):
                r = json.loads(line)
                if r.get("timestamp"):
                    stamps.append(r["timestamp"])
                if r.get("effort"):
                    efforts[str(r["effort"])] += 1
                msg = r.get("message") if isinstance(r.get("message"), dict) else {}
                if msg.get("usage") and msg.get("id"):
                    usage[msg["id"]] = msg["usage"]            # one API message can span rows: keep the last
                    models.add(msg.get("model"))
        except Exception:
            skipped += 1
            continue
        if args.since and stamps and stamps[0][:10] < args.since:
            continue
        t = {k: sum(u.get(k, 0) or 0 for u in usage.values())
             for k in ("input_tokens", "output_tokens", "cache_read_input_tokens", "cache_creation_input_tokens")}
        append(P["attempts"], {
            "agent_id": agent_id, "task_id": task_id_of(m.get("description")), "agent_type": m.get("agentType"),
            "description": m.get("description"), "requested_model": m.get("model"),
            "models": sorted(x for x in models if x and not x.startswith("<")),
            "effort": efforts.most_common(1)[0][0] if efforts else None,
            "started": stamps[0] if stamps else None, "ended": stamps[-1] if stamps else None,
            "api_messages": len(usage), **t,
            # uncached input + output + cache writes; cache reads are cheap and reported separately
            "tokens_total": t["input_tokens"] + t["output_tokens"] + t["cache_creation_input_tokens"],
            "session_dir": os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(meta)))),
        })
        added += 1
    print(f"scan: {added} new subagent runs, {skipped} unreadable")


def cmd_outcome(args, P, cfg):
    if not any(a["task_id"] == args.task_id for a in load(P["assignments"])):
        print(f"warning: {args.task_id} has no assignment; it won't count in the comparison", file=sys.stderr)
    append(P["outcomes"], {"ts": now(), "task_id": args.task_id, "accepted_first_time": args.accepted == "y",
                           "review_rounds": args.review_rounds, "owner_minutes": args.owner_min,
                           "escaped_defect": args.escaped_defect, "notes": args.notes})
    print("ok")


def cmd_report(args, P, cfg):
    stats = summarize(joined(P, cfg))
    print(f"{'type':<10} {'arm':<12} {'n':>3} {'acc':>4} {'rate':>5} {'cost/accepted':>14}")
    for (typ, arm), s in sorted(stats.items()):
        cpa = f"{s['cost_per_accepted']:,.0f}" if s["cost_per_accepted"] else "-"
        print(f"{typ:<10} {arm:<12} {s['n']:>3} {s['k']:>4} {s['rate']:>5.2f} {cpa:>14}")
    print("\n(cost = tokens × model weight from config.json; cache reads not counted)\n")
    for typ in TYPES:
        if any(t == typ for t, _ in stats):
            print(f"{typ}: {decide(stats, typ, cfg)[1]}")
    # Did lanes run what was assigned?
    assigned = {a["task_id"]: a for a in load(P["assignments"])}
    mismatch = []
    for at in load(P["attempts"]):
        a = assigned.get(at.get("task_id"))
        if a and at.get("agent_type") == "implementer":
            ran = family((at.get("models") or [""])[0])
            if ran and ran != a["model"] or (at.get("effort") and at["effort"] != a["effort"]):
                mismatch.append(f"{at['task_id']}: assigned {a['arm']}, ran {ran}:{at.get('effort')}")
    if mismatch:
        print("\nAssigned vs actual differ (check the lane passed model and effort):\n  " + "\n  ".join(mismatch))
    defects = [o for o in load(P["outcomes"]) if o.get("escaped_defect")]
    if defects:
        print(f"\n{len(defects)} escaped defect(s): review the routing rule for those types before trusting it.")
    unlinked = sum(1 for a in load(P["attempts"]) if not a.get("task_id"))
    if unlinked:
        print(f"\n{unlinked} subagent runs without a task ID at the start of the description (not counted).")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.environ.get("LEDGER_ROOT",
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("assign"); a.add_argument("task_id"); a.add_argument("type")
    a.add_argument("--risk", choices=["normal", "high"], default="normal")
    s = sub.add_parser("scan"); s.add_argument("--since")
    o = sub.add_parser("outcome"); o.add_argument("task_id"); o.add_argument("--accepted", choices=["y", "n"], required=True)
    o.add_argument("--review-rounds", type=int); o.add_argument("--owner-min", type=float)
    o.add_argument("--escaped-defect", action="store_true"); o.add_argument("--notes")
    sub.add_parser("report")
    args = ap.parse_args()
    P, cfg = setup(args.root)
    {"assign": cmd_assign, "scan": cmd_scan, "outcome": cmd_outcome, "report": cmd_report}[args.cmd](args, P, cfg)


if __name__ == "__main__":
    main()
