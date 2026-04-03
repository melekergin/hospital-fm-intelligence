/* @bruin
name: raw_aemp_batches
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT *
FROM read_csv_auto(
    'data/raw/synthetic/aemp_batches.csv',
    header = TRUE
);
