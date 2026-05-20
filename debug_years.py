import duckdb
import pandas as pd

con = duckdb.connect('warehouse/social_impact.duckdb', read_only=True)

refugees = con.execute("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS refugees
    FROM unified_social_indicators
    WHERE indicator_name = 'refugee_population'
    AND year BETWEEN 2005 AND 2023
    ORDER BY year
""").fetchdf()

life_exp = con.execute("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS life_expectancy
    FROM unified_social_indicators
    WHERE indicator_name = 'life_expectancy'
    AND year BETWEEN 2005 AND 2023
    ORDER BY year
""").fetchdf()

con.close()

print("Refugees dtypes:", refugees.dtypes)
print("Life exp dtypes:", life_exp.dtypes)
print("Refugees rows:", len(refugees))
print("Life exp rows:", len(life_exp))
print(refugees.head())
print(life_exp.head())

merged = pd.merge(refugees, life_exp, on="year", how="inner")
print("Merged rows:", len(merged))
print(merged)