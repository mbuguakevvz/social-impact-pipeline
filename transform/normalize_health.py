"""
Transform Script 3: Normalize WHO AFRO health raw data
"""

import pandas as pd
import uuid
import os
from datetime import datetime

RAW_PATH = "data/raw/who_kenya_health_raw.csv"
OUT_PATH = "data/processed/health_normalized.csv"

UNIT_MAP = {
    "maternal_mortality_ratio":   "per_100000_live_births",
    "dtp3_immunization_coverage": "percent",
    "tuberculosis_incidence":     "per_100000_population",
    "skilled_birth_attendance":   "percent"
}

def normalize():
    print("Normalizing WHO AFRO health data...")
    df = pd.read_csv(RAW_PATH)

    normalized = []
    for _, row in df.iterrows():
        normalized.append({
            "record_id":       str(uuid.uuid4()),
            "source":          "WHO_AFRO",
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
    print(f"✅ WHO AFRO: {len(out_df)} records → {OUT_PATH}")
    return out_df

if __name__ == "__main__":
    df = normalize()
    print(df.head())