/* @bruin
name: kpi_backlog_risk_band
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_eric
@bruin */

-- KPI: Maintenance backlog risk banding per trust per year.
-- Mirrors the NHS ERIC risk classification approach:
--   HIGH        : backlog cost per bed >= £5,000
--   SIGNIFICANT : backlog cost per bed >= £2,500
--   MODERATE    : backlog cost per bed >= £1,000
--   LOW         : backlog cost per bed <  £1,000
SELECT
    trust_code,
    trust_name,
    region,
    year,
    year_sort,
    maintenance_backlog_cost_gbp                AS backlog_gbp,
    available_beds,
    backlog_cost_per_bed,
    UPPER(backlog_risk_band)                    AS risk_band,

    -- Numeric rank for easy sorting/filtering in dashboards (1=worst)
    CASE
        WHEN backlog_cost_per_bed >= 5000 THEN 1
        WHEN backlog_cost_per_bed >= 2500 THEN 2
        WHEN backlog_cost_per_bed >= 1000 THEN 3
        ELSE                                   4
    END                                         AS risk_rank

FROM stg_eric
WHERE is_valid_record = TRUE
ORDER BY year_sort, risk_rank, backlog_cost_per_bed DESC;
