# Phase 3: Service Configuration Optimization

## Objective
Ensure only toshy-tray has a systemd service, not toshy-gui, while maintaining full functionality.

## Background
Currently, both toshy-tray and toshy-gui have systemd services defined in the NixOS module. According to the requirements, we should only have a service for toshy-tray, not for toshy-gui. This will reduce system overhead and simplify the service architecture while ensuring that toshy-gui can still be launched manually or from the tray icon.

## Tasks

### 1. Review Current Service Configurations
- Analyze the current systemd service configurations in modules/toshy.nix
- Understand the dependencies and relationships between the services
- Identify how toshy-gui is currently integrated with toshy-tray

**Current Configuration (modules/toshy.nix):**
```nix
# Main Toshy daemon service
systemd.user.services.toshy = {
  description = "Toshy Keybinding Service";
  # ...
  wants = optionals cfg.gui.enable [ "toshy-gui.service" ]
       ++ optionals cfg.gui.tray [ "toshy-tray.service" ];
  # ...
};

# GUI service (optional)
systemd.user.services.toshy-gui = mkIf cfg.gui.enable {
  description = "Toshy GUI Service";
  # ...
};

# Tray service (optional)
systemd.user.services.toshy-tray = mkIf cfg.gui.tray {
  description = "Toshy System Tray";
  # ...
};
```

### 2. Modify the NixOS Module
- Update modules/toshy.nix to remove the toshy-gui service
- Ensure toshy-tray service is properly configured
- Update service dependencies to maintain functionality

**Implementation Details:**
```nix
# Main Toshy daemon service
systemd.user.services.toshy = {
  description = "Toshy Keybinding Service";
  # ...
  # Remove toshy-gui.service from wants
  wants = optionals cfg.gui.tray [ "toshy-tray.service" ];
  # ...
};

# Remove the toshy-gui service definition entirely
# systemd.user.services.toshy-gui = mkIf cfg.gui.enable { ... };

# Tray service (optional)
systemd.user.services.toshy-tray = mkIf cfg.gui.tray {
  description = "Toshy System Tray";
  # ...
  # Add functionality to launch GUI when needed
  serviceConfig = {
    # ...
    ExecStart = "${cfg.package}/bin/toshy-tray";
    # ...
  };
  # ...
};
```

### 3. Update the Home Manager Module
- Make similar changes to the Home Manager module (home-manager/toshy.nix)
- Ensure consistency between NixOS and Home Manager modules
- Maintain backward compatibility for existing users

**Implementation Details:**
```nix
# In home-manager/toshy.nix

# Remove the toshy-gui service definition
# systemd.user.services.toshy-gui = mkIf cfg.gui.enable { ... };

# Tray service
systemd.user.services.toshy-tray = mkIf cfg.gui.tray {
  Unit = {
    Description = "Toshy System Tray (Home Manager)";
    After = [ "graphical-session.target" "toshy.service" ];
    PartOf = [ "graphical-session.target" ];
  };
  
  Service = {
    Type = "simple";
    ExecStart = "${cfg.package}/bin/toshy-tray";
    Restart = "on-failure";
    RestartSec = 10;
    
    Environment = [
      "TOSHY_THEME=${cfg.settings.theme}"
      "TOSHY_GUI_ENABLED=${toString cfg.gui.enable}"
    ];
  };
  
  Install = {
    WantedBy = mkIf cfg.settings.autostart [ "graphical-session.target" ];
  };
};
```

### 4. Ensure toshy-gui Can Be Launched from Tray
- Modify toshy_tray.py to include functionality to launch toshy-gui
- Add a menu item to launch the GUI preferences
- Ensure proper error handling for GUI launch

**Implementation Details:**
```python
def fn_open_preferences(widget):
    # First check if toshy-gui exists
    toshy_gui_cmd = shutil.which('toshy-gui')
    if not toshy_gui_cmd:
        _ntfy_icon = icon_file_inverse
        _ntfy_msg = ("The 'toshy-gui' utility is missing.\r"
                    "Please check your installation.")
        ntfy.send_notification(_ntfy_msg, _ntfy_icon, urgency='critical')
        _error_msg = ("The 'toshy-gui' utility is missing.\n"
                    "     Please check your installation.")
        error(f"{_error_msg}")
        return

    # Launch the process
    process = subprocess.Popen([toshy_gui_cmd], stdout=PIPE, stderr=PIPE)

    # Wait a short time to see if it exits immediately
    time.sleep(1)

    # Check if it's still running
    return_code = process.poll()

    if return_code is not None:
        # Process has already terminated
        stderr = process.stderr.read().decode()
        stdout = process.stdout.read().decode()

        _ntfy_icon = icon_file_inverse
        _ntfy_msg = (f"'toshy-gui' exited too quickly (code {return_code}).\r"
                    f"Error: {stderr.strip() if stderr else 'No error output'}")
        ntfy.send_notification(_ntfy_msg, _ntfy_icon, urgency='critical')

        _error_msg = (f"'toshy-gui' exited too quickly with code {return_code}.\n"
                    f"     Error: {stderr.strip() if stderr else 'No error output'}")
        error(f"{_error_msg}")
        return

    # Process is running normally
    return
```

### 5. Test Service Management
- Test starting, stopping, enabling, and disabling the toshy-tray service
- Verify that toshy-gui can be launched from the tray
- Ensure that the services work correctly in different environments
- Test with both NixOS and Home Manager configurations

**Test Script Example:**
```bash
#!/bin/bash
set -e

echo "Testing toshy-tray service management..."

echo "Starting toshy-tray service..."
systemctl --user start toshy-tray

echo "Checking service status..."
systemctl --user status toshy-tray

echo "Stopping toshy-tray service..."
systemctl --user stop toshy-tray

echo "Enabling toshy-tray service..."
systemctl --user enable toshy-tray

echo "Disabling toshy-tray service..."
systemctl --user disable toshy-tray

echo "Service management tests completed successfully!"
```

## Potential Issues
1. **Backward Compatibility**: Existing users might rely on the toshy-gui service
2. **Service Dependencies**: Removing the toshy-gui service might affect other services
3. **Environment Variables**: The toshy-gui command might require specific environment variables
4. **Desktop Integration**: The toshy-gui command might not work correctly in all desktop environments
5. **User Experience**: Users might expect the GUI to start automatically

## Success Criteria
- Only toshy-tray has a systemd service, not toshy-gui
- toshy-gui can still be launched manually from the command line
- toshy-gui can be launched from the toshy-tray menu
- The application works correctly with the updated service configuration
- Documentation is updated to reflect the changes

## Files to Modify
- modules/toshy.nix (to remove the toshy-gui service)
- home-manager/toshy.nix (to remove the toshy-gui service)
- toshy_tray.py (to ensure toshy-gui can be launched from the tray)
- README.md (to update documentation)
