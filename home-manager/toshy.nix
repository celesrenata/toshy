{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.toshy;
  
  # Generate user-specific configuration
  userConfigContent = ''
    # User-specific Toshy configuration
    # Managed by Home Manager
    
    import os
    import sys
    from pathlib import Path
    
    # Import base keymapper functionality
    try:
        from xwaykeyz.models import *
        from xwaykeyz import *
    except ImportError:
        print("Error: xwaykeyz not found")
        sys.exit(1)
    
    # User configuration
    USER_CONFIG_VERSION = "1.0"
    HOME_MANAGER_MANAGED = True
    
    ${optionalString cfg.settings.macStyle ''
    # Mac-style keybindings for user
    keymap("User Mac Style", {
        # Basic shortcuts
        C("a"): C("ctrl-a"),
        C("c"): C("ctrl-c"),
        C("v"): C("ctrl-v"),
        C("x"): C("ctrl-x"),
        C("z"): C("ctrl-z"),
        C("s"): C("ctrl-s"),
        C("o"): C("ctrl-o"),
        C("n"): C("ctrl-n"),
        C("f"): C("ctrl-f"),
        C("w"): C("ctrl-w"),
        C("t"): C("ctrl-t"),
        C("q"): C("alt-f4"),
    })
    ''}
    
    ${concatStringsSep "\n" (mapAttrsToList (appName: bindings: ''
    # User configuration for ${appName}
    keymap("${appName}", {
    ${concatStringsSep ",\n" (mapAttrsToList (from: to: 
      "    \"${from}\": \"${to}\"") bindings)}
    })
    '') cfg.settings.applications)}
    
    ${cfg.extraConfig}
  '';

in {
  options.services.toshy = {
    enable = mkEnableOption "Toshy keybinding service (Home Manager)";
    
    package = mkOption {
      type = types.package;
      default = pkgs.toshy;
      description = "Toshy package to use";
    };
    
    settings = {
      macStyle = mkOption {
        type = types.bool;
        default = true;
        description = "Enable Mac-style keybindings";
      };
      
      applications = mkOption {
        type = types.attrsOf (types.attrsOf types.str);
        default = {};
        description = "Application-specific keybinding overrides";
        example = {
          "firefox" = {
            "Cmd+T" = "Ctrl+T";
            "Cmd+W" = "Ctrl+W";
          };
        };
      };
      
      theme = mkOption {
        type = types.enum ["light" "dark" "auto"];
        default = "auto";
        description = "GUI theme preference";
      };
      
      autostart = mkOption {
        type = types.bool;
        default = true;
        description = "Automatically start with desktop session";
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
    };
    
    extraConfig = mkOption {
      type = types.lines;
      default = "";
      description = "Additional configuration (Python code)";
      example = ''
        # Custom keybindings
        keymap("Custom", {
            C("shift-space"): C("alt-f2"),
        })
      '';
    };
  };

  config = mkIf cfg.enable {
    # Install Toshy package
    home.packages = [ cfg.package ];
    
    # Create configuration directory and files
    xdg.configFile."toshy/toshy_config.py" = {
      text = userConfigContent;
    };
    
    # Create data directories
    xdg.dataFile."toshy/.keep".text = "";
    xdg.cacheFile."toshy/.keep".text = "";
    
    # Systemd user services
    systemd.user.services.toshy = {
      Unit = {
        Description = "Toshy Keybinding Service (Home Manager)";
        Documentation = "https://github.com/celesrenata/toshy";
        After = [ "graphical-session.target" ];
        PartOf = [ "graphical-session.target" ];
      };
      
      Service = {
        Type = "simple";
        ExecStart = "${cfg.package}/bin/toshy-daemon";
        Restart = "always";
        RestartSec = 5;
        
        # Environment
        Environment = [
          "TOSHY_CONFIG_DIR=%h/.config/toshy"
          "TOSHY_LOG_LEVEL=INFO"
          "TOSHY_HOME_MANAGER=1"
        ];
      };
      
      Install = {
        WantedBy = mkIf cfg.settings.autostart [ "graphical-session.target" ];
      };
    };
    
    # GUI service
    systemd.user.services.toshy-gui = mkIf cfg.gui.enable {
      Unit = {
        Description = "Toshy GUI Service (Home Manager)";
        After = [ "graphical-session.target" "toshy.service" ];
        PartOf = [ "graphical-session.target" ];
      };
      
      Service = {
        Type = "simple";
        ExecStart = "${cfg.package}/bin/toshy-gui";
        Restart = "on-failure";
        RestartSec = 10;
        
        Environment = [
          "TOSHY_THEME=${cfg.settings.theme}"
        ];
      };
      
      Install = {
        WantedBy = mkIf cfg.settings.autostart [ "graphical-session.target" ];
      };
    };
    
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
        ];
      };
      
      Install = {
        WantedBy = mkIf cfg.settings.autostart [ "graphical-session.target" ];
      };
    };
    
    # Desktop entry for manual launching
    xdg.desktopEntries.toshy = {
      name = "Toshy";
      comment = "Mac-style keybindings for Linux";
      exec = "${cfg.package}/bin/toshy-gui";
      icon = "input-keyboard";
      categories = [ "Utility" "System" ];
      startupNotify = false;
    };
    
    # Autostart desktop entry
    xdg.configFile."autostart/toshy.desktop" = mkIf cfg.settings.autostart {
      text = ''
        [Desktop Entry]
        Type=Application
        Name=Toshy
        Comment=Mac-style keybindings for Linux
        Exec=${cfg.package}/bin/toshy-daemon
        Icon=input-keyboard
        Categories=Utility;System;
        StartupNotify=false
        Hidden=false
        X-GNOME-Autostart-enabled=true
      '';
    };
  };
}
