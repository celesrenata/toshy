#!/usr/bin/env python3
"""
Toshy Configuration Generator

Generates Toshy configuration files from NixOS module options.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

class ToshyConfigGenerator:
    """Generate Toshy configuration files from structured data"""
    
    def __init__(self):
        self.config_template = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Toshy Configuration - Generated by NixOS
This file is automatically generated. Manual changes will be overwritten.
"""

import os
import sys
from pathlib import Path

# Import the keymapper API
try:
    from xwaykeyz.models import *
    from xwaykeyz import *
except ImportError:
    print("Error: xwaykeyz not found. Please ensure it is installed.")
    sys.exit(1)

# Configuration metadata
GENERATED_BY = "NixOS Toshy Module"
GENERATION_TIME = "{generation_time}"

{base_config}

{mac_style_config}

{application_configs}

{global_shortcuts}

{custom_config}

# Configuration validation
if __name__ == "__main__":
    print(f"Toshy configuration loaded successfully")
    print(f"Generated by: {{GENERATED_BY}}")
    print(f"Generation time: {{GENERATION_TIME}}")
'''

    def generate_base_config(self, options: Dict[str, Any]) -> str:
        """Generate base configuration section"""
        config = []
        
        # Basic settings
        config.append("# Base configuration")
        config.append("TOSHY_CONFIG_VERSION = '1.0'")
        
        # Logging configuration
        log_level = options.get('logging', {}).get('level', 'INFO')
        config.append(f"LOG_LEVEL = '{log_level}'")
        
        # Performance settings
        performance = options.get('performance', {})
        if performance.get('priority'):
            config.append(f"PROCESS_PRIORITY = {performance['priority']}")
        
        # Security settings
        security = options.get('security', {})
        if security.get('restrictedMode'):
            config.append("RESTRICTED_MODE = True")
        
        return '\n'.join(config)

    def generate_mac_style_config(self, enable_mac_style: bool) -> str:
        """Generate Mac-style keybinding configuration"""
        if not enable_mac_style:
            return "# Mac-style keybindings disabled"
        
        config = '''
# Mac-style keybindings configuration
MAC_STYLE_ENABLED = True

