content = open('app/config.py', encoding='utf-8').read()
print("Current DB path in config:")
for line in content.split('\n'):
    if 'DATABASE' in line or 'erp.db' in line or 'instance' in line:
        print(' ', line)

# Fix all database references
content = content.replace(
    "os.path.join(BASE_DIR, 'instance', 'erp.db')",
    "os.path.join(BASE_DIR, 'clients', 'rhodeco', 'data', 'erp.db')"
)
content = content.replace(
    "os.path.join(BASE_DIR, 'instance')",
    "os.path.join(BASE_DIR, 'clients', 'rhodeco', 'data')"
)

open('app/config.py', 'w', encoding='utf-8').write(content)
print("\nFixed config. New DB references:")
for line in content.split('\n'):
    if 'DATABASE' in line or 'erp.db' in line:
        print(' ', line)
print("Done!")