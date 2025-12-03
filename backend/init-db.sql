-- CloudPulse Monitor Database Initialization Script
-- This script sets up the initial database schema and sample data

-- Create database if it doesn't exist (handled by POSTGRES_DB env var)
-- CREATE DATABASE IF NOT EXISTS cloudpulse;

-- Connect to the cloudpulse database
\c cloudpulse;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create logs table
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    level VARCHAR(20) NOT NULL CHECK (level IN ('info', 'warning', 'error', 'debug')),
    message TEXT NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_logs_service_level ON logs(service_name, level);
CREATE INDEX IF NOT EXISTS idx_logs_level ON logs(level);

-- Create services table
CREATE TABLE IF NOT EXISTS services (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('online', 'degraded', 'offline')),
    uptime DECIMAL(5,2) DEFAULT 0.0 CHECK (uptime >= 0.0 AND uptime <= 100.0),
    last_checked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create metrics table for historical data
CREATE TABLE IF NOT EXISTS metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(50) NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    unit VARCHAR(20),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for metrics
CREATE INDEX IF NOT EXISTS idx_metrics_name_timestamp ON metrics(metric_name, timestamp DESC);

-- Insert initial services data
INSERT INTO services (id, name, status, uptime, last_checked) VALUES
    ('api-gateway', 'API Gateway', 'online', 99.98, NOW()),
    ('user-service', 'User Service', 'online', 99.95, NOW()),
    ('payment-service', 'Payment Service', 'online', 99.87, NOW()),
    ('notification-service', 'Notification Service', 'degraded', 98.45, NOW()),
    ('analytics-service', 'Analytics Service', 'online', 99.92, NOW()),
    ('file-storage', 'File Storage', 'online', 99.99, NOW())
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    status = EXCLUDED.status,
    uptime = EXCLUDED.uptime,
    last_checked = EXCLUDED.last_checked,
    updated_at = NOW();

-- Insert sample log entries
INSERT INTO logs (level, message, service_name, timestamp) VALUES
    ('info', 'Service started successfully', 'api-gateway', NOW() - INTERVAL '1 hour'),
    ('info', 'Database connection established', 'user-service', NOW() - INTERVAL '50 minutes'),
    ('warning', 'High memory usage detected', 'payment-service', NOW() - INTERVAL '30 minutes'),
    ('error', 'Failed to connect to external API', 'notification-service', NOW() - INTERVAL '25 minutes'),
    ('info', 'Batch processing completed', 'analytics-service', NOW() - INTERVAL '20 minutes'),
    ('info', 'File upload successful', 'file-storage', NOW() - INTERVAL '15 minutes'),
    ('warning', 'Slow query detected', 'user-service', NOW() - INTERVAL '10 minutes'),
    ('error', 'Payment processing failed', 'payment-service', NOW() - INTERVAL '5 minutes'),
    ('info', 'Cache cleared successfully', 'api-gateway', NOW() - INTERVAL '2 minutes'),
    ('info', 'Health check passed', 'analytics-service', NOW() - INTERVAL '1 minute');

-- Insert sample metrics data
INSERT INTO metrics (metric_name, value, unit, timestamp) VALUES
    ('cpu_usage', 45.2, 'percent', NOW() - INTERVAL '5 minutes'),
    ('memory_usage', 68.7, 'percent', NOW() - INTERVAL '5 minutes'),
    ('network_traffic', 342.5, 'mbps', NOW() - INTERVAL '5 minutes'),
    ('disk_usage', 78.3, 'percent', NOW() - INTERVAL '5 minutes'),
    ('active_connections', 156, 'count', NOW() - INTERVAL '5 minutes');

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for services table
DROP TRIGGER IF EXISTS update_services_updated_at ON services;
CREATE TRIGGER update_services_updated_at
    BEFORE UPDATE ON services
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (if needed for specific user)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Display initialization completion message
SELECT 'CloudPulse Monitor database initialized successfully!' as status;