# Toshy Flake Architecture Design

## Proposed Flake Structure

```
toshy/
├── flake.nix              # Main flake definition
├── flake.lock             # Locked dependencies
├── default.nix            # Backward compatibility
├── packages/
│   ├── default.nix        # Package exports
│   ├── toshy.nix          # Main toshy package
│   ├── xwaykeyz.nix       # Custom xwaykeyz package
│   └── python-deps.nix    # Custom Python dependencies
├── modules/
│   ├── default.nix        # NixOS module exports
│   └── toshy.nix          # NixOS service module
├── overlays/
│   └── default.nix        # Package overlays
└── docs/
    ├── USAGE.md           # Usage documentation
    └── DEVELOPMENT.md     # Development guide
```

## Flake Outputs

### Packages
- `packages.x86_64-linux.toshy` - Main application
- `packages.x86_64-linux.xwaykeyz` - Dependency package
- `packages.x86_64-linux.default` - Alias to toshy

### Development
- `devShells.x86_64-linux.default` - Development environment
- `formatter.x86_64-linux` - Code formatter (nixpkgs-fmt)

### NixOS Integration
- `nixosModules.toshy` - NixOS service module
- `overlays.default` - Package overlay

## Key Design Principles

### 1. Separation of Concerns
- Main application package separate from dependencies
- NixOS module separate from package definition
- Development tools isolated in devShell

### 2. Proper Python Packaging
```nix
buildPythonApplication {
  pname = "toshy";
  version = "24.12.1";
  format = "pyproject";  # Use modern Python packaging
  
  # Proper dependency categorization
  nativeBuildInputs = [ ... ];      # Build-time tools
  buildInputs = [ ... ];            # Native libraries
  propagatedBuildInputs = [ ... ];  # Python runtime deps
}
```

### 3. Version Management
- Use `lib.importTOML ./pyproject.toml` for version extraction
- Support version overrides via flake inputs
- Automatic dependency version resolution

### 4. Cross-Platform Support
- Support multiple architectures (x86_64-linux, aarch64-linux)
- Conditional dependencies based on platform
- Proper system integration

### 5. Testing Integration
- Unit tests in package definition
- Integration tests in devShell
- CI/CD friendly structure

## Migration Strategy

### Phase 1: Basic Flake Structure
1. Create minimal working flake.nix
2. Convert main toshy package
3. Basic NixOS module

### Phase 2: Dependency Cleanup
1. Remove duplicate package definitions
2. Use nixpkgs packages where possible
3. Properly package custom dependencies

### Phase 3: Advanced Features
1. Development environment
2. Testing infrastructure
3. Documentation and examples

### Phase 4: Integration
1. NixOS module with full configuration
2. Home Manager integration
3. Overlay for easy inclusion
