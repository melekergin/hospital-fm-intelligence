# Architecture

## Purpose

The project architecture is designed to support two things at the same time:

1. a reproducible local data engineering workflow
2. a storytelling product about hospital facility management

It combines real NHS estate data with synthetic operational data so the app can explain both high-level estate pressure and day-to-day hospital support processes.

## High-Level Flow

```mermaid
flowchart TD
    A["Official NHS ERIC Files<br/>2023/24 and 2024/25"] --> B["Normalization Script<br/>scripts/normalize_eric_csv_encoding.py"]
    C["Synthetic Equipment Generator<br/>generators/generate_equipment_data.py"] --> D["Synthetic CSVs"]
    E["Synthetic AEMP Generator<br/>generators/generate_aemp_data.py"] --> D
    B --> F["Bruin Ingestion Assets"]
    D --> F
    F --> G["DuckDB Raw Tables"]
    G --> H["Bruin Staging Views"]
    H --> I["Bruin Marts"]
    I --> J["Streamlit Landing Page"]
    I --> K["Story and Domain Pages"]
    I --> L["Trust Drilldown"]
```

## Source Layers

### 1. Official ERIC Data

Location:
- [data/raw/nhs_eric](C:/Users/Melek/hospital-fm-intelligence/data/raw/nhs_eric)

Purpose:
- provide real trust and site-level estate context
- anchor the project in real NHS benchmark data

Current live use:
- maintenance backlog
- energy cost
- cleaning cost
- gross internal floor area
- trust-level estate pressure

### 2. Synthetic Equipment Data

Location:
- [generators/generate_equipment_data.py](C:/Users/Melek/hospital-fm-intelligence/generators/generate_equipment_data.py)
- [data/raw/synthetic](C:/Users/Melek/hospital-fm-intelligence/data/raw/synthetic)

Purpose:
- simulate asset register and maintenance operations
- create equipment lifecycle, reliability, compliance, and work-order flow

Current live use:
- equipment register
- maintenance events
- inspection status
- work-order states

### 3. Synthetic AEMP Data

Location:
- [generators/generate_aemp_data.py](C:/Users/Melek/hospital-fm-intelligence/generators/generate_aemp_data.py)
- [data/raw/synthetic](C:/Users/Melek/hospital-fm-intelligence/data/raw/synthetic)

Purpose:
- simulate sterile processing cycles and dispatch flow
- create process KPIs for conformity, traceability, and reprocessing

Current live use:
- cycle runs
- batch records
- shift profile
- bottleneck stage summary

## Warehouse Layers

### Ingestion

Location:
- [pipelines/assets/ingestion](C:/Users/Melek/hospital-fm-intelligence/pipelines/assets/ingestion)

Responsibility:
- load source CSV files into DuckDB raw tables

Examples:
- ERIC site loads
- equipment register load
- maintenance events load
- AEMP cycle and batch loads

### Staging

Location:
- [pipelines/assets/staging](C:/Users/Melek/hospital-fm-intelligence/pipelines/assets/staging)

Responsibility:
- standardize types
- normalize source columns
- create reusable clean views for marts

Examples:
- ERIC site core staging
- equipment register staging
- maintenance event staging
- AEMP cycle and batch staging

### Marts

Location:
- [pipelines/assets/marts](C:/Users/Melek/hospital-fm-intelligence/pipelines/assets/marts)

Responsibility:
- produce trust-level and process-level KPIs used directly by the app

Core mart groups:

#### Estate
- `kpi_eric_real_trust_estate_metrics`
- `kpi_trust_summary`
- `kpi_backlog_risk_band`

#### Equipment and Maintenance
- `kpi_equipment_reliability`
- `kpi_work_order_flow`
- `fact_equipment_work_orders`

#### Compliance
- `kpi_equipment_compliance`
- `fact_equipment_compliance_assets`

#### AEMP
- `kpi_aemp_process_summary`
- `kpi_aemp_shift_load`

#### Integrated Trust View
- `kpi_trust_operational_cockpit`

## Application Layer

Location:
- [dashboard](C:/Users/Melek/hospital-fm-intelligence/dashboard)

### Shared Logic
- [lib.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/lib.py)

Responsibility:
- shared styles
- DuckDB connection
- reusable query helpers
- common sidebar filtering

### Main Entry
- [app.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/app.py)

Responsibility:
- landing page
- product framing
- domain entry points
- high-level live signals

### Domain Pages
- [1_A_Day_in_FM.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/pages/1_A_Day_in_FM.py)
- [2_Estate_Pressure.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/pages/2_Estate_Pressure.py)
- [3_Equipment_Journey.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/pages/3_Equipment_Journey.py)
- [4_Compliance_Control.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/pages/4_Compliance_Control.py)
- [5_Trust_Drilldown.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/pages/5_Trust_Drilldown.py)
- [6_AEMP_Process.py](C:/Users/Melek/hospital-fm-intelligence/dashboard/pages/6_AEMP_Process.py)

## Design Principles

- Keep the official ERIC layer real and traceable
- Use synthetic data only where public operational datasets do not exist
- Push business logic into marts instead of burying it in Streamlit pages
- Build each operational domain as a coherent slice
- Use the trust cockpit to unify the domains into one hospital story

## Current Limitations

- The old screenshots in `docs/images` do not yet reflect the current multi-page product
- Bed-normalized official metrics are still limited by the shape of the published ERIC site data
- Navigation is improved, but the app could still benefit from custom page-level linking and richer visual onboarding

## Next Architecture Step

The next structural improvement should be a dedicated documentation and media pass:
- refresh screenshots from the current app
- add a simple KPI catalog
- tighten the connection between the landing page and domain pages
