"""
Transform Script 4: Merge all normalized CSVs into DuckDB warehouse
Applies unified schema from schema/unified_schema.sql
"""

import duckdb
import pandas as pd
import os
from datetime import datetime

DB_PATH = "warehouse/social_impact.duckdb"
SCHEMA_PATH = "schema/unified_schema.sql"

NORMALIZED_FILES = [
    "data/processed/worldbank_normalized.csv",
    "data/processed/unhcr_normalized.csv",
    "data/processed/health_normalized.csv"
]

def load_to_duckdb():
    print("=" * 50)
    print("Loading unified data into DuckDB")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 50)

    os.makedirs("warehouse", exist_ok=True)
    con = duckdb.connect(DB_PATH)

    # Apply schema
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    con.execute(schema_sql)
    print("✅ Schema applied")

    # Load each normalized file
    total = 0
    for filepath in NORMALIZED_FILES:
        if not os.path.exists(filepath):
            print(f"  WARNING: {filepath} not found, skipping.")
            continue

        df = pd.read_csv(filepath)
        con.execute("""
            INSERT INTO unified_social_indicators
            SELECT
                record_id,
                source,
                country,
                region,
                indicator_name,
                indicator_value,
                unit,
                year,
                CAST(ingested_at AS TIMESTAMP)
            FROM df
        """)
        print(f"  Loaded {len(df)} records from {filepath}")
        total += len(df)

    print(f"\n✅ Total records in DuckDB: {total}")

    # Quick verification query
    print("\n--- Sample from unified_social_indicators ---")
    result = con.execute("""
        SELECT source, indicator_name, year, indicator_value, unit
        FROM unified_social_indicators
        ORDER BY source, year DESC
        LIMIT 15
    """).fetchdf()
    print(result.to_string())

    # Summary by source
    print("\n--- Record count by source ---")
    summary = con.execute("""
        SELECT source, COUNT(*) as record_count
        FROM unified_social_indicators
        GROUP BY source
        ORDER BY source
    """).fetchdf()
    print(summary.to_string())

    con.close()
    print(f"\n✅ DuckDB warehouse saved to {DB_PATH}")

if __name__ == "__main__":
    load_to_duckdb()