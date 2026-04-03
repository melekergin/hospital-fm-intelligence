/* @bruin
name: kpi_equipment_reliability
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_equipment_register
  - stg_maintenance_events
@bruin */

WITH event_rollup AS (
    SELECT
        asset_id,
        SUM(CASE WHEN event_type = 'Corrective Maintenance' THEN 1 ELSE 0 END) AS corrective_events,
        SUM(CASE WHEN event_type = 'Planned Maintenance' THEN 1 ELSE 0 END) AS planned_events,
        SUM(CASE WHEN event_type = 'Corrective Maintenance' THEN downtime_hours ELSE 0 END) AS corrective_downtime_hours,
        SUM(maintenance_cost_gbp) AS maintenance_cost_gbp
    FROM stg_maintenance_events
    GROUP BY 1
)
SELECT
    r.reporting_year AS year,
    r.trust_code,
    r.trust_name,
    r.region,
    r.equipment_category,
    COUNT(*) AS asset_count,
    SUM(COALESCE(e.corrective_events, 0)) AS corrective_events,
    SUM(COALESCE(e.planned_events, 0)) AS planned_events,
    ROUND(SUM(COALESCE(e.corrective_downtime_hours, 0)), 2) AS downtime_hours,
    ROUND(SUM(COALESCE(e.maintenance_cost_gbp, 0)), 2) AS maintenance_cost_gbp,
    ROUND(SUM(COALESCE(e.corrective_events, 0)) * 1.0 / NULLIF(COUNT(*), 0), 2) AS failure_rate_per_asset,
    ROUND(SUM(COALESCE(e.corrective_downtime_hours, 0)) / NULLIF(SUM(COALESCE(e.corrective_events, 0)), 0), 2) AS mttr_hours,
    ROUND((8760 * COUNT(*) - SUM(COALESCE(e.corrective_downtime_hours, 0))) / NULLIF(8760 * COUNT(*), 0) * 100, 2) AS availability_pct
FROM stg_equipment_register r
LEFT JOIN event_rollup e
    ON r.asset_id = e.asset_id
GROUP BY 1, 2, 3, 4, 5
ORDER BY maintenance_cost_gbp DESC;
