# NixOS Flake Best Practices

This document outlines best practices for creating NixOS flakes, based on the Toshy implementation and general Nix community standards.

## Flake Structure

### Basic Structure

```nix
{
  description = "Your project description";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    # Other inputs...
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachSystem [ "x86_64-linux" "aarch64-linux" ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        # Other variables...
      in {
        # Packages
        packages = {
          default = /* Your default package */;
          # Other packages...
        };

        # Development shell
        devShells.default = /* Your development shell */;

        # Formatter
        formatter = pkgs.nixpkgs-fmt;
      }
    ) // {
      # NixOS module
      nixosModules.default = /* Your NixOS module */;
      
      # Home Manager module
      homeManagerModules.default = /* Your Home Manager module */;
      
      # Overlay
      overlays.default = /* Your overlay */;
    };
}
```

### Multi-platform Support

Use `flake-utils.lib.eachSystem` to support multiple platforms:

```nix
flake-utils.lib.eachSystem [
  "x86_64-linux"
  "aarch64-linux"
  "x86_64-darwin"
  "aarch64-darwin"
] (system: /* ... */)
```

### Platform-specific Configuration

Define platform-specific configurations:

```nix
platformConfig = {
  x86_64-linux = {
    # x86_64-specific configuration
  };
  aarch64-linux = {
    # ARM-specific configuration
  };
};

currentPlatform = platformConfig.${system} or platformConfig.x86_64-linux;
```

## Dependency Management

### Pinning Dependencies

Pin specific versions of dependencies:

```nix
# Custom python-xlib 0.31 to avoid conflicts
pythonXlib031 = python.pkgs.xlib.overrideAttrs (oldAttrs: rec {
  version = "0.31";
  src = pkgs.fetchPypi {
    pname = "python-xlib";
    version = "0.31";
    hash = "sha256-dNg6CB9TK8B/bXr81kFuw4QD1o9oubncnh8o+/LXmek=";
  };
});
```

### Custom Packages

Define custom packages when not available in nixpkgs:

```nix
# Custom package
customPackage = pkgs.stdenv.mkDerivation {
  pname = "custom-package";
  version = "1.0.0";
  
  src = /* ... */;
  
  buildInputs = [ /* ... */ ];
  
  # ...
};
```

### Python Packages

Use `buildPythonPackage` or `buildPythonApplication` for Python packages:

```nix
# Python package
pythonPackage = python.pkgs.buildPythonPackage rec {
  pname = "package-name";
  version = "1.0.0";
  format = "pyproject";

  src = /* ... */;

  nativeBuildInputs = [ /* ... */ ];
  buildInputs = [ /* ... */ ];
  propagatedBuildInputs = [ /* ... */ ];
  
  # ...
};
```

### Conditional Dependencies

Use `lib.optionals` for conditional dependencies:

```nix
buildInputs = with pkgs; [
  # Common dependencies
  gtk3
  gobject-introspection
] ++ lib.optionals (system == "x86_64-linux") [
  # x86_64-specific dependencies
  gdb
  valgrind
];
```

## Package Definition

### Basic Package

```nix
packages.default = pkgs.stdenv.mkDerivation {
  pname = "your-package";
  version = "1.0.0";
  
  src = self;
  
  buildInputs = [ /* ... */ ];
  
  installPhase = ''
    mkdir -p $out/bin
    cp -r . $out/share/your-package
    makeWrapper $out/share/your-package/main.sh $out/bin/your-package
  '';
  
  meta = with pkgs.lib; {
    description = "Your package description";
    homepage = "https://github.com/user/repo";
    license = licenses.mit;
    platforms = platforms.linux;
    mainProgram = "your-package";
  };
};
```

### Python Application

```nix
packages.default = python.pkgs.buildPythonApplication rec {
  pname = "your-app";
  version = "1.0.0";
  format = "pyproject";

  src = self;

  nativeBuildInputs = with pkgs; [
    wrapGAppsHook
    gobject-introspection
  ];

  buildInputs = with pkgs; [
    gtk3
  ];

  propagatedBuildInputs = with python.pkgs; [
    # Python dependencies
    pygobject3
    dbus-python
  ];

  # ...
};
```

## NixOS Module

### Basic Module Structure

```nix
# modules/your-module.nix
{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.your-service;
in {
  options.services.your-service = {
    enable = mkEnableOption "Your service";
    
    package = mkPackageOption pkgs "your-package" { };
    
    # Other options...
  };

  config = mkIf cfg.enable {
    # Configuration when enabled
    environment.systemPackages = [ cfg.package ];
    
    # Systemd services
    systemd.services.your-service = {
      description = "Your Service";
      wantedBy = [ "multi-user.target" ];
      after = [ "network.target" ];
      
      serviceConfig = {
        ExecStart = "${cfg.package}/bin/your-service";
        Restart = "on-failure";
      };
    };
    
    # Other configuration...
  };
}
```

### Configuration Options

Define comprehensive configuration options:

