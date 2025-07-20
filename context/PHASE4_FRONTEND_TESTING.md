# Phase 4: Frontend Testing Implementation

## Objective
Develop comprehensive test cases for the frontend components, ensuring that buttons and other UI elements work correctly.

## Background
Currently, the test suite focuses primarily on backend functionality. To ensure a robust application, we need to extend testing to cover frontend components, particularly the GUI interface and button functionality. This will help catch UI-related issues early and ensure a consistent user experience.

## Tasks

### 1. Set Up Frontend Testing Framework
- Choose an appropriate testing framework for GUI testing (pytest-gtk, pytest-qt, etc.)
- Configure the testing environment for headless testing
- Set up test fixtures for GUI components
- Integrate with the existing test infrastructure

**Implementation Details:**
```python
# In tests/conftest.py
import pytest
import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib

@pytest.fixture
def gtk_app():
    """Fixture to create a GTK application for testing."""
    app = Gtk.Application(application_id="org.toshy.test")
    yield app
    # Clean up
    if app.get_windows():
        for window in app.get_windows():
            window.destroy()

@pytest.fixture
def main_window(gtk_app):
    """Fixture to create the main application window."""
    from toshy_gui.main_gtk4 import ToshyPreferencesWindow
    window = ToshyPreferencesWindow(gtk_app)
    window.show()
    # Process GTK events to ensure window is fully initialized
    while Gtk.events_pending():
        Gtk.main_iteration()
    yield window
    window.destroy()
```

### 2. Create Basic UI Component Tests
- Write tests for basic UI rendering
- Verify that all components are properly initialized
- Test that the UI layout is correct
- Ensure that all required elements are present

**Example Test:**
```python
# In tests/test_gui_components.py
import pytest
from gi.repository import Gtk

def test_main_window_creation(main_window):
    """Test that the main window is created correctly."""
    assert main_window is not None
    assert isinstance(main_window, Gtk.ApplicationWindow)
    assert main_window.get_title() == "Toshy Preferences"

def test_main_window_components(main_window):
    """Test that the main window contains all required components."""
    # Check for main container
    main_box = main_window.get_child()
    assert main_box is not None
    
    # Check for header bar
    header_bar = main_window.get_titlebar()
    assert header_bar is not None
    
    # Check for settings panel
    settings_panel = main_window.get_settings_panel()
    assert settings_panel is not None
    
    # Check for service panel
    service_panel = main_window.get_service_panel()
    assert service_panel is not None
```

### 3. Implement Button Click Tests
- Create tests for button click events
- Verify that buttons trigger the correct actions
- Test error handling for button actions
- Ensure that UI state changes correctly after button clicks

**Example Test:**
```python
# In tests/test_gui_buttons.py
import pytest
from unittest.mock import patch, MagicMock
from gi.repository import Gtk, GLib

def test_preferences_button_click(main_window):
    """Test that the preferences button opens the preferences dialog."""
    with patch('toshy_gui.gui.settings_panel_gtk4.SettingsDialog') as mock_dialog:
        # Get the preferences button
        settings_panel = main_window.get_settings_panel()
        prefs_button = settings_panel.get_preferences_button()
        
        # Click the button
        prefs_button.clicked()
        
        # Process GTK events
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        # Verify that the dialog was created
        mock_dialog.assert_called_once()

def test_service_restart_button(main_window):
    """Test that the service restart button calls the correct function."""
    with patch('toshy_gui.gui.service_panel_gtk4.restart_service') as mock_restart:
        # Get the restart button
        service_panel = main_window.get_service_panel()
        restart_button = service_panel.get_restart_button()
        
        # Click the button
        restart_button.clicked()
        
        # Process GTK events
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        # Verify that the restart function was called
        mock_restart.assert_called_once()
```

### 4. Test Form Input and Validation
- Create tests for form input fields
- Verify that input validation works correctly
- Test form submission and error handling
- Ensure that form data is processed correctly

**Example Test:**
```python
# In tests/test_gui_forms.py
import pytest
from unittest.mock import patch, MagicMock
from gi.repository import Gtk, GLib

def test_settings_form_validation(main_window):
    """Test that the settings form validates input correctly."""
    settings_panel = main_window.get_settings_panel()
    
    # Get the form fields
    theme_combo = settings_panel.get_theme_combo()
    autostart_switch = settings_panel.get_autostart_switch()
    
    # Set invalid values
    theme_combo.set_active_id("invalid_theme")
    
    # Try to save
    with patch('toshy_gui.gui.settings_panel_gtk4.show_error_dialog') as mock_error:
        settings_panel.save_button.clicked()
        
        # Process GTK events
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        # Verify that an error was shown
        mock_error.assert_called_once()
    
    # Set valid values
    theme_combo.set_active_id("dark")
    autostart_switch.set_active(True)
    
    # Try to save
    with patch('toshy_gui.gui.settings_panel_gtk4.save_settings') as mock_save:
        settings_panel.save_button.clicked()
        
        # Process GTK events
        while Gtk.events_pending():
            Gtk.main_iteration()
        
        # Verify that settings were saved
        mock_save.assert_called_once()
        args = mock_save.call_args[0][0]
        assert args["theme"] == "dark"
        assert args["autostart"] == True
```

### 5. Set Up Headless Testing for CI/CD
- Configure a headless testing environment for CI/CD
- Set up Xvfb or similar for running GUI tests without a display
- Create a CI/CD workflow for running the tests
- Ensure tests can run in different environments

**Example CI Configuration:**
```yaml
# In .github/workflows/test.yml
name: Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y xvfb libgtk-4-dev gobject-introspection libgirepository1.0-dev
        python -m pip install --upgrade pip
        pip install pytest pytest-cov pytest-xvfb
        pip install -e .
    
    - name: Run tests
      run: |
        xvfb-run --auto-servernum pytest tests/ -v
```

### 6. Integrate Frontend Tests with Existing Backend Tests
- Ensure frontend tests can run alongside backend tests
- Set up proper test isolation
- Create test categories for different types of tests
- Update the test documentation

**Example Test Configuration:**
```python
# In pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    frontend: marks tests as frontend tests
    backend: marks tests as backend tests
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests

# In tests/test_gui_components.py
import pytest

@pytest.mark.frontend
def test_main_window_creation(main_window):
    """Test that the main window is created correctly."""
    # ...

# In tests/test_config.py
import pytest

@pytest.mark.backend
def test_config_loading():
    """Test that configuration is loaded correctly."""
    # ...
```

## Potential Issues
1. **Headless Testing**: GUI testing in headless environments can be challenging
2. **Test Stability**: GUI tests can be flaky due to timing issues
3. **Environment Dependencies**: Tests might depend on specific GTK versions or themes
4. **Test Performance**: GUI tests can be slower than backend tests
5. **Mocking**: Mocking complex GUI components can be difficult

## Success Criteria
- Frontend tests cover all major UI components
- Button click tests verify that buttons trigger the correct actions
- Form input tests verify that forms handle input correctly
- Tests can run in both development and CI/CD environments
- Tests are stable and reliable
- Documentation is updated to reflect the new testing approach

## Files to Modify
- tests/conftest.py (to add GUI test fixtures)
- tests/test_gui_components.py (new file for UI component tests)
- tests/test_gui_buttons.py (new file for button click tests)
- tests/test_gui_forms.py (new file for form input tests)
- pytest.ini (to add frontend test markers)
- .github/workflows/test.yml (to set up CI/CD for GUI tests)
- README.md (to update testing documentation)
