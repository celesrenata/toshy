#!/usr/bin/env python3
"""
Toshy Debug Utilities

Comprehensive debugging and diagnostic tools for Toshy.
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from .platform_utils import get_platform_detector

class ToshyDebugger:
    """Comprehensive debugging and diagnostic tool"""
    
    def __init__(self):
        self.detector = get_platform_detector()
        self.results = {}
    
    def check_system_requirements(self) -> Dict[str, Any]:
        """Check system requirements and dependencies"""
        checks = {
            'python_version': {
                'required': '3.8+',
                'current': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'status': sys.version_info >= (3, 8),
            },
            'xwaykeyz': self._check_command('xwaykeyz', '--version'),
            'display_server': {
                'detected': self.detector.display_server,
                'status': self.detector.display_server is not None,
            },
            'input_devices': self._check_input_devices(),
            'permissions': self._check_permissions(),
        }
        
        return checks
    
    def _check_command(self, command: str, *args) -> Dict[str, Any]:
        """Check if a command is available and working"""
        try:
            result = subprocess.run([command] + list(args), 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=5)
            return {
                'available': True,
                'version': result.stdout.strip() if result.returncode == 0 else None,
                'status': result.returncode == 0,
                'error': result.stderr.strip() if result.stderr else None,
            }
        except FileNotFoundError:
            return {
                'available': False,
                'status': False,
                'error': f'{command} not found in PATH',
            }
        except subprocess.TimeoutExpired:
            return {
                'available': True,
                'status': False,
                'error': f'{command} timed out',
            }
    
    def _check_input_devices(self) -> Dict[str, Any]:
        """Check input device access"""
        input_devices = []
        device_dir = Path('/dev/input')
        
        if device_dir.exists():
            for device in device_dir.glob('event*'):
                try:
                    # Check if we can read the device
                    readable = os.access(device, os.R_OK)
                    input_devices.append({
                        'device': str(device),
                        'readable': readable,
                    })
                except Exception as e:
                    input_devices.append({
                        'device': str(device),
                        'readable': False,
                        'error': str(e),
                    })
        
        return {
            'devices_found': len(input_devices),
            'devices': input_devices,
            'status': len([d for d in input_devices if d.get('readable', False)]) > 0,
        }
    
    def _check_permissions(self) -> Dict[str, Any]:
        """Check user permissions and group membership"""
        import grp
        import pwd
        
        try:
            user = pwd.getpwuid(os.getuid())
            groups = [grp.getgrgid(gid).gr_name for gid in os.getgroups()]
            
            return {
                'user': user.pw_name,
                'uid': user.pw_uid,
                'groups': groups,
                'in_input_group': 'input' in groups,
                'status': 'input' in groups,
            }
        except Exception as e:
            return {
                'status': False,
                'error': str(e),
            }
    
    def check_configuration(self) -> Dict[str, Any]:
        """Check Toshy configuration"""
        from .daemon import find_config_file
        from .config import validate_config
        
        config_file = find_config_file()
        
        if not config_file:
            return {
                'config_file': None,
                'status': False,
                'error': 'No configuration file found',
            }
        
        config_info = {
            'config_file': config_file,
            'exists': os.path.exists(config_file),
            'readable': os.access(config_file, os.R_OK),
            'size': os.path.getsize(config_file) if os.path.exists(config_file) else 0,
        }
        
        if config_info['readable']:
            config_info['valid'] = validate_config(config_file)
            config_info['status'] = config_info['valid']
        else:
            config_info['status'] = False
            config_info['error'] = 'Configuration file not readable'
        
        return config_info
    
    def check_services(self) -> Dict[str, Any]:
        """Check systemd services status"""
        services = ['toshy', 'toshy-gui', 'toshy-tray']
        service_status = {}
        
        for service in services:
            try:
                result = subprocess.run([
                    'systemctl', '--user', 'is-active', service
                ], capture_output=True, text=True, timeout=5)
                
                service_status[service] = {
                    'active': result.returncode == 0,
                    'status': result.stdout.strip(),
                }
                
                # Get more detailed status
                result = subprocess.run([
                    'systemctl', '--user', 'status', service, '--no-pager', '-l'
                ], capture_output=True, text=True, timeout=5)
                
                service_status[service]['details'] = result.stdout
                
            except (subprocess.TimeoutExpired, FileNotFoundError):
                service_status[service] = {
                    'active': False,
                    'status': 'unknown',
                    'error': 'systemctl not available or timed out',
                }
        
        return service_status
    
    def check_environment(self) -> Dict[str, Any]:
        """Check environment variables and settings"""
        important_vars = [
            'DISPLAY', 'WAYLAND_DISPLAY', 'XDG_SESSION_TYPE',
            'XDG_CURRENT_DESKTOP', 'DESKTOP_SESSION',
            'XDG_RUNTIME_DIR', 'HOME', 'USER',
            'TOSHY_CONFIG_DIR', 'TOSHY_LOG_LEVEL',
        ]
        
        env_info = {}
        for var in important_vars:
            env_info[var] = os.environ.get(var)
        
        return {
            'variables': env_info,
            'platform_info': self.detector.get_platform_info(),
        }
    
    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all diagnostic checks"""
        print("Running comprehensive Toshy diagnostics...")
        
        results = {
            'timestamp': time.time(),
            'system_requirements': self.check_system_requirements(),
            'configuration': self.check_configuration(),
            'services': self.check_services(),
            'environment': self.check_environment(),
        }
        
        # Overall status
        results['overall_status'] = all([
            results['system_requirements'].get('python_version', {}).get('status', False),
            results['system_requirements'].get('xwaykeyz', {}).get('status', False),
            results['system_requirements'].get('display_server', {}).get('status', False),
            results['system_requirements'].get('permissions', {}).get('status', False),
            results['configuration'].get('status', False),
        ])
        
        return results
    
    def print_diagnostic_report(self, results: Dict[str, Any]):
        """Print a formatted diagnostic report"""
        print("\n" + "=" * 60)
        print("TOSHY DIAGNOSTIC REPORT")
        print("=" * 60)
        
        # Overall status
        status_icon = "✅" if results['overall_status'] else "❌"
        print(f"\nOverall Status: {status_icon}")
        
        # System requirements
        print("\n📋 SYSTEM REQUIREMENTS")
        print("-" * 30)
        reqs = results['system_requirements']
        
        for check, info in reqs.items():
            if isinstance(info, dict):
                status_icon = "✅" if info.get('status', False) else "❌"
                print(f"{status_icon} {check.replace('_', ' ').title()}")
                
                if 'current' in info:
                    print(f"   Current: {info['current']}")
                if 'error' in info:
                    print(f"   Error: {info['error']}")
        
        # Configuration
        print("\n⚙️  CONFIGURATION")
        print("-" * 30)
        config = results['configuration']
        status_icon = "✅" if config.get('status', False) else "❌"
        print(f"{status_icon} Configuration Status")
        
        if config.get('config_file'):
            print(f"   File: {config['config_file']}")
            print(f"   Size: {config.get('size', 0)} bytes")
        
        if config.get('error'):
            print(f"   Error: {config['error']}")
        
        # Services
        print("\n🔧 SERVICES")
        print("-" * 30)
        services = results['services']
        
        for service, info in services.items():
            status_icon = "✅" if info.get('active', False) else "❌"
            print(f"{status_icon} {service}: {info.get('status', 'unknown')}")
        
        # Environment
        print("\n🌍 ENVIRONMENT")
        print("-" * 30)
        env = results['environment']
        platform = env['platform_info']
        
        print(f"Architecture: {platform['architecture']}")
        print(f"Display Server: {platform['display_server']}")
        print(f"Desktop Environment: {platform['desktop_environment']}")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 30)
        
        if not results['overall_status']:
            print("❌ Issues detected. Please address the following:")
            
            if not reqs.get('xwaykeyz', {}).get('status', False):
                print("   • Install xwaykeyz package")
            
            if not reqs.get('permissions', {}).get('status', False):
                print("   • Add user to 'input' group: sudo usermod -a -G input $USER")
            
            if not config.get('status', False):
                print("   • Fix configuration file issues")
                print("   • Run: toshy-config --install")
        else:
            print("✅ All checks passed! Toshy should be working correctly.")
        
        print("\n" + "=" * 60)

def main():
    """Main entry point for debug utility"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Toshy debugging and diagnostic tool"
    )
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--output', type=str,
                       help='Save results to file')
    
    args = parser.parse_args()
    
    debugger = ToshyDebugger()
    results = debugger.run_comprehensive_check()
    
    if args.json:
        output = json.dumps(results, indent=2, default=str)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results saved to {args.output}")
        else:
            print(output)
    else:
        debugger.print_diagnostic_report(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nDetailed results saved to {args.output}")

if __name__ == "__main__":
    main()
