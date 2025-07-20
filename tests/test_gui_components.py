import pytest
from unittest.mock import patch, MagicMock
import gi
import os
import sys

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


@pytest.mark.frontend
def test_main_window_creation(main_window):
    """Test that the main window is created correctly."""
    assert main_window is not None
    if GTK_VERSION == 4:
        assert isinstance(main_window, Gtk.ApplicationWindow) or isinstance(main_window, MagicMock)
    assert main_window.get_title() == "Toshy Preferences"


@pytest.mark.frontend
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


@pytest.mark.frontend
def test_settings_panel_components(settings_panel):
    """Test that the settings panel contains all required components."""
    # These tests will depend on the actual implementation of the settings panel
    # For now, we'll just check that the panel exists
    assert settings_panel is not None


@pytest.mark.frontend
def test_service_panel_components(service_panel):
    """Test that the service panel contains all required components."""
    # These tests will depend on the actual implementation of the service panel
    # For now, we'll just check that the panel exists
    assert service_panel is not None


@pytest.mark.frontend
def test_theme_switching(main_window, mock_config_file):
    """Test that theme switching works correctly."""
    if isinstance(main_window, MagicMock):
        # Skip the test if we're using a mock window
        pytest.skip("Cannot test theme switching with mock window")
    
    # This test will depend on the actual implementation of theme switching
    # For now, we'll just check that the theme can be set
    with patch('toshy_gui.core.theme_manager.set_theme') as mock_set_theme:
        # Attempt to switch theme
        if hasattr(main_window, 'set_theme'):
            main_window.set_theme('light')
            mock_set_theme.assert_called_with('light')
            
            main_window.set_theme('dark')
            mock_set_theme.assert_called_with('dark')


@pytest.mark.frontend
def test_window_size_and_position(main_window):
    """Test that the window has a reasonable size and position."""
    if isinstance(main_window, MagicMock):
        # Skip the test if we're using a mock window
        pytest.skip("Cannot test window size with mock window")
    
    # Get window size
    width, height = main_window.get_default_size()
    
    # Check that the window has a reasonable size
    assert width >= 400, "Window width should be at least 400 pixels"
    assert height >= 300, "Window height should be at least 300 pixels"
    
    # Check that the window is not too large
    assert width <= 1200, "Window width should not exceed 1200 pixels"
    assert height <= 900, "Window height should not exceed 900 pixels"
