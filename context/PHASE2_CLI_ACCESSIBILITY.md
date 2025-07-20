# Phase 2: CLI Accessibility Improvement

## Objective
Ensure toshy-tray and toshy-gui are properly exposed as CLI commands and can be executed directly from the command line.

## Background
The Toshy application should provide direct CLI access to its key components, particularly toshy-tray and toshy-gui. This ensures users can easily launch these components from the command line and that other applications can integrate with Toshy through these entry points.

## Tasks

### 1. Verify Entry Points in pyproject.toml
- Check that toshy-tray and toshy-gui are properly defined in the [project.scripts] section
- Ensure the entry points map to the correct functions in the codebase
- Add any missing entry points

**Current Configuration:**
```toml
[project.scripts]
toshy-tray = "toshy.tray:main"
toshy-gui = "toshy.gui.__main__:main"
toshy-layout-selector = "toshy.layout_selector:main"
toshy-config = "toshy.config:main"
toshy-daemon = "toshy.daemon:main"
toshy-config-generator = "toshy.config_generator:main"
toshy-platform = "toshy.platform_utils:main"
toshy-debug = "toshy.debug_utils:main"
toshy-performance = "toshy.performance_utils:main"
```

**Implementation Details:**
- Verify that the entry point functions exist and are properly implemented
- Check for any inconsistencies between the entry point definitions and the actual code
- Ensure the entry points handle command-line arguments correctly

### 2. Ensure Proper Exposure in flake.nix
- Check that the flake.nix correctly exposes the CLI commands
- Verify that the commands are included in the package outputs
- Ensure the commands are properly wrapped with necessary environment variables

**Key Areas to Check:**
```nix
# In flake.nix
packages = {
  inherit toshy xwaykeyz;
  default = toshy;
};

# In the toshy package definition
meta = with pkgs.lib; {
  description = "Mac-style keybindings for Linux";
  homepage = "https://github.com/celesrenata/toshy";
  license = licenses.gpl3Plus;
  maintainers = [ ];
  platforms = platforms.linux;
  mainProgram = "toshy-tray";  # Verify this is correct
};
```

**Implementation Details:**
- Ensure the package's meta.mainProgram is set correctly
- Check that all CLI commands are properly installed to the bin directory
- Verify that the commands have the correct permissions and are executable

### 3. Test Direct CLI Execution
- Create a test script to verify that all CLI commands can be executed directly
- Test with both absolute and relative paths
- Verify that the commands work with different arguments
- Check for proper exit codes and error handling

**Test Script Example:**
```bash
#!/bin/bash
set -e

echo "Testing toshy-tray CLI command..."
which toshy-tray
toshy-tray --help

echo "Testing toshy-gui CLI command..."
which toshy-gui
toshy-gui --help

echo "Testing toshy-gui with different arguments..."
toshy-gui --gtk4
toshy-gui --tk
toshy-gui --verbose

echo "All CLI commands are working correctly!"
```

### 4. Add Error Handling and User Feedback
- Improve error handling in the CLI entry points
- Add clear error messages for common issues
- Implement proper argument parsing
- Add --help and --version flags to all commands

**Example Implementation:**
```python
def main():
    parser = argparse.ArgumentParser(description='Toshy Tray Application')
    parser.add_argument('--version', action='version', version=f'Toshy Tray {__version__}')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--no-autostart', action='store_true', help='Do not automatically start services')
    
    args = parser.parse_args()
    
    if args.verbose:
        import toshy_common.logger
        toshy_common.logger.VERBOSE = True
    
    try:
        # Main application code
        run_tray_application(autostart=not args.no_autostart)
    except KeyboardInterrupt:
        print("Toshy Tray application terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
```

### 5. Update Documentation
- Update the README.md to clearly document the available CLI commands
- Add examples of common usage patterns
- Document all command-line arguments
- Add troubleshooting information for common issues

**Documentation Example:**
```markdown
## CLI Commands

Toshy provides several command-line tools:

### toshy-tray
Launches the Toshy system tray application.

```bash
toshy-tray [--verbose] [--no-autostart]
```

Options:
- `--verbose`: Enable verbose logging
- `--no-autostart`: Do not automatically start services

### toshy-gui
Launches the Toshy GUI preferences application.

```bash
toshy-gui [--gtk4 | --tk] [--verbose]
```

Options:
- `--gtk4`: Use the GTK4 interface (default)
- `--tk`: Use the Tkinter interface
- `--verbose`: Enable verbose logging
```

## Potential Issues
1. **Path Issues**: The commands might not be in the user's PATH
2. **Permission Problems**: The commands might not have the correct executable permissions
3. **Environment Variables**: The commands might require specific environment variables
4. **Dependencies**: The commands might fail if dependencies are not properly installed
5. **Wrapper Scripts**: The Nix-generated wrapper scripts might have issues

## Success Criteria
- toshy-tray and toshy-gui can be executed directly from the command line
- The commands work with all documented arguments
- The commands provide clear error messages for common issues
- The commands are properly documented in the README.md
- The commands work in different environments (e.g., with and without a desktop environment)

## Files to Modify
- pyproject.toml (if entry points need to be added or modified)
- flake.nix (to ensure proper command exposure)
- toshy_tray.py (to improve CLI handling)
- toshy_gui/__main__.py (to improve CLI handling)
- README.md (to update documentation)
