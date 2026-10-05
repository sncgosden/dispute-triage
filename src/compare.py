"""Compare several model runs in one table, using the same scoring code as score.py.

Usage:
    python src/compare.py results/claude_v1.jsonl results/qwen4b_v1.jsonl results/qwen9b_v1.jsonl \
        --out results/comparison_v1.md

Adds two things the single-model report can't show:
- Best review threshold per model: the lowest confidence threshold that meets
  BOTH safety targets (confident-but-wrong <= 5%, review rate <= 30%).
- Error overlap: which cases every model got wrong (likely hard or
  debatable labels) versus errors unique to one model.
"""

import argparse
import statistics
from pathlib import Path

from score import LOCAL_MODELS, p90, review_flags, score

MAX_CONFIDENT_WRONG = 0.05
MAX_REVIEW_RATE = 0.30
CURRENT_THRESHOLD = 0.70


def safety_at(rows, threshold):
    flags = [review_flags(x["_raw"], threshold, 0.15, 0.50) for x in rows]
    auto = [x for x, f in zip(rows, flags) if not f]
    review_rate = sum(flags) / len(rows)
    cbw = sum(not x["correct"] for x in auto) / len(auto) if auto else 0.0
    return review_rate, cbw


def safe_range(rows):
    """All thresholds (0.50-0.99, step 0.01) meeting both targets, as (low, high), or None."""
    ok = []
    for t in [round(0.50 + i / 100, 2) for i in range(50)]:
        review_rate, cbw = safety_at(rows, t)
        if cbw <= MAX_CONFIDENT_WRONG and review_rate <= MAX_REVIEW_RATE:
            ok.append(t)
    return (min(ok), max(ok)) if ok else None


def summarise(path, price_in, price_out):
    _, rows = score(path, price_in, price_out)
    raw = rows[0]["_raw"]
    model = raw["model"]
    decided = [x for x in rows if x["valid"] and not x["said_unclear"]]

    def acc(xs):
        return sum(x["correct"] for x in xs) / len(xs) if xs else float("nan")

    tot = [x["total_seconds"] for x in rows if x["total_seconds"] is not None]
    tin = [x["input_tokens"] for x in rows if x["input_tokens"] is not None]
    tout = [x["output_tokens"] for x in rows if x["output_tokens"] is not None]
    if model in LOCAL_MODELS:
        cost = "£0 (local)"
    elif tin and tout:
        per_case = (statistics.mean(tin) * price_in + statistics.mean(tout) * price_out) / 1_000_000
        cost = f"${per_case * 1000:.2f}"
    else:
        cost = "n/a"
    review_now, cbw_now = safety_at(rows, CURRENT_THRESHOLD)
    return {
        "name": Path(path).stem,
        "model_id": raw["model_id"],
        "n": len(rows),
        "acc": acc(decided),
        "acc_easy": acc([x for x in decided if x["difficulty"] == "easy"]),
        "acc_amb": acc([x for x in decided if x["difficulty"] == "ambiguous"]),
        "recall": statistics.mean(x["evidence_recall"] for x in rows),
        "precision": statistics.mean(x["evidence_precision"] for x in rows),
        "cbw_now": cbw_now,
        "review_now": review_now,
        "safe": safe_range(rows),
        "json_first": sum(x["first_try_valid"] for x in rows) / len(rows),
        "lat_med": statistics.median(tot),
        "lat_p90": p90(tot),
        "cost": cost,
        "wrong": {x["id"] for x in rows if not x["correct"]},
        "rows": rows,
    }


