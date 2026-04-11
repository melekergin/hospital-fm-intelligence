# Hospital FM Intelligence Hub

## Master Vision

### Working Title
**Hospital FM Intelligence Hub**  
*A Day in the Life of NHS Facility Management*

---


## Core Idea

The goal:

> Someone who knows nothing about hospital facility management should understand how it works after 15 minutes with this project.

This is not just a data pipeline project. It is an interactive learning experience that explains the hidden operational world behind a hospital.

It should combine:
- real NHS benchmark data
- synthetic but realistic operational process data
- hospital FM domain knowledge
- storytelling
- interactive process exploration

---

## Narrative Concept

### A Day in the Life of Hospital FM

The project should tell the story of a hospital day through facility management events:

- 6:30 AM: cleaning teams start work
- 8:00 AM: technicians inspect and maintain critical equipment
- 9:15 AM: a CT scanner fails and triggers a maintenance process
- 11:00 AM: AEMP delivers sterile sets to the operating room
- 2:00 PM: backlog and risk are reviewed
- 5:00 PM: the day closes with cost, compliance, and performance outcomes

Each moment should connect three layers:
- a real NHS ERIC KPI or benchmark
- an operational process in hospital FM
- a synthetic SAP-like transaction or workflow

---

## What Makes This Project Unique

Few portfolio projects combine all of the following in one coherent product:

- real NHS ERIC data across multiple years
- synthetic SAP-like equipment and maintenance data
- synthetic AEMP sterilisation process data
- real hospital FM domain framing
- a storytelling approach instead of a generic dashboard
- interactive process flows that explain how hospital support operations work

The project should feel educational, visual, and domain-authentic rather than just analytical.

---

## Zoomcamp Alignment

The project should satisfy the main Data Engineering Zoomcamp requirements:

- **Dataset:** NHS ERIC 2018/19 through 2024/25
- **Data Lake:** DuckDB raw layer
- **Warehouse / Mart Layer:** DuckDB transformed marts
- **Transformations:** Bruin pipelines plus dbt models
- **Dashboard:** Streamlit

---

## Data Sources

### 1. NHS ERIC Data
Public NHS estates and facilities data covering multiple years and NHS Trusts.

Target coverage:
- Years: 2018/19 through 2024/25
- Entities: 200+ Trusts
- Themes:
  - maintenance backlog
  - energy costs
  - cleaning costs
  - estates costs
  - waste
  - catering
  - carbon and infrastructure indicators where available

Important story angle:
- the COVID-era shift in cleaning and operational costs should be visible in the data

### 2. Synthetic Equipment Data
Python-generated hospital equipment and maintenance data.

Target entities:
- CT scanners
- MRI systems
- ventilators
- lifts
- ventilation systems
- IT equipment

Target facts:
- equipment register
- maintenance orders
- failure events
- repair durations
- repair costs
- DGUV inspection records
- status, priority, and lifecycle history

### 3. Synthetic AEMP Data
Python-generated sterile processing data.

Target characteristics:
- realistic large-hospital cycle volume
- batch-level traceability
- day and shift structure
- capacity, delay, and quality metrics

This data is necessary because public AEMP datasets are not realistically available.

---

## The Seven FM Domains

The project should ultimately cover these seven domains:

1. **Medical Technology**  
   equipment, maintenance, reliability, DGUV, STK/MTK

2. **Building Management**  
   cleaning, infrastructure, floor space, service delivery

3. **AEMP / ZSVA**  
   sterilisation cycles, traceability, throughput, utilisation

4. **People / HR**  
   staffing, absenteeism, turnover, operational workforce capacity

5. **Finance / Cost**  
   cost per area, budget impact, benchmark comparisons

6. **Infrastructure / Energy**  
   energy use, maintenance backlog, FCI-like risk framing

7. **Clinical Support Services**  
   how FM supports patient care and clinical throughput

---

## Technical Stack

The architecture should be:

`NHS ERIC CSVs + synthetic FM generators -> Bruin -> DuckDB -> dbt -> Streamlit -> GitHub portfolio repo`

Main tools:
- `Python`
- `Bruin`
- `DuckDB`
- `dbt-duckdb`
- `Streamlit`
- `GitHub`

---

## Dashboard Structure

The Streamlit app should evolve into a multi-page experience:

### Home / Story Entry
- introduce the concept of hospital FM
- explain why this layer of the hospital matters
- allow the user to choose a Trust or story path

### Equipment Journey
- choose a device type
- show lifecycle from purchase to maintenance to failure to repair to replacement
- connect each step to NHS benchmarks and SAP-like transactions
- expose compliance and operational reliability status

### AEMP Process Explorer
- step through the sterilisation process visually
- show dirty, clean, and sterile zones
- include capacity, cycle time, quality, and traceability metrics

### KPI Dashboard
- backlog trends
- energy cost per bed
- cleaning cost per square metre
- cross-year comparisons
- COVID effect visibility

### Process Flows
- Plant Maintenance
- Procure-to-Pay
- AEMP
- role ownership, duration, cost, and transaction steps

### Benchmarking
- compare Trusts, years, and trust sizes
- simulate “if CFM Charite were an NHS Trust”
- allow ranking by chosen KPI criteria

---

## Core KPIs

### Equipment Reliability
- MTBF
- MTTR
- availability percentage
- failure rate by device type

### Compliance
- DGUV inspection rate
- STK/MTK conformity rate
- overdue inspections

### Cost
- maintenance cost as percentage of acquisition value
- replace-versus-repair score
- cost per operating hour
- maintenance backlog by Trust
- energy cost per bed
- cleaning cost per square metre

### AEMP Quality
- cycle conformity rate
- batch traceability rate
- reprocessing rate
- autoclave utilisation

### NHS ERIC Benchmarks
- backlog trend over time
- risk split where available
- carbon indicators
- COVID cleaning effect

---

## Repository Direction

The repo should support:
- raw data ingestion
- synthetic data generation
- transformation layers
- KPI documentation
- a multi-page Streamlit application
- visual process components

The intended structure includes:
- `data/`
- `generators/`
- `pipelines/`
- `dbt/`
- `dashboard/`
- `docs/`

---

## Product Standard

The project should not look like a generic analytics demo.

It should make the viewer feel:

> I now understand how a hospital runs behind the scenes, and this builder clearly understands both the data and the domain.

That is the standard to build against.

---

## Guiding Rules

- Keep the original ambition intact
- Make the technical implementation reproducible
- Use storytelling as a product feature, not a design extra
- Make every KPI meaningful in operational terms
- Ensure synthetic data supports the real benchmark story instead of distracting from it
- Use visual explanation to teach, not just to impress

---

## Current Build Goal

The repo needs to be rebuilt around this vision.

That means:
- rebuilding the data foundation
- restoring the storytelling structure
- adding synthetic FM layers in a controlled way
- growing from a working core into the full original concept

This document is the master vision and should remain broad, ambitious, and stable.
