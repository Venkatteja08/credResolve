-- ==============================================================================
-- 06_analytical_queries.sql
-- Production Analytical Forensics, Simpson's Paradox & Counterfactual Queries
-- ==============================================================================

-- ==============================================================================
-- FORENSIC QUERY 1: DUPLICATE PAYMENTS & ARTIFICIAL INFLATION
-- ==============================================================================
-- Detects identical payment references appearing multiple times with SUCCESS status
SELECT 
    payment_reference,
    COUNT(*) AS total_success_records,
    SUM(amount) AS gross_amount_recorded,
    MIN(amount) AS true_single_amount,
    SUM(amount) - MIN(amount) AS excess_inflated_amount,
    MIN(event_at) AS first_settlement_at,
    MAX(event_at) AS latest_settlement_at,
    COUNT(DISTINCT provider_id) AS distinct_providers_involved
FROM stg_payments
WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
GROUP BY payment_reference
HAVING COUNT(*) > 1
ORDER BY excess_inflated_amount DESC
LIMIT 20;

-- Summary of total double-counted capital across entire portfolio:
SELECT 
    COUNT(DISTINCT payment_reference) AS duplicate_reference_count,
    COUNT(*) - COUNT(DISTINCT payment_reference) AS redundant_duplicate_records,
    ROUND(SUM(amount) - SUM(first_amount), 2) AS total_inflated_rupees,
    ROUND((SUM(amount) - SUM(first_amount)) / 10000000.0, 2) AS total_inflated_crores
FROM (
    SELECT 
        payment_reference,
        amount,
        FIRST_VALUE(amount) OVER (PARTITION BY payment_reference ORDER BY event_at ASC) AS first_amount
    FROM stg_payments
    WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
);

-- ==============================================================================
-- FORENSIC QUERY 2: TIMEZONE CALL MISCLASSIFICATION (UTC vs IST)
-- ==============================================================================
-- Shows how naive hour classification based on raw UTC strings misclassifies
-- evening calls into early afternoon and night calls into previous day!
SELECT 
    raw_timezone,
    CAST(strftime('%H', raw_event_at) AS INTEGER) AS naive_hour_utc,
    CAST(strftime('%H', event_at_ist) AS INTEGER) AS corrected_hour_ist,
    COUNT(*) AS call_volume,
    SUM(CASE WHEN CAST(strftime('%H', raw_event_at) AS INTEGER) BETWEEN 9 AND 19 THEN 1 ELSE 0 END) AS naive_in_prime_hours,
    SUM(CASE WHEN CAST(strftime('%H', event_at_ist) AS INTEGER) BETWEEN 9 AND 19 THEN 1 ELSE 0 END) AS actual_in_prime_hours
FROM clean_calls
WHERE raw_timezone = 'UTC'
GROUP BY raw_timezone, naive_hour_utc, corrected_hour_ist
ORDER BY call_volume DESC
LIMIT 20;

-- ==============================================================================
-- FORENSIC QUERY 3: PHANTOM DISPOSITIONS ON UNANSWERED CALLS
-- ==============================================================================
-- Quantifies dispositions erroneously recorded when borrower never picked up
SELECT 
    c.call_status,
    COUNT(cd.disposition_id) AS total_dispositions_recorded,
    SUM(CASE WHEN cd.disposition_code IN ('PTP', 'PROMISE_TO_PAY') THEN 1 ELSE 0 END) AS phantom_ptps,
    SUM(CASE WHEN cd.disposition_code = 'PAID' THEN 1 ELSE 0 END) AS phantom_paid_flags,
    SUM(CASE WHEN cd.disposition_code = 'DISPUTE' THEN 1 ELSE 0 END) AS phantom_disputes,
    ROUND(CAST(COUNT(cd.disposition_id) AS REAL) / (SELECT COUNT(*) FROM stg_call_dispositions) * 100.0, 2) AS pct_of_all_dispositions
FROM stg_calls c
JOIN stg_call_dispositions cd ON c.call_id = cd.call_id
GROUP BY c.call_status
ORDER BY total_dispositions_recorded DESC;

-- ==============================================================================
-- FORENSIC QUERY 4: SIMPSON'S PARADOX & PORTFOLIO MIX
-- ==============================================================================
-- Evaluates whether recovery rate improved within subgroups or if mix shifted
SELECT 
    a.risk_segment,
    a.loan_type,
    COUNT(DISTINCT a.account_id) AS total_accounts,
    COUNT(DISTINCT p.account_id) AS recovered_accounts,
    ROUND(COUNT(DISTINCT p.account_id) * 100.0 / COUNT(DISTINCT a.account_id), 2) AS account_recovery_rate_pct,
    ROUND(SUM(p.amount) / 10000000.0, 2) AS net_recovered_crores,
    ROUND(AVG(p.amount), 2) AS avg_recovery_per_paying_account
FROM dim_accounts_golden a
LEFT JOIN clean_payments_success p ON a.account_id = p.account_id
GROUP BY a.risk_segment, a.loan_type
ORDER BY a.risk_segment, a.loan_type;

-- ==============================================================================
-- FORENSIC QUERY 5: COUNTERFACTUAL TARGETING STRATEGY EVALUATION
-- ==============================================================================
-- Compares recovery yield across campaign strategy versions (Legacy vs v1/v2/v3)
SELECT 
    c.strategy_version,
    COUNT(DISTINCT dt.account_id) AS targeted_accounts,
    COUNT(DISTINCT p.account_id) AS converted_paying_accounts,
    ROUND(COUNT(DISTINCT p.account_id) * 100.0 / COUNT(DISTINCT dt.account_id), 2) AS targeted_conversion_rate_pct,
    ROUND(SUM(p.amount) / 10000000.0, 2) AS total_settled_crores,
    ROUND(SUM(p.amount) / COUNT(DISTINCT dt.account_id), 2) AS recovery_per_targeted_account
FROM stg_campaigns c
JOIN stg_daily_targeting dt ON c.campaign_id = dt.campaign_id
LEFT JOIN clean_payments_success p ON dt.account_id = p.account_id
GROUP BY c.strategy_version
ORDER BY c.strategy_version;
