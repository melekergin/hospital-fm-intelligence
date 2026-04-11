/* @bruin
name: raw_bed_turnover_events
type: duckdb.sql
materialization:
  type: table
@bruin */

SELECT *
FROM read_csv_auto(
    'data/raw/synthetic/bed_turnover_events.csv',
    header = TRUE
);
