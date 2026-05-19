-- mart_development_indicators.sql
-- Mart: World Bank development indicators for Kenya
-- Pivots into wide format with one row per year

SELECT
    year,
    MAX(CASE WHEN indicator_name = 'poverty_headcount_ratio'
        THEN indicator_value END)               AS poverty_headcount_ratio,
    MAX(CASE WHEN indicator_name = 'literacy_rate'
        THEN indicator_value END)               AS literacy_rate,
    MAX(CASE WHEN indicator_name = 'life_expectancy'
        THEN indicator_value END)               AS life_expectancy,
    MAX(CASE WHEN indicator_name = 'gdp_per_capita'
        THEN indicator_value END)               AS gdp_per_capita
FROM {{ ref('stg_worldbank') }}
GROUP BY year
ORDER BY year ASC