import sqlite3

conn = sqlite3.connect('clients/rhodeco/data/erp.db')

# Add missing columns to dashboard_widgets
cols = [r[1] for r in conn.execute('PRAGMA table_info(dashboard_widgets)').fetchall()]
print('Current columns:', cols)

for col, typ, default in [
    ('widget_title', 'TEXT', "''"),
    ('widget_config', 'TEXT', "'{}'"),
    ('position_x', 'INTEGER', '0'),
    ('position_y', 'INTEGER', '0'),
    ('width', 'INTEGER', '1'),
    ('height', 'INTEGER', '1'),
    ('is_visible', 'INTEGER', '1'),
]:
    if col not in cols:
        conn.execute(f"ALTER TABLE dashboard_widgets ADD COLUMN {col} {typ} DEFAULT {default}")
        print(f'Added: {col}')

conn.commit()
conn.close()
print('Done!')