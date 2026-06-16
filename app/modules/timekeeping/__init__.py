from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, flash, session
from datetime import datetime, date, timedelta
from ..auth import login_required

bp = Blueprint('timekeeping', __name__)

def compute_hours(time_in, time_out, break_mins=60):
    if not time_in or not time_out:
        return 0, 0, 0
    try:
        fmt = '%H:%M'
        ti = datetime.strptime(time_in[:5], fmt)
        to = datetime.strptime(time_out[:5], fmt)
        if to < ti:
            to += timedelta(days=1)
        total_mins = max((to - ti).seconds // 60 - break_mins, 0)
        reg_mins = min(total_mins, 480)
        ot_mins = max(total_mins - 480, 0)
        return total_mins / 60, reg_mins / 60, ot_mins / 60
    except:
        return 0, 0, 0

def calc_late(time_in, work_start='08:00'):
    if not time_in:
        return 0
    try:
        ti = datetime.strptime(time_in[:5], '%H:%M')
        ws = datetime.strptime(work_start, '%H:%M')
        return max((ti - ws).seconds // 60, 0) if ti > ws else 0
    except:
        return 0

def log_adjustment(db, att_id, emp_id, work_date, field, old_val, new_val, reason, user_id):
    db.execute("""INSERT INTO attendance_adjustments
        (attendance_id,employee_id,work_date,field_changed,old_value,new_value,reason,adjusted_by)
        VALUES (?,?,?,?,?,?,?,?)""",
        (att_id, emp_id, work_date, field, str(old_val), str(new_val), reason, user_id))
    db.execute("""UPDATE attendance SET adjusted_by=?, adjusted_at=datetime('now'), adjustment_reason=?
        WHERE id=?""", (user_id, reason, att_id))

@bp.route('/')
@login_required
def index():
    period_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    dept_filter = request.args.get('dept', '')
    query = """
        SELECT e.id, e.employee_no, e.last_name, e.first_name, d.name as dept_name,
               a.id as att_id, a.time_in, a.time_out, a.total_hours, a.ot_hours,
               a.late_minutes, a.undertime_minutes, a.is_absent, a.remarks,
               a.source, a.adjustment_reason
        FROM employees e
        LEFT JOIN departments d ON e.department_id=d.id
        LEFT JOIN attendance a ON a.employee_id=e.id AND a.work_date=?
        WHERE e.status='ACTIVE'
    """
    params = [period_date]
    if dept_filter:
        query += " AND e.department_id=?"; params.append(dept_filter)
    query += " ORDER BY e.last_name, e.first_name"
    employees = g.db.execute(query, params).fetchall()
    summary = g.db.execute("""
        SELECT COUNT(DISTINCT e.id) as total,
               SUM(CASE WHEN a.time_in IS NOT NULL AND a.is_absent=0 THEN 1 ELSE 0 END) as present,
               SUM(CASE WHEN a.is_absent=1 THEN 1 ELSE 0 END) as absent,
               SUM(CASE WHEN a.late_minutes > 0 THEN 1 ELSE 0 END) as late,
               SUM(CASE WHEN a.ot_hours > 0 THEN 1 ELSE 0 END) as with_ot
        FROM employees e
        LEFT JOIN attendance a ON a.employee_id=e.id AND a.work_date=?
        WHERE e.status='ACTIVE'
    """, (period_date,)).fetchone()
    departments = g.db.execute("SELECT * FROM departments WHERE is_active=1 ORDER BY name").fetchall()
    return render_template('timekeeping/index.html', employees=employees,
                           period_date=period_date, summary=summary,
                           departments=departments, dept_filter=dept_filter)

@bp.route('/timesheet/<int:emp_id>')
@login_required
def timesheet(emp_id):
    emp = g.db.execute("""SELECT e.*, d.name as dept_name FROM employees e
        LEFT JOIN departments d ON e.department_id=d.id WHERE e.id=?""", (emp_id,)).fetchone()
    if not emp: return redirect(url_for('timekeeping.index'))
    date_from = request.args.get('from', (date.today().replace(day=1)).strftime('%Y-%m-%d'))
    date_to   = request.args.get('to',   date.today().strftime('%Y-%m-%d'))
    records = g.db.execute("""
        SELECT a.*, adj.field_changed, adj.old_value, adj.new_value, adj.reason as adj_reason,
               u.full_name as adj_by_name
        FROM attendance a
        LEFT JOIN attendance_adjustments adj ON adj.attendance_id=a.id
        LEFT JOIN users u ON adj.adjusted_by=u.id
        WHERE a.employee_id=? AND a.work_date BETWEEN ? AND ?
        ORDER BY a.work_date
    """, (emp_id, date_from, date_to)).fetchall()
    totals = g.db.execute("""
        SELECT COUNT(*) as days, SUM(total_hours) as hours,
               SUM(ot_hours) as ot, SUM(late_minutes) as late,
               SUM(CASE WHEN is_absent=1 THEN 1 ELSE 0 END) as absent
        FROM attendance WHERE employee_id=? AND work_date BETWEEN ? AND ?
    """, (emp_id, date_from, date_to)).fetchone()
    return render_template('timekeeping/timesheet.html', emp=emp, records=records,
                           totals=totals, date_from=date_from, date_to=date_to)

@bp.route('/log', methods=['POST'])
@login_required
def log_attendance():
    data = request.json or request.form
    emp_id = data.get('employee_id')
    work_date = data.get('work_date', date.today().strftime('%Y-%m-%d'))
    time_in = data.get('time_in') or None
    time_out = data.get('time_out') or None
    total_h, reg_h, ot_h = compute_hours(time_in, time_out)
    late_mins = calc_late(time_in)
    g.db.execute("""INSERT INTO attendance
        (employee_id,work_date,time_in,time_out,total_hours,regular_hours,ot_hours,late_minutes,source)
        VALUES (?,?,?,?,?,?,?,?,'MANUAL')
        ON CONFLICT(employee_id,work_date) DO UPDATE SET
        time_in=excluded.time_in, time_out=excluded.time_out,
        total_hours=excluded.total_hours, regular_hours=excluded.regular_hours,
        ot_hours=excluded.ot_hours, late_minutes=excluded.late_minutes""",
        (emp_id, work_date, time_in, time_out, total_h, reg_h, ot_h, late_mins))
    g.db.commit()
    if request.is_json:
        return jsonify({'status': 'ok'})
    flash('Attendance logged.', 'success')
    return redirect(url_for('timekeeping.index', date=work_date))

@bp.route('/adjust/<int:att_id>', methods=['POST'])
@login_required
def adjust(att_id):
    """Admin adjustment with mandatory reason and full audit trail."""
    user_id = session['user']['id']
    role = session['user'].get('role', 'staff')
    if role not in ('admin', 'hr'):
        return jsonify({'error': 'Unauthorized'}), 403

    existing = g.db.execute("SELECT * FROM attendance WHERE id=?", (att_id,)).fetchone()
    if not existing:
        flash('Attendance record not found.', 'error')
        return redirect(url_for('timekeeping.index'))

    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Adjustment reason is required.', 'error')
        return redirect(request.referrer or url_for('timekeeping.index'))

    new_time_in  = request.form.get('time_in')  or existing['time_in']
    new_time_out = request.form.get('time_out') or existing['time_out']
    new_ot = request.form.get('ot_hours')
    new_late = request.form.get('late_minutes')

    total_h, reg_h, ot_h = compute_hours(new_time_in, new_time_out)
    if new_ot is not None and new_ot != '':
        ot_h = float(new_ot)
    late_mins = int(new_late) if new_late else calc_late(new_time_in)

    # Log each changed field
    if new_time_in != existing['time_in']:
        log_adjustment(g.db, att_id, existing['employee_id'], existing['work_date'],
                       'time_in', existing['time_in'], new_time_in, reason, user_id)
    if new_time_out != existing['time_out']:
        log_adjustment(g.db, att_id, existing['employee_id'], existing['work_date'],
                       'time_out', existing['time_out'], new_time_out, reason, user_id)

    g.db.execute("""UPDATE attendance SET
        time_in=?, time_out=?, total_hours=?, regular_hours=?, ot_hours=?,
        late_minutes=?, adjusted_by=?, adjusted_at=datetime('now'), adjustment_reason=?
        WHERE id=?""",
        (new_time_in, new_time_out, total_h, reg_h, ot_h, late_mins, user_id, reason, att_id))
    g.db.commit()
    flash('Attendance adjusted and audit trail saved.', 'success')
    ref = request.form.get('redirect_to') or request.referrer or url_for('timekeeping.index')
    return redirect(ref)

@bp.route('/adjust/new/<int:emp_id>/<work_date>', methods=['POST'])
@login_required
def adjust_new(emp_id, work_date):
    """Create or update attendance for a specific employee+date with audit."""
    user_id = session['user']['id']
    role = session['user'].get('role', 'staff')
    if role not in ('admin', 'hr'):
        flash('Insufficient permissions.', 'error')
        return redirect(url_for('timekeeping.index'))
    reason = request.form.get('reason', '').strip()
    if not reason:
        flash('Reason is required.', 'error')
        return redirect(request.referrer or url_for('timekeeping.index'))
    time_in  = request.form.get('time_in') or None
    time_out = request.form.get('time_out') or None
    total_h, reg_h, ot_h = compute_hours(time_in, time_out)
    late_mins = calc_late(time_in)
    existing = g.db.execute("SELECT id FROM attendance WHERE employee_id=? AND work_date=?",
                            (emp_id, work_date)).fetchone()
    if existing:
        log_adjustment(g.db, existing['id'], emp_id, work_date,
                       'time_in+time_out', '—', f'{time_in}→{time_out}', reason, user_id)
        g.db.execute("""UPDATE attendance SET time_in=?,time_out=?,total_hours=?,
            regular_hours=?,ot_hours=?,late_minutes=?,adjustment_reason=?,
            adjusted_by=?,adjusted_at=datetime('now') WHERE id=?""",
            (time_in, time_out, total_h, reg_h, ot_h, late_mins, reason, user_id, existing['id']))
    else:
        g.db.execute("""INSERT INTO attendance
            (employee_id,work_date,time_in,time_out,total_hours,regular_hours,ot_hours,
             late_minutes,adjustment_reason,adjusted_by,adjusted_at,source)
            VALUES (?,?,?,?,?,?,?,?,?,?,datetime('now'),'MANUAL')""",
            (emp_id, work_date, time_in, time_out, total_h, reg_h, ot_h, late_mins, reason, user_id))
    g.db.commit()
    flash('Timesheet entry saved.', 'success')
    return redirect(request.form.get('redirect_to') or url_for('timekeeping.timesheet', emp_id=emp_id))

@bp.route('/adjustments/log')
@login_required
def adjustment_log():
    records = g.db.execute("""
        SELECT aa.*, e.last_name, e.first_name, e.employee_no,
               u.full_name as adj_by_name
        FROM attendance_adjustments aa
        JOIN employees e ON aa.employee_id=e.id
        LEFT JOIN users u ON aa.adjusted_by=u.id
        ORDER BY aa.adjusted_at DESC LIMIT 200
    """).fetchall()
    return render_template('timekeeping/adjustment_log.html', records=records)

@bp.route('/biometric/punch', methods=['POST'])
def biometric_punch():
    data = request.json or {}
    bio_id = data.get('biometric_id')
    punch_dt = data.get('datetime', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    punch_type = data.get('type', 'IN')
    device_id = data.get('device_id', 'DEVICE_001')
    emp = g.db.execute("SELECT id FROM employees WHERE biometric_id=?", (bio_id,)).fetchone()
    emp_id = emp['id'] if emp else None
    g.db.execute("""INSERT INTO biometric_log (biometric_id,employee_id,punch_datetime,punch_type,device_id)
                   VALUES (?,?,?,?,?)""", (bio_id, emp_id, punch_dt, punch_type, device_id))
    g.db.commit()
    return jsonify({'status': 'recorded', 'employee_id': emp_id})

@bp.route('/biometric/process', methods=['POST'])
@login_required
def process_biometric():
    logs = g.db.execute("""SELECT bl.*, e.id as emp_id FROM biometric_log bl
        LEFT JOIN employees e ON e.biometric_id=bl.biometric_id
        WHERE bl.processed=0 ORDER BY bl.punch_datetime""").fetchall()
    processed = 0
    for log in logs:
        if not log['emp_id']:
            continue
        dt = datetime.strptime(log['punch_datetime'][:16], '%Y-%m-%d %H:%M')
        work_date = dt.strftime('%Y-%m-%d')
        time_str = dt.strftime('%H:%M')
        existing = g.db.execute("SELECT * FROM attendance WHERE employee_id=? AND work_date=?",
                                (log['emp_id'], work_date)).fetchone()
        if not existing:
            g.db.execute("""INSERT OR IGNORE INTO attendance
                (employee_id,work_date,time_in,source) VALUES (?,?,?,'BIOMETRIC')""",
                (log['emp_id'], work_date, time_str))
        elif not existing['time_out'] and log['punch_type'] == 'OUT':
            total_h, reg_h, ot_h = compute_hours(existing['time_in'], time_str)
            g.db.execute("""UPDATE attendance SET time_out=?,total_hours=?,regular_hours=?,ot_hours=?
                WHERE employee_id=? AND work_date=?""",
                (time_str, total_h, reg_h, ot_h, log['emp_id'], work_date))
        g.db.execute("UPDATE biometric_log SET processed=1 WHERE id=?", (log['id'],))
        processed += 1
    g.db.commit()
    return jsonify({'processed': processed})

@bp.route('/period')
@login_required
def period_view():
    date_from = request.args.get('from', '')
    date_to   = request.args.get('to', '')
    if not date_from or not date_to:
        return render_template('timekeeping/period.html', records=[], date_from='', date_to='')
    records = g.db.execute("""
        SELECT e.employee_no, e.last_name, e.first_name, e.payroll_group,
               COUNT(a.id) as days_present, SUM(a.late_minutes) as total_late,
               SUM(a.undertime_minutes) as total_ut, SUM(a.ot_hours) as total_ot,
               SUM(a.nd_hours) as total_nd,
               SUM(CASE WHEN a.is_absent=1 THEN 1 ELSE 0 END) as days_absent
        FROM employees e
        LEFT JOIN attendance a ON a.employee_id=e.id AND a.work_date BETWEEN ? AND ?
        WHERE e.status='ACTIVE' GROUP BY e.id ORDER BY e.last_name
    """, (date_from, date_to)).fetchall()
    return render_template('timekeeping/period.html', records=records,
                           date_from=date_from, date_to=date_to)
