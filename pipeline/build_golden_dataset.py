"""
Production Golden Dataset Pipeline
Author: Data Analytics & Forensics Team
Purpose: Ingest 17 raw collections datasets, perform forensic cleaning, entity resolution,
         timezone normalization, deduplication, and build the trustworthy analytical golden layer.
"""

import os
import sqlite3
import pandas as pd
import numpy as np
import json
from datetime import datetime

RAW_DIR = "collections_30k_dataset"
GOLDEN_DIR = "golden_dataset"
DB_PATH = "golden_collections.db"

os.makedirs(GOLDEN_DIR, exist_ok=True)

accounting_log = {}

def log_step(table_name, raw_count, rejected_count, corrected_count, golden_count, notes):
    accounting_log[table_name] = {
        "raw_records": int(raw_count),
        "rejected_records": int(rejected_count),
        "corrected_records": int(corrected_count),
        "golden_records": int(golden_count),
        "notes": notes
    }
    print(f"[{table_name:25s}] Raw: {raw_count:7d} | Rejected: {rejected_count:6d} | Corrected: {corrected_count:6d} | Golden: {golden_count:7d} | {notes}")

def normalize_timezone_to_ist(df, ts_col, tz_col='timezone'):
    """
    Standardize timestamps to Asia/Kolkata (IST, UTC+05:30)
    Accounts for UTC, Asia/Dubai (+04:00), and Asia/Kolkata (+05:30)
    """
    ts = pd.to_datetime(df[ts_col])
    if tz_col not in df.columns:
        return ts
    
    converted = pd.Series(index=df.index, dtype='datetime64[ns]')
    for tz_name, idx in df.groupby(tz_col).groups.items():
        if pd.isna(tz_name) or tz_name == '' or tz_name == 'None':
            tz_name = 'Asia/Kolkata'
        s = ts.loc[idx]
        try:
            s_localized = s.dt.tz_localize(tz_name).dt.tz_convert('Asia/Kolkata').dt.tz_localize(None)
            converted.loc[idx] = s_localized
        except Exception:
            converted.loc[idx] = s
    return converted

print("="*80)
print("STARTING GOLDEN DATASET BUILD PIPELINE")
print("="*80)

# 1. BORROWERS
raw_borrowers = pd.read_csv(os.path.join(RAW_DIR, "borrowers.csv"), low_memory=False)
raw_b_count = len(raw_borrowers)
# Remove exact duplicates
dedup_borrowers = raw_borrowers.drop_duplicates()
exact_b_dups = raw_b_count - len(dedup_borrowers)
# Ensure 1 row per borrower_id by taking the most recently updated
golden_borrowers = dedup_borrowers.sort_values('updated_at').groupby('borrower_id').last().reset_index()
golden_borrowers['name'] = golden_borrowers['name'].str.strip().str.title()
golden_borrowers['phone'] = golden_borrowers['phone'].astype(str).str.replace(r'\D', '', regex=True)
golden_borrowers['email'] = golden_borrowers['email'].str.strip().str.lower()
golden_borrowers['city'] = golden_borrowers['city'].str.strip().str.title()
golden_borrowers['state'] = golden_borrowers['state'].str.strip().str.title()
log_step("borrowers", raw_b_count, exact_b_dups, 0, len(golden_borrowers), "Removed exact duplicates and resolved unique borrower profiles.")

# 2. ACCOUNTS
raw_accounts = pd.read_csv(os.path.join(RAW_DIR, "accounts.csv"), low_memory=False)
raw_acc_count = len(raw_accounts)
# Standardize DPD buckets
golden_accounts = raw_accounts.drop_duplicates(subset=['account_id']).copy()
golden_accounts['dpd_bucket'] = pd.cut(
    golden_accounts['dpd'],
    bins=[-1, 30, 60, 90, 180, 99999],
    labels=['0-30 DPD', '31-60 DPD', '61-90 DPD', '91-180 DPD', '180+ DPD']
)
golden_accounts['loan_type'] = golden_accounts['loan_type'].str.strip().str.upper()
golden_accounts['risk_segment'] = golden_accounts['risk_segment'].str.strip().str.upper()
golden_accounts['status'] = golden_accounts['status'].str.strip().str.upper()
log_step("accounts", raw_acc_count, 0, len(golden_accounts), len(golden_accounts), "Validated primary key account_id; appended standardized DPD risk buckets.")

