# Market research notes

Public sources only, all checked on **6 Oct 2026**. These notes are the inputs for the next stage of the project: a strategy and business case for offering the triage through payment providers, and a cost model (in progress). Most sources are vendor blogs with a commercial interest. Where possible they were cross-checked against a payment provider's own pages; where sources disagree, both are shown.

## 1. What a dispute costs a UK merchant

| Item | Figure | Source | Confidence |
|---|---|---|---|
| Provider fee per dispute received | **£20**, charged win or lose | Stripe UK pricing page | High (provider's own page) |
| Fee to counter a dispute manually | **£20**, refunded if the merchant wins | Stripe UK pricing page | High |
| Automated evidence (Stripe Smart Disputes) | **30% of the disputed amount**, only on won disputes | Stripe UK pricing page | High |
| Third-party chargeback vendor | **25% of each recovered chargeback** (Chargeflow) | Redo, summarising Chargeflow pricing | Medium (secondary source) |
| Merchant win rate on disputes they fight | **44.6%** | Chargebacks911 2026 Field Report, via Redo | Medium (vendor data, mostly US) |
| Net recovery across all chargebacks | **10.7%** | Same | Medium |
| Total cost per $1 lost to fraud | **$4.61** (US retail and e-commerce) | LexisNexis True Cost of Fraud, Apr 2025, via Redo | Medium. Covers fraud generally, not only disputes, so it shouldn't be used directly as a dispute multiplier. |
| First-party misuse ("friendly fraud") | about **20%** of fraud disputes, up to 30% for high-volume online merchants | Visa 2025 Global eCommerce Payments & Fraud Report, via Redo | Medium |

**What this means:**

- A dispute costs a UK merchant at least £20 before the disputed amount, staff time or lost goods. Our triage costs **$8.57 per 1,000 cases on Claude**, less than 1p per case. Triage cost is negligible next to the fee. The value is in winning more disputes and wasting less time, not in saving on processing.
- The gap between the 44.6% win rate on fought disputes and the 10.7% net recovery suggests most disputes are never fought, or are fought badly. That gap is the opportunity this tool targets. It's an inference, not a measured fact.

## 2. Card-scheme monitoring programmes

These programmes are why payment providers care about their merchants' disputes, not just the merchants.

**Visa Acquirer Monitoring Program (VAMP):**

- **Ratio:** (fraud reports + disputes) ÷ settled transactions. A fraud report that becomes a dispute counts twice. (Justt)
- **Merchant "excessive" threshold:** 2.2% from 1 Jan 2026, then **1.5% from 1 Apr 2026** in most regions, with minimum counts of 1,000 and then 1,500 a month. (Checkout.com support page, Jun 2026; Justt)
- **Conflicting source:** a Trust Payments page (Apr 2026) gives **0.9% from 1 Jan 2026** for UK/Europe merchants, with a minimum of 1,000 disputes a month. **Check this with Visa or an acquirer before quoting it.**
- **Enforcement fee:** **$8 per dispute or fraud report** from 1 Jan 2026, lowered from earlier rates (Checkout.com). Trust Payments gives $10. Same conflict, and also to be checked.
- **Who pays:** Visa fines the acquirer, which usually passes the fine on to the merchant. Acquirers may set stricter internal limits.

**Mastercard Excessive Chargeback Program (Chargebacks911):**

| Programme | Monthly chargebacks | Chargeback ratio | Fines |
|---|---|---|---|
| ECM | 100–299 | 1.5%–2.99% | Rise from €/$1,000 at month 2 to €/$100,000 at month 19+ |
| HECM | 300+ | 3%+ | Rise from €/$1,000 at month 2 to €/$200,000 at month 19+ |

**What this means:** small merchants rarely reach these minimum counts on their own. **The provider carries the risk across its whole merchant portfolio**, along with the operational cost of handling disputes. That supports framing the payment provider as the buyer.

## 3. How disputes are handled today

| Option | How it works | Pricing | Gap for a small merchant |
|---|---|---|---|
| Do nothing / accept | The merchant loses the amount plus the £20 fee | £0 extra | Lost revenue; the dispute ratio still rises |
| Manual response in the provider dashboard | The merchant reads the reason code and uploads evidence | £20 counter fee, refunded on a win | Needs scheme knowledge the merchant doesn't have. This is the problem in our PRD. |
| Provider-built AI (Stripe Smart Disputes) | An AI rules engine builds an evidence packet from Stripe's data and auto-submits it before the deadline | 30% of the amount, only on wins | Only for that provider's merchants and only for eligible disputes; the merchant has little visibility of why |
| Third-party vendors (Chargeflow, Justt, Chargebacks911 and others) | Connect to the provider or store and fight disputes for the merchant | Usually a success fee (e.g. 25%), plus add-ons for alerts and prevention | Success fees take a large share of small disputes; integrations focus on large platforms such as Shopify and Stripe |
| Pre-dispute alerts (Ethoca, Verifi/RDR) | Refund before a dispute is filed so it doesn't count | Per-alert fee (e.g. $29 per deflected chargeback via Chargeflow) | Prevention, not triage. It complements this tool rather than replacing it. |

**What this means:**

- **The market already exists and is moving to AI.** Stripe already offers AI-powered Smart Disputes, so "AI evidence recommendation" on its own isn't a differentiator.
- **Where this tool fits:**
  - Providers that don't have their own tool, such as smaller acquirers, POS and SMB payment providers, and marketplaces.
  - A **transparent** triage the merchant can see and override: the category, why, cited rules and a checklist.
  - Routing to a person when confidence is low.
- **Pricing benchmarks** for the business case: 25–30% success fees, against a triage cost below 1p per case.

## 4. Open questions to check before using these figures

1. The VAMP threshold and fee for UK merchants in 2026 (sources disagree: 0.9% or 1.5%; $8 or $10).
2. UK-specific dispute win rates. The 44.6% is mostly US data.
3. The share of disputes small merchants never respond to. There's no named public source yet, so it will be treated as an assumption.
4. Staff time per dispute for a small merchant. There's no public source; it will be treated as an assumption.

## Sources

- Stripe UK pricing: https://stripe.com/gb/pricing
- Stripe UK pricing update (Apr 2023): https://support.stripe.com/questions/pricing-updates-for-businesses-in-the-united-kingdom
- Stripe Smart Disputes docs: https://docs.stripe.com/disputes/smart-disputes
- Stripe disputes analytics docs: https://docs.stripe.com/payments/analytics/disputes
- Checkout.com, Update to VAMP (Jun 2026): https://support.checkout.com/hc/en-us/articles/26990138066450-Update-to-the-Visa-Acquirer-Monitoring-Program-VAMP
- Trust Payments, VAMP merchant guidance (Apr 2026): https://help.trustpayments.com/hc/en-us/articles/34158381255953-VAMP-Merchant-Guidance
- Justt, VAMP threshold changes (Apr 2026): https://justt.ai/blog/visa-vamp-threshold-changes-april-2026/
- Chargebacks911, Mastercard chargeback thresholds: https://chargebacks911.com/mastercard-chargeback-threshold/
- Redo, Chargeback statistics 2026 (cites Chargebacks911, LexisNexis, Visa, Juniper): https://redo.com/resources/articles/chargebacks/chargeback-statistics
- Redo, Chargeflow pricing: https://redo.com/resources/articles/comparisons/chargeflow-pricing
