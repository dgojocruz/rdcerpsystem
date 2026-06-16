# Fix 1: Add missing columns to dashboard_widgets if needed
import sqlite3
conn = sqlite3.connect('instance/erp.db')
cols = [r[1] for r in conn.execute("PRAGMA table_info(dashboard_widgets)").fetchall()]
print("Existing columns:", cols)
for col, default in [('position_x','0'),('position_y','0'),('width','1'),('height','1')]:
    if col not in cols:
        conn.execute(f"ALTER TABLE dashboard_widgets ADD COLUMN {col} INTEGER DEFAULT {default}")
        print(f"Added column: {col}")
conn.execute("UPDATE dashboard_widgets SET position_x=COALESCE(position_x,0), position_y=COALESCE(position_y,0), width=COALESCE(width,1), height=COALESCE(height,1)")
conn.commit()
conn.close()
print("DB fixed.")

# Fix 2: Patch dashboard __init__.py to use safe ORDER BY
py = open('app/modules/dashboard/__init__.py', encoding='utf-8').read()
old = 'ORDER BY position_y, position_x""", (user_id,)).fetchall()'
new = 'ORDER BY COALESCE(position_y,0), COALESCE(position_x,0)""", (user_id,)).fetchall()'
if old in py:
    py = py.replace(old, new)
    open('app/modules/dashboard/__init__.py', 'w', encoding='utf-8').write(py)
    print("Dashboard query patched.")
else:
    print("Pattern not found - already patched or different version.")
