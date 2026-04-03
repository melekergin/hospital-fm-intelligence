/* @bruin
name: raw_aemp_cycles
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT *
FROM read_csv_auto(
    'data/raw/synthetic/aemp_cycles.csv',
    header = TRUE
);
