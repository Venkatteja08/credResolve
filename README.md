# Collections Analytics & Forensic Investigation Engine
### Executive Portfolio Audit (30,000 Accounts) & ₹10 Cr Capital Deployment Analysis

[![Forensics](https://img.shields.io/badge/Forensic_Audit-11%25_Claim_Debunked-crimson.svg)](#the-11-recovery-improvement-myth-debunked)
[![Database](https://img.shields.io/badge/Golden_Database-SQLite_Medallion-blue.svg)](#golden-dataset--pipeline)
[![Capital Allocation](https://img.shields.io/badge/₹10_Cr_Investment-ML_Targeting_(248%25_ROI)-emerald.svg)](#where-should-we-invest-10-cr)

---

## Executive Overview & Master Verdict

Management reported to executive leadership that **"Recovery has improved by 11% month-on-month."** Leadership expressed skepticism and commissioned this forensic evaluation.

### Key Finding:
**The claimed 11% improvement is entirely FALSE.**  
The apparent jump from February to March 2026 was driven by:
1. **Calendar Length Discrepancy (10.71% Natural Artifact):** February had 28 operating days; March had 31 operating days. A 3-day difference automatically creates an ~10.7% volume surge with zero operational change.
2. **Double-Counted Gateway Retries (₹17.19 Cr Ghost Recovery):** 4,678 duplicate payment records and 2,033 payment references with multiple `SUCCESS` confirmations were logged by ingestion pipelines, inflating raw recovery by ₹17.19 Cr.
3. **Stagnant Operational Fundamentals:** On an independent, daily run-rate normalized basis (Net Settled Cash / Active Operating Days), March collections rose by only **+0.25%** (essentially flat), and April dropped by **-4.58%**. Underlying contact rates (**19.8%**), RPC (**19.5%**), and PTP kept rates (**24.7%**) were flat across the 8-month period.
4. **Targeting Policy Ineffectiveness:** The targeting strategy changes introduced midway through the year produced **0.00% incremental uplift** ($\tau = -0.188\%, p = 0.825$).

### Strategic Capital Recommendation:
Deploy the **₹10 Cr investment into Option 4: Better Borrower Targeting (Machine Learning Propensity & Behavioral Timing Engine)** to deliver **₹34.8 Cr in incremental annual recovery**, an **ROI of 248%**, and a **6.8-month break-even horizon**.

---

## Quick Navigation & Deliverables Index

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **1. SQL Repository** | [`sql/`](sql/) | Production SQL: DDL, cleaning, entity resolution, transformations, KPIs, and forensics. |
| **2. Analysis Notebook** | [`notebook/collections_deep_dive_analysis.ipynb`](notebook/collections_deep_dive_analysis.ipynb) | Fully executed Jupyter Notebook with reasoning, statistics, and tables. |
| **3. Golden Dataset Pipeline** | [`pipeline/build_golden_dataset.py`](pipeline/build_golden_dataset.py) | End-to-end reproducible pipeline writing to `golden_collections.db`. |
| **4. Data Quality Report** | [`reports/data_quality_report.md`](reports/data_quality_report.md) | Exhaustive DQ audit: Raw $\to$ Rejected $\to$ Golden records & forensics. |
| **5. Executive Dashboard** | [`dashboard/executive_dashboard.html`](dashboard/executive_dashboard.html) | Standalone interactive 60-second C-Suite cockpit with ROI simulator. |
| **6. Executive Memo** | [`reports/executive_memo.md`](reports/executive_memo.md) | 2-page C-Level briefing addressing the 5 core leadership questions. |
| **7. Architecture Diagram** | [`architecture/production_analytics_architecture.md`](architecture/production_analytics_architecture.md) | Medallion Lakehouse design, data contracts, lineage, and SLAs. |

---

## Core Findings: Addressing Leadership's Four Questions

### 1. What Happened?
* **When:** February 2026 $\to$ March 2026.
* **What Appeared to Happen:** Successful collections rose from ₹17.41 Cr (Feb) to ₹19.32 Cr (Mar), a reported **+10.99%** MoM increase.
* **What Actually Happened:** Normalizing for operating days (28 days in Feb vs 31 days in Mar), the daily collections run rate went from **₹62.18 Lakhs/day** to **₹62.33 Lakhs/day**—a negligible variance of **+0.25%**. In April, daily collections fell by **-4.58%**.
* **Which Metrics Are Misleading:** Gross unadjusted monthly payments, unconstrained contact rates (inflated by dispositions on unanswered calls), and raw targeting conversion (inflated by denominator gaming).
* **Which Metrics Are Genuinely Improving:** None. The portfolio performance was strictly stationary with random noise.

---

### 2. Why Did It Happen? (Driver Classification)

| Potential Driver | Impact & Evidence | Epistemic Classification |
| :--- | :--- | :---: |
| **Calendar Days (28 vs 31)** | +10.71% natural arithmetic surge from 3 extra operating days in March. | **FACT** |
| **Duplicate Payment Ingestion** | 2,033 references with multiple `SUCCESS` events; ₹17.19 Cr double-counted. | **FACT** |
| **Timezone Logging Distortion** | 66.7% of calls logged in UTC/Dubai without offset, placing calls outside IST prime hours. | **FACT** |
| **Phantom Dispositions** | 79.9% of dispositions (6,370 PTPs) were logged on calls where borrower never answered. | **FACT** |
| **Portfolio Mix Shifts** | Risk segment and loan type mix remained stationary across all 8 months (shift-share $\Delta < 0.08\%$). | **STRONG EVIDENCE** |
| **Targeting Strategy Lift** | Modern campaigns (`v1–v3`) vs legacy control produced $\tau = -0.188\%$ ($p = 0.825$). | **STRONG EVIDENCE** |
| **Agent Tenure & Capacity** | 1,099 employees with 596-day avg tenure; productivity capped by 20% dialer contact rate. | **STRONG EVIDENCE** |
| **Telephony Vendor Differences** | Contact rates across Airtel, Exotel, Twilio, Knowlarity, TataTele all sit at 19.5%–20.7%. | **CORRELATION** |
| **Borrower Self-Cure Propensity** | 92.7% of payments occur $>7$ days away from any outreach call (organic settlement). | **HYPOTHESIS / MODEL** |

---

### 3. Is the Reported 11% Improvement Real?

**NO.** We challenged the 9 historical operational metrics and established independent definitions:

1. **Contact Rate:** Challenged naive disposition counts. True Contact Rate = $\frac{\text{Answered Calls (duration > 0)}}{\text{Dialer Attempts}} = \mathbf{19.8\%}$ (Flat).
2. **Right Party Contact (RPC):** Challenged unverified dispositions. True RPC = Verified borrower contact / accounts dialed = $\mathbf{19.5\%}$ (Flat).
3. **PTP Rate:** Replaced phantom dispositions. True PTP Rate = Verified commitments / RPCs = $\mathbf{27.8\%}$.
4. **PTP Kept Rate:** Audited ledger settlements against promised dates. True Kept Rate = $\mathbf{24.7\%}$ (Flat).
5. **Recovery Rate:** Net settled cash deduplicated on `payment_reference` divided by static outstanding balance = $\mathbf{10.96\%}$ annualized (Stagnant).
6. **Recovery per Account:** Measured against static 30,000 accounts = **₹5,456/account** (Prevents denominator gaming).
7. **Recovery per Agent-Hour:** Attributed voice cash / active logged-in hours = **₹1,470/agent-hour**.
8. **Cost per ₹ Recovered:** Fully loaded operational expenses / net cash = **₹0.041 per Rupee** recovered.
9. **Channel Conversion:** Replaced unconstrained attribution with a tight **7-day post-touchpoint window**, revealing only **7.3%** of cash was outreach-driven.

---

### 4. Where Should We Invest ₹10 Cr?

Leadership can invest the ₹10 Cr in only one area. Below is the comparative financial model:

```
+--------------------------------+-----------+-------------------+-------------+------------------+---------------+-------------------------------+
| Investment Alternative         | Cost (Cr) | Inc. Recovery(Cr) | 1-Yr ROI(%) | Break-Even (Mos) | Downside ROI  | Strategic Verdict             |
+--------------------------------+-----------+-------------------+-------------+------------------+---------------+-------------------------------+
| 4. ML Borrower Targeting       |  ₹10.0 Cr |      ₹34.8 Cr     |    248%     |     6.8 Mos      |     +85%      | RECOMMENDED: Maximum ROI & Lift|
| 1. Telephony Infrastructure    |  ₹10.0 Cr |      ₹28.5 Cr     |    185%     |     8.5 Mos      |     +40%      | High Capex for dialer alone   |
| 3. AI Voice Automation         |  ₹10.0 Cr |      ₹24.0 Cr     |    140%     |    10.5 Mos      |     +10%      | Scalable, but early adoption  |
| 5. WhatsApp/Digital Messaging  |  ₹10.0 Cr |      ₹21.5 Cr     |    115%     |    11.2 Mos      |      -5%      | Ineffective for high DPD      |
| 2. More Collection Agents      |  ₹10.0 Cr |      ₹16.2 Cr     |     62%     |    15.0 Mos      |     -35%      | REJECT: 20% contact bottleneck|
| 6. Field Operations Expansion  |  ₹10.0 Cr |      ₹14.5 Cr     |     45%     |    16.5 Mos      |     -50%      | REJECT: High unit friction    |
+--------------------------------+-----------+-------------------+-------------+------------------+---------------+-------------------------------+
```

#### Why Better Borrower Targeting Wins:
Baseline targeting is currently **100% random**—HIGH risk, LOW risk, and NPA accounts all recover at the exact same ~40% rate. Deploying ₹10 Cr to build an **Enterprise ML Propensity & Timing Engine**:
* Predicts borrower repayment probability and prioritizes high-yield accounts (lifting yield to 48.5%).
* Matches borrowers to optimal channels (automated WhatsApp for credit cards/BNPL, voice agents for high-ticket personal/auto loans).
* Times outreaches to salary cycles (1st–5th of each month) and local IST prime hours (10 AM–6 PM).
* **Expected 1-Yr Incremental Cash:** **₹34.8 Cr** | **ROI:** **248%** | **Break-Even:** **6.8 Months** | **Downside Floor:** **+85% ROI**.

---

## Production Architecture & Medallion Pipeline

```
Raw Sources (PBX, Core LMS, Gateway Webhooks)
   ↓ (Ingestion Contracts, SHA-256 Idempotency, DLQ)
Staging Layer (Append-only Parquet, 72-hr Sliding Window)
   ↓ (Txn-Deduplication, UTC→IST Conversion, Entity Resolution)
Silver Clean Layer (clean_payments, clean_calls, dim_agent_crosswalk)
   ↓ (Kimball Dimensional Modeling)
Gold Analytical Layer (dim_accounts_golden, fact_settled_cash, fact_omnichannel)
   ↓ (dbt Semantic Layer & Anomaly Watchdog)
Serving & C-Suite Executive Cockpit (Daily Run Rate, 60s Decision Dashboard)
```

See [`architecture/production_analytics_architecture.md`](architecture/production_analytics_architecture.md) for full data contracts, schema definitions, and SLAs.

---

## Reproducibility & How to Run

### 1. Requirements
* Python 3.10+
* Standard scientific stack: `pandas`, `numpy`, `matplotlib`, `sqlite3`

### 2. Rebuild the Golden Dataset
```bash
python pipeline/build_golden_dataset.py
```
Outputs `golden_collections.db` and CSV files in `golden_dataset/`.

### 3. Verify Production SQL Reproducibility
```bash
python pipeline/verify_sql_scripts.py
```
Validates all 6 production SQL files in [`sql/`](sql/) against staging data.

### 4. Open the Executive Dashboard
Open [`dashboard/executive_dashboard.html`](dashboard/executive_dashboard.html) directly in any web browser to view the interactive C-suite cockpit and ROI simulator.

---

*Authored by the Quantitative Analytics & Forensics Team for Executive Leadership Review.*
