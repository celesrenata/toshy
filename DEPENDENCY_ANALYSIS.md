# Toshy Dependency Analysis

## Current Dependencies in Overlay

### Python Dependencies
- `python-xlib` - X11 library bindings (available in nixpkgs as `python3Packages.xlib`)
- `dbus-python` - D-Bus bindings (available in nixpkgs as `python3Packages.dbus-python`)
- `hyprpy` - Hyprland Python bindings (PyPI package)
- `i3ipc` - i3 IPC library (available in nixpkgs as `python3Packages.i3ipc`)
- `xwaykeyz` - Custom keybinding library (needs proper packaging)

### System Dependencies
- `gtk3` - GTK3 for GUI components
- `gobject-introspection` - GObject bindings
- `wrapGAppsHook` - GTK application wrapper

### Python Packages (Standard)
- `appdirs` - Application directories
- `pycairo` - Cairo bindings
- `evdev` - Input device access
- `inotify-simple` - File system monitoring
- `pillow` - Image processing
- `pygobject3` - GObject Python bindings
- `lockfile` - File locking
- `systemd` - Systemd integration
- `sv-ttk` - Sun Valley TTK theme
- `watchdog` - File system monitoring
- `ordered-set` - Ordered set data structure
- `psutil` - System and process utilities
- `pywayland` - Wayland protocol bindings
- `pywlroots` - wlroots bindings
- `pydantic` - Data validation

## Recommendations

### Use nixpkgs Packages Where Available
Most Python dependencies are already available in nixpkgs and should be used instead of custom builds:

```nix
python3Packages.xlib          # instead of custom python-xlib
python3Packages.dbus-python   # instead of custom dbus-python  
python3Packages.i3ipc         # instead of custom python-i3ipc
```

### Custom Packages Needed
Only these packages need custom definitions:
- `xwaykeyz` - Custom fork/version
- `hyprpy` - If specific version needed
- `toshy` - Main application

### Dependency Categories

#### Runtime Dependencies (propagatedBuildInputs)
- Core Python libraries that the application imports
- System libraries needed at runtime

#### Build Dependencies (nativeBuildInputs)
- Build tools (setuptools, wheel, etc.)
- Code generation tools
- Wrappers (wrapGAppsHook)

#### System Dependencies (buildInputs)
- Native libraries
- GTK3, GObject introspection
