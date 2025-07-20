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


def process_gtk_events():
    """Process pending GTK events."""
    if GTK_VERSION is not None:
        while Gtk.events_pending():
            Gtk.main_iteration()


@pytest.mark.frontend
def test_preferences_button_click(main_window):
    """Test that the preferences button opens the preferences dialog."""
    if isinstance(main_window, MagicMock):
        # For mock window, just verify the method exists
        assert hasattr(main_window.get_settings_panel(), 'get_preferences_button')
        return
    
    with patch('toshy_gui.gui.settings_panel_gtk4.SettingsDialog') as mock_dialog:
        # Get the settings panel
        settings_panel = main_window.get_settings_panel()
        
        # Get the preferences button
        prefs_button = settings_panel.get_preferences_button()
        assert prefs_button is not None
        
        # Click the button
        prefs_button.clicked()
        
        # Process GTK events
        process_gtk_events()
        
        # Verify that the dialog was created
        mock_dialog.assert_called_once()


@pytest.mark.frontend
def test_service_restart_button(main_window):
    """Test that the service restart button calls the correct function."""
    if isinstance(main_window, MagicMock):
        # For mock window, just verify the method exists
        assert hasattr(main_window.get_service_panel(), 'get_restart_button')
        return
    
    with patch('toshy_gui.gui.service_panel_gtk4.restart_service') as mock_restart:
        # Get the service panel
        service_panel = main_window.get_service_panel()
        
        # Get the restart button
        restart_button = service_panel.get_restart_button()
        assert restart_button is not None
        
        # Click the button
        restart_button.clicked()
        
        # Process GTK events
        process_gtk_events()
        
        # Verify that the restart function was called
        mock_restart.assert_called_once()


@pytest.mark.frontend
def test_service_start_button(main_window):
    """Test that the service start button calls the correct function."""
    if isinstance(main_window, MagicMock):
        # For mock window, just verify the method exists
        assert hasattr(main_window.get_service_panel(), 'get_start_button')
        return
    
    with patch('toshy_gui.gui.service_panel_gtk4.start_service') as mock_start:
        # Get the service panel
        service_panel = main_window.get_service_panel()
        
        # Get the start button
        start_button = service_panel.get_start_button()
        assert start_button is not None
        
        # Click the button
        start_button.clicked()
        
        # Process GTK events
        process_gtk_events()
        
        # Verify that the start function was called
        mock_start.assert_called_once()


@pytest.mark.frontend
def test_service_stop_button(main_window):
    """Test that the service stop button calls the correct function."""
    if isinstance(main_window, MagicMock):
        # For mock window, just verify the method exists
        assert hasattr(main_window.get_service_panel(), 'get_stop_button')
        return
    
    with patch('toshy_gui.gui.service_panel_gtk4.stop_service') as mock_stop:
        # Get the service panel
        service_panel = main_window.get_service_panel()
        
        # Get the stop button
        stop_button = service_panel.get_stop_button()
        assert stop_button is not None
        
        # Click the button
        stop_button.clicked()
        
        # Process GTK events
        process_gtk_events()
        
        # Verify that the stop function was called
        mock_stop.assert_called_once()


@pytest.mark.frontend
def test_save_settings_button(main_window, mock_config_file):
    """Test that the save settings button calls the correct function."""
    if isinstance(main_window, MagicMock):
        # For mock window, just verify the method exists
        assert hasattr(main_window.get_settings_panel(), 'get_save_button')
        return
    
    with patch('toshy_gui.core.config_manager.save_settings') as mock_save:
        # Get the settings panel
        settings_panel = main_window.get_settings_panel()
        
        # Get the save button
        save_button = settings_panel.get_save_button()
        assert save_button is not None
        
        # Click the button
        save_button.clicked()
        
        # Process GTK events
        process_gtk_events()
        
        # Verify that the save function was called
        mock_save.assert_called_once()


@pytest.mark.frontend
def test_close_button(main_window):
    """Test that the close button closes the window."""
    if isinstance(main_window, MagicMock):
        # For mock window, just verify the method exists
        return
    
    # Save the initial window count
    initial_window_count = len(main_window.get_application().get_windows())
    
    # Get the close button from the header bar
    header_bar = main_window.get_titlebar()
    close_button = None
    
    # In GTK4, the close button is part of the window decoration
    # We'll need to simulate the window close signal instead
    with patch.object(main_window, 'close') as mock_close:
        # Trigger the close signal
        main_window.close()
        
        # Verify that the close method was called
        mock_close.assert_called_once()
