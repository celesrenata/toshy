#!/usr/bin/env python3
"""
Fix Wrapped Applications Script for Toshy

This script identifies and modifies code that wraps external applications,
replacing them with direct calls using shutil.which() for path resolution.
"""

import os
import re
import shutil
import sys

def find_python_files(directory):
    """Find all Python files in the given directory recursively."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def fix_terminal_utils(file_path):
    """Fix the terminal_utils.py file to use direct calls."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the TERMINAL_APPS list is defined in the file
    terminal_apps_pattern = r'TERMINAL_APPS\s*=\s*\[(.*?)\]'
    terminal_apps_match = re.search(terminal_apps_pattern, content, re.DOTALL)
    
    if not terminal_apps_match:
        return False
    
    # The terminal_utils.py file already uses shutil.which() for path resolution
    # in the _try_terminal function, but we can improve the TERMINAL_APPS list
    # to use dynamic discovery instead of hardcoding terminal names
    
    # Add a function to dynamically discover available terminals
    discover_terminals_func = """
def discover_available_terminals():
    \"\"\"Discover available terminal emulators on the system.\"\"\"
    available_terminals = []
    common_terminals = [
        ('gnome-terminal',          ['--'],     ['gnome', 'unity', 'cinnamon']     ),
        ('ptyxis',                  ['--'],     ['gnome', 'unity', 'cinnamon']     ),
        ('konsole',                 ['-e'],     ['kde']                            ),
        ('xfce4-terminal',          ['-e'],     ['xfce']                           ),
        ('mate-terminal',           ['-e'],     ['mate']                           ),
        ('qterminal',               ['-e'],     ['lxqt']                           ),
        ('lxterminal',              ['-e'],     ['lxde']                           ),
        ('terminology',             ['-e'],     ['enlightenment']                  ),
        ('cosmic-term',             ['-e'],     ['cosmic']                         ),
        ('io.elementary.terminal',  ['-e'],     ['pantheon']                       ),
        ('kitty',                   ['-e'],     []                                 ),
        ('alacritty',               ['-e'],     []                                 ),
        ('tilix',                   ['-e'],     []                                 ),
        ('terminator',              ['-e'],     []                                 ),
        ('xterm',                   ['-e'],     []                                 ),
        ('rxvt',                    ['-e'],     []                                 ),
        ('urxvt',                   ['-e'],     []                                 ),
        ('st',                      ['-e'],     []                                 ),
        ('kgx',                     ['-e'],     []                                 ),  # GNOME Console
    ]
    
    for terminal_cmd, args_list, de_list in common_terminals:
        if shutil.which(terminal_cmd):
            available_terminals.append((terminal_cmd, args_list, de_list))
    
    return available_terminals

# List of common terminal emulators in descending order of preference.
# Each element is a tuple: (command_name, args_list, supported_DEs)
TERMINAL_APPS = discover_available_terminals()
"""
    
    # Check if the discover_available_terminals function already exists
    if "def discover_available_terminals" not in content:
        # Replace the TERMINAL_APPS list with the dynamic discovery function
        modified_content = re.sub(
            r'# List of common terminal emulators.*?TERMINAL_APPS\s*=\s*\[(.*?)\]',
            discover_terminals_func,
            content,
            flags=re.DOTALL
        )
        
        if modified_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            return True
    
    return False

