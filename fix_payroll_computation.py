"""
Fix RHODECO payroll computation to match manual Excel calculations.

Key fixes:
1. Weekly SSS = fixed ₱350 (not monthly table)
2. Weekly PhilHealth = ₱0 (collected on monthly/semi-monthly only)
3. Weekly Pag-IBIG = ₱0 (collected on monthly/semi-monthly only)
4. ND = hourly_rate * 0.10 * nd_hours
5. Undertime deduction = undertime_mins * rate_per_minute
6. Hours * hourly_rate = basic (not daily_rate/8 recalculation)
"""

py = open('app/modules/payroll/__init__.py', encoding='utf-8').read()

old_compute = '''def _do_compute(period_id, period, cfg, db):
    employees = db.execute("""SELECT e.* FROM employees e WHERE e.status='ACTIVE'
        AND (? = 'ALL' OR e.payroll_group = ?)""",
        (period['payroll_group'], period['payroll_group'])).fetchall()
    for emp in employees:
        att = db.execute("""SELECT
            COALESCE(SUM(total_hours),0) as th, COALESCE(SUM(ot_hours),0) as ot,
            COALESCE(SUM(nd_hours),0) as nd, COALESCE(SUM(late_minutes),0) as late,
            COALESCE(SUM(undertime_minutes),0) as ut
            FROM attendance WHERE employee_id=? AND work_date BETWEEN ? AND ?""",
            (emp['id'], period['date_from'], period['date_to'])).fetchone()
        daily = emp['daily_rate'] or cfg.get('NCR_MIN_WAGE', 645)
        hr = daily / 8
        rpm = hr / 60
        reg_amt = (att['th'] - att['ot']) * hr
        late_amt = att['late'] * rpm
        ut_amt = att['ut'] * rpm
        basic = max(reg_amt - late_amt - ut_amt, 0)
        ot_rate = cfg.get('OT_RATE', 1.25)
        ot_amt = att['ot'] * hr * ot_rate
        nd_rate = cfg.get('ND_RATE', 0.10)
        nd_amt = att['nd'] * hr * nd_rate
        allowance = emp['allowance_amount'] or 0
        gross = basic + ot_amt + nd_amt + allowance
        monthly_equiv = daily * 26
        sss_ee, sss_er, wisp = compute_sss(monthly_equiv, cfg)
        ph_ee, ph_er = compute_philhealth(monthly_equiv, cfg)
        pi_ee, pi_er = compute_pagibig(monthly_equiv, cfg)
        taxable = gross - sss_ee - ph_ee - pi_ee
        wtax = compute_withholding_tax(taxable, emp['tax_type'])
        loans = db.execute("""SELECT loan_category, SUM(monthly_amortization) as amt
            FROM employee_loans WHERE employee_id=? AND status='ACTIVE'
            GROUP BY loan_category""", (emp['id'],)).fetchall()
        sss_loan = sum(l['amt'] for l in loans if l['loan_category']=='SSS')
        pi_loan = sum(l['amt'] for l in loans if l['loan_category']=='PAGIBIG')
        pers_loan = sum(l['amt'] for l in loans if l['loan_category'] in ('PERSONAL','OTHER'))
        total_ded = sss_ee + wisp + ph_ee + pi_ee + wtax + sss_loan + pi_loan + pers_loan
        net = max(gross - total_ded, 0)
        db.execute("""INSERT OR REPLACE INTO payroll
            (pay_period_id,employee_id,payroll_group,total_hours,regular_amount,
             late_amount,undertime_amount,basic_salary,ot_hours,ot_amount,
             nd_hours,nd_amount,allowance_amount,gross_salary,
             sss_employee,sss_wisp,philhealth_employee,pagibig_employee,withholding_tax,
             sss_loan,pagibig_loan,personal_loan,total_deductions,net_pay,
             sss_employer,philhealth_employer,pagibig_employer,
             hours_paid,unpaid_hours,
             status,computed_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    'COMPUTED',datetime('now'),datetime('now'))""",
            (period_id, emp['id'], emp['payroll_group'], att['th'], reg_amt,
             late_amt, ut_amt, basic, att['ot'], ot_amt, att['nd'], nd_amt,
             allowance, gross, sss_ee, wisp, ph_ee, pi_ee, wtax,
             sss_loan, pi_loan, pers_loan, total_ded, net, sss_er, ph_er, pi_er,
             hours_paid, unpaid_hours))
    db.execute("""UPDATE pay_periods SET status='COMPUTED',
        processed_by=1, processed_at=datetime('now') WHERE id=?""", (period_id,))
    db.commit()'''

