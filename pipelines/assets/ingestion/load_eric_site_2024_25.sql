/* @bruin
name: raw_eric_site_2024_25
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT *
FROM read_csv_auto(
    'data/raw/nhs_eric/eric_2024_25_site_data_utf8.csv',
    header = TRUE,
    all_varchar = TRUE
);
