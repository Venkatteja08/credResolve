-- ==============================================================================
-- 03_entity_resolution.sql
-- Production SQL Entity Resolution: Agents & Borrowers
-- ==============================================================================

-- 1. AGENT ENTITY RESOLUTION TABLE
-- Problem: 30,000 raw agent records contain 1,000 agent_ids mapping many-to-many
-- across 1,099 employee codes. A single employee operates under up to 46 distinct agent_ids!
-- Solution: Create a persistent crosswalk table mapping every agent_id to their canonical employee profile.

DROP TABLE IF EXISTS dim_agent_crosswalk;
CREATE TABLE dim_agent_crosswalk AS
WITH deduplicated_agent_rows AS (
    SELECT DISTINCT 
        agent_id,
        employee_code,
        agent_name,
        vendor_id,
        team,
        status,
        joined_at,
        updated_at
    FROM stg_agents
),
ranked_crosswalk AS (
    SELECT 
        agent_id,
        employee_code,
        vendor_id,
        team,
        status,
        ROW_NUMBER() OVER (
            PARTITION BY agent_id 
            ORDER BY updated_at DESC, joined_at DESC
        ) AS rn
    FROM deduplicated_agent_rows
)
SELECT 
    agent_id,
    employee_code,
    vendor_id,
    team,
    status
FROM ranked_crosswalk
WHERE rn = 1;

-- 2. CANONICAL EMPLOYEE DIMENSION
-- Consolidates tenure, team, and canonical metadata per employee_code
DROP TABLE IF EXISTS dim_employees_canonical;
CREATE TABLE dim_employees_canonical AS
WITH ranked_employees AS (
    SELECT 
        employee_code,
        TRIM(agent_name) AS employee_name,
        vendor_id,
        team,
        status,
        MIN(joined_at) OVER (PARTITION BY employee_code) AS first_joined_at,
        MAX(updated_at) OVER (PARTITION BY employee_code) AS latest_updated_at,
        ROW_NUMBER() OVER (
            PARTITION BY employee_code 
            ORDER BY updated_at DESC
        ) AS rn
    FROM stg_agents
)
SELECT 
    employee_code,
    employee_name,
    vendor_id,
    team,
    status,
    first_joined_at,
    latest_updated_at,
    CAST((julianday('2026-08-08') - julianday(first_joined_at)) AS INTEGER) AS tenure_days,
    CASE 
        WHEN (julianday('2026-08-08') - julianday(first_joined_at)) < 365 THEN 'New (<1 yr)'
        WHEN (julianday('2026-08-08') - julianday(first_joined_at)) BETWEEN 365 AND 730 THEN 'Mid-Tenure (1-2 yrs)'
        ELSE 'Senior (>2 yrs)'
    END AS tenure_bucket
FROM ranked_employees
WHERE rn = 1;

-- 3. CALL DISPOSITIONS AUDIT & STANDARDIZATION
-- Problem: 'PTP' and 'PROMISE_TO_PAY' exist concurrently; 79.9% of dispositions occurred on UNANSWERED calls!
DROP TABLE IF EXISTS clean_call_dispositions;
CREATE TABLE clean_call_dispositions AS
SELECT 
    cd.disposition_id,
    cd.account_id,
    cd.borrower_id,
    cd.event_at,
    cd.call_id,
    cd.agent_id,
    ac.employee_code,
    -- Standardize synonymous disposition codes
    CASE 
        WHEN cd.disposition_code = 'PROMISE_TO_PAY' THEN 'PTP'
        ELSE cd.disposition_code 
    END AS standardized_disposition_code,
    cd.disposition_version,
    c.call_status,
    -- Flag whether the call was actually answered (Right Party Contact validation)
    CASE WHEN c.call_status = 'ANSWERED' THEN 1 ELSE 0 END AS is_verified_rpc_disposition
FROM stg_call_dispositions cd
LEFT JOIN stg_calls c ON cd.call_id = c.call_id
LEFT JOIN dim_agent_crosswalk ac ON cd.agent_id = ac.agent_id;
