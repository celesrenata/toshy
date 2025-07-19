#!/usr/bin/env python3
"""
Toshy Tray - System tray application for Toshy keybinding service
"""

import sys

def main():
    """Main entry point for toshy-tray command"""
    try:
        # System tray requires GTK3 - GTK4 doesn't support system trays
        # Use our improved GTK3 tray implementation
        from toshy.tray_gtk3_fixed import main as gtk3_main
        return gtk3_main()
    except ImportError as e:
        print(f"Error importing improved GTK3 tray: {e}", file=sys.stderr)
        print("Falling back to original tray...", file=sys.stderr)
        try:
            # Fallback to original tray
            import toshy_tray
            toshy_tray.main()
        except ImportError as e2:
            print(f"Error importing toshy_tray: {e2}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error running GTK3 tray: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
