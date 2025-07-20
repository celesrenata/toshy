import pytest
import gi
import os
import sys
from unittest.mock import MagicMock, patch

# Try to import GTK4, fall back to GTK3 if not available
try:
    gi.require_version('Gtk', '4.0')
    from gi.repository import Gtk, GLib
    GTK_VERSION = 4
except (ValueError, ImportError):
    try:
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk, GLib
        GTK_VERSION = 3
    except (ValueError, ImportError):
        print("ERROR: Neither GTK4 nor GTK3 could be imported.")
        GTK_VERSION = None

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def gtk_app():
    """Fixture to create a GTK application for testing."""
    if GTK_VERSION is None:
        pytest.skip("GTK not available")
        
    if GTK_VERSION == 4:
        app = Gtk.Application(application_id="org.toshy.test")
    else:  # GTK3
        app = Gtk.Application(application_id="org.toshy.test")
    
    yield app
    
    # Clean up
    if app.get_windows():
        for window in app.get_windows():
            window.destroy()


@pytest.fixture
def main_window(gtk_app):
    """Fixture to create the main application window."""
    if GTK_VERSION is None:
        pytest.skip("GTK not available")
        
    if GTK_VERSION == 4:
        # Import the GTK4 window
        from toshy_gui.main_gtk4 import ToshyPreferencesWindow
        window = ToshyPreferencesWindow(gtk_app)
    else:
        # Mock a basic window for GTK3 or if the main window can't be imported
        window = MagicMock()
        window.get_title.return_value = "Toshy Preferences"
        window.get_child.return_value = MagicMock()
        window.get_titlebar.return_value = MagicMock()
        window.get_settings_panel.return_value = MagicMock()
        window.get_service_panel.return_value = MagicMock()
    
    if not isinstance(window, MagicMock):
        window.show()
        # Process GTK events to ensure window is fully initialized
        while Gtk.events_pending():
            Gtk.main_iteration()
    
    yield window
    
    if not isinstance(window, MagicMock):
        window.destroy()


@pytest.fixture
def settings_panel(main_window):
    """Fixture to get the settings panel."""
    if isinstance(main_window, MagicMock):
        return main_window.get_settings_panel()
    
    return main_window.get_settings_panel()


@pytest.fixture
def service_panel(main_window):
    """Fixture to get the service panel."""
    if isinstance(main_window, MagicMock):
        return main_window.get_service_panel()
    
    return main_window.get_service_panel()


@pytest.fixture
def mock_config_file():
    """Fixture to mock the config file operations."""
    with patch('toshy_gui.core.config_manager.read_config') as mock_read:
        mock_read.return_value = {
            'theme': 'dark',
            'autostart': True,
            'macStyle': True,
            'applications': {
                'firefox': {
                    'Cmd+T': 'Ctrl+T',
                    'Cmd+W': 'Ctrl+W'
                }
            }
        }
        
        with patch('toshy_gui.core.config_manager.write_config') as mock_write:
            yield {
                'read': mock_read,
                'write': mock_write
            }
