-- ============================================================================
-- Customer Health Project: Create Tables
-- ============================================================================
-- This script sets up the SQLite database schema for customer health metrics
-- Drop existing tables and recreate them from scratch

-- ============================================================================
-- 1. CUSTOMERS TABLE
-- ============================================================================
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    plan TEXT NOT NULL,
    industry TEXT NOT NULL,
    contract_value INTEGER NOT NULL,
    renewal_date TEXT NOT NULL
);

-- ============================================================================
-- 2. USAGE EVENTS TABLE
-- ============================================================================
DROP TABLE IF EXISTS usage_events;

CREATE TABLE usage_events (
    customer_id TEXT NOT NULL,
    event_date TEXT NOT NULL,
    event_type TEXT NOT NULL,
    user_id TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Index for common queries
CREATE INDEX idx_usage_events_customer_id ON usage_events(customer_id);
CREATE INDEX idx_usage_events_event_date ON usage_events(event_date);
CREATE INDEX idx_usage_events_event_type ON usage_events(event_type);

-- ============================================================================
-- 3. SUPPORT TICKETS TABLE
-- ============================================================================
DROP TABLE IF EXISTS support_tickets;

CREATE TABLE support_tickets (
    ticket_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    created_date TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- Index for common queries
CREATE INDEX idx_support_tickets_customer_id ON support_tickets(customer_id);
CREATE INDEX idx_support_tickets_status ON support_tickets(status);

-- ============================================================================
-- 4. COMMERCIALS TABLE
-- ============================================================================
DROP TABLE IF EXISTS commercials;

CREATE TABLE commercials (
    customer_id TEXT PRIMARY KEY,
    payment_status TEXT NOT NULL,
    last_qbr_date TEXT NOT NULL,
    renewal_stage TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ============================================================================
-- Setup complete
-- ============================================================================
