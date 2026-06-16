new_html = r'''{% extends 'base.html' %}
{% block title %}{{ emp.last_name }}, {{ emp.first_name }}{% endblock %}
{% block page_title %}{{ emp.last_name }}, {{ emp.first_name }}{% endblock %}
{% block breadcrumb %}<a href="{{ url_for('employees.index') }}">Employees</a> / {{ emp.employee_no }}{% endblock %}
{% block topbar_actions %}
<a href="{{ url_for('employees.edit', emp_id=emp.id) }}" class="btn"><i class="ti ti-edit"></i> Edit</a>
<a href="{{ url_for('payroll.backpay', emp_id=emp.id) }}" class="btn btn-danger"><i class="ti ti-file-text"></i> Backpay</a>
{% endblock %}

{% block content %}
<style>
.collapsible-card { margin-bottom: 16px; }
.collapsible-header {
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; padding: 12px 16px;
  background: var(--color-background-secondary, #f9fafb);
  border-bottom: 1px solid #f3f4f6; user-select: none;
}
.collapsible-header:hover { background: #f3f4f6; }
.collapsible-body { transition: none; }
.collapsible-body.collapsed { display: none; }
.chevron { transition: transform .2s; font-size: 16px; color: #6b7280; }
.chevron.open { transform: rotate(180deg); }
.section-badge { font-size:11px;padding:2px 8px;border-radius:4px;background:#e0f2fe;color:#0369a1;font-weight:500 }
</style>

<div class="grid-2" style="margin-bottom:16px">

<!-- LEFT COLUMN -->
<div>
  <!-- Employee Info Card -->
  <div class="card collapsible-card">
    <div class="collapsible-header" onclick="toggleCard('empInfo')">
      <div class="card-title" style="margin:0">
        <div style="display:flex;align-items:center;gap:10px">
          <div class="emp-avatar" style="width:36px;height:36px;font-size:14px;background:#eff6ff;color:#1d4ed8;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;flex-shrink:0">{{ emp.last_name[0] }}{{ emp.first_name[0] }}</div>
          <div>
            <div style="font-size:15px;font-weight:700">{{ emp.last_name }}, {{ emp.first_name }}{% if emp.middle_name %} {{ emp.middle_name }}{% endif %}</div>
            <div class="text-muted" style="font-size:12px">{{ emp.position_title or '—' }} · {{ emp.dept_name or '—' }}</div>
          </div>
        </div>
      </div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="badge badge-{{ 'green' if emp.status=='ACTIVE' else 'red' }}">{{ emp.status }}</span>
        <span class="badge badge-blue">{{ emp.payroll_group }}</span>
        <span class="badge badge-gray">{{ emp.tax_type }}</span>
        <i class="ti ti-chevron-down chevron open" id="chevron-empInfo"></i>
      </div>
    </div>
    <div class="collapsible-body" id="body-empInfo">
      <div style="padding:12px 16px">
        <div class="section-divider">Employment Information</div>
        {% for row in [
          ('Employee No.', emp.employee_no),
          ('Department', emp.dept_name or '—'),
          ('Position', emp.position_title or '—'),
          ('Dept. Type', emp.dept_type),
          ('Employment Type', emp.employment_type),
          ('Date Hired', emp.date_hired or '—'),
          ('Payment Method', emp.payment_method),
          ('Biometric ID', emp.biometric_id or '—'),
        ] %}
        <div class="d-flex justify-between" style="padding:6px 0;border-bottom:1px solid #f3f4f6">
          <span class="text-sm text-muted">{{ row[0] }}</span>
          <span class="text-sm fw-600">{{ row[1] }}</span>
        </div>
        {% endfor %}

        <!-- Reports To -->
        <div class="d-flex justify-between" style="padding:6px 0;border-bottom:1px solid #f3f4f6">
          <span class="text-sm text-muted"><i class="ti ti-hierarchy" style="vertical-align:-2px;color:#2563eb"></i> Reports To</span>
          <span class="text-sm fw-600">
            {% if emp.mgr_last %}
              <a href="#" style="color:#2563eb">{{ emp.mgr_last }}, {{ emp.mgr_first }}</a>
            {% else %}— (Top Level){% endif %}
          </span>
        </div>

        <div class="section-divider mt-12">Salary Details</div>
        {% for row in [
          ('Daily Rate', '₱' + "{:,.2f}".format(emp.daily_rate or 0)),
          ('Hourly Rate', '₱' + "{:,.2f}".format(emp.hourly_rate or 0)),
          ('Allowance', '₱' + "{:,.2f}".format(emp.allowance_amount or 0)),
        ] %}
        <div class="d-flex justify-between" style="padding:6px 0;border-bottom:1px solid #f3f4f6">
          <span class="text-sm text-muted">{{ row[0] }}</span>
          <span class="text-sm fw-600 font-mono">{{ row[1] }}</span>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- Government IDs Card -->
  <div class="card collapsible-card">
    <div class="collapsible-header" onclick="toggleCard('govIds')">
      <div class="card-title" style="margin:0"><i class="ti ti-file-certificate"></i> Government IDs</div>
      <i class="ti ti-chevron-down chevron open" id="chevron-govIds"></i>
    </div>
    <div class="collapsible-body" id="body-govIds">
      <div style="padding:12px 16px">
        {% for lbl, val in [('TIN', emp.tin), ('SSS', emp.sss_no), ('PhilHealth', emp.philhealth_no), ('Pag-IBIG', emp.pagibig_no)] %}
        <div class="d-flex justify-between" style="padding:6px 0;border-bottom:1px solid #f3f4f6">
          <span class="text-sm text-muted">{{ lbl }}</span>
          <span class="text-sm font-mono">{{ val or '—' }}</span>
        </div>
        {% endfor %}
      </div>
    </div>
  </div>

  <!-- Schedule Manager Card -->
  <div class="card collapsible-card">
    <div class="collapsible-header" onclick="toggleCard('schedMgr')">
      <div class="card-title" style="margin:0"><i class="ti ti-calendar-week"></i> Schedule Manager</div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="section-badge">{{ schedule_history|length }} records</span>
        <i class="ti ti-chevron-down chevron open" id="chevron-schedMgr"></i>
      </div>
    </div>
    <div class="collapsible-body" id="body-schedMgr">
      <!-- Add Schedule Form -->
      <div style="padding:12px 16px;border-bottom:1px solid #f3f4f6;background:#f9fafb">
        <div style="font-size:12px;font-weight:600;color:#374151;margin-bottom:8px"><i class="ti ti-plus"></i> Assign Schedule</div>
        <form method="post" action="{{ url_for('employees.assign_emp_schedule', emp_id=emp.id) }}">
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:8px">
            <div>
              <label style="font-size:11px;color:#6b7280;display:block;margin-bottom:3px">From Date</label>
              <input type="date" name="date_from" class="form-control" style="font-size:12px" required>
            </div>
            <div>
              <label style="font-size:11px;color:#6b7280;display:block;margin-bottom:3px">To Date</label>
              <input type="date" name="date_to" class="form-control" style="font-size:12px" required>
            </div>
            <div>
              <label style="font-size:11px;color:#6b7280;display:block;margin-bottom:3px">Shift</label>
              <select name="shift_id" class="form-control" style="font-size:12px">
                <option value="">Rest Day</option>
                {% for s in shifts %}
                <option value="{{ s.id }}">{{ s.shift_name }}</option>
                {% endfor %}
              </select>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:8px">
            <div>
              <label style="font-size:11px;color:#6b7280;display:block;margin-bottom:3px">Day Type</label>
              <select name="is_rest_day" class="form-control" style="font-size:12px">
                <option value="0">Working Day</option>
                <option value="1">Rest Day</option>
              </select>
            </div>
            <div>
              <label style="font-size:11px;color:#6b7280;display:block;margin-bottom:3px">Remarks</label>
              <input name="remarks" class="form-control" style="font-size:12px" placeholder="Optional note">
            </div>
          </div>
          <button type="submit" class="btn btn-sm btn-primary"><i class="ti ti-check"></i> Save Schedule</button>
        </form>
      </div>
      <!-- Schedule History -->
      <div style="padding:8px 16px;display:flex;align-items:center;justify-content:space-between">
        <span style="font-size:12px;font-weight:600;color:#374151">Schedule Records</span>
        <form method="get" style="display:flex;gap:6px">
          <input type="hidden" name="tk_month" value="{{ tk_month }}">
          <input type="month" name="sch_month" value="{{ sch_month }}" style="border:1px solid #e5e7eb;border-radius:6px;padding:3px 8px;font-size:12px">
          <button type="submit" class="btn btn-sm">Filter</button>
        </form>
      </div>
      <div class="table-responsive">
        <table style="font-size:12px">
          <thead><tr><th>Date</th><th>Shift</th><th>Time In</th><th>Time Out</th><th>Type</th><th>Action</th></tr></thead>
          <tbody>
          {% for s in schedule_history %}
          <tr>
            <td class="fw-600">{{ s.schedule_date }}</td>
            <td>
              {% if s.is_rest_day %}<span class="badge badge-gray">Rest Day</span>
              {% elif s.shift_name %}
                <span style="display:inline-flex;align-items:center;gap:5px">
                  <span style="width:8px;height:8px;border-radius:2px;background:{{ s.color_hex or '#3B82F6' }};display:inline-block"></span>
                  {{ s.shift_name }}
                </span>
              {% else %}—{% endif %}
            </td>
            <td class="font-mono">{{ s.time_in or '—' }}</td>
            <td class="font-mono">{{ s.time_out or '—' }}</td>
            <td class="text-muted">{{ s.schedule_type or 'REGULAR' }}</td>
            <td>
              <form method="post" action="{{ url_for('employees.delete_emp_schedule', emp_id=emp.id, schedule_id=s.id) }}"
                style="display:inline" onsubmit="return confirm('Delete this schedule entry?')">
                <button class="btn btn-xs btn-danger" type="submit"><i class="ti ti-trash"></i></button>
              </form>
            </td>
          </tr>
          {% else %}
          <tr><td colspan="6" class="text-center text-muted" style="padding:16px">No schedule records.</td></tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<!-- RIGHT COLUMN -->
<div>
  <!-- Leave Credits -->
  <div class="card collapsible-card">
    <div class="collapsible-header" onclick="toggleCard('leaveCredits')">
      <div class="card-title" style="margin:0"><i class="ti ti-calendar-off"></i> Leave Credits (2026)</div>
      <i class="ti ti-chevron-down chevron open" id="chevron-leaveCredits"></i>
    </div>
    <div class="collapsible-body" id="body-leaveCredits">
      <div class="table-responsive"><table>
        <thead><tr><th>Type</th><th>Allocated</th><th>Used</th><th>Balance</th></tr></thead>
        <tbody>
        {% for lc in leaves %}
        <tr>
          <td>{{ lc.leave_type }}</td><td>{{ lc.allocated_days }}</td>
          <td>{{ lc.used_days }}</td>
          <td class="fw-600 text-success">{{ lc.balance_days }}</td>
        </tr>
        {% else %}<tr><td colspan="4" class="text-center text-muted">No leave credits</td></tr>{% endfor %}
        </tbody>
      </table></div>
    </div>
  </div>

  <!-- Recent Payslips -->
  <div class="card collapsible-card">
    <div class="collapsible-header" onclick="toggleCard('payslips')">
      <div class="card-title" style="margin:0"><i class="ti ti-cash"></i> Recent Payslips</div>
      <i class="ti ti-chevron-down chevron open" id="chevron-payslips"></i>
    </div>
    <div class="collapsible-body" id="body-payslips">
      <div class="table-responsive"><table>
        <thead><tr><th>Period</th><th>Gross</th><th>Net Pay</th></tr></thead>
        <tbody>
        {% for pr in recent_payroll %}
        <tr>
          <td class="text-sm">{{ pr.period_label }}</td>
          <td class="font-mono text-sm">₱{{ "{:,.2f}".format(pr.gross_salary or 0) }}</td>
          <td class="font-mono text-sm fw-600 text-primary">₱{{ "{:,.2f}".format(pr.net_pay or 0) }}</td>
        </tr>
        {% else %}<tr><td colspan="3" class="text-center text-muted">No payroll records</td></tr>{% endfor %}
        </tbody>
      </table></div>
    </div>
  </div>

  <!-- Audit / Change Log -->
  <div class="card collapsible-card">
    <div class="collapsible-header" onclick="toggleCard('auditLog')">
      <div class="card-title" style="margin:0"><i class="ti ti-history"></i> Change Log</div>
      <div style="display:flex;gap:6px;align-items:center">
        <span class="section-badge">{{ audit_log|length }} entries</span>
        <i class="ti ti-chevron-down chevron collapsed" id="chevron-auditLog"></i>
      </div>
    </div>
    <div class="collapsible-body collapsed" id="body-auditLog">
      <div class="table-responsive">
        <table style="font-size:12px">
          <thead><tr><th>Date/Time</th><th>Action</th><th>Details</th><th>By</th></tr></thead>
          <tbody>
          {% for log in audit_log %}
          <tr>
            <td class="font-mono text-muted" style="font-size:11px">{{ log.created_at }}</td>
            <td><span class="badge badge-{{ 'blue' if log.action=='SCHEDULE_ADD' else 'red' if log.action=='SCHEDULE_DEL' else 'gray' }}">{{ log.action }}</span></td>
            <td class="text-sm">{{ log.details }}</td>
            <td class="text-muted text-sm">{{ log.performed_by or 'admin' }}</td>
          </tr>
          {% else %}
          <tr><td colspan="4" class="text-center text-muted" style="padding:16px">No changes logged.</td></tr>
          {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
</div>

<!-- FULL WIDTH BOTTOM SECTIONS -->

<!-- Timekeeping History -->
<div class="card collapsible-card">
  <div class="collapsible-header" onclick="toggleCard('tkHistory')">
    <div class="card-title" style="margin:0"><i class="ti ti-fingerprint"></i> Timekeeping History</div>
    <div style="display:flex;gap:8px;align-items:center">
      {% if tk_stats %}
      <span class="section-badge">{{ tk_stats.present_days or 0 }} present · {{ tk_stats.absent_days or 0 }} absent · {{ tk_stats.late_days or 0 }} late</span>
      {% endif %}
      <form method="get" style="display:flex;gap:6px" onclick="event.stopPropagation()">
        <input type="hidden" name="sch_month" value="{{ sch_month }}">
        <input type="month" name="tk_month" value="{{ tk_month }}" style="border:1px solid #e5e7eb;border-radius:6px;padding:3px 8px;font-size:12px">
        <button type="submit" class="btn btn-sm">Filter</button>
        {% if tk_month %}<a href="{{ url_for('employees.view', emp_id=emp.id) }}" class="btn btn-sm">Clear</a>{% endif %}
      </form>
      <i class="ti ti-chevron-down chevron open" id="chevron-tkHistory"></i>
    </div>
  </div>
  <div class="collapsible-body" id="body-tkHistory">
    {% if tk_stats %}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:8px;padding:12px 16px;border-bottom:1px solid #f3f4f6">
      <div style="background:#f9fafb;border-radius:8px;padding:8px 12px;text-align:center">
        <div style="font-size:10px;color:#6b7280;margin-bottom:3px">Present</div>
        <div style="font-size:18px;font-weight:600;color:#16a34a">{{ tk_stats.present_days or 0 }}</div>
      </div>
      <div style="background:#f9fafb;border-radius:8px;padding:8px 12px;text-align:center">
        <div style="font-size:10px;color:#6b7280;margin-bottom:3px">Absent</div>
        <div style="font-size:18px;font-weight:600;color:#dc2626">{{ tk_stats.absent_days or 0 }}</div>
      </div>
      <div style="background:#f9fafb;border-radius:8px;padding:8px 12px;text-align:center">
        <div style="font-size:10px;color:#6b7280;margin-bottom:3px">Late days</div>
        <div style="font-size:18px;font-weight:600;color:#d97706">{{ tk_stats.late_days or 0 }}</div>
      </div>
      <div style="background:#f9fafb;border-radius:8px;padding:8px 12px;text-align:center">
        <div style="font-size:10px;color:#6b7280;margin-bottom:3px">Total OT hrs</div>
        <div style="font-size:18px;font-weight:600;color:#2563eb">{{ "%.2f"|format(tk_stats.total_ot or 0) }}</div>
      </div>
      <div style="background:#f9fafb;border-radius:8px;padding:8px 12px;text-align:center">
        <div style="font-size:10px;color:#6b7280;margin-bottom:3px">Late mins</div>
        <div style="font-size:18px;font-weight:600;color:#d97706">{{ tk_stats.total_late_min or 0 }}</div>
      </div>
      <div style="background:#f9fafb;border-radius:8px;padding:8px 12px;text-align:center">
        <div style="font-size:10px;color:#6b7280;margin-bottom:3px">Hrs worked</div>
        <div style="font-size:18px;font-weight:600">{{ "%.1f"|format(tk_stats.total_hours_worked or 0) }}</div>
      </div>
    </div>
    {% endif %}
    <div class="table-responsive">
      <table style="font-size:12px">
        <thead><tr><th>Date</th><th>Time In</th><th>Time Out</th><th>Hours</th><th>OT Hrs</th><th>Late (min)</th><th>Status</th><th>Source</th></tr></thead>
        <tbody>
        {% for a in attendance_history %}
        <tr style="{{ 'background:#fef2f2' if a.is_absent else 'background:#f0fdf4' if a.ot_hours and a.ot_hours > 0 else 'background:#fffbeb' if a.late_minutes and a.late_minutes > 0 else '' }}">
          <td class="fw-600">{{ a.work_date }}</td>
          <td class="font-mono">{{ a.time_in or '—' }}</td>
          <td class="font-mono">{{ a.time_out or '—' }}</td>
          <td class="font-mono">{{ "%.2f"|format(a.total_hours or 0) if not a.is_absent else '—' }}</td>
          <td class="font-mono {{ 'text-primary fw-600' if a.ot_hours and a.ot_hours > 0 else 'text-muted' }}">
            {{ "%.2f"|format(a.ot_hours) if a.ot_hours and a.ot_hours > 0 else '—' }}</td>
          <td class="{{ 'text-danger fw-600' if a.late_minutes and a.late_minutes > 0 else 'text-muted' }}">
            {{ a.late_minutes if a.late_minutes and a.late_minutes > 0 else '—' }}</td>
          <td>
            {% if a.is_absent %}<span class="badge badge-red">Absent</span>
            {% elif a.is_rest_day %}<span class="badge badge-gray">Rest day</span>
            {% elif a.is_holiday %}<span class="badge badge-amber">Holiday</span>
            {% elif a.late_minutes and a.late_minutes > 0 %}<span class="badge badge-amber">Late</span>
            {% elif a.ot_hours and a.ot_hours > 0 %}<span class="badge badge-blue">OT</span>
            {% else %}<span class="badge badge-green">Present</span>{% endif %}
          </td>
          <td class="text-muted" style="font-size:11px">{{ a.source or 'MANUAL' }}</td>
        </tr>
        {% else %}
        <tr><td colspan="8" class="text-center text-muted" style="padding:20px">No attendance records found{% if tk_month %} for this month{% endif %}.</td></tr>
        {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>

<script>
function toggleCard(id) {
  const body = document.getElementById('body-' + id);
  const chevron = document.getElementById('chevron-' + id);
  body.classList.toggle('collapsed');
  chevron.classList.toggle('open');
}
</script>
{% endblock %}
'''

