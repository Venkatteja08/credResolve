import pandas as pd
import numpy as np

payments = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)
payments['event_at_dt'] = pd.to_datetime(payments['event_at'], errors='coerce')
payments['month'] = payments['event_at_dt'].dt.to_period('M')

print("=== PAYMENT METRICS BY MONTH ===")
for status in ['ALL', 'SUCCESS', 'SUCCESS_DEDUP_REF']:
    if status == 'ALL':
        df_p = payments
    elif status == 'SUCCESS':
        df_p = payments[payments['payment_status'].str.upper() == 'SUCCESS']
    elif status == 'SUCCESS_DEDUP_REF':
        df_p = payments[payments['payment_status'].str.upper() == 'SUCCESS'].drop_duplicates(subset=['payment_reference'])
    
    m = df_p.groupby('month')['amount'].agg(count='count', total_recovery='sum', avg_payment='mean')
    m['mom_growth_%'] = m['total_recovery'].pct_change() * 100
    print(f"\n--- {status} ---")
    print(m)

# Let's check how the business might calculate recovery rate:
# Is it recovery divided by target accounts? Or recovery divided by outstanding?
# Or did they look at a specific subset of months?
# Let's inspect payments date range
print("\nPayments min date:", payments['event_at_dt'].min(), "max date:", payments['event_at_dt'].max())

# Let's check account_status_history
ash = pd.read_csv("collections_30k_dataset/account_status_history.csv", low_memory=False)
print("\nAccount status history head:")
print(ash.head(10))
ash['event_at_dt'] = pd.to_datetime(ash['event_at'], errors='coerce')
ash['recorded_at_dt'] = pd.to_datetime(ash['recorded_at'], errors='coerce')
print("Status history event_at range:", ash['event_at_dt'].min(), "to", ash['event_at_dt'].max())
print("Status history statuses:\n", ash['status'].value_counts())

# Let's inspect campaigns and strategy changes
campaigns = pd.read_csv("collections_30k_dataset/campaigns.csv", low_memory=False)
print("\nCampaign strategy versions:\n", campaigns['strategy_version'].value_counts())
print("\nCampaign channels:\n", campaigns['channel'].value_counts())
print("\nCampaigns sorted by start_at:")
print(campaigns.sort_values('start_at')[['campaign_id', 'campaign_name', 'channel', 'strategy_version', 'start_at', 'end_at']].head(20))
