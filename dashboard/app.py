"""
Phase 5: Streamlit Dashboard
Kenya Social Impact Interoperability Pipeline
Visual interface over the unified DuckDB warehouse
"""

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

DB_PATH = "warehouse/social_impact.duckdb"

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="Kenya Social Impact Dashboard",
    page_icon="🇰🇪",
    layout="wide"
)

# ─────────────────────────────────────────
# DB CONNECTION
# ─────────────────────────────────────────
@st.cache_resource
def get_con():
    return duckdb.connect(DB_PATH, read_only=True)

@st.cache_data
def run_query(sql):
    con = get_con()
    return con.execute(sql).fetchdf()

# ─────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────
st.title("🇰🇪 Kenya Social Impact Dashboard")
st.markdown("""
**Interoperability Pipeline** — Unified view across **UNHCR**, **WHO AFRO**, and **World Bank** data.
Built by [mbuguakevvz](https://github.com/mbuguakevvz)
""")
st.divider()

# ─────────────────────────────────────────
# TOP KPI METRICS
# ─────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

total = run_query("SELECT COUNT(*) AS n FROM unified_social_indicators")
sources = run_query("SELECT COUNT(DISTINCT source) AS n FROM unified_social_indicators")
indicators = run_query("SELECT COUNT(DISTINCT indicator_name) AS n FROM unified_social_indicators")
years = run_query("SELECT MIN(year) AS y1, MAX(year) AS y2 FROM unified_social_indicators")

col1.metric("Total Records",    f"{total['n'][0]:,}")
col2.metric("Data Sources",     f"{sources['n'][0]}")
col3.metric("Unique Indicators",f"{indicators['n'][0]}")
col4.metric("Year Range",       f"{years['y1'][0]} – {years['y2'][0]}")

st.divider()

# ─────────────────────────────────────────
# SIDEBAR FILTERS
# ─────────────────────────────────────────
st.sidebar.title("🔎 Filters")

all_sources = run_query("SELECT DISTINCT source FROM unified_social_indicators ORDER BY source")
selected_source = st.sidebar.selectbox(
    "Select Data Source",
    ["All"] + all_sources["source"].tolist()
)

if selected_source != "All":
    ind_filter = f"WHERE source = '{selected_source}'"
else:
    ind_filter = ""

all_indicators = run_query(f"""
    SELECT DISTINCT indicator_name FROM unified_social_indicators
    {ind_filter}
    ORDER BY indicator_name
""")
selected_indicator = st.sidebar.selectbox(
    "Select Indicator",
    all_indicators["indicator_name"].tolist()
)

year_range = run_query("SELECT MIN(year) AS y1, MAX(year) AS y2 FROM unified_social_indicators")
y1 = int(year_range["y1"][0])
y2 = int(year_range["y2"][0])

selected_years = st.sidebar.slider(
    "Year Range",
    min_value=y1,
    max_value=y2,
    value=(y1, y2)
)

st.sidebar.divider()
st.sidebar.markdown("**Pipeline Sources**")
st.sidebar.markdown("- 🌍 UNHCR Refugee Data")
st.sidebar.markdown("- 🏥 WHO AFRO Health Data")
st.sidebar.markdown("- 🏦 World Bank Development Data")

# ─────────────────────────────────────────
# TREND CHART
# ─────────────────────────────────────────
st.subheader(f"📈 Trend: {selected_indicator}")

source_filter = f"AND source = '{selected_source}'" if selected_source != "All" else ""

trend_data = run_query(f"""
    SELECT year, source, indicator_value, unit
    FROM unified_social_indicators
    WHERE indicator_name = '{selected_indicator}'
    {source_filter}
    AND year BETWEEN {selected_years[0]} AND {selected_years[1]}
    ORDER BY year ASC
""")

if not trend_data.empty:
    unit = trend_data["unit"].iloc[0]
    fig = px.line(
        trend_data,
        x="year",
        y="indicator_value",
        color="source",
        markers=True,
        title=f"{selected_indicator} over time",
        labels={"indicator_value": unit, "year": "Year"}
    )
    fig.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white",
        legend_title="Source"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for this selection.")

st.divider()

# ─────────────────────────────────────────
# RECORDS BY SOURCE BAR CHART
# ─────────────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("📊 Records by Source")
    source_counts = run_query("""
        SELECT source, COUNT(*) AS records
        FROM unified_social_indicators
        GROUP BY source ORDER BY records DESC
    """)
    fig2 = px.bar(
        source_counts,
        x="source", y="records",
        color="source",
        title="Total Records per Data Source"
    )
    fig2.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white",
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("📋 Indicators by Source")
    ind_counts = run_query("""
        SELECT source, COUNT(DISTINCT indicator_name) AS unique_indicators
        FROM unified_social_indicators
        GROUP BY source ORDER BY unique_indicators DESC
    """)
    fig3 = px.pie(
        ind_counts,
        names="source",
        values="unique_indicators",
        title="Unique Indicators per Source"
    )
    fig3.update_layout(
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font_color="white"
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

# ─────────────────────────────────────────
# RAW DATA TABLE
# ─────────────────────────────────────────
st.subheader("🗃️ Raw Unified Data")

if selected_source != "All":
    table_filter = f"WHERE source = '{selected_source}'"
else:
    table_filter = ""

table_data = run_query(f"""
    SELECT source, indicator_name, year, indicator_value, unit, region
    FROM unified_social_indicators
    {table_filter}
    ORDER BY year DESC
    LIMIT 200
""")

st.dataframe(table_data, use_container_width=True)

st.caption("Data sources: UNHCR · WHO AFRO · World Bank | Pipeline by mbuguakevvz")