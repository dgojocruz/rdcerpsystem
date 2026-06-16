"""
RHODECO ERP — Import Att.log report (May 4-11, 2026)
Parses raw ZKTeco biometric punches and creates attendance records.
"""
import sqlite3, openpyxl, re
from datetime import datetime, date, timedelta

DB   = 'clients/rhodeco/data/erp.db'
XLSX = 'attendance_may_1_11.xlsx'

SHIFT_IN_HOUR  = 8    # 08:00 standard shift
GRACE_MINS     = 5    # late after 08:05
LUNCH_START    = 12
LUNCH_END      = 13
OVERNIGHT_CUTOFF = 3  # times before 03:00 are treated as previous day's out

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

wb   = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
ws   = wb['Att.log report']
rows = list(ws.iter_rows(values_only=True))

# Day column mapping from row 4
day_cols = {}
for col_idx, val in enumerate(rows[3]):
    if isinstance(val, int) and 1 <= val <= 31:
        day_cols[col_idx] = val

# ── Helpers ──────────────────────────────────────────────────────────────────
def parse_times(cell_val):
    """Extract all HH:MM patterns from a cell."""
    if not cell_val:
        return []
    return re.findall(r'\d{2}:\d{2}', str(cell_val))

def to_mins(t):
    h, m = map(int, t.split(':'))
    return h * 60 + m

def clean_punches(times):
    """
    Deduplicate punches within 1 minute of each other,
    remove lunch mid-punches, keep first and last meaningful times.
    """
    if not times:
        return []
    # Convert to minutes
    mins = [to_mins(t) for t in times]
    # Deduplicate (keep unique within 2-minute window)
    deduped = [mins[0]]
    for m in mins[1:]:
        if abs(m - deduped[-1]) > 2:
            deduped.append(m)
    return deduped

def get_time_in_out(times):
    """From a list of punch times, determine the best time_in and time_out."""
    if not times:
        return None, None
    cleaned = clean_punches(times)
    if not cleaned:
        return None, None

    # Filter out overnight/early morning artifact times (before 3am = previous shift)
    day_punches = [m for m in cleaned if m >= OVERNIGHT_CUTOFF * 60]
    if not day_punches:
        return None, None

    time_in_mins  = min(day_punches)
    time_out_mins = max(day_punches)

    # If in == out, only one punch — treat as time_in only
    if time_in_mins == time_out_mins:
        return f"{time_in_mins//60:02d}:{time_in_mins%60:02d}", None

    time_in  = f"{time_in_mins//60:02d}:{time_in_mins%60:02d}"
    time_out = f"{time_out_mins//60:02d}:{time_out_mins%60:02d}"
    return time_in, time_out

def calc_hours(time_in, time_out):
    """Calculate total hours, OT, late, ND."""
    if not time_in or not time_out:
        return 0, 0, 0, 0, 0
    in_m  = to_mins(time_in)
    out_m = to_mins(time_out)
    if out_m <= in_m:
        out_m += 24 * 60  # overnight

    total_mins = out_m - in_m

    # Deduct lunch (30 mins if worked through lunch)
    lunch_start = LUNCH_START * 60
    lunch_end   = LUNCH_END * 60
    if in_m < lunch_start and out_m > lunch_end:
        total_mins -= 30  # deduct lunch

    total_hrs = round(total_mins / 60, 2)
    regular   = min(8.0, total_hrs)
    ot        = max(0, round(total_hrs - 8.0, 2))

    # Late minutes
    late = max(0, in_m - (SHIFT_IN_HOUR * 60 + GRACE_MINS))

    # Night differential (22:00-06:00)
    nd = 0
    if out_m > 22 * 60:
        nd = round((out_m - 22 * 60) / 60, 2)

    return total_hrs, regular, ot, late, nd

