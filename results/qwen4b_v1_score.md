# Scores: qwen4b_v1.jsonl
Model: `qwen-small` (qwen3.5-4b) · prompt v1 · 80 cases

## Quality
| Metric | Value | PRD target |
|---|---|---|
| Category accuracy (excl. `unclear`) | 75/79 (95%) | ≥ 85% |
| Raw accuracy (all cases) | 75/80 (94%) | |
| Accuracy, easy | 56/56 (100%) | |
| Accuracy, ambiguous | 19/23 (83%) | |
| Evidence recall | 75% | ≥ 80% |
| Evidence precision | 46% | |
| Review rate | 2/80 (2%) | ≤ 30% |
| Confident-but-wrong rate | 4/78 (5%) | ≤ 5% |
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
| not_received | 11/11 (100%) | 79% |
| processing_error | 17/18 (94%) | 80% |
| refund_not_processed | 11/15 (73%) | 80% |
| subscription_cancelled | 8/8 (100%) | 67% |

## Errors (gold → predicted)
- refund_not_processed → not_as_described: 2  (C044, C065)
- refund_not_processed → subscription_cancelled: 1  (C048)
- processing_error → fraud_unauthorised: 1  (C055)
- refund_not_processed → unclear: 1  (C072)

## Calibration (does confidence match accuracy?)
| Confidence | Cases | Accuracy |
|---|---|---|
| 0.00–0.50 | 0 | – |
| 0.50–0.70 | 0 | – |
| 0.70–0.85 | 0 | – |
| 0.85–0.95 | 38 | 33/38 (87%) |
| 0.95–1.00 | 42 | 42/42 (100%) |

## Review threshold sweep (gap 0.15, retrieval 0.50 held fixed)
| Confidence threshold | Review rate | Confident-but-wrong |
|---|---|---|
| 0.50 | 2/80 (2%) | 4/78 (5%) |
| 0.60 | 2/80 (2%) | 4/78 (5%) |
| 0.70 ← current | 2/80 (2%) | 4/78 (5%) |
| 0.80 | 2/80 (2%) | 4/78 (5%) |
| 0.85 | 2/80 (2%) | 4/78 (5%) |
| 0.90 | 13/80 (16%) | 4/67 (6%) |
| 0.95 | 38/80 (48%) | 0/42 (0%) |

