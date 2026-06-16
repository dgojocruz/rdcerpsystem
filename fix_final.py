import sqlite3

conn = sqlite3.connect('clients/rhodeco/data/erp.db')

cols = [r[1] for r in conn.execute('PRAGMA table_info(dashboard_widgets)').fetchall()]
print('Current columns:', cols)

for col in ['position_x', 'position_y', 'width', 'height']:
    if col not in cols:
        conn.execute(f'ALTER TABLE dashboard_widgets ADD COLUMN {col} INTEGER DEFAULT 0')
        print(f'Added: {col}')
    else:
        print(f'Already exists: {col}')

conn.execute('UPDATE dashboard_widgets SET position_x=COALESCE(position_x,0), position_y=COALESCE(position_y,0), width=COALESCE(width,1), height=COALESCE(height,1)')
conn.commit()
conn.close()
print('Done!')