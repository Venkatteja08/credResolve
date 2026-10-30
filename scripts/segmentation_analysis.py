import pandas as pd
import numpy as np

# Load tables
accounts = pd.read_csv("collections_30k_dataset/accounts.csv", low_memory=False)
borrowers = pd.read_csv("collections_30k_dataset/borrowers.csv", low_memory=False)
agents = pd.read_csv("collections_30k_dataset/agents.csv", low_memory=False)
agent_sessions = pd.read_csv("collections_30k_dataset/agent_sessions.csv", low_memory=False)
campaigns = pd.read_csv("collections_30k_dataset/campaigns.csv", low_memory=False)
calls = pd.read_csv("collections_30k_dataset/calls.csv", low_memory=False)
call_attempts = pd.read_csv("collections_30k_dataset/call_attempts.csv", low_memory=False)
vendor_tel = pd.read_csv("collections_30k_dataset/vendor_telephony.csv", low_memory=False)
payments = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)

# Clean payments: only valid SUCCESS deduplicated by payment_reference
payments_clean = payments[payments['payment_status'] == 'SUCCESS'].drop_duplicates('payment_reference').copy()
payments_clean['event_at_dt'] = pd.to_datetime(payments_clean['event_at'])
payments_clean['month'] = payments_clean['event_at_dt'].dt.to_period('M')

print("=== SEGMENTATION & STATISTICAL DRIVERS ===")

# 1. Accounts merge with Borrowers
acc_brw = accounts.merge(borrowers.drop_duplicates('borrower_id'), on='borrower_id', how='left')

# Payment recovery by Loan Type
acc_pay = payments_clean.groupby('account_id')['amount'].sum().reset_index()
acc_full = acc_brw.merge(acc_pay, on='account_id', how='left')
acc_full['amount'] = acc_full['amount'].fillna(0)
acc_full['has_paid'] = (acc_full['amount'] > 0).astype(int)

print("\nRecovery by Loan Type:")
print(acc_full.groupby('loan_type').agg(
    total_accounts=('account_id', 'count'),
    paid_accounts=('has_paid', 'sum'),
    conversion_rate=('has_paid', 'mean'),
    total_recovered=('amount', 'sum'),
    mean_recovery=('amount', 'mean')
))

print("\nRecovery by Risk Segment:")
print(acc_full.groupby('risk_segment').agg(
    total_accounts=('account_id', 'count'),
    paid_accounts=('has_paid', 'sum'),
    conversion_rate=('has_paid', 'mean'),
    total_recovered=('amount', 'sum'),
    mean_recovery=('amount', 'mean')
))

print("\nRecovery by DPD Buckets:")
acc_full['dpd_bucket'] = pd.cut(acc_full['dpd'], bins=[-1, 30, 60, 90, 180, 9999], labels=['0-30', '31-60', '61-90', '91-180', '180+'])
print(acc_full.groupby('dpd_bucket').agg(
    total_accounts=('account_id', 'count'),
    paid_accounts=('has_paid', 'sum'),
    conversion_rate=('has_paid', 'mean'),
    total_recovered=('amount', 'sum'),
    mean_recovery=('amount', 'mean')
))

print("\nRecovery by Top 5 States:")
top_states = acc_full['state'].value_counts().head(5).index
print(acc_full[acc_full['state'].isin(top_states)].groupby('state').agg(
    total_accounts=('account_id', 'count'),
    paid_accounts=('has_paid', 'sum'),
    conversion_rate=('has_paid', 'mean'),
    total_recovered=('amount', 'sum')
))

# 2. Telephony Vendor performance
calls_vnd = calls.merge(vendor_tel[['vendor_id', 'vendor_name']].drop_duplicates('vendor_id'), on='vendor_id', how='left')
print("\nCalls contact rate by Vendor Name:")
print(calls_vnd.groupby('vendor_name').agg(
    total_calls=('call_id', 'count'),
    answered_calls=('call_status', lambda s: (s == 'ANSWERED').sum()),
    contact_rate=('call_status', lambda s: (s == 'ANSWERED').mean()),
    avg_duration_sec=('duration_sec', 'mean')
))

# 3. Agent performance & tenure
agents_clean = agents.drop_duplicates('agent_id').copy()
agents_clean['joined_dt'] = pd.to_datetime(agents_clean['joined_at'])
agents_clean['tenure_days'] = (pd.to_datetime('2026-08-08') - agents_clean['joined_dt']).dt.days
print("\nAgent tenure summary:\n", agents_clean['tenure_days'].describe())

# 4. Attempt frequency in call_attempts
print("\nCall attempt success by Attempt Number:")
print(call_attempts.groupby('attempt_no').agg(
    total_attempts=('attempt_id', 'count'),
    connected=('attempt_status', lambda s: (s == 'CONNECTED').sum()),
    connect_rate=('attempt_status', lambda s: (s == 'CONNECTED').mean())
))

# 5. Calling time (Hour of Day in normalized Asia/Kolkata)
# Convert calls timestamp based on calls['timezone']
print("\nAnalyzing call times...")
calls_sample = calls.head(1000).copy()
print("Calls sample timezones:\n", calls_sample['timezone'].value_counts())
