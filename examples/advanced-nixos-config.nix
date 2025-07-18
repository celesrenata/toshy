# Advanced NixOS configuration showcasing all Toshy features
{
  description = "Advanced NixOS configuration with comprehensive Toshy setup";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    toshy.url = "github:celesrenata/toshy";
    toshy.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, toshy }: {
    nixosConfigurations.advanced-toshy = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        # Import the Toshy NixOS module
        toshy.nixosModules.toshy
        
        ({ config, pkgs, ... }: {
          # Comprehensive Toshy configuration
          services.toshy = {
            enable = true;
            user = "developer";
            
            # GUI configuration
            gui = {
              enable = true;
              tray = true;
              theme = "dark";
              autostart = true;
            };
            
            # Advanced keybinding configuration
            keybindings = {
              macStyle = true;
              
              # Application-specific keybindings
              applications = {
                # Web browsers
                "Firefox" = {
                  "Cmd+T" = "Ctrl+T";           # New tab
                  "Cmd+Shift+T" = "Ctrl+Shift+T"; # Reopen closed tab
                  "Cmd+W" = "Ctrl+W";           # Close tab
                  "Cmd+Shift+W" = "Ctrl+Shift+W"; # Close window
                  "Cmd+R" = "Ctrl+R";           # Reload
                  "Cmd+Shift+R" = "Ctrl+F5";    # Hard reload
                  "Cmd+L" = "Ctrl+L";           # Address bar
                  "Cmd+D" = "Ctrl+D";           # Bookmark
                  "Cmd+Shift+Delete" = "Ctrl+Shift+Delete"; # Clear data
                };
                
                "Google Chrome" = {
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
                  "Cmd+Shift+/" = "Ctrl+Shift+/"; # Block comment
                  "Cmd+D" = "Ctrl+D";           # Select word
                  "Cmd+Shift+D" = "Ctrl+Shift+L"; # Select all occurrences
                  "Cmd+G" = "Ctrl+G";           # Go to line
                  "Cmd+Shift+G" = "Ctrl+Shift+G"; # Go to symbol
                  "Cmd+B" = "Ctrl+B";           # Toggle sidebar
                  "Cmd+J" = "Ctrl+J";           # Toggle panel
                  "Cmd+Shift+E" = "Ctrl+Shift+E"; # Explorer
                  "Cmd+Shift+F" = "Ctrl+Shift+F"; # Search
                  "Cmd+Shift+X" = "Ctrl+Shift+X"; # Extensions
                };
                
                "vim" = {
                  # Vim uses different key handling, minimal remapping
                  "Cmd+S" = "Escape : w Enter"; # Save (basic example)
                };
                
                # Terminal applications
                "gnome-terminal" = {
                  "Cmd+T" = "Ctrl+Shift+T";     # New tab
                  "Cmd+W" = "Ctrl+Shift+W";     # Close tab
                  "Cmd+N" = "Ctrl+Shift+N";     # New window
                  "Cmd+C" = "Ctrl+Shift+C";     # Copy
                  "Cmd+V" = "Ctrl+Shift+V";     # Paste
                  "Cmd+Plus" = "Ctrl+Plus";     # Zoom in
                  "Cmd+Minus" = "Ctrl+Minus";   # Zoom out
                  "Cmd+0" = "Ctrl+0";           # Reset zoom
                };
                
                "konsole" = {
                  "Cmd+T" = "Ctrl+Shift+T";
                  "Cmd+W" = "Ctrl+Shift+W";
                  "Cmd+C" = "Ctrl+Shift+C";
                  "Cmd+V" = "Ctrl+Shift+V";
                };
                
                # File managers
                "nautilus" = {
                  "Cmd+N" = "Ctrl+N";           # New window
                  "Cmd+Shift+N" = "Ctrl+Shift+N"; # New folder
                  "Cmd+O" = "Ctrl+O";           # Open
                  "Cmd+Up" = "Alt+Up";          # Parent directory
                  "Cmd+Down" = "Alt+Down";      # Enter directory
                  "Cmd+1" = "Ctrl+1";           # Icon view
                  "Cmd+2" = "Ctrl+2";           # List view
                  "Cmd+H" = "Ctrl+H";           # Show hidden
                };
                
                # Office applications
                "libreoffice" = {
                  "Cmd+N" = "Ctrl+N";           # New document
                  "Cmd+O" = "Ctrl+O";           # Open
                  "Cmd+S" = "Ctrl+S";           # Save
                  "Cmd+Shift+S" = "Ctrl+Shift+S"; # Save as
                  "Cmd+P" = "Ctrl+P";           # Print
                  "Cmd+B" = "Ctrl+B";           # Bold
                  "Cmd+I" = "Ctrl+I";           # Italic
                  "Cmd+U" = "Ctrl+U";           # Underline
                };
              };
              
              # Global system shortcuts
              globalShortcuts = {
                "Cmd+Space" = "Alt+F2";         # Application launcher
                "Cmd+Tab" = "Alt+Tab";          # Application switcher
                "Cmd+Shift+Tab" = "Alt+Shift+Tab"; # Reverse app switcher
                "Cmd+Q" = "Alt+F4";             # Quit application
                "Cmd+M" = "Alt+F9";             # Minimize window
                "Cmd+Shift+M" = "Alt+F10";      # Maximize window
                "Cmd+H" = "Alt+F6";             # Hide window
                "Cmd+Shift+H" = "Alt+Shift+F6"; # Hide others
              };
            };
            
            # Display system configuration
            wayland = {
              enable = true;
              compositor = "auto";
              protocols = ["wlr-layer-shell" "xdg-shell" "wlr-foreign-toplevel"];
            };
            
            x11 = {
              enable = true;
              windowManager = "auto";
              displayManager = "auto";
            };
            
            # Logging configuration
            logging = {
              level = "INFO";
              file = "/var/log/toshy.log";
            };
            
            # Security configuration
            security = {
              enableInputGroup = true;
              restrictedMode = false;
              allowedUsers = ["developer" "admin"];
            };
            
            # Performance tuning
            performance = {
              priority = -5;              # Higher priority for responsiveness
              memoryLimit = "512M";       # Generous memory limit
              cpuQuota = "75%";          # Allow up to 75% CPU usage
            };
            
            # Custom configuration for advanced users
            config = ''
              # Custom Toshy configuration
              
              # Define custom keymaps for specific applications
              keymap("IntelliJ IDEA", {
                  C("shift-f"):   C("ctrl-shift-f"),    # Find in files
                  C("shift-r"):   C("ctrl-shift-r"),    # Replace in files
                  C("shift-a"):   C("ctrl-shift-a"),    # Find action
                  C("shift-o"):   C("ctrl-shift-n"),    # Find class
                  C("e"):         C("ctrl-e"),          # Recent files
                  C("r"):         C("ctrl-r"),          # Run
                  C("shift-r"):   C("ctrl-shift-f10"),  # Run context
                  C("d"):         C("ctrl-d"),          # Debug
                  C("shift-d"):   C("ctrl-shift-f9"),   # Debug context
              })
              
              # Custom keymap for development tools
              keymap("Development Tools", {
                  # Git shortcuts (for terminal)
                  C("g"): [
                      C("g"), C("i"), C("t"), C("space"),  # "git "
                  ],
                  
                  # Docker shortcuts
                  C("shift-d"): [
                      C("d"), C("o"), C("c"), C("k"), C("e"), C("r"), C("space"),  # "docker "
                  ],
              })
              
              # Conditional keymaps based on window title
              keymap("Terminal - Development", {
                  # Only active when terminal title contains "dev"
                  C("b"):         [C("n"), C("p"), C("m"), C("space")],  # "npm "
                  C("y"):         [C("y"), C("a"), C("r"), C("n"), C("space")],  # "yarn "
              }, when=lambda ctx: "dev" in ctx.wm_name.lower())
              
              # Time-based keymaps (example: different shortcuts during work hours)
              import datetime
              current_hour = datetime.datetime.now().hour
              
              if 9 <= current_hour <= 17:  # Work hours
                  keymap("Work Hours", {
                      C("shift-m"):   C("ctrl-alt-m"),     # Mute microphone
                      C("shift-v"):   C("ctrl-alt-v"),     # Toggle video
                      C("shift-s"):   C("ctrl-alt-s"),     # Share screen
                  })
              
              # Advanced text manipulation
              keymap("Text Editing Advanced", {
                  # Word manipulation
                  C("alt-backspace"):     C("ctrl-backspace"),    # Delete word backward
                  C("alt-delete"):        C("ctrl-delete"),       # Delete word forward
                  C("alt-shift-left"):    C("ctrl-shift-left"),   # Select word left
                  C("alt-shift-right"):   C("ctrl-shift-right"),  # Select word right
                  
                  # Line manipulation
                  C("shift-up"):          C("shift-home"),        # Select to line start
                  C("shift-down"):        C("shift-end"),         # Select to line end
                  C("alt-up"):            C("ctrl-up"),           # Move line up
                  C("alt-down"):          C("ctrl-down"),         # Move line down
              })
            '';
          };
          
          # System user configuration
          users.users.developer = {
            isNormalUser = true;
            description = "Developer User";
            extraGroups = [ "wheel" "input" "audio" "video" ];
            shell = pkgs.zsh;
          };
          
          users.users.admin = {
            isNormalUser = true;
            description = "Admin User";
            extraGroups = [ "wheel" "input" ];
          };
          
          # Enable required system services
          services.xserver = {
            enable = true;
            displayManager.gdm.enable = true;
            desktopManager.gnome.enable = true;
          };
          
          # Wayland support
          programs.hyprland.enable = true;
          programs.sway.enable = true;
          
          # Additional packages for development
          environment.systemPackages = with pkgs; [
            # Development tools
            vscode
            firefox
            google-chrome
            
            # Terminal tools
            gnome.gnome-terminal
            konsole
            
            # File managers
            gnome.nautilus
            
            # Office suite
            libreoffice
            
            # Development utilities
            git
            docker
            nodejs
            yarn
            
            # System utilities
            htop
            neofetch
            tree
          ];
          
          # Enable Docker for development
          virtualisation.docker.enable = true;
          users.users.developer.extraGroups = [ "docker" ];
          
          # Enable sound
          sound.enable = true;
          hardware.pulseaudio.enable = true;
          
          # Enable networking
          networking.networkmanager.enable = true;
          
          # System configuration
          system.stateVersion = "24.11";
          
          # Boot configuration
          boot.loader.systemd-boot.enable = true;
          boot.loader.efi.canTouchEfiVariables = true;
          
          # Timezone and locale
          time.timeZone = "America/New_York";
          i18n.defaultLocale = "en_US.UTF-8";
          
          # Enable zsh system-wide
          programs.zsh.enable = true;
          
          # Firewall configuration
          networking.firewall = {
            enable = true;
            allowedTCPPorts = [ 22 80 443 ];
          };
        })
      ];
    };
  };
}
