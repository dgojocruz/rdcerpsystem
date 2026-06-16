# ── 1. Patch payroll/index.html — add Delete button ─────────────────────────
html = open('app/templates/payroll/index.html', encoding='utf-8').read()

old_actions = '''    <a href="{{ url_for('payroll.view_period', period_id=p.id) }}" class="btn btn-xs"><i class="ti ti-eye"></i> View</a>
    <a href="{{ url_for('payroll.export_excel', period_id=p.id) }}" class="btn btn-xs"><i class="ti ti-file-spreadsheet"></i> Excel</a>'''

new_actions = '''    <a href="{{ url_for('payroll.view_period', period_id=p.id) }}" class="btn btn-xs"><i class="ti ti-eye"></i> View</a>
    <a href="{{ url_for('payroll.export_excel', period_id=p.id) }}" class="btn btn-xs"><i class="ti ti-file-spreadsheet"></i> Excel</a>
    {% if p.status in ['OPEN','COMPUTED'] %}
    <form method="post" action="{{ url_for('payroll.delete_period', period_id=p.id) }}" style="display:inline"
      onsubmit="return confirm('Delete payroll period {{ p.period_label }}?\\nThis will remove all computed records for this period. This cannot be undone.')">
      <button class="btn btn-xs btn-danger" type="submit"><i class="ti ti-trash"></i> Delete</button>
    </form>
    {% endif %}'''

html = html.replace(old_actions, new_actions)
open('app/templates/payroll/index.html', 'w', encoding='utf-8').write(html)
print("OK: payroll/index.html patched")

# ── 2. Add delete route to payroll/__init__.py ───────────────────────────────
py = open('app/modules/payroll/__init__.py', encoding='utf-8').read()

delete_route = '''
@bp.route('/period/<int:period_id>/delete', methods=['POST'])
@login_required
def delete_period(period_id):
    period = g.db.execute("SELECT * FROM pay_periods WHERE id=?", (period_id,)).fetchone()
    if not period:
        flash("Pay period not found.", "error")
        return redirect(url_for("payroll.index"))
    if period["status"] == "RELEASED":
        flash("Cannot delete a released payroll period.", "error")
        return redirect(url_for("payroll.index"))
    if period["status"] == "APPROVED":
        flash("Cannot delete an approved payroll. Please contact your system administrator.", "error")
        return redirect(url_for("payroll.index"))
    label = period["period_label"]
    g.db.execute("DELETE FROM payroll WHERE pay_period_id=?", (period_id,))
    g.db.execute("DELETE FROM pay_periods WHERE id=?", (period_id,))
    g.db.commit()
    flash(f"Payroll period \\"{label}\\" and all its records have been deleted.", "success")
    return redirect(url_for("payroll.index"))
'''

# Insert before the last route (config route)
insert_before = "@bp.route('/config')"
py = py.replace(insert_before, delete_route + insert_before)
open('app/modules/payroll/__init__.py', 'w', encoding='utf-8').write(py)
print("OK: payroll/__init__.py — delete route added")
print("\nDone! Restart the server and you will see a red Delete button on OPEN/COMPUTED payroll periods.")
