/* @bruin
name: raw_equipment_register
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT *
FROM read_csv_auto(
    'data/raw/synthetic/equipment_register.csv',
    header = TRUE
);
