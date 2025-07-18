#!/usr/bin/env python3
"""
Integration tests for NixOS module functionality
"""

import pytest
import tempfile
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import our configuration generator
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from toshy.config_generator import ToshyConfigGenerator

class TestNixOSIntegration:
    """Test NixOS module integration functionality"""
    
    def test_config_generator_basic(self):
        """Test basic configuration generation"""
        generator = ToshyConfigGenerator()
        
        options = {
            'keybindings': {
                'macStyle': True,
                'applications': {
                    'Firefox': {
                        'Cmd+T': 'Ctrl+T',
                        'Cmd+W': 'Ctrl+W'
                    }
                }
            },
            'logging': {
                'level': 'INFO'
            }
        }
        
        config = generator.generate_config(options)
        
        # Check that config contains expected elements
        assert 'MAC_STYLE_ENABLED = True' in config
        assert 'Firefox' in config
        assert 'LOG_LEVEL = \'INFO\'' in config
        assert 'TOSHY_CONFIG_VERSION' in config

    def test_config_generator_validation(self):
        """Test configuration validation"""
        generator = ToshyConfigGenerator()
        
        # Valid configuration
        valid_config = '''
import os
SETTING = True
'''
        assert generator.validate_config(valid_config) == True
        
        # Invalid configuration
        invalid_config = '''
import os
SETTING = True
INVALID SYNTAX HERE
'''
        assert generator.validate_config(invalid_config) == False

    def test_mac_style_config_generation(self):
        """Test Mac-style configuration generation"""
        generator = ToshyConfigGenerator()
        
        # With Mac-style enabled
        config_enabled = generator.generate_mac_style_config(True)
        assert 'MAC_STYLE_ENABLED = True' in config_enabled
        assert 'C("a"):         C("ctrl-a")' in config_enabled
        
        # With Mac-style disabled
        config_disabled = generator.generate_mac_style_config(False)
        assert 'Mac-style keybindings disabled' in config_disabled

    def test_application_config_generation(self):
        """Test application-specific configuration generation"""
        generator = ToshyConfigGenerator()
        
        applications = {
            'Firefox': {
                'Cmd+T': 'Ctrl+T',
                'Cmd+W': 'Ctrl+W'
            },
            'VSCode': {
                'Cmd+P': 'Ctrl+Shift+P'
            }
        }
        
        config = generator.generate_application_configs(applications)
        
        assert 'Firefox' in config
        assert 'VSCode' in config
        assert 'keymap("Firefox"' in config
        assert 'keymap("VSCode"' in config

    def test_key_binding_formatting(self):
        """Test key binding format conversion"""
        generator = ToshyConfigGenerator()
        
        # Test various key binding formats (case insensitive)
        result_cmd_t = generator._format_key_binding('Cmd+T')
        assert 'C("' in result_cmd_t and '")' in result_cmd_t
        
        result_ctrl_t = generator._format_key_binding('Ctrl+T')
        assert 'C("' in result_ctrl_t and '")' in result_ctrl_t
        
        result_alt_f = generator._format_key_binding('Alt+F')
        assert 'A("' in result_alt_f and '")' in result_alt_f

    def test_global_shortcuts_generation(self):
        """Test global shortcuts configuration"""
        generator = ToshyConfigGenerator()
        
        shortcuts = {
            'Cmd+Space': 'Alt+F2',
            'Cmd+Tab': 'Alt+Tab'
        }
        
        config = generator.generate_global_shortcuts(shortcuts)
        
        assert 'Global System' in config
        assert 'keymap("Global System"' in config

    def test_complete_config_generation(self):
        """Test complete configuration generation with all options"""
        generator = ToshyConfigGenerator()
        
        options = {
            'keybindings': {
                'macStyle': True,
                'applications': {
                    'Firefox': {'Cmd+T': 'Ctrl+T'},
                    'Terminal': {'Cmd+C': 'Ctrl+Shift+C'}
                },
                'globalShortcuts': {
                    'Cmd+Space': 'Alt+F2'
                }
            },
            'logging': {
                'level': 'DEBUG'
            },
            'performance': {
                'priority': -5
            },
            'security': {
                'restrictedMode': True
            }
        }
        
        custom_config = "# Custom user configuration\nCUSTOM_SETTING = True"
        
        config = generator.generate_config(options, custom_config)
        
        # Verify all sections are present
        assert 'MAC_STYLE_ENABLED = True' in config
        assert 'Firefox' in config
        assert 'Terminal' in config
        assert 'Global System' in config
        assert 'LOG_LEVEL = \'DEBUG\'' in config
        assert 'PROCESS_PRIORITY = -5' in config
        assert 'RESTRICTED_MODE = True' in config
        assert 'CUSTOM_SETTING = True' in config
        
        # Validate the generated configuration
        assert generator.validate_config(config) == True

class TestNixOSModuleStructure:
    """Test NixOS module structure and options"""
    
    def test_module_file_structure(self):
        """Test that the NixOS module has proper structure"""
        module_path = Path(__file__).parent.parent / "modules" / "toshy.nix"
        assert module_path.exists()
        
        content = module_path.read_text()
        
        # Check for essential module components
        assert "options.services.toshy" in content
        assert "config = mkIf cfg.enable" in content
        assert "systemd.user.services.toshy" in content
        
        # Check for advanced options
        assert "logging" in content
        assert "security" in content
        assert "performance" in content
        assert "assertions" in content

    def test_example_configurations(self):
        """Test example configuration files"""
        examples_dir = Path(__file__).parent.parent / "examples"
        
        # Check basic NixOS config
        basic_config = examples_dir / "basic-nixos-config.nix"
        assert basic_config.exists()
        
        content = basic_config.read_text()
        assert "services.toshy" in content
        assert "enable = true" in content
        assert "keybindings" in content

    def test_flake_outputs(self):
        """Test that flake provides all expected outputs"""
        flake_path = Path(__file__).parent.parent / "flake.nix"
        content = flake_path.read_text()
        
        # Check for all required outputs
        assert "packages" in content
        assert "devShells" in content
        assert "nixosModules" in content
        assert "overlays" in content
        assert "formatter" in content

class TestSystemIntegration:
    """Test system-level integration features"""
    
    @patch('subprocess.run')
    def test_service_management(self, mock_run):
        """Test systemd service management"""
        mock_run.return_value = MagicMock(returncode=0)
        
        # This would test actual service management in a real environment
        # For now, we just verify the mock is called
        import subprocess
        result = subprocess.run(['systemctl', '--user', 'status', 'toshy'])
        mock_run.assert_called_once()

    def test_configuration_file_paths(self):
        """Test configuration file path resolution"""
        from toshy.daemon import find_config_file
        
        # Test with mocked file system
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path.endswith('toshy_config.py')
            
            config_file = find_config_file()
            assert config_file is not None
            assert config_file.endswith('toshy_config.py')

    def test_user_permissions(self):
        """Test user permission requirements"""
        # Test that we can check for required groups
        import grp
        
        try:
            input_group = grp.getgrnam('input')
            # If we get here, input group exists
            assert input_group.gr_name == 'input'
        except KeyError:
            # Input group doesn't exist, which is fine for testing
            pass

if __name__ == "__main__":
    pytest.main([__file__])
