-- mart_health_outcomes.sql
-- Mart: Kenya health outcome indicators over time
-- Pivots WHO AFRO indicators into wide format for easy charting

SELECT
    year,
    MAX(CASE WHEN indicator_name = 'maternal_mortality_ratio'
        THEN indicator_value END)               AS maternal_mortality_ratio,
    MAX(CASE WHEN indicator_name = 'dtp3_immunization_coverage'
        THEN indicator_value END)               AS dtp3_immunization_coverage,
    MAX(CASE WHEN indicator_name = 'tuberculosis_incidence'
        THEN indicator_value END)               AS tuberculosis_incidence,
    MAX(CASE WHEN indicator_name = 'skilled_birth_attendance'
        THEN indicator_value END)               AS skilled_birth_attendance
FROM {{ ref('stg_who_afro') }}
GROUP BY year
ORDER BY year ASC