-- ==============================================================================
-- 05_metric_calculations.sql
-- Production Metric Calculations: Independent, Forensic & Robust KPIs
-- ==============================================================================

-- 1. MONTHLY OPERATIONAL METRICS: VOICE CALLING
-- Contact Rate, RPC, Attempt Yield
DROP TABLE IF EXISTS kpi_voice_operations_monthly;
CREATE TABLE kpi_voice_operations_monthly AS
WITH call_metrics AS (
    SELECT 
        strftime('%Y-%m', event_at_ist) AS metric_month,
        COUNT(call_id) AS total_calls_dialed,
        SUM(is_contact) AS total_calls_answered,
        SUM(duration_sec) / 3600.0 AS total_talk_time_hours,
        COUNT(DISTINCT account_id) AS accounts_called,
        COUNT(DISTINCT CASE WHEN is_contact = 1 THEN account_id END) AS accounts_contacted
    FROM clean_calls
    GROUP BY strftime('%Y-%m', event_at_ist)
),
attempt_metrics AS (
    SELECT 
        strftime('%Y-%m', event_at) AS metric_month,
        COUNT(attempt_id) AS total_dialer_attempts,
        SUM(CASE WHEN attempt_status = 'CONNECTED' THEN 1 ELSE 0 END) AS connected_attempts
    FROM stg_call_attempts
    GROUP BY strftime('%Y-%m', event_at)
)
SELECT 
    c.metric_month,
    a.total_dialer_attempts,
    c.total_calls_dialed,
    c.total_calls_answered,
    -- Independent Contact Rate: Verified answered calls / Dialer attempts
    ROUND((CAST(c.total_calls_answered AS REAL) / c.total_calls_dialed) * 100.0, 2) AS call_contact_rate_pct,
    ROUND((CAST(a.connected_attempts AS REAL) / a.total_dialer_attempts) * 100.0, 2) AS attempt_connection_rate_pct,
    c.accounts_called,
    c.accounts_contacted,
    -- Right Party Contact Rate (RPC %): Unique accounts contacted / Unique accounts dialed
    ROUND((CAST(c.accounts_contacted AS REAL) / c.accounts_called) * 100.0, 2) AS account_rpc_rate_pct,
    ROUND(c.total_talk_time_hours, 1) AS total_talk_time_hours
FROM call_metrics c
LEFT JOIN attempt_metrics a ON c.metric_month = a.metric_month
ORDER BY c.metric_month;

-- 2. PTP & PTP KEPT RATE METRICS
DROP TABLE IF EXISTS kpi_ptp_performance_monthly;
CREATE TABLE kpi_ptp_performance_monthly AS
SELECT 
    strftime('%Y-%m', event_at) AS metric_month,
    COUNT(ptp_id) AS total_ptp_generated,
    SUM(CASE WHEN status = 'KEPT' THEN 1 ELSE 0 END) AS kept_ptp_count,
    SUM(CASE WHEN status = 'BROKEN' THEN 1 ELSE 0 END) AS broken_ptp_count,
    SUM(CASE WHEN status = 'CANCELLED' THEN 1 ELSE 0 END) AS cancelled_ptp_count,
    SUM(promised_amount) AS total_promised_amount,
    -- Independent PTP Kept Rate: Verified kept PTPs / (Kept + Broken matured PTPs)
    ROUND((CAST(SUM(CASE WHEN status = 'KEPT' THEN 1 ELSE 0 END) AS REAL) / 
           NULLIF(SUM(CASE WHEN status IN ('KEPT', 'BROKEN') THEN 1 ELSE 0 END), 0)) * 100.0, 2) AS ptp_kept_rate_pct
FROM stg_promises_to_pay
GROUP BY strftime('%Y-%m', event_at)
ORDER BY metric_month;

