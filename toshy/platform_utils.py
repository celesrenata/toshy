#!/usr/bin/env python3
"""
Platform utilities for Toshy

Provides platform detection and optimization capabilities.
"""

import os
import sys
import platform
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

class PlatformDetector:
    """Detect and provide information about the current platform"""
    
    def __init__(self):
        self._cache = {}
    
    @property
    def architecture(self) -> str:
        """Get the system architecture"""
        if 'architecture' not in self._cache:
            arch = platform.machine().lower()
            # Normalize architecture names
            arch_map = {
                'x86_64': 'x86_64',
                'amd64': 'x86_64',
                'aarch64': 'aarch64',
                'arm64': 'aarch64',
                'armv7l': 'armv7',
                'armv6l': 'armv6',
            }
            self._cache['architecture'] = arch_map.get(arch, arch)
        return self._cache['architecture']
    
    @property
    def is_x86_64(self) -> bool:
        """Check if running on x86_64 architecture"""
        return self.architecture == 'x86_64'
    
    @property
    def is_aarch64(self) -> bool:
        """Check if running on aarch64 architecture"""
        return self.architecture == 'aarch64'
    
    @property
    def is_arm(self) -> bool:
        """Check if running on any ARM architecture"""
        return self.architecture.startswith('arm') or self.architecture == 'aarch64'
    
    @property
    def display_server(self) -> Optional[str]:
        """Detect the current display server"""
        if 'display_server' not in self._cache:
            display_server = None
            
            # Check for Wayland
            if os.environ.get('WAYLAND_DISPLAY'):
                display_server = 'wayland'
            elif os.environ.get('XDG_SESSION_TYPE') == 'wayland':
                display_server = 'wayland'
            # Check for X11
            elif os.environ.get('DISPLAY'):
                display_server = 'x11'
            elif os.environ.get('XDG_SESSION_TYPE') == 'x11':
                display_server = 'x11'
            
            self._cache['display_server'] = display_server
        return self._cache['display_server']
    
    @property
    def desktop_environment(self) -> Optional[str]:
        """Detect the current desktop environment"""
        if 'desktop_environment' not in self._cache:
            de = None
            
            # Check common environment variables
            de_vars = [
                ('GNOME_DESKTOP_SESSION_ID', 'gnome'),
                ('KDE_FULL_SESSION', 'kde'),
                ('DESKTOP_SESSION', None),  # Use value directly
                ('XDG_CURRENT_DESKTOP', None),  # Use value directly
            ]
            
            for var, value in de_vars:
                env_value = os.environ.get(var, '').lower()
                if env_value:
                    if value:
                        de = value
                        break
                    else:
                        # Use the environment variable value directly
                        de = env_value
                        break
            
            self._cache['desktop_environment'] = de
        return self._cache['desktop_environment']
    
    @property
    def wayland_compositor(self) -> Optional[str]:
        """Detect the Wayland compositor if running on Wayland"""
        if 'wayland_compositor' not in self._cache:
            compositor = None
            
            if self.display_server == 'wayland':
                # Check for specific compositors
                if os.environ.get('HYPRLAND_INSTANCE_SIGNATURE'):
                    compositor = 'hyprland'
                elif os.environ.get('SWAYSOCK'):
                    compositor = 'sway'
                elif self.desktop_environment == 'gnome':
                    compositor = 'mutter'
                elif self.desktop_environment == 'kde':
                    compositor = 'kwin'
                else:
                    # Try to detect from process list
                    try:
                        result = subprocess.run(['pgrep', '-f', 'hyprland|sway|mutter|kwin'], 
                                              capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            processes = result.stdout.strip().split('\n')
                            for proc in processes:
                                if 'hyprland' in proc:
                                    compositor = 'hyprland'
                                    break
                                elif 'sway' in proc:
                                    compositor = 'sway'
                                    break
                                elif 'mutter' in proc:
                                    compositor = 'mutter'
                                    break
                                elif 'kwin' in proc:
                                    compositor = 'kwin'
                                    break
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        pass
            
            self._cache['wayland_compositor'] = compositor
        return self._cache['wayland_compositor']
    
    def get_optimization_flags(self) -> List[str]:
        """Get platform-specific optimization flags"""
        flags = []
        
        if self.is_x86_64:
            # x86_64 optimizations
            flags.extend([
                '-march=x86-64',
                '-mtune=generic',
                '-O2',
            ])
        elif self.is_aarch64:
            # ARM64 optimizations
            flags.extend([
                '-march=armv8-a',
                '-mtune=generic',
                '-O2',
            ])
        elif self.architecture.startswith('armv7'):
            # ARMv7 optimizations
            flags.extend([
                '-march=armv7-a',
                '-mfpu=neon',
                '-O2',
            ])
        
        return flags
    
    def get_supported_features(self) -> Dict[str, bool]:
        """Get platform-specific feature support"""
        features = {
            'x11': True,
            'wayland': True,
            'input_devices': True,
            'system_tray': True,
            'notifications': True,
        }
        
        # ARM-specific limitations
        if self.is_arm and not self.is_aarch64:
            # Older ARM devices might have limitations
            features.update({
                'advanced_graphics': False,
                'hardware_acceleration': False,
            })
        
        return features
    
    def get_recommended_settings(self) -> Dict[str, any]:
        """Get platform-specific recommended settings"""
        settings = {
            'memory_limit': '256M',
            'cpu_priority': 0,
            'enable_optimizations': True,
        }
        
        if self.is_aarch64:
            # More conservative settings for ARM
            settings.update({
                'memory_limit': '128M',
                'cpu_priority': 5,  # Lower priority
                'enable_optimizations': False,
            })
        elif self.architecture.startswith('armv'):
            # Even more conservative for older ARM
            settings.update({
                'memory_limit': '64M',
                'cpu_priority': 10,
                'enable_optimizations': False,
            })
        
        return settings
    
    def get_platform_info(self) -> Dict[str, any]:
        """Get comprehensive platform information"""
        return {
            'architecture': self.architecture,
            'is_x86_64': self.is_x86_64,
            'is_aarch64': self.is_aarch64,
            'is_arm': self.is_arm,
            'display_server': self.display_server,
            'desktop_environment': self.desktop_environment,
            'wayland_compositor': self.wayland_compositor,
            'optimization_flags': self.get_optimization_flags(),
            'supported_features': self.get_supported_features(),
            'recommended_settings': self.get_recommended_settings(),
        }

def get_platform_detector() -> PlatformDetector:
    """Get a platform detector instance"""
    return PlatformDetector()

def main():
    """Main entry point for platform detection utility"""
    detector = PlatformDetector()
    info = detector.get_platform_info()
    
    print("Toshy Platform Information:")
    print("=" * 40)
    print(f"Architecture: {info['architecture']}")
    print(f"Display Server: {info['display_server']}")
    print(f"Desktop Environment: {info['desktop_environment']}")
    print(f"Wayland Compositor: {info['wayland_compositor']}")
    print()
    print("Supported Features:")
    for feature, supported in info['supported_features'].items():
        status = "✓" if supported else "✗"
        print(f"  {status} {feature}")
    print()
    print("Recommended Settings:")
    for setting, value in info['recommended_settings'].items():
        print(f"  {setting}: {value}")

if __name__ == "__main__":
    main()
