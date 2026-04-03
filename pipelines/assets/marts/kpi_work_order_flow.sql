/* @bruin
name: kpi_work_order_flow
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_equipment_register
  - stg_maintenance_events
@bruin */

SELECT
    r.reporting_year AS year,
    r.trust_code,
    r.trust_name,
    r.region,
    r.equipment_category,
    e.event_type,
    e.status AS work_order_status,
    e.work_center,
    e.planner_group,
    COUNT(*) AS order_count,
    ROUND(AVG(e.downtime_hours), 2) AS avg_downtime_hours,
    ROUND(AVG(e.maintenance_cost_gbp), 2) AS avg_order_cost_gbp,
    ROUND(SUM(e.maintenance_cost_gbp), 2) AS total_order_cost_gbp
FROM stg_maintenance_events e
JOIN stg_equipment_register r
    ON e.asset_id = r.asset_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
ORDER BY total_order_cost_gbp DESC;
