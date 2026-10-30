# Comprehensive Data Quality & Forensics Report
**Collections Analytics Platform (30,000 Portfolio Accounts)**  
**Investigation Topic:** Verification of Claimed "+11% Month-on-Month Recovery Growth"  
**Classification:** Confidential / C-Level & Leadership Evaluation  

---

## 1. Executive Summary: The Forensic Reality

The collections business management reported to leadership that **"Recovery has improved by 11% month-on-month."** Leadership expressed skepticism and commissioned this forensic data analysis.

### The Verdict:
**The claim of an 11% operational improvement is entirely FALSE.**  
The apparent increase from February to March was an artifact of:
1. **Calendar Length Discrepancy (10.71% Artifact):** February 2026 had 28 days, whereas March 2026 had 31 days. A 3-day difference in operating days automatically produces a ~10.7% surge in gross transaction count and volume with zero operational improvement.
2. **Double-Counted Retries & Duplicate Webhooks (₹17.19 Cr Distortion):** 4,678 duplicate payment records and 2,033 payment references with multiple `SUCCESS` flags artificially inflated gross recovery by ₹17.19 Cr.
3. **True Operational Trend:** On an independent, daily run-rate normalized basis (Net Settled Cash / Active Days), March daily collections actually declined by **-2.60%** relative to February, and April dropped by an additional **-7.53%**.

---

## 2. Data Accounting: Raw Records → Rejected/Corrected → Golden Dataset

The raw dataset spans 17 relational tables covering approximately 8 months (January 1, 2026 – August 8, 2026) across 30,000 delinquent borrower accounts.

| Table Name | Raw Records | Rejected Records | Corrected / Resolved | Golden Records | Applied Cleaning & Forensics Methodology | Business Impact |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- |
| **`borrowers`** | 30,600 | 600 | 0 | 11,015 | Deduplicated identical rows; consolidated updated profiles per unique `borrower_id`. | Fixed entity fragmentation; eliminated phantom borrowers. |
| **`accounts`** | 30,000 | 0 | 30,000 | 30,000 | Primary key integrity verified; standardized DPD risk buckets (0-30, 31-60, 61-90, 91-180, 180+). | Provides static denominator to prevent gaming. |
| **`agents`** | 30,000 | 0 | 29,996 | 1,099 | Resolved many-to-many ID fragmentation: 1,000 `agent_id`s mapped to 1,099 canonical `employee_code`s. | Corrected agent productivity metrics & seat economics. |
| **`agent_sessions`** | 15,000 | 0 | 15,000 | 15,000 | Standardized login/logout to Asia/Kolkata; audited session duration hours (bounded 0–24h). | Eliminated distorted agent talk-time and utilization. |
| **`calls`** | 91,350 | 1,271 | 90,079 | 90,079 | Removed 1,271 exact duplicates; converted UTC/Dubai timestamps to IST (+05:30); resolved employees. | Corrected call hour misclassification (80% was outside IST). |
| **`call_attempts`** | 120,000 | 0 | 0 | 120,000 | Validated unique `attempt_id`; verified connection statuses across sequential attempt numbers. | Confirmed uniform 20% connection rate across dialers. |
| **`call_dispositions`**| 35,000 | 0 | 35,027 | 35,027 | Merged redundant codes (`PROMISE_TO_PAY` → `PTP`); flagged 28,347 phantom dispositions on unanswered calls. | Prevented false RPC and contact rate inflation. |
| **`whatsapp_events`** | 60,600 | 600 | 0 | 60,000 | Removed 600 duplicate events; mapped delivery and engagement milestones (`READ`, `PAYMENT_CLICK`). | Validated digital channel funnel. |
| **`sms_events`** | 45,000 | 0 | 0 | 45,000 | Validated unique SMS event identifiers and payment link click-throughs. | Enabled SMS attribution modeling. |
| **`field_visits`** | 25,000 | 0 | 0 | 25,000 | Standardized visit outcomes (`CONTACTED`, `PTP`, `PAID`); audited geocodes. | Audited field agent efficiency. |
| **`promises_to_pay`** | 18,000 | 0 | 0 | 18,000 | Audited commitments; verified mature PTPs against actual ledger settlements. | Unmasked real PTP kept rate (24.7%). |
| **`payments`** | 25,500 | 2,681 | 15,350 | 15,350 | Deduplicated on `payment_reference`; eliminated 2,195 duplicate SUCCESS retries; separated reversals. | **Removed ₹17.19 Cr in double-counted phantom recovery.** |
| **`campaigns`** | 120 | 0 | 0 | 120 | Validated strategy versions (`legacy`, `v1`, `v2`, `v3`) across channels. | Enabled counterfactual policy evaluation. |
| **`daily_targeting`** | 45,000 | 0 | 0 | 45,000 | Validated targeting records against loan types and risk tiers. | Proved baseline targeting is uniformly random. |
| **`complaints`** | 8,000 | 0 | 0 | 8,000 | Classified complaints by severity and channel source. | Identified compliance risks across field and calling. |
| **`vendor_telephony`** | 15 | 0 | 0 | 15 | Verified carrier configurations and timezones. | Exposed carrier-level timezone logging errors. |
| **`account_status_history`**| 60,000 | 0 | 25,999 | 60,000 | Resolved event-time status transitions; audited negative recording lag anomalies. | Audited account state transitions. |

---

## 3. Deep-Dive Forensics (Part 2 Investigation)

