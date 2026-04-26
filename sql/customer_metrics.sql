-- ============================================================================
-- Customer Health Project: Customer-Level Metrics
-- ============================================================================
-- Comprehensive view of customer health with usage, support, and commercial data
-- Uses aggregated CTEs to prevent duplicate counts from joins

-- ========================================================================
-- CTE 1: USAGE METRICS (aggregated by customer)
-- ========================================================================
WITH usage_metrics AS (
    SELECT
        customer_id,
        COUNT(DISTINCT event_date || event_type || user_id) AS total_events,
        COUNT(DISTINCT user_id) AS unique_active_users,
        CAST((julianday('now') - MAX(julianday(event_date))) AS INTEGER) AS days_since_last_activity,
        SUM(CASE WHEN event_type = 'login' THEN 1 ELSE 0 END) AS login_events,
        SUM(CASE WHEN event_type = 'publish' THEN 1 ELSE 0 END) AS publish_events,
        SUM(CASE WHEN event_type = 'export' THEN 1 ELSE 0 END) AS export_events,
        SUM(CASE WHEN event_type = 'integration' THEN 1 ELSE 0 END) AS integration_events
    FROM usage_events
    GROUP BY customer_id
),

-- ========================================================================
-- CTE 2: TICKET METRICS (aggregated by customer)
-- ========================================================================
ticket_metrics AS (
    SELECT
        customer_id,
        COUNT(DISTINCT ticket_id) AS total_tickets,
        SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_tickets,
        SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) AS high_priority_tickets
    FROM support_tickets
    GROUP BY customer_id
)

-- ========================================================================
-- MAIN QUERY: Join aggregated metrics to customers
-- ========================================================================
SELECT
    -- ========================================================================
    -- CUSTOMER IDENTIFIERS
    -- ========================================================================
    c.customer_id,
    c.company_name,
    c.plan,
    c.industry,
    c.contract_value,
    
    -- ========================================================================
    -- USAGE METRICS (from CTE)
    -- ========================================================================
    COALESCE(um.total_events, 0) AS total_events,
    COALESCE(um.unique_active_users, 0) AS unique_active_users,
    um.days_since_last_activity,
    COALESCE(um.login_events, 0) AS login_events,
    COALESCE(um.publish_events, 0) AS publish_events,
    COALESCE(um.export_events, 0) AS export_events,
    COALESCE(um.integration_events, 0) AS integration_events,
    
    -- ========================================================================
    -- SUPPORT METRICS (from CTE)
    -- ========================================================================
    COALESCE(tm.total_tickets, 0) AS total_tickets,
    COALESCE(tm.open_tickets, 0) AS open_tickets,
    COALESCE(tm.high_priority_tickets, 0) AS high_priority_tickets,
    
    -- ========================================================================
    -- RENEWAL & COMMERCIAL METRICS
    -- ========================================================================
    -- Days until renewal date (negative means overdue)
    CAST((julianday(c.renewal_date) - julianday('now')) AS INTEGER) AS days_until_renewal,
    
    -- Payment status
    cm.payment_status,
    
    -- Renewal risk assessment
    cm.renewal_stage

FROM
    customers c
    LEFT JOIN usage_metrics um ON c.customer_id = um.customer_id
    LEFT JOIN ticket_metrics tm ON c.customer_id = tm.customer_id
    LEFT JOIN commercials cm ON c.customer_id = cm.customer_id

ORDER BY
    c.customer_id;

-- ============================================================================
-- Query Notes:
-- ============================================================================
-- - Uses LEFT JOINs to ensure all customers appear, even if inactive
-- - Event counts default to 0 for customers with no activity
-- - days_since_last_activity is NULL for customers with no events
-- - days_until_renewal can be negative (indicates overdue renewal)
-- - All date calculations use SQLite's julianday() function
-- ============================================================================
