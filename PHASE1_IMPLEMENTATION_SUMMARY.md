# Phase 1 Implementation Summary: Dependency Analysis and Requirements Refinement

## Overview

This document summarizes the implementation of Phase 1 of the Toshy NixOS Improvement Plan. The primary goals of this phase were to create an accurate requirements.txt file based on actual imports and to remove external application wrapping from the codebase.

## Key Accomplishments

1. **Dependency Analysis**
   - Created a comprehensive import scanner that analyzes all Python files in the project
   - Identified and classified all imports as standard library, third-party, or local
   - Generated an accurate requirements.txt file based on actual imports

2. **External Application Unwrapping**
   - Identified wrapped external applications in the codebase
   - Created a script to replace hardcoded executable names with shutil.which() calls
   - Improved terminal_utils.py to use dynamic discovery of terminal emulators

## Implementation Details

### Import Scanner

The import scanner (`import_scanner.py`) uses Python's Abstract Syntax Tree (AST) module to parse Python files and extract import statements. It handles:

- Regular imports (`import x`)
- From-imports (`from x import y`)
- Conditional imports (in try/except blocks and if statements)
- Module aliases

The scanner classifies imports into three categories:
1. **Standard Library**: Built-in Python modules
2. **Third-Party**: External packages that need to be installed
3. **Local**: Modules within the Toshy project

The scanner also analyzes the codebase for wrapped external applications by looking for:
- subprocess.Popen, subprocess.call, and subprocess.run calls with hardcoded executable names
- os.system calls with hardcoded executable names

### Requirements.txt Generation

The updated requirements.txt file (`updated_requirements.txt`) includes:

- **Core dependencies** with version constraints
  ```
  appdirs>=1.4.4
  dbus-python>=1.2.16
  evdev>=1.4.0
  i3ipc>=2.2.1
  inotify-simple>=1.3.5
  lockfile>=0.12.2
  ordered-set>=4.1.0
  pillow>=9.0.0
  psutil>=5.9.0
  pygobject<=3.44.1
  pywayland>=0.4.14
  six>=1.16.0
  systemd-python>=234
  watchdog>=2.1.9
  ```

- **Version-specific dependencies** with pinned versions
  ```
  python-xlib==0.31
  xkbcommon<1.1
  ```

- **Optional dependencies** with environment markers
  ```
  hyprpy; "hyprland" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
  sv-ttk; sys.version_info >= (3, 10)
  ```

### Wrapped Applications Fix

The script to fix wrapped applications (`fix_wrapped_applications.py`) focuses on:

1. **Subprocess Calls**: Replacing hardcoded executable names with shutil.which() calls
   ```python
   # Before
   subprocess.Popen(["gdbus", "introspect", "--session", ...])
   
   # After
   subprocess.Popen([shutil.which("gdbus"), "introspect", "--session", ...])
   ```

2. **OS System Calls**: Replacing hardcoded executable names with shutil.which() calls
   ```python
   # Before
   os.system(f'{pkill_cmd} -f "toshy_tray.py"')
   
   # After
   os.system(f'{shutil.which("pkill")} -f "toshy_tray.py"')
   ```

3. **Terminal Utils**: Improving terminal_utils.py to use dynamic discovery of terminal emulators
   ```python
   # Before
   TERMINAL_APPS = [
       ('gnome-terminal', ['--'], ['gnome', 'unity', 'cinnamon']),
       ('konsole', ['-e'], ['kde']),
       # ...
   ]
   
   # After
   def discover_available_terminals():
       """Discover available terminal emulators on the system."""
       available_terminals = []
       common_terminals = [
           ('gnome-terminal', ['--'], ['gnome', 'unity', 'cinnamon']),
           ('konsole', ['-e'], ['kde']),
           # ...
       ]
       
       for terminal_cmd, args_list, de_list in common_terminals:
           if shutil.which(terminal_cmd):
               available_terminals.append((terminal_cmd, args_list, de_list))
       
       return available_terminals

   TERMINAL_APPS = discover_available_terminals()
   ```

## Wrapped Applications Found

The import scanner identified the following wrapped external applications in the codebase:

1. In `toshy_tray.py`:
   - gdbus
   - xdg-open
   - kde-open

2. In `toshy_common/terminal_utils.py`:
   - Various terminal emulators (gnome-terminal, konsole, etc.)

3. In `toshy_common/notification_manager.py`:
   - notify-send

4. In `toshy_common/shared_device_context.py`:
   - pgrep

5. In `toshy_common/env_context.py`:
   - ps
   - grep

6. In `setup_toshy.py`:
   - touch
   - sudo
   - rpm
   - pacman
   - apk
   - gsettings
   - curl
   - wget

## Benefits of the Implementation

1. **Improved Dependency Management**
   - The accurate requirements.txt file ensures that all necessary dependencies are installed
   - Version constraints help avoid compatibility issues
   - Optional dependencies are only installed when needed

2. **Enhanced Portability**
   - Using shutil.which() for path resolution makes the code more portable across different systems
   - Dynamic discovery of terminal emulators ensures that the application works with whatever terminal is available

3. **Better Maintainability**
   - Removing hardcoded executable names makes the code easier to maintain
   - The code is more robust against changes in the system environment

## Next Steps

1. **Testing**: Test the application with the updated code to ensure it works correctly
2. **Flake.nix Update**: Update the flake.nix file to use the new requirements.txt file
3. **Phase 2**: Proceed to Phase 2: CLI Accessibility Improvement
