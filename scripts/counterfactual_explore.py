import pandas as pd
import numpy as np

camps = pd.read_csv("collections_30k_dataset/campaigns.csv")
print("Campaigns:")
print(camps['strategy_version'].value_counts())
print(camps.groupby('strategy_version')['start_at'].agg(['min', 'max']))
print(camps.groupby('strategy_version')['end_at'].agg(['min', 'max']))

dt = pd.read_csv("collections_30k_dataset/daily_targeting.csv")
dt_camp = dt.merge(camps, on='campaign_id', how='left')
dt_camp['target_date_dt'] = pd.to_datetime(dt_camp['target_date'])
dt_camp['month'] = dt_camp['target_date_dt'].dt.to_period('M')

print("\nTargeting volume by strategy version across months:")
print(pd.crosstab(dt_camp['month'], dt_camp['strategy_version']))

# What about payments on accounts targeted by strategy_version?
payments = pd.read_csv("collections_30k_dataset/payments.csv")
payments_succ = payments[payments['payment_status'] == 'SUCCESS'].drop_duplicates('payment_reference')

# Merge targeting with payments
# Let's see how accounts targeted under v1/v2/v3 vs legacy performed
p_by_acc = payments_succ.groupby('account_id')['amount'].sum().reset_index()

acc_targeting = dt_camp.groupby(['account_id', 'strategy_version']).size().unstack(fill_value=0)
print("\nAccounts targeted under each strategy version:\n", (acc_targeting > 0).sum())

# Check account overlap across strategies
print("Accounts targeted under legacy only vs modern versions:")
print("Total accounts targeted:", dt['account_id'].nunique())
