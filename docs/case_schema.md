# Eval case schema and generation prompt

What one test case looks like, and the prompt used to generate the 80 synthetic cases with Claude.

## Design choices

- **Labels are kept separate from the generator's answers.** The generator writes each case *and* suggests an answer (`gen_category`, `gen_evidence`). Gold labels (`true_category`, `required_evidence`) are in separate columns and were set blind, with the `gen_` columns hidden. Where the two disagree, the gold label wins and `label_note` says why. This avoids testing Claude against its own answers.
- **The model only sees what a merchant would see.** The triage pipeline gets `merchant_type`, `amount_gbp`, `transaction_date` and `dispute_text`, and nothing else. Every other column is for scoring or labelling.
- **Evidence uses fixed IDs.** Gold evidence is written as IDs from the list below, not free text. That makes evidence recall measurable: the scorer checks whether each gold ID is covered by the model's free-text recommendations.
- **The scheme reason code is left out on purpose.** In real life the merchant also sees a reason code. Leaving it out tests whether the model understands the complaint itself, which matters because the stated reason code and the customer's actual story often don't match (for example, friendly fraud). It's listed as a limitation in the memo.

## Columns

| Column | Filled by | Seen by model? | Description |
|---|---|---|---|
| `id` | generator | no | `C001`–`C080` |
| `batch` | generator | no | 1–4 |
| `merchant_type` | generator | **yes** | e.g. `cafe`, `online clothing`, `subscription software` |
| `amount_gbp` | generator | **yes** | Realistic for that merchant type, 2 decimal places |
| `transaction_date` | generator | **yes** | `YYYY-MM-DD`, between 2026-05-01 and 2026-09-30 |
| `dispute_text` | generator | **yes** | The cardholder's complaint as forwarded to the merchant, in the cardholder's own words: messy and realistic |
| `cardholder_claim` | generator | no | A neutral one-line summary of what the cardholder is claiming. Hidden during labelling. |
| `gen_category` | generator | no | The generator's suggested category |
| `gen_evidence` | generator | no | The generator's suggested evidence IDs, separated by `;` |
| `difficulty` | generator, reviewed in labelling | no | `easy` or `ambiguous` |
| `ambiguity_note` | generator | no | For ambiguous cases, the competing category and why. Empty for easy cases. |
| `true_category` | **labeller** | no | Gold label |
| `required_evidence` | **labeller** | no | Gold evidence IDs, separated by `;` (usually 2–4) |
| `label_note` | **labeller** | no | Why the gold label differs from the generator's, or the labelling rule applied |

**Difficulty:** a case is `easy` when one category clearly fits. It's `ambiguous` when a second category is plausible, information is missing, or the cardholder uses the wrong terms (e.g. says "fraud" when the parcel never arrived). A careful expert should still be able to choose, unless the gold label is `unclear`.

## Evidence IDs

| ID | Evidence | Typical categories |
|---|---|---|
| `auth_3ds` | 3-D Secure authentication result | fraud |
| `avs_cvv_match` | Address and CVV check results | fraud |
| `device_ip_history` | Device/IP matches earlier undisputed orders | fraud |
| `prior_undisputed_orders` | Customer's earlier undisputed purchases | fraud |
| `account_activity` | Customer account login and usage history | fraud, subscription |
| `proof_of_delivery` | Carrier proof of delivery or collection | not received, fraud |
| `tracking_expected_date` | Tracking showing the order is still within its delivery window | not received |
| `digital_access_logs` | Download, access or login logs for digital goods | not received, fraud |
| `service_provided_proof` | Proof the service or booking was provided | not received |
| `product_listing` | Product description as shown at checkout | not as described |
| `invoice_or_contract` | Invoice, order confirmation or contract terms | not as described, processing |
| `customer_communications` | Messages exchanged with the customer | most |
| `replacement_offer` | Replacement, repair or partial refund offered or accepted | not as described |
| `return_cancellation_policy` | Return or cancellation policy as disclosed at checkout | refund, not as described |
| `terms_acceptance` | Proof the customer accepted terms at checkout | refund, subscription |
| `subscription_terms` | Recurring billing and cancellation terms as disclosed | subscription |
| `cancellation_log` | Record of cancellation requests (or that none was received) | subscription, refund |
| `post_cancellation_usage` | Service usage after the claimed cancellation date | subscription |
| `refund_issued_proof` | Refund or credit already issued (amount and date) | refund, any |
| `return_not_received` | Proof the returned item never arrived or was outside policy | refund |
| `transaction_records` | Settlement and batch logs showing separate or single transactions | processing |
| `itemised_receipt` | Itemised receipt matching the amount charged | processing |
| `currency_disclosure` | Currency or DCC disclosure the customer accepted | processing |
| `single_payment_proof` | Records showing the card was the only payment method used | processing |
| `authorisation_record` | Authorisation approval code and timestamp | authorisation |
| `timely_presentment_proof` | Proof the transaction was submitted within the time limit | authorisation |

## Target mix (80 cases, 4 batches of 20)

