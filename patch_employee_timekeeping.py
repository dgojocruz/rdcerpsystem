import re

# ── 1. Patch employees/__init__.py — add attendance query to view() ─────────
py = open('app/modules/employees/__init__.py', encoding='utf-8').read()

old_view_query = """    recent_payroll = g.db.execute(\"\"\"SELECT pr.*, pp.period_label FROM payroll pr
        JOIN pay_periods pp ON pr.pay_period_id=pp.id
        WHERE pr.employee_id=? ORDER BY pp.date_from DESC LIMIT 6\"\"\", (emp_id,)).fetchall()
    departments = g.db.execute(\"SELECT * FROM departments WHERE is_active=1\").fetchall()
    return render_template('employees/view.html', emp=emp, loans=loans, leaves=leaves,
                           recent_payroll=recent_payroll, departments=departments)"""

new_view_query = """    recent_payroll = g.db.execute(\"\"\"SELECT pr.*, pp.period_label FROM payroll pr
        JOIN pay_periods pp ON pr.pay_period_id=pp.id
        WHERE pr.employee_id=? ORDER BY pp.date_from DESC LIMIT 6\"\"\", (emp_id,)).fetchall()

    # Timekeeping history
    month_filter = request.args.get('tk_month', '')
    tk_query = \"\"\"SELECT work_date, time_in, time_out, total_hours, regular_hours,
        ot_hours, nd_hours, late_minutes, undertime_minutes,
        is_absent, is_holiday, holiday_type, is_rest_day, source, remarks
        FROM attendance WHERE employee_id=?\"\"\"
    tk_params = [emp_id]
    if month_filter:
        tk_query += \" AND strftime('%Y-%m', work_date)=?\"
        tk_params.append(month_filter)
    tk_query += \" ORDER BY work_date DESC LIMIT 60\"
    attendance_history = g.db.execute(tk_query, tk_params).fetchall()

    # Attendance summary stats
    tk_stats = g.db.execute(\"\"\"SELECT
        COUNT(*) as total_days,
        SUM(CASE WHEN is_absent=0 AND is_rest_day=0 AND is_holiday=0 THEN 1 ELSE 0 END) as present_days,
        SUM(CASE WHEN is_absent=1 THEN 1 ELSE 0 END) as absent_days,
        SUM(CASE WHEN late_minutes>0 THEN 1 ELSE 0 END) as late_days,
        COALESCE(SUM(ot_hours),0) as total_ot,
        COALESCE(SUM(late_minutes),0) as total_late_min,
        COALESCE(SUM(total_hours),0) as total_hours_worked
        FROM attendance WHERE employee_id=?
        AND (? = '' OR strftime('%Y-%m', work_date)=?)
    \"\"\", (emp_id, month_filter, month_filter)).fetchone()

    departments = g.db.execute(\"SELECT * FROM departments WHERE is_active=1\").fetchall()
    return render_template('employees/view.html', emp=emp, loans=loans, leaves=leaves,
                           recent_payroll=recent_payroll, departments=departments,
                           attendance_history=attendance_history, tk_stats=tk_stats,
                           tk_month=month_filter)"""

py = py.replace(old_view_query, new_view_query)
open('app/modules/employees/__init__.py', 'w', encoding='utf-8').write(py)
print("OK: employees/__init__.py patched")

# ── 2. Patch view.html — add timekeeping tracker section ────────────────────
html = open('app/templates/employees/view.html', encoding='utf-8').read()

tk_section = """
{% endblock %}
"""

new_tk_section = """
<div class="card mt-16">
  <div class="card-header" style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
    <div class="card-title"><i class="ti ti-fingerprint"></i> Timekeeping History</div>
    <form method="get" style="display:flex;gap:8px;align-items:center">
      <input type="month" name="tk_month" value="{{ tk_month }}"
        style="border:1px solid #e5e7eb;border-radius:6px;padding:4px 10px;font-size:13px">
      <button type="submit" class="btn btn-sm"><i class="ti ti-filter"></i> Filter</button>
      {% if tk_month %}<a href="{{ url_for('employees.view', emp_id=emp.id) }}" class="btn btn-sm">Clear</a>{% endif %}
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
          <th>Date</th>
          <th>Day</th>
          <th>Time In</th>
          <th>Time Out</th>
          <th>Hours</th>
          <th>OT Hrs</th>
          <th>Late (min)</th>
          <th>Status</th>
          <th>Type</th>
          <th>Source</th>
        </tr>
      </thead>
      <tbody>
      {% for a in attendance_history %}
      {% set wd = a.work_date %}
      <tr style="{{ 'background:#fef2f2' if a.is_absent else 'background:#f0fdf4' if a.ot_hours and a.ot_hours > 0 else 'background:#fffbeb' if a.late_minutes and a.late_minutes > 0 else '' }}">
        <td class="fw-600">{{ a.work_date }}</td>
        <td class="text-muted" style="font-size:11px">
          {% set days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] %}
          {{ a.work_date }}
        </td>
        <td class="font-mono">{{ a.time_in or '—' }}</td>
        <td class="font-mono">{{ a.time_out or '—' }}</td>
        <td class="font-mono">{{ "%.2f"|format(a.total_hours or 0) if not a.is_absent else '—' }}</td>
        <td class="font-mono {{ 'text-primary fw-600' if a.ot_hours and a.ot_hours > 0 else 'text-muted' }}">
          {{ "%.2f"|format(a.ot_hours) if a.ot_hours and a.ot_hours > 0 else '—' }}
        </td>
        <td class="{{ 'text-danger fw-600' if a.late_minutes and a.late_minutes > 0 else 'text-muted' }}">
          {{ a.late_minutes if a.late_minutes and a.late_minutes > 0 else '—' }}
        </td>
        <td>
          {% if a.is_absent %}
            <span class="badge badge-red">Absent</span>
          {% elif a.is_rest_day %}
            <span class="badge badge-gray">Rest day</span>
          {% elif a.is_holiday %}
            <span class="badge badge-amber">Holiday</span>
          {% elif a.late_minutes and a.late_minutes > 0 %}
            <span class="badge badge-amber">Late</span>
          {% elif a.ot_hours and a.ot_hours > 0 %}
            <span class="badge badge-blue">OT</span>
          {% else %}
            <span class="badge badge-green">Present</span>
          {% endif %}
        </td>
        <td class="text-muted" style="font-size:11px">{{ a.holiday_type or ('Rest' if a.is_rest_day else 'Regular') }}</td>
        <td class="text-muted" style="font-size:11px">{{ a.source or 'MANUAL' }}</td>
      </tr>
      {% else %}
      <tr><td colspan="10" class="text-center text-muted" style="padding:24px">No attendance records found{% if tk_month %} for this month{% endif %}.</td></tr>
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
"""

html = html.replace("{% endblock %}", new_tk_section, 1)
open('app/templates/employees/view.html', 'w', encoding='utf-8').write(html)
print("OK: employees/view.html patched")
print("\nDone! Restart the server and open any employee profile to see the Timekeeping History section.")
