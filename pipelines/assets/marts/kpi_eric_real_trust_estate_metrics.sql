/* @bruin
name: kpi_eric_real_trust_estate_metrics
type: duckdb.sql
materialization:
  type: table
depends:
  - stg_eric_site_core
@bruin */

SELECT
    year,
    year_sort,
    trust_code,
    trust_name,
    region,
    trust_type,
    COUNT(DISTINCT site_code) AS site_count,
    SUM(gross_internal_floor_area_m2) AS gross_internal_floor_area_m2,
    SUM(inpatient_room_proxy) AS inpatient_room_proxy,
    SUM(backlog_high_risk_gbp) AS backlog_high_risk_gbp,
    SUM(backlog_significant_risk_gbp) AS backlog_significant_risk_gbp,
    SUM(backlog_moderate_risk_gbp) AS backlog_moderate_risk_gbp,
    SUM(backlog_low_risk_gbp) AS backlog_low_risk_gbp,
    SUM(total_backlog_gbp) AS total_backlog_gbp,
    SUM(total_energy_cost_gbp) AS total_energy_cost_gbp,
    SUM(cleaning_service_cost_gbp) AS total_cleaning_cost_gbp,
    ROUND(SUM(total_backlog_gbp) / NULLIF(SUM(gross_internal_floor_area_m2), 0), 2) AS backlog_cost_per_m2,
    ROUND(SUM(total_energy_cost_gbp) / NULLIF(SUM(gross_internal_floor_area_m2), 0), 2) AS energy_cost_per_m2,
    ROUND(SUM(cleaning_service_cost_gbp) / NULLIF(SUM(gross_internal_floor_area_m2), 0), 2) AS cleaning_cost_per_m2,
    ROUND(SUM(total_backlog_gbp) / NULLIF(SUM(inpatient_room_proxy), 0), 2) AS backlog_per_inpatient_room_proxy,
    CASE
        WHEN SUM(total_backlog_gbp) / NULLIF(SUM(gross_internal_floor_area_m2), 0) >= 500 THEN 'High'
        WHEN SUM(total_backlog_gbp) / NULLIF(SUM(gross_internal_floor_area_m2), 0) >= 250 THEN 'Significant'
        WHEN SUM(total_backlog_gbp) / NULLIF(SUM(gross_internal_floor_area_m2), 0) >= 100 THEN 'Moderate'
        ELSE 'Low'
    END AS backlog_risk_band_by_m2
FROM stg_eric_site_core
WHERE is_valid_record = TRUE
GROUP BY 1, 2, 3, 4, 5, 6
ORDER BY year_sort, total_backlog_gbp DESC;
