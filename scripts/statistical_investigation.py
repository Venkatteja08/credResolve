import sqlite3
import pandas as pd
import numpy as np

conn = sqlite3.connect("golden_collections.db")

print("=== PART 3: STATISTICAL INVESTIGATION & SIMPSON'S PARADOX ===")

# 1. Simpson's Paradox: Risk Segments & Loan Types
acc_summary = pd.read_sql_query("SELECT * FROM fact_account_summary", conn)

print("\n--- Recovery Conversion by Risk Segment ---")
risk_grp = acc_summary.groupby('risk_segment').agg(
    total_accounts=('account_id', 'count'),
    recovered_accounts=('is_recovered', 'sum'),
    conversion_rate=('is_recovered', 'mean'),
    total_recovered=('total_net_recovery', 'sum'),
    avg_recovered_per_payer=('total_net_recovery', lambda s: s[s > 0].mean())
)
risk_grp['conversion_pct'] = risk_grp['conversion_rate'] * 100.0
print(risk_grp[['total_accounts', 'recovered_accounts', 'conversion_pct', 'total_recovered', 'avg_recovered_per_payer']])

print("\n--- Recovery Conversion by Loan Type ---")
loan_grp = acc_summary.groupby('loan_type').agg(
    total_accounts=('account_id', 'count'),
    recovered_accounts=('is_recovered', 'sum'),
    conversion_rate=('is_recovered', 'mean'),
    total_recovered=('total_net_recovery', 'sum'),
    avg_recovered_per_payer=('total_net_recovery', lambda s: s[s > 0].mean())
)
loan_grp['conversion_pct'] = loan_grp['conversion_rate'] * 100.0
print(loan_grp[['total_accounts', 'recovered_accounts', 'conversion_pct', 'total_recovered', 'avg_recovered_per_payer']])

print("\n--- Cross-Tab: Risk Segment x Loan Type Conversion Rate (%) ---")
ct = pd.crosstab(acc_summary['risk_segment'], acc_summary['loan_type'], values=acc_summary['is_recovered'], aggfunc='mean') * 100
print(ct.round(2))

# 2. Shift-Share / Mix Effects Decomposition
# Monthly portfolio recovery
payments = pd.read_sql_query("SELECT * FROM fact_payments_success", conn)
payments['event_at_dt'] = pd.to_datetime(payments['event_at'])
payments['payment_month'] = payments['event_at_dt'].dt.to_period('M').astype(str)

acc_pay = payments.merge(acc_summary[['account_id', 'risk_segment', 'loan_type', 'dpd_bucket']], on='account_id', how='left')

print("\n--- Monthly Recovery by Risk Segment (Rs Cr) ---")
m_risk = pd.crosstab(acc_pay['payment_month'], acc_pay['risk_segment'], values=acc_pay['amount'] / 1e7, aggfunc='sum')
print(m_risk.round(2))

print("\n--- Monthly Recovery by Loan Type (Rs Cr) ---")
m_loan = pd.crosstab(acc_pay['payment_month'], acc_pay['loan_type'], values=acc_pay['amount'] / 1e7, aggfunc='sum')
print(m_loan.round(2))

# 3. Attribution-Window Bias
calls = pd.read_sql_query("SELECT call_id, account_id, event_at_ist FROM fact_calls", conn)
calls['call_dt'] = pd.to_datetime(calls['event_at_ist'])
p_sample = payments.head(3000).copy()
c_sample = calls[calls['account_id'].isin(p_sample['account_id'])].copy()

merged_tp = p_sample.merge(c_sample, on='account_id', how='inner')
merged_tp['diff_days'] = (pd.to_datetime(merged_tp['event_at']) - merged_tp['call_dt']).dt.total_seconds() / 86400.0
prior_touches = merged_tp[merged_tp['diff_days'] >= 0]

print("\nAttribution Coverage by Window Size (Voice Calls to Payments):")
for window in [1, 7, 14, 30]:
    in_win = prior_touches[prior_touches['diff_days'] <= window]
    attributed_payments = in_win['payment_id'].nunique()
    pct = (attributed_payments / len(p_sample)) * 100.0
    print(f"  Window <= {window:2d} days: Attributed Payments = {attributed_payments:5d} / {len(p_sample)} ({pct:5.1f}%)")

# 4. PART 4: COUNTERFACTUAL ESTIMATION (Legacy vs Modern Targeting)
dt_full = pd.read_sql_query("""
    SELECT 
        dt.account_id,
        c.strategy_version
    FROM fact_daily_targeting dt
    JOIN dim_campaigns c ON dt.campaign_id = c.campaign_id
""", conn)

strat_per_acc = dt_full.groupby('account_id')['strategy_version'].unique()
legacy_only = strat_per_acc[strat_per_acc.apply(lambda x: len(x) == 1 and x[0] == 'legacy')].index
modern_exposed = strat_per_acc[strat_per_acc.apply(lambda x: any(v in ['v1', 'v2', 'v3'] for v in x))].index

print(f"\nCounterfactual Groups:")
print(f"  Control Group (Legacy targeting only): {len(legacy_only)} accounts")
print(f"  Treatment Group (Modern v1-v3 targeting): {len(modern_exposed)} accounts")

acc_summary['group'] = 'Untargeted'
acc_summary.loc[acc_summary['account_id'].isin(legacy_only), 'group'] = 'Control (Legacy Only)'
acc_summary.loc[acc_summary['account_id'].isin(modern_exposed), 'group'] = 'Treatment (Modern v1-v3)'

comp_outcomes = acc_summary[acc_summary['group'].isin(['Control (Legacy Only)', 'Treatment (Modern v1-v3)'])].groupby('group').agg(
    account_count=('account_id', 'count'),
    mean_outstanding=('outstanding_amount', 'mean'),
    conversion_rate=('is_recovered', 'mean'),
    mean_recovery=('total_net_recovery', 'mean'),
    recovery_rate_pct=('recovery_rate_pct', 'mean')
)
comp_outcomes['conversion_pct'] = comp_outcomes['conversion_rate'] * 100.0
print("\nCounterfactual Comparison: Outcomes by Group")
print(comp_outcomes[['account_count', 'mean_outstanding', 'conversion_pct', 'mean_recovery', 'recovery_rate_pct']])

conv_treat = acc_summary[acc_summary['group'] == 'Treatment (Modern v1-v3)']['is_recovered']
conv_ctrl = acc_summary[acc_summary['group'] == 'Control (Legacy Only)']['is_recovered']

diff = conv_treat.mean() - conv_ctrl.mean()
se = np.sqrt(conv_treat.var() / len(conv_treat) + conv_ctrl.var() / len(conv_ctrl))
z_stat = diff / se
print(f"\nDifference in Conversion (Treatment - Control): {diff*100:.3f}%")
print(f"Standard Error: {se*100:.3f}%, Z-stat: {z_stat:.3f}")

conn.close()
