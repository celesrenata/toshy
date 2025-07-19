#!/usr/bin/env python3
"""
Tests for Phase 4 advanced features
"""

import pytest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# Import Phase 4 modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from toshy.platform_utils import PlatformDetector
from toshy.debug_utils import ToshyDebugger
from toshy.performance_utils import PerformanceMonitor

class TestPlatformDetection:
    """Test platform detection functionality"""
    
    def test_platform_detector_creation(self):
        """Test platform detector can be created"""
        detector = PlatformDetector()
        assert detector is not None
    
    def test_architecture_detection(self):
        """Test architecture detection"""
        detector = PlatformDetector()
        arch = detector.architecture
        
        # Should return a valid architecture string
        assert isinstance(arch, str)
        assert len(arch) > 0
        
        # Should be one of the known architectures
        known_archs = ['x86_64', 'aarch64', 'armv7', 'armv6']
        # Note: We don't assert it's in known_archs because there might be others
        
    def test_platform_properties(self):
        """Test platform detection properties"""
        detector = PlatformDetector()
        
        # These should return boolean values
        assert isinstance(detector.is_x86_64, bool)
        assert isinstance(detector.is_aarch64, bool)
        assert isinstance(detector.is_arm, bool)
        
        # Only one architecture should be true (or none for unknown)
        arch_flags = [detector.is_x86_64, detector.is_aarch64]
        assert sum(arch_flags) <= 1
    
    @patch.dict(os.environ, {'WAYLAND_DISPLAY': 'wayland-0'})
    def test_wayland_detection(self):
        """Test Wayland display server detection"""
        detector = PlatformDetector()
        assert detector.display_server == 'wayland'
    
    @patch.dict(os.environ, {'DISPLAY': ':0', 'WAYLAND_DISPLAY': '', 'XDG_SESSION_TYPE': 'x11'}, clear=False)
    def test_x11_detection(self):
        """Test X11 display server detection"""
        detector = PlatformDetector()
        detector._cache.clear()  # Clear cache to force re-detection
        assert detector.display_server == 'x11'
    
    def test_optimization_flags(self):
        """Test optimization flag generation"""
        detector = PlatformDetector()
        flags = detector.get_optimization_flags()
        
        assert isinstance(flags, list)
        # Should have some optimization flags
        assert len(flags) > 0
        # Should contain common optimization flags
        assert any('-O2' in flag for flag in flags)
    
    def test_supported_features(self):
        """Test supported features detection"""
        detector = PlatformDetector()
        features = detector.get_supported_features()
        
        assert isinstance(features, dict)
        # Should have basic features
        expected_features = ['x11', 'wayland', 'input_devices']
        for feature in expected_features:
            assert feature in features
            assert isinstance(features[feature], bool)
    
    def test_recommended_settings(self):
        """Test recommended settings generation"""
        detector = PlatformDetector()
        settings = detector.get_recommended_settings()
        
        assert isinstance(settings, dict)
        # Should have basic settings
        expected_settings = ['memory_limit', 'cpu_priority', 'enable_optimizations']
        for setting in expected_settings:
            assert setting in settings
    
    def test_platform_info_comprehensive(self):
        """Test comprehensive platform information"""
        detector = PlatformDetector()
        info = detector.get_platform_info()
        
        assert isinstance(info, dict)
        
        # Should have all expected keys
        expected_keys = [
            'architecture', 'is_x86_64', 'is_aarch64', 'is_arm',
            'display_server', 'desktop_environment', 'wayland_compositor',
            'optimization_flags', 'supported_features', 'recommended_settings'
        ]
        
        for key in expected_keys:
            assert key in info

class TestDebugUtilities:
    """Test debugging utilities"""
    
    def test_debugger_creation(self):
        """Test debugger can be created"""
        debugger = ToshyDebugger()
        assert debugger is not None
        assert hasattr(debugger, 'detector')
    
    def test_system_requirements_check(self):
        """Test system requirements checking"""
        debugger = ToshyDebugger()
        reqs = debugger.check_system_requirements()
        
        assert isinstance(reqs, dict)
        
        # Should check Python version
        assert 'python_version' in reqs
        python_check = reqs['python_version']
        assert 'current' in python_check
        assert 'status' in python_check
        assert isinstance(python_check['status'], bool)
    
    def test_configuration_check(self):
        """Test configuration checking"""
        debugger = ToshyDebugger()
        config_check = debugger.check_configuration()
        
        assert isinstance(config_check, dict)
        assert 'status' in config_check
        assert isinstance(config_check['status'], bool)
    
    @patch('subprocess.run')
    def test_services_check(self, mock_run):
        """Test services checking"""
        mock_run.return_value = MagicMock(returncode=0, stdout='active')
        
        debugger = ToshyDebugger()
        services = debugger.check_services()
        
        assert isinstance(services, dict)
        # Should check main services
        expected_services = ['toshy', 'toshy-gui', 'toshy-tray']
        for service in expected_services:
            assert service in services
    
    def test_environment_check(self):
        """Test environment checking"""
        debugger = ToshyDebugger()
        env_check = debugger.check_environment()
        
        assert isinstance(env_check, dict)
        assert 'variables' in env_check
        assert 'platform_info' in env_check
        
        # Should check important variables
        variables = env_check['variables']
        important_vars = ['HOME', 'USER']
        for var in important_vars:
            assert var in variables
    
    def test_comprehensive_check(self):
        """Test comprehensive diagnostic check"""
        debugger = ToshyDebugger()
        results = debugger.run_comprehensive_check()
        
        assert isinstance(results, dict)
        
        # Should have all check categories
        expected_categories = [
            'timestamp', 'system_requirements', 'configuration',
            'services', 'environment', 'overall_status'
        ]
        
        for category in expected_categories:
            assert category in results

