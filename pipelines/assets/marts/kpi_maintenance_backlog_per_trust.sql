/* @bruin
name: kpi_maintenance_backlog_per_trust
type: duckdb.sql
materialization:
  type: view
depends:
  - stg_eric
@bruin */

-- KPI: Maintenance backlog per trust (£ and %)
WITH totals AS (
    SELECT year, SUM(maintenance_backlog_cost_gbp) as total_backlog
    FROM stg_eric
    WHERE is_valid_record = TRUE
    GROUP BY year
)
SELECT 
    e.year,
    e.year_sort,
    e.trust_code,
    e.trust_name,
    e.region,
    e.maintenance_backlog_cost_gbp AS backlog_gbp,
    CASE 
        WHEN t.total_backlog = 0 THEN 0 
        ELSE (e.maintenance_backlog_cost_gbp / t.total_backlog) * 100 
    END AS backlog_percent
FROM stg_eric e
JOIN totals t ON e.year = t.year
WHERE e.is_valid_record = TRUE;
