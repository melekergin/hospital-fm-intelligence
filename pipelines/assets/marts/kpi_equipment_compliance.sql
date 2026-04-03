/* @bruin
name: kpi_equipment_compliance
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_equipment_register
@bruin */

SELECT
    reporting_year AS year,
    trust_code,
    trust_name,
    region,
    equipment_category,
    COUNT(*) AS asset_count,
    SUM(CASE WHEN compliance_status = 'In Date' THEN 1 ELSE 0 END) AS in_date_assets,
    SUM(CASE WHEN compliance_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_assets,
    SUM(CASE WHEN compliance_status = 'Action Required' THEN 1 ELSE 0 END) AS action_required_assets,
    ROUND(SUM(CASE WHEN compliance_status = 'In Date' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS compliance_rate_pct,
    MIN(next_inspection_due_date) AS next_due_date_min,
    MAX(next_inspection_due_date) AS next_due_date_max
FROM stg_equipment_register
GROUP BY 1, 2, 3, 4, 5
ORDER BY overdue_assets DESC, action_required_assets DESC;
