from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, flash, session
from ..auth import login_required
import json

bp = Blueprint('dashboard', __name__)

WIDGET_REGISTRY = {
    'stat_headcount':      {'label': 'Total Employees',        'size': '1x1', 'icon': 'ti-users',          'color': 'blue'},
    'stat_pending_leave':  {'label': 'Pending Leave Requests', 'size': '1x1', 'icon': 'ti-calendar-off',   'color': 'amber'},
    'stat_payroll_last':   {'label': 'Last Payroll Net Pay',   'size': '1x1', 'icon': 'ti-cash',           'color': 'green'},
    'stat_today_absent':   {'label': 'Absent Today',           'size': '1x1', 'icon': 'ti-user-off',       'color': 'red'},
    'stat_loan_balance':   {'label': 'Total Loan Balance',     'size': '1x1', 'icon': 'ti-credit-card',    'color': 'purple'},
    'chart_dept_headcount':{'label': 'Headcount by Department','size': '2x2', 'icon': 'ti-chart-bar',      'color': 'blue'},
    'chart_payroll_trend': {'label': 'Payroll Trend (6mo)',    'size': '2x2', 'icon': 'ti-chart-line',     'color': 'green'},
    'table_recent_payroll':{'label': 'Recent Payroll Runs',    'size': '2x2', 'icon': 'ti-table',          'color': 'gray'},
    'list_holidays':       {'label': 'Upcoming Holidays',      'size': '2x1', 'icon': 'ti-calendar-event', 'color': 'amber'},
    'list_pending_leaves': {'label': 'Pending Leave Requests', 'size': '2x1', 'icon': 'ti-clock',         'color': 'red'},
    'list_recent_hires':   {'label': 'Recent Hires',           'size': '2x1', 'icon': 'ti-user-plus',      'color': 'green'},
}

def fetch_widget_data(widget_type, db):
    today = db.execute("SELECT date('now')").fetchone()[0]
    if widget_type == 'stat_headcount':
        val = db.execute("SELECT COUNT(*) FROM employees WHERE status='ACTIVE'").fetchone()[0]
        sub = db.execute("SELECT COUNT(*) FROM departments WHERE is_active=1").fetchone()[0]
        return {'value': val, 'sub': f'{sub} departments'}
    if widget_type == 'stat_pending_leave':
        val = db.execute("SELECT COUNT(*) FROM leave_requests WHERE status='PENDING'").fetchone()[0]
        return {'value': val, 'sub': 'awaiting approval'}
    if widget_type == 'stat_payroll_last':
        row = db.execute("SELECT SUM(net_pay) as net, period_label FROM payroll pr JOIN pay_periods pp ON pr.pay_period_id=pp.id ORDER BY pp.date_from DESC LIMIT 1").fetchone()
        val = f"₱{row['net']:,.0f}" if row and row['net'] else '—'
        sub = row['period_label'] if row and row['period_label'] else 'No payroll yet'
        return {'value': val, 'sub': sub}
    if widget_type == 'stat_today_absent':
        val = db.execute("SELECT COUNT(*) FROM attendance WHERE work_date=? AND is_absent=1", (today,)).fetchone()[0]
        return {'value': val, 'sub': f'as of {today}'}
    if widget_type == 'stat_loan_balance':
        val = db.execute("SELECT COALESCE(SUM(outstanding_balance),0) FROM employee_loans WHERE status='ACTIVE'").fetchone()[0]
        return {'value': f'₱{val:,.0f}', 'sub': 'active loans'}
    if widget_type == 'chart_dept_headcount':
        rows = db.execute("""SELECT d.name, COUNT(e.id) as count FROM departments d
            LEFT JOIN employees e ON e.department_id=d.id AND e.status='ACTIVE'
            WHERE d.is_active=1 GROUP BY d.id ORDER BY count DESC""").fetchall()
        return {'labels': [r['name'] for r in rows], 'values': [r['count'] for r in rows]}
    if widget_type == 'chart_payroll_trend':
        rows = db.execute("""SELECT pp.period_label, SUM(pr.net_pay) as net
            FROM pay_periods pp LEFT JOIN payroll pr ON pp.id=pr.pay_period_id
            GROUP BY pp.id ORDER BY pp.date_from DESC LIMIT 6""").fetchall()
        rows = list(reversed(rows))
        return {'labels': [r['period_label'] for r in rows], 'values': [r['net'] or 0 for r in rows]}
    if widget_type == 'table_recent_payroll':
        rows = db.execute("""SELECT pp.period_label, pp.status, COUNT(pr.id) as cnt, SUM(pr.net_pay) as net
            FROM pay_periods pp LEFT JOIN payroll pr ON pp.id=pr.pay_period_id
            GROUP BY pp.id ORDER BY pp.date_from DESC LIMIT 5""").fetchall()
        return {'rows': [dict(r) for r in rows]}
    if widget_type == 'list_holidays':
        rows = db.execute("SELECT holiday_date, holiday_name, holiday_type FROM holidays WHERE holiday_date >= ? ORDER BY holiday_date LIMIT 6", (today,)).fetchall()
        return {'rows': [dict(r) for r in rows]}
    if widget_type == 'list_pending_leaves':
        rows = db.execute("""SELECT e.last_name, e.first_name, lr.leave_type, lr.date_from, lr.num_days
            FROM leave_requests lr JOIN employees e ON lr.employee_id=e.id
            WHERE lr.status='PENDING' ORDER BY lr.created_at DESC LIMIT 6""").fetchall()
        return {'rows': [dict(r) for r in rows]}
    if widget_type == 'list_recent_hires':
        rows = db.execute("""SELECT employee_no, last_name, first_name, position_title, date_hired
            FROM employees WHERE status='ACTIVE' ORDER BY date_hired DESC LIMIT 6""").fetchall()
        return {'rows': [dict(r) for r in rows]}
    return {}

