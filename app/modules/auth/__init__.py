from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import check_password_hash

bp = Blueprint('auth', __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard.index'))
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = g.db.execute(
            "SELECT * FROM users WHERE username=? AND is_active=1", (username,)
        ).fetchone()
        if user and check_password_hash(user['password_hash'], password):
            session.permanent = True
            session['user'] = {
                'id': user['id'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role'],
            }
            g.db.execute("UPDATE users SET last_login=datetime('now') WHERE id=?", (user['id'],))
            g.db.commit()
            return redirect(request.args.get('next') or url_for('dashboard.index'))
        error = 'Invalid username or password.'
    return render_template('auth/login.html', error=error)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
