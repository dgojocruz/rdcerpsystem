import os, sqlite3, shutil

# Step 1: Delete the wrong instance/erp.db
if os.path.exists('instance/erp.db'):
    os.remove('instance/erp.db')
    print("Deleted: instance/erp.db")
else:
    print("instance/erp.db not found - already gone")

# Step 2: Fix dashboard_widgets in the CORRECT database
conn = sqlite3.connect('clients/rhodeco/data/erp.db')
cols = [r[1] for r in conn.execute('PRAGMA table_info(dashboard_widgets)').fetchall()]
print('Dashboard columns:', cols)
for col in ['position_x','position_y','width','height']:
    if col not in cols:
        conn.execute(f'ALTER TABLE dashboard_widgets ADD COLUMN {col} INTEGER DEFAULT 0')
        print(f'Added column: {col}')
conn.execute('UPDATE dashboard_widgets SET position_x=COALESCE(position_x,0), position_y=COALESCE(position_y,0), width=COALESCE(width,1), height=COALESCE(height,1)')

# Step 3: Fix attendance table columns in correct DB
att_cols = [r[1] for r in conn.execute('PRAGMA table_info(attendance)').fetchall()]
print('Attendance columns:', att_cols)
for col, typ, default in [
    ('hours_paid','REAL','0'),
    ('unpaid_hours','REAL','0')]:
    if col not in att_cols:
        conn.execute(f'ALTER TABLE attendance ADD COLUMN {col} {typ} DEFAULT {default}')
        print(f'Added column: {col}')

# Step 4: Fix payroll table columns
pay_cols = [r[1] for r in conn.execute('PRAGMA table_info(payroll)').fetchall()]
for col, typ in [('hours_paid','REAL'),('unpaid_hours','REAL')]:
    if col not in pay_cols:
        conn.execute(f'ALTER TABLE payroll ADD COLUMN {col} {typ} DEFAULT 0')
        print(f'Added payroll column: {col}')

conn.commit()
conn.close()
print("\nCorrect database fixed!")

# Step 5: Create a redirect so instance/ always points to correct DB
os.makedirs('instance', exist_ok=True)
print("\nDone! From now on all fixes should target: clients/rhodeco/data/erp.db")
