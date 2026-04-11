from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "hospital_fm.db"
OUTPUT_DIR = ROOT / "data" / "raw" / "synthetic"
BED_EVENTS_PATH = OUTPUT_DIR / "bed_turnover_events.csv"

WARD_TYPES = [
    ("General Ward", 0.46),
    ("Medical Ward", 0.22),
    ("Surgical Ward", 0.18),
    ("Critical Care", 0.07),
    ("Emergency Observation", 0.07),
]

PRIMARY_BLOCKERS = [
    ("No major blocker", 0.34),
    ("Cleaning queue", 0.22),
    ("Equipment not ready", 0.14),
    ("Deep clean / isolation reset", 0.09),
    ("Awaiting porter / room release", 0.09),
    ("Maintenance clearance", 0.07),
    ("Clinical hold / late discharge", 0.05),
]


def load_trusts() -> list[tuple]:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    rows = con.execute(
        """
        WITH ranked AS (
            SELECT
                year,
                year_sort,
                trust_code,
                trust_name,
                region,
                site_count,
                inpatient_room_proxy,
                total_backlog_gbp,
                ROW_NUMBER() OVER (PARTITION BY year ORDER BY total_backlog_gbp DESC) AS rn
            FROM kpi_eric_real_trust_estate_metrics
        )
        SELECT
            year,
            year_sort,
            trust_code,
            trust_name,
            region,
            site_count,
            inpatient_room_proxy,
            total_backlog_gbp
        FROM ranked
        WHERE rn <= 24
        ORDER BY year_sort, total_backlog_gbp DESC
        """
    ).fetchall()
    con.close()
    return rows


def event_count_for_trust(room_proxy: float, site_count: int) -> int:
    base = max(90, min(220, int(room_proxy * 1.2)))
    return max(base, site_count * 20)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def generate_events() -> list[dict]:
    rng = random.Random(84)
    rows: list[dict] = []

    for year, year_sort, trust_code, trust_name, region, site_count, room_proxy, backlog in load_trusts():
        year_start = datetime(year_sort, 4, 1, 0, 0, 0)
        year_end = datetime(year_sort + 1, 3, 31, 23, 0, 0)
        total_events = event_count_for_trust(room_proxy, site_count)

        for idx in range(1, total_events + 1):
            site_no = rng.randint(1, max(int(site_count), 1))
            site_code = f"{trust_code}-SITE-{site_no:02d}"
            ward_type = rng.choices([w[0] for w in WARD_TYPES], weights=[w[1] for w in WARD_TYPES], k=1)[0]
            bed_id = f"{trust_code}-{site_no:02d}-{idx:04d}"

            discharge_ts = year_start + timedelta(
                days=rng.randint(0, (year_end - year_start).days),
                hours=rng.randint(0, 23),
                minutes=rng.choice([0, 10, 20, 30, 40, 50]),
            )

            base_queue_minutes = rng.randint(5, 24)
            cleaning_minutes = rng.randint(18, 55)
            porter_delay_minutes = rng.randint(5, 25) if rng.random() < 0.18 else 0
            equipment_delay_minutes = rng.randint(10, 70) if rng.random() < 0.12 else 0
            maintenance_delay_minutes = rng.randint(20, 150) if rng.random() < 0.08 else 0
            isolation_delay_minutes = rng.randint(40, 160) if rng.random() < 0.07 else 0
            clinical_hold_minutes = rng.randint(15, 90) if rng.random() < 0.08 else 0

            primary_blocker = rng.choices(
                [b[0] for b in PRIMARY_BLOCKERS],
                weights=[b[1] for b in PRIMARY_BLOCKERS],
                k=1,
            )[0]

            if primary_blocker == "Cleaning queue":
                base_queue_minutes += rng.randint(20, 70)
            elif primary_blocker == "Deep clean / isolation reset":
                isolation_delay_minutes += rng.randint(60, 180)
            elif primary_blocker == "Equipment not ready":
                equipment_delay_minutes += rng.randint(35, 120)
            elif primary_blocker == "Maintenance clearance":
                maintenance_delay_minutes += rng.randint(60, 220)
            elif primary_blocker == "Awaiting porter / room release":
                porter_delay_minutes += rng.randint(20, 60)
            elif primary_blocker == "Clinical hold / late discharge":
                clinical_hold_minutes += rng.randint(40, 120)

            cleaning_start_ts = discharge_ts + timedelta(minutes=base_queue_minutes + porter_delay_minutes + clinical_hold_minutes)
            cleaning_complete_ts = cleaning_start_ts + timedelta(minutes=cleaning_minutes)
            maintenance_clear_ts = cleaning_complete_ts + timedelta(minutes=maintenance_delay_minutes)
            equipment_ready_ts = cleaning_complete_ts + timedelta(minutes=equipment_delay_minutes)
            isolation_clear_ts = cleaning_complete_ts + timedelta(minutes=isolation_delay_minutes)
            bed_ready_ts = max(cleaning_complete_ts, maintenance_clear_ts, equipment_ready_ts, isolation_clear_ts)

            turnaround_minutes = int((bed_ready_ts - discharge_ts).total_seconds() / 60)
            if turnaround_minutes <= 60:
                bucket = "Under 1 hour"
            elif turnaround_minutes <= 120:
                bucket = "1-2 hours"
            elif turnaround_minutes <= 240:
                bucket = "2-4 hours"
            elif turnaround_minutes <= 480:
                bucket = "4-8 hours"
            else:
                bucket = "Over 8 hours"

            rows.append(
                {
                    "event_id": f"BED-{trust_code}-{year_sort}-{idx:05d}",
                    "reporting_year": year,
                    "trust_code": trust_code,
                    "trust_name": trust_name,
                    "region": region,
                    "site_code": site_code,
                    "ward_type": ward_type,
                    "bed_id": bed_id,
                    "discharge_ts": discharge_ts.isoformat(),
                    "cleaning_start_ts": cleaning_start_ts.isoformat(),
                    "cleaning_complete_ts": cleaning_complete_ts.isoformat(),
                    "maintenance_clear_ts": maintenance_clear_ts.isoformat(),
                    "equipment_ready_ts": equipment_ready_ts.isoformat(),
                    "isolation_clear_ts": isolation_clear_ts.isoformat(),
                    "bed_ready_ts": bed_ready_ts.isoformat(),
                    "turnaround_target_minutes": 120,
                    "turnaround_minutes": turnaround_minutes,
                    "turnaround_bucket": bucket,
                    "within_target": "Yes" if turnaround_minutes <= 120 else "No",
                    "primary_blocker": primary_blocker,
                    "queue_delay_minutes": base_queue_minutes,
                    "cleaning_minutes": cleaning_minutes,
                    "porter_delay_minutes": porter_delay_minutes,
                    "equipment_delay_minutes": equipment_delay_minutes,
                    "maintenance_delay_minutes": maintenance_delay_minutes,
                    "isolation_delay_minutes": isolation_delay_minutes,
                    "clinical_hold_minutes": clinical_hold_minutes,
                }
            )

    return rows


def main() -> None:
    rows = generate_events()
    write_csv(BED_EVENTS_PATH, rows)
    print(f"wrote {len(rows)} bed turnover rows to {BED_EVENTS_PATH}")


if __name__ == "__main__":
    main()
