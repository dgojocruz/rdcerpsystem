import os

# ── 1. New shifts/index.html with template builder ──────────────────────────
shifts_index = r'''{% extends 'base.html' %}
{% block title %}Shift Management{% endblock %}
{% block page_title %}Shift & Leave Management{% endblock %}
{% block breadcrumb %}Shifts{% endblock %}
{% block topbar_actions %}
<a href="{{ url_for('shifts.attendance_dashboard') }}" class="btn btn-primary"><i class="ti ti-layout-dashboard"></i> Attendance Dashboard</a>
<a href="{{ url_for('shifts.calendar') }}" class="btn"><i class="ti ti-calendar"></i> Calendar View</a>
{% endblock %}
{% block content %}
<div class="grid-2 mb-20">
<div class="card">
  <div class="card-header">
    <div class="card-title"><i class="ti ti-sun"></i> Shift Definitions</div>
    <button class="btn btn-sm btn-primary" onclick="openModal('addShiftModal')"><i class="ti ti-plus"></i> Add Shift</button>
  </div>
  <div class="table-responsive"><table>
  <thead><tr><th>Shift Name</th><th>Time In</th><th>Time Out</th><th>Break</th><th>Overnight</th><th>Color</th></tr></thead>
  <tbody>
  {% for s in shifts %}
  <tr>
    <td class="fw-600">{{ s.shift_name }}</td>
    <td class="font-mono">{{ s.time_in }}</td>
    <td class="font-mono">{{ s.time_out }}</td>
    <td class="text-muted">{{ s.break_minutes }} min</td>
    <td>{{ 'Yes' if s.is_overnight else '—' }}</td>
    <td><span style="display:inline-block;width:20px;height:20px;border-radius:4px;background:{{ s.color_hex }}"></span></td>
  </tr>
  {% else %}<tr><td colspan="6" class="text-center text-muted" style="padding:16px">No shifts defined.</td></tr>
  {% endfor %}
  </tbody></table></div>
</div>

<div class="card">
  <div class="card-header">
    <div class="card-title"><i class="ti ti-clipboard-list"></i> Schedule Templates</div>
    <button class="btn btn-sm btn-primary" onclick="openModal('addTemplateModal')"><i class="ti ti-plus"></i> New Template</button>
  </div>
  <div class="table-responsive"><table>
  <thead><tr><th>Template Name</th><th>Type</th><th>Group</th><th>Action</th></tr></thead>
  <tbody>
  {% for t in templates %}
  <tr>
    <td class="fw-600">{{ t.template_name }}</td>
    <td><span class="badge badge-blue">{{ t.template_type }}</span></td>
    <td class="text-muted text-sm">{{ t.applies_to_group or 'All' }}</td>
    <td>
      <form method="post" action="{{ url_for('shifts.apply_template', tmpl_id=t.id) }}" style="display:inline">
        <button class="btn btn-xs btn-primary" type="submit"><i class="ti ti-player-play"></i> Apply</button>
      </form>
      <form method="post" action="{{ url_for('shifts.delete_template', tmpl_id=t.id) }}" style="display:inline"
        onsubmit="return confirm('Delete this template?')">
        <button class="btn btn-xs btn-danger" type="submit"><i class="ti ti-trash"></i></button>
      </form>
    </td>
  </tr>
  {% else %}<tr><td colspan="4" class="text-center text-muted" style="padding:16px">No templates yet.</td></tr>
  {% endfor %}
  </tbody></table></div>
</div>
</div>

<div class="card mb-20">
<div class="card-header">
  <div class="card-title"><i class="ti ti-calendar-plus"></i> Assign Schedule</div>
</div>
<div class="card-body">
<form method="post" action="{{ url_for('shifts.assign_schedule') }}">
  <div class="form-row cols-4">
    <div class="form-group"><label class="form-label">From Date</label><input type="date" name="date_from" class="form-control" required></div>
    <div class="form-group"><label class="form-label">To Date</label><input type="date" name="date_to" class="form-control" required></div>
    <div class="form-group"><label class="form-label">Shift</label>
      <select name="shift_id" class="form-control">
        <option value="">Rest Day</option>
        {% for s in shifts %}<option value="{{ s.id }}">{{ s.shift_name }} ({{ s.time_in }}-{{ s.time_out }})</option>{% endfor %}
      </select>
    </div>
    <div class="form-group"><label class="form-label">Rest Day?</label>
      <select name="is_rest_day" class="form-control"><option value="0">Working Day</option><option value="1">Rest Day</option></select>
    </div>
  </div>
  <div class="form-group">
    <label class="form-label">Employees (hold Ctrl for multiple)</label>
    <select name="employee_ids" class="form-control" multiple style="height:120px" required>
      {% for e in employees %}
      <option value="{{ e.id }}">{{ e.last_name }}, {{ e.first_name }} ({{ e.employee_no }})</option>
      {% endfor %}
    </select>
  </div>
  <button type="submit" class="btn btn-primary"><i class="ti ti-check"></i> Assign Schedule</button>
</form>
</div></div>

<!-- Add Shift Modal -->
<div class="modal-backdrop" id="addShiftModal">
<div class="modal-dialog">
  <div class="modal-header"><div class="modal-title">Add Shift Definition</div>
    <button class="btn btn-xs" onclick="closeModal('addShiftModal')"><i class="ti ti-x"></i></button>
  </div>
  <form method="post" action="{{ url_for('shifts.add_shift') }}">
  <div class="modal-body">
    <div class="form-group"><label class="form-label">Shift Name *</label><input name="shift_name" class="form-control" required placeholder="e.g. Morning A"></div>
    <div class="form-row cols-2">
      <div class="form-group"><label class="form-label">Time In *</label><input type="time" name="time_in" class="form-control" required></div>
      <div class="form-group"><label class="form-label">Time Out *</label><input type="time" name="time_out" class="form-control" required></div>
    </div>
    <div class="form-row cols-2">
      <div class="form-group"><label class="form-label">Break (minutes)</label><input name="break_minutes" type="number" class="form-control" value="60"></div>
      <div class="form-group"><label class="form-label">Color</label><input name="color_hex" type="color" class="form-control" value="#3B82F6" style="height:36px;padding:4px"></div>
    </div>
    <div class="form-group">
      <label class="form-label">Overnight shift?</label>
      <select name="is_overnight" class="form-control"><option value="0">No</option><option value="1">Yes (crosses midnight)</option></select>
    </div>
  </div>
  <div class="modal-footer">
    <button type="button" class="btn" onclick="closeModal('addShiftModal')">Cancel</button>
    <button type="submit" class="btn btn-primary"><i class="ti ti-check"></i> Save Shift</button>
  </div>
  </form>
</div></div>

<!-- Add Template Modal -->
<div class="modal-backdrop" id="addTemplateModal">
<div class="modal-dialog" style="max-width:600px">
  <div class="modal-header">
    <div class="modal-title">New Schedule Template</div>
    <button class="btn btn-xs" onclick="closeModal('addTemplateModal')"><i class="ti ti-x"></i></button>
  </div>
  <form method="post" action="{{ url_for('shifts.save_template') }}">
  <div class="modal-body">
    <div class="form-row cols-2">
      <div class="form-group"><label class="form-label">Template Name *</label>
        <input name="template_name" class="form-control" required placeholder="e.g. Regular MWF"></div>
      <div class="form-group"><label class="form-label">Template Type</label>
        <select name="template_type" class="form-control" id="tmplType" onchange="showTypeFields()">
          <option value="WEEKLY">Weekly (fixed days)</option>
          <option value="DAILY">Daily (same shift every day)</option>
          <option value="STAGGERED">Staggered (rotating shifts)</option>
          <option value="COMPRESSED">Compressed (4-day work week)</option>
        </select>
      </div>
    </div>
    <div class="form-row cols-2">
      <div class="form-group"><label class="form-label">Payroll Group</label>
        <select name="applies_to_group" class="form-control">
          <option value="">All Employees</option>
          <option value="WEEKLY">Weekly</option>
          <option value="MONTHLY">Monthly</option>
        </select>
      </div>
      <div class="form-group"><label class="form-label">Default Shift</label>
        <select name="default_shift_id" class="form-control" id="defaultShift">
          <option value="">— None —</option>
          {% for s in shifts %}<option value="{{ s.id }}">{{ s.shift_name }}</option>{% endfor %}
        </select>
      </div>
    </div>

    <div id="weeklyFields">
      <label class="form-label">Work Days</label>
      <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
        {% for day in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] %}
        <label style="display:flex;align-items:center;gap:4px;padding:6px 12px;border:1.5px solid #e5e7eb;border-radius:6px;cursor:pointer;font-size:13px">
          <input type="checkbox" name="work_days" value="{{ loop.index }}"
            {% if day not in ['Sat','Sun'] %}checked{% endif %}> {{ day }}
        </label>
        {% endfor %}
      </div>
    </div>

    <div id="staggeredFields" style="display:none">
      <label class="form-label">Rotation Pattern</label>
      <div class="form-row cols-2">
        <div class="form-group"><label class="form-label" style="font-size:11px">Week A Shift</label>
          <select name="week_a_shift" class="form-control">
            {% for s in shifts %}<option value="{{ s.id }}">{{ s.shift_name }}</option>{% endfor %}
          </select>
        </div>
        <div class="form-group"><label class="form-label" style="font-size:11px">Week B Shift</label>
          <select name="week_b_shift" class="form-control">
            {% for s in shifts %}<option value="{{ s.id }}">{{ s.shift_name }}</option>{% endfor %}
          </select>
        </div>
      </div>
    </div>

    <div id="compressedFields" style="display:none">
      <label class="form-label">Compressed Work Days (pick 4)</label>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        {% for day in ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'] %}
        <label style="display:flex;align-items:center;gap:4px;padding:6px 12px;border:1.5px solid #e5e7eb;border-radius:6px;cursor:pointer;font-size:13px">
          <input type="checkbox" name="compressed_days" value="{{ loop.index }}"
            {% if day in ['Mon','Tue','Wed','Thu'] %}checked{% endif %}> {{ day }}
        </label>
        {% endfor %}
      </div>
      <p style="font-size:11px;color:#9ca3af;margin-top:6px">Employees work 10hrs/day on selected days</p>
    </div>

    <input type="hidden" name="template_data" id="template_data">
  </div>
  <div class="modal-footer">
    <button type="button" class="btn" onclick="closeModal('addTemplateModal')">Cancel</button>
    <button type="submit" class="btn btn-primary" onclick="buildTemplateData()"><i class="ti ti-check"></i> Save Template</button>
  </div>
  </form>
</div></div>

<script>
function showTypeFields() {
  const t = document.getElementById('tmplType').value;
  document.getElementById('weeklyFields').style.display = ['WEEKLY','DAILY'].includes(t) ? 'block' : 'none';
  document.getElementById('staggeredFields').style.display = t === 'STAGGERED' ? 'block' : 'none';
  document.getElementById('compressedFields').style.display = t === 'COMPRESSED' ? 'block' : 'none';
}
function buildTemplateData() {
  const t = document.getElementById('tmplType').value;
  let data = { type: t };
  if (t === 'WEEKLY' || t === 'DAILY') {
    data.work_days = [...document.querySelectorAll('input[name="work_days"]:checked')].map(i=>parseInt(i.value));
  }
  if (t === 'STAGGERED') {
    data.week_a = document.querySelector('[name="week_a_shift"]').value;
    data.week_b = document.querySelector('[name="week_b_shift"]').value;
  }
  if (t === 'COMPRESSED') {
    data.work_days = [...document.querySelectorAll('input[name="compressed_days"]:checked')].map(i=>parseInt(i.value));
    data.hours_per_day = 10;
  }
  document.getElementById('template_data').value = JSON.stringify(data);
}
</script>
{% endblock %}
'''
open('app/templates/shifts/index.html', 'w', encoding='utf-8').write(shifts_index)
print("OK: shifts/index.html rebuilt")

