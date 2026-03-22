/* @bruin
name: raw_eric
type: duckdb.sql
materialization:
  type: table
@bruin */

-- This query reads the CSV file and loads it into a table named 'raw_eric' in DuckDB
SELECT 
    Trust_Code,
    Year,
    CAST(Maintenance_Backlog_Cost AS DOUBLE) AS Maintenance_Backlog_Cost,
    CAST(Total_Energy_Cost AS DOUBLE) AS Total_Energy_Cost,
    CAST(Available_Beds AS INT) AS Available_Beds
FROM read_csv_auto('data/raw/eric_data.csv', header=True);
