"""
Transform Script 1: Normalize World Bank raw data
Maps to unified_social_indicators schema
"""

import pandas as pd
import uuid
import os
from datetime import datetime

RAW_PATH = "data/raw/worldbank_kenya_raw.csv"
OUT_PATH = "data/processed/worldbank_normalized.csv"

UNIT_MAP = {
    "poverty_headcount_ratio": "percent",
    "literacy_rate":           "percent",
    "life_expectancy":         "years",
    "gdp_per_capita":          "USD"
}

def normalize():
    print("Normalizing World Bank data...")
    df = pd.read_csv(RAW_PATH)

    normalized = []
    for _, row in df.iterrows():
        normalized.append({
            "record_id":       str(uuid.uuid4()),
            "source":          "WorldBank",
            "country":         "KEN",
            "region":          "National",
            "indicator_name":  row["indicator_name"],
            "indicator_value": round(float(row["value"]), 4),
            "unit":            UNIT_MAP.get(row["indicator_name"], "unknown"),
            "year":            int(row["year"]),
            "ingested_at":     datetime.utcnow().isoformat()
        })

    out_df = pd.DataFrame(normalized)
    os.makedirs("data/processed", exist_ok=True)
    out_df.to_csv(OUT_PATH, index=False)
    print(f"✅ WorldBank: {len(out_df)} records → {OUT_PATH}")
    return out_df

if __name__ == "__main__":
    df = normalize()
    print(df.head())