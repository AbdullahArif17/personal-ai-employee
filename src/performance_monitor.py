'''
Performance monitoring for the Personal AI Employee system.
Implements performance monitoring for all features (30s Ralph loop, 10s social media gen, 5s Odoo ops).
'''

import time
import functools
from datetime import datetime
from typing import Callable, Any
import sys
from pathlib import Path

# Add the src directory to the Python path to allow imports when running as a script
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

try:
    from .logger import setup_logger, AuditLogger
except ImportError:
    # Fallback for when running as a script directly
    from logger import setup_logger, AuditLogger

logger = setup_logger('performance_monitor')
audit_logger = AuditLogger('performance_monitor')

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    'ralph_loop': 30,  # 30 seconds for Ralph loop processing
    'social_media_gen': 10,  # 10 seconds for social media generation
    'odoo_ops': 5,  # 5 seconds for Odoo operations
    'twitter_ops': 10,  # 10 seconds for Twitter operations
    'facebook_ops': 10,  # 10 seconds for Facebook operations
    'instagram_ops': 10,  # 10 seconds for Instagram operations
    'weekly_audit': 300,  # 5 minutes for weekly audit processing
}

class PerformanceMonitor:
    """
    Performance monitoring class to track execution times and alert on slow operations.
    """

    def __init__(self):
        self.performance_metrics = {}

    def time_function(self, operation_name: str):
        """
        Decorator to time function execution and log performance metrics.

        Args:
            operation_name: Name of the operation being timed
        """
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                start_time = time.time()

                try:
                    result = func(*args, **kwargs)
                    execution_time = time.time() - start_time

                    # Log the execution time
                    self.log_performance(operation_name, execution_time)

                    return result
                except Exception as e:
                    execution_time = time.time() - start_time
                    self.log_performance(operation_name, execution_time, error=str(e))
                    raise
            return wrapper
        return decorator

    def log_performance(self, operation_name: str, execution_time: float, error: str = None):
        """
        Log performance metrics for an operation.

        Args:
            operation_name: Name of the operation
            execution_time: Execution time in seconds
            error: Error message if operation failed
        """
        threshold = PERFORMANCE_THRESHOLDS.get(operation_name, 30)  # Default to 30s

        if execution_time > threshold:
            # Performance warning - operation took longer than threshold
            perf_msg = f"PERFORMANCE WARNING: {operation_name} took {execution_time:.2f}s (threshold: {threshold}s)"
            logger.warning(perf_msg)

            audit_logger.log_external_action(
                "performance_warning",
                operation_name,
                False,
                {
                    "execution_time": execution_time,
                    "threshold": threshold,
                    "error": error
                }
            )
        else:
            # Normal performance - operation within threshold
            perf_msg = f"PERFORMANCE OK: {operation_name} took {execution_time:.2f}s (threshold: {threshold}s)"
            logger.debug(perf_msg)

            audit_logger.log_external_action(
                "performance_ok",
                operation_name,
                True,
                {
                    "execution_time": execution_time,
                    "threshold": threshold,
                    "error": error
                }
            )

        # Update metrics store
        if operation_name not in self.performance_metrics:
            self.performance_metrics[operation_name] = []

        self.performance_metrics[operation_name].append({
            'timestamp': datetime.now().isoformat(),
            'execution_time': execution_time,
            'threshold': threshold,
            'error': error
        })

    def get_average_execution_time(self, operation_name: str) -> float:
        """
        Get average execution time for an operation.

        Args:
            operation_name: Name of the operation

        Returns:
            Average execution time in seconds, or 0 if no metrics available
        """
        if operation_name not in self.performance_metrics:
            return 0

        metrics = self.performance_metrics[operation_name]
        if not metrics:
            return 0

        total_time = sum(m['execution_time'] for m in metrics)
        return total_time / len(metrics)

    def get_slow_operations(self, operation_name: str, threshold_multiplier: float = 1.0) -> list:
        """
        Get operations that took longer than the threshold multiplied by the multiplier.

        Args:
            operation_name: Name of the operation
            threshold_multiplier: Multiplier for the threshold (e.g., 2.0 for 2x threshold)

        Returns:
            List of slow operations
        """
        if operation_name not in self.performance_metrics:
            return []

        threshold = PERFORMANCE_THRESHOLDS.get(operation_name, 30) * threshold_multiplier
        slow_ops = [m for m in self.performance_metrics[operation_name] if m['execution_time'] > threshold]

        return slow_ops


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    return perf_monitor


# Convenience decorators for common operations
def time_ralph_loop(func: Callable) -> Callable:
    """Decorator to time Ralph Wiggum Loop operations."""
    return perf_monitor.time_function('ralph_loop')(func)

def time_social_media_gen(func: Callable) -> Callable:
    """Decorator to time social media generation operations."""
    return perf_monitor.time_function('social_media_gen')(func)

def time_odoo_ops(func: Callable) -> Callable:
    """Decorator to time Odoo operations."""
    return perf_monitor.time_function('odoo_ops')(func)

def time_twitter_ops(func: Callable) -> Callable:
    """Decorator to time Twitter operations."""
    return perf_monitor.time_function('twitter_ops')(func)

def time_facebook_ops(func: Callable) -> Callable:
    """Decorator to time Facebook operations."""
    return perf_monitor.time_function('facebook_ops')(func)

def time_instagram_ops(func: Callable) -> Callable:
    """Decorator to time Instagram operations."""
    return perf_monitor.time_function('instagram_ops')(func)

def time_weekly_audit(func: Callable) -> Callable:
    """Decorator to time weekly audit operations."""
    return perf_monitor.time_function('weekly_audit')(func)