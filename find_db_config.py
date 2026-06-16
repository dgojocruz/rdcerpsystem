import os

# Find all config files
for root, dirs, files in os.walk('.'):
    for f in files:
        if f in ['config.py', 'config.ini', 'settings.py'] or f.endswith('.cfg'):
            path = os.path.join(root, f)
            content = open(path, encoding='utf-8', errors='ignore').read()
            if 'db' in content.lower() or 'database' in content.lower() or 'sqlite' in content.lower():
                print(f"\n=== {path} ===")
                print(content[:500])