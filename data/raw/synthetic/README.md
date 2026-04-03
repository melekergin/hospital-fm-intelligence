# Synthetic Data

This folder contains generated operational hospital FM data used to extend the real NHS ERIC benchmark layer.

Current generator outputs:
- `equipment_register.csv`
- `maintenance_events.csv`
- `aemp_cycles.csv`
- `aemp_batches.csv`

Generation command:

```powershell
python generators/generate_equipment_data.py
python generators/generate_aemp_data.py
```
