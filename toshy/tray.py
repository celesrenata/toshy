#!/usr/bin/env python3
"""
Toshy Tray - System tray application for Toshy keybinding service
"""

import sys

def main():
    """Main entry point for toshy-tray command"""
    try:
        # Import and run the original tray script
        import toshy_tray
        toshy_tray.main()
    except ImportError as e:
        print(f"Error importing toshy_tray: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running toshy tray: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
