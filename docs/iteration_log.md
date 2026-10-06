# Iteration log

What I tried, what happened, and what I decided, written as I went. Numbers come from files in `results/`. Negative results were kept on purpose.

---

**Thinking mode used up the token budget.** With Qwen's thinking mode on, the model spent its whole output budget reasoning and returned no answer. *Decision:* thinking off by default for all models (a prefilled empty think block for Qwen).

**Routing will be simulated offline.** The routing experiment will use saved outputs rather than live calls, because the two local models can't be loaded together.

**Labelling changed the taxonomy.** I labelled all 80 generated cases blind, without seeing the generator's labels. None of the 8 cases written as `authorisation_issue` read as a distinct category: in a cardholder's words, "declined but charged" or "charged months later" is indistinguishable from a processing error. *Decision:* merged `authorisation_issue` into `processing_error` (now 6 categories + `unclear`), before any model ran. Logged in `docs/categories.md`.

**`unclear` became a review route, not a scored category.** Every case the generator wrote as `unclear` could be resolved on careful reading. *Decision:* a model answer of `unclear` counts as "sent to review"; accuracy is calculated on the other cases, and the 30% review-rate cap stops the model scoring well by saying `unclear` to everything.

**Agreement with the generator's labels was low on ambiguous cases.** My blind labels matched the generator's on 44/56 easy cases but only 9/24 ambiguous ones. After fixing my own slips, final agreement is 58/80 (73%). This is why I labelled the cases myself: otherwise the eval would partly test Claude against itself.

**Evidence-ID naming caused bad gold labels.** 43 of 80 cases had an evidence ID that didn't fit the category (e.g. `auth_3ds`, meaning 3-D Secure, used for "declined but charged"; `itemised_receipt` used for quality complaints). The ID names were ambiguous. *Decision:* revised by rule-based mapping with Claude; every change is logged in the `claude_revision` column and was reviewed by me. Category labels remain fully mine; gold evidence is partly rule-revised (a limitation for the memo).

**Retrieval baseline was below target.** nomic-embed-text v1.5, k=3: the correct rule section was in the top 3 for 84% of cases and ranked 1st for 52% (`python src/retrieve.py --check`). 7 of 13 misses were `not_as_described`. The general section (R0) took up a slot without ever being the right answer.

**Two general fixes, checked against a held-out half.** (1) R0 always included in the prompt instead of being ranked. (2) A "Customers often write" line in each section, because the rules were written in merchant language and complaints are in customer language. I only looked at misses from batches 1–2; batches 3–4 were held out. Result: top 3 rose to 86% (dev 92→95%, held out 75→78%). Similar gains in both halves suggest the fix wasn't tuned to the test. I removed one phrase I'd added because it was prompted by a held-out case. *Decision:* stopped tuning. The remaining misses look like a limit of the embedding model (e.g. "£42 came out TWICE" retrieves fraud first), and the end-to-end effect is measured below.

**The smoke test caught a cut-off bug.** First 10 cases on Claude: 8/10 correct, but 2 replies hit the 600-token limit mid-explanation, so the JSON was incomplete (one recovered on retry, one failed and went to review). *Fix:* explanation capped at 60 words, limit raised to 1,000, and truncation detected so the retry message says "too long". Rerun: 10/10 valid first time, about 190 output tokens, median 2.3s.

**The smoke test also exposed label problems.** C010 (a May car hire charged in September) was still labelled `unclear` from before the merge; under the written rule it's `processing_error`. C006 (festival moved) and C046 (coach cancelled, alternative not taken) sat between two categories. *Decision:* the received-or-used test: if the customer never received or used what they paid for, it's `not_received`; if they did and it was poor, it's `not_as_described`. Applied to the labels, rules and prompt before the full run. I changed labels only where they contradicted a written rule, never just because the model disagreed.

**Claude v1, full run (80 cases, prompt v1):** `results/claude_v1_score.md`

| Metric                      | Result                                                                 | PRD target |
| --------------------------- | ---------------------------------------------------------------------- | ---------- |
| Category accuracy           | 95% (easy 100%, ambiguous 83%)                                         | ≥ 85%      |
| Confident-but-wrong         | 0/69                                                                   | ≤ 5%       |
| Review rate                 | 14%                                                                    | ≤ 30%      |
| Evidence recall / precision | 80% / 48%                                                              | ≥ 80%      |
| Valid JSON                  | 100% (1 retry)                                                         | 100%       |
| Latency median / p90        | 2.5s / 6.3s                                                            |            |
| Cost                        | $0.0086 per case, $8.57 per 1,000 ($2/$10 per M tokens, checked 5 Oct) |            |

Three observations:

1. **Confidence is a good safety signal for Claude.** Below 0.70, accuracy was 64% (7/11); at 0.70 and above, 69/69. All 4 errors were flagged for review. The threshold sweep supports 0.70: at 0.60 one error gets through unreviewed; at 0.85 the review rate nearly doubles with no gain.
2. **All 4 errors are complaints with two claims in one** (e.g. "not as promised *and* I asked to cancel", "service fell short *and* the promised partial refund never came"). Several of Claude's answers are defensible. Not relabelled. Candidate for v2: tell the model to classify the claim the merchant must act on first.
3. **Evidence is weaker than category.** The model suggests about 4 items against 2–3 gold, giving high coverage but low precision (48%). Recall is lowest for subscription (60%) and refund (64%) cases, partly because of gold-label quality (see the evidence-ID note above).

