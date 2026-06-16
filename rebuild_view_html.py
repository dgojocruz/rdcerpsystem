new_html = '''{% extends 'base.html' %}
{% block title %}{{ emp.last_name }}, {{ emp.first_name }}{% endblock %}
{% block page_title %}{{ emp.last_name }}, {{ emp.first_name }}{% endblock %}
{% block breadcrumb %}<a href="{{ url_for('employees.index') }}">Employees</a> / {{ emp.employee_no }}{% endblock %}
{% block topbar_actions %}
<a href="{{ url_for('employees.edit', emp_id=emp.id) }}" class="btn"><i class="ti ti-edit"></i> Edit</a>
<a href="{{ url_for('payroll.backpay', emp_id=emp.id) }}" class="btn btn-danger"><i class="ti ti-file-text"></i> Backpay</a>
{% endblock %}
{% block content %}
<div class="grid-2">
<div class="card">
  <div class="card-body">
    <div class="d-flex align-center gap-8 mb-16">
      <div class="emp-avatar" style="width:56px;height:56px;font-size:18px;background:#eff6ff;color:#1d4ed8">{{ emp.last_name[0] }}{{ emp.first_name[0] }}</div>
      <div>
        <div style="font-size:18px;font-weight:700">{{ emp.last_name }}, {{ emp.first_name }} {% if emp.middle_name %}{{ emp.middle_name }}{% endif %}</div>
        <div class="text-muted">{{ emp.position_title or "—" }} · {{ emp.dept_name or "—" }}</div>
        <div class="d-flex gap-8 mt-8">
          <span class="badge badge-{{ "green" if emp.status=="ACTIVE" else "red" }}">{{ emp.status }}</span>
          <span class="badge badge-blue">{{ emp.payroll_group }}</span>
          <span class="badge badge-gray">{{ emp.tax_type }}</span>
        </div>
      </div>
    </div>
    <div class="section-divider">Employment Information</div>
    {% for row in [
      ("Employee No.", emp.employee_no),
      ("Department", emp.dept_name or "—"),
      ("Position", emp.position_title or "—"),
      ("Dept. Type", emp.dept_type),
      ("Employment Type", emp.employment_type),
      ("Date Hired", emp.date_hired or "—"),
      ("Payment Method", emp.payment_method),
    ] %}
    <div class="d-flex justify-between" style="padding:7px 0;border-bottom:1px solid #f3f4f6">
      <span class="text-sm text-muted">{{ row[0] }}</span>
      <span class="text-sm fw-600">{{ row[1] }}</span>
    </div>
    {% endfor %}
    <div class="section-divider mt-16">Salary Details</div>
    {% for row in [
      ("Daily Rate", "₱" + "{:,.2f}".format(emp.daily_rate or 0)),
      ("Hourly Rate", "₱" + "{:,.2f}".format(emp.hourly_rate or 0)),
      ("Allowance", "₱" + "{:,.2f}".format(emp.allowance_amount or 0)),
    ] %}
    <div class="d-flex justify-between" style="padding:7px 0;border-bottom:1px solid #f3f4f6">
      <span class="text-sm text-muted">{{ row[0] }}</span>
      <span class="text-sm fw-600 font-mono">{{ row[1] }}</span>
    </div>
    {% endfor %}
  </div>
</div>
<div>
  <div class="card mb-16">
    <div class="card-header"><div class="card-title"><i class="ti ti-file-certificate"></i> Government IDs</div></div>
    <div class="card-body">
      {% for lbl, val in [("TIN", emp.tin), ("SSS", emp.sss_no), ("PhilHealth", emp.philhealth_no), ("Pag-IBIG", emp.pagibig_no)] %}
      <div class="d-flex justify-between" style="padding:7px 0;border-bottom:1px solid #f3f4f6">
        <span class="text-sm text-muted">{{ lbl }}</span>
        <span class="text-sm font-mono">{{ val or "—" }}</span>
      </div>
      {% endfor %}
    </div>
  </div>
  <div class="card mb-16">
    <div class="card-header"><div class="card-title"><i class="ti ti-calendar-off"></i> Leave Credits (2026)</div></div>
    <div class="table-responsive"><table>
      <thead><tr><th>Type</th><th>Allocated</th><th>Used</th><th>Balance</th></tr></thead>
      <tbody>
      {% for lc in leaves %}
      <tr>
        <td>{{ lc.leave_type }}</td>
        <td>{{ lc.allocated_days }}</td>
        <td>{{ lc.used_days }}</td>
        <td class="fw-600 text-success">{{ lc.balance_days }}</td>
      </tr>
      {% else %}<tr><td colspan="4" class="text-center text-muted">No leave credits</td></tr>{% endfor %}
      </tbody>
    </table></div>
  </div>
  <div class="card">
    <div class="card-header"><div class="card-title"><i class="ti ti-cash"></i> Recent Payslips</div></div>
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
</div>

<div class="card" style="margin-top:16px">
  <div class="card-header" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div class="card-title"><i class="ti ti-fingerprint"></i> Timekeeping History</div>
    <form method="get" style="display:flex;gap:8px;align-items:center">
      <input type="month" name="tk_month" value="{{ tk_month }}" style="border:1px solid #e5e7eb;border-radius:6px;padding:4px 10px;font-size:13px">
      <button type="submit" class="btn btn-sm"><i class="ti ti-filter"></i> Filter</button>
      {% if tk_month %}<a href="{{ url_for("employees.view", emp_id=emp.id) }}" class="btn btn-sm">Clear</a>{% endif %}
    </form>
  </div>
  {% if tk_stats %}
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;padding:14px 16px;border-bottom:1px solid #f3f4f6">
    <div style="background:#f9fafb;border-radius:8px;padding:10px 14px;text-align:center">
      <div style="font-size:11px;color:#6b7280;margin-bottom:4px">Present</div>
      <div style="font-size:20px;font-weight:600;color:#16a34a">{{ tk_stats.present_days or 0 }}</div>
    </div>
    <div style="background:#f9fafb;border-radius:8px;padding:10px 14px;text-align:center">
      <div style="font-size:11px;color:#6b7280;margin-bottom:4px">Absent</div>
      <div style="font-size:20px;font-weight:600;color:#dc2626">{{ tk_stats.absent_days or 0 }}</div>
    </div>
    <div style="background:#f9fafb;border-radius:8px;padding:10px 14px;text-align:center">
      <div style="font-size:11px;color:#6b7280;margin-bottom:4px">Late days</div>
      <div style="font-size:20px;font-weight:600;color:#d97706">{{ tk_stats.late_days or 0 }}</div>
    </div>
    <div style="background:#f9fafb;border-radius:8px;padding:10px 14px;text-align:center">
      <div style="font-size:11px;color:#6b7280;margin-bottom:4px">Total OT hrs</div>
      <div style="font-size:20px;font-weight:600;color:#2563eb">{{ "%.2f"|format(tk_stats.total_ot or 0) }}</div>
    </div>
    <div style="background:#f9fafb;border-radius:8px;padding:10px 14px;text-align:center">
      <div style="font-size:11px;color:#6b7280;margin-bottom:4px">Late mins</div>
      <div style="font-size:20px;font-weight:600;color:#d97706">{{ tk_stats.total_late_min or 0 }}</div>
    </div>
    <div style="background:#f9fafb;border-radius:8px;padding:10px 14px;text-align:center">
      <div style="font-size:11px;color:#6b7280;margin-bottom:4px">Total hrs worked</div>
      <div style="font-size:20px;font-weight:600">{{ "%.1f"|format(tk_stats.total_hours_worked or 0) }}</div>
    </div>
  </div>
  {% endif %}
  <div class="table-responsive">
    <table style="font-size:12px">
      <thead>
        <tr>
          <th>Date</th><th>Time In</th><th>Time Out</th><th>Hours</th>
          <th>OT Hrs</th><th>Late (min)</th><th>Status</th><th>Source</th>
        </tr>
      </thead>
      <tbody>
      {% for a in attendance_history %}
      <tr style="{{ "background:#fef2f2" if a.is_absent else "background:#f0fdf4" if a.ot_hours and a.ot_hours > 0 else "background:#fffbeb" if a.late_minutes and a.late_minutes > 0 else "" }}">
        <td class="fw-600">{{ a.work_date }}</td>
        <td class="font-mono">{{ a.time_in or "—" }}</td>
        <td class="font-mono">{{ a.time_out or "—" }}</td>
        <td class="font-mono">{{ "%.2f"|format(a.total_hours or 0) if not a.is_absent else "—" }}</td>
        <td class="font-mono {{ "text-primary fw-600" if a.ot_hours and a.ot_hours > 0 else "text-muted" }}">
          {{ "%.2f"|format(a.ot_hours) if a.ot_hours and a.ot_hours > 0 else "—" }}
        </td>
        <td class="{{ "text-danger fw-600" if a.late_minutes and a.late_minutes > 0 else "text-muted" }}">
          {{ a.late_minutes if a.late_minutes and a.late_minutes > 0 else "—" }}
        </td>
        <td>
          {% if a.is_absent %}<span class="badge badge-red">Absent</span>
          {% elif a.is_rest_day %}<span class="badge badge-gray">Rest day</span>
          {% elif a.is_holiday %}<span class="badge badge-amber">Holiday</span>
          {% elif a.late_minutes and a.late_minutes > 0 %}<span class="badge badge-amber">Late</span>
          {% elif a.ot_hours and a.ot_hours > 0 %}<span class="badge badge-blue">OT</span>
          {% else %}<span class="badge badge-green">Present</span>
          {% endif %}
        </td>
        <td class="text-muted" style="font-size:11px">{{ a.source or "MANUAL" }}</td>
      </tr>
      {% else %}
      <tr><td colspan="8" class="text-center text-muted" style="padding:24px">No attendance records found{% if tk_month %} for this month{% endif %}.</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
  {% if attendance_history|length == 60 %}
  <div style="padding:10px 16px;font-size:12px;color:#6b7280;border-top:1px solid #f3f4f6">
    Showing latest 60 records. Use the month filter to narrow results.
  </div>
  {% endif %}
</div>
{% endblock %}
'''

open('app/templates/employees/view.html', 'w', encoding='utf-8').write(new_html)
print("Done! view.html rebuilt cleanly.")
print("Endblock count:", new_html.count('endblock'))
