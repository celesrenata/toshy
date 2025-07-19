#!/usr/bin/env python3
"""
Toshy Daemon - Main keybinding service daemon

This daemon starts the xwaykeyz keymapper with the Toshy configuration.
"""

import sys
import os
import subprocess
import time
import signal
from pathlib import Path
from .platform_utils import get_platform_detector

# Import xwaykeyz as a module instead of calling it as subprocess
try:
    import xwaykeyz.main
    XWAYKEYZ_AVAILABLE = True
except ImportError:
    XWAYKEYZ_AVAILABLE = False
    print("Warning: xwaykeyz module not available, falling back to subprocess", file=sys.stderr)

def find_config_file():
    """Find the Toshy configuration file"""
    # Standard locations to check for config file
    config_locations = [
        os.path.expanduser("~/.config/toshy/toshy_config.py"),
        os.path.join(os.path.dirname(__file__), "..", "default-toshy-config", "toshy_config.py"),
        "/etc/toshy/toshy_config.py",
    ]
    
    for config_path in config_locations:
        if os.path.exists(config_path):
            return config_path
    
    return None

def wait_for_display():
    """Wait for X11 or Wayland display to be ready"""
    session_type = os.environ.get('XDG_SESSION_TYPE', '')
    
    if session_type == 'x11':
        # Wait for X11 display
        display = os.environ.get('DISPLAY')
        if not display:
            print("Toshy Daemon: DISPLAY not set for X11 session", file=sys.stderr)
            return False
            
        # Try to use xset to check if X server is ready
        for attempt in range(30):  # Wait up to 30 seconds
            try:
                result = subprocess.run(['xset', '-q'], 
                                      capture_output=True, 
                                      timeout=5)
                if result.returncode == 0:
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            print(f"Toshy Daemon: Waiting for X server (attempt {attempt + 1}/30)", file=sys.stderr)
            time.sleep(1)
            
    elif session_type == 'wayland':
        # Wait for Wayland display
        wayland_display = os.environ.get('WAYLAND_DISPLAY')
        if not wayland_display:
            print("Toshy Daemon: WAYLAND_DISPLAY not set for Wayland session", file=sys.stderr)
            return False
        
        # For Wayland, we just check if the socket exists
        runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
        if runtime_dir:
            wayland_socket = os.path.join(runtime_dir, wayland_display)
            for attempt in range(30):  # Wait up to 30 seconds
                if os.path.exists(wayland_socket):
                    return True
                print(f"Toshy Daemon: Waiting for Wayland socket (attempt {attempt + 1}/30)", file=sys.stderr)
                time.sleep(1)
    
    return True  # If we can't determine session type, proceed anyway

def cleanup_existing_processes():
    """Stop any existing keymapper processes"""
    processes_to_kill = ['xwaykeyz', 'keyszer', 'xkeysnail']
    
    for process_name in processes_to_kill:
        try:
            subprocess.run(['pkill', '-f', f'bin/{process_name}'], 
                         capture_output=True)
        except FileNotFoundError:
            # pkill not available, try alternative
            try:
                subprocess.run(['killall', process_name], 
                             capture_output=True)
            except FileNotFoundError:
                pass

def setup_x11_permissions():
    """Set up X11 permissions if needed"""
    session_type = os.environ.get('XDG_SESSION_TYPE', '')
    if session_type == 'x11':
        try:
            subprocess.run(['xhost', '+local:'], 
                         capture_output=True, 
                         timeout=5)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

def main():
    """Main entry point for toshy-daemon command"""
    print("Toshy daemon starting...")
    
    # Get platform information
    detector = get_platform_detector()
    platform_info = detector.get_platform_info()
    
    print(f"Platform: {platform_info['architecture']}")
    print(f"Display: {platform_info['display_server']}")
    if platform_info['wayland_compositor']:
        print(f"Compositor: {platform_info['wayland_compositor']}")
    
    # Apply platform-specific optimizations
    recommended = platform_info['recommended_settings']
    if not recommended['enable_optimizations']:
        print("Running in compatibility mode for this platform")
    
    # Check if xwaykeyz is available
    if not XWAYKEYZ_AVAILABLE:
        # Fallback to subprocess check
        try:
            result = subprocess.run(['xwaykeyz', '--version'], 
                                  capture_output=True, 
                                  timeout=5)
            if result.returncode != 0:
                raise FileNotFoundError
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("Error: xwaykeyz not available as module or command. Please ensure xwaykeyz is installed.", file=sys.stderr)
            sys.exit(1)
    else:
        print("xwaykeyz module available - using integrated execution")
    
    # Find configuration file
    config_file = find_config_file()
    if not config_file:
        print("Error: Could not find Toshy configuration file", file=sys.stderr)
        print("Looked in:", file=sys.stderr)
        print("  ~/.config/toshy/toshy_config.py", file=sys.stderr)
        print("  /etc/toshy/toshy_config.py", file=sys.stderr)
        sys.exit(1)
    
    print(f"Using configuration file: {config_file}")
    
    # Wait for display system to be ready
    if not wait_for_display():
        print("Warning: Display system may not be ready", file=sys.stderr)
    
    # Clean up any existing processes
    cleanup_existing_processes()
    
    # Set up X11 permissions if needed
    setup_x11_permissions()
    
    # Create marker file to indicate service has started
    runtime_dir = os.environ.get('XDG_RUNTIME_DIR')
    if runtime_dir:
        marker_file = os.path.join(runtime_dir, 'toshy-daemon.start')
        Path(marker_file).touch()
    
    # Start xwaykeyz with the configuration
    print(f"Using configuration file: {config_file}")
    
    try:
        if XWAYKEYZ_AVAILABLE:
            # Use xwaykeyz as a Python module (preferred method)
            # This ensures the configuration runs in the same Python environment
            print("Starting xwaykeyz as Python module...")
            
            # Set up signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                print(f"Received signal {signum}, shutting down...")
                sys.exit(0)
            
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Prepare arguments for xwaykeyz
            # Simulate command line: xwaykeyz -w -c config_file
            original_argv = sys.argv.copy()
            sys.argv = ['xwaykeyz', '-w', '-c', config_file]
            
            try:
                # Call xwaykeyz main function directly
                xwaykeyz.main.main()
            finally:
                # Restore original argv
                sys.argv = original_argv
                
        else:
            # Fallback to subprocess method
            cmd = ['xwaykeyz', '-w', '-c', config_file]
            print(f"Starting: {' '.join(cmd)}")
            
            # Run xwaykeyz and wait for it to complete
            process = subprocess.Popen(cmd)
            
            def signal_handler(signum, frame):
                print(f"Received signal {signum}, shutting down...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                sys.exit(0)
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGTERM, signal_handler)
            signal.signal(signal.SIGINT, signal_handler)
            
            # Wait for the process to complete
            return_code = process.wait()
            
            if return_code != 0:
                print(f"xwaykeyz exited with code {return_code}", file=sys.stderr)
                sys.exit(return_code)
            
    except KeyboardInterrupt:
        print("Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error running xwaykeyz: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
