"""Simulate routing strategies offline from saved results (no new model calls).

Idea: answer cheap cases locally and send only uncertain ones to Claude.
Each strategy decides, per case, whose saved answer to use. Then accuracy,
safety, cost and latency are recalculated as if it had run live.

Usage:
    python src/route.py --small results/qwen4b_v2.jsonl --large results/qwen9b_v1.jsonl \
        --claude results/claude_v1.jsonl --out results/routing_v2.md

Assumptions (stated in the report):
- Local models run one after the other on one machine, so their latencies add.
- An escalated case costs the local time(s) plus Claude's time and Claude's tokens.
- The human-review rule still applies to whichever answer is used (each run's
  own needs_human_review flag, at the 0.70 threshold).
"""

import argparse
import csv
import statistics
from pathlib import Path

from score import p90, score

MAX_CONFIDENT_WRONG = 0.05
MAX_REVIEW_RATE = 0.30


def load(path, price_in, price_out):
    _, rows = score(path, price_in, price_out)
    return {x["id"]: x for x in rows}


def claude_cost(x, price_in, price_out):
    return ((x["input_tokens"] or 0) * price_in + (x["output_tokens"] or 0) * price_out) / 1_000_000


def simulate(name, decide, small, large, claude, price_in, price_out):
    """decide(case_id) -> ('small'|'large'|'claude', local_models_called)"""
    out = []
    for cid in sorted(claude):
        source, locals_used = decide(cid)
        chosen = {"small": small, "large": large, "claude": claude}[source][cid]
        secs = sum({"small": small, "large": large}[m][cid]["total_seconds"] for m in locals_used)
        cost = 0.0
        if source == "claude":
            secs += claude[cid]["total_seconds"]
            cost = claude_cost(claude[cid], price_in, price_out)
        out.append({
            "strategy": name, "id": cid, "answered_by": source,
            "pred": chosen["pred"], "gold": chosen["gold"], "correct": chosen["correct"],
            "confidence": chosen["confidence"], "review": chosen["review"],
            "evidence_recall": chosen["evidence_recall"], "seconds": secs, "cost": cost,
        })
    n = len(out)
    auto = [x for x in out if not x["review"]]
    secs = [x["seconds"] for x in out]
    return {
        "name": name,
        "acc": sum(x["correct"] for x in out) / n,
        "cbw": sum(not x["correct"] for x in auto) / len(auto) if auto else 0.0,
        "review": sum(x["review"] for x in out) / n,
        "to_claude": sum(x["answered_by"] == "claude" for x in out) / n,
        "recall": statistics.mean(x["evidence_recall"] for x in out),
        "lat_med": statistics.median(secs),
        "lat_p90": p90(secs),
        "cost_1000": sum(x["cost"] for x in out) / n * 1000,
        "rows": out,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--small", required=True, help="small local model results (e.g. qwen4b_v2)")
    ap.add_argument("--large", required=True, help="larger local model results (e.g. qwen9b_v1)")
    ap.add_argument("--claude", required=True, help="Claude results")
    ap.add_argument("--thresholds", type=float, nargs="+", default=[0.90, 0.95])
    ap.add_argument("--price-in", type=float, default=2.0)
    ap.add_argument("--price-out", type=float, default=10.0)
    ap.add_argument("--out", help="markdown report")
    ap.add_argument("--csv", help="per-case decisions for every strategy")
    a = ap.parse_args()

    small, large, claude = (load(p, a.price_in, a.price_out) for p in (a.small, a.large, a.claude))
    sname, lname = Path(a.small).stem, Path(a.large).stem
    conf = lambda m, cid: m[cid]["confidence"] if m[cid]["confidence"] is not None else 0.0

    strategies = [
        (f"All {sname} (local only)", lambda c: ("small", ["small"])),
        (f"All {lname} (local only)", lambda c: ("large", ["large"])),
        ("All Claude", lambda c: ("claude", [])),
    ]
    for t in a.thresholds:
        strategies.append((f"{sname}; to Claude if confidence < {t:.2f}",
                           lambda c, t=t: ("small", ["small"]) if conf(small, c) >= t else ("claude", ["small"])))
    strategies.append((f"{sname} + {lname} agree; else Claude",
                       lambda c: ("small", ["small", "large"]) if small[c]["pred"] == large[c]["pred"] else ("claude", ["small", "large"])))
    strategies.append((f"Agree AND {sname} confidence ≥ 0.90; else Claude",
                       lambda c: ("small", ["small", "large"]) if small[c]["pred"] == large[c]["pred"] and conf(small, c) >= 0.90 else ("claude", ["small", "large"])))

    results = [simulate(n, d, small, large, claude, a.price_in, a.price_out) for n, d in strategies]

    pct = lambda v: f"{v:.0%}"
    lines = ["# Routing simulation (offline, from saved results)\n",
             f"Local models: `{sname}` (small), `{lname}` (large). Escalation target: Claude (`{Path(a.claude).stem}`). "
             f"Claude priced at ${a.price_in}/${a.price_out} per M tokens. Local models are £0 marginal cost. "
             "Local latencies add because the models run one after the other on one machine. "
             "The review rule (each run's own 0.70 threshold) applies to whichever answer is used.\n",
             "| Strategy | Accuracy | Confident-but-wrong | Review rate | Sent to Claude | Evidence recall | Latency median / p90 | Cost per 1,000 |",
             "|---|---|---|---|---|---|---|---|"]
    for r in results:
        ok = r["cbw"] <= MAX_CONFIDENT_WRONG and r["review"] <= MAX_REVIEW_RATE
        lines.append(f"| {r['name']} | {pct(r['acc'])} | {r['cbw']:.1%} {'✓' if r['cbw'] <= MAX_CONFIDENT_WRONG else '✗'} | "
                     f"{pct(r['review'])} | {pct(r['to_claude'])} | {pct(r['recall'])} | "
                     f"{r['lat_med']:.1f}s / {r['lat_p90']:.1f}s | ${r['cost_1000']:.2f} |")
    lines.append("\nTargets: confident-but-wrong ≤ 5%, review rate ≤ 30%, accuracy ≥ 85%, evidence recall ≥ 80%.\n")

    lines.append("## Errors that slipped through without review\n")
    for r in results:
        bad = [f"{x['id']} ({x['answered_by']}: {x['pred']} {x['confidence']}, gold {x['gold']})"
               for x in r["rows"] if not x["correct"] and not x["review"]]
        lines.append(f"- **{r['name']}**: {'; '.join(bad) if bad else 'none'}")
    report = "\n".join(lines)
    print(report)
    if a.out:
        Path(a.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nSaved report to {a.out}")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(results[0]["rows"][0].keys()))
            w.writeheader()
            for r in results:
                w.writerows(r["rows"])
        print(f"Saved per-case decisions to {a.csv}")


if __name__ == "__main__":
    main()
