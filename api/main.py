"""
Phase 4: FastAPI Exposure Layer
Social Impact Interoperability Pipeline
Exposes unified DuckDB warehouse via REST endpoints
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import duckdb
import os

DB_PATH = "warehouse/social_impact.duckdb"

app = FastAPI(
    title="Kenya Social Impact API",
    description="Unified interoperability API combining UNHCR, WHO AFRO, and World Bank data for Kenya.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

def get_con():
    return duckdb.connect(DB_PATH, read_only=True)


# ─────────────────────────────────────────
# ROOT
# ─────────────────────────────────────────
@app.get("/")
def root():
    return {
        "project": "Kenya Social Impact Interoperability Pipeline",
        "author":  "mbuguakevvz",
        "version": "1.0.0",
        "endpoints": [
            "/indicators",
            "/sources",
            "/data",
            "/summary",
            "/trend"
        ]
    }


# ─────────────────────────────────────────
# LIST ALL UNIQUE INDICATORS
# ─────────────────────────────────────────
@app.get("/indicators")
def list_indicators():
    """Returns all unique indicator names across all sources."""
    con = get_con()
    result = con.execute("""
        SELECT DISTINCT indicator_name, source, unit
        FROM unified_social_indicators
        ORDER BY source, indicator_name
    """).fetchdf()
    con.close()
    return result.to_dict(orient="records")


# ─────────────────────────────────────────
# LIST ALL SOURCES
# ─────────────────────────────────────────
@app.get("/sources")
def list_sources():
    """Returns record counts per source."""
    con = get_con()
    result = con.execute("""
        SELECT
            source,
            COUNT(*)            AS total_records,
            MIN(year)           AS earliest_year,
            MAX(year)           AS latest_year
        FROM unified_social_indicators
        GROUP BY source
        ORDER BY source
    """).fetchdf()
    con.close()
    return result.to_dict(orient="records")


# ─────────────────────────────────────────
# QUERY DATA
# ─────────────────────────────────────────
@app.get("/data")
def get_data(
    source:         Optional[str] = Query(None, description="Filter by source: UNHCR, WorldBank, WHO_AFRO"),
    indicator_name: Optional[str] = Query(None, description="Filter by indicator name"),
    year_from:      Optional[int] = Query(None, description="Start year"),
    year_to:        Optional[int] = Query(None, description="End year"),
    limit:          int           = Query(100,  description="Max records to return")
):
    """
    Query the unified social indicators warehouse.
    Supports filtering by source, indicator, and year range.
    """
    con = get_con()

    filters = []
    if source:
        filters.append(f"source = '{source}'")
    if indicator_name:
        filters.append(f"indicator_name = '{indicator_name}'")
    if year_from:
        filters.append(f"year >= {year_from}")
    if year_to:
        filters.append(f"year <= {year_to}")

    where_clause = ("WHERE " + " AND ".join(filters)) if filters else ""

    query = f"""
        SELECT
            source,
            country,
            region,
            indicator_name,
            indicator_value,
            unit,
            year
        FROM unified_social_indicators
        {where_clause}
        ORDER BY year DESC
        LIMIT {limit}
    """

    result = con.execute(query).fetchdf()
    con.close()

    return {
        "count":  len(result),
        "data":   result.to_dict(orient="records")
    }


# ─────────────────────────────────────────
# SUMMARY STATISTICS
# ─────────────────────────────────────────
@app.get("/summary")
def get_summary():
    """Returns summary statistics across all indicators and sources."""
    con = get_con()
    result = con.execute("""
        SELECT
            source,
            indicator_name,
            unit,
            COUNT(*)                        AS data_points,
            ROUND(MIN(indicator_value), 2)  AS min_value,
            ROUND(MAX(indicator_value), 2)  AS max_value,
            ROUND(AVG(indicator_value), 2)  AS avg_value,
            MIN(year)                       AS year_from,
            MAX(year)                       AS year_to
        FROM unified_social_indicators
        GROUP BY source, indicator_name, unit
        ORDER BY source, indicator_name
    """).fetchdf()
    con.close()
    return result.to_dict(orient="records")


# ─────────────────────────────────────────
# TREND FOR A SPECIFIC INDICATOR
# ─────────────────────────────────────────
@app.get("/trend")
def get_trend(
    indicator_name: str = Query(..., description="Indicator name to trend"),
    source:         Optional[str] = Query(None, description="Filter by source")
):
    """Returns year-by-year trend for a specific indicator."""
    con = get_con()

    source_filter = f"AND source = '{source}'" if source else ""

    result = con.execute(f"""
        SELECT
            year,
            source,
            indicator_name,
            indicator_value,
            unit
        FROM unified_social_indicators
        WHERE indicator_name = '{indicator_name}'
        {source_filter}
        ORDER BY year ASC
    """).fetchdf()
    con.close()

    if result.empty:
        return {"message": f"No data found for indicator: {indicator_name}"}

    return {
        "indicator": indicator_name,
        "data_points": len(result),
        "trend": result.to_dict(orient="records")
    }