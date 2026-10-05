# Model comparison

Same 80 cases, prompt, retrieval and scorer for every run. Claude priced at $2.0/$10.0 per M tokens.

## Quality, safety, speed and cost

| Metric | claude_v1 | qwen4b_v1 | qwen9b_v1 | qwen4b_v2 | qwen9b_v2 | Target |
|---|---|---|---|---|---|---|
| Model | `claude-sonnet-5-5` | `qwen3.5-4b` | `qwen3.5-9b-mlx` | `qwen3.5-4b` | `qwen3.5-9b-mlx` |  |
| Category accuracy | 98% ✓ | 95% ✓ | 96% ✓ | 96% ✓ | 89% ✓ | ≥ 85% |
| Accuracy, easy / ambiguous | 100% / 92% | 100% / 83% | 98% / 92% | 100% / 88% | 95% / 75% |  |
| Evidence recall | 83% ✓ | 75% ✗ | 70% ✗ | 69% ✗ | 66% ✗ | ≥ 80% |
| Evidence precision | 50% | 46% | 41% | 47% | 38% |  |
| Confident-but-wrong @ 0.7 | 0.0% ✓ | 5.1% ✗ | 3.8% ✓ | 3.8% ✓ | 9.2% ✗ | ≤ 5% |
| Review rate @ 0.7 | 14% ✓ | 2% ✓ | 1% ✓ | 0% ✓ | 5% ✓ | ≤ 30% |
| Safe threshold range | 0.50–0.87 | none ✗ | 0.50–0.95 | 0.50–0.90 | 0.86–0.95 | meets both |
| …review / confident-but-wrong at top of range | 30% / 0% | – | 19% / 2% | 12% / 4% | 25% / 2% |  |
| Valid JSON first try | 99% | 96% | 100% | 94% | 100% |  |
| Latency median / p90 | 2.5s / 6.3s | 4.5s / 7.1s | 11.7s / 17.4s | 5.3s / 8.2s | 9.3s / 13.2s |  |
| Cost per 1,000 cases | $8.57 | £0 (local) | £0 (local) | £0 (local) | £0 (local) |  |

*Safe threshold range* = every confidence threshold at which confident-but-wrong ≤ 5% AND review rate ≤ 30%. The top of the range is the safest setting that still respects the review cap. Confidence scales differ between models, so one shared threshold is not fair to all of them.

## Error overlap

- Wrong for **every** model (0): none. These are likely hard or debatable cases; recheck their labels.
- Wrong only for claude_v1 (0): none
- Wrong only for qwen4b_v1 (2): C065, C072
- Wrong only for qwen9b_v1 (0): none
- Wrong only for qwen4b_v2 (0): none
- Wrong only for qwen9b_v2 (4): C027, C046, C050, C053
- Wrong for at least one model: 12 of 80 cases

| Case | Gold | claude_v1 | qwen4b_v1 | qwen9b_v1 | qwen4b_v2 | qwen9b_v2 |
|---|---|---|---|---|---|---|
| C016 | not_as_described | refund_not_processed (0.55) | ✓ | ✓ | ✓ | refund_not_processed (0.85) |
| C027 | subscription_cancelled | ✓ | ✓ | ✓ | ✓ | refund_not_processed (0.75) |
| C044 | refund_not_processed | ✓ | not_as_described (0.92) | ✓ | not_as_described (0.9) | ✓ |
| C046 | not_received | ✓ | ✓ | ✓ | ✓ | refund_not_processed (0.85) |
| C047 | not_as_described | ✓ | ✓ | refund_not_processed (0.85) | ✓ | refund_not_processed (0.85) |
| C048 | refund_not_processed | ✓ | subscription_cancelled (0.92) | subscription_cancelled (0.95) | subscription_cancelled (0.95) | subscription_cancelled (0.95) |
| C050 | processing_error | ✓ | ✓ | ✓ | ✓ | refund_not_processed (0.85) |
| C053 | processing_error | ✓ | ✓ | ✓ | ✓ | subscription_cancelled (0.85) |
| C055 | processing_error | fraud_unauthorised (0.62) | fraud_unauthorised (0.92) | ✓ | ✓ | subscription_cancelled (0.85) |
| C056 | not_as_described | ✓ | ✓ | subscription_cancelled (0.85) | subscription_cancelled (0.9) | subscription_cancelled (0.85) |
| C065 | refund_not_processed | ✓ | not_as_described (0.92) | ✓ | ✓ | ✓ |
| C072 | refund_not_processed | ✓ | unclear (0.85) | ✓ | ✓ | ✓ |