def fix_subprocess_calls(file_path):
    """Fix subprocess calls to use shutil.which for path resolution."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find subprocess calls with hardcoded executable names
    pattern = r'subprocess\.(Popen|call|run)\s*\(\s*\[?\s*[\'"]([^\'"./]+)[\'"]'
    
    # Check if shutil is already imported
    has_shutil_import = re.search(r'import\s+shutil|from\s+shutil\s+import', content) is not None
    
    modified_content = content
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        return False
    
    # Add shutil import if needed
    if not has_shutil_import:
        import_pattern = r'(import\s+[^\n]+\n|from\s+[^\n]+\n)'
        first_import = re.search(import_pattern, content)
        if first_import:
            modified_content = content[:first_import.end()] + 'import shutil\n' + content[first_import.end():]
    
    # Replace hardcoded executable names with shutil.which calls
    for match in reversed(matches):
        cmd_name = match.group(2)
        # Skip if it's a Python command or already using a variable
        if cmd_name in ['python', 'python3'] or cmd_name.startswith('$'):
            continue
        
        start, end = match.start(2), match.end(2)
        # Replace the hardcoded name with shutil.which call
        replacement = f'shutil.which("{cmd_name}")'
        modified_content = modified_content[:start-1] + replacement + modified_content[end+1:]
    
    # Write the modified content back to the file if changes were made
    if modified_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        return True
    
    return False

def fix_os_system_calls(file_path):
    """Fix os.system calls to use shutil.which for path resolution."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to find os.system calls with hardcoded executable names
    pattern = r'os\.system\s*\(\s*[\'"]([^\'"./\s]+)'
    
    # Check if shutil is already imported
    has_shutil_import = re.search(r'import\s+shutil|from\s+shutil\s+import', content) is not None
    
    modified_content = content
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        return False
    
    # Add shutil import if needed
    if not has_shutil_import:
        import_pattern = r'(import\s+[^\n]+\n|from\s+[^\n]+\n)'
        first_import = re.search(import_pattern, content)
        if first_import:
            modified_content = content[:first_import.end()] + 'import shutil\n' + content[first_import.end():]
    
    # Replace hardcoded executable names with shutil.which calls
    for match in reversed(matches):
        cmd_name = match.group(1)
        # Skip if it's a Python command or already using a variable
        if cmd_name in ['python', 'python3'] or cmd_name.startswith('$'):
            continue
        
        start, end = match.start(1), match.end(1)
        # Replace the hardcoded name with shutil.which call
        replacement = f'{{shutil.which("{cmd_name}")}}'
        modified_content = modified_content[:start-1] + replacement + modified_content[end+1:]
    
    # Write the modified content back to the file if changes were made
    if modified_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        return True
    
    return False

def fix_toshy_tray(file_path):
    """Fix toshy_tray.py to use direct calls for external applications."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The toshy_tray.py file already uses shutil.which() for most path resolution
    # Check for any remaining hardcoded paths
    
    # Pattern to find hardcoded executable names in function calls
    pattern = r'([\'"])([a-zA-Z0-9_-]+)([\'"])\s*\)'
    
    modified_content = content
    matches = list(re.finditer(pattern, content))
    
    if not matches:
        return False
    
    # Replace hardcoded executable names with shutil.which calls
    for match in reversed(matches):
        cmd_name = match.group(2)
        # Skip if it's not an executable name
        if not re.match(r'^[a-z0-9_-]+$', cmd_name) or cmd_name in ['python', 'python3']:
            continue
        
        start, end = match.start(2), match.end(2)
        # Check if this is actually an executable name
        context_before = content[max(0, start-20):start]
        if not re.search(r'(run|call|Popen|system|which)\s*\(', context_before):
            continue
        
        # Replace the hardcoded name with shutil.which call
        replacement = f'shutil.which("{cmd_name}")'
        modified_content = modified_content[:start-1] + replacement + modified_content[end+1:]
    
    # Write the modified content back to the file if changes were made
    if modified_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        return True
    
    return False

def main():
    """Main function to run the script."""
    project_dir = "."  # Current directory
    
    print("Scanning Python files for wrapped applications...")
    python_files = find_python_files(project_dir)
    
    modified_files = 0
    
    for file_path in python_files:
        print(f"Checking {file_path}...")
        
        # Apply fixes based on file type
        if os.path.basename(file_path) == 'terminal_utils.py':
            if fix_terminal_utils(file_path):
                modified_files += 1
                print(f"  Modified {file_path}")
        elif os.path.basename(file_path) == 'toshy_tray.py':
            if fix_toshy_tray(file_path):
                modified_files += 1
                print(f"  Modified {file_path}")
        else:
            # Apply general fixes
            if fix_subprocess_calls(file_path):
                modified_files += 1
                print(f"  Modified subprocess calls in {file_path}")
            
            if fix_os_system_calls(file_path):
                modified_files += 1
                print(f"  Modified os.system calls in {file_path}")
    
    print(f"\nModified {modified_files} files to use direct calls to external applications.")
    print("Done!")

if __name__ == "__main__":
    main()