# ── 2. New attendance dashboard template ─────────────────────────────────────
os.makedirs('app/templates/shifts', exist_ok=True)
attendance_dash = r'''{% extends 'base.html' %}
{% block title %}Attendance Dashboard{% endblock %}
{% block page_title %}Attendance Dashboard{% endblock %}
{% block breadcrumb %}<a href="{{ url_for('shifts.index') }}">Shifts</a> / Attendance Dashboard{% endblock %}
{% block topbar_actions %}
<input type="date" id="dashDate" value="{{ today }}" onchange="loadDashboard()" class="form-control" style="width:160px">
<select id="deptFilter" class="form-control" style="width:160px" onchange="loadDashboard()">
  <option value="">All Departments</option>
  {% for d in departments %}<option value="{{ d.id }}">{{ d.name }}</option>{% endfor %}
</select>
{% endblock %}
{% block content %}

<div class="stats-grid mb-16" id="statsGrid">
  <div class="stat-card"><div class="stat-icon blue"><i class="ti ti-users"></i></div><div class="stat-val" id="stat-total">—</div><div class="stat-label">Total Active</div></div>
  <div class="stat-card"><div class="stat-icon green"><i class="ti ti-circle-check"></i></div><div class="stat-val" id="stat-present">—</div><div class="stat-label">Present</div></div>
  <div class="stat-card"><div class="stat-icon red"><i class="ti ti-user-off"></i></div><div class="stat-val" id="stat-absent">—</div><div class="stat-label">Absent</div></div>
  <div class="stat-card"><div class="stat-icon amber"><i class="ti ti-clock"></i></div><div class="stat-val" id="stat-late">—</div><div class="stat-label">Late</div></div>
  <div class="stat-card"><div class="stat-icon blue"><i class="ti ti-player-play"></i></div><div class="stat-val" id="stat-ot">—</div><div class="stat-label">With OT</div></div>
  <div class="stat-card"><div class="stat-icon gray"><i class="ti ti-calendar-off"></i></div><div class="stat-val" id="stat-notlogged">—</div><div class="stat-label">Not Logged</div></div>
</div>

<div class="grid-2 mb-16">
  <div class="card">
    <div class="card-header"><div class="card-title"><i class="ti ti-chart-pie"></i> Status Breakdown</div></div>
    <div class="card-body" style="position:relative;height:220px">
      <canvas id="statusChart" role="img" aria-label="Attendance status pie chart"></canvas>
    </div>
  </div>
  <div class="card">
    <div class="card-header"><div class="card-title"><i class="ti ti-chart-bar"></i> By Department</div></div>
    <div class="card-body" style="position:relative;height:220px">
      <canvas id="deptChart" role="img" aria-label="Department attendance bar chart"></canvas>
    </div>
  </div>
</div>

<div class="card">
  <div class="card-header" style="display:flex;align-items:center;justify-content:space-between">
    <div class="card-title"><i class="ti ti-fingerprint"></i> Employee Attendance Log</div>
    <div style="display:flex;gap:8px">
      <input type="text" id="empSearch" placeholder="Search employee..." class="form-control" style="width:200px" oninput="filterTable()">
      <select id="statusFilter" class="form-control" style="width:140px" onchange="filterTable()">
        <option value="">All Status</option>
        <option value="Present">Present</option>
        <option value="Late">Late</option>
        <option value="Absent">Absent</option>
        <option value="OT">With OT</option>
        <option value="Not Logged">Not Logged</option>
      </select>
    </div>
  </div>
  <div class="table-responsive">
    <table style="font-size:13px" id="attTable">
      <thead>
        <tr>
          <th>Employee</th><th>Dept</th><th>Shift</th>
          <th>Time In</th><th>Time Out</th><th>Hours</th><th>OT</th><th>Late</th><th>Status</th>
        </tr>
      </thead>
      <tbody id="attBody">
        <tr><td colspan="9" class="text-center text-muted" style="padding:24px">Loading...</td></tr>
      </tbody>
    </table>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
let statusChart, deptChart, allRows = [];

function loadDashboard() {
  const date = document.getElementById('dashDate').value;
  const dept = document.getElementById('deptFilter').value;
  fetch(`/shifts/api/attendance-dashboard?date=${date}&dept=${dept}`)
    .then(r => r.json())
    .then(data => {
      document.getElementById('stat-total').textContent = data.stats.total;
      document.getElementById('stat-present').textContent = data.stats.present;
      document.getElementById('stat-absent').textContent = data.stats.absent;
      document.getElementById('stat-late').textContent = data.stats.late;
      document.getElementById('stat-ot').textContent = data.stats.ot;
      document.getElementById('stat-notlogged').textContent = data.stats.not_logged;
      renderStatusChart(data.stats);
      renderDeptChart(data.by_dept);
      allRows = data.employees;
      renderTable(allRows);
    });
}

function renderStatusChart(s) {
  if (statusChart) statusChart.destroy();
  statusChart = new Chart(document.getElementById('statusChart'), {
    type: 'doughnut',
    data: {
      labels: ['Present','Late','Absent','Not Logged'],
      datasets: [{
        data: [s.present - s.late, s.late, s.absent, s.not_logged],
        backgroundColor: ['#16a34a','#d97706','#dc2626','#9ca3af'],
        borderWidth: 0
      }]
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { font: { size: 11 } } } } }
  });
}

function renderDeptChart(byDept) {
  if (deptChart) deptChart.destroy();
  const labels = byDept.map(d => d.dept);
  const present = byDept.map(d => d.present);
  const absent = byDept.map(d => d.absent);
  const h = Math.max(220, labels.length * 36 + 60);
  document.getElementById('deptChart').parentElement.style.height = h + 'px';
  deptChart = new Chart(document.getElementById('deptChart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [
        { label: 'Present', data: present, backgroundColor: '#16a34a' },
        { label: 'Absent', data: absent, backgroundColor: '#dc2626' }
      ]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: true } },
      scales: { x: { stacked: true }, y: { stacked: true, ticks: { font: { size: 10 } } } }
    }
  });
}

function renderTable(rows) {
  const tbody = document.getElementById('attBody');
  if (!rows.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted" style="padding:24px">No data for this date.</td></tr>';
    return;
  }
  tbody.innerHTML = rows.map(r => {
    const statusColors = { Present:'badge-green', Late:'badge-amber', Absent:'badge-red', OT:'badge-blue', 'Not Logged':'badge-gray' };
    const rowBg = r.status==='Absent' ? 'background:#fef2f2' : r.status==='Late' ? 'background:#fffbeb' : r.status==='OT' ? 'background:#eff6ff' : '';
    return `<tr style="${rowBg}" class="att-row" data-name="${r.name.toLowerCase()}" data-status="${r.status}">
      <td><div class="fw-600">${r.name}</div><div class="text-sm text-muted">${r.emp_no}</div></td>
      <td class="text-muted text-sm">${r.dept || '—'}</td>
      <td class="text-sm">${r.shift || '—'}</td>
      <td class="font-mono">${r.time_in || '—'}</td>
      <td class="font-mono">${r.time_out || '—'}</td>
      <td class="font-mono">${r.hours ? r.hours.toFixed(2) : '—'}</td>
      <td class="font-mono ${r.ot > 0 ? 'text-primary fw-600' : 'text-muted'}">${r.ot > 0 ? r.ot.toFixed(2) : '—'}</td>
      <td class="${r.late > 0 ? 'text-danger fw-600' : 'text-muted'}">${r.late > 0 ? r.late + 'm' : '—'}</td>
      <td><span class="badge ${statusColors[r.status] || 'badge-gray'}">${r.status}</span></td>
    </tr>`;
  }).join('');
}

function filterTable() {
  const q = document.getElementById('empSearch').value.toLowerCase();
  const s = document.getElementById('statusFilter').value;
  const filtered = allRows.filter(r =>
    (!q || r.name.toLowerCase().includes(q)) &&
    (!s || r.status === s || (s === 'OT' && r.ot > 0))
  );
  renderTable(filtered);
}

loadDashboard();
</script>
{% endblock %}
'''
open('app/templates/shifts/attendance_dashboard.html', 'w', encoding='utf-8').write(attendance_dash)
print("OK: shifts/attendance_dashboard.html created")