open('app/templates/employees/view.html', 'w', encoding='utf-8').write(new_html)
print("OK: view.html rebuilt cleanly")
print("Endblocks:", new_html.count('endblock'))

# ── Patch employees/__init__.py ──────────────────────────────────────────────
py = open('app/modules/employees/__init__.py', encoding='utf-8').read()

# 1. Update view() to include shifts, audit_log
old_return = '''    # Schedule history
    sch_month = request.args.get('sch_month', '')
    sch_query = """SELECT es.schedule_date, es.is_rest_day, es.schedule_type,
        sd.shift_name, sd.time_in, sd.time_out, sd.break_minutes, sd.color_hex
        FROM employee_schedules es
        LEFT JOIN shift_definitions sd ON es.shift_id=sd.id
        WHERE es.employee_id=?"""
    sch_params = [emp_id]
    if sch_month:
        sch_query += " AND strftime('%Y-%m', es.schedule_date)=?"
        sch_params.append(sch_month)
    sch_query += " ORDER BY es.schedule_date DESC LIMIT 60"
    schedule_history = g.db.execute(sch_query, sch_params).fetchall()

    departments = g.db.execute("SELECT * FROM departments WHERE is_active=1").fetchall()
    return render_template('employees/view.html', emp=emp, loans=loans, leaves=leaves,
                           recent_payroll=recent_payroll, departments=departments,
                           attendance_history=attendance_history, tk_stats=tk_stats,
                           tk_month=month_filter, schedule_history=schedule_history,
                           sch_month=sch_month)'''

