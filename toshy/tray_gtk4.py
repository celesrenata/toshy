#!/usr/bin/env python3
"""
Toshy Tray GTK4 - Modern GTK4 system tray application for Toshy keybinding service
"""

import os
import sys
import threading
import subprocess
from pathlib import Path

# GTK4 imports
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio

# Initialize Toshy runtime
from toshy.common.runtime_utils import initialize_toshy_runtime
runtime = initialize_toshy_runtime()

# Local imports
from toshy.common import logger
from toshy.common.logger import debug, info, warn, error
from toshy.common.settings_class import Settings
from toshy.common.service_manager import ServiceManager


class ToshyTrayGTK4:
    """Modern GTK4 system tray for Toshy"""
    
    def __init__(self):
        self.app = None
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
            debug("GTK4 Tray: Settings initialized")
        except Exception as e:
            error(f"GTK4 Tray: Failed to initialize settings: {e}")
            
    def setup_services(self):
        """Initialize service manager"""
        try:
            self.service_manager = ServiceManager()
            debug("GTK4 Tray: Service manager initialized")
        except Exception as e:
            error(f"GTK4 Tray: Failed to initialize service manager: {e}")
    
    def create_application(self):
        """Create GTK4 application"""
        # Use a unique application ID and set it as a service
        self.app = Adw.Application(application_id="com.toshy.tray.gtk4")
        self.app.connect("activate", self.on_activate)
        
        # Set application flags for background service
        self.app.set_flags(Gio.ApplicationFlags.IS_SERVICE | Gio.ApplicationFlags.ALLOW_REPLACEMENT)
        
        return self.app
    
    def on_activate(self, app):
        """Application activation callback"""
        debug("GTK4 Tray: Application activated")
        
        # Create status icon (GTK4 approach)
        self.create_status_icon()
        
        # Start monitoring
        self.start_monitoring()
        
    def create_status_icon(self):
        """Create system tray status icon"""
        try:
            # GTK4 doesn't have traditional system tray, but we can create
            # a background service that shows notifications and can be
            # accessed via the GUI
            debug("GTK4 Tray: Status icon created (background service)")
            
            # Send notification that tray is running
            self.send_notification("Toshy Tray", "GTK4 tray service started")
            
        except Exception as e:
            error(f"GTK4 Tray: Failed to create status icon: {e}")
    
    def start_monitoring(self):
        """Start service monitoring"""
        try:
            # Monitor services in background thread
            def monitor_services():
                while True:
                    try:
                        # Check service status periodically
                        GLib.timeout_add_seconds(5, self.check_services)
                        threading.Event().wait(30)  # Check every 30 seconds
                    except Exception as e:
                        error(f"GTK4 Tray: Monitoring error: {e}")
                        
            monitor_thread = threading.Thread(target=monitor_services, daemon=True)
            monitor_thread.start()
            debug("GTK4 Tray: Service monitoring started")
            
        except Exception as e:
            error(f"GTK4 Tray: Failed to start monitoring: {e}")
    
    def check_services(self):
        """Check service status"""
        try:
            if self.service_manager:
                # This would check actual service status
                # For now, just log that we're monitoring
                debug("GTK4 Tray: Checking service status...")
                
        except Exception as e:
            error(f"GTK4 Tray: Service check failed: {e}")
            
        return True  # Continue periodic checks
    
    def send_notification(self, title, message):
        """Send desktop notification"""
        try:
            # Use notify-send for notifications
            subprocess.run([
                "notify-send", 
                "--app-name=Toshy",
                "--icon=toshy_app_icon_rainbow",
                title, 
                message
            ], check=False)
            
        except Exception as e:
            debug(f"GTK4 Tray: Notification failed: {e}")
    
    def run(self):
        """Run the tray application"""
        try:
            debug("GTK4 Tray: Starting application...")
            app = self.create_application()
            
            # Handle registration failure gracefully
            try:
                return app.run(sys.argv)
            except GLib.Error as e:
                if "Unable to acquire bus name" in str(e):
                    info("GTK4 Tray: Another instance may be running, exiting gracefully")
                    return 0
                else:
                    raise
            
        except Exception as e:
            error(f"GTK4 Tray: Failed to run: {e}")
            return 1


def main():
    """Main entry point for GTK4 tray"""
    try:
        debug("Starting Toshy GTK4 Tray...")
        
        # Initialize Adwaita
        Adw.init()
        
        # Create and run tray
        tray = ToshyTrayGTK4()
        return tray.run()
        
    except KeyboardInterrupt:
        info("GTK4 Tray: Interrupted by user")
        return 0
    except Exception as e:
        error(f"GTK4 Tray: Fatal error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
