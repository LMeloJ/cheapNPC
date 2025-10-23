"""
Test file to verify the landing page setup function works correctly.
"""

from cheapNPC.presentation.web.components.landing_page import LandingPageComponent

# Create component
landing = LandingPageComponent()

# Test database check
status_msg, is_setup, show_button = landing.check_database_status()
print(f"Status: {status_msg}")
print(f"Is Setup: {is_setup}")
print(f"Show Button: {show_button}")

# Test world creation (if you want to test it)
# result = landing.run_create_world(lambda msg: print(f"Progress: {msg}"))
# print(f"Result: {result}")