def find_employee(bio_id, name):
    """Find employee by biometric ID first, then by name."""
    # Try biometric ID
    emp = conn.execute(
        "SELECT id, last_name, first_name FROM employees WHERE biometric_id=?",
        (str(bio_id),)
    ).fetchone()
    if emp:
        return emp

    # Try name matching
    if ',' in name:
        parts = name.split(',', 1)
        last  = parts[0].strip().upper()
        first = parts[1].strip().upper()
    else:
        parts = name.strip().split()
        last  = parts[0].upper() if parts else ''
        first = parts[1].upper() if len(parts) > 1 else ''

    emp = conn.execute("""SELECT id, last_name, first_name FROM employees
        WHERE UPPER(last_name)=? AND UPPER(SUBSTR(first_name,1,4))=SUBSTR(?,1,4)""",
        (last, first)
    ).fetchone()
    if emp:
        return emp

    # Last name only
    emp = conn.execute(
        "SELECT id, last_name, first_name FROM employees WHERE UPPER(last_name)=?",
        (last,)
    ).fetchone()
    return emp

# ── Parse and import ─────────────────────────────────────────────────────────
inserted = updated = not_found = 0

i = 4
while i < len(rows):
    row = rows[i]
    if row[0] != 'ID:':
        i += 1
        continue

    bio_id   = str(row[2]).strip() if row[2] else ''
    name     = str(row[10]).strip() if row[10] else ''
    punch_row = rows[i+1] if i+1 < len(rows) else None
    i += 2

    if not name or name in ['', 'None']:
        continue

    emp = find_employee(bio_id, name)
    if not emp:
        print(f"  NOT FOUND: {name} (Bio:{bio_id})")
        not_found += 1
        continue

    emp_id = emp['id']

    # Update biometric ID on employee record if not set
    if bio_id:
        conn.execute(
            "UPDATE employees SET biometric_id=? WHERE id=? AND (biometric_id IS NULL OR biometric_id='')",
            (bio_id, emp_id)
        )

    # Process each day
    day_records = {}
    if punch_row:
        for col_idx, day_num in day_cols.items():
            times = parse_times(punch_row[col_idx])
            if times:
                day_records[day_num] = times

    emp_name = f"{emp['last_name']}, {emp['first_name']}"
    print(f"\n  Processing: {emp_name} (Bio:{bio_id}, EMP ID:{emp_id})")

    for day_num, times in day_records.items():
        work_date = date(2026, 5, day_num)
        time_in, time_out = get_time_in_out(times)
        total, regular, ot, late, nd = calc_hours(time_in, time_out)
        is_rest = 1 if work_date.weekday() == 6 else 0  # Sunday

        print(f"    May {day_num}: IN={time_in or '-'} OUT={time_out or '-'} | {total}h | OT:{ot}h | Late:{late}m | ND:{nd}h")

        try:
            conn.execute("""INSERT OR REPLACE INTO attendance
                (employee_id, work_date, time_in, time_out,
                 total_hours, regular_hours, ot_hours, nd_hours,
                 late_minutes, is_absent, is_rest_day,
                 source, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?,
                        'BIOMETRIC', datetime('now'))""",
                (emp_id, work_date.isoformat(),
                 time_in, time_out,
                 total, regular, ot, nd,
                 late, is_rest))
            inserted += 1
        except Exception as e:
            print(f"    ERROR: {e}")

    # Mark absent days (May 4-11 with no punches, excluding Sunday)
    all_days = set(range(4, 12))
    punched_days = set(day_records.keys())
    absent_days  = all_days - punched_days
    for day_num in absent_days:
        work_date = date(2026, 5, day_num)
        is_rest = 1 if work_date.weekday() == 6 else 0
        try:
            conn.execute("""INSERT OR IGNORE INTO attendance
                (employee_id, work_date, is_absent, is_rest_day, source, created_at)
                VALUES (?, ?, ?, ?, 'BIOMETRIC', datetime('now'))""",
                (emp_id, work_date.isoformat(), 0 if is_rest else 1, is_rest))
        except:
            pass

conn.commit()
conn.close()
print(f"\n{'='*50}")
print(f"Done! {inserted} records inserted, {not_found} employees not found.")
print(f"Go to Timekeeping and browse May 4-11, 2026 to verify.")
