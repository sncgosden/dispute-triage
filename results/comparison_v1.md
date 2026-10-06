# Model comparison

Same 80 cases, retrieval and scorer for every run (the prompt version is in each run name). Claude priced at $2.0/$10.0 per M tokens.

## Quality, safety, speed and cost

| Metric | claude_v1 | qwen4b_v1 | qwen9b_v1 | Target |
|---|---|---|---|---|
| Model | `claude-sonnet-5-5` | `qwen3.5-4b` | `qwen3.5-9b-mlx` |  |
| Category accuracy | 98% ✓ | 95% ✓ | 96% ✓ | ≥ 85% |
| Accuracy, easy / ambiguous | 100% / 92% | 100% / 83% | 98% / 92% |  |
| Evidence recall | 83% ✓ | 75% ✗ | 70% ✗ | ≥ 80% |
| Evidence precision | 50% | 46% | 41% |  |
| Confident-but-wrong @ 0.7 | 0.0% ✓ | 5.1% ✗ | 3.8% ✓ | ≤ 5% |
| Review rate @ 0.7 | 14% ✓ | 2% ✓ | 1% ✓ | ≤ 30% |
| Safe threshold range | 0.50–0.87 | none ✗ | 0.50–0.95 | meets both |
| …review / confident-but-wrong at top of range | 30% / 0% | – | 19% / 2% |  |
| Valid JSON first try | 99% | 96% | 100% |  |
| Latency median / p90 | 2.5s / 6.3s | 4.5s / 7.1s | 11.7s / 17.4s |  |
| Cost per 1,000 cases | $8.57 | £0 (local) | £0 (local) |  |

*Safe threshold range* = every confidence threshold at which confident-but-wrong ≤ 5% AND review rate ≤ 30%. The top of the range is the safest setting that still respects the review cap. Confidence scales differ between models, so one shared threshold is not fair to all of them.

## Error overlap

- Wrong for **every** model (0): none. These are likely hard or debatable cases; recheck their labels.
- Wrong only for claude_v1 (1): C016
- Wrong only for qwen4b_v1 (3): C044, C065, C072
- Wrong only for qwen9b_v1 (2): C047, C056
- Wrong for at least one model: 8 of 80 cases

| Case | Gold | claude_v1 | qwen4b_v1 | qwen9b_v1 |
|---|---|---|---|---|
| C016 | not_as_described | refund_not_processed (0.55) | ✓ | ✓ |
| C044 | refund_not_processed | ✓ | not_as_described (0.92) | ✓ |
| C047 | not_as_described | ✓ | ✓ | refund_not_processed (0.85) |
| C048 | refund_not_processed | ✓ | subscription_cancelled (0.92) | subscription_cancelled (0.95) |
| C055 | processing_error | fraud_unauthorised (0.62) | fraud_unauthorised (0.92) | ✓ |
| C056 | not_as_described | ✓ | ✓ | subscription_cancelled (0.85) |
| C065 | refund_not_processed | ✓ | not_as_described (0.92) | ✓ |
| C072 | refund_not_processed | ✓ | unclear (0.85) | ✓ |

