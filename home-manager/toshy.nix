{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.toshy;
in {
  options.services.toshy = {
    enable = mkEnableOption "Toshy keybinding service";
    
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
      
      theme = mkOption {
        type = types.str;
        default = "auto";
        description = "GUI theme (auto, light, dark)";
      };
      
      autostart = mkOption {
        type = types.bool;
        default = true;
        description = "Automatically start services";
      };
      
      applications = mkOption {
        type = types.attrsOf (types.attrsOf types.str);
        default = {};
        description = "Application-specific keybindings";
        example = literalExpression ''
          {
            "firefox" = {
              "Cmd+T" = "Ctrl+T";
              "Cmd+W" = "Ctrl+W";
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
    };
    
    extraConfig = mkOption {
      type = types.lines;
      default = "";
      description = "Extra configuration to append to toshy_config.py";
      example = ''
        # Custom keybindings
        keymap("Custom", {
            C("shift-space"): C("alt-f2"),
        })
      '';
    };
  };

  config = mkIf cfg.enable {
    # Add the package to the user's packages
    home.packages = [ cfg.package ];
    
    # Create the configuration directory
    home.file.".config/toshy/.keep".text = "";
    
    # Generate the configuration file
    home.file.".config/toshy/toshy_config.py" = mkIf (cfg.extraConfig != "" || cfg.settings.applications != {}) {
      text = ''
        # Generated Toshy configuration for Home Manager
        # This file is managed by Home Manager - do not edit manually
        
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
        
        # Home Manager configuration
        
        # Mac-style keybindings
        ${optionalString cfg.settings.macStyle ''
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
        ''}
        
        # Application-specific keybindings
        ${concatStringsSep "\n\n" (mapAttrsToList (appName: bindings: ''
        # Bindings for ${appName}
        keymap("${appName}", {
        ${concatStringsSep ",\n" (mapAttrsToList (from: to: 
          "    \"${from}\": \"${to}\"") bindings)}
        })
        '') cfg.settings.applications)}
        
        # Extra configuration
        ${cfg.extraConfig}
      '';
      
      onChange = ''
        # Restart the service if it's running
        if systemctl --user is-active toshy.service &>/dev/null; then
          systemctl --user restart toshy.service
        fi
      '';
    };
    
    # Main service
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
    
    # Tray service - keep this service
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