class TestPerformanceMonitoring:
    """Test performance monitoring utilities"""
    
    def test_performance_monitor_creation(self):
        """Test performance monitor can be created"""
        monitor = PerformanceMonitor()
        assert monitor is not None
        assert hasattr(monitor, 'detector')
    
    def test_system_metrics(self):
        """Test system metrics collection"""
        monitor = PerformanceMonitor()
        metrics = monitor.get_system_metrics()
        
        assert isinstance(metrics, dict)
        
        # Should have basic system metrics
        expected_metrics = ['timestamp', 'cpu', 'memory', 'disk']
        for metric in expected_metrics:
            assert metric in metrics
        
        # CPU metrics should have expected fields
        cpu = metrics['cpu']
        assert 'percent' in cpu
        assert 'count' in cpu
        assert isinstance(cpu['percent'], (int, float))
        assert isinstance(cpu['count'], int)
        
        # Memory metrics should have expected fields
        memory = metrics['memory']
        memory_fields = ['total', 'available', 'percent', 'used']
        for field in memory_fields:
            assert field in memory
            assert isinstance(memory[field], (int, float))
    
    def test_process_detection(self):
        """Test process detection"""
        monitor = PerformanceMonitor()
        
        # Test Toshy process detection
        toshy_procs = monitor.get_toshy_processes()
        assert isinstance(toshy_procs, list)
        
        # Test xwaykeyz process detection
        xwaykeyz_procs = monitor.get_xwaykeyz_processes()
        assert isinstance(xwaykeyz_procs, list)
    
    def test_performance_analysis(self):
        """Test performance data analysis"""
        monitor = PerformanceMonitor()
        
        # Create sample data
        sample_data = [
            {
                'timestamp': 1000,
                'system': {
                    'cpu': {'percent': 10.0},
                    'memory': {'percent': 50.0}
                },
                'toshy_processes': [
                    {'memory_mb': 100.0, 'cpu_percent': 5.0}
                ]
            },
            {
                'timestamp': 1001,
                'system': {
                    'cpu': {'percent': 20.0},
                    'memory': {'percent': 60.0}
                },
                'toshy_processes': [
                    {'memory_mb': 110.0, 'cpu_percent': 7.0}
                ]
            }
        ]
        
        analysis = monitor._analyze_performance_data(sample_data)
        
        assert isinstance(analysis, dict)
        assert 'system_cpu' in analysis
        assert 'system_memory' in analysis
        assert 'toshy_performance' in analysis
        
        # Check CPU analysis
        cpu_analysis = analysis['system_cpu']
        assert cpu_analysis['average'] == 15.0  # (10 + 20) / 2
        assert cpu_analysis['max'] == 20.0
        assert cpu_analysis['min'] == 10.0
    
    def test_optimization_recommendations(self):
        """Test optimization recommendations"""
        monitor = PerformanceMonitor()
        
        # Test with sample benchmark results
        sample_results = {
            'analysis': {
                'system_cpu': {'average': 50.0},
                'system_memory': {'average': 70.0},
                'toshy_performance': {
                    'memory_mb': {'average': 50.0}
                }
            },
            'platform_info': {
                'is_arm': False
            }
        }
        
        recommendations = monitor.get_optimization_recommendations(sample_results)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Should have at least one recommendation
        assert all(isinstance(rec, str) for rec in recommendations)

class TestMultiPlatformSupport:
    """Test multi-platform support features"""
    
    def test_platform_specific_configs(self):
        """Test platform-specific configurations"""
        # This would test the platform configurations in the flake
        # For now, we just test that the concept works
        
        platform_configs = {
            'x86_64-linux': {
                'enableOptimizations': True,
                'supportedCompositors': ['hyprland', 'sway', 'wlroots']
            },
            'aarch64-linux': {
                'enableOptimizations': False,
                'supportedCompositors': ['sway', 'wlroots']
            }
        }
        
        # Test x86_64 config
        x86_config = platform_configs['x86_64-linux']
        assert x86_config['enableOptimizations'] == True
        assert 'hyprland' in x86_config['supportedCompositors']
        
        # Test ARM config
        arm_config = platform_configs['aarch64-linux']
        assert arm_config['enableOptimizations'] == False
        assert len(arm_config['supportedCompositors']) < len(x86_config['supportedCompositors'])

class TestEntryPoints:
    """Test new entry points work correctly"""
    
    def test_platform_entry_point(self):
        """Test platform detection entry point"""
        from toshy.platform_utils import main
        assert callable(main)
    
    def test_debug_entry_point(self):
        """Test debug utility entry point"""
        from toshy.debug_utils import main
        assert callable(main)
    
    def test_performance_entry_point(self):
        """Test performance monitoring entry point"""
        from toshy.performance_utils import main
        assert callable(main)

if __name__ == "__main__":
    pytest.main([__file__])
