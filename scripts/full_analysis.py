import pandas as pd
import numpy as np

# Load core datasets
accounts = pd.read_csv("collections_30k_dataset/accounts.csv", low_memory=False)
borrowers = pd.read_csv("collections_30k_dataset/borrowers.csv", low_memory=False)
agents = pd.read_csv("collections_30k_dataset/agents.csv", low_memory=False)
agent_sessions = pd.read_csv("collections_30k_dataset/agent_sessions.csv", low_memory=False)
campaigns = pd.read_csv("collections_30k_dataset/campaigns.csv", low_memory=False)
daily_targeting = pd.read_csv("collections_30k_dataset/daily_targeting.csv", low_memory=False)
calls = pd.read_csv("collections_30k_dataset/calls.csv", low_memory=False)
call_attempts = pd.read_csv("collections_30k_dataset/call_attempts.csv", low_memory=False)
call_dispositions = pd.read_csv("collections_30k_dataset/call_dispositions.csv", low_memory=False)
whatsapp = pd.read_csv("collections_30k_dataset/whatsapp_events.csv", low_memory=False)
sms = pd.read_csv("collections_30k_dataset/sms_events.csv", low_memory=False)
field_visits = pd.read_csv("collections_30k_dataset/field_visits.csv", low_memory=False)
ptp = pd.read_csv("collections_30k_dataset/promises_to_pay.csv", low_memory=False)
payments = pd.read_csv("collections_30k_dataset/payments.csv", low_memory=False)
complaints = pd.read_csv("collections_30k_dataset/complaints.csv", low_memory=False)
vendor_tel = pd.read_csv("collections_30k_dataset/vendor_telephony.csv", low_memory=False)
ash = pd.read_csv("collections_30k_dataset/account_status_history.csv", low_memory=False)

print("--- Data Loaded Successfully ---")

# Let's inspect date ranges and months across all activity tables
for name, df, col in [
    ('calls', calls, 'event_at'),
    ('call_attempts', call_attempts, 'event_at'),
    ('call_dispositions', call_dispositions, 'event_at'),
    ('whatsapp', whatsapp, 'event_at'),
    ('sms', sms, 'event_at'),
    ('field_visits', field_visits, 'event_at'),
    ('ptp', ptp, 'event_at'),
    ('payments', payments, 'event_at'),
    ('daily_targeting', daily_targeting, 'target_date'),
    ('agent_sessions', agent_sessions, 'login_at'),
    ('complaints', complaints, 'event_at')
]:
    dt = pd.to_datetime(df[col], errors='coerce')
    print(f"{name:18s} | Min: {dt.min()} | Max: {dt.max()} | Null dates: {dt.isna().sum()}")

# Inspect agent_sessions hours
agent_sessions['login_dt'] = pd.to_datetime(agent_sessions['login_at'])
agent_sessions['logout_dt'] = pd.to_datetime(agent_sessions['logout_at'])
agent_sessions['session_hours'] = (agent_sessions['logout_dt'] - agent_sessions['login_dt']).dt.total_seconds() / 3600.0
print("\nAgent session hours summary:\n", agent_sessions['session_hours'].describe())
agent_sessions['month'] = agent_sessions['login_dt'].dt.to_period('M')
agent_hours_m = agent_sessions.groupby('month')['session_hours'].sum()
print("\nTotal agent session hours by month:\n", agent_hours_m)

# Inspect calls metrics by month
calls['event_at_dt'] = pd.to_datetime(calls['event_at'])
calls['month'] = calls['event_at_dt'].dt.to_period('M')
calls_m = calls.groupby('month').agg(
    total_calls=('call_id', 'count'),
    answered_calls=('call_status', lambda s: (s == 'ANSWERED').sum()),
    total_duration_hrs=('duration_sec', lambda s: s.sum() / 3600.0)
)
calls_m['contact_rate_%'] = (calls_m['answered_calls'] / calls_m['total_calls']) * 100
print("\nCalls summary by month:\n", calls_m)

# Inspect attempts metrics by month
call_attempts['event_at_dt'] = pd.to_datetime(call_attempts['event_at'])
call_attempts['month'] = call_attempts['event_at_dt'].dt.to_period('M')
attempts_m = call_attempts.groupby('month').agg(
    total_attempts=('attempt_id', 'count'),
    connected_attempts=('attempt_status', lambda s: (s == 'CONNECTED').sum())
)
attempts_m['connection_rate_%'] = (attempts_m['connected_attempts'] / attempts_m['total_attempts']) * 100
print("\nAttempts summary by month:\n", attempts_m)

# Inspect PTP metrics by month
ptp['event_at_dt'] = pd.to_datetime(ptp['event_at'])
ptp['month'] = ptp['event_at_dt'].dt.to_period('M')
ptp_m = ptp.groupby('month').agg(
    total_ptp=('ptp_id', 'count'),
    kept_ptp=('status', lambda s: (s == 'KEPT').sum()),
    broken_ptp=('status', lambda s: (s == 'BROKEN').sum()),
    total_promised_amt=('promised_amount', 'sum')
)
ptp_m['ptp_kept_rate_%'] = (ptp_m['kept_ptp'] / ptp_m['total_ptp']) * 100
print("\nPTP summary by month:\n", ptp_m)

# Inspect WhatsApp & SMS events
whatsapp['month'] = pd.to_datetime(whatsapp['event_at']).dt.to_period('M')
wa_m = whatsapp.groupby('month').agg(
    total_wa=('whatsapp_event_id', 'count'),
    delivered_wa=('event_type', lambda s: (s == 'DELIVERED').sum()),
    read_wa=('event_type', lambda s: (s == 'READ').sum()),
    clicked_wa=('event_type', lambda s: (s == 'PAYMENT_CLICK').sum()),
    replied_wa=('event_type', lambda s: (s == 'REPLIED').sum())
)
print("\nWhatsApp summary by month:\n", wa_m)

sms['month'] = pd.to_datetime(sms['event_at']).dt.to_period('M')
sms_m = sms.groupby('month').agg(
    total_sms=('sms_event_id', 'count'),
    delivered_sms=('event_type', lambda s: (s == 'DELIVERED').sum()),
    clicked_sms=('event_type', lambda s: (s == 'CLICKED').sum())
)
print("\nSMS summary by month:\n", sms_m)

# Field visits summary
field_visits['month'] = pd.to_datetime(field_visits['event_at']).dt.to_period('M')
fv_m = field_visits.groupby('month').agg(
    total_visits=('visit_id', 'count'),
    contacted_visits=('outcome', lambda s: (s == 'CONTACTED').sum()),
    paid_visits=('outcome', lambda s: (s == 'PAID').sum()),
    ptp_visits=('outcome', lambda s: (s == 'PTP').sum())
)
print("\nField visits summary by month:\n", fv_m)
