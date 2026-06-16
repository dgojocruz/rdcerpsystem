py = open('app/modules/dashboard/__init__.py', encoding='utf-8').read()

# Fix column names to match actual schema
py = py.replace(
    'ORDER BY COALESCE(position_y,0), COALESCE(position_x,0)',
    'ORDER BY COALESCE(position_row,0), COALESCE(position_col,0)'
)
py = py.replace(
    'item.get(\'y\', 0), item.get(\'w\', 1), item.get(\'h\', 1)',
    'item.get(\'y\', 0), item.get(\'w\', 1), item.get(\'h\', 1)'
)
py = py.replace(
    '(item.get(\'x\', 0), item.get(\'y\', 0), item.get(\'w\', 1), item.get(\'h\', 1)',
    '(item.get(\'x\', 0), item.get(\'y\', 0), item.get(\'w\', 1), item.get(\'h\', 1)'
)
py = py.replace(
    'SET position_x=?, position_y=?, width=?, height=?',
    'SET position_col=?, position_row=?, width_units=?, is_visible=is_visible'
)

open('app/modules/dashboard/__init__.py', 'w', encoding='utf-8').write(py)
print('Fixed!')
print('Verify:', 'position_row' in open('app/modules/dashboard/__init__.py').read())