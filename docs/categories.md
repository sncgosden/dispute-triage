# Dispute categories

This is the label set the classifier will predict. It is based on public card-scheme guidance only (sources at the bottom).

## Design choices

- **Merchant-facing labels, scheme-mapped.** A small merchant thinks "the customer says it never arrived", not "Visa 13.1 / Mastercard 4853". So the labels describe what the cardholder is claiming in plain language, and each one maps to the scheme reason codes behind it.
- **Classify the claim, not the truth.** A cardholder who made the purchase but files it as fraud ("friendly fraud") is still labelled `fraud_unauthorised`, because that is the reason code the merchant has to answer. Whether the claim is true is a question for the evidence step, not the classification step.
- **7 categories + 1 fallback.** That's few enough for a 4B model to tell apart reliably, and enough to cover the disputes a small online merchant actually sees. `unclear` is a real output: low confidence should send the case to a human, not force a guess.
- **Out of scope:** ATM cash disputes (Visa 13.9), original credit transactions (Visa 13.8), fraud-monitoring-programme disputes (Visa 10.5), Mastercard instalment billing (4850) and Europe-domestic disputes (4999). None of these is a dispute a small merchant can act on.

## Categories at a glance

| # | Label | The cardholder says… | Visa | Mastercard |
|---|---|---|---|---|
| 1 | `fraud_unauthorised` | "I didn't make this purchase." | 10.1–10.4 | 4837, 4840, 4849, 4863, 4870, 4871 |
| 2 | `not_received` | "I paid but never got it." | 13.1 | 4853 (legacy 4855) |
| 3 | `not_as_described` | "It's broken / fake / not what was advertised." | 13.3, 13.4, 13.5 | 4853 |
| 4 | `subscription_cancelled` | "I cancelled but was charged again." | 13.2 | 4841 |
| 5 | `refund_not_processed` | "I returned it or cancelled, and no refund came." | 13.6, 13.7 | 4853 (legacy 4860) |
| 6 | `processing_error` | "I was charged twice / the wrong amount / in the wrong currency / I already paid another way." | 12.x | 4831, 4834, 4842, 4846 |
| 7 | `authorisation_issue` | Usually raised by the issuer, not the customer: the transaction wasn't properly authorised or was submitted too late. | 11.1–11.3 | 4808 |
| – | `unclear` | Not enough information, or it plausibly fits two or more categories. | – | – |

## Category detail

### 1. `fraud_unauthorised`
- **Definition:** The cardholder denies making or authorising the transaction.
- **Signals:** "didn't make", "don't recognise", "card stolen", "hacked", an unfamiliar merchant name on the statement.
- **Key evidence:** 3-D Secure / Visa Secure authentication result; AVS/CVV match; device ID, IP address or fingerprint matching earlier undisputed orders (Visa Compelling Evidence: 2+ prior undisputed transactions 120–365 days old); delivery to the cardholder's verified address; the customer's account login and usage history.
- **Watch for:** "I don't recognise this charge" can just mean an unclear statement descriptor. If the customer then recognises the merchant, this becomes another category.

### 2. `not_received`
- **Definition:** Goods or services were paid for but never delivered or provided.
- **Signals:** "never arrived", "no tracking", "service never happened", "event cancelled".
- **Key evidence:** Carrier proof of delivery or collection (signature, GPS, photo); the expected delivery date if the order is still in transit; for digital goods, download/access logs; for services, proof the service was provided.
- **Watch for:** "It arrived broken" is `not_as_described`, not this category.

### 3. `not_as_described`
- **Definition:** Something was delivered, but it was defective, damaged, counterfeit, or materially different from what was described or agreed.
- **Signals:** "broken", "damaged", "fake", "wrong item", "not what was advertised", "poor quality".
- **Key evidence:** The product listing and description as shown at checkout; invoice or contract terms; photos from fulfilment; messages with the customer; proof a replacement or repair was offered or accepted; the return policy.
- **Watch for:** If the customer *has already returned it* and wants their money back, this is `refund_not_processed`.

### 4. `subscription_cancelled`
- **Definition:** A recurring charge was taken after the cardholder cancelled, or withdrew permission to bill.
- **Signals:** "subscription", "membership", "cancelled last month", "still charging me", "free trial".
- **Key evidence:** Subscription terms and how cancellation was disclosed; the cancellation request log (or proof that none was received); usage after the claimed cancellation date (Visa accepts this from 19 Oct 2024); trial-to-paid disclosures.
- **Watch for:** A one-off order the customer cancelled before it shipped is `refund_not_processed`.

### 5. `refund_not_processed`
- **Definition:** The cardholder returned the goods or cancelled the order or service and expected a refund (credit) that hasn't arrived.
- **Signals:** "returned it", "promised a refund", "cancelled my order/booking", "still waiting for my money".
- **Key evidence:** Proof the refund was already issued (amount and date); the return or cancellation policy shown at checkout; proof the return wasn't received or fell outside policy; how the customer agreed to the terms.
- **Watch for:** If there is no return or cancellation, only dissatisfaction with the item, it's `not_as_described`.

### 6. `processing_error`
- **Definition:** The transaction was processed incorrectly: a duplicate, the wrong amount, the wrong currency, late presentment, or the customer paid by another method as well.
- **Signals:** "charged twice", "double charge", "wrong amount", "different from receipt", "paid cash", "charged in dollars".
- **Key evidence:** Settlement and batch logs showing two separate purchases (or that only one settled); itemised receipt matching the charged amount; currency / DCC disclosure; records showing the card was the only payment method used.
- **Watch for:** A pending authorisation plus a settled charge often looks like a duplicate to customers but isn't one.

### 7. `authorisation_issue`
- **Definition:** The issuer disputes the authorisation itself: declined, never obtained, or the transaction was submitted outside the time limit.
- **Signals:** Rarely in the customer's own words; it shows up as an issuer reason code or as "declined but still charged".
- **Key evidence:** Authorisation approval code and timestamp; proof of timely presentment.
- **Watch for:** Small merchants rarely see this directly. It's in the label set for completeness, and it's the category most likely to come from a reason code rather than free text.

### `unclear` (fallback)
- **Use when:** Confidence is below threshold, the narrative is too short, or two categories are equally plausible (e.g. "arrived damaged and they won't refund me").
- **Action:** Route to human review with the top two candidate categories.

## Confusion pairs to test in the eval set

These are the boundaries most likely to trip a model, so the synthetic cases should deliberately include them:

1. `not_as_described` ↔ `refund_not_processed` (was it returned?)
2. `subscription_cancelled` ↔ `refund_not_processed` (recurring or one-off?)
3. `fraud_unauthorised` ↔ `processing_error` ("I don't recognise this" vs "charged twice")
4. `not_received` ↔ `not_as_described` ("arrived wrong" vs "never arrived")

## Sources

- Visa, *Dispute Management Guidelines for Visa Merchants* (June 2024): https://bd.visa.com/dam/VCOM/global/support-legal/documents/merchants-dispute-management-guidelines.pdf
- Visa, merchant disputes overview: https://usa.visa.com/run-your-business/merchant-support/merchant-disputes.html
- Mastercard, *Chargeback Guide*: https://www.mastercard.us/content/dam/mccom/en-us/documents/rules/chargeback-guide.pdf (public edition dated Dec 2018; the current reason code list was cross-checked against the current secondary summary below)
- Chargeflow, Mastercard reason codes summary: https://www.chargeflow.io/blog/mastercard-chargeback-reason-codes

Scheme rules change frequently. These mappings are for a prototype, not operational advice.
