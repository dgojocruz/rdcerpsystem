new_html = '''{% extends 'base.html' %}
{% block title %}New Pay Period{% endblock %}
{% block page_title %}New Pay Period{% endblock %}
{% block breadcrumb %}<a href="{{ url_for('payroll.index') }}">Payroll</a> / New Period{% endblock %}
{% block content %}
<div class="card" style="max-width:720px">
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
    style="border:2px solid #e5e7solid #e5e7eb;border-radius:10px;padding:16px 12px;text-align:center;cursor:pointer;transition:.15s">
    <i class="ti ti-calendar-month" style="font-size:24px;color:#6b7280"></i>
    <div style="font-weight:600;margin-top:6px;font-size:14px">Monthly</div>
    <div style="font-size:11px;color:#9ca3af;margin-top:2px">Full month</div>
  </div>
</div>

<form method="post" id="periodForm">
  <input type="hidden" name="period_type" id="period_type" value="">
  <input type="hidden" name="included_dates" id="included_dates" value="">

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
      <input type="date" name="date_from" id="date_from" class="form-control" required onchange="buildCalendar()">
    </div>
    <div class="form-group">
      <label class="form-label">Date To</label>
      <input type="date" name="date_to" id="date_to" class="form-control" required onchange="buildCalendar()">
    </div>
  </div>

  <div id="calendar_section" style="display:none;margin-bottom:20px">
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
      <label class="form-label" style="margin:0">
        <i class="ti ti-calendar-check" style="vertical-align:-2px"></i>
        Included Work Dates
        <span style="font-size:11px;color:#9ca3af;font-weight:400">(uncheck to exclude a day from this payroll)</span>
      </label>
      <div style="display:flex;gap:6px">
        <button type="button" onclick="selectAll(true)" style="font-size:11px;padding:3px 10px;border:1px solid #e5e7eb;border-radius:5px;background:#fff;cursor:pointer">All</button>
        <button type="button" onclick="selectAll(false)" style="font-size:11px;padding:3px 10px;border:1px solid #e5e7eb;border-radius:5px;background:#fff;cursor:pointer">None</button>
        <button type="button" onclick="selectWeekdays()" style="font-size:11px;padding:3px 10px;border:1px solid #e5e7eb;border-radius:5px;background:#fff;cursor:pointer">Weekdays only</button>
      </div>
    </div>
    <div id="calendar_grid" style="display:flex;flex-wrap:wrap;gap:6px"></div>
    <div style="margin-top:8px;font-size:12px;color:#6b7280">
      <span id="included_count">0</span> days included for payroll computation
    </div>
  </div>

  <div class="d-flex gap-8 justify-between">
    <a href="{{ url_for('payroll.index') }}" class="btn">Cancel</a>
    <button type="submit" class="btn btn-primary" id="submitBtn" disabled onclick="saveIncluded()">
      <i class="ti ti-arrow-right"></i> Create & Compute
    </button>
  </div>
</form>
</div></div>

<style>
.day-chip{display:inline-flex;flex-direction:column;align-items:center;width:52px;padding:6px 4px;border-radius:8px;border:1.5px solid #e5e7eb;cursor:pointer;font-size:11px;user-select:none;transition:.1s}
.day-chip.included{background:#eff6ff;border-color:#2563eb;color:#1d4ed8}
.day-chip.excluded{background:#f9fafb;border-color:#e5e7eb;color:#9ca3af;text-decoration:line-through}
.day-chip.weekend{background:#faf5ff;border-color:#d8b4fe;color:#7c3aed}
.day-chip .day-name{font-weight:600;font-size:10px}
.day-chip .day-num{font-size:14px;font-weight:700;margin-top:1px}
</style>

<script>
const MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
const DAYS = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
let currentType = '';
let dayStates = {};

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
  const now = new Date();
  const ym = now.getFullYear() + '-' + String(now.getMonth()+1).padStart(2,'0');
  if (!document.getElementById('ref_month').value)
    document.getElementById('ref_month').value = ym;
  if (type === 'WEEKLY' && !document.getElementById('week_start').value) {
    const d = new Date();
    d.setDate(d.getDate() - ((d.getDay()+6)%7));
    document.getElementById('week_start').value = d.toISOString().split('T')[0];
  }
  updateDates();
}

function updateDates() {
  if (!currentType) return;
  const monthVal = document.getElementById('ref_month').value;
  let dateFrom, dateTo, label;
  if (currentType === 'WEEKLY') {
    const ws = document.getElementById('week_start').value;
    if (!ws) return;
    const start = new Date(ws + 'T00:00:00');
    const end = new Date(ws + 'T00:00:00');
    end.setDate(end.getDate() + 6);
    dateFrom = ws;
    dateTo = end.toISOString().split('T')[0];
    label = `Week of ${MONTHS[start.getMonth()]} ${start.getDate()}-${end.getDate()}, ${start.getFullYear()}`;
  } else if (currentType === 'SEMI_MONTHLY') {
    const half = document.querySelector('input[name="semi_half"]:checked');
    if (!half || !monthVal) return;
    const [yr, mo] = monthVal.split('-').map(Number);
    if (half.value === '1ST') {
      dateFrom = `${yr}-${String(mo).padStart(2,'0')}-01`;
      dateTo   = `${yr}-${String(mo).padStart(2,'0')}-15`;
      label = `${MONTHS[mo-1]} 1-15, ${yr}`;
    } else {
      const lastDay = new Date(yr, mo, 0).getDate();
      dateFrom = `${yr}-${String(mo).padStart(2,'0')}-16`;
      dateTo   = `${yr}-${String(mo).padStart(2,'0')}-${lastDay}`;
      label = `${MONTHS[mo-1]} 16-${lastDay}, ${yr}`;
    }
  } else {
    if (!monthVal) return;
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
  buildCalendar();
}

function buildCalendar() {
  const from = document.getElementById('date_from').value;
  const to   = document.getElementById('date_to').value;
  if (!from || !to) return;
  const grid = document.getElementById('calendar_grid');
  grid.innerHTML = '';
  dayStates = {};
  let cur = new Date(from + 'T00:00:00');
  const end = new Date(to + 'T00:00:00');
  while (cur <= end) {
    const ds = cur.toISOString().split('T')[0];
    const dow = cur.getDay();
    const isWeekend = dow === 0 || dow === 6;
    dayStates[ds] = !isWeekend;
    const chip = document.createElement('div');
    chip.className = 'day-chip ' + (isWeekend ? 'excluded weekend' : 'included');
    chip.id = 'chip_' + ds;
    chip.innerHTML = `<span class="day-name">${DAYS[dow]}</span><span class="day-num">${cur.getDate()}</span><span style="font-size:9px">${MONTHS[cur.getMonth()]}</span>`;
    chip.onclick = () => toggleDay(ds);
    grid.appendChild(chip);
    cur.setDate(cur.getDate() + 1);
  }
  document.getElementById('calendar_section').style.display = 'block';
  updateCount();
}

function toggleDay(ds) {
  dayStates[ds] = !dayStates[ds];
  const chip = document.getElementById('chip_' + ds);
  const dow = new Date(ds + 'T00:00:00').getDay();
  const isWeekend = dow === 0 || dow === 6;
  chip.className = 'day-chip ' + (dayStates[ds] ? (isWeekend ? 'weekend included' : 'included') : 'excluded');
  updateCount();
}

function selectAll(val) {
  Object.keys(dayStates).forEach(ds => {
    dayStates[ds] = val;
    const dow = new Date(ds + 'T00:00:00').getDay();
    const isWeekend = dow === 0 || dow === 6;
    document.getElementById('chip_' + ds).className = 'day-chip ' + (val ? (isWeekend ? 'weekend included' : 'included') : 'excluded');
  });
  updateCount();
}

function selectWeekdays() {
  Object.keys(dayStates).forEach(ds => {
    const dow = new Date(ds + 'T00:00:00').getDay();
    const isWD = dow !== 0 && dow !== 6;
    dayStates[ds] = isWD;
    document.getElementById('chip_' + ds).className = 'day-chip ' + (isWD ? 'included' : 'excluded');
  });
  updateCount();
}

function updateCount() {
  const count = Object.values(dayStates).filter(Boolean).length;
  document.getElementById('included_count').textContent = count;
}

function saveIncluded() {
  const included = Object.entries(dayStates).filter(([,v])=>v).map(([k])=>k);
  document.getElementById('included_dates').value = included.join(',');
}
</script>
{% endblock %}
'''

open('app/templates/payroll/new_period.html', 'w', encoding='utf-8').write(new_html)
print("OK: new_period.html rebuilt with custom date selector")
