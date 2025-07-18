# Example NixOS configuration using the Toshy flake
{
  description = "Example NixOS configuration with Toshy";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    toshy.url = "github:celesrenata/toshy";
    toshy.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, toshy }: {
    nixosConfigurations.example = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        # Import the Toshy NixOS module
        toshy.nixosModules.toshy
        
        # Your system configuration
        ({ config, pkgs, ... }: {
          # Enable Toshy with basic configuration
          services.toshy = {
            enable = true;
            user = "alice";  # Replace with your username
            
            # Enable GUI components
            gui = {
              enable = true;
              tray = true;
              theme = "auto";
            };
            
            # Configure keybindings
            keybindings = {
              macStyle = true;
              applications = {
                "Firefox" = {
                  "Cmd+T" = "Ctrl+T";      # New tab
                  "Cmd+W" = "Ctrl+W";      # Close tab
                  "Cmd+R" = "Ctrl+R";      # Reload
                  "Cmd+L" = "Ctrl+L";      # Address bar
                };
                "code" = {
                  "Cmd+P" = "Ctrl+Shift+P";  # Command palette
                  "Cmd+Shift+P" = "Ctrl+P";  # File search
                  "Cmd+/" = "Ctrl+/";        # Toggle comment
                };
              };
            };
            
            # Enable Wayland support if using Wayland
            wayland = {
              enable = true;
              compositor = "auto";
            };
            
            # Enable X11 support if using X11
            x11 = {
              enable = true;
              windowManager = "auto";
            };
          };
          
          # Ensure your user is created
          users.users.alice = {
            isNormalUser = true;
            extraGroups = [ "wheel" "input" ];
          };
          
          # Other system configuration...
          system.stateVersion = "24.11";
        })
      ];
    };
  };
}
