# Phase 2: CLI Accessibility Improvement

## Objective
Ensure toshy-tray and toshy-gui are properly exposed as CLI commands and can be executed directly from the command line.

## Implementation Summary

### 1. Updated Entry Points in pyproject.toml
- Verified and updated the entry points in pyproject.toml
- Ensured all CLI commands are properly defined
- Added clear documentation for each entry point

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

### 2. Enhanced CLI Command Exposure in flake.nix
- Updated the flake.nix to ensure proper CLI command exposure
- Added a postInstall hook to ensure all CLI commands are executable
- Set toshy-tray as the mainProgram in the package metadata

```nix
# Ensure CLI commands are properly exposed
postInstall = ''
  # Make sure the CLI commands are executable
  for cmd in toshy-tray toshy-gui toshy-layout-selector toshy-config toshy-daemon toshy-config-generator toshy-platform toshy-debug toshy-performance; do
    chmod +x $out/bin/$cmd
  done
'';

meta = with pkgs.lib; {
  description = "Mac-style keybindings for Linux";
  homepage = "https://github.com/celesrenata/toshy";
  license = licenses.gpl3Plus;
  maintainers = [ ];
  platforms = platforms.linux;
  # Set toshy-tray as the main program
  mainProgram = "toshy-tray";
};
```

### 3. Created Test Script for CLI Commands
- Developed a test script to verify CLI command accessibility
- The script checks if each command is available in PATH
- It also verifies command permissions and help output

```bash
#!/bin/bash
set -e

echo "Testing Toshy CLI commands..."
echo "=============================="

# Function to test a command
test_command() {
    local cmd=$1
    local desc=$2
    
    echo -n "Testing $cmd ($desc)... "
    
    if command -v $cmd &> /dev/null; then
        echo "FOUND"
        echo "  Command path: $(which $cmd)"
        echo "  Command permissions: $(ls -l $(which $cmd))"
        echo "  Help output:"
        $cmd --help 2>&1 | head -n 5 | sed 's/^/    /'
        echo ""
    else
        echo "NOT FOUND"
        echo "  Error: $cmd command is not available in PATH"
        echo ""
    fi
}

# Test all CLI commands
test_command "toshy-tray" "System tray application"
test_command "toshy-gui" "GUI preferences application"
# ... other commands ...
```

### 4. Updated NixOS and Home Manager Modules
- Modified the NixOS module to ensure proper CLI command exposure
- Updated the Home Manager module to maintain consistency
- Prepared for Phase 3 by removing the toshy-gui service

## Testing
To test the CLI accessibility improvements, run the test script:

```bash
./test_cli_commands.sh
```

This will verify that all CLI commands are properly exposed and executable.

## Next Steps
- Phase 3: Service Configuration Optimization
  - Ensure only toshy-tray has a systemd service, not toshy-gui
  - Update the NixOS and Home Manager modules accordingly
  - Ensure toshy-gui can be launched from the tray

## Files Modified
- flake.nix
- pyproject.toml
- modules/toshy.nix
- home-manager/toshy.nix

## Files Created
- test_cli_commands.sh
- PHASE2_README.md
