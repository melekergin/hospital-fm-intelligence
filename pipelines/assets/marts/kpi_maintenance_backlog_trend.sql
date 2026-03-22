/* @bruin
name: kpi_maintenance_backlog_trend
type: duckdb.sql
materialization:
  type: view
depends:
  - stg_eric
@bruin */

-- KPI: Maintenance backlog trend 2021->2024
SELECT
    trust_code,
    year,
    maintenance_backlog_cost AS current_backlog_gbp,
    LAG(maintenance_backlog_cost) OVER (PARTITION BY trust_code ORDER BY year) as previous_year_backlog_gbp,
    maintenance_backlog_cost - LAG(maintenance_backlog_cost) OVER (PARTITION BY trust_code ORDER BY year) AS backlog_growth_absolute
FROM stg_eric;
