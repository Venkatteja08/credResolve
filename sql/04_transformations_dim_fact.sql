-- ==============================================================================
-- 04_transformations_dim_fact.sql
-- Production Dimensional Modeling: Kimball-Style Star Schema & Facts
-- ==============================================================================

-- 1. GOLDEN ACCOUNTS DIMENSION (dim_accounts_golden)
DROP TABLE IF EXISTS dim_accounts_golden;
CREATE TABLE dim_accounts_golden AS
SELECT 
    a.account_id,
    a.borrower_id,
    b.name AS borrower_name,
    b.phone AS borrower_phone,
    b.city AS borrower_city,
    b.state AS borrower_state,
    UPPER(TRIM(a.loan_type)) AS loan_type,
    a.principal_amount,
    a.outstanding_amount,
    a.dpd,
    CASE 
        WHEN a.dpd <= 30 THEN '0-30 DPD'
        WHEN a.dpd <= 60 THEN '31-60 DPD'
        WHEN a.dpd <= 90 THEN '61-90 DPD'
        WHEN a.dpd <= 180 THEN '91-180 DPD'
        ELSE '180+ DPD'
    END AS dpd_bucket,
    UPPER(TRIM(a.risk_segment)) AS risk_segment,
    UPPER(TRIM(a.status)) AS account_status,
    a.opened_at,
    a.schema_version
FROM stg_accounts a
LEFT JOIN clean_borrowers b ON a.borrower_id = b.borrower_id;

-- 2. FACT_DAILY_OMNICHANNEL_TOUCHPOINTS
-- Consolidated timeline of all borrower interactions across voice, digital, and field
DROP TABLE IF EXISTS fact_daily_omnichannel_touchpoints;
CREATE TABLE fact_daily_omnichannel_touchpoints AS
-- Voice Calls
SELECT 
    call_id AS event_id,
    account_id,
    borrower_id,
    event_at_ist AS event_at,
    DATE(event_at_ist) AS event_date,
    strftime('%Y-%m', event_at_ist) AS event_month,
    'VOICE' AS channel,
    call_status AS interaction_status,
    is_contact AS is_successful_contact,
    duration_sec AS duration_or_unit,
    agent_id
FROM clean_calls

UNION ALL

-- WhatsApp Events
SELECT 
    whatsapp_event_id AS event_id,
    account_id,
    borrower_id,
    event_at,
    DATE(event_at) AS event_date,
    strftime('%Y-%m', event_at) AS event_month,
    'WHATSAPP' AS channel,
    event_type AS interaction_status,
    is_engaged AS is_successful_contact,
    0 AS duration_or_unit,
    NULL AS agent_id
FROM clean_whatsapp_events

UNION ALL

-- SMS Events
SELECT 
    sms_event_id AS event_id,
    account_id,
    borrower_id,
    event_at,
    DATE(event_at) AS event_date,
    strftime('%Y-%m', event_at) AS event_month,
    'SMS' AS channel,
    event_type AS interaction_status,
    is_clicked AS is_successful_contact,
    0 AS duration_or_unit,
    NULL AS agent_id
FROM clean_sms_events

UNION ALL

-- Field Visits
SELECT 
    visit_id AS event_id,
    account_id,
    borrower_id,
    event_at,
    DATE(event_at) AS event_date,
    strftime('%Y-%m', event_at) AS event_month,
    'FIELD' AS channel,
    outcome AS interaction_status,
    CASE WHEN outcome IN ('CONTACTED', 'PTP', 'PAID') THEN 1 ELSE 0 END AS is_successful_contact,
    0 AS duration_or_unit,
    agent_id
FROM stg_field_visits;

-- 3. FACT_MONTHLY_COLLECTIONS_SUMMARY
-- Aggregated monthly metrics layer
DROP TABLE IF EXISTS fact_monthly_collections_summary;
CREATE TABLE fact_monthly_collections_summary AS
SELECT 
    p.payment_month,
    COUNT(DISTINCT p.payment_reference) AS net_settled_payment_count,
    COUNT(DISTINCT p.account_id) AS distinct_paying_accounts,
    SUM(p.amount) AS total_net_settled_recovery,
    AVG(p.amount) AS avg_payment_size,
    COUNT(DISTINCT DATE(p.event_at)) AS active_calendar_days,
    SUM(p.amount) / COUNT(DISTINCT DATE(p.event_at)) AS daily_run_rate_recovery
FROM clean_payments_success p
GROUP BY p.payment_month;
