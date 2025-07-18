# Example Home Manager configuration using Toshy
{ config, pkgs, ... }:

{
  # Import Toshy Home Manager module
  imports = [
    # Add this to your Home Manager configuration:
    # inputs.toshy.homeManagerModules.toshy
  ];

  # Toshy configuration for the user
  services.toshy = {
    enable = true;
    
    # Basic settings
    settings = {
      macStyle = true;
      theme = "auto";
      autostart = true;
      
      # Application-specific keybindings
      applications = {
        # Web browsers
        "firefox" = {
          "Cmd+T" = "Ctrl+T";           # New tab
          "Cmd+W" = "Ctrl+W";           # Close tab
          "Cmd+Shift+T" = "Ctrl+Shift+T"; # Reopen closed tab
          "Cmd+R" = "Ctrl+R";           # Reload
          "Cmd+L" = "Ctrl+L";           # Address bar
          "Cmd+D" = "Ctrl+D";           # Bookmark
        };
        
        "google-chrome" = {
          "Cmd+T" = "Ctrl+T";
          "Cmd+W" = "Ctrl+W";
          "Cmd+R" = "Ctrl+R";
          "Cmd+L" = "Ctrl+L";
          "Cmd+Shift+I" = "F12";        # Developer tools
        };
        
        # Code editors
        "code" = {
          "Cmd+P" = "Ctrl+Shift+P";     # Command palette
          "Cmd+Shift+P" = "Ctrl+P";     # Quick open
          "Cmd+/" = "Ctrl+/";           # Toggle comment
          "Cmd+D" = "Ctrl+D";           # Select word
          "Cmd+G" = "Ctrl+G";           # Go to line
          "Cmd+B" = "Ctrl+B";           # Toggle sidebar
          "Cmd+J" = "Ctrl+J";           # Toggle panel
        };
        
        # Terminal
        "gnome-terminal" = {
          "Cmd+T" = "Ctrl+Shift+T";     # New tab
          "Cmd+W" = "Ctrl+Shift+W";     # Close tab
          "Cmd+N" = "Ctrl+Shift+N";     # New window
          "Cmd+C" = "Ctrl+Shift+C";     # Copy
          "Cmd+V" = "Ctrl+Shift+V";     # Paste
        };
        
        # File manager
        "nautilus" = {
          "Cmd+N" = "Ctrl+N";           # New window
          "Cmd+Shift+N" = "Ctrl+Shift+N"; # New folder
          "Cmd+Up" = "Alt+Up";          # Parent directory
          "Cmd+H" = "Ctrl+H";           # Show hidden files
        };
      };
    };
    
    # GUI configuration
    gui = {
      enable = true;
      tray = true;
    };
    
    # Custom configuration for advanced users
    extraConfig = ''
      # Custom keybindings for development workflow
      keymap("Development", {
          # Quick terminal commands
          C("shift-t"): [
              C("ctrl-alt-t"),  # Open terminal
          ],
          
          # Screenshot shortcuts
          C("shift-3"): C("print"),           # Full screenshot
          C("shift-4"): C("shift-print"),     # Area screenshot
          C("shift-5"): C("ctrl-shift-print"), # Window screenshot
      })
      
      # Text editing enhancements
      keymap("Text Editing", {
          # Word navigation
          C("alt-left"):  C("ctrl-left"),     # Previous word
          C("alt-right"): C("ctrl-right"),    # Next word
          C("alt-shift-left"):  C("ctrl-shift-left"),   # Select word left
          C("alt-shift-right"): C("ctrl-shift-right"),  # Select word right
          
          # Line manipulation
          C("shift-up"):   C("shift-home"),   # Select to line start
          C("shift-down"): C("shift-end"),    # Select to line end
      })
      
      # Application launcher shortcuts
      keymap("System", {
          C("space"):       C("alt-f2"),      # Application launcher
          C("shift-space"): C("alt-f1"),      # Activities overview
      })
    '';
  };
  
  # Additional packages that work well with Toshy
  home.packages = with pkgs; [
    # Development tools
    vscode
    firefox
    
    # Terminal
    gnome.gnome-terminal
    
    # File manager
    gnome.nautilus
    
    # System utilities
    flameshot  # Screenshot tool
    albert     # Application launcher
  ];
  
  # Configure other Home Manager services that complement Toshy
  programs = {
    # Shell configuration
    zsh = {
      enable = true;
      enableCompletion = true;
      autosuggestion.enable = true;
      syntaxHighlighting.enable = true;
    };
    
    # Git configuration
    git = {
      enable = true;
      userName = "Your Name";
      userEmail = "your.email@example.com";
    };
    
    # VS Code configuration
    vscode = {
      enable = true;
      extensions = with pkgs.vscode-extensions; [
        ms-vscode.cpptools
        ms-python.python
        ms-vscode.vscode-typescript-next
      ];
    };
  };
  
  # Desktop environment integration
  xdg = {
    enable = true;
    
    # MIME type associations
    mimeApps = {
      enable = true;
      defaultApplications = {
        "text/html" = "firefox.desktop";
        "x-scheme-handler/http" = "firefox.desktop";
        "x-scheme-handler/https" = "firefox.desktop";
        "text/plain" = "code.desktop";
      };
    };
  };
  
  # Systemd user services
  systemd.user = {
    # Enable lingering to start services on boot
    startServices = "sd-switch";
  };
}
