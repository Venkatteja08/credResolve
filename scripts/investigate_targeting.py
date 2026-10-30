import pandas as pd
import numpy as np

print("="*60)
print("INVESTIGATING TARGETING STRATEGY & DENOMINATOR MANIPULATION")
print("="*60)

dt = pd.read_csv("collections_30k_dataset/daily_targeting.csv", low_memory=False)
dt['target_date_dt'] = pd.to_datetime(dt['target_date'])
dt['month'] = dt['target_date_dt'].dt.to_period('M')

accs = pd.read_csv("collections_30k_dataset/accounts.csv", low_memory=False)
camps = pd.read_csv("collections_30k_dataset/campaigns.csv", low_memory=False)

dt_acc = dt.merge(accs, on='account_id', how='left')
dt_acc_camp = dt_acc.merge(camps, on='campaign_id', how='left')

print("Monthly targeting count:")
print(dt.groupby('month').size())

print("\nTargeting by Risk Segment over months:")
print(pd.crosstab(dt_acc['month'], dt_acc['risk_segment'], normalize='index') * 100)

print("\nTargeting by Loan Type over months:")
print(pd.crosstab(dt_acc['month'], dt_acc['loan_type'], normalize='index') * 100)

print("\nTargeting by DPD distribution over months:")
dt_acc['dpd_bucket'] = pd.cut(dt_acc['dpd'], bins=[-1, 30, 60, 90, 180, 9999], labels=['0-30', '31-60', '61-90', '91-180', '180+'])
print(pd.crosstab(dt_acc['month'], dt_acc['dpd_bucket'], normalize='index') * 100)

print("\nMean DPD of targeted accounts over months:")
print(dt_acc.groupby('month')['dpd'].agg(['count', 'mean', 'median']))

print("\nTargeting by Campaign Strategy Version over months:")
print(pd.crosstab(dt_acc_camp['month'], dt_acc_camp['strategy_version'], normalize='index') * 100)

print("\nRecommended Channel over months:")
print(pd.crosstab(dt_acc['month'], dt_acc['recommended_channel'], normalize='index') * 100)

print("\nTargeting Status over months:")
print(pd.crosstab(dt_acc['month'], dt_acc['status_x'], normalize='index') * 100)

print("\n" + "="*60)
print("PAYMENT ATTRIBUTION & CONVERSION INVESTIGATION")
print("="*60)
# Look at payments vs accounts
p = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)
p['event_at_dt'] = pd.to_datetime(p['event_at'])
p['month'] = p['event_at_dt'].dt.to_period('M')

# Check how many distinct accounts paid per month (deduplicated success payments)
p_succ = p[p['payment_status'] == 'SUCCESS'].drop_duplicates('payment_reference')
paid_accs_m = p_succ.groupby('month')['account_id'].nunique()
targeted_accs_m = dt.groupby('month')['account_id'].nunique()

conv_df = pd.DataFrame({'targeted_accounts': targeted_accs_m, 'paying_accounts': paid_accs_m})
conv_df['conversion_rate_%'] = (conv_df['paying_accounts'] / conv_df['targeted_accounts']) * 100
conv_df['total_collected'] = p_succ.groupby('month')['amount'].sum()
conv_df['collected_per_targeted'] = conv_df['total_collected'] / conv_df['targeted_accounts']
conv_df['collected_per_payer'] = conv_df['total_collected'] / conv_df['paying_accounts']
print(conv_df)

# Check overlap of paying accounts with targeted accounts
p_succ_dt = p_succ.merge(dt, on='account_id', how='left')
print("\nPercentage of paying accounts that were targeted in daily_targeting:")
print(p_succ['account_id'].isin(dt['account_id']).mean() * 100)
