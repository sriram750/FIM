-- PostgreSQL Database Initialization Script for FIM Enterprise
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE fim_enterprise TO fim_admin;
