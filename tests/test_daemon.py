#!/usr/bin/env python3
"""
Tests for Toshy daemon functionality
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock
from toshy.daemon import find_config_file, wait_for_display

def test_find_config_file_exists():
    """Test finding an existing config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='toshy_config.py', delete=False) as f:
        f.write("# Test config")
        f.flush()
        
        # Mock the expanduser to return our temp file location
        with patch('os.path.expanduser') as mock_expanduser:
            mock_expanduser.return_value = f.name
            
            result = find_config_file()
            assert result == f.name
        
        # Clean up
        os.unlink(f.name)

def test_find_config_file_none():
    """Test when no config file exists"""
    with patch('os.path.exists', return_value=False):
        result = find_config_file()
        assert result is None

@patch.dict(os.environ, {'XDG_SESSION_TYPE': 'x11', 'DISPLAY': ':0'})
@patch('subprocess.run')
def test_wait_for_display_x11_success(mock_run):
    """Test waiting for X11 display when successful"""
    mock_run.return_value = MagicMock(returncode=0)
    
    result = wait_for_display()
    assert result == True
    mock_run.assert_called()

@patch.dict(os.environ, {'XDG_SESSION_TYPE': 'wayland', 'WAYLAND_DISPLAY': 'wayland-0', 'XDG_RUNTIME_DIR': '/tmp'})
@patch('os.path.exists')
def test_wait_for_display_wayland_success(mock_exists):
    """Test waiting for Wayland display when successful"""
    mock_exists.return_value = True
    
    result = wait_for_display()
    assert result == True

@patch.dict(os.environ, {}, clear=True)
def test_wait_for_display_no_session_type():
    """Test when no session type is set"""
    result = wait_for_display()
    assert result == True  # Should proceed anyway

if __name__ == "__main__":
    pytest.main([__file__])
