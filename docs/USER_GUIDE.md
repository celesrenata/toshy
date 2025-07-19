# Toshy User Guide

Welcome to Toshy! This guide will help you get started with Mac-style keybindings on Linux using the modern Nix flake implementation.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Troubleshooting](#troubleshooting)
5. [Advanced Usage](#advanced-usage)
6. [Platform Support](#platform-support)

## Quick Start

### Prerequisites

- NixOS or Nix package manager
- Linux system with X11 or Wayland
- Input device access (user in `input` group)

### Basic Installation

Add Toshy to your NixOS configuration:

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    toshy.url = "github:celesrenata/toshy";
    toshy.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, toshy }: {
    nixosConfigurations.mySystem = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        toshy.nixosModules.toshy
        {
          services.toshy = {
            enable = true;
            user = "your-username";
          };
        }
      ];
    };
  };
}
```

### Home Manager Installation

For user-level installation:

```nix
{
  imports = [ inputs.toshy.homeManagerModules.toshy ];
  
  services.toshy = {
    enable = true;
    settings.macStyle = true;
    gui.enable = true;
  };
}
```

## Installation

### System Requirements

- **Operating System**: Linux (NixOS recommended)
- **Architecture**: x86_64-linux, aarch64-linux
- **Display Server**: X11 or Wayland
- **Memory**: 128MB+ available RAM
- **Python**: 3.8+ (automatically provided)

### Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| x86_64-linux | ✅ Full Support | All features available |
| aarch64-linux | ✅ Full Support | Optimized for ARM64 |
| NixOS | ✅ Recommended | Best integration |
| Other Linux | ✅ Via Nix | Requires Nix package manager |

### Supported Desktop Environments

| Environment | X11 | Wayland | Notes |
|-------------|-----|---------|-------|
| GNOME | ✅ | ✅ | Full support |
| KDE Plasma | ✅ | ✅ | Full support |
| Hyprland | N/A | ✅ | Excellent support |
| Sway | N/A | ✅ | Excellent support |
| i3/i3-gaps | ✅ | N/A | Good support |
| XFCE | ✅ | Limited | Basic support |
| Others | ✅ | ✅ | May require configuration |

## Configuration

### Basic Configuration

Enable Toshy with default Mac-style keybindings:

```nix
services.toshy = {
  enable = true;
  user = "alice";
  keybindings.macStyle = true;
};
```

### Application-Specific Keybindings

Configure keybindings for specific applications:

```nix
services.toshy = {
  enable = true;
  user = "alice";
  
  keybindings = {
    macStyle = true;
    applications = {
      "Firefox" = {
        "Cmd+T" = "Ctrl+T";           # New tab
        "Cmd+W" = "Ctrl+W";           # Close tab
        "Cmd+Shift+T" = "Ctrl+Shift+T"; # Reopen closed tab
        "Cmd+L" = "Ctrl+L";           # Address bar
        "Cmd+R" = "Ctrl+R";           # Reload
      };
      
      "code" = {
        "Cmd+P" = "Ctrl+Shift+P";     # Command palette
        "Cmd+Shift+P" = "Ctrl+P";     # Quick open
        "Cmd+/" = "Ctrl+/";           # Toggle comment
        "Cmd+D" = "Ctrl+D";           # Select word
      };
      
      "gnome-terminal" = {
        "Cmd+T" = "Ctrl+Shift+T";     # New tab
        "Cmd+W" = "Ctrl+Shift+W";     # Close tab
        "Cmd+C" = "Ctrl+Shift+C";     # Copy
        "Cmd+V" = "Ctrl+Shift+V";     # Paste
      };
    };
  };
};
```

### Global System Shortcuts

Configure system-wide shortcuts:

```nix
services.toshy = {
  keybindings = {
    globalShortcuts = {
      "Cmd+Space" = "Alt+F2";         # Application launcher
      "Cmd+Tab" = "Alt+Tab";          # Application switcher
      "Cmd+Q" = "Alt+F4";             # Quit application
      "Cmd+M" = "Alt+F9";             # Minimize window
    };
  };
};
```

### GUI Configuration

Enable and configure GUI components:

```nix
services.toshy = {
  gui = {
    enable = true;
    tray = true;                      # System tray icon
    theme = "auto";                   # "light", "dark", or "auto"
    autostart = true;                 # Start with desktop session
  };
};
```

### Advanced Configuration

#### Custom Python Configuration

Add custom keybinding logic:

```nix
services.toshy = {
  config = ''
    # Custom keybindings
    keymap("Development Tools", {
        # Git shortcuts in terminal
        C("g"): [C("g"), C("i"), C("t"), C("space")],  # "git "
        
        # Docker shortcuts
        C("shift-d"): [C("d"), C("o"), C("c"), C("k"), C("e"), C("r"), C("space")],  # "docker "
    })
    
    # Conditional keymaps
    keymap("Work Hours", {
        C("shift-m"): C("ctrl-alt-m"),     # Mute microphone
        C("shift-v"): C("ctrl-alt-v"),     # Toggle video
    }, when=lambda ctx: 9 <= datetime.datetime.now().hour <= 17)
  '';
};
```

#### Performance Tuning

Optimize performance for your system:

```nix
services.toshy = {
  performance = {
    priority = -5;                    # Higher priority (-20 to 19)
    memoryLimit = "256M";             # Memory limit
    cpuQuota = "50%";                 # CPU usage limit
  };
};
```

#### Security Configuration

Configure security settings:

```nix
services.toshy = {
  security = {
    enableInputGroup = true;          # Add user to input group
    restrictedMode = false;           # Enable full functionality
    allowedUsers = ["alice" "bob"];   # Additional allowed users
  };
};
```

#### Logging Configuration

Configure logging:

```nix
services.toshy = {
  logging = {
    level = "INFO";                   # DEBUG, INFO, WARNING, ERROR
    file = "/var/log/toshy.log";      # Optional log file
  };
};
```

## Troubleshooting

### Diagnostic Tools

Toshy includes comprehensive diagnostic tools:

```bash
# Check system status
toshy-debug

