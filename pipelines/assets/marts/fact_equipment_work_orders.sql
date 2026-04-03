/* @bruin
name: fact_equipment_work_orders
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_equipment_register
  - stg_maintenance_events
@bruin */

SELECT
    e.event_id,
    r.reporting_year AS year,
    e.trust_code,
    r.trust_name,
    r.region,
    r.site_code,
    r.asset_id,
    r.equipment_category,
    r.criticality,
    e.event_type,
    e.priority,
    e.status AS work_order_status,
    e.work_center,
    e.planner_group,
    e.event_reported_ts,
    e.first_response_ts,
    e.work_started_ts,
    e.technically_complete_ts,
    e.closed_ts,
    e.event_start_ts,
    e.downtime_hours,
    e.maintenance_cost_gbp,
    e.response_target_minutes,
    e.response_sla_met,
    ROUND(EXTRACT(EPOCH FROM (e.first_response_ts - e.event_reported_ts)) / 60.0, 2) AS response_minutes,
    ROUND(EXTRACT(EPOCH FROM (COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts)) / 3600.0, 2) AS work_order_age_hours,
    ROUND(EXTRACT(EPOCH FROM (COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts)) / 86400.0, 2) AS work_order_age_days,
    ROUND(EXTRACT(EPOCH FROM (e.closed_ts - e.event_reported_ts)) / 3600.0, 2) AS resolution_hours,
    CASE
        WHEN COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts < INTERVAL '1 day' THEN 'Under 1 day'
        WHEN COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts < INTERVAL '3 day' THEN '1-3 days'
        WHEN COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts < INTERVAL '7 day' THEN '3-7 days'
        WHEN COALESCE(e.closed_ts, e.as_of_ts) - e.event_reported_ts < INTERVAL '14 day' THEN '1-2 weeks'
        ELSE 'Over 2 weeks'
    END AS work_order_age_bucket,
    e.failure_mode,
    r.last_inspection_date,
    r.next_inspection_due_date,
    r.inspection_outcome,
    r.compliance_status
FROM stg_maintenance_events e
JOIN stg_equipment_register r
    ON e.asset_id = r.asset_id;
