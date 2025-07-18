#!/usr/bin/env python3
"""
Tests for Toshy configuration management
"""

import pytest
import tempfile
import os
from pathlib import Path
from toshy.config import validate_config, find_config_file

def test_validate_config_valid():
    """Test validation of a valid configuration file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
# Valid Python configuration
import os

# Simple configuration
SETTING_1 = True
SETTING_2 = "test"
""")
        f.flush()
        
        assert validate_config(f.name) == True
        
        # Clean up
        os.unlink(f.name)

def test_validate_config_invalid():
    """Test validation of an invalid configuration file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("""
# Invalid Python syntax
import os

# Missing closing quote
SETTING_1 = "unclosed string
SETTING_2 = True
""")
        f.flush()
        
        assert validate_config(f.name) == False
        
        # Clean up
        os.unlink(f.name)

def test_validate_config_nonexistent():
    """Test validation of a non-existent file"""
    assert validate_config("/nonexistent/file.py") == False

def test_find_config_file_none():
    """Test finding config file when none exists"""
    # This test assumes no config file exists in standard locations
    # In a real environment, this might need to be mocked
    pass  # Skip for now as it depends on environment

if __name__ == "__main__":
    pytest.main([__file__])
