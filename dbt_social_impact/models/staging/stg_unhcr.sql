-- stg_unhcr.sql
-- Staging model: UNHCR displacement data
-- Filters and casts raw unified records from UNHCR source

SELECT
    record_id,
    source,
    country,
    region,
    indicator_name,
    CAST(indicator_value AS DOUBLE)  AS indicator_value,
    unit,
    CAST(year AS INTEGER)            AS year,
    ingested_at
FROM {{ source('warehouse', 'unified_social_indicators') }}
WHERE source = 'UNHCR'
  AND indicator_value IS NOT NULL
  AND year IS NOT NULL