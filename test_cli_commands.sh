#!/bin/bash
set -e

echo "Testing Toshy CLI commands..."
echo "=============================="

# Function to test a command
test_command() {
    local cmd=$1
    local desc=$2
    
    echo -n "Testing $cmd ($desc)... "
    
    if command -v $cmd &> /dev/null; then
        echo "FOUND"
        echo "  Command path: $(which $cmd)"
        echo "  Command permissions: $(ls -l $(which $cmd))"
        echo "  Help output:"
        $cmd --help 2>&1 | head -n 5 | sed 's/^/    /'
        echo ""
    else
        echo "NOT FOUND"
        echo "  Error: $cmd command is not available in PATH"
        echo ""
    fi
}

# Test all CLI commands
test_command "toshy-tray" "System tray application"
test_command "toshy-gui" "GUI preferences application"
test_command "toshy-layout-selector" "Keyboard layout selector"
test_command "toshy-config" "Configuration utility"
test_command "toshy-daemon" "Main daemon service"
test_command "toshy-config-generator" "Configuration generator"
test_command "toshy-platform" "Platform detection utility"
test_command "toshy-debug" "Debug utility"
test_command "toshy-performance" "Performance monitoring utility"

echo "=============================="
echo "CLI command testing completed."