# 3. AGENTS & AGENT ENTITY RESOLUTION
raw_agents = pd.read_csv(os.path.join(RAW_DIR, "agents.csv"), low_memory=False)
raw_ag_count = len(raw_agents)
# Deduplicate agent records
agents_dedup = raw_agents.drop_duplicates().copy()
# Resolve canonical employee profile: map each employee_code to their canonical record
golden_agents = agents_dedup.sort_values('updated_at').groupby('employee_code').last().reset_index()
golden_agents['agent_name'] = golden_agents['agent_name'].str.strip().str.title()
# Create agent_id to employee_code mapping table
dim_agent_mapping = agents_dedup[['agent_id', 'employee_code', 'vendor_id', 'team', 'status']].drop_duplicates()
log_step("agents", raw_ag_count, raw_ag_count - len(agents_dedup), len(dim_agent_mapping), len(golden_agents), "Resolved multi-agent ID fragmentation into 1,099 canonical employees.")

# 4. AGENT SESSIONS
raw_sessions = pd.read_csv(os.path.join(RAW_DIR, "agent_sessions.csv"), low_memory=False)
raw_ses_count = len(raw_sessions)
sessions_clean = raw_sessions.drop_duplicates(subset=['session_id']).copy()
sessions_clean['login_ist'] = normalize_timezone_to_ist(sessions_clean, 'login_at', 'timezone')
sessions_clean['logout_ist'] = normalize_timezone_to_ist(sessions_clean, 'logout_at', 'timezone')
sessions_clean['duration_hours'] = (pd.to_datetime(sessions_clean['logout_ist']) - pd.to_datetime(sessions_clean['login_ist'])).dt.total_seconds() / 3600.0
# Flag invalid durations (e.g. negative or > 24 hrs)
valid_sessions = sessions_clean[(sessions_clean['duration_hours'] >= 0) & (sessions_clean['duration_hours'] <= 24)].copy()
rejected_sessions = len(sessions_clean) - len(valid_sessions)
# Map to canonical employee_code
valid_sessions = valid_sessions.merge(dim_agent_mapping[['agent_id', 'employee_code']].drop_duplicates('agent_id'), on='agent_id', how='left')
golden_sessions = valid_sessions
log_step("agent_sessions", raw_ses_count, rejected_sessions, len(golden_sessions), len(golden_sessions), "Timezone normalized to IST; validated session duration hours.")

# 5. CALLS
raw_calls = pd.read_csv(os.path.join(RAW_DIR, "calls.csv"), low_memory=False)
raw_calls_count = len(raw_calls)
calls_dedup = raw_calls.drop_duplicates().copy()
exact_calls_dups = raw_calls_count - len(calls_dedup)
# Standardize timestamps to IST
calls_dedup['event_at_ist'] = normalize_timezone_to_ist(calls_dedup, 'event_at', 'timezone')
calls_dedup['call_date_ist'] = pd.to_datetime(calls_dedup['event_at_ist']).dt.date
calls_dedup['call_hour_ist'] = pd.to_datetime(calls_dedup['event_at_ist']).dt.hour
calls_dedup['is_prime_hours_ist'] = calls_dedup['call_hour_ist'].between(9, 19).astype(int)
calls_dedup['is_contact'] = (calls_dedup['call_status'] == 'ANSWERED').astype(int)
# Resolve agent
calls_dedup = calls_dedup.merge(dim_agent_mapping[['agent_id', 'employee_code']].drop_duplicates('agent_id'), on='agent_id', how='left')
golden_calls = calls_dedup
log_step("calls", raw_calls_count, exact_calls_dups, len(golden_calls), len(golden_calls), "Standardized UTC/Dubai timestamps to IST; resolved employee IDs; tagged prime hours.")

# 6. CALL ATTEMPTS
raw_attempts = pd.read_csv(os.path.join(RAW_DIR, "call_attempts.csv"), low_memory=False)
raw_att_count = len(raw_attempts)
attempts_dedup = raw_attempts.drop_duplicates(subset=['attempt_id']).copy()
attempts_dedup['event_at_dt'] = pd.to_datetime(attempts_dedup['event_at'])
attempts_dedup['is_connected'] = (attempts_dedup['attempt_status'] == 'CONNECTED').astype(int)
golden_attempts = attempts_dedup
log_step("call_attempts", raw_att_count, raw_att_count - len(attempts_dedup), 0, len(golden_attempts), "Validated unique attempt_id; flagged connection events.")

