/* @bruin
name: kpi_trust_operational_cockpit
type: duckdb.sql
materialization:
  type: table
depends:
  - kpi_eric_real_trust_estate_metrics
  - kpi_equipment_reliability
  - kpi_equipment_compliance
  - kpi_work_order_flow
  - kpi_aemp_process_summary
@bruin */

WITH equipment_rollup AS (
    SELECT
        year,
        trust_code,
        trust_name,
        region,
        SUM(asset_count) AS asset_count,
        SUM(corrective_events) AS corrective_events,
        SUM(planned_events) AS planned_events,
        SUM(downtime_hours) AS downtime_hours,
        SUM(maintenance_cost_gbp) AS maintenance_cost_gbp,
        ROUND(AVG(failure_rate_per_asset), 2) AS avg_failure_rate_per_asset,
        ROUND(AVG(mttr_hours), 2) AS avg_mttr_hours,
        ROUND(AVG(availability_pct), 2) AS avg_availability_pct
    FROM kpi_equipment_reliability
    GROUP BY 1, 2, 3, 4
),
compliance_rollup AS (
    SELECT
        year,
        trust_code,
        trust_name,
        region,
        SUM(asset_count) AS compliance_asset_count,
        SUM(in_date_assets) AS in_date_assets,
        SUM(overdue_assets) AS overdue_assets,
        SUM(action_required_assets) AS action_required_assets,
        ROUND(
            SUM(in_date_assets) * 100.0 / NULLIF(SUM(asset_count), 0),
            2
        ) AS compliance_rate_pct
    FROM kpi_equipment_compliance
    GROUP BY 1, 2, 3, 4
),
work_order_rollup AS (
    SELECT
        year,
        trust_code,
        trust_name,
        region,
        SUM(order_count) AS total_work_orders,
        SUM(CASE WHEN event_type = 'Corrective Maintenance' THEN order_count ELSE 0 END) AS corrective_work_orders,
        SUM(CASE WHEN event_type = 'Planned Maintenance' THEN order_count ELSE 0 END) AS planned_work_orders,
        SUM(CASE WHEN work_order_status = 'Notification' THEN order_count ELSE 0 END) AS status_notification,
        SUM(CASE WHEN work_order_status = 'Planning' THEN order_count ELSE 0 END) AS status_planning,
        SUM(CASE WHEN work_order_status = 'Approved' THEN order_count ELSE 0 END) AS status_approved,
        SUM(CASE WHEN work_order_status = 'In Progress' THEN order_count ELSE 0 END) AS status_in_progress,
        SUM(CASE WHEN work_order_status = 'Technically Complete' THEN order_count ELSE 0 END) AS status_technically_complete,
        SUM(CASE WHEN work_order_status = 'Closed' THEN order_count ELSE 0 END) AS status_closed,
        ROUND(AVG(avg_order_cost_gbp), 2) AS avg_work_order_cost_gbp
    FROM kpi_work_order_flow
    GROUP BY 1, 2, 3, 4
),
aemp_rollup AS (
    SELECT
        year,
        trust_code,
        trust_name,
        region,
        cycle_count AS aemp_cycle_count,
        autoclave_count,
        avg_cycle_duration_minutes,
        conformity_rate_pct,
        traceability_rate_pct,
        reprocess_rate_pct,
        batch_count AS aemp_batch_count,
        instrument_units AS aemp_instrument_units,
        avg_dispatch_delay_minutes
    FROM kpi_aemp_process_summary
)
SELECT
    e.year,
    e.year_sort,
    e.trust_code,
    e.trust_name,
    e.region,
    e.trust_type,
    e.site_count,
    e.gross_internal_floor_area_m2,
    e.inpatient_room_proxy,
    e.total_backlog_gbp,
    e.total_energy_cost_gbp,
    e.total_cleaning_cost_gbp,
    e.backlog_cost_per_m2,
    e.energy_cost_per_m2,
    e.cleaning_cost_per_m2,
    e.backlog_per_inpatient_room_proxy,
    e.backlog_risk_band_by_m2,
    COALESCE(r.asset_count, 0) AS asset_count,
    COALESCE(r.corrective_events, 0) AS corrective_events,
    COALESCE(r.planned_events, 0) AS planned_events,
    COALESCE(r.downtime_hours, 0) AS downtime_hours,
    COALESCE(r.maintenance_cost_gbp, 0) AS maintenance_cost_gbp,
    r.avg_failure_rate_per_asset,
    r.avg_mttr_hours,
    r.avg_availability_pct,
    COALESCE(c.in_date_assets, 0) AS in_date_assets,
    COALESCE(c.overdue_assets, 0) AS overdue_assets,
    COALESCE(c.action_required_assets, 0) AS action_required_assets,
    c.compliance_rate_pct,
    COALESCE(w.total_work_orders, 0) AS total_work_orders,
    COALESCE(w.corrective_work_orders, 0) AS corrective_work_orders,
    COALESCE(w.planned_work_orders, 0) AS planned_work_orders,
    COALESCE(w.status_notification, 0) AS status_notification,
    COALESCE(w.status_planning, 0) AS status_planning,
    COALESCE(w.status_approved, 0) AS status_approved,
    COALESCE(w.status_in_progress, 0) AS status_in_progress,
    COALESCE(w.status_technically_complete, 0) AS status_technically_complete,
    COALESCE(w.status_closed, 0) AS status_closed,
    w.avg_work_order_cost_gbp,
    COALESCE(a.aemp_cycle_count, 0) AS aemp_cycle_count,
    COALESCE(a.autoclave_count, 0) AS autoclave_count,
    a.avg_cycle_duration_minutes,
    a.conformity_rate_pct,
    a.traceability_rate_pct,
    a.reprocess_rate_pct,
    COALESCE(a.aemp_batch_count, 0) AS aemp_batch_count,
    COALESCE(a.aemp_instrument_units, 0) AS aemp_instrument_units,
    a.avg_dispatch_delay_minutes
FROM kpi_eric_real_trust_estate_metrics e
LEFT JOIN equipment_rollup r
    ON e.year = r.year
   AND e.trust_code = r.trust_code
LEFT JOIN compliance_rollup c
    ON e.year = c.year
   AND e.trust_code = c.trust_code
LEFT JOIN work_order_rollup w
    ON e.year = w.year
   AND e.trust_code = w.trust_code
LEFT JOIN aemp_rollup a
    ON e.year = a.year
   AND e.trust_code = a.trust_code
ORDER BY e.year_sort DESC, e.total_backlog_gbp DESC;
