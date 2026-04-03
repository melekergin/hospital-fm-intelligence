from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hospital_fm.db"
OUTPUT_DIR = ROOT / "data" / "raw" / "synthetic"
REGISTER_PATH = OUTPUT_DIR / "equipment_register.csv"
EVENTS_PATH = OUTPUT_DIR / "maintenance_events.csv"


DEVICE_PROFILES = [
    {"category": "CT Scanner", "prefix": "CT", "service_days": 45, "failure_rate": 0.14, "base_cost": 12500},
    {"category": "MRI Scanner", "prefix": "MRI", "service_days": 60, "failure_rate": 0.10, "base_cost": 16000},
    {"category": "Ventilator", "prefix": "VENT", "service_days": 30, "failure_rate": 0.18, "base_cost": 2400},
    {"category": "Infusion Pump", "prefix": "PUMP", "service_days": 21, "failure_rate": 0.16, "base_cost": 320},
    {"category": "Patient Monitor", "prefix": "MON", "service_days": 28, "failure_rate": 0.13, "base_cost": 540},
    {"category": "Lift", "prefix": "LIFT", "service_days": 40, "failure_rate": 0.08, "base_cost": 3100},
    {"category": "Air Handling Unit", "prefix": "AHU", "service_days": 35, "failure_rate": 0.11, "base_cost": 4200},
]

WORK_ORDER_STATUSES = [
    ("Notification", 0.08),
    ("Planning", 0.12),
    ("Approved", 0.14),
    ("In Progress", 0.18),
    ("Technically Complete", 0.18),
    ("Closed", 0.30),
]

INSPECTION_OUTCOMES = [
    ("Pass", 0.78),
    ("Pass with Advisory", 0.16),
    ("Fail", 0.06),
]


def load_trusts() -> list[tuple]:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        """
        SELECT
            year,
            trust_code,
            trust_name,
            region,
            trust_type,
            site_count,
            gross_internal_floor_area_m2,
            total_backlog_gbp
        FROM kpi_eric_real_trust_estate_metrics
        WHERE year = '2024/25'
        ORDER BY total_backlog_gbp DESC
        LIMIT 24
        """
    ).fetchall()
    con.close()
    return rows


def equipment_count_for_profile(profile: dict, area_m2: float, site_count: int) -> int:
    if profile["category"] in {"CT Scanner", "MRI Scanner"}:
        return max(1, round(area_m2 / 180000))
    if profile["category"] == "Ventilator":
        return max(6, round(area_m2 / 20000))
    if profile["category"] == "Infusion Pump":
        return max(30, round(area_m2 / 3500))
    if profile["category"] == "Patient Monitor":
        return max(18, round(area_m2 / 5000))
    if profile["category"] == "Lift":
        return max(2, site_count * 2)
    if profile["category"] == "Air Handling Unit":
        return max(4, round(area_m2 / 25000))
    return 1