```nix
options.services.your-service = {
  enable = mkEnableOption "Your service";
  
  package = mkPackageOption pkgs "your-package" { };
  
  user = mkOption {
    type = types.str;
    description = "User to run the service as";
    example = "alice";
  };
  
  config = mkOption {
    type = types.lines;
    default = "";
    description = "Custom configuration";
    example = ''
      # Custom configuration
      setting = value
    '';
  };
  
  # Nested options
  advanced = {
    enable = mkEnableOption "Advanced features";
    
    setting1 = mkOption {
      type = types.int;
      default = 42;
      description = "Setting 1";
    };
    
    setting2 = mkOption {
      type = types.str;
      default = "default";
      description = "Setting 2";
    };
  };
};
```

### Configuration Validation

Add assertions for configuration validation:

```nix
assertions = [
  {
    assertion = cfg.user != "";
    message = "services.your-service.user must be specified";
  }
  {
    assertion = cfg.advanced.setting1 >= 0;
    message = "services.your-service.advanced.setting1 must be non-negative";
  }
];
```

### Configuration Generation

Generate configuration files from user settings:

```nix
# Generate configuration file
configFile = pkgs.writeText "your-service.conf" ''
  # Generated configuration
  user = ${cfg.user}
  setting1 = ${toString cfg.advanced.setting1}
  setting2 = ${cfg.advanced.setting2}
  
  ${cfg.config}
'';

# Use the generated configuration
systemd.services.your-service.serviceConfig.ExecStart = "${cfg.package}/bin/your-service --config ${configFile}";
```

## Home Manager Module

### Basic Module Structure

```nix
# home-manager/your-module.nix
{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.services.your-service;
in {
  options.services.your-service = {
    enable = mkEnableOption "Your service";
    
    package = mkOption {
      type = types.package;
      default = pkgs.your-package;
      description = "Your package to use";
    };
    
    # Other options...
  };

  config = mkIf cfg.enable {
    # Configuration when enabled
    home.packages = [ cfg.package ];
    
    # Systemd user services
    systemd.user.services.your-service = {
      Unit = {
        Description = "Your Service";
        After = [ "graphical-session.target" ];
        PartOf = [ "graphical-session.target" ];
      };
      
      Service = {
        ExecStart = "${cfg.package}/bin/your-service";
        Restart = "on-failure";
      };
      
      Install = {
        WantedBy = [ "graphical-session.target" ];
      };
    };
    
    # Other configuration...
  };
}
```

## Development Environment

### Basic Development Shell

```nix
devShells.default = pkgs.mkShell {
  buildInputs = with pkgs; [
    # Development tools
    git
    nixpkgs-fmt
    
    # Project dependencies
    python3
    python3Packages.pip
    python3Packages.setuptools
    python3Packages.wheel
    
    # Testing tools
    python3Packages.pytest
    python3Packages.pytest-cov
    
    # System dependencies
    gtk3
    gobject-introspection
  ];

  shellHook = ''
    echo "Development environment for Your Project"
    echo "Python: $(python --version)"
    echo ""
    echo "Available commands:"
    echo "  - nixpkgs-fmt: Format Nix files"
    echo "  - nix build: Build the package"
    echo "  - nix run: Run the application"
    echo "  - pytest: Run tests"
  '';
};
```

### Platform-specific Development Tools

```nix
devShells.default = pkgs.mkShell {
  buildInputs = with pkgs; [
    # Common tools
    git
    nixpkgs-fmt
    
    # Platform-specific tools
  ] ++ lib.optionals (system == "x86_64-linux") [
    # x86_64-specific tools
    gdb
    valgrind
  ] ++ lib.optionals (system == "aarch64-linux") [
    # ARM-specific tools
  ];
};
```

## Testing

### Test Configuration

```nix
# Enable tests
doCheck = true;

# Test dependencies
nativeCheckInputs = with python.pkgs; [
  pytest
  pytest-cov
  pytest-mock
];

# Test phase
checkPhase = ''
  runHook preCheck
  
  # Run tests
  python -m pytest tests/ -v
  
  runHook postCheck
'';
```

### Test Commands in Development Shell

```nix
shellHook = ''
  # ...
  
  echo "Testing:"
  echo "  - pytest tests/: Run all tests"
  echo "  - pytest tests/test_specific.py: Run specific test file"
  echo "  - pytest --cov=your_package tests/: Run tests with coverage"
'';
```

## Documentation

### Example Configurations

Provide example configurations:

```nix
# examples/basic-nixos-config.nix
{
  description = "Example NixOS configuration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    your-flake.url = "github:user/repo";
    your-flake.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, your-flake }: {
    nixosConfigurations.example = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        your-flake.nixosModules.default
        ({ config, pkgs, ... }: {
          services.your-service = {
            enable = true;
            # Configuration...
          };
        })
      ];
    };
  };
}
```

### README

Include a comprehensive README with:

- Project description
- Installation instructions
- Usage examples
- Configuration options
- Development instructions
- Troubleshooting

## Conclusion

Following these best practices will help you create clean, maintainable, and user-friendly NixOS flakes. The Toshy implementation demonstrates how to apply these practices to a complex application with system integration.

Remember that flakes are still an experimental feature of Nix, so some aspects may change in the future. However, the general principles outlined in this document are likely to remain valid.
