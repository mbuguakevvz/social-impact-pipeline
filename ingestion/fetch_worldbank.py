"""
Ingestion Script 1: World Bank API
Fetches Kenya development indicators:
  - Poverty headcount ratio (SI.POV.DDAY)
  - Literacy rate (SE.ADT.LITR.ZS)
  - Life expectancy (SP.DYN.LE00.IN)
  - GDP per capita (NY.GDP.PCAP.CD)
Source: https://api.worldbank.org/v2/
"""

import requests
import pandas as pd
import os
import json
from datetime import datetime

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

INDICATORS = {
    "SI.POV.DDAY": "poverty_headcount_ratio",
    "SE.ADT.LITR.ZS": "literacy_rate",
    "SP.DYN.LE00.IN": "life_expectancy",
    "NY.GDP.PCAP.CD": "gdp_per_capita"
}

COUNTRY = "KE"
BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

def fetch_indicator(indicator_code, indicator_name):
    url = BASE_URL.format(country=COUNTRY, indicator=indicator_code)
    params = {
        "format": "json",
        "per_page": 100,
        "mrv": 20  # Most recent 20 years
    }

    print(f"  Fetching: {indicator_name} ({indicator_code})...")
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    # World Bank returns [metadata, records]
    if len(data) < 2 or not data[1]:
        print(f"  WARNING: No data returned for {indicator_name}")
        return []

    records = []
    for entry in data[1]:
        if entry.get("value") is not None:
            records.append({
                "country": entry["country"]["value"],
                "country_code": entry["countryiso3code"],
                "indicator_code": indicator_code,
                "indicator_name": indicator_name,
                "year": int(entry["date"]),
                "value": float(entry["value"]),
                "source": "WorldBank"
            })

    print(f"  Got {len(records)} records.")
    return records

def run():
    print("=" * 50)
    print("World Bank Ingestion Started")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    print("=" * 50)

    all_records = []

    for code, name in INDICATORS.items():
        records = fetch_indicator(code, name)
        all_records.extend(records)

    df = pd.DataFrame(all_records)
    output_path = os.path.join(RAW_DIR, "worldbank_kenya_raw.csv")
    df.to_csv(output_path, index=False)

    print(f"\n✅ Saved {len(df)} total records to {output_path}")
    print(df.head(10).to_string())

if __name__ == "__main__":
    run()