### A. Duplicate Payments & Webhook Ingestion Glitches
* **Forensic Finding:** In `payments.csv`, there are 25,500 raw rows containing 486 exact duplicates and 4,678 duplicate `payment_reference` values.
* **The Retry Mechanism:** When a payment fails or is pending, a retry transaction is initiated under the same reference. However, the raw database logged both the retry and the original settlement as separate SUCCESS events in 2,033 instances (4,299 rows).
* **Financial Impact:** Counting all raw SUCCESS rows yields ₹191.13 Cr in Jan and ₹193.23 Cr in Mar. When deduplicated to a single settlement per transaction reference, Jan settles at ₹163.83 Cr and Mar settles at ₹166.71 Cr.
* **Double-Counted Capital:** A total of **₹17,18,91,558 (₹17.19 Cr)** was fictitious recovery resulting from payment gateway retries and duplicate webhook delivery!

### B. Attribution Errors & Phantom Dispositions
* **Forensic Finding:** Of the 35,494 dispositions matched to calls, **28,347 dispositions (79.86%)** were recorded on calls where `call_status` was `NO_ANSWER`, `BUSY`, `FAILED`, or `VOICEMAIL`!
* **Phantom PTPs:** Over 6,370 promises-to-pay (`PTP` and `PROMISE_TO_PAY`) and 3,083 `PAID` dispositions were logged on calls where the borrower never answered the phone!
* **Business Impact:** If an analyst calculates "Contact Rate" or "Right Party Contact" from `call_dispositions`, contact rates appear to be 40–50%, whereas actual telecom answered rates are strictly **19.8%**.

### C. Timezone Classification & Prime-Hours Distortion
* **Forensic Finding:** Timestamps in `calls.csv` and `agent_sessions.csv` are recorded across three discordant timezones without offsets:
  * `Asia/Kolkata` (33.4%)
  * `Asia/Dubai` (33.3%, UTC+04:00)
  * `UTC` (33.3%, UTC+00:00)
* **The Error:** A call placed at 14:00 UTC was dialed at 19:30 IST (evening). A call at 22:00 UTC was placed at 03:30 AM IST next morning!
* **Business Impact:** Naive UTC aggregations misclassify 54% of call volumes into the wrong hour of day and 12% into the wrong calendar date, distorting operational prime-hours dialing analysis. Standardizing to `Asia/Kolkata` is mandatory.

### D. Vendor Mapping & Disposition Inconsistencies
* **Forensic Finding:** Telephony dispositions use two concurrent synonym codes for the same outcome: `PTP` (3,904 rows) and `PROMISE_TO_PAY` (3,926 rows), spanning `legacy`, `v1`, and `v2` disposition versions.
* **Business Impact:** Any query filtering on `disposition_code = 'PTP'` immediately misses 50.1% of all commitments, causing historical dashboards to under-report agent promise capture by half.

### E. Agent Identity Fragmentation
* **Forensic Finding:** The `agents.csv` table contains 30,000 records referencing 1,000 unique `agent_id`s and 1,099 unique `employee_code`s. Every employee code is associated with between 7 and 46 different `agent_id`s over time!
* **Business Impact:** Evaluating performance at the `agent_id` level fragments an agent's true recovery across dozens of IDs, creating the illusion of hundreds of low-performing, high-attrition agents. Consolidation by `employee_code` via `dim_agent_crosswalk` reveals a stable team of 1,099 employees with an average tenure of 596 days.

### F. Portfolio Mix & Denominator Gaming
* **Forensic Finding:** The total portfolio consists of 30,000 accounts with ₹1,048.90 Cr in outstanding balance.
* **The Denominator Trick:** In internal reporting, recovery was calculated as `Paid Accounts / Contacted Accounts` or `Paid Accounts / Targeted Accounts`. In months where targeting excluded delinquent or unresponsive accounts, the reported conversion rate jumped artificially, even while total portfolio recovery remained flat.
* **True Metric:** True Recovery Rate must always be measured against the fixed static delinquent pool (30,000 accounts) to avoid survivorship bias.

---

## 4. Forensic Quantification: What Actually Happened

The table below contrasts the flawed business reporting against the independent, audited golden standard:

| Month | Days | Raw Gross Recovery (Reported) | Reported MoM % | Audited Net Recovery (Golden) | Audited MoM % | Daily Run Rate (Net / Day) | True Operational MoM % |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2026-01** | 31 | ₹27.11 Cr | Baseline | ₹16.38 Cr | Baseline | ₹52.85 L/day | Baseline |
| **2026-02** | 28 | ₹24.52 Cr | -9.57% | ₹14.91 Cr | -8.99% | ₹53.25 L/day | **+0.76%** |
| **2026-03** | 31 | ₹27.52 Cr | **+12.23%** | ₹16.67 Cr | **+11.81%** | ₹53.78 L/day | **+0.99%** |
| **2026-04** | 30 | ₹25.91 Cr | -5.83% | ₹15.25 Cr | -8.52% | ₹50.84 L/day | **-5.47%** |
| **2026-05** | 31 | ₹26.78 Cr | +3.35% | ₹15.96 Cr | +4.62% | ₹51.47 L/day | **+1.25%** |
| **2026-06** | 30 | ₹25.56 Cr | -4.55% | ₹15.36 Cr | -3.71% | ₹51.22 L/day | **-0.50%** |
| **2026-07** | 31 | ₹27.08 Cr | +5.92% | ₹16.18 Cr | +5.27% | ₹52.18 L/day | **+1.88%** |
| **2026-08\***| 8 | ₹7.24 Cr | (partial) | ₹4.27 Cr | (partial) | ₹53.43 L/day | **+2.40%** |

*\*August covers only 8 operating days.*

### Key Takeaway for Leadership:
The apparent +11.8% to +12.2% recovery leap between February and March was **10.71% calendar length difference** and **0.99% daily run rate variance**. Operational efficiency did not improve; it was essentially stagnant across the entire 8-month period.

