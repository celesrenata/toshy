# Toshy Packaging Issues Analysis

## Critical Issues in Current Implementation

### 1. Incorrect Attribute Names
```nix
# WRONG (current code)
BuildInputs = with prev.pkgs.python312Packages; [ ... ];

# CORRECT
buildInputs = with prev.pkgs.python312Packages; [ ... ];
```

### 2. Duplicate Package Definitions
The current overlay defines packages twice:
- `python-xlib-init` and `python-xlib`
- `dbus-python-init` and `dbus-python`
- `python-xwaykeyz-init` and `python-xwaykeyz`

This is unnecessary complexity and should be simplified.

### 3. Improper Dependency Classification

#### Current Issues:
- `BuildInputs` used instead of `buildInputs`
- `propagatedNativeBuildInputs` used incorrectly
- System dependencies mixed with Python packages

#### Correct Classification:
```nix
nativeBuildInputs = [
  # Build-time tools
  setuptools
  wheel
  wrapGAppsHook
];

buildInputs = [
  # Native system libraries
  gtk3
  gobject-introspection
];

propagatedBuildInputs = [
  # Python runtime dependencies
  python3Packages.appdirs
  python3Packages.evdev
  # ... other Python packages
];
```

### 4. Manual Installation Phase Problems

Current approach uses shell scripts:
```bash
find scripts/ | awk '{ print "install -m755 -D " $0 " \$out/" $0 }' | bash
```

Issues:
- Not reproducible
- Doesn't handle file permissions properly
- Doesn't integrate with Python packaging
- Hard to maintain

### 5. Missing Python Package Structure

The application should use proper Python packaging:
- `pyproject.toml` or `setup.py`
- Proper entry points
- Package metadata
- Dependency declarations

## Recommended Solutions

### 1. Use Standard Python Packaging
```nix
buildPythonApplication {
  pname = "toshy";
  version = "24.12.1";
  format = "pyproject";  # or "setuptools"
  
  # Let Python packaging handle installation
  # No custom installPhase needed
}
```

### 2. Leverage nixpkgs Packages
```nix
propagatedBuildInputs = with python3Packages; [
  xlib              # instead of custom python-xlib
  dbus-python       # instead of custom dbus-python
  i3ipc             # instead of custom python-i3ipc
  # ... other standard packages
];
```

### 3. Proper Entry Points
Define console scripts in `pyproject.toml`:
```toml
[project.scripts]
toshy-gui = "toshy.gui:main"
toshy-tray = "toshy.tray:main"
toshy-config = "toshy.config:main"
```

### 4. Systemd Integration
Use NixOS modules for service management instead of bundling systemd files.

### 5. Configuration Management
- Use NixOS options for configuration
- Provide sensible defaults
- Allow user customization

## Testing Strategy

### Unit Tests
```nix
checkInputs = with python3Packages; [
  pytest
  pytest-cov
  pytest-mock
];

checkPhase = ''
  pytest tests/
'';
```

### Integration Tests
- Test GUI components
- Test keybinding functionality
- Test system integration

### Build Tests
- Verify all dependencies resolve
- Check for missing files
- Validate entry points
