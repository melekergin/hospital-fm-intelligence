/* @bruin
name: kpi_aemp_process_summary
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_aemp_cycles
  - stg_aemp_batches
@bruin */

WITH batch_rollup AS (
    SELECT
        cycle_id,
        COUNT(*) AS batch_count,
        SUM(instrument_units) AS instrument_units,
        AVG(dispatch_delay_minutes) AS avg_dispatch_delay_minutes
    FROM stg_aemp_batches
    GROUP BY 1
)
SELECT
    c.year,
    c.trust_code,
    c.trust_name,
    c.region,
    COUNT(*) AS cycle_count,
    COUNT(DISTINCT c.autoclave_id) AS autoclave_count,
    ROUND(AVG(c.cycle_duration_minutes), 2) AS avg_cycle_duration_minutes,
    SUM(CASE WHEN c.result = 'Passed' THEN 1 ELSE 0 END) AS passed_cycles,
    SUM(CASE WHEN c.result = 'Failed' THEN 1 ELSE 0 END) AS failed_cycles,
    ROUND(SUM(CASE WHEN c.result = 'Passed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS conformity_rate_pct,
    ROUND(SUM(CASE WHEN c.traceability_complete THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS traceability_rate_pct,
    ROUND(SUM(CASE WHEN c.reprocess_required THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS reprocess_rate_pct,
    SUM(c.load_units) AS load_units,
    SUM(COALESCE(b.batch_count, 0)) AS batch_count,
    SUM(COALESCE(b.instrument_units, 0)) AS instrument_units,
    ROUND(AVG(COALESCE(b.avg_dispatch_delay_minutes, 0)), 2) AS avg_dispatch_delay_minutes
FROM stg_aemp_cycles c
LEFT JOIN batch_rollup b
    ON c.cycle_id = b.cycle_id
GROUP BY 1, 2, 3, 4
ORDER BY cycle_count DESC;