| Category | Per batch | Total |
|---|---|---|
| `fraud_unauthorised` | 3 | 12 |
| `not_received` | 3 | 12 |
| `not_as_described` | 3 | 12 |
| `refund_not_processed` | 3 | 12 |
| `subscription_cancelled` | 2 | 8 |
| `processing_error` | 2 | 8 |
| `authorisation_issue` | 2 | 8 |
| `unclear` | 2 | 8 |
| **Total** | **20** | **80** |

*Note (5 Oct 2026):* this is the mix used for generation. After labelling, `authorisation_issue` was merged into `processing_error` (see `docs/categories.md`), so the generator's `authorisation_issue` cases now carry other gold labels.

Each batch has 6 ambiguous cases (30%). The smallest categories have 8 cases, so up to 2 could be removed during labelling while keeping the minimum of 6 per category.

---

## Generation prompt 


```text
You are generating synthetic test cases for evaluating an AI that helps small UK merchants triage card payment disputes (chargebacks). The data must be entirely fictional: no real people, no real company or brand names, no real card numbers or addresses.

## Categories (use these exact labels)
- fraud_unauthorised: cardholder says they did not make or authorise the purchase.
- not_received: paid, but goods or service never arrived or never happened.
- not_as_described: something arrived but was defective, damaged, counterfeit, wrong, or materially different from what was advertised.
- subscription_cancelled: a recurring charge taken after the cardholder cancelled or withdrew permission.
- refund_not_processed: cardholder returned goods or cancelled a one-off order or booking, and the promised or expected refund has not arrived.
- processing_error: charged twice, wrong amount, wrong currency, or already paid by another method.
- authorisation_issue: the payment was declined or never properly authorised, or submitted very late. In the cardholder's words this usually reads as "my card was declined but I was still charged" or "this charge appeared months later".
- unclear: the complaint is too vague or genuinely fits two categories equally. A careful expert could not choose.

## Evidence IDs (use only these, separated by ";")
auth_3ds; avs_cvv_match; device_ip_history; prior_undisputed_orders; account_activity; proof_of_delivery; tracking_expected_date; digital_access_logs; service_provided_proof; product_listing; invoice_or_contract; customer_communications; replacement_offer; return_cancellation_policy; terms_acceptance; subscription_terms; cancellation_log; post_cancellation_usage; refund_issued_proof; return_not_received; transaction_records; itemised_receipt; currency_disclosure; single_payment_proof; authorisation_record; timely_presentment_proof

## This batch
Batch 1, ids C001 to C020. Exactly this mix:
fraud_unauthorised 3, not_received 3, not_as_described 3, refund_not_processed 3, subscription_cancelled 2, processing_error 2, authorisation_issue 2, unclear 2.
Exactly 6 of the 20 must be "ambiguous" (the 2 unclear cases count towards the 6). The rest are "easy".
Shuffle the order so categories are not grouped together.

## Make the cases realistic and varied
- Merchant types: vary widely, e.g. cafe, online clothing, subscription software, hotel, furniture, event tickets, online course, phone accessories, florist, gym, takeaway delivery, mobile game credits, car hire, dog grooming. No more than 2 cases per merchant type in a batch.
- amount_gbp: realistic for the merchant type (a coffee is £3.40, a sofa is £1,249.00).
- transaction_date: between 2026-05-01 and 2026-09-30.
- dispute_text: the cardholder's own words, 1 to 6 sentences. Vary tone and quality: angry, polite, vague, rambling, very short, typos, non-native English, irrelevant detail, wrong terminology (e.g. calling a non-delivery "fraud"). Never mention the category name or a reason code.
- Ambiguous cases should come mainly from these confusable pairs:
  not_as_described vs refund_not_processed (was it returned?);
  subscription_cancelled vs refund_not_processed (recurring or one-off?);
  fraud_unauthorised vs processing_error ("I don't recognise this" vs "charged twice");
  not_received vs not_as_described (partial delivery, wrong item);
  fraud_unauthorised vs a family member using the card.
- cardholder_claim: one neutral sentence summarising the claim.
- gen_evidence: the 2 to 4 most important evidence IDs a merchant should submit.
- ambiguity_note: for ambiguous cases, name the competing category and why. Leave empty for easy cases.

## Output format
Output ONLY CSV, with no commentary before or after, inside a single code block.
First line is this header exactly:
id,batch,merchant_type,amount_gbp,transaction_date,dispute_text,cardholder_claim,gen_category,gen_evidence,difficulty,ambiguity_note
Wrap every field in double quotes. Escape any double quote inside a field by doubling it (""). No line breaks inside fields.

---
FOLLOW-UP MESSAGE FOR LATER BATCHES (send one at a time, change the numbers):
Batch 2, ids C021 to C040. Same mix and rules. Use different merchant types and different wording styles from earlier batches. Output the data rows only, with no header.
```

Batches 2–4 used the same prompt with the batch number and ID range changed, asking for different merchant types and wording styles from earlier batches. The raw output was committed before labelling, so the generator's answers are on record.
