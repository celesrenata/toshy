#!/usr/bin/env python3
"""
Tests for Toshy entry points
"""

import pytest
import subprocess
import sys
from unittest.mock import patch, MagicMock

def test_entry_points_importable():
    """Test that all entry point modules can be imported"""
    try:
        import toshy.tray
        import toshy.layout_selector
        import toshy.config
        import toshy.daemon
        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import entry point modules: {e}")

def test_entry_points_have_main():
    """Test that all entry point modules have main functions"""
    import toshy.tray
    import toshy.layout_selector
    import toshy.config
    import toshy.daemon
    
    assert hasattr(toshy.tray, 'main')
    assert hasattr(toshy.layout_selector, 'main')
    assert hasattr(toshy.config, 'main')
    assert hasattr(toshy.daemon, 'main')
    
    assert callable(toshy.tray.main)
    assert callable(toshy.layout_selector.main)
    assert callable(toshy.config.main)
    assert callable(toshy.daemon.main)

@patch('toshy.config.find_config_file')
def test_config_main_no_args(mock_find_config):
    """Test config main function with no arguments"""
    mock_find_config.return_value = None
    
    from toshy.config import main
    
    # Should not raise an exception
    with pytest.raises(SystemExit) as exc_info:
        with patch('sys.argv', ['toshy-config']):
            main()
    
    # Should exit with error code due to no config file
    assert exc_info.value.code == 1

if __name__ == "__main__":
    pytest.main([__file__])
