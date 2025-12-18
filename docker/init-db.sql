-- Create football_analytics database
CREATE DATABASE football_analytics;

-- Connect to football_analytics database
\c football_analytics

-- Create schema for raw data
CREATE SCHEMA IF NOT EXISTS raw;

-- Create schema for staging data
CREATE SCHEMA IF NOT EXISTS staging;

-- Create schema for analytics data
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE football_analytics TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA raw TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA staging TO airflow;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO airflow;
