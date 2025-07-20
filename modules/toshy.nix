{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.toshy;
  
  # Generate configuration file content
  generateToshyConfig = {
    baseConfig = ''
      # Generated Toshy configuration
      # This file is managed by NixOS - do not edit manually
      
      import os
      import sys
      from pathlib import Path
      
      # Add the default config to Python path
      sys.path.insert(0, str(Path(__file__).parent))
      
      # Import base configuration
      try:
          from toshy_config_base import *
      except ImportError:
          # Fallback to minimal config if base not found
          from xwaykeyz.models import *
          
      # NixOS-managed configuration overrides
    '';
    
    macStyleConfig = optionalString cfg.keybindings.macStyle ''
      
      # Mac-style keybindings enabled
      ENABLE_MAC_STYLE_KEYBINDINGS = True
      
      # Common Mac-style shortcuts
      keymap("General", {
          # Text editing
          C("a"): C("ctrl-a"),          # Select all
          C("c"): C("ctrl-c"),          # Copy
          C("v"): C("ctrl-v"),          # Paste
          C("x"): C("ctrl-x"),          # Cut
          C("z"): C("ctrl-z"),          # Undo
          C("shift-z"): C("ctrl-y"),    # Redo
          
          # Navigation
          C("left"): C("home"),         # Beginning of line
          C("right"): C("end"),         # End of line
          C("up"): C("ctrl-home"),      # Beginning of document
          C("down"): C("ctrl-end"),     # End of document
          
          # Window management
          C("w"): C("ctrl-w"),          # Close window/tab
          C("t"): C("ctrl-t"),          # New tab
          C("shift-t"): C("ctrl-shift-t"), # Reopen closed tab
          C("tab"): C("ctrl-tab"),      # Next tab
          C("shift-tab"): C("ctrl-shift-tab"), # Previous tab
          
          # System shortcuts
          C("space"): C("alt-f2"),      # Application launcher
          C("q"): C("alt-f4"),          # Quit application
      })
    '';
    
    applicationConfigs = concatStringsSep "\n" (mapAttrsToList (appName: bindings: ''
      
      # Application-specific bindings for ${appName}
      keymap("${appName}", {
      ${concatStringsSep ",\n" (mapAttrsToList (from: to: 
        "    \"${from}\": \"${to}\"") bindings)}
      })
    '') cfg.keybindings.applications);
    
    customConfig = optionalString (cfg.config != "") ''
      
      # Custom user configuration
      ${cfg.config}
    '';
  };
  
  # Complete configuration content
  toshyConfigContent = concatStringsSep "\n" [
    generateToshyConfig.baseConfig
    generateToshyConfig.macStyleConfig
    generateToshyConfig.applicationConfigs
    generateToshyConfig.customConfig
  ];

in {
  options.services.toshy = {
    enable = mkEnableOption "Toshy keybinding service";
    
    package = mkPackageOption pkgs "toshy" { };
    
    user = mkOption {
      type = types.str;
      description = "User to run Toshy service as";
      example = "alice";
    };
    
    config = mkOption {
      type = types.lines;
      default = "";
      description = "Custom Toshy configuration";
      example = ''
        # Custom keybindings
        keymap("Custom", {
            C("shift-space"): C("alt-f2"),
        })
      '';
    };
    
    keybindings = {
      macStyle = mkOption {
        type = types.bool;
        default = true;
        description = "Enable Mac-style keybindings";
      };
      
      applications = mkOption {
        type = types.attrsOf (types.attrsOf types.str);
        default = {};
        description = "Application-specific keybindings";
        example = literalExpression ''
          {
            "Firefox" = {
              "Cmd+T" = "Ctrl+T";  # New tab
              "Cmd+W" = "Ctrl+W";  # Close tab
            };
          }
        '';
      };
    };
    
    gui = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable GUI components";
      };
      
      tray = mkOption {
        type = types.bool;
        default = true;
        description = "Enable system tray icon";
      };
      
      autostart = mkOption {
        type = types.bool;
        default = true;
        description = "Automatically start GUI components";
      };
      
      theme = mkOption {
        type = types.str;
        default = "auto";
        description = "GUI theme (auto, light, dark)";
      };
      
      fileManager = mkOption {
        type = types.str;
        default = "auto";
        description = "File manager to use (auto, or specific command)";
      };
      
      terminal = mkOption {
        type = types.str;
        default = "auto";
        description = "Terminal emulator to use (auto, or specific command)";
      };
    };
    
    wayland = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable Wayland support";
      };
      
      compositor = mkOption {
        type = types.str;
        default = "auto";
        description = "Wayland compositor (auto, hyprland, sway, wlroots, gnome, kde)";
      };
    };
    
    x11 = {
      enable = mkOption {
        type = types.bool;
        default = true;
        description = "Enable X11 support";
      };
      
      windowManager = mkOption {
        type = types.str;
        default = "auto";
        description = "X11 window manager (auto, i3, bspwm, xmonad, gnome, kde, xfce)";
      };
    };
    
    logging = {
      level = mkOption {
        type = types.str;
        default = "INFO";
        description = "Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)";
      };
      
      file = mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "Log file path (null for no file logging)";
        example = "/var/log/toshy.log";
      };
    };
    
    security = {
      restrictedMode = mkOption {
        type = types.bool;
        default = false;
        description = "Enable restricted security mode";
      };
    };
    
    performance = {
      priority = mkOption {
        type = types.int;
        default = 0;
        description = "Process priority (-20 to 19, lower is higher priority)";
      };
      
      memoryLimit = mkOption {
        type = types.str;
        default = "256M";
        description = "Memory limit for the service";
      };
      
      cpuQuota = mkOption {
        type = types.nullOr types.str;
        default = null;
        description = "CPU quota for the service (e.g., '50%')";
        example = "50%";
      };
    };
  };

  config = mkIf cfg.enable {
    # Main Toshy daemon service
    systemd.user.services.toshy = {
      description = "Toshy Keybinding Service";
      documentation = [ "https://github.com/celesrenata/toshy" ];
      
      wantedBy = [ "graphical-session.target" ];
      partOf = [ "graphical-session.target" ];
      after = [ "graphical-session.target" ];
      
      # Service dependencies - only include toshy-tray, not toshy-gui
      wants = optionals cfg.gui.tray [ "toshy-tray.service" ];
      
      serviceConfig = {
        Type = "simple";
        ExecStart = "${cfg.package}/bin/toshy-daemon";
        ExecReload = "${pkgs.coreutils}/bin/kill -HUP $MAINPID";
        
        # Restart configuration
        Restart = "always";
        RestartSec = 5;
        StartLimitBurst = 3;
        StartLimitIntervalSec = 30;
        
        # Security settings
        NoNewPrivileges = true;
        PrivateTmp = true;
        ProtectSystem = "strict";
        ProtectHome = false; # Need access to user config
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectControlGroups = true;
        
        # File system access
        ReadWritePaths = [ 
          "/home/${cfg.user}/.config/toshy"
          "/home/${cfg.user}/.local/share/toshy"
          "/home/${cfg.user}/.cache/toshy"
          # XDG_RUNTIME_DIR access is handled automatically by systemd user services
        ] ++ optionals (cfg.logging.file != null) [
          (dirOf cfg.logging.file)
        ];
        
        # Resource limits
        MemoryMax = cfg.performance.memoryLimit;
        TasksMax = 50;
        Nice = cfg.performance.priority;
      } // optionalAttrs (cfg.performance.cpuQuota != null) {
        CPUQuota = cfg.performance.cpuQuota;
      } // optionalAttrs (!cfg.security.restrictedMode) {
        # Additional permissions for full functionality
        # Note: SupplementaryGroups not supported in user services
        # User should be added to input group via users.users.${user}.extraGroups
      };
      
      environment = {
        TOSHY_CONFIG_DIR = "/home/${cfg.user}/.config/toshy";
        TOSHY_LOG_LEVEL = cfg.logging.level;
        TOSHY_USER = cfg.user;
        
        # GUI-specific environment
        TOSHY_DATA_DIR = "/home/${cfg.user}/.local/share/toshy";
        XDG_DATA_HOME = "/home/${cfg.user}/.local/share";
        XDG_CONFIG_HOME = "/home/${cfg.user}/.config";
        
        # Display environment  
        DISPLAY = ":0";
        # XDG_RUNTIME_DIR is automatically set by systemd for user services
        
        # Add libnotify to PATH for system commands needed by configuration and GUI
        PATH = mkForce "${pkgs.libnotify}/bin:${pkgs.coreutils}/bin:/etc/profiles/per-user/${cfg.user}/bin:/run/current-system/sw/bin";
        
        # GTK4 environment variables for GUI
        GI_TYPELIB_PATH = "${pkgs.gtk4}/lib/girepository-1.0:${pkgs.libadwaita}/lib/girepository-1.0:${pkgs.gobject-introspection}/lib/girepository-1.0";
        XDG_DATA_DIRS = "${pkgs.gtk4}/share:${pkgs.libadwaita}/share:${pkgs.gsettings-desktop-schemas}/share";
        GSK_RENDERER = "gl"; # Use OpenGL renderer for better performance
        
        # Ensure notify-send is available
        NOTIFY_SEND = "${pkgs.libnotify}/bin/notify-send";
      } // optionalAttrs cfg.wayland.enable {
        WAYLAND_DISPLAY = "wayland-1";  # Match actual socket name
        XDG_SESSION_TYPE = "wayland";
      } // optionalAttrs cfg.x11.enable {
        XDG_SESSION_TYPE = "x11";
      } // optionalAttrs (cfg.logging.file != null) {
        TOSHY_LOG_FILE = cfg.logging.file;
      };
    };
    
    # Tray service (optional) - keep this service
    systemd.user.services.toshy-tray = mkIf cfg.gui.tray {
      description = "Toshy System Tray";
      documentation = [ "https://github.com/celesrenata/toshy" ];
      
      wantedBy = optionals cfg.gui.autostart [ "graphical-session.target" ];
      partOf = [ "graphical-session.target" ];
      after = [ "graphical-session.target" "toshy.service" ];
      
      serviceConfig = {
        Type = "simple";
        ExecStart = "${cfg.package}/bin/toshy-tray";
        Restart = "on-failure";
        RestartSec = 10;
        
        # Add notify-send to PATH
        Environment = "PATH=${pkgs.libnotify}/bin:${pkgs.coreutils}/bin:/etc/profiles/per-user/${cfg.user}/bin:/run/current-system/sw/bin";
        
        # Security settings - relaxed for tray GTK compatibility
        NoNewPrivileges = false;  # GTK needs this
        PrivateTmp = false;       # GTK needs access to tmp
        ProtectSystem = "false";  # GTK needs system access
        ProtectHome = false;
        
        # Resource limits
        MemoryMax = "64M";
        TasksMax = 10;
      };
      
      environment = {
        DISPLAY = ":0";
        XDG_RUNTIME_DIR = "/run/user/1000";  # Use actual user ID
        TOSHY_THEME = cfg.gui.theme;
        # Wayland display for GTK
        WAYLAND_DISPLAY = "wayland-1";
        XDG_SESSION_TYPE = "wayland";
        # GTK backend preference - try GTK3 first for tray compatibility
        GDK_BACKEND = "x11,wayland";
        # Fix dconf permissions
        DCONF_USER_CONFIG_DIR = "/home/${cfg.user}/.config/dconf";
      } // optionalAttrs cfg.wayland.enable {
        WAYLAND_DISPLAY = "wayland-1";
      };
    };
    
    # Configuration file generation (system-wide)
    environment.etc."toshy/config.py" = mkIf (cfg.config != "" || cfg.keybindings.applications != {}) {
      text = toshyConfigContent;
      mode = "0644";
    };
    
    # Required system permissions and setup
    users.users.${cfg.user}.extraGroups = [ "input" ];
    
    # Ensure the configuration directory exists
    systemd.user.services.toshy-config-dir = {
      description = "Toshy Configuration Directory";
      wantedBy = [ "toshy.service" ];
      before = [ "toshy.service" ];
      
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${pkgs.coreutils}/bin/mkdir -p /home/${cfg.user}/.config/toshy";
        ExecStartPost = "${pkgs.coreutils}/bin/mkdir -p /home/${cfg.user}/.local/share/toshy";
        RemainAfterExit = true;
      };
    };
    
    # Logger service for file logging
    systemd.user.services.toshy-logger = mkIf (cfg.logging.file != null) {
      description = "Toshy Log Manager";
      wantedBy = [ "toshy.service" ];
      before = [ "toshy.service" ];
      
      serviceConfig = {
        Type = "oneshot";
        ExecStart = "${pkgs.coreutils}/bin/mkdir -p ${dirOf cfg.logging.file}";
        ExecStartPost = "${pkgs.coreutils}/bin/touch ${cfg.logging.file}";
        RemainAfterExit = true;
      };
    };
    
    # Logrotate configuration for log files
    services.logrotate.settings.toshy = mkIf (cfg.logging.file != null) {
      files = [ cfg.logging.file ];
      frequency = "weekly";
      rotate = 4;
      compress = true;
      delaycompress = true;
      missingok = true;
      notifempty = true;
      create = "644 ${cfg.user} users";
    };
    
    # Environment variables for all users
    environment.variables = {
      TOSHY_SYSTEM_ENABLED = "1";
    } // optionalAttrs cfg.wayland.enable {
      TOSHY_WAYLAND_ENABLED = "1";
    } // optionalAttrs cfg.x11.enable {
      TOSHY_X11_ENABLED = "1";
    };
    
    # Fonts for GUI components
    fonts.packages = mkIf cfg.gui.enable [
      pkgs.dejavu_fonts
      pkgs.liberation_ttf
    ];
  };
}
