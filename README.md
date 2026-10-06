# Dispute-triage assistant for small merchants

**Problem.** When a small merchant receives a card dispute (chargeback), they often don't know what they're being accused of or which evidence would win, so they accept the loss or submit evidence that doesn't answer the claim. This prototype reads the cardholder's complaint and returns the dispute category, the evidence to submit, and a short explanation that cites the rules, with a human-review flag when it isn't sure.

**Decision:** launch with **Claude plus human review** (98% accuracy, 0 confident errors, under 1p per dispute). **Agreement routing** between two local models matched Claude's accuracy at about 3% of the cost, but misses the evidence target, so it's the scale-up path, not the launch option. → [Decision memo](docs/decision_memo.md)

## Approach

1. **Define success first.** A [PRD](docs/prd.md) with targets set before any model ran: accuracy ≥ 85%, confident-but-wrong ≤ 5%, review rate ≤ 30%, evidence recall ≥ 80%.
2. **Build an eval set.** 80 synthetic disputes, labelled blind by me against a 6-category [taxonomy](docs/categories.md) built from public Visa and Mastercard guidance, with a written [labelling rules log](docs/categories.md#labelling-rules-log).
3. **Build the pipeline.** Retrieve rules (local embeddings) → classify with confidence → recommend evidence from a fixed list → explain with citations → apply the review rule in code.
4. **Compare and iterate.** Claude Sonnet 5.5 against Qwen 3.5 4B and 9B (local), all graded by the same scorer. Then two changes: prompt v2, and routing between models.

## Results

| | Claude | Qwen 4B (v2 prompt) | Qwen 9B (v1 prompt) | **Agreement routing** (4B + 9B, else Claude) | Target |
|---|---|---|---|---|---|
| Category accuracy | **98%** | 96% | 96% | **98%** | ≥ 85% |
| Confident-but-wrong | **0%** | 3.8% | 3.8% | 2.5% | ≤ 5% |
| Evidence recall | **83%** | 69% | 70% | 69% | ≥ 80% |
| Latency median | **2.5s** | 5.3s | 11.7s | 17.7s | |
| Cost per 1,000 cases | $8.57 | £0 | £0 | **$0.29** | |

Full tables: [comparison](results/comparison_v2.md) · [routing](results/routing_v2.md)

**What I learned**

- **Accuracy didn't separate the models; safety did.** All three were 95–98% accurate in the first round, but only Claude's confidence tracked its errors. The local models gave every answer between 0.85 and 0.95 confidence, so a single review threshold caught almost nothing. **Thresholds must be calibrated for each model.**
- **Half of the first-round errors came from a gap in the spec, not the models:** complaints with two claims and no rule for which wins. → [Failure analysis](docs/failure_analysis_v1.md)
- **The same prompt fix helped the 4B and hurt the 9B** (96% → 89%). Kept as a negative result.
- **Two models agreeing is a better signal than one model's confidence.** But two models from the same family share blind spots.

Every decision, including what didn't work, is in the [iteration log](docs/iteration_log.md).

## Limitations

80 synthetic cases (one case = 1.25 points); written by Claude and labelled by one person; 3 labels corrected under written rules after the first runs (original-label results kept). Claude runs at its API default temperature; the Qwen models at 0. Local timings are from one laptop.

## Next steps

Real anonymised merchant disputes (300+, with a held-out set) · fix evidence quality · agreement routing across different model families · pilot metrics: dispute win rate, merchant time saved, human overturn rate.

## Repository

| Path | What |
|---|---|
| `docs/` | PRD, categories and labelling rules, case schema, failure analysis, iteration log, decision memo |
| `data/` | `cases_raw.csv` (generated), `cases_labelled.csv` (gold labels, with an audit trail of every change) |
| `rules/` | `dispute_rules.md`, the knowledge base used for retrieval |
| `src/` | `llm.py` (model wrapper) · `retrieve.py` (embeddings) · `triage.py` (pipeline) · `score.py` · `compare.py` · `route.py` |
| `results/` | Raw outputs (`.jsonl`), run settings (`.meta.jsonl`), scores, comparisons, `run_config.md` |

## Running it

Requires Python 3, LM Studio (local models), and an Anthropic API key in `.env` (see `results/run_config.md`).

```sh
pip install -r requirements.txt
lms load text-embedding-nomic-embed-text-v1.5          # embeddings for retrieval
python src/retrieve.py --check                          # retrieval hit rate
python src/triage.py --model claude --all --out results/claude_run.jsonl
python src/score.py results/claude_run.jsonl --price-in 2 --price-out 10
```

Local Qwen models must be loaded **one at a time**; loading both at once exceeds available memory:

```sh
lms unload --all
lms load <model-id> --context-length 8192               # QWEN_SMALL or QWEN_LARGE from .env
lms load text-embedding-nomic-embed-text-v1.5
```
