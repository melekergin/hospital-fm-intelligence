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
    e.event_start_ts,
    e.downtime_hours,
    e.maintenance_cost_gbp,
    e.failure_mode,
    r.last_inspection_date,
    r.next_inspection_due_date,
    r.inspection_outcome,
    r.compliance_status
FROM stg_maintenance_events e
JOIN stg_equipment_register r
    ON e.asset_id = r.asset_id;