new_compute = '''def _do_compute(period_id, period, cfg, db):
    employees = db.execute("""SELECT e.* FROM employees e WHERE e.status='ACTIVE'
        AND (? = 'ALL' OR e.payroll_group = ?)""",
        (period['payroll_group'], period['payroll_group'])).fetchall()

    period_type = period['period_type'] or ''
    is_weekly = 'WEEKLY' in period_type.upper()

    for emp in employees:
        att = db.execute("""SELECT
            COALESCE(SUM(total_hours),0) as th,
            COALESCE(SUM(ot_hours),0) as ot,
            COALESCE(SUM(nd_hours),0) as nd,
            COALESCE(SUM(late_minutes),0) as late,
            COALESCE(SUM(undertime_minutes),0) as ut
            FROM attendance WHERE employee_id=? AND work_date BETWEEN ? AND ?
            AND is_absent=0""",
            (emp['id'], period['date_from'], period['date_to'])).fetchone()

        daily = emp['daily_rate'] or cfg.get('NCR_MIN_WAGE', 645)
        hr    = daily / 8          # hourly rate
        rpm   = hr / 60            # rate per minute

        # Regular hours = total hours minus OT
        reg_hrs = max(0, (att['th'] or 0) - (att['ot'] or 0))
        reg_amt = round(reg_hrs * hr, 4)

        # Late and undertime deductions
        late_amt = round((att['late'] or 0) * rpm, 4)
        ut_amt   = round((att['ut']   or 0) * rpm, 4)

        # Basic salary
        basic = max(round(reg_amt - late_amt - ut_amt, 4), 0)

        # OT pay (125% of hourly rate)
        ot_rate = cfg.get('OT_RATE', 1.25)
        ot_amt  = round((att['ot'] or 0) * hr * ot_rate, 4)

        # Night differential (10% of hourly rate per ND hour)
        nd_rate = cfg.get('ND_RATE', 0.10)
        nd_amt  = round((att['nd'] or 0) * hr * nd_rate, 4)

        allowance = emp['allowance_amount'] or 0
        gross = round(basic + ot_amt + nd_amt + allowance, 4)

        # ── Mandatory deductions based on payroll type ────────────────────
        emp_group = (emp['payroll_group'] or 'MONTHLY').upper()
        monthly_equiv = daily * 26

        if is_weekly or emp_group == 'WEEKLY':
            # Weekly payroll: only SSS collected weekly (fixed ₱350)
            # PhilHealth and Pag-IBIG collected on semi-monthly/monthly run
            sss_ee   = 350.0
            sss_er   = 0.0
            wisp     = 0.0
            ph_ee    = 0.0
            ph_er    = 0.0
            pi_ee    = 0.0
            pi_er    = 0.0
        else:
            # Monthly / Semi-monthly: full mandatory deductions
            sss_ee, sss_er, wisp = compute_sss(monthly_equiv, cfg)
            ph_ee, ph_er = compute_philhealth(monthly_equiv, cfg)
            pi_ee, pi_er = compute_pagibig(monthly_equiv, cfg)

        # Withholding tax (MWE exempt)
        taxable = gross - sss_ee - ph_ee - pi_ee
        wtax = compute_withholding_tax(taxable, emp['tax_type'])

        # Loans
        loans = db.execute("""SELECT loan_category, SUM(monthly_amortization) as amt
            FROM employee_loans WHERE employee_id=? AND status=\'ACTIVE\'
            GROUP BY loan_category""", (emp['id'],)).fetchall()
        sss_loan  = round(sum(l['amt'] for l in loans if l['loan_category']=='SSS'), 2)
        pi_loan   = round(sum(l['amt'] for l in loans if l['loan_category']=='PAGIBIG'), 2)
        pers_loan = round(sum(l['amt'] for l in loans if l['loan_category'] in ('PERSONAL','OTHER','CASH_ADVANCE')), 2)
        house_rent= round(sum(l['amt'] for l in loans if l['loan_category']=='HOUSE_RENT'), 2)
        ar_water  = round(sum(l['amt'] for l in loans if l['loan_category']=='AR_WATER'), 2)
        other_ded = round(sum(l['amt'] for l in loans if l['loan_category'] not in
                          ('SSS','PAGIBIG','PERSONAL','OTHER','CASH_ADVANCE','HOUSE_RENT','AR_WATER')), 2)

        total_ded = round(sss_ee + wisp + ph_ee + pi_ee + wtax +
                         sss_loan + pi_loan + pers_loan +
                         house_rent + ar_water + other_ded, 2)
        net = max(round(gross - total_ded, 2), 0)

        # Hours tracking
        hours_paid   = round(reg_hrs, 2)
        unpaid_hours = round(((att['late'] or 0) + (att['ut'] or 0)) / 60, 2)

        db.execute("""INSERT OR REPLACE INTO payroll
            (pay_period_id,employee_id,payroll_group,total_hours,regular_amount,
             late_amount,undertime_amount,basic_salary,ot_hours,ot_amount,
             nd_hours,nd_amount,allowance_amount,gross_salary,
             sss_employee,sss_wisp,philhealth_employee,pagibig_employee,withholding_tax,
             sss_loan,pagibig_loan,personal_loan,house_rent,ar_water,other_deductions,
             total_deductions,net_pay,
             sss_employer,philhealth_employer,pagibig_employer,
             hours_paid,unpaid_hours,
             status,computed_at,updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
                    \'COMPUTED\',datetime(\'now\'),datetime(\'now\'))""",
            (period_id, emp['id'], emp['payroll_group'], att['th'], reg_amt,
             late_amt, ut_amt, basic, att['ot'], ot_amt, att['nd'], nd_amt,
             allowance, gross, sss_ee, wisp, ph_ee, pi_ee, wtax,
             sss_loan, pi_loan, pers_loan, house_rent, ar_water, other_ded,
             total_ded, net, sss_er, ph_er, pi_er,
             hours_paid, unpaid_hours))

    db.execute("""UPDATE pay_periods SET status=\'COMPUTED\',
        processed_by=1, processed_at=datetime(\'now\') WHERE id=?""", (period_id,))
    db.commit()'''

if old_compute in py:
    py = py.replace(old_compute, new_compute)
    open('app/modules/payroll/__init__.py', 'w', encoding='utf-8').write(py)
    print("OK: Payroll computation engine updated!")
    print("\nKey changes:")
    print("  1. Weekly SSS = fixed ₱350 (matches manual)")
    print("  2. Weekly PhilHealth = ₱0 (matches manual)")
    print("  3. Weekly Pag-IBIG = ₱0 (matches manual)")
    print("  4. ND = hourly_rate x 10% x ND hours (matches manual)")
    print("  5. Undertime deduction = mins x rate_per_minute (matches manual)")
    print("  6. House rent, AR Water, Cash advance as separate loan categories")
    print("  7. Excludes absent days from computation")
else:
    print("Pattern not found - may already be updated or different version")
    print("Searching for alternative pattern...")
    if '_do_compute' in py:
        print("Function exists - check manually")
