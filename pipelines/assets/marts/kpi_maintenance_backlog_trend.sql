/* @bruin
name: kpi_maintenance_backlog_trend
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_eric
@bruin */

-- KPI: Maintenance backlog trend year-on-year (materialized as table — LAG() shouldn't recompute on every query)
SELECT
    trust_code,
    year,
    year_sort,
    maintenance_backlog_cost                                                      AS current_backlog_gbp,
    backlog_cost_per_bed                                                          AS current_backlog_per_bed,

    LAG(maintenance_backlog_cost) OVER (PARTITION BY trust_code ORDER BY year_sort)
                                                                                  AS prev_year_backlog_gbp,

    maintenance_backlog_cost
        - LAG(maintenance_backlog_cost) OVER (PARTITION BY trust_code ORDER BY year_sort)
                                                                                  AS backlog_growth_gbp,

    ROUND(
        (maintenance_backlog_cost
            - LAG(maintenance_backlog_cost) OVER (PARTITION BY trust_code ORDER BY year_sort))
        / NULLIF(LAG(maintenance_backlog_cost) OVER (PARTITION BY trust_code ORDER BY year_sort), 0) * 100,
    1)                                                                            AS backlog_growth_pct

FROM stg_eric
WHERE is_valid_record = TRUE
ORDER BY trust_code, year_sort;

