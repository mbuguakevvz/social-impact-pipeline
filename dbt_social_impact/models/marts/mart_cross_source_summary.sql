-- mart_cross_source_summary.sql
-- Mart: Cross-source unified summary
-- Joins displacement, health, and development data by year
-- This is the core interoperability model

WITH displacement AS (
    SELECT * FROM {{ ref('mart_displacement_trends') }}
),
health AS (
    SELECT * FROM {{ ref('mart_health_outcomes') }}
),
development AS (
    SELECT * FROM {{ ref('mart_development_indicators') }}
),
all_years AS (
    SELECT DISTINCT year FROM displacement
    UNION
    SELECT DISTINCT year FROM health
    UNION
    SELECT DISTINCT year FROM development
)
SELECT
    a.year,

    -- Displacement
    d.refugee_population,
    d.asylum_seeker_population,
    d.idp_population,
    d.total_displaced,

    -- Health
    h.maternal_mortality_ratio,
    h.dtp3_immunization_coverage,
    h.tuberculosis_incidence,
    h.skilled_birth_attendance,

    -- Development
    dev.poverty_headcount_ratio,
    dev.life_expectancy,
    dev.gdp_per_capita

FROM all_years a
LEFT JOIN displacement  d   ON a.year = d.year
LEFT JOIN health        h   ON a.year = h.year
LEFT JOIN development   dev ON a.year = dev.year
ORDER BY a.year ASC