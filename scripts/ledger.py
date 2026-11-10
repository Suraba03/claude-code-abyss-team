#!/usr/bin/env python3
"""Model-routing ledger: which model gets a task, what it cost, whether it was accepted.

Data lives in <root>/notes/model-ledger/ (JSONL, append-only):
  assignments.jsonl  the lead's choice per task (assign)
  attempts.jsonl     subagent runs read from Claude Code transcripts (scan)
  outcomes.jsonl     the result per task after the owner accepts or rejects it (outcome)

Convention: every Agent description starts with the task ID, e.g. "T-12 implement x" or "[T-12] implement x".

usage:
  ledger.py assign  <task_id> <type> [--risk high]       -> prints sonnet|opus and logs it
  ledger.py scan    [--since YYYY-MM-DD]                 -> imports subagent runs of this project
  ledger.py outcome <task_id> --accepted y|n [--review-rounds N] [--owner-min M] [--escaped-defect] [--notes TEXT]
  ledger.py report                                       -> per type x model: success, usage, recommendation
Root: --root DIR or $LEDGER_ROOT, else the folder above this script's folder.
Transcript format: Claude Code 2.1.x (~/.claude/projects/<encoded path>/<session>/subagents/agent-*.jsonl + .meta.json);
it isn't a documented API, so scan skips files it can't read instead of failing.
"""
import argparse, glob, json, os, random, re, sys, datetime as dt

TYPES = ["diagnosis", "feature", "refactor", "tests", "docs", "research"]
ARMS = ["sonnet", "opus"]
POLICY = "v1"
MIN_PER_ARM = 20          # tasks per arm per type before exploiting
MARGIN = 0.05             # Sonnet may be up to 5 points worse in success rate...
CONFIDENCE = 0.90         # ...with this posterior probability
MIN_SAVING = 0.20         # ...and must use >=20% fewer tokens per accepted task
EXPLORE_AFTER = 0.20      # share of eligible tasks still randomized after a decision


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def paths(root):
    d = os.path.join(root, "notes", "model-ledger")
    os.makedirs(d, exist_ok=True)
    return {k: os.path.join(d, f"{k}.jsonl") for k in ("assignments", "attempts", "outcomes")}


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


# ---------- stats ----------
def beta_draws(k, n, size=4000, rng=random.Random(7)):
    return [rng.betavariate(1 + k, 1 + n - k) for _ in range(size)]


def summarize(rows):
    """rows: outcome rows joined with assignment model. -> {(type, model): stats}"""
    out = {}
    for r in rows:
        key = (r["type"], r["model"])
        s = out.setdefault(key, {"n": 0, "k": 0, "tokens": 0, "accepted_tokens": 0})
        s["n"] += 1
        s["k"] += 1 if r["accepted"] else 0
        s["tokens"] += r.get("tokens", 0)
    for s in out.values():
        s["rate"] = (1 + s["k"]) / (2 + s["n"])           # posterior mean, Beta(1,1) prior
        s["tokens_per_accepted"] = s["tokens"] / s["k"] if s["k"] else None
    return out


def decide(stats, typ):
    s, o = stats.get((typ, "sonnet")), stats.get((typ, "opus"))
    if not s or not o or s["n"] < MIN_PER_ARM or o["n"] < MIN_PER_ARM:
        return None, "explore: need %d tasks per arm (have sonnet %d, opus %d)" % (
            MIN_PER_ARM, s["n"] if s else 0, o["n"] if o else 0)
    ps, po = beta_draws(s["k"], s["n"]), beta_draws(o["k"], o["n"])
    p_ok = sum(a >= b - MARGIN for a, b in zip(ps, po)) / len(ps)
    tps, tpo = s["tokens_per_accepted"], o["tokens_per_accepted"]
    saving = (1 - tps / tpo) if tps and tpo else 0
    if p_ok > CONFIDENCE and saving >= MIN_SAVING:
        return "sonnet", f"sonnet: P(not worse by >{MARGIN:.0%})={p_ok:.2f}, {saving:.0%} fewer tokens/accepted"
    return "opus", f"opus: P(sonnet not worse)={p_ok:.2f}, saving {saving:.0%} (needs >{CONFIDENCE} and >={MIN_SAVING:.0%})"


