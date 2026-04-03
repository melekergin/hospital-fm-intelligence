/* @bruin
name: stg_equipment_register
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_equipment_register
@bruin */

SELECT
    trust_code,
    trust_name,
    region,
    trust_type,
    reporting_year,
    asset_id,
    site_code,
    equipment_category,
    manufacturer,
    criticality,
    CAST(install_year AS INTEGER) AS install_year,
    CAST(expected_service_interval_days AS INTEGER) AS expected_service_interval_days,
    CAST(last_inspection_date AS DATE) AS last_inspection_date,
    CAST(next_inspection_due_date AS DATE) AS next_inspection_due_date,
    inspection_outcome,
    compliance_status,
    CAST(acquisition_value_gbp AS DOUBLE) AS acquisition_value_gbp
FROM raw_equipment_register;
