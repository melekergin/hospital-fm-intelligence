/* @bruin
name: kpi_energy_cost_per_bed
type: duckdb.sql
materialization:
  type: view
depends:
  - stg_eric
@bruin */

-- KPI: Energy cost per bed
SELECT
    year,
    trust_code,
    total_energy_cost,
    available_beds,
    total_energy_cost / NULLIF(available_beds, 0) AS energy_cost_per_bed
FROM stg_eric;
