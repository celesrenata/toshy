#!/usr/bin/env python3
"""
Toshy Tray GTK3 Fixed - Improved GTK3 system tray with better error handling
"""

import os
import sys
import threading
import subprocess
from pathlib import Path

# Set up GTK3 environment before imports
os.environ['GTK_A11Y'] = 'none'
os.environ['NO_AT_BRIDGE'] = '1'

# GTK3 imports with better error handling
import gi
gi.require_version('Gtk', '3.0')

try:
    # Try AyatanaAppIndicator3 first (more modern)
    gi.require_version('AyatanaAppIndicator3', '0.1')
    from gi.repository import AyatanaAppIndicator3 as AppIndicator3
    INDICATOR_AVAILABLE = True
except (ValueError, ImportError):
    try:
        # Fallback to AppIndicator3
        gi.require_version('AppIndicator3', '0.1')
        from gi.repository import AppIndicator3
        INDICATOR_AVAILABLE = True
    except (ValueError, ImportError):
        # No AppIndicator available - use StatusIcon fallback
        INDICATOR_AVAILABLE = False

from gi.repository import Gtk, GLib, GdkPixbuf

# Initialize Toshy runtime
from toshy.common.runtime_utils import initialize_toshy_runtime
runtime = initialize_toshy_runtime()

# Local imports
from toshy.common import logger
from toshy.common.logger import debug, info, warn, error
from toshy.common.settings_class import Settings
from toshy.common.service_manager import ServiceManager


class ToshyTrayGTK3Fixed:
    """Improved GTK3 system tray for Toshy with better error handling"""
    
    def __init__(self):
        self.indicator = None
        self.status_icon = None
        self.menu = None
        self.settings = None
        self.service_manager = None
        self.setup_settings()
        self.setup_services()
        
    def setup_settings(self):
        """Initialize settings"""
        try:
            config_dir_path = runtime.config_dir
            self.settings = Settings(config_dir_path)
            self.settings.watch_database()
            debug("GTK3 Tray: Settings initialized")
        except Exception as e:
            error(f"GTK3 Tray: Failed to initialize settings: {e}")
            
    def setup_services(self):
        """Initialize service manager"""
        try:
            self.service_manager = ServiceManager()
            debug("GTK3 Tray: Service manager initialized")
        except Exception as e:
            error(f"GTK3 Tray: Failed to initialize service manager: {e}")
    
    def create_menu(self):
        """Create the tray menu"""
        menu = Gtk.Menu()
        
        # Toshy Preferences
        prefs_item = Gtk.MenuItem(label="Toshy Preferences")
        prefs_item.connect("activate", self.show_preferences)
        menu.append(prefs_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Start/Stop Services
        start_item = Gtk.MenuItem(label="Start Services")
        start_item.connect("activate", self.start_services)
        menu.append(start_item)
        
        stop_item = Gtk.MenuItem(label="Stop Services")
        stop_item.connect("activate", self.stop_services)
        menu.append(stop_item)
        
        # Separator
        menu.append(Gtk.SeparatorMenuItem())
        
        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit_tray)
        menu.append(quit_item)
        
        menu.show_all()
        return menu
    
    def create_tray_icon(self):
        """Create system tray icon"""
        try:
            self.menu = self.create_menu()
            
            if INDICATOR_AVAILABLE:
                # Use AppIndicator if available
                self.indicator = AppIndicator3.Indicator.new(
                    "toshy-tray",
                    "toshy_app_icon_rainbow",
                    AppIndicator3.IndicatorCategory.APPLICATION_STATUS
                )
                self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
                self.indicator.set_menu(self.menu)
                debug("GTK3 Tray: AppIndicator created")
            else:
                # Fallback to StatusIcon
                self.status_icon = Gtk.StatusIcon()
                self.status_icon.set_from_icon_name("toshy_app_icon_rainbow")
                self.status_icon.set_tooltip_text("Toshy Keybinding Service")
                self.status_icon.connect("popup-menu", self.on_status_icon_popup)
                self.status_icon.set_visible(True)
                debug("GTK3 Tray: StatusIcon created")
                
        except Exception as e:
            error(f"GTK3 Tray: Failed to create tray icon: {e}")
            raise
    
    def on_status_icon_popup(self, icon, button, time):
        """Handle StatusIcon popup menu"""
        if self.menu:
            self.menu.popup(None, None, None, None, button, time)
    
    def show_preferences(self, widget):
        """Show Toshy preferences"""
        try:
            subprocess.Popen(["toshy-gui"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            error(f"GTK3 Tray: Failed to show preferences: {e}")
    
    def start_services(self, widget):
        """Start Toshy services"""
        try:
            if self.service_manager:
                self.service_manager.restart_services()
        except Exception as e:
            error(f"GTK3 Tray: Failed to start services: {e}")
    
    def stop_services(self, widget):
        """Stop Toshy services"""
        try:
            if self.service_manager:
                self.service_manager.stop_services()
        except Exception as e:
            error(f"GTK3 Tray: Failed to stop services: {e}")
    
    def quit_tray(self, widget):
        """Quit the tray application"""
        debug("GTK3 Tray: Quitting...")
        Gtk.main_quit()
    
    def run(self):
        """Run the tray application"""
        try:
            debug("GTK3 Tray: Starting...")
            
            # Create tray icon
            self.create_tray_icon()
            
            # Send startup notification
            self.send_notification("Toshy Tray", "System tray started")
            
            # Run GTK main loop
            debug("GTK3 Tray: Starting main loop...")
            Gtk.main()
            
            return 0
            
        except Exception as e:
            error(f"GTK3 Tray: Failed to run: {e}")
            return 1
    
    def send_notification(self, title, message):
        """Send desktop notification"""
        try:
            subprocess.run([
                "notify-send", 
                "--app-name=Toshy",
                "--icon=toshy_app_icon_rainbow",
                title, 
                message
            ], check=False)
        except Exception as e:
            debug(f"GTK3 Tray: Notification failed: {e}")


def main():
    """Main entry point for GTK3 tray"""
    try:
        debug("Starting Toshy GTK3 Fixed Tray...")
        
        # Create and run tray
        tray = ToshyTrayGTK3Fixed()
        return tray.run()
        
    except KeyboardInterrupt:
        info("GTK3 Tray: Interrupted by user")
        return 0
    except Exception as e:
        error(f"GTK3 Tray: Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
