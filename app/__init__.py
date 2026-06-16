import os, sqlite3
from flask import Flask, g, session

def get_db(app):
    db = sqlite3.connect(app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    db.execute("PRAGMA journal_mode = WAL")
    return db

def create_app(client_id=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    from .config import get_config
    cfg = get_config(client_id)
    app.config.from_object(cfg)
    os.makedirs(app.config['INSTANCE_PATH'], exist_ok=True)
    os.makedirs(app.config.get('UPLOAD_FOLDER', app.config['INSTANCE_PATH']+'/uploads'), exist_ok=True)

    from .database import init_db
    with app.app_context():
        init_db(app)

    from .modules.auth import bp as auth_bp
    from .modules.dashboard import bp as dash_bp
    from .modules.employees import bp as emp_bp
    from .modules.timekeeping import bp as time_bp
    from .modules.payroll import bp as pay_bp
    from .modules.leaves import bp as leave_bp
    from .modules.shifts import bp as shift_bp
    from .modules.loans import bp as loan_bp
    from .modules.reports import bp as report_bp
    from .modules.settings import bp as settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dash_bp)
    app.register_blueprint(emp_bp, url_prefix='/employees')
    app.register_blueprint(time_bp, url_prefix='/timekeeping')
    app.register_blueprint(pay_bp, url_prefix='/payroll')
    app.register_blueprint(leave_bp, url_prefix='/leaves')
    app.register_blueprint(shift_bp, url_prefix='/shifts')
    app.register_blueprint(loan_bp, url_prefix='/loans')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')

    @app.before_request
    def before_request():
        g.db = get_db(app)

    @app.teardown_request
    def teardown_request(exc):
        db = getattr(g, 'db', None)
        if db is not None:
            db.close()

    @app.context_processor
    def inject_globals():
        company = None
        modules = []
        try:
            company = g.db.execute("SELECT * FROM company_settings LIMIT 1").fetchone()
            modules = g.db.execute("SELECT * FROM modules WHERE is_enabled=1 ORDER BY sort_order").fetchall()
        except:
            pass
        return dict(company=company, current_user=session.get('user'), nav_modules=modules)

    return app
