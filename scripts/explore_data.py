import os
import glob
import pandas as pd
import numpy as np

print("--- 1. ROW COUNTS & BASIC METRICS ---")
for f in sorted(glob.glob("collections_30k_dataset/*.csv")):
    name = os.path.basename(f)
    if name == "data_dictionary.csv":
        continue
    df = pd.read_csv(f, low_memory=False)
    print(f"{name:30s} | Rows: {len(df):8d} | Unique rows: {len(df.drop_duplicates()):8d} | Dups: {len(df) - len(df.drop_duplicates()):6d}")

print("\n--- 2. PAYMENTS INVESTIGATION ---")
payments = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)
print("Payments columns:", payments.columns.tolist())
print("Payment status distribution:\n", payments['payment_status'].value_counts(dropna=False))
print("\nUnique payment_id:", payments['payment_id'].nunique(), "Unique payment_reference:", payments['payment_reference'].nunique())
print("Duplicates on payment_reference:", payments['payment_reference'].duplicated().sum())

payments['event_at_dt'] = pd.to_datetime(payments['event_at'], errors='coerce')
payments['month'] = payments['event_at_dt'].dt.to_period('M')

# Check raw sum by month
print("\nRaw sum by month (all statuses):")
raw_m = payments.groupby('month')['amount'].agg(['count', 'sum', 'mean'])
print(raw_m)
raw_m['sum_pct_change'] = raw_m['sum'].pct_change() * 100
print("\nRaw sum MoM % change:\n", raw_m[['sum', 'sum_pct_change']])

# Check sum by month for SUCCESS only
print("\nSuccessful payments by month:")
succ_m = payments[payments['payment_status'] == 'success'].groupby('month')['amount'].agg(['count', 'sum'])
succ_m['pct_change'] = succ_m['sum'].pct_change() * 100
print(succ_m)

# Deduplicated on payment_reference
succ_dedup = payments[payments['payment_status'] == 'success'].drop_duplicates(subset=['payment_reference'])
succ_dedup_m = succ_dedup.groupby('month')['amount'].agg(['count', 'sum'])
succ_dedup_m['pct_change'] = succ_dedup_m['sum'].pct_change() * 100
print("\nSuccessful Deduplicated (by payment_reference) by month:")
print(succ_dedup_m)

print("\n--- 3. ACCOUNTS & TARGETING INVESTIGATION ---")
accounts = pd.read_csv("collections_30k_dataset/accounts.csv", low_memory=False)
print("Accounts count:", len(accounts), "Unique account_id:", accounts['account_id'].nunique())
print("Loan types:\n", accounts['loan_type'].value_counts())
print("Risk segments:\n", accounts['risk_segment'].value_counts())
print("Statuses:\n", accounts['status'].value_counts())
print("Schema versions:\n", accounts['schema_version'].value_counts())

campaigns = pd.read_csv("collections_30k_dataset/campaigns.csv", low_memory=False)
print("\nCampaigns:\n", campaigns)

daily_targeting = pd.read_csv("collections_30k_dataset/daily_targeting.csv", low_memory=False)
print("\nDaily targeting shape:", daily_targeting.shape)
daily_targeting['target_date_dt'] = pd.to_datetime(daily_targeting['target_date'], errors='coerce')
print("Targeting date range:", daily_targeting['target_date_dt'].min(), "to", daily_targeting['target_date_dt'].max())
print("Targeting by campaign_id:\n", daily_targeting['campaign_id'].value_counts())

agents = pd.read_csv("collections_30k_dataset/agents.csv", low_memory=False)
print("\nAgents count:", len(agents), "Unique agent_id:", agents['agent_id'].nunique(), "Unique employee_code:", agents['employee_code'].nunique())
dup_emp = agents.groupby('employee_code')['agent_id'].nunique()
print("Employee codes with >1 agent_id:", (dup_emp > 1).sum())

dispositions = pd.read_csv("collections_30k_dataset/call_dispositions.csv", low_memory=False)
print("\nCall dispositions disposition_version:\n", dispositions['disposition_version'].value_counts())
print("Top 10 disposition codes:\n", dispositions['disposition_code'].value_counts().head(10))

vendor_tel = pd.read_csv("collections_30k_dataset/vendor_telephony.csv", low_memory=False)
print("\nVendor telephony:\n", vendor_tel)
