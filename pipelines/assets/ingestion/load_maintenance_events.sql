/* @bruin
name: raw_maintenance_events
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT *
FROM read_csv_auto(
    'data/raw/synthetic/maintenance_events.csv',
    header = TRUE
);
