# Scores: qwen9b_v1.jsonl
Model: `qwen-large` (qwen3.5-9b-mlx) · prompt v1 · 80 cases

## Quality
| Metric | Value | PRD target |
|---|---|---|
| Category accuracy (excl. `unclear`) | 74/80 (92%) | ≥ 85% |
| Raw accuracy (all cases) | 74/80 (92%) | |
| Accuracy, easy | 55/56 (98%) | |
| Accuracy, ambiguous | 19/24 (79%) | |
| Evidence recall | 70% | ≥ 80% |
| Evidence precision | 40% | |
| Review rate | 1/80 (1%) | ≤ 30% |
| Confident-but-wrong rate | 6/79 (8%) | ≤ 5% |
| Valid JSON (after retry) | 80/80 (100%) | 100% |
| Valid JSON first try | 80/80 (100%) | |
| Cases with made-up evidence IDs | 0/80 (0%) | |
| Cases citing a section not provided | 1/80 (1%) | |
| Model said `unclear` | 0/80 (0%) | |

## Speed and cost
| Metric | Value |
|---|---|
| Latency median / p90 | 11.7s / 17.4s |
| Time to first token, median | 3.71s |
| Tokens per case, mean in / out | 1879 / 144 |
| Cost per case | £0 marginal (local) |

## By gold category
| Category | Correct | Evidence recall |
|---|---|---|
| fraud_unauthorised | 11/11 (100%) | 64% |
| not_as_described | 14/17 (82%) | 62% |
| not_received | 11/12 (92%) | 79% |
| processing_error | 18/19 (95%) | 71% |
| refund_not_processed | 13/14 (93%) | 79% |
| subscription_cancelled | 7/7 (100%) | 60% |

## Errors (gold → predicted)
- not_as_described → refund_not_processed: 2  (C047, C065)
- not_received → not_as_described: 1  (C016)
- processing_error → subscription_cancelled: 1  (C030)
- refund_not_processed → subscription_cancelled: 1  (C048)
- not_as_described → subscription_cancelled: 1  (C056)

## Calibration (does confidence match accuracy?)
| Confidence | Cases | Accuracy |
|---|---|---|
| 0.00–0.50 | 0 | – |
| 0.50–0.70 | 0 | – |
| 0.70–0.85 | 0 | – |
| 0.85–0.95 | 14 | 10/14 (71%) |
| 0.95–1.00 | 66 | 64/66 (97%) |

## Review threshold sweep (gap 0.15, retrieval 0.50 held fixed)
| Confidence threshold | Review rate | Confident-but-wrong |
|---|---|---|
| 0.50 | 1/80 (1%) | 6/79 (8%) |
| 0.60 | 1/80 (1%) | 6/79 (8%) |
| 0.70 ← current | 1/80 (1%) | 6/79 (8%) |
| 0.80 | 1/80 (1%) | 6/79 (8%) |
| 0.85 | 1/80 (1%) | 6/79 (8%) |
| 0.90 | 11/80 (14%) | 2/69 (3%) |
| 0.95 | 15/80 (19%) | 2/65 (3%) |

