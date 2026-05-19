"""
Transform Script 2: Normalize UNHCR raw data
Unpivots refugee/asylum/idp columns into unified schema rows
"""

import pandas as pd
import uuid
import os
from datetime import datetime

RAW_PATH = "data/raw/unhcr_kenya_raw.csv"
OUT_PATH = "data/processed/unhcr_normalized.csv"

# Each of these columns becomes a separate indicator row
POPULATION_COLUMNS = {
    "refugees":        ("refugee_population",  "count"),
    "asylum_seekers":  ("asylum_seeker_population", "count"),
    "idps":            ("internally_displaced_population", "count"),
    "stateless":       ("stateless_population", "count")
}

def normalize():
    print("Normalizing UNHCR data...")
    df = pd.read_csv(RAW_PATH)

    normalized = []
    for _, row in df.iterrows():
        for col, (indicator_name, unit) in POPULATION_COLUMNS.items():
            value = row.get(col, 0)
            # Skip zero values — not meaningful for displacement data
            if pd.isna(value) or float(value) == 0:
                continue
            normalized.append({
                "record_id":       str(uuid.uuid4()),
                "source":          "UNHCR",
                "country":         "KEN",
                "region":          "National",
                "indicator_name":  indicator_name,
                "indicator_value": float(value),
                "unit":            unit,
                "year":            int(row["year"]),
                "ingested_at":     datetime.utcnow().isoformat()
            })

    out_df = pd.DataFrame(normalized)
    os.makedirs("data/processed", exist_ok=True)
    out_df.to_csv(OUT_PATH, index=False)
    print(f"✅ UNHCR: {len(out_df)} records → {OUT_PATH}")
    return out_df

if __name__ == "__main__":
    df = normalize()
    print(df.head())