# ── 3. Patch shifts/__init__.py ──────────────────────────────────────────────
py = open('app/modules/shifts/__init__.py', encoding='utf-8').read()

# Add employees to index route
old_index = '''    return render_template('shifts/index.html', shifts=shifts, templates=templates)'''
new_index = '''    employees = g.db.execute("SELECT id,employee_no,last_name,first_name FROM employees WHERE status='ACTIVE' ORDER BY last_name").fetchall()
    return render_template('shifts/index.html', shifts=shifts, templates=templates, employees=employees)'''
py = py.replace(old_index, new_index)

# Add new routes before the end
new_routes = '''
@bp.route('/attendance-dashboard')
@login_required
def attendance_dashboard():
    from datetime import date as dt_date
    today = dt_date.today().strftime('%Y-%m-%d')
    departments = g.db.execute("SELECT * FROM departments WHERE is_active=1 ORDER BY name").fetchall()
    return render_template('shifts/attendance_dashboard.html', today=today, departments=departments)

@bp.route('/api/attendance-dashboard')
@login_required
def api_attendance_dashboard():
    req_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    dept_filter = request.args.get('dept', '')

    emp_query = """SELECT e.id, e.employee_no, e.last_name, e.first_name,
        d.name as dept_name, sd.shift_name, sd.time_in as sched_in, sd.time_out as sched_out
        FROM employees e
        LEFT JOIN departments d ON e.department_id=d.id
        LEFT JOIN employee_schedules es ON es.employee_id=e.id AND es.schedule_date=?
        LEFT JOIN shift_definitions sd ON es.shift_id=sd.id
        WHERE e.status='ACTIVE'"""
    emp_params = [req_date]
    if dept_filter:
        emp_query += " AND e.department_id=?"
        emp_params.append(dept_filter)
    emp_query += " ORDER BY e.last_name"
    employees = g.db.execute(emp_query, emp_params).fetchall()

    att_map = {}
    att_rows = g.db.execute("""SELECT employee_id, time_in, time_out, total_hours,
        ot_hours, late_minutes, is_absent FROM attendance WHERE work_date=?""", (req_date,)).fetchall()
    for a in att_rows:
        att_map[a['employee_id']] = a

    rows = []
    stats = {'total':0,'present':0,'absent':0,'late':0,'ot':0,'not_logged':0}
    dept_map = {}

    for e in employees:
        stats['total'] += 1
        a = att_map.get(e['id'])
        dept = e['dept_name'] or 'Unknown'
        if dept not in dept_map:
            dept_map[dept] = {'dept':dept,'present':0,'absent':0}

        if not a:
            status = 'Not Logged'
            stats['not_logged'] += 1
            time_in = time_out = None
            hours = ot = late = 0
        elif a['is_absent']:
            status = 'Absent'
            stats['absent'] += 1
            dept_map[dept]['absent'] += 1
            time_in = time_out = None
            hours = ot = late = 0
        else:
            dept_map[dept]['present'] += 1
            stats['present'] += 1
            time_in = a['time_in']
            time_out = a['time_out']
            hours = a['total_hours'] or 0
            ot = a['ot_hours'] or 0
            late = a['late_minutes'] or 0
            if late > 0:
                status = 'Late'
                stats['late'] += 1
            elif ot > 0:
                status = 'OT'
                stats['ot'] += 1
            else:
                status = 'Present'

        rows.append({
            'emp_no': e['employee_no'],
            'name': f"{e['last_name']}, {e['first_name']}",
            'dept': dept,
            'shift': f"{e['shift_name']} ({e['sched_in']}-{e['sched_out']})" if e['shift_name'] else None,
            'time_in': time_in,
            'time_out': time_out,
            'hours': hours,
            'ot': ot,
            'late': late,
            'status': status
        })

    return jsonify({
        'stats': stats,
        'employees': rows,
        'by_dept': list(dept_map.values())
    })

@bp.route('/templates/<int:tmpl_id>/apply', methods=['POST'])
@login_required
def apply_template(tmpl_id):
    tmpl = g.db.execute("SELECT * FROM schedule_templates WHERE id=?", (tmpl_id,)).fetchone()
    if not tmpl:
        flash('Template not found.', 'error')
        return redirect(url_for('shifts.index'))
    flash(f'Template "{tmpl["template_name"]}" applied. Use Assign Schedule to set dates.', 'info')
    return redirect(url_for('shifts.index'))

@bp.route('/templates/<int:tmpl_id>/delete', methods=['POST'])
@login_required
def delete_template(tmpl_id):
    g.db.execute("DELETE FROM schedule_templates WHERE id=?", (tmpl_id,))
    g.db.commit()
    flash('Template deleted.', 'success')
    return redirect(url_for('shifts.index'))
'''

