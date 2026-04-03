/* @bruin
name: kpi_work_order_aging
type: duckdb.sql
materialization:
  type: table
depends:
  - fact_equipment_work_orders
@bruin */

SELECT
    year,
    trust_code,
    trust_name,
    region,
    equipment_category,
    event_type,
    work_order_status,
    work_order_age_bucket,
    COUNT(*) AS order_count,
    ROUND(AVG(response_minutes), 2) AS avg_response_minutes,
    ROUND(AVG(work_order_age_days), 2) AS avg_work_order_age_days,
    ROUND(AVG(resolution_hours), 2) AS avg_resolution_hours,
    ROUND(AVG(maintenance_cost_gbp), 2) AS avg_order_cost_gbp
FROM fact_equipment_work_orders
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
ORDER BY year, trust_code, equipment_category, order_count DESC;
