/* @bruin
name: stg_eric
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_eric
@bruin */

SELECT
    Trust_Code AS trust_code,
    Year AS year,
    Maintenance_Backlog_Cost AS maintenance_backlog_cost,
    Total_Energy_Cost AS total_energy_cost,
    Available_Beds AS available_beds
FROM raw_eric
WHERE Available_Beds IS NOT NULL 
  AND Available_Beds > 0;
