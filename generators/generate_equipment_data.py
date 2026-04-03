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


def sample_response_minutes(rng: random.Random, priority: str) -> tuple[int, int]:
    if priority == "Urgent":
        target = 120
        return target, rng.randint(12, 150)
    if priority == "Routine":
        target = 480
        return target, rng.randint(45, 540)
    target = 1440
    return target, rng.randint(60, 480)


def build_planned_timeline(
    rng: random.Random,
    status: str,
    as_of_ts: datetime,
    duration_hours: int,
) -> dict[str, datetime | int | str | None]:
    response_target, response_minutes = sample_response_minutes(rng, "Planned")

    if status == "Closed":
        event_start = as_of_ts - timedelta(days=rng.randint(10, 260), hours=rng.randint(0, 20))
        reported = event_start - timedelta(days=rng.randint(5, 30), hours=rng.randint(0, 8))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = event_start - timedelta(hours=rng.randint(0, 3))
        tech_complete = work_started + timedelta(hours=duration_hours)
        closed_ts = tech_complete + timedelta(hours=rng.randint(2, 36))
    elif status == "Technically Complete":
        event_start = as_of_ts - timedelta(days=rng.randint(1, 10), hours=rng.randint(0, 10))
        reported = event_start - timedelta(days=rng.randint(3, 18), hours=rng.randint(0, 6))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = event_start - timedelta(hours=rng.randint(0, 2))
        tech_complete = work_started + timedelta(hours=duration_hours)
        closed_ts = None
    elif status == "In Progress":
        event_start = as_of_ts - timedelta(days=rng.randint(0, 6), hours=rng.randint(0, 10))
        reported = event_start - timedelta(days=rng.randint(2, 12), hours=rng.randint(0, 5))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = min(
            first_response + timedelta(minutes=rng.randint(15, 180)),
            event_start + timedelta(hours=rng.randint(0, 2)),
        )
        tech_complete = None
        closed_ts = None
    elif status == "Approved":
        event_start = as_of_ts + timedelta(days=rng.randint(1, 21), hours=rng.randint(6, 12))
        reported = as_of_ts - timedelta(days=rng.randint(1, 8), hours=rng.randint(0, 6))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = None
        tech_complete = None
        closed_ts = None
    elif status == "Planning":
        event_start = as_of_ts + timedelta(days=rng.randint(3, 30), hours=rng.randint(6, 12))
        reported = as_of_ts - timedelta(days=rng.randint(0, 6), hours=rng.randint(0, 8))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = None
        tech_complete = None
        closed_ts = None
    else:
        event_start = as_of_ts + timedelta(days=rng.randint(5, 35), hours=rng.randint(6, 12))
        reported = as_of_ts - timedelta(days=rng.randint(0, 3), hours=rng.randint(0, 8))
        first_response = None
        work_started = None
        tech_complete = None
        closed_ts = None

    return {
        "event_start": event_start,
        "reported": reported,
        "first_response": first_response,
        "work_started": work_started,
        "tech_complete": tech_complete,
        "closed": closed_ts,
        "response_target": response_target,
        "response_minutes": response_minutes if first_response else None,
    }