# Check platform information
toshy-platform

# Monitor performance
toshy-performance --benchmark 60

# Validate configuration
toshy-config --validate
```

### Common Issues

#### 1. Keybindings Not Working

**Symptoms**: Key combinations don't trigger expected actions

**Solutions**:
1. Check if Toshy daemon is running:
   ```bash
   systemctl --user status toshy
   ```

2. Verify user permissions:
   ```bash
   groups $USER  # Should include 'input'
   ```

3. Check configuration:
   ```bash
   toshy-config --info
   ```

4. Run diagnostics:
   ```bash
   toshy-debug
   ```

#### 2. Service Won't Start

**Symptoms**: Toshy service fails to start

**Solutions**:
1. Check system requirements:
   ```bash
   toshy-debug
   ```

2. Verify xwaykeyz installation:
   ```bash
   which xwaykeyz
   xwaykeyz --version
   ```

3. Check logs:
   ```bash
   journalctl --user -u toshy -f
   ```

#### 3. High CPU/Memory Usage

**Symptoms**: System slowdown, high resource usage

**Solutions**:
1. Monitor performance:
   ```bash
   toshy-performance --benchmark 30
   ```

2. Adjust performance settings:
   ```nix
   services.toshy.performance = {
     priority = 5;           # Lower priority
     memoryLimit = "128M";   # Reduce memory limit
     cpuQuota = "25%";       # Limit CPU usage
   };
   ```

3. Enable restricted mode:
   ```nix
   services.toshy.security.restrictedMode = true;
   ```

#### 4. GUI Components Not Appearing

**Symptoms**: Tray icon or GUI missing

**Solutions**:
1. Check GUI service:
   ```bash
   systemctl --user status toshy-gui
   systemctl --user status toshy-tray
   ```

2. Verify desktop environment support:
   ```bash
   toshy-platform
   ```

3. Check autostart configuration:
   ```nix
   services.toshy.gui.autostart = true;
   ```

### Platform-Specific Issues

#### ARM64 Systems

- Use conservative performance settings
- Some compositors may have limited support
- Enable compatibility mode if needed

#### Wayland Systems

- Ensure compositor support is enabled
- Some features may require specific protocols
- Check compositor-specific configuration

#### X11 Systems

- Verify X server permissions
- Check window manager compatibility
- Ensure proper display environment

## Advanced Usage

### Custom Keybinding Development

Create complex keybinding scenarios:

```python
# Time-based keymaps
import datetime

