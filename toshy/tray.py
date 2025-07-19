#!/usr/bin/env python3
"""
Toshy Tray - System tray application for Toshy keybinding service
"""

import sys

def main():
    """Main entry point for toshy-tray command"""
    # GTK4 doesn't support system trays, so we must use GTK3
    # Try our implementations in order of preference
    
    try:
        # First try: Our improved GTK3 tray
        from toshy.tray_gtk3_fixed import main as gtk3_main
        print("(DD) Using improved GTK3 tray implementation")
        return gtk3_main()
    except ImportError:
        print("(DD) Improved GTK3 tray not available, trying original...")
        pass
    
    try:
        # Second try: Original GTK3 tray
        import toshy_tray
        print("(DD) Using original GTK3 tray implementation")
        return toshy_tray.main()
    except ImportError:
        print("(EE) No GTK3 tray implementation available!", file=sys.stderr)
        pass
    
    # Last resort: Explain the situation
    print("(EE) ERROR: No system tray implementation available!", file=sys.stderr)
    print("(EE) GTK4 doesn't support system trays - GTK3 is required.", file=sys.stderr)
    print("(EE) Please ensure GTK3 and AppIndicator3 are installed.", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