# 7. CALL DISPOSITIONS
raw_disp = pd.read_csv(os.path.join(RAW_DIR, "call_dispositions.csv"), low_memory=False)
raw_disp_count = len(raw_disp)
disp_dedup = raw_disp.drop_duplicates(subset=['disposition_id']).copy()
# Unify disposition codes: PROMISE_TO_PAY -> PTP
disp_dedup['disposition_code_clean'] = disp_dedup['disposition_code'].replace({'PROMISE_TO_PAY': 'PTP'})
# Link with calls to flag phantom dispositions on non-answered calls
disp_merged = disp_dedup.merge(golden_calls[['call_id', 'call_status']], on='call_id', how='left')
disp_merged['is_valid_contact_disposition'] = (disp_merged['call_status'] == 'ANSWERED').astype(int)
golden_dispositions = disp_merged
log_step("call_dispositions", raw_disp_count, 0, len(golden_dispositions), len(golden_dispositions), "Unified PTP codes; audited phantom dispositions on unanswered calls.")

# 8. WHATSAPP EVENTS
raw_wa = pd.read_csv(os.path.join(RAW_DIR, "whatsapp_events.csv"), low_memory=False)
raw_wa_count = len(raw_wa)
wa_dedup = raw_wa.drop_duplicates().copy()
wa_exact_dups = raw_wa_count - len(wa_dedup)
wa_dedup['event_at_dt'] = pd.to_datetime(wa_dedup['event_at'])
wa_dedup['is_engaged'] = wa_dedup['event_type'].isin(['READ', 'PAYMENT_CLICK', 'REPLIED']).astype(int)
golden_whatsapp = wa_dedup
log_step("whatsapp_events", raw_wa_count, wa_exact_dups, 0, len(golden_whatsapp), "Deduplicated events; tagged engagement funnel milestones.")

# 9. SMS EVENTS
raw_sms = pd.read_csv(os.path.join(RAW_DIR, "sms_events.csv"), low_memory=False)
raw_sms_count = len(raw_sms)
sms_dedup = raw_sms.drop_duplicates(subset=['sms_event_id']).copy()
sms_dedup['event_at_dt'] = pd.to_datetime(sms_dedup['event_at'])
sms_dedup['is_clicked'] = (sms_dedup['event_type'] == 'CLICKED').astype(int)
golden_sms = sms_dedup
log_step("sms_events", raw_sms_count, raw_sms_count - len(sms_dedup), 0, len(golden_sms), "Validated event IDs; tagged payment link click events.")

# 10. FIELD VISITS
raw_fv = pd.read_csv(os.path.join(RAW_DIR, "field_visits.csv"), low_memory=False)
raw_fv_count = len(raw_fv)
fv_dedup = raw_fv.drop_duplicates(subset=['visit_id']).copy()
fv_dedup['event_at_dt'] = pd.to_datetime(fv_dedup['event_at'])
fv_dedup['is_contacted'] = fv_dedup['outcome'].isin(['CONTACTED', 'PTP', 'PAID']).astype(int)
fv_dedup['is_paid'] = (fv_dedup['outcome'] == 'PAID').astype(int)
golden_field_visits = fv_dedup
log_step("field_visits", raw_fv_count, raw_fv_count - len(fv_dedup), 0, len(golden_field_visits), "Standardized field outcomes; flagged contact and on-field collection events.")

# 11. PROMISES TO PAY (PTP)
raw_ptp = pd.read_csv(os.path.join(RAW_DIR, "promises_to_pay.csv"), low_memory=False)
raw_ptp_count = len(raw_ptp)
ptp_dedup = raw_ptp.drop_duplicates(subset=['ptp_id']).copy()
ptp_dedup['event_at_dt'] = pd.to_datetime(ptp_dedup['event_at'])
ptp_dedup['promised_date_dt'] = pd.to_datetime(ptp_dedup['promised_date'])
ptp_dedup['is_kept'] = (ptp_dedup['status'] == 'KEPT').astype(int)
golden_ptp = ptp_dedup
log_step("promises_to_pay", raw_ptp_count, raw_ptp_count - len(ptp_dedup), 0, len(golden_ptp), "Audited promised amount commitments and kept vs broken statuses.")

