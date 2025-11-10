-- Database initialization script
-- Run this script to set up the database for the first time

-- Create database (if using psql directly)
-- CREATE DATABASE agentsandbox;

-- Connect to database
\c agentsandbox;

-- Run the main schema
\i /docker-entrypoint-initdb.d/schema.sql

-- Insert initial audit log
INSERT INTO audit_logs (event_type, event_data)
VALUES ('database_initialized', '{"message": "Database schema created successfully", "version": "1.0.0"}');

-- Display success message
SELECT 'Database initialized successfully!' AS status;
SELECT 'Extensions installed:' AS info;
SELECT extname FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector', 'pg_trgm', 'pgcrypto');