Other notes: flagged cases were slower (6–11s), because the model writes more when it's unsure. One retrieval miss (C073) was still answered correctly, so retrieval misses don't necessarily cause wrong answers. The one "cited a section not provided" flag was a false alarm in my check (R1's text points to R6).

**Caveat:** Claude generated the case wording, so it may find these complaints unusually easy to read. Treat 95% as a ceiling, not a real-world forecast. The Qwen runs will show how much of the score comes from the model and how much from the data.

---

## Open questions after the Claude baseline

- How do the 4B and 9B compare on ambiguous cases and on calibration? Is their confidence as useful as Claude's?
- How many local-model errors line up with retrieval misses?
- Next: a prompt fix for multi-claim complaints, and routing (4B when confident, otherwise 9B or Claude).
---

## Three-model comparison and failure analysis

**Runner and settings.** Added resume, run settings files and per-case timestamps. Temperature fixed at 0 for Qwen. Claude's temperature can't be set with the SDK in use, so it runs at its default (an asymmetry, documented in `results/run_config.md`). No batching or pauses.

**Results** (`results/comparison_v1.md`):

| | Claude | Qwen 4B | Qwen 9B |
|---|---|---|---|
| Accuracy (easy / ambiguous) | 95% (100 / 83) | 94% (100 / 78) | 92% (98 / 79) |
| Evidence recall | 80% | 75% | 70% |
| Confident-but-wrong @0.70 | 0% | 6% | 8% |
| Safe threshold range | 0.51–0.87 | none | 0.86–0.95 |
| Latency median / p90 | 2.5 / 6.3s | 4.5 / 7.1s | 11.7 / 17.4s |
| Cost per 1,000 | $8.57 | £0 | £0 |

**Key finding: confidence calibration, not accuracy, separates the models.** All three are at 92–95% accuracy. But the Qwen models never report confidence below 0.85, so a 0.70 review threshold never triggers and their errors go unreviewed. The 9B's confidence still carries signal on a compressed scale (safe at 0.86–0.95); the 4B's doesn't (no safe threshold). **One shared threshold is wrong; thresholds must be calibrated per model.**

**Bigger wasn't better.** The 9B was slightly less accurate than the 4B, with weaker evidence and 2.6× the latency. Its only advantage is usable confidence.

**Operational note.** LM Studio crashed partway through the 9B run (connection lost after 24 cases); the run resumed after a restart. The 9B's latency spans both periods.

**Failure analysis:** `docs/failure_analysis_v1.md`. 16 errors across 9 cases, in four types: multi-claim with no priority rule (8), recurring vs one-off (4), unrecognised charge from a known merchant (2), misreading (2). In 4 of 9 cases the models agree with each other against my label. A sensitivity check shows that relabelling those under existing principles would put Claude at 100%, but every relabel moves towards Claude's answer, so I'm keeping the original labels as the baseline and reporting the sensitivity. Retrieval misses explain only 4 of 16 errors.

**Hypotheses for v2:** H1, a claim-priority rule for multi-claim complaints; H2, a recurring-charge signal.

---

## v2 changes: prompt and routing

**Labels first, then the prompt.** I wrote rules H1 (claim priority) and H2 (recurring signal) into `docs/categories.md`, then scanned all 80 cases for conflicts. Three labels changed: C065 → refund (H1), C030 → subscription (H2), C016 → not_as_described (it failed the received-or-used test; this goes *against* Claude's answer). C055 was left alone because no new rule covers it. v1 was rescored on the corrected labels (Claude 98%, 4B 95%, 9B 96%); the original-label table is kept.

**Change 1, prompt v2:** H1, H2, the received-or-used test, calibration guidance and three invented worked examples. Run on both Qwen models.
- **4B: better.** 96% accuracy, ambiguous 88%, confident-but-wrong 3.8% (passes), safe range 0.50–0.90.
- **9B: worse.** 89% accuracy, ambiguous 75%, confident-but-wrong 9.2%. It over-applied the new rules (C046 coach cancelled → refund; C050 paid by insurer → refund; C053 late charge → subscription). Exactly the risk noted for H1.
- **Calibration guidance didn't work**, and evidence recall fell for both models.
- **Lesson:** the same prompt change helped one model and hurt another. Test every change on every candidate model. I'm keeping the 9B on v1.

**Change 2, routing** (simulated offline from saved outputs; `results/routing_v2.md`):
- 4B, to Claude below 0.90 confidence: 94%. **Worse** than the 4B alone, because escalation sent some correct answers to Claude, which got them wrong.
- 4B, to Claude below 0.95: 96%, confident-but-wrong 1.4%, 31% to Claude, $3.03 per 1,000.
- **4B and 9B agree, else Claude: 98% (= Claude), 2% to Claude, $0.29 per 1,000.** Agreement is a far better signal than confidence. Caveats: shared blind spots (C048 and C056 slip through because both models are wrong the same way), only 2 escalations on 80 cases, about 18s latency, and evidence recall unchanged at 69%.

**Still unsolved:** evidence recall. Every local-first route is at 69–76% against an 80% target.
