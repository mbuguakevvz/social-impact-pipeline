-- Unified Social Impact Schema
-- All sources are normalized into this single table

CREATE SEQUENCE IF NOT EXISTS record_seq;

CREATE TABLE IF NOT EXISTS unified_social_indicators (
    record_id       VARCHAR PRIMARY KEY,
    source          VARCHAR NOT NULL,
    country         VARCHAR(10) NOT NULL,
    region          VARCHAR(100),
    indicator_name  VARCHAR(150) NOT NULL,
    indicator_value DOUBLE,
    unit            VARCHAR(50),
    year            INTEGER,
    ingested_at     TIMESTAMP DEFAULT current_timestamp
);