def build_corrective_timeline(
    rng: random.Random,
    status: str,
    as_of_ts: datetime,
    duration_hours: int,
    priority: str,
) -> dict[str, datetime | int | str | None]:
    response_target, response_minutes = sample_response_minutes(rng, priority)

    if status == "Closed":
        event_start = as_of_ts - timedelta(days=rng.randint(2, 120), hours=rng.randint(0, 20))
        reported = event_start + timedelta(minutes=rng.randint(5, 90) if priority == "Urgent" else rng.randint(10, 180))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = first_response + timedelta(minutes=rng.randint(10, 120))
        tech_complete = work_started + timedelta(hours=duration_hours)
        closed_ts = tech_complete + timedelta(hours=rng.randint(2, 24))
    elif status == "Technically Complete":
        event_start = as_of_ts - timedelta(days=rng.randint(1, 6), hours=rng.randint(0, 12))
        reported = event_start + timedelta(minutes=rng.randint(5, 60) if priority == "Urgent" else rng.randint(15, 120))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = first_response + timedelta(minutes=rng.randint(10, 120))
        tech_complete = work_started + timedelta(hours=duration_hours)
        closed_ts = None
    elif status == "In Progress":
        event_start = as_of_ts - timedelta(days=rng.randint(0, 4), hours=rng.randint(0, 12))
        reported = event_start + timedelta(minutes=rng.randint(5, 45) if priority == "Urgent" else rng.randint(10, 90))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = first_response + timedelta(minutes=rng.randint(10, 90))
        tech_complete = None
        closed_ts = None
    elif status == "Approved":
        event_start = as_of_ts - timedelta(days=rng.randint(0, 3), hours=rng.randint(0, 10))
        reported = event_start + timedelta(minutes=rng.randint(5, 30) if priority == "Urgent" else rng.randint(10, 90))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = None
        tech_complete = None
        closed_ts = None
    elif status == "Planning":
        event_start = as_of_ts - timedelta(days=rng.randint(0, 2), hours=rng.randint(0, 8))
        reported = event_start + timedelta(minutes=rng.randint(5, 20) if priority == "Urgent" else rng.randint(10, 60))
        first_response = reported + timedelta(minutes=response_minutes)
        work_started = None
        tech_complete = None
        closed_ts = None
    else:
        event_start = as_of_ts - timedelta(days=rng.randint(0, 1), hours=rng.randint(0, 6))
        reported = event_start + timedelta(minutes=rng.randint(5, 20) if priority == "Urgent" else rng.randint(10, 45))
        first_response = None
        work_started = None
        tech_complete = None
        closed_ts = None

    return {
        "event_start": event_start,
        "reported": reported,
        "first_response": first_response,
        "work_started": work_started,
        "tech_complete": tech_complete,
        "closed": closed_ts,
        "response_target": response_target,
        "response_minutes": response_minutes if first_response else None,
    }


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
    as_of_ts = datetime(2025, 3, 31, 18, 0, 0)

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

                planned_duration = rng.randint(2, 8) if criticality == "High" else rng.randint(1, 4)
                planned_cost = round(profile["base_cost"] * rng.uniform(0.5, 1.4), 2)
                planned_status = rng.choices(
                    [item[0] for item in WORK_ORDER_STATUSES],
                    weights=[item[1] for item in WORK_ORDER_STATUSES],
                    k=1,
                )[0]
                planned_timeline = build_planned_timeline(
                    rng,
                    planned_status,
                    as_of_ts,
                    planned_duration,
                )
                events.append(
                    {
                        "event_id": f"PM-{asset_id}-001",
                        "asset_id": asset_id,
                        "trust_code": trust_code,
                        "event_type": "Planned Maintenance",
                        "priority": "Planned",
                        "event_start_ts": planned_timeline["event_start"].isoformat(),
                        "downtime_hours": planned_duration,
                        "maintenance_cost_gbp": planned_cost,
                        "status": planned_status,
                        "work_center": rng.choice(["Biomedical", "Facilities", "External Vendor"]),
                        "planner_group": rng.choice(["MED", "EST", "OPS"]),
                        "failure_mode": "",
                        "event_reported_ts": planned_timeline["reported"].isoformat(),
                        "first_response_ts": planned_timeline["first_response"].isoformat() if planned_timeline["first_response"] else "",
                        "work_started_ts": planned_timeline["work_started"].isoformat() if planned_timeline["work_started"] else "",
                        "technically_complete_ts": planned_timeline["tech_complete"].isoformat() if planned_timeline["tech_complete"] else "",
                        "closed_ts": planned_timeline["closed"].isoformat() if planned_timeline["closed"] else "",
                        "response_target_minutes": planned_timeline["response_target"],
                        "response_sla_met": (
                            "Yes"
                            if planned_timeline["response_minutes"] is not None
                            and planned_timeline["response_minutes"] <= planned_timeline["response_target"]
                            else "No"
                        ),
                        "as_of_ts": as_of_ts.isoformat(),
                    }
                )

                if rng.random() < profile["failure_rate"]:
                    downtime = rng.randint(6, 72) if criticality == "High" else rng.randint(2, 24)
                    repair_cost = round(profile["base_cost"] * rng.uniform(0.7, 2.2), 2)
                    priority = "Urgent" if criticality == "High" else "Routine"
                    corrective_status = rng.choices(
                        [item[0] for item in WORK_ORDER_STATUSES],
                        weights=[item[1] for item in WORK_ORDER_STATUSES],
                        k=1,
                    )[0]
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
                    corrective_timeline = build_corrective_timeline(
                        rng,
                        corrective_status,
                        as_of_ts,
                        downtime,
                        priority,
                    )
                    events.append(
                        {
                            "event_id": f"CM-{asset_id}-001",
                            "asset_id": asset_id,
                            "trust_code": trust_code,
                            "event_type": "Corrective Maintenance",
                            "priority": priority,
                            "event_start_ts": corrective_timeline["event_start"].isoformat(),
                            "downtime_hours": downtime,
                            "maintenance_cost_gbp": repair_cost,
                            "status": corrective_status,
                            "work_center": rng.choice(["Biomedical", "Facilities", "External Vendor"]),
                            "planner_group": rng.choice(["MED", "EST", "OPS"]),
                            "failure_mode": failure_mode,
                            "event_reported_ts": corrective_timeline["reported"].isoformat(),
                            "first_response_ts": corrective_timeline["first_response"].isoformat() if corrective_timeline["first_response"] else "",
                            "work_started_ts": corrective_timeline["work_started"].isoformat() if corrective_timeline["work_started"] else "",
                            "technically_complete_ts": corrective_timeline["tech_complete"].isoformat() if corrective_timeline["tech_complete"] else "",
                            "closed_ts": corrective_timeline["closed"].isoformat() if corrective_timeline["closed"] else "",
                            "response_target_minutes": corrective_timeline["response_target"],
                            "response_sla_met": (
                                "Yes"
                                if corrective_timeline["response_minutes"] is not None
                                and corrective_timeline["response_minutes"] <= corrective_timeline["response_target"]
                                else "No"
                            ),
                            "as_of_ts": as_of_ts.isoformat(),
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
