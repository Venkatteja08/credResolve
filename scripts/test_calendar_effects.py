import pandas as pd
import numpy as np

payments = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)
payments['event_at_dt'] = pd.to_datetime(payments['event_at'], errors='coerce')
payments['date'] = payments['event_at_dt'].dt.date
payments['month'] = payments['event_at_dt'].dt.to_period('M')

succ = payments[payments['payment_status'] == 'SUCCESS']

m_daily = succ.groupby('month').agg(
    total_amount=('amount', 'sum'),
    payment_count=('amount', 'count'),
    active_days=('date', 'nunique')
)
m_daily['daily_run_rate_amount'] = m_daily['total_amount'] / m_daily['active_days']
m_daily['daily_run_rate_count'] = m_daily['payment_count'] / m_daily['active_days']
m_daily['total_amount_mom_%'] = m_daily['total_amount'].pct_change() * 100
m_daily['daily_run_rate_mom_%'] = m_daily['daily_run_rate_amount'].pct_change() * 100

print("=== DAILY RUN RATE ANALYSIS (SUCCESS PAYMENTS) ===")
print(m_daily)

# Now check deduplicated payments
succ_dedup = payments[payments['payment_status'] == 'SUCCESS'].drop_duplicates(subset=['payment_reference'])
m_dedup = succ_dedup.groupby('month').agg(
    total_amount=('amount', 'sum'),
    payment_count=('amount', 'count'),
    active_days=('date', 'nunique')
)
m_dedup['daily_run_rate_amount'] = m_dedup['total_amount'] / m_dedup['active_days']
m_dedup['total_amount_mom_%'] = m_dedup['total_amount'].pct_change() * 100
m_dedup['daily_run_rate_mom_%'] = m_dedup['daily_run_rate_amount'].pct_change() * 100

print("\n=== DAILY RUN RATE ANALYSIS (SUCCESS DEDUPLICATED BY PAYMENT_REFERENCE) ===")
print(m_dedup)