current_hour = datetime.datetime.now().hour

if 9 <= current_hour <= 17:  # Work hours
    keymap("Work Mode", {
        C("shift-m"): C("ctrl-alt-m"),     # Mute
        C("shift-v"): C("ctrl-alt-v"),     # Video toggle
    })
else:  # Personal time
    keymap("Personal Mode", {
        C("shift-g"): C("ctrl-shift-g"),   # Gaming mode
    })
```

### Integration with Other Tools

#### Window Manager Integration

```nix
# i3 integration
services.toshy.x11 = {
  enable = true;
  windowManager = "i3";
};

# Hyprland integration
services.toshy.wayland = {
  enable = true;
  compositor = "hyprland";
};
```

#### Development Environment Setup

```nix
# Development-focused configuration
services.toshy = {
  keybindings.applications = {
    "code" = {
      # VS Code shortcuts
      "Cmd+P" = "Ctrl+Shift+P";
      "Cmd+Shift+P" = "Ctrl+P";
      "Cmd+/" = "Ctrl+/";
    };
    
    "gnome-terminal" = {
      # Terminal shortcuts
      "Cmd+T" = "Ctrl+Shift+T";
      "Cmd+W" = "Ctrl+Shift+W";
    };
    
    "firefox" = {
      # Browser shortcuts for development
      "Cmd+Shift+I" = "F12";          # Developer tools
      "Cmd+Shift+C" = "Ctrl+Shift+C"; # Element inspector
    };
  };
};
```

### Performance Optimization

#### System Tuning

```nix
services.toshy = {
  performance = {
    priority = -10;        # High priority for responsiveness
    memoryLimit = "512M";  # Generous memory for complex configs
    cpuQuota = "75%";      # Allow high CPU for processing
  };
  
  # Optimize for your platform
  wayland.protocols = [
    "wlr-layer-shell"
    "xdg-shell" 
    "wlr-foreign-toplevel"
  ];
};
```

#### Configuration Optimization

- Use specific application matches instead of wildcards
- Minimize complex conditional logic
- Cache frequently used keybinding patterns
- Profile configuration loading time

### Monitoring and Maintenance

#### Regular Health Checks

```bash
# Weekly system check
toshy-debug --json --output weekly-check.json

# Performance monitoring
toshy-performance --benchmark 300 --output perf-report.json

# Configuration validation
toshy-config --validate
```

#### Log Management

```nix
services.toshy.logging = {
  level = "INFO";
  file = "/var/log/toshy.log";
};

# Automatic log rotation is configured
```

## Platform Support

### Architecture Support

| Architecture | Status | Performance | Notes |
|--------------|--------|-------------|-------|
| x86_64 | ✅ Excellent | High | Full optimization |
| aarch64 | ✅ Excellent | Good | ARM64 optimized |
| armv7 | ⚠️ Limited | Fair | Basic support |
| armv6 | ⚠️ Limited | Fair | Minimal features |

### Cross-Compilation

Build for different architectures:

```bash
# Build for ARM64
nix build .#packages.aarch64-linux.toshy

# Check all platforms
nix flake check --all-systems
```

### Platform-Specific Optimizations

The system automatically detects your platform and applies appropriate optimizations:

- **x86_64**: Full feature set with performance optimizations
- **aarch64**: Balanced performance and power efficiency
- **ARM**: Conservative settings for stability

Check your platform configuration:

```bash
toshy-platform
```

## Getting Help

### Community Resources

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Comprehensive guides and examples
- **Examples**: Real-world configuration examples

### Diagnostic Information

When reporting issues, include:

```bash
# Generate diagnostic report
toshy-debug --json --output diagnostic-report.json

# Platform information
toshy-platform

# Performance data (if relevant)
toshy-performance --benchmark 60 --json --output performance-data.json
```

### Contributing

Toshy is open source and welcomes contributions:

1. **Bug Reports**: Use the diagnostic tools to gather information
2. **Feature Requests**: Describe your use case and requirements
3. **Code Contributions**: Follow the development guide
4. **Documentation**: Help improve guides and examples

---

*This guide covers the essential aspects of using Toshy. For more advanced topics, see the [Developer Guide](DEVELOPER_GUIDE.md) and [API Reference](API_REFERENCE.md).*
