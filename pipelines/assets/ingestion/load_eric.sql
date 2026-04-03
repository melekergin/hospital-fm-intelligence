/* @bruin
name: raw_eric
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT
    trust_code,
    trust_name,
    region,
    year,
    CAST(maintenance_backlog_cost_gbp AS DOUBLE) AS maintenance_backlog_cost_gbp,
    CAST(total_energy_cost_gbp AS DOUBLE) AS total_energy_cost_gbp,
    CAST(cleaning_cost_gbp AS DOUBLE) AS cleaning_cost_gbp,
    CAST(cleaned_floor_area_m2 AS DOUBLE) AS cleaned_floor_area_m2,
    CAST(available_beds AS INTEGER) AS available_beds
FROM read_csv_auto('data/raw/eric_sample_trusts.csv', header = TRUE);
