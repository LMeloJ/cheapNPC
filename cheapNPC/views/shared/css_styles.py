"""
Shared CSS styles for CheapNPC web interface.

This module loads CSS from external files and provides them to Gradio components.
"""

from pathlib import Path


# Base directory for CSS files
# Path relative to this file's location
CSS_DIR = Path(__file__).parent / "static" / "css"


def _load_css(filename: str) -> str:
    """
    Load CSS from an external file.
    
    Args:
        filename: Name of the CSS file to load
        
    Returns:
        str: CSS content or empty string if file doesn't exist
    """
    css_file = CSS_DIR / filename
    try:
        with open(css_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Return empty string if file doesn't exist
        return ""


def get_landing_page_css() -> str:
    """Load landing page CSS from external file."""
    return _load_css("landing_page.css")


def get_dashboard_css() -> str:
    """Load dashboard CSS from external file."""
    return _load_css("dashboard.css")


def get_unified_interface_css() -> str:
    """Load unified interface CSS (combination of all styles)."""
    landing = get_landing_page_css()
    dashboard = get_dashboard_css()
    common = get_common_utility_css()
    return landing + "\n" + dashboard + "\n" + common


def get_common_utility_css() -> str:
    """Load common utility CSS from external file."""
    return _load_css("common_utilities.css")


# For backward compatibility, provide constants
LANDING_PAGE_CSS = get_landing_page_css()
DASHBOARD_CSS = get_dashboard_css()
COMMON_UTILITY_CSS = get_common_utility_css()
UNIFIED_INTERFACE_CSS = get_unified_interface_css()
