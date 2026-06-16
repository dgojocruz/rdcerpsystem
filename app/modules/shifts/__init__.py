from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, flash
from ..auth import login_required
import json
from datetime import datetime, date, timedelta

bp = Blueprint('shifts', __name__)

@bp.route('/')
@login_required
def index():
    shifts = g.db.execute("SELECT * FROM shift_definitions WHERE is_active=1 ORDER BY time_in").fetchall()
    templates = g.db.execute("SELECT * FROM schedule_templates ORDER BY template_name").fetchall()
    return render_template('shifts/index.html', shifts=shifts, templates=templates)

@bp.route('/calendar')
@login_required
def calendar():
    year = int(request.args.get('year', date.today().year))
    month = int(request.args.get('month', date.today().month))
    dept_filter = request.args.get('dept', '')
    shifts = g.db.execute("SELECT * FROM shift_definitions WHERE is_active=1").fetchall()
    departments = g.db.execute("SELECT * FROM departments WHERE is_active=1 ORDER BY name").fetchall()
    return render_template('shifts/calendar.html', year=year, month=month,
                           dept_filter=dept_filter, shifts=shifts, departments=departments)

@bp.route('/api/calendar-events')
@login_required
def api_calendar_events():
    start = request.args.get('start', '')
    end = request.args.get('end', '')
    dept_filter = request.args.get('dept', '')
    query = """
        SELECT es.schedule_date, es.is_rest_day, es.schedule_type,
               sd.shift_name, sd.time_in, sd.time_out, sd.color_hex,
               e.last_name, e.first_name, e.id as emp_id
        FROM employee_schedules es
        JOIN employees e ON es.employee_id = e.id
        LEFT JOIN shift_definitions sd ON es.shift_id = sd.id
        LEFT JOIN departments d ON e.department_id = d.id
        WHERE es.schedule_date BETWEEN ? AND ? AND e.status='ACTIVE'
    """
    params = [start[:10] if start else '', end[:10] if end else '']
    if dept_filter:
        query += " AND e.department_id=?"
        params.append(dept_filter)
    schedules = g.db.execute(query, params).fetchall()
    leave_query = """
        SELECT lr.date_from, lr.date_to, lr.leave_type, lr.status,
               e.last_name, e.first_name, e.id as emp_id
        FROM leave_requests lr
        JOIN employees e ON lr.employee_id = e.id
        WHERE lr.status='APPROVED' AND lr.date_from <= ? AND lr.date_to >= ?
    """
    leaves = g.db.execute(leave_query, [end[:10] if end else '', start[:10] if start else '']).fetchall()
    events = []
    for s in schedules:
        color = '#9CA3AF' if s['is_rest_day'] else (s['color_hex'] or '#3B82F6')
        title = 'Rest Day' if s['is_rest_day'] else f"{s['shift_name']} ({s['time_in']}-{s['time_out']})"
        events.append({
            'title': f"{s['last_name']}, {s['first_name'][0]} — {title}",
            'start': s['schedule_date'], 'color': color,
            'extendedProps': {'type': 'shift', 'emp_id': s['emp_id']}
        })
    for lr in leaves:
        d_start = datetime.strptime(lr['date_from'], '%Y-%m-%d')
        d_end = datetime.strptime(lr['date_to'], '%Y-%m-%d')
        events.append({
            'title': f"{lr['last_name']}, {lr['first_name'][0]} — {lr['leave_type']} Leave",
            'start': lr['date_from'],
            'end': (d_end + timedelta(days=1)).strftime('%Y-%m-%d'),
            'color': '#F59E0B',
            'extendedProps': {'type': 'leave', 'emp_id': lr['emp_id']}
        })
    return jsonify(events)

@bp.route('/definitions/add', methods=['POST'])
@login_required
def add_shift():
    f = request.form
    g.db.execute("""INSERT INTO shift_definitions
        (shift_name,time_in,time_out,break_minutes,is_overnight,color_hex)
        VALUES (?,?,?,?,?,?)""",
        (f['shift_name'], f['time_in'], f['time_out'],
         int(f.get('break_minutes',60)), int(f.get('is_overnight',0)),
         f.get('color_hex','#3B82F6')))
    g.db.commit()
    flash('Shift added.', 'success')
    return redirect(url_for('shifts.index'))

@bp.route('/schedules/assign', methods=['POST'])
@login_required
def assign_schedule():
    f = request.form
    emp_ids = request.form.getlist('employee_ids')
    date_from = datetime.strptime(f['date_from'], '%Y-%m-%d')
    date_to = datetime.strptime(f['date_to'], '%Y-%m-%d')
    shift_id = f.get('shift_id') or None
    is_rest = int(f.get('is_rest_day', 0))
    count = 0
    current = date_from
    while current <= date_to:
        ds = current.strftime('%Y-%m-%d')
        for eid in emp_ids:
            g.db.execute("""INSERT INTO employee_schedules
                (employee_id,shift_id,schedule_date,is_rest_day,schedule_type)
                VALUES (?,?,?,?,'REGULAR')
                ON CONFLICT(employee_id,schedule_date) DO UPDATE SET
                shift_id=excluded.shift_id, is_rest_day=excluded.is_rest_day""",
                (eid, shift_id, ds, is_rest))
            count += 1
        current += timedelta(days=1)
    g.db.commit()
    flash(f'{count} schedule entries saved.', 'success')
    return redirect(url_for('shifts.calendar'))

@bp.route('/templates/save', methods=['POST'])
@login_required
def save_template():
    f = request.form
    g.db.execute("""INSERT INTO schedule_templates (template_name,template_type,template_data,applies_to_group)
                   VALUES (?,?,?,?)""",
        (f['template_name'], f['template_type'], f['template_data'], f.get('applies_to_group','')))
    g.db.commit()
    flash('Template saved.', 'success')
    return redirect(url_for('shifts.index'))
