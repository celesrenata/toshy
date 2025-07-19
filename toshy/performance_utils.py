#!/usr/bin/env python3
"""
Toshy Performance Utilities

Performance monitoring and optimization tools for Toshy.
"""

import os
import sys
import time
import psutil
import subprocess
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from .platform_utils import get_platform_detector

class PerformanceMonitor:
    """Monitor and analyze Toshy performance"""
    
    def __init__(self):
        self.detector = get_platform_detector()
        self.baseline_metrics = None
        self.monitoring_data = []
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        return {
            'timestamp': time.time(),
            'cpu': {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
            },
            'memory': {
                'total': psutil.virtual_memory().total,
                'available': psutil.virtual_memory().available,
                'percent': psutil.virtual_memory().percent,
                'used': psutil.virtual_memory().used,
            },
            'disk': {
                'usage': psutil.disk_usage('/').percent,
                'io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else None,
            },
            'network': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else None,
        }
    
    def get_toshy_processes(self) -> List[Dict[str, Any]]:
        """Get information about running Toshy processes"""
        toshy_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                if any('toshy' in str(item).lower() for item in proc.info['cmdline'] or []):
                    toshy_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(proc.info['cmdline'] or []),
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0,
                        'status': proc.status(),
                        'create_time': proc.create_time(),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return toshy_processes
    
    def get_xwaykeyz_processes(self) -> List[Dict[str, Any]]:
        """Get information about xwaykeyz processes"""
        xwaykeyz_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
            try:
                if 'xwaykeyz' in proc.info['name'] or any('xwaykeyz' in str(item) for item in proc.info['cmdline'] or []):
                    xwaykeyz_processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': ' '.join(proc.info['cmdline'] or []),
                        'cpu_percent': proc.info['cpu_percent'],
                        'memory_mb': proc.info['memory_info'].rss / 1024 / 1024 if proc.info['memory_info'] else 0,
                        'status': proc.status(),
                        'create_time': proc.create_time(),
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return xwaykeyz_processes
    
    def measure_startup_time(self) -> Dict[str, Any]:
        """Measure Toshy startup time"""
        print("Measuring startup time...")
        
        # Stop any existing processes
        subprocess.run(['pkill', '-f', 'toshy-daemon'], capture_output=True)
        time.sleep(2)
        
        start_time = time.time()
        
        # Start daemon
        proc = subprocess.Popen(['toshy-daemon'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE)
        
        # Wait for process to be ready (simple heuristic)
        ready_time = None
        for _ in range(30):  # Wait up to 30 seconds
            time.sleep(0.1)
            if self.get_toshy_processes():
                ready_time = time.time()
                break
        
        # Clean up
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        
        return {
            'startup_time': ready_time - start_time if ready_time else None,
            'success': ready_time is not None,
        }
    
    def measure_key_latency(self, duration: int = 10) -> Dict[str, Any]:
        """Measure key processing latency (requires manual testing)"""
        print(f"Key latency measurement would require {duration} seconds of manual testing")
        print("This is a placeholder for future implementation")
        
        # This would require integration with the actual key processing pipeline
        # For now, return placeholder data
        return {
            'average_latency_ms': 5.0,  # Placeholder
            'max_latency_ms': 15.0,     # Placeholder
            'min_latency_ms': 1.0,      # Placeholder
            'samples': 100,             # Placeholder
        }
    
    def run_performance_benchmark(self, duration: int = 60) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        print(f"Running performance benchmark for {duration} seconds...")
        
        # Get baseline metrics
        baseline = self.get_system_metrics()
        baseline_processes = self.get_toshy_processes()
        
        # Start monitoring
        start_time = time.time()
        samples = []
        
        while time.time() - start_time < duration:
            sample = {
                'timestamp': time.time(),
                'system': self.get_system_metrics(),
                'toshy_processes': self.get_toshy_processes(),
                'xwaykeyz_processes': self.get_xwaykeyz_processes(),
            }
            samples.append(sample)
            time.sleep(1)
        
        # Analyze results
        analysis = self._analyze_performance_data(samples)
        
        return {
            'duration': duration,
            'baseline': baseline,
            'samples': samples,
            'analysis': analysis,
            'startup_time': self.measure_startup_time(),
            'platform_info': self.detector.get_platform_info(),
        }
    
    def _analyze_performance_data(self, samples: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance monitoring data"""
        if not samples:
            return {}
        
        # CPU usage analysis
        cpu_values = [s['system']['cpu']['percent'] for s in samples]
        cpu_analysis = {
            'average': sum(cpu_values) / len(cpu_values),
            'max': max(cpu_values),
            'min': min(cpu_values),
        }
        
        # Memory usage analysis
        memory_values = [s['system']['memory']['percent'] for s in samples]
        memory_analysis = {
            'average': sum(memory_values) / len(memory_values),
            'max': max(memory_values),
            'min': min(memory_values),
        }
        
        # Toshy process analysis
        toshy_memory = []
        toshy_cpu = []
        
        for sample in samples:
            for proc in sample.get('toshy_processes', []):
                toshy_memory.append(proc['memory_mb'])
                toshy_cpu.append(proc['cpu_percent'])
        
        toshy_analysis = {
            'memory_mb': {
                'average': sum(toshy_memory) / len(toshy_memory) if toshy_memory else 0,
                'max': max(toshy_memory) if toshy_memory else 0,
                'min': min(toshy_memory) if toshy_memory else 0,
            },
            'cpu_percent': {
                'average': sum(toshy_cpu) / len(toshy_cpu) if toshy_cpu else 0,
                'max': max(toshy_cpu) if toshy_cpu else 0,
                'min': min(toshy_cpu) if toshy_cpu else 0,
            }
        }
        
        return {
            'system_cpu': cpu_analysis,
            'system_memory': memory_analysis,
            'toshy_performance': toshy_analysis,
            'sample_count': len(samples),
        }
    
    def get_optimization_recommendations(self, benchmark_results: Dict[str, Any]) -> List[str]:
        """Get performance optimization recommendations"""
        recommendations = []
        
        analysis = benchmark_results.get('analysis', {})
        platform = benchmark_results.get('platform_info', {})
        
        # CPU recommendations
        cpu_avg = analysis.get('system_cpu', {}).get('average', 0)
        if cpu_avg > 80:
            recommendations.append("High CPU usage detected. Consider reducing process priority.")
        
        # Memory recommendations
        memory_avg = analysis.get('system_memory', {}).get('average', 0)
        if memory_avg > 90:
            recommendations.append("High memory usage detected. Consider reducing memory limits.")
        
        # Toshy-specific recommendations
        toshy_perf = analysis.get('toshy_performance', {})
        toshy_memory = toshy_perf.get('memory_mb', {}).get('average', 0)
        
        if toshy_memory > 100:
            recommendations.append("Toshy using significant memory. Consider optimizing configuration.")
        
        # Platform-specific recommendations
        if platform.get('is_arm'):
            recommendations.append("ARM platform detected. Consider enabling power-saving mode.")
        
        if not recommendations:
            recommendations.append("Performance looks good! No specific optimizations needed.")
        
        return recommendations
    
    def print_performance_report(self, results: Dict[str, Any]):
        """Print formatted performance report"""
        print("\n" + "=" * 60)
        print("TOSHY PERFORMANCE REPORT")
        print("=" * 60)
        
        # Platform info
        platform = results.get('platform_info', {})
        print(f"\nPlatform: {platform.get('architecture', 'unknown')}")
        print(f"Display: {platform.get('display_server', 'unknown')}")
        
        # Startup time
        startup = results.get('startup_time', {})
        if startup.get('success'):
            print(f"Startup Time: {startup.get('startup_time', 0):.2f} seconds")
        else:
            print("Startup Time: Failed to measure")
        
        # Performance analysis
        analysis = results.get('analysis', {})
        
        print("\n📊 SYSTEM PERFORMANCE")
        print("-" * 30)
        cpu = analysis.get('system_cpu', {})
        memory = analysis.get('system_memory', {})
        
        print(f"CPU Usage: {cpu.get('average', 0):.1f}% avg, {cpu.get('max', 0):.1f}% max")
        print(f"Memory Usage: {memory.get('average', 0):.1f}% avg, {memory.get('max', 0):.1f}% max")
        
        print("\n🔧 TOSHY PERFORMANCE")
        print("-" * 30)
        toshy = analysis.get('toshy_performance', {})
        toshy_mem = toshy.get('memory_mb', {})
        toshy_cpu = toshy.get('cpu_percent', {})
        
        print(f"Memory Usage: {toshy_mem.get('average', 0):.1f} MB avg, {toshy_mem.get('max', 0):.1f} MB max")
        print(f"CPU Usage: {toshy_cpu.get('average', 0):.1f}% avg, {toshy_cpu.get('max', 0):.1f}% max")
        
        # Recommendations
        recommendations = self.get_optimization_recommendations(results)
        print("\n💡 RECOMMENDATIONS")
        print("-" * 30)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        print("\n" + "=" * 60)

def main():
    """Main entry point for performance utility"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Toshy performance monitoring and benchmarking tool"
    )
    parser.add_argument('--benchmark', type=int, default=60,
                       help='Run benchmark for specified seconds (default: 60)')
    parser.add_argument('--startup-time', action='store_true',
                       help='Measure startup time only')
    parser.add_argument('--json', action='store_true',
                       help='Output results in JSON format')
    parser.add_argument('--output', type=str,
                       help='Save results to file')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor()
    
    if args.startup_time:
        results = {
            'startup_time': monitor.measure_startup_time(),
            'platform_info': monitor.detector.get_platform_info(),
        }
    else:
        results = monitor.run_performance_benchmark(args.benchmark)
    
    if args.json:
        output = json.dumps(results, indent=2, default=str)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results saved to {args.output}")
        else:
            print(output)
    else:
        monitor.print_performance_report(results)
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\nDetailed results saved to {args.output}")

if __name__ == "__main__":
    main()