new_return = '''    # Schedule history
    sch_month = request.args.get('sch_month', '')
    sch_query = """SELECT es.id, es.schedule_date, es.is_rest_day, es.schedule_type,
        sd.shift_name, sd.time_in, sd.time_out, sd.break_minutes, sd.color_hex
        FROM employee_schedules es
        LEFT JOIN shift_definitions sd ON es.shift_id=sd.id
        WHERE es.employee_id=?"""
    sch_params = [emp_id]
    if sch_month:
        sch_query += " AND strftime('%Y-%m', es.schedule_date)=?"
        sch_params.append(sch_month)
    sch_query += " ORDER BY es.schedule_date DESC LIMIT 60"
    schedule_history = g.db.execute(sch_query, sch_params).fetchall()

    # Shifts list for dropdown
    shifts = g.db.execute("SELECT * FROM shift_definitions WHERE is_active=1 ORDER BY time_in").fetchall()

    # Audit/change log for this employee
    audit_log = g.db.execute("""SELECT al.*, u.username as performed_by
        FROM audit_log al LEFT JOIN users u ON al.user_id=u.id
        WHERE al.record_id=? AND al.table_name IN ('employee_schedules','employees')
        ORDER BY al.created_at DESC LIMIT 30""", (emp_id,)).fetchall()

    departments = g.db.execute("SELECT * FROM departments WHERE is_active=1").fetchall()
    return render_template('employees/view.html', emp=emp, loans=loans, leaves=leaves,
                           recent_payroll=recent_payroll, departments=departments,
                           attendance_history=attendance_history, tk_stats=tk_stats,
                           tk_month=month_filter, schedule_history=schedule_history,
                           sch_month=sch_month, shifts=shifts, audit_log=audit_log)'''

