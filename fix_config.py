content = open('app/config.py', encoding='utf-8').read()
print("Before:")
print(content[:600])

# Fix the default database path to point to rhodeco client DB
content = content.replace(
    "DATABASE = os.path.join(BASE_DIR, 'instance', 'erp.db')",
    "DATABASE = os.path.join(BASE_DIR, 'clients', 'rhodeco', 'data', 'erp.db')"
)

open('app/config.py', 'w', encoding='utf-8').write(content)
print("\nFixed! Default DB now points to clients/rhodeco/data/erp.db")