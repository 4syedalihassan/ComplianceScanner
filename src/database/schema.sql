-- CIS Compliance Scanner Database Schema
-- PostgreSQL 15+

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =====================
-- USER MANAGEMENT
-- =====================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'viewer' CHECK (role IN ('admin', 'operator', 'viewer')),
    mfa_enabled BOOLEAN DEFAULT FALSE,
    mfa_secret_encrypted VARCHAR(255),
    mfa_backup_codes TEXT[],
    failed_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customer_access (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    access_level VARCHAR(20) DEFAULT 'read' CHECK (access_level IN ('read', 'write', 'admin')),
    PRIMARY KEY (user_id, customer_id)
);

-- =====================
-- CUSTOMERS
-- =====================

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(20) CHECK (type IN ('aws', 'onprem', 'hybrid')),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- AWS Account Registry
CREATE TABLE aws_accounts (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    account_id VARCHAR(12) NOT NULL,
    role_arn VARCHAR(2048) NOT NULL,
    region VARCHAR(20) DEFAULT 'us-east-1',
    external_id VARCHAR(256),
    enabled BOOLEAN DEFAULT TRUE,
    last_scan TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(customer_id, account_id)
);

-- On-Premise Environments
CREATE TABLE onprem_environments (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) CHECK (type IN ('linux', 'windows', 'network', 'vmware', 'kubernetes')),
    connection_type VARCHAR(50) CHECK (connection_type IN ('ssh', 'winrm', 'api', 'agent')),
    host VARCHAR(255),
    port INT DEFAULT 22,
    credentials_encrypted JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    last_scan TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Azure Environments  
CREATE TABLE azure_subscriptions (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    subscription_id VARCHAR(64) NOT NULL,
    tenant_id VARCHAR(64),
    client_id VARCHAR(64),
    client_secret_encrypted VARCHAR(512),
    enabled BOOLEAN DEFAULT TRUE,
    last_scan TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(customer_id, subscription_id)
);

-- GCP Projects
CREATE TABLE gcp_projects (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    project_id VARCHAR(64) NOT NULL,
    project_number VARCHAR(64),
    service_account_json_encrypted JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    last_scan TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(customer_id, project_id)
);

-- =====================
-- SCANS
-- =====================

CREATE TABLE scans (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    scan_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    findings_count INT DEFAULT 0,
    error_message TEXT,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- FINDINGS
-- =====================

CREATE TABLE findings (
    id SERIAL PRIMARY KEY,
    scan_id INT REFERENCES scans(id) ON DELETE CASCADE,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    control_id VARCHAR(50) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    severity VARCHAR(20) CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'fixed', 'accepted')),
    asset VARCHAR(255),
    remediation TEXT,
    raw_output JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- NOTIFICATIONS
-- =====================

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
    created_at TIMESTAMP DEFAULT NOW(),
    sent_at TIMESTAMP
);

CREATE TABLE notification_preferences (
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    event_type VARCHAR(50),
    enabled BOOLEAN DEFAULT TRUE,
    priority_threshold VARCHAR(20) DEFAULT 'medium',
    PRIMARY KEY (user_id, event_type)
);

-- =====================
-- EMAIL TEMPLATES
-- =====================

CREATE TABLE email_templates (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) UNIQUE NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body_html TEXT,
    body_text TEXT
);

-- =====================
-- AUDIT LOGGING
-- =====================

CREATE TABLE audit_login (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    event VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(512),
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_scans (
    id SERIAL PRIMARY KEY,
    scan_id INT REFERENCES scans(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    details JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- =====================
-- SCHEDULES
-- =====================

CREATE TABLE scan_schedules (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id) ON DELETE CASCADE,
    schedule_type VARCHAR(50) CHECK (schedule_type IN ('daily', 'weekly', 'monthly', 'custom')),
    cron_expression VARCHAR(100),
    scan_types TEXT[] DEFAULT '{}',
    enabled BOOLEAN DEFAULT TRUE,
    next_run TIMESTAMP,
    last_run TIMESTAMP,
    created_by INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================
-- INDEXES
-- =====================

CREATE INDEX idx_findings_customer ON findings(customer_id);
CREATE INDEX idx_findings_scan ON findings(scan_id);
CREATE INDEX idx_findings_severity ON findings(severity);
CREATE INDEX idx_findings_control ON findings(control_id);
CREATE INDEX idx_findings_status ON findings(status);

CREATE INDEX idx_scans_customer ON scans(customer_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_scans_created ON scans(created_at);

CREATE INDEX idx_aws_accounts_customer ON aws_accounts(customer_id);
CREATE INDEX idx_onprem_environments_customer ON onprem_environments(customer_id);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);

CREATE INDEX idx_audit_login_user ON audit_login(user_id);
CREATE INDEX idx_audit_login_timestamp ON audit_login(timestamp);

-- =====================
-- INITIAL DATA
-- =====================

-- Default admin user (password: ChangeMe123!)
-- Generate with: crypt('ChangeMe123!', gen_salt('bf', 12))
INSERT INTO users (email, password_hash, full_name, role) 
VALUES ('admin@cloudaisle.com', '$2b$12$LQv3c1GoBqC3kNnPaMQDuePJ6Oi2W/qJ.wZAZZHGKwRqJU2yHBR2Pa', 'System Admin', 'admin');

-- Email templates
INSERT INTO email_templates (event_type, subject, body_text) VALUES
('scan_completed', 'Scan Complete: {{customer_name}}', 
 'Hi {{user_name}},

Scan completed for {{customer_name}}.
Findings: {{finding_count}}
Score: {{compliance_score}}%

View the full report at: {{report_url}}'),
('finding_critical', 'CRITICAL: {{customer_name}}',
 'Hi {{user_name}},

Critical finding detected for {{customer_name}}:

Control: {{control_id}}
Title: {{finding_title}}
Asset: {{asset}}
Severity: {{severity}}

Remediation: {{remediation}}'),
('scan_failed', 'Scan Failed: {{customer_name}}',
 'Hi {{user_name}},

Scan failed for {{customer_name}}.

Error: {{error}}
Please investigate and retry.'),
('drift_detected', 'Compliance Drift: {{customer_name}}',
 'Hi {{user_name}},

Compliance drift detected for {{customer_name}}:

New failures: {{new_failures}}
Fixed: {{fixed}}
Severity increases: {{severity_increases}}

View changes at: {{report_url}}'),
('user_login_fail', 'Failed Login Attempt',
 'Hi {{user_name}},

Failed login attempt detected.

Time: {{timestamp}}
IP: {{ip_address}}
Attempts: {{attempt_count}}

If this wasn''t you, please reset your password.');