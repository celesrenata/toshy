# Phase 1: Dependency Analysis and Requirements Refinement

## Objective
Create an accurate requirements.txt by scanning all imports and remove external application wrapping.

## Background
The current requirements.txt is marked as "DO_NOT_USE" and is only for information purposes. The real dependencies are defined in pyproject.toml and flake.nix. We need to ensure all dependencies are accurately captured and remove any wrapped external applications like thunar.

## Tasks

### 1. Scan All Python Files for Import Statements
- Create a script to recursively scan all Python files in the project
- Extract all import statements (both regular imports and from-imports)
- Handle conditional imports (e.g., try/except blocks, if statements)
- Create a comprehensive list of all imported modules

**Implementation Details:**
```python
import os
import re
import ast
from collections import defaultdict

def scan_imports(directory):
    imports = defaultdict(set)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        tree = ast.parse(f.read())
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for name in node.names:
                                    imports[name.name].add(file_path)
                            elif isinstance(node, ast.ImportFrom):
                                module = node.module or ''
                                for name in node.names:
                                    full_name = f"{module}.{name.name}" if module else name.name
                                    imports[full_name].add(file_path)
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    return imports

# Usage
imports = scan_imports('/path/to/toshy')
```

### 2. Compare Found Dependencies with Current Requirements
- Compare the extracted imports with entries in requirements.txt and pyproject.toml
- Identify missing dependencies
- Identify unused dependencies
- Determine which dependencies are standard library vs. third-party

**Files to Analyze:**
- requirements.txt
- DO_NOT_USE_requirements.txt
- pyproject.toml
- flake.nix

### 3. Identify and Remove Wrapped External Applications
- Search for instances where external applications (like thunar) are wrapped
- Look in flake.nix for wrapped applications in buildInputs or propagatedBuildInputs
- Check for system calls or subprocess executions that could be replaced with direct calls

**Key Files to Check:**
- flake.nix
- modules/toshy.nix
- home-manager/toshy.nix
- toshy_gui/main_gtk4.py
- toshy_tray.py
- toshy_common/terminal_utils.py

### 4. Update flake.nix to Directly Call External Applications
- Modify flake.nix to use direct calls to external applications
- Replace wrapped applications with direct path references
- Use `pkgs.lib.getExe` for executable paths when appropriate

**Example Change:**
```nix
# Before
buildInputs = with pkgs; [
  thunar  # File manager wrapped into the application
];

# After
# Remove from buildInputs and use direct calls instead
# In the code, replace:
# subprocess.Popen(["thunar", path])
# With:
# fileManager = shutil.which('thunar') or shutil.which('nautilus') or shutil.which('dolphin')
# subprocess.Popen([fileManager, path])
```

### 5. Create an Accurate requirements.txt
- Generate a new requirements.txt based on actual imports
- Include version constraints where necessary
- Add comments for clarity
- Ensure compatibility with both pip and Nix packaging

**Example Format:**
```
# Core dependencies
appdirs>=1.4.4
dbus-python>=1.2.16
evdev>=1.4.0
i3ipc>=2.2.1
inotify-simple>=1.3.5
lockfile>=0.12.2
ordered-set>=4.1.0
pillow>=9.0.0
psutil>=5.9.0
pygobject>=3.42.0
pywayland>=0.4.14
six>=1.16.0
systemd-python>=234
watchdog>=2.1.9

# Version-specific dependencies
python-xlib==0.31  # Pinned for compatibility
xkbcommon<1.1  # Version constraint due to API changes

# Optional dependencies
hyprpy; "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
sv-ttk; sys.version_info >= (3, 10)  # For modern theming
```

## Potential Issues
1. **Conditional Imports**: Some imports may be conditional and only used in certain environments
2. **Dynamic Imports**: Code using `__import__()` or `importlib` may be harder to detect
3. **Optional Dependencies**: Some dependencies might be optional and only needed for specific features
4. **Version Conflicts**: Different parts of the code might require different versions of the same dependency

## Success Criteria
- All necessary dependencies are accurately captured in requirements.txt
- No external applications are wrapped within the Toshy application
- flake.nix is updated to use direct calls to external applications
- The application works correctly with the updated dependency management
- Documentation is updated to reflect the changes

## Files to Modify
- requirements.txt
- flake.nix
- modules/toshy.nix
- home-manager/toshy.nix
- Any files that directly wrap external applications
