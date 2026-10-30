-- ==============================================================================
-- 01_schema_staging.sql
-- Production DDL for Ingestion & Staging Layer
-- ==============================================================================

-- Staging Accounts Table
CREATE TABLE IF NOT EXISTS stg_accounts (
    account_id TEXT PRIMARY KEY,
    borrower_id TEXT NOT NULL,
    loan_type TEXT,
    principal_amount REAL,
    outstanding_amount REAL,
    dpd INTEGER,
    risk_segment TEXT,
    status TEXT,
    opened_at TEXT,
    timezone TEXT,
    schema_version TEXT
);

-- Staging Borrowers Table
CREATE TABLE IF NOT EXISTS stg_borrowers (
    borrower_id TEXT,
    name TEXT,
    phone TEXT,
    email TEXT,
    city TEXT,
    created_at TEXT,
    updated_at TEXT,
    state TEXT
);

-- Staging Agents Table
CREATE TABLE IF NOT EXISTS stg_agents (
    agent_id TEXT,
    employee_code TEXT,
    agent_name TEXT,
    vendor_id TEXT,
    team TEXT,
    status TEXT,
    joined_at TEXT,
    updated_at TEXT
);

-- Staging Agent Sessions Table
CREATE TABLE IF NOT EXISTS stg_agent_sessions (
    session_id TEXT PRIMARY KEY,
    agent_id TEXT,
    login_at TEXT,
    channel TEXT,
    device_id TEXT,
    timezone TEXT,
    logout_at TEXT
);

-- Staging Calls Table
CREATE TABLE IF NOT EXISTS stg_calls (
    call_id TEXT,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    agent_id TEXT,
    campaign_id TEXT,
    direction TEXT,
    vendor_id TEXT,
    call_status TEXT,
    duration_sec INTEGER,
    timezone TEXT
);

-- Staging Call Attempts Table
CREATE TABLE IF NOT EXISTS stg_call_attempts (
    attempt_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    call_id TEXT,
    agent_id TEXT,
    attempt_no INTEGER,
    vendor_id TEXT,
    attempt_status TEXT
);

-- Staging Call Dispositions Table
CREATE TABLE IF NOT EXISTS stg_call_dispositions (
    disposition_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    call_id TEXT,
    agent_id TEXT,
    disposition_code TEXT,
    disposition_version TEXT
);

-- Staging Payments Table
CREATE TABLE IF NOT EXISTS stg_payments (
    payment_id TEXT,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    payment_reference TEXT,
    amount REAL,
    payment_status TEXT,
    payment_method TEXT,
    provider_id TEXT
);

-- Staging Campaigns Table
CREATE TABLE IF NOT EXISTS stg_campaigns (
    campaign_id TEXT PRIMARY KEY,
    campaign_name TEXT,
    channel TEXT,
    strategy_version TEXT,
    start_at TEXT,
    target_definition TEXT,
    end_at TEXT
);

-- Staging Daily Targeting Table
CREATE TABLE IF NOT EXISTS stg_daily_targeting (
    target_id TEXT PRIMARY KEY,
    account_id TEXT,
    campaign_id TEXT,
    target_date TEXT,
    priority INTEGER,
    recommended_channel TEXT,
    status TEXT
);

-- Staging WhatsApp Events Table
CREATE TABLE IF NOT EXISTS stg_whatsapp_events (
    whatsapp_event_id TEXT,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    message_id TEXT,
    event_type TEXT,
    template_code TEXT,
    provider_id TEXT
);

-- Staging SMS Events Table
CREATE TABLE IF NOT EXISTS stg_sms_events (
    sms_event_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    message_id TEXT,
    event_type TEXT,
    template_code TEXT,
    provider_id TEXT
);

-- Staging Field Visits Table
CREATE TABLE IF NOT EXISTS stg_field_visits (
    visit_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    agent_id TEXT,
    visit_type TEXT,
    outcome TEXT,
    latitude REAL,
    longitude REAL,
    scheduled_at TEXT
);

-- Staging Promises To Pay Table
CREATE TABLE IF NOT EXISTS stg_promises_to_pay (
    ptp_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    agent_id TEXT,
    promised_amount REAL,
    promised_date TEXT,
    status TEXT,
    source TEXT
);

-- Staging Vendor Telephony Table
CREATE TABLE IF NOT EXISTS stg_vendor_telephony (
    vendor_id TEXT PRIMARY KEY,
    vendor_name TEXT,
    vendor_account_id TEXT,
    timezone TEXT,
    status TEXT,
    schema_version TEXT
);

-- Staging Complaints Table
CREATE TABLE IF NOT EXISTS stg_complaints (
    complaint_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    complaint_type TEXT,
    severity TEXT,
    status TEXT,
    source TEXT,
    resolution_at TEXT
);

-- Staging Account Status History Table
CREATE TABLE IF NOT EXISTS stg_account_status_history (
    history_id TEXT PRIMARY KEY,
    account_id TEXT,
    borrower_id TEXT,
    event_at TEXT,
    status TEXT,
    changed_by TEXT,
    source TEXT,
    recorded_at TEXT
);