py = py + new_routes
open('app/modules/shifts/__init__.py', 'w', encoding='utf-8').write(py)
print("OK: shifts/__init__.py updated")

# ── 4. Add schedule history to employee view.html ────────────────────────────
view = open('app/templates/employees/view.html', encoding='utf-8').read()

schedule_section = '''
<div class="card" style="margin-top:16px">
  <div class="card-header" style="display:flex;align-items:center;justify-content:space-between">
    <div class="card-title"><i class="ti ti-calendar-week"></i> Schedule History</div>
    <form method="get" style="display:flex;gap:8px;align-items:center">
      <input type="hidden" name="tk_month" value="{{ tk_month }}">
      <input type="month" name="sch_month" value="{{ sch_month }}"
        style="border:1px solid #e5e7eb;border-radius:6px;padding:4px 10px;font-size:13px">
      <button type="submit" class="btn btn-sm"><i class="ti ti-filter"></i> Filter</button>
    </form>
  </div>
  <div class="table-responsive">
    <table style="font-size:12px">
      <thead><tr><th>Date</th><th>Shift</th><th>Time In</th><th>Time Out</th><th>Break</th><th>Type</th></tr></thead>
      <tbody>
      {% for s in schedule_history %}
      <tr>
        <td class="fw-600">{{ s.schedule_date }}</td>
        <td>
          {% if s.is_rest_day %}<span class="badge badge-gray">Rest Day</span>
          {% elif s.shift_name %}<span style="display:inline-flex;align-items:center;gap:6px">
            <span style="width:10px;height:10px;border-radius:2px;background:{{ s.color_hex or "#3B82F6" }};display:inline-block"></span>
            {{ s.shift_name }}
          </span>
          {% else %}—{% endif %}
        </td>
        <td class="font-mono">{{ s.time_in or '—' }}</td>
        <td class="font-mono">{{ s.time_out or '—' }}</td>
        <td class="text-muted">{{ s.break_minutes ~ ' min' if s.break_minutes else '—' }}</td>
        <td class="text-muted text-sm">{{ s.schedule_type or 'REGULAR' }}</td>
      </tr>
      {% else %}
      <tr><td colspan="6" class="text-center text-muted" style="padding:20px">No schedule records found.</td></tr>
      {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}'''

view = view.replace('{% endblock %}', schedule_section, 1)
open('app/templates/employees/view.html', 'w', encoding='utf-8').write(view)
print("OK: employees/view.html — schedule history added")

# ── 5. Patch employees/__init__.py to pass schedule history ──────────────────
emp_py = open('app/modules/employees/__init__.py', encoding='utf-8').read()

old_return = '''    departments = g.db.execute("SELECT * FROM departments WHERE is_active=1").fetchall()
    return render_template('employees/view.html', emp=emp, loans=loans, leaves=leaves,
                           recent_payroll=recent_payroll, departments=departments,
                           attendance_history=attendance_history, tk_stats=tk_stats,
                           tk_month=month_filter)'''

new_return = '''    # Schedule history
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

emp_py = emp_py.replace(old_return, new_return)
open('app/modules/employees/__init__.py', 'w', encoding='utf-8').write(emp_py)
print("OK: employees/__init__.py — schedule history query added")

print("\nAll done! Restart the server and check:")
print("  1. Shifts → New Template button")
print("  2. Shifts → Attendance Dashboard button")
print("  3. Any employee profile → Schedule History section at bottom")
