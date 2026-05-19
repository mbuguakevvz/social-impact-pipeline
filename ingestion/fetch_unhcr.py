"""
Ingestion Script 2: UNHCR Refugee Data API
Fetches refugee and asylum seeker population data for Kenya
Source: https://api.unhcr.org/population/v1/
"""

import requests
import pandas as pd
import os
from datetime import datetime

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://api.unhcr.org/population/v1/population/"

def fetch_unhcr_kenya():
    print("=" * 50)
    print("UNHCR Ingestion Started")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 50)

    params = {
        "limit": 100,
        "dataset": "population",
        "displayType": "totals",
        "coa": "KEN",         # Country of asylum = Kenya
        "yearFrom": 2005,
        "yearTo": 2023
    }

    print("  Fetching UNHCR population data for Kenya...")
    response = requests.get(BASE_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    items = data.get("items", [])

    if not items:
        print("  WARNING: No items returned from UNHCR API")
        return

    records = []
    for entry in items:
        records.append({
            "country_of_origin":        entry.get("coo_name", "Unknown"),
            "country_of_origin_code":   entry.get("coo", ""),
            "country_of_asylum":        entry.get("coa_name", "Kenya"),
            "country_of_asylum_code":   entry.get("coa", "KEN"),
            "year":                     entry.get("year"),
            "refugees":                 entry.get("refugees", 0),
            "asylum_seekers":           entry.get("asylum_seekers", 0),
            "idps":                     entry.get("idps", 0),
            "stateless":                entry.get("stateless", 0),
            "total_population":         entry.get("totalPopulation", 0),
            "source":                   "UNHCR"
        })

    df = pd.DataFrame(records)
    output_path = os.path.join(RAW_DIR, "unhcr_kenya_raw.csv")
    df.to_csv(output_path, index=False)

    print(f"\n✅ Saved {len(df)} records to {output_path}")
    print(df.head(10).to_string())

if __name__ == "__main__":
    fetch_unhcr_kenya()