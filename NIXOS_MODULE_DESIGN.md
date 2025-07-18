# Toshy NixOS Module Design

## Module Structure

The NixOS module should provide a clean interface for configuring Toshy system-wide or per-user.

### Configuration Options

```nix
services.toshy = {
  enable = lib.mkEnableOption "Toshy keybinding service";
  
  package = lib.mkPackageOption pkgs "toshy" { };
  
  user = lib.mkOption {
    type = lib.types.str;
    description = "User to run Toshy service as";
    example = "alice";
  };
  
  config = lib.mkOption {
    type = lib.types.lines;
    default = "";
    description = "Custom Toshy configuration";
    example = ''
      # Custom keybindings
      keymap("Terminal", {
          C("c"): C("shift-c"),  # Copy in terminal
          C("v"): C("shift-v"),  # Paste in terminal
      })
    '';
  };
  
  gui = {
    enable = lib.mkEnableOption "Toshy GUI components";
    
    tray = lib.mkEnableOption "System tray icon";
    
    theme = lib.mkOption {
      type = lib.types.enum ["light" "dark" "auto"];
      default = "auto";
      description = "GUI theme preference";
    };
  };
  
  keybindings = {
    macStyle = lib.mkEnableOption "Mac-style keybindings" // { default = true; };
    
    applications = lib.mkOption {
      type = lib.types.attrsOf (lib.types.attrsOf lib.types.str);
      default = {};
      description = "Application-specific keybinding overrides";
      example = {
        "Firefox" = {
          "Cmd+T" = "Ctrl+T";  # New tab
          "Cmd+W" = "Ctrl+W";  # Close tab
        };
      };
    };
  };
  
  wayland = {
    enable = lib.mkEnableOption "Wayland support";
    
    compositor = lib.mkOption {
      type = lib.types.enum ["hyprland" "sway" "wlroots" "auto"];
      default = "auto";
      description = "Wayland compositor to integrate with";
    };
  };
  
  x11 = {
    enable = lib.mkEnableOption "X11 support";
    
    windowManager = lib.mkOption {
      type = lib.types.enum ["i3" "bspwm" "xmonad" "auto"];
      default = "auto";
      description = "X11 window manager to integrate with";
    };
  };
};
```

### Service Implementation

```nix
config = lib.mkIf cfg.enable {
  # System packages
  environment.systemPackages = [ cfg.package ];
  
  # User service
  systemd.user.services.toshy = {
    description = "Toshy Keybinding Service";
    wantedBy = [ "graphical-session.target" ];
    partOf = [ "graphical-session.target" ];
    
    serviceConfig = {
      Type = "simple";
      ExecStart = "${cfg.package}/bin/toshy-daemon";
      Restart = "on-failure";
      RestartSec = 5;
    };
    
    environment = {
      TOSHY_CONFIG_DIR = "/home/${cfg.user}/.config/toshy";
      TOSHY_LOG_LEVEL = "INFO";
    };
  };
  
  # GUI service (optional)
  systemd.user.services.toshy-gui = lib.mkIf cfg.gui.enable {
    description = "Toshy GUI Service";
    wantedBy = [ "graphical-session.target" ];
    partOf = [ "graphical-session.target" ];
    
    serviceConfig = {
      Type = "simple";
      ExecStart = "${cfg.package}/bin/toshy-gui";
      Restart = "on-failure";
      RestartSec = 5;
    };
  };
  
  # Configuration file generation
  environment.etc."toshy/config.py" = lib.mkIf (cfg.config != "") {
    text = cfg.config;
    mode = "0644";
  };
  
  # Required system permissions
  security.polkit.enable = true;
  
  # Input group access for evdev
  users.groups.input = {};
  users.users.${cfg.user}.extraGroups = [ "input" ];
  
  # Udev rules for device access
  services.udev.extraRules = ''
    # Allow input group to access input devices
    KERNEL=="event*", GROUP="input", MODE="0664"
    SUBSYSTEM=="input", GROUP="input", MODE="0664"
  '';
};
```

## Home Manager Integration

For user-level configuration:

```nix
services.toshy = {
  enable = true;
  
  settings = {
    gui.enable = true;
    gui.tray = true;
    
    keybindings = {
      macStyle = true;
      applications = {
        "code" = {
          "Cmd+P" = "Ctrl+Shift+P";  # Command palette
          "Cmd+Shift+P" = "Ctrl+P";  # File search
        };
      };
    };
  };
};
```

## Configuration File Management

### Default Configuration
The module should provide sensible defaults that work out of the box.

### User Customization
- Allow inline configuration via Nix options
- Support external configuration files
- Merge system and user configurations

### Dynamic Reconfiguration
- Support configuration reloading without restart
- Validate configuration before applying
- Provide configuration testing tools

## Security Considerations

### Permissions
- Minimal required permissions
- Input device access only when needed
- No root privileges required

### Isolation
- Run as unprivileged user
- Sandbox GUI components
- Limit system access

### Configuration Validation
- Validate keybinding syntax
- Check for conflicts
- Prevent dangerous configurations
