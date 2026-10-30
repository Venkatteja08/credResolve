-- ==============================================================================
-- 02_data_cleaning.sql
-- Production SQL Cleaning, Deduplication & Forensic Filtering
-- ==============================================================================

-- 1. CLEAN BORROWERS: Eliminate 600 duplicate rows, retain canonical record
DROP TABLE IF EXISTS clean_borrowers;
CREATE TABLE clean_borrowers AS
WITH ranked_borrowers AS (
    SELECT 
        borrower_id,
        TRIM(name) AS name,
        phone,
        LOWER(TRIM(email)) AS email,
        TRIM(city) AS city,
        TRIM(state) AS state,
        created_at,
        updated_at,
        ROW_NUMBER() OVER (
            PARTITION BY borrower_id 
            ORDER BY updated_at DESC
        ) AS rn
    FROM stg_borrowers
)
SELECT 
    borrower_id,
    name,
    phone,
    email,
    city,
    state,
    created_at,
    updated_at
FROM ranked_borrowers
WHERE rn = 1;

-- 2. CLEAN CALLS: Remove 1,271 duplicate rows, convert timestamps to Asia/Kolkata (IST)
DROP TABLE IF EXISTS clean_calls;
CREATE TABLE clean_calls AS
WITH dedup_calls AS (
    SELECT DISTINCT 
        call_id,
        account_id,
        borrower_id,
        event_at,
        agent_id,
        campaign_id,
        direction,
        vendor_id,
        call_status,
        duration_sec,
        timezone
    FROM stg_calls
)
SELECT 
    call_id,
    account_id,
    borrower_id,
    event_at AS raw_event_at,
    timezone AS raw_timezone,
    -- Timezone conversion to IST (Asia/Kolkata)
    CASE 
        WHEN timezone = 'UTC' THEN datetime(event_at, '+5 hours', '+30 minutes')
        WHEN timezone = 'Asia/Dubai' THEN datetime(event_at, '+1 hours', '+30 minutes')
        ELSE datetime(event_at)
    END AS event_at_ist,
    agent_id,
    campaign_id,
    direction,
    vendor_id,
    call_status,
    duration_sec,
    CASE WHEN call_status = 'ANSWERED' THEN 1 ELSE 0 END AS is_contact,
    CASE 
        WHEN CAST(strftime('%H', CASE 
            WHEN timezone = 'UTC' THEN datetime(event_at, '+5 hours', '+30 minutes')
            WHEN timezone = 'Asia/Dubai' THEN datetime(event_at, '+1 hours', '+30 minutes')
            ELSE datetime(event_at)
        END) AS INTEGER) BETWEEN 9 AND 19 THEN 1 
        ELSE 0 
    END AS is_prime_calling_hours
FROM dedup_calls;

-- 3. CLEAN PAYMENTS: Forensic deduplication of payment_reference
-- Critical Business Logic: Discard duplicate SUCCESS rows and retry attempts that artificially inflate recovery by Rs 17.19 Cr!
DROP TABLE IF EXISTS clean_payments_success;
CREATE TABLE clean_payments_success AS
WITH ranked_success_payments AS (
    SELECT 
        payment_id,
        account_id,
        borrower_id,
        event_at,
        payment_reference,
        amount,
        UPPER(TRIM(payment_status)) AS payment_status,
        payment_method,
        provider_id,
        ROW_NUMBER() OVER (
            PARTITION BY payment_reference 
            ORDER BY event_at ASC, payment_id ASC
        ) AS txn_rank
    FROM stg_payments
    WHERE UPPER(TRIM(payment_status)) = 'SUCCESS'
)
SELECT 
    payment_id,
    account_id,
    borrower_id,
    event_at,
    payment_reference,
    amount,
    payment_status,
    payment_method,
    provider_id,
    strftime('%Y-%m', event_at) AS payment_month,
    DATE(event_at) AS payment_date
FROM ranked_success_payments
WHERE txn_rank = 1;

-- 4. CLEAN AUDIT PAYMENTS: Track all non-success and duplicate attempts for financial audit
DROP TABLE IF EXISTS clean_payments_audit;
CREATE TABLE clean_payments_audit AS
SELECT 
    payment_id,
    account_id,
    borrower_id,
    event_at,
    payment_reference,
    amount,
    UPPER(TRIM(payment_status)) AS payment_status,
    payment_method,
    provider_id,
    strftime('%Y-%m', event_at) AS payment_month
FROM stg_payments;

-- 5. CLEAN WHATSAPP EVENTS: Remove 600 duplicate rows
DROP TABLE IF EXISTS clean_whatsapp_events;
CREATE TABLE clean_whatsapp_events AS
SELECT DISTINCT 
    whatsapp_event_id,
    account_id,
    borrower_id,
    event_at,
    message_id,
    event_type,
    template_code,
    provider_id,
    CASE WHEN event_type IN ('READ', 'PAYMENT_CLICK', 'REPLIED') THEN 1 ELSE 0 END AS is_engaged
FROM stg_whatsapp_events;

-- 5B. CLEAN SMS EVENTS
DROP TABLE IF EXISTS clean_sms_events;
CREATE TABLE clean_sms_events AS
SELECT DISTINCT 
    sms_event_id,
    account_id,
    borrower_id,
    event_at,
    message_id,
    event_type,
    template_code,
    provider_id,
    CASE WHEN event_type = 'CLICKED' THEN 1 ELSE 0 END AS is_clicked
FROM stg_sms_events;

-- 6. CLEAN AGENT SESSIONS: Filter invalid session durations and map IST
DROP TABLE IF EXISTS clean_agent_sessions;
CREATE TABLE clean_agent_sessions AS
SELECT 
    session_id,
    agent_id,
    login_at AS raw_login_at,
    logout_at AS raw_logout_at,
    timezone,
    CASE 
        WHEN timezone = 'UTC' THEN datetime(login_at, '+5 hours', '+30 minutes')
        WHEN timezone = 'Asia/Dubai' THEN datetime(login_at, '+1 hours', '+30 minutes')
        ELSE datetime(login_at)
    END AS login_at_ist,
    CASE 
        WHEN timezone = 'UTC' THEN datetime(logout_at, '+5 hours', '+30 minutes')
        WHEN timezone = 'Asia/Dubai' THEN datetime(logout_at, '+1 hours', '+30 minutes')
        ELSE datetime(logout_at)
    END AS logout_at_ist,
    (julianday(logout_at) - julianday(login_at)) * 24.0 AS session_duration_hours,
    channel,
    device_id
FROM stg_agent_sessions
WHERE (julianday(logout_at) - julianday(login_at)) * 24.0 BETWEEN 0.0 AND 24.0;
