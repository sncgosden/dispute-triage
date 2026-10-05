# Scores: qwen9b_v1.jsonl
Model: `qwen-large` (qwen3.5-9b-mlx) · prompt v1 · 80 cases

## Quality
| Metric | Value | PRD target |
|---|---|---|
| Category accuracy (excl. `unclear`) | 77/80 (96%) | ≥ 85% |
| Raw accuracy (all cases) | 77/80 (96%) | |
| Accuracy, easy | 55/56 (98%) | |
| Accuracy, ambiguous | 22/24 (92%) | |
| Evidence recall | 70% | ≥ 80% |
| Evidence precision | 41% | |
| Review rate | 1/80 (1%) | ≤ 30% |
| Confident-but-wrong rate | 3/79 (4%) | ≤ 5% |
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
| not_as_described | 15/17 (88%) | 64% |
| not_received | 11/11 (100%) | 77% |
| processing_error | 18/18 (100%) | 75% |
| refund_not_processed | 14/15 (93%) | 78% |
| subscription_cancelled | 8/8 (100%) | 60% |

## Errors (gold → predicted)
- not_as_described → refund_not_processed: 1  (C047)
- refund_not_processed → subscription_cancelled: 1  (C048)
- not_as_described → subscription_cancelled: 1  (C056)

## Calibration (does confidence match accuracy?)
| Confidence | Cases | Accuracy |
|---|---|---|
| 0.00–0.50 | 0 | – |
| 0.50–0.70 | 0 | – |
| 0.70–0.85 | 0 | – |
| 0.85–0.95 | 14 | 12/14 (86%) |
| 0.95–1.00 | 66 | 65/66 (98%) |

## Review threshold sweep (gap 0.15, retrieval 0.50 held fixed)
| Confidence threshold | Review rate | Confident-but-wrong |
|---|---|---|
| 0.50 | 1/80 (1%) | 3/79 (4%) |
| 0.60 | 1/80 (1%) | 3/79 (4%) |
| 0.70 ← current | 1/80 (1%) | 3/79 (4%) |
| 0.80 | 1/80 (1%) | 3/79 (4%) |
| 0.85 | 1/80 (1%) | 3/79 (4%) |
| 0.90 | 11/80 (14%) | 1/69 (1%) |
| 0.95 | 15/80 (19%) | 1/65 (2%) |

