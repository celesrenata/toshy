# Toshy NixOS Flake Context

This document provides context for the NixOS flake implementation of Toshy, a Mac-style keybinding service for Linux.

## Current Implementation

The current flake.nix implementation by Q is comprehensive and follows NixOS best practices:

### 1. Flake Structure

```nix
{
  description = "Toshy - Mac-style keybindings for Linux";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachSystem [ 
      "x86_64-linux" 
      "aarch64-linux"
    ] (system: 
      # Package definitions
    ) // {
      # NixOS and Home Manager modules
      nixosModules.toshy = import ./modules/toshy.nix;
      nixosModules.default = self.nixosModules.toshy;
      
      homeManagerModules.toshy = import ./home-manager/toshy.nix;
      homeManagerModules.default = self.homeManagerModules.toshy;
      
      overlays.default = final: prev: {
        toshy = self.packages.${prev.system}.toshy;
        xwaykeyz = self.packages.${prev.system}.xwaykeyz;
      };
    };
}
```

### 2. Key Components

1. **Platform Support**:
   - Multi-architecture support (x86_64-linux, aarch64-linux)
   - Platform-specific configurations and optimizations

2. **Custom Dependencies**:
   - Custom python-xlib 0.31 package to avoid conflicts
   - Custom xwaykeyz package (main dependency not in nixpkgs)

3. **Main Package Definition**:
   - Comprehensive build inputs and dependencies
   - Test configuration
   - Proper metadata

4. **NixOS Module**:
   - Extensive configuration options
   - Systemd service definitions
   - Security and performance settings

5. **Home Manager Module**:
   - User-specific configuration
   - Systemd user services
   - Desktop entries and autostart

6. **Development Environment**:
   - Comprehensive development shell
   - Testing and debugging tools

## Integration with NixOS

### NixOS Module Usage

The NixOS module provides system-wide configuration:

```nix
# configuration.nix
{ config, pkgs, ... }:

{
  imports = [
    # Import the Toshy module
    inputs.toshy.nixosModules.default
  ];

  # Enable and configure Toshy
  services.toshy = {
    enable = true;
    user = "yourusername";
    
    # Mac-style keybindings
    keybindings.macStyle = true;
    
    # Application-specific bindings
    keybindings.applications = {
      "Firefox" = {
        "Cmd+T" = "Ctrl+T";  # New tab
        "Cmd+W" = "Ctrl+W";  # Close tab
      };
    };
    
    # GUI settings
    gui = {
      enable = true;
      tray = true;
      theme = "dark";
    };
    
    # Wayland support
    wayland.enable = true;
    wayland.compositor = "hyprland";
    
    # X11 support
    x11.enable = true;
    x11.windowManager = "i3";
  };
}
```

### Home Manager Usage

The Home Manager module provides user-specific configuration:

```nix
# home.nix
{ config, pkgs, ... }:

{
  imports = [
    # Import the Toshy Home Manager module
    inputs.toshy.homeManagerModules.default
  ];

  # Enable and configure Toshy
  services.toshy = {
    enable = true;
    
    # Settings
    settings = {
      macStyle = true;
      theme = "dark";
      autostart = true;
      
      # Application-specific bindings
      applications = {
        "firefox" = {
          "Cmd+T" = "Ctrl+T";
          "Cmd+W" = "Ctrl+W";
        };
      };
    };
    
    # GUI components
    gui = {
      enable = true;
      tray = true;
    };
    
    # Additional configuration
    extraConfig = ''
      # Custom keybindings
      keymap("Custom", {
          C("shift-space"): C("alt-f2"),
      })
    '';
  };
}
```

## Development Workflow

The flake provides a comprehensive development environment:

```bash
# Enter development shell
nix develop

# Build the package
nix build

# Run Toshy
nix run

# Check all platforms
nix flake check --all-systems
```

## Example Configurations

The repository includes example configurations for both NixOS and Home Manager:

