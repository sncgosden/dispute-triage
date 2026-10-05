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