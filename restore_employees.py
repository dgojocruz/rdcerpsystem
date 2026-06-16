import sqlite3
import openpyxl

wb = openpyxl.load_workbook('payroll_MAY_PAY_OUT.xlsx', read_only=True, data_only=True)
ws = wb['Payroll Register']
rows = list(ws.iter_rows(values_only=True))

conn = sqlite3.connect('clients/rhodeco/data/erp.db')

DEPT_MAP = {
    'Accounting': 'ACCTG', 'Purchasing': 'PURCH', 'Sales & Marketing': 'SALES',
    'Administration': 'ADMIN', 'Human Resources': 'HR', 'Maintenance': 'MAINT',
    'Compounding': 'COMP', 'Vulcanizing': 'VULC', 'Trimming': 'TRIM',
    'QA / Laboratory': 'QA', 'Warehouse': 'WH', 'Logistics': 'LOG'
}

inserted = 0
skipped = 0

for row in rows[3:]:
    if not row[0] or not str(row[0]).startswith('EMP'):
        continue

    emp_no = str(row[0]).strip()
    full_name = str(row[1]).strip()
    dept_name = str(row[2]).strip() if row[2] else ''
    group = str(row[3]).strip() if row[3] else 'WEEKLY'
    daily_rate = float(row[4]) if row[4] else 695.0

    # Split name (format: LAST, FIRST)
    if ',' in full_name:
        parts = full_name.split(',', 1)
        last_name = parts[0].strip()
        first_name = parts[1].strip()
    else:
        last_name = full_name
        first_name = ''

    # Get department ID
    dept_code = DEPT_MAP.get(dept_name, '')
    dept_id = None
    if dept_code:
        d = conn.execute("SELECT id FROM departments WHERE code=?", (dept_code,)).fetchone()
        if d:
            dept_id = d[0]

    # Check if already exists
    exists = conn.execute("SELECT id FROM employees WHERE employee_no=?", (emp_no,)).fetchone()
    if exists:
        skipped += 1
        continue

    conn.execute("""INSERT INTO employees
        (employee_no, last_name, first_name, department_id, position_title,
         payroll_group, daily_rate, hourly_rate, monthly_rate, status,
         employment_type, payment_method, tax_type)
        VALUES (?,?,?,?,?,?,?,?,?,'ACTIVE','REGULAR','ATM','AWE')""",
        (emp_no, last_name, first_name, dept_id, dept_name,
         group, daily_rate, round(daily_rate/8, 4), round(daily_rate*26, 2)))

    # Get the new employee ID
    emp_id = conn.execute("SELECT id FROM employees WHERE employee_no=?", (emp_no,)).fetchone()[0]

    # Add leave credits
    for lt, days in [('VL', 5), ('SL', 5), ('EL', 3)]:
        conn.execute("""INSERT OR IGNORE INTO leave_credits
            (employee_id, year, leave_type, allocated_days, used_days, balance_days)
            VALUES (?, '2026', ?, ?, 0, ?)""", (emp_id, lt, days, days))

    inserted += 1
    print(f"  OK: {emp_no} - {last_name}, {first_name}")

conn.commit()
conn.close()
print(f"\nDone! {inserted} inserted, {skipped} skipped.")