def joined(P):
    assigns = {a["task_id"]: a for a in load(P["assignments"])}
    tokens = {}
    for at in load(P["attempts"]):
        if at.get("task_id"):
            tokens[at["task_id"]] = tokens.get(at["task_id"], 0) + at.get("tokens_total", 0)
    rows = []
    for o in load(P["outcomes"]):
        a = assigns.get(o["task_id"])
        if not a or a.get("forced"):          # forced (high-risk) tasks don't count toward the comparison
            continue
        rows.append({"type": a["type"], "model": a["model"], "accepted": o["accepted_first_time"],
                     "tokens": tokens.get(o["task_id"], 0)})
    return rows


# ---------- commands ----------
def cmd_assign(args, P):
    if args.type not in TYPES:
        sys.exit(f"type must be one of {TYPES}")
    if any(a["task_id"] == args.task_id for a in load(P["assignments"])):
        sys.exit(f"{args.task_id} already assigned (see assignments.jsonl)")
    if args.risk == "high":
        model, prob, why, forced = "opus", 1.0, "high risk: never explore", True
    else:
        forced = False
        best, why = decide(summarize(joined(P)), args.type)
        if best is None:                       # explore: balance the arms within the type
            counts = {m: 0 for m in ARMS}
            for a in load(P["assignments"]):
                if a["type"] == args.type and not a.get("forced"):
                    counts[a["model"]] += 1
            low = min(counts.values())
            cands = [m for m in ARMS if counts[m] == low]
            model, prob = random.choice(cands), 1 / len(cands)
        elif random.random() < EXPLORE_AFTER:
            model, prob = random.choice(ARMS), EXPLORE_AFTER / 2
            why += "; exploring"
        else:
            model, prob = best, 1 - EXPLORE_AFTER / 2
    append(P["assignments"], {"ts": now(), "task_id": args.task_id, "type": args.type, "risk": args.risk,
                              "model": model, "probability": prob, "forced": forced, "policy": POLICY, "why": why})
    print(model)
    print(why, file=sys.stderr)


def encoded(path):
    return re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(path))


def cmd_scan(args, P):
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
            usage, models, stamps = {}, set(), []
            for line in open(meta[:-len(".meta.json")] + ".jsonl"):
                r = json.loads(line)
                if r.get("timestamp"):
                    stamps.append(r["timestamp"])
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
            "models": sorted(x for x in models if x and not x.startswith("<")), "started": stamps[0] if stamps else None,
            "ended": stamps[-1] if stamps else None, "api_messages": len(usage), **t,
            # uncached input + output + cache writes; cache reads are cheap and reported separately
            "tokens_total": t["input_tokens"] + t["output_tokens"] + t["cache_creation_input_tokens"],
            "session_dir": os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(meta)))),
        })
        added += 1
    print(f"scan: {added} new subagent runs, {skipped} unreadable")


def cmd_outcome(args, P):
    if not any(a["task_id"] == args.task_id for a in load(P["assignments"])):
        print(f"warning: {args.task_id} has no assignment; it won't count in the comparison", file=sys.stderr)
    append(P["outcomes"], {"ts": now(), "task_id": args.task_id, "accepted_first_time": args.accepted == "y",
                           "review_rounds": args.review_rounds, "owner_minutes": args.owner_min,
                           "escaped_defect": args.escaped_defect, "notes": args.notes})
    print("ok")


def cmd_report(args, P):
    stats = summarize(joined(P))
    print(f"{'type':<10} {'model':<7} {'n':>3} {'acc':>4} {'rate':>5} {'tok/accepted':>13}")
    for (typ, model), s in sorted(stats.items()):
        tpa = f"{s['tokens_per_accepted']:,.0f}" if s["tokens_per_accepted"] else "-"
        print(f"{typ:<10} {model:<7} {s['n']:>3} {s['k']:>4} {s['rate']:>5.2f} {tpa:>13}")
    print()
    for typ in TYPES:
        if any(t == typ for t, _ in stats):
            print(f"{typ}: {decide(stats, typ)[1]}")
    defects = [o for o in load(P["outcomes"]) if o.get("escaped_defect")]
    if defects:
        print(f"\n{len(defects)} escaped defect(s): review the routing rule for those types before trusting it.")
    unlinked = sum(1 for a in load(P["attempts"]) if not a.get("task_id"))
    if unlinked:
        print(f"\n{unlinked} subagent runs without a [task ID] in the description (not counted).")


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
    P = paths(args.root)
    {"assign": cmd_assign, "scan": cmd_scan, "outcome": cmd_outcome, "report": cmd_report}[args.cmd](args, P)


if __name__ == "__main__":
    main()
