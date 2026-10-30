import sqlite3
import pandas as pd
import json

conn = sqlite3.connect("golden_collections.db")

data = {}

# 1. Monthly benchmark
df_bench = pd.read_sql_query("SELECT * FROM kpi_recovery_benchmark_monthly", conn)
data['monthly_benchmark'] = df_bench.to_dict(orient='records')

# 2. Risk x Loan Type conversion matrix
acc_summary = pd.read_sql_query("SELECT * FROM fact_account_summary", conn)
ct_risk_loan = pd.crosstab(
    acc_summary['risk_segment'], 
    acc_summary['loan_type'], 
    values=acc_summary['is_recovered'], 
    aggfunc='mean'
) * 100
data['risk_loan_matrix'] = ct_risk_loan.round(2).to_dict()

# 3. Monthly by loan type & risk
payments = pd.read_sql_query("SELECT * FROM fact_payments_success", conn)
payments['month'] = pd.to_datetime(payments['event_at']).dt.to_period('M').astype(str)
acc_pay = payments.merge(acc_summary[['account_id', 'risk_segment', 'loan_type', 'dpd_bucket']], on='account_id', how='left')

m_loan = pd.crosstab(acc_pay['month'], acc_pay['loan_type'], values=acc_pay['amount'] / 1e7, aggfunc='sum').round(2)
data['monthly_by_loan'] = m_loan.to_dict()

m_risk = pd.crosstab(acc_pay['month'], acc_pay['risk_segment'], values=acc_pay['amount'] / 1e7, aggfunc='sum').round(2)
data['monthly_by_risk'] = m_risk.to_dict()

# 4. Telephony vendors
calls = pd.read_sql_query("SELECT * FROM fact_calls", conn)
v_tel = pd.read_sql_query("SELECT * FROM dim_vendor_telephony", conn)
calls_vnd = calls.merge(v_tel[['vendor_id', 'vendor_name']], on='vendor_id', how='left')
vnd_perf = calls_vnd.groupby('vendor_name').agg(
    total_calls=('call_id', 'count'),
    answered_calls=('is_contact', 'sum'),
    contact_rate=('is_contact', lambda s: round(s.mean() * 100, 2)),
    avg_duration_sec=('duration_sec', lambda s: round(s.mean(), 1))
).reset_index()
data['vendor_performance'] = vnd_perf.to_dict(orient='records')

# 5. Attempts performance
att = pd.read_sql_query("SELECT * FROM fact_call_attempts", conn)
att_perf = att.groupby('attempt_no').agg(
    total_attempts=('attempt_id', 'count'),
    connected=('is_connected', 'sum'),
    connect_rate=('is_connected', lambda s: round(s.mean() * 100, 2))
).reset_index()
data['attempt_performance'] = att_perf.to_dict(orient='records')

# 6. Accounting log
with open("pipeline/accounting_log.json") as f:
    data['accounting_log'] = json.load(f)

# 7. Dispositions audit
disp_audit = pd.read_sql_query("""
    SELECT 
        c.call_status,
        COUNT(cd.disposition_id) AS total_dispositions,
        SUM(CASE WHEN cd.standardized_disposition_code = 'PTP' THEN 1 ELSE 0 END) AS ptp_count,
        SUM(CASE WHEN cd.standardized_disposition_code = 'PAID' THEN 1 ELSE 0 END) AS paid_count,
        SUM(CASE WHEN cd.standardized_disposition_code = 'CALLBACK' THEN 1 ELSE 0 END) AS callback_count,
        SUM(CASE WHEN cd.standardized_disposition_code = 'DISPUTE' THEN 1 ELSE 0 END) AS dispute_count
    FROM clean_calls c
    JOIN clean_call_dispositions cd ON c.call_id = cd.call_id
    GROUP BY c.call_status
""", conn)
data['disposition_audit'] = disp_audit.to_dict(orient='records')

# 8. Timezone audit
tz_audit = pd.read_sql_query("""
    SELECT 
        raw_timezone,
        COUNT(*) AS total_calls,
        SUM(CASE WHEN CAST(strftime('%H', raw_event_at) AS INTEGER) BETWEEN 9 AND 19 THEN 1 ELSE 0 END) AS naive_prime,
        SUM(CASE WHEN CAST(strftime('%H', event_at_ist) AS INTEGER) BETWEEN 9 AND 19 THEN 1 ELSE 0 END) AS ist_prime
    FROM clean_calls
    GROUP BY raw_timezone
""", conn)
data['timezone_audit'] = tz_audit.to_dict(orient='records')

# 9. Duplicate payments sample
dup_sample = pd.read_sql_query("""
    SELECT 
        payment_reference,
        COUNT(*) as attempts_count,
        MIN(amount) as single_amount,
        SUM(amount) as gross_amount,
        SUM(amount) - MIN(amount) as excess_amount,
        MIN(event_at) as first_seen,
        MAX(event_at) as last_seen
    FROM stg_payments
    WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
    GROUP BY payment_reference
    HAVING COUNT(*) > 1
    ORDER BY excess_amount DESC
    LIMIT 10
""", conn)
data['duplicate_sample'] = dup_sample.to_dict(orient='records')

conn.close()

with open("dashboard/frontend_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("Saved dashboard/frontend_data.json successfully!")

