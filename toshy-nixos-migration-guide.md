# Toshy NixOS Migration Guide

This guide helps users migrate from the old overlay-based Toshy installation to the new flake-based approach.

## Overview

The Toshy application has been modernized from a complex Nix overlay to a clean, maintainable Nix flake. This migration guide will help you transition to the new approach.

## Prerequisites

- NixOS with flakes enabled
- Basic understanding of NixOS configuration
- Basic understanding of Nix flakes

## Enabling Flakes

If you haven't enabled flakes yet, add the following to your NixOS configuration:

```nix
# configuration.nix
{ config, pkgs, ... }:

{
  nix = {
    settings.experimental-features = [ "nix-command" "flakes" ];
  };
}
```

## Migration Steps

### 1. Remove Old Overlay

First, remove the old overlay-based Toshy installation from your configuration:

```nix
# Old approach (remove this)
nixpkgs.overlays = [
  (import /path/to/toshy/overlay.nix)
];

environment.systemPackages = with pkgs; [
  toshy
];
```

### 2. Add Flake Input

Add the Toshy flake as an input to your NixOS flake:

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    
    # Add Toshy flake
    toshy.url = "github:celesrenata/toshy";
    toshy.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, toshy, ... }: {
    # Your outputs here
  };
}
```

### 3. Import NixOS Module

Import the Toshy NixOS module in your configuration:

```nix
# configuration.nix
{ config, pkgs, ... }:

{
  imports = [
    # Other imports...
    
    # Import Toshy module
    inputs.toshy.nixosModules.default
  ];
}
```

### 4. Configure Toshy

Configure Toshy using the new module options:

```nix
# configuration.nix
{ config, pkgs, ... }:

{
  # Enable and configure Toshy
  services.toshy = {
    enable = true;
    user = "yourusername";  # Replace with your username
    
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
    wayland.compositor = "auto";
    
    # X11 support
    x11.enable = true;
    x11.windowManager = "auto";
  };
}
```

### 5. Migrate Custom Configuration

If you had custom configuration in your old setup, migrate it to the new format:

#### Old Format (typically in ~/.config/toshy/toshy_config.py):

```python
# Old custom configuration
from xwaykeyz.models import *

keymap("Firefox", {
    C("a"): C("ctrl-a"),
    C("c"): C("ctrl-c"),
})
```

#### New Format (in NixOS configuration):

```nix
# New configuration in configuration.nix
services.toshy = {
  # Other configuration...
  
  # Custom configuration
  config = ''
    # Custom keybindings
    keymap("Firefox", {
        C("a"): C("ctrl-a"),
        C("c"): C("ctrl-c"),
    })
  '';
};
```

### 6. User-Specific Configuration with Home Manager

For user-specific configuration, you can use the Home Manager module:

```nix
# home.nix
{ config, pkgs, ... }:

{
  imports = [
    inputs.toshy.homeManagerModules.default
  ];

  services.toshy = {
    enable = true;
    
    settings = {
      macStyle = true;
      theme = "dark";
      autostart = true;
      
      applications = {
        "firefox" = {
          "Cmd+T" = "Ctrl+T";
          "Cmd+W" = "Ctrl+W";
        };
      };
    };
    
    gui = {
      enable = true;
      tray = true;
    };
    
    extraConfig = ''
      # Custom keybindings
      keymap("Custom", {
          C("shift-space"): C("alt-f2"),
      })
    '';
  };
}
```

### 7. Apply Configuration

Apply your new configuration:

```bash
# For NixOS
sudo nixos-rebuild switch

# For Home Manager
home-manager switch
```

## Troubleshooting

### Service Not Starting

If the Toshy service doesn't start after migration:

1. Check the service status:
   ```bash
   systemctl --user status toshy
   ```

2. Check the logs:
   ```bash
   journalctl --user -u toshy
   ```

3. Ensure your user is in the required groups:
   ```bash
   # Add your user to the input group
   sudo usermod -a -G input yourusername
   ```

### Configuration Issues

If your configuration doesn't work as expected:

1. Check the generated configuration file:
   ```bash
   cat ~/.config/toshy/toshy_config.py
   ```

2. Try with a minimal configuration first, then add your customizations gradually.

3. Ensure you're using the correct syntax for keybindings in the new format.

## Advanced Migration

### Custom Dependencies

If you had custom dependencies in your old setup, you can add them to the flake:

```nix
# flake.nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    toshy.url = "github:celesrenata/toshy";
    
    # Add your custom dependencies
    custom-dep.url = "github:user/repo";
    
    # Make toshy use your custom dependency
    toshy.inputs.custom-dep.follows = "custom-dep";
  };
}
```

### Multiple Users

For multiple users, configure Toshy for each user:

```nix
# configuration.nix
{
  # System-wide configuration
  services.toshy = {
    enable = true;
    user = "main-user";
    # Common configuration...
  };
  
  # Additional users can use Home Manager
  home-manager.users.user1 = { ... }: {
    imports = [ inputs.toshy.homeManagerModules.default ];
    services.toshy = {
      enable = true;
      # User-specific configuration...
    };
  };
  
  home-manager.users.user2 = { ... }: {
    imports = [ inputs.toshy.homeManagerModules.default ];
    services.toshy = {
      enable = true;
      # User-specific configuration...
    };
  };
}
```

## Conclusion

You have successfully migrated from the old overlay-based Toshy installation to the new flake-based approach. The new approach provides better integration with NixOS, more configuration options, and improved maintainability.

If you encounter any issues during migration, please open an issue on the [Toshy GitHub repository](https://github.com/celesrenata/toshy).
