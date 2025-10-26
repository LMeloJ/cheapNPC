# CSS Files for CheapNPC

This directory contains external CSS files that are loaded by the CheapNPC application.

## Files

- `landing_page.css` - Styles specific to the landing page
- `dashboard.css` - Styles specific to the dashboard interface  
- `common_utilities.css` - Shared utility classes and animations

## Usage

These CSS files are automatically loaded by `css_styles.py` in the parent directory. The Python module provides functions to load and combine these styles for use with Gradio components.

### Loading Styles

```python
from cheapNPC.views.shared.css_styles import (
    LANDING_PAGE_CSS,
    DASHBOARD_CSS,
    COMMON_UTILITY_CSS,
    UNIFIED_INTERFACE_CSS
)

# Use in Gradio Blocks
with gr.Blocks(css=LANDING_PAGE_CSS + COMMON_UTILITY_CSS):
    # ...
```

## Benefits of External CSS Files

- ✅ Proper CSS syntax highlighting in your IDE
- ✅ Can be edited independently of Python code
- ✅ IDE auto-completion for CSS properties
- ✅ Can be linted with CSS linters
- ✅ Better separation of concerns
- ✅ Easier to maintain and organize
- ✅ Can be minified for production if needed
