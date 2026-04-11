/* @bruin
name: kpi_bed_readiness_summary
type: duckdb.sql
materialization:
  type: table
depends:
  - fact_bed_readiness_events
@bruin */

SELECT
    year,
    trust_code,
    trust_name,
    region,
    COUNT(*) AS turnover_event_count,
    ROUND(AVG(turnaround_minutes), 2) AS avg_turnaround_minutes,
    ROUND(MEDIAN(turnaround_minutes), 2) AS median_turnaround_minutes,
    ROUND(QUANTILE_CONT(turnaround_minutes, 0.90), 2) AS p90_turnaround_minutes,
    ROUND(100.0 * AVG(CASE WHEN within_target = 'Yes' THEN 1 ELSE 0 END), 2) AS within_target_pct,
    SUM(CASE WHEN turnaround_minutes > 240 THEN 1 ELSE 0 END) AS events_over_4h,
    SUM(CASE WHEN primary_blocker = 'Cleaning queue' THEN 1 ELSE 0 END) AS blocker_cleaning_queue,
    SUM(CASE WHEN primary_blocker = 'Deep clean / isolation reset' THEN 1 ELSE 0 END) AS blocker_isolation_reset,
    SUM(CASE WHEN primary_blocker = 'Equipment not ready' THEN 1 ELSE 0 END) AS blocker_equipment_not_ready,
    SUM(CASE WHEN primary_blocker = 'Maintenance clearance' THEN 1 ELSE 0 END) AS blocker_maintenance_clearance,
    SUM(CASE WHEN primary_blocker = 'Awaiting porter / room release' THEN 1 ELSE 0 END) AS blocker_porter_release,
    SUM(CASE WHEN primary_blocker = 'Clinical hold / late discharge' THEN 1 ELSE 0 END) AS blocker_clinical_hold
FROM fact_bed_readiness_events
GROUP BY 1, 2, 3, 4
ORDER BY year, avg_turnaround_minutes DESC;
