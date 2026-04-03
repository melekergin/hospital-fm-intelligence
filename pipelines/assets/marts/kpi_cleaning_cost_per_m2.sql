/* @bruin
name: kpi_cleaning_cost_per_m2
type: duckdb.sql
materialization:
  type: view
depends:
  - stg_eric
@bruin */

SELECT
    year,
    year_sort,
    trust_code,
    trust_name,
    region,
    cleaning_cost_gbp,
    cleaned_floor_area_m2,
    cleaning_cost_per_m2
FROM stg_eric
WHERE is_valid_record = TRUE
ORDER BY trust_code, year_sort;
