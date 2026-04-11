/* @bruin
name: fact_bed_readiness_events
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_bed_turnover_events
@bruin */

SELECT
    year,
    trust_code,
    trust_name,
    region,
    site_code,
    ward_type,
    bed_id,
    event_id,
    discharge_ts,
    cleaning_start_ts,
    cleaning_complete_ts,
    maintenance_clear_ts,
    equipment_ready_ts,
    isolation_clear_ts,
    bed_ready_ts,
    turnaround_target_minutes,
    turnaround_minutes,
    turnaround_bucket,
    within_target,
    primary_blocker,
    queue_delay_minutes,
    cleaning_minutes,
    porter_delay_minutes,
    equipment_delay_minutes,
    maintenance_delay_minutes,
    isolation_delay_minutes,
    clinical_hold_minutes
FROM stg_bed_turnover_events;
