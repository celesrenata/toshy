__version__ = '20250714'

import os
import time
import subprocess
from subprocess import DEVNULL

from toshy_common.logger import debug, error
from toshy_common.notification_manager import NotificationManager


class ServiceManager:
    """
    Manages Toshy systemd services and config-only operations.
    
    Provides common service control functionality shared between 
    GUI and tray applications.
    """
    
    def __init__(self, notification_manager: NotificationManager=None, 
                    icon_active=None, icon_inactive=None, icon_grayscale=None):
        """
        Initialize service manager.
        
        Args:
            notification_manager: NotificationManager instance for sending notifications
            icon_active: Icon to use for "services started" notifications
            icon_inactive: Icon to use for "services stopped" notifications
            icon_grayscale: Icon to use for "services disabled/unknown" notifications
        """
        self.ntfy               = notification_manager
        self.icon_active        = icon_active
        self.icon_inactive      = icon_inactive
        self.icon_grayscale     = icon_grayscale
        
        # Set up paths
        self.home_dir = os.path.expanduser("~")
        self.home_local_bin = os.path.join(self.home_dir, '.local', 'bin')
        
        # Modern systemd commands instead of old shell scripts
        self.systemctl_cmd = "systemctl"
        
        # Service names
        self.toshy_services = ["toshy", "toshy-gui", "toshy-tray"]

    def restart_services(self):
        """
        (Re)Start Toshy services with systemd commands.
        
        Starts the main toshy daemon service.
        Shows notification if notification manager is available.
        """
        try:
            debug("Starting Toshy services with systemd...")
            
            # Restart the main toshy service
            result = subprocess.run([
                self.systemctl_cmd, "--user", "restart", "toshy"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                message = 'Toshy systemd service (re)started.'
                debug(message)
                if self.ntfy:
                    self.ntfy.send_notification(message, self.icon_active)
            else:
                raise subprocess.CalledProcessError(result.returncode, result.args, result.stderr)
                
        except Exception as e:
            message = f"Failed to start Toshy services: {e}"
            error(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_grayscale)

    def stop_services(self):
        """
        Stop Toshy services with systemd commands.
        
        Stops the main toshy daemon service.
        Shows notification if notification manager is available.
        """
        try:
            debug("Stopping Toshy services with systemd...")
            
            # Stop the main toshy service
            result = subprocess.run([
                self.systemctl_cmd, "--user", "stop", "toshy"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                message = 'Toshy systemd service stopped.'
                debug(message)
                if self.ntfy:
                    self.ntfy.send_notification(message, self.icon_grayscale)
            else:
                raise subprocess.CalledProcessError(result.returncode, result.args, result.stderr)
                
        except Exception as e:
            message = f"Failed to stop Toshy services: {e}"
            error(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_grayscale)
            
            message = 'Toshy systemd services stopped.'
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_inactive)
                
            debug(message)
            
        except Exception as e:
            message = (f"Failed to stop Toshy services: {e}")
            error(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_grayscale)

    def restart_config_only(self):
        """
        Start the config service only (manual run mode).
        
        This is used for testing or when running config independently
        of the full systemd service setup.
        """
        try:
            debug("Starting Toshy config only...")
            subprocess.Popen([self.toshy_cfg_restart_cmd], stdout=DEVNULL, stderr=DEVNULL)
            time.sleep(3)
            message = 'Toshy config-only process (re)started.'
            debug(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_active)
            
        except Exception as e:
            message = (f"Failed to start Toshy config-only: {e}")
            error(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_grayscale)

    def stop_config_only(self):
        """
        Stop the config service only (manual run mode).
        
        This stops the config service without affecting other services.
        """
        try:
            debug("Stopping Toshy config-only process...")
            subprocess.Popen([self.toshy_cfg_stop_cmd], stdout=DEVNULL, stderr=DEVNULL)
            time.sleep(1)
            message = 'Toshy config-only process stopped.'
            debug(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_inactive)
            
        except Exception as e:
            message = (f"Failed to stop Toshy config-only: {e}")
            error(message)
            if self.ntfy:
                self.ntfy.send_notification(message, self.icon_grayscale)

    def enable_services(self):
        """
        Enable all Toshy systemd services for autostart at login.
        
        Enables services in the correct order:
        1. Session monitor
        2. D-Bus services (e.g., COSMIC, KWin, Wlroots)
        3. Config service (last, as it depends on others)
        
        Raises:
            subprocess.CalledProcessError: If any systemctl command fails
        """
        # Service names (should match the tray app's service variables)
        services_to_enable = [
            'toshy-session-monitor.service',
            'toshy-cosmic-dbus.service', 
            'toshy-kwin-dbus.service',
            'toshy-wlroots-dbus.service',
            'toshy-config.service',  # Last, as it may depend on others
        ]
        
        enable_cmd_base = ["systemctl", "--user", "enable"]
        
        for service in services_to_enable:
            try:
                debug(f"Enabling service: {service}")
                subprocess.run(enable_cmd_base + [service], check=True)
            except subprocess.CalledProcessError as e:
                error(f"Failed to enable service {service}: {e}")
                raise  # Re-raise to let caller handle the error
                
        time.sleep(1)
        message = "Toshy services ENABLED. Will autostart at login."
        debug(message)
        if self.ntfy:
            self.ntfy.send_notification(message, self.icon_active)

    def disable_services(self):
        """
        Disable all Toshy systemd services from autostart at login.
        
        Disables services in reverse order (config first, then dependencies):
        1. Config service (first, as others support it)
        2. D-Bus services (e.g., COSMIC, KWin, Wlroots)
        3. Session monitor (last)
        
        Raises:
            subprocess.CalledProcessError: If any systemctl command fails
        """
        # Service names in reverse order for clean shutdown
        services_to_disable = [
            'toshy-config.service',  # First, as others support it
            'toshy-cosmic-dbus.service',
            'toshy-kwin-dbus.service', 
            'toshy-wlroots-dbus.service',
            'toshy-session-monitor.service',  # Last
        ]
        
        disable_cmd_base = ["systemctl", "--user", "disable"]
        
        for service in services_to_disable:
            try:
                debug(f"Disabling service: {service}")
                subprocess.run(disable_cmd_base + [service], check=True)
            except subprocess.CalledProcessError as e:
                error(f"Failed to disable service {service}: {e}")
                raise  # Re-raise to let caller handle the error
                
        time.sleep(1)
        message = "Toshy systemd services DISABLED. Will not autostart."
        debug(message)
        if self.ntfy:
            self.ntfy.send_notification(message, self.icon_inactive)

    def check_commands_exist(self):
        """
        Check if systemctl command exists.
        
        Returns:
            dict: Status of systemctl command
        """
        commands = {
            'systemctl': shutil.which(self.systemctl_cmd) is not None,
        }
        
        status = {}
        for name, available in commands.items():
            status[name] = available
            if not status[name]:
                debug(f"Command not found: {name}")
                
        return status