@bp.route('/')
@login_required
def index():
    user_id = session['user']['id']
    widgets = g.db.execute("""SELECT * FROM dashboard_widgets WHERE user_id=? AND is_visible=1
        ORDER BY position_y, position_x""", (user_id,)).fetchall()
    widget_data = {}
    for w in widgets:
        try:
            widget_data[w['id']] = fetch_widget_data(w['widget_type'], g.db)
        except:
            widget_data[w['id']] = {}
    return render_template('dashboard/index.html',
        widgets=widgets, widget_data=widget_data,
        widget_registry=WIDGET_REGISTRY)

@bp.route('/api/widget-data/<widget_type>')
@login_required
def widget_data_api(widget_type):
    try:
        data = fetch_widget_data(widget_type, g.db)
        return jsonify({'ok': True, 'data': data})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 400

@bp.route('/widgets/save', methods=['POST'])
@login_required
def save_widgets():
    user_id = session['user']['id']
    layout = request.json.get('layout', [])
    for item in layout:
        g.db.execute("""UPDATE dashboard_widgets SET position_x=?, position_y=?, width=?, height=?
            WHERE id=? AND user_id=?""",
            (item.get('x', 0), item.get('y', 0), item.get('w', 1), item.get('h', 1),
             item['id'], user_id))
    g.db.commit()
    return jsonify({'ok': True})

@bp.route('/widgets/add', methods=['POST'])
@login_required
def add_widget():
    user_id = session['user']['id']
    wtype = request.form.get('widget_type')
    if wtype not in WIDGET_REGISTRY:
        flash('Unknown widget type.', 'error')
        return redirect(url_for('dashboard.index'))
    meta = WIDGET_REGISTRY[wtype]
    w, h = (int(x) for x in meta['size'].split('x'))
    g.db.execute("""INSERT INTO dashboard_widgets (user_id,widget_type,widget_title,widget_config,width,height)
        VALUES (?,?,?,?,?,?)""", (user_id, wtype, meta['label'], '{}', w, h))
    g.db.commit()
    flash(f'Widget "{meta["label"]}" added.', 'success')
    return redirect(url_for('dashboard.index'))

@bp.route('/widgets/<int:wid>/remove', methods=['POST'])
@login_required
def remove_widget(wid):
    user_id = session['user']['id']
    g.db.execute("DELETE FROM dashboard_widgets WHERE id=? AND user_id=?", (wid, user_id))
    g.db.commit()
    return jsonify({'ok': True})

@bp.route('/widgets/<int:wid>/configure', methods=['POST'])
@login_required
def configure_widget(wid):
    user_id = session['user']['id']
    title = request.form.get('title', '')
    config = request.form.get('config', '{}')
    g.db.execute("""UPDATE dashboard_widgets SET widget_title=?, widget_config=?
        WHERE id=? AND user_id=?""", (title, config, wid, user_id))
    g.db.commit()
    flash('Widget updated.', 'success')
    return redirect(url_for('dashboard.index'))
