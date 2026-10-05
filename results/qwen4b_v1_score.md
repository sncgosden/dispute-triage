# Scores: qwen4b_v1.jsonl
Model: `qwen-small` (qwen3.5-4b) · prompt v1 · 80 cases

## Quality
| Metric | Value | PRD target |
|---|---|---|
| Category accuracy (excl. `unclear`) | 74/79 (94%) | ≥ 85% |
| Raw accuracy (all cases) | 74/80 (92%) | |
| Accuracy, easy | 56/56 (100%) | |
| Accuracy, ambiguous | 18/23 (78%) | |
| Evidence recall | 75% | ≥ 80% |
| Evidence precision | 46% | |
| Review rate | 2/80 (2%) | ≤ 30% |
| Confident-but-wrong rate | 5/78 (6%) | ≤ 5% |
| Valid JSON (after retry) | 80/80 (100%) | 100% |
| Valid JSON first try | 77/80 (96%) | |
| Cases with made-up evidence IDs | 0/80 (0%) | |
| Cases citing a section not provided | 0/80 (0%) | |
| Model said `unclear` | 1/80 (1%) | |

## Speed and cost
| Metric | Value |
|---|---|
| Latency median / p90 | 4.5s / 7.1s |
| Time to first token, median | 1.68s |
| Tokens per case, mean in / out | 1955 / 127 |
| Cost per case | £0 marginal (local) |

## By gold category
| Category | Correct | Evidence recall |
|---|---|---|
| fraud_unauthorised | 11/11 (100%) | 62% |
| not_as_described | 17/17 (100%) | 75% |
| not_received | 11/12 (92%) | 81% |
| processing_error | 17/19 (89%) | 77% |
| refund_not_processed | 11/14 (79%) | 83% |
| subscription_cancelled | 7/7 (100%) | 67% |

## Errors (gold → predicted)
- not_received → not_as_described: 1  (C016)
- processing_error → subscription_cancelled: 1  (C030)
- refund_not_processed → not_as_described: 1  (C044)
- refund_not_processed → subscription_cancelled: 1  (C048)
- processing_error → fraud_unauthorised: 1  (C055)
- refund_not_processed → unclear: 1  (C072)

## Calibration (does confidence match accuracy?)
| Confidence | Cases | Accuracy |
|---|---|---|
| 0.00–0.50 | 0 | – |
| 0.50–0.70 | 0 | – |
| 0.70–0.85 | 0 | – |
| 0.85–0.95 | 38 | 32/38 (84%) |
| 0.95–1.00 | 42 | 42/42 (100%) |

## Review threshold sweep (gap 0.15, retrieval 0.50 held fixed)
| Confidence threshold | Review rate | Confident-but-wrong |
|---|---|---|
| 0.50 | 2/80 (2%) | 5/78 (6%) |
| 0.60 | 2/80 (2%) | 5/78 (6%) |
| 0.70 ← current | 2/80 (2%) | 5/78 (6%) |
| 0.80 | 2/80 (2%) | 5/78 (6%) |
| 0.85 | 2/80 (2%) | 5/78 (6%) |
| 0.90 | 13/80 (16%) | 4/67 (6%) |
| 0.95 | 38/80 (48%) | 0/42 (0%) |

