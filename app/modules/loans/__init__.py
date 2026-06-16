from flask import Blueprint, render_template, request, redirect, url_for, g, jsonify, flash
from ..auth import login_required

bp = Blueprint('loans', __name__)

LOAN_CATEGORIES = {
    'SSS': ['SSS Salary Loan', 'SSS Calamity Loan', 'SSS Housing Loan'],
    'PAGIBIG': ['Pag-IBIG Multi-Purpose Loan', 'Pag-IBIG Calamity Loan', 'Pag-IBIG Housing Loan'],
    'PERSONAL': ['Cash Advance', 'Company Loan', 'Personal Loan'],
    'OTHER': ['House Rent', 'Water / Utilities', 'Others']
}

@bp.route('/')
@login_required
def index():
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', 'ACTIVE')
    q = """SELECT el.*, e.last_name, e.first_name, e.employee_no
           FROM employee_loans el JOIN employees e ON el.employee_id=e.id
           WHERE el.status LIKE ?"""
    params = [status_filter if status_filter else '%']
    if category_filter:
        q += " AND el.loan_category=?"
        params.append(category_filter)
    q += " ORDER BY e.last_name, el.created_at DESC"
    loans = g.db.execute(q, params).fetchall()
    totals = g.db.execute("""SELECT loan_category,
        COUNT(*) as count, SUM(outstanding_balance) as total_balance,
        SUM(monthly_amortization) as total_monthly
        FROM employee_loans WHERE status='ACTIVE' GROUP BY loan_category""").fetchall()
    return render_template('loans/index.html', loans=loans, totals=totals,
                           categories=LOAN_CATEGORIES, category_filter=category_filter,
                           status_filter=status_filter)

@bp.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'POST':
        f = request.form
        principal = float(f['principal_amount'])
        amort = float(f['monthly_amortization'])
        g.db.execute("""INSERT INTO employee_loans
            (employee_id,loan_category,loan_type,principal_amount,
             outstanding_balance,monthly_amortization,start_date,end_date,notes)
            VALUES (?,?,?,?,?,?,?,?,?)""",
            (f['employee_id'], f['loan_category'], f['loan_type'],
             principal, principal, amort, f.get('start_date',''), f.get('end_date',''),
             f.get('notes','')))
        g.db.commit()
        flash('Loan recorded.', 'success')
        return redirect(url_for('loans.index'))
    employees = g.db.execute("SELECT id,employee_no,last_name,first_name FROM employees WHERE status='ACTIVE' ORDER BY last_name").fetchall()
    return render_template('loans/form.html', employees=employees, categories=LOAN_CATEGORIES)

@bp.route('/<int:loan_id>/payment', methods=['POST'])
@login_required
def record_payment(loan_id):
    amount = float(request.form.get('amount', 0))
    loan = g.db.execute("SELECT * FROM employee_loans WHERE id=?", (loan_id,)).fetchone()
    if loan:
        new_balance = max(loan['outstanding_balance'] - amount, 0)
        new_paid = (loan['total_paid'] or 0) + amount
        status = 'PAID' if new_balance <= 0 else 'ACTIVE'
        g.db.execute("""UPDATE employee_loans SET outstanding_balance=?, total_paid=?, status=?
                       WHERE id=?""", (new_balance, new_paid, status, loan_id))
        g.db.commit()
        flash(f'Payment of ₱{amount:,.2f} recorded.', 'success')
    return redirect(url_for('loans.index'))

@bp.route('/api/employee/<int:emp_id>')
@login_required
def api_employee_loans(emp_id):
    loans = g.db.execute("""SELECT * FROM employee_loans
                            WHERE employee_id=? AND status='ACTIVE'""", (emp_id,)).fetchall()
    return jsonify([dict(l) for l in loans])
