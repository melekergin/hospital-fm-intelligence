/* @bruin
name: stg_aemp_batches
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_aemp_batches
@bruin */

SELECT
    batch_id,
    cycle_id,
    trust_code,
    batch_type,
    CAST(instrument_units AS INTEGER) AS instrument_units,
    priority,
    CAST(dispatch_delay_minutes AS DOUBLE) AS dispatch_delay_minutes,
    destination
FROM raw_aemp_batches;
