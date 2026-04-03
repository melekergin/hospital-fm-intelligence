# KPI Catalog

## Purpose

This document defines the main KPIs currently used in the app. It is intentionally compact and focused on the live build.

## Estate KPIs

### Backlog Cost per m2
- Source: official NHS ERIC site data
- Grain: trust-year
- Logic: `total_backlog_gbp / gross_internal_floor_area_m2`
- Meaning: shows how much unresolved estate burden sits behind each square metre of estate footprint

### Energy Cost per m2
- Source: official NHS ERIC site data
- Grain: trust-year
- Logic: `total_energy_cost_gbp / gross_internal_floor_area_m2`
- Meaning: approximates the operating cost of keeping the estate live and functional

### Cleaning Cost per m2
- Source: official NHS ERIC site data
- Grain: trust-year
- Logic: `total_cleaning_cost_gbp / gross_internal_floor_area_m2`
- Meaning: compares how expensive it is to keep estates clean across different trust footprints

### Backlog Risk Band by m2
- Source: derived from official NHS ERIC site data
- Grain: trust-year
- Logic:
  - `High` if backlog per m2 >= 500
  - `Significant` if backlog per m2 >= 250
  - `Moderate` if backlog per m2 >= 100
  - otherwise `Low`
- Meaning: provides a readable risk framing for estate pressure

## Equipment and Maintenance KPIs

### Failure Rate per Asset
- Source: synthetic equipment and maintenance data
- Grain: trust-year-equipment category
- Logic: `corrective_events / asset_count`
- Meaning: approximates how frequently a device class breaks down relative to the installed base

### MTTR Hours
- Source: synthetic equipment and maintenance data
- Grain: trust-year-equipment category
- Logic: `corrective_downtime_hours / corrective_events`
- Meaning: average time to recover from corrective maintenance

### Availability Percent
- Source: synthetic equipment and maintenance data
- Grain: trust-year-equipment category
- Logic: `(8760 * asset_count - downtime_hours) / (8760 * asset_count) * 100`
- Meaning: approximates how available equipment remains over the reporting year

### Work-Order Status Counts
- Source: synthetic maintenance flow data
- Grain: trust-year
- Logic: counts of work orders in statuses such as `Notification`, `Planning`, `Approved`, `In Progress`, `Technically Complete`, and `Closed`
- Meaning: shows where maintenance activity is accumulating operationally

## Compliance KPIs

### Compliance Rate Percent
- Source: synthetic inspection status data
- Grain: trust-year-equipment category
- Logic: `in_date_assets / asset_count * 100`
- Meaning: shows how much of the asset base is still within inspection date

### Overdue Assets
- Source: synthetic inspection status data
- Grain: trust-year-equipment category
- Logic: count of assets with `compliance_status = 'Overdue'`
- Meaning: highlights inspection backlog

### Action Required Assets
- Source: synthetic inspection status data
- Grain: trust-year-equipment category
- Logic: count of assets with `compliance_status = 'Action Required'`
- Meaning: shows the most urgent inspection or compliance issues

### Compliance Risk Bucket
- Source: synthetic inspection status data
- Grain: asset
- Logic:
  - `Action Required`
  - `Critical Overdue`
  - `Overdue`
  - `Due Soon`
  - `In Date`
- Meaning: converts raw due dates into a more operational inspection-control view

## AEMP KPIs

### Conformity Rate Percent
- Source: synthetic AEMP cycle data
- Grain: trust-year
- Logic: `passed_cycles / cycle_count * 100`
- Meaning: indicates the share of AEMP cycles that complete successfully

### Traceability Rate Percent
- Source: synthetic AEMP cycle data
- Grain: trust-year
- Logic: `traceability_complete / cycle_count * 100`
- Meaning: indicates how consistently sterile processing records remain traceable

### Reprocess Rate Percent
- Source: synthetic AEMP cycle data
- Grain: trust-year
- Logic: `reprocess_required / cycle_count * 100`
- Meaning: indicates how much throughput is lost to failed or repeated processing

### Average Dispatch Delay Minutes
- Source: synthetic AEMP batch data
- Grain: trust-year
- Logic: average of batch dispatch delay
- Meaning: approximates how long sterile sets take to move back into clinical use

## Trust Cockpit KPIs

### Total Work Orders
- Source: synthetic maintenance flow data
- Grain: trust-year
- Logic: sum of work-order counts across statuses and equipment categories
- Meaning: gives a high-level sense of operational maintenance load

### AEMP Cycle Count
- Source: synthetic AEMP cycle data
- Grain: trust-year
- Logic: count of AEMP cycles
- Meaning: acts as a trust-level proxy for sterile processing throughput

### Combined Trust Cockpit
- Source: official ERIC plus synthetic maintenance, compliance, and AEMP marts
- Grain: trust-year
- Meaning: integrates estate pressure and operational process pressure into one trust-level view
