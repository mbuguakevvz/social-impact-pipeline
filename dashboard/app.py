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
import json
import os

DB_PATH = "warehouse/social_impact.duckdb"

st.set_page_config(
    page_title="Kenya Social Impact Dashboard",
    page_icon="Kenya",
    layout="wide"
)

def run_query(sql):
    con = duckdb.connect(DB_PATH, read_only=True)
    result = con.execute(sql).fetchdf()
    con.close()
    return result

st.title("Kenya Social Impact Dashboard")
st.markdown("""
**Interoperability Pipeline** - Unified view across **UNHCR**, **WHO AFRO**, and **World Bank** data.
Built by [mbuguakevvz](https://github.com/mbuguakevvz)
""")
st.divider()

col1, col2, col3, col4 = st.columns(4)
total      = run_query("SELECT COUNT(*) AS n FROM unified_social_indicators")
sources    = run_query("SELECT COUNT(DISTINCT source) AS n FROM unified_social_indicators")
indicators = run_query("SELECT COUNT(DISTINCT indicator_name) AS n FROM unified_social_indicators")
years      = run_query("SELECT MIN(year) AS y1, MAX(year) AS y2 FROM unified_social_indicators")
col1.metric("Total Records",     f"{total['n'][0]:,}")
col2.metric("Data Sources",      f"{sources['n'][0]}")
col3.metric("Unique Indicators", f"{indicators['n'][0]}")
col4.metric("Year Range",        f"{years['y1'][0]} - {years['y2'][0]}")
st.divider()

st.sidebar.title("Filters")
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
selected_years = st.sidebar.slider("Year Range", min_value=y1, max_value=y2, value=(y1, y2))
st.sidebar.divider()
st.sidebar.markdown("**Pipeline Sources**")
st.sidebar.markdown("- UNHCR Refugee Data")
st.sidebar.markdown("- WHO AFRO Health Data")
st.sidebar.markdown("- World Bank Development Data")

st.subheader(f"Trend: {selected_indicator}")
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
        x="year", y="indicator_value",
        color="source", markers=True,
        title=f"{selected_indicator} over time",
        labels={"indicator_value": unit, "year": "Year"}
    )
    fig.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", legend_title="Source"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available for this selection.")

st.divider()

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Records by Source")
    source_counts = run_query("""
        SELECT source, COUNT(*) AS records
        FROM unified_social_indicators
        GROUP BY source ORDER BY records DESC
    """)
    fig2 = px.bar(
        source_counts, x="source", y="records", color="source",
        title="Total Records per Data Source"
    )
    fig2.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117",
        font_color="white", showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("Indicators by Source")
    ind_counts = run_query("""
        SELECT source, COUNT(DISTINCT indicator_name) AS unique_indicators
        FROM unified_social_indicators
        GROUP BY source ORDER BY unique_indicators DESC
    """)
    fig3 = px.pie(
        ind_counts, names="source", values="unique_indicators",
        title="Unique Indicators per Source"
    )
    fig3.update_layout(
        plot_bgcolor="#0e1117", paper_bgcolor="#0e1117", font_color="white"
    )
    st.plotly_chart(fig3, use_container_width=True)

st.divider()

st.subheader("Raw Unified Data")
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
st.caption("Data sources: UNHCR - WHO AFRO - World Bank | Pipeline by mbuguakevvz")
st.divider()

st.subheader("Kenya County-Level Social Indicators Map")
county_json = "data/raw/kenya_counties.json"
if os.path.exists(county_json):
    with open(county_json) as f:
        counties = json.load(f)
    county_df = pd.DataFrame(counties)
    map_indicator = st.selectbox(
        "Map Indicator",
        ["simulated_poverty_rate", "simulated_health_score"],
        format_func=lambda x: "Poverty Rate (%)" if x == "simulated_poverty_rate" else "Health Score"
    )
    label = "Poverty Rate (%)" if map_indicator == "simulated_poverty_rate" else "Health Score"
    fig_map = px.scatter_mapbox(
        county_df,
        lat="lat", lon="lon",
        size=map_indicator, color=map_indicator,
        hover_name="county",
        hover_data={
            "region": True,
            "simulated_poverty_rate": True,
            "simulated_health_score": True,
            "lat": False, "lon": False
        },
        color_continuous_scale="Reds",
        size_max=40, opacity=0.8,
        zoom=5, center={"lat": 0.0236, "lon": 37.9062},
        mapbox_style="carto-darkmatter",
        title=f"Kenya Counties - {label}",
        labels={map_indicator: label}
    )
    fig_map.update_layout(
        paper_bgcolor="#0e1117", font_color="white",
        height=600, margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title=label)
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption(f"Showing {len(county_df)} Kenya counties - Bubble size and color represent indicator intensity")
else:
    st.warning("County data not found. Run data/raw/generate_kenya_geojson.py first.")

st.divider()
st.subheader("Cross-Source Insights")
st.markdown("*Insights only possible by combining UNHCR + WHO AFRO + World Bank data together*")

refugees = run_query("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS refugees
    FROM unified_social_indicators
    WHERE indicator_name = 'refugee_population'
    AND year BETWEEN 2005 AND 2023
    ORDER BY year
""")
life_exp = run_query("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS life_expectancy
    FROM unified_social_indicators
    WHERE indicator_name = 'life_expectancy'
    AND year BETWEEN 2005 AND 2023
    ORDER BY year
""")
refugees["year"]  = refugees["year"].astype("int64")
life_exp["year"]  = life_exp["year"].astype("int64")
insight1          = pd.merge(refugees, life_exp, on="year", how="inner")
insight1["year_str"] = insight1["year"].astype(str)