# Define the main keymap for Mac-style shortcuts
keymap("Mac-style Global", {
    # Text editing shortcuts
    C("a"):         C("ctrl-a"),        # Select all
    C("c"):         C("ctrl-c"),        # Copy
    C("v"):         C("ctrl-v"),        # Paste
    C("x"):         C("ctrl-x"),        # Cut
    C("z"):         C("ctrl-z"),        # Undo
    C("shift-z"):   C("ctrl-y"),        # Redo
    C("s"):         C("ctrl-s"),        # Save
    C("o"):         C("ctrl-o"),        # Open
    C("n"):         C("ctrl-n"),        # New
    C("p"):         C("ctrl-p"),        # Print
    C("f"):         C("ctrl-f"),        # Find
    C("g"):         C("ctrl-g"),        # Find next
    C("shift-g"):   C("ctrl-shift-g"),  # Find previous
    C("h"):         C("ctrl-h"),        # Replace
    
    # Navigation shortcuts
    C("left"):      C("home"),          # Beginning of line
    C("right"):     C("end"),           # End of line
    C("up"):        C("ctrl-home"),     # Beginning of document
    C("down"):      C("ctrl-end"),      # End of document
    C("shift-left"): C("shift-home"),   # Select to beginning of line
    C("shift-right"): C("shift-end"),   # Select to end of line
    C("shift-up"):  C("ctrl-shift-home"), # Select to beginning
    C("shift-down"): C("ctrl-shift-end"), # Select to end
    
    # Word navigation
    C("alt-left"):  C("ctrl-left"),     # Previous word
    C("alt-right"): C("ctrl-right"),    # Next word
    C("alt-shift-left"): C("ctrl-shift-left"),   # Select previous word
    C("alt-shift-right"): C("ctrl-shift-right"), # Select next word
    
    # Window and tab management
    C("w"):         C("ctrl-w"),        # Close window/tab
    C("shift-w"):   C("ctrl-shift-w"),  # Close window
    C("t"):         C("ctrl-t"),        # New tab
    C("shift-t"):   C("ctrl-shift-t"),  # Reopen closed tab
    C("tab"):       C("ctrl-tab"),      # Next tab
    C("shift-tab"): C("ctrl-shift-tab"), # Previous tab
    C("1"):         C("ctrl-1"),        # Switch to tab 1
    C("2"):         C("ctrl-2"),        # Switch to tab 2
    C("3"):         C("ctrl-3"),        # Switch to tab 3
    C("4"):         C("ctrl-4"),        # Switch to tab 4
    C("5"):         C("ctrl-5"),        # Switch to tab 5
    C("6"):         C("ctrl-6"),        # Switch to tab 6
    C("7"):         C("ctrl-7"),        # Switch to tab 7
    C("8"):         C("ctrl-8"),        # Switch to tab 8
    C("9"):         C("ctrl-9"),        # Switch to tab 9
    
    # Application shortcuts
    C("q"):         C("alt-f4"),        # Quit application
    C("m"):         C("alt-f9"),        # Minimize window
    C("shift-m"):   C("alt-f10"),       # Maximize window
    
    # System shortcuts
    C("space"):     C("alt-f2"),        # Application launcher
    C("shift-space"): C("alt-f1"),      # System menu
})
'''
        return config

    def generate_application_configs(self, applications: Dict[str, Dict[str, str]]) -> str:
        """Generate application-specific configurations"""
        if not applications:
            return "# No application-specific configurations"
        
        configs = ["# Application-specific keybinding configurations"]
        
        for app_name, bindings in applications.items():
            configs.append(f'\n# Configuration for {app_name}')
            configs.append(f'keymap("{app_name}", {{')
            
            for mac_key, linux_key in bindings.items():
                # Convert key notation if needed
                mac_formatted = self._format_key_binding(mac_key)
                linux_formatted = self._format_key_binding(linux_key)
                configs.append(f'    {mac_formatted}: {linux_formatted},')
            
            configs.append('})')
        
        return '\n'.join(configs)

    def generate_global_shortcuts(self, shortcuts: Dict[str, str]) -> str:
        """Generate global system shortcuts"""
        if not shortcuts:
            return "# No global shortcuts configured"
        
        configs = ["# Global system shortcuts"]
        configs.append('keymap("Global System", {')
        
        for mac_key, linux_key in shortcuts.items():
            mac_formatted = self._format_key_binding(mac_key)
            linux_formatted = self._format_key_binding(linux_key)
            configs.append(f'    {mac_formatted}: {linux_formatted},')
        
        configs.append('})')
        
        return '\n'.join(configs)

    def _format_key_binding(self, key_binding: str) -> str:
        """Format key binding for xwaykeyz syntax"""
        # Convert common key notations
        key_binding = key_binding.replace('Cmd+', 'C("').replace('Ctrl+', 'C("')
        key_binding = key_binding.replace('Alt+', 'A("').replace('Shift+', 'shift-')
        
        # Handle special cases
        if key_binding.startswith('C("') and not key_binding.endswith('")'):
            key_binding += '")'
        elif key_binding.startswith('A("') and not key_binding.endswith('")'):
            key_binding += '")'
        elif not (key_binding.startswith('C("') or key_binding.startswith('A("')):
            # Simple key
            key_binding = f'K("{key_binding.lower()}")'
        
        return key_binding

    def generate_config(self, options: Dict[str, Any], custom_config: str = "") -> str:
        """Generate complete configuration file"""
        import datetime
        
        generation_time = datetime.datetime.now().isoformat()
        
        # Generate each section
        base_config = self.generate_base_config(options)
        
        keybindings = options.get('keybindings', {})
        mac_style_config = self.generate_mac_style_config(
            keybindings.get('macStyle', False)
        )
        
        application_configs = self.generate_application_configs(
            keybindings.get('applications', {})
        )
        
        global_shortcuts = self.generate_global_shortcuts(
            keybindings.get('globalShortcuts', {})
        )
        
        # Format the complete configuration
        return self.config_template.format(
            generation_time=generation_time,
            base_config=base_config,
            mac_style_config=mac_style_config,
            application_configs=application_configs,
            global_shortcuts=global_shortcuts,
            custom_config=custom_config or "# No custom configuration"
        )

    def validate_config(self, config_content: str) -> bool:
        """Validate generated configuration"""
        try:
            compile(config_content, '<generated_config>', 'exec')
            return True
        except SyntaxError as e:
            print(f"Configuration validation failed: {e}")
            return False

def main():
    """Main entry point for configuration generator"""
    parser = argparse.ArgumentParser(
        description="Generate Toshy configuration from NixOS options"
    )
    parser.add_argument('--options', required=True,
                       help='JSON file containing NixOS module options')
    parser.add_argument('--output', required=True,
                       help='Output configuration file path')
    parser.add_argument('--custom-config', 
                       help='Additional custom configuration file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate generated configuration')
    
    args = parser.parse_args()
    
    # Load options from JSON
    try:
        with open(args.options, 'r') as f:
            options = json.load(f)
    except Exception as e:
        print(f"Error loading options: {e}")
        return 1
    
    # Load custom configuration if provided
    custom_config = ""
    if args.custom_config and os.path.exists(args.custom_config):
        with open(args.custom_config, 'r') as f:
            custom_config = f.read()
    
    # Generate configuration
    generator = ToshyConfigGenerator()
    config_content = generator.generate_config(options, custom_config)
    
    # Validate if requested
    if args.validate:
        if not generator.validate_config(config_content):
            return 1
        print("Configuration validation passed")
    
    # Write output file
    try:
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(config_content)
        print(f"Configuration generated: {args.output}")
        return 0
    except Exception as e:
        print(f"Error writing configuration: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
