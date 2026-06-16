import shutil, os

# Step 1: Fix dashboard
import sqlite3
conn = sqlite3.connect('instance/erp.db')
for col in ['position_x','position_y','width','height']:
    try:
        conn.execute(f"ALTER TABLE dashboard_widgets ADD COLUMN {col} INTEGER DEFAULT 0")
    except: pass
conn.execute("UPDATE dashboard_widgets SET position_x=COALESCE(position_x,0), position_y=COALESCE(position_y,0), width=COALESCE(width,1), height=COALESCE(height,1)")
conn.commit()
conn.close()
print("Step 1: DB fixed")

py = open('app/modules/dashboard/__init__.py', encoding='utf-8').read()
if 'COALESCE(position_y' not in py:
    py = py.replace('ORDER BY position_y, position_x', 'ORDER BY COALESCE(position_y,0), COALESCE(position_x,0)')
    open('app/modules/dashboard/__init__.py', 'w', encoding='utf-8').write(py)
print("Step 2: Dashboard patched")

# Step 2: Write clean view.html
# Find the script directory and copy the clean HTML
script_dir = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(script_dir, 'employee_view_clean.html')
dst = 'app/templates/employees/view.html'

if os.path.exists(src):
    shutil.copy2(src, dst)
    content = open(dst, encoding='utf-8').read()
    print(f"Step 3: view.html written ({len(content)} chars, {content.count('endblock')} endblocks)")
    print("Has Schedule Manager:", 'Schedule Manager' in content)
    print("Has collapsible:", 'collapsible-card' in content)
    print("Has Reports To:", 'Reports To' in content)
else:
    print(f"ERROR: {src} not found. Make sure employee_view_clean.html is in the same folder.")

print("\nDone! Restart the server.")