### Basic NixOS Configuration

```nix
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
        })
      ];
    };
  };
}
```

### Home Manager Configuration

```nix
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
        "firefox" = {
          "Cmd+T" = "Ctrl+T";           # New tab
          "Cmd+W" = "Ctrl+W";           # Close tab
          "Cmd+R" = "Ctrl+R";           # Reload
        };
        
        "code" = {
          "Cmd+P" = "Ctrl+Shift+P";     # Command palette
          "Cmd+Shift+P" = "Ctrl+P";     # Quick open
          "Cmd+/" = "Ctrl+/";           # Toggle comment
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
          C("shift-t"): C("ctrl-alt-t"),  # Open terminal
          
          # Screenshot shortcuts
          C("shift-3"): C("print"),       # Full screenshot
          C("shift-4"): C("shift-print"), # Area screenshot
      })
    '';
  };
}
```

## Best Practices

1. **Dependency Management**:
   - Pin specific versions of problematic dependencies
   - Use overrideAttrs for minor package modifications
   - Use buildPythonPackage for custom Python packages

2. **Platform Support**:
   - Use flake-utils.lib.eachSystem for multi-platform support
   - Define platform-specific configurations
   - Use lib.optionals for conditional dependencies

3. **Module Design**:
   - Provide comprehensive configuration options
   - Use mkOption with proper types and descriptions
   - Include assertions for configuration validation
   - Generate configuration files from user settings

4. **Security**:
   - Configure systemd services with appropriate security settings
   - Manage permissions and access control
   - Handle user-specific configuration safely

5. **Testing**:
   - Include test dependencies and configuration
   - Enable tests with doCheck
   - Provide test commands in development shell

## Testing

The repository includes comprehensive tests for the NixOS module and integration:

### NixOS Module Tests

```python
class TestNixOSModuleStructure:
    """Test NixOS module structure and options"""
    
    def test_module_file_structure(self):
        """Test that the NixOS module has proper structure"""
        module_path = Path(__file__).parent.parent / "modules" / "toshy.nix"
        assert module_path.exists()
        
        content = module_path.read_text()
        
        # Check for essential module components
        assert "options.services.toshy" in content
        assert "config = mkIf cfg.enable" in content
        assert "systemd.user.services.toshy" in content
        
        # Check for advanced options
        assert "logging" in content
        assert "security" in content
        assert "performance" in content
        assert "assertions" in content
```

### Integration Tests

```python
class TestNixOSIntegration:
    """Test NixOS module integration functionality"""
    
    def test_config_generator_basic(self):
        """Test basic configuration generation"""
        generator = ToshyConfigGenerator()
        
        options = {
            'keybindings': {
                'macStyle': True,
                'applications': {
                    'Firefox': {
                        'Cmd+T': 'Ctrl+T',
                        'Cmd+W': 'Ctrl+W'
                    }
                }
            },
            'logging': {
                'level': 'INFO'
            }
        }
        
        config = generator.generate_config(options)
        
        # Check that config contains expected elements
        assert 'MAC_STYLE_ENABLED = True' in config
        assert 'Firefox' in config
        assert 'LOG_LEVEL = \'INFO\'' in config
        assert 'TOSHY_CONFIG_VERSION' in config
```

## Future Improvements

1. **Documentation**:
   - Add more comprehensive documentation
   - Include examples for different desktop environments
   - Create a dedicated website with usage guides

2. **Testing**:
   - Expand test coverage
   - Add integration tests for more desktop environments
   - Add performance tests

3. **CI Integration**:
   - Add GitHub Actions workflow
   - Automate testing and building
   - Set up automatic releases

4. **Package Optimization**:
   - Optimize build process
   - Reduce dependencies where possible
   - Improve startup time

5. **Module Enhancements**:
   - Add more configuration options
   - Improve integration with different desktop environments
   - Add support for more window managers and compositors
