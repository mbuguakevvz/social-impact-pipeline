"""
Ingestion Script 3: WHO AFRO / Global Health Observatory
Fetches Kenya health indicators:
  - Maternal mortality ratio
  - Immunization coverage (DTP3)
  - Tuberculosis incidence
  - Skilled birth attendance
Source: https://ghoapi.azureedge.net/api/
"""

import requests
import pandas as pd
import os
from datetime import datetime

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://ghoapi.azureedge.net/api/{indicator}"

INDICATORS = {
    "MDG_0000000026":   "maternal_mortality_ratio",
    "WHS4_544":         "dtp3_immunization_coverage",
    "MDG_0000000020":   "tuberculosis_incidence",
    "WHS4_543":         "skilled_birth_attendance"
}

COUNTRY_CODE = "KEN"

def fetch_who_indicator(indicator_code, indicator_name):
    url = BASE_URL.format(indicator=indicator_code)
    params = {"$filter": f"SpatialDim eq '{COUNTRY_CODE}'"}

    print(f"  Fetching: {indicator_name} ({indicator_code})...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    items = data.get("value", [])

    if not items:
        print(f"  WARNING: No data for {indicator_name}")
        return []

    records = []
    for entry in items:
        value = entry.get("NumericValue")
        year = entry.get("TimeDim")
        if value is not None and year is not None:
            records.append({
                "country":          "Kenya",
                "country_code":     COUNTRY_CODE,
                "indicator_code":   indicator_code,
                "indicator_name":   indicator_name,
                "year":             int(year),
                "value":            float(value),
                "source":           "WHO_AFRO"
            })

    print(f"  Got {len(records)} records.")
    return records

def run():
    print("=" * 50)
    print("WHO AFRO Health Ingestion Started")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 50)

    all_records = []

    for code, name in INDICATORS.items():
        records = fetch_who_indicator(code, name)
        all_records.extend(records)

    df = pd.DataFrame(all_records)
    output_path = os.path.join(RAW_DIR, "who_kenya_health_raw.csv")
    df.to_csv(output_path, index=False)

    print(f"\n✅ Saved {len(df)} total records to {output_path}")
    print(df.head(10).to_string())

if __name__ == "__main__":
    run()