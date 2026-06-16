lines = open('app/modules/dashboard/__init__.py', encoding='utf-8').readlines()
for i, l in enumerate(lines[70:80], 71):
    print(f"{i}: {l}", end='')