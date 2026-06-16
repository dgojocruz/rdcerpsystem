from flask import Blueprint, render_template, request, redirect, url_for, g, flash
from werkzeug.security import generate_password_hash
from ..auth import login_required

bp = Blueprint('settings', __name__)

@bp.route('/')
@login_required
def index():
    company = g.db.execute("SELECT * FROM company_settings LIMIT 1").fetchone()
    modules = g.db.execute("SELECT * FROM modules ORDER BY sort_order").fetchall()
    users = g.db.execute("SELECT id,username,full_name,role,is_active,last_login FROM users").fetchall()
    departments = g.db.execute("""SELECT d.*, COUNT(e.id) as emp_count FROM departments d
        LEFT JOIN employees e ON e.department_id=d.id AND e.status='ACTIVE'
        GROUP BY d.id ORDER BY d.name""").fetchall()
    holidays = g.db.execute("SELECT * FROM holidays ORDER BY holiday_date").fetchall()
    custom_fields = g.db.execute("SELECT * FROM custom_field_definitions ORDER BY sort_order").fetchall()
    return render_template('settings/index.html', company=company, modules=modules,
        users=users, departments=departments, holidays=holidays, custom_fields=custom_fields)

@bp.route('/company', methods=['POST'])
@login_required
def update_company():
    f = request.form
    g.db.execute("""UPDATE company_settings SET
        company_name=?,trade_name=?,address=?,city=?,province=?,zip_code=?,
        phone=?,email=?,tin=?,sss_employer_no=?,philhealth_employer_no=?,pagibig_employer_no=?,
        work_hours_per_day=?,work_days_per_week=?,updated_at=datetime('now') WHERE id=1""",
        (f.get('company_name'),f.get('trade_name'),f.get('address'),f.get('city'),
         f.get('province'),f.get('zip_code'),f.get('phone'),f.get('email'),
         f.get('tin'),f.get('sss_employer_no'),f.get('philhealth_employer_no'),
         f.get('pagibig_employer_no'),f.get('work_hours_per_day',8),f.get('work_days_per_week',6)))
    g.db.commit()
    flash('Company settings updated.', 'success')
    return redirect(url_for('settings.index'))

@bp.route('/modules/toggle', methods=['POST'])
@login_required
def toggle_module():
    g.db.execute("UPDATE modules SET is_enabled=1-is_enabled WHERE module_key=?",
                 (request.form.get('module_key'),))
    g.db.commit()
    return redirect(url_for('settings.index'))

@bp.route('/users/add', methods=['POST'])
@login_required
def add_user():
    f = request.form
    g.db.execute("INSERT INTO users (username,password_hash,full_name,email,role) VALUES (?,?,?,?,?)",
        (f['username'], generate_password_hash(f['password']), f['full_name'], f.get('email',''), f.get('role','staff')))
    g.db.commit()
    flash('User added.', 'success')
    return redirect(url_for('settings.index'))

@bp.route('/departments/add', methods=['POST'])
@login_required
def add_department():
    f = request.form
    g.db.execute("INSERT OR IGNORE INTO departments (code,name,dept_type) VALUES (?,?,?)",
        (f['code'].upper(), f['name'], f.get('dept_type','IND')))
    g.db.commit()
    flash('Department added.', 'success')
    return redirect(url_for('settings.index'))

@bp.route('/holidays/add', methods=['POST'])
@login_required
def add_holiday():
    f = request.form
    g.db.execute("INSERT OR REPLACE INTO holidays (holiday_date,holiday_name,holiday_type) VALUES (?,?,?)",
        (f['holiday_date'], f['holiday_name'], f['holiday_type']))
    g.db.commit()
    flash('Holiday added.', 'success')
    return redirect(url_for('settings.index'))

@bp.route('/custom-fields/add', methods=['POST'])
@login_required
def add_custom_field():
    f = request.form
    g.db.execute("""INSERT INTO custom_field_definitions
        (field_key,field_label,field_type,field_options,applies_to,is_required)
        VALUES (?,?,?,?,?,?)""",
        (f['field_key'].lower().replace(' ','_'), f['field_label'],
         f.get('field_type','TEXT'), f.get('field_options',''),
         f.get('applies_to','employee'), int(f.get('is_required',0))))
    g.db.commit()
    flash('Custom field added.', 'success')
    return redirect(url_for('settings.index'))
