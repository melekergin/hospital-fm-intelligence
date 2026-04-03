# Source Log

## NHS ERIC files in repo

Initial real-data sources downloaded on 2026-04-03:

- 2023/24 trust data CSV
- 2023/24 site data CSV
- 2023/24 data definitions workbook
- 2024/25 trust data CSV
- 2024/25 site data CSV

Publication pages:
- [ERIC 2023/24 publication](https://digital.nhs.uk/data-and-information/publications/statistical/estates-returns-information-collection/summary-page-and-dataset-for-eric-2023-24)
- [ERIC 2024/25 publication](https://digital.nhs.uk/data-and-information/publications/statistical/estates-returns-information-collection/summary-page-and-dataset-for-eric-2024-25)

Notes:
- The trust CSVs do not expose all Phase 1 KPI fields directly.
- The site CSVs contain backlog, energy, cleaning, and floor-area fields needed for real-data aggregation.
- The published files use inconsistent encodings across years, so the repo normalizes them to UTF-8 before ingestion.
