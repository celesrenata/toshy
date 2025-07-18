# Migration Guide: From Overlay to Flake

## Current State vs Target State

### Current (Overlay-based)
```nix
# In configuration.nix
nixpkgs.overlays = [ (import ./overlays/toshy.nix) ];
environment.systemPackages = [ pkgs.toshy ];
```

### Target (Flake-based)
```nix
# In flake.nix
inputs.toshy.url = "github:celesrenata/toshy";

# In configuration.nix
imports = [ inputs.toshy.nixosModules.toshy ];
services.toshy.enable = true;
```

## Migration Steps

### Step 1: Remove Old Overlay
1. Remove `toshy.nix` from overlays
2. Remove overlay reference from configuration
3. Remove manual package installation

### Step 2: Add Flake Input
```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    toshy.url = "github:celesrenata/toshy";
    toshy.inputs.nixpkgs.follows = "nixpkgs";
  };
}
```

### Step 3: Import Module
```nix
# In your NixOS configuration
imports = [
  inputs.toshy.nixosModules.toshy
];
```

### Step 4: Configure Service
```nix
services.toshy = {
  enable = true;
  user = "your-username";
  gui.enable = true;
  gui.tray = true;
};
```

## Configuration Migration

### Old Manual Configuration
Previously, configuration required manual file editing and service management.

### New Declarative Configuration
```nix
services.toshy = {
  enable = true;
  user = "alice";
  
  config = ''
    # Custom keybindings
    keymap("Firefox", {
        C("t"): C("shift-t"),
        C("w"): C("shift-w"),
    })
  '';
  
  keybindings = {
    macStyle = true;
    applications = {
      "code" = {
        "Cmd+P" = "Ctrl+Shift+P";
      };
    };
  };
};
```

## Benefits of Migration

### 1. Simplified Management
- No manual overlay maintenance
- Automatic dependency resolution
- Integrated system configuration

### 2. Better Integration
- NixOS service management
- Proper systemd integration
- Security and permissions handled

### 3. Easier Updates
- Flake lock file for reproducibility
- Simple update commands
- Version management

### 4. Development Experience
- Development shell included
- Testing infrastructure
- Documentation and examples

## Troubleshooting Migration

### Common Issues

#### 1. Service Not Starting
```bash
# Check service status
systemctl --user status toshy

# Check logs
journalctl --user -u toshy -f
```

#### 2. Permission Issues
Ensure user is in input group:
```nix
users.users.your-username.extraGroups = [ "input" ];
```

#### 3. Configuration Errors
Validate configuration:
```bash
toshy-config --validate
```

#### 4. GUI Not Appearing
Check GUI service:
```bash
systemctl --user status toshy-gui
```

### Migration Checklist

- [ ] Remove old overlay references
- [ ] Add flake input
- [ ] Import NixOS module
- [ ] Configure service options
- [ ] Test basic functionality
- [ ] Migrate custom configuration
- [ ] Verify GUI components
- [ ] Test keybinding functionality
- [ ] Update system configuration
- [ ] Document custom settings

## Rollback Plan

If migration fails, you can rollback:

1. Re-add overlay to configuration
2. Disable new flake-based service
3. Restore manual configuration
4. Rebuild system

```nix
# Temporary rollback
services.toshy.enable = false;
nixpkgs.overlays = [ (import ./overlays/toshy.nix) ];
environment.systemPackages = [ pkgs.toshy ];
```

## Support and Resources

### Getting Help
- Check documentation in the flake
- Review example configurations
- File issues on GitHub repository
- Join community discussions

### Useful Commands
```bash
# Update flake
nix flake update

# Check flake info
nix flake show github:celesrenata/toshy

# Test configuration
nixos-rebuild test

# Apply configuration
nixos-rebuild switch
```