st.markdown("### Insight 1: Refugee Population vs Life Expectancy Over Time")
st.markdown("""
> *As Kenya's refugee population grew from 251K (2005) to 539K (2023),
> life expectancy simultaneously rose from 54 to 64 years -
> suggesting humanitarian hosting and national development can co-exist.*
""")

if not insight1.empty:
    ref_min = insight1["refugees"].min()
    ref_max = insight1["refugees"].max()
    le_min  = insight1["life_expectancy"].min()
    le_max  = insight1["life_expectancy"].max()
    insight1["refugees_norm"]        = (insight1["refugees"] - ref_min) / (ref_max - ref_min) * 100
    insight1["life_expectancy_norm"] = (insight1["life_expectancy"] - le_min) / (le_max - le_min) * 100

    fig_i1 = go.Figure()
    fig_i1.add_trace(go.Scatter(
        x=insight1["year_str"],
        y=insight1["refugees_norm"],
        name=f"Refugee Population (max={int(ref_max):,})",
        mode="lines+markers",
        line=dict(color="#FF6B6B", width=3),
        marker=dict(size=8)
    ))
    fig_i1.add_trace(go.Scatter(
        x=insight1["year_str"],
        y=insight1["life_expectancy_norm"],
        name=f"Life Expectancy (max={le_max:.1f} yrs)",
        mode="lines+markers",
        line=dict(color="#4ECDC4", width=3),
        marker=dict(size=8)
    ))
    fig_i1.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white", height=400,
        yaxis=dict(title="Normalized Scale (0-100)", gridcolor="#333"),
        xaxis=dict(title="Year", gridcolor="#333"),
        legend=dict(bgcolor="#0e1117"),
        title="Both series normalized to 0-100 for comparison"
    )
    st.plotly_chart(fig_i1, use_container_width=True)

st.divider()

poverty = run_query("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS poverty_rate
    FROM unified_social_indicators
    WHERE indicator_name = 'poverty_headcount_ratio'
    ORDER BY year
""")
maternal = run_query("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS maternal_mortality
    FROM unified_social_indicators
    WHERE indicator_name = 'maternal_mortality_ratio'
    ORDER BY year
""")
poverty["year"]  = poverty["year"].astype("int64")
maternal["year"] = maternal["year"].astype("int64")
insight2         = pd.merge(poverty, maternal, on="year", how="inner")
insight2["year_str"] = insight2["year"].astype(str)

st.markdown("### Insight 2: Poverty Rate vs Maternal Mortality")
st.markdown("""
> *World Bank poverty data and WHO maternal mortality data together reveal
> that years with higher poverty headcount ratios correlate strongly
> with higher maternal mortality - making poverty reduction a health intervention.*
""")

if not insight2.empty:
    fig_i2 = go.Figure()
    fig_i2.add_trace(go.Scatter(
        x=insight2["poverty_rate"],
        y=insight2["maternal_mortality"],
        mode="markers+text",
        text=insight2["year_str"],
        textposition="top center",
        marker=dict(
            size=14,
            color=insight2["poverty_rate"],
            colorscale="Reds",
            showscale=True,
            colorbar=dict(title="Poverty %"),
            line=dict(width=1, color="white")
        ),
        name="Year"
    ))
    fig_i2.update_layout(
        title="Poverty Rate (%) vs Maternal Mortality (per 100k live births)",
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white", height=400,
        xaxis=dict(title="Poverty Rate (%)", gridcolor="#333"),
        yaxis=dict(title="Maternal Mortality (per 100k)", gridcolor="#333")
    )
    st.plotly_chart(fig_i2, use_container_width=True)

st.divider()

gdp = run_query("""
    SELECT CAST(year AS INTEGER) AS year, indicator_value AS gdp_per_capita
    FROM unified_social_indicators
    WHERE indicator_name = 'gdp_per_capita'
    AND year BETWEEN 2005 AND 2023
    ORDER BY year
""")
gdp["year"]      = gdp["year"].astype("int64")
refugees["year"] = refugees["year"].astype("int64")
insight3         = pd.merge(refugees, gdp, on="year", how="inner")
insight3["year_str"] = insight3["year"].astype(str)

st.markdown("### Insight 3: GDP per Capita vs Refugee Burden")
st.markdown("""
> *Even as Kenya's GDP per capita grew from 700 USD (2005) to 2000 USD (2023),
> the refugee population also grew - showing Kenya continues to absorb
> displacement pressure despite limited economic capacity.*
""")

if not insight3.empty:
    fig_i3 = go.Figure()
    fig_i3.add_trace(go.Bar(
        x=insight3["year_str"],
        y=insight3["gdp_per_capita"],
        name="GDP per Capita (USD)",
        marker_color="#45B7D1",
        yaxis="y1"
    ))
    fig_i3.add_trace(go.Scatter(
        x=insight3["year_str"],
        y=insight3["refugees"],
        name="Refugee Population",
        mode="lines+markers",
        line=dict(color="#FF6B6B", width=3),
        marker=dict(size=8),
        yaxis="y2"
    ))
    fig_i3.update_layout(
        paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
        font_color="white", height=400,
        xaxis=dict(title="Year", gridcolor="#333"),
        yaxis=dict(title="GDP per Capita (USD)", color="#45B7D1"),
        yaxis2=dict(
            title="Refugee Population",
            color="#FF6B6B",
            overlaying="y",
            side="right"
        ),
        legend=dict(bgcolor="#0e1117")
    )
    st.plotly_chart(fig_i3, use_container_width=True)

st.divider()
st.caption("Pipeline by mbuguakevvz - Data: UNHCR - WHO AFRO - World Bank - Built with DuckDB, dbt, FastAPI, Streamlit")