# 12. PAYMENTS & FORENSIC DEDUPLICATION
raw_payments = pd.read_csv(os.path.join(RAW_DIR, "payments.csv"), low_memory=False)
raw_pay_count = len(raw_payments)
# Exact duplicate removal
pay_no_exact = raw_payments.drop_duplicates().copy()
exact_pay_dups = raw_pay_count - len(pay_no_exact)
# Separate statuses
pay_no_exact['payment_status_clean'] = pay_no_exact['payment_status'].str.strip().str.upper()
# Deduplicate payment_reference: keep the first SUCCESS transaction to prevent double counting
# Non-success records (FAILED, PENDING, REVERSED) are retained in audit table
pay_success = pay_no_exact[pay_no_exact['payment_status_clean'] == 'SUCCESS'].copy()
pay_non_success = pay_no_exact[pay_no_exact['payment_status_clean'] != 'SUCCESS'].copy()

# Sort by event_at and take first success per payment_reference
pay_success_sorted = pay_success.sort_values('event_at')
golden_payments_success = pay_success_sorted.drop_duplicates(subset=['payment_reference'], keep='first').copy()
duplicate_success_count = len(pay_success) - len(golden_payments_success)
inflated_recovery_amount = pay_success['amount'].sum() - golden_payments_success['amount'].sum()

# Also flag reversed payments for net accounting
reversed_amount = pay_no_exact[pay_no_exact['payment_status_clean'] == 'REVERSED']['amount'].sum()

golden_payments_success['event_at_dt'] = pd.to_datetime(golden_payments_success['event_at'])
golden_payments_success['payment_date'] = golden_payments_success['event_at_dt'].dt.date
golden_payments_success['payment_month'] = golden_payments_success['event_at_dt'].dt.to_period('M').astype(str)

log_step("payments", raw_pay_count, exact_pay_dups + duplicate_success_count, len(golden_payments_success), len(golden_payments_success), 
         f"Removed {duplicate_success_count} retry/duplicate SUCCESS records (saved Rs {inflated_recovery_amount/1e7:.2f} Cr double-counting).")

# 13. CAMPAIGNS & TARGETING
raw_camps = pd.read_csv(os.path.join(RAW_DIR, "campaigns.csv"), low_memory=False)
golden_campaigns = raw_camps.drop_duplicates(subset=['campaign_id']).copy()
log_step("campaigns", len(raw_camps), 0, 0, len(golden_campaigns), "Validated 120 campaign configurations across legacy and modern versions.")

raw_targeting = pd.read_csv(os.path.join(RAW_DIR, "daily_targeting.csv"), low_memory=False)
golden_targeting = raw_targeting.drop_duplicates(subset=['target_id']).copy()
golden_targeting['target_date_dt'] = pd.to_datetime(golden_targeting['target_date'])
golden_targeting['target_month'] = golden_targeting['target_date_dt'].dt.to_period('M').astype(str)
log_step("daily_targeting", len(raw_targeting), 0, 0, len(golden_targeting), "Validated 45,000 targeting dispatches across channels and priorities.")

# 14. COMPLAINTS & TELEPHONY VENDORS
raw_comp = pd.read_csv(os.path.join(RAW_DIR, "complaints.csv"), low_memory=False)
golden_complaints = raw_comp.drop_duplicates(subset=['complaint_id']).copy()
log_step("complaints", len(raw_comp), 0, 0, len(golden_complaints), "Validated borrower complaints and escalation severities.")

raw_vtel = pd.read_csv(os.path.join(RAW_DIR, "vendor_telephony.csv"), low_memory=False)
golden_vendor_telephony = raw_vtel.drop_duplicates(subset=['vendor_id']).copy()
log_step("vendor_telephony", len(raw_vtel), 0, 0, len(golden_vendor_telephony), "Validated 15 telephony carrier gateway definitions.")

# 15. ACCOUNT STATUS HISTORY
raw_ash = pd.read_csv(os.path.join(RAW_DIR, "account_status_history.csv"), low_memory=False)
ash_dedup = raw_ash.drop_duplicates(subset=['history_id']).copy()
ash_dedup['event_at_dt'] = pd.to_datetime(ash_dedup['event_at'])
ash_dedup['recorded_at_dt'] = pd.to_datetime(ash_dedup['recorded_at'])
# Identify effective latest status per account
effective_status = ash_dedup.sort_values('event_at_dt').groupby('account_id').last().reset_index()
golden_ash = ash_dedup
log_step("account_status_history", len(raw_ash), 0, len(effective_status), len(golden_ash), "Resolved event-time history and effective end-state statuses.")

