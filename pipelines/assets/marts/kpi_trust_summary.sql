/* @bruin
name: kpi_trust_summary
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_eric
@bruin */

-- KPI: Latest-year snapshot per trust — one row per trust, most recent year only.
-- This is the "executive dashboard" mart: one glance, full picture.
WITH latest_year AS (
    SELECT MAX(year_sort) AS max_year
    FROM stg_eric
    WHERE is_valid_record = TRUE
),
prior_year AS (
    SELECT trust_code,
           maintenance_backlog_cost_gbp AS prior_backlog_gbp,
           total_energy_cost_gbp        AS prior_energy_cost,
           cleaning_cost_gbp            AS prior_cleaning_cost
    FROM stg_eric
    WHERE year_sort = (SELECT max_year - 1 FROM latest_year)
      AND is_valid_record = TRUE
)
SELECT
    s.trust_code,
    s.trust_name,
    s.region,
    s.year                                                           AS latest_year,
    s.maintenance_backlog_cost_gbp                                   AS backlog_gbp,
    s.total_energy_cost_gbp                                          AS energy_cost_gbp,
    s.cleaning_cost_gbp                                              AS cleaning_cost_gbp,
    s.cleaned_floor_area_m2,
    s.available_beds,
    s.energy_cost_per_bed,
    s.backlog_cost_per_bed,
    s.cleaning_cost_per_m2,
    s.backlog_risk_band,

    -- YoY change vs prior year
    s.maintenance_backlog_cost_gbp - p.prior_backlog_gbp             AS backlog_change_gbp,
    ROUND(
        (s.maintenance_backlog_cost_gbp - p.prior_backlog_gbp)
        / NULLIF(p.prior_backlog_gbp, 0) * 100,
    1)                                                               AS backlog_change_pct,

    s.total_energy_cost_gbp - p.prior_energy_cost                    AS energy_change_gbp,
    ROUND(
        (s.total_energy_cost_gbp - p.prior_energy_cost)
        / NULLIF(p.prior_energy_cost, 0) * 100,
    1)                                                               AS energy_change_pct,

    s.cleaning_cost_gbp - p.prior_cleaning_cost                      AS cleaning_change_gbp,
    ROUND(
        (s.cleaning_cost_gbp - p.prior_cleaning_cost)
        / NULLIF(p.prior_cleaning_cost, 0) * 100,
    1)                                                               AS cleaning_change_pct

FROM stg_eric s
JOIN latest_year ly ON s.year_sort = ly.max_year
LEFT JOIN prior_year p ON s.trust_code = p.trust_code
WHERE s.is_valid_record = TRUE
ORDER BY s.maintenance_backlog_cost_gbp DESC;
