# Scores: claude_v1.jsonl
Model: `claude` (claude-sonnet-5-5) · prompt v1 · 80 cases

## Quality
| Metric | Value | PRD target |
|---|---|---|
| Category accuracy (excl. `unclear`) | 78/80 (98%) | ≥ 85% |
| Raw accuracy (all cases) | 78/80 (98%) | |
| Accuracy, easy | 56/56 (100%) | |
| Accuracy, ambiguous | 22/24 (92%) | |
| Evidence recall | 83% | ≥ 80% |
| Evidence precision | 50% | |
| Review rate | 11/80 (14%) | ≤ 30% |
| Confident-but-wrong rate | 0/69 (0%) | ≤ 5% |
| Valid JSON (after retry) | 80/80 (100%) | 100% |
| Valid JSON first try | 79/80 (99%) | |
| Cases with made-up evidence IDs | 0/80 (0%) | |
| Cases citing a section not provided | 1/80 (1%) | |
| Model said `unclear` | 0/80 (0%) | |

## Speed and cost
| Metric | Value |
|---|---|
| Latency median / p90 | 2.5s / 6.3s |
| Time to first token, median | 0.92s |
| Tokens per case, mean in / out | 2832 / 291 |
| Cost per case / per 1,000 cases | $0.0086 / $8.57 (at $2.0/$10.0 per M tokens) |

## By gold category
| Category | Correct | Evidence recall |
|---|---|---|
| fraud_unauthorised | 11/11 (100%) | 92% |
| not_as_described | 16/17 (94%) | 82% |
| not_received | 11/11 (100%) | 97% |
| processing_error | 17/18 (94%) | 92% |
| refund_not_processed | 15/15 (100%) | 64% |
| subscription_cancelled | 8/8 (100%) | 65% |

## Errors (gold → predicted)
- not_as_described → refund_not_processed: 1  (C016)
- processing_error → fraud_unauthorised: 1  (C055)

## Calibration (does confidence match accuracy?)
| Confidence | Cases | Accuracy |
|---|---|---|
| 0.00–0.50 | 0 | – |
| 0.50–0.70 | 11 | 9/11 (82%) |
| 0.70–0.85 | 10 | 10/10 (100%) |
| 0.85–0.95 | 35 | 35/35 (100%) |
| 0.95–1.00 | 24 | 24/24 (100%) |

## Review threshold sweep (gap 0.15, retrieval 0.50 held fixed)
| Confidence threshold | Review rate | Confident-but-wrong |
|---|---|---|
| 0.50 | 1/80 (1%) | 2/79 (3%) |
| 0.60 | 7/80 (9%) | 1/73 (1%) |
| 0.70 ← current | 11/80 (14%) | 0/69 (0%) |
| 0.80 | 15/80 (19%) | 0/65 (0%) |
| 0.85 | 21/80 (26%) | 0/59 (0%) |
| 0.90 | 26/80 (32%) | 0/54 (0%) |
| 0.95 | 56/80 (70%) | 0/24 (0%) |

