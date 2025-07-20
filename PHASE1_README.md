# Phase 1: Dependency Analysis and Requirements Refinement

This directory contains the implementation of Phase 1 of the Toshy NixOS Improvement Plan, focusing on dependency analysis and requirements refinement.

## Objectives

1. Create an accurate requirements.txt by scanning all imports
2. Remove external application wrapping
3. Update code to directly call external applications

## Files

- `import_scanner.py`: Script to scan all Python files for import statements and generate an accurate requirements.txt file
- `fix_wrapped_applications.py`: Script to identify and fix wrapped external applications in the codebase
- `updated_requirements.txt`: The new requirements.txt file generated based on actual imports

## Usage

### Scanning Imports

To scan all Python files for imports and generate a requirements.txt file:

```bash
python import_scanner.py
```

This will:
1. Recursively scan all Python files in the project
2. Extract all import statements
3. Classify imports as standard library, third-party, or local
4. Generate a list of required third-party packages
5. Create a `generated_requirements.txt` file

### Fixing Wrapped Applications

To identify and fix wrapped external applications in the codebase:

```bash
python fix_wrapped_applications.py
```

This will:
1. Recursively scan all Python files in the project
2. Identify hardcoded executable names in subprocess calls and os.system calls
3. Replace them with shutil.which() calls for path resolution
4. Improve the terminal_utils.py file to use dynamic discovery of terminal emulators
5. Fix any remaining hardcoded paths in toshy_tray.py

## Implementation Details

### Import Scanner

The import scanner uses Python's AST (Abstract Syntax Tree) module to parse Python files and extract import statements. It handles both regular imports and from-imports, and can detect imports in try/except blocks and conditional statements.

The scanner classifies imports as:
- Standard library: Built-in Python modules
- Third-party: External packages that need to be installed
- Local: Modules within the Toshy project

### Wrapped Applications Fix

The script to fix wrapped applications focuses on:

1. **Subprocess Calls**: Replacing hardcoded executable names in subprocess.Popen, subprocess.call, and subprocess.run calls with shutil.which() calls.

2. **OS System Calls**: Replacing hardcoded executable names in os.system calls with shutil.which() calls.

3. **Terminal Utils**: Improving the terminal_utils.py file to use dynamic discovery of terminal emulators instead of hardcoding them.

4. **Toshy Tray**: Fixing any remaining hardcoded paths in toshy_tray.py.

### Requirements.txt

The updated requirements.txt file includes:
- Core dependencies with version constraints
- Version-specific dependencies with pinned versions
- Optional dependencies with environment markers
- Comments for clarity

## Next Steps

After implementing Phase 1:

1. Review the generated requirements.txt file and make any necessary adjustments
2. Test the application with the updated code to ensure it works correctly
3. Update the flake.nix file to use the new requirements.txt file
4. Proceed to Phase 2: CLI Accessibility Improvement
