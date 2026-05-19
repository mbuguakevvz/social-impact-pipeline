# 🇰🇪 Kenya Social Impact Interoperability Pipeline

A production-grade data engineering pipeline that ingests, normalizes, and unifies
social impact data from three international sources into a single queryable warehouse —
exposed via a REST API and an interactive dashboard.

---

## 🎯 Problem Statement

Social impact data in Kenya is fragmented across dozens of organizations — UN agencies,
government bodies, NGOs, and global banks — each publishing data in different formats,
schemas, and standards. This makes cross-sector analysis nearly impossible without
significant manual effort.

This pipeline solves that by building an **interoperability layer** that standardizes
heterogeneous data into one unified schema, enabling analysts, policymakers, and
humanitarian organizations to query across datasets that were previously siloed.

---

## 📦 Data Sources

| Source | Data | Records |
|--------|------|---------|
| [UNHCR Population API](https://api.unhcr.org) | Refugee, IDP & stateless populations in Kenya (2005–2023) | 61 |
| [WHO AFRO / GHO API](https://ghoapi.azureedge.net) | Maternal mortality, immunization, TB incidence (1985–2022) | 114 |
| [World Bank API](https://api.worldbank.org) | Poverty, literacy, life expectancy, GDP per capita (1992–2024) | 49 |

**Total: 224 records · 12 indicators · 3 sources · 1985–2024**

---

## 🏗️ Architecture
---

## 🗂️ Project Structure
---

## 🔁 Unified Schema

All sources are normalized into one table:

```sql
unified_social_indicators (
    record_id        VARCHAR PRIMARY KEY,   -- UUID
    source           VARCHAR,               -- UNHCR | WorldBank | WHO_AFRO
    country          VARCHAR,               -- ISO3 code (KEN)
    region           VARCHAR,               -- National / County
    indicator_name   VARCHAR,               -- e.g. refugee_population
    indicator_value  DOUBLE,                -- numeric value
    unit             VARCHAR,               -- percent | count | years | USD
    year             INTEGER,               -- observation year
    ingested_at      TIMESTAMP              -- pipeline run time
)
```

---

## 🚀 Getting Started

### 1. Clone & setup

```bash
git clone https://github.com/mbuguakevvz/social-impact-pipeline.git
cd social-impact-pipeline
python -m venv venv
venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
```

### 2. Run ingestion

```bash
python ingestion\fetch_worldbank.py
python ingestion\fetch_unhcr.py
python ingestion\fetch_kenya_health.py
```

### 3. Run transforms & load warehouse

```bash
python transform\normalize_worldbank.py
python transform\normalize_unhcr.py
python transform\normalize_health.py
python transform\merge_unified.py
```

### 4. Start the API

```bash
uvicorn api.main:app --reload
# → http://127.0.0.1:8000/docs
```

### 5. Start the dashboard

```bash
streamlit run dashboard\app.py
# → http://localhost:8501
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Project info |
| GET | `/sources` | Record counts per source |
| GET | `/indicators` | All unique indicators |
| GET | `/data` | Query with filters (source, indicator, year range) |
| GET | `/summary` | Summary statistics per indicator |
| GET | `/trend` | Year-by-year trend for any indicator |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10 |
| Warehouse | DuckDB |
| API | FastAPI + Uvicorn |
| Dashboard | Streamlit + Plotly |
| Data | pandas, requests |
| Version Control | Git + GitHub |

---

## 🌍 Humanitarian Use Cases

- **NGOs** can benchmark their program indicators against national health and poverty data
- **Government agencies** can track displacement trends alongside development indicators
- **Researchers** can run cross-source analysis previously requiring manual data wrangling
- **Donors** can verify impact claims against standardized multi-source data

---

## 👤 Author

**Kevin Mbugua** · [@mbuguakevvz](https://github.com/mbuguakevvz)

Data Engineer | Kenya
