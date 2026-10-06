# PRD: Dispute-triage assistant for small merchants

**Status:** v1.1 (targets confirmed after the baseline run) · **Owner:** project author · **Date:** 5 Oct 2026 · Prototype using synthetic data and public card-scheme guidance only.

## User
The owner or operations lead at a small online merchant: a few staff, no payments or risk team, and disputes handled between other jobs. They see a few chargebacks a month, through their payment provider's dashboard.

## Problem
A dispute arrives as a reason code and the customer's short complaint, with a tight response deadline. The merchant doesn't know what they're actually being accused of or what evidence answers it. So they either accept the loss, or submit generic evidence that doesn't address the claim and lose anyway. Both outcomes cost revenue and add to the merchant's dispute ratio.

## Job to be done
*When a dispute lands, help me understand what I'm being accused of and exactly what evidence to send, so I can respond correctly before the deadline without becoming a card-scheme expert.*

## Scope
**In:** For each case, the system returns JSON with: the category (one of the 6 in `docs/categories.md`, or `unclear`), a confidence score, a checklist of recommended evidence, a plain-language explanation that cites the retrieved rule passages, and a human-review flag. Pipeline: retrieve rules (embeddings) → classify → recommend evidence → explain. Compares Qwen 3.5 4B, Qwen 3.5 9B (both local) and Claude.

**Out:** Submitting responses to providers; predicting win likelihood or advising whether to fight; fraud prevention; real merchant or cardholder data; live integration with payment providers; ATM, instalment and other out-of-scope dispute types; legal advice.

## Success metrics
Measured per model on the labelled synthetic evaluation set: 80 cases (60 minimum), about 70% easy and 30% ambiguous, with at least 6 cases per category. Accuracy is calculated on cases the system does not mark `unclear`; those count as sent to review and are capped by the review-rate guardrail.

| Metric | Definition | Target |
|---|---|---|
| Category accuracy | Predicted category = gold label; also reported separately for easy and ambiguous cases | **≥ 85%** overall |
| Evidence recall | Share of the gold evidence items for each case that appear in the recommendation, averaged across cases | ≥ 80% |
| Latency | Median and p90 seconds from request to complete JSON | p90 ≤ 20 s local, ≤ 10 s Claude |
| Cost per case | API spend ÷ cases (also shown per 1,000 cases); local models = £0 marginal | ≤ $0.02 Claude |
| *Guardrail:* confident-but-wrong rate | Share of cases *not* flagged for review that are wrong | ≤ 5% |
| *Guardrail:* review rate | Share of cases flagged for human review | ≤ 30% |
| *Guardrail:* valid JSON | Output passes the schema check (one retry allowed) | 100% |

Three targets were marked provisional in v1. After the baseline run **I kept them unchanged**, so no target was moved after seeing results.

## Human-review rule
Flag `needs_human_review = true` if **any** of these is true:
1. The category is `unclear`.
2. Confidence is below **0.70**. This is a starting value; I'll tune it on the evaluation set until the confident-but-wrong rate is ≤ 5%.
3. The top two categories are within 0.15 of each other.
4. Retrieval returned no rule passage above the similarity threshold, so there's nothing to ground the answer on.
5. The output still fails the schema check after one retry.

## Risks and mitigations
- **Wrong category leads to wrong evidence and a lost dispute.** Mitigation: the human-review rule, plus the confident-but-wrong guardrail.
- **Self-reported confidence from small models is poorly calibrated.** Mitigation: tune the threshold against observed accuracy rather than trusting the raw score; report a calibration table.
- **Invented rules or reason codes.** Mitigation: explanations must cite retrieved passages, and categories and evidence IDs are validated against fixed lists.
- **Synthetic data is cleaner than real complaints.** Mitigation: include the confusion pairs, short or vague narratives, and noise. Results don't claim to reflect real-world performance.
- **Scheme rules change.** Mitigation: sources are dated in `docs/categories.md`. This is a prototype, not operational guidance.
- **Local model limits on 24 GB.** Mitigation: one model loaded at a time, a fixed 8,192-token context, and thinking mode off.

## Change log
- **v1.1:** provisional targets confirmed unchanged. Categories reduced from 7 to 6 (`authorisation_issue` merged into `processing_error` during labelling). Labelling rules added: received-or-used test, claim priority (H1), recurring signal (H2). See the labelling rules log in `docs/categories.md`.