-- 3. RECOVERY PERFORMANCE & DAILY RUN RATE
-- Debunking the MoM Myth: Raw vs Deduplicated vs Daily Run Rate
DROP TABLE IF EXISTS kpi_recovery_benchmark_monthly;
CREATE TABLE kpi_recovery_benchmark_monthly AS
WITH monthly_stats AS (
    SELECT 
        payment_month,
        COUNT(DISTINCT DATE(event_at)) AS calendar_days,
        -- Gross Reported Recovery (Flawed Business Claim including duplicates & retries)
        SUM(amount) AS raw_reported_recovery,
        -- Deduplicated Net Settled Cash Recovery (Independent Golden Standard)
        SUM(CASE WHEN txn_rank = 1 THEN amount ELSE 0 END) AS net_settled_recovery,
        COUNT(DISTINCT CASE WHEN txn_rank = 1 THEN payment_reference END) AS net_payment_count,
        COUNT(DISTINCT CASE WHEN txn_rank = 1 THEN account_id END) AS paying_accounts
    FROM (
        SELECT 
            *,
            strftime('%Y-%m', event_at) AS payment_month,
            ROW_NUMBER() OVER (PARTITION BY payment_reference ORDER BY event_at ASC) AS txn_rank
        FROM stg_payments
        WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
    )
    GROUP BY payment_month
)
SELECT 
    payment_month,
    calendar_days,
    raw_reported_recovery,
    -- Month-on-Month % change of raw recovery
    ROUND((raw_reported_recovery - LAG(raw_reported_recovery) OVER (ORDER BY payment_month)) / 
          LAG(raw_reported_recovery) OVER (ORDER BY payment_month) * 100.0, 2) AS raw_mom_growth_pct,
    net_settled_recovery,
    -- Month-on-Month % change of net settled recovery
    ROUND((net_settled_recovery - LAG(net_settled_recovery) OVER (ORDER BY payment_month)) / 
          LAG(net_settled_recovery) OVER (ORDER BY payment_month) * 100.0, 2) AS net_mom_growth_pct,
    -- Daily Run Rate (Normalized for February's 28 days vs March's 31 days)
    ROUND(net_settled_recovery / calendar_days, 2) AS daily_run_rate_recovery,
    ROUND(((net_settled_recovery / calendar_days) - 
           LAG(net_settled_recovery / calendar_days) OVER (ORDER BY payment_month)) / 
          LAG(net_settled_recovery / calendar_days) OVER (ORDER BY payment_month) * 100.0, 2) AS daily_run_rate_mom_pct,
    -- Recovery per static portfolio account (30,000 accounts)
    ROUND(net_settled_recovery / 30000.0, 2) AS recovery_per_portfolio_account
FROM monthly_stats
ORDER BY payment_month;

-- 4. AGENT PRODUCTIVITY & COST PER RUPEE RECOVERED
DROP TABLE IF EXISTS kpi_agent_productivity_monthly;
CREATE TABLE kpi_agent_productivity_monthly AS
WITH monthly_hours AS (
    SELECT 
        strftime('%Y-%m', login_at_ist) AS metric_month,
        COUNT(DISTINCT employee_code) AS active_agents,
        SUM(session_duration_hours) AS total_logged_in_hours
    FROM (
        SELECT 
            s.*,
            ac.employee_code
        FROM clean_agent_sessions s
        LEFT JOIN dim_agent_crosswalk ac ON s.agent_id = ac.agent_id
    )
    GROUP BY strftime('%Y-%m', login_at_ist)
),
monthly_recovery AS (
    SELECT 
        payment_month AS metric_month,
        SUM(amount) AS net_recovery
    FROM clean_payments_success
    GROUP BY payment_month
)
SELECT 
    h.metric_month,
    h.active_agents,
    ROUND(h.total_logged_in_hours, 1) AS total_agent_hours,
    r.net_recovery,
    -- Recovery per Agent-Hour
    ROUND(r.net_recovery / h.total_logged_in_hours, 2) AS recovery_per_agent_hour,
    -- Operational Cost Model: Telephony (Rs 0.40/min) + Agent Base Salary (Rs 30,000/mo) + Tech Overheads
    ROUND((h.active_agents * 30000.0) + (h.total_logged_in_hours * 60 * 0.40) + 1500000.0, 2) AS estimated_operational_cost,
    -- Cost per Rupee Recovered
    ROUND(((h.active_agents * 30000.0) + (h.total_logged_in_hours * 60 * 0.40) + 1500000.0) / r.net_recovery, 4) AS cost_per_rupee_recovered
FROM monthly_hours h
LEFT JOIN monthly_recovery r ON h.metric_month = r.metric_month
ORDER BY h.metric_month;
