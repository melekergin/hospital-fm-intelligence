from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hospital_fm.db"
OUTPUT_DIR = ROOT / "data" / "raw" / "synthetic"
CYCLES_PATH = OUTPUT_DIR / "aemp_cycles.csv"
BATCHES_PATH = OUTPUT_DIR / "aemp_batches.csv"


SHIFT_WINDOWS = [
    ("Night", 0, 8),
    ("Day", 8, 16),
    ("Late", 16, 24),
]

PROGRAMS = [
    ("Instrument Set", 75, 0.95),
    ("Container Set", 92, 0.97),
    ("Flexible Scope Tray", 68, 0.91),
    ("Orthopaedic Tray", 88, 0.94),
]


def load_trusts() -> list[tuple]:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        """
        SELECT
            trust_code,
            trust_name,
            region,
            trust_type,
            gross_internal_floor_area_m2,
            total_backlog_gbp
        FROM kpi_eric_real_trust_estate_metrics
        WHERE year = '2024/25'
        ORDER BY total_backlog_gbp DESC
        LIMIT 18
        """
    ).fetchall()
    con.close()
    return rows


def cycle_count(area_m2: float) -> int:
    return max(2200, round(area_m2 / 420))


def build_rows() -> tuple[list[dict], list[dict]]:
    rng = random.Random(84)
    trusts = load_trusts()
    cycles: list[dict] = []
    batches: list[dict] = []

    for trust_code, trust_name, region, trust_type, area_m2, backlog in trusts:
        total_cycles = cycle_count(area_m2)
        autoclave_count = max(4, round(area_m2 / 140000))
        start_date = datetime(2024, 4, 1, 0, 0, 0)

        for idx in range(1, total_cycles + 1):
            day_offset = rng.randint(0, 364)
            shift_name, start_hour, end_hour = rng.choice(SHIFT_WINDOWS)
            start_ts = start_date + timedelta(days=day_offset, hours=rng.randint(start_hour, end_hour - 1), minutes=rng.choice([0, 10, 20, 30, 40, 50]))
            program_name, avg_minutes, pass_rate = rng.choice(PROGRAMS)
            cycle_minutes = max(38, int(rng.gauss(avg_minutes, 8)))
            end_ts = start_ts + timedelta(minutes=cycle_minutes)
            autoclave_id = f"{trust_code}-AUTO-{rng.randint(1, autoclave_count):02d}"
            cycle_id = f"{trust_code}-CYCLE-{idx:05d}"
            result = "Passed" if rng.random() < pass_rate else "Failed"
            traceability_complete = rng.random() < 0.985
            load_units = max(4, int(rng.gauss(11, 3)))
            reprocess_required = result == "Failed" or rng.random() < 0.012
            bottleneck_stage = rng.choice(["Decontamination", "Packing", "Sterilisation", "Cooling", "Dispatch"])

            cycles.append(
                {
                    "cycle_id": cycle_id,
                    "trust_code": trust_code,
                    "trust_name": trust_name,
                    "region": region,
                    "trust_type": trust_type,
                    "reporting_year": "2024/25",
                    "shift_name": shift_name,
                    "autoclave_id": autoclave_id,
                    "program_name": program_name,
                    "cycle_start_ts": start_ts.isoformat(),
                    "cycle_end_ts": end_ts.isoformat(),
                    "cycle_duration_minutes": cycle_minutes,
                    "result": result,
                    "traceability_complete": str(traceability_complete),
                    "load_units": load_units,
                    "reprocess_required": str(reprocess_required),
                    "bottleneck_stage": bottleneck_stage,
                }
            )

            batch_count = rng.randint(1, 3)
            for batch_idx in range(1, batch_count + 1):
                batch_id = f"{cycle_id}-B{batch_idx}"
                batch_type = rng.choice(["Theatre Set", "Ward Set", "Scope Tray", "Emergency Set"])
                batches.append(
                    {
                        "batch_id": batch_id,
                        "cycle_id": cycle_id,
                        "trust_code": trust_code,
                        "batch_type": batch_type,
                        "instrument_units": max(8, int(rng.gauss(22, 6))),
                        "priority": rng.choice(["Routine", "Urgent", "Urgent", "Routine", "Scheduled"]),
                        "dispatch_delay_minutes": max(0, int(rng.gauss(18 if result == "Passed" else 55, 14))),
                        "destination": rng.choice(["Theatre", "ICU", "Ward", "Cath Lab", "Endoscopy"]),
                    }
                )

    return cycles, batches


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    cycles, batches = build_rows()
    write_csv(CYCLES_PATH, cycles)
    write_csv(BATCHES_PATH, batches)
    print(f"wrote {len(cycles)} AEMP cycle rows to {CYCLES_PATH}")
    print(f"wrote {len(batches)} AEMP batch rows to {BATCHES_PATH}")


if __name__ == "__main__":
    main()
