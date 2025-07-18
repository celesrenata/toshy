# Toshy Nix Modernization Context

## Current State Analysis

The existing `toshy.nix` overlay has several critical issues that prevent it from following modern Nix practices:

### Major Problems Identified

1. **Duplicate Package Definitions**: Multiple `-init` variants of packages that serve no clear purpose
2. **Incorrect Attribute Usage**: Using `BuildInputs` instead of `buildInputs` (case sensitivity)
3. **Improper Dependency Management**: Mixing `nativeBuildInputs`, `buildInputs`, and `propagatedBuildInputs` incorrectly
4. **Manual Installation Phase**: Using shell scripts instead of proper Python packaging
5. **Hardcoded Versions**: No version management or update mechanism
6. **Missing Flake Structure**: Not following modern Nix flake conventions
7. **Overlay Complexity**: Overly complex overlay structure when simpler approaches exist

### Dependencies That Need Proper Packaging

- `python-xlib` (already available in nixpkgs)
- `dbus-python` (already available in nixpkgs)
- `xwaykeyz` (custom dependency)
- `hyprpy` (available on PyPI)
- `i3ipc` (available in nixpkgs)
- Various Python packages that should use nixpkgs versions

## Modernization Goals

1. **Convert to Nix Flake**: Use modern flake.nix structure
2. **Proper Python Packaging**: Use buildPythonApplication correctly
3. **Dependency Management**: Use nixpkgs packages where available
4. **Clean Architecture**: Separate concerns properly
5. **Version Management**: Implement proper versioning and updates
6. **Testing**: Add proper test infrastructure
7. **Documentation**: Clear usage and development docs
