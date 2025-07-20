{
  description = "NixOS configuration with Toshy Phase 4 implementation";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    
    # Toshy flake targeting the cline branch for Phase 4 implementation
    toshy = {
      url = "github:celesrenata/toshy/cline";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    
    # Home Manager for user-level configuration
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, toshy, home-manager, ... }:
    let
      system = "x86_64-linux";  # Adjust if using a different architecture
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      # NixOS configuration
      nixosConfigurations.default = nixpkgs.lib.nixosSystem {
        inherit system;
        modules = [
          # Import the Toshy NixOS module
          toshy.nixosModules.default
          
          # Basic system configuration
          {
            system.stateVersion = "23.11";  # Adjust to your NixOS version
            
            # Enable Toshy with Phase 4 frontend testing implementation
            services.toshy = {
              enable = true;
              
              # Only toshy-tray should have a service, not toshy-gui (Phase 3)
              gui = {
                enable = true;
                tray = true;
              };
              
              # Basic configuration
              settings = {
                theme = "dark";
                autostart = true;
              };
            };
            
            # Enable flakes
            nix = {
              settings = {
                experimental-features = [ "nix-command" "flakes" ];
                trusted-users = [ "root" "@wheel" ];
              };
            };
          }
        ];
      };
      
      # Home Manager configuration
      homeConfigurations.default = home-manager.lib.homeManagerConfiguration {
        inherit pkgs;
        modules = [
          # Import the Toshy Home Manager module
          toshy.homeManagerModules.default
          
          # User-specific configuration
          {
            home.stateVersion = "23.11";  # Adjust to your Home Manager version
            
            # Enable Toshy with user-specific settings
            services.toshy = {
              enable = true;
              
              # GUI settings
              gui = {
                enable = true;
                tray = true;
              };
              
              # User-specific settings
              settings = {
                theme = "dark";
                autostart = true;
                
                # Example application-specific keybindings
                applications = {
                  "firefox" = {
                    "Cmd+T" = "Ctrl+T";  # New tab
                    "Cmd+W" = "Ctrl+W";  # Close tab
                  };
                };
              };
            };
          }
        ];
      };
      
      # Development shell for working on Toshy
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          # Development tools
          git
          nixpkgs-fmt
          
          # Python development
          python3
          python3Packages.pip
          python3Packages.setuptools
          python3Packages.wheel
          
          # Testing tools for Phase 4
          python3Packages.pytest
          python3Packages.pytest-cov
          python3Packages.pytest-mock
          python3Packages.pytest-xvfb  # For headless GUI testing
          
          # GTK development
          gtk4
          gobject-introspection
          libadwaita
          
          # For running tests in CI
          xvfb-run
        ];
        
        shellHook = ''
          echo "Toshy Phase 4 development environment"
          echo "Python: $(python3 --version)"
          echo ""
          echo "Available commands:"
          echo "  - nix build: Build the package"
          echo "  - nix run: Run the application"
          echo "  - pytest: Run tests"
          echo ""
          echo "Frontend Testing (Phase 4):"
          echo "  - pytest tests/test_gui_components.py: Test UI components"
          echo "  - pytest tests/test_gui_buttons.py: Test button functionality"
          echo "  - pytest tests/test_gui_forms.py: Test form input and validation"
          echo "  - xvfb-run pytest tests/: Run tests in headless environment"
        '';
      };
    };
}
