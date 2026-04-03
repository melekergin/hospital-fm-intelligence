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
    ROUND(SUM(e.maintenance_cost_gbp), 2) AS total_order_cost_gbp,
    ROUND(AVG(EXTRACT(EPOCH FROM (e.first_response_ts - e.event_reported_ts)) / 60.0), 2) AS avg_response_minutes,
    ROUND(AVG(EXTRACT(EPOCH FROM (COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts)) / 86400.0), 2) AS avg_work_order_age_days,
    ROUND(
        100.0 * AVG(
            CASE WHEN e.response_sla_met = 'Yes' THEN 1 ELSE 0 END
        ),
        2
    ) AS response_sla_met_pct
FROM stg_maintenance_events e
JOIN stg_equipment_register r
    ON e.asset_id = r.asset_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
ORDER BY total_order_cost_gbp DESC;
