# ── 1. Rebuild new_period.html with smart auto-fill ─────────────────────────
new_period_html = '''{% extends 'base.html' %}
{% block title %}New Pay Period{% endblock %}
{% block page_title %}New Pay Period{% endblock %}
{% block breadcrumb %}<a href="{{ url_for('payroll.index') }}">Payroll</a> / New Period{% endblock %}
{% block content %}
<div class="card" style="max-width:680px">
<div class="card-header"><div class="card-title">Create Pay Period</div></div>
<div class="card-body">

<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:24px">
  <div id="btn-weekly" onclick="selectType('WEEKLY')"
    style="border:2px solid #e5e7eb;border-radius:10px;padding:16px 12px;text-align:center;cursor:pointer;transition:.15s">
    <i class="ti ti-calendar-week" style="font-size:24px;color:#6b7280"></i>
    <div style="font-weight:600;margin-top:6px;font-size:14px">Weekly</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">Every 7 days</div>
  </div>
  <div id="btn-semi" onclick="selectType('SEMI_MONTHLY')"
    style="border:2px solid #e5e7eb;border-radius:10px;padding:16px 12px;text-align:center;cursor:pointer;transition:.15s">
    <i class="ti ti-calendar-stats" style="font-size:24px;color:#6b7280"></i>
    <div style="font-weight:600;margin-top:6px;font-size:14px">Bi-Monthly</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">1st–15 / 16–end</div>
  </div>
  <div id="btn-monthly" onclick="selectType('MONTHLY')"
    style="border:2px solid #e5e7eb;border-radius:10px;padding:16px 12px;text-align:center;cursor:pointer;transition:.15s">
    <i class="ti ti-calendar-month" style="font-size:24px;color:#6b7280"></i>
    <div style="font-weight:600;margin-top:6px;font-size:14px">Monthly</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">Full month</div>
  </div>
</div>

<form method="post" id="periodForm">
  <input type="hidden" name="period_type" id="period_type" value="">

  <div class="form-group" id="semi_half_group" style="display:none">
    <label class="form-label">Which half?</label>
    <div style="display:flex;gap:10px">
      <label style="flex:1;border:1.5px solid #e5e7eb;border-radius:8px;padding:10px 14px;cursor:pointer;display:flex;align-items:center;gap:8px">
        <input type="radio" name="semi_half" value="1ST" onchange="updateDates()"> 1st Half (1–15)
      </label>
      <label style="flex:1;border:1.5px solid #e5e7eb;border-radius:8px;padding:10px 14px;cursor:pointer;display:flex;align-items:center;gap:8px">
        <input type="radio" name="semi_half" value="2ND" onchange="updateDates()"> 2nd Half (16–end)
      </label>
    </div>
  </div>

  <div class="form-row cols-2">
    <div class="form-group">
      <label class="form-label">Month</label>
      <input type="month" id="ref_month" class="form-control" onchange="updateDates()">
    </div>
    <div class="form-group" id="week_num_group" style="display:none">
      <label class="form-label">Week starting</label>
      <input type="date" id="week_start" class="form-control" onchange="updateDates()">
    </div>
    <div class="form-group">
      <label class="form-label">Payroll Group</label>
      <select name="payroll_group" class="form-control">
        <option value="ALL">All Employees</option>
        <option value="MONTHLY">Monthly Only</option>
        <option value="WEEKLY">Weekly Only</option>
      </select>
    </div>
  </div>

  <div style="background:#f9fafb;border-radius:10px;padding:14px 16px;margin-bottom:16px;display:none" id="preview_box">
    <div style="font-size:12px;color:#6b7280;margin-bottom:6px">Generated period</div>
    <div style="font-size:16px;font-weight:600" id="preview_label">—</div>
    <div style="font-size:13px;color:#6b7280;margin-top:4px" id="preview_dates">—</div>
  </div>

  <div class="form-group">
    <label class="form-label">Period Label <span style="color:#9ca3af;font-size:11px">(auto-filled, editable)</span></label>
    <input name="period_label" id="period_label" class="form-control" placeholder="Select a pay type above" required>
  </div>
  <div class="form-row cols-2">
    <div class="form-group">
      <label class="form-label">Date From</label>
      <input type="date" name="date_from" id="date_from" class="form-control" required>
    </div>
    <div class="form-group">
      <label class="form-label">Date To</label>
      <input type="date" name="date_to" id="date_to" class="form-control" required>
    </div>
  </div>

  <div class="d-flex gap-8 justify-between">
    <a href="{{ url_for('payroll.index') }}" class="btn">Cancel</a>
    <button type="submit" class="btn btn-primary" id="submitBtn" disabled>
      <i class="ti ti-arrow-right"></i> Create & Compute
    </button>
  </div>
</form>
</div></div>

<script>
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
let currentType = '';

function selectType(type) {
  currentType = type;
  document.getElementById('period_type').value = type;

  ['weekly','semi','monthly'].forEach(t => {
    const el = document.getElementById('btn-' + t);
    el.style.border = '2px solid #e5e7eb';
    el.style.background = '';
    el.querySelector('i').style.color = '#6b7280';
  });
  const map = {WEEKLY:'weekly', SEMI_MONTHLY:'semi', MONTHLY:'monthly'};
  const active = document.getElementById('btn-' + map[type]);
  active.style.border = '2px solid #2563eb';
  active.style.background = '#eff6ff';
  active.querySelector('i').style.color = '#2563eb';

  document.getElementById('semi_half_group').style.display = type === 'SEMI_MONTHLY' ? 'block' : 'none';
  document.getElementById('week_num_group').style.display = type === 'WEEKLY' ? 'block' : 'none';

  // Set default month to current
  const now = new Date();
  const ym = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0');
  if (!document.getElementById('ref_month').value)
    document.getElementById('ref_month').value = ym;
  if (type === 'WEEKLY' && !document.getElementById('week_start').value) {
    // Default to Monday of current week
    const d = new Date();
    d.setDate(d.getDate() - ((d.getDay()+6)%7));
    document.getElementById('week_start').value = d.toISOString().split('T')[0];
  }
  updateDates();
}

function updateDates() {
  if (!currentType) return;
  const monthVal = document.getElementById('ref_month').value;
  if (!monthVal && currentType !== 'WEEKLY') return;

  let dateFrom, dateTo, label;

  if (currentType === 'WEEKLY') {
    const ws = document.getElementById('week_start').value;
    if (!ws) return;
    const start = new Date(ws);
    const end = new Date(ws);
    end.setDate(end.getDate() + 6);
    dateFrom = ws;
    dateTo = end.toISOString().split('T')[0];
    label = `Week of ${MONTHS[start.getMonth()]} ${start.getDate()}–${end.getDate()}, ${start.getFullYear()}`;

  } else if (currentType === 'SEMI_MONTHLY') {
    const half = document.querySelector('input[name="semi_half"]:checked');
    if (!half) return;
    const [yr, mo] = monthVal.split('-').map(Number);
    if (half.value === '1ST') {
      dateFrom = `${yr}-${String(mo).padStart(2,'0')}-01`;
      dateTo   = `${yr}-${String(mo).padStart(2,'0')}-15`;
      label = `${MONTHS[mo-1]} 1–15, ${yr}`;
    } else {
      const lastDay = new Date(yr, mo, 0).getDate();
      dateFrom = `${yr}-${String(mo).padStart(2,'0')}-16`;
      dateTo   = `${yr}-${String(mo).padStart(2,'0')}-${lastDay}`;
      label = `${MONTHS[mo-1]} 16–${lastDay}, ${yr}`;
    }

  } else if (currentType === 'MONTHLY') {
    const [yr, mo] = monthVal.split('-').map(Number);
    const lastDay = new Date(yr, mo, 0).getDate();
    dateFrom = `${yr}-${String(mo).padStart(2,'0')}-01`;
    dateTo   = `${yr}-${String(mo).padStart(2,'0')}-${lastDay}`;
    label = `${MONTHS[mo-1]} ${yr} (Monthly)`;
  }

  document.getElementById('date_from').value = dateFrom;
  document.getElementById('date_to').value = dateTo;
  document.getElementById('period_label').value = label;
  document.getElementById('preview_label').textContent = label;
  document.getElementById('preview_dates').textContent = dateFrom + ' to ' + dateTo;
  document.getElementById('preview_box').style.display = 'block';
  document.getElementById('submitBtn').disabled = false;
}
</script>
{% endblock %}
'''

open('app/templates/payroll/new_period.html', 'w', encoding='utf-8').write(new_period_html)
print("OK: new_period.html rebuilt")

# ── 2. Update payroll index to show period type nicely ──────────────────────
payroll_index_html = open('app/templates/payroll/index.html', encoding='utf-8').read()

old_type_cell = '<td class="text-sm text-muted">{{ p.period_type }}</td>'
new_type_cell = '''<td>
  {% if "WEEKLY" in p.period_type %}<span class="badge badge-purple">Weekly</span>
  {% elif "SEMI" in p.period_type %}<span class="badge badge-blue">Bi-Monthly</span>
  {% elif "MONTHLY" in p.period_type %}<span class="badge badge-teal">Monthly</span>
  {% else %}<span class="badge badge-gray">{{ p.period_type }}</span>{% endif %}
</td>'''

if old_type_cell in payroll_index_html:
    payroll_index_html = payroll_index_html.replace(old_type_cell, new_type_cell)
    open('app/templates/payroll/index.html', 'w', encoding='utf-8').write(payroll_index_html)
    print("OK: payroll/index.html updated")
else:
    print("SKIP: index.html pattern not found")

print("\nAll done! Refresh the Payroll page and click New Pay Period.")