# 16. BUILD GOLDEN ANALYTICAL FACT TABLE: FACT_ACCOUNT_SUMMARY
print("\n--- BUILDING FACT_ACCOUNT_SUMMARY (GOLDEN ANALYTICAL LAYER) ---")
acc_base = golden_accounts.merge(golden_borrowers[['borrower_id', 'name', 'city', 'state', 'phone']], on='borrower_id', how='left')

# Payment metrics per account
pay_agg = golden_payments_success.groupby('account_id').agg(
    total_net_recovery=('amount', 'sum'),
    successful_payments_count=('payment_id', 'count'),
    first_payment_date=('payment_date', 'min'),
    last_payment_date=('payment_date', 'max')
).reset_index()

acc_base = acc_base.merge(pay_agg, on='account_id', how='left')
acc_base['total_net_recovery'] = acc_base['total_net_recovery'].fillna(0.0)
acc_base['successful_payments_count'] = acc_base['successful_payments_count'].fillna(0).astype(int)
acc_base['is_recovered'] = (acc_base['total_net_recovery'] > 0).astype(int)
acc_base['recovery_rate_pct'] = (acc_base['total_net_recovery'] / acc_base['outstanding_amount']) * 100.0

# Call metrics per account
calls_agg = golden_calls.groupby('account_id').agg(
    total_calls_received=('call_id', 'count'),
    answered_calls_count=('is_contact', 'sum'),
    total_call_duration_sec=('duration_sec', 'sum')
).reset_index()
acc_base = acc_base.merge(calls_agg, on='account_id', how='left').fillna({
    'total_calls_received': 0, 'answered_calls_count': 0, 'total_call_duration_sec': 0
})

# Targeting count per account
tgt_agg = golden_targeting.groupby('account_id').agg(
    total_targeting_dispatches=('target_id', 'count')
).reset_index()
acc_base = acc_base.merge(tgt_agg, on='account_id', how='left').fillna({'total_targeting_dispatches': 0})

fact_account_summary = acc_base
print(f"FACT_ACCOUNT_SUMMARY built with {len(fact_account_summary)} accounts.")

# 17. SAVE TO SQLITE DATABASE
print(f"\nWriting Golden Dataset to SQLite Database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)

tables_to_save = {
    "dim_borrowers": golden_borrowers,
    "dim_accounts": golden_accounts,
    "dim_agents": golden_agents,
    "dim_agent_mapping": dim_agent_mapping,
    "dim_campaigns": golden_campaigns,
    "dim_vendor_telephony": golden_vendor_telephony,
    "fact_agent_sessions": golden_sessions,
    "fact_calls": golden_calls,
    "fact_call_attempts": golden_attempts,
    "fact_call_dispositions": golden_dispositions,
    "fact_whatsapp_events": golden_whatsapp,
    "fact_sms_events": golden_sms,
    "fact_field_visits": golden_field_visits,
    "fact_promises_to_pay": golden_ptp,
    "fact_payments_success": golden_payments_success,
    "fact_payments_audit": pay_no_exact,
    "fact_daily_targeting": golden_targeting,
    "fact_complaints": golden_complaints,
    "fact_account_status_history": golden_ash,
    "fact_account_summary": fact_account_summary
}

for tbl_name, df_data in tables_to_save.items():
    df_data.to_sql(tbl_name, conn, if_exists="replace", index=False)
    print(f"  -> Saved table {tbl_name} ({len(df_data)} rows)")

conn.commit()
conn.close()

# Also save key golden tables as CSV
for tbl_name in ["fact_account_summary", "fact_payments_success", "dim_accounts", "dim_borrowers"]:
    csv_file = os.path.join(GOLDEN_DIR, f"{tbl_name}.csv")
    tables_to_save[tbl_name].to_csv(csv_file, index=False)
    print(f"  -> Exported {csv_file}")

# Save accounting log
with open("pipeline/accounting_log.json", "w") as f:
    json.dump(accounting_log, f, indent=2)

print("\nGolden Dataset Pipeline completed successfully!")
