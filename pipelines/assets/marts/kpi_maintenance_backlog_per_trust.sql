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
    SELECT year, SUM(maintenance_backlog_cost) as total_backlog
    FROM stg_eric
    GROUP BY year
)
SELECT 
    e.year,
    e.trust_code,
    e.maintenance_backlog_cost AS backlog_gbp,
    CASE 
        WHEN t.total_backlog = 0 THEN 0 
        ELSE (e.maintenance_backlog_cost / t.total_backlog) * 100 
    END AS backlog_percent
FROM stg_eric e
JOIN totals t ON e.year = t.year;
