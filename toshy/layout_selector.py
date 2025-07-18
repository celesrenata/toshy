#!/usr/bin/env python3
"""
Toshy GUI - Layout selector and configuration interface
"""

import sys

def main():
    """Main entry point for toshy-gui command"""
    try:
        # Import the layout selector module
        import toshy_layout_selector
        
        # Execute the main logic from the original script
        cnxn, cur = toshy_layout_selector.setup_layout_database()
        toshy_layout_selector.parse_xkb_layouts_and_variants_from_xml(cnxn, cur)
        app = toshy_layout_selector.LayoutSelector(cnxn, cur)
        app.mainloop()
        
    except ImportError as e:
        print(f"Error importing toshy_layout_selector: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error running toshy GUI: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