def create_register_and_events() -> tuple[list[dict], list[dict]]:
    rng = random.Random(42)
    trusts = load_trusts()
    register: list[dict] = []
    events: list[dict] = []

    for year, trust_code, trust_name, region, trust_type, site_count, area_m2, backlog in trusts:
        for profile in DEVICE_PROFILES:
            count = equipment_count_for_profile(profile, area_m2, site_count)
            for idx in range(1, count + 1):
                asset_id = f"{trust_code}-{profile['prefix']}-{idx:03d}"
                install_year = rng.randint(2012, 2024)
                criticality = "High" if profile["category"] in {"CT Scanner", "MRI Scanner", "Ventilator", "Air Handling Unit"} else "Medium"
                acquisition_value = round(profile["base_cost"] * rng.uniform(18, 140), 2)
                site_label = f"{trust_code}-SITE-{rng.randint(1, max(site_count, 1)):02d}"
                inspection_interval_days = 365 if criticality == "High" else 540
                last_inspection_date = date(2024, 4, 1) - timedelta(days=rng.randint(20, 420))
                next_inspection_due_date = last_inspection_date + timedelta(days=inspection_interval_days)
                inspection_outcome = rng.choices(
                    [item[0] for item in INSPECTION_OUTCOMES],
                    weights=[item[1] for item in INSPECTION_OUTCOMES],
                    k=1,
                )[0]
                compliance_status = "Overdue" if next_inspection_due_date < date(2025, 3, 31) else "In Date"
                if inspection_outcome == "Fail":
                    compliance_status = "Action Required"
                register.append(
                    {
                        "trust_code": trust_code,
                        "trust_name": trust_name,
                        "region": region,
                        "trust_type": trust_type,
                        "reporting_year": year,
                        "asset_id": asset_id,
                        "site_code": site_label,
                        "equipment_category": profile["category"],
                        "manufacturer": rng.choice(["Siemens", "GE Healthcare", "Philips", "Drager", "Otis", "Daikin"]),
                        "criticality": criticality,
                        "install_year": install_year,
                        "expected_service_interval_days": profile["service_days"],
                        "last_inspection_date": last_inspection_date.isoformat(),
                        "next_inspection_due_date": next_inspection_due_date.isoformat(),
                        "inspection_outcome": inspection_outcome,
                        "compliance_status": compliance_status,
                        "acquisition_value_gbp": acquisition_value,
                    }
                )

                start_of_year = date(2024, 4, 1)
                end_of_year = date(2025, 3, 31)
                planned_date = start_of_year + timedelta(days=rng.randint(0, 330))
                planned_duration = rng.randint(2, 8) if criticality == "High" else rng.randint(1, 4)
                planned_cost = round(profile["base_cost"] * rng.uniform(0.5, 1.4), 2)
                events.append(
                    {
                        "event_id": f"PM-{asset_id}-001",
                        "asset_id": asset_id,
                        "trust_code": trust_code,
                        "event_type": "Planned Maintenance",
                        "priority": "Planned",
                        "event_start_ts": datetime.combine(planned_date, datetime.min.time()).isoformat(),
                        "downtime_hours": planned_duration,
                        "maintenance_cost_gbp": planned_cost,
                        "status": rng.choices(
                            [item[0] for item in WORK_ORDER_STATUSES],
                            weights=[item[1] for item in WORK_ORDER_STATUSES],
                            k=1,
                        )[0],
                        "work_center": rng.choice(["Biomedical", "Facilities", "External Vendor"]),
                        "planner_group": rng.choice(["MED", "EST", "OPS"]),
                        "failure_mode": "",
                    }
                )

                if rng.random() < profile["failure_rate"]:
                    fail_date = start_of_year + timedelta(days=rng.randint(10, 360))
                    downtime = rng.randint(6, 72) if criticality == "High" else rng.randint(2, 24)
                    repair_cost = round(profile["base_cost"] * rng.uniform(0.7, 2.2), 2)
                    priority = "Urgent" if criticality == "High" else "Routine"
                    failure_mode = rng.choice(
                        [
                            "Power supply failure",
                            "Sensor drift",
                            "Cooling issue",
                            "Mechanical wear",
                            "Software fault",
                            "Calibration failure",
                        ]
                    )
                    events.append(
                        {
                            "event_id": f"CM-{asset_id}-001",
                            "asset_id": asset_id,
                            "trust_code": trust_code,
                            "event_type": "Corrective Maintenance",
                            "priority": priority,
                            "event_start_ts": datetime.combine(fail_date, datetime.min.time()).isoformat(),
                            "downtime_hours": downtime,
                            "maintenance_cost_gbp": repair_cost,
                            "status": rng.choices(
                                [item[0] for item in WORK_ORDER_STATUSES],
                                weights=[item[1] for item in WORK_ORDER_STATUSES],
                                k=1,
                            )[0],
                            "work_center": rng.choice(["Biomedical", "Facilities", "External Vendor"]),
                            "planner_group": rng.choice(["MED", "EST", "OPS"]),
                            "failure_mode": failure_mode,
                        }
                    )

    return register, events


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    register, events = create_register_and_events()
    write_csv(REGISTER_PATH, register)
    write_csv(EVENTS_PATH, events)
    print(f"wrote {len(register)} equipment rows to {REGISTER_PATH}")
    print(f"wrote {len(events)} maintenance rows to {EVENTS_PATH}")


if __name__ == "__main__":
    main()
