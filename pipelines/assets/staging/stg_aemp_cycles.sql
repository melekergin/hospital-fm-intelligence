/* @bruin
name: stg_aemp_cycles
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_aemp_cycles
@bruin */

SELECT
    cycle_id,
    trust_code,
    trust_name,
    region,
    trust_type,
    reporting_year AS year,
    shift_name,
    autoclave_id,
    program_name,
    CAST(cycle_start_ts AS TIMESTAMP) AS cycle_start_ts,
    CAST(cycle_end_ts AS TIMESTAMP) AS cycle_end_ts,
    CAST(cycle_duration_minutes AS DOUBLE) AS cycle_duration_minutes,
    result,
    CAST(traceability_complete AS BOOLEAN) AS traceability_complete,
    CAST(load_units AS INTEGER) AS load_units,
    CAST(reprocess_required AS BOOLEAN) AS reprocess_required,
    bottleneck_stage
FROM raw_aemp_cycles;
