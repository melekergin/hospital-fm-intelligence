/* @bruin
name: stg_bed_turnover_events
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_bed_turnover_events
@bruin */

SELECT
    event_id,
    reporting_year AS year,
    trust_code,
    trust_name,
    region,
    site_code,
    ward_type,
    bed_id,
    CAST(discharge_ts AS TIMESTAMP) AS discharge_ts,
    CAST(cleaning_start_ts AS TIMESTAMP) AS cleaning_start_ts,
    CAST(cleaning_complete_ts AS TIMESTAMP) AS cleaning_complete_ts,
    CAST(maintenance_clear_ts AS TIMESTAMP) AS maintenance_clear_ts,
    CAST(equipment_ready_ts AS TIMESTAMP) AS equipment_ready_ts,
    CAST(isolation_clear_ts AS TIMESTAMP) AS isolation_clear_ts,
    CAST(bed_ready_ts AS TIMESTAMP) AS bed_ready_ts,
    CAST(turnaround_target_minutes AS INTEGER) AS turnaround_target_minutes,
    CAST(turnaround_minutes AS INTEGER) AS turnaround_minutes,
    turnaround_bucket,
    within_target,
    primary_blocker,
    CAST(queue_delay_minutes AS INTEGER) AS queue_delay_minutes,
    CAST(cleaning_minutes AS INTEGER) AS cleaning_minutes,
    CAST(porter_delay_minutes AS INTEGER) AS porter_delay_minutes,
    CAST(equipment_delay_minutes AS INTEGER) AS equipment_delay_minutes,
    CAST(maintenance_delay_minutes AS INTEGER) AS maintenance_delay_minutes,
    CAST(isolation_delay_minutes AS INTEGER) AS isolation_delay_minutes,
    CAST(clinical_hold_minutes AS INTEGER) AS clinical_hold_minutes
FROM raw_bed_turnover_events;
