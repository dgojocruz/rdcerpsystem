# Strip ALL timekeeping sections and endblocks, then rebuild cleanly
content = open('app/templates/employees/view.html', encoding='utf-8').read()

# Find the position of the LAST </div></div> before any endblock chaos
# Strategy: find the original end of the grid-2 div, then rewrite from there

# The original file ends with the recent payslips card then endblock
# Find the clean end - everything up to and including the closing grid div
# before any timekeeping injection

# Remove all injected timekeeping sections (there may be multiple)
import re

# First, find where the original content ends (before timekeeping was added)
# The original last section is the recent payslips card ending with </div>\n</div>\n{% endblock %}
# Let's find the payslips section end

# Clean approach: rebuild the file from scratch using the known good structure
# Keep everything up to (and including) the closing of the two-column grid
# then add timekeeping section once, then close with single endblock

# Split on the timekeeping card div to remove all injected copies
TK_MARKER = '<div class="card mt-16">\n  <div class="card-header" style="display:flex;align-items:center;justify-content:space-between'

# Find where original content ends (before first TK injection)
if TK_MARKER in content:
    clean_end = content.index(TK_MARKER)
    original = content[:clean_end].rstrip()
else:
    # Find last endblock and strip from there
    original = content[:content.rfind('{% endblock %}')].rstrip()

# Make sure original ends with closing grid div
print("Last 200 chars of original:")
print(repr(original[-200:]))
print("\nOriginal ends cleanly:", original.rstrip().endswith('</div>'))
