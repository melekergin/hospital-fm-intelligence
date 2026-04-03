/* @bruin
name: stg_eric
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_eric
@bruin */

SELECT
    trust_code,
    trust_name,
    region,
    year,

    CAST(SPLIT_PART(year, '/', 1) AS INTEGER)           AS year_sort,

    maintenance_backlog_cost_gbp,
    total_energy_cost_gbp,
    cleaning_cost_gbp,
    cleaned_floor_area_m2,
    available_beds,

    ROUND(
        total_energy_cost_gbp / NULLIF(available_beds, 0),
        2
    )                                                   AS energy_cost_per_bed,

    ROUND(
        maintenance_backlog_cost_gbp / NULLIF(available_beds, 0),
        2
    )                                                   AS backlog_cost_per_bed,

    ROUND(
        cleaning_cost_gbp / NULLIF(cleaned_floor_area_m2, 0),
        2
    )                                                   AS cleaning_cost_per_m2,

    CASE
        WHEN maintenance_backlog_cost_gbp IS NULL OR maintenance_backlog_cost_gbp < 0 THEN FALSE
        WHEN total_energy_cost_gbp IS NULL OR total_energy_cost_gbp < 0 THEN FALSE
        WHEN cleaning_cost_gbp IS NULL OR cleaning_cost_gbp < 0 THEN FALSE
        WHEN cleaned_floor_area_m2 IS NULL OR cleaned_floor_area_m2 <= 0 THEN FALSE
        WHEN available_beds IS NULL OR available_beds <= 0 THEN FALSE
        ELSE TRUE
    END                                                 AS is_valid_record,

    CASE
        WHEN maintenance_backlog_cost_gbp / NULLIF(available_beds, 0) >= 5000 THEN 'High'
        WHEN maintenance_backlog_cost_gbp / NULLIF(available_beds, 0) >= 2500 THEN 'Significant'
        WHEN maintenance_backlog_cost_gbp / NULLIF(available_beds, 0) >= 1000 THEN 'Moderate'
        ELSE 'Low'
    END                                                 AS backlog_risk_band

FROM raw_eric
WHERE available_beds IS NOT NULL
  AND available_beds > 0;

