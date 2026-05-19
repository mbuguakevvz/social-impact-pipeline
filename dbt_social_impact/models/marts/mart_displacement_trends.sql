-- mart_displacement_trends.sql
-- Mart: Year-by-year displacement trends in Kenya
-- Combines refugee, asylum seeker, IDP and stateless populations

SELECT
    year,
    MAX(CASE WHEN indicator_name = 'refugee_population'
        THEN indicator_value END)               AS refugee_population,
    MAX(CASE WHEN indicator_name = 'asylum_seeker_population'
        THEN indicator_value END)               AS asylum_seeker_population,
    MAX(CASE WHEN indicator_name = 'internally_displaced_population'
        THEN indicator_value END)               AS idp_population,
    MAX(CASE WHEN indicator_name = 'stateless_population'
        THEN indicator_value END)               AS stateless_population,
    SUM(indicator_value)                        AS total_displaced
FROM {{ ref('stg_unhcr') }}
GROUP BY year
ORDER BY year ASC