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
    CAST(event_reported_ts AS TIMESTAMP) AS event_reported_ts,
    CAST(first_response_ts AS TIMESTAMP) AS first_response_ts,
    CAST(work_started_ts AS TIMESTAMP) AS work_started_ts,
    CAST(technically_complete_ts AS TIMESTAMP) AS technically_complete_ts,
    CAST(closed_ts AS TIMESTAMP) AS closed_ts,
    CAST(downtime_hours AS DOUBLE) AS downtime_hours,
    CAST(maintenance_cost_gbp AS DOUBLE) AS maintenance_cost_gbp,
    CAST(response_target_minutes AS INTEGER) AS response_target_minutes,
    CASE
        WHEN CAST(response_sla_met AS VARCHAR) IN ('true', 'True', 'TRUE', 'Yes') THEN 'Yes'
        ELSE 'No'
    END AS response_sla_met,
    CAST(as_of_ts AS TIMESTAMP) AS as_of_ts,
    status,
    work_center,
    planner_group,
    NULLIF(failure_mode, '') AS failure_mode
FROM raw_maintenance_events;