py = py.replace(old_return, new_return)

# 2. Add new routes at end
new_routes = '''
@bp.route('/<int:emp_id>/schedule/assign', methods=['POST'])
@login_required
def assign_emp_schedule(emp_id):
    from datetime import datetime, timedelta
    f = request.form
    date_from = datetime.strptime(f['date_from'], '%Y-%m-%d')
    date_to   = datetime.strptime(f['date_to'],   '%Y-%m-%d')
    shift_id  = f.get('shift_id') or None
    is_rest   = int(f.get('is_rest_day', 0))
    remarks   = f.get('remarks', '')
    count = 0
    cur = date_from
    while cur <= date_to:
        ds = cur.strftime('%Y-%m-%d')
        g.db.execute("""INSERT INTO employee_schedules
            (employee_id, shift_id, schedule_date, is_rest_day, schedule_type)
            VALUES (?,?,?,?,'REGULAR')
            ON CONFLICT(employee_id,schedule_date) DO UPDATE SET
            shift_id=excluded.shift_id, is_rest_day=excluded.is_rest_day""",
            (emp_id, shift_id, ds, is_rest))
        count += 1
        cur += timedelta(days=1)
    # Log the change
    try:
        g.db.execute("""INSERT INTO audit_log (table_name, record_id, action, details, user_id, created_at)
            VALUES ('employee_schedules', ?, 'SCHEDULE_ADD', ?, 1, datetime('now'))""",
            (emp_id, f"Assigned {'Rest Day' if is_rest else 'shift '+str(shift_id)} from {f['date_from']} to {f['date_to']} ({count} days). {remarks}"))
    except:
        pass
    g.db.commit()
    flash(f'{count} schedule entries saved.', 'success')
    return redirect(url_for('employees.view', emp_id=emp_id))

@bp.route('/<int:emp_id>/schedule/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete_emp_schedule(emp_id, schedule_id):
    sched = g.db.execute("SELECT * FROM employee_schedules WHERE id=? AND employee_id=?",
        (schedule_id, emp_id)).fetchone()
    if sched:
        g.db.execute("DELETE FROM employee_schedules WHERE id=?", (schedule_id,))
        try:
            g.db.execute("""INSERT INTO audit_log (table_name, record_id, action, details, user_id, created_at)
                VALUES ('employee_schedules', ?, 'SCHEDULE_DEL', ?, 1, datetime('now'))""",
                (emp_id, f"Deleted schedule entry for {sched['schedule_date']}"))
        except:
            pass
        g.db.commit()
        flash('Schedule entry deleted.', 'success')
    return redirect(url_for('employees.view', emp_id=emp_id))
'''

py = py + new_routes
open('app/modules/employees/__init__.py', 'w', encoding='utf-8').write(py)
print("OK: employees/__init__.py updated with schedule routes + audit log")
print("\nAll done! Restart the server.")
