/* @bruin
name: fact_equipment_compliance_assets
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_equipment_register
@bruin */

WITH base AS (
    SELECT
        reporting_year AS year,
        trust_code,
        trust_name,
        region,
        trust_type,
        site_code,
        asset_id,
        equipment_category,
        manufacturer,
        criticality,
        install_year,
        expected_service_interval_days,
        last_inspection_date,
        next_inspection_due_date,
        inspection_outcome,
        compliance_status,
        acquisition_value_gbp,
        DATE '2025-03-31' - next_inspection_due_date AS days_from_due_date
    FROM stg_equipment_register
)
SELECT
    year,
    trust_code,
    trust_name,
    region,
    trust_type,
    site_code,
    asset_id,
    equipment_category,
    manufacturer,
    criticality,
    install_year,
    expected_service_interval_days,
    last_inspection_date,
    next_inspection_due_date,
    inspection_outcome,
    compliance_status,
    acquisition_value_gbp,
    CAST(days_from_due_date AS INTEGER) AS days_from_due_date,
    CASE
        WHEN compliance_status = 'Action Required' THEN 'Action Required'
        WHEN days_from_due_date >= 90 THEN 'Critical Overdue'
        WHEN days_from_due_date >= 1 THEN 'Overdue'
        WHEN days_from_due_date >= -30 THEN 'Due Soon'
        ELSE 'In Date'
    END AS compliance_risk_bucket,
    CASE
        WHEN compliance_status = 'Action Required' THEN 1
        WHEN days_from_due_date >= 90 THEN 2
        WHEN days_from_due_date >= 1 THEN 3
        WHEN days_from_due_date >= -30 THEN 4
        ELSE 5
    END AS compliance_risk_rank
FROM base;
