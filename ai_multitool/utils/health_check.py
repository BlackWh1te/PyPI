"""Health check functionality for ai-multitool."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time
import psutil
import os
from pathlib import Path
from ai_multitool.constants import DEFAULT_MAX_METRICS
from typing import Tuple


def determine_memory_status(available_percent: float) -> Tuple[str, str]:
    """Determine memory health status based on available percentage.
    
    Args:
        available_percent: Percentage of available memory
        
    Returns:
        Tuple of (status, message)
    """
    if available_percent < 10:
        return "unhealthy", f"Low memory: {available_percent:.1f}% available"
    elif available_percent < 20:
        return "degraded", f"Memory getting low: {available_percent:.1f}% available"
    else:
        return "healthy", f"Memory OK: {available_percent:.1f}% available"


def determine_disk_status(available_percent: float, unhealthy_threshold: float = 10, degraded_threshold: float = 20) -> Tuple[str, str]:
    """Determine disk health status based on available percentage.
    
    Args:
        available_percent: Percentage of available disk space
        unhealthy_threshold: Threshold for unhealthy status (default: 10)
        degraded_threshold: Threshold for degraded status (default: 20)
        
    Returns:
        Tuple of (status, message)
    """
    if available_percent < unhealthy_threshold:
        return "unhealthy", f"Low disk space: {available_percent:.1f}% available"
    elif available_percent < degraded_threshold:
        return "degraded", f"Disk getting low: {available_percent:.1f}% available"
    else:
        return "healthy", f"Disk OK: {available_percent:.1f}% available"


def determine_config_status(env_exists: bool, has_api_key: bool, api_key_length: int) -> Tuple[str, str]:
    """Determine configuration health status.
    
    Args:
        env_exists: Whether .env file exists
        has_api_key: Whether API key is present
        api_key_length: Length of API key
        
    Returns:
        Tuple of (status, message)
    """
    if has_api_key and api_key_length > 0:
        return "healthy", "Configuration OK: API key present"
    elif env_exists and not has_api_key:
        return "degraded", "Configuration incomplete: .env exists but API key missing"
    else:
        return "unhealthy", "Configuration missing: No .env file or API key"


def determine_metrics_file_status(metrics_file_exists: bool, file_size: int) -> Tuple[str, str]:
    """Determine metrics file health status.
    
    Args:
        metrics_file_exists: Whether metrics file exists
        file_size: Size of metrics file in bytes
        
    Returns:
        Tuple of (status, message)
    """
    if not metrics_file_exists:
        return "healthy", "Metrics file not created yet"
    
    if file_size > 10 * 1024 * 1024:  # 10 MB
        return "degraded", f"Metrics file large: {file_size / 1024 / 1024:.1f} MB"
    else:
        return "healthy", "Metrics file OK"


@dataclass
class HealthCheckResult:
    """Result of a health check."""
    component: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: str
    metrics: Dict[str, Any]
    timestamp: float


class HealthChecker:
    """Health checker for ai-multitool components."""
    
    def __init__(self, max_checks: int = 100):
        """Initialize the health checker.
        
        Args:
            max_checks: Maximum number of checks to store (default: 100)
        """
        self.checks = []
        self.max_checks = max_checks
    
    def _add_check(self, result: HealthCheckResult) -> None:
        """Add a check result, enforcing max limit.
        
        Args:
            result: HealthCheckResult to add
        """
        self.checks.append(result)
        if len(self.checks) > self.max_checks:
            self.checks = self.checks[-self.max_checks:]  # Keep only recent
    
    def check_all(self) -> Dict[str, HealthCheckResult]:
        """Run all health checks.
        
        Returns:
            Dictionary of check name to HealthCheckResult
        """
        results = {}
        
        # Memory check
        results["memory"] = self._check_memory()
        self._add_check(results["memory"])
        
        # Disk check
        results["disk"] = self._check_disk()
        self._add_check(results["disk"])
        
        # Configuration check
        results["configuration"] = self._check_configuration()
        self._add_check(results["configuration"])
        
        # Metrics file check
        results["metrics_file"] = self._check_metrics_file()
        self._add_check(results["metrics_file"])
        
        return results
    
    def check_memory(self) -> HealthCheckResult:
        """Check memory usage.
        
        Returns:
            HealthCheckResult for memory
        """
        try:
            memory = psutil.virtual_memory()
            available_percent = memory.available / memory.total * 100
            
            metrics = {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "used_percent": memory.percent,
                "available_percent": available_percent
            }
            
            status, message = determine_memory_status(available_percent)
            
            return HealthCheckResult(
                component="memory",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                component="memory",
                status="unhealthy",
                message=f"Failed to check memory: {str(e)}",
                metrics={},
                timestamp=time.time()
            )
    
    def check_disk(self) -> HealthCheckResult:
        """Check disk usage.
        
        Returns:
            HealthCheckResult for disk
        """
        try:
            disk = psutil.disk_usage('/')
            available_percent = disk.free / disk.total * 100
            
            metrics = {
                "total_gb": disk.total / (1024**3),
                "used_gb": disk.used / (1024**3),
                "free_gb": disk.free / (1024**3),
                "used_percent": disk.percent,
                "available_percent": available_percent
            }
            
            status, message = determine_disk_status(available_percent, unhealthy_threshold=5, degraded_threshold=10)
            
            return HealthCheckResult(
                component="disk",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                component="disk",
                status="unhealthy",
                message=f"Failed to check disk: {str(e)}",
                metrics={},
                timestamp=time.time()
            )
    
    def check_configuration(self) -> HealthCheckResult:
        """Check configuration.
        
        Returns:
            HealthCheckResult for configuration
        """
        try:
            # Check if .env file exists
            env_file = Path(".env")
            env_exists = env_file.exists()
            
            # Check for required environment variables
            api_key = os.getenv("ANTHROPIC_API_KEY")
            has_api_key = bool(api_key and api_key.strip())
            
            metrics = {
                "env_file_exists": env_exists,
                "has_api_key": has_api_key,
                "api_key_length": len(api_key) if api_key else 0
            }
            
            status, message = determine_config_status(env_exists, has_api_key, metrics["api_key_length"])
            
            return HealthCheckResult(
                component="configuration",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                component="configuration",
                status="unhealthy",
                message=f"Failed to check configuration: {str(e)}",
                metrics={},
                timestamp=time.time()
            )
    
    def check_metrics_file(self) -> HealthCheckResult:
        """Check metrics file.
        
        Returns:
            HealthCheckResult for metrics file
        """
        try:
            metrics_file = Path.home() / ".ai-multitool" / "metrics.json"
            metrics_file_exists = metrics_file.exists()
            
            metrics = {
                "metrics_file_exists": metrics_file_exists,
                "metrics_file_path": str(metrics_file)
            }
            
            file_size = 0
            if metrics_file_exists:
                file_size = metrics_file.stat().st_size
                metrics["file_size_bytes"] = file_size
                metrics["file_size_kb"] = file_size / 1024
            
            status, message = determine_metrics_file_status(metrics_file_exists, file_size)
            
            return HealthCheckResult(
                component="metrics_file",
                status=status,
                message=message,
                metrics=metrics,
                timestamp=time.time()
            )
        except Exception as e:
            return HealthCheckResult(
                component="metrics_file",
                status="unhealthy",
                message=f"Failed to check metrics file: {str(e)}",
                metrics={},
                timestamp=time.time()
            )
    
    def get_overall_status(self) -> str:
        """Get overall health status.
        
        Returns:
            Overall status: "healthy", "degraded", or "unhealthy"
        """
        results = self.check_all()
        
        statuses = [r.status for r in results.values()]
        
        if "unhealthy" in statuses:
            return "unhealthy"
        elif "degraded" in statuses:
            return "degraded"
        else:
            return "healthy"
    
    def print_health_report(self):
        """Print a formatted health report."""
        results = self.check_all()
        overall_status = self.get_overall_status()
        
        print("=" * 60)
        print(f"Health Check Report - {overall_status.upper()}")
        print("=" * 60)
        print()
        
        for component, result in results.items():
            status_icon = {
                "healthy": "✓",
                "degraded": "⚠",
                "unhealthy": "✗"
            }.get(result.status, "?")
            
            print(f"{status_icon} {component.upper()}: {result.message}")
            
            if result.metrics:
                print(f"  Metrics: {result.metrics}")
            print()


def run_health_check() -> Dict[str, HealthCheckResult]:
    """Run health check and return results.
    
    Returns:
        Dictionary of check results
    """
    checker = HealthChecker()
    return checker.check_all()


if __name__ == "__main__":
    checker = HealthChecker()
    checker.print_health_report()
