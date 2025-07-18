#!/usr/bin/env python3
"""
Toshy Config - Configuration management utilities
"""

import sys
import os
import argparse
import shutil
from pathlib import Path

def find_config_file():
    """Find the current Toshy configuration file"""
    config_locations = [
        os.path.expanduser("~/.config/toshy/toshy_config.py"),
        "/etc/toshy/toshy_config.py",
    ]
    
    for config_path in config_locations:
        if os.path.exists(config_path):
            return config_path
    
    return None

def validate_config(config_file):
    """Validate a Toshy configuration file"""
    if not os.path.exists(config_file):
        print(f"Error: Configuration file not found: {config_file}", file=sys.stderr)
        return False
    
    try:
        # Try to compile the Python file to check for syntax errors
        with open(config_file, 'r') as f:
            content = f.read()
        
        compile(content, config_file, 'exec')
        print(f"✓ Configuration file syntax is valid: {config_file}")
        return True
        
    except SyntaxError as e:
        print(f"✗ Syntax error in configuration file: {config_file}", file=sys.stderr)
        print(f"  Line {e.lineno}: {e.text.strip() if e.text else ''}", file=sys.stderr)
        print(f"  {e.msg}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"✗ Error validating configuration file: {e}", file=sys.stderr)
        return False

def show_config_info():
    """Show information about the current configuration"""
    config_file = find_config_file()
    
    if not config_file:
        print("No Toshy configuration file found.")
        print("Expected locations:")
        print("  ~/.config/toshy/toshy_config.py")
        print("  /etc/toshy/toshy_config.py")
        return False
    
    print(f"Current configuration file: {config_file}")
    
    # Show file info
    stat = os.stat(config_file)
    print(f"Size: {stat.st_size} bytes")
    print(f"Modified: {Path(config_file).stat().st_mtime}")
    
    # Validate the config
    return validate_config(config_file)

def backup_config():
    """Create a backup of the current configuration"""
    config_file = find_config_file()
    
    if not config_file:
        print("No configuration file found to backup.", file=sys.stderr)
        return False
    
    backup_file = f"{config_file}.backup"
    try:
        shutil.copy2(config_file, backup_file)
        print(f"Configuration backed up to: {backup_file}")
        return True
    except Exception as e:
        print(f"Error creating backup: {e}", file=sys.stderr)
        return False

def restore_config():
    """Restore configuration from backup"""
    config_file = find_config_file()
    
    if not config_file:
        print("No configuration file location found.", file=sys.stderr)
        return False
    
    backup_file = f"{config_file}.backup"
    
    if not os.path.exists(backup_file):
        print(f"No backup file found: {backup_file}", file=sys.stderr)
        return False
    
    try:
        shutil.copy2(backup_file, config_file)
        print(f"Configuration restored from: {backup_file}")
        return True
    except Exception as e:
        print(f"Error restoring backup: {e}", file=sys.stderr)
        return False

def install_default_config():
    """Install the default Toshy configuration"""
    config_dir = os.path.expanduser("~/.config/toshy")
    config_file = os.path.join(config_dir, "toshy_config.py")
    
    # Find the default config file
    default_config_locations = [
        os.path.join(os.path.dirname(__file__), "..", "default-toshy-config", "toshy_config.py"),
        "/usr/share/toshy/default-toshy-config/toshy_config.py",
    ]
    
    default_config = None
    for location in default_config_locations:
        if os.path.exists(location):
            default_config = location
            break
    
    if not default_config:
        print("Error: Default configuration file not found", file=sys.stderr)
        return False
    
    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    
    # Check if config already exists
    if os.path.exists(config_file):
        response = input(f"Configuration file already exists: {config_file}\nOverwrite? (y/N): ")
        if response.lower() != 'y':
            print("Installation cancelled.")
            return False
        
        # Backup existing config
        backup_config()
    
    try:
        shutil.copy2(default_config, config_file)
        print(f"Default configuration installed to: {config_file}")
        return True
    except Exception as e:
        print(f"Error installing default configuration: {e}", file=sys.stderr)
        return False

def main():
    """Main entry point for toshy-config command"""
    parser = argparse.ArgumentParser(
        description="Toshy configuration management tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  toshy-config --info          Show current configuration info
  toshy-config --validate      Validate configuration syntax
  toshy-config --backup        Create configuration backup
  toshy-config --restore       Restore from backup
  toshy-config --install       Install default configuration
        """
    )
    
    parser.add_argument('--info', action='store_true',
                       help='Show information about current configuration')
    parser.add_argument('--validate', metavar='FILE',
                       help='Validate configuration file (default: current config)')
    parser.add_argument('--backup', action='store_true',
                       help='Create backup of current configuration')
    parser.add_argument('--restore', action='store_true',
                       help='Restore configuration from backup')
    parser.add_argument('--install', action='store_true',
                       help='Install default configuration')
    
    args = parser.parse_args()
    
    # If no arguments provided, show info by default
    if not any(vars(args).values()):
        args.info = True
    
    success = True
    
    if args.info:
        success = show_config_info() and success
    
    if args.validate:
        if args.validate == 'current':
            config_file = find_config_file()
            if not config_file:
                print("No current configuration file found.", file=sys.stderr)
                success = False
            else:
                success = validate_config(config_file) and success
        else:
            success = validate_config(args.validate) and success
    
    if args.backup:
        success = backup_config() and success
    
    if args.restore:
        success = restore_config() and success
    
    if args.install:
        success = install_default_config() and success
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
