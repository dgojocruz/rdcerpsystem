from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from ..auth import login_required

bp = Blueprint('leaves', __name__)

@bp.route('/')
@login_required
def index():
    status_filter = request.args.get('status', '')
    q = "SELECT lr.*, e.last_name, e.first_name, e.employee_no FROM leave_requests lr JOIN employees e ON lr.employee_id=e.id"
    params = []
    if status_filter:
        q += " WHERE lr.status=?"
        params.append(status_filter)
    q += " ORDER BY lr.created_at DESC"
    requests = g.db.execute(q, params).fetchall()
    return render_template('leaves/index.html', requests=requests, status_filter=status_filter)

@bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    if request.method == 'POST':
        f = request.form
        from datetime import datetime
        d1 = datetime.strptime(f['date_from'], '%Y-%m-%d')
        d2 = datetime.strptime(f['date_to'], '%Y-%m-%d')
        days = (d2 - d1).days + 1
        g.db.execute("""INSERT INTO leave_requests
            (employee_id,leave_type,date_from,date_to,num_days,reason,status)
            VALUES (?,?,?,?,?,?,'PENDING')""",
            (f['employee_id'], f['leave_type'], f['date_from'], f['date_to'], days, f.get('reason','')))
        g.db.commit()
        flash('Leave request submitted.', 'success')
        return redirect(url_for('leaves.index'))
    employees = g.db.execute("SELECT * FROM employees WHERE status='ACTIVE' ORDER BY last_name").fetchall()
    return render_template('leaves/apply.html', employees=employees)

@bp.route('/<int:req_id>/approve', methods=['POST'])
@login_required
def approve(req_id):
    lr = g.db.execute("SELECT * FROM leave_requests WHERE id=?", (req_id,)).fetchone()
    if lr:
        g.db.execute("""UPDATE leave_requests SET status='APPROVED', approved_by=1, approved_at=datetime('now')
                       WHERE id=?""", (req_id,))
        g.db.execute("""UPDATE leave_credits SET used_days=used_days+?, balance_days=balance_days-?
                       WHERE employee_id=? AND leave_type=? AND year=strftime('%Y','now')""",
                     (lr['num_days'], lr['num_days'], lr['employee_id'], lr['leave_type']))
        g.db.commit()
    flash('Leave approved.', 'success')
    return redirect(url_for('leaves.index'))

@bp.route('/<int:req_id>/reject', methods=['POST'])
@login_required
def reject(req_id):
    g.db.execute("UPDATE leave_requests SET status='REJECTED' WHERE id=?", (req_id,))
    g.db.commit()
    flash('Leave rejected.', 'info')
    return redirect(url_for('leaves.index'))

@bp.route('/credits')
@login_required
def credits():
    credits = g.db.execute("""SELECT lc.*, e.last_name, e.first_name, e.employee_no
        FROM leave_credits lc JOIN employees e ON lc.employee_id=e.id
        WHERE lc.year=strftime('%Y','now') ORDER BY e.last_name, lc.leave_type""").fetchall()
    return render_template('leaves/credits.html', credits=credits)