def mark(value, ok):
    return f"{value} ✓" if ok else f"{value} ✗"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results", nargs="+", help=".jsonl results files to compare")
    parser.add_argument("--out", help="save the comparison as markdown")
    parser.add_argument("--price-in", type=float, default=2.0, help="Claude USD per M input tokens (default 2)")
    parser.add_argument("--price-out", type=float, default=10.0, help="Claude USD per M output tokens (default 10)")
    args = parser.parse_args()

    runs = [summarise(p, args.price_in, args.price_out) for p in args.results]
    out = []
    w = out.append
    w("# Model comparison\n")
    w(f"Same 80 cases, prompt, retrieval and scorer for every run. Claude priced at ${args.price_in}/${args.price_out} per M tokens.\n")

    w("## Quality, safety, speed and cost\n")
    w("| Metric | " + " | ".join(r["name"] for r in runs) + " | Target |")
    w("|---|" + "---|" * len(runs) + "---|")
    pct = lambda v: f"{v:.0%}"
    lines = [
        ("Model", lambda r: f"`{r['model_id']}`", ""),
        ("Category accuracy", lambda r: mark(pct(r["acc"]), r["acc"] >= 0.85), "≥ 85%"),
        ("Accuracy, easy / ambiguous", lambda r: f"{pct(r['acc_easy'])} / {pct(r['acc_amb'])}", ""),
        ("Evidence recall", lambda r: mark(pct(r["recall"]), r["recall"] >= 0.80), "≥ 80%"),
        ("Evidence precision", lambda r: pct(r["precision"]), ""),
        (f"Confident-but-wrong @ {CURRENT_THRESHOLD}", lambda r: mark(f"{r['cbw_now']:.1%}", r["cbw_now"] <= MAX_CONFIDENT_WRONG), "≤ 5%"),
        (f"Review rate @ {CURRENT_THRESHOLD}", lambda r: mark(pct(r["review_now"]), r["review_now"] <= MAX_REVIEW_RATE), "≤ 30%"),
        ("Safe threshold range", lambda r: f"{r['safe'][0]:.2f}–{r['safe'][1]:.2f}" if r["safe"] else "none ✗", "meets both"),
        ("…review / confident-but-wrong at top of range", lambda r: "{} / {}".format(*map(pct, safety_at(r["rows"], r["safe"][1]))) if r["safe"] else "–", ""),
        ("Valid JSON first try", lambda r: pct(r["json_first"]), ""),
        ("Latency median / p90", lambda r: f"{r['lat_med']:.1f}s / {r['lat_p90']:.1f}s", ""),
        ("Cost per 1,000 cases", lambda r: r["cost"], ""),
    ]
    for label, fn, target in lines:
        w(f"| {label} | " + " | ".join(fn(r) for r in runs) + f" | {target} |")
    w("")
    w("*Safe threshold range* = every confidence threshold at which confident-but-wrong ≤ 5% AND review rate ≤ 30%. The top of the range is the safest setting that still respects the review cap. Confidence scales differ between models, so one shared threshold is not fair to all of them.\n")

    w("## Error overlap\n")
    all_wrong = set.intersection(*(r["wrong"] for r in runs))
    any_wrong = set.union(*(r["wrong"] for r in runs))
    w(f"- Wrong for **every** model ({len(all_wrong)}): {', '.join(sorted(all_wrong)) or 'none'}. These are likely hard or debatable cases; recheck their labels.")
    for r in runs:
        others = set.union(set(), *(o["wrong"] for o in runs if o is not r))
        only = r["wrong"] - others
        w(f"- Wrong only for {r['name']} ({len(only)}): {', '.join(sorted(only)) or 'none'}")
    w(f"- Wrong for at least one model: {len(any_wrong)} of {runs[0]['n']} cases\n")

    w("| Case | Gold | " + " | ".join(r["name"] for r in runs) + " |")
    w("|---|---|" + "---|" * len(runs))
    by_id = [{x["id"]: x for x in r["rows"]} for r in runs]
    for cid in sorted(any_wrong):
        gold = by_id[0][cid]["gold"]
        cells = []
        for m in by_id:
            x = m.get(cid)
            cells.append("–" if x is None else ("✓" if x["correct"] else f"{x['pred']} ({x['confidence']})"))
        w(f"| {cid} | {gold} | " + " | ".join(cells) + " |")
    w("")

    report = "\n".join(out)
    print(report)
    if args.out:
        Path(args.out).write_text(report + "\n", encoding="utf-8")
        print(f"\nSaved to {args.out}")


if __name__ == "__main__":
    main()
