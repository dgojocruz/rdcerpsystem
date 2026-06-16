#!/usr/bin/env python3
"""
Client Setup Wizard — Create and configure a new ERP client
Usage:  python scripts/setup_client.py
"""
import sys
import os
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ask(prompt, default='', required=False):
    while True:
        val = input(f"  {prompt}{' [' + default + ']' if default else ''}: ").strip()
        if not val and default:
            return default
        if val:
            return val
        if required:
            print("   ⚠ This field is required.")
        else:
            return ''

def main():
    print("\n" + "="*60)
    print("  ERP System — New Client Setup Wizard")
    print("="*60 + "\n")

    print("Step 1: Client Identifier")
    print("  (Used as folder name — no spaces, lowercase, e.g. 'rhodeco', 'abc_corp')")
    while True:
        client_id = ask("Client ID", required=True).lower().replace(' ', '_')
        if re.match(r'^[a-z0-9_]+$', client_id):
            break
        print("   ⚠ Client ID can only contain letters, numbers, and underscores.")

    print("\nStep 2: Company Information")
    company_name = ask("Company Name (full legal name)", required=True)
    trade_name   = ask("Trade Name / Short Name", company_name[:15])
    address      = ask("Address")
    city         = ask("City", "Quezon City")
    province     = ask("Province", "NCR")

    print("\nStep 3: Government Numbers (can update later in Settings)")
    tin       = ask("Company TIN", "000-000-000-000")
    sss_no    = ask("SSS Employer No.")
    phic_no   = ask("PhilHealth Employer Code")
    hdmf_no   = ask("Pag-IBIG Employer No.")

    print("\nStep 4: Payroll Configuration")
    payroll_type = ask("Payroll Type", "SEMI_MONTHLY+WEEKLY",
                       )
    min_wage     = ask("Daily Minimum Wage (NCR default ₱695)", "695")

    print("\nStep 5: Admin Account")
    admin_user = ask("Admin Username", "admin")
    admin_pass = ask("Admin Password", "admin123")

    # Build config
    config = {
        "company_name": company_name,
        "trade_name": trade_name,
        "address": address,
        "city": city,
        "province": province,
        "tin": tin,
        "sss_employer_no": sss_no,
        "philhealth_employer_no": phic_no,
        "pagibig_employer_no": hdmf_no,
        "payroll_type": payroll_type,
        "ncr_minimum_wage": float(min_wage or 695),
        "admin_username": admin_user,
        "admin_password": admin_pass,
        "client_id": client_id,
    }

    from app.config import create_client, CLIENTS_DIR
    client_dir = create_client(client_id, company_name, config)

    # Initialize database with correct admin
    from app import create_app
    app = create_app(client_id=client_id)
    from werkzeug.security import generate_password_hash
    import sqlite3
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    h = generate_password_hash(admin_pass)
    conn.execute("UPDATE users SET username=?, password_hash=?, full_name=? WHERE id=1",
                 (admin_user, h, f"Administrator"))
    conn.execute("""UPDATE company_settings SET
        company_name=?,trade_name=?,address=?,city=?,province=?,
        tin=?,sss_employer_no=?,philhealth_employer_no=?,pagibig_employer_no=?
        WHERE id=1""",
        (company_name, trade_name, address, city, province,
         tin, sss_no, phic_no, hdmf_no))
    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print(f"  ✓ Client '{client_id}' created successfully!")
    print(f"  Client folder: {client_dir}")
    print(f"  Database: {db_path}")
    print("\n  To start this client:")
    print(f"    python run.py --client {client_id}")
    print(f"  Or on Windows: START_ERP.bat {client_id}")
    print(f"\n  Login: {admin_user} / {admin_pass}")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
