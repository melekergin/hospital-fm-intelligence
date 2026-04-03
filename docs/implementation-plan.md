# Hospital FM Intelligence Hub

## Implementation Plan

This document keeps the full original project scope but breaks it into a build order that can be executed without losing momentum.

The rule is:

> Do not reduce the vision. Sequence it.

---

## Delivery Strategy

The project will be built as a set of thin vertical slices:
- real data ingestion first
- then first KPIs
- then first story page
- then synthetic process depth
- then full multi-domain expansion

Every phase must leave the repo in a runnable state.

---

## Phase 1: Real Data Foundation

### Objective
Create a working local data platform around NHS ERIC data.

### Scope
- set up reproducible repo structure
- prepare local Python environment
- configure Bruin and DuckDB
- download and store the first NHS ERIC source files
- ingest raw files into DuckDB
- build first staging models
- create first marts for a small set of trust-level KPIs

### Deliverables
- `data/raw/` contains selected NHS ERIC source files
- DuckDB database created locally
- first Bruin ingestion pipeline runs end to end
- first cleaned staging tables exist
- first KPI mart exists

### Initial KPI Set
- maintenance backlog
- energy cost per bed
- cleaning cost per square metre

### Exit Criteria
- pipeline runs locally without manual data edits
- output tables can be queried
- KPI values are plausible and documented

---

## Phase 2: First Storytelling Release

### Objective
Turn the technical pipeline into a product someone can understand.

### Scope
- rebuild the Streamlit app structure
- create a home page with project framing
- create the first “day in the life” story page
- connect charts to operational explanations
- allow first Trust selection or filtering

### Deliverables
- working Streamlit app shell
- home page
- first story page
- first KPI page

### Exit Criteria
- a non-expert can explain what hospital FM does after using the app for a few minutes
- the app clearly ties metrics to real hospital operations

---

## Phase 3: Equipment and Maintenance Domain

### Objective
Add synthetic medical equipment and maintenance process depth.

### Scope
- create equipment register generator
- create failure event generator
- create maintenance order generator
- simulate DGUV and related compliance tracking
- build lifecycle and reliability marts
- create equipment journey dashboard page

### Deliverables
- synthetic equipment datasets
- maintenance and reliability KPIs
- equipment lifecycle visualisation
- SAP-like process framing for maintenance flow

### Exit Criteria
- the equipment journey is operationally believable
- synthetic events line up with the hospital FM narrative

---

## Phase 4: AEMP / ZSVA Domain

### Objective
Add sterile processing as a major FM domain with process storytelling.

### Scope
- generate sterilisation cycle data
- generate batches and traceability records
- simulate shift operations and throughput
- model quality and utilisation KPIs
- create AEMP process explorer page

### Deliverables
- synthetic AEMP datasets
- cycle and quality marts
- visual process explorer
- traceability and utilisation metrics

### Exit Criteria
- the user can understand how sterile processing supports clinical operations
- AEMP data feels realistic and consistent

---

## Phase 5: Multi-Domain Expansion

### Objective
Extend the project beyond the first operational slices into the full FM landscape.

### Scope
- add more NHS ERIC years until the full intended period is covered
- expand domain marts for finance, infrastructure, cleaning, and HR-related themes
- deepen benchmarking logic across Trusts and years
- add process explanations for procure-to-pay and related flows

### Deliverables
- broader KPI coverage
- cross-year benchmarks
- additional process explanations
- richer filtering and ranking

### Exit Criteria
- the dashboard begins to reflect the full original seven-domain concept

---

## Phase 6: Final Product Polish

### Objective
Make the repo presentation-ready for portfolio use.

### Scope
- improve README
- add KPI catalog
- add architecture documentation
- add screenshots and narrative explanation
- refine visual language and storytelling consistency

### Deliverables
- polished repo docs
- portfolio-friendly README
- screenshots and support documentation
- cleaner UX and copy

### Exit Criteria
- the project is strong enough for public portfolio sharing and discussion in interviews

---

## Technical Workstreams

These workstreams cut across multiple phases:

### Data Engineering
- source ingestion
- schema cleanup
- transformations
- marts
- checks and validation

### Synthetic Data Design
- realistic volume assumptions
- entity relationships
- event timing
- consistency rules

### Product Storytelling
- user journey
- page structure
- explanatory text
- process flow visuals

### Domain Authenticity
- KPI definitions
- FM process realism
- SAP framing
- operational interpretation

---

## Non-Negotiable Build Rules

- Keep the full original scope as the product target
- Build one working slice at a time
- Never add synthetic complexity before the base data model is usable
- Validate each phase before expanding
- Keep the repo runnable throughout
- Tie every chart to an operational explanation

---

## Immediate Execution Order

This is the next implementation sequence:

1. inspect the current repo structure and gaps
2. prepare local environment and dependencies
3. download the first NHS ERIC data files
4. create the first Bruin raw ingestion pipeline
5. create first staging transformations
6. create first trust KPI mart
7. wire the first Streamlit page to real outputs

That is the first serious milestone.

---

## Definition of Success

The project succeeds if it does both of these well:

1. demonstrates solid data engineering practice
2. teaches hospital FM in a memorable, domain-authentic way

This document is the execution companion to the master vision in [project-vision.md](/C:/Users/Melek/hospital-fm-intelligence/docs/project-vision.md).
