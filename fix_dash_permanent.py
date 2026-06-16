py = open('app/modules/dashboard/__init__.py', encoding='utf-8').read()
print('Before:', 'COALESCE' in py)
py = py.replace(
    'ORDER BY position_y, position_x',
    'ORDER BY COALESCE(position_y,0), COALESCE(position_x,0)'
)
open('app/modules/dashboard/__init__.py', 'w', encoding='utf-8').write(py)
print('After:', 'COALESCE' in py)
print('Done!')