-- stg_worldbank.sql
-- Staging model: World Bank development indicators
-- Filters and casts raw unified records from WorldBank source

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
WHERE source = 'WorldBank'
  AND indicator_value IS NOT NULL
  AND year IS NOT NULL