/* @bruin
name: stg_eric
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_eric
@bruin */

SELECT
    -- Core identifiers
    Trust_Code                                          AS trust_code,
    Year                                                AS year,

    -- Parse year into a sortable integer (e.g. '2022/23' -> 2022)
    CAST(SPLIT_PART(Year, '/', 1) AS INTEGER)           AS year_sort,

    -- Raw financials
    Maintenance_Backlog_Cost                            AS maintenance_backlog_cost,
    Total_Energy_Cost                                   AS total_energy_cost,
    Available_Beds                                      AS available_beds,

    -- Derived per-bed KPIs (computed once, reused across marts)
    ROUND(
        Total_Energy_Cost / NULLIF(Available_Beds, 0),
    2)                                                  AS energy_cost_per_bed,

    ROUND(
        Maintenance_Backlog_Cost / NULLIF(Available_Beds, 0),
    2)                                                  AS backlog_cost_per_bed,

    -- Data quality flag
    CASE
        WHEN Maintenance_Backlog_Cost IS NULL OR Maintenance_Backlog_Cost < 0 THEN FALSE
        WHEN Total_Energy_Cost IS NULL OR Total_Energy_Cost < 0              THEN FALSE
        WHEN Available_Beds IS NULL OR Available_Beds <= 0                   THEN FALSE
        ELSE TRUE
    END                                                 AS is_valid_record

FROM raw_eric
WHERE Available_Beds IS NOT NULL
  AND Available_Beds > 0;

