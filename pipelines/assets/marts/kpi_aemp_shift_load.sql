/* @bruin
name: kpi_aemp_shift_load
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_aemp_cycles
@bruin */

SELECT
    year,
    trust_code,
    trust_name,
    region,
    shift_name,
    bottleneck_stage,
    COUNT(*) AS cycle_count,
    ROUND(AVG(cycle_duration_minutes), 2) AS avg_cycle_duration_minutes,
    ROUND(SUM(CASE WHEN reprocess_required THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS reprocess_rate_pct
FROM stg_aemp_cycles
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY cycle_count DESC;
