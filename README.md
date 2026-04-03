# Hospital FM Intelligence Hub

**Hospital FM Intelligence Hub** is a data engineering and storytelling portfolio project about hospital facility management.

The goal is not just to show pipelines and charts. The goal is to help someone who does not know hospital FM understand how the hospital runs behind the scenes through estates, maintenance, compliance, and sterile processing.

## Product Vision

This project combines:
- official NHS ERIC estate data
- synthetic but realistic hospital operations data
- a local DuckDB warehouse
- Bruin pipelines
- a multi-page Streamlit app

The current narrative is:
- the estate must be cleaned and powered every day
- equipment must stay available and compliant
- sterile goods must move through AEMP with traceability
- backlog and operational risk accumulate if FM systems fail

Supporting docs:
- [project-vision.md](C:/Users/Melek/hospital-fm-intelligence/docs/project-vision.md)
- [implementation-plan.md](C:/Users/Melek/hospital-fm-intelligence/docs/implementation-plan.md)
- [architecture.md](C:/Users/Melek/hospital-fm-intelligence/docs/architecture.md)
- [kpi-catalog.md](C:/Users/Melek/hospital-fm-intelligence/docs/kpi-catalog.md)
- [source-log.md](C:/Users/Melek/hospital-fm-intelligence/docs/source-log.md)

## What Is Live Right Now

### Real Data Layer
- Official NHS ERIC site data for `2023/24` and `2024/25`
- Trust-level estate metrics built from the site returns
- Backlog, energy, cleaning, area, and trust-level risk views

### Synthetic Operations Layer
- Equipment register
- Maintenance events
- Compliance inspection status
- SAP-like work-order flow states
- AEMP cycle and batch data

### Streamlit Product Pages
- `app.py`: landing page and product entry
- `1_A_Day_in_FM.py`: narrative story page
- `2_Estate_Pressure.py`: trust comparison view
- `3_Equipment_Journey.py`: maintenance and reliability view
- `4_Compliance_Control.py`: inspection and compliance view
- `5_Trust_Drilldown.py`: trust-level operational cockpit
- `6_AEMP_Process.py`: sterile processing view

## First-Time Walkthrough

If you are opening the app for the first time, use this order:

1. Start at `app.py` to understand what the product covers.
2. Open `1_A_Day_in_FM.py` for the narrative view of the hospital day.
3. Open `5_Trust_Drilldown.py` for a single-trust operational cockpit.
4. Explore `3_Equipment_Journey.py` and `4_Compliance_Control.py` for maintenance depth.
5. Open `6_AEMP_Process.py` for the sterile processing domain.

## Architecture

### Data Sources
- NHS ERIC trust and site files in [data/raw/nhs_eric](C:/Users/Melek/hospital-fm-intelligence/data/raw/nhs_eric)
- Synthetic operational CSVs in [data/raw/synthetic](C:/Users/Melek/hospital-fm-intelligence/data/raw/synthetic)

### Pipeline Stack
- `Python` for synthetic generators and utility scripts
- `Bruin` for ingestion, staging, and marts
- `DuckDB` for the local analytical warehouse
- `Streamlit` for the app layer

### Main Flow
1. Download and normalize source files
2. Generate synthetic hospital process data
3. Load all sources into DuckDB with Bruin
4. Build staging views and trust-level marts
5. Render the app from the mart layer

For a fuller system view, see [architecture.md](C:/Users/Melek/hospital-fm-intelligence/docs/architecture.md).
For KPI definitions, see [kpi-catalog.md](C:/Users/Melek/hospital-fm-intelligence/docs/kpi-catalog.md).

## Repository Structure

```text
hospital-fm-intelligence/
|-- dashboard/
|   |-- app.py
|   |-- lib.py
|   `-- pages/
|-- data/
|   `-- raw/
|       |-- nhs_eric/
|       `-- synthetic/
|-- docs/
|-- generators/
|-- pipelines/
|   `-- assets/
|       |-- ingestion/
|       |-- staging/
|       `-- marts/
|-- scripts/
`-- hospital_fm.db
```

## Quick Start

### 1. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Prepare the real and synthetic data

Normalize the official ERIC site CSV encodings:

```powershell
python scripts/normalize_eric_csv_encoding.py
```

Generate synthetic maintenance and AEMP data:

```powershell
python generators/generate_equipment_data.py
python generators/generate_aemp_data.py
```

### 3. Build the DuckDB warehouse

```powershell
bruin run pipelines/
```

### 4. Launch the app

```powershell
streamlit run dashboard/app.py
```

## Current Marts

Examples of core marts already in use:
- `kpi_eric_real_trust_estate_metrics`
- `kpi_equipment_reliability`
- `kpi_equipment_compliance`
- `kpi_work_order_flow`
- `fact_equipment_work_orders`
- `kpi_aemp_process_summary`
- `kpi_aemp_shift_load`
- `kpi_trust_operational_cockpit`

## Current Scope

### Implemented
- Estate pressure from official NHS ERIC site data
- Equipment reliability and maintenance flow
- Compliance control
- Trust operational cockpit
- AEMP synthetic process layer
- Multi-page product navigation

### Not Yet Implemented
- refreshed screenshots from the current multi-page app
- broader HR and finance domain expansion
- procure-to-pay and broader SAP process simulation
- richer media and documentation polish

## Important Notes

- Bed-normalized official energy metrics are not yet the main live metric because the published site CSVs do not directly expose total available beds in the same shape as the site-level estate fields.
- The synthetic layers are intentionally synthetic. They are designed to be operationally believable and aligned to trust scale, not to represent live hospital records.

## Why This Repo Exists

This repo is meant to show both:
- technical data engineering ability
- real hospital FM domain understanding

The project standard is simple:

> Someone should come away understanding how a hospital runs behind the scenes, not just what the charts say.
