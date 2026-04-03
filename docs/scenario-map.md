# Scenario Map

## Purpose

This project should teach hospital facility management through recognizable situations, not through technical page names alone.

The question is not just:

> "What KPI is this?"

The better question is:

> "What hospital problem is happening here, and what does FM have to do with it?"

## Core Scenarios

### 1. Why is there no bed for a new patient?

What the user learns:
- a bed can exist physically but still not be ready for use
- cleaning, room readiness, maintenance, and equipment availability all affect patient flow

Current app links:
- landing page
- `1_A_Day_in_FM.py`
- `2_Estate_Pressure.py`
- `5_Trust_Drilldown.py`

### 2. What happens when a CT scanner fails?

What the user learns:
- equipment is registered, maintained, inspected, and repaired through a process
- a failure affects more than the machine itself
- downtime can affect appointments, diagnostics, and clinical throughput

Current app links:
- `3_Equipment_Journey.py`
- `4_Compliance_Control.py`
- `5_Trust_Drilldown.py`

### 3. Why can surgery be delayed because of sterile instruments?

What the user learns:
- sterile processing is a hidden operational dependency
- traceability, conformity, reprocessing, and dispatch delay matter clinically

Current app links:
- `6_AEMP_Process.py`
- `1_A_Day_in_FM.py`
- `5_Trust_Drilldown.py`

### 4. What happens when inspections are overdue?

What the user learns:
- compliance is not just paperwork
- overdue inspections create operational and safety risk
- some issues are urgent even before a visible failure happens

Current app links:
- `4_Compliance_Control.py`
- `3_Equipment_Journey.py`
- `5_Trust_Drilldown.py`

### 5. Why does maintenance backlog matter if patients never see it?

What the user learns:
- hidden building and infrastructure problems accumulate over time
- backlog becomes a strategic risk even when patients do not notice it immediately
- estate problems can later turn into clinical disruption

Current app links:
- `app.py`
- `1_A_Day_in_FM.py`
- `2_Estate_Pressure.py`
- `5_Trust_Drilldown.py`

### 6. Why do energy and cleaning matter every single day?

What the user learns:
- FM is not only about breakdowns
- hospitals depend on constant background support to stay usable, safe, and efficient

Current app links:
- `app.py`
- `1_A_Day_in_FM.py`
- `2_Estate_Pressure.py`

## Design Rule

Each scenario page or card should answer:
- what is happening?
- why does it matter?
- which FM team or process is involved?
- what should the user notice in the visual?

## Glossary Terms That Need Simple Explanations

- backlog
- trust
- estate
- work order
- planned maintenance
- corrective maintenance
- compliance
- traceability
- reprocessing
- AEMP / ZSVA

## Next UX Direction

The app should gradually move from:
- technical dashboard language

toward:
- human scenario language

That means:
- simpler page intros
- more “how to read this” guidance
- visible glossary support
- scenario-first navigation from the landing page
