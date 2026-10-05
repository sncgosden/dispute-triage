# Failure analysis: v1 runs

**Status:** first-pass analysis drafted by Claude from `results/error_review_v1.md`, for Sebastian to review. Failure types and relabel proposals are recommendations; **no gold labels have been changed.**

Scope: every wrong answer in `claude_v1`, `qwen4b_v1` and `qwen9b_v1` (prompt v1, 80 cases): **16 errors across 9 cases** (Claude 4, Qwen 4B 6, Qwen 9B 6).

## Failure types

| # | Failure type | What happens | Cases | Claude | 4B | 9B | Total |
|---|---|---|---|---|---|---|---|
| 1 | **Multi-claim complaint, no priority rule** | Two claims in one message (e.g. "not as promised" *and* "refund promised but not paid"); the model answers a different one from the gold label. | C016, C044, C048, C065 | 2 | 3 | 3 | **8** |
| 2 | **Recurring vs one-off** | A repeat charge for a pack or plan after the customer gave notice is read as a subscription (or the reverse). | C030, C056 | 1 | 1 | 2 | **4** |
| 3 | **Unrecognised charge from a known merchant** | "Bought from them before, don't know what this new charge is": fraud (denies ordering) or processing error (merchant mistake)? Retrieval also missed R6 here. | C055 | 1 | 1 | 0 | **2** |
| 4 | **Misreading** | The model invents or misses a fact in the complaint. | C047 (9B invented a refund claim), C072 (4B said `unclear` on a resolvable case; flagged for review, so harmless) | 0 | 1 | 1 | **2** |
| | | | | **4** | **6** | **6** | **16** |

**Half of all errors (8/16) are type 1.** The prompt and rules define each category, but say nothing about **which claim to classify when a complaint contains two**. All three models fail here, so it's a gap in the spec, not just a model weakness.

## Is it the label, the model or retrieval?

**Label quality.** In 4 of the 9 cases (C016, C030, C055, C065), at least two models agree with each other against the gold label. In three of them the generator's label sided with the models too. Under principles already written down, several gold labels are debatable:

| Case | Gold | Models | Proposed label | Principle |
|---|---|---|---|---|
| C016 | not_received | refund (Claude), NAD (4B, 9B) | `refund_not_processed` | The course was received, so the received-or-used test rules out `not_received`. The customer cancelled in week one and is "still waiting". |
| C065 | not_as_described | refund (Claude, 9B) | `refund_not_processed` | The manager promised a partial refund that hasn't arrived: the claim the merchant must answer first (proposed priority rule below). |
| C030 | processing_error | subscription (all 3) | `subscription_cancelled` | A second pack charged automatically after the customer gave notice is a recurring charge after cancelling (R4). |
| C055 | processing_error | fraud (Claude, 4B) | `fraud_unauthorised` | "I haven't ordered anything else" is a denial of authorising the payment. **Classify the claim, not the truth** (docs/categories.md). |

**Sensitivity check (labels not changed):** if these four relabels were accepted:

| | Accuracy now → relabelled | Ambiguous | Confident-but-wrong @0.70 | Safe threshold range |
|---|---|---|---|---|
| Claude | 95% → **100%** | 83% → 100% | 0% → 0% | 0.51–0.87 → 0.50–0.87 |
| Qwen 4B | 94% → 95% | 78% → 83% | 6% → 5% | none → 0.86–0.92 |
| Qwen 9B | 92% → 94% | 79% → 83% | 8% → 6% | 0.86–0.95 → unchanged |

**Read this with caution.** Every proposed relabel moves the gold label towards Claude's answer, so all of Claude's "errors" disappear. That is exactly the bias the plan warns about: using the strongest model as the judge. Each relabel above cites a principle written *before* these runs, but the honest summary is:

> Claude's 4 errors are all on cases with debatable gold labels. The Qwen models make the same debatable-label errors **plus** genuine ones (C044, C047, C048, C056, C072).

**Recommendation:** keep the v1 scores on the **original** labels as the official baseline. Report the sensitivity table alongside it. Write the priority rule first, then decide relabels against that rule, and rescore v1 and v2 on the same labels so the comparison stays fair.

**Retrieval.** The gold category's section was missing in only **4 of 16** error instances (C055 for Claude and the 4B, C065 for Claude and the 9B). In both cases another model got the answer right *without* that section (9B on C055, 4B on C065). **Retrieval is a minor contributor; the prompt and rules matter more.**

**Model.** Genuine model errors (wrong under any reasonable reading) are C047 (9B), C044 (4B), C048 (4B, 9B; the refund promise is ignored) and C056 (9B). **These are all Qwen**, and all except C047 come from the 0.85–0.95 confidence band, so they slip past the 0.70 review threshold.

## Hypotheses for v2

**H1: add a claim-priority rule (targets type 1, 8 of 16 errors).**
Add to the prompt and rules: *"If a complaint contains more than one claim, classify the one the merchant must act on first: (1) a refund or credit the merchant promised or confirmed that hasn't arrived → `refund_not_processed`; (2) a recurring charge after cancelling → `subscription_cancelled`; (3) otherwise, the complaint about the goods or service itself."*
**Expected effect:** fixes most type 1 errors for all models, if the gold labels follow the same rule (decide C016 and C065 first). **Risk:** may push some genuine `not_as_described` cases into `refund_not_processed` if the model sees any mention of a refund as a promise.

**H2: add a recurring-charge signal (targets type 2, 4 errors).**
Add to R4 and the prompt: *"A second automatic charge for a pack, plan or membership after the customer gave notice counts as a recurring charge."*
**Expected effect:** fixes C030 for all models (if relabelled) and C056 for the 9B. **Risk:** small; one-off duplicates are already covered under R6.

Type 3 (one case) and type 4 (model misreading) aren't worth a targeted fix yet: one case is too few to tune on, and misreading is what the human-review rule is for.
