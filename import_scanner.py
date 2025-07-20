#!/usr/bin/env python3
"""
Import Scanner for Toshy

This script recursively scans all Python files in the project and extracts import statements.
It classifies imports as standard library, third-party, or local, and generates a list of
required third-party packages that can be used to create an accurate requirements.txt file.
"""

import os
import re
import ast
import sys
import pkgutil
from collections import defaultdict
import importlib.metadata

def scan_imports(directory):
    """
    Recursively scan all Python files in the directory and extract imports.
    Returns a dictionary mapping module names to the files that import them.
    """
    imports = defaultdict(set)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
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
                        except SyntaxError as e:
                            print(f"Syntax error in {file_path}: {e}")
                        except Exception as e:
                            print(f"Error parsing {file_path}: {e}")
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return imports

def get_standard_library_modules():
    """Get a set of standard library module names."""
    std_lib_modules = set(sys.builtin_module_names)
    
    # Add modules from standard library paths
    for path in sys.path:
        if path.startswith(sys.prefix) and 'site-packages' not in path:
            try:
                for module_info in pkgutil.iter_modules([path]):
                    std_lib_modules.add(module_info.name)
            except (ImportError, OSError):
                pass
    
    # Add some common standard library modules that might be missed
    std_lib_modules.update([
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'configparser',
        'contextlib', 'copy', 'csv', 'datetime', 'enum', 'functools', 'glob', 'hashlib',
        'hmac', 'html', 'http', 'importlib', 'inspect', 'io', 'itertools', 'json',
        'logging', 'math', 'multiprocessing', 'os', 'pathlib', 'pickle', 'platform',
        'queue', 're', 'shutil', 'signal', 'socket', 'sqlite3', 'string', 'struct',
        'subprocess', 'sys', 'tempfile', 'threading', 'time', 'traceback', 'types',
        'typing', 'unittest', 'urllib', 'uuid', 'warnings', 'weakref', 'xml', 'zipfile'
    ])
    
    return std_lib_modules

def classify_imports(imports):
    """
    Classify imports as standard library, third-party, or local.
    """
    std_lib_modules = get_standard_library_modules()
    
    classified = {
        'standard_library': defaultdict(set),
        'third_party': defaultdict(set),
        'local': defaultdict(set)
    }
    
    for module, files in imports.items():
        base_module = module.split('.')[0]
        if base_module in std_lib_modules:
            classified['standard_library'][module] = files
        elif base_module.startswith('toshy') or base_module.startswith('xwaykeyz'):
            classified['local'][module] = files
        else:
            classified['third_party'][module] = files
    
    return classified

def get_installed_package_version(package_name):
    """Get the installed version of a package."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None

def map_import_to_package(import_name):
    """Map an import name to its corresponding package name."""
    # Common mappings where import name differs from package name
    mappings = {
        'gi': 'PyGObject',
        'PIL': 'Pillow',
        'psycopg2': 'psycopg2-binary',
        'yaml': 'PyYAML',
        'bs4': 'beautifulsoup4',
        'dbus': 'dbus-python',
        'xlib': 'python-xlib',
    }
    
    base_name = import_name.split('.')[0]
    return mappings.get(base_name, base_name)

def generate_requirements(classified_imports, current_requirements=None):
    """
    Generate a requirements.txt file from classified imports.
    If current_requirements is provided, it will try to preserve version constraints.
    """
    third_party_modules = sorted(classified_imports['third_party'].keys())
    requirements = {}
    
    # Parse current requirements if provided
    current_versions = {}
    if current_requirements:
        try:
            with open(current_requirements, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Handle different formats like package==1.0.0, package>=1.0.0, etc.
                        parts = re.split(r'[=<>~]', line, 1)
                        if len(parts) > 1:
                            package = parts[0].strip()
                            current_versions[package.lower()] = line
                        else:
                            current_versions[line.lower()] = line
        except Exception as e:
            print(f"Error reading current requirements file: {e}")
    
    # Process third-party modules
    for module in third_party_modules:
        base_module = module.split('.')[0]
        package_name = map_import_to_package(base_module)
        
        if package_name.lower() not in requirements:
            # Try to preserve version constraints from current requirements
            if package_name.lower() in current_versions:
                requirements[package_name.lower()] = current_versions[package_name.lower()]
            else:
                # Try to get the installed version
                version = get_installed_package_version(package_name)
                if version:
                    requirements[package_name.lower()] = f"{package_name}>={version}"
                else:
                    requirements[package_name.lower()] = package_name
    
    return sorted(requirements.values())

def analyze_wrapped_applications(directory):
    """
    Analyze the codebase for wrapped external applications.
    Looks for subprocess calls and system executions.
    """
    wrapped_apps = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Look for subprocess calls
                        subprocess_pattern = r'subprocess\.(Popen|call|run)\s*\(\s*\[?\s*[\'"]([^\'"]+)[\'"]'
                        for match in re.finditer(subprocess_pattern, content):
                            app_name = match.group(2)
                            if not app_name.startswith(('python', 'toshy', './', '/')):
                                wrapped_apps.append((app_name, file_path))
                        
                        # Look for os.system calls
                        system_pattern = r'os\.system\s*\(\s*[\'"]([^\'"]+)[\'"]'
                        for match in re.finditer(system_pattern, content):
                            command = match.group(1).split()[0]
                            if not command.startswith(('python', 'toshy', './', '/')):
                                wrapped_apps.append((command, file_path))
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")
    
    return wrapped_apps

def main():
    """Main function to run the import scanner."""
    project_dir = "."  # Current directory
    
    print("Scanning Python files for imports...")
    imports = scan_imports(project_dir)
    
    print("Classifying imports...")
    classified = classify_imports(imports)
    
    print("\n=== Import Analysis Results ===")
    print(f"Standard Library Imports: {len(classified['standard_library'])}")
    print(f"Third-Party Imports: {len(classified['third_party'])}")
    print(f"Local Imports: {len(classified['local'])}")
    
    print("\n=== Standard Library Imports ===")
    for module in sorted(classified['standard_library'].keys()):
        files_count = len(classified['standard_library'][module])
        print(f"- {module} (used in {files_count} files)")
    
    print("\n=== Third-Party Imports ===")
    for module in sorted(classified['third_party'].keys()):
        files_count = len(classified['third_party'][module])
        print(f"- {module} (used in {files_count} files)")
    
    print("\n=== Local Imports ===")
    for module in sorted(classified['local'].keys()):
        files_count = len(classified['local'][module])
        print(f"- {module} (used in {files_count} files)")
    
    print("\n=== Analyzing Wrapped Applications ===")
    wrapped_apps = analyze_wrapped_applications(project_dir)
    if wrapped_apps:
        print("Found potential wrapped applications:")
        for app, file_path in wrapped_apps:
            print(f"- {app} (in {file_path})")
    else:
        print("No wrapped applications found.")
    
    print("\n=== Generating Requirements ===")
    # Try to preserve version constraints from current requirements.txt
    requirements = generate_requirements(classified, "requirements.txt")
    
    # Write requirements to file
    with open("generated_requirements.txt", "w") as f:
        f.write("# Generated requirements.txt for Toshy\n")
        f.write("# This file was automatically generated by import_scanner.py\n\n")
        
        # Core dependencies
        f.write("# Core dependencies\n")
        for req in requirements:
            f.write(f"{req}\n")
    
    print(f"Generated requirements written to generated_requirements.txt")
    print("Done!")

if __name__ == "__main__":
    main()
