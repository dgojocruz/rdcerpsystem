import sqlite3, os
from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS company_settings (
    id INTEGER PRIMARY KEY,
    company_name TEXT NOT NULL DEFAULT 'My Company',
    trade_name TEXT, address TEXT, city TEXT, province TEXT,
    zip_code TEXT, phone TEXT, email TEXT, website TEXT,
    tin TEXT, sss_employer_no TEXT, philhealth_employer_no TEXT,
    pagibig_employer_no TEXT, logo_path TEXT,
    payroll_type TEXT DEFAULT 'SEMI_MONTHLY',
    work_days_per_week INTEGER DEFAULT 6,
    work_hours_per_day INTEGER DEFAULT 8,
    currency TEXT DEFAULT 'PHP',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS modules (
    id INTEGER PRIMARY KEY, module_key TEXT UNIQUE NOT NULL,
    module_name TEXT NOT NULL, is_enabled INTEGER DEFAULT 1,
    sort_order INTEGER DEFAULT 0, icon TEXT DEFAULT 'ti-puzzle', url_prefix TEXT
);
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL, full_name TEXT, email TEXT,
    role TEXT DEFAULT 'staff', is_active INTEGER DEFAULT 1,
    last_login TEXT, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY, code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL, dept_type TEXT DEFAULT 'IND', is_active INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY, employee_no TEXT UNIQUE NOT NULL,
    last_name TEXT NOT NULL, first_name TEXT NOT NULL, middle_name TEXT, suffix TEXT,
    date_of_birth TEXT, gender TEXT, civil_status TEXT, address TEXT, city TEXT,
    phone TEXT, email TEXT, department_id INTEGER REFERENCES departments(id),
    position_title TEXT, dept_type TEXT DEFAULT 'IND',
    manager_id INTEGER REFERENCES employees(id),
    employment_type TEXT DEFAULT 'REGULAR',
    payroll_group TEXT DEFAULT 'MONTHLY', payment_method TEXT DEFAULT 'ATM',
    bank_name TEXT, bank_account_no TEXT,
    date_hired TEXT, date_regularized TEXT, date_resigned TEXT,
    status TEXT DEFAULT 'ACTIVE',
    daily_rate REAL DEFAULT 0, hourly_rate REAL DEFAULT 0, monthly_rate REAL DEFAULT 0,
    tax_type TEXT DEFAULT 'AWE', tin TEXT, sss_no TEXT, philhealth_no TEXT, pagibig_no TEXT,
    allowance_amount REAL DEFAULT 0, photo_path TEXT, biometric_id TEXT, notes TEXT,
    created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS custom_field_definitions (
    id INTEGER PRIMARY KEY, field_key TEXT UNIQUE NOT NULL, field_label TEXT NOT NULL,
    field_type TEXT NOT NULL DEFAULT 'TEXT', field_options TEXT,
    applies_to TEXT DEFAULT 'employee', is_required INTEGER DEFAULT 0,
    sort_order INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS custom_field_values (
    id INTEGER PRIMARY KEY, entity_type TEXT NOT NULL, entity_id INTEGER NOT NULL,
    field_id INTEGER REFERENCES custom_field_definitions(id), field_value TEXT,
    UNIQUE(entity_type, entity_id, field_id)
);
CREATE TABLE IF NOT EXISTS lifecycle_events (
    id INTEGER PRIMARY KEY, employee_id INTEGER REFERENCES employees(id),
    event_type TEXT NOT NULL, status TEXT DEFAULT 'PENDING',
    checklist TEXT, initiated_by INTEGER REFERENCES users(id),
    target_date TEXT, completed_at TEXT, notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS shift_definitions (
    id INTEGER PRIMARY KEY, shift_name TEXT NOT NULL, time_in TEXT NOT NULL,
    time_out TEXT NOT NULL, break_minutes INTEGER DEFAULT 60,
    is_overnight INTEGER DEFAULT 0, color_hex TEXT DEFAULT '#3B82F6',
    is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS employee_schedules (
    id INTEGER PRIMARY KEY, employee_id INTEGER REFERENCES employees(id),
    shift_id INTEGER REFERENCES shift_definitions(id),
    schedule_date TEXT NOT NULL, week_number INTEGER,
    schedule_type TEXT DEFAULT 'REGULAR', is_rest_day INTEGER DEFAULT 0, notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(employee_id, schedule_date)
);
CREATE TABLE IF NOT EXISTS schedule_templates (
    id INTEGER PRIMARY KEY, template_name TEXT NOT NULL, template_type TEXT NOT NULL,
    template_data TEXT NOT NULL, applies_to_group TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS pay_periods (
    id INTEGER PRIMARY KEY, period_type TEXT NOT NULL, period_label TEXT NOT NULL,
    date_from TEXT NOT NULL, date_to TEXT NOT NULL,
    payroll_group TEXT DEFAULT 'ALL', status TEXT DEFAULT 'OPEN',
    processed_by INTEGER REFERENCES users(id), processed_at TEXT,
    approved_by INTEGER REFERENCES users(id), approved_at TEXT, released_at TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY, employee_id INTEGER REFERENCES employees(id),
    work_date TEXT NOT NULL, time_in TEXT, time_out TEXT,
    total_hours REAL DEFAULT 0, regular_hours REAL DEFAULT 0,
    ot_hours REAL DEFAULT 0, nd_hours REAL DEFAULT 0,
    late_minutes INTEGER DEFAULT 0, undertime_minutes INTEGER DEFAULT 0,
    is_absent INTEGER DEFAULT 0, is_holiday INTEGER DEFAULT 0,
    holiday_type TEXT, is_rest_day INTEGER DEFAULT 0,
    remarks TEXT, adjusted_by INTEGER REFERENCES users(id),
    adjusted_at TEXT, adjustment_reason TEXT,
    source TEXT DEFAULT 'MANUAL', created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(employee_id, work_date)
);
CREATE TABLE IF NOT EXISTS biometric_log (
    id INTEGER PRIMARY KEY, biometric_id TEXT NOT NULL,
    employee_id INTEGER REFERENCES employees(id),
    punch_datetime TEXT NOT NULL, punch_type TEXT DEFAULT 'IN',
    device_id TEXT, processed INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS payroll (
    id INTEGER PRIMARY KEY, pay_period_id INTEGER REFERENCES pay_periods(id),
    employee_id INTEGER REFERENCES employees(id), payroll_group TEXT,
    total_hours REAL DEFAULT 0, regular_amount REAL DEFAULT 0,
    late_amount REAL DEFAULT 0, undertime_amount REAL DEFAULT 0,
    vl_amount REAL DEFAULT 0, sl_amount REAL DEFAULT 0, el_amount REAL DEFAULT 0,
    basic_salary REAL DEFAULT 0, ot_hours REAL DEFAULT 0, ot_amount REAL DEFAULT 0,
    nd_hours REAL DEFAULT 0, nd_amount REAL DEFAULT 0,
    special_holiday_hours REAL DEFAULT 0, special_holiday_amount REAL DEFAULT 0,
    legal_holiday_hours REAL DEFAULT 0, legal_holiday_amount REAL DEFAULT 0,
    allowance_amount REAL DEFAULT 0, thirteenth_month REAL DEFAULT 0,
    gross_salary REAL DEFAULT 0,
    sss_employee REAL DEFAULT 0, sss_wisp REAL DEFAULT 0,
    philhealth_employee REAL DEFAULT 0, pagibig_employee REAL DEFAULT 0,
    withholding_tax REAL DEFAULT 0,
    sss_loan REAL DEFAULT 0, pagibig_loan REAL DEFAULT 0,
    personal_loan REAL DEFAULT 0, cash_advance REAL DEFAULT 0,
    house_rent REAL DEFAULT 0, ar_water REAL DEFAULT 0,
    other_deductions REAL DEFAULT 0, total_deductions REAL DEFAULT 0,
    net_pay REAL DEFAULT 0,
    sss_employer REAL DEFAULT 0, philhealth_employer REAL DEFAULT 0,
    pagibig_employer REAL DEFAULT 0,
    status TEXT DEFAULT 'DRAFT', computed_at TEXT,
    created_at TEXT DEFAULT (datetime('now')), updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(pay_period_id, employee_id)
);
CREATE TABLE IF NOT EXISTS employee_loans (
    id INTEGER PRIMARY KEY, employee_id INTEGER REFERENCES employees(id),
    loan_category TEXT NOT NULL DEFAULT 'PERSONAL',
    loan_type TEXT NOT NULL, principal_amount REAL NOT NULL,
    outstanding_balance REAL NOT NULL, monthly_amortization REAL NOT NULL,
    total_paid REAL DEFAULT 0, start_date TEXT, end_date TEXT,
    status TEXT DEFAULT 'ACTIVE', notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS leave_credits (
    id INTEGER PRIMARY KEY, employee_id INTEGER REFERENCES employees(id),
    year INTEGER NOT NULL, leave_type TEXT NOT NULL,
    allocated_days REAL DEFAULT 0, used_days REAL DEFAULT 0, balance_days REAL DEFAULT 0,
    UNIQUE(employee_id, year, leave_type)
);
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY, employee_id INTEGER REFERENCES employees(id),
    leave_type TEXT NOT NULL, date_from TEXT NOT NULL, date_to TEXT NOT NULL,
    num_days REAL NOT NULL, reason TEXT, status TEXT DEFAULT 'PENDING',
    approved_by INTEGER REFERENCES users(id), approved_at TEXT, remarks TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS payroll_config (
    id INTEGER PRIMARY KEY, config_key TEXT UNIQUE NOT NULL,
    config_label TEXT NOT NULL, config_value TEXT NOT NULL,
    config_type TEXT DEFAULT 'DECIMAL', config_group TEXT DEFAULT 'GENERAL',
    notes TEXT, updated_by INTEGER REFERENCES users(id),
    updated_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS holidays (
    id INTEGER PRIMARY KEY, holiday_date TEXT UNIQUE NOT NULL,
    holiday_name TEXT NOT NULL, holiday_type TEXT NOT NULL,
    is_recurring INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS dashboard_widgets (
    id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id),
    widget_type TEXT NOT NULL, widget_config TEXT,
    position_col INTEGER DEFAULT 0, position_row INTEGER DEFAULT 0,
    width_units INTEGER DEFAULT 1, is_visible INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY, user_id INTEGER REFERENCES users(id),
    action TEXT NOT NULL, module TEXT, table_name TEXT, record_id INTEGER,
    before_value TEXT, after_value TEXT, change_reason TEXT,
    ip_address TEXT, created_at TEXT DEFAULT (datetime('now'))
);
"""

DEFAULT_DATA = [
("company_settings","INSERT OR IGNORE INTO company_settings (id,company_name,trade_name,address,city,province) VALUES (1,'RHODECO RUBBER PROCESSING SERVICES INC.','RHODECO','Quezon City','Quezon City','NCR')"),
("modules","""INSERT OR IGNORE INTO modules (module_key,module_name,is_enabled,sort_order,icon,url_prefix) VALUES
('dashboard','Dashboard',1,1,'ti-layout-dashboard','/'),
('employees','Employees',1,2,'ti-users','/employees'),
('timekeeping','Timekeeping',1,3,'ti-fingerprint','/timekeeping'),
('payroll','Payroll',1,4,'ti-cash','/payroll'),
('loans','Loans',1,5,'ti-credit-card','/loans'),
('shifts','Shift & Leave',1,6,'ti-calendar-week','/shifts'),
('reports','Reports',1,7,'ti-file-certificate','/reports'),
('inventory','Inventory',0,8,'ti-package','/inventory'),
('accounting','Accounting',0,9,'ti-calculator','/accounting'),
('settings','Settings',1,10,'ti-settings','/settings')"""),
("departments","""INSERT OR IGNORE INTO departments (code,name,dept_type) VALUES
('ACCTG','Accounting','ADM'),('PURCH','Purchasing','ADM'),
('SALES','Sales & Marketing','ADM'),('ADMIN','Administration','ADM'),
('HR','Human Resources','ADM'),('MAINT','Maintenance','IND'),
('COMP','Compounding','DL'),('VULC','Vulcanizing','DL'),
('TRIM','Trimming','DL'),('QA','QA / Laboratory','DL'),
('WH','Warehouse','IND'),('LOG','Logistics','IND')"""),
("shift_definitions","""INSERT OR IGNORE INTO shift_definitions (id,shift_name,time_in,time_out,break_minutes,color_hex) VALUES
(1,'Morning Shift','06:00','14:00',60,'#3B82F6'),
(2,'Regular Shift','08:00','17:00',60,'#10B981'),
(3,'Afternoon Shift','14:00','22:00',60,'#F59E0B'),
(4,'Night Shift','22:00','06:00',60,'#8B5CF6')"""),
("payroll_config","""INSERT OR IGNORE INTO payroll_config (config_key,config_label,config_value,config_type,config_group,notes) VALUES
('NCR_MIN_WAGE','NCR Daily Minimum Wage','645','DECIMAL','GENERAL','As of 2025'),
('SSS_EE_RATE','SSS Employee Rate','0.045','PERCENT','SSS','4.5%'),
('SSS_ER_RATE','SSS Employer Rate','0.085','PERCENT','SSS','8.5%'),
('SSS_MAX_MSC','SSS Max Monthly Salary Credit','20250','DECIMAL','SSS','2025 table'),
('PHIC_RATE','PhilHealth Total Rate','0.05','PERCENT','PHILHEALTH','5% split equally'),
('PHIC_MAX_SAL','PhilHealth Max Salary Basis','100000','DECIMAL','PHILHEALTH',''),
('PHIC_MIN_CON','PhilHealth Min Contribution','500','DECIMAL','PHILHEALTH',''),
('HDMF_EE_RATE','Pag-IBIG Employee Rate','0.02','PERCENT','PAGIBIG','2%'),
('HDMF_ER_RATE','Pag-IBIG Employer Rate','0.02','PERCENT','PAGIBIG','2%'),
('HDMF_MAX_SAL','Pag-IBIG Max Fund Salary','10000','DECIMAL','PAGIBIG',''),
('HDMF_MAX_CON','Pag-IBIG Max Contribution','200','DECIMAL','PAGIBIG','Per month'),
('OT_RATE','Overtime Rate Multiplier','1.25','DECIMAL','RATES','125%'),
('ND_RATE','Night Differential Rate','0.10','DECIMAL','RATES','10% additional'),
('REST_DAY_RATE','Rest Day Pay Rate','1.30','DECIMAL','RATES','130%'),
('SPECIAL_HOL_RATE','Special Holiday Rate','1.30','DECIMAL','RATES','130%'),
('LEGAL_HOL_RATE','Legal Holiday Rate','2.00','DECIMAL','RATES','200%'),
('OT_HOL_RATE','OT on Legal Holiday Rate','2.60','DECIMAL','RATES','260%'),
('13TH_MONTH_ENABLED','Enable 13th Month Computation','1','BOOL','GENERAL',''),
('BACKPAY_ENABLED','Enable Backpay Computation','1','BOOL','GENERAL','')"""),
("holidays","""INSERT OR IGNORE INTO holidays (holiday_date,holiday_name,holiday_type) VALUES
('2026-01-01','New Year Day','LEGAL'),
('2026-04-02','Maundy Thursday','LEGAL'),
('2026-04-03','Good Friday','LEGAL'),
('2026-04-04','Black Saturday','SPECIAL'),
('2026-04-09','Araw ng Kagitingan','LEGAL'),
('2026-05-01','Labor Day','LEGAL'),
('2026-06-12','Independence Day','LEGAL'),
('2026-08-31','National Heroes Day','LEGAL'),
('2026-11-01','All Saints Day','SPECIAL'),
('2026-11-02','All Souls Day','SPECIAL'),
('2026-11-30','Bonifacio Day','LEGAL'),
('2026-12-08','Feast Immaculate Conception','SPECIAL'),
('2026-12-24','Christmas Eve','SPECIAL'),
('2026-12-25','Christmas Day','LEGAL'),
('2026-12-30','Rizal Day','LEGAL'),
('2026-12-31','New Year Eve','SPECIAL')"""),
]

def init_db(app):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    for label, sql in DEFAULT_DATA:
        try:
            conn.executescript(sql)
        except Exception as e:
            print(f"Seed {label}: {e}")
    conn.commit()
    h = generate_password_hash('admin123')
    existing = conn.execute("SELECT id FROM users WHERE username='admin'").fetchone()
    if existing:
        conn.execute("UPDATE users SET password_hash=? WHERE username='admin'", (h,))
    else:
        conn.execute("INSERT INTO users (username,password_hash,full_name,role) VALUES ('admin',?,'System Administrator','admin')", (h,))
    conn.commit()
    conn.close()
