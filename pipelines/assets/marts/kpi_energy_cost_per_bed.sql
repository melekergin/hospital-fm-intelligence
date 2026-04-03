/* @bruin
name: kpi_energy_cost_per_bed
type: duckdb.sql
materialization:
  type: view
depends:
  - stg_eric
@bruin */

-- KPI: Energy cost per bed (uses pre-computed field from staging)
SELECT
    year,
    year_sort,
    trust_code,
    trust_name,
    region,
    total_energy_cost_gbp,
    available_beds,
    energy_cost_per_bed
FROM stg_eric
WHERE is_valid_record = TRUE
ORDER BY trust_code, year_sort;

