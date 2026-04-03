/* @bruin
name: stg_maintenance_events
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_maintenance_events
@bruin */

SELECT
    event_id,
    asset_id,
    trust_code,
    event_type,
    priority,
    CAST(event_start_ts AS TIMESTAMP) AS event_start_ts,
    CAST(downtime_hours AS DOUBLE) AS downtime_hours,
    CAST(maintenance_cost_gbp AS DOUBLE) AS maintenance_cost_gbp,
    status,
    work_center,
    planner_group,
    NULLIF(failure_mode, '') AS failure_mode
FROM raw_maintenance_events;
