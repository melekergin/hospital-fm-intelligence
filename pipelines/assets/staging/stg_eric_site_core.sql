/* @bruin
name: stg_eric_site_core
type: duckdb.sql
materialization:
  type: view
depends:
  - raw_eric_site_2023_24
  - raw_eric_site_2024_25
@bruin */

WITH site_2023 AS (
    SELECT
        '2023/24' AS year,
        2023 AS year_sort,
        "Trust Code" AS trust_code,
        "Trust Name" AS trust_name,
        "Commissioning Region" AS region,
        "Trust Type" AS trust_type,
        "Site Code" AS site_code,
        "Site Name" AS site_name,
        "Site Type" AS site_type,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Gross internal floor area (m²)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS gross_internal_floor_area_m2,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Single bedrooms for patients with en-suite facilities (No.)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS single_bedrooms_ensuite,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Single bedrooms for patients without en-suite facilities (No.)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS single_bedrooms_no_ensuite,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Isolation rooms (No.)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS isolation_rooms,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate high risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_high_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate significant risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_significant_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate moderate risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_moderate_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate low risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_low_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cleaning service cost (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS cleaning_service_cost_gbp,
        COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - green electricity tariff costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - trust owned solar costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - third party owned solar costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - other renewables costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - other costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + 0
        + 0
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Gas costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Oil costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Non-fossil fuel - renewable costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Other energy costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0) AS total_energy_cost_gbp
    FROM raw_eric_site_2023_24
),
site_2024 AS (
    SELECT
        '2024/25' AS year,
        2024 AS year_sort,
        "Trust Code" AS trust_code,
        "Trust Name" AS trust_name,
        "Commissioning Region" AS region,
        "Trust Type" AS trust_type,
        "Site Code" AS site_code,
        "Site Name" AS site_name,
        "Site Type" AS site_type,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Gross internal floor area (m²)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS gross_internal_floor_area_m2,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Single bedrooms for patients with en-suite facilities (No.)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS single_bedrooms_ensuite,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Single bedrooms for patients without en-suite facilities (No.)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS single_bedrooms_no_ensuite,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Isolation rooms (No.)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS isolation_rooms,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate high risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_high_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate significant risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_significant_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate moderate risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_moderate_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cost to eradicate low risk backlog (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS backlog_low_risk_gbp,
        TRY_CAST(REPLACE(NULLIF(NULLIF("Cleaning service cost (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE) AS cleaning_service_cost_gbp,
        COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - green electricity tariff costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - trust owned solar costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - third party owned solar costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - other renewables costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity - other costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Electricity purchased from CHP costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Thermal energy purchased from CHP costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Gas costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Oil costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Non-fossil fuel - renewable costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0)
        + COALESCE(TRY_CAST(REPLACE(NULLIF(NULLIF("Other energy costs (£)", 'Not Applicable'), ''), ',', '') AS DOUBLE), 0) AS total_energy_cost_gbp
    FROM raw_eric_site_2024_25
)
SELECT
    year,
    year_sort,
    trust_code,
    trust_name,
    region,
    trust_type,
    site_code,
    site_name,
    site_type,
    gross_internal_floor_area_m2,
    single_bedrooms_ensuite,
    single_bedrooms_no_ensuite,
    isolation_rooms,
    COALESCE(single_bedrooms_ensuite, 0) + COALESCE(single_bedrooms_no_ensuite, 0) + COALESCE(isolation_rooms, 0) AS inpatient_room_proxy,
    backlog_high_risk_gbp,
    backlog_significant_risk_gbp,
    backlog_moderate_risk_gbp,
    backlog_low_risk_gbp,
    COALESCE(backlog_high_risk_gbp, 0)
        + COALESCE(backlog_significant_risk_gbp, 0)
        + COALESCE(backlog_moderate_risk_gbp, 0)
        + COALESCE(backlog_low_risk_gbp, 0) AS total_backlog_gbp,
    cleaning_service_cost_gbp,
    total_energy_cost_gbp,
    CASE
        WHEN gross_internal_floor_area_m2 IS NULL OR gross_internal_floor_area_m2 <= 0 THEN FALSE
        WHEN total_energy_cost_gbp IS NULL THEN FALSE
        WHEN cleaning_service_cost_gbp IS NULL THEN FALSE
        ELSE TRUE
    END AS is_valid_record
FROM site_2023

UNION ALL

SELECT
    year,
    year_sort,
    trust_code,
    trust_name,
    region,
    trust_type,
    site_code,
    site_name,
    site_type,
    gross_internal_floor_area_m2,
    single_bedrooms_ensuite,
    single_bedrooms_no_ensuite,
    isolation_rooms,
    COALESCE(single_bedrooms_ensuite, 0) + COALESCE(single_bedrooms_no_ensuite, 0) + COALESCE(isolation_rooms, 0) AS inpatient_room_proxy,
    backlog_high_risk_gbp,
    backlog_significant_risk_gbp,
    backlog_moderate_risk_gbp,
    backlog_low_risk_gbp,
    COALESCE(backlog_high_risk_gbp, 0)
        + COALESCE(backlog_significant_risk_gbp, 0)
        + COALESCE(backlog_moderate_risk_gbp, 0)
        + COALESCE(backlog_low_risk_gbp, 0) AS total_backlog_gbp,
    cleaning_service_cost_gbp,
    total_energy_cost_gbp,
    CASE
        WHEN gross_internal_floor_area_m2 IS NULL OR gross_internal_floor_area_m2 <= 0 THEN FALSE
        WHEN total_energy_cost_gbp IS NULL THEN FALSE
        WHEN cleaning_service_cost_gbp IS NULL THEN FALSE
        ELSE TRUE
    END AS is_valid_record
FROM site_2024;
