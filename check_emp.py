import sqlite3
conn = sqlite3.connect('instance/erp.db')
total = conn.execute('SELECT COUNT(id) FROM employees').fetchone()[0]
active = conn.execute("SELECT COUNT(id) FROM employees WHERE status='ACTIVE'").fetchone()[0]
print('Total employees:', total)
print('Active employees:', active)
conn.close()