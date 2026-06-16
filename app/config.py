import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIENTS_DIR = os.path.join(BASE_DIR, 'clients')

class BaseConfig:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'erp-dev-secret-change-in-production-2026')
    DEBUG = False
    TESTING = False
    INSTANCE_PATH = os.path.join(BASE_DIR, 'instance')
    DATABASE = os.path.join(BASE_DIR, 'instance', 'erp.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'instance', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Philippine Labor Law Constants (updated 2025-2026)
    NCR_MINIMUM_WAGE = 695.00
    OT_RATE_MULTIPLIER = 1.25
    NIGHT_DIFF_RATE = 0.10
    REST_DAY_RATE = 1.30
    SPECIAL_HOLIDAY_RATE = 1.30
    LEGAL_HOLIDAY_RATE = 2.00
    LEGAL_HOLIDAY_OT_RATE = 2.60

    # SSS 2025 Contribution Table
    SSS_EMPLOYEE_RATE = 0.045
    SSS_EMPLOYER_RATE = 0.085
    SSS_EC_RATE = 0.01
    SSS_WISP_THRESHOLD = 20250
    SSS_MAX_MONTHLY_SALARY_CREDIT = 30000

    # PhilHealth 2025
    PHILHEALTH_RATE = 0.05  # 5% total, split 50/50
    PHILHEALTH_MAX_SALARY = 100000
    PHILHEALTH_MIN_CONTRIBUTION = 500

    # Pag-IBIG
    PAGIBIG_EMPLOYEE_RATE = 0.02
    PAGIBIG_EMPLOYER_RATE = 0.02
    PAGIBIG_MAX_FUND_SALARY = 10000
    PAGIBIG_MAX_CONTRIBUTION = 200

    # BIR Withholding Tax Brackets (TRAIN Law, effective Jan 2023)
    TAX_BRACKETS = [
        (0, 20833, 0, 0),
        (20833, 33332, 0, 0.15),
        (33332, 66666, 1875, 0.20),
        (66666, 166666, 8541.80, 0.25),
        (166666, 666666, 33541.80, 0.30),
        (666666, float('inf'), 183541.80, 0.35),
    ]


class DevelopmentConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False


class ClientConfig(BaseConfig):
    """Loaded dynamically per client from clients/<client_id>/config.json"""
    def __init__(self, client_id):
        client_dir = os.path.join(CLIENTS_DIR, client_id)
        config_file = os.path.join(client_dir, 'config.json')
        if os.path.exists(config_file):
            with open(config_file) as f:
                data = json.load(f)
            for k, v in data.items():
                setattr(self, k.upper(), v)
        self.INSTANCE_PATH = os.path.join(client_dir, 'data')
        self.DATABASE = os.path.join(client_dir, 'data', 'erp.db')
        self.UPLOAD_FOLDER = os.path.join(client_dir, 'data', 'uploads')
        os.makedirs(self.INSTANCE_PATH, exist_ok=True)
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)


def get_config(client_id=None):
    if client_id:
        return ClientConfig(client_id)
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig()
    return DevelopmentConfig()


def list_clients():
    if not os.path.exists(CLIENTS_DIR):
        return []
    return [d for d in os.listdir(CLIENTS_DIR)
            if os.path.isdir(os.path.join(CLIENTS_DIR, d))]


def create_client(client_id, company_name, config_overrides=None):
    client_dir = os.path.join(CLIENTS_DIR, client_id)
    os.makedirs(os.path.join(client_dir, 'data'), exist_ok=True)
    os.makedirs(os.path.join(client_dir, 'data', 'uploads'), exist_ok=True)
    config = {
        'company_name': company_name,
        'client_id': client_id,
    }
    if config_overrides:
        config.update(config_overrides)
    with open(os.path.join(client_dir, 'config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    return client_dir
